/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * "Project values" above a calculation form: proposes inputs from the project ground model (soil profiles indexed by
 * python-backend/core/project) for one location and depth interval, each with its source. Nothing is applied until the
 * user ticks it; applied values merge into the form (SchemaForm patchValues) and their sources are kept for the run.
 */
import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { Database, RefreshCw, ChevronDown, FileUp } from 'lucide-react';
import { api } from '@/api/client';

const fmt = (v) => (typeof v === 'number' ? Number(v.toPrecision(5)) : v);

// `embedded`: the content only, always open, for a panel inside the form card (no card or header of its own).
// `actionsSlot`: a DOM element (the dialog title bar) the sync / import icons are rendered into; without it they
// sit in the panel.
export const ProjectValues = ({ functionId, onApply, embedded = false, actionsSlot = null }) => {
    const [expanded, setExpanded] = useState(false);
    const open = embedded || expanded;
    const [project, setProject] = useState(null);
    const [locationId, setLocationId] = useState('');
    const [zTop, setZTop] = useState('0');
    const [zBottom, setZBottom] = useState('1');
    const [result, setResult] = useState(null);
    const [picked, setPicked] = useState({});
    const [error, setError] = useState(null);
    const [busy, setBusy] = useState(false);
    const [notice, setNotice] = useState(null);
    const agsInput = useRef(null);

    const load = async (sync = false) => {
        setBusy(true);
        setError(null);
        try {
            const p = sync ? await api.projectSync() : await api.projectSummary();
            setProject(p);
            if (!locationId && p.locations?.length) setLocationId(String(p.locations[0].id));
        } catch (e) {
            setError(e.message);
        } finally {
            setBusy(false);
        }
    };

    // An AGS file's holes, strata and SPT become locations (read in the browser, parsed by the backend).
    const importAgs = async (file) => {
        if (!file) return;
        setBusy(true);
        setError(null);
        setNotice(null);
        try {
            const r = await api.projectImportAgs(await file.text(), file.name);
            setProject(r);
            if (!locationId && r.locations?.length) setLocationId(String(r.locations[0].id));
            const n = r.imported?.locations ?? 0;
            setNotice(`${file.name}: ${n} location${n === 1 ? '' : 's'} imported`
                + (r.imported?.skipped?.length ? `; skipped ${r.imported.skipped.join('; ')}` : ''));
        } catch (e) {
            setError(e.message);
        } finally {
            setBusy(false);
            if (agsInput.current) agsInput.current.value = '';
        }
    };

    const iconButton = 'inline-flex h-7 w-7 items-center justify-center rounded-md text-text-muted hover:bg-surface-muted hover:text-text-main disabled:opacity-50';
    const actions = (
        <>
            <button type="button" onClick={() => load(true)} disabled={busy} className={iconButton}
                title="Sync from saved profiles (re-read the soil profiles and CPT tables saved in GeoCore)" aria-label="Sync from saved profiles">
                <RefreshCw size={15} className={busy ? 'animate-spin' : ''} />
            </button>
            <input ref={agsInput} type="file" accept=".ags" className="hidden" onChange={(e) => importAgs(e.target.files?.[0])} />
            <button type="button" onClick={() => agsInput.current?.click()} disabled={busy} className={iconButton}
                title="Import AGS (boreholes, strata and SPT from an AGS 3.1 / 4.0 file)" aria-label="Import AGS file">
                <FileUp size={15} />
            </button>
        </>
    );

    useEffect(() => { if (open && !project) load(false); }, [open]); // eslint-disable-line react-hooks/exhaustive-deps
    useEffect(() => { setResult(null); setPicked({}); }, [functionId]);

    const find = async () => {
        setBusy(true);
        setError(null);
        try {
            const r = await api.projectPrefill({ function_id: functionId, location_id: Number(locationId),
                z_top: Number(zTop), z_bottom: Number(zBottom) });
            setResult(r);
            setPicked(Object.fromEntries(Object.keys(r.proposals).map((k) => [k, true])));
        } catch (e) {
            setError(e.message);
        } finally {
            setBusy(false);
        }
    };

    const apply = () => {
        const chosen = Object.entries(result.proposals).filter(([k]) => picked[k]);
        onApply(Object.fromEntries(chosen.map(([k, p]) => [k, fmt(p.value)])),
            Object.fromEntries(chosen.map(([k, p]) => [k, { source: p.source, inputs: p.inputs }])), Number(locationId));
    };

    const body = (
                <div className={embedded ? 'space-y-3 text-xs' : 'space-y-3 border-t border-border px-4 py-3 text-xs'} data-project-values={embedded ? '' : undefined}>
                    {error && <p className="text-error" role="alert">{error}</p>}
                    {notice && <p className="text-text-muted" role="status">{notice}</p>}
                    {project && !project.locations?.length && (
                        <p className="text-text-muted">The project has no locations yet. Sync the soil profiles saved in GeoCore or import an AGS file (icons above).</p>
                    )}
                    <div className="flex flex-wrap items-end gap-3">
                        {project?.locations?.length > 0 && (
                            <label className="flex flex-col gap-1">
                                <span className="font-semibold text-text-main">Location</span>
                                <select value={locationId} onChange={(e) => { setLocationId(e.target.value); setResult(null); }}
                                    className="rounded-md border border-border bg-background px-2 py-1 text-text-main">
                                    {project.locations.map((l) => (
                                        <option key={l.id} value={l.id}>{l.name} ({l.layers} layers, to {fmt(l.depth_m)} m)</option>
                                    ))}
                                </select>
                            </label>
                        )}
                        {project?.locations?.length > 0 && (
                            <>
                                <label className="flex flex-col gap-1"><span className="font-semibold text-text-main">From [m]</span>
                                    <input type="number" step="any" value={zTop} onChange={(e) => setZTop(e.target.value)} className="w-20 rounded-md border border-border bg-background px-2 py-1" /></label>
                                <label className="flex flex-col gap-1"><span className="font-semibold text-text-main">To [m]</span>
                                    <input type="number" step="any" value={zBottom} onChange={(e) => setZBottom(e.target.value)} className="w-20 rounded-md border border-border bg-background px-2 py-1" /></label>
                                <button type="button" onClick={find} disabled={busy} className="btn-brand h-7 rounded-md px-3 font-semibold disabled:opacity-60">Find values</button>
                            </>
                        )}
                        {actionsSlot ? createPortal(actions, actionsSlot) : <div className="ml-auto flex items-center gap-1">{actions}</div>}
                    </div>

                    {result && (
                        <div className="space-y-2">
                            {Object.keys(result.proposals).length === 0 && <p className="text-text-muted">No input of this calculation could be taken from this location and depth range.</p>}
                            {Object.entries(result.proposals).map(([field, p]) => (
                                <label key={field} className="flex items-start gap-2 rounded-md border border-border px-2.5 py-1.5">
                                    <input type="checkbox" className="mt-0.5" checked={!!picked[field]} onChange={(e) => setPicked({ ...picked, [field]: e.target.checked })} />
                                    <span className="min-w-0">
                                        <span className="font-mono text-text-main">{field}</span> = <span className="font-semibold tabular-nums">{fmt(p.value)}</span> {p.unit !== '-' ? p.unit : ''}
                                        <span className="block text-[11px] text-text-muted">{p.source}</span>
                                    </span>
                                </label>
                            ))}
                            {Object.entries(result.unavailable || {}).map(([field, why]) => (
                                <p key={field} className="text-[11px] text-text-muted"><span className="font-mono">{field}</span>: {why}</p>
                            ))}
                            {Object.keys(result.proposals).length > 0 && (
                                <button type="button" onClick={apply} disabled={!Object.values(picked).some(Boolean)}
                                    className="rounded-md border border-primary/50 px-3 py-1 font-semibold text-primary hover:bg-primary/10 disabled:opacity-50">Apply selected to the form</button>
                            )}
                        </div>
                    )}
                </div>
    );
    if (embedded) return body;

    return (
        <section className="rounded-md border border-border bg-surface shadow-card" data-project-values>
            <button type="button" onClick={() => setExpanded(!expanded)} aria-expanded={open}
                className="flex w-full items-center justify-between gap-2 px-4 py-2.5 text-left">
                <span className="flex items-center gap-2 text-sm font-semibold text-text-main"><Database size={14} className="text-primary" />Project values</span>
                <ChevronDown size={15} className={`text-text-muted transition-transform ${open ? 'rotate-180' : ''}`} />
            </button>
            {open && body}
        </section>
    );
};

export default ProjectValues;
