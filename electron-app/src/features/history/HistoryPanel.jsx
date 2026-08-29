/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useHistory } from '../../context/HistoryContext';
import { X, Clock, Trash2 } from 'lucide-react';
import { ConfirmationModal } from '../../components/common/ConfirmationModal';

export const HistoryPanel = ({ isOpen, onClose, onSelect }) => {
    const { history, clearHistory, removeFromHistory } = useHistory();
    const [itemToDelete, setItemToDelete] = useState(null);
    const [showClearAllConfirm, setShowClearAllConfirm] = useState(false);

    const handleConfirmDeleteItem = () => {
        if (itemToDelete) {
            removeFromHistory(itemToDelete.id);
            setItemToDelete(null);
        }
    };

    const handleConfirmClearAll = () => {
        clearHistory();
        setShowClearAllConfirm(false);
    };

    return (
        <>
            <AnimatePresence>
                {isOpen && (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 0.5 }}
                            exit={{ opacity: 0 }}
                            onClick={onClose}
                            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
                        />
                        <motion.div
                            initial={{ x: '100%' }}
                            animate={{ x: 0 }}
                            exit={{ x: '100%' }}
                            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                            className="fixed right-0 top-13 h-[calc(100vh-56px)] w-80 bg-surface border-l border-border z-50 shadow-2xl flex flex-col"
                        >
                            <div className="p-4 border-b border-border flex justify-between items-center bg-background">
                                <h3 className="font-semibold text-text-main flex items-center gap-2">
                                    <Clock size={16} /> History
                                </h3>
                                <button onClick={onClose} className="text-text-muted hover:text-text-main transition-colors">
                                    <X size={20} />
                                </button>
                            </div>

                            <div className="flex-1 overflow-y-auto p-4 space-y-3">
                                {history.length === 0 ? (
                                    <p className="text-center text-text-muted text-sm mt-10">No calculation history</p>
                                ) : (
                                    history.map((item) => (
                                        <div
                                            key={item.id}
                                            onClick={() => onSelect(item)}
                                            className="bg-background p-3 rounded border border-border hover:border-text-muted cursor-pointer transition-colors group relative flex flex-col gap-2"
                                        >
                                            <div className="flex justify-between items-start pr-6">
                                                <span className="font-medium text-primary text-sm line-clamp-2">{item.functionName}</span>
                                            </div>

                                            <div className="text-xs text-text-muted truncate">
                                                Inputs: {Object.keys(item.inputs || {}).join(', ')}
                                            </div>

                                            <div className="flex items-center gap-1 text-[10px] text-text-muted mt-1">
                                                <Clock size={10} />
                                                <span>{new Date(item.timestamp).toLocaleString()}</span>
                                            </div>

                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    setItemToDelete(item);
                                                }}
                                                className="absolute top-2 right-2 p-1 text-text-muted hover:text-red-500 rounded-full hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-all"
                                                title="Delete this record"
                                            >
                                                <X size={14} />
                                            </button>
                                        </div>
                                    ))
                                )}
                            </div>

                            {history.length > 0 && (
                                <div className="p-4 border-t border-border bg-background">
                                    <button
                                        onClick={() => setShowClearAllConfirm(true)}
                                        className="w-full py-2 text-xs text-red-500 hover:text-red-600 hover:bg-red-500/10 rounded transition-colors flex items-center justify-center gap-1.5 font-medium"
                                    >
                                        <Trash2 size={13} />
                                        <span>Clear History</span>
                                    </button>
                                </div>
                            )}
                        </motion.div>
                    </>
                )}
            </AnimatePresence>

            {/* Delete single item modal */}
            <ConfirmationModal
                isOpen={!!itemToDelete}
                title="Delete Calculation Record?"
                message={`Are you sure you want to delete "${itemToDelete?.functionName || 'this calculation'}" from your history?`}
                confirmText="Delete"
                cancelText="Cancel"
                variant="danger"
                onConfirm={handleConfirmDeleteItem}
                onCancel={() => setItemToDelete(null)}
            />

            {/* Clear all history modal */}
            <ConfirmationModal
                isOpen={showClearAllConfirm}
                title="Clear All History?"
                message="Are you sure you want to delete all calculation history records? This cannot be undone."
                confirmText="Clear All"
                cancelText="Cancel"
                variant="danger"
                onConfirm={handleConfirmClearAll}
                onCancel={() => setShowClearAllConfirm(false)}
            />
        </>
    );
};
