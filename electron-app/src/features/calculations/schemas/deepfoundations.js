/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

export const deepFoundationsSchemas = {
    // --- Unit Skin Friction ---
    API_unit_shaft_friction_clay: {
        title: "API Unit Shaft Friction - Clay",
        description: "Calculates unit skin friction according to the alpha method in API RP 2GEO.",
        type: "object",
        properties: {
            undrained_shear_strength: {
                type: "number",
                title: "Undrained Shear Strength (s_u) [kPa]",
                minimum: 0,
                maximum: 400,
                description: "Undrained shear strength of the clay"
            },
            sigma_vo_eff: {
                type: "number",
                title: "In-situ Vert. Eff. Stress (sigma' v0) [kPa]",
                minimum: 0,
                description: "In-situ vertical effective stress at the depth of interest"
            }
        },
        required: ["undrained_shear_strength", "sigma_vo_eff"],
        documentation: `
            <h3>API Unit Shaft Friction - Clay</h3>
            <p>Calculates unit skin friction according to the alpha method in API RP 2GEO (2011).</p>
            <p><strong>Caution:</strong> The function should be applied with considerable care for high ratios of undrained shear strength to vertical effective stress (> 3). Low plasticity clays should be treated with particular caution.</p>
        `
    },
    API_unit_shaft_friction_sand_rp2geo: {
        title: "API Unit Shaft Friction - Sand (RP 2GEO)",
        description: "Calculates unit skin friction according to the beta method in API RP 2GEO.",
        type: "object",
        properties: {
            api_relativedensity: {
                type: "string",
                title: "Relative Density",
                enum: ["Very loose", "Loose", "Medium dense", "Dense", "Very dense"],
                default: "Medium dense",
                description: "Relative density of the sand"
            },
            api_soildescription: {
                type: "string",
                title: "Soil Description",
                enum: ["Sand", "Sand-silt"],
                default: "Sand",
                description: "Description of the soil type"
            },
            sigma_vo_eff: {
                type: "number",
                title: "In-situ Vert. Eff. Stress (sigma' v0) [kPa]",
                minimum: 0,
                description: "In-situ vertical effective stress"
            },
            fs_limit: {
                type: "boolean",
                title: "Apply f_s limit?",
                default: false,
                description: "Whether to apply the unit skin friction limit"
            },
            tension_modifier: {
                type: "number",
                title: "Tension Modifier",
                default: 1.0,
                description: "Multiplier applied for tension loading"
            }
        },
        required: ["api_relativedensity", "api_soildescription", "sigma_vo_eff"],
        documentation: `
            <h3>API Unit Shaft Friction - Sand (RP 2GEO)</h3>
            <p>Calculates unit skin friction according to the beta method in API RP 2GEO. The beta-parameter is defined directly in API RP 2GEO.</p>
        `
    },
    unitskinfriction_clay_almhamre: {
        title: "Unit Skin Friction - Clay (Alm & Hamre)",
        description: "Calculates the unit skin friction in clay according to the method by Alm & Hamre (2001).",
        type: "object",
        properties: {
            depth: { type: "number", title: "Calculation Depth [m]", minimum: 0 },
            embedded_length: { type: "number", title: "Pile Tip Depth [m]", minimum: 0, description: "Depth of the pile tip below mudline" },
            qt: { type: "number", title: "Total Cone Resistance (q_t) [MPa]", minimum: 0, maximum: 120 },
            fs: { type: "number", title: "Sleeve Friction (f_s) [kPa]", minimum: 0 },
            sigma_vo_eff: { type: "number", title: "Vertical Effective Stress (sigma' v0) [kPa]", minimum: 0 },
            shape_factor_multiplier: { type: "number", title: "Shape Factor Multiplier (k)", default: 80.0 },
            multiplier_fsres_1: { type: "number", title: "Multiplier f_s,res 1", default: 0.004 },
            multiplier_fsres_2: { type: "number", title: "Multiplier f_s,res 2", default: 0.0025 },
            multiplier_fs_initial: { type: "number", title: "Multiplier f_s,initial", default: 1.0 },
            multiplier_outside: { type: "number", title: "Multiplier Outside", default: 1.0 },
            multiplier_inside: { type: "number", title: "Multiplier Inside", default: 1.0 }
        },
        required: ["depth", "embedded_length", "qt", "fs", "sigma_vo_eff"],
        documentation: `
            <h3>Unit Skin Friction - Clay (Alm & Hamre)</h3>
            <p>Calculates the unit skin friction in clay according to the method by Alm & Hamre. Includes the effect of friction fatigue based on back-analysis from North Sea jacket piles.</p>
        `
    },
    unitskinfriction_sand_almhamre: {
        title: "Unit Skin Friction - Sand (Alm & Hamre)",
        description: "Calculates the unit skin friction in sand according to the method by Alm & Hamre (2001).",
        type: "object",
        properties: {
            qt: { type: "number", title: "Total Cone Resistance (q_t) [MPa]", minimum: 0, maximum: 120 },
            sigma_vo_eff: { type: "number", title: "Vertical Effective Stress (sigma' v0) [kPa]", minimum: 0 },
            interface_friction_angle: { type: "number", title: "Interface Friction Angle [deg]", minimum: 10, maximum: 50 },
            depth: { type: "number", title: "Calculation Depth [m]", minimum: 0 },
            embedded_length: { type: "number", title: "Pile Tip Depth [m]", minimum: 0 },
            shape_factor_multiplier: { type: "number", title: "Shape Factor Multiplier (k)", default: 80.0 },
            atmospheric_pressure: { type: "number", title: "Atmospheric Pressure [kPa]", default: 101.325 },
            fsi_sand_multiplier: { type: "number", title: "f_s,i Sand Multiplier", default: 0.0132 },
            fsi_sand_exponent: { type: "number", title: "f_s,i Sand Exponent", default: 0.13 },
            multiplier_fsres: { type: "number", title: "Multiplier f_s,res", default: 0.2 },
            multiplier_outside: { type: "number", title: "Multiplier Outside", default: 0.5 },
            multiplier_inside: { type: "number", title: "Multiplier Inside", default: 0.5 }
        },
        required: ["qt", "sigma_vo_eff", "interface_friction_angle", "depth", "embedded_length"],
        documentation: `
            <h3>Unit Skin Friction - Sand (Alm & Hamre)</h3>
            <p>Calculates the unit skin friction in sand according to the method by Alm & Hamre. Includes the effect of friction fatigue.</p>
        `
    },
    // --- Unit End Bearing ---
    API_unit_end_bearing_clay: {
        title: "API Unit End Bearing - Clay",
        description: "Calculates unit end bearing in clay according to API RP 2GEO.",
        type: "object",
        properties: {
            undrained_shear_strength: {
                type: "number",
                title: "Undrained Shear Strength at Tip (s_u) [kPa]",
                minimum: 0,
                maximum: 400,
                description: "Undrained shear strength at the pile tip"
            },
            N_c: {
                type: "number",
                title: "Bearing Capacity Factor (N_c)",
                default: 9.0,
                minimum: 7.0,
                maximum: 12.0,
                description: "Bearing capacity factor"
            }
        },
        required: ["undrained_shear_strength"],
        documentation: `
            <h3>API Unit End Bearing - Clay</h3>
            <p>Calculates unit end bearing in clay according to API RP 2GEO (2011).</p>
            <p>For piles considered to be plugged, the bearing pressure may be assumed to act over the entire cross-section. For unplugged piles, it acts on the pile wall annulus only.</p>
        `
    },
    API_unit_end_bearing_sand_rp2geo: {
        title: "API Unit End Bearing - Sand (RP 2GEO)",
        description: "Calculates unit end bearing in sand according to API RP 2GEO.",
        type: "object",
        properties: {
            api_relativedensity: {
                type: "string",
                title: "Relative Density",
                enum: ["Very loose", "Loose", "Medium dense", "Dense", "Very dense"],
                default: "Medium dense"
            },
            api_soildescription: {
                type: "string",
                title: "Soil Description",
                enum: ["Sand", "Sand-silt"],
                default: "Sand"
            },
            sigma_vo_eff: {
                type: "number",
                title: "Vert. Eff. Stress at Tip (sigma' v0) [kPa]",
                minimum: 0,
                description: "In-situ vertical effective stress at the pile tip"
            },
            qb_limit: {
                type: "boolean",
                title: "Apply q_b limit?",
                default: false
            }
        },
        required: ["api_relativedensity", "api_soildescription", "sigma_vo_eff"],
        documentation: `
            <h3>API Unit End Bearing - Sand (RP 2GEO)</h3>
            <p>Calculates unit end bearing in sand according to API RP 2GEO (2011).</p>
        `
    },
    unitendbearing_clay_almhamre: {
        title: "Unit End Bearing - Clay (Alm & Hamre)",
        description: "Calculates unit end bearing in clay according to Alm & Hamre.",
        type: "object",
        properties: {
            qt: {
                type: "number",
                title: "Total Cone Resistance (q_t) [MPa]",
                minimum: 0,
                maximum: 120
            },
            multiplier: {
                type: "number",
                title: "End Bearing Multiplier",
                default: 0.6,
                description: "Multiplier for unit end bearing"
            }
        },
        required: ["qt"],
        documentation: `
            <h3>Unit End Bearing - Clay (Alm & Hamre)</h3>
            <p>Calculates unit end bearing in clay according to Alm & Hamre. This method is often used for driveability predictions.</p>
        `
    },
    unitendbearing_sand_almhamre: {
        title: "Unit End Bearing - Sand (Alm & Hamre)",
        description: "Calculates unit end bearing in sand according to Alm & Hamre.",
        type: "object",
        properties: {
            qt: {
                type: "number",
                title: "Total Cone Resistance (q_t) [MPa]",
                minimum: 0,
                maximum: 120
            },
            sigma_vo_eff: {
                type: "number",
                title: "Vertical Effective Stress (sigma' v0) [kPa]",
                minimum: 0
            },
            multiplier: {
                type: "number",
                title: "End Bearing Multiplier",
                default: 0.15
            },
            exponent: {
                type: "number",
                title: "End Bearing Exponent",
                default: 0.2
            }
        },
        required: ["qt", "sigma_vo_eff"],
        documentation: `
            <h3>Unit End Bearing - Sand (Alm & Hamre)</h3>
            <p>Calculates unit end bearing in sand according to Alm & Hamre.</p>
        `
    },
    // --- Axial Capacity ---
    AxCapCalculation: {
        title: "Axial Capacity Calculation (AxCap)",
        description: "Calculates total axial capacity profile for a pile.",
        type: "object",
        properties: {
            soilprofile: {
                type: "object_select",
                title: "Soil Profile",
                description: "Select a Soil Profile with 'Unit skin friction' and 'Unit end bearing' columns",
                objectType: "SoilProfile"
            },
            circumference: {
                type: "number",
                title: "Pile Circumference [m]",
                minimum: 0
            },
            base_area: {
                type: "number",
                title: "Pile Base Area [m2]",
                minimum: 0
            },
            internal_circumference: {
                type: "number",
                title: "Internal Circumference [m] (Optional)",
                description: "Required for coring conditions"
            },
            annulus_area: {
                type: "number",
                title: "Annulus Area [m2] (Optional)",
                description: "Required for coring conditions"
            },
            pile_weight_permeter: {
                type: "number",
                title: "Pile Weight [kN/m]",
                default: 0
            },
            soilplug_weight_permeter: {
                type: "number",
                title: "Soil Plug Weight [kN/m]",
                default: 0
            },
            dz: {
                type: "number",
                title: "Grid Spacing (dz) [m]",
                default: 1.0,
                minimum: 0.1
            }
        },
        required: ["soilprofile", "circumference", "base_area"],
        documentation: `
            <h3>Axial Capacity Calculation</h3>
            <p>Calculates the compression and tension capacity of a pile vs depth.</p>
            <p>Requires a Soil Profile that already has <b>Unit skin friction</b> and <b>Unit end bearing</b> calculated (e.g. using the Unit Skin Friction/End Bearing modules).</p>
        `
    },
    // --- De Beer ---
    DeBeerCalculation: {
        title: "De Beer Calculation (Eurocode 7)",
        description: "Calculates pile capacity using De Beer's method and CPT data.",
        type: "object",
        properties: {
            soilprofile: {
                type: "object_select",
                title: "Soil Profile (w/ CPT Data)",
                description: "Select a Soil Profile containing CPT data (qc) and soil type information",
                objectType: "SoilProfile"
            },
            pile_diameter: {
                type: "number",
                title: "Pile Diameter [m]",
                minimum: 0.2,
                description: "Diameter of the pile (min 0.2m)"
            },
            cone_diameter: {
                type: "number",
                title: "Cone Diameter [m]",
                default: 0.0357,
                minimum: 0
            },
            qc_col: {
                type: "column_select",
                title: "Cone Resistance Column",
                description: "Column name for qc in the Soil Profile"
            },
            depth_col: {
                type: "column_select",
                title: "Depth Column",
                description: "Column name for depth (positive downwards)"
            },
            soil_type_col: {
                type: "column_select",
                title: "Soil Type Column",
                description: "Column name for soil type (Clay, Sand, etc.)"
            },
            tertiary_clay_col: {
                type: "column_select",
                title: "Tertiary Clay Column",
                description: "Column name for Tertiary clay boolean (optional)"
            },
            gamma_col: {
                type: "column_select",
                title: "Total Unit Weight Column",
                description: "Column name for total unit weight"
            },
            water_level: {
                type: "number",
                title: "Water Level [m]",
                default: 0,
                description: "Depth of the water table"
            },
            alpha_b_tertiary_clay: {
                type: "number",
                title: "Alpha b (Tertiary Clay)",
                default: 0.5,
                description: "Base factor for tertiary clay"
            },
            alpha_b_other: {
                type: "number",
                title: "Alpha b (Other)",
                default: 0.5,
                description: "Base factor for other soils"
            },
            alpha_s_tertiary_clay: {
                type: "number",
                title: "Alpha s (Tertiary Clay)",
                default: 0.025,
                description: "Shaft factor for tertiary clay"
            },
            alpha_s_other: {
                type: "number",
                title: "Alpha s (Other)",
                default: 0.01,
                description: "Shaft factor for other soils"
            }
        },
        required: ["soilprofile", "pile_diameter", "qc_col", "depth_col", "soil_type_col", "gamma_col"],
        documentation: `
            <h3>De Beer Calculation</h3>
            <p>Calculates pile base and shaft resistance based on CPT data according to De Beer's method.</p>
            <p>Requires a Soil Profile with:
                <ul>
                    <li><b>qc [MPa]</b>: Cone resistance data</li>
                    <li><b>Soil type</b>: 'Clay', 'Sand', 'Loam (silt)', etc. (Belgian classification)</li>
                    <li><b>Total unit weight [kN/m3]</b></li>
                </ul>
            </p>
        `
    },
    // --- Koppejan ---
    KoppejanCalculation: {
        title: "Koppejan Calculation",
        description: "Calculates pile capacity according to Koppejan's method.",
        type: "object",
        properties: {
            soilprofile: {
                type: "object_select",
                title: "Soil Profile (w/ CPT Data)",
                description: "Select a Soil Profile containing CPT data (qc) and Total Unit Weight",
                objectType: "SoilProfile"
            },
            pile_diameter: {
                type: "number",
                title: "Pile Diameter [m]",
                minimum: 0,
                description: "Diameter of the pile"
            },
            pile_penetration: {
                type: "number",
                title: "Target Penetration [m] (Optional)",
                minimum: 0,
                description: "Depth for detailed analysis plots. Defaults to max depth - 4D."
            },
            qc_col: {
                type: "column_select",
                title: "Cone Resistance Column",
                description: "Column name for qc"
            },
            depth_from_col: {
                type: "column_select",
                title: "Depth From Column",
                description: "Column for layer top depth"
            },
            depth_to_col: {
                type: "column_select",
                title: "Depth To Column",
                description: "Column for layer bottom depth"
            },
            gamma_col: {
                type: "column_select",
                title: "Total Unit Weight Column",
                description: "Column name for total unit weight"
            },
            water_level: {
                type: "number",
                title: "Water Level [m]",
                default: 0,
                description: "Depth of the water table"
            },
            water_unit_weight: {
                type: "number",
                title: "Water Unit Weight [kN/m3]",
                default: 10,
                description: "Unit weight of water"
            },
            alpha_s: {
                type: "number",
                title: "Alpha s (Shaft Friction Factor)",
                default: 0.006,
                description: "Factor for shaft friction (0.006 - 0.01)"
            },
            alpha_p: {
                type: "number",
                title: "Alpha p (Base Resistance Factor)",
                default: 0.3, // Common value
                description: "Factor for base resistance (e.g. 0.3)"
            },
            base_coefficient: {
                type: "number",
                title: "Base Coefficient (Beta)",
                default: 1.0,
                description: "Coefficient for enlarged bases"
            },
            crosssection_coefficient: {
                type: "number",
                title: "Cross-section Coefficient (s)",
                default: 1.0,
                description: "Coefficient for non-circular cross-sections"
            },
            coring: {
                type: "boolean",
                title: "Coring Pile?",
                default: false,
                description: "Whether the pile behaves in a coring manner"
            },
            wall_thickness: {
                type: "number",
                title: "Wall Thickness [mm]",
                description: "Required if Coring is checked"
            }
        },
        required: ["soilprofile", "pile_diameter", "qc_col", "depth_from_col", "depth_to_col", "gamma_col"],
        documentation: `
            <h3>Koppejan Pile Calculation</h3>
            <p>Calculates pile capacity based on Koppejan's method.</p>
            <p>Generates detailed base and shaft resistance construction plots for a specific penetration depth, and a capacity profile vs depth.</p>
        `
    },
    // --- LCPC ---
    LCPC_Calculation: {
        title: "LCPC Method (Bustamante & Gianeselli)",
        description: "Calculates pile axial capacity using the LCPC method based on CPT data.",
        type: "object",
        properties: {
            soilprofile: {
                type: "object_select",
                title: "Soil Profile (w/ CPT Data)",
                description: "Select a Soil Profile containing CPT data (qc) and Soil Type.",
                objectType: "SoilProfile"
            },
            pile_diameter: {
                type: "number",
                title: "Pile Diameter [m]",
                minimum: 0.2,
                description: "Diameter of the pile (min 0.2m)"
            },
            diameter_shaft: {
                type: "number",
                title: "Shaft Diameter [m] (Optional)",
                description: "Diameter of the shaft if different from base."
            },
            group_base: {
                type: "string",
                title: "Pile Group (Base)",
                enum: ["I", "II"],
                default: "I",
                description: "LCPC Soil/Pile Group for Base Resistance"
            },
            group_shaft: {
                type: "string",
                title: "Pile Group (Shaft)",
                enum: ["IA", "IB", "IIA", "IIB"],
                default: "IA",
                description: "LCPC Soil/Pile Group for Shaft Resistance"
            },
            careful_execution: {
                type: "boolean",
                title: "Careful Execution?",
                default: false,
                description: "Use factors for careful execution (higher friction)"
            },
            qc_col: {
                type: "column_select",
                title: "Cone Resistance Column",
                description: "Column name for qc"
            },
            depth_col: {
                type: "column_select",
                title: "Depth Column",
                description: "Column name for depth"
            },
            soil_type_col: {
                type: "column_select",
                title: "Soil Type Column",
                description: "Column name for soil type (Must be: Clay, Silt, Sand, Chalk, Gravel)"
            },
            water_level: {
                type: "number",
                title: "Water Level [m]",
                default: 0,
                description: "Depth of the water table"
            }
        },
        required: ["soilprofile", "pile_diameter", "qc_col", "depth_col", "soil_type_col"],
        documentation: `
            <h3>LCPC Method (Bustamante & Gianeselli)</h3>
            <p>Calculates axial pile capacity based on CPT data.</p>
            <p><b>Important Requirements:</b></p>
            <ul>
                <li><b>Soil Type:</b> The Soil Profile MUST contain a 'Soil type' column with values restricted to: 
                    <b>'Clay', 'Silt', 'Sand', 'Chalk', 'Gravel'</b>.
                </li>
                <li><b>qc:</b> Cone resistance in MPa.</li>
            </ul>
        `
    },
    // --- Negative Skin Friction ---
    negativeskinfriction_pilegroup_zeevaertdebeer: {
        title: "Negative Skin Friction (Zeevaert & De Beer)",
        description: "Calculates negative skin friction for a pile in a group.",
        type: "object",
        properties: {
            soilprofile: {
                type: "object_select",
                title: "Soil Profile",
                description: "Select a Soil Profile containing unit weight, K0, and friction angle data",
                objectType: "SoilProfile"
            },
            eff_unit_weight_col: {
                type: "column_select",
                title: "Effective Unit Weight Column",
                description: "Column for effective unit weight"
            },
            k_col: {
                type: "column_select",
                title: "Lateral Earth Pressure Coeff. Column",
                description: "Column for lateral earth pressure coefficient (K)"
            },
            delta_col: {
                type: "column_select",
                title: "Interface Friction Angle Column",
                description: "Column for interface friction angle"
            },
            surcharge: {
                type: "number",
                title: "Surcharge [kPa]",
                default: 0,
                minimum: 0,
                description: "Surcharge load on the soil surface"
            },
            diameter: {
                type: "number",
                title: "Pile Diameter [m]",
                minimum: 0.1,
                description: "Diameter of the pile"
            },
            diameter_influence: {
                type: "number",
                title: "Diameter of Influence [m]",
                minimum: 0.1,
                description: "Diameter of the zone of influence for negative skin friction"
            }
        },
        required: ["soilprofile", "diameter", "diameter_influence", "eff_unit_weight_col", "k_col", "delta_col"],
        documentation: `
            <h3>Negative Skin Friction (Zeevaert & De Beer)</h3>
            <p>Calculates the negative skin friction for a pile using the Zeevaert & De Beer method.</p>
            <p>Requires a Soil Profile with defined columns for:
                <ul>
                    <li>Effective Unit Weight</li>
                    <li>Lateral Earth Pressure Coefficient (K)</li>
                    <li>Interface Friction Angle (delta)</li>
                </ul>
            </p>
        `
    },
    // --- Settlement ---
    PileSettlementCurves: {
        title: "Pile Settlement Curves (Load-Settlement)",
        description: "Calculates pile settlement curves for shaft and base based on empirical trends.",
        type: "object",
        properties: {
            diameter: {
                type: "number",
                title: "Pile Diameter [m]",
                minimum: 0,
                description: "Diameter of the pile"
            },
            shaft_resistance: {
                type: "number",
                title: "Total Shaft Resistance (Rs) [kN]",
                minimum: 0,
                description: "Total shaft resistance capacity"
            },
            base_resistance: {
                type: "number",
                title: "Total Base Resistance (Rb) [kN]",
                minimum: 0,
                description: "Total base resistance capacity"
            },
            pile_type: {
                type: "string",
                title: "Pile Type",
                enum: ["driven", "CFA", "bored"],
                default: "driven",
                description: "Method of pile installation"
            }
        },
        required: ["diameter", "shaft_resistance", "base_resistance", "pile_type"],
        documentation: `
            <h3>Pile Settlement Curves</h3>
            <p>Calculates the pile settlement curve for pile shaft and pile base from empirical trends established based on axial pile load tests.</p>
            <p>Generates a Load-Settlement plot showing the mobilization of shaft and base resistance.</p>
        `
    },
    // --- Pile Testing ---
    piletest_chinkondler: {
        title: "Chin-Kondler Extrapolation",
        description: "Extrapolates pile head load-settlement curve using Chin-Kondler method.",
        type: "object",
        properties: {
            soilprofile: {
                type: "object_select",
                title: "Test Data (Soil Profile)",
                description: "Select a profile containing Load and Settlement data",
                objectType: "SoilProfile"
            },
            load_col: {
                type: "column_select",
                title: "Load Column [kN]",
                description: "Column containing load test data"
            },
            settlement_col: {
                type: "column_select",
                title: "Settlement Column [mm]",
                description: "Column containing settlement data"
            },
            no_discard_points: {
                type: "integer",
                title: "Discard Points",
                default: 1,
                minimum: 0,
                description: "Number of initial points to discard for linear regression"
            },
            max_settlement: {
                type: "number",
                title: "Max Settlement for Plot [mm]",
                default: 50,
                minimum: 0,
                description: "Maximum settlement to extend the extrapolated curve to"
            },
            selected_settlement: {
                type: "number",
                title: "Selected Settlement for Q [mm]",
                default: 40,
                minimum: 0,
                description: "Settlement at which to report pile resistance (e.g. 10% D)"
            }
        },
        required: ["soilprofile", "load_col", "settlement_col"],
        documentation: `
            <h3>Chin-Kondler Extrapolation</h3>
            <p>Extrapolates a pile head load-settlement curve based on the procedure by Chin-Kondler.</p>
            <p>The settlements are divided by the corresponding loads, yielding a straight line in a graph of this fraction vs settlement.</p>
            <p>Requires a Soil Profile (or data table) with <b>Load</b> and <b>Settlement</b> columns.</p>
        `
    }
};
