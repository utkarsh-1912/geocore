"""
Per-turn outcome tracing for GeoAI chat reliability.

Every streamed chat turn is classified into one outcome and appended as a JSON line to
``geoai_turns.jsonl`` in the config directory (local only, size-capped). The classification is
derived from the events the agent emitted, so it adds no behaviour to the agent itself.

Author: Utkarsh Gupta
License: GPL v3
"""
import json
import logging
import re
import threading
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

TRACE_FILENAME = "geoai_turns.jsonl"
MAX_TRACE_BYTES = 2 * 1024 * 1024

# Outcomes. Everything except OK, TOOL_ERROR-with-answer and CANCELLED counts as a failed chat.
OK = "ok"
TOOL_ERROR = "tool_error"
EMPTY_ANSWER = "empty_answer"
MALFORMED_TOOL_CALL = "malformed_tool_call"
NO_TOOL_CALL = "no_tool_call_suspected"
TIMEOUT = "timeout"
CANCELLED = "cancelled"
ERROR = "error"
FAILURES = {EMPTY_ANSWER, MALFORMED_TOOL_CALL, NO_TOOL_CALL, TIMEOUT, ERROR}

EMPTY_ANSWER_MESSAGE = (
    "GeoAI did not produce an answer for that request. Nothing was calculated. "
    "Try rephrasing it, or state the calculation and its inputs with units "
    "(for example: \"bearing capacity, cohesion 20 kPa, friction angle 30 degrees, footing width 2 m\")."
)

_CALC_VERB = re.compile(r"\b(calculate|compute|determine|estimate|evaluate|find)\b", re.I)
_TOOL_MARKUP = re.compile(r"<tool_call>|<\|tool_call\|>|\[TOOL_CALLS\]|<function=|\"arguments\"\s*:", re.I)


def looks_like_calculation(prompt: str) -> bool:
    """A calculation request that should have produced a tool call (verb plus a number)."""
    return bool(_CALC_VERB.search(prompt or "") and re.search(r"\d", prompt or ""))


def classify_turn(prompt: str, events: List[Any], error: Optional[BaseException] = None) -> str:
    """Outcome of one turn from its emitted AgentStreamEvents (see agent.AgentStreamEvent)."""
    if error is not None:
        message = str(error)
        if type(error).__name__ == "GenerationCancelled":
            return TIMEOUT if "time limit" in message else CANCELLED
        return ERROR
    text = "".join(e.content or "" for e in events if e.type == "token")
    called = [e for e in events if e.type == "tool_start"]
    results = [e for e in events if e.type == "tool_result"]
    if not called:
        if not text.strip():
            return EMPTY_ANSWER
        if _TOOL_MARKUP.search(text):
            return MALFORMED_TOOL_CALL
        return NO_TOOL_CALL if looks_like_calculation(prompt) else OK
    if any((e.tool_result or {}).get("status") == "error" for e in results):
        return TOOL_ERROR
    return OK if text.strip() else EMPTY_ANSWER


_write_lock = threading.Lock()


def _trace_path():
    from core.paths import get_config_dir
    return get_config_dir() / TRACE_FILENAME


def record_turn(outcome: str, prompt: str, events: List[Any], started: float,
                model: Optional[Dict[str, Any]] = None, error: Optional[BaseException] = None) -> None:
    """Append one trace line; tracing must never break a chat, so failures are only logged."""
    try:
        stages = [e.content for e in events if e.type == "stage"]
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "outcome": outcome,
            "elapsed_s": round(time.monotonic() - started, 2),
            "prompt_chars": len(prompt or ""),
            "stages": stages,
            "tools": [e.tool_name for e in events if e.type == "tool_start"],
            "tool_errors": [e.tool_name for e in events
                            if e.type == "tool_result" and (e.tool_result or {}).get("status") == "error"],
            "answer_chars": sum(len(e.content or "") for e in events if e.type == "token"),
            "model": (model or {}).get("model_path"),
            "chat_format": (model or {}).get("chat_format"),
            "error": f"{type(error).__name__}: {error}" if error else None,
        }
        path = _trace_path()
        with _write_lock:
            if path.exists() and path.stat().st_size > MAX_TRACE_BYTES:
                path.replace(path.with_suffix(".jsonl.1"))
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning(f"GeoAI turn trace failed: {e}")
