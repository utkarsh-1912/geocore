/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Form settings: a dedicated side panel for customising a calculation form. Lists every field of the
 * current function; choosing one (here, or by clicking it in the form) opens its editor in place.
 * Changes are saved per field through the same override store as before (`onSave`); an empty
 * override resets a field to the schema default.
 */
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, ChevronRight, FileText, ImagePlus, RotateCcw, Save, Search, SlidersHorizontal, Trash2, Undo2, X } from 'lucide-react';
import { Tooltip } from '../../components/ui/Tooltip';

const REGEX_PATTERNS = [
    { label: 'None', value: '' },
    { label: 'Positive Number', value: '^\\d*\\.?\\d+$' },
    { label: 'Integer', value: '^-?\\d+$' },
    { label: 'Email', value: '^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$' },
    { label: 'URL', value: '^(https?|ftp):\\/\\/[^\\s/$.?#].[^\\s]*$' },
    { label: 'Phone', value: '^\\+?[1-9]\\d{1,14}$' },
    { label: 'Alphanumeric', value: '^[a-zA-Z0-9]+$' },
];

const DISPLAY_TYPES = [
    { value: 'auto', label: 'Auto (from schema)' },
    { value: 'column_multi_select', label: 'Multi-parameter tag picker (profile)' },
    { value: 'column_select', label: 'Single column dropdown (profile)' },
    { value: 'dropdown', label: 'Custom options dropdown' },
    { value: 'text', label: 'Text input' },
    { value: 'number', label: 'Numeric input' },
];

const CONTROL = 'w-full rounded-md border border-border-strong bg-input px-3 py-2 text-sm text-text-main placeholder:text-text-subtle transition-all focus:border-primary/70 focus:outline-none focus:ring-4 focus:ring-primary/15';

const Label = ({ children }) => <label className="mb-1 block text-[11px] font-semibold uppercase tracking-wider text-text-subtle">{children}</label>;

