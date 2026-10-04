# Author: Utkarsh Gupta
# License: GPL v3
"""
Project soil-parameter lookup with provenance for GeoAI calculation tools (AGENTS.md §9, §14, §17).

A tool that is missing a soil parameter asks this module for a representative value from the
current project's soil profile (``ProjectContext`` / ``SoilProfileAccessor`` in
``core.geoai.data_access``). Every value comes back with its source ("project profile 'BH-01':
layer 3 'Soft Clay' (2.5-5.0 m)"), or with the reason it is not available, so the tool can either
report the provenance or return a structured missing-parameter error. Nothing is defaulted.

Rules (deterministic):

* Column names are matched after normalisation (lower case, units in brackets and non-alphanumerics
  removed) against ``context_resolver.PROPERTY_SYNONYMS`` plus the aliases below, so both
  ``'Friction angle [deg]'`` and ``'FrictionAngle [deg]'`` are recognised.
* Column units in brackets are converted with ``core.geoai.units``; an unverifiable unit makes the
  value unavailable (never guessed). A column without a unit (or ``[-]``) is read in the expected unit
  and the source says so.
* A representative value over a depth interval is the thickness-weighted mean of the layers that
  overlap it. Zero or negative strength/compressibility values mean "not defined for this layer"
  (e.g. phi' = 0 in a clay layer). The parameter must be defined over the whole interval; otherwise
  the value is unavailable and the reason names the layers that lack it.
"""
import re
from dataclasses import dataclass, asdict
from typing import Any, Callable, Dict, List, Optional, Tuple

from core.geoai.context_resolver import PROPERTY_SYNONYMS

_TOL = 1e-6


@dataclass
class ResolvedValue:
    """A calculation input with its unit and source (user input or project profile)."""
    value: float
    unit: str
    source: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["value"] = round_sig(self.value)
        return d


def round_sig(x: Any, sig: int = 5) -> Any:
    """Round a float to ``sig`` significant figures (compact tool outputs); other values unchanged."""
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return x
    x = float(x)
    if x == 0.0 or x != x:
        return x
    from math import floor, log10
    return round(x, sig - 1 - int(floor(log10(abs(x)))))


def normalise_name(name: str) -> str:
    """'Friction angle [deg]' -> 'frictionangle'; 'UnitWeight [kN_m3]' -> 'unitweight'."""
    return re.sub(r"[^a-z0-9]", "", str(name).split("[")[0].lower())


def bracket_unit(name: str) -> str:
    """Unit written in a column name ('UnitWeight [kN_m3]' -> 'kN/m3'); '' when absent."""
    m = re.search(r"\[([^\]]*)\]", str(name))
    return m.group(1).strip().replace("_", "/") if m else ""


def _names(*groups: List[str]) -> frozenset:
    return frozenset(normalise_name(n) for g in groups for n in g)


#: Canonical parameter -> normalised column names that hold it.
PARAMETER_COLUMNS: Dict[str, frozenset] = {
    "friction_angle": _names(PROPERTY_SYNONYMS["phi_eff"], ["FrictionAngle", "effective friction angle"]),
    "effective_cohesion": _names(PROPERTY_SYNONYMS["c_eff"]),
    "undrained_shear_strength": _names(PROPERTY_SYNONYMS["su"],
                                       ["UndrainedCohesion", "undrained shear strength", "cu"]),
    "unit_weight": _names(PROPERTY_SYNONYMS["gamma"], ["UnitWeight", "total unit weight", "bulk unit weight"]),
    "saturated_unit_weight": _names(["saturated unit weight", "gamma_sat", "SaturatedUnitWeight"]),
    "compression_index": _names(["Cc", "compression index", "CompressionIndex"]),
    "recompression_index": _names(["Cr", "recompression index", "RecompressionIndex"]),
    # Not PROPERTY_SYNONYMS["void_ratio"]: its bare 'e' would also match a modulus column 'E [MPa]'.
    "initial_void_ratio": _names(["e0", "initial void ratio", "InitialVoidRatio", "void ratio"]),
    "ocr": _names(["OCR", "overconsolidation ratio"]),
    "preconsolidation_pressure": _names(["pc", "preconsolidation pressure", "sigma_p", "PreconsolidationPressure"]),
    "mv": _names(["mv", "coefficient of volume compressibility", "volume compressibility"]),
    "groundwater_depth": _names(["WaterTable", "water table", "water table depth", "groundwater depth",
                                 "groundwater level", "gwt", "water level"]),
}

_SOIL_NAME_COLUMNS = frozenset({"soiltype", "soildescription", "description", "soilname", "soil",
                                "lithology", "stratum", "unit", "geologicalunit"})

#: Compressibility units outside the core unit taxonomy (-> 1/kPa).
_MV_UNITS = {"1/kpa": 1.0, "m2/kn": 1.0, "m^2/kn": 1.0, "1/mpa": 1e-3, "m2/mn": 1e-3, "m^2/mn": 1e-3}


