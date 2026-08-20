/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

export const insituTestsSchemas = {
    // PCPT Functions
    behaviourindex_pcpt_nonnormalised: {
        inputs: [
            { name: "qc", type: "float", description: "Cone resistance [MPa]", required: true },
            { name: "Rf", type: "float", description: "Friction ratio [%]", required: true },
            { name: "atmospheric_pressure", type: "float", description: "Atmospheric pressure [kPa]", default: 100.0 }
        ]
    },
    behaviourindex_pcpt_robertsonwride: {
        inputs: [
            { name: "Qtn", type: "float", description: "Normalised cone resistance", required: true },
            { name: "Fr", type: "float", description: "Normalised friction ratio [%]", required: true }
        ]
    },
    constrainedmodulus_pcpt_robertson: {
        inputs: [
            { name: "qt", type: "float", description: "Corrected cone resistance [MPa]", required: true },
            { name: "sigma_vo", type: "float", description: "Total vertical stress [kPa]", required: true },
            { name: "Ic", type: "float", description: "Soil behaviour type index", required: true }
        ]
    },
    frictionangle_sand_kulhawymayne: {
        inputs: [
            { name: "qt", type: "float", description: "Corrected cone resistance [MPa]", required: true },
            { name: "sigma_vo_eff", type: "float", description: "Effective vertical stress [kPa]", required: true },
            { name: "pa", type: "float", default: 100.0, description: "Atmospheric pressure [kPa]" }
        ]
    },
    ic_soilclass_robertson: {
        inputs: [
            { name: "Ic", type: "float", description: "Soil behaviour type index", required: true }
        ]
    },
    undrainedshearstrength_clay_radlunne: {
        inputs: [
            { name: "qt", type: "float", description: "Corrected cone resistance [MPa]", required: true },
            { name: "sigma_vo", type: "float", description: "Total vertical stress [kPa]", required: true },
            { name: "Nkt", type: "float", default: 15.0, description: "Cone factor (default 15)" }
        ]
    },
    unitweight_mayne: {
        inputs: [
            { name: "fs", type: "float", description: "Sleeve friction [MPa]", required: true },
            { name: "sigma_vo_eff", type: "float", description: "Effective vertical stress [kPa]", required: true },
            { name: "pa", type: "float", default: 100.0, description: "Atmospheric pressure [kPa]" }
        ]
    },
    // SPT Functions
    frictionangle_spt_kulhawymayne: {
        inputs: [
            { name: "N1_60", type: "float", description: "Corrected SPT N-value", required: true },
            { name: "sigma_vo_eff", type: "float", description: "Effective vertical stress [kPa]", required: true },
            { name: "pa", type: "float", default: 100.0, description: "Atmospheric pressure [kPa]" }
        ]
    },
    overburdencorrection_spt_liaowhitman: {
        inputs: [
            { name: "sigma_vo_eff", type: "float", description: "Effective vertical stress [kPa]", required: true },
            { name: "pa", type: "float", default: 100.0, description: "Atmospheric pressure [kPa]" }
        ]
    },
    spt_N60_correction: {
        inputs: [
            { name: "N_measured", type: "float", description: "Measured SPT blow count", required: true },
            { name: "energy_ratio", type: "float", default: 0.6, description: "Energy ratio (default 0.6)" },
            { name: "borehole_diameter_factor", type: "float", default: 1.0 },
            { name: "sampler_factor", type: "float", default: 1.0 },
            { name: "rod_length_factor", type: "float", default: 1.0 }
        ]
    }
};
