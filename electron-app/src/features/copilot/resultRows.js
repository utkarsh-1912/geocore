/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Name / symbol / unit / value rows for the scalar values of a GeoAI tool result (see ResultValues.jsx).
 */
import { getParameterNotation } from '@/utils/geoNotation';
import { unitFor } from '@/utils/quantities';

const bareName = (key) => String(key).replace(/\s*\[[^\]]*\]\s*$/, '').trim();

export const formatResultValue = (value) => {
    if (typeof value === 'number') return Number.isFinite(value) ? value.toLocaleString(undefined, { maximumFractionDigits: 4 }) : '–';
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    return value === null || value === undefined || value === '' ? '–' : String(value);
};

/** {key, label, symbol, unit, value} for each displayable entry (internal "_" keys and nested objects are skipped). */
export const resultRows = (results, functionId, outputUnits = {}) => Object.entries(results || {})
    .filter(([key, value]) => !key.startsWith('_') && (value === null || typeof value !== 'object'))
    .map(([key, value]) => {
        const notation = getParameterNotation(key, undefined, functionId);
        const unit = unitFor(functionId, key, outputUnits?.[key]);
        return {
            key,
            label: notation?.label || bareName(key).replace(/_/g, ' '),
            symbol: notation?.symbol || '',
            unit: unit && unit !== '-' ? unit : '',
            value,
        };
    });
