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

# Sentence boundary: terminal punctuation followed by spaces, or a line break. A decimal
# point ("360.99") is never followed by whitespace, so numbers are not split.
_SENTENCE_BREAK = re.compile(r"((?<=[.!?])[ \t]+|\n+)")

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


def sentence_keys(text: Optional[str]) -> List[str]:
    """Normalized sentence keys (len > 20) usable to seed cross-turn repetition dedup."""
    if not text:
        return []
    pieces = _SENTENCE_BREAK.split(text)
    return [key for key in (_norm_sentence(pieces[i]) for i in range(0, len(pieces), 2)) if len(key) > 20]


def collapse_repetition(text: Optional[str], seed: Iterable[str] = ()) -> str:
    """
    Remove verbatim repeated sentences (keeping the first occurrence) and a trailing
    fragment that merely restarts an earlier sentence (typical of a max_tokens cut-off).
    ``seed`` pre-populates the seen set with sentences already shown in earlier turns, so a
    continuation that restates them (small models often do, see AnswerStreamCleaner) is dropped too.
    """
    if not text:
        return text or ""
    pieces = _SENTENCE_BREAK.split(text)  # [sentence, separator, sentence, separator, ...]
    seen: List[str] = list(seed)
    kept: List[List[str]] = []  # [sentence, separator]
    removed = False
    for i in range(0, len(pieces), 2):
        sentence = pieces[i]
        sep = pieces[i + 1] if i + 1 < len(pieces) else ""
        key = _norm_sentence(sentence)
        if len(key) > 20 and key in seen:
            removed = True
            if "\n" in sep and kept:  # keep paragraph structure of the surviving text
                kept[-1][1] = sep
            continue
        if key:
            seen.append(key)
        kept.append([sentence, sep])
    if removed and kept:
        tail = _norm_sentence(kept[-1][0])
        if tail and not re.search(r"[.!?]$", tail) and any(s.startswith(tail) for s in seen[:-1]):
            kept.pop()
    out = "".join(s + sep for s, sep in kept)
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


# Small models sometimes narrate "[Calculation record: ...]" in free text instead of
# actually calling a tool (AGENTS.md §5, §17: never fabricate a result). That colon form
# is not the real tag agent.py._calculation_record emits ("[Calculation record] {json}"),
# so it is matched here too and stripped the same way.
_RECORD_LINE = re.compile(r"^[ \t]*\[Calculation record[\]:].*$\n?", re.MULTILINE)
# A record echoed after other text on the same line ("... [Calculation record] {...}" or
# the fabricated "... [Calculation record: ..."); a plain mention of the tag with no
# payload marker following it is kept.
_RECORD_INLINE = re.compile(r"[ \t]*\[Calculation record\][ \t]*\{[^\n]*|[ \t]*\[Calculation record:[^\n]*")
_RECORD_INLINE_DONE = re.compile(
    r"[ \t]*\[Calculation record\][ \t]*\{[^\n]*(?=\n)|[ \t]*\[Calculation record:[^\n]*(?=\n)")
_RECORD_INLINE_OPEN = re.compile(r"\[Calculation record\][ \t]*(?:\{|$)|\[Calculation record:")
# Models copy JSON-escaped text from tool results ("EC7 §9.5"); show the character.
_UNICODE_ESCAPE = re.compile(r"\\u([0-9a-fA-F]{4})")


def strip_calculation_records(text: Optional[str]) -> str:
    """Remove echoed history records (agent.history_to_messages) from a model answer."""
    return _RECORD_INLINE.sub("", _RECORD_LINE.sub("", text or "")).strip()


def unescape_unicode(text: str) -> str:
    """Replace literal JSON escapes such as \\u00a7 with the character they encode."""
    return _UNICODE_ESCAPE.sub(lambda m: chr(int(m.group(1), 16)), text)


def clean_answer(text: Optional[str], tools_used: Optional[Iterable[Dict[str, Any]]] = None,
                  seed: Iterable[str] = ()) -> str:
    """Apply all guards to a final answer. ``seed``: see ``collapse_repetition``."""
    cleaned = collapse_repetition(strip_calculation_records(text), seed=seed)
    return unescape_unicode(fix_result_units(cleaned, tools_used or []))


# No trailing "]" here: a streamed prefix is checked against this probe before it is known
# whether the tag will resolve as the real "]" form or the fabricated ":" form (see above).
_RECORD_TAG = "[Calculation record"
_RECORD_LINE_DONE = re.compile(r"^[ \t]*\[Calculation record[\]:][^\n]*\n", re.MULTILINE)
_RECORD_LINE_START = re.compile(r"^[ \t]*\[Calculation record[\]:]", re.MULTILINE)


# Verbatim repeated sentences after which a streamed answer is treated as a loop and generation
# is stopped: nothing after the loop starts would be shown anyway (repeats are dropped).
LOOP_STOP_REPEATS = 3

