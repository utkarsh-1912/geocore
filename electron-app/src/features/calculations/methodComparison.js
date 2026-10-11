/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Side-by-side comparison of the methods of one catalogue calculation (e.g. Pile axial capacity by LCPC,
 * Koppejan and De Beer), built from results the user already obtained in this session. Nothing is recalculated
 * here: each method's own response is read as returned by /api/execute.
 *
 *  - Scalar outputs ({"f_s_comp_out [kPa]": 12.3}, or a wrapper's Output/Value/Unit table) are aligned by key.
 *  - Depth tables (rows with a depth column) give resistance-depth profiles. Methods name the same quantity
 *    differently, so the series are matched through PROFILE_SERIES: Groundhog's LCPC calls shaft and base
 *    resistance "Qs" / "Qb" where Koppejan and De Beer call them "Rs" / "Rb"; total is "Rc" everywhere.
 *  - Inputs that two methods share by name but were run with different values are listed, so a comparison of
 *    different piles or soils is never shown as like-for-like.
 */

import { validateField, isBlank } from '../../utils/formValidation';

const DEPTH_KEYS = ['Depth [m]', 'z [m]', 'depth [m]', 'Depth from [m]'];
export const PROFILE_SERIES = {
    'Rc [kN]': { label: 'Total resistance Rc', aliases: ['Rc [kN]'] },
    'Rs [kN]': { label: 'Shaft resistance Rs', aliases: ['Rs [kN]', 'Qs [kN]'] },
    'Rb [kN]': { label: 'Base resistance Rb', aliases: ['Rb [kN]', 'Qb [kN]'] },
};

const isNumber = (v) => typeof v === 'number' && Number.isFinite(v);

/** {scalars: {key: number}, profile: {depthKey, series: {name: [[depth, value], ...]}} | null} of one response. */
export function comparable(results) {
    const scalars = {};
    let profile = null;
    if (!results || typeof results !== 'object' || Array.isArray(results) || results.error) return { scalars, profile };

    for (const [key, value] of Object.entries(results)) {
        if (!key.startsWith('_') && isNumber(value)) scalars[key] = value;
    }
    const rows = results.results?.data;
    if (Array.isArray(rows) && rows.length && rows[0] && typeof rows[0] === 'object') {
        if ('Output' in rows[0] && 'Value' in rows[0]) {
            rows.forEach((r) => {
                if (!isNumber(r.Value)) return;
                const unit = r.Unit && r.Unit !== '-' ? ` [${r.Unit}]` : '';
                scalars[`${r.Output}${unit}`] = r.Value;
            });
        }
        const depthKey = DEPTH_KEYS.find((k) => k in rows[0]);
        if (depthKey) {
            const series = {};
            for (const [name, { aliases }] of Object.entries(PROFILE_SERIES)) {
                const column = aliases.find((a) => a in rows[0]);
                if (!column) continue;
                const points = rows.filter((r) => isNumber(r[depthKey]) && isNumber(r[column])).map((r) => [r[depthKey], r[column]]);
                if (points.length) series[name] = points;
            }
            if (Object.keys(series).length) profile = { depthKey, series };
        }
    }
    return { scalars, profile };
}

const sameValue = (a, b) => (isNumber(a) && isNumber(b) ? Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(a), Math.abs(b)) : String(a) === String(b));

/**
 * runs: [{id, title, inputs, results}] (one per method, the latest run of each).
 * Returns {methods, scalarRows: [{key, values: {id: number}, shared}], profiles: {name: [{id, title, points}]},
 *          deepest: [{name, values: {id: {depth, value}}}], atCommonDepth: [{name, depth, values: {id: {depth, value}}}],
 *          inputDifferences: [{name, values: {id: value}}]}.
 */
export function compareRuns(runs) {
    const methods = runs.map(({ id, title }) => ({ id, title }));
    const parsed = runs.map((r) => ({ ...r, ...comparable(r.results) }));

    const keys = new Map();
    parsed.forEach((r) => Object.keys(r.scalars).forEach((k) => keys.set(k, (keys.get(k) || 0) + 1)));
    const scalarRows = [...keys.entries()]
        .sort((a, b) => b[1] - a[1])
        .map(([key, count]) => ({
            key,
            shared: count > 1,
            values: Object.fromEntries(parsed.filter((r) => key in r.scalars).map((r) => [r.id, r.scalars[key]])),
        }));

    const profiles = {};
    const deepest = [];
    const atCommonDepth = [];
    for (const name of Object.keys(PROFILE_SERIES)) {
        const lines = parsed.filter((r) => r.profile?.series[name]).map((r) => ({ id: r.id, title: r.title, points: r.profile.series[name] }));
        if (!lines.length) continue;
        profiles[name] = lines;
        deepest.push({
            name,
            values: Object.fromEntries(lines.map((l) => {
                const last = l.points.reduce((a, p) => (p[0] > a[0] ? p : a), l.points[0]);
                return [l.id, { depth: last[0], value: last[1] }];
            })),
        });
        // The deepest depth every run reaches; each method's own computed point at or above it (no interpolation).
        if (lines.length > 1) {
            const common = Math.min(...lines.map((l) => Math.max(...l.points.map((p) => p[0]))));
            atCommonDepth.push({
                name,
                depth: common,
                values: Object.fromEntries(lines.map((l) => {
                    const above = l.points.filter((p) => p[0] <= common + 1e-9);
                    const pick = above.reduce((a, p) => (p[0] > a[0] ? p : a), above[0]);
                    return [l.id, pick ? { depth: pick[0], value: pick[1] } : null];
                })),
            });
        }
    }

    const inputNames = new Map();
    runs.forEach((r) => Object.entries(r.inputs || {}).forEach(([k, v]) => {
        if (v === null || v === undefined || v === '' || typeof v === 'object') return;
        if (!inputNames.has(k)) inputNames.set(k, {});
        inputNames.get(k)[r.id] = v;
    }));
    const inputDifferences = [...inputNames.entries()]
        .filter(([, values]) => Object.keys(values).length > 1)
        .filter(([, values]) => { const v = Object.values(values); return v.some((x) => !sameValue(x, v[0])); })
        .map(([name, values]) => ({ name, values }));

    return { methods, scalarRows, profiles, deepest, atCommonDepth, inputDifferences };
}

