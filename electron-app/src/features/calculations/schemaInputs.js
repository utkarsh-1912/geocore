/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * A form schema's inputs as one flat list, whichever way the schema is written (an `inputs` array or JSON-Schema
 * `properties` + `required`), and Groundhog's validated input ranges. Shared by the calculation form and the
 * method comparison so both see the same fields, required marks and limits.
 */
import { api } from '../../api/client';

export const normalizeSchemaInputs = (schema) => {
    if (!schema) return [];
    if (schema.inputs) return schema.inputs;
    if (schema.properties) {
        return Object.entries(schema.properties).map(([key, prop]) => ({
            name: key,
            label: prop.title || key,
            type: prop.type,
            description: prop.description,
            default: prop.default,
            required: schema.required?.includes(key),
            enum: prop.enum,
            minimum: prop.minimum,
            maximum: prop.maximum,
            unit: prop.unit,
            objectType: prop.objectType
        }));
    }
    return [];
};

// Groundhog's validated ranges never change while the app runs: fetch once, share across forms.
let boundsPromise = null;
export const loadFieldBounds = () => {
    if (!boundsPromise) {
        boundsPromise = api.getFieldBounds().catch(err => {
            boundsPromise = null; // allow a retry once the engine is up
            console.warn('Field bounds unavailable; forms fall back to schema limits.', err);
            return {};
        });
    }
    return boundsPromise;
};
