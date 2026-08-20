/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

export const classificationSchemas = {
    bulkunitweight: {
        inputs: [
            { name: "saturation", type: "float", description: "Saturation (0.0 - 1.0)", required: true },
            { name: "voidratio", type: "float", description: "Void ratio (0.0 - 4.0)", required: true },
            { name: "specific_gravity", type: "float", default: 2.65, description: "Specific gravity" },
            { name: "unitweight_water", type: "float", default: 10.0, description: "Unit weight of water [kN/m3]" }
        ]
    },
    bulkunitweight_dryunitweight: {
        inputs: [
            { name: "dryunitweight", type: "float", description: "Dry unit weight [kN/m3]", required: true },
            { name: "watercontent", type: "float", description: "Water content", required: true },
            { name: "unitweight_water", type: "float", default: 10.0, description: "Unit weight of water [kN/m3]" }
        ]
    },
    density_unitweight: {
        inputs: [
            { name: "gamma", type: "float", description: "Unit weight [kN/m3]", required: true },
            { name: "g", type: "float", default: 9.81, description: "Gravity [m/s2]" }
        ]
    },
    dryunitweight_watercontent: {
        inputs: [
            { name: "watercontent", type: "float", description: "Water content", required: true },
            { name: "bulkunitweight", type: "float", description: "Bulk unit weight [kN/m3]", required: true }
        ]
    },
    porosity_voidratio: {
        inputs: [
            { name: "voidratio", type: "float", description: "Void ratio", required: true }
        ]
    },
    relative_density: {
        inputs: [
            { name: "void_ratio", type: "float", description: "Void ratio", required: true },
            { name: "e_min", type: "float", description: "Min void ratio", required: true },
            { name: "e_max", type: "float", description: "Max void ratio", required: true }
        ]
    },
    saturation_watercontent: {
        inputs: [
            { name: "water_content", type: "float", description: "Water content", required: true },
            { name: "voidratio", type: "float", description: "Void ratio", required: true },
            { name: "specific_gravity", type: "float", default: 2.65, description: "Specific gravity" }
        ]
    },
    unitweight_density: {
        inputs: [
            { name: "density", type: "float", description: "Density [kg/m3]", required: true },
            { name: "g", type: "float", default: 9.81, description: "Gravity [m/s2]" }
        ]
    },
    unitweight_watercontent_saturated: {
        inputs: [
            { name: "water_content", type: "float", description: "Water content", required: true },
            { name: "specific_gravity", type: "float", default: 2.65, description: "Specific gravity" },
            { name: "gamma_w", type: "float", default: 10.0, description: "Unit weight of water [kN/m3]" }
        ]
    },
    voidratio_bulkunitweight: {
        inputs: [
            { name: "bulkunitweight", type: "float", description: "Bulk unit weight [kN/m3]", required: true },
            { name: "saturation", type: "float", default: 1.0, description: "Saturation (0.0 - 1.0)" },
            { name: "specific_gravity", type: "float", default: 2.65, description: "Specific gravity" },
            { name: "unitweight_water", type: "float", default: 10.0, description: "Unit weight of water [kN/m3]" }
        ]
    },
    voidratio_drydensity: {
        inputs: [
            { name: "dry_density", type: "float", description: "Dry density [kg/m3]", required: true },
            { name: "specific_gravity", type: "float", default: 2.65, description: "Specific gravity" },
            { name: "water_density", type: "float", default: 1000.0, description: "Water density [kg/m3]" }
        ]
    },
    voidratio_porosity: {
        inputs: [
            { name: "porosity", type: "float", description: "Porosity", required: true }
        ]
    },
    voidratio_watercontent: {
        inputs: [
            { name: "water_content", type: "float", description: "Water content", required: true },
            { name: "saturation", type: "float", default: 1.0, description: "Saturation (0.0 - 1.0)" },
            { name: "specific_gravity", type: "float", default: 2.65, description: "Specific gravity" }
        ]
    },
    watercontent_voidratio: {
        inputs: [
            { name: "voidratio", type: "float", description: "Void ratio", required: true },
            { name: "saturation", type: "float", default: 1.0, description: "Saturation (0.0 - 1.0)" },
            { name: "specific_gravity", type: "float", default: 2.65, description: "Specific gravity" }
        ]
    },
    relativedensity_categories: {
        inputs: [
            { name: "relative_density", type: "float", description: "Relative density (0.0 - 1.0)", required: true }
        ]
    },
    samplequality_voidratio_lunne: {
        inputs: [
            { name: "voidratio", type: "float", description: "Initial void ratio", required: true },
            { name: "voidratio_change", type: "float", description: "Change in void ratio", required: true },
            { name: "ocr", type: "float", description: "Overconsolidation ratio", required: true }
        ]
    },
    su_categories: {
        inputs: [
            { name: "undrained_shear_strength", type: "float", description: "Undrained shear strength [kPa]", required: true },
            { name: "standard", type: "select", options: ["BS 5930:2015", "ASTM D-2488"], default: "BS 5930:2015", description: "Classification standard" }
        ]
    },
    uscs_categories: {
        inputs: [
            { name: "symbol", type: "string", description: "USCS symbol (e.g. SP, CL)", required: true }
        ]
    }
};
