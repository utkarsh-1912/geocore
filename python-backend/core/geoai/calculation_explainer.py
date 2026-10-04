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
from typing import Any, Dict, List, Optional

from core.geoai.tool_metadata import get_tool_metadata

_MATH_BLOCK_RE = re.compile(r"\.\. math::\n((?:[ \t]+\S.*\n?)+)")


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
    """
    meta = get_tool_metadata(function_id)
    formula = extract_formula(_docstring_for(function_id))
    output_units = meta.get("output_units") or {}
    outputs = [
        {"key": k, "value": v, "unit": output_units.get(k)}
        for k, v in (results or {}).items()
        if not k.startswith("_") and k not in ("warnings", "status") and v is not None
    ]
    return {
        "tool_name": function_id,
        "method": meta.get("method", f"Groundhog calculation ({function_id})"),
        "standard": meta.get("standard"),
        "assumptions": meta.get("assumptions", []),
        "formula": formula,
        "inputs": inputs or {},
        "outputs": outputs,
    }


_NARRATION_SYSTEM_PROMPT = (
    "You explain a geotechnical calculation that has already been performed by Groundhog. You are "
    "given the method, formula, and the exact input and output values. Write at most 2 short "
    "sentences in plain engineering language narrating what was computed. Never introduce a number, "
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
    if explanation.get("inputs"):
        lines.append("Inputs: " + ", ".join(f"{k}={_format_value(v)}" for k, v in explanation["inputs"].items()))
    if explanation.get("outputs"):
        lines.append("Outputs: " + ", ".join(
            f"{o['key']}={_format_value(o['value'], o.get('unit'))}" for o in explanation["outputs"]
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
