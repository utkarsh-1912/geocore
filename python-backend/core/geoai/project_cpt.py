# Author: Utkarsh Gupta
# License: GPL v3
"""
Project CPT access for GeoAI (AGENTS.md §9, §10, §14, §16).

GeoCore keeps the current project's data in the workspace object store
(``core.state.state_manager``). CPT soundings reach that store as:

- ``SoilProfile`` objects (Excel/CSV uploads, ``/objects/upload``) whose columns hold CPT
  channels, e.g. ``'z [m]'``, ``'qc [MPa]'``, ``'fs [kPa]'``, ``'u2 [kPa]'`` -- the
  "Soil Profile (w/ CPT Data)" used by the desktop De Beer / LCPC / Koppejan forms;
- ``PCPTProcessing`` objects (Groundhog) with loaded ``.data`` (``'qc [MPa]'``, ``'fs [MPa]'``...);
- ``AGSConverter`` objects (AGS 3.1 / 4 uploads) containing an ``SCPT`` group.

This module does not create a second store: it reads those objects deterministically and
normalises them to one compact structure (depth [m], qc [MPa], fs [kPa], u2 [kPa]) with
provenance. Units are taken only from the column headers; a channel whose unit is missing
or unknown is not used (never guessed) and is reported as a data-quality flag.

Soil behaviour type intervals reuse ``core.geoai.cpt.CPTSounding`` (Robertson Ic).
"""
from dataclasses import dataclass, field
import math
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

from core.geoai.exceptions import GeoAIValidationError

#: Unit weight used only for the stress normalisation behind Ic / SBT classification
#: (the same default as core.geoai.cpt.CPTSounding).
SBT_UNIT_WEIGHT_KN_M3 = 18.5
DEFAULT_MIN_LAYER_THICKNESS_M = 0.5
DEFAULT_MAX_INTERVALS = 12
MAX_INTERVALS_LIMIT = 15

_HEADER = re.compile(r"^\s*(?P<base>.*?)\s*[\[(]\s*(?P<unit>[^\])]*?)\s*[\])]\s*$")

_DEPTH_BASES = {"z", "depth", "penetration", "penetrationdepth", "penetrationlength", "scptdpth", "testdepth"}
_QC_BASES = {"qc", "coneresistance", "conetipresistance", "tipresistance", "measuredconeresistance", "scptres"}
_FS_BASES = {"fs", "sleevefriction", "localfriction", "localsleevefriction", "scptfres"}
_U2_BASES = {"u2", "porepressureu2", "porewaterpressureu2", "shoulderporepressure", "scptpwp2"}
_ID_BASES = {"cptid", "cpt", "locaid", "holeid", "locationid", "location", "testid", "pointid", "sounding",
             "soundingid", "cptname", "name"}
_EAST_BASES = {"easting", "x", "locanate", "holenatx", "eastingm"}
_NORTH_BASES = {"northing", "y", "locanatn", "holenaty", "northingm"}
_GL_BASES = {"groundlevel", "elevation", "groundelevation", "locagl", "holegl", "surfaceelevation"}
_DEPTH_FROM = "depthfrom"
_DEPTH_TO = "depthto"

_TARGET_UNITS = {"depth": "m", "qc": "MPa", "fs": "kPa", "u2": "kPa"}


