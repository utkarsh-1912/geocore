# Author: Utkarsh Gupta
# License: GPL v3
"""
AGS (3.1 / 4.0) into the project ground model: each exploratory hole (HOLE / LOCA) becomes a location, its
stratigraphy (GEOL) its layers, and its SPT blow counts (ISPT) a measured parameter of the layer they were taken
in. A layer with several tests gets their mean, and the source names every test depth and the file, so a form
pre-filled from it says exactly where the number came from. Nothing is correlated or defaulted here.

Re-importing a file replaces the locations that file created; workspace syncs leave them alone (their source is
the file, not a saved workspace object).
"""
import math
import re
import time
from typing import Any, Dict, List, Optional

from core.project.store import connect

AGS_PREFIX = "ags:"
SPT_COLUMN = "SPT N [-]"


def _num(value: Any) -> Optional[float]:
    try:
        v = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _first(row: Dict[str, Any], *keys: str) -> Any:
    for k in keys:
        if row.get(k) not in (None, ""):
            return row[k]
    return None


def _holes(dataset) -> List[Dict[str, Any]]:
    group = dataset.groups.get("LOCA")
    if group is None:
        group = dataset.groups.get("HOLE")
    if group is None:
        return []
    out = []
    for row in group.to_dict("records"):
        hole = _first(row, "LOCA_ID", "HOLE_ID")
        if hole:
            out.append({"id": str(hole).strip(), "type": _first(row, "LOCA_TYPE", "HOLE_TYPE")})
    return out


def _rows_for(dataset, group: str, hole: str) -> List[Dict[str, Any]]:
    df = dataset.groups.get(group)
    if df is None:
        return []
    id_col = "LOCA_ID" if "LOCA_ID" in df.columns else "HOLE_ID"
    if id_col not in df.columns:
        return []
    return [r for r in df.to_dict("records") if str(r.get(id_col, "")).strip().upper() == hole.upper()]


def _spt_tests(dataset, hole: str) -> List[Dict[str, Any]]:
    tests = []
    for r in _rows_for(dataset, "ISPT", hole):
        depth = _num(_first(r, "ISPT_TOP", "ISPT_DPTH"))
        raw = str(_first(r, "ISPT_NVAL", "ISPT_MAIN") or "").strip()
        digits = re.sub(r"[^0-9.]", "", raw)
        n = _num(digits) if digits else None
        if depth is None or n is None:
            continue
        tests.append({"depth": depth, "n": n, "refusal": raw.startswith(">") or "*" in raw})
    return tests


def import_ags(text: str, filename: str = "dataset.ags") -> Dict[str, Any]:
    """Store the AGS file's holes, strata and SPT as project locations. Returns counts and what was skipped."""
    from core.geoai.ags import AGSProjectDataset
    from core.project.ground import _quantity_of
    dataset = AGSProjectDataset.parse_ags_text(text, filename=filename)
    spt_quantity = _quantity_of(SPT_COLUMN)
    holes = _holes(dataset)
    counts: Dict[str, Any] = {"locations": 0, "layers": 0, "parameters": 0, "skipped": []}
    if not holes:
        counts["skipped"].append("no HOLE or LOCA group: no exploratory holes in the file")
        return counts
    now = time.time()
    with connect() as db:
        db.execute("DELETE FROM locations WHERE source_object LIKE ?", (f"{AGS_PREFIX}{filename}:%",))
        for hole in holes:
            strata = []
            for r in _rows_for(dataset, "GEOL", hole["id"]):
                top, base = _num(r.get("GEOL_TOP")), _num(r.get("GEOL_BASE"))
                if top is None or base is None or base <= top:
                    continue
                strata.append((top, base, (_first(r, "GEOL_DESC", "GEOL_LEG", "GEOL_GEOL") or "").strip() or None))
            if not strata:
                counts["skipped"].append(f"{hole['id']}: no stratigraphy (GEOL)")
                continue
            strata.sort()
            loc = db.execute("INSERT INTO locations (name, kind, source_object, groundwater_m, synced_at) VALUES (?,?,?,?,?)",
                             (hole["id"], "borehole", f"{AGS_PREFIX}{filename}:{hole['id']}", None, now)).lastrowid
            counts["locations"] += 1
            tests = _spt_tests(dataset, hole["id"])
            for i, (top, base, desc) in enumerate(strata):
                lay = db.execute("INSERT INTO layers (location_id, idx, top_m, bottom_m, soil_type) VALUES (?,?,?,?,?)",
                                 (loc, i + 1, top, base, desc)).lastrowid
                counts["layers"] += 1
                last = i == len(strata) - 1
                inside = [t for t in tests if top <= t["depth"] < base or (last and t["depth"] == base)]
                if not inside:
                    continue
                mean = sum(t["n"] for t in inside) / len(inside)
                depths = ", ".join(f"{t['depth']:g}" + (" (refusal)" if t["refusal"] else "") for t in inside)
                source = (f"AGS '{filename}' hole {hole['id']}, layer {i + 1} ({top:g}-{base:g} m): "
                          + (f"mean of {len(inside)} SPT at {depths} m" if len(inside) > 1 else f"SPT at {depths} m"))
                db.execute("INSERT INTO parameters (location_id, layer_id, column_name, quantity, value, unit, "
                           "source_kind, source_ref, param_key, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                           (loc, lay, SPT_COLUMN, spt_quantity, mean, "-", "measured", source,
                            f"{AGS_PREFIX}{filename}:{hole['id']}|{SPT_COLUMN}|{i + 1}", now))
                counts["parameters"] += 1
    return counts
