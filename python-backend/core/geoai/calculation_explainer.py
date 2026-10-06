# Author: Utkarsh Gupta
# License: GPL v3
"""
Grounded explanation of a single calculation result shown in the GeoCore calculation UI (not the
GeoAI chat): the method/standard from TOOL_METADATA, the formula taken straight from the groundhog
function's own docstring (never invented), and the actual substituted inputs/outputs. These three
things are deterministic and need no model.

An optional short narration from the local model reads these facts aloud for the UI's "quick
explanation" card. Per AGENTS.md SS5/SS18, the model only explains here — it is never asked to
produce a number, a formula, a method or a standard; those are already given to it.
"""
import inspect
import re
import textwrap
from typing import Any, Dict, List, Optional, Tuple

from core.geoai.tool_metadata import curated_tool_metadata, get_tool_metadata

_MATH_BLOCK_RE = re.compile(r"\.\. math::\n((?:[ \t]+\S.*\n?)+)")
# ":param key: Human description (:math:`symbol`) [:math:`unit`] - Suggested range: ..." — keep only
# the human description, same convention website/_content/extract_docs.py uses for the API reference.
_PARAM_RE = re.compile(r"^:param\s+(\w+):\s*(.*)$", re.MULTILINE)
_PARAM_TRAILER_RE = re.compile(r"\s*\(:math:|\s*\[:math:|\s*-\s*Suggested range:")
# The symbol and unit groundhog documents for a parameter or output: "(:math:`p'_{o,tip}`) [:math:`kPa`]".
_SYMBOL_RE = re.compile(r"\(:math:`([^`]+)`\)")
_UNIT_RE = re.compile(r"\[(?::math:`)?([^`\]]*)`?\]")
# Output key with its unit, as groundhog returns it: "q_b_coring [kPa]".
_KEY_UNIT_RE = re.compile(r"^(.*?)\s*\[([^\]]*)\]\s*$")
# A symbol in a LaTeX formula: N_q, p'_{o,tip}, \sigma_{1,f}.
_FORMULA_SYMBOL_RE = re.compile(r"\\?[A-Za-z]+'?(?:_(?:\{[^}]*\}|[A-Za-z0-9]))?'?")


def extract_param_labels(docstring: Optional[str]) -> Dict[str, str]:
    """
    ``{param_name: human description}`` straight from the groundhog docstring's own ``:param:``
    lines (e.g. "bulkunitweight" -> "Bulk unit weight of the sample"), for showing a real label
    next to a raw Python parameter name instead of the smashed-together identifier itself.
    """
    if not docstring:
        return {}
    labels = {}
    for key, raw in _PARAM_RE.findall(docstring):
        trailer = _PARAM_TRAILER_RE.search(raw)
        text = (raw[:trailer.start()] if trailer else raw).strip().rstrip(".")
        if text:
            labels[key] = text
    return labels


def _symbol_and_unit(text: str) -> Tuple[Optional[str], Optional[str]]:
    symbol = _SYMBOL_RE.search(text)
    unit = _UNIT_RE.search(text[symbol.end():] if symbol else text)
    unit_text = unit.group(1).strip() if unit else None
    return (symbol.group(1).strip() if symbol else None), (unit_text or None)


def extract_param_docs(docstring: Optional[str]) -> Dict[str, Dict[str, Optional[str]]]:
    """``{param_name: {"label", "symbol", "unit"}}`` from the docstring's ``:param:`` lines."""
    labels = extract_param_labels(docstring)
    docs = {}
    for key, raw in _PARAM_RE.findall(docstring or ""):
        symbol, unit = _symbol_and_unit(raw)
        docs[key] = {"label": labels.get(key), "symbol": symbol, "unit": unit}
    return docs


def extract_output_docs(docstring: Optional[str]) -> Dict[str, Dict[str, Optional[str]]]:
    """
    ``{output_key: {"label", "symbol"}}`` from the docstring's ``:returns:`` section, keyed by the
    exact result key. Two groundhog styles: a "- 'key [unit]': Label (:math:`sym`)" list, or a
    positional "Label (:math:`sym`) [:math:`unit`], ..." list paired with ``:rtype: ... keys [...]``.
    Callers look results up by exact key, so a docstring that lists other keys than the function
    returns labels nothing rather than the wrong output.
    """
    if not docstring:
        return {}
    docs = {}
    for key, rest in re.findall(r"^\s*-\s*'([^']+)'\s*:\s*(.*)$", docstring, re.MULTILINE):
        symbol, _ = _symbol_and_unit(rest)
        docs[key] = {"label": _PARAM_TRAILER_RE.split(rest)[0].strip().rstrip(".") or None, "symbol": symbol}
    returns = re.search(r"^:returns?:\s*(.+)$", docstring, re.MULTILINE)
    rtype = re.search(r"^:rtype:.*?keys\s*\[(.*)\]\s*$", docstring, re.MULTILINE)
    if returns and rtype and not docs:
        entries = [e for e in re.split(r"(?<=\])\s*,\s*", returns.group(1).strip()) if e]
        keys = re.findall(r"'([^']+)'", rtype.group(1))
        if len(entries) == len(keys):
            for key, entry in zip(keys, entries):
                symbol, _ = _symbol_and_unit(entry)
                docs[key] = {"label": _PARAM_TRAILER_RE.split(entry)[0].strip() or None, "symbol": symbol}
    return docs


