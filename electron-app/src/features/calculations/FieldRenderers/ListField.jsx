/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React from 'react';
import { FieldWrapper } from './FieldWrapper';

/**
 * ListField — Monospaced multiline array input
 * Extracted from SchemaForm lines 902-919
 */
export const ListField = ({ input, value, onChange, isEditMode, onEditField, validationError, disabled }) => {
    return (
        <FieldWrapper input={input} isEditMode={isEditMode} onEditField={onEditField} validationError={validationError}>
            <textarea
                value={value || ''}
                onChange={(e) => onChange(e.target.value)}
                placeholder={input.description || 'Enter values separated by commas or new lines...'}
                className="bg-background border border-border rounded px-3 py-2 text-text-main font-mono text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all w-full min-h-[80px]"
                required={input.required}
                disabled={disabled || isEditMode}
            />
            <span className="text-[10px] text-text-muted mt-1">Example: 10, 20, 30.5</span>
        </FieldWrapper>
    );
};
