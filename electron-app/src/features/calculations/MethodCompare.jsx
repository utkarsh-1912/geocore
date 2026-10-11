/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Comparison of the methods of one calculation the user has run in this session (rules in methodComparison.js):
 * a warning for inputs that differ between the runs, resistance-depth profiles overlaid per method, the values at
 * the deepest point, and the scalar outputs side by side. Values are the methods' own results, unchanged.
 */
import React, { useMemo } from 'react';
import { AlertTriangle, X } from 'lucide-react';
import { ThemedChart } from '../results/ThemedChart';
import { getParameterNotation } from '@/utils/geoNotation';
import { unitFor } from '@/utils/quantities';
import { compareRuns, PROFILE_SERIES } from './methodComparison';

const fmt = (v) => (typeof v === 'number' ? v.toLocaleString(undefined, { maximumFractionDigits: 3 }) : v ?? '–');
const label = (key, functionId) => {
    const notation = getParameterNotation(key, undefined, functionId);
    const unit = unitFor(functionId, key);
    const name = notation?.label || String(key).replace(/\s*\[[^\]]*\]\s*$/, '').replace(/_/g, ' ');
    return { name, symbol: notation?.symbol || '', unit: unit && unit !== '-' ? unit : '' };
};

const Table = ({ head, rows }) => (
    <div className="overflow-x-auto rounded-md border border-border">
        <table className="w-full border-collapse text-xs">
            <thead className="bg-surface-muted text-text-muted">
                <tr>{head.map((h, i) => <th key={i} className="px-2.5 py-1.5 text-left font-semibold whitespace-nowrap">{h}</th>)}</tr>
            </thead>
            <tbody>
                {rows.map((r, i) => (
                    <tr key={i} className="border-t border-border/50">
                        {r.map((c, j) => <td key={j} className={`px-2.5 py-1.5 ${j ? 'tabular-nums' : 'text-text-main'}`}>{c}</td>)}
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
);

// `embedded`: inside the form card's panel (no card, title or close button of its own: the panel has them).
export const MethodCompare = ({ title, runs, onClose, embedded = false }) => {
    const cmp = useMemo(() => compareRuns(runs), [runs]);
    const fid = runs[0]?.id;
    const head = ['', ...cmp.methods.map((m) => m.title)];

    return (
        <section className={embedded ? 'space-y-4' : 'rounded-md border border-primary/30 bg-surface p-4 shadow-card space-y-4'} data-method-compare>
            {embedded ? (
                <p className="text-xs text-text-muted">Latest run of each method of {title} in this session. Values are each method's own results.</p>
            ) : (
                <div className="flex items-start justify-between gap-3">
                    <div>
                        <h3 className="text-sm font-bold text-text-main">Compare methods · {title}</h3>
                        <p className="text-xs text-text-muted">Latest run of each method in this session. Values are each method's own results.</p>
                    </div>
                    <button type="button" onClick={onClose} aria-label="Close comparison" className="rounded-md p-1 text-text-muted hover:bg-surface-muted hover:text-text-main"><X size={16} /></button>
                </div>
            )}

            {cmp.inputDifferences.length > 0 && (
                <div className="flex gap-2 rounded-md border border-warning/40 bg-warning/10 px-3 py-2 text-xs text-text-main" role="alert">
                    <AlertTriangle size={14} className="mt-0.5 shrink-0 text-warning" />
                    <div>
                        <div className="font-semibold">The methods were run with different inputs, so this is not a like-for-like comparison:</div>
                        <ul className="mt-1 list-disc pl-4">
                            {cmp.inputDifferences.map((d) => (
                                <li key={d.name}><span className="font-mono">{d.name}</span>: {cmp.methods.filter((m) => m.id in d.values).map((m) => `${m.title} ${d.values[m.id]}`).join(' · ')}</li>
                            ))}
                        </ul>
                    </div>
                </div>
            )}

            {Object.entries(cmp.profiles).map(([name, lines]) => (
                <ThemedChart key={name} title={`${PROFILE_SERIES[name].label} by method`}
                    figure={{
                        data: lines.map((l) => ({ type: 'scatter', mode: 'lines', name: l.title, x: l.points.map((p) => p[1]), y: l.points.map((p) => p[0]) })),
                        layout: { xaxis: { title: { text: name } }, yaxis: { title: { text: 'Depth [m]' }, autorange: 'reversed' }, height: 420 },
                    }} />
            ))}

            {cmp.atCommonDepth.length > 0 && (
                <div className="space-y-1.5">
                    <h4 className="text-xs font-semibold text-text-main">
                        At the deepest depth all runs reach (z ≤ {fmt(cmp.atCommonDepth[0].depth)} m)
                    </h4>
                    <Table head={head} rows={cmp.atCommonDepth.map((d) => [
                        PROFILE_SERIES[d.name].label + ' [kN]',
                        ...cmp.methods.map((m) => (d.values[m.id] ? `${fmt(d.values[m.id].value)} (z = ${fmt(d.values[m.id].depth)} m)` : '–')),
                    ])} />
                    <p className="text-[11px] text-text-muted">Each value is the method's own result at its nearest computed depth at or above this level (no interpolation).</p>
                </div>
            )}

            {cmp.deepest.length > 0 && (
                <div className="space-y-1.5">
                    <h4 className="text-xs font-semibold text-text-main">At the deepest point of each run</h4>
                    <Table head={head} rows={cmp.deepest.map((d) => [
                        PROFILE_SERIES[d.name].label + ' [kN]',
                        ...cmp.methods.map((m) => (d.values[m.id] ? `${fmt(d.values[m.id].value)} (z = ${fmt(d.values[m.id].depth)} m)` : '–')),
                    ])} />
                </div>
            )}

            {cmp.scalarRows.length > 0 && (
                <div className="space-y-1.5">
                    <h4 className="text-xs font-semibold text-text-main">Results</h4>
                    <Table head={head} rows={cmp.scalarRows.map((r) => {
                        const l = label(r.key, fid);
                        return [
                            <span key="n" className={r.shared ? '' : 'text-text-muted'}>{l.name}{l.symbol ? ` (${l.symbol})` : ''}{l.unit ? ` [${l.unit}]` : ''}</span>,
                            ...cmp.methods.map((m) => fmt(r.values[m.id])),
                        ];
                    })} />
                    {cmp.scalarRows.some((r) => !r.shared) && <p className="text-[11px] text-text-muted">Greyed rows are given by one method only.</p>}
                </div>
            )}

            {!cmp.deepest.length && !cmp.scalarRows.length && (
                <p className="text-xs text-text-muted">These results have no numbers in common to compare.</p>
            )}
        </section>
    );
};

export default MethodCompare;
