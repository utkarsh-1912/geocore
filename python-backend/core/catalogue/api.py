# Author: Utkarsh Gupta
# License: GPL v3
"""Catalogue endpoints: the catalogue itself (read-only) and the phase-relations "solve for" calculation."""
from typing import Any, Dict

from fastapi import APIRouter, Body, HTTPException

from core.catalogue import api_payload

router = APIRouter()


@router.get("/catalogue")
def get_catalogue():
    """Domains -> calculations -> methods; each method names the function /api/execute runs for it."""
    return api_payload()


@router.post("/calculations/{calculation_id}/run")
def run_calculation(calculation_id: str, payload: Dict[str, Any] = Body(...)):
    """
    Body: {"method": optional method id (default: the calculation's default), "inputs": {...}}. Runs through the
    same path as /api/execute; returns the raw response unchanged plus its normalised values and any error.
    """
    from core.catalogue.run import CatalogueRunError, run_method
    try:
        return run_method(calculation_id, payload.get("method"), payload.get("inputs") or {})
    except CatalogueRunError as e:
        raise HTTPException(status_code=404, detail={"error": str(e)})


@router.get("/calculations/{calculation_id}/suggest")
def suggest_calculation_method(calculation_id: str):
    """The "Auto" method for the data saved in the workspace: {method, label, reason, available, fits}."""
    from core.catalogue.suggest import suggest_method
    try:
        return suggest_method(calculation_id)
    except KeyError:
        raise HTTPException(status_code=404, detail={"error": f"Unknown calculation '{calculation_id}'."})


@router.post("/calculations/{calculation_id}/compare")
def compare_calculation(calculation_id: str, payload: Dict[str, Any] = Body(...)):
    """
    Body: {"inputs": {...}, "methods": optional [method ids], "method_inputs": optional {method id: {...}}}.
    Every method on the same inputs (plus its own, if given), side by side.
    """
    from core.catalogue.run import CatalogueRunError, compare_methods
    try:
        return compare_methods(calculation_id, payload.get("inputs") or {}, payload.get("methods"),
                               payload.get("method_inputs"))
    except CatalogueRunError as e:
        raise HTTPException(status_code=404, detail={"error": str(e)})


@router.get("/calculations/phase_relations")
def phase_relations_info():
    """Quantities the phase-relations solver knows, its constants and the soil defaults it may assume."""
    from core.catalogue.phase_relations import describe
    return describe()


@router.post("/calculations/phase_relations/solve")
def phase_relations_solve(payload: Dict[str, Any] = Body(...)):
    """
    Body: {"known": {quantity: value}, "target": quantity, "assume": ["specific_gravity"|"saturation"],
           "unit_weight_water": optional kN/m3}. Every step runs an existing Groundhog function.
    422 with {"error", "needs"} when the target cannot be reached; "needs" lists what would make it reachable.
    """
    from core.catalogue.phase_relations import PhaseRelationError, solve
    known = payload.get("known") or {}
    if not isinstance(known, dict) or not payload.get("target"):
        raise HTTPException(status_code=400, detail={"error": "Give 'known' (quantity: value) and 'target'."})
    try:
        clean = {k: float(v) for k, v in known.items() if v not in (None, "")}
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail={"error": "Every known value must be a number."})
    try:
        return solve(clean, payload["target"], payload.get("assume") or [], payload.get("unit_weight_water"))
    except PhaseRelationError as e:
        raise HTTPException(status_code=422, detail={"error": str(e), "needs": e.needs, "skipped": e.skipped})
