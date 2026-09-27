# Author: Utkarsh Gupta
# License: GPL v3
"""
Canonical Pydantic schemas for the GeoAI shallow-foundation design tools
(``calculate_shallow_foundation_capacity`` and ``calculate_foundation_settlement``,
implemented in ``core.geoai.tools_shallow``).

Soil parameters are optional in the schema on purpose: a value the user did not give is
looked up in the current project's soil profile, and if it is not there either the tool
returns a structured missing-parameter error (AGENTS.md §5, §17). Nothing is defaulted.
"""
from typing import Any, Dict, List, Literal, Optional

from pydantic import AliasChoices

from core.geoai.schemas.base import GeoAIBaseModel, GeoAIOutputModel, GeotechnicalField

FootingShape = Literal["strip", "square", "rectangular", "circular"]


def _alias(*names: str) -> AliasChoices:
    return AliasChoices(*names)


class _FootingGeometryFields(GeoAIBaseModel):
    """Geometry fields shared by the capacity and settlement tools."""
    foundation_shape: FootingShape = GeotechnicalField(
        ...,
        description="Footing plan shape: 'strip', 'square', 'rectangular' or 'circular'",
        validation_alias=_alias("foundation_shape", "shape", "footing_shape"),
    )
    width_m: float = GeotechnicalField(
        ..., gt=0.0, le=100.0, unit="m",
        description="Footing width B (diameter for a circular footing)",
        validation_alias=_alias("width_m", "width", "B", "breadth", "diameter"),
    )
    length_m: Optional[float] = GeotechnicalField(
        None, gt=0.0, le=500.0, unit="m",
        description="Footing length L (rectangular footings only)",
        validation_alias=_alias("length_m", "length", "L"),
    )
    foundation_depth_m: float = GeotechnicalField(
        ..., ge=0.0, le=50.0, unit="m",
        description="Embedment depth Df of the footing base below ground surface",
        validation_alias=_alias("foundation_depth_m", "depth", "Df", "embedment_depth", "base_depth"),
    )


class ShallowFoundationCapacityInput(_FootingGeometryFields):
    """Ultimate vertical bearing capacity of a shallow foundation (API RP 2GEO via Groundhog)."""
    analysis: Optional[Literal["drained", "undrained"]] = GeotechnicalField(
        None,
        description="'drained' (effective stress, phi') or 'undrained' (total stress, su); "
                    "inferred from the strength parameter given when omitted",
        validation_alias=_alias("analysis", "condition", "drainage"),
    )
    friction_angle_deg: Optional[float] = GeotechnicalField(
        None, ge=20.0, le=50.0, unit="deg",
        description="Effective friction angle phi' of the soil below the base (drained; method range 20-50 deg)",
        validation_alias=_alias("friction_angle_deg", "phi", "phi_eff", "friction_angle"),
    )
    effective_cohesion_kpa: Optional[float] = GeotechnicalField(
        None, ge=0.0, le=500.0, unit="kPa",
        description="Effective cohesion c' (drained). Not used by the API RP 2GEO drained method; reported only",
        validation_alias=_alias("effective_cohesion_kpa", "c_eff", "cohesion"),
    )
    undrained_shear_strength_kpa: Optional[float] = GeotechnicalField(
        None, gt=0.0, le=2000.0, unit="kPa",
        description="Undrained shear strength su at base level (undrained)",
        validation_alias=_alias("undrained_shear_strength_kpa", "su", "su_base", "cu"),
    )
    su_increase_kpa_per_m: float = GeotechnicalField(
        0.0, ge=0.0, le=100.0, unit="kPa/m",
        description="Linear increase of su with depth below the base (0 = constant su)",
        validation_alias=_alias("su_increase_kpa_per_m", "su_increase", "k_su"),
    )
    unit_weight_kn_m3: Optional[float] = GeotechnicalField(
        None, ge=10.0, le=25.0, unit="kN/m3",
        description="Total (bulk) unit weight gamma of the soil",
        validation_alias=_alias("unit_weight_kn_m3", "gamma", "unit_weight", "bulk_unit_weight"),
    )
    saturated_unit_weight_kn_m3: Optional[float] = GeotechnicalField(
        None, ge=10.0, le=25.0, unit="kN/m3",
        description="Saturated unit weight below the water table (defaults to the total unit weight)",
        validation_alias=_alias("saturated_unit_weight_kn_m3", "gamma_sat"),
    )
    groundwater_depth_m: Optional[float] = GeotechnicalField(
        None, ge=0.0, le=200.0, unit="m",
        description="Groundwater table depth below ground surface (drained analysis)",
        validation_alias=_alias("groundwater_depth_m", "water_table_depth", "gwt", "groundwater_depth"),
    )
    vertical_load_kn: Optional[float] = GeotechnicalField(
        None, gt=0.0, unit="kN",
        description="Applied vertical load V (kN; kN per metre run for a strip). Needed with horizontal load or moments",
        validation_alias=_alias("vertical_load_kn", "vertical_load", "V"),
    )
    horizontal_load_kn: float = GeotechnicalField(
        0.0, ge=0.0, unit="kN",
        description="Applied horizontal load H (kN; kN per metre run for a strip)",
        validation_alias=_alias("horizontal_load_kn", "horizontal_load", "H"),
    )
    moment_b_knm: float = GeotechnicalField(
        0.0, ge=0.0, unit="kNm",
        description="Overturning moment giving eccentricity across the width B (kNm; kNm/m for a strip)",
        validation_alias=_alias("moment_b_knm", "moment", "moment_b", "M"),
    )
    moment_l_knm: float = GeotechnicalField(
        0.0, ge=0.0, unit="kNm",
        description="Overturning moment giving eccentricity along the length L (rectangular/square)",
        validation_alias=_alias("moment_l_knm", "moment_l"),
    )
    eccentricity_b_m: float = GeotechnicalField(
        0.0, ge=0.0, unit="m",
        description="Load eccentricity e_B across the width (alternative to moment_b_knm)",
        validation_alias=_alias("eccentricity_b_m", "eccentricity", "e_b", "eccentricity_width"),
    )
    eccentricity_l_m: float = GeotechnicalField(
        0.0, ge=0.0, unit="m",
        description="Load eccentricity e_L along the length (alternative to moment_l_knm)",
        validation_alias=_alias("eccentricity_l_m", "e_l", "eccentricity_length"),
    )
    skirted: bool = GeotechnicalField(
        False,
        description="True for a skirted foundation (overburden at base excluded); False for a base-embedded pad",
    )
    unit_weight_water_kn_m3: float = GeotechnicalField(
        10.0, ge=9.0, le=10.5, unit="kN/m3",
        description="Unit weight of water gamma_w (Groundhog convention 10 kN/m3)",
        validation_alias=_alias("unit_weight_water_kn_m3", "gamma_w"),
    )
    soil_profile: Optional[str] = GeotechnicalField(
        None,
        description="Name of the project soil profile to take missing soil parameters from (default: the active one)",
        validation_alias=_alias("soil_profile", "profile", "borehole"),
    )


