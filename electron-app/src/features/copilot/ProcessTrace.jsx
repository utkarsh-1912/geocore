/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * "What GeoAI did" for one turn: a live checklist of the agent's stages while it works, kept on the
 * finished message behind a toggle (collapsed by default once the answer is written).
 */
import React, { useEffect, useRef, useState } from 'react';
import { Check, ChevronRight, Loader2, Square, TriangleAlert } from 'lucide-react';
import { describeStage, formatElapsed } from './geoaiStream';

const formatParam = (value) => {
    if (value == null) return '—';
    if (typeof value === 'number') return Number.isInteger(value) ? String(value) : String(Number(value.toPrecision(6)));
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
};

const StepIcon = ({ state }) => {
    if (state === 'active') return <Loader2 size={13} className="animate-spin text-primary" />;
    if (state === 'failed') return <TriangleAlert size={13} className="text-amber-400" />;
    if (state === 'stopped') return <Square size={9} className="fill-current text-text-muted" />;
    return <Check size={13} strokeWidth={3} className="text-primary" />;
};

const Step = ({ step, now, isLast }) => {
    const { title, hint } = describeStage(step.stage);
    const state = step.failed === 'error' ? 'failed' : step.failed === 'cancelled' ? 'stopped' : step.endedAt == null ? 'active' : 'done';
    const seconds = ((step.endedAt ?? now) - step.startedAt) / 1000;
    const params = step.parameters && typeof step.parameters === 'object' ? Object.entries(step.parameters) : [];

    return (
        <li className="relative flex gap-3 pb-3 last:pb-0">
            {!isLast && <span className="absolute left-[9px] top-5 bottom-0 w-px bg-gradient-to-b from-primary/40 to-primary/5" aria-hidden />}
            <span
                className={`relative z-10 mt-0.5 flex h-[19px] w-[19px] shrink-0 items-center justify-center rounded-full border ${
                    state === 'active'
                        ? 'border-primary/60 bg-primary/10 shadow-[0_0_12px_-2px_var(--glow-brand)]'
                        : 'border-primary/30 bg-primary/10'
                }`}
            >
                <StepIcon state={state} />
            </span>
            <div className="min-w-0 flex-1">
                <div className="flex items-baseline justify-between gap-3">
                    <span className={`text-xs font-semibold ${state === 'active' ? 'text-text-main' : 'text-text-main/90'}`}>{title}</span>
                    <span className="shrink-0 font-mono text-[10px] tabular-nums text-text-subtle">
                        {state === 'active' || seconds >= 1 ? formatElapsed(seconds) : '<1s'}
                    </span>
                </div>
                {hint && <p className="mt-0.5 text-[11px] leading-snug text-text-muted">{hint}</p>}
                {params.length > 0 && (
                    <dl className="mt-2 grid grid-cols-[auto_1fr] gap-x-3 gap-y-0.5 rounded-md border border-border/70 bg-background/60 px-2.5 py-2 font-mono text-[10.5px]">
                        {params.map(([key, value]) => (
                            <React.Fragment key={key}>
                                <dt className="text-text-subtle">{key}</dt>
                                <dd className="truncate text-text-main" title={formatParam(value)}>{formatParam(value)}</dd>
                            </React.Fragment>
                        ))}
                    </dl>
                )}
            </div>
        </li>
    );
};

/**
 * `steps`: recorded stages (see createTraceRecorder). `active`: the turn is still running.
 * `totalMs`: final duration for a finished turn. `elapsedSeconds`: live timer (re-renders each second).
 */
export const ProcessTrace = ({ steps = [], active = false, totalMs = null, outcome = 'done', elapsedSeconds = 0 }) => {
    const [open, setOpen] = useState(active);
    const touched = useRef(false);
    const [now, setNow] = useState(() => Date.now());

    useEffect(() => { setNow(Date.now()); }, [elapsedSeconds, steps]);
    // Collapse when the answer is done, unless the user has already opened/closed it themselves.
    useEffect(() => {
        if (!touched.current) setOpen(active);
    }, [active]);

    if (!active && steps.length === 0) return null;

    const current = steps.length ? describeStage(steps[steps.length - 1].stage).title : 'Getting started';
    const total = active ? formatElapsed(elapsedSeconds) : formatElapsed((totalMs ?? 0) / 1000);
    const heading = active
        ? 'Working'
        : outcome === 'cancelled' ? 'Stopped after' : outcome === 'error' ? 'Failed after' : 'Processed in';

    return (
        <div className="mb-2 overflow-hidden rounded-md border border-primary/20 bg-gradient-to-br from-primary/[0.06] via-transparent to-primary/[0.04]">
            <button
                type="button"
                onClick={() => { touched.current = true; setOpen((v) => !v); }}
                aria-expanded={open}
                className="flex w-full items-center gap-2.5 px-3 py-2 text-left transition-colors hover:bg-primary/[0.05]"
            >
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10">
                    {active
                        ? <Loader2 size={12} className="animate-spin text-primary" />
                        : outcome === 'done' ? <Check size={12} strokeWidth={3} className="text-primary" /> : <TriangleAlert size={12} className="text-amber-400" />}
                </span>
                <span className="min-w-0 flex-1 truncate text-xs">
                    <span className="font-semibold text-text-main">{heading} {total}</span>
                    <span className="text-text-muted"> · {active ? current : `${steps.length} ${steps.length === 1 ? 'step' : 'steps'}`}</span>
                </span>
                <ChevronRight size={14} className={`shrink-0 text-text-muted transition-transform duration-200 ${open ? 'rotate-90' : ''}`} />
            </button>
            {open && (
                <ol className="border-t border-primary/10 px-3 pb-3 pt-3">
                    {steps.length === 0 && <li className="text-[11px] text-text-muted">Waiting for the first step…</li>}
                    {steps.map((step, i) => (
                        <Step key={`${i}-${step.stage}`} step={step} now={now} isLast={i === steps.length - 1} />
                    ))}
                </ol>
            )}
        </div>
    );
};
