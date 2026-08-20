/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

export const pipelineSchemas = {
    contactwidth: {
        inputs: [
            { name: "diameter", type: "float", unit: "m", description: "Pipeline or cable diameter", required: true },
            { name: "penetration", type: "float", unit: "m", description: "Pipeline or cable penetration", required: true }
        ]
    },
    embedment_drained: {
        inputs: [
            { name: "penetration", type: "float", unit: "m", description: "Penetration depth", required: true },
            { name: "gamma_eff", type: "float", unit: "kN/m3", description: "Submerged unit weight", required: true },
            { name: "phi_eff", type: "float", unit: "deg", description: "Effective friction angle", required: true },
            { name: "diameter", type: "float", unit: "m", description: "Pipeline diameter", required: true },
            { name: "roughness_factor", type: "float", default: 0.67, description: "Roughness (0=smooth, 1=rough)" },
            { name: "Ngamma_theory", type: "string", default: "Vesic", description: "Theory (Vesic, Meyerhof, DavisBooker)" }
        ]
    },
    embedment_undrained_method1: {
        inputs: [
            { name: "diameter", type: "float", unit: "m", description: "Pipeline diameter", required: true },
            { name: "undrained_shear_strength", type: "float", unit: "kPa", description: "Su at seabed", required: true },
            { name: "k_su", type: "float", unit: "kPa/m", description: "Rate of Su increase", required: true },
            { name: "gamma_eff", type: "float", unit: "kN/m3", description: "Submerged unit weight", required: true },
            { name: "penetration", type: "float", unit: "m", description: "Penetration depth", required: true },
            { name: "Nc", type: "float", default: 5.14, description: "Bearing capacity factor" },
            { name: "roughness", type: "float", default: 0.67, description: "Roughness factor" }
        ]
    },
    embedment_undrained_method2: {
        inputs: [
            { name: "diameter", type: "float", unit: "m", description: "Pipeline diameter", required: true },
            { name: "penetration", type: "float", unit: "m", description: "Penetration depth", required: true },
            { name: "undrained_shear_strength", type: "float", unit: "kPa", description: "Su at pipe invert", required: true },
            { name: "gamma_eff", type: "float", unit: "kN/m3", description: "Submerged unit weight", required: true }
        ]
    },
    lay_touchdown_factor: {
        inputs: [
            { name: "penetration", type: "float", unit: "m", description: "Static penetration", required: true },
            { name: "submerged_weight", type: "float", unit: "kN/m", description: "Submerged weight", required: true },
            { name: "seabed_stiffness", type: "float", unit: "kN/m/m", description: "Seabed stiffness", required: true },
            { name: "lay_tension", type: "float", unit: "kN", description: "Lay tension", required: true },
            { name: "bending_stiffness", type: "float", unit: "kNm2", description: "Bending stiffness", required: true }
        ]
    },
    penetratedarea: {
        inputs: [
            { name: "diameter", type: "float", unit: "m", description: "Pipeline diameter", required: true },
            { name: "penetration", type: "float", unit: "m", description: "Penetration depth", required: true }
        ],
        documentation: `
            <h3>Penetrated Area Calculation</h3>
            <p>Calculates the cross-sectional area of a pipe that has penetrated into the seabed.</p>
            <p><b>Inputs:</b></p>
            <ul>
                <li><b>Diameter (D):</b> Outer diameter of the pipeline [m]</li>
                <li><b>Penetration (z):</b> Depth of penetration from the seabed surface to the pipe invert [m]</li>
            </ul>
            <p><b>Output:</b></p>
            <ul>
                <li><b>Area:</b> The cross-sectional area of the submerged portion of the pipe [m²]</li>
            </ul>
        `
    }
};
