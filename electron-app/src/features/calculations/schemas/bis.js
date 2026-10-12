/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Indian Standard (BIS) calculations: python-backend/core/standards/bis.
 * Inputs mirror core/geoai/schemas/bis.py (same names, units and options).
 */

// Theory, equations and clause references are in the Guide (website/_build/bis_docs.py -> functionDocs.json).
const BIS_NOTE = `<p><i>GeoCore implementation of the clauses cited. Results support, and do not replace, engineering judgement; check against the current edition of the code.</i></p>`;

export const bisSchemas = {
    bearing_capacity_is6403: {
        inputs: [
            { name: "width", type: "float", unit: "m", description: "Footing width B (diameter for a circle) [m]", required: true },
            { name: "depth", type: "float", unit: "m", description: "Founding depth Df below ground level [m]", required: true },
            { name: "water_table_depth", type: "float", unit: "m", description: "Highest likely water table depth below ground level [m]", required: true },
            { name: "unit_weight", type: "float", unit: "kN/m3", description: "Bulk unit weight γ [kN/m3]", required: true },
            { name: "cohesion", type: "float", unit: "kPa", default: 0, description: "Cohesion c (undrained cohesion for φ = 0) [kPa]" },
            { name: "friction_angle", type: "float", unit: "deg", default: 0, description: "Angle of shearing resistance φ, 0-50 [deg]" },
            { name: "shape", type: "select", options: ["strip", "square", "circle", "rectangle"], default: "strip", description: "Footing shape" },
            { name: "length", type: "float", unit: "m", description: "Footing length L, rectangle only (L ≥ B) [m]" },
            { name: "failure_mode", type: "select", options: ["general", "local", "from_relative_density"], default: "general", description: "Shear failure mode (Table 3 uses relative density)" },
            { name: "relative_density", type: "float", unit: "%", description: "Relative density, for failure_mode = from_relative_density [%]" },
            { name: "load_inclination", type: "float", unit: "deg", default: 0, description: "Load inclination to the vertical α [deg]" },
            { name: "eccentricity_width", type: "float", unit: "m", default: 0, description: "Eccentricity along the width eB [m]" },
            { name: "eccentricity_length", type: "float", unit: "m", default: 0, description: "Eccentricity along the length eL [m]" },
            { name: "saturated_unit_weight", type: "float", unit: "kN/m3", description: "Saturated unit weight, if the water table is above the base [kN/m3]" },
            { name: "apply_depth_factors", type: "boolean", default: false, description: "Apply depth factors (only with properly compacted backfill)" },
            { name: "factor_of_safety", type: "float", description: "Factor of safety for the net safe bearing capacity (optional)" },
            { name: "unit_weight_water", type: "float", unit: "kN/m3", default: 9.81, description: "Unit weight of water [kN/m3]" }
        ],
        documentation: BIS_NOTE
    },
    classify_soil_is1498: {
        inputs: [
            { name: "percent_fines", type: "float", unit: "%", description: "Passing 75-micron IS sieve [%]", required: true },
            { name: "percent_gravel", type: "float", unit: "%", default: 0, description: "Retained on 4.75 mm IS sieve [%]" },
            { name: "liquid_limit", type: "float", unit: "%", description: "Liquid limit wL [%]" },
            { name: "plastic_limit", type: "float", unit: "%", description: "Plastic limit wP [%]" },
            { name: "non_plastic", type: "boolean", default: false, description: "Non-plastic (plastic limit cannot be determined)" },
            { name: "d10", type: "float", unit: "mm", description: "D10 [mm]" },
            { name: "d30", type: "float", unit: "mm", description: "D30 [mm]" },
            { name: "d60", type: "float", unit: "mm", description: "D60 [mm]" },
            { name: "liquid_limit_oven_dried", type: "float", unit: "%", description: "Oven-dried liquid limit (organic check) [%]" },
            { name: "highly_organic", type: "boolean", default: false, description: "Peat / highly organic soil (identified visually)" },
            { name: "boundary_tolerance", type: "float", unit: "%", default: 0, description: "Tolerance for lying 'on' the A-line or wL = 35/50 lines [%]" }
        ],
        documentation: BIS_NOTE
    },
    spt_correction_is2131: {
        inputs: [
            { name: "n_observed", type: "float", description: "Observed N (blows / 300 mm)", required: true },
            { name: "effective_overburden_pressure", type: "float", unit: "kPa", description: "Effective vertical overburden at test depth [kPa]", required: true },
            { name: "fine_sand_or_silt_below_water_table", type: "boolean", default: false, description: "Fine sand / silt below water table (dilatancy correction)" },
            { name: "energy_ratio", type: "float", unit: "%", description: "Measured hammer energy ratio (optional N60 normalisation) [%]" }
        ],
        documentation: BIS_NOTE
    },
    investigation_depth_is1892: {
        inputs: [
            { name: "foundation_type", type: "select", options: ["shallow", "raft", "pile", "embankment", "well"], default: "shallow", description: "Foundation type", required: true },
            { name: "width", type: "float", unit: "m", description: "Largest foundation / raft / well width [m]" },
            { name: "pile_diameter", type: "float", unit: "m", description: "Pile diameter [m]" },
            { name: "embankment_height", type: "float", unit: "m", description: "Embankment height [m]" },
            { name: "founding_depth", type: "float", unit: "m", default: 0, description: "Founding level / pile tip below ground level [m]" }
        ],
        documentation: BIS_NOTE
    },
    borehole_layout_is1892: {
        inputs: [
            { name: "structure_type", type: "select", options: ["light_residential", "site_0_4_ha", "large_plan_or_multiple_buildings", "tall_building", "linear", "solar_plant"], default: "light_residential", description: "Structure category (Table 2)", required: true },
            { name: "plan_length", type: "float", unit: "m", description: "Built-up plan length [m]" },
            { name: "plan_width", type: "float", unit: "m", description: "Built-up plan width [m]" },
            { name: "route_length", type: "float", unit: "m", description: "Length of linear structure [m]" },
            { name: "site_area", type: "float", unit: "ha", description: "Solar plant site area [ha]" }
        ],
        documentation: BIS_NOTE
    },
    permissible_settlement_is1904: {
        inputs: [
            { name: "foundation_type", type: "select", options: ["isolated", "raft"], default: "isolated", description: "Foundation type", required: true },
            { name: "structure_type", type: "select", options: ["steel", "reinforced_concrete", "multistorey_framed", "load_bearing_walls", "water_tower_silo"], default: "reinforced_concrete", description: "Type of structure", required: true },
            { name: "soil_type", type: "select", options: ["sand_hard_clay", "plastic_clay"], default: "sand_hard_clay", description: "Soil group", required: true },
            { name: "span_length", type: "float", unit: "m", description: "L: column spacing / deflected length [m]" },
            { name: "length_height_ratio", type: "float", description: "L/H for load bearing walls (2-7)" },
            { name: "calculated_max_settlement", type: "float", unit: "mm", description: "Calculated maximum settlement to check [mm]" },
            { name: "calculated_differential_settlement", type: "float", unit: "mm", description: "Calculated differential settlement to check [mm]" }
        ],
        documentation: BIS_NOTE
    },
    stability_check_is1904: {
        inputs: [
            { name: "check", type: "select", options: ["sliding", "overturning"], default: "sliding", description: "Stability check", required: true },
            { name: "resisting", type: "float", description: "Resisting force / moment", required: true },
            { name: "disturbing", type: "float", description: "Disturbing force / moment (same units)", required: true },
            { name: "wind_or_seismic", type: "boolean", default: false, description: "Wind or seismic forces included" }
        ],
        documentation: BIS_NOTE
    },
    raft_rigidity_is2950: {
        inputs: [
            { name: "shape", type: "select", options: ["rectangular", "circular"], default: "rectangular", description: "Raft shape", required: true },
            { name: "raft_thickness", type: "float", unit: "m", description: "Raft thickness d [m]", required: true },
            { name: "concrete_modulus", type: "float", unit: "kPa", description: "Concrete modulus E [kPa]", required: true },
            { name: "soil_modulus", type: "float", unit: "kPa", description: "Soil modulus of compressibility Es [kPa]", required: true },
            { name: "raft_length", type: "float", unit: "m", description: "Rectangular: length b in bending axis [m]" },
            { name: "raft_radius", type: "float", unit: "m", description: "Circular: radius R [m]" },
            { name: "subgrade_modulus", type: "float", unit: "kN/m3", description: "Modulus of subgrade reaction k [kN/m3]" },
            { name: "raft_width", type: "float", unit: "m", description: "Raft width B [m]" },
            { name: "moment_of_inertia", type: "float", unit: "m4", description: "Moment of inertia I (default B·d³/12) [m4]" },
            { name: "column_spacing", type: "float", unit: "m", description: "Column spacing [m]" }
        ],
        documentation: BIS_NOTE
    },
    specific_gravity_is2720: {
        inputs: [
            { name: "mass_bottle", type: "float", unit: "g", description: "m1, empty bottle [g]", required: true },
            { name: "mass_bottle_soil", type: "float", unit: "g", description: "m2, bottle + dry soil [g]", required: true },
            { name: "mass_bottle_soil_water", type: "float", unit: "g", description: "m3, bottle + soil + water [g]", required: true },
            { name: "mass_bottle_water", type: "float", unit: "g", description: "m4, bottle + water [g]", required: true },
            { name: "temperature", type: "float", unit: "degC", default: 27, description: "Test temperature [°C]" }
        ],
        documentation: BIS_NOTE
    },
    flow_index_is2720: {
        inputs: [
            { name: "water_content_1", type: "float", unit: "%", description: "w1 [%]", required: true },
            { name: "blows_1", type: "float", description: "N1 drops", required: true },
            { name: "water_content_2", type: "float", unit: "%", description: "w2 [%]", required: true },
            { name: "blows_2", type: "float", description: "N2 drops", required: true }
        ],
        documentation: BIS_NOTE
    },
    liquid_limit_one_point_is2720: {
        inputs: [
            { name: "water_content", type: "float", unit: "%", description: "Water content of accepted trial [%]", required: true },
            { name: "method", type: "select", options: ["casagrande", "cone"], default: "casagrande", description: "Apparatus" },
            { name: "blows", type: "float", description: "Casagrande drops (15-35)" },
            { name: "cone_penetration", type: "float", unit: "mm", description: "Cone penetration (16-26 mm)" }
        ],
        documentation: BIS_NOTE
    },
    consistency_indices_is2720: {
        inputs: [
            { name: "liquid_limit", type: "float", unit: "%", description: "Liquid limit wL [%]", required: true },
            { name: "plastic_limit", type: "float", unit: "%", description: "Plastic limit wP [%]", required: true },
            { name: "natural_water_content", type: "float", unit: "%", description: "Natural water content [%]" },
            { name: "flow_index", type: "float", unit: "%", description: "Flow index If [%]" }
        ],
        documentation: BIS_NOTE
    },
    permeability_constant_head_is2720: {
        inputs: [
            { name: "discharge_volume", type: "float", unit: "cm3", description: "Volume collected Q [cm3]", required: true },
            { name: "specimen_length", type: "float", unit: "cm", description: "Specimen length L [cm]", required: true },
            { name: "specimen_area", type: "float", unit: "cm2", description: "Specimen area A [cm2]", required: true },
            { name: "head_loss", type: "float", unit: "cm", description: "Head loss h [cm]", required: true },
            { name: "time", type: "float", unit: "s", description: "Time t [s]", required: true },
            { name: "temperature", type: "float", unit: "degC", default: 27, description: "Water temperature [°C]" }
        ],
        documentation: BIS_NOTE
    },
    permeability_falling_head_is2720: {
        inputs: [
            { name: "standpipe_area", type: "float", unit: "cm2", description: "Stand-pipe area a [cm2]", required: true },
            { name: "specimen_length", type: "float", unit: "cm", description: "Specimen length L [cm]", required: true },
            { name: "specimen_area", type: "float", unit: "cm2", description: "Specimen area A [cm2]", required: true },
            { name: "initial_head", type: "float", unit: "cm", description: "Initial head h1 [cm]", required: true },
            { name: "final_head", type: "float", unit: "cm", description: "Final head h2 [cm]", required: true },
            { name: "time", type: "float", unit: "s", description: "Elapsed time [s]", required: true },
            { name: "temperature", type: "float", unit: "degC", default: 27, description: "Water temperature [°C]" }
        ],
        documentation: BIS_NOTE
    }
};
