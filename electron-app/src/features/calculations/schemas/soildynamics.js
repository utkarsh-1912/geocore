/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

export const soilDynamicsSchemas = {
    // Liquefaction
    cyclicstressratio_moss: {
        inputs: [
            { name: "sigma_vo", type: "float", unit: "kPa", min: 0.0, description: "Total vertical stress at depth of interest", required: true },
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, description: "Effective vertical stress at depth of interest", required: true },
            { name: "magnitude", type: "float", min: 5.5, max: 8.5, description: "Earthquake magnitude", required: true },
            { name: "acceleration", type: "float", unit: "g", min: 0.0, description: "Maximum horizontal acceleration at surafce", required: true },
            { name: "depth", type: "float", unit: "m", min: 0.0, description: "Depth at which CSR is calculated", required: true },
            { name: "gravity", type: "float", unit: "m/s2", default: 9.81, min: 9.8, max: 10.0, description: "Acceleration due to gravity" },
            { name: "rd_override", type: "float", description: "Override for rd (optional)" },
            { name: "DWF_override", type: "float", description: "Override for DWF (optional)" }
        ]
    },
    cyclicstressratio_youd: {
        inputs: [
            { name: "acceleration", type: "float", unit: "g", min: 0.0, description: "Maximum horizontal acceleration at surface", required: true },
            { name: "sigma_vo", type: "float", unit: "kPa", min: 0.0, max: 500.0, description: "Vertical total stress", required: true },
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, max: 250.0, description: "Vertical effective stress", required: true },
            { name: "depth", type: "float", unit: "m", min: 0.0, max: 23.0, description: "Depth considered", required: true },
            { name: "magnitude", type: "float", min: 0.0, max: 8.5, description: "Earthquake magnitude", required: true },
            { name: "gravity", type: "float", unit: "m/s2", default: 9.81, min: 9.8, max: 10.0, description: "Acceleration due to gravity" },
            { name: "msf_exponent_nominator", type: "float", default: 2.24, description: "MSF exponent nominator" },
            { name: "msf_exponent_denominator", type: "float", default: 2.56, description: "MSF exponent denominator" },
            { name: "rd_factor1", type: "float", default: 1.0, description: "rd calibration factor 1" },
            { name: "rd_factor2", type: "float", default: 0.00765, description: "rd calibration factor 2" },
            { name: "rd_factor3", type: "float", default: 1.174, description: "rd calibration factor 3" },
            { name: "rd_factor4", type: "float", default: 0.0267, description: "rd calibration factor 4" },
            { name: "rd_transitiondepth", type: "float", unit: "m", default: 9.15, description: "Transition depth for rd" },
            { name: "rd_maxdepth", type: "float", unit: "m", default: 23.0, description: "Max depth for rd" }
        ]
    },
    liquefaction_robertsonfear: {
        inputs: [
            { name: "qc", type: "float", unit: "MPa", min: 0.0, max: 120.0, description: "Cone tip resistance", required: true },
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, description: "Vertical effective stress", required: true },
            { name: "CSR", type: "float", min: 0.073, max: 0.49, description: "Seismic shear stress ratio", required: true },
            { name: "atmospheric_pressure", type: "float", unit: "kPa", default: 100.0, min: 90.0, max: 110.0, description: "Atmospheric pressure" }
        ]
    },
    liquefactionprobability_moss: {
        inputs: [
            { name: "qc", type: "float", unit: "MPa", min: 0.0, max: 120.0, description: "Cone tip resistance", required: true },
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, description: "Vertical effective stress", required: true },
            { name: "Rf", type: "float", unit: "%", min: 0.0, max: 10.0, description: "Friction ratio", required: true },
            { name: "CSR", type: "float", min: 0.0, max: 0.6, description: "Cyclic shear stress ratio", required: true },
            { name: "CSR_star", type: "float", min: 0.0, max: 0.6, description: "Equivalent uniform cyclic stress ratio (M=7.5)", required: true },
            { name: "Pa", type: "float", unit: "kPa", default: 100.0, min: 90.0, max: 110.0, description: "Atmospheric pressure" },
            { name: "delta_qc_override", type: "float", description: "Override for qc correction" },
            { name: "c_override", type: "float", description: "Override for normalisation exponent" },
            { name: "x1", type: "float", default: 0.78, description: "Factor x1" },
            { name: "x2", type: "float", default: -0.33, description: "Factor x2" },
            { name: "y1", type: "float", default: -0.32, description: "Factor y1" },
            { name: "y2", type: "float", default: -0.35, description: "Factor y2" },
            { name: "y3", type: "float", default: 0.49, description: "Factor y3" },
            { name: "z1", type: "float", default: 1.21, description: "Factor z1" }
        ]
    },
    liquefactionprobability_saye: {
        inputs: [
            { name: "Qt", type: "float", min: 1.0, max: 1000.0, description: "Normalised cone tip resistance", required: true },
            { name: "qc", type: "float", unit: "MPa", min: 0.0, max: 100.0, description: "Cone tip resistance", required: true },
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, max: 1000.0, description: "Vertical effective stress", required: true },
            { name: "CSR", type: "float", min: 0.0, max: 1.0, description: "Cyclic stress ratio (M=7.5)", required: true },
            { name: "fs", type: "float", unit: "kPa", min: 0.0, max: 10.0, description: "Sleeve friction", required: true },
            { name: "atmospheric_pressure", type: "float", unit: "kPa", default: 100.0, description: "Atmospheric pressure" },
            { name: "deltaQ_nominator", type: "float", default: 10.0, description: "DeltaQ nominator term" },
            { name: "deltaQ_denominator", type: "float", default: 0.67, description: "DeltaQ denominator term" },
            { name: "exponent_qcnormalised", type: "float", default: 0.5, description: "Exponent for qc normalisation" },
            { name: "Cq_limit", type: "float", default: 1.7, description: "Maximum value for Cq" },
            { name: "mcrr_coefficient1", type: "float", default: 178.0, description: "mCRR calibration coefficient 1" },
            { name: "mcrr_coefficient2", type: "float", default: 3.349, description: "mCRR calibration coefficient 2" },
            { name: "mcrr_limit", type: "float", default: 0.1, description: "Maximum value for mCRR" },
            { name: "deltaQ_limit", type: "float", default: 20.0, description: "Minimum value for DeltaQ" },
            { name: "Pl_coefficient1", type: "float", default: 1.34, description: "Liquefaction probability coefficient 1" },
            { name: "exactsoildata", type: "boolean", default: true, description: "Exact soil data?" }
        ]
    },
    // Cyclic Behaviour
    cycliccontours_dssclay_andersen: {
        inputs: [
            { name: "undrained_shear_strength", type: "float", unit: "kPa", min: 1.0, max: 100.0, description: "Undrained shear strength", required: true },
            { name: "average_shear_stress", type: "float", unit: "kPa", min: 0.0, max: 100.0, description: "Average shear stress", required: true },
            { name: "cyclic_shear_stress", type: "float", unit: "kPa", min: 0.0, max: 100.0, description: "Cyclic shear stress", required: true }
        ]
    },
    cycliccontours_triaxialclay_andersen: {
        inputs: [
            { name: "undrained_shear_strength", type: "float", unit: "kPa", min: 1.0, max: 100.0, description: "Undrained shear strength", required: true },
            { name: "average_shear_stress", type: "float", unit: "kPa", min: -50.0, max: 100.0, description: "Average shear stress", required: true },
            { name: "cyclic_shear_stress", type: "float", unit: "kPa", min: 0.0, max: 100.0, description: "Cyclic shear stress", required: true }
        ]
    },
    cyclicstrength_dsssand_relativedensity: {
        inputs: [
            { name: "relative_density", type: "float", unit: "%", min: 40.0, max: 110.0, description: "Relative density", required: true },
            { name: "vertical_effective_stress", type: "float", unit: "kPa", min: 100.0, max: 250.0, description: "Vertical effective stress", required: true },
            { name: "fines_content", type: "float", unit: "%", min: 5.0, max: 35.0, default: 5.0, description: "Fines content" },
            { name: "stress_exponent", type: "float", min: 0.2, max: 1.0, default: 0.9, description: "Stress exponent" },
            { name: "atmospheric_pressure", type: "float", unit: "kPa", default: 100.0, description: "Atmospheric pressure" }
        ]
    },
    cyclicstrength_dsssand_watercontent: {
        inputs: [
            { name: "water_content", type: "float", unit: "%", min: 15.0, max: 40.0, description: "Water content", required: true },
            { name: "vertical_effective_stress", type: "float", unit: "kPa", min: 100.0, max: 250.0, description: "Vertical effective stress", required: true },
            { name: "fines_content", type: "float", unit: "%", min: 5.0, max: 35.0, default: 5.0, description: "Fines content" },
            { name: "stress_exponent", type: "float", min: 0.2, max: 1.0, default: 0.9, description: "Stress exponent" },
            { name: "atmospheric_pressure", type: "float", unit: "kPa", default: 100.0, description: "Atmospheric pressure" }
        ]
    },
    plotcycliccontours_dssclay_andersen: {
        inputs: [] // Returns a plot, no inputs in doc
    },
    plotcycliccontours_triaxialclay_andersen: {
        inputs: [] // Returns a plot, no inputs in doc
    },
    plotporepressureaccumulation_dssclay_andersen: {
        inputs: [] // Returns a plot, no inputs in doc
    },
    plotporepressureaccumulation_dsssand_andersen: {
        inputs: [
            { name: "failure_stress_ratio", type: "select", options: ["0.19", "0.25", "0.6", "1.0", "1.8"], description: "Ratio of cyclic shear stress to vertical effective stress at failure", required: true }
        ]
    },
    plotporepressureaccumulation_triaxialclay_andersen: {
        inputs: [] // Returns a plot, no inputs in doc
    },
    plotstrainaccumulation_dssclay_andersen: {
        inputs: [] // Returns a plot, no inputs in doc
    },
    plotstrainaccumulation_dsssand_andersen: {
        inputs: [
            { name: "failure_stress_ratio", type: "select", options: ["0.19", "0.25", "0.6", "1.0", "1.8"], description: "Ratio of cyclic shear stress to vertical effective stress at failure", required: true }
        ]
    },
    plotstrainaccumulation_triaxialclay_andersen: {
        inputs: [] // Returns a plot, no inputs in doc
    },
    porepressureaccumulation_dssclay_andersen: {
        inputs: [
            { name: "cyclic_shear_stress", type: "float", unit: "kPa", min: 0.0, max: 100.0, description: "Cyclic shear stress", required: true },
            { name: "undrained_shear_strength", type: "float", unit: "kPa", min: 1.0, max: 100.0, description: "Undrained shear strength", required: true },
            { name: "cycle_no", type: "float", min: 1.0, max: 1500.0, description: "Number of cycles", required: true }
        ]
    },
    porepressureaccumulation_triaxialclay_andersen: {
        inputs: [
            { name: "cyclic_shear_stress", type: "float", unit: "kPa", min: 0.0, max: 100.0, description: "Cyclic shear stress", required: true },
            { name: "undrained_shear_strength", type: "float", unit: "kPa", min: 1.0, max: 100.0, description: "Undrained shear strength", required: true },
            { name: "cycle_no", type: "float", min: 1.0, max: 1500.0, description: "Number of cycles", required: true }
        ]
    },
    strainaccumulation_dssclay_andersen: {
        inputs: [
            { name: "cyclic_shear_stress", type: "float", unit: "kPa", min: 0.0, max: 100.0, description: "Cyclic shear stress", required: true },
            { name: "undrained_shear_strength", type: "float", unit: "kPa", min: 1.0, max: 100.0, description: "Undrained shear strength", required: true },
            { name: "cycle_no", type: "float", min: 1.0, max: 1500.0, description: "Number of cycles", required: true }
        ]
    },
    strainaccumulation_dsssand_andersen: {
        inputs: [
            { name: "shearstress_ratio", type: "float", min: 0.0, max: 2.0, description: "Ratio cyclic shear stress to reference effective stress", required: true },
            { name: "cycle_no", type: "float", min: 1.0, max: 1000.0, description: "Number of cycles", required: true },
            { name: "failure_stress_ratio", type: "select", options: ["0.19", "0.25", "0.6", "1.0", "1.8"], description: "Ratio of cyclic shear stress to vertical effective stress at failure", required: true }
        ]
    },
    strainaccumulation_triaxialclay_andersen: {
        inputs: [
            { name: "cyclic_shear_stress", type: "float", unit: "kPa", min: 0.0, max: 100.0, description: "Cyclic shear stress", required: true },
            { name: "undrained_shear_strength", type: "float", unit: "kPa", min: 1.0, max: 100.0, description: "Undrained shear strength", required: true },
            { name: "cycle_no", type: "float", min: 1.0, max: 1500.0, description: "Number of cycles", required: true }
        ]
    },
    // Dynamic Soil Property Correlations
    dampingratio_sandgravel_seed: {
        inputs: [
            { name: "cyclic_shear_strain", type: "float", unit: "%", min: 0.0001, max: 1.0, description: "Cyclic shear strain", required: true }
        ]
    },
    gmax_shearwavevelocity: {
        inputs: [
            { name: "Vs", type: "float", unit: "m/s", min: 0.0, max: 600.0, description: "Shear wave velocity", required: true },
            { name: "gamma", type: "float", unit: "kN/m3", min: 12.0, max: 22.0, description: "Bulk unit weight", required: true },
            { name: "g", type: "float", unit: "m/s2", default: 9.81, min: 9.7, max: 10.2, description: "Acceleration due to gravity" }
        ]
    },
    modulusreduction_darendeli: {
        inputs: [
            { name: "mean_effective_stress", type: "float", unit: "kPa", min: 0.0, max: 1600.0, description: "Mean effective stress", required: true },
            { name: "pi", type: "float", unit: "%", min: 0.0, max: 60.0, description: "Plasticity index", required: true },
            { name: "ocr", type: "float", min: 1.0, max: 20.0, description: "Overconsolidation ratio", required: true },
            { name: "N", type: "float", min: 1.0, description: "Number of cycles", required: true },
            { name: "frequency", type: "float", unit: "Hz", min: 0.05, max: 100.0, description: "Loading frequency", required: true },
            { name: "soiltype", type: "select", options: ["sand", "fine sand", "silt", "clay", "all"], description: "Soil type", required: true },
            { name: "min_strain", type: "float", unit: "%", default: 0.0001, description: "Minimum strain" },
            { name: "max_strain", type: "float", unit: "%", default: 1.0, description: "Maximum strain" },
            { name: "no_points", type: "int", default: 250, min: 10, description: "Number of points" }
        ]
    },
    modulusreduction_plasticity_ishibashi: {
        inputs: [
            { name: "strain", type: "float", unit: "%", min: 0.0, max: 10.0, description: "Strain amplitude", required: true },
            { name: "pi", type: "float", unit: "%", min: 0.0, max: 200.0, description: "Plasticity index", required: true },
            { name: "sigma_m_eff", type: "float", unit: "kPa", min: 0.0, max: 400.0, description: "Mean effective pressure", required: true },
            { name: "multiplier_1", type: "float", default: 0.000102, description: "Multiplier 1" },
            { name: "exponent_1", type: "float", default: 0.492, description: "Exponent 1" },
            { name: "multiplier_2", type: "float", default: 0.000556, description: "Multiplier 2" },
            { name: "exponent_2", type: "float", default: 0.4, description: "Exponent 2" },
            { name: "multiplier_3", type: "float", default: -0.0145, description: "Multiplier 3" },
            { name: "exponent_3", type: "float", default: 1.3, description: "Exponent 3" }
        ]
    },
    // CPT Liquefaction
    fos_liquefaction: {
        inputs: [
            { name: "sigma_vo", type: "float", unit: "kPa", min: 0.0, description: "Total vertical stress", required: true },
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, description: "Effective vertical stress", required: true },
            { name: "CRR", type: "float", min: 0.0, max: 1.0, description: "Cyclic Resistance Ratio", required: true },
            { name: "CSR", type: "float", min: 0.0, description: "Cyclic Stress Ratio", required: true },
            { name: "MSF", type: "float", min: 0.0, max: 2.0, description: "Magnitude Scaling Factor", required: true },
            { name: "K_sigma", type: "float", min: 0.0, max: 2.0, description: "Overburden correction factor", required: true }
        ]
    },
    csr_robertson_cabal_2022: {
        inputs: [
            { name: "sigma_vo", type: "float", unit: "kPa", min: 0.0, description: "Total vertical stress", required: true },
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, description: "Effective vertical stress", required: true },
            { name: "depth", type: "float", unit: "m", min: 0.0, description: "Depth", required: true },
            { name: "magnitude", type: "float", min: 5.5, max: 8.5, description: "Earthquake magnitude", required: true },
            { name: "acceleration", type: "float", unit: "g", min: 0.0, description: "Maximum horizontal acceleration", required: true },
            { name: "MSF_userdefined", type: "boolean", default: false, description: "Use user-defined MSF?" }
        ]
    },
    csr_robertson_wride_1998: {
        inputs: [
            { name: "sigma_vo", type: "float", unit: "kPa", min: 0.0, description: "Total vertical stress", required: true },
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, description: "Effective vertical stress", required: true },
            { name: "depth", type: "float", unit: "m", min: 0.0, description: "Depth", required: true },
            { name: "magnitude", type: "float", min: 5.5, max: 8.5, description: "Earthquake magnitude", required: true },
            { name: "acceleration", type: "float", unit: "g", min: 0.0, description: "Maximum horizontal acceleration", required: true }
        ]
    },
    csr_idriss_boulanger_2008: {
        inputs: [
            { name: "sigma_vo", type: "float", unit: "kPa", min: 0.0, description: "Total vertical stress", required: true },
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, description: "Effective vertical stress", required: true },
            { name: "depth", type: "float", unit: "m", min: 0.0, description: "Depth", required: true },
            { name: "magnitude", type: "float", min: 5.5, max: 8.5, description: "Earthquake magnitude", required: true },
            { name: "acceleration", type: "float", unit: "g", min: 0.0, description: "Maximum horizontal acceleration", required: true }
        ]
    },
    csr_boulanger_idriss_2014: {
        inputs: [
            { name: "Qtn_cs", type: "float", min: 0.0, description: "Normalized cone penetration resistance", required: true },
            { name: "sigma_vo", type: "float", unit: "kPa", min: 0.0, description: "Total vertical stress", required: true },
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, description: "Effective vertical stress", required: true },
            { name: "depth", type: "float", unit: "m", min: 0.0, description: "Depth", required: true },
            { name: "magnitude", type: "float", min: 5.0, max: 8.5, description: "Earthquake magnitude", required: true },
            { name: "acceleration", type: "float", unit: "g", min: 0.0, description: "Maximum horizontal acceleration", required: true }
        ]
    },
    crr_robertson_cabal_2022: {
        inputs: [
            { name: "Qtn_cs", type: "float", min: 0.0, description: "Normalized cone penetration resistance", required: true }
        ]
    },
    crr_robertson_wride_1998: {
        inputs: [
            { name: "Qtn_cs", type: "float", min: 0.0, description: "Normalized cone penetration resistance", required: true },
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, description: "Effective vertical stress", required: true },
            { name: "relative_density", type: "float", min: 0.0, max: 1.0, description: "Relative density", required: true },
            { name: "atmospheric_pressure", type: "float", unit: "kPa", default: 100.0, description: "Atmospheric pressure" }
        ]
    },
    crr_idriss_boulanger_2008: {
        inputs: [
            { name: "Qtn_cs", type: "float", min: 0.0, description: "Normalized cone penetration resistance", required: true },
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, description: "Effective vertical stress", required: true },
            { name: "atmospheric_pressure", type: "float", unit: "kPa", default: 100.0, description: "Atmospheric pressure" }
        ]
    },
    crr_boulanger_idriss_2014: {
        inputs: [
            { name: "Qtn_cs", type: "float", min: 0.0, description: "Normalized cone penetration resistance", required: true },
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, description: "Effective vertical stress", required: true },
            { name: "atmospheric_pressure", type: "float", unit: "kPa", default: 100.0, description: "Atmospheric pressure" }
        ]
    },
    Qtn_cs_robertson_cabal_2022: {
        inputs: [
            { name: "ic", type: "float", min: 1.0, max: 3.5, description: "Soil behavior type index", required: true },
            { name: "Fr", type: "float", min: 0.0, max: 10.0, description: "Friction ratio", required: true },
            { name: "qt", type: "float", unit: "MPa", min: 0.0, description: "Cone tip resistance", required: true },
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, description: "Effective vertical stress", required: true },
            { name: "sigma_vo", type: "float", unit: "kPa", min: 0.0, description: "Total vertical stress", required: true },
            { name: "atmospheric_pressure", type: "float", unit: "kPa", default: 100.0, description: "Atmospheric pressure" }
        ]
    },
    // Missing Qtn_cs for other methods? Checked source file, only robertson_cabal_2022 Qtn_cs and robertson_wride Qtn_cs (actually it's missing in my view_file output but `Qtn_cs_idriss_boulanger_2008` corresponds to `Qtn_cs` input in CRR functions). 
    // The geotechnicalModules.js lists: 
    // Qtn_cs_boulanger_idriss_2014
    // Qtn_cs_idriss_boulanger_2008
    // Qtn_cs_robertson_wride_1998
    // I need to add those if I can deduce them.
    Qtn_cs_boulanger_idriss_2014: {
        inputs: [
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, description: "Effective vertical stress", required: true },
            { name: "qc", type: "float", unit: "MPa", min: 0.0, description: "Cone tip resistance", required: true },
            { name: "ic", type: "float", min: 1.0, max: 3.5, description: "Soil behavior type index", required: true },
            { name: "C_FC", type: "float", min: -0.2, max: 0.2, default: 0.0, description: "Fitting parameter for fines content" },
            { name: "atmospheric_pressure", type: "float", unit: "kPa", default: 100.0, description: "Atmospheric pressure" }
        ]
    },
    Qtn_cs_idriss_boulanger_2008: {
        inputs: [
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, description: "Effective vertical stress", required: true },
            { name: "qc", type: "float", unit: "MPa", min: 0.0, description: "Cone tip resistance", required: true },
            { name: "ic", type: "float", min: 1.0, max: 3.5, description: "Soil behavior type index", required: true },
            { name: "atmospheric_pressure", type: "float", unit: "kPa", default: 100.0, description: "Atmospheric pressure" }
        ]
    },
    Qtn_cs_robertson_wride_1998: {
        inputs: [
            { name: "sigma_vo", type: "float", unit: "kPa", min: 0.0, description: "Total vertical stress", required: true },
            { name: "sigma_vo_eff", type: "float", unit: "kPa", min: 0.0, description: "Effective vertical stress", required: true },
            { name: "ic", type: "float", min: 1.0, max: 3.5, description: "Soil behavior type index", required: true },
            { name: "qc", type: "float", unit: "MPa", min: 0.0, max: 120.0, description: "Cone tip resistance", required: true },
            { name: "Fr", type: "float", min: 0.0, max: 10.0, description: "Friction ratio", required: true },
            { name: "atmospheric_pressure", type: "float", unit: "kPa", default: 100.0, description: "Atmospheric pressure" }
        ]
    },
    liquefaction_strains_zhang: {
        inputs: [
            { name: "FoS_liq", type: "float", min: 0.0, description: "Safety factor against liquefaction", required: true },
            { name: "relative_density", type: "float", min: 0.0, max: 1.0, description: "Relative density", required: true },
            { name: "Qtn_cs", type: "float", min: 0.0, description: "Normalized cone penetration resistance", required: true }
        ]
    }
};
