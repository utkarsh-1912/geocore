# Author: Utkarsh Gupta
# License: GPL v3
"""
Curated schemas for the project-CPT retrieval tools and the CPT-based axial pile capacity
tool (core.geoai.tools_cpt_piles). Units are explicit on every numeric field (AGENTS.md §16).

Required pile inputs are never defaulted: when they are missing the input model raises a
structured ``GeoAIMissingParameterError`` naming each missing input and its unit, so the
agent asks the user instead of assuming a value (§5, §17).
"""
import re
from typing import Any, Dict, List, Literal, Optional

from pydantic import AliasChoices, field_validator, model_validator

from core.geoai.exceptions import GeoAIValidationError
from core.geoai.schemas.base import GeoAIBaseModel, GeoAIOutputModel, GeotechnicalField


class GeoAIMissingParameterError(GeoAIValidationError):
    """Required engineering inputs are missing; ``errors`` lists each one with its unit."""


PILE_TYPES = ("driven_closed_steel_pipe", "driven_open_steel_pipe", "driven_precast_concrete",
              "bored_support_fluid", "cfa")
METHODS = ("lcpc", "koppejan", "debeer")

_METHOD_SYNONYMS = {
    "lcpc": "lcpc", "bustamante": "lcpc", "bustamantegianeselli": "lcpc", "lcpcbustamantegianeselli": "lcpc",
    "koppejan": "koppejan", "nen": "koppejan", "dutch": "koppejan",
    "debeer": "debeer", "belgian": "debeer",
}
_PILE_SYNONYMS = {
    "drivenclosedsteelpipe": "driven_closed_steel_pipe", "closedendedsteelpipe": "driven_closed_steel_pipe",
    "closedsteelpipe": "driven_closed_steel_pipe", "closedendsteelpipe": "driven_closed_steel_pipe",
    "drivenclosedendedsteelpipe": "driven_closed_steel_pipe", "drivenclosedendedpipe": "driven_closed_steel_pipe",
    "drivenopensteelpipe": "driven_open_steel_pipe", "openendedsteelpipe": "driven_open_steel_pipe",
    "opensteelpipe": "driven_open_steel_pipe", "drivenopenendedsteelpipe": "driven_open_steel_pipe",
    "openendedpipe": "driven_open_steel_pipe", "openendsteelpipe": "driven_open_steel_pipe",
    "drivenprecastconcrete": "driven_precast_concrete", "precastconcrete": "driven_precast_concrete",
    "precast": "driven_precast_concrete", "drivenprecast": "driven_precast_concrete",
    "boredsupportfluid": "bored_support_fluid", "boredbentonite": "bored_support_fluid",
    "boredwithbentonite": "bored_support_fluid", "boredwithsupportfluid": "bored_support_fluid",
    "cfa": "cfa", "continuousflightauger": "cfa", "augercast": "cfa",
}


def _key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


class CPTIdInput(GeoAIBaseModel):
    cpt_id: str = GeotechnicalField(
        ..., description="CPT location id in the current project, e.g. 'CPT-03' (see list_project_cpts)",
        validation_alias=AliasChoices("cpt_id", "cpt", "cpt_name", "location_id"))


class ListProjectCPTsInput(GeoAIBaseModel):
    """No inputs: lists the CPT soundings stored in the current GeoCore project."""


class ListProjectCPTsOutput(GeoAIOutputModel):
    count: int = GeotechnicalField(..., unit="-", description="Number of usable CPT soundings")
    cpts: List[Dict[str, Any]] = GeotechnicalField(..., description="id, depth range [m], channels, location, groundwater depth [m]")
    unusable_sources: List[Dict[str, Any]] = GeotechnicalField(default_factory=list, description="CPT-like data that cannot be used, with reason")
    note: str = GeotechnicalField("", description="How the list was built")


class CPTSummaryInput(CPTIdInput):
    min_layer_thickness_m: float = GeotechnicalField(
        0.5, unit="m", ge=0.0, le=5.0,
        description="SBT intervals thinner than this are merged into a neighbour [m]")
    max_intervals: int = GeotechnicalField(
        12, unit="-", ge=1, le=15, description="Maximum number of layering intervals returned")