def convert_column_value(raw: Any, column: str, expected_unit: str) -> Tuple[Optional[float], str]:
    """(value in ``expected_unit`` or None, note) for a numeric profile cell."""
    from core.geoai.units import convert_unit, normalize_unit_str
    from core.geoai.exceptions import GeoAIValidationError
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None, f"non-numeric value in column '{column}'"
    if value != value:  # NaN
        return None, f"no value in column '{column}'"
    unit = bracket_unit(column)
    if not unit or unit == "-":
        note = "" if expected_unit == "-" else f"column '{column}' states no unit; read as {expected_unit}"
        return value, note
    if expected_unit == "1/kPa":
        factor = _MV_UNITS.get(normalize_unit_str(unit))
        if factor is None:
            return None, f"unit '{unit}' of column '{column}' cannot be verified as 1/kPa"
        return value * factor, ""
    try:
        return float(convert_unit(value, unit, expected_unit, field_name=column)), ""
    except GeoAIValidationError:
        return None, f"unit '{unit}' of column '{column}' cannot be converted to {expected_unit}"


def load_project_context() -> Any:
    """The current project: the active GeoAI project context, else the saved workspace soil profiles."""
    from core.geoai.data_access import ProjectContext, active_project_context, recorded_groundwater_depth
    if active_project_context.list_profile_names():
        active_project_context.water_table_depth = recorded_groundwater_depth()
        return active_project_context
    return ProjectContext.from_state_manager()