class FoundationSettlementInput(_FootingGeometryFields):
    """Primary consolidation settlement of clay below a footing (Groundhog functions)."""
    applied_pressure_kpa: Optional[float] = GeotechnicalField(
        None, gt=0.0, le=5000.0, unit="kPa",
        description="Gross average bearing pressure q at the footing base (or give vertical_load_kn)",
        validation_alias=_alias("applied_pressure_kpa", "pressure", "bearing_pressure", "q", "applied_stress"),
    )
    vertical_load_kn: Optional[float] = GeotechnicalField(
        None, gt=0.0, unit="kN",
        description="Total vertical load V on the footing (kN; kN per metre run for a strip)",
        validation_alias=_alias("vertical_load_kn", "vertical_load", "V", "load"),
    )
    clay_top_depth_m: Optional[float] = GeotechnicalField(
        None, ge=0.0, le=200.0, unit="m",
        description="Depth of the top of the compressible clay layer below ground surface",
        validation_alias=_alias("clay_top_depth_m", "clay_top", "layer_top"),
    )
    clay_bottom_depth_m: Optional[float] = GeotechnicalField(
        None, gt=0.0, le=200.0, unit="m",
        description="Depth of the bottom of the compressible clay layer below ground surface",
        validation_alias=_alias("clay_bottom_depth_m", "clay_bottom", "layer_bottom"),
    )
    compression_index: Optional[float] = GeotechnicalField(
        None, gt=0.0, le=5.0, unit="-",
        description="Compression index Cc (log10)",
        validation_alias=_alias("compression_index", "Cc", "cc"),
    )
    recompression_index: Optional[float] = GeotechnicalField(
        None, gt=0.0, le=2.0, unit="-",
        description="Recompression index Cr (needed unless OCR = 1)",
        validation_alias=_alias("recompression_index", "Cr", "cr"),
    )
    initial_void_ratio: Optional[float] = GeotechnicalField(
        None, gt=0.0, le=10.0, unit="-",
        description="Initial void ratio e0 of the clay",
        validation_alias=_alias("initial_void_ratio", "e0", "void_ratio"),
    )
    preconsolidation_pressure_kpa: Optional[float] = GeotechnicalField(
        None, gt=0.0, le=5000.0, unit="kPa",
        description="Preconsolidation pressure sigma'p (constant over the layer); or give ocr",
        validation_alias=_alias("preconsolidation_pressure_kpa", "sigma_p", "pc", "preconsolidation_pressure"),
    )
    ocr: Optional[float] = GeotechnicalField(
        None, ge=1.0, le=50.0, unit="-",
        description="Overconsolidation ratio OCR (sigma'p = OCR x sigma'v0); 1 = normally consolidated",
        validation_alias=_alias("ocr", "OCR"),
    )
    mv_per_kpa: Optional[float] = GeotechnicalField(
        None, gt=0.0, le=0.1, unit="1/kPa",
        description="Coefficient of volume compressibility mv [1/kPa = m2/kN] (alternative to Cc/Cr/e0)",
        validation_alias=_alias("mv_per_kpa", "mv", "compressibility"),
    )
    unit_weight_kn_m3: Optional[float] = GeotechnicalField(
        None, ge=10.0, le=25.0, unit="kN/m3",
        description="Total (bulk) unit weight gamma of the soil",
        validation_alias=_alias("unit_weight_kn_m3", "gamma", "unit_weight", "bulk_unit_weight"),
    )
    saturated_unit_weight_kn_m3: Optional[float] = GeotechnicalField(
        None, ge=10.0, le=25.0, unit="kN/m3",
        description="Saturated unit weight below the water table (defaults to the total unit weight)",
        validation_alias=_alias("saturated_unit_weight_kn_m3", "gamma_sat"),
    )
    groundwater_depth_m: Optional[float] = GeotechnicalField(
        None, ge=0.0, le=200.0, unit="m",
        description="Groundwater table depth below ground surface",
        validation_alias=_alias("groundwater_depth_m", "water_table_depth", "gwt", "groundwater_depth"),
    )
    use_net_pressure: bool = GeotechnicalField(
        True,
        description="Subtract the overburden removed at the base (sigma_v0 at Df) from q to get the stress increase",
        validation_alias=_alias("use_net_pressure", "net_pressure"),
    )
    sublayer_thickness_m: float = GeotechnicalField(
        0.5, ge=0.05, le=5.0, unit="m",
        description="Sublayer thickness for the depth discretisation (Groundhog SettlementCalculation default 0.5 m)",
        validation_alias=_alias("sublayer_thickness_m", "dz"),
    )
    unit_weight_water_kn_m3: float = GeotechnicalField(
        10.0, ge=9.0, le=10.5, unit="kN/m3",
        description="Unit weight of water gamma_w (Groundhog convention 10 kN/m3)",
        validation_alias=_alias("unit_weight_water_kn_m3", "gamma_w"),
    )
    soil_profile: Optional[str] = GeotechnicalField(
        None,
        description="Name of the project soil profile to take missing soil parameters from (default: the active one)",
        validation_alias=_alias("soil_profile", "profile", "borehole"),
    )


