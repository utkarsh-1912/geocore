/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

export const labTestingSchemas = {
    undercompaction_cohesionless_ladd: {
        inputs: [
            { name: "sample_height", type: "float", description: "Sample height [m]", required: true },
            { name: "no_layers", type: "integer", description: "Number of layers", required: true },
            { name: "undercompaction_deepest", type: "float", description: "Undercompaction of deepest layer [%]", required: true },
            { name: "undercompaction_shallowest", type: "float", description: "Undercompaction of shallowest layer [%]", default: 0.0 }
        ]
    },
    logtimemethod: {
        inputs: [
            { name: "times", type: "list", description: "Time [s]", required: true },
            { name: "settlements", type: "list", description: "Settlement [mm]", required: true },
            { name: "drainagelength", type: "float", description: "Drainage length [m]", required: true }
        ]
    },
    roottimemethod: {
        inputs: [
            { name: "times", type: "list", description: "Time [s]", required: true },
            { name: "settlements", type: "list", description: "Settlement [mm]", required: true },
            { name: "drainagelength", type: "float", description: "Drainage length [m]", required: true }
        ]
    },
    PlasticityChart: {
        inputs: [
            { name: "ll", type: "list", description: "Liquid Limit [%]", required: true },
            { name: "pi", type: "list", description: "Plasticity Index [%]", required: true },
            { name: "name", type: "string", description: "Trace Name", default: "Sample" },
            { name: "plot_title", type: "string", description: "Plot Title", default: "Plasticity Chart" }
        ]
    },
    PSDChart: {
        inputs: [
            { name: "grainsize", type: "list", description: "Grain Size [mm]", required: true },
            { name: "pctpassing", type: "list", description: "Percent Passing [%]", required: true },
            { name: "name", type: "string", description: "Trace Name", default: "Sample" },
            { name: "plot_title", type: "string", description: "Plot Title", default: "PSD Chart" }
        ]
    }
};
