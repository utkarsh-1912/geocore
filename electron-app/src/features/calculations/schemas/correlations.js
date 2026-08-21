/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

export const correlationsSchemas = {
    // All soil types
    acousticimpedance_bulkunitweight_chen: {
        inputs: [
            { name: "vp", type: "float", description: "P-wave velocity [m/s]", required: true }
        ]
    },
    k0_frictionangle_mesri: {
        inputs: [
            { name: "phi_cs", type: "float", description: "Friction angle [deg]", required: true }
        ]
    },
    shearwavevelocity_compressionindex_cha: {
        inputs: [
            { name: "vs", type: "float", description: "Shear wave velocity [m/s]", required: true }
        ]
    },
    // Cohesive soils
    compressionindex_watercontent_koppula: {
        inputs: [
            { name: "water_content", type: "float", description: "Water content [%]", required: true },
            { name: "cc_cr_ratio", type: "float", default: 7.5, description: "Ratio of Cc/Cr" }
        ]
    },
    cv_liquidlimit_usnavy: {
        inputs: [
            { name: "liquid_limit", type: "float", description: "Liquid limit [%]", required: true },
            { name: "trend", type: "select", options: ["Remoulded", "NC", "OC"], default: "NC" }
        ]
    },
    frictionangle_plasticityindex: {
        inputs: [
            { name: "plasticity_index", type: "float", description: "Plasticity index [%]", required: true }
        ]
    },
    gmax_plasticityocr_andersen: {
        inputs: [
            { name: "pi", type: "float", description: "Plasticity index [%]", required: true },
            { name: "ocr", type: "float", description: "Overconsolidation ratio", required: true },
            { name: "sigma_vo_eff", type: "float", description: "Vertical effective stress [kPa]", required: true }
        ]
    },
    icl_scl_burland: {
        inputs: [
            { name: "voidratio_liquidlimit", type: "float", description: "Void ratio at liquid limit", required: true }
        ]
    },
    k0_plasticity_kenney: {
        inputs: [
            { name: "pi", type: "float", description: "Plasticity index [%]", required: true },
            { name: "ocr", type: "float", default: 1.0, description: "Overconsolidation ratio" }
        ]
    },
    // Cohesionless soils
    gmax_sand_hardinblack: {
        inputs: [
            { name: "void_ratio", type: "float", description: "Void ratio", required: true },
            { name: "sigma_m0", type: "float", description: "Mean effective stress [kPa]", required: true }
        ]
    },
    hssmall_parameters_sand: {
        inputs: [
            { name: "relative_density", type: "float", description: "Relative density [%] (10 - 100)", required: true }
        ]
    },
    permeability_d10_hazen: {
        inputs: [
            { name: "grain_size", type: "float", description: "d10 particle size [mm]", required: true }
        ]
    },
    stress_dilatancy_bolton: {
        inputs: [
            { name: "relative_density", type: "float", description: "Relative density (0.0 - 1.0)", required: true },
            { name: "p_eff", type: "float", description: "Mean effective stress [kPa]", required: true },
            { name: "Q", type: "float", default: 10.0, description: "Q constant (default 10 for silica sand)" }
        ]
    }
};
