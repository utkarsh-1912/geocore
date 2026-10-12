/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Display formatting for calculated numbers. A fixed number of decimals rounds small results such as a
 * volume compressibility of 2.4e-5 1/kPa to "0", so values below 1 keep significant figures instead,
 * and very small values switch to scientific notation.
 */
const SIG_FIGS = 4;

export function formatNumber(value, { grouping = true } = {}) {
    if (typeof value !== 'number') return String(value);
    if (!Number.isFinite(value)) return String(value);
    const abs = Math.abs(value);
    if (abs !== 0 && abs < 1e-3) {
        // 2.383e-5, trailing zeros in the mantissa dropped
        return value.toExponential(SIG_FIGS - 1).replace(/\.?0+e/, 'e');
    }
    const options = abs < 1
        ? { maximumSignificantDigits: SIG_FIGS }
        : { maximumFractionDigits: SIG_FIGS };
    return value.toLocaleString(undefined, { ...options, useGrouping: grouping });
}
