/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Custom method comparison (POST /api/calculations/{id}/compare): start from the open method, add the methods to
 * compare it with, and set the parameters in a column per method - every input any picked method takes, shared
 * ones first. Values start from the form as typed (or the last calculation) and each method's own defaults.
 * Before running, each method's required inputs and value limits are checked and shared inputs set differently
 * between methods are flagged (comparisonWarnings), so a method that cannot run says why instead of failing.
 * Results line up by quantity across methods.
 */
import React, { useEffect, useMemo, useState } from 'react';
import { Play, AlertTriangle, Info, Plus, X, RotateCcw, CopyCheck } from 'lucide-react';
import { api } from '@/api/client';
import { inputLabel } from '@/utils/geoNotation';
import { describeRange, isNumericInput, resolveLimits } from '@/utils/formValidation';
import { getSchema, hasSchema } from './schemas';
import { normalizeSchemaInputs, loadFieldBounds } from './schemaInputs';
import { ObjectSelector } from './SchemaForm';
import { mergeMethodParameters, comparisonWarnings, spreadPercent } from './methodComparison';

const fmt = (v) => (typeof v === 'number' ? Number(v.toPrecision(5)).toLocaleString() : String(v));
const CONTROL = 'w-full min-w-0 rounded-md border bg-input px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:ring-2 focus:ring-primary/20';
// Inputs filled from a file or its columns: kept from the calculation form, not edited here.
const FROM_FORM_TYPES = new Set(['file', 'column_select']);

/** One method's starting values: its own schema defaults, then the form's values for the inputs it takes. */
const startValues = (method, seed) => {
    const values = {};
    method.inputs.forEach((i) => {
        if (i.default !== undefined && i.default !== null) values[i.name] = i.default;
        if (seed && i.name in seed) values[i.name] = seed[i.name];
    });
    // A method without a known schema gets everything the form had.
    return method.known ? values : { ...(seed || {}) };
};
const startAll = (methods, seed) => Object.fromEntries(methods.map((m) => [m.id, startValues(m, seed)]));

/** Request values: blanks left out (the method then applies its own default); files sent by path. */
const toPayload = (values) => Object.fromEntries(Object.entries(values || {})
    .filter(([, v]) => v !== undefined && v !== null && !(typeof v === 'string' && v.trim() === ''))
    .map(([k, v]) => [k, v instanceof File ? (v.path || v.name) : v]));

const ParameterControl = ({ id, input, value, onChange, invalid }) => {
    const border = invalid ? 'border-error' : 'border-border-strong';
    if (FROM_FORM_TYPES.has(input.type)) {
        const shown = value instanceof File ? value.name : value;
        return <span className="text-text-muted italic">{shown ? String(shown) : 'Set in the calculation form'}</span>;
    }
    if (input.type === 'object_select') {
        return <ObjectSelector id={id} objectType={input.objectType} value={value || ''} onChange={onChange} invalid={invalid} />;
    }
    if (input.type === 'boolean') {
        return <input id={id} type="checkbox" checked={value === true || value === 'true'} onChange={(e) => onChange(e.target.checked)} className="h-4 w-4 accent-primary" />;
    }
    const options = input.enum || input.options;
    if (options || input.type === 'select') {
        return (
            <select id={id} value={value ?? ''} onChange={(e) => onChange(e.target.value)} className={`${CONTROL} ${border}`}>
                <option value="">—</option>
                {(options || []).map((o) => {
                    const v = typeof o === 'object' ? o.value : o;
                    return <option key={String(v)} value={v}>{typeof o === 'object' ? (o.label ?? o.value) : o}</option>;
                })}
            </select>
        );
    }
    return <input id={id} type="text" inputMode={isNumericInput(input) ? 'decimal' : undefined} value={value ?? ''}
        onChange={(e) => onChange(e.target.value)} className={`${CONTROL} ${border} font-mono`} />;
};

const Notice = ({ tone = 'warning', children }) => (
    <div className={`flex gap-2 rounded-md border px-3 py-2 text-xs text-text-main ${tone === 'warning' ? 'border-warning/40 bg-warning/10' : 'border-border bg-surface-muted/50'}`}
        role={tone === 'warning' ? 'alert' : undefined}>
        {tone === 'warning' ? <AlertTriangle size={14} className="mt-0.5 shrink-0 text-warning" /> : <Info size={14} className="mt-0.5 shrink-0 text-text-muted" />}
        <div className="min-w-0 space-y-1">{children}</div>
    </div>
);

