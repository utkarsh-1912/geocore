/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React from 'react';
import { Input } from '../../../components/ui/Input';
import { Check, Zap } from 'lucide-react';
import { FieldWrapper } from './FieldWrapper';

/**
 * ParameterChipsSelector — Interactive multi-parameter tag/chip selector
 * Extracted from SchemaForm lines 86-215
 */
export const ParameterChipsSelector = ({ name, value, availableColumns, onChange, required, disabled, placeholder }) => {
    const [rawMode, setRawMode] = React.useState(false);

    const selectedList = React.useMemo(() => {
        if (!value) return [];
        if (Array.isArray(value)) return value.map(v => String(v).trim()).filter(Boolean);
        return String(value)
            .split(/[,;\n]/)
            .map(s => s.trim())
            .filter(Boolean);
    }, [value]);

    const toggleColumn = (col) => {
        let newList;
        if (selectedList.includes(col)) {
            newList = selectedList.filter(c => c !== col);
        } else {
            newList = [...selectedList, col];
        }
        onChange(newList.join(', '));
    };

    const selectAll = () => {
        onChange(availableColumns.join(', '));
    };

    const selectNumeric = () => {
        const numeric = availableColumns.filter(c => {
            const lc = c.toLowerCase();
            return !lc.includes('soil type') && !lc.includes('description') && !lc.includes('layer') && !lc.includes('name') && !lc.includes('lithology') && !lc.includes('color');
        });
        onChange(numeric.join(', '));
    };

    const clearAll = () => {
        onChange('');
    };

    if (rawMode || availableColumns.length === 0) {
        return (
            <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                    <span className="text-[11px] text-text-muted">Comma-separated parameters:</span>
                    {availableColumns.length > 0 && (
                        <button
                            type="button"
                            onClick={() => setRawMode(false)}
                            className="text-[11px] text-primary hover:underline font-medium"
                        >
                            Switch to Tag Selection
                        </button>
                    )}
                </div>
                <Input
                    type="text"
                    value={value || ''}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={placeholder || "e.g. qc [MPa], fs [kPa]"}
                    required={required}
                    disabled={disabled}
                />
            </div>
        );
    }

    return (
        <div className="space-y-2 p-3 bg-surface/50 border border-border rounded-md">
            <div className="flex flex-wrap items-center justify-between gap-1.5 text-xs">
                <span className="text-text-muted font-medium">
                    Select parameters from profile ({selectedList.length} selected):
                </span>
                <div className="flex items-center gap-1.5">
                    <button
                        type="button"
                        onClick={selectNumeric}
                        className="text-[11px] px-2 py-0.5 rounded bg-primary/10 hover:bg-primary/20 text-primary font-medium transition-colors flex items-center gap-1"
                        title="Select typical numeric columns"
                    >
                        <Zap size={11} className="stroke-[2.5]" />
                        <span>Numeric</span>
                    </button>
                    <button
                        type="button"
                        onClick={selectAll}
                        className="text-[11px] px-2 py-0.5 rounded bg-primary/10 hover:bg-primary/20 text-primary font-medium transition-colors"
                    >
                        All
                    </button>
                    <button
                        type="button"
                        onClick={clearAll}
                        className="text-[11px] px-2 py-0.5 rounded bg-background hover:bg-border text-text-muted transition-colors"
                    >
                        Clear
                    </button>
                    <button
                        type="button"
                        onClick={() => setRawMode(true)}
                        className="text-[11px] text-text-muted hover:text-primary transition-colors underline"
                    >
                        Custom Text
                    </button>
                </div>
            </div>

            {/* Chips Grid */}
            <div className="flex flex-wrap gap-1.5 max-h-48 overflow-y-auto p-1.5 bg-background/50 rounded border border-border/50">
                {availableColumns.map(col => {
                    const isSelected = selectedList.includes(col);
                    return (
                        <button
                            key={col}
                            type="button"
                            onClick={() => toggleColumn(col)}
                            disabled={disabled}
                            className={`px-2.5 py-1 rounded text-xs font-medium transition-all flex items-center gap-1.5 ${
                                isSelected
                                    ? 'bg-primary text-white shadow-sm ring-1 ring-primary'
                                    : 'bg-surface border border-border text-text-main hover:border-primary/50 hover:bg-primary/5'
                            }`}
                        >
                            {isSelected && <Check size={12} className="stroke-[2.5]" />}
                            <span>{col}</span>
                        </button>
                    );
                })}
            </div>
        </div>
    );
};

export const ParameterChipsField = ({ input, value, onChange, isEditMode, onEditField, validationError, disabled, fileColumns }) => {
    return (
        <FieldWrapper input={input} isEditMode={isEditMode} onEditField={onEditField} validationError={validationError} className="md:col-span-2">
            <ParameterChipsSelector
                name={input.name}
                value={value}
                availableColumns={fileColumns || []}
                onChange={onChange}
                required={input.required}
                disabled={disabled}
                placeholder={input.placeholder || input.description}
            />
        </FieldWrapper>
    );
};
