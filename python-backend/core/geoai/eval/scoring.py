# Author: Utkarsh Gupta
# License: GPL v3
"""
Deterministic GeoAI turn scorer (AGENTS.md §21, §25).

``score_turn(example, model_response)`` judges ONE model turn against an
``EvalExample`` and returns a ``ScoreBreakdown`` with per-criterion scores in
[0, 1], a weighted total in [0, 1] and human-readable reasons.

Design rules:

* No LLM is ever used as the oracle. Every criterion is computed from the
  example metadata, the real tool schemas held by the GeoAI Tool Registry and
  the deterministic unit engine in ``core.geoai.units``.
* Tool schemas are never duplicated here: argument validity and the effective
  values Groundhog would receive come from ``tool.input_model`` (the same
  Pydantic model the registry validates with).
* Side-effect free by default. The optional end-to-end check
  (``execute=True``) invokes the registry, which only runs deterministic
  Groundhog functions; tools that write state (see ``SIDE_EFFECT_TOOLS``) are
  never executed by the scorer.
* Pure function of its inputs, so it can be used directly as a GRPO reward:
  ``score_turn(example_dict, completion_text).total``.
"""

import json
import math
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from core.geoai.eval.example import EvalExample, ExampleLike, as_example
from core.geoai.exceptions import GeoAIUnitError
from core.geoai.units import (
    convert_unit,
    get_unit_dimension,
    normalize_parameter_value,
)

# Tools the scorer must never execute (they mutate local state).
SIDE_EFFECT_TOOLS = frozenset({"index_document_text"})

CRITERION_WEIGHTS: Dict[str, float] = {
    "action": 3.0,
    "tool": 2.0,
    "schema": 1.0,
    "arguments": 2.0,
    "no_invented": 2.0,
    "clarification": 1.0,
    "unit_trap": 1.5,
    "execution": 1.0,
    "grounding": 2.0,
    "caution": 1.0,
}

# A turn that invents parameter values can never score above this (§5, §17).
INVENTED_VALUE_CAP = 0.5
# When a tool call is expected, calling the right tool with a WRONG value for a
# parameter the user stated caps the total at BASE + SLOPE * arguments_score, so
# argument correctness dominates format/action credit (RL signal, §16):
#   all stated values right -> uncapped (~1.0); half right -> 0.425; none right -> 0.25.
ARGUMENT_MISMATCH_CAP_BASE = 0.25
ARGUMENT_MISMATCH_CAP_SLOPE = 0.35
# Calling a tool when a different tool was expected can never score above this.
WRONG_TOOL_CAP = 0.2

DEFAULT_REL_TOL = 0.01
DEFAULT_ABS_TOL = 1e-6

_CLARIFY_CUES = (
    "?", "please provide", "please specify", "please confirm", "please supply",
    "please clarify", "please check", "please verify", "could you", "can you provide",
    "can you confirm", "can you clarify", "i need", "need the", "need to know",
    "missing", "which value", "which of", "not provided", "not specified",
    "not available", "do you want", "would you like", "please tell me", "tell me", "let me know",
    "please share", "please send", "please give",
)
_REJECT_CUES = (
    "invalid", "must be", "cannot be", "can't be", "not physically", "physically impossible",
    "out of range", "outside the valid", "outside the range", "outside the allowed",
    "not valid", "negative", "impossible", "not possible", "exceeds", "should be positive",
    "must be positive", "must be greater", "must be less", "not realistic", "unrealistic",
    "error", "failed", "rejected",
)

_GLOBAL_FORBIDDEN = (
    r"\b(?:design|foundation|wall|pile|slope|structure|it|this)\s+is\s+(?:completely\s+|perfectly\s+|definitely\s+|100%\s+)?safe\b",
    r"\bis\s+guaranteed\b",
    r"\bguaranteed\s+to\s+be\s+safe\b",
)
_DOI_PATTERN = r"(?:doi:\s*10\.\d{4,9}/|\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)"


# =====================================================================
# Response normalisation
# =====================================================================

@dataclass
class ParsedToolCall:
    name: str
    arguments: Dict[str, Any]
    parse_error: Optional[str] = None


@dataclass
class ParsedResponse:
    content: str = ""
    tool_calls: List[ParsedToolCall] = field(default_factory=list)