export const CompareAllMethods = ({ calculationId, methods = [], inputs, activeFunctionId }) => {
    // Every method of the calculation with its normalised schema inputs.
    const allMethods = useMemo(() => methods.map((m) => ({
        id: m.id, method: m.method || m.id, title: m.title,
        known: hasSchema(m.id), inputs: hasSchema(m.id) ? normalizeSchemaInputs(getSchema(m.id)) : [],
    })), [methods]);
    // Starts with the open method only; the user adds the ones to compare it with.
    const [selected, setSelected] = useState(() => {
        const current = allMethods.find((m) => m.id === activeFunctionId) || allMethods[0];
        return current ? [current.id] : [];
    });
    const chosen = useMemo(() => allMethods.filter((m) => selected.includes(m.id)), [allMethods, selected]);
    const params = useMemo(() => mergeMethodParameters(chosen), [chosen]);
    // {method id: {input: value}} for every method, so one added later already has its starting values.
    const [values, setValues] = useState(() => startAll(allMethods, inputs));
    const [bounds, setBounds] = useState({});
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);

    useEffect(() => {
        let alive = true;
        loadFieldBounds().then((all) => { if (alive) setBounds(all || {}); });
        return () => { alive = false; };
    }, []);

    const warnings = useMemo(() => comparisonWarnings(chosen, params, values, bounds), [chosen, params, values, bounds]);
    const titleOf = (id) => allMethods.find((m) => m.id === id)?.title || id;
    const cellMissing = (id, name) => warnings.missing.some((w) => w.id === id && w.names.includes(name));
    const cellInvalid = (id, name) => warnings.invalid.find((w) => w.id === id && w.name === name)?.message;
    const differs = (name) => warnings.differing.some((d) => d.name === name);

    const setValue = (id, name, v) => setValues((prev) => ({ ...prev, [id]: { ...prev[id], [name]: v } }));
    // Give every selected method that takes this input the same value.
    const applyToAll = (p, v) => setValues((prev) => {
        const next = { ...prev };
        p.usedBy.forEach((id) => { next[id] = { ...next[id], [p.name]: v }; });
        return next;
    });
    const remove = (id) => setSelected((prev) => prev.filter((x) => x !== id));
    const add = (id) => id && setSelected((prev) => allMethods.map((m) => m.id).filter((x) => x === id || prev.includes(x)));
    const unselected = allMethods.filter((m) => !selected.includes(m.id));

    const run = async () => {
        setBusy(true);
        setError(null);
        try {
            const ready = chosen.filter((m) => warnings.runnable.includes(m.id));
            // Shared: what the form had beyond the listed inputs (uploaded rows and the like); each method: its own column.
            const listed = new Set(allMethods.flatMap((m) => m.inputs.map((i) => i.name)));
            const shared = toPayload(Object.fromEntries(Object.entries(inputs || {}).filter(([k]) => !listed.has(k))));
            const own = Object.fromEntries(ready.map((m) => [m.method, toPayload(values[m.id])]));
            setResult(await api.compareMethods(calculationId, shared, ready.map((m) => m.method), own));
        } catch (e) {
            setError(e.message);
        } finally {
            setBusy(false);
        }
    };

    const ran = result?.methods.filter((m) => !m.error) || [];
    const failed = result?.methods.filter((m) => m.error) || [];
    const skipped = chosen.filter((m) => !warnings.runnable.includes(m.id));
    const runnableCount = warnings.runnable.length;

    return (
        <div className="space-y-4 text-xs" data-compare-all>
            {/* 1. Methods */}
            <section className="space-y-2">
                <h4 className="font-semibold text-text-main">Methods to compare</h4>
                <div className="flex flex-wrap items-center gap-1.5">
                    {chosen.map((m) => (
                        <span key={m.id} className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 ${warnings.runnable.includes(m.id) ? 'border-primary/40 bg-primary/5 text-text-main' : 'border-warning/50 bg-warning/10 text-text-main'}`}>
                            {m.title}{m.id === activeFunctionId && <span className="text-text-muted">(current)</span>}
                            <button type="button" onClick={() => remove(m.id)} aria-label={`Remove ${m.title}`} className="rounded-full p-0.5 text-text-muted hover:text-text-main"><X size={11} /></button>
                        </span>
                    ))}
                    {unselected.length > 0 && (
                        <label className="inline-flex items-center gap-1 rounded-full border border-dashed border-border-strong px-2 py-0.5 text-text-muted hover:border-primary/60">
                            <Plus size={12} />
                            <select aria-label="Add method" value="" onChange={(e) => add(e.target.value)} className="bg-transparent py-0.5 text-xs text-text-main focus:outline-none">
                                <option value="">Add method</option>
                                {unselected.map((m) => <option key={m.id} value={m.id}>{m.title}</option>)}
                            </select>
                        </label>
                    )}
                </div>
                {chosen.length < 2 && <p className="text-text-muted">Add a method to compare with.</p>}
            </section>

            {/* 2. Parameters: a column per method */}
            {chosen.length > 0 && (
                <section className="space-y-2">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                        <h4 className="font-semibold text-text-main">Parameters</h4>
                        {inputs && (
                            <button type="button" onClick={() => setValues(startAll(allMethods, inputs))}
                                className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-text-muted hover:bg-surface-muted hover:text-text-main">
                                <RotateCcw size={12} />Reload form values
                            </button>
                        )}
                    </div>
                    <div className="max-w-full overflow-x-auto rounded-md border border-border">
                        <table className="w-full border-collapse text-left">
                            <thead className="border-b border-border bg-surface-muted text-text-muted">
                                <tr>
                                    <th className="px-3 py-2 font-medium">Parameter</th>
                                    {chosen.map((m) => <th key={m.id} className="min-w-[10rem] px-3 py-2 font-medium">{m.title}</th>)}
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border/60">
                                {params.map((p) => {
                                    const label = inputLabel(p.input, p.usedBy[0]);
                                    const titleMatch = /^(.*?)\s*\[([^\]]+)\]\s*$/.exec(p.input.label || '');
                                    const name = titleMatch ? titleMatch[1] : label.text;
                                    const unit = p.input.unit || (titleMatch ? titleMatch[2] : null);
                                    const range = isNumericInput(p.input) ? describeRange(resolveLimits(p.input, bounds[p.usedBy[0]])) : null;
                                    const shared = p.usedBy.length > 1;
                                    const differing = differs(p.name);
                                    return (
                                        <tr key={p.name} className={differing ? 'bg-warning/5' : ''}>
                                            <td className="px-3 py-1.5 align-top">
                                                <div className="flex flex-wrap items-center gap-1.5 text-text-main" title={p.name}>
                                                    {label.symbol && <span className="rounded bg-primary/10 px-1 font-mono text-primary">{label.symbol}</span>}
                                                    <span>{name}</span>
                                                    {unit && unit !== '-' && <span className="text-text-muted">[{unit}]</span>}
                                                    {shared && (
                                                        <span className={`rounded px-1.5 py-0.5 font-medium ${differing ? 'bg-warning/15 text-warning' : 'bg-primary/10 text-primary'}`}
                                                            title={differing ? 'Set differently between methods' : 'Taken by several methods'}>
                                                            {differing ? 'differs' : 'shared'}
                                                        </span>
                                                    )}
                                                </div>
                                                {range && <div className="font-mono text-[10px] text-text-muted">{range}</div>}
                                            </td>
                                            {chosen.map((m) => {
                                                const def = p.defs[m.id];
                                                if (!def) return <td key={m.id} className="px-3 py-1.5 align-top text-text-subtle">—</td>;
                                                const missing = cellMissing(m.id, p.name);
                                                const invalid = cellInvalid(m.id, p.name);
                                                const value = values[m.id]?.[p.name];
                                                return (
                                                    <td key={m.id} className="px-3 py-1.5 align-top">
                                                        <div className="flex items-center gap-1">
                                                            <div className="min-w-0 flex-1">
                                                                <ParameterControl id={`compare-${m.id}-${p.name}`} input={def} value={value}
                                                                    onChange={(v) => setValue(m.id, p.name, v)} invalid={missing || Boolean(invalid)} />
                                                            </div>
                                                            {def.required && <span className="font-bold text-primary" title="Required by this method">*</span>}
                                                            {differing && !FROM_FORM_TYPES.has(def.type) && (
                                                                <button type="button" onClick={() => applyToAll(p, value)} title="Use this value for every method"
                                                                    aria-label={`Use ${m.title}'s ${p.name} for every method`}
                                                                    className="shrink-0 rounded p-1 text-text-muted hover:bg-surface-muted hover:text-primary">
                                                                    <CopyCheck size={12} />
                                                                </button>
                                                            )}
                                                        </div>
                                                        {missing && <div className="mt-1 text-error">Required</div>}
                                                        {invalid && <div className="mt-1 text-error">{invalid}</div>}
                                                    </td>
                                                );
                                            })}
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                    <p className="text-[11px] text-text-muted">— the method does not take this input. * required by that method; blank optional inputs use the method's own default.</p>
                </section>
            )}

            {/* 3. Warnings before running */}
            {skipped.length > 0 && (
                <Notice>
                    <div className="font-semibold">{skipped.length === chosen.length ? 'No method can run yet:' : 'These methods will be skipped until their inputs are complete:'}</div>
                    <ul className="list-disc pl-4">
                        {skipped.map((m) => {
                            const miss = warnings.missing.find((w) => w.id === m.id);
                            const bad = warnings.invalid.filter((w) => w.id === m.id);
                            return (
                                <li key={m.id}>
                                    <span className="font-medium">{m.title}</span>
                                    {miss && <> needs <span className="font-mono">{miss.names.join(', ')}</span></>}
                                    {miss && bad.length > 0 && ';'}
                                    {bad.length > 0 && <> has invalid {bad.map((b) => <span key={b.name} className="font-mono">{b.name} ({b.message.toLowerCase()})</span>).reduce((a, b) => [a, ', ', b])}</>}
                                </li>
                            );
                        })}
                    </ul>
                </Notice>
            )}
            {warnings.differing.length > 0 && (
                <Notice>
                    <div className="font-semibold">Shared inputs are set differently between methods, so this is not a like-for-like comparison:</div>
                    <ul className="list-disc pl-4">
                        {warnings.differing.map((d) => (
                            <li key={d.name}><span className="font-mono">{d.name}</span>: {Object.entries(d.values).map(([id, v]) => `${titleOf(id)} ${v === undefined || v === null || v === '' ? 'blank' : String(v)}`).join(' · ')}</li>
                        ))}
                    </ul>
                </Notice>
            )}
            {warnings.sharedBlank.length > 0 && (
                <Notice>
                    <div className="font-semibold">Shared inputs left blank: each method falls back on its own default, so the comparison may not be like-for-like.</div>
                    <ul className="list-disc pl-4">
                        {warnings.sharedBlank.map((s) => <li key={s.name}><span className="font-mono">{s.name}</span> ({s.usedBy.map(titleOf).join(', ')})</li>)}
                    </ul>
                </Notice>
            )}
            {chosen.some((m) => !m.known) && (
                <Notice tone="info">
                    The inputs of {chosen.filter((m) => !m.known).map((m) => m.title).join(', ')} are not listed here; it runs with the form's values and reports anything it is missing.
                </Notice>
            )}
            {warnings.exclusive.length > 0 && (
                <Notice tone="info">
                    <div>Some inputs are taken by one method only, so its result also depends on them:</div>
                    <ul className="list-disc pl-4">
                        {warnings.exclusive.map((e) => <li key={e.id}><span className="font-medium">{e.title}</span>: <span className="font-mono">{e.names.join(', ')}</span></li>)}
                    </ul>
                </Notice>
            )}

            {/* 4. Run */}
            <div className="flex flex-wrap items-center justify-end gap-2">
                <span className="text-text-muted">{runnableCount} of {chosen.length} method{chosen.length === 1 ? '' : 's'} ready</span>
                <button type="button" onClick={run} disabled={busy || runnableCount === 0}
                    className="inline-flex h-8 items-center gap-1.5 rounded-md bg-primary px-3 font-medium text-white hover:bg-primary/90 disabled:opacity-50">
                    <Play size={13} />{busy ? 'Running…' : runnableCount === chosen.length ? 'Run all' : `Run ${runnableCount} ready`}
                </button>
            </div>

            {/* 5. Results */}
            {error && <p className="text-error" role="alert">{error}</p>}
            {result && ran.length > 0 && result.rows.length > 0 && (
                <div className="max-w-full overflow-x-auto rounded-md border border-border">
                    <table className="w-full border-collapse text-left">
                        <thead className="border-b border-border bg-surface-muted text-text-muted">
                            <tr>
                                <th className="px-3 py-2 font-medium">Output</th>
                                {ran.map((m) => <th key={m.method} className="px-3 py-2 font-medium">{m.label}</th>)}
                                {ran.length > 1 && <th className="px-3 py-2 font-medium" title="(max − min) / |mean| across methods">Spread</th>}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {result.rows.map((r) => {
                                const spread = spreadPercent(r.values);
                                return (
                                    <tr key={`${r.label}|${r.unit}`}>
                                        <td className="px-3 py-1.5 text-text-main">{r.label}{r.symbol ? <span className="ml-1 font-mono text-primary">{r.symbol}</span> : null}{r.unit ? <span className="ml-1 text-text-muted">[{r.unit}]</span> : null}</td>
                                        {ran.map((m) => <td key={m.method} className="px-3 py-1.5 font-mono tabular-nums text-text-main">{m.method in r.values ? fmt(r.values[m.method]) : '–'}</td>)}
                                        {ran.length > 1 && <td className="px-3 py-1.5 font-mono tabular-nums text-text-muted">{spread === null ? '–' : `${spread.toFixed(1)} %`}</td>}
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}
            {failed.map((m) => (
                <p key={m.method} className="flex gap-1.5 text-text-main">
                    <AlertTriangle size={13} className="mt-0.5 shrink-0 text-warning" />
                    <span><span className="font-semibold">{m.label}</span> did not run: {m.error}</span>
                </p>
            ))}
        </div>
    );
};

export default CompareAllMethods;
