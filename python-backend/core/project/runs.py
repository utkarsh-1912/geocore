# Author: Utkarsh Gupta
# License: GPL v3
"""
Calculation runs in the project, the parameters they derive, and whether they are still current.

``record_run`` stores a finished calculation as the app received it (figures dropped: they are large and are
re-created by running again), its scalar results as derived parameters (named through the result envelope, so a
later form can be pre-filled from them), and which project values it consumed (``input_sources``, from prefill).

A run is stale when a value it consumed has changed or disappeared since (e.g. the soil profile was edited and the
project re-synced), or when a run it consumed is itself stale. Staleness is computed when asked, never stored.
"""
import json
import time
from typing import Any, Dict, List, Optional

from core.project.store import connect, row_dict

_FIGURE_KEYS = {"plots", "plot", "image", "figure", "Plot", "fig"}


def _compact(results: Any) -> Any:
    """The response without figures (a run report lists values and tables; figures come from re-running)."""
    if isinstance(results, dict):
        return {k: _compact(v) for k, v in results.items()
                if k not in _FIGURE_KEYS and not (isinstance(v, dict) and v.get("type") in ("plotly", "image"))}
    if isinstance(results, list):
        return [_compact(v) for v in results]
    return results


def record_run(function_id: str, inputs: Dict[str, Any], results: Any,
               input_sources: Optional[Dict[str, Dict[str, Any]]] = None,
               location_id: Optional[int] = None, note: Optional[str] = None) -> int:
    from core.catalogue import effective_status, find_method
    from core.catalogue.envelope import extract_values
    from core.project.ground import _quantity_of
    hit = find_method(function_id)
    now = time.time()
    with connect() as db:
        run_id = db.execute(
            "INSERT INTO runs (function_id, calculation, method, status, inputs_json, results_json, created_at, location_id, note) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (function_id, hit["calculation"]["id"] if hit else None, hit["method"]["id"] if hit else None,
             effective_status(hit["method"]) if hit else None, json.dumps(inputs, default=str),
             json.dumps(_compact(results), default=str), now, location_id, note)).lastrowid
        for name, src in (input_sources or {}).items():
            for consumed in src.get("inputs") or [{"param_key": None, "value": None}]:
                db.execute("INSERT INTO run_inputs (run_id, name, value, param_key, source) VALUES (?,?,?,?,?)",
                           (run_id, name, consumed.get("value"), consumed.get("param_key"), src.get("source")))
        label = hit["method"]["label"] if hit else function_id
        for v in extract_values(function_id, results):
            if isinstance(v["value"], bool) or not isinstance(v["value"], (int, float)):
                continue
            db.execute("INSERT INTO parameters (location_id, layer_id, column_name, quantity, value, unit, source_kind, "
                       "source_ref, param_key, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                       (location_id, None, v["key"], _quantity_of(v["key"], function_id), float(v["value"]), v["unit"],
                        "calculation", f"run #{run_id} {label}: {v['label']}", f"run:{run_id}|{v['key']}", now))
    return run_id


def _staleness(db, run_id: int, seen: Optional[set] = None) -> List[str]:
    """Why a run is out of date ([] when current): changed or removed inputs, or a stale upstream run."""
    seen = (seen or set()) | {run_id}
    reasons = []
    for ri in db.execute("SELECT * FROM run_inputs WHERE run_id = ? AND param_key IS NOT NULL", (run_id,)):
        key = ri["param_key"]
        cur = db.execute("SELECT value FROM parameters WHERE param_key = ? ORDER BY id DESC LIMIT 1", (key,)).fetchone()
        if cur is None:
            reasons.append(f"{ri['name']}: its source is no longer in the project ({ri['source'] or key})")
        elif ri["value"] is not None and abs(cur["value"] - ri["value"]) > 1e-9 * max(1.0, abs(ri["value"])):
            reasons.append(f"{ri['name']}: {ri['source'] or key} changed from {ri['value']:g} to {cur['value']:g}")
        if key.startswith("run:"):
            upstream = int(key.split("|")[0][4:])
            if upstream not in seen and _staleness(db, upstream, seen):
                reasons.append(f"{ri['name']}: comes from run #{upstream}, which is out of date")
    return list(dict.fromkeys(reasons))


def _review(db, run_id: int) -> Optional[Dict[str, Any]]:
    row = db.execute("SELECT reviewer, note, reviewed_at FROM run_reviews WHERE run_id = ?", (run_id,)).fetchone()
    return dict(row) if row else None


def review_run(run_id: int, reviewer: str, note: Optional[str] = None) -> Dict[str, Any]:
    """Record that ``reviewer`` checked the run (replaces an earlier sign-off). KeyError for an unknown run."""
    reviewer = (reviewer or "").strip()
    if not reviewer:
        raise ValueError("Give the reviewer's name.")
    with connect() as db:
        if db.execute("SELECT 1 FROM runs WHERE id = ?", (run_id,)).fetchone() is None:
            raise KeyError(run_id)
        db.execute("INSERT OR REPLACE INTO run_reviews (run_id, reviewer, note, reviewed_at) VALUES (?,?,?,?)",
                   (run_id, reviewer, (note or "").strip() or None, time.time()))
        return _review(db, run_id)


def clear_review(run_id: int) -> bool:
    with connect() as db:
        return db.execute("DELETE FROM run_reviews WHERE run_id = ?", (run_id,)).rowcount > 0


def list_runs() -> List[Dict[str, Any]]:
    with connect() as db:
        rows = [row_dict(r) for r in db.execute("SELECT * FROM runs ORDER BY created_at DESC")]
        for r in rows:
            r["stale"] = _staleness(db, r["id"])
            r["review"] = _review(db, r["id"])
            r["inputs_from_project"] = [dict(x) for x in db.execute(
                "SELECT name, value, param_key, source FROM run_inputs WHERE run_id = ?", (r["id"],))]
            r.pop("results", None)
    return rows


def get_run(run_id: int) -> Optional[Dict[str, Any]]:
    with connect() as db:
        row = db.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        if row is None:
            return None
        run = row_dict(row)
        run["stale"] = _staleness(db, run_id)
        run["review"] = _review(db, run_id)
        run["inputs_from_project"] = [dict(x) for x in db.execute(
            "SELECT name, value, param_key, source FROM run_inputs WHERE run_id = ?", (run_id,))]
        loc = db.execute("SELECT name FROM locations WHERE id = ?", (run["location_id"],)).fetchone() if run["location_id"] else None
        run["location"] = loc["name"] if loc else None
    return run


def delete_run(run_id: int) -> bool:
    with connect() as db:
        db.execute("DELETE FROM parameters WHERE param_key LIKE ?", (f"run:{run_id}|%",))
        return db.execute("DELETE FROM runs WHERE id = ?", (run_id,)).rowcount > 0