_TOOL_CALL_TAG = re.compile(r"<tool_call>\s*(.*?)\s*(?:</tool_call>|$)", re.DOTALL | re.IGNORECASE)
_FENCED_JSON = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def _coerce_arguments(raw: Any) -> Tuple[Dict[str, Any], Optional[str]]:
    if raw is None:
        return {}, None
    if isinstance(raw, dict):
        return dict(raw), None
    if isinstance(raw, str):
        try:
            val = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError as e:
            return {}, f"arguments are not valid JSON: {e}"
        if isinstance(val, dict):
            return val, None
        return {}, "arguments JSON is not an object"
    return {}, f"unsupported arguments type {type(raw).__name__}"


def _tool_call_from_obj(obj: Any) -> Optional[ParsedToolCall]:
    if not isinstance(obj, dict):
        return None
    if "function" in obj and isinstance(obj["function"], dict):
        obj = obj["function"]
    name = obj.get("name") or obj.get("function_name") or obj.get("tool")
    if not name or not isinstance(name, str):
        return None
    raw_args = obj.get("arguments", obj.get("parameters", obj.get("args")))
    args, err = _coerce_arguments(raw_args)
    return ParsedToolCall(name=name, arguments=args, parse_error=err)


def parse_completion(text: str) -> ParsedResponse:
    """
    Parse a raw completion string (e.g. a GRPO rollout) into content + tool calls.

    Supports Hermes/Qwen ``<tool_call>{...}</tool_call>`` blocks, fenced JSON
    and a bare JSON object with ``name``/``arguments``. Anything else is
    treated as plain text.
    """
    text = text or ""
    calls: List[ParsedToolCall] = []
    remainder = text

    tagged = _TOOL_CALL_TAG.findall(text)
    if tagged:
        for blob in tagged:
            try:
                obj = json.loads(blob)
            except json.JSONDecodeError as e:
                calls.append(ParsedToolCall(name="", arguments={}, parse_error=f"invalid tool_call JSON: {e}"))
                continue
            tc = _tool_call_from_obj(obj)
            if tc:
                calls.append(tc)
        remainder = _TOOL_CALL_TAG.sub("", text)
    else:
        candidates = _FENCED_JSON.findall(text)
        stripped = text.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            candidates.append(stripped)
        for blob in candidates:
            try:
                obj = json.loads(blob)
            except json.JSONDecodeError:
                continue
            objs = obj.get("tool_calls") if isinstance(obj, dict) and isinstance(obj.get("tool_calls"), list) else [obj]
            for o in objs:
                tc = _tool_call_from_obj(o)
                if tc:
                    calls.append(tc)
            if calls:
                remainder = text.replace(blob, "")
                break
    return ParsedResponse(content=remainder.strip(), tool_calls=calls)


def normalise_response(response: Any) -> ParsedResponse:
    """Accept ModelResponse, ParsedResponse, OpenAI-style dict, AgentResponse-like dict or str."""
    if isinstance(response, ParsedResponse):
        return response
    if response is None:
        return ParsedResponse()
    if isinstance(response, str):
        return parse_completion(response)

    # ModelResponse / ChatMessage (duck-typed to avoid import cycles)
    if hasattr(response, "tool_calls") and hasattr(response, "content") and not isinstance(response, dict):
        calls = []
        for tc in response.tool_calls or []:
            name = getattr(tc, "function_name", None) or getattr(tc, "name", "")
            args, err = _coerce_arguments(getattr(tc, "arguments", {}))
            calls.append(ParsedToolCall(name=name, arguments=args, parse_error=err))
        content = response.content or ""
        if not calls and content:
            parsed = parse_completion(content)
            if parsed.tool_calls:
                return parsed
        return ParsedResponse(content=content, tool_calls=calls)

    if isinstance(response, dict):
        content = response.get("content") or response.get("response") or ""
        raw_calls = response.get("tool_calls") or []
        calls = []
        for rc in raw_calls:
            tc = _tool_call_from_obj(rc)
            if tc:
                calls.append(tc)
        if not calls and content:
            parsed = parse_completion(content)
            if parsed.tool_calls:
                return parsed
        return ParsedResponse(content=content, tool_calls=calls)

    raise TypeError(f"Unsupported model response type: {type(response)!r}")


# =====================================================================
# Registry / schema helpers (schemas are read, never duplicated)
# =====================================================================

_DEFAULT_REGISTRY = None