class ProjectSoil:
    """Lazy, read-only view of one soil profile of the current project, with provenance."""

    def __init__(self, profile_name: Optional[str] = None,
                 context_loader: Optional[Callable[[], Any]] = None):
        self._profile_name = profile_name
        self._loader = context_loader or load_project_context
        self._loaded = False
        self.layers: List[Dict[str, Any]] = []
        self.name: Optional[str] = None
        self.unavailable_reason: Optional[str] = None
        self.other_profiles: List[str] = []
        self.project_water_table: Optional[float] = None

    # ------------------------------------------------------------------ loading
    def _load(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        try:
            ctx = self._loader()
        except Exception as exc:  # the project is optional: report, never fail the tool here
            self.unavailable_reason = f"the current project could not be read ({exc})"
            return
        # The recorded groundwater level is project-wide: usable even without a soil profile.
        self.project_water_table = getattr(ctx, "water_table_depth", None)
        names = list(ctx.list_profile_names()) if ctx is not None else []
        if not names:
            self.unavailable_reason = "no soil profile is loaded in the current project"
            return
        if self._profile_name and self._profile_name not in names:
            self.unavailable_reason = (f"soil profile '{self._profile_name}' is not in the current project "
                                       f"(available: {', '.join(names)})")
            return
        self.name = self._profile_name or names[0]
        self.other_profiles = [n for n in names if n != self.name]
        try:
            accessor = ctx.get_profile(self.name)
            self.layers = accessor.get_stratigraphy_summary()
            self._add_soil_names(accessor.layer_table)
        except Exception as exc:
            self.unavailable_reason = f"soil profile '{self.name}' could not be read ({exc})"
            return
        if not self.layers:
            self.unavailable_reason = f"soil profile '{self.name}' has no layers"

    def _add_soil_names(self, table: Any) -> None:
        """Use a descriptive text column ('SoilType', 'Soil description', ...) for layer labels."""
        name_cols = [c for c in getattr(table, "columns", []) if normalise_name(c) in _SOIL_NAME_COLUMNS]
        if not name_cols or len(table) != len(self.layers):
            return
        for layer, (_, row) in zip(self.layers, table.iterrows()):
            text = row[name_cols[0]]
            if isinstance(text, str) and text.strip():
                layer["soil_type"] = text.strip()

    @property
    def available(self) -> bool:
        self._load()
        return self.unavailable_reason is None

    def profile_note(self) -> Optional[str]:
        """Warning text when the profile was chosen among several."""
        self._load()
        if self.name and self.other_profiles:
            return (f"Project soil parameters were taken from profile '{self.name}'; the project also has "
                    f"{', '.join(self.other_profiles)} (pass soil_profile to choose another).")
        return None

    # ------------------------------------------------------------------ lookups
    @staticmethod
    def layer_label(layer: Dict[str, Any]) -> str:
        return (f"layer {layer.get('layer')} '{layer.get('soil_type', 'Soil')}' "
                f"({layer['z_from']:g}-{layer['z_to']:g} m)")

    @staticmethod
    def find_column(layer: Dict[str, Any], parameter: str) -> Optional[str]:
        wanted = PARAMETER_COLUMNS[parameter]
        for col in layer:
            if col in ("layer", "z_from", "z_to", "soil_type"):
                continue
            if normalise_name(col) in wanted:
                return col
        return None

    def layer_value(self, layer: Dict[str, Any], parameter: str, unit: str,
                    positive: bool = True) -> Tuple[Optional[float], str]:
        """(value, note) of ``parameter`` in one layer; value None when not defined there."""
        col = self.find_column(layer, parameter)
        if col is None:
            return None, "no column"
        value, note = convert_column_value(layer[col], col, unit)
        if value is not None and positive and value <= 0.0:
            return None, "not defined (value <= 0)"
        return value, note

    def representative(self, parameter: str, z_top: float, z_bottom: float, unit: str,
                       positive: bool = True) -> Tuple[Optional[ResolvedValue], str]:
        """Thickness-weighted value of ``parameter`` over [z_top, z_bottom] (m below ground surface)."""
        self._load()
        if self.unavailable_reason:
            return None, self.unavailable_reason
        span = z_bottom - z_top
        if span <= _TOL:
            return None, f"empty depth interval {z_top:g}-{z_bottom:g} m"
        covered, weighted, used, lacking, notes = 0.0, 0.0, [], [], []
        for layer in self.layers:
            dz = min(z_bottom, layer["z_to"]) - max(z_top, layer["z_from"])
            if dz <= _TOL:
                continue
            value, note = self.layer_value(layer, parameter, unit, positive)
            if value is None:
                lacking.append(f"{self.layer_label(layer)}: {note}")
                continue
            if note:
                notes.append(note)
            covered += dz
            weighted += value * dz
            used.append((layer, value))
        interval = f"{z_top:g}-{z_bottom:g} m"
        if covered < span - _TOL:
            parts = [f"'{parameter}' is not defined over the whole interval {interval} of profile '{self.name}'"]
            if lacking:
                parts.append("lacking in " + "; ".join(lacking))
            deepest = max(l["z_to"] for l in self.layers)
            if deepest < z_bottom - _TOL:
                parts.append(f"the profile ends at {deepest:g} m")
            return None, ", ".join(parts)
        value = weighted / covered
        if len(used) == 1:
            where = self.layer_label(used[0][0])
        else:
            where = (f"thickness-weighted over {interval} from "
                     + ", ".join(f"{self.layer_label(l)} = {round_sig(v, 4):g}" for l, v in used))
        source = f"project profile '{self.name}': {where}"
        if notes:
            source += " [" + "; ".join(dict.fromkeys(notes)) + "]"
        return ResolvedValue(value, unit, source), ""

    def groundwater_depth(self) -> Tuple[Optional[ResolvedValue], str]:
        """
        Groundwater depth [m]: a water-table column holding one value for the whole profile,
        else the recorded project groundwater level.
        """
        from core.geoai.data_access import GROUNDWATER_PROVENANCE
        self._load()
        if self.unavailable_reason:
            if self.project_water_table is not None:
                return ResolvedValue(float(self.project_water_table), "m", GROUNDWATER_PROVENANCE), ""
            return None, self.unavailable_reason
        values, column = set(), None
        for layer in self.layers:
            col = self.find_column(layer, "groundwater_depth")
            if col is None:
                continue
            value, _ = convert_column_value(layer[col], col, "m")
            if value is not None:
                values.add(round(value, 6))
                column = col
        if not values:
            if self.project_water_table is not None:
                return ResolvedValue(float(self.project_water_table), "m", GROUNDWATER_PROVENANCE), ""
            return None, f"profile '{self.name}' has no groundwater (water table) column"
        if len(values) > 1:
            return None, f"profile '{self.name}' column '{column}' holds different water-table values {sorted(values)}"
        depth = values.pop()
        note = "" if bracket_unit(column) not in ("", "-") else " (no unit stated; read as depth below ground in m)"
        return ResolvedValue(depth, "m", f"project profile '{self.name}': column '{column}'{note}"), ""

    def unit_weight_segments(self, z_bottom: float) -> Tuple[Optional[List[Tuple[float, float, float]]], str]:
        """[(top, bottom, gamma kN/m3)] covering 0..z_bottom from the profile's per-layer unit weights."""
        self._load()
        if self.unavailable_reason:
            return None, self.unavailable_reason
        segments, lacking = [], []
        for layer in self.layers:
            top, bottom = max(0.0, layer["z_from"]), min(z_bottom, layer["z_to"])
            if bottom - top <= _TOL:
                continue
            value, note = self.layer_value(layer, "unit_weight", "kN/m3")
            if value is None:
                lacking.append(f"{self.layer_label(layer)}: {note}")
                continue
            segments.append((top, bottom, value))
        covered = sum(b - t for t, b, _ in segments)
        if covered < z_bottom - _TOL:
            reason = f"unit weight is not defined from 0 to {z_bottom:g} m in profile '{self.name}'"
            if lacking:
                reason += ": lacking in " + "; ".join(lacking)
            return None, reason
        return segments, ""

    def compressible_layers(self, below_depth: float) -> List[Dict[str, Any]]:
        """Profile layers extending below ``below_depth`` that define Cc or mv (> 0)."""
        self._load()
        if self.unavailable_reason:
            return []
        found = []
        for layer in self.layers:
            if layer["z_to"] <= below_depth + _TOL:
                continue
            cc, _ = self.layer_value(layer, "compression_index", "-")
            mv, _ = self.layer_value(layer, "mv", "1/kPa")
            if cc is not None or mv is not None:
                found.append(layer)
        return found