class CPTSummaryOutput(GeoAIOutputModel):
    cpt_id: str = GeotechnicalField(..., description="CPT id")
    depth_range_m: List[float] = GeotechnicalField(..., unit="m", description="First and last CPT depth [m]")
    n_points: int = GeotechnicalField(..., unit="-", description="Number of CPT readings")
    median_spacing_m: Optional[float] = GeotechnicalField(None, unit="m", description="Median reading spacing [m]")
    channels: List[str] = GeotechnicalField(..., description="Available channels (qc, fs, u2)")
    groundwater_depth_m: Optional[float] = GeotechnicalField(None, unit="m", description="Groundwater depth if stored with the CPT [m]")
    location: Optional[Dict[str, Any]] = GeotechnicalField(None, description="Easting/northing/ground level if stored")
    layering: List[Dict[str, Any]] = GeotechnicalField(..., description="SBT intervals with qc [MPa], fs/u2 [kPa] ranges and mean Ic")
    data_quality_flags: List[str] = GeotechnicalField(..., description="Missing channels, negative qc, gaps")
    provenance: Dict[str, Any] = GeotechnicalField(..., description="Source object, columns/units, processing method")


class PileSoilLayer(GeoAIBaseModel):
    """One explicit soil layer (overrides the CPT-derived SBT layering)."""
    depth_from_m: float = GeotechnicalField(..., unit="m", ge=0.0, le=200.0, description="Layer top depth [m]")
    depth_to_m: float = GeotechnicalField(..., unit="m", gt=0.0, le=200.0, description="Layer bottom depth [m]")
    soil_type: Optional[str] = GeotechnicalField(
        None, description="LCPC: Clay/Silt/Sand/Chalk/Gravel; De Beer: Clay, Loam (silt), Sandy clay / loam (silt), "
                          "Clayey sand / loam (silt), Sand; not used by Koppejan")
    total_unit_weight_kn_m3: Optional[float] = GeotechnicalField(
        None, unit="kN/m3", gt=5.0, le=30.0, description="Total unit weight [kN/m3]")


#: Required inputs of the pile tool: field -> (unit, description) used in the missing-parameter error.
_REQUIRED = {
    "cpt_id": ("-", "CPT location id in the current project, e.g. 'CPT-03'"),
    "method": ("-", "calculation method: lcpc, koppejan or debeer"),
    "pile_type": ("-", "pile type: " + ", ".join(PILE_TYPES)),
    "pile_diameter_m": ("m", "outer pile diameter"),
    "pile_tip_depth_m": ("m", "pile tip depth below the CPT ground level"),
}
_OPEN_ENDED = {
    "wall_thickness_mm": ("mm", "steel wall thickness of the open-ended pipe"),
    "open_end_condition": ("-", "open-ended base behaviour: coring (steel annulus only) or plugged (full base area)"),
}
_DEBEER = {
    "debeer_alpha_s": ("-", "De Beer shaft factor alpha_s for this pile type (Belgian practice, not defaulted)"),
    "debeer_alpha_b": ("-", "De Beer base factor alpha_b for this pile type (Belgian practice, not defaulted)"),
}
_SENTINELS = {"", "-", "--", "n/a", "na", "null", "nil", "undefined", "none"}


