/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

export const eurocodeSchemas = {
    parameter_selection_constant_value: {
        inputs: [
            { name: "data", type: "list", description: "List of measurements (e.g. [10, 12, 11])", required: true },
            { name: "mode", type: "select", options: ["Low", "Mean"], default: "Low", description: "Mode: 'Low' (5% fractile) or 'Mean' (95% confidence)" },
            { name: "cov", min: 0, type: "float", description: "Coefficient of variation (CoV). Leave blank if unknown." },
            { name: "confidence", min: 0, max: 1, minExclusive: true, maxExclusive: true, type: "float", default: 0.95, description: "Confidence level (default 0.95)" }
        ],
        documentation: `
            <h3>Eurocode 7 - Parameter Selection (Constant Value)</h3>
            <p>Selects characteristic values from measurements assuming a constant value profile.</p>
            <ul>
                <li><b>Low:</b> 5% fractile (conservative estimate).</li>
                <li><b>Mean:</b> 95% confidence mean value.</li>
            </ul>
        `
    },
    parameter_selection_linear_trend: {
        inputs: [
            { name: "data", type: "list", description: "Measurements", required: true },
            { name: "depths", type: "list", description: "Depths corresponding to measurements", required: true },
            { name: "requested_depths", type: "list", description: "Depths to calculate characteristic values at", required: true },
            { name: "mode", type: "select", options: ["Low", "Mean"], default: "Low", description: "'Low' or 'Mean'" },
            { name: "confidence", min: 0, max: 1, minExclusive: true, maxExclusive: true, type: "float", default: 0.95, description: "Confidence level" }
        ],
        documentation: `
            <h3>Eurocode 7 - Parameter Selection (Linear Trend)</h3>
            <p>Selects characteristic values assuming a linear trend with depth.</p>
        `
    },
    eurocode7_factors: {
        inputs: [
            { name: "design_approach", type: "select", options: ["DA1-1", "DA1-2", "DA2", "DA3-1", "DA3-2"], default: "DA1-1", description: "Design Approach" },
            { name: "foundation_type", type: "select", options: ["Spread foundation", "Driven pile", "Bored pile", "CFA pile", "Prestressed anchorage", "Retaining structure", "Slopes"], default: "Spread foundation", description: "Foundation type (selects the resistance factors)" }
        ],
        documentation: `
            <h3>Eurocode 7 Partial Factors</h3>
            <p>Returns the partial factors for actions, soil parameters, and resistances based on the selected Design Approach.</p>
        `
    }
};
