"""
Deterministic post-processing of SLM answers.

Small local models occasionally degenerate after a tool round (the same sentence
repeated until max_tokens) or attach an invented unit to a Groundhog result
(e.g. "Qt is 360.99 kPa" when Qt is dimensionless). These guards repair the text
using only the tool's own structured output; they never add engineering content.

Author: Utkarsh Gupta
License: GPL v3
"""
import math
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .tool_metadata import get_tool_metadata

# Sentence = text up to terminal punctuation followed by whitespace/end.
_SENTENCE = re.compile(r"[^.!?\n]+(?:[.!?]+|$)|\n+")

# Units a model may (wrongly) attach to a numeric result. Longest alternatives first.
_UNIT_TOKEN = (
    r"kN/m(?:\^?[23]|[²³])|kN/m|MN/m(?:\^?2|²)|MN|kN|GPa|MPa|kPa|Pa|"
    r"m/s|mm|cm|m|%|degrees|degree|deg|°"
)
_NUMBER_WITH_UNIT = re.compile(
    r"(?<![\w.])(?P<num>-?\d+(?:\.\d+)?)(?P<sep>\s?)(?P<unit>" + _UNIT_TOKEN + r")(?![\w/^²³])"
)

_DIMENSIONLESS = {"-", "", "dimensionless", "none"}
_UNIT_ALIASES = {"deg": "deg", "degree": "deg", "degrees": "deg", "°": "deg",
                 "kn/m2": "kpa", "kn/m^2": "kpa", "kn/m²": "kpa"}


def _norm_sentence(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def collapse_repetition(text: Optional[str]) -> str:
    """
    Remove verbatim repeated sentences (keeping the first occurrence) and a trailing
    fragment that merely restarts an earlier sentence (typical of a max_tokens cut-off).
    """
    if not text:
        return text or ""
    parts = _SENTENCE.findall(text)
    seen: List[str] = []
    kept: List[str] = []
    removed = False
    for part in parts:
        if part.startswith("\n"):
            kept.append(part)
            continue
        key = _norm_sentence(part)
        if len(key) > 20 and key in seen:
            removed = True
            continue
        seen.append(key)
        kept.append(part)
    if removed and kept:
        tail = _norm_sentence(kept[-1])
        if tail and not re.search(r"[.!?]$", tail) and any(s.startswith(tail) for s in seen[:-1]):
            kept.pop()
    out = "".join(kept)
    out = re.sub(r"[ \t]+\n", "\n", out)
    return out.strip()


def _canon_unit(u: str) -> str:
    u = u.strip().lower()
    return _UNIT_ALIASES.get(u, u)


def _is_rounding_of(shown: str, value: float) -> bool:
    """True when `shown` is `value` rounded or truncated to its written precision."""
    try:
        n = float(shown)
    except ValueError:
        return False
    if n == 0 or not math.isfinite(value):
        return False
    digits = len(shown.split(".")[1]) if "." in shown else 0
    significant = len(re.sub(r"[^0-9]", "", shown).lstrip("0"))
    if significant < 2:  # "1 kPa" is too ambiguous to attribute to a result
        return False
    return abs(n - value) < 10 ** (-digits)


def _numeric_outputs(result: Dict[str, Any]) -> Dict[str, float]:
    return {k: float(v) for k, v in result.items()
            if not k.startswith("_") and isinstance(v, (int, float)) and not isinstance(v, bool)}


def _tool_outputs(tools_used: Iterable[Dict[str, Any]]) -> List[Tuple[Dict[str, float], Dict[str, str]]]:
    """(numeric outputs, declared output units) for every successful tool call."""
    out = []
    for t in tools_used or []:
        wrapper = t.get("result")
        if not isinstance(wrapper, dict) or wrapper.get("status") != "success":
            continue
        res = wrapper.get("result")
        if not isinstance(res, dict):
            continue
        prov = res.get("_provenance") if isinstance(res.get("_provenance"), dict) else {}
        units = prov.get("output_units") or get_tool_metadata(t.get("name", "")).get("output_units") or {}
        out.append((_numeric_outputs(res), dict(units)))
    return out


def fix_result_units(text: Optional[str], tools_used: Iterable[Dict[str, Any]]) -> str:
    """
    Where the text quotes a tool result value followed by a unit that disagrees with the
    unit the tool declared for that output, drop the unit (dimensionless outputs) or
    replace it with the declared unit. Only numbers that round-match a result are touched.
    """
    if not text:
        return text or ""
    outputs = _tool_outputs(tools_used)
    if not outputs:
        return text

    def _declared(num: str) -> Optional[str]:
        for values, units in outputs:
            for key, value in values.items():
                if key in units and _is_rounding_of(num, value):
                    return units[key]
        return None

    def _sub(m: "re.Match[str]") -> str:
        declared = _declared(m.group("num"))
        if declared is None:
            return m.group(0)
        if declared.strip().lower() in _DIMENSIONLESS:
            return m.group("num")
        if _canon_unit(declared) == _canon_unit(m.group("unit")):
            return m.group(0)
        sep = "" if declared == "%" else " "
        return f"{m.group('num')}{sep}{declared}"

    return _NUMBER_WITH_UNIT.sub(_sub, text)


_RECORD_LINE = re.compile(r"^[ \t]*\[Calculation record\].*$\n?", re.MULTILINE)


def strip_calculation_records(text: Optional[str]) -> str:
    """Remove echoed history records (agent.history_to_messages) from a model answer."""
    return _RECORD_LINE.sub("", text or "").strip()


def clean_answer(text: Optional[str], tools_used: Optional[Iterable[Dict[str, Any]]] = None) -> str:
    """Apply all guards to a final answer."""
    return fix_result_units(collapse_repetition(strip_calculation_records(text)), tools_used or [])
