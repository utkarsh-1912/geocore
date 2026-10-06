/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Folder, Layers, Calculator, Moon, History, HelpCircle, Clock, CornerDownLeft } from 'lucide-react';
import { GeoAILogo } from '@/components/common/GeoAILogo';
import { KBD } from '@/components/ui/KBD';
import { GEOTECHNICAL_MODULES } from '@/config/geotechnicalModules';
import { useHistory } from '@/context/HistoryContext';
import { loadFunctionDocs } from '@/features/calculations/guide/functionDocs';

const MAX_PER_GROUP = { Function: 8, Module: 4, Category: 3, Action: 3 };
const GROUPS = [
    ['Function', 'Calculations'],
    ['Module', 'Modules'],
    ['Category', 'Categories'],
    ['Action', 'Actions'],
];
const MAX_RECENT = 5;

// Abbreviations and alternative names engineers type, mapped to the wording the tool titles,
// descriptions and docstrings use. A query token matches if it, or one of these, matches.
const SYNONYMS = {
    spt: ['standard penetration'],
    cpt: ['cone penetration'],
    cptu: ['cone penetration'],
    phi: ['friction angle', 'shearing resistance'],
    su: ['undrained shear strength'],
    cu: ['undrained shear strength'],
    gamma: ['unit weight', 'weight density'],
    ka: ['earth pressure'],
    kp: ['earth pressure'],
    k0: ['earth pressure', 'at rest'],
    ec7: ['eurocode 7'],
    eurocode: ['eurocode'],
    dr: ['relative density'],
    ocr: ['overconsolidation'],
    gmax: ['small strain shear modulus', 'shear modulus'],
    vs: ['shear wave velocity'],
    cc: ['compression index'],
    cv: ['coefficient of consolidation'],
    sbt: ['soil behaviour type', 'soil behavior type'],
    uscs: ['soil classification'],
    bis: ['indian standard'],
    pile: ['piles'],
    footing: ['shallow foundation', 'spread foundation'],
    settlement: ['settlements'],
    liquefaction: ['liquefaction', 'cyclic'],
};

const words = (text) => text.split(/[^a-z0-9]+/).filter(Boolean);

// Edit distance between two short words, giving up (returning max + 1) once it exceeds `max`.
const editDistance = (a, b, max) => {
    if (Math.abs(a.length - b.length) > max) return max + 1;
    let prev = Array.from({ length: b.length + 1 }, (_, j) => j);
    for (let i = 1; i <= a.length; i++) {
        const cur = [i];
        let rowMin = i;
        for (let j = 1; j <= b.length; j++) {
            cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
            rowMin = Math.min(rowMin, cur[j]);
        }
        if (rowMin > max) return max + 1;
        prev = cur;
    }
    return prev[b.length];
};

/**
 * How well one search term matches a text: a whole word beats a word prefix, which beats a
 * substring; a one- or two-letter typo in a longer word still counts, weakly. Short terms
 * ("is", "k0") only match at the start of a word, so "is" does not hit "this".
 */
const scoreTerm = (term, text, textWords) => {
    if (!text) return 0;
    if (term.includes(' ')) return text.includes(term) ? 26 : 0; // a whole phrase: above a word prefix
    if (textWords.includes(term)) return 30;
    if (textWords.some((w) => w.startsWith(term))) return 24;
    if (term.length >= 3 && text.includes(term)) return 12;
    if (term.length >= 5) {
        const max = term.length >= 8 ? 2 : 1;
        if (textWords.some((w) => w.length >= 4 && editDistance(term, w, max) <= max)) return 8;
    }
    return 0;
};

// Bolds the parts of `text` that match one of the (already lower-cased) query tokens.
const HighlightMatch = ({ text, tokens }) => {
    const usable = (tokens || []).filter((t) => t.length >= 2);
    if (usable.length === 0) return text;
    const pattern = usable.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
    return text.split(new RegExp(`(${pattern})`, 'gi')).map((part, i) =>
        usable.includes(part.toLowerCase())
            ? <mark key={i} className="bg-transparent text-primary font-semibold">{part}</mark>
            : part
    );
};