def default_registry():
    """The global GeoAI Tool Registry with canonical tool definitions loaded."""
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        import core.geoai.tool_definitions  # noqa: F401  (registers canonical tools)
        from core.geoai.tool_registry import tool_registry
        _DEFAULT_REGISTRY = tool_registry
    return _DEFAULT_REGISTRY


def clean_unit(unit: Optional[str]) -> str:
    """Strip Sphinx ':math:`...`' wrappers found in auto-generated schemas."""
    if not unit:
        return "-"
    u = str(unit).strip()
    m = re.fullmatch(r":math:`(.*)`", u)
    if m:
        u = m.group(1).strip()
    return u or "-"


def field_unit(field_info) -> str:
    extra = field_info.json_schema_extra if isinstance(field_info.json_schema_extra, dict) else {}
    return clean_unit(extra.get("unit"))


def field_aliases(input_model) -> Dict[str, str]:
    """Map every accepted key (field name + validation aliases) to the canonical field name."""
    out: Dict[str, str] = {}
    for name, fi in input_model.model_fields.items():
        out[name] = name
        alias = fi.validation_alias
        choices: Sequence[Any] = ()
        if alias is not None:
            if hasattr(alias, "choices"):
                choices = alias.choices
            elif isinstance(alias, str):
                choices = (alias,)
        for c in choices:
            if isinstance(c, str):
                out.setdefault(c, name)
        if fi.alias:
            out.setdefault(fi.alias, name)
    return out


def canonicalise_keys(input_model, args: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Return ({canonical_field: raw_value}, [unknown keys])."""
    amap = field_aliases(input_model)
    canon: Dict[str, Any] = {}
    unknown: List[str] = []
    for k, v in (args or {}).items():
        f = amap.get(k)
        if f is None:
            unknown.append(k)
        elif f not in canon:
            canon[f] = v
    return canon, unknown


def effective_arguments(input_model, args: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Values Groundhog would actually receive (schema validation + unit normalisation)."""
    try:
        inst = input_model(**(args or {}))
        return inst.model_dump(exclude_unset=False), None
    except Exception as e:  # pydantic ValidationError, GeoAIUnitError, TypeError...
        return None, str(e).splitlines()[0] if str(e) else type(e).__name__


def normalise_field_value(input_model, field_name: str, value: Any) -> Any:
    """Deterministically normalise ONE value to the field's canonical unit (units.py)."""
    fi = input_model.model_fields.get(field_name)
    unit = field_unit(fi) if fi is not None else "-"
    try:
        return normalize_parameter_value(value, expected_unit=None if unit == "-" else unit, field_name=field_name)
    except Exception:
        return value


def shares_schema(registry, tool_a: str, tool_b: str) -> bool:
    ta, tb = registry.get_tool(tool_a), registry.get_tool(tool_b)
    return bool(ta and tb and ta.input_model is tb.input_model)


# =====================================================================
# Value comparison / text grounding
# =====================================================================

def _is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v))


def values_match(expected: Any, actual: Any, rel_tol: float = DEFAULT_REL_TOL, abs_tol: float = DEFAULT_ABS_TOL) -> bool:
    if isinstance(expected, bool):
        return isinstance(actual, (bool, int)) and bool(actual) == expected
    if isinstance(actual, bool):
        return False
    if _is_number(expected):
        if isinstance(actual, str):
            try:
                actual = float(actual)
            except ValueError:
                return False
        if not _is_number(actual):
            return False
        return math.isclose(float(expected), float(actual), rel_tol=rel_tol, abs_tol=abs_tol)
    if isinstance(expected, str):
        if not isinstance(actual, str):
            return False
        exp_tokens = set(re.findall(r"[a-z0-9]+", expected.lower()))
        act_tokens = set(re.findall(r"[a-z0-9]+", actual.lower()))
        if not exp_tokens:
            return True
        return len(exp_tokens & act_tokens) / len(exp_tokens) >= 0.5
    return expected == actual


_SUPERSCRIPTS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
_NUM_UNIT = re.compile(
    r"(?<![A-Za-z_])([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*"
    r"([A-Za-z°%µ][A-Za-z0-9°%/\^²³·]*)?"
)
_SCI_TIMES = re.compile(r"([+-]?\d+(?:\.\d+)?)\s*[x×\*]\s*10\s*\^?\s*\(?\s*([+-−]?\d+)\s*\)?")


