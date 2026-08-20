/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

export const constitutiveSchemas = {
    hardening_soil_drained_triaxial: {
        inputs: [
            // Material Parameters (__init__)
            { name: "friction_angle", type: "float", unit: "deg", description: "Friction angle", required: true },
            { name: "cohesion", type: "float", unit: "kPa", description: "Cohesion", required: true },
            { name: "Rf", type: "float", default: 0.9, description: "Failure ratio (default 0.9)", required: true },

            // Stiffness Parameters (set_reference_moduli)
            { name: "E50_ref", type: "float", unit: "kPa", description: "Secant stiffness at 50% strength", required: true },
            { name: "Eur_ref", type: "float", unit: "kPa", description: "Unloading/reloading stiffness", required: true },
            { name: "Eoed_ref", type: "float", unit: "kPa", description: "Oedometric stiffness", required: true },
            { name: "p_ref", type: "float", unit: "kPa", default: 100, description: "Reference pressure", required: true },

            // Test Parameters (calculate_drainedtriaxial)
            { name: "sigma3", type: "float", unit: "kPa", description: "Confining pressure (sigma3)", required: true },
            { name: "sigma1_0", type: "float", unit: "kPa", description: "Initial vertical stress", required: true },
            { name: "m", type: "float", description: "Stress dependence power (m)", required: true },
            { name: "N", type: "int", default: 100, description: "Number of steps" }
        ],
        documentation: `
            <h3>Hardening Soil Model - Drained Triaxial Test</h3>
            <p>Simulates a drained triaxial test using the Hardening Soil model.</p>
            
            <h4>Parameters</h4>
            <h5>Strength</h5>
            <ul>
                <li><b>Friction Angle (phi):</b> Internal friction angle [deg]</li>
                <li><b>Cohesion (c):</b> Cohesion intercept [kPa]</li>
                <li><b>Rf:</b> Failure ratio (q_f / q_a), typically 0.9.</li>
            </ul>

            <h5>Stiffness (at p_ref)</h5>
            <ul>
                <li><b>E50_ref:</b> Secant stiffness in standard drained triaxial test [kPa]</li>
                <li><b>Eur_ref:</b> Unloading-reloading stiffness [kPa]</li>
                <li><b>Eoed_ref:</b> Tangent stiffness for primary oedometric loading [kPa]</li>
                <li><b>p_ref:</b> Reference stress for stiffnesss [kPa]</li>
            </ul>

            <h5>Test Conditions</h5>
            <ul>
                <li><b>sigma3:</b> Constant confining pressure [kPa]</li>
                <li><b>sigma1_0:</b> Initial vertical stress [kPa]</li>
                <li><b>m:</b> Power for stress-level dependency of stiffness (0.5 - 1.0)</li>
            </ul>
        `
    }
};