const TYPE_STYLE = {
    Function: { icon: Calculator, tile: 'bg-primary/12 text-primary ring-primary/20' },
    Module: { icon: Layers, tile: 'bg-surface-muted text-text-muted ring-border' },
    Category: { icon: Folder, tile: 'bg-surface-muted text-text-muted ring-border' },
    Action: { icon: null, tile: 'bg-surface-muted text-text-muted ring-border' },
};

const ResultRow = ({ item, index, selected, recent, tokens, onSelect, onHover }) => {
    const style = TYPE_STYLE[item.type];
    const Icon = recent ? Clock : (item.icon || style.icon);
    const path = item.type === 'Function'
        ? [item.category?.title, item.subModule?.title].filter(Boolean).join(' › ')
        : item.type === 'Module' ? item.category?.title : null;
    const detail = item.summary || (item.type !== 'Function' ? item.description : null);
    return (
        <li role="option" aria-selected={selected} data-row={index}>
            <button
                type="button"
                onClick={() => onSelect(item)}
                onMouseMove={() => onHover(index)}
                className={`group w-full text-left mx-1.5 px-2.5 py-2 rounded-md flex items-center gap-3 transition-colors ${
                    selected ? 'bg-primary/10' : 'hover:bg-surface-muted'
                }`}
                style={{ width: 'calc(100% - 0.75rem)' }}
            >
                <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-md ring-1 ${style.tile}`}>
                    <Icon size={15} />
                </span>
                <span className="flex-1 min-w-0">
                    <span className="flex items-baseline gap-2 min-w-0">
                        <span className="text-sm font-medium text-text-main truncate">
                            <HighlightMatch text={item.title} tokens={tokens} />
                        </span>
                        {path && <span className="text-[11px] text-text-subtle truncate shrink">{path}</span>}
                    </span>
                    {detail && (
                        <span className="block text-xs text-text-muted truncate mt-0.5">
                            <HighlightMatch text={detail} tokens={tokens} />
                        </span>
                    )}
                </span>
                {item.shortcut && <KBD className="shrink-0">{item.shortcut}</KBD>}
                {selected && !item.shortcut && (
                    <CornerDownLeft size={14} className="shrink-0 text-text-subtle" aria-hidden="true" />
                )}
            </button>
        </li>
    );
};

/**
 * CommandPalette — Ctrl+K search over every calculation, module, category and app action.
 * Results are grouped by kind; calculations show their module path and the one-line summary
 * from the groundhog docs (loaded lazily on first open), which are also searched along with the
 * references, so "API end bearing" or "IS 2720" find the right tools. Recently used
 * calculations are listed when the box is empty.
 */
export const CommandPalette = ({ isOpen, onClose, onNavigate, onAction }) => {
    const [query, setQuery] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);
    const [docs, setDocs] = useState(null);
    const inputRef = useRef(null);
    const listRef = useRef(null);
    const { history } = useHistory();

    // The docs bundle (summaries, references) is only needed once the palette is used.
    useEffect(() => {
        if (!isOpen || docs) return;
        let cancelled = false;
        loadFunctionDocs().then((d) => { if (!cancelled) setDocs(d.functions || {}); }).catch(() => {});
        return () => { cancelled = true; };
    }, [isOpen, docs]);

    // Flat search index. Each item carries its own text plus its category/module ancestry and,
    // for calculations, the docs summary and references, so a query can match across levels
    // ("pile capacity": "Vertical Capacity" under "Pile calculations").
    const searchIndex = useMemo(() => {
        const items = [];
        const idWords = (id) => (id || '').replace(/[_-]+/g, ' ');
        const makeItem = (base) => {
            const ancestry = [base.category?.title, base.category?.description, base.subModule?.title,
                base.subModule?.description].filter(Boolean).join(' ');
            const haystack = [base.title, base.description, base.summary, base.references, idWords(base.id), ancestry]
                .filter(Boolean).join(' ').toLowerCase();
            const title = base.title.toLowerCase();
            return { ...base, haystack, haystackWords: words(haystack), titleLower: title, titleWords: words(title) };
        };

        items.push(makeItem({ type: 'Action', id: 'toggle_theme', title: 'Toggle dark / light mode', icon: Moon, action: 'toggleTheme' }));
        items.push(makeItem({ type: 'Action', id: 'open_history', title: 'Open calculation history', icon: History, shortcut: 'Ctrl+H', action: 'openHistory' }));
        items.push(makeItem({ type: 'Action', id: 'open_copilot', title: 'Open GeoAI assistant', icon: GeoAILogo, shortcut: 'Ctrl+Shift+A', action: 'openCopilot' }));
        items.push(makeItem({ type: 'Action', id: 'open_help', title: 'Help & keyboard shortcuts', icon: HelpCircle, action: 'openHelp' }));

        GEOTECHNICAL_MODULES.forEach((category) => {
            items.push(makeItem({ type: 'Category', id: category.id, title: category.title, description: category.description, category }));
            (category.items || []).forEach((subModule) => {
                items.push(makeItem({ type: 'Module', id: subModule.id || subModule.title, title: subModule.title, description: subModule.description, category, subModule }));
                (subModule.functions || []).forEach((func) => {
                    const doc = docs?.[func.id];
                    items.push(makeItem({
                        type: 'Function', id: func.id, title: func.title, description: func.description,
                        summary: doc?.summary, references: (doc?.references || []).join(' '),
                        category, subModule, func,
                    }));
                });
            });
        });
        return items;
    }, [docs]);

    const queryTokens = useMemo(() => query.toLowerCase().trim().split(/\s+/).filter(Boolean), [query]);

    // Grouped results: [{ label, items, recent? }]
    const groups = useMemo(() => {
        if (queryTokens.length === 0) {
            const byId = new Map(searchIndex.filter((i) => i.type === 'Function').map((i) => [i.id, i]));
            const seen = new Set();
            const recent = [];
            for (const h of history || []) {
                const item = byId.get(h.functionId);
                if (item && !seen.has(item.id)) {
                    seen.add(item.id);
                    recent.push(item);
                }
                if (recent.length >= MAX_RECENT) break;
            }
            return [
                { label: 'Recent', items: recent, recent: true },
                { label: 'Actions', items: searchIndex.filter((i) => i.type === 'Action') },
                { label: 'Categories', items: searchIndex.filter((i) => i.type === 'Category') },
            ].filter((g) => g.items.length > 0);
        }

        const q = queryTokens.join(' ');
        const scored = [];
        for (const item of searchIndex) {
            // Every token must match somewhere (as typed or as a synonym); the title counts double.
            let total = 0;
            for (const token of queryTokens) {
                let best = 0;
                for (const [term, weight] of [[token, 1], ...(SYNONYMS[token] || []).map((s) => [s, 0.9])]) {
                    const s = Math.max(scoreTerm(term, item.titleLower, item.titleWords) * 2,
                        scoreTerm(term, item.haystack, item.haystackWords)) * weight;
                    best = Math.max(best, s);
                }
                if (best === 0) { total = 0; break; }
                total += best;
            }
            if (total === 0) continue;
            if (item.titleLower === q) total += 100;
            else if (item.titleLower.startsWith(q)) total += 40;
            else if (item.titleLower.includes(q)) total += 20;
            scored.push({ item, score: total });
        }
        scored.sort((a, b) => b.score - a.score);
        return GROUPS.map(([type, label]) => ({
            label,
            items: scored.filter((s) => s.item.type === type).slice(0, MAX_PER_GROUP[type]).map((s) => s.item),
        })).filter((g) => g.items.length > 0);
    }, [queryTokens, searchIndex, history]);

    const rows = useMemo(() => groups.flatMap((g) => g.items), [groups]);

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
        listRef.current?.querySelector(`[data-row="${selectedIndex}"]`)?.scrollIntoView({ block: 'nearest' });
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
            setSelectedIndex((prev) => Math.min(prev + 1, rows.length - 1));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setSelectedIndex((prev) => Math.max(prev - 1, 0));
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (rows[selectedIndex]) handleSelect(rows[selectedIndex]);
        } else if (e.key === 'Escape') {
            onClose();
        }
    };

    let rowIndex = -1;
    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-[100] flex items-start justify-center px-4 pt-[12vh] bg-black/50 backdrop-blur-sm"
                    onClick={onClose}
                >
                    <motion.div
                        initial={{ opacity: 0, scale: 0.97, y: -8 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.97, y: -8 }}
                        transition={{ duration: 0.14 }}
                        className="w-full max-w-2xl bg-surface border border-border rounded-lg shadow-pop overflow-hidden"
                        onClick={(e) => e.stopPropagation()}
                        role="dialog"
                        aria-modal="true"
                        aria-label="Search"
                    >
                        {/* Search input */}
                        <div className="flex items-center gap-3 px-4 h-14 border-b border-border">
                            <Search size={18} className="text-primary shrink-0" />
                            <input
                                ref={inputRef}
                                type="text"
                                value={query}
                                onChange={(e) => { setQuery(e.target.value); setSelectedIndex(0); }}
                                onKeyDown={handleKeyDown}
                                placeholder="Search calculations, modules, standards…"
                                className="flex-1 bg-transparent text-text-main text-base outline-none placeholder:text-text-subtle"
                                autoComplete="off"
                                spellCheck={false}
                                role="combobox"
                                aria-expanded="true"
                                aria-controls="command-palette-results"
                            />
                            <KBD className="hidden sm:inline-flex">Esc</KBD>
                        </div>

                        {/* Results */}
                        <div ref={listRef} id="command-palette-results" className="max-h-[56vh] overflow-y-auto py-1.5" role="listbox">
                            {rows.length > 0 ? groups.map((group) => (
                                <section key={group.label} className="pb-1">
                                    <h3 className="px-4 pt-2 pb-1 text-[10px] font-semibold uppercase tracking-wider text-text-subtle">
                                        {group.label}
                                    </h3>
                                    <ul>
                                        {group.items.map((item) => {
                                            rowIndex += 1;
                                            const idx = rowIndex;
                                            return (
                                                <ResultRow
                                                    key={`${group.label}-${item.type}-${item.id}`}
                                                    item={item}
                                                    index={idx}
                                                    selected={selectedIndex === idx}
                                                    recent={group.recent}
                                                    tokens={queryTokens}
                                                    onSelect={handleSelect}
                                                    onHover={setSelectedIndex}
                                                />
                                            );
                                        })}
                                    </ul>
                                </section>
                            )) : (
                                <div className="py-10 text-center text-sm text-text-muted">
                                    <p>No results for “{query}”</p>
                                    <p className="text-xs mt-1 text-text-subtle">Try a method, a parameter (e.g. “phi”, “Su”) or a standard (e.g. “API”, “IS 2720”).</p>
                                </div>
                            )}
                        </div>

                        {/* Footer */}
                        <div className="flex items-center justify-between px-4 py-2 border-t border-border bg-surface-muted/50 text-[11px] text-text-muted">
                            <div className="flex items-center gap-3">
                                <span className="flex items-center gap-1"><KBD>↑</KBD><KBD>↓</KBD> navigate</span>
                                <span className="flex items-center gap-1"><KBD>↵</KBD> open</span>
                                <span className="flex items-center gap-1"><KBD>Esc</KBD> close</span>
                            </div>
                            <span>{queryTokens.length ? `${rows.length} result${rows.length !== 1 ? 's' : ''}` : 'Type to search'}</span>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};
