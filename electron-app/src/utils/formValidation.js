/** Author: Utkarsh Gupta, License: GPL v3 */

// Field-level validation for calculation forms, so out-of-range and missing inputs are flagged while
// typing instead of after the backend rejects the run. Limits come from the form schema
// (minimum/maximum) and from Groundhog's own validated ranges (GET /api/schema/bounds); Groundhog wins.

const NUMERIC_TYPES = new Set(['number', 'float', 'int', 'integer']);

const isBlank = (v) => v === undefined || v === null || v === '' || (typeof v === 'string' && v.trim() === '');

const firstDefined = (...vals) => vals.find((v) => v !== undefined && v !== null && v !== '');

export const isNumericInput = (input) => NUMERIC_TYPES.has(input.type);

/** Effective {min, max, integer} of an input after merging schema limits with Groundhog bounds. */
export function resolveLimits(input, groundhogBounds) {
    const gh = groundhogBounds?.[input.name];
    const toNum = (v) => (v === undefined || v === null || v === '' ? undefined : Number(v));
    const min = toNum(firstDefined(gh?.min, input.min, input.minimum));
    const max = toNum(firstDefined(gh?.max, input.max, input.maximum));
    return {
        min: Number.isFinite(min) ? min : undefined,
        max: Number.isFinite(max) ? max : undefined,
        integer: Boolean(gh?.integer) || input.type === 'int' || input.type === 'integer',
    };
}

const fmt = (n) => (Math.abs(n) >= 1e6 || (n !== 0 && Math.abs(n) < 1e-4) ? n.toExponential(2) : String(n));

/** Short hint such as "0 – 0.5", "≥ 0" or "≤ 90"; null when unbounded. */
export function describeRange(limits) {
    const { min, max } = limits;
    if (min !== undefined && max !== undefined) return `${fmt(min)} – ${fmt(max)}`;
    if (min !== undefined) return `≥ ${fmt(min)}`;
    if (max !== undefined) return `≤ ${fmt(max)}`;
    return null;
}

const isCountedAsMissing = (input, value) => {
    if (input.type === 'boolean') return false;
    if (input.type === 'file') return !value;
    return isBlank(value);
};

/**
 * Returns an error message for one field, or null when it is valid.
 * `value` is the raw form value (inputs of type=number hand back strings).
 */
export function validateField(input, value, groundhogBounds) {
    if (isCountedAsMissing(input, value)) {
        return input.required ? 'Required' : null;
    }

    if (isNumericInput(input)) {
        const text = typeof value === 'string' ? value.trim() : value;
        const num = Number(text);
        if (text === '' || !Number.isFinite(num)) return 'Enter a valid number';
        const limits = resolveLimits(input, groundhogBounds);
        if (limits.integer && !Number.isInteger(num)) return 'Must be a whole number';
        if (limits.min !== undefined && num < limits.min) return `Must be ≥ ${fmt(limits.min)}`;
        if (limits.max !== undefined && num > limits.max) return `Must be ≤ ${fmt(limits.max)}`;
        return null;
    }

    if (input.type === 'list' && typeof value === 'string') {
        // Every list field in the schemas holds numbers (depths, times, limits, measurements).
        const bad = value.split(/[\s,;\[\]]+/).find((t) => t !== '' && !Number.isFinite(Number(t)));
        if (bad !== undefined) return `"${bad}" is not a number`;
    }

    if (input.validationRegex && typeof value !== 'object') {
        try {
            if (!new RegExp(input.validationRegex).test(String(value))) return 'Invalid format';
        } catch {
            // A malformed override pattern must not block the calculation.
        }
    }
    return null;
}

/** Validates every input; returns {fieldName: message} for the invalid ones only. */
export function validateForm(inputs, formData, groundhogBounds) {
    const errors = {};
    for (const input of inputs) {
        const message = validateField(input, formData[input.name], groundhogBounds);
        if (message) errors[input.name] = message;
    }
    return errors;
}
