/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import { SOIL_PROFILE_DOCS, CALCULATION_GRID_DOCS } from '../documentation';

export const generalSchemas = {
    SoilProfile: {
        documentation: SOIL_PROFILE_DOCS,
        inputs: [
            { name: "data", type: "file", description: "Upload CSV/Excel file with soil data", required: true, accept: ".csv,.xlsx,.xls" },
            { name: "depth_from_col", type: "column_select", default: "Depth from [m]", description: "Column name for top depth", required: true },
            { name: "depth_to_col", type: "column_select", default: "Depth to [m]", description: "Column name for bottom depth", required: true },
            { name: "nan_strategy", type: "string", default: "fill", description: "Strategy for NaN values" }
        ]
    },
    CalculationGrid: {
        documentation: CALCULATION_GRID_DOCS,
        inputs: [
            { name: "soilprofile", type: "object_select", objectType: "SoilProfile", description: "SoilProfile object", required: true },
            { name: "dz", type: "float", unit: "m", default: 0.5, description: "Grid step size", required: true },
            { name: "include_layertransitions", type: "boolean", default: true, description: "Include nodes at layer transitions" }
        ]
    }
};
