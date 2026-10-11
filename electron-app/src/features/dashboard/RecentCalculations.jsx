/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Home: the latest calculations from the history, as cards that show what was run - where it sits, a few of the
 * inputs and the headline results - and reopen it with those inputs and results. Values are shown exactly as
 * stored in the history; nothing is recalculated here.
 */
import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { Clock, Trash2, X, AlertTriangle, ChevronRight, History } from 'lucide-react';
import { FavoriteStar } from '@/components/common/FavoriteStar';
import { getParameterNotation } from '@/utils/geoNotation';
import { comparable } from '../calculations/methodComparison';

const SHOWN = 5; // the rest are in the History panel (header icon)

const timeAgo = (timestamp) => {
    if (!timestamp) return '';
    const mins = Math.floor((Date.now() - new Date(timestamp).getTime()) / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return days < 7 ? `${days}d ago` : new Date(timestamp).toLocaleDateString();
};

const fmt = (v) => (typeof v === 'number' ? Number(v.toPrecision(4)).toLocaleString() : String(v));

/** "Relative density" / "D_r" from a key such as "Dr [-]"; the unit from its [..] suffix. */
const describe = (key, functionId) => {
    const unitMatch = /\[([^\]]*)\]\s*$/.exec(key);
    const unit = unitMatch && unitMatch[1] !== '-' ? unitMatch[1] : '';
    const notation = getParameterNotation(key, undefined, functionId);
    const name = notation?.label || key.replace(/\s*\[[^\]]*\]\s*$/, '').replace(/_/g, ' ');
    return { name, unit };
};

/** Up to `n` simple inputs (numbers, short text, booleans) as {name, value}. */
const keyInputs = (inputs, functionId, n) => Object.entries(inputs || {})
    .filter(([k, v]) => !k.startsWith('_') && k !== 'raw_data' && (typeof v === 'number' || typeof v === 'boolean' || (typeof v === 'string' && v.trim() && v.length <= 24)))
    .slice(0, n)
    .map(([k, v]) => ({ key: k, name: describe(k, functionId).name, value: typeof v === 'boolean' ? (v ? 'yes' : 'no') : v }));

const RecentCard = ({ item, onOpen, onRemove }) => {
    const functionId = item.functionId || item.functionName;
    const failed = Boolean(item.results?.error);
    const outputs = useMemo(() => (failed ? [] : Object.entries(comparable(item.results).scalars).slice(0, 2)), [item.results, failed]);
    const inputs = useMemo(() => keyInputs(item.inputs, functionId, 3), [item.inputs, functionId]);
    const path = [item.category?.title, item.subModule?.title].filter(Boolean);

    return (
        <div role="button" tabIndex={0} onClick={() => onOpen(item)}
            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onOpen(item); } }}
            className="card-lift group relative flex flex-col gap-2.5 rounded-lg border border-border bg-surface p-3.5 text-left cursor-pointer"
            data-recent-card>
            <div className="flex items-start gap-2">
                <div className="min-w-0 flex-1">
                    <div className="text-sm font-semibold text-text-main truncate group-hover:text-primary transition-colors">{item.functionName}</div>
                    {path.length > 0 && (
                        <div className="flex items-center gap-1 text-[11px] text-text-muted truncate mt-0.5">
                            {path.map((p, i) => <React.Fragment key={i}>{i > 0 && <ChevronRight size={10} className="shrink-0" />}<span className="truncate">{p}</span></React.Fragment>)}
                        </div>
                    )}
                </div>
                <div className="flex items-center -mr-1 -mt-1">
                    <FavoriteStar id={functionId} label={item.functionName} size={13} reveal />
                    {onRemove && (
                        <button type="button" onClick={(e) => { e.stopPropagation(); onRemove(item.id); }}
                            aria-label={`Remove ${item.functionName} from recent`} title="Remove from recent"
                            className="rounded-md p-1 text-text-muted opacity-0 group-hover:opacity-100 focus-visible:opacity-100 hover:bg-surface-muted hover:text-error transition-all">
                            <X size={13} />
                        </button>
                    )}
                </div>
            </div>

            {failed ? (
                <div className="flex items-start gap-1.5 text-xs text-error">
                    <AlertTriangle size={12} className="mt-0.5 shrink-0" />
                    <span className="line-clamp-2">{String(item.results.error)}</span>
                </div>
            ) : outputs.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                    {outputs.map(([key, value]) => {
                        const d = describe(key, functionId);
                        return (
                            <span key={key} className="inline-flex items-baseline gap-1 rounded-md bg-primary/10 px-2 py-1 text-xs" title={key}>
                                <span className="text-text-muted truncate max-w-[9rem]">{d.name}</span>
                                <span className="font-mono font-semibold tabular-nums text-primary">{fmt(value)}</span>
                                {d.unit && <span className="text-text-muted">{d.unit}</span>}
                            </span>
                        );
                    })}
                </div>
            )}

            <div className="mt-auto flex items-end justify-between gap-2 pt-1 border-t border-border/60">
                <div className="min-w-0 text-[11px] text-text-muted truncate">
                    {inputs.length > 0
                        ? inputs.map((i) => <span key={i.key} className="mr-2"><span>{i.name}</span> <span className="font-mono text-text-main">{fmt(i.value)}</span></span>)
                        : 'No inputs recorded'}
                </div>
                <span className="shrink-0 text-[11px] text-text-subtle tabular-nums">{timeAgo(item.timestamp)}</span>
            </div>
        </div>
    );
};

export const RecentCalculations = ({ history = [], onOpen, onRemove, onClear, onViewAll, onRequestClear }) => {
    if (!history.length) return null;
    const shown = history.slice(0, SHOWN);

    return (
        <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15, duration: 0.3 }} data-home-recent>
            <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                <h2 className="text-lg font-semibold text-text-main flex items-center gap-2">
                    <Clock size={18} className="text-text-muted" />
                    Recent
                </h2>
                <div className="flex items-center gap-1">
                    {onViewAll && (
                        <button type="button" onClick={onViewAll} title="Open calculation history" aria-label="Open calculation history"
                            className="h-7 w-7 flex items-center justify-center rounded-md text-text-muted hover:text-text-main hover:bg-surface-muted transition-colors">
                            <History size={15} />
                        </button>
                    )}
                    {(onClear || onRequestClear) && (
                        <button type="button" onClick={(e) => { e.stopPropagation(); (onRequestClear || onClear)(); }}
                            title="Clear recent calculations" aria-label="Clear recent calculations"
                            className="h-7 w-7 flex items-center justify-center rounded-md text-text-muted hover:text-error hover:bg-error/10 transition-colors">
                            <Trash2 size={15} />
                        </button>
                    )}
                </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {shown.map((item, idx) => <RecentCard key={item.id || idx} item={item} onOpen={onOpen} onRemove={onRemove} />)}
            </div>
        </motion.section>
    );
};

export default RecentCalculations;
