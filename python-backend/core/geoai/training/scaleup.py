# Author: Utkarsh Gupta
# License: GPL v3
"""
Programmatic, registry-validated GeoAI dataset generator (AGENTS.md §19-§21).

Produces ~2,000-3,000 deterministic examples from the *registered* GeoAI tools:

* parameter names, required/optional status, bounds and canonical units are
  read from each tool's live ``input_model`` (no duplicated schemas);
* realistic values / phrasing come from ``tool_specs.py``;
* every expected tool call is executed through the GeoAI Tool Registry and
  the example is dropped if execution fails or returns non-finite values, so
  ground-truth arguments and results are correct by construction;
* every expected clarification / rejection is checked the other way round
  (the registry must refuse the incomplete / invalid / wrong-dimension call).

Covers all seven §20 categories, multi-turn trajectories (user -> tool call ->
real registry result -> grounded final answer with provenance and units),
stratified group-wise train/val/test splits (test never exported for SFT) and
ChatML JSONL compatible with TRL / Unsloth SFT (``messages`` + ``tools``).

CLI:  python -m core.geoai.training.scaleup --out core/geoai/training/data
"""

import argparse
import copy
import hashlib
import json
import math
import random
import re
from collections import Counter, defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.geoai.eval.example import CATEGORIES, EvalExample, save_examples_jsonl
from core.geoai.eval.scoring import clean_unit, default_registry, effective_arguments, field_unit, values_match
from core.geoai.exceptions import GeoAIValidationError
from core.geoai.system_prompt import build_system_prompt
from core.geoai.tool_metadata import get_tool_metadata
from core.geoai.training import tool_specs as S
from core.geoai.units import convert_unit, get_unit_dimension

GENERATOR_VERSION = "1.0.0"
DEFAULT_SEED = 20260926
DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "data"
FIXED_TIMESTAMP = "2026-01-01T00:00:00+00:00"
SPLITS = ("train", "val", "test")

_REJECT_WORDS = ["must", "invalid", "negative", "positive", "cannot", "between", "greater", "less",
                 "range", "physically", "not possible", "impossible", "check"]
_UNAVAILABLE_WORDS = ["not available", "not found", "no data", "isn't in", "is not in", "not in the",
                      "missing", "unavailable", "cannot find", "could not find", "couldn't find",
                      "no record", "don't have", "do not have", "not loaded"]
_NO_EVIDENCE = [["no ", "not find", "didn't find", "did not find", "none", "0 ", "zero", "no matching", "no relevant"],
                ["local", "document", "index", "library"]]


# =====================================================================
# Small formatting helpers
# =====================================================================

def fmt_num(v: float, decimals: int) -> str:
    if decimals <= 0:
        return str(int(round(v)))
    s = f"{v:.{decimals}f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def fmt_sig(v: float, sig: int = 4) -> str:
    if v == 0:
        return "0"
    d = max(0, sig - 1 - int(math.floor(math.log10(abs(v)))))
    return fmt_num(round(v, d), d)


def fmt_result(v: float) -> str:
    if v == 0:
        return "0"
    a = abs(v)
    if a < 1e-3 or a >= 1e6:
        return f"{v:.3e}"
    return fmt_sig(v, 4)


