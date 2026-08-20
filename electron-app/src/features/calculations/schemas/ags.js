/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

export const agsSchemas = {
    AGSConverter: {
        inputs: [
            { name: "data", type: "file", accept: ".ags", description: "AGS File", required: true },
            { name: "encoding", type: "string", default: "utf8", description: "File encoding" },
            { name: "agsformat", type: "select", options: ["4", "3.1"], default: "4", description: "AGS Format version" },
            { name: "name", type: "string", description: "Object name (optional)" }
        ]
    },
    AGSConverter_convert_ags_group: {
        inputs: [
            { name: "agsconverter", type: "object_select", objectType: "AGSConverter", description: "AGSConverter object", required: true },
            { name: "groupname", type: "string", description: "Name of the group (e.g. SCPT, GEOL)", required: true },
            { name: "verbose_keys", type: "boolean", default: false, description: "Use verbose equivalents for keys?" },
            { name: "use_shorthands", type: "boolean", default: false, description: "Use shorthand codes?" }
        ]
    }
};
