/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import { SOIL_PROFILE_DOCS, CALCULATION_GRID_DOCS } from '../documentation';
import { DATA_KIND_OPTIONS } from '../../../utils/dataKind';

export const generalSchemas = {
    SoilProfile: {
        documentation: SOIL_PROFILE_DOCS,
        inputs: [
            { name: "data", type: "file", description: "Upload CSV/Excel file with soil data", required: true, accept: ".csv,.xlsx,.xls" },
            { name: "data_kind", label: "File contains", type: "select", options: DATA_KIND_OPTIONS, default: "soil_profile", description: "CPT sounding or layered soil profile (suggested from the file's columns). GeoAI reads CPT soundings with its CPT tools and layered profiles as the project stratigraphy.", required: true },
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
