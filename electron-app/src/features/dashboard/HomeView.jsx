/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import {
    ArrowRight, Folder, Clock, Star, Book, Command, Trash2, Search
} from 'lucide-react';
import { getCategoryIcon } from '@/config/categoryIcons';
import { GeoAILogo } from '@/components/common/GeoAILogo';
import { ConfirmationModal } from '@/components/common/ConfirmationModal';


/**
 * Count total functions recursively in a module category
 */
const countTools = (category) => {
    let count = 0;
    if (category.items) {
        category.items.forEach(sub => {
            if (sub.functions) count += sub.functions.length;
        });
    }
    return count;
};

/**
 * HomeView — Enhanced landing page with quick actions, favorites, recent calculations, and module grid
 */
export const HomeView = ({ modules, onSelectCategory, onSelectFunction, history = [], favorites = [], onClearRecent, onOpenCopilot, onOpenCommands, onOpenHelp }) => {
    const [showClearConfirm, setShowClearConfirm] = useState(false);
    const [moduleFilter, setModuleFilter] = useState('');

    const totalTools = useMemo(() => modules.reduce((n, c) => n + countTools(c), 0), [modules]);

    const visibleModules = useMemo(() => {
        const q = moduleFilter.trim().toLowerCase();
        if (!q) return modules;
        return modules.filter(c => `${c.title} ${c.description || ''}`.toLowerCase().includes(q));
    }, [modules, moduleFilter]);

    const recentCalcs = useMemo(() => {
        return (history || []).slice(0, 5);
    }, [history]);

    const favoriteTools = useMemo(() => {
        if (!favorites || favorites.length === 0) return [];
        const tools = [];
        modules.forEach(cat => {
            if (cat.items) {
                cat.items.forEach(sub => {
                    if (sub.functions) {
                        sub.functions.forEach(fn => {
                            if (favorites.includes(fn.id)) {
                                tools.push({ ...fn, category: cat, subModule: sub });
                            }
                        });
                    }
                });
            }
        });
        return tools;
    }, [favorites, modules]);

    const formatTimeAgo = (timestamp) => {
        if (!timestamp) return '';
        const diff = Date.now() - new Date(timestamp).getTime();
        const mins = Math.floor(diff / 60000);
        if (mins < 1) return 'just now';
        if (mins < 60) return `${mins}m ago`;
        const hours = Math.floor(mins / 60);
        if (hours < 24) return `${hours}h ago`;
        const days = Math.floor(hours / 24);
        return `${days}d ago`;
    };

    return (
        <div className="max-w-7xl mx-auto space-y-8">
            {/* Welcome Banner */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
            >
                <div className="hero-surface relative overflow-hidden rounded-xl border border-primary/15 p-6 md:p-9">
                    <div className="hero-surface__grid" aria-hidden />
                    <div className="relative z-10">
                    <div className="flex items-start justify-between">
                        <div>
                            <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-white mb-2">
                                Welcome to <span className="geoai-gradient-text">GeoCore</span>
                            </h1>
                            <p className="text-white/70 text-sm max-w-xl leading-relaxed">
                                Professional Geotechnical Engineering Workstation — 213+ calculation tools powered by Groundhog with offline GeoAI assistance.
                            </p>
                        </div>
                        <span className="text-xs text-white/70 bg-white/5 border border-white/10 px-2 py-1 rounded-md font-mono hidden sm:block">v1.0.0</span>
                    </div>

                    {/* Quick Actions */}
                    <div className="flex flex-wrap gap-2 mt-5">
                        {onOpenCopilot && (
                            <button
                                onClick={onOpenCopilot}
                                className="btn-brand flex items-center gap-2 px-3.5 py-2 rounded-md text-sm font-semibold"
                            >
                                <GeoAILogo size={14} />
                                <span>Ask GeoAI</span>
                            </button>
                        )}
                        <button
                            onClick={onOpenCommands}
                            className="flex items-center gap-2 px-3.5 py-2 bg-white/5 border border-white/15 rounded-md hover:bg-white/10 hover:border-primary/50 transition-colors text-sm text-white"
                        >
                            <Command size={14} className="text-primary" />
                            <span>Commands</span>
                            <kbd className="text-[10px] font-mono text-white/70 bg-white/5 border border-white/15 rounded-md px-1 ml-1">Ctrl+K</kbd>
                        </button>
                        <button
                            onClick={onOpenHelp}
                            className="flex items-center gap-2 px-3.5 py-2 bg-white/5 border border-white/15 rounded-md hover:bg-white/10 hover:border-primary/50 transition-colors text-sm text-white"
                        >
                            <Book size={14} className="text-primary" />
                            <span>Guide</span>
                        </button>
                    </div>

                    {/* Stat chips */}
                    <div className="flex flex-wrap gap-2 mt-6 pt-5 border-t border-white/10">
                        {[
                            { label: 'modules', value: modules.length },
                            { label: 'calculation tools', value: totalTools },
                            { label: 'saved favorites', value: favorites.length },
                            { label: 'recent calculations', value: (history || []).length },
                        ].map(stat => (
                            <div key={stat.label} className="flex items-baseline gap-1.5 rounded-md border border-white/10 bg-white/5 px-3 py-1.5">
                                <span className="text-base font-semibold text-white tabular-nums">{stat.value}</span>
                                <span className="text-xs text-white/60">{stat.label}</span>
                            </div>
                        ))}
                    </div>
                    </div>
                </div>
            </motion.div>

            {/* Favorites Section */}
            {favoriteTools.length > 0 && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1, duration: 0.3 }}
                >
                    <h2 className="text-lg font-semibold text-text-main mb-3 flex items-center gap-2">
                        <Star size={18} className="text-amber-400" />
                        Favorites
                    </h2>
                    <div className="flex gap-3 overflow-x-auto pb-2 no-scrollbar">
                        {favoriteTools.map((tool) => (
                            <button
                                key={tool.id}
                                onClick={() => onSelectFunction?.(tool, tool.category, tool.subModule)}
                                className="card-lift shrink-0 bg-surface border border-border rounded-lg px-4 py-3 text-left min-w-[160px]"
                            >
                                <div className="text-sm font-medium text-text-main truncate">{tool.title}</div>
                                <div className="text-xs text-text-muted truncate mt-1">{tool.category?.title}</div>
                            </button>
                        ))}
                    </div>
                </motion.div>
            )}

            {/* Recent Calculations */}
            {recentCalcs.length > 0 && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.15, duration: 0.3 }}
                >
                    <div className="flex items-center justify-between mb-3">
                        <h2 className="text-lg font-semibold text-text-main flex items-center gap-2">
                            <Clock size={18} className="text-text-muted" />
                            Recent Calculations
                        </h2>
                        {onClearRecent && (
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setShowClearConfirm(true);
                                }}
                                className="text-xs text-text-muted hover:text-error hover:bg-error/10 px-2.5 py-1 rounded-md transition-colors flex items-center gap-1.5 font-medium border border-transparent hover:border-error/20"
                                title="Clear recent calculation history"
                            >
                                <Trash2 size={13} />
                                <span>Clear Recent</span>
                            </button>
                        )}
                    </div>
                    <div className="bg-surface border border-border rounded-lg divide-y divide-border overflow-hidden shadow-card">
                        {recentCalcs.map((calc, idx) => (
                            <button
                                key={idx}
                                onClick={() => onSelectFunction?.({
                                    title: calc.functionName,
                                    id: calc.functionId || calc.functionName
                                }, calc.category, calc.subModule)}
                                className="w-full text-left px-4 py-3 hover:bg-background transition-colors flex items-center justify-between group"
                            >
                                <div className="min-w-0">
                                    <div className="text-sm font-medium text-text-main truncate">{calc.functionName}</div>
                                    <div className="text-xs text-text-muted truncate">{calc.category?.title}</div>
                                </div>
                                <div className="flex items-center gap-3 shrink-0">
                                    <span className="text-xs text-text-muted">{formatTimeAgo(calc.timestamp)}</span>
                                    <ArrowRight size={14} className="text-text-muted opacity-0 group-hover:opacity-100 transition-opacity" />
                                </div>
                            </button>
                        ))}
                    </div>
                </motion.div>
            )}

            {/* Module Categories Grid */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.3 }}
            >
                <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
                    <h2 className="text-lg font-semibold text-text-main flex items-center gap-2">
                        <Folder size={18} className="text-primary" />
                        All Modules
                        <span className="text-xs font-medium text-text-muted bg-surface-muted border border-border rounded-md px-2 py-0.5 tabular-nums">
                            {visibleModules.length}
                        </span>
                    </h2>
                    <div className="relative w-full sm:w-64">
                        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-subtle pointer-events-none" />
                        <input
                            type="text"
                            value={moduleFilter}
                            onChange={(e) => setModuleFilter(e.target.value)}
                            onKeyDown={(e) => e.key === 'Escape' && setModuleFilter('')}
                            placeholder="Filter modules…"
                            aria-label="Filter modules"
                            className="w-full h-8 pl-8 pr-3 rounded-md border border-border bg-surface text-sm text-text-main placeholder:text-text-subtle outline-none transition-all focus:border-primary/50 focus:shadow-[0_0_0_3px_color-mix(in_srgb,var(--color-primary)_12%,transparent)]"
                        />
                    </div>
                </div>
                {visibleModules.length === 0 && (
                    <div className="rounded-lg border border-dashed border-border py-10 text-center text-sm text-text-muted">
                        No modules match “{moduleFilter}”.
                    </div>
                )}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {visibleModules.map((category, index) => {
                        const Icon = getCategoryIcon(category.id);
                        const toolCount = countTools(category);

                        return (
                            <motion.div
                                key={category.id || category.title}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.25 + index * 0.03 }}
                                onClick={() => onSelectCategory(category)}
                                className="cursor-pointer group"
                            >
                                <Card className="card-lift h-full relative overflow-hidden !rounded-lg">
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="p-2.5 rounded-lg bg-gradient-to-br from-primary/20 to-primary/5 text-primary ring-1 ring-primary/20">
                                            <Icon size={22} />
                                        </div>
                                        <div className="flex items-center gap-2">
                                            {toolCount > 0 && (
                                                <span className="text-[10px] font-medium text-text-muted bg-background border border-border rounded-md px-2 py-0.5">
                                                    {toolCount} tools
                                                </span>
                                            )}
                                            <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                                <ArrowRight size={18} className="text-primary" />
                                            </div>
                                        </div>
                                    </div>

                                    <h3 className="text-lg font-semibold text-text-main mb-1.5 group-hover:text-primary transition-colors">
                                        {category.title}
                                    </h3>
                                    <p className="text-text-muted text-sm line-clamp-2">
                                        {category.description || "Access geotechnical modules and calculations."}
                                    </p>
                                </Card>
                            </motion.div>
                        );
                    })}
                </div>
            </motion.div>

            {/* Custom Clear History Confirmation Modal */}
            <ConfirmationModal
                isOpen={showClearConfirm}
                title="Clear Recent History?"
                message="Are you sure you want to clear your recent calculation history? Quick-access links on this dashboard will be removed."
                confirmText="Clear All"
                cancelText="Cancel"
                variant="danger"
                onConfirm={() => {
                    onClearRecent?.();
                    setShowClearConfirm(false);
                }}
                onCancel={() => setShowClearConfirm(false)}
            />
        </div>
    );
};