// ---------------------------------------------------------------------------- custom comparison set-up

/**
 * Every input of the selected methods, once per name. methods: [{id, title, inputs: normalised schema inputs}].
 * Returns [{name, input, usedBy: [id], requiredBy: [id], defs: {id: input}}]: inputs several methods take come
 * first (they decide whether the comparison is like-for-like), then the rest in schema order.
 */
export function mergeMethodParameters(methods) {
    const params = new Map();
    methods.forEach((m) => (m.inputs || []).forEach((input) => {
        if (!params.has(input.name)) params.set(input.name, { name: input.name, input, usedBy: [], requiredBy: [], defs: {} });
        const p = params.get(input.name);
        p.usedBy.push(m.id);
        if (input.required) p.requiredBy.push(m.id);
        p.defs[m.id] = input;
    }));
    const list = [...params.values()];
    return [...list.filter((p) => p.usedBy.length > 1), ...list.filter((p) => p.usedBy.length <= 1)];
}

const sameInput = (a, b) => {
    if (isBlank(a) || isBlank(b)) return isBlank(a) && isBlank(b);
    const x = Number(a);
    const y = Number(b);
    if (typeof a !== 'boolean' && typeof b !== 'boolean' && Number.isFinite(x) && Number.isFinite(y)) return sameValue(x, y);
    return String(a).trim() === String(b).trim();
};

/**
 * What stands between the selected methods and a fair comparison, given each method's own values
 * (valuesByMethod: {method id: {input: value}}):
 *  - missing:     required inputs a method has no value for; that method cannot run.
 *  - invalid:     values outside a method's own limits (validateField with that method's input and bounds).
 *  - differing:   inputs several methods take but with different values, so it is not like-for-like.
 *  - sharedBlank: inputs several methods take, left blank everywhere: each falls back on its own default.
 *  - exclusive:   inputs only one selected method takes; its result also depends on them.
 *  - runnable:    ids of the methods with every required input given and no invalid value.
 */
export function comparisonWarnings(methods, params, valuesByMethod, boundsByMethod = {}) {
    const valueOf = (id, name) => valuesByMethod[id]?.[name];
    const missing = [];
    const invalid = [];
    methods.forEach((m) => {
        const names = [];
        params.filter((p) => p.defs[m.id]).forEach((p) => {
            const def = p.defs[m.id];
            const value = valueOf(m.id, p.name);
            if (def.type !== 'boolean' && isBlank(value)) {
                if (def.required) names.push(p.name);
                return;
            }
            const message = validateField(def, value, boundsByMethod[m.id]);
            if (message) invalid.push({ id: m.id, title: m.title, name: p.name, message });
        });
        if (names.length) missing.push({ id: m.id, title: m.title, names });
    });
    const shared = params.filter((p) => p.usedBy.length > 1);
    const differing = shared
        .filter((p) => p.usedBy.some((id) => !sameInput(valueOf(id, p.name), valueOf(p.usedBy[0], p.name))))
        .map((p) => ({ name: p.name, values: Object.fromEntries(p.usedBy.map((id) => [id, valueOf(id, p.name)])) }));
    const sharedBlank = shared
        .filter((p) => p.input.type !== 'boolean' && p.usedBy.every((id) => isBlank(valueOf(id, p.name))))
        .filter((p) => p.requiredBy.length < p.usedBy.length) // required everywhere is already "missing"
        .map((p) => ({ name: p.name, usedBy: p.usedBy }));
    const exclusive = methods.length > 1
        ? methods.map((m) => ({ id: m.id, title: m.title, names: params.filter((p) => p.usedBy.length === 1 && p.usedBy[0] === m.id).map((p) => p.name) }))
            .filter((e) => e.names.length)
        : [];
    const blocked = new Set([...missing.map((x) => x.id), ...invalid.map((x) => x.id)]);
    return { missing, invalid, differing, sharedBlank, exclusive, runnable: methods.map((m) => m.id).filter((id) => !blocked.has(id)) };
}

/** Relative spread of one output across methods, (max - min) / |mean| in %, or null below two values. */
export function spreadPercent(values) {
    const nums = Object.values(values).filter(isNumber);
    if (nums.length < 2) return null;
    const mean = nums.reduce((a, b) => a + b, 0) / nums.length;
    if (mean === 0) return null;
    return ((Math.max(...nums) - Math.min(...nums)) / Math.abs(mean)) * 100;
}
