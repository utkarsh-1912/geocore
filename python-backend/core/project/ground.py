# Author: Utkarsh Gupta
# License: GPL v3
"""
Ground data of the project: indexing the workspace's saved soil profiles, and representative values for forms.

``sync_from_workspace`` reads (never writes) the saved SoilProfile objects and the recorded groundwater level and
stores them as locations, layers and parameters. A parameter keeps the profile column it came from (with its
unit), and the standard quantity that column means (quantity directory), so a form field can find it by quantity.

``prefill`` proposes values for a calculation form: for each field, the quantity it means in that function, then a
thickness-weighted value over the requested depth interval of one location, converted to the field's unit with
the same rules the GeoAI tools use (core/geoai/project_soil.py: a column whose unit cannot be verified is not
offered, and values <= 0 mean "not defined for this layer"). Every value comes with its source; nothing is
defaulted. The user decides which proposals to apply.
"""
import math
import re
import time
from typing import Any, Dict, List, Optional

from core.project.store import connect

_DEPTH_COLUMNS = {"depth from [m]", "depth to [m]", "z from [m]", "z to [m]"}
_SOIL_TYPE = re.compile(r"^(soil\s*type|soiltype|soil description|description)$", re.I)
_TOL = 1e-6


def _quantity_of(column: str, function_id: Optional[str] = None) -> Optional[str]:
    from core import quantity_directory as qd
    bare = re.sub(r"\s*\[[^\]]*\]\s*$", "", column).strip()
    q = qd.lookup_in(function_id, bare) if function_id else qd.lookup(bare)
    return q["id"] if q else None


def _unit_of(column: str) -> Optional[str]:
    m = re.search(r"\[([^\]]*)\]\s*$", column)
    return m.group(1).strip() if m else None


def sync_from_workspace() -> Dict[str, Any]:
    """Index every saved soil profile as a location with layers and parameters. Returns counts."""
    from core.geoai.data_access import recorded_groundwater_depth
    from core.state import state_manager
    groundwater = recorded_groundwater_depth()
    counts = {"locations": 0, "layers": 0, "parameters": 0, "skipped": []}
    now = time.time()
    with connect() as db:
        seen = []
        for meta in state_manager.list_by_type("SoilProfile"):
            obj = state_manager.get(meta["id"])
            table = obj  # a groundhog SoilProfile is a pandas DataFrame subclass
            if table is None or not hasattr(table, "columns") or not hasattr(table, "iterrows"):
                counts["skipped"].append(meta.get("name") or meta["id"])
                continue
            cols = {c.lower(): c for c in table.columns}
            top_c, bot_c = cols.get("depth from [m]"), cols.get("depth to [m]")
            if not top_c or not bot_c:
                counts["skipped"].append(meta.get("name") or meta["id"])  # e.g. a point table without layers
                continue
            kind = "cpt" if meta.get("kind") == "cpt" or any("qc" in c.lower() for c in table.columns) else "borehole"
            db.execute("DELETE FROM locations WHERE source_object = ?", (meta["id"],))
            cur = db.execute("INSERT INTO locations (name, kind, source_object, groundwater_m, synced_at) VALUES (?,?,?,?,?)",
                             (meta.get("name") or meta["id"], kind, meta["id"],
                              float(groundwater) if isinstance(groundwater, (int, float)) else None, now))
            loc = cur.lastrowid
            seen.append(meta["id"])
            counts["locations"] += 1
            soil_col = next((c for c in table.columns if _SOIL_TYPE.match(str(c).strip())), None)
            for i, (_, row) in enumerate(table.iterrows()):
                top, bottom = float(row[top_c]), float(row[bot_c])
                lay = db.execute("INSERT INTO layers (location_id, idx, top_m, bottom_m, soil_type) VALUES (?,?,?,?,?)",
                                 (loc, i + 1, top, bottom,
                                  str(row[soil_col]).strip() if soil_col and isinstance(row[soil_col], str) else None)).lastrowid
                counts["layers"] += 1
                for col in table.columns:
                    if col.lower() in _DEPTH_COLUMNS or col == soil_col:
                        continue
                    v = row[col]
                    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(float(v)):
                        continue
                    db.execute("INSERT INTO parameters (location_id, layer_id, column_name, quantity, value, unit, "
                               "source_kind, source_ref, param_key, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                               (loc, lay, col, _quantity_of(col), float(v), _unit_of(col), "measured",
                                f"profile '{meta.get('name') or meta['id']}' column '{col}', layer {i + 1} "
                                f"({top:g}-{bottom:g} m)", f"{meta['id']}|{col}|{i + 1}", now))
                    counts["parameters"] += 1
        # Locations whose saved profile was deleted from the workspace go too (derived runs keep their record).
        # (Locations imported from AGS files belong to their file, not to the workspace.)
        rows = db.execute("SELECT id, source_object FROM locations WHERE source_object IS NOT NULL "
                          "AND source_object NOT LIKE 'ags:%'").fetchall()
        for r in rows:
            if r["source_object"] not in seen and state_manager.get(r["source_object"]) is None:
                db.execute("DELETE FROM locations WHERE id = ?", (r["id"],))
    return counts


