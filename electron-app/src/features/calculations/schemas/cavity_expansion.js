/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

export const cavityExpansionSchemas = {
    // --- Cylinder Expansion (Tresca) ---
    expansion_cylinder_tresca: {
        title: "Cylinder Expansion (Tresca)",
        description: "Calculates cavity expansion for a cylinder in Tresca material.",
        type: "object",
        properties: {
            insitu_pressure: {
                type: "number",
                title: "In-situ Pressure [kPa]",
                minimum: 0,
                description: "Isotropic horizontal stress before excavation"
            },
            borehole_pressure: {
                type: "number",
                title: "Borehole Pressure [kPa]",
                minimum: 0,
                description: "Pressure on the borehole wall"
            },
            diameter: {
                type: "number",
                title: "Borehole Diameter [m]",
                minimum: 0,
                description: "Initial borehole diameter"
            },
            undrained_shear_strength: {
                type: "number",
                title: "Undrained Shear Strength [kPa]",
                minimum: 0,
                description: "Shear strength of surrounding material"
            },
            shear_modulus: {
                type: "number",
                title: "Shear Modulus [kPa]",
                minimum: 0,
                description: "Shear modulus of surrounding material"
            },
            poissons_ratio: {
                type: "number",
                title: "Poisson's Ratio",
                default: 0.5,
                minimum: 0,
                maximum: 0.5,
                description: "Poisson's ratio (default 0.5 for undrained)"
            },
            max_radius_multiplier: {
                type: "number",
                title: "Max Radius Multiplier",
                default: 10.0,
                minimum: 1.0,
                description: "Multiplier on borehole radius for calculation extent"
            },
            number_radii: {
                type: "integer",
                title: "Number of Radii",
                default: 250,
                minimum: 10,
                description: "Number of calculation points"
            }
        },
        required: ["insitu_pressure", "borehole_pressure", "diameter", "undrained_shear_strength", "shear_modulus"],
        documentation: `
            <h3>Cylinder Expansion (Tresca)</h3>
            <p>Calculates stresses and displacements around a cylindrical cavity in a Tresca material.</p>
            <p>Useful for analyzing borehole stability and pressuremeter tests.</p>
        `
    },

    // --- Thick Sphere Expansion (Tresca) ---
    expansion_tresca_thicksphere: {
        title: "Thick Sphere Expansion (Tresca)",
        description: "Calculates stresses for cavity expansion around a thick-walled sphere (Tresca).",
        type: "object",
        properties: {
            undrained_shear_strength: {
                type: "number",
                title: "Undrained Shear Strength [kPa]",
                minimum: 0,
                description: "Shear strength of surrounding material"
            },
            internal_radius: {
                type: "number",
                title: "Internal Radius [m]",
                minimum: 0,
                description: "Initial internal radius of the sphere"
            },
            external_radius: {
                type: "number",
                title: "External Radius [m]",
                minimum: 0,
                description: "Initial external radius of the region"
            },
            internal_pressure: {
                type: "number",
                title: "Internal Pressure [kPa]",
                minimum: 0,
                description: "Pressure applied inside the sphere"
            },
            external_pressure: {
                type: "number",
                title: "External Pressure [kPa]",
                minimum: 0,
                description: "Pressure applied outside the sphere"
            },
            youngs_modulus: {
                type: "number",
                title: "Young's Modulus [kPa]",
                minimum: 0,
                description: "Elastic modulus of the material"
            },
            poissons_ratio: {
                type: "number",
                title: "Poisson's Ratio",
                default: 0.5,
                minimum: 0,
                maximum: 0.5,
                description: "Poisson's ratio"
            },
            seed: {
                type: "integer",
                title: "Calculation Points (Seed)",
                default: 100,
                minimum: 10,
                description: "Number of radii for calculation"
            }
        },
        required: ["undrained_shear_strength", "internal_radius", "external_radius", "internal_pressure", "external_pressure", "youngs_modulus"],
        documentation: `
            <h3>Thick Sphere Expansion (Tresca)</h3>
            <p>Elastic-plastic analysis of a thick-walled spherical cavity.</p>
            <p>Determines the plastic radius and stress distribution.</p>
        `
    },

    // --- Elastic Cylinder Stress (Isotropic) ---
    stress_cylinder_elastic_isotropic: {
        title: "Elastic Cylinder Stress (Isotropic)",
        description: "Calculates radial and tangential stress around a borehole (Elastic).",
        type: "object",
        properties: {
            radius: {
                type: "string",
                title: "Radii to Calculate [m]",
                description: "Comma-separated list of radii (e.g., 0.5, 1.0, 1.5) or single value",
                default: "0.5, 0.6, 0.7, 0.8, 0.9, 1.0"
            },
            internal_pressure: {
                type: "number",
                title: "Internal Pressure [kPa]",
                minimum: 0,
                description: "Pressure on the borehole wall"
            },
            farfield_pressure: {
                type: "number",
                title: "Far-field Pressure [kPa]",
                minimum: 0,
                description: "In-situ horizontal stress"
            },
            borehole_radius: {
                type: "number",
                title: "Borehole Radius [m]",
                minimum: 0,
                description: "Radius of the borehole"
            },
            shear_modulus: {
                type: "number",
                title: "Shear Modulus [kPa] (Optional)",
                description: "Required for displacement calculation",
                default: null
            }
        },
        required: ["radius", "internal_pressure", "farfield_pressure", "borehole_radius"],
        documentation: `
            <h3>Elastic Cylinder Stress (Isotropic)</h3>
            <p>Calculates elastic stress distribution around a borehole.</p>
        `
    }
};
