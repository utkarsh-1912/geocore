/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * The calculation form header, from the calculation catalogue:
 *
 * - CalculationMeta (under the title, SchemaForm `toolbar`): the method's verification status and standards.
 * - CalculationMenu (an icon in the header, SchemaForm `actions`): "More options" - the calculation's other
 *   methods (picking one opens that method's own form, which runs exactly as before) and the form's tools -
 *   project values, the phase-relation solver, the method comparison - each opening one panel inside the form
 *   card (SchemaForm `panel`, wrapped in ToolPanel), at most one at a time.
 */
import React, { useEffect, useRef, useState } from 'react';
import { GitCompare, Database, Calculator, MoreHorizontal, Check, X } from 'lucide-react';
import { catalogueEntry } from '@/config/navigation';
import { api } from '@/api/client';
import { CALC_STATUS } from './calcStatus';

const TOOL_LABELS = { project: 'Project values', solver: 'Solve for any phase quantity', compare: 'Compare methods' };

const tools = (functionId, runsCount) => {
    const entry = catalogueEntry(functionId);
    const list = [{ id: 'project', label: TOOL_LABELS.project, icon: Database, hint: 'Fill inputs from the project ground model' }];
    if (entry?.calculation === 'phase_relations') {
        list.push({ id: 'solver', label: TOOL_LABELS.solver, icon: Calculator, hint: 'Chain the phase relations from what you know' });
    }
    if (entry && entry.methods.length > 1) {
        list.push({ id: 'compare', label: TOOL_LABELS.compare, icon: GitCompare,
            hint: runsCount >= 2 ? `Every method on the same inputs; ${runsCount} run in this session` : 'Every method on the same inputs' });
    }
    return list;
};

const MenuHeading = ({ children }) => (
    <div className="px-3 pt-2.5 pb-1 text-[10px] font-semibold uppercase tracking-wider text-text-muted">{children}</div>
);

/** "More options": the calculation's methods and the form's tools, behind one icon. */
export const CalculationMenu = ({ functionId, onSelectMethod, runsCount = 0, panel, onPanel }) => {
    const [open, setOpen] = useState(false);
    // "Auto": the method that fits the saved data, with the reason (only for methods that list their data).
    const [suggestion, setSuggestion] = useState(null);
    const ref = useRef(null);
    useEffect(() => {
        if (!open) return undefined;
        const onDown = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
        const onKey = (e) => { if (e.key === 'Escape') setOpen(false); };
        document.addEventListener('mousedown', onDown);
        document.addEventListener('keydown', onKey);
        return () => { document.removeEventListener('mousedown', onDown); document.removeEventListener('keydown', onKey); };
    }, [open]);

    const entry = catalogueEntry(functionId);
    const methods = entry?.methods || [];
    const list = tools(functionId, runsCount);
    const suggests = methods.length > 1 && methods.some((m) => (m.data || []).length > 0);
    const shown = suggestion?.calculation === entry?.calculation ? suggestion : null;

    const toggle = () => {
        if (!open && suggests) {
            api.suggestMethod(entry.calculation)
                .then((s) => setSuggestion({ ...s, calculation: entry.calculation }))
                .catch(() => setSuggestion(null));
        }
        setOpen(!open);
    };

    return (
        <div ref={ref} className="relative" data-calculation-menu>
            <button type="button" onClick={toggle} aria-haspopup="menu" aria-expanded={open}
                aria-label="More options" title="More options"
                className={`inline-flex h-8 w-8 items-center justify-center rounded-md border transition-colors ${open || panel
                    ? 'border-primary/50 bg-primary/10 text-primary'
                    : 'border-border bg-surface text-text-muted hover:border-primary/40 hover:text-text-main'}`}>
                <MoreHorizontal size={16} />
            </button>
            {open && (
                <div role="menu" className="absolute right-0 z-50 mt-1.5 w-72 overflow-hidden rounded-md border border-border bg-surface pb-1.5 text-xs shadow-pop">
                    {methods.length > 1 && (
                        <>
                            <MenuHeading>Method · {entry.title}</MenuHeading>
                            {shown && (
                                <p className="px-3 pb-1.5 text-[11px] text-text-muted" data-method-suggestion>
                                    Suggested: <span className="font-medium text-text-main">{shown.label}</span> ({shown.reason})
                                </p>
                            )}
                            <div className="max-h-56 overflow-y-auto">
                                {methods.map((m) => (
                                    <button key={m.id} type="button" role="menuitemradio" aria-checked={m.id === functionId}
                                        onClick={() => { setOpen(false); if (m.id !== functionId) onSelectMethod(m.id); }}
                                        className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-text-main hover:bg-surface-muted">
                                        <Check size={13} className={m.id === functionId ? 'text-primary' : 'invisible'} />
                                        <span className="min-w-0 truncate">{m.title}</span>
                                        {shown && shown.method === (m.method || m.id) && (
                                            <span className="ml-auto shrink-0 rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-semibold text-primary">Suggested</span>
                                        )}
                                    </button>
                                ))}
                            </div>
                            <div className="my-1.5 border-t border-border" />
                        </>
                    )}
                    <MenuHeading>Tools</MenuHeading>
                    {list.map((t) => {
                        const Icon = t.icon;
                        return (
                            <button key={t.id} type="button" role="menuitemcheckbox" aria-checked={panel === t.id} disabled={t.disabled}
                                onClick={() => { setOpen(false); onPanel(panel === t.id ? null : t.id); }}
                                className="flex w-full items-start gap-2 px-3 py-1.5 text-left hover:bg-surface-muted disabled:opacity-40 disabled:pointer-events-none">
                                <Icon size={14} className={`mt-0.5 shrink-0 ${panel === t.id ? 'text-primary' : 'text-text-muted'}`} />
                                <span className="min-w-0">
                                    <span className={`block font-medium ${panel === t.id ? 'text-primary' : 'text-text-main'}`}>{t.label}</span>
                                    <span className="block text-[11px] text-text-muted">{t.hint}</span>
                                </span>
                            </button>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

/**
 * A tool in a dialog over the form (project values, method comparison): Esc or a click outside closes it.
 * ``children`` may be a function of the title bar's action slot (a DOM element), for tools that put icon buttons
 * beside the heading.
 */
export const ToolModal = ({ tool, onClose, children }) => {
    const [slot, setSlot] = useState(null);
    useEffect(() => {
        const onKey = (e) => { if (e.key === 'Escape') onClose(); };
        document.addEventListener('keydown', onKey);
        return () => document.removeEventListener('keydown', onKey);
    }, [onClose]);
    return (
        <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/40 p-4 sm:p-6" onMouseDown={onClose}
            role="dialog" aria-modal="true" aria-label={TOOL_LABELS[tool] || tool} data-tool-modal={tool}>
            <div className="mt-10 flex max-h-[85vh] w-full max-w-3xl flex-col rounded-md border border-border bg-surface shadow-pop"
                onMouseDown={(e) => e.stopPropagation()}>
                <div className="flex items-center justify-between gap-2 border-b border-border px-5 py-3">
                    <h2 className="text-sm font-semibold text-text-main">{TOOL_LABELS[tool] || tool}</h2>
                    <div className="flex items-center gap-1">
                        <div ref={setSlot} className="flex items-center gap-1" data-tool-modal-actions />
                        <button type="button" onClick={onClose} aria-label="Close" title="Close (Esc)"
                            className="inline-flex h-7 w-7 items-center justify-center rounded-md text-text-muted hover:bg-surface-muted hover:text-text-main">
                            <X size={16} />
                        </button>
                    </div>
                </div>
                <div className="min-h-0 overflow-y-auto px-5 py-4">{typeof children === 'function' ? children(slot) : children}</div>
            </div>
        </div>
    );
};

/** A tool's panel inside the form card: its name and a close button above the content. */
export const ToolPanel = ({ tool, onClose, children }) => (
    <div data-tool-panel={tool}>
        <div className="mb-3 flex items-center justify-between gap-2">
            <span className="text-sm font-semibold text-text-main">{TOOL_LABELS[tool] || tool}</span>
            <button type="button" onClick={onClose} aria-label="Close panel" title="Close"
                className="rounded-md p-1 text-text-muted hover:bg-surface-muted hover:text-text-main">
                <X size={15} />
            </button>
        </div>
        {children}
    </div>
);

export const CalculationMeta = ({ functionId }) => {
    const entry = catalogueEntry(functionId);
    if (!entry) return null;
    const current = entry.methods.find((m) => m.id === functionId) || {};
    const status = CALC_STATUS[current.status];
    const multi = entry.methods.length > 1;
    if (!multi && !status && !(current.standards || []).length) return null;

    return (
        <div className="space-y-1" data-calculation-toolbar={entry.calculation}>
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-text-muted">
                {multi && <span>{entry.title} · method {entry.methods.findIndex((m) => m.id === functionId) + 1} of {entry.methods.length}</span>}
                {status && (
                    <span title={current.status_note || (current.benchmarks?.length ? `Checked against: ${current.benchmarks.join('; ')}` : status.label)}
                        className={`inline-flex items-center gap-1 font-medium ${status.className}`}>
                        <status.Icon size={13} />{status.label}
                    </span>
                )}
                {(current.standards || []).length > 0 && <span>{current.standards.join(' · ')}</span>}
            </div>
            {current.status_note && status && <p className="text-[11px] text-text-muted">{current.status_note}</p>}
        </div>
    );
};
