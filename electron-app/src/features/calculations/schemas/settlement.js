/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

const settlementSchemas = {
    // --- Settlement Functions ---
    consolidationsettlement_mv: {
        title: "Consolidation Settlement (mv)",
        description: "Calculates consolidation settlement using modulus of volumetric compressibility (mv).",
        type: "object",
        properties: {
            initial_height: { type: "number", title: "Initial Layer Height (H0) [m]", minimum: 0, description: "Initial thickness of the layer" },
            effective_stress_increase: { type: "number", title: "Eff. Stress Increase [kPa]", minimum: 0, description: "Increase in vertical effective stress under the given load" },
            compressibility: { type: "number", title: "Compressibility (mv) [1/MPa]", minimum: 1e-4, maximum: 10, description: "Modulus of volumetric compressibility" }
        },
        required: ["initial_height", "effective_stress_increase", "compressibility"],
        documentation: `
            <h3>Consolidation Settlement (mv)</h3>
            <p>Calculates the consolidation settlement using the compressibility mv (inverse of constrained modulus M).</p>
        `
    },
    primaryconsolidationsettlement_nc: {
        title: "Primary Settlement - NC Clay",
        description: "Calculates primary consolidation settlement for normally consolidated clay.",
        type: "object",
        properties: {
            initial_height: { type: "number", title: "Initial Layer Height (H0) [m]", minimum: 0, description: "Initial thickness of the layer" },
            initial_voidratio: { type: "number", title: "Initial Void Ratio (e0)", minimum: 0.1, maximum: 5.0, description: "Initial void ratio of the layer" },
            initial_effective_stress: { type: "number", title: "Initial Eff. Stress [kPa]", minimum: 0, description: "Initial vertical effective stress in the center of the layer" },
            effective_stress_increase: { type: "number", title: "Eff. Stress Increase [kPa]", minimum: 0, description: "Increase in vertical effective stress under the given load" },
            compression_index: { type: "number", title: "Compression Index (Cc)", minimum: 0.1, maximum: 0.8, description: "Compression index derived from oedometer tests" },
            e_min: { type: "number", title: "Min Void Ratio", default: 0.3, description: "Minimum void ratio below which no further consolidation occurs" }
        },
        required: ["initial_height", "initial_voidratio", "initial_effective_stress", "effective_stress_increase", "compression_index"],
        documentation: `
            <h3>Primary Settlement - NC Clay</h3>
            <p>Calculates the primary consolidation settlement for normally consolidated fine grained soil.</p>
        `
    },
    primaryconsolidationsettlement_oc: {
        title: "Primary Settlement - OC Clay",
        description: "Calculates primary consolidation settlement for overconsolidated clay.",
        type: "object",
        properties: {
            initial_height: { type: "number", title: "Initial Layer Height (H0) [m]", minimum: 0, description: "Initial thickness of the layer" },
            initial_voidratio: { type: "number", title: "Initial Void Ratio (e0)", minimum: 0.1, maximum: 5.0, description: "Initial void ratio of the layer" },
            initial_effective_stress: { type: "number", title: "Initial Eff. Stress [kPa]", minimum: 0, description: "Initial vertical effective stress in the center of the layer" },
            preconsolidation_pressure: { type: "number", title: "Preconsolidation Pressure [kPa]", minimum: 0, description: "Preconsolidation pressure" },
            effective_stress_increase: { type: "number", title: "Eff. Stress Increase [kPa]", minimum: 0, description: "Increase in vertical effective stress under the given load" },
            compression_index: { type: "number", title: "Compression Index (Cc)", minimum: 0.1, maximum: 0.8, description: "Compression index" },
            recompression_index: { type: "number", title: "Recompression Index (Cr)", minimum: 0.015, maximum: 0.35, description: "Recompression index" },
            e_min: { type: "number", title: "Min Void Ratio", default: 0.3, description: "Minimum void ratio below which no further consolidation occurs" }
        },
        required: ["initial_height", "initial_voidratio", "initial_effective_stress", "preconsolidation_pressure", "effective_stress_increase", "compression_index", "recompression_index"],
        documentation: `
            <h3>Primary Settlement - OC Clay</h3>
            <p>Calculates the primary consolidation settlement for an overconsolidated clay.</p>
        `
    },

    // --- SettlementCalculation Class Wrapper ---
    settlement_calculation: {
        title: "Settlement Calculation (General)",
        description: "Calculates settlement using a Soil Profile and defined Foundation.",
        type: "object",
        properties: {
            soilprofile: { type: "object_select", title: "Soil Profile", objectType: "SoilProfile", description: "Soil Profile object containing layer data" },
            foundation_width: { type: "number", title: "Foundation Width [m]", minimum: 0, description: "Width of the foundation (diameter for circular)" },
            foundation_shape: {
                type: "string",
                title: "Foundation Shape",
                enum: ["strip", "circular", "rectangular"],
                default: "strip",
                description: "Shape of the foundation"
            },
            foundation_length: { type: "number", title: "Foundation Length [m]", default: 0, description: "Out-of-plane length (only required for rectangular)" },
            skirt_depth: { type: "number", title: "Skirt Depth [m]", default: 0, description: "Depth of skirts (load transfer to base)" },
            applied_stress: { type: "number", title: "Applied Stress [kPa]", minimum: 0, description: "Applied vertical stress" },
            water_level: { type: "number", title: "Water Level [m]", default: 0, description: "Depth of water table" }
        },
        required: ["soilprofile", "foundation_width", "applied_stress"],
        documentation: `
            <h3>Settlement Calculation (General)</h3>
            <p>Calculates shallow foundation settlement under a certain distributed load using a Soil Profile.</p>
        `
    }
};

export { settlementSchemas };