class ShallowFoundationCapacityOutput(GeoAIOutputModel):
    analysis: str = GeotechnicalField(..., description="'drained' or 'undrained'")
    q_ult_kpa: float = GeotechnicalField(..., unit="kPa", description="Ultimate bearing pressure on the effective area")
    Q_ult_kn: Optional[float] = GeotechnicalField(None, unit="kN", description="Ultimate vertical capacity (finite footings)")
    Q_ult_kn_per_m: Optional[float] = GeotechnicalField(None, unit="kN/m", description="Ultimate vertical capacity per metre run (strip)")
    effective_area_m2: Optional[float] = GeotechnicalField(None, unit="m2", description="Effective base area A' (finite footings)")
    bearing_pressure_basis: str = GeotechnicalField(..., description="Whether q_ult is gross or net of the overburden")
    method: str = GeotechnicalField(..., description="Calculation method and Groundhog routine")
    footing: Dict[str, Any] = GeotechnicalField(..., description="Geometry, effective dimensions and eccentricities")
    factors: Dict[str, Any] = GeotechnicalField(..., description="Bearing capacity and correction factors used")
    stresses: Dict[str, Any] = GeotechnicalField(..., description="Stresses at base level and unit weights used")
    soil_parameters: Dict[str, Any] = GeotechnicalField(..., description="Soil parameters with value, unit and source")
    assumptions: List[str] = GeotechnicalField(..., description="Assumptions and limitations")
    warnings: List[str] = GeotechnicalField(..., description="Warnings raised during the calculation")
    note: str = GeotechnicalField(..., description="Scope note (ultimate values; factors of safety are separate)")


class FoundationSettlementOutput(GeoAIOutputModel):
    settlement_mm: float = GeotechnicalField(..., unit="mm", description="Calculated primary consolidation settlement")
    applied_pressure_kpa: float = GeotechnicalField(..., unit="kPa", description="Gross bearing pressure q at the base")
    net_pressure_kpa: float = GeotechnicalField(..., unit="kPa", description="Pressure used for the stress increase")
    method: str = GeotechnicalField(..., description="Calculation method and Groundhog routines")
    footing: Dict[str, Any] = GeotechnicalField(..., description="Footing geometry")
    compressible_layers: List[Dict[str, Any]] = GeotechnicalField(..., description="Layers, parameters and settlement per layer")
    breakdown: List[Dict[str, Any]] = GeotechnicalField(..., description="Settlement by depth interval (<= 15 rows)")
    discretisation: Dict[str, Any] = GeotechnicalField(..., description="Sublayer discretisation used")
    soil_parameters: Dict[str, Any] = GeotechnicalField(..., description="Soil parameters with value, unit and source")
    assumptions: List[str] = GeotechnicalField(..., description="Assumptions and limitations")
    warnings: List[str] = GeotechnicalField(..., description="Warnings raised during the calculation")
    note: str = GeotechnicalField(..., description="Scope note")
