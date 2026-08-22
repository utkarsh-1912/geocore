/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React, { useState, useEffect } from 'react';
import { HelpCircle, Edit2, Settings } from 'lucide-react';

/**
 * ObjectSelector — Fetches available objects from backend registry
 * Extracted from SchemaForm lines 21-65
 */
const ObjectSelectorInner = ({ objectType, value, onChange, required, refreshTrigger, disabled }) => {
    const [options, setOptions] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!objectType) return;
        fetchObjects();
    }, [objectType, refreshTrigger]);

    const fetchObjects = () => {
        setLoading(true);
        fetch(`http://127.0.0.1:8000/api/objects/${objectType}`)
            .then(res => res.json())
            .then(data => {
                setOptions(data.objects || []);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to load objects", err);
                setLoading(false);
            });
    };

    return (
        <select
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="bg-background border border-border rounded px-3 py-2 text-text-main focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all w-full"
            required={required}
            disabled={disabled}
        >
            <option value="">Select {objectType}...</option>
            {value && !options.find(o => o.id === value) && (
                <option value={value}>Profile {value.substring(0, 8)}</option>
            )}
            {options.map(opt => (
                <option key={opt.id} value={opt.id}>
                    {opt.name || `${objectType} (${opt.id.substring(0, 6)}...)`}
                </option>
            ))}
            {options.length === 0 && !loading && <option disabled>No {objectType}s created yet</option>}
        </select>
    );
};

export const ObjectSelectField = ({ input, value, onChange, isEditMode, onEditField, validationError, disabled, refreshTrigger, onManageClick }) => {
    return (
        <div className={`relative ${isEditMode ? 'border border-dashed border-primary/20 rounded-md p-2' : ''}`}>
            {isEditMode && (
                <div
                    className="absolute inset-0 z-10 cursor-pointer"
                    onClick={() => onEditField(input)}
                    title="Click to Edit"
                />
            )}
            <div className="flex flex-col">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 mb-1 group/label">
                        <label className="text-sm text-text-muted flex items-center gap-1 cursor-default">
                            {input.label || input.name}
                            {input.required && <span className="text-primary font-bold">*</span>}
                        </label>

                        {input.description && (
                            <div className="relative group/tooltip">
                                <HelpCircle size={12} className="text-text-muted cursor-help" />
                                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-2 bg-surface border border-border rounded shadow-xl text-xs text-text-main opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-all z-50 pointer-events-none">
                                    <div dangerouslySetInnerHTML={{ __html: input.description }} />
                                </div>
                            </div>
                        )}

                        {isEditMode && (
                            <button
                                type="button"
                                onClick={(e) => {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    onEditField(input);
                                }}
                                className="p-0.5 rounded hover:bg-primary/10 text-text-muted hover:text-primary transition-all"
                                title="Edit Field"
                            >
                                <Edit2 size={10} />
                            </button>
                        )}
                    </div>

                    {input.objectType === 'SoilProfile' && onManageClick && (
                        <button
                            type="button"
                            onClick={onManageClick}
                            className="text-xs text-primary hover:underline flex items-center gap-1"
                            disabled={isEditMode}
                        >
                            <Settings size={12} /> Manage
                        </button>
                    )}
                </div>
                <ObjectSelectorInner
                    objectType={input.objectType}
                    value={value || ''}
                    onChange={onChange}
                    required={input.required}
                    refreshTrigger={refreshTrigger}
                    disabled={disabled || isEditMode}
                />
            </div>
        </div>
    );
};
