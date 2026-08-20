/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

export const validationSchemas = {
    check_layer_overlap: {
        inputs: [
            { name: "df", type: "object_select", objectType: "SoilProfile", description: "SoilProfile object (Dataframe)", required: true },
            { name: "raise_error", type: "boolean", default: true, description: "Raise error on overlap?" },
            { name: "z_from_key", type: "column_select", description: "Key for start depth (optional if standard)" },
            { name: "z_to_key", type: "column_select", description: "Key for end depth (optional if standard)" }
        ]
    },
    validate_boolean: {
        inputs: [
            { name: "var_name", type: "string", description: "Variable name for error message", required: true },
            { name: "value", type: "boolean", description: "Value to validate", required: true }
        ]
    },
    validate_float: {
        inputs: [
            { name: "var_name", type: "string", description: "Variable name for error message", required: true },
            { name: "value", type: "float", description: "Value to validate", required: true },
            { name: "min_value", type: "float", description: "Minimum value" },
            { name: "max_value", type: "float", description: "Maximum value" }
        ]
    },
    validate_integer: {
        inputs: [
            { name: "var_name", type: "string", description: "Variable name for error message", required: true },
            { name: "value", type: "int", description: "Value to validate", required: true },
            { name: "min_value", type: "int", description: "Minimum value" },
            { name: "max_value", type: "int", description: "Maximum value" }
        ]
    },
    validate_list: {
        inputs: [
            { name: "var_name", type: "string", description: "Variable name for error message", required: true },
            { name: "value", type: "string", description: "List values (comma separated)", required: true },
            { name: "elementtype", type: "select", options: ["float", "int", "string", "boolean"], description: "Type of elements" },
            { name: "order", type: "select", options: ["ascending", "descending"], description: "Order requirement" },
            { name: "unique", type: "boolean", description: "Require unique values?" },
            { name: "empty_allowed", type: "boolean", default: true, description: "Allow empty list?" }
        ]
    },
    validate_string: {
        inputs: [
            { name: "var_name", type: "string", description: "Variable name for error message", required: true },
            { name: "value", type: "string", description: "Value to validate", required: true },
            { name: "options", type: "string", description: "Allowed options (comma separated)" },
            { name: "regex", type: "string", description: "Regex pattern" }
        ]
    }
};