def _base(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def split_header(col: Any) -> Tuple[str, Optional[str]]:
    """``'qc [MPa]'`` -> ``('qc', 'MPa')``; ``'qc'`` -> ``('qc', None)``."""
    text = str(col)
    m = _HEADER.match(text)
    if m:
        unit = m.group("unit").strip() or None
        return _base(m.group("base")), unit
    return _base(text), None


def normalize_cpt_id(value: Any) -> str:
    """Case/spacing/zero-padding-insensitive CPT id: 'CPT-03', 'cpt 3', 'CPT_003' -> 'cpt3'."""
    text = re.sub(r"\.(xlsx?|csv|ags|gef|txt)$", "", str(value).strip(), flags=re.I)
    text = re.sub(r"[^a-z0-9]", "", text.lower())
    return re.sub(r"\d+", lambda m: str(int(m.group())), text)


def _convert(values: np.ndarray, unit: Optional[str], target: str, label: str) -> np.ndarray:
    """Deterministic unit conversion of a channel (core.geoai.units); raises on unknown units."""
    from core.geoai.units import convert_unit
    if not unit or unit.strip() in ("-", ""):
        raise GeoAIValidationError(f"column '{label}' has no unit")
    factor = convert_unit(1.0, unit, target, field_name=label)
    return values.astype(float) * factor


@dataclass
class ProjectCPT:
    """One CPT sounding normalised from the project store (depth [m], qc [MPa], fs/u2 [kPa])."""
    cpt_id: str
    data: pd.DataFrame
    source: Dict[str, Any]
    location: Dict[str, Optional[float]] = field(default_factory=dict)
    groundwater_depth_m: Optional[float] = None
    groundwater_source: Optional[str] = None
    notes: List[str] = field(default_factory=list)

    @property
    def depth_min(self) -> float:
        return float(self.data["depth_m"].min())

    @property
    def depth_max(self) -> float:
        return float(self.data["depth_m"].max())

    def channels(self) -> List[str]:
        out = ["qc"]
        for ch in ("fs", "u2"):
            col = f"{ch}_kpa"
            if col in self.data and self.data[col].notna().any() and (self.data[col].fillna(0) != 0).any():
                out.append(ch)
        return out

    def listing(self) -> Dict[str, Any]:
        loc = {k: v for k, v in self.location.items() if v is not None}
        return {
            "cpt_id": self.cpt_id,
            "depth_range_m": [round(self.depth_min, 2), round(self.depth_max, 2)],
            "n_points": int(len(self.data)),
            "channels": self.channels(),
            "location": loc or None,
            "groundwater_depth_m": self.groundwater_depth_m,
            "source": f"{self.source.get('object_type')} '{self.source.get('object_name')}'",
        }


# --------------------------------------------------------------------------- store access

def default_store():
    from core.state import state_manager
    return state_manager


def _iter_store(store) -> Iterable[Tuple[Dict[str, Any], Any]]:
    for meta in list(store.list_by_type("all")):
        obj = store.get(meta.get("id"))
        if obj is not None:
            yield meta, obj


def _constant(series: pd.Series) -> Optional[float]:
    vals = pd.to_numeric(series, errors="coerce").dropna().unique()
    if len(vals) == 1 and math.isfinite(float(vals[0])):
        return float(vals[0])
    return None


def _find(columns: Iterable[Any], bases: set) -> Optional[Any]:
    for col in columns:
        if split_header(col)[0] in bases:
            return col
    return None


def _table_to_cpts(df: pd.DataFrame, source: Dict[str, Any], default_id: str,
                   location: Optional[Dict[str, Optional[float]]] = None) -> Tuple[List[ProjectCPT], Optional[str]]:
    """Normalise a CPT table; returns (cpts, reason-not-usable)."""
    cols = list(df.columns)
    qc_col = _find(cols, _QC_BASES)
    if qc_col is None:
        return [], None                       # not a CPT table (e.g. an ordinary layered soil profile)
    depth_col = _find(cols, _DEPTH_BASES)
    notes: List[str] = []
    from_col = next((c for c in cols if split_header(c)[0] == _DEPTH_FROM), None)
    to_col = next((c for c in cols if split_header(c)[0] == _DEPTH_TO), None)

    try:
        if depth_col is not None:
            depth = _convert(pd.to_numeric(df[depth_col], errors="coerce").to_numpy(), split_header(depth_col)[1], "m", str(depth_col))
            depth_desc = str(depth_col)
        elif from_col is not None and to_col is not None:
            z1 = _convert(pd.to_numeric(df[from_col], errors="coerce").to_numpy(), split_header(from_col)[1], "m", str(from_col))
            z2 = _convert(pd.to_numeric(df[to_col], errors="coerce").to_numpy(), split_header(to_col)[1], "m", str(to_col))
            depth = 0.5 * (z1 + z2)
            depth_desc = f"midpoint of '{from_col}' and '{to_col}'"
            notes.append("CPT stored as depth intervals; point depth taken as interval midpoint.")
        else:
            return [], f"qc column '{qc_col}' found but no depth column (expected e.g. 'z [m]' or 'Depth [m]')"
        qc = _convert(pd.to_numeric(df[qc_col], errors="coerce").to_numpy(), split_header(qc_col)[1], "MPa", str(qc_col))
    except GeoAIValidationError as e:
        return [], (f"{e.message}; units must be given in the column header, e.g. 'qc [MPa]', "
                    "'z [m]' (units are never assumed)")

    channels = {"depth_m": depth, "qc_mpa": qc}
    columns_used = {"depth": depth_desc, "qc": str(qc_col)}
    for key, bases in (("fs", _FS_BASES), ("u2", _U2_BASES)):
        col = _find(cols, bases)
        if col is None:
            channels[f"{key}_kpa"] = np.full(len(df), np.nan)
            continue
        try:
            channels[f"{key}_kpa"] = _convert(pd.to_numeric(df[col], errors="coerce").to_numpy(),
                                              split_header(col)[1], "kPa", str(col))
            columns_used[key] = str(col)
        except GeoAIValidationError as e:
            channels[f"{key}_kpa"] = np.full(len(df), np.nan)
            notes.append(f"{key} channel not used: {e.message}.")
    table = pd.DataFrame(channels)

    gw_col = next((c for c in cols if "water" in split_header(c)[0] and any(
        w in split_header(c)[0] for w in ("level", "table", "depth"))), None) or _find(cols, {"gwt", "groundwater"})
    east_col, north_col, gl_col = _find(cols, _EAST_BASES), _find(cols, _NORTH_BASES), _find(cols, _GL_BASES)
    id_col = _find([c for c in cols if df[c].dtype == object], _ID_BASES)

    groups = [(default_id, df.index)]
    if id_col is not None:
        ids = df[id_col].astype(str).str.strip()
        groups = [(str(v), ids.index[ids == v]) for v in pd.unique(ids) if v and v.lower() != "nan"]

    out = []
    for cpt_id, idx in groups:
        part = table.loc[idx]
        raw = df.loc[idx]
        loc = dict(location or {})
        for key, col in (("easting", east_col), ("northing", north_col), ("ground_level", gl_col)):
            if col is not None:
                loc[key] = _constant(raw[col])
        gw, gw_src = None, None
        if gw_col is not None:
            val = _constant(raw[gw_col])
            unit = split_header(gw_col)[1]
            if val is not None and (unit in (None, "-", "m") ):
                gw, gw_src = val, f"column '{gw_col}' of {source.get('object_type')} '{source.get('object_name')}'"
        src = dict(source, columns=columns_used, **({"id_column": str(id_col)} if id_col is not None else {}))
        cpt = _finalise(cpt_id, part, src, loc, gw, gw_src, list(notes))
        if cpt is not None:
            out.append(cpt)
    return out, None


def _finalise(cpt_id, table, source, location, gw, gw_src, notes) -> Optional[ProjectCPT]:
    n0 = len(table)
    table = table[np.isfinite(table["depth_m"]) & np.isfinite(table["qc_mpa"])]
    if len(table) < n0:
        notes.append(f"{n0 - len(table)} rows without depth or qc dropped.")
    if table.empty:
        return None
    if not table["depth_m"].is_monotonic_increasing:
        notes.append("Depths were not in increasing order; data sorted by depth.")
    table = table.sort_values("depth_m", kind="mergesort")
    dup = int(table["depth_m"].duplicated().sum())
    if dup:
        notes.append(f"{dup} duplicate depth rows removed (first kept).")
        table = table.drop_duplicates("depth_m", keep="first")
    return ProjectCPT(cpt_id=str(cpt_id), data=table.reset_index(drop=True), source=source,
                      location=location, groundwater_depth_m=gw, groundwater_source=gw_src, notes=notes)


def _pcpt_to_cpts(meta: Dict[str, Any], obj: Any) -> Tuple[List[ProjectCPT], Optional[str]]:
    data = getattr(obj, "data", None)
    if not isinstance(data, pd.DataFrame) or data.empty:
        return [], "PCPTProcessing object has no CPT data loaded"
    loc = {}
    for key, attr in (("easting", "easting"), ("northing", "northing"), ("ground_level", "elevation")):
        val = getattr(obj, attr, None)
        loc[key] = float(val) if isinstance(val, (int, float)) and math.isfinite(val) else None
    name = getattr(obj, "title", None) or meta.get("name") or meta.get("id")
    source = {"object_type": "PCPTProcessing", "object_name": meta.get("name") or name,
              "object_id": meta.get("id"), "processing": "Groundhog PCPTProcessing.data"}
    return _table_to_cpts(data, source, str(name), loc)


def _ags_to_cpts(meta: Dict[str, Any], obj: Any) -> Tuple[List[ProjectCPT], Optional[str]]:
    groups = set(getattr(obj, "groupnames", []) or [])
    if "SCPT" not in groups:
        return [], None
    try:
        df = obj.convert_ags_group("SCPT")
    except Exception as e:  # malformed group: report, do not guess
        return [], f"AGS SCPT group could not be read ({e})"
    source = {"object_type": "AGSConverter", "object_name": meta.get("name"), "object_id": meta.get("id"),
              "processing": "Groundhog AGSConverter.convert_ags_group('SCPT')"}
    cpts, reason = _table_to_cpts(df, source, str(meta.get("name") or "AGS"))
    if cpts and "LOCA" in groups:
        try:
            loca = obj.convert_ags_group("LOCA")
            id_col = _find(loca.columns, {"locaid"})
            for cpt in cpts:
                row = loca[loca[id_col].astype(str).str.strip() == cpt.cpt_id] if id_col is not None else loca.iloc[0:0]
                for key, bases in (("easting", {"locanate"}), ("northing", {"locanatn"}), ("ground_level", {"locagl"})):
                    col = _find(loca.columns, bases)
                    if col is not None and len(row):
                        cpt.location[key] = _constant(row[col])
        except Exception:
            pass
    return cpts, reason


def discover_project_cpts(store=None) -> Tuple[List[ProjectCPT], List[Dict[str, str]]]:
    """All CPT soundings in the project store plus the CPT-like sources that cannot be used."""
    store = store if store is not None else default_store()
    cpts: List[ProjectCPT] = []
    unusable: List[Dict[str, str]] = []
    for meta, obj in _iter_store(store):
        type_name = meta.get("type") or type(obj).__name__
        try:
            if type_name == "PCPTProcessing" or type(obj).__name__ == "PCPTProcessing":
                found, reason = _pcpt_to_cpts(meta, obj)
            elif type_name == "AGSConverter" or type(obj).__name__ == "AGSConverter":
                found, reason = _ags_to_cpts(meta, obj)
            elif isinstance(obj, pd.DataFrame):
                source = {"object_type": type_name, "object_name": meta.get("name"), "object_id": meta.get("id"),
                          "processing": "column mapping of the stored table"}
                found, reason = _table_to_cpts(obj, source, str(meta.get("name") or meta.get("id")))
            else:
                continue
        except Exception as e:  # never let one malformed object hide the others
            found, reason = [], f"could not be read ({type(e).__name__}: {e})"
        cpts.extend(found)
        if reason:
            unusable.append({"source": f"{type_name} '{meta.get('name')}'", "reason": reason})
    return cpts, unusable


def resolve_cpt(cpt_id: str, store=None) -> ProjectCPT:
    """Find one CPT by id (normalised), or by the store object id / name. Raises a clear error."""
    cpts, unusable = discover_project_cpts(store)
    key = normalize_cpt_id(cpt_id)
    matches = [c for c in cpts if normalize_cpt_id(c.cpt_id) == key]
    if not matches:
        matches = [c for c in cpts if str(cpt_id) == str(c.source.get("object_id"))
                   or (key and normalize_cpt_id(c.source.get("object_name") or "") == key and
                       len([d for d in cpts if d.source.get("object_id") == c.source.get("object_id")]) == 1)]
    if len(matches) == 1:
        return matches[0]
    available = ", ".join(sorted(c.cpt_id for c in cpts)) or "none"
    if not matches:
        hint = ""
        if unusable:
            hint = " Unusable CPT sources: " + "; ".join(f"{u['source']}: {u['reason']}" for u in unusable[:3]) + "."
        raise GeoAIValidationError(
            f"CPT '{cpt_id}' was not found in the current project. Available CPTs: {available}.{hint}",
            errors=[{"field": "cpt_id", "type": "cpt_not_found", "input_value": str(cpt_id),
                     "available": sorted(c.cpt_id for c in cpts)}])
    raise GeoAIValidationError(
        f"CPT id '{cpt_id}' is ambiguous: it matches {len(matches)} soundings "
        f"({', '.join(c.source.get('object_name') or '?' for c in matches)}). Ask the user which one.",
        errors=[{"field": "cpt_id", "type": "cpt_ambiguous", "input_value": str(cpt_id)}])


# --------------------------------------------------------------------------- interpretation

def classify_sbt(cpt: ProjectCPT, water_table_depth: Optional[float] = None) -> pd.DataFrame:
    """Robertson Ic / SBT zone per point via CPTSounding; rows without valid qc>0 and fs get NaN."""
    from core.geoai.cpt import CPTSounding
    d = cpt.data
    raw = pd.DataFrame({"depth": d["depth_m"], "qc": d["qc_mpa"], "fs": d["fs_kpa"],
                        "u2": d["u2_kpa"].fillna(0.0)})
    sounding = CPTSounding(sounding_id=cpt.cpt_id, raw_data=raw.iloc[0:0])
    sounding.raw_data = raw.reset_index(drop=True)
    derived = sounding.calculate_normalized_parameters(
        water_table_depth=0.0 if water_table_depth is None else float(water_table_depth),
        gamma_soil=SBT_UNIT_WEIGHT_KN_M3)
    valid = (d["qc_mpa"].to_numpy() > 0) & np.isfinite(d["fs_kpa"].to_numpy()) & (d["fs_kpa"].to_numpy() > 0)
    derived = derived.copy()
    derived.loc[~valid, ["Ic", "SBT_zone"]] = np.nan
    derived.loc[~valid, "SBT_description"] = None
    return derived


def sbt_available(cpt: ProjectCPT) -> bool:
    return "fs" in cpt.channels()


def sbt_intervals(cpt: ProjectCPT, min_thickness: float = DEFAULT_MIN_LAYER_THICKNESS_M,
                  max_intervals: int = DEFAULT_MAX_INTERVALS,
                  water_table_depth: Optional[float] = None) -> List[Dict[str, Any]]:
    """
    Contiguous SBT-zone intervals, deterministic merging: the thinnest interval thinner than
    ``min_thickness`` (or, while there are more than ``max_intervals``, the thinnest overall)
    is merged into its thicker neighbour. Boundaries lie midway between CPT points; the first
    interval starts at 0 m and the last ends at the final CPT depth.
    """
    derived = classify_sbt(cpt, water_table_depth)
    z = derived["depth"].to_numpy(dtype=float)
    zone = derived["SBT_zone"].to_numpy(dtype=float)
    ok = np.isfinite(zone)
    if not ok.any():
        return []
    zc, zonec = z[ok], zone[ok].astype(int)
    runs: List[List[Any]] = []            # [first_idx, last_idx, zone]
    for i, zn in enumerate(zonec):
        if runs and runs[-1][2] == zn:
            runs[-1][1] = i
        else:
            runs.append([i, i, zn])

    def bounds(k):
        top = 0.0 if k == 0 else 0.5 * (zc[runs[k - 1][1]] + zc[runs[k][0]])
        bot = float(z.max()) if k == len(runs) - 1 else 0.5 * (zc[runs[k][1]] + zc[runs[k + 1][0]])
        return top, bot

    while len(runs) > 1:
        thick = [bounds(k)[1] - bounds(k)[0] for k in range(len(runs))]
        k = int(np.argmin(thick))
        if thick[k] >= min_thickness and len(runs) <= max_intervals:
            break
        if k == 0:
            j = 1
        elif k == len(runs) - 1:
            j = k - 1
        else:
            j = k - 1 if thick[k - 1] >= thick[k + 1] else k + 1
        lo, hi = min(k, j), max(k, j)
        runs[lo] = [runs[lo][0], runs[hi][1], runs[j][2]]
        del runs[hi]
        # re-merge neighbours that now share a zone
        merged: List[List[Any]] = []
        for r in runs:
            if merged and merged[-1][2] == r[2]:
                merged[-1][1] = r[1]
            else:
                merged.append(r)
        runs = merged

    from core.geoai.cpt import SBT_ZONES_IC
    names = {zn: name for _, _, zn, name in SBT_ZONES_IC}
    d = cpt.data
    out = []
    for k, (_, _, zn) in enumerate(runs):
        top, bot = bounds(k)
        last = k == len(runs) - 1
        sel = (d["depth_m"] >= top) & ((d["depth_m"] <= bot) if last else (d["depth_m"] < bot))
        ic = derived.loc[sel.to_numpy(), "Ic"]
        row = {"depth_from_m": round(top, 2), "depth_to_m": round(bot, 2), "sbt_zone": int(zn),
               "sbt": names.get(int(zn), "unknown"), "ic_mean": _r(ic.mean(), 2),
               "qc_mpa": _stats(d.loc[sel, "qc_mpa"], 2)}
        for ch in ("fs", "u2"):
            if ch in cpt.channels():
                row[f"{ch}_kpa"] = _stats(d.loc[sel, f"{ch}_kpa"], 1)
        row["_top"], row["_bottom"] = top, bot
        out.append(row)
    return out


def _r(v: Any, nd: int) -> Optional[float]:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return round(v, nd) if math.isfinite(v) else None


def _stats(series: pd.Series, nd: int) -> Optional[Dict[str, Optional[float]]]:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return None
    return {"min": _r(s.min(), nd), "mean": _r(s.mean(), nd), "max": _r(s.max(), nd)}


def data_quality_flags(cpt: ProjectCPT) -> List[str]:
    """Deterministic data-quality checks (missing channels, negative/zero qc, gaps, start depth)."""
    d = cpt.data
    flags = list(cpt.notes)
    chans = cpt.channels()
    for ch, why in (("fs", "SBT/Ic classification not possible"), ("u2", "qt taken equal to qc (u2 = 0)")):
        if ch not in chans:
            col = d[f"{ch}_kpa"]
            state = "all zero" if col.notna().any() else "missing"
            flags.append(f"{ch} channel {state}: {why}.")
        else:
            nz = int((d[f"{ch}_kpa"].fillna(0) == 0).sum()) if ch == "fs" else 0
            if nz:
                flags.append(f"{nz} points with fs = 0 or missing excluded from SBT classification.")
    neg = d[d["qc_mpa"] < 0]
    if len(neg):
        flags.append(f"{len(neg)} points with negative qc (between {neg['depth_m'].min():.2f} and {neg['depth_m'].max():.2f} m).")
    zero = int((d["qc_mpa"] == 0).sum())
    if zero:
        flags.append(f"{zero} points with qc = 0.")
    if len(d) > 2:
        dz = np.diff(d["depth_m"].to_numpy())
        med = float(np.median(dz))
        gap_idx = np.where(dz > max(0.5, 5 * med))[0]
        if len(gap_idx):
            gaps = ", ".join(f"{d['depth_m'].iloc[i]:.2f}-{d['depth_m'].iloc[i + 1]:.2f} m" for i in gap_idx[:5])
            flags.append(f"{len(gap_idx)} data gap(s) larger than max(0.5 m, 5x median spacing): {gaps}.")
    if cpt.depth_min > 0.5:
        flags.append(f"CPT starts at {cpt.depth_min:.2f} m (no data above; pre-drilled or removed).")
    return flags


def median_spacing(cpt: ProjectCPT) -> Optional[float]:
    z = cpt.data["depth_m"].to_numpy()
    return float(np.median(np.diff(z))) if len(z) > 1 else None
