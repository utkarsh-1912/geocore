/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Phase relations "solve for": enter what you know, pick what you need; the backend chains the existing Groundhog
 * phase-relation functions (python-backend/core/catalogue/phase_relations.py) and returns the value with every step,
 * the constants used and any soil property it was allowed to assume. Soil properties (Gs, Sr) are only assumed when
 * the user ticks them. The individual phase-relation forms below stay available.
 */
import React, { useEffect, useMemo, useState } from 'react';
import { Calculator, AlertTriangle, ChevronDown } from 'lucide-react';
import { api } from '@/api/client';
import { catalogueEntry } from '@/config/navigation';

const fmt = (v) => (typeof v === 'number' ? Number(v.toPrecision(5)).toLocaleString(undefined, { maximumFractionDigits: 6 }) : v);

// `embedded`: the content only, for a panel inside the form card (no card or collapsible header of its own).
export const PhaseSolver = ({ functionId, embedded = false }) => {
    const [info, setInfo] = useState(null);
    const [loadError, setLoadError] = useState(null);
    const [open, setOpen] = useState(true);
    const [known, setKnown] = useState({});
    const [target, setTarget] = useState('bulk_unit_weight');
    const [assume, setAssume] = useState([]);
    const [unitWeightWater, setUnitWeightWater] = useState('');
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);

    useEffect(() => {
        let cancelled = false;
        api.phaseRelationsInfo().then((d) => !cancelled && setInfo(d)).catch((e) => !cancelled && setLoadError(e.message));
        return () => { cancelled = true; };
    }, []);

    const methodTitles = useMemo(() => {
        const entry = catalogueEntry(functionId);
        return Object.fromEntries((entry?.methods || []).map((m) => [m.id, m.title]));
    }, [functionId]);
    const labelOf = (id) => info?.quantities.find((q) => q.id === id)?.label || info?.constants.find((c) => c.id === id)?.label || id;
    const unitOf = (id) => info?.quantities.find((q) => q.id === id)?.unit || info?.constants.find((c) => c.id === id)?.unit || '';

    const solve = async () => {
        setBusy(true);
        setError(null);
        setResult(null);
        const given = Object.fromEntries(Object.entries(known).filter(([q, v]) => q !== target && v !== '' && v !== undefined));
        try {
            setResult(await api.phaseRelationsSolve({
                known: given, target, assume,
                unit_weight_water: unitWeightWater === '' ? undefined : Number(unitWeightWater),
            }));
        } catch (e) {
            setError({ message: e.message, needs: e.needs || [] });
        } finally {
            setBusy(false);
        }
    };

    if (loadError) return null; // engine offline: the individual forms below still work once it is up
    if (!info) return null;

    const body = (
                <div className={embedded ? 'space-y-4' : 'space-y-4 border-t border-border px-4 py-4'} data-phase-solver={embedded ? '' : undefined}>
                    <p className="text-xs text-text-muted">Enter the quantities you know (water content, saturation and porosity as fractions) and choose the one you need. Each step uses one of the phase-relation calculations below.</p>
                    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
                        {info.quantities.map((q) => (
                            <label key={q.id} className={`flex items-center justify-between gap-2 rounded-md border px-2.5 py-1.5 text-xs ${q.id === target ? 'border-primary/40 bg-primary/5' : 'border-border'}`}>
                                <span className="min-w-0 truncate text-text-main" title={q.label}>{q.label}</span>
                                {q.id === target
                                    ? <span className="shrink-0 font-semibold text-primary">to solve</span>
                                    : (
                                        <span className="flex shrink-0 items-center gap-1">
                                            <input type="number" step="any" value={known[q.id] ?? ''} aria-label={q.label}
                                                onChange={(e) => setKnown({ ...known, [q.id]: e.target.value })}
                                                className="w-20 rounded-md border border-border bg-background px-1.5 py-0.5 text-right tabular-nums text-text-main" />
                                            <span className="w-9 text-text-muted">{q.unit === '-' ? '' : q.unit}</span>
                                        </span>
                                    )}
                            </label>
                        ))}
                    </div>
                    <div className="flex flex-wrap items-end gap-4 text-xs">
                        <label className="flex flex-col gap-1">
                            <span className="font-semibold text-text-main">Solve for</span>
                            <select value={target} onChange={(e) => { setTarget(e.target.value); setResult(null); setError(null); }}
                                className="rounded-md border border-border bg-background px-2 py-1 text-text-main">
                                {info.quantities.map((q) => <option key={q.id} value={q.id}>{q.label}</option>)}
                            </select>
                        </label>
                        <fieldset className="flex flex-col gap-1">
                            <legend className="font-semibold text-text-main">Allow Groundhog defaults (reported as assumptions)</legend>
                            <div className="flex flex-wrap gap-3">
                                {info.assumable.map((a) => (
                                    <label key={a.id} className="flex items-center gap-1.5 text-text-muted">
                                        <input type="checkbox" checked={assume.includes(a.id)}
                                            onChange={(e) => setAssume(e.target.checked ? [...assume, a.id] : assume.filter((x) => x !== a.id))} />
                                        {a.label} = {a.value}
                                    </label>
                                ))}
                            </div>
                        </fieldset>
                        <label className="flex flex-col gap-1">
                            <span className="font-semibold text-text-main">γw [kN/m³] (optional)</span>
                            <input type="number" step="any" placeholder="9.81 (ρw·g)" value={unitWeightWater}
                                onChange={(e) => setUnitWeightWater(e.target.value)}
                                className="w-28 rounded-md border border-border bg-background px-2 py-1 text-text-main" />
                        </label>
                        <button type="button" onClick={solve} disabled={busy}
                            className="btn-brand ml-auto h-8 rounded-md px-4 text-xs font-semibold disabled:opacity-60">{busy ? 'Solving…' : 'Solve'}</button>
                    </div>

                    {error && (
                        <div className="flex gap-2 rounded-md border border-warning/40 bg-warning/10 px-3 py-2 text-xs text-text-main" role="alert">
                            <AlertTriangle size={14} className="mt-0.5 shrink-0 text-warning" />
                            <div>
                                <div>{error.message}</div>
                                {error.needs.length > 0 && (
                                    <div className="mt-1 text-text-muted">To get it, also give one of: {error.needs.map((n) => n.map(labelOf).join(' + ')).join('; or ')}.</div>
                                )}
                            </div>
                        </div>
                    )}

                    {result && (
                        <div className="space-y-3" data-phase-result>
                            <div className="rounded-md border border-primary/30 bg-primary/5 px-3 py-2">
                                <div className="text-xs text-text-muted">{result.label}</div>
                                <div className="text-lg font-bold tabular-nums text-text-main">{fmt(result.value)} <span className="text-sm font-normal text-text-muted">{result.unit === '-' ? '' : result.unit}</span></div>
                            </div>
                            <ol className="space-y-1.5 text-xs">
                                {result.steps.map((s, i) => (
                                    <li key={i} className="rounded-md border border-border px-3 py-2">
                                        <div className="font-semibold text-text-main">{i + 1}. {methodTitles[s.function] || s.function}</div>
                                        <div className="text-text-muted">
                                            {Object.entries(s.inputs).map(([q, v]) => `${labelOf(q)} = ${fmt(v)}${unitOf(q) && unitOf(q) !== '-' ? ` ${unitOf(q)}` : ''}`).join(', ')}
                                            {'  →  '}
                                            <span className="text-text-main">{Object.entries(s.outputs).map(([q, v]) => `${labelOf(q)} = ${fmt(v)}${unitOf(q) && unitOf(q) !== '-' ? ` ${unitOf(q)}` : ''}`).join(', ')}</span>
                                        </div>
                                    </li>
                                ))}
                            </ol>
                            {(result.constants.length > 0 || result.assumptions.length > 0) && (
                                <div className="text-[11px] text-text-muted space-y-0.5">
                                    {result.constants.length > 0 && <div>Constants: {result.constants.map((c) => `${c.label} = ${fmt(c.value)} ${c.unit}`).join(', ')}.</div>}
                                    {result.assumptions.map((a) => <div key={a.quantity} className="text-warning">Assumed {a.label} = {a.value} ({a.note}).</div>)}
                                </div>
                            )}
                        </div>
                    )}
                </div>
    );
    if (embedded) return body;

    return (
        <section className="rounded-md border border-border bg-surface shadow-card" data-phase-solver>
            <button type="button" onClick={() => setOpen(!open)} aria-expanded={open}
                className="flex w-full items-center justify-between gap-2 px-4 py-3 text-left">
                <span className="flex items-center gap-2 text-sm font-semibold text-text-main"><Calculator size={15} className="text-primary" />Solve for any phase quantity</span>
                <ChevronDown size={15} className={`text-text-muted transition-transform ${open ? 'rotate-180' : ''}`} />
            </button>
            {open && body}
        </section>
    );
};

export default PhaseSolver;