def extract_numbers(text: str) -> List[Tuple[float, Optional[str]]]:
    """Extract (value, unit-or-None) pairs from free text, handling 1,234 and 2.6 × 10^-4."""
    if not text:
        return []
    t = text.translate(_SUPERSCRIPTS).replace("−", "-")
    t = re.sub(r"(?<=\d),(?=\d{3}\b)", "", t)
    out: List[Tuple[float, Optional[str]]] = []

    def _sci(m):
        try:
            out.append((float(m.group(1)) * 10 ** int(m.group(2).replace("−", "-")), None))
        except ValueError:
            pass
        return " "
    t = _SCI_TIMES.sub(_sci, t)
    for m in _NUM_UNIT.finditer(t):
        try:
            val = float(m.group(1))
        except ValueError:
            continue
        unit = m.group(2)
        if unit:
            unit = unit.replace("²", "2").replace("³", "3").replace("·", "")
        out.append((val, unit))
    return out


def _number_in_text(value: float, numbers: List[Tuple[float, Optional[str]]], unit: Optional[str] = None,
                    rel_tol: float = 0.015) -> bool:
    if not _is_number(value):
        return False
    v = float(value)
    for n, u in numbers:
        if math.isclose(n, v, rel_tol=rel_tol, abs_tol=1e-9):
            return True
        if u and unit and unit != "-":
            try:
                if get_unit_dimension(u) is not None and get_unit_dimension(u) == get_unit_dimension(unit):
                    if math.isclose(convert_unit(n, u, unit), v, rel_tol=rel_tol, abs_tol=1e-9):
                        return True
            except Exception:
                pass
    return False


def value_grounded(value: Any, numbers: List[Tuple[float, Optional[str]]], unit: str) -> bool:
    """Is a numeric argument value traceable to a number stated in the prompt/context?"""
    if not _is_number(value):
        return isinstance(value, (str, bool))  # textual/boolean flags are not numeric inventions
    v = float(value)
    for n, u in numbers:
        if math.isclose(n, v, rel_tol=0.01, abs_tol=1e-9):
            return True
        if u == "%" and math.isclose(n / 100.0, v, rel_tol=0.01, abs_tol=1e-9):
            return True
        if u and unit != "-":
            try:
                if math.isclose(convert_unit(n, u, unit), v, rel_tol=0.01, abs_tol=1e-9):
                    return True
            except Exception:
                pass
    return False


def _group_hits(text: str, groups: List[List[str]]) -> Tuple[int, List[str]]:
    low = (text or "").lower()
    hits, missed = 0, []
    for g in groups:
        if any(s.lower() in low for s in g):
            hits += 1
        else:
            missed.append(g[0] if g else "?")
    return hits, missed


def _text_classes(text: str) -> List[str]:
    low = (text or "").strip().lower()
    if not low:
        return []
    classes = []
    if any(c in low for c in _CLARIFY_CUES):
        classes.append("clarify")
    if any(c in low for c in _REJECT_CUES):
        classes.append("reject")
    if len(low) >= 40 or not classes:
        classes.append("synthesize")
    return classes


# =====================================================================
# Score breakdown
# =====================================================================

@dataclass
class ScoreBreakdown:
    """Per-criterion scores in [0, 1]; ``None`` means the criterion does not apply."""
    action: Optional[float] = None
    tool: Optional[float] = None
    schema: Optional[float] = None
    arguments: Optional[float] = None
    no_invented: Optional[float] = None
    clarification: Optional[float] = None
    unit_trap: Optional[float] = None
    execution: Optional[float] = None
    grounding: Optional[float] = None
    caution: Optional[float] = None
    total: float = 0.0
    passed: bool = False
    expected_action: str = ""
    predicted_action: str = "empty"
    predicted_tool: Optional[str] = None
    predicted_arguments: Optional[Dict[str, Any]] = None
    invented_params: List[str] = field(default_factory=list)
    unknown_params: List[str] = field(default_factory=list)
    hallucinated_tool: bool = False
    reasons: List[str] = field(default_factory=list)

    CRITERIA = tuple(CRITERION_WEIGHTS.keys())

    def criteria(self) -> Dict[str, Optional[float]]:
        return {c: getattr(self, c) for c in self.CRITERIA}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _finalise(sb: ScoreBreakdown, weights: Dict[str, float]) -> ScoreBreakdown:
    num = den = 0.0
    for c, s in sb.criteria().items():
        if s is None:
            continue
        w = weights.get(c, 0.0)
        num += w * s
        den += w
    total = num / den if den else 0.0
    if sb.invented_params or sb.unknown_params:
        total = min(total, INVENTED_VALUE_CAP)
    if sb.predicted_action == "tool_call" and sb.tool is not None:
        if sb.tool == 0.0:
            total = min(total, WRONG_TOOL_CAP)
        elif sb.arguments is not None and sb.arguments < 1.0:
            total = min(total, ARGUMENT_MISMATCH_CAP_BASE + ARGUMENT_MISMATCH_CAP_SLOPE * sb.arguments)
    sb.total = round(total, 6)
    sb.passed = bool(
        sb.action == 1.0
        and all(s is None or s >= 0.999 for s in sb.criteria().values())
    )
    return sb


