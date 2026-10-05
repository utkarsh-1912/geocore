/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Folder, FileText, Settings, Moon, Sun, History, HelpCircle, Command, Box, Wrench, Terminal } from 'lucide-react';
import { GeoAILogo } from '@/components/common/GeoAILogo';
import { GEOTECHNICAL_MODULES } from '@/config/geotechnicalModules';

// Bolds the parts of `text` that match one of the (already lower-cased) query tokens.
const HighlightMatch = ({ text, tokens }) => {
    if (!tokens || tokens.length === 0) return text;
    const pattern = tokens.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
    const parts = text.split(new RegExp(`(${pattern})`, 'gi'));
    return parts.map((part, i) =>
        tokens.includes(part.toLowerCase())
            ? <b key={i} className="text-primary font-semibold">{part}</b>
            : part
    );
};

/**
 * CommandPalette — VS-Code-style Ctrl+K command palette overlay
 * Fuzzy-searches all 213+ tools, categories, modules, and app actions.
 */
export const CommandPalette = ({ isOpen, onClose, onNavigate, onAction }) => {
    const [query, setQuery] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);
    const inputRef = useRef(null);
    const listRef = useRef(null);

    // Build flat search index once. Each item carries its own text plus its
    // ancestry's (category/module) title+description, so a query like "pile
    // capacity" or "bearing capacity" can match even when no single title
    // contains both words verbatim (e.g. "Vertical Capacity" under the "Pile
    // calculations" category, or "Unit end bearing" under a category
    // described as "Axial capacity, settlements, …").
    const searchIndex = useMemo(() => {
        const items = [];
        const idWords = (id) => (id || '').replace(/[_-]+/g, ' ');

        const makeItem = (base) => {
            const ancestry = [base.category?.title, base.category?.description, base.subModule?.title, base.subModule?.description]
                .filter(Boolean).join(' ');
            const haystack = [base.title, base.description, idWords(base.id), ancestry]
                .filter(Boolean).join(' ').toLowerCase();
            return { ...base, haystack };
        };

        // Actions
        items.push(makeItem({ type: 'Action', id: 'toggle_theme', title: 'Toggle Dark / Light Mode', icon: Moon, shortcut: '', action: 'toggleTheme' }));
        items.push(makeItem({ type: 'Action', id: 'open_history', title: 'Open Calculation History', icon: History, shortcut: 'Ctrl+H', action: 'openHistory' }));
        items.push(makeItem({ type: 'Action', id: 'open_copilot', title: 'Open GeoAI Assistant', icon: GeoAILogo, shortcut: 'Ctrl+Shift+A', action: 'openCopilot' }));
        items.push(makeItem({ type: 'Action', id: 'open_help', title: 'Help & Keyboard Shortcuts', icon: HelpCircle, shortcut: '', action: 'openHelp' }));

        // Categories, Sub-modules, Functions
        GEOTECHNICAL_MODULES.forEach(category => {
            items.push(makeItem({ type: 'Category', id: category.id, title: category.title, description: category.description, category, icon: Folder }));

            if (category.items) {
                category.items.forEach(subModule => {
                    items.push(makeItem({ type: 'Module', id: subModule.id || subModule.title, title: subModule.title, description: subModule.description, category, subModule, icon: Folder }));

                    if (subModule.functions) {
                        subModule.functions.forEach(func => {
                            items.push(makeItem({ type: 'Function', id: func.id, title: func.title, description: func.description, category, subModule, func, icon: FileText }));
                        });
                    }
                });
            }
        });

        return items;
    }, []);

    // Score a single query token against a piece of text: exact/prefix/substring
    // beat a fuzzy in-order-subsequence match, which is kept only as a last resort.
    const scoreToken = (token, text) => {
        if (!text) return 0;
        if (text === token) return 40;
        if (text.startsWith(token)) return 30;
        if (text.includes(token)) return 18;
        let qi = 0;
        for (let i = 0; i < text.length && qi < token.length; i++) {
            if (text[i] === token[qi]) qi++;
        }
        return qi === token.length ? 4 : 0;
    };

    // Filtered results
    const results = useMemo(() => {
        if (!query.trim()) {
            // Show actions + top categories when empty
            return searchIndex.filter(i => i.type === 'Action' || i.type === 'Category').slice(0, 15);
        }

        const q = query.toLowerCase().trim();
        const tokens = q.split(/\s+/).filter(Boolean);

        const scored = searchIndex
            .map(item => {
                const title = item.title.toLowerCase();

                // Every token must match somewhere in the item's own text or its
                // category/module ancestry — this is what lets multi-word terms
                // like "bearing capacity" find results even split across levels.
                let total = 0;
                for (const token of tokens) {
                    const best = Math.max(scoreToken(token, title) * 2, scoreToken(token, item.haystack));
                    if (best === 0) { total = 0; break; }
                    total += best;
                }
                if (total === 0) return { ...item, score: 0 };

                if (title === q) total += 100;
                else if (title.startsWith(q)) total += 40;
                else if (title.includes(q)) total += 20;

                return { ...item, score: total };
            })
            .filter(item => item.score > 0)
            .sort((a, b) => b.score - a.score);

        return scored.slice(0, 15);
    }, [query, searchIndex]);

    // Tokens used to highlight matches in the results list.
    const queryTokens = useMemo(() => query.toLowerCase().trim().split(/\s+/).filter(Boolean), [query]);

    // Reset on open
    useEffect(() => {
        if (isOpen) {
            setQuery('');
            setSelectedIndex(0);
            setTimeout(() => inputRef.current?.focus(), 50);
        }
    }, [isOpen]);

    // Scroll selected item into view
    useEffect(() => {
        if (listRef.current) {
            const el = listRef.current.children[selectedIndex];
            if (el) el.scrollIntoView({ block: 'nearest' });
        }
    }, [selectedIndex]);

    const handleSelect = (item) => {
        if (item.type === 'Action') {
            onAction?.(item.action);
        } else {
            onNavigate?.(item.type, item, item.category, item.subModule);
        }
        onClose();
    };

    const handleKeyDown = (e) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setSelectedIndex(prev => Math.min(prev + 1, results.length - 1));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setSelectedIndex(prev => Math.max(prev - 1, 0));
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (results[selectedIndex]) handleSelect(results[selectedIndex]);
        } else if (e.key === 'Escape') {
            onClose();
        }
    };

    const typeColors = {
        Category: 'text-blue-500',
        Module: 'text-purple-500',
        Function: 'text-primary',
        Action: 'text-amber-500'
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh] bg-black/50 backdrop-blur-sm"
                    onClick={onClose}
                >
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -10 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: -10 }}
                        transition={{ duration: 0.15 }}
                        className="w-full max-w-xl bg-surface border border-border rounded-md shadow-2xl overflow-hidden"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Search Input */}
                        <div className="flex items-center gap-3 px-4 py-3 border-b border-border">
                            <Search size={18} className="text-text-muted shrink-0" />
                            <input
                                ref={inputRef}
                                type="text"
                                value={query}
                                onChange={(e) => { setQuery(e.target.value); setSelectedIndex(0); }}
                                onKeyDown={handleKeyDown}
                                placeholder="Search tools, modules, actions..."
                                className="flex-1 bg-transparent text-text-main text-sm outline-none placeholder-text-muted"
                                autoComplete="off"
                                spellCheck={false}
                            />
                            <kbd className="hidden sm:inline-flex items-center px-1.5 py-0.5 text-[10px] font-mono text-text-muted bg-background border border-border rounded-sm">
                                ESC
                            </kbd>
                        </div>

                        {/* Results */}
                        <div ref={listRef} className="max-h-[50vh] overflow-y-auto">
                            {results.length > 0 ? (
                                <ul className="py-1">
                                    {results.map((item, idx) => {
                                        const Icon = item.icon || FileText;
                                        return (
                                            <li key={`${item.type}-${item.id}`}>
                                                <button
                                                    onClick={() => handleSelect(item)}
                                                    onMouseEnter={() => setSelectedIndex(idx)}
                                                    className={`w-full text-left px-4 py-2.5 flex items-center gap-3 transition-colors ${
                                                        selectedIndex === idx
                                                            ? 'bg-primary/10 border-l-2 border-primary'
                                                            : 'hover:bg-background border-l-2 border-transparent'
                                                    }`}
                                                >
                                                    <div className={`p-1 rounded bg-background shrink-0 ${typeColors[item.type]}`}>
                                                        <Icon size={14} />
                                                    </div>
                                                    <div className="flex-1 min-w-0">
                                                        <div className="text-sm font-medium text-text-main truncate">
                                                            <HighlightMatch text={item.title} tokens={queryTokens} />
                                                        </div>
                                                        <div className="text-xs text-text-muted truncate">
                                                            {item.type}
                                                            {item.category && item.type !== 'Category' && ` • ${item.category.title}`}
                                                        </div>
                                                    </div>
                                                    {item.shortcut && (
                                                        <kbd className="text-[10px] font-mono text-text-muted bg-background border border-border rounded-sm px-1.5 py-0.5 shrink-0">
                                                            {item.shortcut}
                                                        </kbd>
                                                    )}
                                                </button>
                                            </li>
                                        );
                                    })}
                                </ul>
                            ) : (
                                <div className="py-8 text-center text-sm text-text-muted">
                                    <p>No results found for "{query}"</p>
                                    <p className="text-xs mt-1 text-text-subtle">Try a different word, e.g. a method name or module.</p>
                                </div>
                            )}
                        </div>

                        {/* Footer */}
                        <div className="flex items-center justify-between px-4 py-2 border-t border-border bg-background/50 text-[10px] text-text-muted">
                            <div className="flex items-center gap-3">
                                <span>↑↓ Navigate</span>
                                <span>Enter Select</span>
                                <span>ESC Close</span>
                            </div>
                            <span>{results.length} result{results.length !== 1 ? 's' : ''}</span>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};
