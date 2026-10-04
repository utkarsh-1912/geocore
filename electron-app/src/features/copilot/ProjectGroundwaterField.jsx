/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Project groundwater level for GeoAI: recorded depth below ground level [m], or "not recorded"
 * (GeoAI then asks for it instead of assuming one). Stored with the workspace by the backend
 * (/api/geoai/project/groundwater).
 */

import React, { useEffect, useState } from 'react';
import { Droplets } from 'lucide-react';
import { toast } from 'sonner';
import { api } from '../../api/client';

// Same rule as the backend (core/geoai/data_access.py validate_groundwater_depth): a number >= 0, in m.
const parseDepth = (text) => {
    const trimmed = String(text).trim();
    if (!trimmed) return { error: 'Enter a depth in m, or Clear to leave it not recorded.' };
    const value = Number(trimmed);
    if (!Number.isFinite(value)) return { error: 'Enter a number in m.' };
    if (value < 0) return { error: 'Depth must be 0 m or more below ground level.' };
    return { value };
};

export const ProjectGroundwaterField = () => {
    const [recorded, setRecorded] = useState(null); // number [m] or null = not recorded
    const [status, setStatus] = useState('loading'); // loading | ready | unavailable
    const [editing, setEditing] = useState(false);
    const [draft, setDraft] = useState('');
    const [error, setError] = useState(null);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        let cancelled = false;
        api.geoaiGetGroundwater()
            .then((res) => { if (!cancelled) { setRecorded(res.groundwater_depth_m); setStatus('ready'); } })
            .catch(() => { if (!cancelled) setStatus('unavailable'); });
        return () => { cancelled = true; };
    }, []);

    const startEditing = () => {
        setDraft(recorded == null ? '' : String(recorded));
        setError(null);
        setEditing(true);
    };

    const save = async (value) => {
        setSaving(true);
        try {
            const res = await api.geoaiSetGroundwater(value);
            setRecorded(res.groundwater_depth_m);
            setEditing(false);
            setError(null);
            toast.success(res.groundwater_depth_m == null
                ? 'Groundwater level cleared (not recorded).'
                : `Groundwater level recorded: ${res.groundwater_depth_m} m below ground level.`);
        } catch (err) {
            setError(err.message || 'Could not save the groundwater level.');
        } finally {
            setSaving(false);
        }
    };

    const submit = (e) => {
        e.preventDefault();
        const parsed = parseDepth(draft);
        if (parsed.error) {
            setError(parsed.error);
            return;
        }
        save(parsed.value);
    };

    return (
        <div className="border-t border-border px-3 py-2 shrink-0 text-[11px]">
            <div className="flex items-center justify-between gap-2 mb-1">
                <span className="font-semibold text-text-muted uppercase tracking-wider flex items-center gap-1.5">
                    <Droplets size={12} className="text-primary" />
                    Groundwater level
                </span>
                {status === 'ready' && !editing && (
                    <button onClick={startEditing} className="text-primary hover:underline">
                        {recorded == null ? 'Set' : 'Edit'}
                    </button>
                )}
            </div>

            {status === 'loading' && <div className="text-text-muted">Loading...</div>}
            {status === 'unavailable' && <div className="text-text-muted">Unavailable (backend not reachable)</div>}

            {status === 'ready' && !editing && (
                <div className={recorded == null ? 'text-text-muted italic' : 'text-text-main'} title="Project groundwater level used by GeoAI">
                    {recorded == null ? 'not recorded' : `${recorded} m below ground level`}
                </div>
            )}

            {status === 'ready' && editing && (
                <form onSubmit={submit} noValidate className="space-y-1.5">
                    <div className="flex items-center gap-1.5">
                        <input
                            type="number"
                            step="any"
                            min="0"
                            autoFocus
                            value={draft}
                            onChange={(e) => { setDraft(e.target.value); setError(null); }}
                            aria-label="Groundwater depth below ground level in m"
                            placeholder="e.g. 2.5"
                            className={`w-full min-w-0 bg-background border rounded px-2 py-1 text-text-main focus:outline-none focus:border-primary ${error ? 'border-red-500' : 'border-border'}`}
                        />
                        <span className="text-text-muted shrink-0">m</span>
                    </div>
                    {error && <div className="text-red-500">{error}</div>}
                    <div className="flex items-center gap-1.5">
                        <button type="submit" disabled={saving} className="px-2 py-1 rounded bg-primary text-on-primary font-semibold disabled:opacity-50">
                            Save
                        </button>
                        <button type="button" disabled={saving} onClick={() => { setEditing(false); setError(null); }} className="px-2 py-1 rounded border border-border text-text-muted hover:text-text-main">
                            Cancel
                        </button>
                        {recorded != null && (
                            <button type="button" disabled={saving} onClick={() => save(null)} className="ml-auto px-2 py-1 rounded text-text-muted hover:text-red-500" title="Clear back to not recorded">
                                Clear
                            </button>
                        )}
                    </div>
                </form>
            )}
        </div>
    );
};