def extract_summary(docstring: Optional[str]) -> Optional[str]:
    """The docstring's first sentence ("Calculates unit end bearing in sand according to API RP2 GEO.")."""
    if not docstring:
        return None
    paragraph = docstring.strip().split("\n\n")[0].replace("\n", " ").strip()
    if not paragraph or paragraph.startswith(":"):
        return None
    return re.split(r"(?<=\.)\s+(?=[A-Z])", paragraph)[0]


def extract_reference(docstring: Optional[str]) -> Optional[str]:
    """The docstring's "Reference - ..." paragraph, without the prefix, or None."""
    match = re.search(r"^References?\s*[-:]\s*(.+?)(?:\n\s*\n|\Z)", docstring or "", re.MULTILINE | re.DOTALL)
    return " ".join(match.group(1).split()) if match else None


def _normalise_symbol(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _formula_where(formula: str, quantities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    The given inputs and computed outputs that appear in the formula, for its "where" list: matched
    by their documented symbol, or (for an output with none, e.g. "Nq") by key against a formula
    symbol such as N_q. Only values that were actually supplied or returned are listed.
    """
    compact = formula.replace(" ", "")
    # normalised symbol -> the symbol as written in the formula ("nq" -> "N_q")
    tokens = {_normalise_symbol(t): t for t in _FORMULA_SYMBOL_RE.findall(formula) if not t.startswith("\\")}
    where, seen = [], set()
    for q in quantities:
        symbol = q.get("symbol")
        if symbol:
            matched = symbol.replace(" ", "") in compact
        else:
            symbol = tokens.get(_normalise_symbol(q["key"]))
            matched = symbol is not None
        if matched and q["key"] not in seen:
            seen.add(q["key"])
            where.append({"symbol": symbol, "label": q.get("label"), "value": q["value"], "unit": q.get("unit")})
    return where


def extract_formula(docstring: Optional[str]) -> Optional[str]:
    """
    The first `.. math::` block in a groundhog docstring, as raw LaTeX lines joined with `\\\\`,
    or None when the docstring has no such block. Never fabricates a formula.
    """
    if not docstring:
        return None
    match = _MATH_BLOCK_RE.search(docstring)
    if not match:
        return None
    lines = [ln.strip() for ln in textwrap.dedent(match.group(1)).splitlines() if ln.strip()]
    return " \\\\ ".join(lines) if lines else None


def _docstring_for(function_id: str) -> Optional[str]:
    from core.registry import registry
    func = registry.find_function(function_id)
    return inspect.getdoc(func) if func is not None else None


def explain_calculation(function_id: str, inputs: Optional[Dict[str, Any]],
                        results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    The deterministic part of a calculation explanation. Always available (no model needed), and
    adds no numbers or claims beyond what `TOOL_METADATA`, the docstring and `results` already say.

    ``steps`` is the worked derivation shown in the UI: objective, given inputs, governing equation
    with the value of each of its symbols, and the results. Built only from the docstring and the
    actual inputs/outputs; the equation is never evaluated here (groundhog already did that).
    """
    curated = curated_tool_metadata(function_id)
    meta = curated or get_tool_metadata(function_id)
    docstring = _docstring_for(function_id)
    formula = extract_formula(docstring)
    param_docs = extract_param_docs(docstring)
    output_docs = extract_output_docs(docstring)
    summary = extract_summary(docstring)
    reference = extract_reference(docstring)
    output_units = meta.get("output_units") or {}

    outputs, output_keys = [], []
    for k, v in (results or {}).items():
        if k.startswith("_") or k in ("warnings", "status") or v is None:
            continue
        doc = output_docs.get(k, {})
        if isinstance(v, dict):
            # A table of values (e.g. Eurocode 7 factors per action type): one row per entry,
            # "actions › Permanent unfavourable", instead of an unreadable object.
            for sub_key, sub_value in v.items():
                if sub_value is not None and not isinstance(sub_value, (dict, list)):
                    outputs.append({"key": f"{k} › {sub_key}", "label": f"{doc.get('label') or k} › {sub_key}",
                                    "symbol": None, "value": sub_value, "unit": None})
                    output_keys.append(f"{k} › {sub_key}")
            continue
        key_unit = _KEY_UNIT_RE.match(k)
        outputs.append({"key": k, "label": doc.get("label"), "symbol": doc.get("symbol"), "value": v,
                        "unit": output_units.get(k) or (key_unit.group(2) if key_unit else None) or None})
        output_keys.append(key_unit.group(1) if key_unit else k)
    inputs = [
        {"key": k, "label": param_docs.get(k, {}).get("label"), "symbol": param_docs.get(k, {}).get("symbol"),
         "value": v, "unit": param_docs.get(k, {}).get("unit")}
        for k, v in (inputs or {}).items()
    ]

    # Without a hand-written entry, the docstring's own description and reference say more than
    # the generic "Groundhog routine" text, and the generic assumption says nothing at all.
    method = meta.get("method") if curated else (summary or meta.get("method"))
    standard = meta.get("standard") if curated else (reference or meta.get("standard"))

    steps = []
    if summary and summary != method:  # otherwise the card's heading already says it
        steps.append({"title": "Objective", "text": summary})
    if inputs:
        steps.append({"title": "Given", "items": inputs})
    if formula:
        # Output keys without their "[unit]" suffix, so "Nq [-]" can match the symbol N_q.
        quantities = inputs + [{**o, "key": base} for o, base in zip(outputs, output_keys)]
        steps.append({"title": "Governing equation", "formula": formula,
                      "where": _formula_where(formula, quantities)})
    if outputs:
        steps.append({"title": "Result", "items": outputs})

    return {
        "tool_name": function_id,
        "method": method or f"Groundhog calculation ({function_id})",
        "standard": standard,
        "assumptions": meta.get("assumptions", []) if curated else [],
        "formula": formula,
        "reference": reference,
        "inputs": inputs,
        "outputs": outputs,
        "steps": steps,
    }


_NARRATION_SYSTEM_PROMPT = (
    "You explain a geotechnical calculation that has already been performed by Groundhog. You are "
    "given the method, formula, and the exact input and output values. In 2 or 3 short sentences of "
    "plain engineering language, walk through the calculation step by step: what is calculated, "
    "which inputs enter the formula, and what the result represents. Never introduce a number, "
    "formula, method or standard that is not given to you below. Never state that the result is "
    "'safe', 'correct' or 'acceptable' — only describe it."
)


def _format_value(value: Any, unit: Optional[str] = None) -> str:
    text = f"{value:.4g}" if isinstance(value, float) else str(value)
    return f"{text} {unit}" if unit else text


def build_narration_prompt(explanation: Dict[str, Any]) -> str:
    lines = [f"Method: {explanation['method']}"]
    if explanation.get("standard"):
        lines.append(f"Standard: {explanation['standard']}")
    if explanation.get("formula"):
        lines.append(f"Formula: {explanation['formula']}")
    where = next((st.get("where") for st in explanation.get("steps", []) if st.get("where")), None)
    if where:
        lines.append("Where: " + ", ".join(
            f"{w['symbol']}{f' ({w['label']})' if w.get('label') else ''} = {_format_value(w['value'], w.get('unit'))}"
            for w in where))
    if explanation.get("inputs"):
        lines.append("Inputs: " + ", ".join(
            f"{i.get('label') or i['key']}={_format_value(i['value'])}" for i in explanation["inputs"]
        ))
    # Yes/no flags (e.g. internal_friction: False) are switches, not results; models misread them.
    outputs = [o for o in explanation.get("outputs") or [] if not isinstance(o["value"], bool)]
    if outputs:
        lines.append("Outputs: " + ", ".join(
            f"{o.get('label') or o['key']}={_format_value(o['value'], o.get('unit'))}" for o in outputs
        ))
    return "\n".join(lines)


def narrate_explanation(explanation: Dict[str, Any], provider: Any) -> str:
    """Short plain-language narration from the local model, grounded strictly in `explanation`."""
    from core.geoai.model_provider import make_system_message, make_user_message
    from core.geoai.response_guard import clean_answer
    messages = [make_system_message(_NARRATION_SYSTEM_PROMPT),
                make_user_message(build_narration_prompt(explanation))]
    response = provider.generate(messages=messages, tools=None, temperature=0.1, max_tokens=150)
    return clean_answer(response.content).strip()
