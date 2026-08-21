/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */


import React, { useState, useEffect } from 'react';
import { X, Save, Upload, Plus, Trash, Settings, FileText, CheckCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const REGEX_PATTERNS = [
    { label: 'None', value: '' },
    { label: 'Positive Number', value: '^\\d*\\.?\\d+$' },
    { label: 'Integer', value: '^-?\\d+$' },
    { label: 'Email', value: '^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$' },
    { label: 'URL', value: '^(https?|ftp):\\/\\/[^\\s/$.?#].[^\\s]*$' },
    { label: 'Phone', value: '^\\+?[1-9]\\d{1,14}$' },
    { label: 'Alphanumeric', value: '^[a-zA-Z0-9]+$' }
];

const SchemaEditor = ({ isOpen, onClose, field, onSave, functionId }) => {
    const [formData, setFormData] = useState({
        label: '',
        description: '',
        unit: '',
        placeholder: '',
        validationRegex: ''
    });

    useEffect(() => {
        if (field) {
            setFormData({
                label: field.label || '',
                description: field.description || '',
                unit: field.unit || '',
                placeholder: field.placeholder || '',
                validationRegex: field.validationRegex || ''
            });
        }
    }, [field]);

    if (!isOpen || !field) return null;

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSave = () => {
        onSave(functionId, field.name, formData);
        onClose();
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 0.5 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/20 backdrop-blur-sm z-50"
                    />
                    <motion.div
                        initial={{ x: 20, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: 20, opacity: 0 }}
                        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                        className="fixed right-0 top-13 bottom-auto max-h-[calc(100vh-56px)] w-96 bg-surface border border-border z-50 shadow-2xl flex flex-col overflow-hidden"
                    >
                        <div className="p-4 border-b border-border flex justify-between items-center bg-background shrink-0">
                            <h3 className="font-semibold text-lg text-text-main">Edit Field: {field.name}</h3>
                            <button onClick={onClose} className="p-1 hover:bg-secondary/20 rounded-full text-text-muted transition-colors">
                                <X size={20} />
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto p-4 space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-text-main">Label</label>
                                <input
                                    name="label"
                                    value={formData.label}
                                    onChange={handleChange}
                                    className="w-full bg-background border border-border rounded px-3 py-2 text-sm text-text-main focus:ring-1 focus:ring-primary focus:outline-none"
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-text-main">Unit</label>
                                    <input
                                        name="unit"
                                        value={formData.unit}
                                        onChange={handleChange}
                                        className="w-full bg-background border border-border rounded px-3 py-2 text-sm text-text-main focus:ring-1 focus:ring-primary focus:outline-none"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-text-main">Placeholder</label>
                                    <input
                                        name="placeholder"
                                        value={formData.placeholder}
                                        onChange={handleChange}
                                        className="w-full bg-background border border-border rounded px-3 py-2 text-sm text-text-main focus:ring-1 focus:ring-primary focus:outline-none"
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-text-main">Description (HTML Supported)</label>
                                <textarea
                                    name="description"
                                    value={formData.description}
                                    onChange={handleChange}
                                    rows={4}
                                    className="w-full bg-background border border-border rounded px-3 py-2 text-sm text-text-main focus:ring-1 focus:ring-primary focus:outline-none"
                                    placeholder="Enter help text or documentation..."
                                />
                            </div>

                            <div className="space-y-2 pt-2 border-t border-border">
                                <label className="text-sm font-medium text-text-main flex items-center gap-2">
                                    Validation Pattern (Regex)
                                </label>
                                <select
                                    onChange={(e) => handleChange({ target: { name: 'validationRegex', value: e.target.value } })}
                                    value={REGEX_PATTERNS.find(p => p.value === formData.validationRegex) ? formData.validationRegex : 'custom'}
                                    className="w-full bg-background border border-border rounded px-3 py-2 text-sm text-text-main mb-2 focus:ring-1 focus:ring-primary focus:outline-none"
                                >
                                    {REGEX_PATTERNS.map(p => (
                                        <option key={p.label} value={p.value}>{p.label}</option>
                                    ))}
                                    <option value="custom">Custom...</option>
                                </select>

                                <input
                                    name="validationRegex"
                                    value={formData.validationRegex}
                                    onChange={handleChange}
                                    placeholder="e.g. ^[0-9]+$"
                                    className="w-full bg-background border border-border rounded px-3 py-2 text-sm font-mono text-text-main focus:ring-1 focus:ring-primary focus:outline-none"
                                />
                            </div>
                        </div>

                        <div className="p-4 border-t border-border bg-background flex gap-2 shrink-0">
                            <button
                                onClick={handleSave}
                                className="flex-1 bg-primary hover:bg-primary/90 text-white rounded py-2 text-sm font-medium flex items-center justify-center gap-2 transition-colors shadow-sm"
                            >
                                <Save size={16} /> Save Changes
                            </button>
                            <button
                                onClick={onClose}
                                className="flex-1 bg-secondary/20 hover:bg-secondary/30 text-text-main rounded py-2 text-sm font-medium flex items-center justify-center gap-2 transition-colors"
                            >
                                Cancel
                            </button>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};

export default SchemaEditor;
