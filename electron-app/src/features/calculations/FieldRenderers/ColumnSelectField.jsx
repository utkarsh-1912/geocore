/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React from 'react';
import { Input } from '../../../components/ui/Input';
import { Check } from 'lucide-react';
import { FieldWrapper } from './FieldWrapper';

/**
 * ColumnSelectDropdown — Smart single-column dropdown with custom text fallback
 */
const ColumnSelectDropdownInner = ({ name, value, availableColumns, onChange, required, disabled, placeholder }) => {
    const [isCustom, setIsCustom] = React.useState(false);

    return (
        <div className="space-y-1.5">
            {!isCustom ? (
                <div className="flex gap-2">
                    <select
                        value={value || ''}
                        onChange={(e) => {
                            if (e.target.value === '__custom__') {
                                setIsCustom(true);
                            } else {
                                onChange(e.target.value);
                            }
                        }}
                        className="bg-background border border-border rounded px-3 py-2 text-text-main focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all w-full text-sm"
                        disabled={disabled}
                        required={required}
                    >
                        <option value="">-- Select column --</option>
                        {availableColumns.map(col => (
                            <option key={col} value={col}>{col}</option>
                        ))}
                        <option value="__custom__">Add column name...</option>
                    </select>
                </div>
            ) : (
                <div className="flex gap-2 items-center">
                    <Input
                        type="text"
                        value={value || ''}
                        onChange={(e) => onChange(e.target.value)}
                        placeholder="Enter custom column name"
                        className="flex-1"
                        required={required}
                        disabled={disabled}
                    />
                    <button
                        type="button"
                        onClick={() => setIsCustom(false)}
                        className="text-xs text-primary hover:underline px-2 shrink-0"
                    >
                        Back to List
                    </button>
                </div>
            )}
        </div>
    );
};

export const ColumnSelectField = ({ input, value, onChange, isEditMode, onEditField, validationError, disabled, fileColumns }) => {
    return (
        <FieldWrapper input={input} isEditMode={isEditMode} onEditField={onEditField} validationError={validationError}>
            {fileColumns && fileColumns.length > 0 ? (
                <ColumnSelectDropdownInner
                    name={input.name}
                    value={value}
                    availableColumns={fileColumns}
                    onChange={onChange}
                    required={input.required}
                    disabled={disabled}
                />
            ) : (
                <>
                    <select
                        value={value || ''}
                        onChange={(e) => onChange(e.target.value)}
                        className="bg-background border border-border rounded px-3 py-2 text-text-main focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                        disabled={true}
                    >
                        <option value="">Select a column...</option>
                    </select>
                    <span className="text-xs text-text-muted mt-1">Upload a file or select SoilProfile to see columns</span>
                </>
            )}
        </FieldWrapper>
    );
};