def _cap(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s


def _join(items: List[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def _stable_hash(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]


def _numeric_outputs(result: Dict[str, Any]) -> Dict[str, float]:
    return {k: float(v) for k, v in result.items()
            if not k.startswith("_") and isinstance(v, (int, float)) and not isinstance(v, bool)}


def _finite_result(result: Dict[str, Any]) -> bool:
    nums = _numeric_outputs(result)
    return bool(nums) and all(math.isfinite(v) for v in nums.values())


def _key_unit(key: str, tool: str, output_model) -> str:
    m = re.search(r"\[([^\]]+)\]\s*$", key)
    if m:
        return m.group(1).strip()
    units = get_tool_metadata(tool).get("output_units", {})
    if key in units:
        return units[key]
    if output_model is not None and key in getattr(output_model, "model_fields", {}):
        return field_unit(output_model.model_fields[key])
    return "-"


def _key_label(key: str) -> str:
    return re.sub(r"\s*\[[^\]]+\]\s*$", "", key).strip()


def _bounds(field_info) -> Dict[str, float]:
    out = {}
    for m in field_info.metadata or []:
        for attr in ("ge", "gt", "le", "lt"):
            if hasattr(m, attr) and getattr(m, attr) is not None:
                out[attr] = float(getattr(m, attr))
    return out


def _bounds_text(b: Dict[str, float]) -> str:
    parts = []
    if "gt" in b:
        parts.append(f"greater than {fmt_sig(b['gt'])}")
    if "ge" in b:
        parts.append(f"at least {fmt_sig(b['ge'])}")
    if "lt" in b:
        parts.append(f"less than {fmt_sig(b['lt'])}")
    if "le" in b:
        parts.append(f"at most {fmt_sig(b['le'])}")
    return " and ".join(parts) if parts else "within the tool's accepted range"


# =====================================================================
# Generator
# =====================================================================

@dataclass
class _Draft:
    example: EvalExample
    target_call: Optional[Dict[str, Any]] = None       # {"name", "arguments"} as trained (may carry unit strings)
    tool_message: Optional[Dict[str, Any]] = None       # exact agent-style tool result wrapper
    final_answer: Optional[str] = None
    final_eval: bool = False                            # also emit a final-answer eval turn


@dataclass
class GenerationReport:
    counts: Dict[str, Dict[str, int]] = field(default_factory=dict)
    dropped: Dict[str, int] = field(default_factory=dict)
    skipped_tools: Dict[str, str] = field(default_factory=dict)
    total: int = 0


class _Generator:
    def __init__(self, seed: int, registry):
        self.seed = seed
        self.rng = random.Random(seed)
        self.reg = registry
        self.drafts: List[_Draft] = []
        self.dropped: Counter = Counter()
        self.skipped: Dict[str, str] = {}
        self.specs: List[S.ToolSpec] = []
        for spec in S.TOOL_SPECS:
            tool = registry.get_tool(spec.tool)
            if tool is None:
                self.skipped[spec.tool] = "not registered"
                continue
            fields_ = tool.input_model.model_fields
            unknown = [p for p in spec.params if p not in fields_]
            if unknown:
                raise ValueError(f"tool_specs drift: {spec.tool} has no parameters {unknown}")
            missing_required = [n for n, f in fields_.items() if f.is_required() and n not in spec.params]
            if missing_required:
                self.skipped[spec.tool] = f"no phrasing for required params {missing_required}"
                continue
            self.specs.append(spec)

    # ---------------- schema helpers ----------------
    def _tool(self, name):
        return self.reg.get_tool(name)

    def _field(self, tool: str, p: str):
        return self._tool(tool).input_model.model_fields[p]

    def _required(self, spec: S.ToolSpec) -> List[str]:
        fields_ = self._tool(spec.tool).input_model.model_fields
        return [p for p in spec.params if fields_[p].is_required()]

    def _canon_unit(self, tool: str, p: str) -> str:
        return field_unit(self._field(tool, p))

    def _display_unit(self, spec: S.ToolSpec, p: str) -> str:
        ps = spec.params[p]
        u = ps.display_unit or self._canon_unit(spec.tool, p)
        return "" if u in ("-", "") else u

    def _with_unit(self, valstr: str, unit: str) -> str:
        if not unit:
            return valstr
        if unit == "deg":
            return valstr + self.rng.choice(["°", " degrees", " deg"])
        if unit == "kN/m3":
            return valstr + self.rng.choice([" kN/m3", " kN/m³"])
        return f"{valstr} {unit}"

    def _sample(self, spec: S.ToolSpec, include_optional: bool = True) -> Dict[str, float]:
        vals: Dict[str, float] = {}
        required = set(self._required(spec))
        for p, ps in spec.params.items():
            if p not in required and (not include_optional or self.rng.random() > ps.include_prob):
                continue
            if ps.choices:
                v = float(self.rng.choice(ps.choices))
            elif ps.integer:
                v = int(self.rng.randint(int(ps.low), int(ps.high)))
            else:
                v = round(self.rng.uniform(ps.low, ps.high), ps.decimals)
            vals[p] = v
        if spec.constrain:
            vals = spec.constrain(dict(vals))
        return vals

    def _value_str(self, spec: S.ToolSpec, p: str, v: float) -> str:
        ps = spec.params[p]
        return str(int(v)) if ps.integer else fmt_num(v, ps.decimals)

    def _phrase(self, spec: S.ToolSpec, p: str, shown: str, style: int) -> str:
        name = self.rng.choice(spec.params[p].names)
        if style == 0:
            return f"{name} of {shown}"
        if style == 1:
            return f"{name} = {shown}"
        return f"the {name} is {shown}"

    # ---------------- registry execution ----------------
    def _execute(self, tool: str, args: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            res = self.reg.invoke_tool(tool, dict(args))
        except GeoAIValidationError as e:
            return None, str(e)
        except Exception as e:  # Groundhog runtime failure
            return None, f"Execution failed: {e}"
        res = copy.deepcopy(res)
        if isinstance(res.get("_provenance"), dict):
            res["_provenance"]["timestamp_utc"] = FIXED_TIMESTAMP
        return res, None

    def _refused(self, tool: str, args: Dict[str, Any]) -> bool:
        res, err = self._execute(tool, args)
        return err is not None

    def _valid(self, tool: str, args: Dict[str, Any]) -> bool:
        res, err = self._execute(tool, args)
        return err is None and _finite_result(res)

    def _tool_msg(self, tool: str, result: Optional[Dict[str, Any]], error: Optional[str]) -> Dict[str, Any]:
        if error is not None:
            payload = {"status": "error", "tool_name": tool, "error": error}
        else:
            payload = {"status": "success", "tool_name": tool, "result": result}
        return {"role": "tool", "name": tool, "content": json.dumps(payload)}

    def _acceptable_tools(self, tool: str) -> List[str]:
        t = self._tool(tool)
        return sorted(n for n, o in self.reg._tools.items() if n != tool and o.input_model is t.input_model)

    # ---------------- final answers ----------------
    def _final_answer(self, spec: S.ToolSpec, args_shown: Dict[str, str], result: Dict[str, Any],
                      defaults_used: List[str]) -> Tuple[str, Dict[str, float], Dict[str, str]]:
        tool = self._tool(spec.tool)
        meta = get_tool_metadata(spec.tool)
        nums = _numeric_outputs(result)
        keys = [k for k in (spec.result_keys or nums.keys()) if k in nums][:4]
        lines = [f"Result from `{spec.tool}` ({meta.get('method', 'Groundhog routine')}):"]
        units: Dict[str, str] = {}
        values: Dict[str, float] = {}
        for k in keys:
            u = _key_unit(k, spec.tool, tool.output_model)
            units[k] = u
            values[k] = nums[k]
            lines.append(f"- {_key_label(k)} = {fmt_result(nums[k])}{'' if u in ('-', '') else ' ' + u}")
        text_nums = [v for k, v in result.items() if isinstance(v, str) and not k.startswith("_")]
        for s in text_nums[:1]:
            lines.append(f"- classification: {s}")
        inputs = ", ".join(f"{k} = {v}" for k, v in args_shown.items())
        lines.append(f"\nInputs used (as supplied): {inputs}.")
        if defaults_used:
            lines.append("Tool defaults applied for: " + ", ".join(defaults_used) + " (not supplied; please confirm they suit your case).")
        assumptions = meta.get("assumptions") or []
        basis = f"Basis: {meta.get('standard', 'Groundhog')}; calculated deterministically by Groundhog."
        if assumptions:
            basis += " Key assumptions: " + "; ".join(assumptions[:2]) + "."
        lines.append(basis)
        lines.append("These values depend on the supplied parameters and should be reviewed with engineering "
                     "judgement before being used in design.")
        return "\n".join(lines), values, units

    # ---------------- example factory ----------------
    def _add(self, *, category: str, stratum: str, template: str, prompt: Optional[str] = None,
             messages: Optional[List[Dict[str, Any]]] = None, expected_action: str,
             context: Optional[Dict[str, Any]] = None, **kw) -> _Draft:
        msgs = messages if messages is not None else [{"role": "user", "content": prompt}]
        target_call = kw.pop("target_call", None)
        tool_message = kw.pop("tool_message", None)
        final_answer = kw.pop("final_answer", None)
        final_eval = kw.pop("final_eval", False)
        ex = EvalExample(
            id="", category=category, expected_action=expected_action, messages=msgs,
            context=context, group=f"{category}|{stratum}|{template}", **kw,
        )
        d = _Draft(ex, target_call, tool_message, final_answer, final_eval)
        self.drafts.append(d)
        return d

    def _render_params(self, spec: S.ToolSpec, shown: Dict[str, str], eq: bool = False) -> Tuple[str, str]:
        style = 1 if eq else self.rng.randint(0, 1)
        items = [self._phrase(spec, p, s, style) for p, s in shown.items()]
        items_is = [self._phrase(spec, p, s, 2) for p, s in shown.items()]
        return _join(items), _join(items_is)

    def _frame(self, idx: int, spec: S.ToolSpec, shown: Dict[str, str]) -> str:
        task = self.rng.choice(spec.tasks)
        q = self.rng.choice(spec.questions)
        pl, pli = self._render_params(spec, shown, eq=(idx in (5,)))
        if not shown:
            return [f"{_cap(task)}.", f"{_cap(q)}?", f"Can you {task}?", f"Please {task} for me.",
                    f"{_cap(task)}.", f"I need to {task}.", f"Please {task}.", f"{_cap(q)}?"][idx]
        frames = [
            f"{_cap(task)} for {pl}.",
            f"{_cap(task)} with {pl}.",
            f"{_cap(q)} if {pli}?",
            f"Can you {task} given {pl}?",
            f"We have {pl}. {_cap(task)}.",
            f"I need to {task}. Inputs: {pl}.",
            f"Please {task} using {pl}.",
            f"{_cap(q)}? Data: {pl}.",
        ]
        return frames[idx]

    # =================================================================
    # Category builders
    # =================================================================
    def build_correct(self, per_tool: int):
        for spec in self.specs:
            for i in range(per_tool):
                idx = i % 8
                vals = self._sample(spec)
                shown = {p: self._with_unit(self._value_str(spec, p, v), self._display_unit(spec, p)) for p, v in vals.items()}
                prompt = self._frame(idx, spec, shown)
                self._tool_example("correct_request", spec, f"T{idx}", prompt, vals, shown,
                                   final_eval=(i % 3 == 0))
            # project-context vertical slice (§28)
            for i in range(max(4, per_tool // 4)):
                self._project_example(spec, i)

    def _tool_example(self, category, spec, template, prompt, vals, shown, *, context=None,
                      target_args=None, unit_trap=None, expected_values=None, final_eval=False):
        args = dict(target_args if target_args is not None else vals)
        result, err = self._execute(spec.tool, args)
        if err is not None or not _finite_result(result):
            self.dropped[f"{category}:execution_failed"] += 1
            return
        model = self._tool(spec.tool).input_model
        eff, eerr = effective_arguments(model, args)
        expected = {p: (expected_values or vals)[p] for p in vals}
        if eerr or any(not values_match(v, eff.get(p), rel_tol=1e-6) for p, v in expected.items()):
            self.dropped[f"{category}:normalisation_mismatch"] += 1
            return
        req = set(self._required(spec))
        defaults_used = [p for p, f in model.model_fields.items() if not f.is_required() and p not in vals and p in spec.params]
        answer, values, units = self._final_answer(spec, shown, result, defaults_used)
        self._add(
            category=category, stratum=spec.tool, template=template, prompt=prompt, context=context,
            expected_action="tool_call", expected_tool=spec.tool,
            acceptable_tools=self._acceptable_tools(spec.tool),
            expected_arguments={p: float(v) if not isinstance(v, int) else v for p, v in expected.items()},
            provided_params=sorted(vals.keys()), unit_trap=unit_trap,
            expected_result=_numeric_outputs(result), expected_result_values=values,
            metadata={"result_units": units, "required_params": sorted(req)},
            target_call={"name": spec.tool, "arguments": args},
            tool_message=self._tool_msg(spec.tool, result, None), final_answer=answer, final_eval=final_eval,
        )

    def _context_block(self, spec: S.ToolSpec, vals: Dict[str, float], label: str) -> str:
        rows = ["### ACTIVE PROJECT CONTEXT",
                f"- Project: {label}",
                "| Parameter | Value | Unit | Source |", "|---|---|---|---|"]
        sources = ["lab testing", "CPT interpretation", "design basis report", "borehole log"]
        for p, v in vals.items():
            u = self._display_unit(spec, p) or "-"
            rows.append(f"| {spec.params[p].names[0]} ({p}) | {self._value_str(spec, p, v)} | {u} | {self.rng.choice(sources)} |")
        return "\n".join(rows)

    def _project_example(self, spec: S.ToolSpec, i: int):
        vals = self._sample(spec)
        keys = list(vals.keys())
        self.rng.shuffle(keys)
        n_prompt = self.rng.randint(0, max(0, len(keys) - 1))
        in_prompt = {p: vals[p] for p in keys[:n_prompt]}
        in_ctx = {p: vals[p] for p in keys[n_prompt:]}
        label = self.rng.choice(["Harbour Quay Extension", "Riverside Embankment", "Northfield Substation",
                                 "Offshore Export Cable", "Canal Street Basement"])
        ctx = {"project_context": self._context_block(spec, in_ctx, label)}
        task = self.rng.choice(spec.tasks)
        shown_p = {p: self._with_unit(self._value_str(spec, p, v), self._display_unit(spec, p)) for p, v in in_prompt.items()}
        extra = f" with {self._render_params(spec, shown_p)[0]}" if shown_p else ""
        idx = i % 4
        prompt = [f"{_cap(task)} using the current project{extra}.",
                  f"Using the project data, {task}{extra}.",
                  f"Use the active project parameters to {task}{extra}.",
                  f"{_cap(task)} for the current project{extra}."][idx]
        shown_all = {p: self._with_unit(self._value_str(spec, p, v), self._display_unit(spec, p)) for p, v in vals.items()}
        self._tool_example("correct_request", spec, f"P{idx}", prompt, vals, shown_all, context=ctx, final_eval=False)

        # Same request where the project lacks one required parameter -> clarify.
        req = [p for p in self._required(spec) if p in in_ctx]
        if req:
            drop = self.rng.choice(req)
            ctx2_vals = {p: v for p, v in in_ctx.items() if p != drop}
            ctx2 = {"project_context": self._context_block(spec, ctx2_vals, label)}
            self._missing_example(spec, f"P{idx}", prompt, {**in_prompt, **ctx2_vals}, drop, context=ctx2)

    def _missing_example(self, spec, template, prompt, present_vals, drop, context=None):
        if not self._refused(spec.tool, present_vals):
            self.dropped["missing_data:registry_accepted_incomplete_call"] += 1
            return
        ps = spec.params[drop]
        unit = self._display_unit(spec, drop)
        names = list(ps.names) + [drop]
        task = spec.tasks[0]
        ref = (f"To {task} I also need the {ps.names[0]}"
               f"{' (in ' + unit + ')' if unit else ''}, which is not given. "
               f"Could you provide it? I won't assume a typical value because the result depends on it.")
        self._add(category="missing_data", stratum=spec.tool, template=template, prompt=prompt, context=context,
                  expected_action="clarify", expected_tool=spec.tool, provided_params=sorted(present_vals.keys()),
                  missing_params=[drop], clarify_keywords=[names], reference_response=ref)

    def build_missing(self, per_tool: int):
        for spec in self.specs:
            req = self._required(spec)
            for i in range(per_tool):
                drop = req[i % len(req)]
                vals = self._sample(spec, include_optional=self.rng.random() < 0.3)
                vals.pop(drop, None)
                shown = {p: self._with_unit(self._value_str(spec, p, v), self._display_unit(spec, p)) for p, v in vals.items()}
                idx = i % 8
                prompt = self._frame(idx, spec, shown)
                self._missing_example(spec, f"T{idx}", prompt, vals, drop)

    def build_units(self, per_tool: int):
        for spec in self.specs:
            convertible = [p for p, ps in spec.params.items() if ps.alt_units or ps.fraction]
            traps = [p for p, ps in spec.params.items() if ps.trap_units and p in self._required(spec)]
            if convertible:
                for i in range(per_tool):
                    self._convertible_example(spec, self.rng.choice(convertible), i % 8)
            if traps:
                for i in range(max(2, per_tool // 2)):
                    self._dimension_trap_example(spec, self.rng.choice(traps), i % 8)

    def _convertible_example(self, spec, p, idx):
        vals = self._sample(spec)
        if p not in vals:
            ps0 = spec.params[p]
            vals[p] = round(self.rng.uniform(ps0.low, ps0.high), ps0.decimals) if not ps0.choices else float(self.rng.choice(ps0.choices))
            if spec.constrain:
                vals = spec.constrain(vals)
        ps = spec.params[p]
        canon_unit = self._canon_unit(spec.tool, p)
        options = list(ps.alt_units) + (["%"] if ps.fraction else [])
        alt = self.rng.choice(options)
        if alt == "%":
            shown_num = fmt_num(vals[p] * 100.0, max(0, ps.decimals - 2))
            given = f"{shown_num}%"
            expected_v = float(shown_num) / 100.0
            target_v: Any = expected_v
        else:
            conv = convert_unit(vals[p], canon_unit if canon_unit != "-" else (ps.display_unit or "-"), alt)
            shown_num = fmt_sig(conv, 4)
            given = f"{shown_num} {alt}"
            src_unit = canon_unit if canon_unit != "-" else ps.display_unit
            expected_v = convert_unit(float(shown_num), alt, src_unit)
            # Prefer deterministic conversion by the registry (§16) when the schema supports it.
            eff, err = effective_arguments(self._tool(spec.tool).input_model, {p: given})
            unit_known = get_unit_dimension(canon_unit) is not None
            target_v = given if (unit_known and err is None and values_match(expected_v, eff.get(p), rel_tol=1e-6)) else expected_v
        expected_vals = dict(vals)
        expected_vals[p] = expected_v
        target_args = dict(vals)
        target_args[p] = target_v
        shown = {q: (given if q == p else self._with_unit(self._value_str(spec, q, v), self._display_unit(spec, q)))
                 for q, v in vals.items()}
        prompt = self._frame(idx, spec, shown)
        self._tool_example("wrong_units", spec, f"T{idx}", prompt, expected_vals, shown,
                           target_args=target_args, expected_values=expected_vals,
                           unit_trap={"param": p, "kind": "convertible", "given": given},
                           final_eval=(idx % 4 == 0))

    def _dimension_trap_example(self, spec, p, idx):
        vals = self._sample(spec)
        ps = spec.params[p]
        wrong = self.rng.choice(ps.trap_units)
        given = f"{self._value_str(spec, p, vals[p])} {wrong}"
        bad_args = dict(vals)
        bad_args[p] = given
        if not self._refused(spec.tool, bad_args):
            self.dropped["wrong_units:registry_accepted_wrong_dimension"] += 1
            return
        shown = {q: (given if q == p else self._with_unit(self._value_str(spec, q, v), self._display_unit(spec, q)))
                 for q, v in vals.items()}
        prompt = self._frame(idx, spec, shown)
        canon = self._canon_unit(spec.tool, p)
        ref = (f"Unit problem: {ps.names[0]} was given as {given}, but '{wrong}' is not a valid unit for this "
               f"quantity (expected {canon}). Did you mean {self._value_str(spec, p, vals[p])} {canon}? "
               f"Please confirm before I run the calculation.")
        self._add(category="wrong_units", stratum=spec.tool, template=f"D{idx}", prompt=prompt,
                  expected_action="clarify", expected_tool=spec.tool,
                  provided_params=sorted(q for q in vals if q != p),
                  unit_trap={"param": p, "kind": "dimension_mismatch", "given": given},
                  clarify_keywords=[list(ps.names) + [p], ["unit", wrong.lower(), canon.lower()]],
                  reference_response=ref)

    def build_conflicting(self, per_tool: int):
        for spec in self.specs:
            req = self._required(spec)
            for i in range(per_tool):
                p = req[i % len(req)]
                vals = self._sample(spec)
                ps = spec.params[p]
                v1 = vals[p]
                factor = 1 + self.rng.choice([-1, 1]) * self.rng.uniform(0.15, 0.35)
                v2 = int(round(v1 * factor)) if ps.integer else round(v1 * factor, ps.decimals)
                if v2 == v1:
                    continue
                alt_vals = dict(vals)
                alt_vals[p] = v2
                if not (self._valid(spec.tool, vals) and self._valid(spec.tool, alt_vals)):
                    self.dropped["conflicting_data:variant_invalid"] += 1
                    continue
                unit = self._display_unit(spec, p)
                s1 = self._with_unit(self._value_str(spec, p, v1), unit)
                s2 = self._with_unit(self._value_str(spec, p, v2), unit)
                src1, src2 = S.CONFLICT_SOURCES[i % len(S.CONFLICT_SOURCES)]
                others = {q: self._with_unit(self._value_str(spec, q, v), self._display_unit(spec, q))
                          for q, v in vals.items() if q != p}
                name = self.rng.choice(ps.names)
                task = self.rng.choice(spec.tasks)
                tail = f" with {self._render_params(spec, others)[0]}" if others else ""
                idx = i % 4
                prompt = [f"{_cap(src1)} gives {name} = {s1} but {src2} gives {s2}. {_cap(task)}{tail}.",
                          f"{_cap(task)}{tail}. Note: {src1} reports a {name} of {s1}, {src2} reports {s2}.",
                          f"We have two values for the {name}: {s1} ({src1}) and {s2} ({src2}). {_cap(task)}{tail}.",
                          f"{_cap(task)}{tail}; the {name} is {s1} according to {src1} and {s2} according to {src2}."][idx]
                ref = (f"The inputs conflict: {src1} gives {name} = {s1} whereas {src2} gives {s2}. "
                       f"Which value should I adopt? I can also run the calculation for both values to show the "
                       f"sensitivity, but I won't pick one silently.")
                self._add(category="conflicting_data", stratum=spec.tool, template=f"C{idx}", prompt=prompt,
                          expected_action="clarify", acceptable_actions=["synthesize"], expected_tool=spec.tool,
                          provided_params=sorted(q for q in vals if q != p),
                          clarify_keywords=[list(ps.names) + [p], ["which", "confirm", "both", "either", "sensitiv", "choose", "adopt"]],
                          reference_response=ref)
        # CPT vs borehole description conflicts (text synthesis)
        ids = [("CPT-01", "BH-02"), ("CPT-04", "BH-01"), ("SCPT-03", "BH-05"), ("CPT-11", "BH-07")]
        frames = [
            "{cpt} at {d} m indicates {c}, but borehole log {bh} at {d} m describes {b}. How should I reconcile this?",
            "The CPT ({cpt}) shows {c} at {d} m while {bh} logs {b} at the same depth. Which should I use for design?",
            "Conflict at {d} m: {cpt} suggests {c}, {bh} says {b}. What do you recommend?",
            "{bh} describes {b} at {d} m but {cpt} interprets {c}. Explain the discrepancy.",
        ]
        for fi, fr in enumerate(frames):
            for si, (c, b) in enumerate(S.SOIL_CONFLICTS):
                for k in range(2):
                    cpt, bh = ids[(si + k) % len(ids)]
                    d = fmt_num(self.rng.uniform(2.0, 18.0), 1)
                    prompt = fr.format(cpt=cpt, bh=bh, c=c, b=b, d=d)
                    ref = (f"These are conflicting pieces of project evidence, so neither should be adopted silently.\n"
                           f"- Project evidence: {cpt} interprets {c} at {d} m; {bh} logs {b} at {d} m.\n"
                           f"- Check the plan distance between {cpt} and {bh} and whether the stratigraphy could change laterally (channel infill, dipping layers).\n"
                           f"- Review the continuous CPT profile (qt, fs, u2) around {d} m and the borehole sample recovery and description quality.\n"
                           f"- If the discrepancy remains, consider an additional CPT or sampling next to {bh}.\n"
                           f"Until resolved, a design would need to consider both interpretations; engineering judgement is required.")
                    self._add(category="conflicting_data", stratum="cpt_vs_borehole", template=f"X{fi}", prompt=prompt,
                              expected_action="synthesize", acceptable_actions=["clarify"],
                              required_mentions=[["cpt", "cone"], ["borehole", "bh-", "log"],
                                                 ["verify", "check", "review", "confirm", "investigat", "additional"]],
                              reference_response=ref)

    def build_ambiguous(self):
        for pi, (base, kws) in enumerate(S.AMBIGUOUS_PROMPTS):
            for wi, wrap in enumerate(S.AMBIGUOUS_WRAPPERS):
                prompt = wrap.format(p=base)
                ref = ("I can help, but the request is under-specified. Could you tell me the "
                       + _join([g[0] for g in kws])
                       + " (and anything else specific to your case)? I will not assume these values.")
                self._add(category="ambiguous_request", stratum="vague", template=f"A{pi}", prompt=prompt,
                          expected_action="clarify", provided_params=[], clarify_keywords=kws, reference_response=ref)

    def build_research(self):
        tool = "search_local_documents"
        if self._tool(tool) is None:
            self.skipped[tool] = "not registered"
            return
        for ti, (topic, query) in enumerate(S.RESEARCH_TOPICS):
            for fi, fr in enumerate(S.RESEARCH_FRAMES):
                prompt = fr.format(topic=topic)
                args = {"query": query}
                if self._refused(tool, args):
                    self.dropped["research:query_invalid"] += 1
                    continue
                empty = {"query": query, "total_found": 0, "results": [],
                         "_provenance": {"tool_name": tool, "timestamp_utc": FIXED_TIMESTAMP,
                                         **{k: v for k, v in get_tool_metadata(tool).items() if k in ("method", "standard")}}}
                answer = (f"I searched the local document index for \"{query}\" and found no matching documents, "
                          f"so I cannot cite verified sources on {topic}.\n"
                          f"- Literature evidence: none retrieved.\n"
                          f"- Model interpretation (unverified): I can outline the general background if useful, clearly labelled as such.\n"
                          f"To get a grounded answer, index the relevant reports, papers or standards into GeoCore and ask again.")
                self._add(category="research", stratum=f"topic{ti}", template=f"R{ti}", prompt=prompt,
                          expected_action="tool_call", expected_tool=tool, expected_arguments={"query": query},
                          provided_params=["query", "top_k"],
                          target_call={"name": tool, "arguments": args},
                          tool_message={"role": "tool", "name": tool,
                                        "content": json.dumps({"status": "success", "tool_name": tool, "result": empty})},
                          final_answer=answer, final_eval=(fi % 2 == 0))

    def build_tool_failure(self):
        # (a) physically invalid inputs -> reject before calling a tool
        for spec in self.specs:
            invalid = [p for p, ps in spec.params.items() if ps.invalid_value is not None]
            for i, p in enumerate(invalid * 3):
                vals = self._sample(spec, include_optional=False)
                ps = spec.params[p]
                vals[p] = ps.invalid_value if i < len(invalid) else (
                    ps.invalid_value * self.rng.uniform(0.5, 2.0) if ps.invalid_value < 0 else ps.invalid_value + self.rng.uniform(0.05, 0.5))
                vals[p] = int(round(vals[p])) if ps.integer else round(vals[p], max(ps.decimals, 1))
                if not self._refused(spec.tool, vals):
                    self.dropped["tool_failure:registry_accepted_invalid_value"] += 1
                    continue
                shown = {q: self._with_unit(self._value_str(spec, q, v) if q != p else fmt_num(v, max(ps.decimals, 1)),
                                            self._display_unit(spec, q)) for q, v in vals.items()}
                idx = i % 8
                prompt = self._frame(idx, spec, shown)
                b = _bounds(self._field(spec.tool, p))
                ref = (f"The {ps.names[0]} of {shown[p]} is not physically valid (it must be {_bounds_text(b)}). "
                       f"Please check the value (sign convention, sensor zero offset or units) and resend it; "
                       f"I won't run the calculation with it or substitute a value myself.")
                self._add(category="tool_failure", stratum=spec.tool, template=f"T{idx}", prompt=prompt,
                          expected_action="reject", acceptable_actions=["clarify"], expected_tool=spec.tool,
                          provided_params=sorted(vals.keys()),
                          clarify_keywords=[list(ps.names) + [p], _REJECT_WORDS], reference_response=ref)
        # (b) requested project data not available
        frames = [
            "Classify the soil at {d} m in {id} from the current project.",
            "Use {id} to derive the undrained shear strength at {d} m.",
            "What does {id} show at {d} m depth?",
            "Normalise the SPT at {d} m in {id} for the current project.",
            "Interpret {id} at {d} m using the project data.",
        ]
        available = "| Sounding | Type | Depth range |\n|---|---|---|\n| CPT-01 | CPT | 0-18 m |\n| CPT-02 | CPT | 0-22 m |\n| BH-01 | Borehole/SPT | 0-30 m |"
        for fi, fr in enumerate(frames):
            for ii, sid in enumerate(S.MISSING_DATA_IDS):
                d = fmt_num(self.rng.uniform(2.0, 20.0), 1)
                with_ctx = ii % 2 == 0
                ctx = {"project_context": "### ACTIVE PROJECT CONTEXT\n- Project: Harbour Quay Extension\n" + available} if with_ctx else None
                prompt = fr.format(id=sid, d=d)
                ref = (f"{sid} is not available in the {'current project data (loaded: CPT-01, CPT-02, BH-01)' if with_ctx else 'loaded project data'}. "
                       f"Could you import it or provide the measured values at {d} m (e.g. qc and fs for a CPT, N for an SPT)? "
                       f"I won't estimate them.")
                self._add(category="tool_failure", stratum="data_unavailable", template=f"U{fi}", prompt=prompt, context=ctx,
                          expected_action="clarify", provided_params=[],
                          clarify_keywords=[[sid.lower()], _UNAVAILABLE_WORDS + ["provide", "import", "upload"]],
                          reference_response=ref)
        # (c) execution-time failures (trajectories: real registry error / NaN result -> grounded explanation)
        self._failure_trajectories()

    def _failure_trajectories(self):
        spec_map = {s.tool: s for s in self.specs}
        # Rankine with backfill slope steeper than phi' -> Groundhog returns NaN
        rk = spec_map.get("calculate_earth_pressure_rankine")
        if rk:
            for i in range(24):
                phi = float(self.rng.randint(22, 32))
                beta = float(min(44, phi + self.rng.randint(3, 10)))
                args = {"phi_eff": phi, "top_angle": beta}
                result, err = self._execute(rk.tool, args)
                if err is not None or _finite_result(result):
                    self.dropped["tool_failure:no_nan_result"] += 1
                    continue
                shown = {"phi_eff": self._with_unit(fmt_num(phi, 0), "deg"), "top_angle": self._with_unit(fmt_num(beta, 0), "deg")}
                prompt = self._frame(i % 8, rk, shown)
                answer = (f"The Rankine calculation did not return a valid result (the coefficients came back as NaN). "
                          f"Rankine's solution for a sloping backfill requires the backfill slope angle ({fmt_num(beta, 0)} deg) "
                          f"to be no greater than the friction angle ({fmt_num(phi, 0)} deg); here it is steeper, so the retained slope "
                          f"would not be stable on its own. Please check the slope angle and friction angle, or consider a "
                          f"different method (e.g. a slope stability or trial-wedge analysis). I have not reported any Ka/Kp values.")
                self._add(category="tool_failure", stratum="rankine_nan", template=f"T{i % 8}", prompt=prompt,
                          expected_action="tool_call", expected_tool=rk.tool, expected_arguments=args,
                          provided_params=sorted(args), target_call={"name": rk.tool, "arguments": args},
                          tool_message=self._tool_msg(rk.tool, result, None), final_answer=answer, final_eval=True,
                          metadata={"final_required_mentions": [["nan", "not a number", "no valid", "not return a valid", "invalid", "undefined", "could not", "did not return"],
                                                                ["slope", "backfill"]]})
        # Values outside the tool's accepted range -> registry validation error
        cases = [("derive_cpt_parameters", "Nkt", (32, 45)), ("normalize_spt_test", "energy_ratio", (1.05, 1.4))]
        for tool, p, (lo, hi) in cases:
            spec = spec_map.get(tool)
            if not spec:
                continue
            for i in range(16):
                vals = self._sample(spec, include_optional=False)
                vals[p] = float(self.rng.randint(int(lo), int(hi))) if hi > 5 else round(self.rng.uniform(lo, hi), 2)
                result, err = self._execute(tool, vals)
                if err is None:
                    self.dropped["tool_failure:registry_accepted_out_of_range"] += 1
                    continue
                shown = {q: self._with_unit(self._value_str(spec, q, v), self._display_unit(spec, q)) for q, v in vals.items()}
                prompt = self._frame(i % 8, spec, shown)
                ps = spec.params[p]
                b = _bounds(self._field(tool, p))
                answer = (f"The calculation was not run: the tool rejected the input because {ps.names[0]} = {shown[p]} is "
                          f"outside its accepted range (it must be {_bounds_text(b)}). Please confirm the value "
                          f"(for example whether it was entered in the intended units); I won't substitute a different "
                          f"{ps.names[0]} myself.")
                self._add(category="tool_failure", stratum=f"{tool}_range", template=f"T{i % 8}", prompt=prompt,
                          expected_action="tool_call", expected_tool=tool, expected_arguments=dict(vals),
                          provided_params=sorted(vals), target_call={"name": tool, "arguments": vals},
                          tool_message=self._tool_msg(tool, None, err), final_answer=answer, final_eval=True,
                          metadata={"final_required_mentions": [list(ps.names) + [p],
                                                                ["range", "must be", "at most", "at least", "outside", "exceed", "not run", "rejected"]]})


# =====================================================================
# Assembly: final-answer turns, dedupe, ids, splits
# =====================================================================

def _assistant_tool_call_msg(call: Dict[str, Any], call_id: str) -> Dict[str, Any]:
    return {"role": "assistant", "content": "",
            "tool_calls": [{"id": call_id, "type": "function",
                            "function": {"name": call["name"], "arguments": call["arguments"]}}]}


def _final_turn(d: _Draft) -> EvalExample:
    ex = d.example
    call_id = f"call_{ex.id}"
    tool_msg = dict(d.tool_message)
    tool_msg["tool_call_id"] = call_id
    msgs = list(ex.messages) + [_assistant_tool_call_msg(d.target_call, call_id), tool_msg]
    meta = dict(ex.metadata or {})
    req_mentions = meta.pop("final_required_mentions", None)
    success = json.loads(d.tool_message["content"]).get("status") == "success"
    values = ex.expected_result_values if (success and req_mentions is None and ex.category != "research") else None
    if ex.category == "research":
        req_mentions = _NO_EVIDENCE
    return EvalExample(
        id=ex.id + "__final", category=ex.category, expected_action="synthesize", messages=msgs,
        turn_type="final_answer", context=ex.context, expected_tool=None,
        expected_result_values=values, required_mentions=req_mentions or [],
        reference_response=d.final_answer, split=ex.split, source=ex.source, group=ex.group,
        metadata={"result_units": meta.get("result_units", {}), "parent_id": ex.id},
    )


def _dedupe_key(ex: EvalExample) -> str:
    ctx = json.dumps(ex.context, sort_keys=True) if ex.context else ""
    return ex.turn_type + "|" + re.sub(r"\s+", " ", ex.user_prompt.strip().lower()) + "|" + ctx


def assign_splits(examples: List[EvalExample], seed: int, test_frac: float = 0.12, val_frac: float = 0.10) -> None:
    """Group-wise stratified split: all examples of a template group land in one split."""
    strata: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    for ex in examples:
        cat, stratum, _tmpl = ex.group.split("|", 2)
        if ex.group not in strata[(cat, stratum)]:
            strata[(cat, stratum)].append(ex.group)
    group_split: Dict[str, str] = {}
    for (cat, stratum), groups in sorted(strata.items()):
        groups = sorted(groups)
        random.Random(f"{seed}|{cat}|{stratum}").shuffle(groups)
        n = len(groups)
        if n >= 5:
            n_test = max(1, round(n * test_frac))
            n_val = max(1, round(n * val_frac))
        elif n >= 2:
            n_test, n_val = 1, 0
        else:
            n_test, n_val = 0, 0
        for i, g in enumerate(groups):
            group_split[g] = "test" if i < n_test else ("val" if i < n_test + n_val else "train")
    # Strata with a single group: distribute whole groups by hash so each category still gets test coverage.
    for ex in examples:
        split = group_split.get(ex.group)
        if split is None or (len(strata[tuple(ex.group.split("|", 2)[:2])]) == 1):
            h = int(_stable_hash(f"{seed}|{ex.group}"), 16) % 100
            split = "test" if h < test_frac * 100 else ("val" if h < (test_frac + val_frac) * 100 else "train")
            group_split[ex.group] = split
        ex.split = split


def build_dataset(seed: int = DEFAULT_SEED, registry=None, per_tool: int = 30) -> Tuple[List[EvalExample], List[_Draft], GenerationReport]:
    """
    Build the full generated dataset (decision + final-answer turns) with splits assigned.

    Returns (examples, drafts, report). ``drafts`` carry the SFT trajectories for
    decision turns (tool call, real tool result, final answer).
    """
    reg = registry if registry is not None else default_registry()
    g = _Generator(seed, reg)
    g.build_correct(per_tool)
    g.build_missing(max(6, per_tool // 3))
    g.build_units(max(6, per_tool // 3))
    g.build_conflicting(max(4, per_tool // 6))
    g.build_ambiguous()
    g.build_research()
    g.build_tool_failure()

    # dedupe decision turns (first occurrence wins; generation order is deterministic)
    seen = set()
    drafts: List[_Draft] = []
    for d in g.drafts:
        k = _dedupe_key(d.example)
        if k in seen:
            g.dropped["duplicate"] += 1
            continue
        seen.add(k)
        drafts.append(d)
    for d in drafts:
        d.example.id = f"{d.example.category}-{_stable_hash(_dedupe_key(d.example))}"
    assign_splits([d.example for d in drafts], seed)

    examples: List[EvalExample] = []
    for d in drafts:
        # Trajectory-only failure decisions are trained on but not evaluated as decisions.
        if not (d.example.category == "tool_failure" and d.target_call is not None):
            examples.append(d.example)
        if d.final_eval and d.target_call and d.tool_message and d.final_answer:
            examples.append(_final_turn(d))

    report = GenerationReport(dropped=dict(g.dropped), skipped_tools=dict(g.skipped), total=len(examples))
    counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for ex in examples:
        counts[ex.category][ex.split] += 1
    report.counts = {c: dict(v) for c, v in counts.items()}
    return examples, drafts, report


# =====================================================================
# Gold set (existing hand-written examples)
# =====================================================================

_GOLD_KEYWORDS = {
    "ambiguous_01_pile": [["diameter", "geometry", "length"], ["method", "lcpc", "api", "cpt"]],
    "ambiguous_02_settlement": [["dimension", "width", "size"], ["load", "pressure"], ["compressib", "modulus", "cc", "mv"]],
    "missing_01_bearing_capacity": [["friction angle", "phi", "su", "shear strength", "cohesion"], ["unit weight", "gamma"]],
    "missing_02_retaining_wall": [["friction angle", "phi"]],
    "unit_trap_01_pressure": [["unit weight", "gamma"], ["unit", "kpa", "kn/m"]],
    "failure_01_invalid_cpt": [["qc", "cone", "tip resistance"], ["positive", "negative", "must", "invalid"]],
}


def gold_examples() -> List[EvalExample]:
    from core.geoai.training.dataset_generator import build_core_training_examples
    out: List[EvalExample] = []
    for g in build_core_training_examples():
        ex = EvalExample(
            id=f"gold-{g.id}", category=g.category, expected_action=g.expected_action,
            messages=[{"role": "user", "content": g.user_prompt}], context=g.context,
            expected_tool=g.expected_tool, expected_arguments=g.expected_arguments,
            provided_params=sorted(g.expected_arguments) if g.expected_arguments else None,
            clarify_keywords=_GOLD_KEYWORDS.get(g.id, []), reference_response=g.expected_response,
            split="gold", source="gold", group=f"gold|{g.id}|0",
        )
        if g.id == "unit_trap_01_pressure":
            ex.unit_trap = {"param": "gamma", "kind": "dimension_mismatch", "given": "19 kPa"}
            ex.expected_tool = "calculate_gmax_from_shear_wave_velocity"
        if g.category == "conflicting_data":
            ex.acceptable_actions = ["clarify"]
            ex.required_mentions = [["cpt", "cone"], ["borehole", "bh-"]]
        if g.expected_action == "reject":
            ex.acceptable_actions = ["clarify"]
        out.append(ex)
    return out


# =====================================================================
# SFT export (TRL / Unsloth ChatML: messages + tools)
# =====================================================================

@contextmanager
def _cached_tool_definitions():
    """Memoise the (expensive, static) tool schema list while exporting."""
    import core.geoai.tool_selector as ts

    class _RegistryView:
        def __init__(self, reg):
            self._reg = reg
            self._listing = reg.list_tools()

        def list_tools(self):
            return self._listing

        def __getattr__(self, item):
            return getattr(self._reg, item)

    original_defs, original_reg = ts.generate_openai_tool_definitions, ts.tool_registry
    cache = original_defs()
    ts.generate_openai_tool_definitions = lambda: cache
    ts.tool_registry = _RegistryView(original_reg)
    try:
        yield
    finally:
        ts.generate_openai_tool_definitions = original_defs
        ts.tool_registry = original_reg


def _tools_for(prompt: str, context: Optional[Dict[str, Any]], expected_tool: Optional[str], all_defs: Dict[str, Any]) -> Tuple[List[dict], bool]:
    from core.geoai.tool_selector import format_tools_for_prompt, select_relevant_tools
    tools = select_relevant_tools(prompt, context)
    names = [t["function"]["name"] for t in tools]
    miss = bool(expected_tool) and expected_tool not in names
    if miss and expected_tool in all_defs:
        tools = format_tools_for_prompt([all_defs[expected_tool]]) + tools[:19]
    return tools, miss


def sft_record(d: _Draft, all_defs: Dict[str, Any]) -> Dict[str, Any]:
    ex = d.example
    msgs: List[Dict[str, Any]] = [{"role": "system", "content": build_system_prompt(ex.context)}]
    msgs += [dict(m) for m in ex.messages]
    if d.target_call is not None:
        call_id = f"call_{ex.id}"
        msgs.append(_assistant_tool_call_msg(d.target_call, call_id))
        tm = dict(d.tool_message)
        tm["tool_call_id"] = call_id
        msgs.append(tm)
        msgs.append({"role": "assistant", "content": d.final_answer})
    else:
        msgs.append({"role": "assistant", "content": ex.reference_response or ""})
    tools, miss = _tools_for(ex.user_prompt, ex.context, ex.expected_tool, all_defs)
    return {"id": ex.id, "category": ex.category, "split": ex.split, "messages": msgs, "tools": tools,
            "selector_missed_expected_tool": miss}


def export_dataset(out_dir: Path = DEFAULT_DATA_DIR, seed: int = DEFAULT_SEED, per_tool: int = 30) -> Dict[str, Any]:
    """Write eval_{train,val,test,gold}.jsonl, sft_{train,val}.jsonl and manifest.json."""
    from core.geoai.slm_schema_generator import generate_openai_tool_definitions
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    examples, drafts, report = build_dataset(seed=seed, per_tool=per_tool)
    gold = gold_examples()

    files: Dict[str, int] = {}
    for split in SPLITS:
        files[f"eval_{split}.jsonl"] = save_examples_jsonl([e for e in examples if e.split == split], out_dir / f"eval_{split}.jsonl")
    files["eval_gold.jsonl"] = save_examples_jsonl(gold, out_dir / "eval_gold.jsonl")

    selector_misses = 0
    with _cached_tool_definitions():
        all_defs = {t["function"]["name"]: t for t in generate_openai_tool_definitions()}
        for split in ("train", "val"):  # test (and gold) are held out: never exported for training
            n = 0
            with open(out_dir / f"sft_{split}.jsonl", "w", encoding="utf-8") as f:
                for d in drafts:
                    if d.example.split != split:
                        continue
                    rec = sft_record(d, all_defs)
                    selector_misses += int(rec["selector_missed_expected_tool"])
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    n += 1
            files[f"sft_{split}.jsonl"] = n

    manifest = {
        "generator_version": GENERATOR_VERSION, "seed": seed, "per_tool": per_tool,
        "files": files, "counts_by_category_split": report.counts,
        "dropped": report.dropped, "skipped_tools": report.skipped_tools,
        "selector_missed_expected_tool": selector_misses,
        "tools_covered": sorted({e.expected_tool for e in examples if e.expected_tool}),
        "format": "TRL/Unsloth conversational SFT: {'messages': [...], 'tools': [OpenAI function schemas]}; "
                  "tool_call arguments are JSON objects (not strings).",
    }
    with open(out_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    return manifest


def load_split(split: str, data_dir: Path = DEFAULT_DATA_DIR, seed: int = DEFAULT_SEED) -> List[EvalExample]:
    """Load an eval split from disk if exported, otherwise regenerate it deterministically."""
    from core.geoai.eval.example import load_examples_jsonl
    if split == "gold":
        return gold_examples()
    path = Path(data_dir) / f"eval_{split}.jsonl"
    if path.exists():
        return load_examples_jsonl(path)
    examples, _, _ = build_dataset(seed=seed)
    return [e for e in examples if e.split == split]


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate the registry-validated GeoAI SFT/eval dataset.")
    ap.add_argument("--out", type=Path, default=DEFAULT_DATA_DIR)
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--per-tool", type=int, default=30)
    args = ap.parse_args(argv)
    manifest = export_dataset(args.out, seed=args.seed, per_tool=args.per_tool)
    print(json.dumps({k: manifest[k] for k in ("files", "counts_by_category_split", "dropped", "skipped_tools",
                                                "selector_missed_expected_tool")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
