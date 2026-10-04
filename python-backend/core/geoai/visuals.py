# Author: Utkarsh Gupta
# License: GPL v3
"""
Display blocks (tables, charts, notes) built deterministically from GeoAI tool results.

The chat UI renders these next to the model's answer (AGENTS.md §22): the user sees the tool's
own numbers as tables and plots, never numbers re-typed by the model (§5, §6). Visuals go to the
UI only; they are not added to the model's prompt, so they may carry data the model must not see
in full, such as a decimated CPT trace (§9).

Block types (all JSON-serialisable; every block carries ``tool`` and ``detail``, true for
secondary blocks the UI may collapse):

- ``metrics``        {"title", "items": [{"label", "value", "unit"}]}
- ``table``          {"title", "columns": [{"key", "label", "unit"}], "rows": [[...]], "truncated": int}
- ``notes``          {"title", "tone": "info"|"warning", "items": [str]}
- ``depth_profile``  {"title", "tracks": [{"title", "unit", "series": [...]}], "bands": [...], "markers": [...],
                      "note"}; a series is {"name", "kind": "line", "depth", "value"} or
                      {"name", "kind": "intervals", "top", "bottom", "value"}
- ``xy``             {"title", "x": {"label", "unit"}, "y": {"label", "unit"}, "series": [{"name", "x", "y"}]}
"""
import logging
import math
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

MAX_TABLE_ROWS = 60
MAX_METRIC_TEXT = 80
# A CPT trace is decimated to at most this many points per channel for display (and storage
# in the saved conversation).
MAX_PROFILE_POINTS = 400
MAX_PROFILE_TRACKS = 3

# Unit suffixes used by GeoAI tool output keys (e.g. q_ult_kpa, pile_tip_depth_m).
_UNIT_SUFFIXES = [
    ("_kn_per_m", "kN/m"), ("_kn_m3", "kN/m³"), ("_kn_m", "kN/m"), ("_m2", "m²"), ("_m3", "m³"),
    ("_kpa", "kPa"), ("_mpa", "MPa"), ("_kn", "kN"), ("_mm", "mm"), ("_m", "m"),
    ("_deg", "°"), ("_pct", "%"), ("_s", "s"),
]
# Groundhog-style keys carry the unit in brackets: "Gmax [kPa]".
_BRACKET_UNIT = re.compile(r"^(.*?)\s*\[([^\]]*)\]\s*$")
# Interval columns that turn a table into a depth profile.
_DEPTH_PAIRS = [("depth_from_m", "depth_to_m"), ("z_top_m", "z_bottom_m")]
_WARNING_KEYS = {"warnings", "data_quality_flags"}
_NOTE_KEYS = _WARNING_KEYS | {"assumptions", "notes"}
# Top-level keys that hold bookkeeping rather than results.
_SKIP_KEYS = {"provenance", "_provenance"}


def split_unit(key: str, output_units: Optional[Dict[str, str]] = None) -> Tuple[str, Optional[str]]:
    """Display label and unit of a result key ("q_ult_kpa" -> ("q ult", "kPa"))."""
    unit = (output_units or {}).get(key)
    m = _BRACKET_UNIT.match(key)
    if m:
        return m.group(1).strip(), unit or m.group(2).strip() or None
    for suffix, suffix_unit in _UNIT_SUFFIXES:
        if key.lower().endswith(suffix) and len(key) > len(suffix):
            return key[: -len(suffix)].replace("_", " "), unit or suffix_unit
    return key.replace("_", " "), unit


def _title(key: str) -> str:
    label = key.replace("_", " ").strip()
    return label[:1].upper() + label[1:]


def _is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v))


def _is_scalar(v: Any) -> bool:
    return v is None or isinstance(v, (str, bool)) or _is_number(v)


def _is_stats(v: Any) -> bool:
    return isinstance(v, dict) and set(v) == {"min", "mean", "max"}


def _fmt_num(v: Any) -> str:
    return "–" if v is None else f"{float(v):.4g}"


def _cell(v: Any) -> Any:
    """A table cell: scalars stay as they are; min/mean/max stats and lists become text."""
    if _is_scalar(v):
        return v
    if _is_stats(v):
        return f"{_fmt_num(v['mean'])} ({_fmt_num(v['min'])}–{_fmt_num(v['max'])})"
    if isinstance(v, (list, tuple)) and all(_is_scalar(x) for x in v):
        return ", ".join("–" if x is None else str(x) for x in v)
    return str(v)


