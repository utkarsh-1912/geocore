/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 * 
 * Reusable Confirmation & Permission Modal Component.
 * Minimal border-radius, strict theme variables, and keyboard accessibility.
 */

import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, Trash2, X, AlertCircle } from 'lucide-react';

export const ConfirmationModal = ({
    isOpen,
    title = "Are you sure?",
    message = "This action cannot be undone.",
    confirmText = "Delete",
    cancelText = "Cancel",
    variant = "danger", // 'danger' | 'warning' | 'primary'
    icon: CustomIcon,
    onConfirm,
    onCancel,
    isLoading = false
}) => {
    // Keyboard accessibility: Escape to cancel, Enter to confirm
    useEffect(() => {
        if (!isOpen) return;

        const handleKeyDown = (e) => {
            if (e.key === 'Escape') {
                e.preventDefault();
                onCancel?.();
            } else if (e.key === 'Enter' && !isLoading) {
                e.preventDefault();
                onConfirm?.();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, isLoading, onConfirm, onCancel]);

    const IconComponent = CustomIcon || (variant === 'danger' ? Trash2 : AlertTriangle);

    const variantStyles = {
        danger: {
            iconBg: 'bg-red-500/10 text-red-500 border-red-500/20',
            buttonBg: 'bg-red-500 hover:bg-red-600 text-white',
        },
        warning: {
            iconBg: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
            buttonBg: 'bg-amber-500 hover:bg-amber-600 text-white',
        },
        primary: {
            iconBg: 'bg-primary/10 text-primary border-primary/20',
            buttonBg: 'bg-primary hover:bg-primary/90 text-white',
        }
    }[variant] || {
        iconBg: 'bg-red-500/10 text-red-500 border-red-500/20',
        buttonBg: 'bg-red-500 hover:bg-red-600 text-white',
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onCancel}
                        className="absolute inset-0"
                    />

                    {/* Modal Card */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 12 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 12 }}
                        transition={{ duration: 0.15 }}
                        className="relative w-full max-w-sm bg-surface border border-border rounded-md shadow-2xl overflow-hidden p-5 space-y-4 font-sans z-10"
                    >
                        <div className="flex items-start gap-3.5">
                            <div className={`p-2.5 rounded-full border shrink-0 ${variantStyles.iconBg}`}>
                                <IconComponent size={18} />
                            </div>

                            <div className="space-y-1 pr-4">
                                <h3 className="text-sm font-bold text-text-main">{title}</h3>
                                <div className="text-xs text-text-muted leading-relaxed">
                                    {message}
                                </div>
                            </div>

                            <button
                                onClick={onCancel}
                                className="absolute top-4 right-4 p-1 rounded text-text-muted hover:text-text-main hover:bg-background transition-colors"
                            >
                                <X size={14} />
                            </button>
                        </div>

                        <div className="flex items-center justify-end gap-2 pt-2 border-t border-border/60">
                            <button
                                type="button"
                                onClick={onCancel}
                                disabled={isLoading}
                                className="px-3 py-1.5 rounded text-xs font-medium text-text-muted hover:text-text-main border border-border hover:bg-background transition-colors disabled:opacity-50"
                            >
                                {cancelText}
                            </button>

                            <button
                                type="button"
                                onClick={onConfirm}
                                disabled={isLoading}
                                className={`px-3.5 py-1.5 rounded text-xs font-semibold shadow-xs transition-colors flex items-center gap-1.5 disabled:opacity-50 ${variantStyles.buttonBg}`}
                            >
                                {variant === 'danger' && <Trash2 size={12} />}
                                <span>{confirmText}</span>
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};

export default ConfirmationModal;
