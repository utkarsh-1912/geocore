/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

export const consolidationSchemas = {
    // Groundwater flow
    hydraulicconductivity_unconfinedaquifer: {
        inputs: [
            { name: "radius_1", type: "float", unit: "m", min: 0.0, description: "Radial distance to first standpipe", required: true },
            { name: "radius_2", type: "float", unit: "m", min: 0.0, description: "Radial distance to second standpipe", required: true },
            { name: "piezometric_height_1", type: "float", unit: "m", min: 0.0, description: "Piezometric height in first standpipe", required: true },
            { name: "piezometric_height_2", type: "float", unit: "m", min: 0.0, description: "Piezometric height in second standpipe", required: true },
            { name: "flowrate", type: "float", unit: "m3/s", min: 0.0, description: "Flowrate extracted from pumping well", required: true }
        ]
    },
    // Pore pressure dissipation analysis
    consolidation_degree: {
        inputs: [
            { name: "time", type: "float", unit: "s", min: 0.0, description: "Time at which excess pore pressures are computed", required: true },
            { name: "cv", type: "float", unit: "m2/s", min: 0.0, description: "Coefficient of consolidation", required: true },
            { name: "drainage_length", type: "float", unit: "m", min: 0.0, description: "Drainage length", required: true },
            { name: "distribution", type: "select", options: ["uniform", "triangular"], default: "uniform", description: "Shape of initial excess pore pressure distribution" }
        ]
    },
    pore_pressure_fourier: {
        inputs: [
            { name: "delta_u_0", type: "float", unit: "kPa", description: "Initial excess pore pressure", required: true },
            { name: "depths", type: "float", is_array: true, unit: "m", description: "Depths for excess pore pressures (comma separated)", required: true },
            { name: "time", type: "float", unit: "s", min: 0.0, description: "Time at which excess pore pressures are computed", required: true },
            { name: "cv", type: "float", unit: "m2/s", min: 0.0, description: "Coefficient of consolidation", required: true },
            { name: "layer_thickness", type: "float", unit: "m", min: 0.0, description: "Thickness of the layer", required: true },
            { name: "no_terms", type: "int", default: 1000, min: 1, description: "Number of terms for Fourier series" }
        ]
    },
    // Wrapper for ConsolidationCalculation class
    consolidation_calculation: {
        inputs: [
            { name: "height", type: "float", unit: "m", min: 0.0, description: "Height of the layer", required: true },
            { name: "total_time", type: "float", unit: "s", min: 0.0, description: "Total time for calculation", required: true },
            { name: "no_nodes", type: "int", default: 50, min: 2, description: "Number of nodes for discretization", required: true },
            { name: "cv", type: "float", unit: "m2/yr", min: 0.0, description: "Coefficient of consolidation", required: true }, // Input in m2/yr per docstring, wrapper handles conversion? No, doc says 'cv is specified in m2/yr and is converted to m2/s inside the routine'
            { name: "u0", type: "float", unit: "kPa", description: "Initial excess pore pressure (scalar or array)", required: true }, // Simplified to scalar for now or handle array string
            { name: "freedrainage_top", type: "boolean", default: true, description: "Free drainage at top?" },
            { name: "freedrainage_bottom", type: "boolean", default: true, description: "Free drainage at bottom?" }
        ]
    }
};