# =====================================================================
# Main API
# =====================================================================

def score_turn(
    example: ExampleLike,
    model_response: Any,
    *,
    registry=None,
    execute: bool = False,
    rel_tol: float = DEFAULT_REL_TOL,
    weights: Optional[Dict[str, float]] = None,
) -> ScoreBreakdown:
    """
    Score one model turn deterministically.

    Args:
        example: ``EvalExample`` or its dict form (e.g. a JSONL row).
        model_response: ``ModelResponse``, OpenAI-style dict, or raw completion
            text (``<tool_call>{json}</tool_call>`` or bare JSON supported).
        registry: GeoAI Tool Registry (defaults to the global registry).
        execute: also run the predicted tool call through the registry and
            compare with ``example.expected_result`` (end-to-end check).
        rel_tol: relative tolerance for argument comparison after unit
            normalisation.
        weights: optional override of ``CRITERION_WEIGHTS``.

    Returns:
        ``ScoreBreakdown`` — ``total`` in [0, 1] (capped at 0.5 when invented
        parameter values are detected); ``passed`` is True only when every
        applicable criterion is fully satisfied.
    """
    ex: EvalExample = as_example(example)
    reg = registry if registry is not None else default_registry()
    resp = normalise_response(model_response)
    w = dict(CRITERION_WEIGHTS)
    if weights:
        w.update(weights)

    sb = ScoreBreakdown(expected_action=ex.expected_action)
    allowed = {ex.expected_action, *ex.acceptable_actions}
    text = resp.content or ""

    # ---------------- action ----------------
    tc: Optional[ParsedToolCall] = None
    if resp.tool_calls:
        sb.predicted_action = "tool_call"
        tc = resp.tool_calls[0]
        if ex.expected_tool:
            for cand in resp.tool_calls:
                if cand.name == ex.expected_tool or cand.name in ex.acceptable_tools:
                    tc = cand
                    break
        sb.predicted_tool = tc.name
        sb.predicted_arguments = tc.arguments
        sb.action = 1.0 if "tool_call" in allowed else 0.0
        if sb.action == 0.0:
            sb.reasons.append(f"called tool '{tc.name}' but expected {ex.expected_action}")
    else:
        classes = _text_classes(text)
        if not classes:
            sb.predicted_action = "empty"
            sb.action = 0.0
            sb.reasons.append("empty response")
        else:
            match = [c for c in classes if c in allowed]
            sb.predicted_action = match[0] if match else classes[0]
            if match:
                sb.action = 1.0
            elif "tool_call" not in allowed:
                sb.action = 0.5
                sb.reasons.append(f"answered without a tool (good) but response reads as {classes[0]}, expected {ex.expected_action}")
            else:
                sb.action = 0.0
                sb.reasons.append(f"expected a tool call to '{ex.expected_tool}', got a text {classes[0]}")

    tool_expected = ex.expected_action == "tool_call" or ("tool_call" in allowed and ex.expected_tool)
    tool_obj = reg.get_tool(tc.name) if tc and tc.name else None

    # ---------------- tool selection ----------------
    if tool_expected and ex.expected_tool:
        if tc is None:
            sb.tool = 0.0
        elif tc.name == ex.expected_tool:
            sb.tool = 1.0
        elif tc.name in ex.acceptable_tools or (tool_obj and shares_schema(reg, tc.name, ex.expected_tool)):
            sb.tool = 0.75
            sb.reasons.append(f"used equivalent tool '{tc.name}' instead of '{ex.expected_tool}'")
        else:
            sb.tool = 0.0
            sb.reasons.append(f"wrong tool '{tc.name}' (expected '{ex.expected_tool}')")

    effective: Optional[Dict[str, Any]] = None
    canon: Dict[str, Any] = {}
    if tc is not None:
        if tc.parse_error:
            sb.reasons.append(tc.parse_error)
        if tool_obj is None:
            sb.hallucinated_tool = True
            sb.schema = 0.0
            sb.reasons.append(f"tool '{tc.name}' is not in the GeoAI Tool Registry")
        else:
            canon, unknown = canonicalise_keys(tool_obj.input_model, tc.arguments)
            sb.unknown_params = sorted(unknown)
            effective, err = effective_arguments(tool_obj.input_model, tc.arguments)
            if tc.parse_error:
                sb.schema = 0.0
            elif err is not None:
                sb.schema = 0.0
                sb.reasons.append(f"arguments fail schema validation: {err}")
            elif unknown:
                sb.schema = 0.0
                sb.reasons.append(f"unknown parameters for '{tc.name}': {sorted(unknown)}")
            else:
                sb.schema = 1.0

    # ---------------- argument values ----------------
    tool_ok = tc is not None and tool_obj is not None and sb.tool is not None and sb.tool > 0
    if tool_expected and ex.expected_arguments:
        if not tool_ok:
            sb.arguments = 0.0
        else:
            matched, bad = 0, []
            for name, exp_val in ex.expected_arguments.items():
                if effective is not None and name in effective:
                    act = effective[name]
                elif name in canon:
                    act = normalise_field_value(tool_obj.input_model, name, canon[name])
                else:
                    fi = tool_obj.input_model.model_fields.get(name)
                    act = fi.default if fi is not None and not fi.is_required() else None
                if values_match(exp_val, act, rel_tol=rel_tol):
                    matched += 1
                else:
                    bad.append(f"{name}: expected {exp_val!r}, got {act!r}")
            sb.arguments = matched / len(ex.expected_arguments)
            if bad:
                sb.reasons.append("argument mismatch: " + "; ".join(bad))

    # ---------------- invented parameters ----------------
    if tc is not None and tool_obj is not None:
        sb.no_invented = 1.0
        grounding_text = _grounding_text(ex)
        numbers = extract_numbers(grounding_text)
        invented = []
        for name, raw in canon.items():
            fi = tool_obj.input_model.model_fields.get(name)
            norm = effective.get(name) if effective is not None and name in effective else normalise_field_value(tool_obj.input_model, name, raw)
            if fi is not None and not fi.is_required() and values_match(fi.default, norm, rel_tol=1e-9, abs_tol=1e-12):
                continue  # restating a schema default is not an invention
            if ex.provided_params is not None:
                if name in ex.provided_params:
                    continue
                if name in ex.missing_params or not value_grounded(norm, numbers, field_unit(fi) if fi else "-"):
                    invented.append(name)
            else:
                if not value_grounded(norm, numbers, field_unit(fi) if fi else "-") and not value_grounded(raw, numbers, "-"):
                    invented.append(name)
        sb.invented_params = sorted(invented)
        if invented or sb.unknown_params:
            sb.no_invented = 0.0
            if invented:
                sb.reasons.append(f"invented values for parameters not given in prompt/context: {sb.invented_params}")

    # ---------------- clarification / rejection ----------------
    if ex.expected_action in ("clarify", "reject"):
        if tc is not None:
            sb.clarification = 0.0
        elif not text.strip():
            sb.clarification = 0.0
        elif ex.clarify_keywords:
            hits, missed = _group_hits(text, ex.clarify_keywords)
            sb.clarification = hits / len(ex.clarify_keywords)
            if missed:
                sb.reasons.append(f"clarification does not mention: {missed}")
        else:
            sb.clarification = 1.0 if sb.action == 1.0 else 0.5

    # ---------------- unit traps ----------------
    trap = ex.unit_trap
    if trap:
        param = trap.get("param")
        if trap.get("kind") == "convertible":
            exp_val = (ex.expected_arguments or {}).get(param)
            if tc is None or not tool_ok:
                sb.unit_trap = 0.0
            else:
                act = effective.get(param) if effective is not None and param in effective else (
                    normalise_field_value(tool_obj.input_model, param, canon[param]) if param in canon else None)
                sb.unit_trap = 1.0 if values_match(exp_val, act, rel_tol=rel_tol) else 0.0
                if sb.unit_trap == 0.0:
                    sb.reasons.append(f"unit conversion trap failed for '{param}' (given {trap.get('given')}; expected {exp_val}, got {act})")
        else:  # dimension_mismatch: must NOT pass the value on; should flag the unit
            if tc is not None and param in canon:
                sb.unit_trap = 0.0
                sb.reasons.append(f"passed dimensionally wrong value '{trap.get('given')}' for '{param}' to a tool")
            elif tc is not None:
                sb.unit_trap = 0.5
            else:
                given_unit = str(trap.get("given", "")).split()[-1].lower() if trap.get("given") else ""
                low = text.lower()
                mentions = "unit" in low or (given_unit and given_unit in low)
                sb.unit_trap = 1.0 if mentions else 0.5
                if not mentions:
                    sb.reasons.append("did not point out the unit/dimension problem")

    # ---------------- end-to-end execution ----------------
    if execute and ex.expected_result and tool_ok and tc.name not in SIDE_EFFECT_TOOLS:
        try:
            got = reg.invoke_tool(tc.name, dict(tc.arguments))
            keys = [k for k, v in ex.expected_result.items() if _is_number(v) and k in got]
            if not keys:
                # equivalent tool with differently named outputs: compare the value sets instead
                exp_vals = sorted(float(v) for v in ex.expected_result.values() if _is_number(v))
                got_vals = sorted(float(v) for k, v in got.items() if not k.startswith("_") and _is_number(v))
                ok = bool(exp_vals) and all(any(values_match(e, g, rel_tol=rel_tol) for g in got_vals) for e in exp_vals)
                bad = [] if ok else ["<outputs>"]
            else:
                bad = [k for k in keys if not values_match(ex.expected_result[k], got.get(k), rel_tol=rel_tol)]
            sb.execution = 0.0 if bad else 1.0
            if bad:
                sb.reasons.append(f"Groundhog result differs from expected for {bad}")
        except Exception as e:
            sb.execution = 0.0
            sb.reasons.append(f"tool execution failed: {str(e).splitlines()[0]}")

    # ---------------- grounded final answer ----------------
    # Result values are only judged on final-answer turns; required mentions on any turn.
    check_values = ex.turn_type == "final_answer" and bool(ex.expected_result_values)
    if check_values or ex.required_mentions:
        total_items = hits = 0
        if tc is None and text:
            nums = extract_numbers(text)
            units = (ex.metadata or {}).get("result_units", {})
            missing_vals = []
            for k, v in ((ex.expected_result_values or {}) if check_values else {}).items():
                total_items += 1
                if _number_in_text(v, nums, units.get(k)):
                    hits += 1
                else:
                    missing_vals.append(k)
            if ex.required_mentions:
                h, missed = _group_hits(text, ex.required_mentions)
                hits += h
                total_items += len(ex.required_mentions)
                missing_vals += missed
            if missing_vals:
                sb.reasons.append(f"final answer does not report: {missing_vals}")
            sb.grounding = hits / total_items if total_items else 1.0
        else:
            sb.grounding = 0.0

    # ---------------- engineering caution (§11, §18) ----------------
    if text.strip():
        patterns = list(_GLOBAL_FORBIDDEN) + list(ex.forbidden_patterns or [])
        hit = next((p for p in patterns if re.search(p, text, re.IGNORECASE)), None)
        if hit is None and re.search(_DOI_PATTERN, text, re.IGNORECASE):
            if not re.search(_DOI_PATTERN, _grounding_text(ex), re.IGNORECASE):
                hit = "unverified DOI"
        sb.caution = 0.0 if hit else 1.0
        if hit:
            sb.reasons.append(f"engineering-caution violation ({hit})")

    return _finalise(sb, w)


def _grounding_text(ex: EvalExample) -> str:
    """All evidence the model was given: messages + project context."""
    parts: List[str] = []
    for m in ex.messages:
        if m.get("content"):
            parts.append(str(m["content"]))
        for tcall in m.get("tool_calls") or []:
            fn = tcall.get("function", tcall)
            args = fn.get("arguments")
            parts.append(args if isinstance(args, str) else json.dumps(args))
    if ex.context:
        pc = ex.context.get("project_context")
        if isinstance(pc, str):
            parts.append(pc)
        elif pc is not None and hasattr(pc, "get_compact_context_string"):
            parts.append(pc.get_compact_context_string())
    return "\n".join(parts)


def reward(example: ExampleLike, completion: Any, **kwargs) -> float:
    """Scalar convenience wrapper (e.g. for GRPO): ``score_turn(...).total``."""
    return score_turn(example, completion, **kwargs).total
