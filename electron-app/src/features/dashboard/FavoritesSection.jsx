/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Home: starred methods and folders (FavoritesContext), filterable by kind. Each entry is resolved against the
 * current navigation; a method filed elsewhere in the other grouping is still found by its catalogue entry.
 */
import React, { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { Star, FileText, Folder, ChevronRight } from 'lucide-react';
import { useFavorites } from '@/context/FavoritesContext';
import { FavoriteStar } from '@/components/common/FavoriteStar';
import { findFunction, catalogueEntry } from '@/config/navigation';

const FILTERS = [
    { id: 'all', label: 'All' },
    { id: 'method', label: 'Methods' },
    { id: 'folder', label: 'Folders' },
];

/** Favourite entries with what they point to in `modules`; entries that no longer exist are left out. */
const resolve = (entries, modules) => entries.map((f) => {
    if (f.type === 'method') {
        const match = findFunction(modules, f.id);
        if (match) return { ...f, title: match.fn.title, fn: match.fn, cat: match.cat, sub: match.sub };
        const entry = catalogueEntry(f.id);
        const method = entry?.methods.find((m) => m.id === f.id);
        return method ? { ...f, title: method.title, fn: { id: f.id, title: method.title }, path: [entry.title] } : null;
    }
    const [catId, subId] = f.id.split('/');
    const cat = modules.find((c) => c.id === catId);
    const sub = cat?.items?.find((s) => (s.id || s.title) === subId);
    return sub ? { ...f, title: sub.title, cat, sub } : null;
}).filter(Boolean);

export const FavoritesSection = ({ modules, onSelectFunction, onSelectFolder }) => {
    const { entries } = useFavorites();
    const [filter, setFilter] = useState('all');
    const items = useMemo(() => resolve(entries, modules), [entries, modules]);
    const counts = { all: items.length, method: items.filter((i) => i.type === 'method').length, folder: items.filter((i) => i.type === 'folder').length };
    const shown = items.filter((i) => filter === 'all' || i.type === filter);

    if (items.length === 0) return null; // nothing starred: no section at all

    const open = (item) => (item.type === 'folder' ? onSelectFolder?.(item.cat, item.sub) : onSelectFunction?.(item.fn, item.cat, item.sub));

    return (
        <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1, duration: 0.3 }} data-home-favorites>
            <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
                <h2 className="text-lg font-semibold text-text-main flex items-center gap-2">
                    <Star size={18} className="text-text-muted" />
                    Favourites
                </h2>
                <div role="tablist" aria-label="Favourite kind" className="flex rounded-md border border-border p-0.5 text-xs">
                    {FILTERS.map((f) => (
                        <button key={f.id} type="button" role="tab" aria-selected={filter === f.id} onClick={() => setFilter(f.id)}
                            className={`px-2.5 py-1 rounded font-medium transition-colors ${filter === f.id ? 'bg-primary/15 text-primary' : 'text-text-muted hover:text-text-main'}`}>
                            {f.label} <span className="tabular-nums opacity-70">{counts[f.id]}</span>
                        </button>
                    ))}
                </div>
            </div>

            {shown.length === 0 ? (
                <div className="rounded-lg border border-dashed border-border px-4 py-5 text-sm text-text-muted">
                    No {filter === 'method' ? 'methods' : 'folders'} starred yet.
                </div>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                    {shown.map((item) => {
                        const Icon = item.type === 'folder' ? Folder : FileText;
                        const path = item.path || [item.cat?.title, item.type === 'method' ? item.sub?.title : null].filter(Boolean);
                        const count = item.type === 'folder' ? (item.sub.functions || []).length : null;
                        return (
                            <div key={`${item.type}:${item.id}`} role="button" tabIndex={0} onClick={() => open(item)}
                                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(item); } }}
                                className="card-lift group flex items-start gap-3 rounded-lg border border-border bg-surface px-3.5 py-3 text-left cursor-pointer">
                                <span className={`mt-0.5 shrink-0 rounded-md p-1.5 ring-1 ${item.type === 'folder' ? 'bg-primary/10 text-primary ring-primary/20' : 'bg-surface-muted text-text-muted ring-border'}`}>
                                    <Icon size={15} />
                                </span>
                                <span className="min-w-0 flex-1">
                                    <span className="block text-sm font-medium text-text-main truncate group-hover:text-primary transition-colors">{item.title}</span>
                                    <span className="flex items-center gap-1 text-xs text-text-muted truncate mt-0.5">
                                        {path.map((p, i) => (
                                            <React.Fragment key={i}>{i > 0 && <ChevronRight size={11} className="shrink-0" />}<span className="truncate">{p}</span></React.Fragment>
                                        ))}
                                        {count !== null && <span className="shrink-0">{path.length ? ' · ' : ''}{count} calculation{count === 1 ? '' : 's'}</span>}
                                    </span>
                                </span>
                                <FavoriteStar id={item.id} type={item.type} label={item.title} size={14} />
                            </div>
                        );
                    })}
                </div>
            )}
        </motion.section>
    );
};

export default FavoritesSection;