const FieldEditor = ({ field, hasOverride, onSave, onReset, onUploadImage, onRemoveImage }) => {
    const [data, setData] = useState({});

    useEffect(() => {
        setData({
            label: field.label || '',
            unit: field.unit || '',
            placeholder: field.placeholder || '',
            description: field.description || '',
            displayType: field.displayType || 'auto',
            allowedOptions: Array.isArray(field.allowedOptions) ? field.allowedOptions.join(', ') : (field.allowedOptions || ''),
            validationRegex: field.validationRegex || '',
        });
    }, [field.name]); // eslint-disable-line react-hooks/exhaustive-deps

    const set = (name) => (e) => setData((prev) => ({ ...prev, [name]: e.target.value }));
    const regexPreset = REGEX_PATTERNS.some((p) => p.value === data.validationRegex) ? data.validationRegex : 'custom';

    return (
        <div className="space-y-3 border-t border-border/70 bg-surface-muted/40 px-3.5 py-3.5">
            <div>
                <Label>Label</Label>
                <input className={CONTROL} value={data.label || ''} onChange={set('label')} />
            </div>
            <div className="grid grid-cols-2 gap-3">
                <div>
                    <Label>Unit</Label>
                    <input className={CONTROL} value={data.unit || ''} onChange={set('unit')} />
                </div>
                <div>
                    <Label>Placeholder</Label>
                    <input className={CONTROL} value={data.placeholder || ''} onChange={set('placeholder')} />
                </div>
            </div>
            <div>
                <Label>Help text (HTML supported)</Label>
                <textarea className={CONTROL} rows={3} value={data.description || ''} onChange={set('description')} placeholder="Shown next to the field…" />
            </div>
            <div>
                <Label>Input type</Label>
                <select className={CONTROL} value={data.displayType || 'auto'} onChange={set('displayType')}>
                    {DISPLAY_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
            </div>
            {data.displayType === 'dropdown' && (
                <div>
                    <Label>Options (comma-separated)</Label>
                    <input className={CONTROL} value={data.allowedOptions || ''} onChange={set('allowedOptions')} placeholder="Option A, Option B" />
                </div>
            )}
            <div>
                <Label>Validation pattern</Label>
                <select
                    className={`${CONTROL} mb-2`}
                    value={regexPreset}
                    onChange={(e) => e.target.value !== 'custom' && setData((prev) => ({ ...prev, validationRegex: e.target.value }))}
                >
                    {REGEX_PATTERNS.map((p) => <option key={p.label} value={p.value}>{p.label}</option>)}
                    <option value="custom">Custom…</option>
                </select>
                <input className={`${CONTROL} font-mono`} value={data.validationRegex || ''} onChange={set('validationRegex')} placeholder="e.g. ^[0-9]+$" />
            </div>

            <div>
                <Label>Reference image</Label>
                <div className="flex items-center gap-3">
                    {field.imageUrl ? (
                        <img src={field.imageUrl} alt="Reference" className="h-12 w-12 rounded-md border border-border object-cover" />
                    ) : (
                        <span className="flex h-12 w-12 items-center justify-center rounded-md border border-dashed border-border-strong text-text-subtle">
                            <ImagePlus size={16} />
                        </span>
                    )}
                    <Tooltip content={field.imageUrl ? 'Replace image' : 'Upload image'} position="top">
                        <label className="flex h-9 w-9 cursor-pointer items-center justify-center rounded-md border border-border text-text-muted transition-colors hover:border-primary/40 hover:text-primary">
                            <ImagePlus size={15} />
                            <input type="file" accept="image/*" className="hidden" aria-label="Upload reference image" onChange={(e) => { onUploadImage?.(e.target.files[0]); e.target.value = ''; }} />
                        </label>
                    </Tooltip>
                    {field.imageUrl && (
                        <Tooltip content="Remove image" position="top">
                            <button type="button" onClick={onRemoveImage} aria-label="Remove reference image" className="flex h-9 w-9 items-center justify-center rounded-md border border-border text-text-muted transition-colors hover:border-error/40 hover:text-error">
                                <Trash2 size={15} />
                            </button>
                        </Tooltip>
                    )}
                </div>
            </div>

            <div className="flex items-center gap-2 pt-1">
                <button
                    type="button"
                    onClick={() => onSave(data)}
                    className="btn-brand flex flex-1 items-center justify-center gap-2 rounded-md py-2 text-sm font-semibold"
                >
                    <Check size={15} /> Apply
                </button>
                <Tooltip content="Reset to schema default" position="top">
                    <button
                        type="button"
                        onClick={onReset}
                        disabled={!hasOverride}
                        aria-label="Reset field to schema default"
                        className="flex h-9 w-9 items-center justify-center rounded-md border border-border text-text-muted transition-colors hover:border-error/40 hover:text-error disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:border-border disabled:hover:text-text-muted"
                    >
                        <RotateCcw size={15} />
                    </button>
                </Tooltip>
            </div>
        </div>
    );
};

const GuideEditor = ({ guide }) => (
    <div className="flex min-h-0 flex-1 flex-col gap-3 p-3">
        <p className="px-1 text-[11px] leading-snug text-text-muted">
            Usage notes shown in the Guide for this calculation. HTML and plain text are supported.
        </p>
        <textarea
            value={guide.value}
            onChange={(e) => guide.onChange(e.target.value)}
            spellCheck={false}
            placeholder="Enter HTML or text documentation…"
            className="min-h-[18rem] w-full flex-1 resize-none rounded-md border border-border-strong bg-input p-3 font-mono text-xs leading-relaxed text-text-main placeholder:text-text-subtle focus:border-primary/70 focus:outline-none focus:ring-4 focus:ring-primary/15"
        />
        <div className="flex items-center gap-2">
            <button
                type="button"
                onClick={guide.onSave}
                disabled={!guide.dirty}
                className="btn-brand flex flex-1 items-center justify-center gap-2 rounded-md py-2 text-sm font-semibold disabled:opacity-50"
            >
                <Save size={15} /> Save guide
            </button>
            <Tooltip content="Discard unsaved changes" position="top">
                <button type="button" onClick={guide.onRevert} disabled={!guide.dirty} aria-label="Discard unsaved changes" className="flex h-9 w-9 items-center justify-center rounded-md border border-border text-text-muted transition-colors hover:border-primary/40 hover:text-primary disabled:cursor-not-allowed disabled:opacity-40">
                    <Undo2 size={15} />
                </button>
            </Tooltip>
            <Tooltip content="Reset to default template" position="top">
                <button type="button" onClick={guide.onResetTemplate} aria-label="Reset to default template" className="flex h-9 w-9 items-center justify-center rounded-md border border-border text-text-muted transition-colors hover:border-error/40 hover:text-error">
                    <RotateCcw size={15} />
                </button>
            </Tooltip>
        </div>
    </div>
);

export const FormSettingsPanel = ({ isOpen, onClose, functionName, fields, overrides, selectedName, onSelect, onSave, onUploadImage, guide }) => {
    const [query, setQuery] = useState('');
    const [tab, setTab] = useState('fields'); // 'fields' | 'guide'
    const panelRef = useRef(null);

    useEffect(() => {
        if (!isOpen) return undefined;
        const onKey = (e) => { if (e.key === 'Escape') onClose(); };
        // Close on a click elsewhere, except on what the panel works with: the form's field pickers
        // and its own toggle (marked data-form-settings-keep), and dialogs opened on top of it.
        const onPointerDown = (e) => {
            const target = e.target;
            if (!(target instanceof Element) || panelRef.current?.contains(target)) return;
            if (target.closest('[data-form-settings-keep], [role="dialog"], [aria-modal="true"]')) return;
            onClose();
        };
        document.addEventListener('keydown', onKey);
        document.addEventListener('pointerdown', onPointerDown);
        return () => {
            document.removeEventListener('keydown', onKey);
            document.removeEventListener('pointerdown', onPointerDown);
        };
    }, [isOpen, onClose]);

    const fnOverrides = overrides?.[functionName] || {};
    const hasOverride = (name) => Object.keys(fnOverrides[name] || {}).length > 0;
    const customisedCount = fields.filter((f) => hasOverride(f.name)).length;

    const visible = useMemo(() => {
        const q = query.trim().toLowerCase();
        return q ? fields.filter((f) => `${f.label || ''} ${f.name}`.toLowerCase().includes(q)) : fields;
    }, [fields, query]);

    const resetAll = () => fields.forEach((f) => hasOverride(f.name) && onSave(functionName, f.name, {}));

    // Portal: the page container is transformed, which would otherwise anchor `fixed` to it.
    return createPortal(
        <AnimatePresence>
            {isOpen && (
                <motion.aside
                    ref={panelRef}
                    initial={{ x: 40, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: 40, opacity: 0 }}
                    transition={{ type: 'spring', damping: 28, stiffness: 320 }}
                    className="hairline-top fixed bottom-0 right-0 top-13 z-40 flex w-[22rem] max-w-[92vw] flex-col border-l border-border bg-surface shadow-pop"
                    aria-label="Form settings"
                >
                    <div className="flex shrink-0 items-center gap-3 border-b border-border px-4 py-3">
                        <span className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/12 text-primary ring-1 ring-primary/20">
                            <SlidersHorizontal size={16} />
                        </span>
                        <div className="min-w-0 flex-1">
                            <h3 className="text-sm font-semibold leading-tight text-text-main">{tab === 'guide' ? 'Guide' : 'Form settings'}</h3>
                            <p className="truncate text-[11px] text-text-muted" title={functionName}>{functionName}</p>
                        </div>
                        {guide && (
                            <div className="flex rounded-md border border-border-strong bg-input p-0.5" role="tablist" aria-label="Settings sections">
                                {[['fields', SlidersHorizontal, 'Field settings'], ['guide', FileText, 'Edit guide']].map(([key, Icon, tip]) => (
                                    <Tooltip key={key} content={tip} position="bottom">
                                        <button
                                            type="button"
                                            role="tab"
                                            aria-selected={tab === key}
                                            aria-label={tip}
                                            onClick={() => setTab(key)}
                                            className={`flex h-7 w-8 items-center justify-center rounded-md transition-all ${tab === key ? 'btn-brand' : 'text-text-muted hover:text-text-main'}`}
                                        >
                                            <Icon size={14} />
                                        </button>
                                    </Tooltip>
                                ))}
                            </div>
                        )}
                        <Tooltip content="Close" position="bottom">
                            <button type="button" onClick={onClose} aria-label="Close settings" className="rounded-md p-1.5 text-text-muted transition-colors hover:bg-surface-muted hover:text-text-main">
                                <X size={16} />
                            </button>
                        </Tooltip>
                    </div>

                    {tab === 'guide' && guide ? <GuideEditor guide={guide} /> : (<>
                    <div className="shrink-0 border-b border-border px-4 py-2.5">
                        <div className="relative">
                            <Search size={14} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-text-subtle" />
                            <input
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="Find a field…"
                                className="w-full rounded-md border border-border-strong bg-input py-1.5 pl-8 pr-3 text-sm text-text-main placeholder:text-text-subtle focus:border-primary/70 focus:outline-none focus:ring-4 focus:ring-primary/15"
                            />
                        </div>
                    </div>

                    <ul className="flex-1 space-y-1.5 overflow-y-auto p-3">
                        {visible.length === 0 && <li className="px-2 py-6 text-center text-xs text-text-muted">No matching fields.</li>}
                        {visible.map((field) => {
                            const open = selectedName === field.name;
                            const custom = hasOverride(field.name);
                            return (
                                <li key={field.name} className={`overflow-hidden rounded-md border transition-colors ${open ? 'border-primary/40 bg-background' : 'border-border bg-background/50 hover:border-border-strong'}`}>
                                    <button
                                        type="button"
                                        onClick={() => onSelect(open ? null : field)}
                                        aria-expanded={open}
                                        className="flex w-full items-center gap-2.5 px-3.5 py-2.5 text-left"
                                    >
                                        <span className="min-w-0 flex-1">
                                            <span className="block truncate text-sm font-medium text-text-main">{fnOverrides[field.name]?.label || field.label || field.name}</span>
                                            <span className="block truncate font-mono text-[10.5px] text-text-subtle">{field.name}</span>
                                        </span>
                                        {custom && <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-primary shadow-[0_0_8px_var(--glow-brand)]" title="Customised" />}
                                        <ChevronRight size={14} className={`shrink-0 text-text-muted transition-transform duration-200 ${open ? 'rotate-90' : ''}`} />
                                    </button>
                                    {open && (
                                        <FieldEditor
                                            field={{ ...field, ...(fnOverrides[field.name] || {}) }}
                                            hasOverride={custom}
                                            onSave={(data) => onSave(functionName, field.name, { ...(fnOverrides[field.name] || {}), ...data })}
                                            onReset={() => onSave(functionName, field.name, {})}
                                            onUploadImage={(file) => onUploadImage?.(file, field.name)}
                                            onRemoveImage={() => onSave(functionName, field.name, { ...(fnOverrides[field.name] || {}), imageUrl: '' })}
                                        />
                                    )}
                                </li>
                            );
                        })}
                    </ul>

                    <div className="flex shrink-0 items-center justify-between gap-2 border-t border-border bg-surface-muted/40 px-4 py-2.5 text-[11px] text-text-muted">
                        <span>{customisedCount === 0 ? 'No customised fields' : `${customisedCount} customised`}</span>
                        <button
                            type="button"
                            onClick={resetAll}
                            disabled={customisedCount === 0}
                            className="flex items-center gap-1.5 rounded-md px-2 py-1 font-medium transition-colors hover:bg-error/10 hover:text-error disabled:opacity-40 disabled:hover:bg-transparent disabled:hover:text-text-muted"
                        >
                            <RotateCcw size={12} /> Reset all
                        </button>
                    </div>
                    </>)}
                </motion.aside>
            )}
        </AnimatePresence>,
        document.body
    );
};