def summary() -> Dict[str, Any]:
    with connect() as db:
        locations = [dict(r) for r in db.execute(
            "SELECT l.id, l.name, l.kind, l.groundwater_m, l.synced_at, "
            "(SELECT COUNT(*) FROM layers y WHERE y.location_id = l.id) AS layers, "
            "(SELECT MAX(bottom_m) FROM layers y WHERE y.location_id = l.id) AS depth_m "
            "FROM locations l ORDER BY l.name")]
        runs = db.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        derived = db.execute("SELECT COUNT(*) FROM parameters WHERE source_kind = 'calculation'").fetchone()[0]
    return {"locations": locations, "runs": runs, "derived_parameters": derived}


def _field_units(function_id: str) -> Dict[str, Optional[str]]:
    from core.geoai.schemas import get_schema
    pair = get_schema(function_id)
    if not pair:
        return {}
    out = {}
    for name, field in pair[0].model_fields.items():
        extra = field.json_schema_extra if isinstance(field.json_schema_extra, dict) else {}
        out[name] = extra.get("unit")
    return out


def prefill(function_id: str, location_id: int, z_top: float, z_bottom: float,
            fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    {"proposals": {field: {"value", "unit", "source"}}, "unavailable": {field: reason}} for one location and depth
    interval. Only fields that mean a known quantity are considered.
    """
    from core.geoai.project_soil import convert_column_value, round_sig
    if z_bottom - z_top <= _TOL:
        raise ValueError("The depth interval must have a positive thickness.")
    units = _field_units(function_id)
    names = fields or list(units)
    proposals: Dict[str, Any] = {}
    unavailable: Dict[str, str] = {}
    with connect() as db:
        loc = db.execute("SELECT * FROM locations WHERE id = ?", (location_id,)).fetchone()
        if loc is None:
            raise ValueError(f"Location {location_id} is not in the project.")
        layers = [dict(r) for r in db.execute("SELECT * FROM layers WHERE location_id = ? ORDER BY idx", (location_id,))]
        params = [dict(r) for r in db.execute(
            "SELECT * FROM parameters WHERE location_id = ? AND source_kind = 'measured'", (location_id,))]
    for field in names:
        quantity = _quantity_of(field, function_id)
        unit = units.get(field)
        if not quantity or unit in (None, ""):
            continue
        per_layer = {}
        for p in params:
            if p["quantity"] == quantity and p["layer_id"] not in per_layer:
                per_layer[p["layer_id"]] = p
        if not per_layer:
            unavailable[field] = f"no '{quantity.replace('_', ' ')}' column in '{loc['name']}'"
            continue
        covered = weighted = 0.0
        used, lacking = [], []
        for layer in layers:
            dz = min(z_bottom, layer["bottom_m"]) - max(z_top, layer["top_m"])
            if dz <= _TOL:
                continue
            p = per_layer.get(layer["id"])
            value, note = (None, "no value")
            if p is not None:
                value, note = convert_column_value(p["value"], p["column_name"], unit)
                if value is not None and value <= 0:
                    value, note = None, "not defined (value <= 0)"
            if value is None:
                lacking.append(f"layer {layer['idx']} ({note})")
                continue
            covered += dz
            weighted += value * dz
            used.append((layer, value, p))
        if covered < (z_bottom - z_top) - _TOL:
            unavailable[field] = (f"not defined over {z_top:g}-{z_bottom:g} m of '{loc['name']}'"
                                  + (f": {', '.join(lacking)}" if lacking else ": the profile is shallower"))
            continue
        value = weighted / covered
        where = (f"layer {used[0][0]['idx']} ({used[0][0]['top_m']:g}-{used[0][0]['bottom_m']:g} m)" if len(used) == 1 else
                 f"thickness-weighted over {z_top:g}-{z_bottom:g} m from "
                 + ", ".join(f"layer {l['idx']} = {round_sig(v, 4):g}" for l, v, _ in used))
        source = f"project '{loc['name']}', column '{used[0][2]['column_name']}', {where}"
        imported = [p["source_ref"] for _, _, p in used if str(p["param_key"]).startswith("ags:")]
        if imported:  # AGS values: name the tests behind each layer value
            source += " [" + "; ".join(imported) + "]"
        proposals[field] = {"value": value, "unit": unit, "quantity": quantity,
                            "source": source,
                            "inputs": [{"param_key": p["param_key"], "value": p["value"]} for _, _, p in used]}
    # Values derived by earlier calculations at this location (Phase 5 chaining), for fields still open.
    for field in names:
        if field in proposals:
            continue
        quantity = _quantity_of(field, function_id)
        if not quantity:
            continue
        with connect() as db:
            d = db.execute("SELECT p.*, r.function_id FROM parameters p JOIN runs r ON p.param_key LIKE 'run:' || r.id || '|%' "
                           "WHERE p.location_id = ? AND p.source_kind = 'calculation' AND p.quantity = ? "
                           "ORDER BY p.created_at DESC LIMIT 1", (location_id, quantity)).fetchone()
        if d is not None:
            converted, _ = convert_column_value(d["value"], f"x [{d['unit']}]" if d["unit"] else "x", units.get(field) or "")
            if converted is not None:
                proposals[field] = {"value": converted, "unit": units.get(field), "quantity": quantity,
                                    "source": d["source_ref"], "inputs": [{"param_key": d["param_key"], "value": d["value"]}]}
                unavailable.pop(field, None)
    return {"location": dict(loc), "proposals": proposals, "unavailable": unavailable}
