/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

export const plottingSchemas = {
    LogPlot: {
        inputs: [
            { name: "soilprofile", type: "object_select", objectType: "SoilProfile", description: "SoilProfile to plot", required: true },
            { name: "parameters", type: "string", description: "Parameters to plot (comma separated, e.g. 'qc [MPa]')" },
            { name: "soiltypecolumn", type: "string", description: "Column name for soil type (optional, auto-detected if empty)" }
        ]
    },
    LogPlotMatplotlib: {
        inputs: [
            { name: "soilprofile", type: "object_select", objectType: "SoilProfile", description: "SoilProfile to plot", required: true },
            { name: "parameters", type: "string", description: "Parameters to plot (comma separated)" },
            { name: "soiltypecolumn", type: "string", description: "Column name for soil type (optional)" }
        ]
    },
    plot_with_log: {
        inputs: [
            { name: "soilprofile", type: "object_select", objectType: "SoilProfile", description: "SoilProfile to plot", required: true },
            { name: "parameters", type: "string", description: "Parameters to plot (comma separated, e.g. 'qc [MPa]')" },
            { name: "soiltypecolumn", type: "string", description: "Column name for soil type (optional)" }
        ]
    }
};
