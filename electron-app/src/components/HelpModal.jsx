/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, HelpCircle, Keyboard, Info } from 'lucide-react';

export const HelpModal = ({ isOpen, onClose }) => {
    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
                    />

                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="relative w-full max-w-2xl bg-surface border border-border rounded-md shadow-2xl overflow-hidden"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-4 border-b border-border bg-background/50">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-primary/10 rounded text-primary">
                                    <HelpCircle size={22} />
                                </div>
                                <div>
                                    <h2 className="text-lg font-bold text-text-main font-display">System Help & Guides</h2>
                                    <p className="text-xs text-text-muted">Explore workstation features and keyboard shortcuts</p>
                                </div>
                            </div>
                            <button
                                onClick={onClose}
                                className="p-1.5 hover:bg-background rounded text-text-muted hover:text-text-main transition-colors"
                            >
                                <X size={18} />
                            </button>
                        </div>

                        {/* Content */}
                        <div className="p-6 max-h-[70vh] overflow-y-auto space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Section 1: Getting Started */}
                                <section className="space-y-3 bg-surface/50 border border-border rounded-md p-4">
                                    <div className="flex items-center gap-2 text-primary font-bold text-sm">
                                        <Info size={16} />
                                        <h3>Getting Started</h3>
                                    </div>
                                    <ul className="space-y-2 text-xs text-text-muted">
                                        <li className="flex gap-2">
                                            <span className="font-bold text-primary">1.</span>
                                            Select a category from the sidebar or dashboard.
                                        </li>
                                        <li className="flex gap-2">
                                            <span className="font-bold text-primary">2.</span>
                                            Choose an engineering calculation routine.
                                        </li>
                                        <li className="flex gap-2">
                                            <span className="font-bold text-primary">3.</span>
                                            Fill in the input parameters (units and ranges provided in labels).
                                        </li>
                                        <li className="flex gap-2">
                                            <span className="font-bold text-primary">4.</span>
                                            Click <strong>Calculate</strong> to inspect results, tables, and interactive Plotly graphs.
                                        </li>
                                    </ul>
                                </section>

                                {/* Section 2: Shortcuts */}
                                <section className="space-y-3 bg-surface/50 border border-border rounded-md p-4">
                                    <div className="flex items-center gap-2 text-primary font-bold text-sm">
                                        <Keyboard size={16} />
                                        <h3>Keyboard Shortcuts</h3>
                                    </div>
                                    <div className="space-y-1.5">
                                        {[
                                            { key: 'Ctrl+K', desc: 'Command search & actions' },
                                            { key: 'Ctrl+H', desc: 'Toggle calculation history' },
                                            { key: '↑ / ↓', desc: 'Navigate list selections' },
                                            { key: 'Enter', desc: 'Confirm & execute' },
                                            { key: 'Esc', desc: 'Close dialogs & overlays' }
                                        ].map((shortcut, i) => (
                                            <div key={i} className="flex justify-between items-center text-xs p-1.5 bg-background rounded border border-border/50">
                                                <span className="text-text-muted">{shortcut.desc}</span>
                                                <kbd className="px-1.5 py-0.5 bg-surface border border-border rounded text-[10px] font-mono font-bold text-primary">
                                                    {shortcut.key}
                                                </kbd>
                                            </div>
                                        ))}
                                    </div>
                                </section>
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="p-3 bg-background/80 border-t border-border flex justify-end">
                            <button
                                onClick={onClose}
                                className="px-4 py-1.5 bg-primary text-white text-xs font-semibold rounded hover:bg-primary/90 transition-all shadow-sm"
                            >
                                Got it
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};