def _range_value(v: Any) -> Optional[str]:
    if isinstance(v, (list, tuple)) and len(v) == 2 and all(_is_number(x) for x in v):
        return f"{_fmt_num(v[0])} – {_fmt_num(v[1])}"
    return None


def metrics_block(title: str, values: Dict[str, Any], tool: str,
                  output_units: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
    items = []
    for key, v in values.items():
        label, unit = split_unit(key, output_units)
        if unit == "-":
            unit = None
        rng = _range_value(v)
        if rng is not None:
            items.append({"label": label, "value": rng, "unit": unit})
        elif _is_scalar(v) and v is not None:
            items.append({"label": label, "value": v, "unit": unit})
    return {"type": "metrics", "tool": tool, "title": title, "items": items} if items else None


def table_block(title: str, rows: List[Dict[str, Any]], tool: str) -> Optional[Dict[str, Any]]:
    """Table from a list of dicts (keys in first-seen order); long tables are truncated."""
    keys: List[str] = []
    for r in rows:
        keys.extend(k for k in r if not k.startswith("_") and k not in keys)
    if not keys:
        return None
    columns = []
    for k in keys:
        label, unit = split_unit(k)
        if any(_is_stats(r.get(k)) for r in rows):
            label += " mean (range)"
        columns.append({"key": k, "label": label, "unit": unit})
    shown = rows[:MAX_TABLE_ROWS]
    return {"type": "table", "tool": tool, "title": title, "columns": columns,
            "rows": [[_cell(r.get(k)) for k in keys] for r in shown],
            "truncated": len(rows) - len(shown)}


def kv_table_block(title: str, values: Dict[str, Any], tool: str) -> Optional[Dict[str, Any]]:
    """Two-column Parameter / Value table for a nested dict (pile geometry, method factors...)."""
    rows = []
    for k, v in values.items():
        if k.startswith("_") or isinstance(v, dict) and not _is_stats(v):
            continue
        label, unit = split_unit(k)
        rows.append([label, _cell(v), unit or ""])
    if not rows:
        return None
    return {"type": "table", "tool": tool, "title": title,
            "columns": [{"key": "parameter", "label": "Parameter", "unit": None},
                        {"key": "value", "label": "Value", "unit": None},
                        {"key": "unit", "label": "Unit", "unit": None}],
            "rows": rows, "truncated": 0}


def notes_block(title: str, items: List[Any], tool: str, tone: str = "info") -> Optional[Dict[str, Any]]:
    texts = [str(x) for x in items if x not in (None, "")]
    return {"type": "notes", "tool": tool, "title": title, "tone": tone, "items": texts} if texts else None


def interval_profile_block(title: str, rows: List[Dict[str, Any]], tool: str) -> Optional[Dict[str, Any]]:
    """
    Depth profile from rows with a depth interval (depth_from_m/depth_to_m or z_top_m/z_bottom_m):
    one step-plot track per numeric (or min/mean/max) column, at most MAX_PROFILE_TRACKS.
    """
    if len(rows) < 2:
        return None
    pair = next((p for p in _DEPTH_PAIRS if all(_is_number(r.get(p[0])) and _is_number(r.get(p[1]))
                                                for r in rows)), None)
    if pair is None:
        return None
    top = [float(r[pair[0]]) for r in rows]
    bottom = [float(r[pair[1]]) for r in rows]
    tracks = []
    for key in rows[0]:
        # sbt_zone is categorical and merged_layers bookkeeping: neither is a quantity to plot.
        if key in pair or key.startswith("_") or key in ("sbt_zone", "merged_layers")                 or len(tracks) >= MAX_PROFILE_TRACKS:
            continue
        col = [r.get(key) for r in rows]
        if all(_is_stats(v) for v in col):
            values = [v["mean"] for v in col]
        elif all(_is_number(v) or v is None for v in col) and any(_is_number(v) for v in col):
            values = col
        else:
            continue
        label, unit = split_unit(key)
        tracks.append({"title": label, "unit": unit,
                       "series": [{"name": label, "kind": "intervals", "top": top, "bottom": bottom,
                                   "value": values}]})
    if not tracks:
        return None
    return {"type": "depth_profile", "tool": tool, "title": title, "tracks": tracks, "bands": [], "markers": []}


def xy_block(title: str, arrays: Dict[str, List[float]], tool: str,
             output_units: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
    """Line chart of equal-length numeric arrays: the first array is x, the rest are series."""
    keys = list(arrays)
    if len(keys) < 2:
        return None
    x_label, x_unit = split_unit(keys[0], output_units)
    series = []
    y_units = set()
    for k in keys[1:]:
        label, unit = split_unit(k, output_units)
        y_units.add(unit)
        series.append({"name": label, "x": arrays[keys[0]], "y": arrays[k]})
    y_unit = y_units.pop() if len(y_units) == 1 else None
    return {"type": "xy", "tool": tool, "title": title,
            "x": {"label": x_label, "unit": x_unit},
            "y": {"label": series[0]["name"] if len(series) == 1 else "", "unit": y_unit},
            "series": series}


def generic_visuals(tool: str, result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Blocks for any tool result dict, by the shape of each value."""
    prov = result.get("_provenance") if isinstance(result.get("_provenance"), dict) else {}
    units = prov.get("output_units") if isinstance(prov.get("output_units"), dict) else {}
    scalars: Dict[str, Any] = {}
    arrays: Dict[str, List[float]] = {}
    blocks: List[Dict[str, Any]] = []
    notes: List[Dict[str, Any]] = []

    for key, v in result.items():
        if key.startswith("_") or key in _SKIP_KEYS:
            continue
        if isinstance(v, str) and len(v) > MAX_METRIC_TEXT:
            notes.append(notes_block(_title(key), [v], tool))
        elif _is_scalar(v) or _range_value(v) is not None:
            scalars[key] = v
        elif isinstance(v, list) and v and all(isinstance(x, str) and 0 < len(x) <= 20 and " " not in x
                                               for x in v) and key not in _NOTE_KEYS:
            scalars[key] = ", ".join(v)  # e.g. channels: qc, fs, u2
        elif isinstance(v, dict):
            if v and all(_is_scalar(x) or _is_stats(x) or isinstance(x, list) for x in v.values()):
                blocks.append(kv_table_block(_title(key), v, tool))
        elif isinstance(v, list) and v:
            if all(isinstance(x, dict) for x in v):
                blocks.append(interval_profile_block(_title(key), v, tool))
                blocks.append(table_block(_title(key), v, tool))
            elif all(isinstance(x, str) for x in v):
                notes.append(notes_block(_title(key), v, tool,
                                         tone="warning" if key in _WARNING_KEYS else "info"))
            elif len(v) >= 3 and all(_is_number(x) for x in v):
                arrays[key] = [float(x) for x in v]

    out = [metrics_block("Results", scalars, tool, units)]
    # Groundhog functions that return curves give several equal-length arrays.
    if arrays:
        lengths = {len(a) for a in arrays.values()}
        if len(lengths) == 1 and len(arrays) >= 2:
            out.append(xy_block(_title(tool), arrays, tool, units))
        else:
            out.extend(table_block(_title(k), [{"index": i, k: x} for i, x in enumerate(a)], tool)
                       for k, a in arrays.items())
    return [b for b in out + blocks + notes if b]


# --------------------------------------------------------------------------- tool-specific additions

def _decimate(n: int, limit: int = MAX_PROFILE_POINTS) -> int:
    return max(1, int(math.ceil(n / limit)))


def _cpt_trace_block(tool: str, cpt_id: str, result: Dict[str, Any],
                     max_depth: Optional[float] = None, title: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """qc / fs / u2 against depth from the project CPT itself, with SBT layers as bands."""
    from core.geoai import project_cpt
    from core.geoai.tools_cpt_piles import _store
    cpt = project_cpt.resolve_cpt(cpt_id, _store())
    data = cpt.data.sort_values("depth_m")
    if max_depth is not None:
        data = data[data["depth_m"] <= max_depth]
    if data.empty:
        return None
    step = _decimate(len(data))
    shown = data.iloc[::step]
    depth = [round(float(z), 3) for z in shown["depth_m"]]

    def series(col: str) -> List[Optional[float]]:
        return [None if not math.isfinite(float(v)) else round(float(v), 4) for v in shown[col]]

    tracks = [{"title": "qc", "unit": "MPa", "series": [{"name": "qc", "kind": "line", "depth": depth,
                                                          "value": series("qc_mpa")}]}]
    for ch in ("fs", "u2"):
        if ch in cpt.channels():
            tracks.append({"title": ch, "unit": "kPa", "series": [{"name": ch, "kind": "line", "depth": depth,
                                                                   "value": series(f"{ch}_kpa")}]})
    bands = [{"top": lay["depth_from_m"], "bottom": lay["depth_to_m"], "label": lay.get("sbt", "")}
             for lay in result.get("layering") or [] if _is_number(lay.get("depth_from_m"))]
    markers = []
    if _is_number(cpt.groundwater_depth_m):
        markers.append({"depth": cpt.groundwater_depth_m, "label": "Groundwater"})
    note = f"{cpt.cpt_id}: {len(data)} points" + (f", every {step}th point shown" if step > 1 else "")
    return {"type": "depth_profile", "tool": tool, "title": title or f"{cpt.cpt_id} profile",
            "tracks": tracks, "bands": bands, "markers": markers, "note": note}


def _cpt_summary_visuals(tool: str, args: Dict[str, Any], result: Dict[str, Any]) -> List[Dict[str, Any]]:
    trace = _cpt_trace_block(tool, result.get("cpt_id") or args.get("cpt_id"), result)
    # The layering table stays; its step profile would duplicate the trace.
    rest = [b for b in generic_visuals(tool, result)
            if not (b["type"] == "depth_profile" and b["title"] == "Layering")]
    return ([trace] if trace else []) + rest


def _pile_capacity_visuals(tool: str, args: Dict[str, Any], result: Dict[str, Any]) -> List[Dict[str, Any]]:
    blocks = generic_visuals(tool, result)
    tip = result.get("pile", {}).get("tip_depth_m") if isinstance(result.get("pile"), dict) else None
    if not _is_number(tip):
        return blocks
    trace = _cpt_trace_block(tool, result.get("cpt_id") or args.get("cpt_id"), {},
                             max_depth=float(tip) + 2.0, title=f"{result.get('cpt_id')} qc and pile tip")
    if trace:
        # One depth axis: the measured qc next to the per-layer shaft results (whose own qc mean
        # track would repeat the trace).
        trace["tracks"] = trace["tracks"][:1]
        trace["markers"].append({"depth": float(tip), "label": "Pile tip"})
        breakdown = next((b for b in blocks if b["type"] == "depth_profile"), None)
        if breakdown:
            blocks.remove(breakdown)
            trace["tracks"] += [t for t in breakdown["tracks"] if not t["title"].startswith("qc")]
        blocks.insert(1, trace)
    return blocks


_SPECIFIC: Dict[str, Callable[[str, Dict[str, Any], Dict[str, Any]], List[Dict[str, Any]]]] = {
    "get_cpt_summary": _cpt_summary_visuals,
    "calculate_pile_capacity_from_cpt": _pile_capacity_visuals,
}


def _mark_details(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Flag secondary blocks (parameter tables, informational notes) with ``detail: True`` so the UI
    can collapse them; results, charts, data tables and warnings stay visible.
    """
    for b in blocks:
        kv_table = b["type"] == "table" and [c["key"] for c in b["columns"]] == ["parameter", "value", "unit"]
        b["detail"] = kv_table or (b["type"] == "notes" and b.get("tone") != "warning")
    return blocks


def build_visuals(tool_name: str, arguments: Optional[Dict[str, Any]], wrapper: Any) -> List[Dict[str, Any]]:
    """
    Display blocks for one executed tool call (``wrapper`` as returned by the agent:
    {"status", "result" | "error"}). Failed calls get none (the answer explains the error).
    Never raises: a visual is a convenience, so a failure here must not fail the chat turn.
    """
    if not isinstance(wrapper, dict) or wrapper.get("status") != "success":
        return []
    result = wrapper.get("result")
    if not isinstance(result, dict):
        result = {"result": result}
    try:
        specific = _SPECIFIC.get(tool_name)
        if specific:
            return _mark_details(specific(tool_name, arguments or {}, result))
        return _mark_details(generic_visuals(tool_name, result))
    except Exception as e:
        logger.warning(f"GeoAI: visuals for {tool_name} failed: {e}")
        try:
            return _mark_details(generic_visuals(tool_name, result))
        except Exception:
            return []
