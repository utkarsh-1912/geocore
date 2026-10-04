# Author: Utkarsh Gupta
# License: GPL v3
"""
Input schemas for the Indian Standard (BIS) calculations in core.standards.bis.

Registered in SCHEMA_REGISTRY under the function names, so they validate the desktop forms and are
the GeoAI tool schemas (core.geoai.schema_factory.populate_full_coverage). Field names equal the
function parameters; units are explicit and normalised by GeoAIBaseModel (AGENTS.md §16).
"""
from typing import Any, Literal, Optional, get_args, get_origin, Union

from pydantic import model_validator

from core.geoai.schemas.base import GeoAIBaseModel, GeotechnicalField


def _literal_options(annotation: Any):
    if get_origin(annotation) is Union:
        for arg in get_args(annotation):
            if get_origin(arg) is Literal:
                return get_args(arg)
    if get_origin(annotation) is Literal:
        return get_args(annotation)
    return None


class _BISInput(GeoAIBaseModel):
    """Accepts text options case-, space- and hyphen-insensitively ('Square', 'plastic clay')."""

    @model_validator(mode='before')
    @classmethod
    def _normalise_options(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        out = dict(data)
        for name, field in cls.model_fields.items():
            options = _literal_options(field.annotation)
            value = out.get(name)
            if options and isinstance(value, str):
                key = value.strip().lower().replace('-', '_').replace(' ', '_')
                out[name] = next((o for o in options if o == key), value)
        return out


# --- IS 6403 ---
class BearingCapacityIS6403Input(_BISInput):
    """Net ultimate bearing capacity of a shallow foundation, IS 6403:1981 (shear criterion)."""
    width: float = GeotechnicalField(..., gt=0, le=100, unit="m", description="Footing width B (diameter for a circle)")
    depth: float = GeotechnicalField(..., ge=0, le=20, unit="m", description="Founding depth Df below surrounding ground level")
    water_table_depth: float = GeotechnicalField(..., ge=0, le=200, unit="m",
                                                 description="Depth of the highest likely water table below ground level")
    unit_weight: float = GeotechnicalField(..., gt=5, le=30, unit="kN/m3", description="Bulk unit weight gamma of the foundation soil")
    cohesion: float = GeotechnicalField(0.0, ge=0, le=2000, unit="kPa", description="Cohesion c (undrained cohesion for phi = 0)")
    friction_angle: float = GeotechnicalField(0.0, ge=0, le=50, unit="deg", description="Angle of shearing resistance phi (0-50)")
    shape: Literal["strip", "square", "circle", "rectangle"] = GeotechnicalField("strip", description="Footing shape")
    length: Optional[float] = GeotechnicalField(None, gt=0, le=500, unit="m", description="Footing length L (rectangle, L >= B)")
    failure_mode: Literal["general", "local", "from_relative_density"] = GeotechnicalField(
        "general", description="Shear failure mode; from_relative_density applies IS 6403 Table 3")
    relative_density: Optional[float] = GeotechnicalField(None, ge=0, le=100, unit="%",
                                                          description="Relative density, for failure_mode = from_relative_density")
    load_inclination: float = GeotechnicalField(0.0, ge=0, lt=90, unit="deg", description="Inclination of the load to the vertical alpha")
    eccentricity_width: float = GeotechnicalField(0.0, ge=0, unit="m", description="Load eccentricity along the width eB")
    eccentricity_length: float = GeotechnicalField(0.0, ge=0, unit="m", description="Load eccentricity along the length eL")
    saturated_unit_weight: Optional[float] = GeotechnicalField(None, gt=5, le=30, unit="kN/m3",
                                                               description="Saturated unit weight (needed if the water table is above the base)")
    apply_depth_factors: bool = GeotechnicalField(False, description="Apply depth factors (only with properly compacted backfill)")
    factor_of_safety: Optional[float] = GeotechnicalField(None, ge=1, le=10, unit="-",
                                                          description="Factor of safety for the net safe bearing capacity (designer's choice)")
    unit_weight_water: float = GeotechnicalField(9.81, gt=9, le=10.5, unit="kN/m3", description="Unit weight of water")


# --- IS 1498 ---
class ClassifySoilIS1498Input(_BISInput):
    """Indian Standard Soil Classification, IS 1498:1970 laboratory method."""
    percent_fines: float = GeotechnicalField(..., ge=0, le=100, unit="%", description="Percentage passing the 75-micron IS sieve")
    percent_gravel: float = GeotechnicalField(0.0, ge=0, le=100, unit="%", description="Percentage retained on the 4.75 mm IS sieve")
    liquid_limit: Optional[float] = GeotechnicalField(None, gt=0, le=1000, unit="%", description="Liquid limit wL")
    plastic_limit: Optional[float] = GeotechnicalField(None, ge=0, le=1000, unit="%", description="Plastic limit wP")
    non_plastic: bool = GeotechnicalField(False, description="True when the plastic limit cannot be determined (NP)")
    d10: Optional[float] = GeotechnicalField(None, gt=0, le=100, unit="mm", description="Particle size D10 (10 % finer)")
    d30: Optional[float] = GeotechnicalField(None, gt=0, le=100, unit="mm", description="Particle size D30 (30 % finer)")
    d60: Optional[float] = GeotechnicalField(None, gt=0, le=100, unit="mm", description="Particle size D60 (60 % finer)")
    liquid_limit_oven_dried: Optional[float] = GeotechnicalField(None, gt=0, le=1000, unit="%",
                                                                 description="Liquid limit after oven drying (identifies organic fines)")
    highly_organic: bool = GeotechnicalField(False, description="True for peat / highly organic soil identified visually")
    boundary_tolerance: float = GeotechnicalField(0.0, ge=0, le=5, unit="%",
                                                  description="Tolerance for plotting 'on' the A-line or wL = 35 / 50 lines")


# --- IS 2131 ---
class SPTCorrectionIS2131Input(_BISInput):
    """Corrected SPT N for cohesionless soil, IS 2131:1981 cl. 3.6."""
    n_observed: float = GeotechnicalField(..., ge=0, le=200, unit="-", description="Observed N value (blows per 300 mm)")
    effective_overburden_pressure: float = GeotechnicalField(..., gt=0, le=2000, unit="kPa",
                                                             description="Effective vertical overburden pressure at the test depth")
    fine_sand_or_silt_below_water_table: bool = GeotechnicalField(False, description="Fine sand or silt below the water table (dilatancy correction)")
    energy_ratio: Optional[float] = GeotechnicalField(None, gt=0, le=100, unit="%",
                                                      description="Measured hammer energy ratio; normalises N to 60 % energy first")


# --- IS 1892 ---
class InvestigationDepthIS1892Input(_BISInput):
    """Guideline depth of subsurface investigation, IS 1892:2021 cl. 5.6.3."""
    foundation_type: Literal["shallow", "raft", "pile", "embankment", "well"] = GeotechnicalField(..., description="Foundation type")
    width: Optional[float] = GeotechnicalField(None, gt=0, le=500, unit="m",
                                               description="Largest foundation width, raft width, or well width/diameter")
    pile_diameter: Optional[float] = GeotechnicalField(None, gt=0, le=5, unit="m", description="Pile diameter")
    embankment_height: Optional[float] = GeotechnicalField(None, gt=0, le=100, unit="m", description="Embankment height")
    founding_depth: float = GeotechnicalField(0.0, ge=0, le=200, unit="m",
                                              description="Founding level (pile tip / well termination) below ground level")


class BoreholeLayoutIS1892Input(_BISInput):
    """Disposition of boreholes / trial pits, IS 1892:2021 Table 2."""
    structure_type: Literal["light_residential", "site_0_4_ha", "large_plan_or_multiple_buildings", "tall_building",
                            "linear", "solar_plant"] = GeotechnicalField(..., description="Structure category of Table 2")
    plan_length: Optional[float] = GeotechnicalField(None, gt=0, le=10000, unit="m", description="Plan length of the built-up area")
    plan_width: Optional[float] = GeotechnicalField(None, gt=0, le=10000, unit="m", description="Plan width of the built-up area")
    route_length: Optional[float] = GeotechnicalField(None, gt=0, le=1e6, unit="m", description="Length of a linear structure")
    site_area: Optional[float] = GeotechnicalField(None, gt=0, le=1e5, unit="ha", description="Site area of a solar power plant")


# --- IS 1904 ---
class PermissibleSettlementIS1904Input(_BISInput):
    """Permissible settlements of shallow foundations, IS 1904:2021 Table 1."""
    foundation_type: Literal["isolated", "raft"] = GeotechnicalField(..., description="Foundation type")
    structure_type: Literal["steel", "reinforced_concrete", "multistorey_framed", "load_bearing_walls",
                            "water_tower_silo"] = GeotechnicalField(..., description="Type of structure")
    soil_type: Literal["sand_hard_clay", "plastic_clay"] = GeotechnicalField(..., description="Soil group of Table 1")
    span_length: Optional[float] = GeotechnicalField(None, gt=0, le=500, unit="m",
                                                     description="L: deflected length of wall/raft or column centre distance")
    length_height_ratio: Optional[float] = GeotechnicalField(None, ge=2, le=7, unit="-", description="L/H of a load bearing wall (2-7)")
    calculated_max_settlement: Optional[float] = GeotechnicalField(None, ge=0, le=5000, unit="mm",
                                                                   description="Calculated maximum settlement to check")
    calculated_differential_settlement: Optional[float] = GeotechnicalField(None, ge=0, le=5000, unit="mm",
                                                                            description="Calculated differential settlement over L to check")


class StabilityCheckIS1904Input(_BISInput):
    """Factor of safety against sliding / overturning, IS 1904:2021 cl. 17.1."""
    check: Literal["sliding", "overturning"] = GeotechnicalField(..., description="Stability check")
    resisting: float = GeotechnicalField(..., ge=0, unit="-", description="Resisting force or moment (same units as disturbing)")
    disturbing: float = GeotechnicalField(..., gt=0, unit="-", description="Disturbing force or overturning moment")
    wind_or_seismic: bool = GeotechnicalField(False, description="Wind or seismic forces included in the load case")


# --- IS 2950 (Part 1) ---
class RaftRigidityIS2950Input(_BISInput):
    """Rigid or flexible raft, IS 2950 (Part 1):1981 Appendix C."""
    shape: Literal["rectangular", "circular"] = GeotechnicalField(..., description="Raft shape")
    raft_thickness: float = GeotechnicalField(..., gt=0, le=10, unit="m", description="Raft thickness d")
    concrete_modulus: float = GeotechnicalField(..., gt=0, unit="kPa", description="Modulus of elasticity of the raft concrete E")
    soil_modulus: float = GeotechnicalField(..., gt=0, unit="kPa", description="Modulus of compressibility of the foundation soil Es")
    raft_length: Optional[float] = GeotechnicalField(None, gt=0, le=1000, unit="m",
                                                     description="Rectangular raft: length b of the section in the bending axis")
    raft_radius: Optional[float] = GeotechnicalField(None, gt=0, le=500, unit="m", description="Circular raft: radius R")
    subgrade_modulus: Optional[float] = GeotechnicalField(None, gt=0, unit="kN/m3", description="Modulus of subgrade reaction k")
    raft_width: Optional[float] = GeotechnicalField(None, gt=0, le=1000, unit="m", description="Raft width B")
    moment_of_inertia: Optional[float] = GeotechnicalField(None, gt=0, unit="m4", description="Moment of inertia of the raft over width B")
    column_spacing: Optional[float] = GeotechnicalField(None, gt=0, le=100, unit="m", description="Column spacing")


# --- IS 2720 ---
class SpecificGravityIS2720Input(_BISInput):
    """Specific gravity by density bottle, IS 2720 (Part 3/Sec 1)."""
    mass_bottle: float = GeotechnicalField(..., gt=0, unit="g", description="m1, empty density bottle")
    mass_bottle_soil: float = GeotechnicalField(..., gt=0, unit="g", description="m2, bottle and dry soil")
    mass_bottle_soil_water: float = GeotechnicalField(..., gt=0, unit="g", description="m3, bottle, soil and water")
    mass_bottle_water: float = GeotechnicalField(..., gt=0, unit="g", description="m4, bottle full of water")
    temperature: float = GeotechnicalField(27.0, ge=0, le=40, unit="degC", description="Test temperature")


class FlowIndexIS2720Input(_BISInput):
    """Flow index from two flow-curve points, IS 2720 (Part 5)."""
    water_content_1: float = GeotechnicalField(..., gt=0, unit="%", description="Water content w1")
    blows_1: float = GeotechnicalField(..., gt=0, le=200, unit="-", description="Number of drops N1")
    water_content_2: float = GeotechnicalField(..., gt=0, unit="%", description="Water content w2")
    blows_2: float = GeotechnicalField(..., gt=0, le=200, unit="-", description="Number of drops N2")


class LiquidLimitOnePointIS2720Input(_BISInput):
    """One-point liquid limit, IS 2720 (Part 5) cl. 5 / 6."""
    water_content: float = GeotechnicalField(..., gt=0, le=1000, unit="%", description="Water content of the accepted trial")
    method: Literal["casagrande", "cone"] = GeotechnicalField("casagrande", description="Apparatus")
    blows: Optional[float] = GeotechnicalField(None, ge=15, le=35, unit="-", description="Casagrande drops (15-35)")
    cone_penetration: Optional[float] = GeotechnicalField(None, ge=16, le=26, unit="mm", description="Cone penetration (16-26)")


class ConsistencyIndicesIS2720Input(_BISInput):
    """Plasticity, liquidity, consistency and toughness indices, IS 2720 (Part 5)."""
    liquid_limit: float = GeotechnicalField(..., gt=0, le=1000, unit="%", description="Liquid limit wL")
    plastic_limit: float = GeotechnicalField(..., ge=0, le=1000, unit="%", description="Plastic limit wP")
    natural_water_content: Optional[float] = GeotechnicalField(None, ge=0, le=1000, unit="%", description="Natural water content w0")
    flow_index: Optional[float] = GeotechnicalField(None, gt=0, unit="%", description="Flow index If")


class PermeabilityConstantHeadIS2720Input(_BISInput):
    """Constant head permeability test, IS 2720 (Part 17)."""
    discharge_volume: float = GeotechnicalField(..., gt=0, unit="cm3", description="Quantity of water Q collected")
    specimen_length: float = GeotechnicalField(..., gt=0, unit="cm", description="Specimen length L")
    specimen_area: float = GeotechnicalField(..., gt=0, unit="cm2", description="Specimen cross-sectional area A")
    head_loss: float = GeotechnicalField(..., gt=0, unit="cm", description="Head loss h over L")
    time: float = GeotechnicalField(..., gt=0, unit="s", description="Collection time t")
    temperature: float = GeotechnicalField(27.0, ge=0, le=40, unit="degC", description="Water temperature")


class PermeabilityFallingHeadIS2720Input(_BISInput):
    """Falling head permeability test, IS 2720 (Part 17)."""
    standpipe_area: float = GeotechnicalField(..., gt=0, unit="cm2", description="Stand-pipe area a")
    specimen_length: float = GeotechnicalField(..., gt=0, unit="cm", description="Specimen length L")
    specimen_area: float = GeotechnicalField(..., gt=0, unit="cm2", description="Specimen area A")
    initial_head: float = GeotechnicalField(..., gt=0, unit="cm", description="Initial head h1")
    final_head: float = GeotechnicalField(..., gt=0, unit="cm", description="Final head h2")
    time: float = GeotechnicalField(..., gt=0, unit="s", description="Elapsed time")
    temperature: float = GeotechnicalField(27.0, ge=0, le=40, unit="degC", description="Water temperature")


BIS_SCHEMAS = {
    'bearing_capacity_is6403': BearingCapacityIS6403Input,
    'classify_soil_is1498': ClassifySoilIS1498Input,
    'spt_correction_is2131': SPTCorrectionIS2131Input,
    'investigation_depth_is1892': InvestigationDepthIS1892Input,
    'borehole_layout_is1892': BoreholeLayoutIS1892Input,
    'permissible_settlement_is1904': PermissibleSettlementIS1904Input,
    'stability_check_is1904': StabilityCheckIS1904Input,
    'raft_rigidity_is2950': RaftRigidityIS2950Input,
    'specific_gravity_is2720': SpecificGravityIS2720Input,
    'flow_index_is2720': FlowIndexIS2720Input,
    'liquid_limit_one_point_is2720': LiquidLimitOnePointIS2720Input,
    'consistency_indices_is2720': ConsistencyIndicesIS2720Input,
    'permeability_constant_head_is2720': PermeabilityConstantHeadIS2720Input,
    'permeability_falling_head_is2720': PermeabilityFallingHeadIS2720Input,
}
