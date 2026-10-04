/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Indian Standard (BIS) calculations: python-backend/core/standards/bis.
 * Inputs mirror core/geoai/schemas/bis.py (same names, units and options).
 */

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
        documentation: `
            <h3>IS 6403:1981 - Bearing capacity of shallow foundations</h3>
            <p>Net ultimate bearing capacity on the shear criterion (cl. 5.1.2):</p>
            <p>q<sub>d</sub> = c N<sub>c</sub> s<sub>c</sub> d<sub>c</sub> i<sub>c</sub> + q (N<sub>q</sub> − 1) s<sub>q</sub> d<sub>q</sub> i<sub>q</sub> + ½ B γ N<sub>γ</sub> s<sub>γ</sub> d<sub>γ</sub> i<sub>γ</sub> W′</p>
            <ul>
                <li>Bearing capacity factors per Table 1; local shear uses c′ = 2c/3 and φ′ = tan⁻¹(0.67 tan φ).</li>
                <li>Shape factors per Table 2, depth factors per cl. 5.1.2.2, inclination factors per cl. 5.1.2.3.</li>
                <li>W′ = 0.5 with the water table at or above the base and 1 at or below Df + B, interpolated linearly between.</li>
                <li>Eccentric loads use B′ = B − 2e<sub>B</sub> and L′ = L − 2e<sub>L</sub> (cl. 5.0.1).</li>
            </ul>
            <p>Allowable bearing capacity is the lesser of q<sub>d</sub>/FS and the pressure for permissible settlement (cl. 6.1, IS 1904). IS 6403 is under revision by BIS.</p>
            ${BIS_NOTE}
        `
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
        documentation: `
            <h3>IS 1498:1970 - Indian Standard Soil Classification</h3>
            <ul>
                <li>Coarse-grained if more than 50 % is retained on the 75-micron sieve; gravel if more than half the coarse fraction is retained on 4.75 mm.</li>
                <li>GW: Cu &gt; 4 and Cc 1-3; SW: Cu &gt; 6 and Cc 1-3. Less than 5 % fines is clean, more than 12 % is dirty, and 5-12 % gets a dual symbol.</li>
                <li>Fine-grained soils: L (wL &lt; 35), I (35-50), H (&gt; 50). A-line: I<sub>p</sub> = 0.73 (wL − 20). ML-CL applies above the A-line with I<sub>p</sub> 4-7.</li>
            </ul>
            ${BIS_NOTE}
        `
    },
    spt_correction_is2131: {
        inputs: [
            { name: "n_observed", type: "float", description: "Observed N (blows / 300 mm)", required: true },
            { name: "effective_overburden_pressure", type: "float", unit: "kPa", description: "Effective vertical overburden at test depth [kPa]", required: true },
            { name: "fine_sand_or_silt_below_water_table", type: "boolean", default: false, description: "Fine sand / silt below water table (dilatancy correction)" },
            { name: "energy_ratio", type: "float", unit: "%", description: "Measured hammer energy ratio (optional N60 normalisation) [%]" }
        ],
        documentation: `
            <h3>IS 2131:1981 - SPT corrections (cl. 3.6)</h3>
            <ul>
                <li>Overburden (Fig. 1): C<sub>N</sub> = 0.77 log<sub>10</sub>(20/σ′<sub>v</sub>), with σ′<sub>v</sub> in kgf/cm² and C<sub>N</sub> ≤ 2.</li>
                <li>Dilatancy, for fine sand or silt below the water table when N′ &gt; 15: N″ = 15 + ½(N′ − 15).</li>
                <li>If the energy ratio is given, N is first normalised to N60 = N·ER/60 (ISO 22476-3). This step is not part of IS 2131:1981; check it against IS 2131:2025.</li>
            </ul>
            ${BIS_NOTE}
        `
    },
    investigation_depth_is1892: {
        inputs: [
            { name: "foundation_type", type: "select", options: ["shallow", "raft", "pile", "embankment", "well"], default: "shallow", description: "Foundation type", required: true },
            { name: "width", type: "float", unit: "m", description: "Largest foundation / raft / well width [m]" },
            { name: "pile_diameter", type: "float", unit: "m", description: "Pile diameter [m]" },
            { name: "embankment_height", type: "float", unit: "m", description: "Embankment height [m]" },
            { name: "founding_depth", type: "float", unit: "m", default: 0, description: "Founding level / pile tip below ground level [m]" }
        ],
        documentation: `
            <h3>IS 1892:2021 - Depth of investigation (cl. 5.6.3)</h3>
            <ul>
                <li>Shallow foundations: 2-3 × the largest width. Rafts: 1-2 × the width (taken as at least 6 m).</li>
                <li>Piles: at least the greater of 5 m and 5 diameters below the tip. Embankments: 1-2 × the height. Wells: 1.5-2 × the width.</li>
                <li>Extend at least 5 m into rock if it is met earlier. The stress increase at the final depth must be below 10 % of the in-situ stress.</li>
            </ul>
            ${BIS_NOTE}
        `
    },
    borehole_layout_is1892: {
        inputs: [
            { name: "structure_type", type: "select", options: ["light_residential", "site_0_4_ha", "large_plan_or_multiple_buildings", "tall_building", "linear", "solar_plant"], default: "light_residential", description: "Structure category (Table 2)", required: true },
            { name: "plan_length", type: "float", unit: "m", description: "Built-up plan length [m]" },
            { name: "plan_width", type: "float", unit: "m", description: "Built-up plan width [m]" },
            { name: "route_length", type: "float", unit: "m", description: "Length of linear structure [m]" },
            { name: "site_area", type: "float", unit: "ha", description: "Solar plant site area [ha]" }
        ],
        documentation: `<h3>IS 1892:2021 Table 2 - Disposition of boreholes</h3><p>Minimum boreholes by structure type: grid at ≤ 50 m spacing for large plans, at least three per building over 50 m high, 50-500 m spacing along linear works, and one per 2-5 ha (minimum five) for solar plants.</p>${BIS_NOTE}`
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
        documentation: `<h3>IS 1904:2021 Table 1 - Permissible settlements</h3><p>Maximum settlement, differential settlement (× L) and angular distortion for isolated and raft foundations. Per the code note, these values are a guide; the designer decides the limits. In the 2021 revision, the maximum for rafts under RC structures on plastic clay is 125 mm.</p>${BIS_NOTE}`
    },
    stability_check_is1904: {
        inputs: [
            { name: "check", type: "select", options: ["sliding", "overturning"], default: "sliding", description: "Stability check", required: true },
            { name: "resisting", type: "float", description: "Resisting force / moment", required: true },
            { name: "disturbing", type: "float", description: "Disturbing force / moment (same units)", required: true },
            { name: "wind_or_seismic", type: "boolean", default: false, description: "Wind or seismic forces included" }
        ],
        documentation: `<h3>IS 1904:2021 cl. 17.1 - Sliding and overturning</h3><p>Minimum factor of safety: 1.5 with wind or seismic loads. Without them, 1.75 for sliding and 2.0 for overturning.</p>${BIS_NOTE}`
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
        documentation: `<h3>IS 2950 (Part 1):1981 Appendix C - Rigid or flexible raft</h3><p>K = E/(12E<sub>s</sub>)·(d/b)³, and K &gt; 0.5 means rigid. With λ = (kB/4E<sub>c</sub>I)<sup>¼</sup>, the rigid (conventional) method may also be used when the column spacing is less than 1.75/λ.</p>${BIS_NOTE}`
    },
    specific_gravity_is2720: {
        inputs: [
            { name: "mass_bottle", type: "float", unit: "g", description: "m1, empty bottle [g]", required: true },
            { name: "mass_bottle_soil", type: "float", unit: "g", description: "m2, bottle + dry soil [g]", required: true },
            { name: "mass_bottle_soil_water", type: "float", unit: "g", description: "m3, bottle + soil + water [g]", required: true },
            { name: "mass_bottle_water", type: "float", unit: "g", description: "m4, bottle + water [g]", required: true },
            { name: "temperature", type: "float", unit: "degC", default: 27, description: "Test temperature [°C]" }
        ],
        documentation: `<h3>IS 2720 (Part 3/Sec 1) - Specific gravity</h3><p>G = (m2 − m1)/((m4 − m1) − (m3 − m2)), corrected to 27 °C by the ratio of water densities.</p>${BIS_NOTE}`
    },
    flow_index_is2720: {
        inputs: [
            { name: "water_content_1", type: "float", unit: "%", description: "w1 [%]", required: true },
            { name: "blows_1", type: "float", description: "N1 drops", required: true },
            { name: "water_content_2", type: "float", unit: "%", description: "w2 [%]", required: true },
            { name: "blows_2", type: "float", description: "N2 drops", required: true }
        ],
        documentation: `<h3>IS 2720 (Part 5) - Flow index</h3><p>I<sub>f</sub> = (w1 − w2)/log<sub>10</sub>(N2/N1).</p>${BIS_NOTE}`
    },
    liquid_limit_one_point_is2720: {
        inputs: [
            { name: "water_content", type: "float", unit: "%", description: "Water content of accepted trial [%]", required: true },
            { name: "method", type: "select", options: ["casagrande", "cone"], default: "casagrande", description: "Apparatus" },
            { name: "blows", type: "float", description: "Casagrande drops (15-35)" },
            { name: "cone_penetration", type: "float", unit: "mm", description: "Cone penetration (16-26 mm)" }
        ],
        documentation: `<h3>IS 2720 (Part 5) - One-point liquid limit</h3><p>Casagrande: w<sub>L</sub> = w<sub>N</sub>/(1.3215 − 0.23 log N). Cone: w<sub>N</sub>/(0.77 log D) or w<sub>N</sub>/(0.65 + 0.0175 D).</p>${BIS_NOTE}`
    },
    consistency_indices_is2720: {
        inputs: [
            { name: "liquid_limit", type: "float", unit: "%", description: "Liquid limit wL [%]", required: true },
            { name: "plastic_limit", type: "float", unit: "%", description: "Plastic limit wP [%]", required: true },
            { name: "natural_water_content", type: "float", unit: "%", description: "Natural water content [%]" },
            { name: "flow_index", type: "float", unit: "%", description: "Flow index If [%]" }
        ],
        documentation: `<h3>IS 2720 (Part 5) - Consistency indices</h3><p>I<sub>p</sub> = w<sub>L</sub> − w<sub>P</sub>; I<sub>L</sub> = (w − w<sub>P</sub>)/I<sub>p</sub>; I<sub>c</sub> = (w<sub>L</sub> − w)/I<sub>p</sub>; I<sub>t</sub> = I<sub>p</sub>/I<sub>f</sub>.</p>${BIS_NOTE}`
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
        documentation: `<h3>IS 2720 (Part 17) - Constant head permeability</h3><p>k<sub>T</sub> = QL/(Aht), and k<sub>27</sub> = k<sub>T</sub>·η<sub>T</sub>/η<sub>27</sub>.</p>${BIS_NOTE}`
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
        documentation: `<h3>IS 2720 (Part 17) - Falling head permeability</h3><p>k<sub>T</sub> = 2.303·aL/(At)·log<sub>10</sub>(h1/h2), and k<sub>27</sub> = k<sub>T</sub>·η<sub>T</sub>/η<sub>27</sub>.</p>${BIS_NOTE}`
    }
};
