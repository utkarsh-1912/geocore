/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/Card';
import {
    ArrowRight, Folder, FileText, Clock, Star, Bot, Book, Command, Trash2,
    Database, Box, Shovel, Activity, Droplets, Ruler, Layers, Anchor
} from 'lucide-react';

// Category icon map (matches Sidebar.jsx)
const CATEGORY_ICONS = {
    general: Database,
    site_investigation: Ruler,
    piles: Box,
    shallow: Layers,
    consolidation: Droplets,
    excavations: Shovel,
    dynamics: Activity,
    standards: Ruler,
    constitutive: Layers,
    pipelines: Anchor,
};

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
                <div className="bg-gradient-to-br from-primary/10 via-surface to-primary-light/5 border border-border rounded-md p-6 md:p-8">
                    <div className="flex items-start justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-text-main mb-2">
                                Welcome to <span className="text-primary">GeoCore</span>
                            </h1>
                            <p className="text-text-muted text-sm max-w-xl">
                                Professional Geotechnical Engineering Workstation — 213+ calculation tools powered by Groundhog with offline GeoAI assistance.
                            </p>
                        </div>
                        <span className="text-xs text-text-muted bg-background border border-border px-2 py-1 rounded font-mono hidden sm:block">v1.0.0</span>
                    </div>

                    {/* Quick Actions */}
                    <div className="flex flex-wrap gap-2 mt-5">
                        <button
                            onClick={onOpenCommands}
                            className="flex items-center gap-2 px-3 py-2 bg-surface border border-border rounded hover:border-primary/50 transition-colors text-sm text-text-main"
                        >
                            <Command size={14} className="text-primary" />
                            <span>Commands</span>
                            <kbd className="text-[10px] font-mono text-text-muted bg-background border border-border rounded px-1 ml-1">Ctrl+K</kbd>
                        </button>
                        <button
                            onClick={onOpenHelp}
                            className="flex items-center gap-2 px-3 py-2 bg-surface border border-border rounded hover:border-primary/50 transition-colors text-sm text-text-main"
                        >
                            <Book size={14} className="text-primary" />
                            <span>Guide</span>
                        </button>
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
                                className="shrink-0 bg-surface border border-border rounded-md px-4 py-3 hover:border-primary/50 transition-colors text-left min-w-[160px]"
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
                                    onClearRecent();
                                }}
                                className="text-xs text-text-muted hover:text-red-500 hover:bg-red-500/10 px-2.5 py-1 rounded transition-colors flex items-center gap-1.5 font-medium border border-transparent hover:border-red-500/20"
                                title="Clear recent calculation history"
                            >
                                <Trash2 size={13} />
                                <span>Clear Recent</span>
                            </button>
                        )}
                    </div>
                    <div className="bg-surface border border-border rounded-md divide-y divide-border">
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
                <h2 className="text-lg font-semibold text-text-main mb-3 flex items-center gap-2">
                    <Folder size={18} className="text-primary" />
                    All Modules
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {modules.map((category, index) => {
                        const Icon = CATEGORY_ICONS[category.id] || FileText;
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
                                <Card className="h-full hover:border-primary transition-colors duration-300 relative overflow-hidden group-hover:shadow-md">
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="p-2.5 rounded bg-primary/10 text-primary">
                                            <Icon size={22} />
                                        </div>
                                        <div className="flex items-center gap-2">
                                            {toolCount > 0 && (
                                                <span className="text-[10px] font-medium text-text-muted bg-background border border-border rounded px-2 py-0.5">
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
        </div>
    );
};
