/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * The calculations saved to the project: when, what, whether still current (a changed or removed input makes a run
 * out of date, also through the runs it took values from), and their calculation reports as printable HTML files.
 */
import React, { useEffect, useState } from 'react';
import { X, FileText, AlertTriangle, Trash2, FileDown, BadgeCheck } from 'lucide-react';
import { api } from '@/api/client';
import { catalogueEntry } from '@/config/navigation';
import { downloadHtml, saveReportPdf } from '@/utils/downloadHtml';

export const ProjectRuns = ({ isOpen, onClose }) => {
    const [runs, setRuns] = useState(null);
    const [error, setError] = useState(null);
    const [notice, setNotice] = useState(null);
    // The run being signed off, and the reviewer name (remembered on this computer for the next sign-off).
    const [signing, setSigning] = useState(null);
    const [reviewer, setReviewer] = useState(() => { try { return localStorage.getItem('geocore-reviewer') || ''; } catch { return ''; } });
    const [note, setNote] = useState('');

    const load = () => api.projectRuns().then(setRuns).catch((e) => setError(e.message));
    useEffect(() => { if (isOpen) load(); }, [isOpen]);
    if (!isOpen) return null;

    const report = async (id) => {
        try { downloadHtml(await api.projectRunReport(id), `geocore-run-${id}-report.html`); } catch (e) { setError(e.message); }
    };
    const projectReport = async () => {
        try { downloadHtml(await api.projectReport(), 'geocore-project-report.html'); } catch (e) { setError(e.message); }
    };
    const remove = async (id) => { await api.projectDeleteRun(id).catch((e) => setError(e.message)); load(); };
    const pdf = async (getHtml, name) => {
        try {
            const saved = await saveReportPdf(await getHtml(), name);
            if (saved && saved !== 'print') setNotice(`Saved ${saved}`);
        } catch (e) { setError(e.message); }
    };
    const signOff = async (id) => {
        try {
            await api.projectReviewRun(id, reviewer, note);
            try { localStorage.setItem('geocore-reviewer', reviewer); } catch { /* per-computer convenience only */ }
            setSigning(null);
            setNote('');
            load();
        } catch (e) { setError(e.message); }
    };
    const withdraw = async (id) => { await api.projectClearReview(id).catch((e) => setError(e.message)); load(); };

    return (
        <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/40 p-6" role="dialog" aria-label="Project calculations" onClick={onClose}>
            <div className="mt-10 w-full max-w-3xl rounded-md border border-border bg-surface shadow-pop" onClick={(e) => e.stopPropagation()}>
                <div className="flex items-center justify-between border-b border-border px-4 py-3">
                    <h2 className="text-sm font-bold text-text-main">Project calculations</h2>
                    <div className="flex items-center gap-2">
                        <button type="button" onClick={projectReport} disabled={!runs?.length}
                            className="inline-flex items-center gap-1 rounded-md border border-border px-2 py-1 text-xs font-semibold text-text-main hover:border-primary/50 disabled:opacity-50">
                            <FileText size={12} />Project report</button>
                        <button type="button" onClick={() => pdf(api.projectReport, 'geocore-project-report.pdf')} disabled={!runs?.length}
                            className="inline-flex items-center gap-1 rounded-md border border-border px-2 py-1 text-xs font-semibold text-text-main hover:border-primary/50 disabled:opacity-50">
                            <FileDown size={12} />PDF</button>
                        <button type="button" onClick={onClose} aria-label="Close" className="rounded-md p-1 text-text-muted hover:bg-surface-muted"><X size={16} /></button>
                    </div>
                </div>
                <div className="max-h-[70vh] overflow-y-auto p-3 space-y-2 text-xs">
                    {error && <p className="text-error" role="alert">{error}</p>}
                    {notice && <p className="text-text-muted" role="status">{notice}</p>}
                    {runs && runs.length === 0 && <p className="p-3 text-text-muted">No calculations saved yet. Use "Save to project" under a result.</p>}
                    {(runs || []).map((r) => (
                        <div key={r.id} className={`rounded-md border px-3 py-2 ${r.stale.length ? 'border-warning/50 bg-warning/5' : 'border-border'}`} data-run={r.id}>
                            <div className="flex items-center justify-between gap-2">
                                <div className="min-w-0">
                                    <span className="font-semibold text-text-main">#{r.id} {catalogueEntry(r.function_id)?.title || r.function_id}</span>
                                    <span className="text-text-muted"> · {catalogueEntry(r.function_id)?.methods.find((m) => m.id === r.function_id)?.title || ''}</span>
                                    <span className="block text-[11px] text-text-muted">{new Date(r.created_at * 1000).toLocaleString()} · {r.status || 'unverified'}{r.inputs_from_project.length ? ` · ${r.inputs_from_project.length} input(s) from the project` : ''}</span>
                                </div>
                                <div className="flex shrink-0 items-center gap-1">
                                    <button type="button" onClick={() => report(r.id)} className="inline-flex items-center gap-1 rounded-md border border-border px-2 py-0.5 hover:border-primary/50"><FileText size={11} />Report</button>
                                    <button type="button" onClick={() => pdf(() => api.projectRunReport(r.id), `geocore-run-${r.id}-report.pdf`)} className="inline-flex items-center gap-1 rounded-md border border-border px-2 py-0.5 hover:border-primary/50"><FileDown size={11} />PDF</button>
                                    {!r.review && (
                                        <button type="button" onClick={() => setSigning(signing === r.id ? null : r.id)} className="inline-flex items-center gap-1 rounded-md border border-border px-2 py-0.5 hover:border-primary/50"><BadgeCheck size={11} />Sign off</button>
                                    )}
                                    <button type="button" onClick={() => remove(r.id)} aria-label={`Delete run ${r.id}`} className="rounded-md p-1 text-text-muted hover:text-error"><Trash2 size={12} /></button>
                                </div>
                            </div>
                            {r.review && (
                                <div className="mt-1 flex flex-wrap items-center gap-1.5 text-[11px] text-text-main">
                                    <BadgeCheck size={12} className={r.stale.length ? 'text-warning' : 'text-success'} />
                                    <span>Checked by {r.review.reviewer} on {new Date(r.review.reviewed_at * 1000).toLocaleString()}
                                        {r.review.note ? ` · ${r.review.note}` : ''}{r.stale.length ? ' · before its inputs changed' : ''}</span>
                                    <button type="button" onClick={() => withdraw(r.id)} className="text-text-muted underline hover:text-text-main">withdraw</button>
                                </div>
                            )}
                            {signing === r.id && (
                                <div className="mt-2 flex flex-wrap items-center gap-1.5" data-sign-off={r.id}>
                                    <input value={reviewer} onChange={(e) => setReviewer(e.target.value)} placeholder="Reviewer name" aria-label="Reviewer name"
                                        className="h-7 w-40 rounded-md border border-border bg-background px-2" />
                                    <input value={note} onChange={(e) => setNote(e.target.value)} placeholder="Note (optional)" aria-label="Review note"
                                        className="h-7 min-w-0 flex-1 rounded-md border border-border bg-background px-2" />
                                    <button type="button" onClick={() => signOff(r.id)} disabled={!reviewer.trim()}
                                        className="h-7 rounded-md border border-primary/50 px-2.5 font-semibold text-primary hover:bg-primary/10 disabled:opacity-50">Sign off</button>
                                </div>
                            )}
                            {r.stale.length > 0 && (
                                <div className="mt-1 flex gap-1.5 text-[11px] text-text-main"><AlertTriangle size={12} className="mt-0.5 shrink-0 text-warning" />
                                    <span>Out of date: {r.stale.join('; ')}</span></div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ProjectRuns;
