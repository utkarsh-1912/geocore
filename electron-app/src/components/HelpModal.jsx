/**
 * Author: Utkarsh Gupta
 * License: GPL v2
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
                        className="relative w-full max-w-2xl bg-surface border border-border rounded-lg shadow-2xl overflow-hidden"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-4 border-b border-border bg-background/50">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-primary/10 rounded-lg text-primary">
                                    <HelpCircle size={24} />
                                </div>
                                <div>
                                    <h2 className="text-xl font-bold text-text-main font-display">System Help & Guides</h2>
                                    <p className="text-sm text-text-muted">Explore features and keyboard shortcuts</p>
                                </div>
                            </div>
                            <button
                                onClick={onClose}
                                className="p-2 hover:bg-background rounded-full text-text-muted hover:text-text-main transition-colors"
                            >
                                <X size={20} />
                            </button>
                        </div>

                        {/* Content */}
                        <div className="p-6 max-h-[70vh] overflow-y-auto">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Section 1: Getting Started */}
                                <section className="space-y-4">
                                    <div className="flex items-center gap-2 text-primary font-bold">
                                        <Info size={18} />
                                        <h3>Getting Started</h3>
                                    </div>
                                    <ul className="space-y-3 text-sm text-text-muted">
                                        <li className="flex gap-2">
                                            <span className="font-bold text-primary">1.</span>
                                            Select a category from the dashboard (e.g., Shallow Foundations).
                                        </li>
                                        <li className="flex gap-2">
                                            <span className="font-bold text-primary">2.</span>
                                            Choose a calculation module.
                                        </li>
                                        <li className="flex gap-2">
                                            <span className="font-bold text-primary">3.</span>
                                            Fill in the input parameters (units are provided in labels).
                                        </li>
                                        <li className="flex gap-2">
                                            <span className="font-bold text-primary">4.</span>
                                            Click 'Calculate' to see the results and plot.
                                        </li>
                                    </ul>
                                </section>

                                {/* Section 2: Shortcuts */}
                                <section className="space-y-4">
                                    <div className="flex items-center gap-2 text-primary font-bold">
                                        <Keyboard size={18} />
                                        <h3>Keyboard Shortcuts</h3>
                                    </div>
                                    <div className="space-y-2">
                                        {[
                                            { key: '/', desc: 'Focus search bar' },
                                            { key: '↑/↓', desc: 'Navigate search results' },
                                            { key: 'Enter', desc: 'Select search result' },
                                            { key: 'Esc', desc: 'Close modals / search' },
                                            { key: 'Ctrl+H', desc: 'Toggle history' }
                                        ].map((shortcut, i) => (
                                            <div key={i} className="flex justify-between items-center text-sm p-2 bg-background/50 rounded-lg border border-border/50">
                                                <span className="text-text-muted">{shortcut.desc}</span>
                                                <kbd className="px-2 py-1 bg-surface border border-border rounded text-xs font-mono font-bold text-primary">
                                                    {shortcut.key}
                                                </kbd>
                                            </div>
                                        ))}
                                    </div>
                                </section>
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="p-4 bg-background/80 border-t border-border text-center">
                            <button
                                onClick={onClose}
                                className="px-6 py-2 bg-primary text-white font-bold rounded-lg hover:bg-primary/90 transition-all shadow-lg shadow-primary/20"
                            >
                                Got it!
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};
