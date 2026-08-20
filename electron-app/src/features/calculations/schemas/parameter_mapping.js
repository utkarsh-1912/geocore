/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

export const parameterMappingSchemas = {
    get_projected_point: {
        inputs: [
            { name: "lon1", type: "float", description: "Longitude of line end 1", required: true },
            { name: "lat1", type: "float", description: "Latitude of line end 1", required: true },
            { name: "lon2", type: "float", description: "Longitude of line end 2", required: true },
            { name: "lat2", type: "float", description: "Latitude of line end 2", required: true },
            { name: "lon3", type: "float", description: "Longitude of point", required: true },
            { name: "lat3", type: "float", description: "Latitude of point", required: true }
        ]
    },
    latlon_distance: {
        inputs: [
            { name: "lon1", type: "float", required: true },
            { name: "lat1", type: "float", required: true },
            { name: "lon2", type: "float", required: true },
            { name: "lat2", type: "float", required: true }
        ]
    },
    map_depth_properties: {
        inputs: [
            { name: "target_soilprofile", type: "object_select", objectType: "SoilProfile", description: "Profile to map properties TO", required: true },
            { name: "layering_soilprofile", type: "object_select", objectType: "SoilProfile", description: "Profile containing layering properties", required: true },
            { name: "target_z_key", type: "column_select", description: "Depth key in target (optional)" },
            { name: "layering_zfrom_key", type: "column_select", description: "Start depth key in layering (optional)" },
            { name: "layering_zto_key", type: "column_select", description: "End depth key in layering (optional)" }
        ]
    },
    offsets_api: {
        inputs: [
            { name: "x1", type: "float", description: "Start point X/Lon", required: true },
            { name: "y1", type: "float", description: "Start point Y/Lat", required: true },
            { name: "x2", type: "float", description: "End point X/Lon", required: true },
            { name: "y2", type: "float", description: "End point Y/Lat", required: true },
            { name: "xp", type: "float", description: "Point X/Lon", required: true },
            { name: "yp", type: "float", description: "Point Y/Lat", required: true },
            { name: "latlon", type: "boolean", default: false, description: "Is coordinate system Lat/Lon?" }
        ]
    },
    merge_two_dicts: {
        inputs: [
            { name: "x", type: "string", description: "JSON dictionary 1", required: true },
            { name: "y", type: "string", description: "JSON dictionary 2", required: true }
        ]
    },
    reverse_dict: {
        inputs: [
            { name: "input_dict", type: "string", description: "JSON dictionary", required: true }
        ]
    }
};
