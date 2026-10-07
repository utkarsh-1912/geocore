/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * GeoAI Copilot: the slide-out drawer. It hosts the same GeoAI workspace as the GeoAI tab
 * (compact mode), so the model selector, history, tracing and tool cards behave identically
 * and conversations are shared with the tab.
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GeoAIFullWindow } from './GeoAIFullWindow';

export const GeoAICopilot = ({ isOpen, onClose, onExpand, onSelectFunction, canOpenForm, currentContext }) => {
    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={onClose}
                className="fixed inset-0 bg-black/40 backdrop-blur-xs z-40"
            />

            <motion.div
                initial={{ x: '100%' }}
                animate={{ x: 0 }}
                exit={{ x: '100%' }}
                transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                className="fixed top-0 right-0 bottom-0 w-[min(640px,100vw)] bg-surface border-l border-border z-50 shadow-xl"
            >
                <GeoAIFullWindow
                    compact
                    onClose={onClose}
                    onExpand={onExpand}
                    onSelectFunction={onSelectFunction && ((tool, params) => { onSelectFunction(tool, params); onClose(); })}
                    canOpenForm={canOpenForm}
                    currentContext={currentContext}
                />
            </motion.div>
        </AnimatePresence>
    );
};
