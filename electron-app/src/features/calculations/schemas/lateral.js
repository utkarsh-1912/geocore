/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

export const lateralSchemas = {
    // --- Pile Group Effect (Reese & Van Impe) ---
    pilegroupeffect_reesevanimpe: {
        title: "Pile Group Effect (Reese & Van Impe)",
        description: "Calculates the efficiency of pile groups under lateral loading.",
        type: "object",
        properties: {
            pile_x: {
                type: "string",
                title: "Pile X-Coordinates [m]",
                description: "Comma-separated list of X-coordinates (e.g., 0, 1.5, 0, 1.5)",
                default: "0, 3, 0, 3"
            },
            pile_y: {
                type: "string",
                title: "Pile Y-Coordinates [m]",
                description: "Comma-separated list of Y-coordinates (e.g., 0, 0, 1.5, 1.5)",
                default: "0, 0, 3, 3"
            },
            pile_diameters: {
                type: "string",
                title: "Pile Diameters [m]",
                description: "Comma-separated list of diameters (e.g., 0.5, 0.5, 0.5, 0.5)",
                default: "1.0, 1.0, 1.0, 1.0"
            },
            load_x: {
                type: "number",
                title: "Load X-Component [kN]",
                default: 100,
                description: "X-component of the lateral load"
            },
            load_y: {
                type: "number",
                title: "Load Y-Component [kN]",
                default: 0,
                description: "Y-component of the lateral load"
            }
        },
        required: ["pile_x", "pile_y", "pile_diameters", "load_x", "load_y"],
        documentation: `
            <h3>Pile Group Effect (Reese & Van Impe)</h3>
            <p>Calculates the group efficiency factors for laterally loaded piles according to Reese & Van Impe.</p>
            <p>P-multipliers are calculated based on pile spacing and loading direction.</p>
        `
    },
    // --- Reinforced Circular Section Inertia ---
    reinforced_circularsection_inertia: {
        title: "Reinforced Circular Section Inertia",
        description: "Calculates the combined inertia of a reinforced concrete circular section.",
        type: "object",
        properties: {
            diameter: {
                type: "number",
                title: "Section Diameter [m]",
                minimum: 0,
                description: "Diameter of the concrete section"
            },
            modulus_ratio: {
                type: "number",
                title: "Modulus Ratio (E_steel / E_concrete)",
                default: 7, // Approx 210 GPa / 30 GPa
                minimum: 0,
                description: "Ratio of Young's modulus of steel to concrete"
            },
            n_bars: {
                type: "integer",
                title: "Number of Rebar Rods",
                default: 8,
                minimum: 1,
                description: "Number of reinforcing bars"
            },
            offset: {
                type: "number",
                title: "Rebar Offset Radius [m]",
                minimum: 0,
                description: "Distance from center to rebar ring"
            },
            rebar_diameter: {
                type: "number",
                title: "Rebar Diameter [m]",
                minimum: 0,
                description: "Diameter of individual rebar rods"
            },
            maximum_resistance: {
                type: "boolean",
                title: "Optimize for Max Resistance?",
                default: true,
                description: "Orient bars for maximum bending resistance"
            }
        },
        required: ["diameter", "modulus_ratio", "n_bars", "offset", "rebar_diameter"],
        documentation: `
            <h3>Reinforced Circular Section Inertia</h3>
            <p>Calculates the moment of inertia for a circular concrete section with steel reinforcement.</p>
            <p>Uses Steiner's theorem to combine the stiffness of concrete and steel.</p>
        `
    }
};
