/** Author: Utkarsh Gupta, License: GPL v3 */

// Field-level validation for calculation forms, so out-of-range and missing inputs are flagged while
// typing instead of after the backend rejects the run. Limits come from the form schema
// (minimum/maximum) and from Groundhog's own validated ranges (GET /api/schema/bounds); Groundhog wins.

const NUMERIC_TYPES = new Set(['number', 'float', 'int', 'integer']);

export const isBlank = (v) => v === undefined || v === null || v === '' || (typeof v === 'string' && v.trim() === '');

const firstDefined = (...vals) => vals.find((v) => v !== undefined && v !== null && v !== '');

export const isNumericInput = (input) => NUMERIC_TYPES.has(input.type);

/**
 * Effective {min, max, minExclusive, maxExclusive, integer} of an input after merging schema limits with
 * the calculation's validated bounds. An exclusive end is a value the calculation rejects itself, e.g.
 * σ'v0 = 0 when the method divides by it, so the range is "> 0" rather than "≥ 0".
 */
export function resolveLimits(input, groundhogBounds) {
    const gh = groundhogBounds?.[input.name];
    const toNum = (v) => (v === undefined || v === null || v === '' ? undefined : Number(v));
    const ghMin = toNum(gh?.min);
    const ghMax = toNum(gh?.max);
    const min = toNum(firstDefined(gh?.min, input.min, input.minimum));
    const max = toNum(firstDefined(gh?.max, input.max, input.maximum));
    return {
        min: Number.isFinite(min) ? min : undefined,
        max: Number.isFinite(max) ? max : undefined,
        minExclusive: ghMin !== undefined ? Boolean(gh.min_exclusive) : Boolean(input.minExclusive),
        maxExclusive: ghMax !== undefined ? Boolean(gh.max_exclusive) : Boolean(input.maxExclusive),
        integer: Boolean(gh?.integer) || input.type === 'int' || input.type === 'integer',
    };
}

const fmt = (n) => (Math.abs(n) >= 1e6 || (n !== 0 && Math.abs(n) < 1e-4) ? n.toExponential(2) : String(n));

/** Short hint such as "0 – 0.5", "> 0, ≤ 100", "≥ 0" or "< 90"; null when unbounded. */
export function describeRange(limits) {
    const { min, max, minExclusive, maxExclusive } = limits;
    const lower = min !== undefined ? `${minExclusive ? '>' : '≥'} ${fmt(min)}` : null;
    const upper = max !== undefined ? `${maxExclusive ? '<' : '≤'} ${fmt(max)}` : null;
    if (lower && upper) return minExclusive || maxExclusive ? `${lower}, ${upper}` : `${fmt(min)} – ${fmt(max)}`;
    return lower || upper;
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
        if (limits.min !== undefined && (limits.minExclusive ? num <= limits.min : num < limits.min)) {
            return `Must be ${limits.minExclusive ? '>' : '≥'} ${fmt(limits.min)}`;
        }
        if (limits.max !== undefined && (limits.maxExclusive ? num >= limits.max : num > limits.max)) {
            return `Must be ${limits.maxExclusive ? '<' : '≤'} ${fmt(limits.max)}`;
        }
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
