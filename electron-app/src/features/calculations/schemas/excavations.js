/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

export const excavationsSchemas = {
    // Earth pressure coefficients
    earthpressurecoefficients_frictionangle: {
        inputs: [
            { name: "phi_eff", type: "float", unit: "deg", min: 20.0, max: 50.0, description: "Effective friction of the soil", required: true }
        ]
    },
    earthpressurecoefficients_poncelet: {
        inputs: [
            { name: "phi_eff", type: "float", unit: "deg", min: 20.0, max: 50.0, description: "Effective friction angle of the soil", required: true },
            { name: "interface_friction_angle", type: "float", unit: "deg", min: 15.0, max: 40.0, description: "Interface friction angle of the wall-soil interaction", required: true },
            { name: "wall_angle", type: "float", unit: "deg", min: 0.0, max: 70.0, description: "Angle to the vertical of the portion of the wall in contact with the soil", required: true },
            { name: "top_angle", type: "float", unit: "deg", min: 0.0, max: 70.0, description: "Angle to the horizontal of the slope on top of the wall", required: true }
        ]
    },
    earthpressurecoefficients_rankine: {
        inputs: [
            { name: "phi_eff", type: "float", unit: "deg", min: 20.0, max: 50.0, description: "Effective friction angle of the soil", required: true },
            { name: "wall_angle", type: "float", unit: "deg", min: 0.0, max: 70.0, description: "Angle to the vertical of the portion of the wall in contact with the soil", required: true },
            { name: "top_angle", type: "float", unit: "deg", min: 0.0, max: 70.0, description: "Angle to the horizontal of the slope on top of the wall", required: true }
        ]
    },
    // Soilmix
    bendingstiffness_soilmix_method1: {
        inputs: [
            { name: "moment_inertia_reinforcement", type: "float", unit: "m4", min: 0.0, description: "Moment of inertia of the reinforcement", required: true },
            { name: "modulus_soilmix", type: "float", unit: "kPa", min: 0.0, description: "Youngs modulus of the soilmix", required: true },
            { name: "height_soilmix", type: "float", unit: "m", min: 0.0, description: "Height of the soilmix material", required: true },
            { name: "reinforcement_offset", type: "float", unit: "m", min: 0.0, description: "Offset of reinforcement elements (center to center)", required: true },
            { name: "height_reinforcement", type: "float", unit: "m", min: 0.0, description: "Longest dimension of the reinforcement", required: true },
            { name: "flange_thickness", type: "float", unit: "m", min: 0.0, description: "Thickness of the flanges", required: true },
            { name: "connection_thickness", type: "float", unit: "m", min: 0.0, description: "Thickness of the connection between the flanges", required: true },
            { name: "flange_width", type: "float", unit: "m", min: 0.0, description: "Width of the flanges", required: true },
            { name: "modulus_reinforcement", type: "float", unit: "kPa", default: 210000000.0, min: 0.0, max: 300000000.0, description: "Youngs modulus of the reinforcement" },
            { name: "participating_width", type: "float", unit: "m", min: 0.0, description: "Participating width for bending (optional)" },
            { name: "tensile_strength_soilmix", type: "float", unit: "kPa", min: 0.0, description: "Tensile strength of soilmix (optional)" }
        ]
    },
    bendingstiffness_soilmix_method2: {
        inputs: [
            { name: "bendingstiffness_reinforcement", type: "float", unit: "m4", min: 0.0, description: "Bending stiffness of the reinforcement", required: true },
            { name: "modulus_soilmix", type: "float", unit: "kPa", min: 0.0, description: "Youngs modulus of the soilmix material", required: true },
            { name: "height_soilmix", type: "float", unit: "m", min: 0.0, description: "Height of the soilmix material", required: true },
            { name: "reinforcement_offset", type: "float", unit: "m", min: 0.0, description: "Center-to-center offset of reinforcement elements", required: true },
            { name: "participating_width", type: "float", unit: "m", min: 0.0, description: "Participating width for bending (optional)" }
        ]
    }
};
