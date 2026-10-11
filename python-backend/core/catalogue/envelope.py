# Author: Utkarsh Gupta
# License: GPL v3
"""
Normalised view of a calculation response, for the catalogue-driven UI, reports and GeoAI of later phases.

``envelope(function_id, raw)`` returns

    {"calculation", "method", "status",               # from the catalogue (None for internal/unknown functions)
     "values": [{"key", "label", "symbol", "unit", "value"}],   # the scalar results, named by the quantity directory
     "raw": raw}                                       # the response exactly as /api/execute returned it

It only reads ``raw``: the same object is handed back untouched, so every custom output (Plotly figures,
multi-plot payloads, tables, saved objects) keeps working as it does today. tests/golden/golden_tools.py checks
that for every recorded calculation. Not wired into /api/execute in Phase 0.
"""
import math
import re
from typing import Any, Dict, List, Optional

from core.catalogue import find_method

_KEY_UNIT = re.compile(r"^(.*?)\s*\[([^\]]*)\]\s*$")
# Keys of wrapper payloads that are structure, not results.
_STRUCTURE_KEYS = {"type", "plots", "data", "layout", "message", "status", "warnings", "results", "plot",
                   "image", "figure", "id", "name", "columns", "_provenance"}


def _is_scalar(v: Any) -> bool:
    if isinstance(v, bool) or v is None or isinstance(v, str):
        return True
    return isinstance(v, (int, float)) and math.isfinite(v)


def _value(function_id: str, key: str, value: Any, unit: Optional[str] = None) -> Dict[str, Any]:
    from core import quantity_directory as qd
    m = _KEY_UNIT.match(key)
    bare, key_unit = (m.group(1).strip(), m.group(2).strip()) if m else (key.strip(), None)
    documented = unit if unit not in (None, "") else key_unit
    q = qd.resolve(function_id, bare, documented)
    shown_unit = (q or {}).get("unit") or qd.canonical_unit(documented) or documented
    return {"key": key, "label": (q or {}).get("name") or bare.replace("_", " "),
            "symbol": (q or {}).get("symbol") or "", "unit": None if shown_unit in (None, "", "-") else shown_unit,
            "value": value}


def extract_values(function_id: str, raw: Any) -> List[Dict[str, Any]]:
    """The scalar results of a response: a wrapper's Output/Value/Unit table, or a function's flat result dict."""
    if not isinstance(raw, dict):
        return []
    results = raw.get("results")
    rows = results.get("data") if isinstance(results, dict) else None
    if isinstance(rows, list) and rows and all(isinstance(r, dict) and {"Output", "Value"} <= set(r) for r in rows):
        return [_value(function_id, str(r["Output"]), r["Value"], r.get("Unit"))
                for r in rows if _is_scalar(r["Value"])]
    if "error" in raw or "detail" in raw:
        return []
    nested = raw.get("result")
    if isinstance(nested, dict) and not any(isinstance(k, str) and not k.startswith("_") and k not in _STRUCTURE_KEYS
                                            and k != "result" and _is_scalar(v) for k, v in raw.items()):
        raw = nested  # {"result": {...}, "warnings": [...]}: the values are one level down
    return [_value(function_id, k, v) for k, v in raw.items()
            if isinstance(k, str) and not k.startswith("_") and k not in _STRUCTURE_KEYS and _is_scalar(v)]


def envelope(function_id: str, raw: Any) -> Dict[str, Any]:
    hit = find_method(function_id)
    return {
        "calculation": hit["calculation"]["id"] if hit else None,
        "method": hit["method"]["id"] if hit else None,
        "status": hit["method"]["status"] if hit else None,
        "values": extract_values(function_id, raw),
        "raw": raw,
    }