TRUNCATION_NOTE = "\n\n*(Answer cut off at the output length limit. Ask GeoAI to continue.)*"


class AnswerStreamCleaner:
    """
    Incremental ``clean_answer`` for a streamed final answer: text is released one whole
    sentence at a time, with the same guards applied per sentence (verbatim repeats dropped,
    echoed [Calculation record] lines removed, result units corrected). <think> blocks are
    removed earlier by the model provider. ``feed`` returns the text that is safe to show
    now; ``flush`` returns the rest. ``seed`` (see ``collapse_repetition``) also drops verbatim
    restatements of sentences already shown in earlier turns, e.g. after the user says "continue".
    """

    def __init__(self, tools_used: Optional[Iterable[Dict[str, Any]]] = None, seed: Iterable[str] = ()):
        self._tools = list(tools_used or [])
        self._buf = ""
        self._seen: List[str] = list(seed)
        self._removed = False
        self._started = False
        self._last_sep = ""
        self._line_start = True  # the unconsumed buffer starts a new line
        self._pending_ws = ""
        self._repeats = 0

    @property
    def looping(self) -> bool:
        """True once the model has repeated LOOP_STOP_REPEATS sentences verbatim: stop generating."""
        return self._repeats >= LOOP_STOP_REPEATS

    def feed(self, delta: Optional[str]) -> str:
        self._buf += delta or ""
        return self._drain(final=False)

    def flush(self) -> str:
        return self._drain(final=True)

    def _emit(self, sentence: str, sep: str) -> str:
        # Trailing spaces are held back: clean_answer drops them before a line break and at the end.
        out = self._emit_sentence(sentence, sep)
        stripped = out.rstrip(" \t")
        trailing = out[len(stripped):]
        if not stripped:
            self._pending_ws += trailing
            return ""
        body = stripped if stripped.startswith("\n") else self._pending_ws + stripped
        self._pending_ws = trailing
        return body

    def _emit_sentence(self, sentence: str, sep: str) -> str:
        self._line_start = "\n" in sep
        key = _norm_sentence(sentence)
        if len(key) > 20 and key in self._seen:
            self._removed = True
            self._repeats += 1
            # keep paragraph structure of the surviving text
            return sep if ("\n" in sep and "\n" not in self._last_sep and self._started) else ""
        if key:
            self._seen.append(key)
        if "\n" in sep:
            sentence = sentence.rstrip(" \t")
        text = unescape_unicode(fix_result_units(sentence, self._tools))
        if not self._started:
            text = text.lstrip()
            if not text:
                return ""
            self._started = True
        self._last_sep = sep
        return text + sep

    def _drain(self, final: bool) -> str:
        buf = self._buf
        # Echoed calculation records are whole lines: drop complete ones, hold a partial one.
        # (a sentinel keeps "^" from matching at the buffer start when that is mid-line)
        lead = "" if self._line_start else "\x00"
        buf = (_RECORD_LINE if final else _RECORD_LINE_DONE).sub("", lead + buf)[len(lead):]
        buf = (_RECORD_INLINE if final else _RECORD_INLINE_DONE).sub("", buf)
        hold_from = len(buf)
        if not final:
            line_start = buf.rfind("\n") + 1
            line = buf[line_start:].lstrip()
            record = _RECORD_LINE_START.search(lead + buf)
            if record:
                hold_from = record.start() - len(lead)
            elif line and (line_start or self._line_start) and _RECORD_TAG.startswith(line[:len(_RECORD_TAG)]):
                hold_from = line_start
            # an inline record, or a tag that may still be arriving mid-line
            inline = _RECORD_INLINE_OPEN.search(buf)
            tag_at = buf.rfind("[")
            if inline:
                hold_from = min(hold_from, inline.start())
            elif tag_at >= 0 and _RECORD_TAG.startswith(buf[tag_at:]):
                hold_from = min(hold_from, tag_at)
        work, held = buf[:hold_from], buf[hold_from:]
        pieces = _SENTENCE_BREAK.split(work)  # [sentence, sep, sentence, sep, ..., rest]
        rest = pieces.pop()
        out: List[str] = []
        if final:
            for i in range(0, len(pieces), 2):
                out.append(self._emit(pieces[i], pieces[i + 1]))
            key = _norm_sentence(rest)
            restarts_earlier = (self._removed and key and not re.search(r"[.!?]$", key)
                                and any(s.startswith(key) for s in self._seen))
            if key and not restarts_earlier:
                out.append(self._emit(rest, ""))
            self._buf = ""
            return "".join(out).rstrip()
        if not rest and len(pieces) >= 2:
            # the buffer ends on a separator that may still grow ("\n" -> "\n\n"): hold that sentence
            sep = pieces.pop()
            rest = pieces.pop() + sep
        for i in range(0, len(pieces), 2):
            out.append(self._emit(pieces[i], pieces[i + 1]))
        self._buf = rest + held
        return "".join(out)
