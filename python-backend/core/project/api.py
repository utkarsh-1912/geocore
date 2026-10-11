# Author: Utkarsh Gupta
# License: GPL v3
"""Project endpoints (/api/project/...). Additive: nothing else in the app depends on them."""
from typing import Any, Dict

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/project")


@router.get("")
def project_summary():
    from core.project.ground import summary
    return summary()


@router.post("/import_ags")
def project_import_ags(payload: Dict[str, Any] = Body(...)):
    """Body: {"text": AGS file content, "filename": name}. Holes, strata and SPT become project locations."""
    from core.project.ags_import import import_ags
    from core.project.ground import summary
    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        raise HTTPException(status_code=400, detail={"error": "Give the AGS file content as 'text'."})
    counts = import_ags(text, str(payload.get("filename") or "dataset.ags"))
    return {"imported": counts, **summary()}


@router.post("/sync")
def project_sync():
    """Index the workspace's saved soil profiles (read-only) as project locations, layers and parameters."""
    from core.project.ground import summary, sync_from_workspace
    counts = sync_from_workspace()
    return {**counts, **summary()}


@router.get("/locations/{location_id}/layers")
def location_layers(location_id: int):
    from core.project.store import connect
    with connect() as db:
        if db.execute("SELECT 1 FROM locations WHERE id = ?", (location_id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail="Location not found")
        return [dict(r) for r in db.execute("SELECT idx, top_m, bottom_m, soil_type FROM layers WHERE location_id = ? "
                                            "ORDER BY idx", (location_id,))]


@router.post("/prefill")
def project_prefill(payload: Dict[str, Any] = Body(...)):
    """Body: {function_id, location_id, z_top, z_bottom, fields?}. Proposals with sources; the user applies them."""
    from core.project.ground import prefill
    try:
        return prefill(payload["function_id"], int(payload["location_id"]), float(payload["z_top"]),
                       float(payload["z_bottom"]), payload.get("fields"))
    except (KeyError, TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})


@router.post("/runs")
def save_run(payload: Dict[str, Any] = Body(...)):
    """Body: {function_id, inputs, results, input_sources?, location_id?, note?} -> {id}."""
    from core.project.runs import record_run
    if not payload.get("function_id") or not isinstance(payload.get("inputs"), dict):
        raise HTTPException(status_code=400, detail={"error": "Give function_id, inputs and results."})
    run_id = record_run(payload["function_id"], payload["inputs"], payload.get("results"),
                        payload.get("input_sources"), payload.get("location_id"), payload.get("note"))
    return {"id": run_id}


@router.get("/runs")
def runs():
    from core.project.runs import list_runs
    return list_runs()


@router.delete("/runs/{run_id}")
def remove_run(run_id: int):
    from core.project.runs import delete_run
    if not delete_run(run_id):
        raise HTTPException(status_code=404, detail="Run not found")
    return {"deleted": run_id}


@router.post("/runs/{run_id}/review")
def sign_off_run(run_id: int, payload: Dict[str, Any] = Body(...)):
    """Body: {"reviewer": name, "note": optional}. Records the sign-off shown in the run's report."""
    from core.project.runs import review_run
    try:
        return review_run(run_id, str(payload.get("reviewer") or ""), payload.get("note"))
    except KeyError:
        raise HTTPException(status_code=404, detail="Run not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})


@router.delete("/runs/{run_id}/review")
def withdraw_review(run_id: int):
    from core.project.runs import clear_review
    return {"cleared": clear_review(run_id)}


@router.get("/runs/{run_id}/report")
def run_report(run_id: int, format: str = "html"):
    from core.project.report import build_report, render_html
    try:
        report = build_report(run_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Run not found")
    return report if format == "json" else HTMLResponse(render_html([report]))


@router.get("/report")
def project_report():
    from core.project.report import project_report_html
    return HTMLResponse(project_report_html())