class PileCapacityFromCPTInput(GeoAIBaseModel):
    """
    Ultimate axial compression capacity of a single circular pile from a project CPT.
    """
    cpt_id: str = GeotechnicalField(
        ..., description="CPT location id in the current project, e.g. 'CPT-03'",
        validation_alias=AliasChoices("cpt_id", "cpt", "cpt_name", "location_id"))
    method: Literal["lcpc", "koppejan", "debeer"] = GeotechnicalField(
        ..., description="lcpc (Bustamante & Gianeselli 1982), koppejan, debeer (Belgian practice)")
    pile_type: Literal["driven_closed_steel_pipe", "driven_open_steel_pipe", "driven_precast_concrete",
                       "bored_support_fluid", "cfa"] = GeotechnicalField(
        ..., description="Pile type / installation (circular section)")
    pile_diameter_m: float = GeotechnicalField(
        ..., unit="m", gt=0.0, le=5.0, description="Outer pile diameter [m]",
        validation_alias=AliasChoices("pile_diameter_m", "pile_diameter", "diameter", "D"))
    pile_tip_depth_m: float = GeotechnicalField(
        ..., unit="m", gt=0.0, le=200.0, description="Pile tip depth below CPT ground level [m]",
        validation_alias=AliasChoices("pile_tip_depth_m", "tip_depth", "pile_penetration", "penetration"))
    wall_thickness_mm: Optional[float] = GeotechnicalField(
        None, unit="mm", gt=0.0, le=200.0, description="Wall thickness, open-ended pipe only [mm]")
    open_end_condition: Optional[Literal["coring", "plugged"]] = GeotechnicalField(
        None, description="Open-ended pipe base: coring (annulus) or plugged (full area)")
    shaft_start_depth_m: Optional[float] = GeotechnicalField(
        None, unit="m", ge=0.0, le=200.0,
        description="Depth where shaft resistance starts (pile head/cut-off) [m]; omitted = ground level")
    groundwater_depth_m: Optional[float] = GeotechnicalField(
        None, unit="m", ge=0.0, le=200.0, description="Groundwater depth below ground level [m] (needed for debeer)")
    debeer_alpha_s: Optional[float] = GeotechnicalField(
        None, unit="-", gt=0.0, le=2.0, description="De Beer shaft factor alpha_s (debeer only)")
    debeer_alpha_b: Optional[float] = GeotechnicalField(
        None, unit="-", gt=0.0, le=2.0, description="De Beer base factor alpha_b (debeer only)")
    soil_layers: Optional[List[PileSoilLayer]] = GeotechnicalField(
        None, description="Optional explicit layering from 0 m to the CPT end; default = CPT SBT layering")

    @model_validator(mode="before")
    @classmethod
    def _report_missing_inputs(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        accepted = cls.geoai_accepted_keys()
        given: Dict[str, Any] = {}
        for k, v in data.items():
            name = accepted.get(k)
            if name is None:
                continue
            if v is None or (isinstance(v, str) and v.strip().lower() in _SENTINELS):
                continue
            given[name] = v
        required = dict(_REQUIRED)
        if _key(given.get("pile_type", "")) in ("drivenopensteelpipe",) or \
                _PILE_SYNONYMS.get(_key(given.get("pile_type", ""))) == "driven_open_steel_pipe":
            required.update(_OPEN_ENDED)
        if _METHOD_SYNONYMS.get(_key(given.get("method", ""))) == "debeer":
            required.update(_DEBEER)
        missing = [f for f in required if f not in given]
        if missing:
            details = [{"field": f, "type": "missing_parameter", "unit": required[f][0],
                        "description": required[f][1]} for f in missing]
            listing = "; ".join(f"{f} [{required[f][0]}] - {required[f][1]}" for f in missing)
            raise GeoAIMissingParameterError(
                f"Missing required input(s): {listing}. Ask the user for these values; do not assume them.",
                errors=details)
        return data

    @field_validator("method", mode="before")
    @classmethod
    def _method_synonyms(cls, v: Any) -> Any:
        return _METHOD_SYNONYMS.get(_key(v), v) if isinstance(v, str) else v

    @field_validator("pile_type", mode="before")
    @classmethod
    def _pile_synonyms(cls, v: Any) -> Any:
        return _PILE_SYNONYMS.get(_key(v), v) if isinstance(v, str) else v

    @field_validator("open_end_condition", mode="before")
    @classmethod
    def _open_end_lower(cls, v: Any) -> Any:
        return v.strip().lower() if isinstance(v, str) else v


class PileCapacityFromCPTOutput(GeoAIOutputModel):
    cpt_id: str = GeotechnicalField(..., description="CPT used")
    method: str = GeotechnicalField(..., description="Calculation method")
    method_reference: str = GeotechnicalField(..., description="Method reference")
    groundhog_class: str = GeotechnicalField(..., description="Groundhog class that performed the calculation")
    ultimate_shaft_resistance_kn: float = GeotechnicalField(..., unit="kN", description="Ultimate shaft resistance Rs [kN]")
    ultimate_base_resistance_kn: float = GeotechnicalField(..., unit="kN", description="Ultimate base resistance Rb [kN]")
    ultimate_total_resistance_kn: float = GeotechnicalField(..., unit="kN", description="Ultimate compression resistance Rc = Rs + Rb [kN]")
    pile: Dict[str, Any] = GeotechnicalField(..., description="Pile geometry used (m, m2, mm)")
    base_details: Dict[str, Any] = GeotechnicalField(..., description="Unit base resistance and averaging values")
    shaft_breakdown: List[Dict[str, Any]] = GeotechnicalField(..., description="Per-layer shaft contribution (<= 15 rows)")
    method_factors: Dict[str, Any] = GeotechnicalField(..., description="Factors taken for the pile type")
    soil_layering_source: str = GeotechnicalField(..., description="Where the soil layering came from")
    cpt_depth_range_m: List[float] = GeotechnicalField(..., unit="m", description="CPT depth range [m]")
    cpt_depth_used_m: List[float] = GeotechnicalField(..., unit="m", description="CPT depth range used [m]")
    groundwater_depth_m: Optional[float] = GeotechnicalField(None, unit="m", description="Groundwater depth used [m]")
    assumptions: List[str] = GeotechnicalField(..., description="Assumptions made")
    warnings: List[str] = GeotechnicalField(default_factory=list, description="Warnings and data-quality flags")
    provenance: Dict[str, Any] = GeotechnicalField(..., description="CPT source and processing")
    scope_note: str = GeotechnicalField(..., description="What the result is and is not")
