/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card } from '../../components/ui/Card';
import { ArrowRight, Folder, FileText } from 'lucide-react';
import { loadFunctionDocs } from '../calculations/guide/functionDocs';
import { CALC_STATUS } from '../calculations/calcStatus';
import { FavoriteStar } from '../../components/common/FavoriteStar';

/**
 * One-line summaries of the calculations on a page, from the offline Guide docs (loaded on first use and
 * cached). Summaries that only introduce a list or equation ("... as follows:") are skipped.
 */
const useFunctionSummaries = (items) => {
    const [summaries, setSummaries] = useState({});
    const wanted = (items || []).filter((item) => !item.description && item.id).map((item) => item.id).join(',');
    useEffect(() => {
        if (!wanted) return undefined;
        let cancelled = false;
        loadFunctionDocs()
            .then((docs) => {
                if (cancelled) return;
                const found = {};
                for (const id of wanted.split(',')) {
                    const summary = docs.functions?.[id]?.summary?.trim();
                    if (summary && !summary.endsWith(':')) found[id] = summary;
                }
                setSummaries(found);
            })
            .catch(() => { /* docs unavailable: cards show their title only */ });
        return () => { cancelled = true; };
    }, [wanted]);
    return summaries;
};

const CardMeta = ({ item }) => {
    const status = CALC_STATUS[item.status];
    const standards = item.standards || [];
    if (!status && standards.length === 0) return null;
    return (
        <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs">
            {status && (
                <span className={`inline-flex items-center gap-1 ${status.className}`}>
                    <status.Icon size={12} /> {status.label}
                </span>
            )}
            {standards.length > 0 && <span className="text-text-muted truncate">{standards.join(' · ')}</span>}
        </div>
    );
};

// `favoriteOf(item)` -> {id, type} gives each card a favourite star (a folder or a method).
export const DashboardGrid = ({ items, onSelect, title, description, isCategory = false, favoriteOf }) => {
    const summaries = useFunctionSummaries(items);
    return (
        <div className="max-w-7xl mx-auto h-full flex flex-col">
            <div className="mb-8 shrink-0">
                <h2 className="text-3xl font-bold tracking-tight text-text-main mb-2">{title}</h2>
                {description && <p className="text-text-muted">{description}</p>}
            </div>

            {items && items.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-4">
                    {items.map((item, index) => (
                        <motion.div
                            key={item.id || item.title}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                            onClick={() => onSelect(item)}
                            className="cursor-pointer group"
                        >
                            <Card className="card-lift h-full relative overflow-hidden">
                                <div className="flex items-start justify-between mb-4">
                                    <div className={`p-3 rounded-md ring-1 ring-primary/20 bg-gradient-to-br from-primary/20 to-primary/5 text-primary`}>
                                        {isCategory ? <Folder size={24} /> : <FileText size={24} />}
                                    </div>
                                    <div className="flex items-center gap-1">
                                        {favoriteOf && <FavoriteStar {...favoriteOf(item)} label={item.title} size={17} reveal />}
                                        <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 transform translate-x-2 group-hover:translate-x-0">
                                            <ArrowRight size={20} className="text-primary" />
                                        </div>
                                    </div>
                                </div>

                                <h3 className="text-xl font-semibold text-text-main mb-2 group-hover:text-primary transition-colors duration-300">
                                    {item.title}
                                </h3>

                                {(item.description || summaries[item.id]) && (
                                    <p className="text-text-muted text-sm line-clamp-2">
                                        {item.description || summaries[item.id]}
                                    </p>
                                )}
                                <CardMeta item={item} />
                            </Card>
                        </motion.div>
                    ))}
                </div>
            ) : (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.4, ease: "easeOut" }}
                    className="flex-1 flex flex-col items-center justify-center p-12 min-h-[400px] text-center"
                >
                    <h3 className="text-xl font-semibold text-text-muted mb-2">No Modules Available</h3>
                    <p className="text-text-muted/70 max-w-sm">
                        This category does not have any active calculation modules yet. Please explore other categories in the sidebar.
                    </p>
                </motion.div>
            )}
        </div>
    );
};
