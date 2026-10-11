# Author: Utkarsh Gupta
# License: GPL v3
"""
Running catalogue calculations by calculation and method id, and comparing a calculation's methods on the same
inputs. Every run goes through ``registry.execute_function`` - the path /api/execute and the forms use - so the
wrappers, corrections and input validation apply exactly as they do today; the raw response is returned untouched
next to its normalised values (``envelope.extract_values``).

Comparison: each method gets the same inputs and uses the ones it takes (Groundhog functions accept and ignore
extra keyword arguments; wrappers read their own fields). A method that lacks an input it needs reports that as its
own error; the others still run. Values are lined up across methods by quantity name and unit, so "Ka" of one
method sits next to "KaR" of another when the quantity directory names both the same.
"""
from typing import Any, Dict, List, Optional

from core.catalogue import effective_status, load_catalogue


class CatalogueRunError(ValueError):
    """Unknown calculation or method."""


def _calculation(calculation_id: str) -> Dict[str, Any]:
    calc = load_catalogue()["calculations"].get(calculation_id)
    if calc is None:
        raise CatalogueRunError(f"Unknown calculation '{calculation_id}'.")
    return calc


def _method(calc: Dict[str, Any], method_id: Optional[str]) -> Dict[str, Any]:
    wanted = method_id or calc["default_method"]
    for m in calc["methods"]:
        if m["id"] == wanted:
            return m
    raise CatalogueRunError(f"Calculation '{calc['id']}' has no method '{wanted}' "
                            f"(methods: {', '.join(m['id'] for m in calc['methods'])}).")


def _error_of(raw: Any) -> Optional[str]:
    if not isinstance(raw, dict):
        return None
    if raw.get("error"):
        return str(raw["error"])
    if raw.get("status") == "ValidationError" or raw.get("detail"):
        detail = raw.get("detail") or raw
        return str(detail.get("error") if isinstance(detail, dict) and detail.get("error") else detail)
    return None


def run_method(calculation_id: str, method_id: Optional[str], inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Run one method (default: the calculation's default method). Never raises for a calculation failure."""
    from core.catalogue.envelope import extract_values
    from core.registry import registry
    calc = _calculation(calculation_id)
    method = _method(calc, method_id)
    function_id = method["function"]
    try:
        raw = registry.execute_function(calculation_id, function_id, dict(inputs or {}))
    except Exception as e:  # an engine exception is this method's result, not a server error
        raw = {"error": f"{type(e).__name__}: {e}"}
    error = _error_of(raw)
    return {"calculation": calc["id"], "method": method["id"], "label": method["label"], "function": function_id,
            "status": effective_status(method), "error": error,
            "values": [] if error else extract_values(function_id, raw), "raw": raw}


def compare_methods(calculation_id: str, inputs: Dict[str, Any], methods: Optional[List[str]] = None,
                    method_inputs: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Run the given methods (default: all) on the same inputs; ``method_inputs`` ({method_id: {...}}) gives a method
    its own values on top of them, so the user can set each method's parameters separately.
    Returns {"calculation", "title", "methods": [run_method results without "raw"], "rows": [{"label", "symbol",
    "unit", "values": {method_id: value}}]} - rows in first-seen order, one per quantity name and unit.
    """
    calc = _calculation(calculation_id)
    chosen = [_method(calc, m) for m in methods] if methods else list(calc["methods"])
    runs = []
    rows: Dict[tuple, Dict[str, Any]] = {}
    for m in chosen:
        own = (method_inputs or {}).get(m["id"]) or {}
        run = run_method(calculation_id, m["id"], {**(inputs or {}), **own})
        run.pop("raw", None)
        runs.append(run)
        for v in run["values"]:
            if not isinstance(v["value"], (int, float)) or isinstance(v["value"], bool):
                continue
            key = (v["label"].strip().lower(), v["unit"] or "")
            row = rows.setdefault(key, {"label": v["label"], "symbol": v["symbol"], "unit": v["unit"], "values": {}})
            row["values"].setdefault(m["id"], v["value"])
    return {"calculation": calc["id"], "title": calc["title"], "methods": runs, "rows": list(rows.values())}
