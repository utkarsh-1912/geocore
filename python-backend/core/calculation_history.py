# Author: Utkarsh Gupta
# License: GPL v3
"""
Persistent audit trail of calculations run through the main calculation UI (``/api/execute``).

Every successful calculation is recorded here regardless of which calculator was used, so the
project has a durable history of what was run, with what inputs, and when — independent of
``core/geoai/data_access.py``'s ``ProjectContext.calculation_history``, which is an in-memory,
per-session list built for the GeoAI chat agent's own prompt context (AGENTS.md SS15: conversation
memory, project memory and calculation history are kept separate).

Stored as a project setting (``core/state.py``'s existing atomic, thread-safe JSON store) rather
than a new file format, so there is one way saved project data is persisted, not two.
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

SETTING_KEY = "calculation_history"
#: Oldest entries are dropped past this count so the project settings file never grows unbounded.
MAX_ENTRIES = 500


def _compact_value(v: Any) -> Any:
    if isinstance(v, float):
        return float(f"{v:.4g}")
    if isinstance(v, (int, str, bool)) or v is None:
        return v
    if isinstance(v, list):
        return f"[{len(v)} items]" if len(v) > 8 else [_compact_value(x) for x in v]
    if isinstance(v, dict):
        return f"{{{len(v)} keys}}" if len(v) > 8 else {k: _compact_value(x) for k, x in v.items()}
    return str(v)


def _compact_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """A short, JSON-safe summary of a calculation result: scalars kept, large structures sized."""
    return {
        k: _compact_value(v)
        for k, v in result.items()
        if not k.startswith("_") and k not in ("warnings", "status")
    }


def record_calculation(function_id: str, args: Optional[Dict[str, Any]], result: Dict[str, Any]) -> None:
    """
    Appends one entry to the project's calculation history. Never raises: a history-recording
    failure must not break the calculation response that triggered it.
    """
    try:
        from core.state import state_manager
        entry = {
            "id": uuid.uuid4().hex,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "function_id": function_id,
            "inputs": _compact_result(args or {}),
            "outputs": _compact_result(result or {}),
            # Sign-off: a calculation stays "unreviewed" until someone explicitly marks it
            # checked (see mark_reviewed). Single-user app: this records that a check happened
            # and when, not who — there's no second account to attribute it to.
            "reviewed": False,
            "reviewed_at": None,
            "reviewed_note": None,
        }
        history = list(state_manager.get_project_setting(SETTING_KEY, []))
        history.append(entry)
        if len(history) > MAX_ENTRIES:
            history = history[-MAX_ENTRIES:]
        state_manager.set_project_setting(SETTING_KEY, history)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to record calculation history for {function_id}: {e}")


def list_calculation_history(limit: Optional[int] = 50) -> List[Dict[str, Any]]:
    """Most recent entries first."""
    from core.state import state_manager
    history = list(state_manager.get_project_setting(SETTING_KEY, []))
    history.reverse()
    return history[:limit] if limit else history


def clear_calculation_history() -> None:
    from core.state import state_manager
    state_manager.set_project_setting(SETTING_KEY, None)


def mark_reviewed(entry_id: str, reviewed: bool = True, note: Optional[str] = None) -> bool:
    """Marks (or unmarks) one entry as checked. Returns False when ``entry_id`` doesn't exist."""
    from core.state import state_manager
    history = list(state_manager.get_project_setting(SETTING_KEY, []))
    for entry in history:
        if entry.get("id") == entry_id:
            entry["reviewed"] = reviewed
            entry["reviewed_at"] = datetime.now(timezone.utc).isoformat() if reviewed else None
            entry["reviewed_note"] = note if reviewed else None
            state_manager.set_project_setting(SETTING_KEY, history)
            return True
    return False
