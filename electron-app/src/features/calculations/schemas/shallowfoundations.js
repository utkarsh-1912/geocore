/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

const shallowFoundationsSchemas = {
    // --- Stress Distributions ---
    stresses_circle: {
        title: "Stress Distribution - Circular Footing",
        description: "Calculates the stress distribution below a uniformly loaded circular foundation.",
        type: "object",
        properties: {
            z: { type: "number", title: "Depth below base (z) [m]", minimum: 0, description: "Depth below the base of the foundation" },
            footing_radius: { type: "number", title: "Footing Radius (R) [m]", minimum: 0, description: "Radius of the circular foundation" },
            imposedstress: { type: "number", title: "Imposed Stress (q) [kPa]", description: "Applied uniform stress to the circular footing" },
            poissonsratio: { type: "number", title: "Poisson's Ratio", minimum: 0, maximum: 0.5, default: 0.3, description: "Poissons ratio for the soil material" }
        },
        required: ["z", "footing_radius", "imposedstress"],
        documentation: `
            <h3>Stress Distribution - Circular Footing</h3>
            <p>Calculates the stress distribution below a uniformly loaded circular foundation. The stresses are calculated below the center of the circular foundation.</p>
        `
    },
    stresses_lineload_retainingwall: {
        title: "Stress Distribution - Line Load (Retaining Wall)",
        description: "Calculates the elastic stress increase due to a line load next to a buried earth-retaining structure.",
        type: "object",
        properties: {
            lineload: { type: "number", title: "Line Load [kN/m]", minimum: 0, description: "Magnitude of the applied line load" },
            toe_depth: { type: "number", title: "Toe Depth [m]", minimum: 0, description: "Depth of the toe of the retaining wall" },
            horizontal_offset: { type: "number", title: "Horizontal Offset [m]", minimum: 0, description: "Offset between the line load and the retaining structure" },
            depth: { type: "number", title: "Depth [m]", minimum: 0, description: "Depth considered for the calculation" }
        },
        required: ["lineload", "toe_depth", "horizontal_offset", "depth"],
        documentation: `
            <h3>Stress Distribution - Line Load (Retaining Wall)</h3>
            <p>Calculates the elastic stress increase due to a line load (infinitely long out of plane) next to a buried earth-retaining structure.</p>
        `
    },
    stresses_pointload: {
        title: "Stress Distribution - Point Load",
        description: "Calculates stresses at a point below a point load (Boussinesq).",
        type: "object",
        properties: {
            pointload: { type: "number", title: "Point Load (Q) [kN]", description: "Magnitude of the point load" },
            z: { type: "number", title: "Vertical depth (z) [m]", minimum: 0, description: "Vertical distance from the surface" },
            r: { type: "number", title: "Radial distance (r) [m]", minimum: 0, description: "Radial distance from the surface" },
            poissonsratio: { type: "number", title: "Poisson's Ratio", minimum: 0, maximum: 0.5, default: 0.3, description: "Poisson's ratio" }
        },
        required: ["pointload", "z", "r"],
        documentation: `
            <h3>Stress Distribution - Point Load</h3>
            <p>Calculates the stresses at a point below a line load according the solution proposed by Boussinesq (1885).</p>
        `
    },
    stresses_rectangle: {
        title: "Stress Distribution - Rectangular Footing",
        description: "Calculates stresses under the corner of a uniformly loaded rectangular area.",
        type: "object",
        properties: {
            imposedstress: { type: "number", title: "Imposed Stress (q) [kPa]", description: "Stress applied to the uniformly loaded area" },
            length: { type: "number", title: "Length (L) [m]", minimum: 0, description: "Dimension of the longest edge of the rectangle" },
            width: { type: "number", title: "Width (B) [m]", minimum: 0, description: "Dimension of the shortest edge of the rectangle" },
            z: { type: "number", title: "Depth below footing (z) [m]", minimum: 0, description: "Depth below the footing" }
        },
        required: ["imposedstress", "length", "width", "z"],
        documentation: `
            <h3>Stress Distribution - Rectangular Footing</h3>
            <p>Calculates the stresses under the corner of a uniformly loaded rectangular area. Stresses under other points can be calculated by superposition.</p>
        `
    },
    stresses_stripload: {
        title: "Stress Distribution - Strip Load",
        description: "Calculates stress redistribution due to a strip load.",
        type: "object",
        properties: {
            z: { type: "number", title: "Vertical depth (z) [m]", minimum: 0, description: "Vertical distance from the soil surface" },
            x: { type: "number", title: "Horizontal offset (x) [m]", description: "Horizontal offset from the leftmost corner of the strip footing" },
            width: { type: "number", title: "Width (B) [m]", minimum: 0, description: "Width of the strip footing" },
            imposedstress: { type: "number", title: "Imposed Stress (q) [kPa]", description: "Maximum value of the imposed force per unit area" },
            triangular: { type: "boolean", title: "Triangular Load?", default: false, description: "Boolean determining whether a triangular load pattern is applied" }
        },
        required: ["z", "x", "width", "imposedstress"],
        documentation: `
            <h3>Stress Distribution - Strip Load</h3>
            <p>Calculates the stress redistribution at a point in the subsoil due to a strip load with a given width, applied at the surface.</p>
        `
    },
    stresses_stripload_retainingwall: {
        title: "Stress Distribution - Strip Load (Retaining Wall)",
        description: "Calculates the elastic stress increase due to a strip load next to a buried earth-retaining structure.",
        type: "object",
        properties: {
            imposedstress: { type: "number", title: "Imposed Stress [kPa]", minimum: 0, description: "Applied stress for the strip load" },
            width: { type: "number", title: "Width [m]", minimum: 0, description: "Width of the strip load" },
            offset: { type: "number", title: "Offset [m]", minimum: 0, description: "Shortest horizontal offset between the strip load and the retaining wall" },
            toe_depth: { type: "number", title: "Toe Depth [m]", minimum: 0, description: "Toe depth of the retaining structure" },
            depth: { type: "number", title: "Depth [m]", minimum: 0, description: "Depth for the stress calculation" }
        },
        required: ["imposedstress", "width", "offset", "toe_depth", "depth"],
        documentation: `
            <h3>Stress Distribution - Strip Load (Retaining Wall)</h3>
            <p>Calculates the elastic stress increase due to a strip load (infinitely long out of plane) at an offset from a buried earth-retaining structure.</p>
        `
    },

    // --- Shallow Foundation Capacity (Classes) ---
    shallow_foundation_capacity_undrained: {
        title: "Shallow Foundation Capacity - Undrained",
        description: "Comprehensive undrained capacity analysis (Bearing, Sliding, Envelope).",
        type: "object",
        properties: {
            foundation_shape: { type: "string", title: "Shape", enum: ["rectangle", "circle"], default: "rectangle", description: "Shape of the foundation" },
            length: { type: "number", title: "Length (L) [m]", minimum: 0, description: "Foundation length (rectangular)" },
            width: { type: "number", title: "Width (B) / Diameter (D) [m]", minimum: 0, description: "Foundation width or diameter" },
            eccentricity_length: { type: "number", title: "Eccentricity L [m]", default: 0, description: "Eccentricity in length direction" },
            eccentricity_width: { type: "number", title: "Eccentricity B [m]", default: 0, description: "Eccentricity in width direction" },
            unit_weight: { type: "number", title: "Unit Weight [kN/m3]", minimum: 12, maximum: 22, description: "Unit weight of the soil" },
            su_base: { type: "number", title: "Su at Base [kPa]", minimum: 0, description: "Undrained shear strength at foundation base level" },
            su_increase: { type: "number", title: "Su Increase [kPa/m]", default: 0, description: "Linear increase in undrained shear strength" },
            su_above_base: { type: "number", title: "Avg Su above base [kPa]", description: "Average undrained shear strength above base level" },
            base_depth: { type: "number", title: "Base Depth [m]", default: 0, minimum: 0 },
            skirted: { type: "boolean", title: "Skirted?", default: true },
            factor_sliding: { type: "number", title: "Factor (Sliding)", default: 1.5, minimum: 1.0, description: "Safety factor for sliding capacity" },
            factor_bearing: { type: "number", title: "Factor (Bearing)", default: 2.0, minimum: 1.0, description: "Safety factor for vertical bearing capacity" }
        },
        required: ["foundation_shape", "width", "unit_weight", "su_base"],
        documentation: `
            <h3>Shallow Foundation Capacity - Undrained</h3>
            <p>Generates a capacity analysis for undrained (short term) conditions. Includes bearing capacity, sliding capacity, and failure envelopes.</p>
        `
    },
    shallow_foundation_capacity_drained: {
        title: "Shallow Foundation Capacity - Drained",
        description: "Comprehensive drained capacity analysis (Bearing, Sliding, Envelope).",
        type: "object",
        properties: {
            foundation_shape: { type: "string", title: "Shape", enum: ["rectangle", "circle"], default: "rectangle", description: "Shape of the foundation" },
            length: { type: "number", title: "Length (L) [m]", minimum: 0, description: "Foundation length (rectangular)" },
            width: { type: "number", title: "Width (B) / Diameter (D) [m]", minimum: 0, description: "Foundation width or diameter" },
            eccentricity_length: { type: "number", title: "Eccentricity L [m]", default: 0, description: "Eccentricity in length direction" },
            eccentricity_width: { type: "number", title: "Eccentricity B [m]", default: 0, description: "Eccentricity in width direction" },
            effective_unit_weight: { type: "number", title: "Effective Unit Weight [kN/m3]", minimum: 2, maximum: 12, description: "Effective unit weight of the soil" },
            friction_angle: { type: "number", title: "Friction Angle [deg]", minimum: 20, maximum: 50, description: "Effective friction angle" },
            effective_stress_base: { type: "number", title: "Eff. Stress at Base [kPa]", minimum: 0, description: "Vertical effective stress at base level" },
            vertical_load: { type: "number", title: "Vertical Load [kN]", minimum: 0, description: "Vertical load for sliding check" },
            base_depth: { type: "number", title: "Base Depth [m]", default: 0, minimum: 0 },
            skirted: { type: "boolean", title: "Skirted?", default: true },
            factor_sliding: { type: "number", title: "Factor (Sliding)", default: 1.5, minimum: 1.0 },
            factor_bearing: { type: "number", title: "Factor (Bearing)", default: 2.0, minimum: 1.0 }
        },
        required: ["foundation_shape", "width", "effective_unit_weight", "friction_angle", "effective_stress_base", "vertical_load"],
        documentation: `
            <h3>Shallow Foundation Capacity - Drained</h3>
            <p>Generates a capacity analysis for drained (long term) conditions. Includes bearing capacity, sliding capacity, and failure envelopes.</p>
        `
    },

    // --- Capacity (Stateless/API) ---
    effectivearea_circle_api: {
        title: "Effective Area - Circular (API)",
        description: "Calculates reduced area for circular foundation (API RP 2GEO).",
        type: "object",
        properties: {
            foundation_radius: { type: "number", title: "Foundation Radius [m]", minimum: 0.01 },
            vertical_load: { type: "number", title: "Vertical Load (V) [kN]", minimum: 0.01 },
            overturning_moment: { type: "number", title: "Overturning Moment (M) [kNm]", minimum: 0, default: 0 },
            eccentricity: { type: "number", title: "Eccentricity (e) [m]", minimum: 0, default: 0 }
        },
        required: ["foundation_radius"],
        documentation: `
            <h3>Effective Area - Circular (API)</h3>
            <p>Calculates the reduced area for a circular foundation to account for load eccentricity.</p>
        `
    },
    effectivearea_rectangle_api: {
        title: "Effective Area - Rectangular (API)",
        description: "Calculates reduced area for rectangular footing (API RP 2GEO).",
        type: "object",
        properties: {
            length: { type: "number", title: "Length (L) [m]", minimum: 0, description: "Longest foundation dimension" },
            width: { type: "number", title: "Width (B) [m]", minimum: 0, description: "Shortest foundation dimension" },
            vertical_load: { type: "number", title: "Vertical Load (V) [kN]", minimum: 0.001 },
            moment_length: { type: "number", title: "Moment Length (M_L) [kNm]", minimum: 0, default: 0 },
            moment_width: { type: "number", title: "Moment Width (M_B) [kNm]", minimum: 0, default: 0 },
            eccentricity_length: { type: "number", title: "Eccentricity Length [m]", minimum: 0, default: 0 },
            eccentricity_width: { type: "number", title: "Eccentricity Width [m]", minimum: 0, default: 0 }
        },
        required: ["length", "width"],
        documentation: `
            <h3>Effective Area - Rectangular (API)</h3>
            <p>Calculates the reduced area of a rectangular footing to account for eccentricity of the load.</p>
        `
    },
    envelope_drained_api: {
        title: "Envelope - Drained (API)",
        description: "Calculates a drained failure envelope for shallow foundations.",
        type: "object",
        properties: {
            vertical_effective_stress: { type: "number", title: "Vert. Eff. Stress [kPa]", minimum: 0 },
            effective_friction_angle: { type: "number", title: "Eff. Friction Angle [deg]", minimum: 20, maximum: 50 },
            effective_unit_weight: { type: "number", title: "Eff. Unit Weight [kN/m3]", minimum: 3, maximum: 12 },
            effective_length: { type: "number", title: "Effective Length [m]", minimum: 0 },
            effective_width: { type: "number", title: "Effective Width [m]", minimum: 0 },
            full_area: { type: "number", title: "Full Area [m2]", minimum: 0 },
            base_depth: { type: "number", title: "Base Depth [m]", default: 0, minimum: 0 },
            skirted: { type: "boolean", title: "Skirted?", default: true },
            embedded_section_area: { type: "number", title: "Embedded Section Area [m2]", default: 0, minimum: 0 },
            depth_to_base: { type: "number", title: "Depth to Base [m]", default: 0, minimum: 0 },
            reaction_factor_override: { type: "number", title: "Reaction Factor Override (Krd)", description: "Drained horizontal reaction factor." },
            factor_sliding: { type: "number", title: "Factor (Sliding)", default: 1.5, minimum: 1.0 },
            factor_bearing: { type: "number", title: "Factor (Bearing)", default: 2.0, minimum: 1.0 },
            effective_friction_angle_sliding: { type: "number", title: "Sliding Friction Angle [deg]", minimum: 15, maximum: 45 }
        },
        required: ["vertical_effective_stress", "effective_friction_angle", "effective_unit_weight", "effective_length", "effective_width", "full_area"],
        documentation: `
            <h3>Envelope - Drained (API)</h3>
            <p>Calculates a drained failure envelope for shallow foundations according to API RP 2GEO.</p>
        `
    },
    envelope_undrained_api: {
        title: "Envelope - Undrained (API)",
        description: "Calculates the undrained failure envelope according to API RP 2GEO.",
        type: "object",
        properties: {
            su_base: { type: "number", title: "Su at Base [kPa]", minimum: 0, maximum: 1000 },
            full_area: { type: "number", title: "Full Area [m2]", minimum: 0 },
            effective_length: { type: "number", title: "Effective Length [m]", minimum: 0 },
            effective_width: { type: "number", title: "Effective Width [m]", minimum: 0 },
            base_depth: { type: "number", title: "Base Depth [m]", default: 0, minimum: 0 },
            su_above_base: { type: "number", title: "Avg Su above base [kPa]", description: "Average undrained shear strength along the skirt depth / above base." },
            skirted: { type: "boolean", title: "Skirted?", default: true },
            embedded_section_area: { type: "number", title: "Embedded Section Area [m2]", default: 0, minimum: 0 },
            soil_reaction_coefficient: { type: "number", title: "Soil Reaction Coeff (Kru)", default: 4, minimum: 1 },
            factor_sliding: { type: "number", title: "Factor (Sliding)", default: 1.5, minimum: 1.0 },
            factor_bearing: { type: "number", title: "Factor (Bearing)", default: 2.0, minimum: 1.0 }
        },
        required: ["su_base", "full_area", "effective_length", "effective_width"],
        documentation: `
            <h3>Envelope - Undrained (API)</h3>
            <p>Calculates the undrained failure envelope according to API RP 2GEO.</p>
        `
    },
    failuremechanism_prandtl: {
        title: "Failure Mechanism - Prandtl",
        description: "Calculates the shape of the Prandtl failure mechanism.",
        type: "object",
        properties: {
            friction_angle: { type: "number", title: "Friction Angle [deg]", minimum: 0, maximum: 60 },
            width: { type: "number", title: "Footing Width [m]", minimum: 0 },
            showfig: { type: "boolean", title: "Show Figure", default: true }
        },
        required: ["friction_angle", "width"],
        documentation: `
            <h3>Failure Mechanism - Prandtl</h3>
            <p>Calculates the shape of the Prandtl failure mechanism for a given friction angle.</p>
        `
    },
    ngamma_frictionangle_davisbooker: {
        title: "N_gamma - Davis & Booker",
        description: "Calculates N_gamma bearing capacity factor (Davis & Booker).",
        type: "object",
        properties: {
            friction_angle: { type: "number", title: "Friction Angle [deg]", minimum: 20, maximum: 50 },
            roughness_factor: { type: "number", title: "Roughness (0=Smooth, 1=Rough)", minimum: 0, maximum: 1 }
        },
        required: ["friction_angle", "roughness_factor"],
        documentation: `
            <h3>N_gamma - Davis & Booker</h3>
            <p>Calculates the bearing capacity factor Ngamma according to the equation proposed by Davis and Booker (1971).</p>
        `
    },
    ngamma_frictionangle_meyerhof: {
        title: "N_gamma - Meyerhof",
        description: "Calculates N_gamma bearing capacity factor (Meyerhof).",
        type: "object",
        properties: {
            friction_angle: { type: "number", title: "Friction Angle [deg]", minimum: 20, maximum: 50 }
        },
        required: ["friction_angle"],
        documentation: `
            <h3>N_gamma - Meyerhof</h3>
            <p>Calculates the bearing capacity factor Ngamma according to the equation proposed by Meyerhof (1976).</p>
        `
    },
    ngamma_frictionangle_vesic: {
        title: "N_gamma - Vesic",
        description: "Calculates N_gamma bearing capacity factor (Vesic).",
        type: "object",
        properties: {
            friction_angle: { type: "number", title: "Friction Angle [deg]", minimum: 20, maximum: 50 }
        },
        required: ["friction_angle"],
        documentation: `
            <h3>N_gamma - Vesic</h3>
            <p>Calculates the bearing capacity factor Ngamma according to the equation proposed by Vesic (1973).</p>
        `
    },
    nq_frictionangle_sand: {
        title: "N_q - Sand",
        description: "Calculates N_q bearing capacity factor.",
        type: "object",
        properties: {
            friction_angle: { type: "number", title: "Friction Angle [deg]", minimum: 20, maximum: 50 }
        },
        required: ["friction_angle"],
        documentation: `
            <h3>N_q - Sand</h3>
            <p>Calculate the bearing capacity factor Nq from the friction angle.</p>
        `
    },
    slidingcapacity_drained_api: {
        title: "Sliding Capacity - Drained (API)",
        description: "Calculates drained sliding capacity (API RP 2GEO).",
        type: "object",
        properties: {
            vertical_load: { type: "number", title: "Vertical Load (V) [kN]", minimum: 0 },
            effective_friction_angle: { type: "number", title: "Eff. Friction Angle [deg]", minimum: 20, maximum: 50 },
            effective_unit_weight: { type: "number", title: "Eff. Unit Weight [kN/m3]", minimum: 3, maximum: 12 },
            embedded_section_area: { type: "number", title: "Embedded Section Area [m2]", default: 0, minimum: 0 },
            depth_to_base: { type: "number", title: "Depth to Base [m]", default: 0, minimum: 0 },
            reaction_factor_override: { type: "number", title: "Reaction Factor Override (Krd)", description: "Drained horizontal reaction factor. If left blank, it is calculated from friction angle." }
        },
        required: ["vertical_load", "effective_friction_angle", "effective_unit_weight"],
        documentation: `
            <h3>Sliding Capacity - Drained (API)</h3>
            <p>Calculates the drained sliding capacity for a shallow foundation.</p>
        `
    },
    slidingcapacity_undrained_api: {
        title: "Sliding Capacity - Undrained (API)",
        description: "Calculates undrained sliding capacity (API RP 2GEO).",
        type: "object",
        properties: {
            su_base: { type: "number", title: "Su at Base [kPa]", minimum: 0 },
            foundation_area: { type: "number", title: "Foundation Area [m2]", minimum: 0 },
            su_above_base: { type: "number", title: "Avg Su above base [kPa]", default: 0, minimum: 0 },
            embedded_section_area: { type: "number", title: "Embedded Section Area [m2]", default: 0, minimum: 0 },
            soil_reaction_coefficient: { type: "number", title: "Soil Reaction Coeff (Kru)", default: 4, minimum: 1, maximum: 6 }
        },
        required: ["su_base", "foundation_area"],
        documentation: `
            <h3>Sliding Capacity - Undrained (API)</h3>
            <p>Calculates the undrained sliding capacity for a shallow foundation on clay.</p>
        `
    },
    verticalcapacity_drained_api: {
        title: "Vertical Capacity - Drained (API)",
        description: "Calculates drained vertical capacity (API RP 2GEO).",
        type: "object",
        properties: {
            vertical_effective_stress: { type: "number", title: "Vert. Eff. Stress [kPa]", minimum: 0 },
            effective_friction_angle: { type: "number", title: "Eff. Friction Angle [deg]", minimum: 20, maximum: 50 },
            effective_unit_weight: { type: "number", title: "Eff. Unit Weight [kN/m3]", minimum: 3, maximum: 12 },
            effective_length: { type: "number", title: "Eff. Length [m]", minimum: 0 },
            effective_width: { type: "number", title: "Eff. Width [m]", minimum: 0 },
            base_depth: { type: "number", title: "Base Depth [m]", default: 0, minimum: 0 },
            skirted: { type: "boolean", title: "Skirted?", default: true },
            load_inclination: { type: "number", title: "Load Inclination (H_eff/V_eff)", default: 0, minimum: 0 },
            foundation_inclination: { type: "number", title: "Foundation Inclination [deg]", default: 0, minimum: -90, maximum: 90 },
            ground_surface_inclination: { type: "number", title: "Ground Surface Inclination [deg]", default: 0, minimum: -90, maximum: 90 }
        },
        required: ["vertical_effective_stress", "effective_friction_angle", "effective_unit_weight", "effective_length", "effective_width"],
        documentation: `
            <h3>Vertical Capacity - Drained (API)</h3>
            <p>Calculates the vertical capacity for a shallow foundation in sand with effective friction angle characterized from drained triaxial tests.</p>
        `
    },
    verticalcapacity_undrained_api: {
        title: "Vertical Capacity - Undrained (API)",
        description: "Calculates undrained vertical capacity (API RP 2GEO).",
        type: "object",
        properties: {
            effective_length: { type: "number", title: "Eff. Length [m]", minimum: 0 },
            effective_width: { type: "number", title: "Eff. Width [m]", minimum: 0 },
            su_base: { type: "number", title: "Su at Base [kPa]", minimum: 0 },
            su_increase: { type: "number", title: "Su Increase [kPa/m]", default: 0, minimum: 0 },
            base_depth: { type: "number", title: "Base Depth [m]", default: 0, minimum: 0 },
            skirted: { type: "boolean", title: "Skirted?", default: true },
            roughness: { type: "number", title: "Roughness (0-1)", default: 0.67, minimum: 0, maximum: 1 },
            su_above_base: { type: "number", title: "Avg Su above base [kPa]", description: "Average undrained shear strength along the skirt depth / above base. Required if Su Increase > 0." },
            base_sigma_v: { type: "number", title: "Total stress at base [kPa]", default: 0, description: "Vertical total stress at base level. Used for non-skirted foundations." }
        },
        required: ["effective_length", "effective_width", "su_base"],
        documentation: `
            <h3>Vertical Capacity - Undrained (API)</h3>
            <p>Calculates the vertical capacity for a shallow foundation in clay with constant or linearly increasing undrained shear strength according to API RP 2GEO.</p>
        `
    }
};

export { shallowFoundationsSchemas };
