/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React from 'react';
import { FieldWrapper } from './FieldWrapper';

/**
 * BooleanField — True/False select dropdown
 * Extracted from SchemaForm lines 920-938
 */
export const BooleanField = ({ input, value, onChange, isEditMode, onEditField, validationError, disabled }) => {
    return (
        <FieldWrapper input={input} isEditMode={isEditMode} onEditField={onEditField} validationError={validationError}>
            <select
                value={String(value ?? false)}
                onChange={(e) => onChange(e.target.value === 'true')}
                className="bg-background border border-border rounded px-3 py-2 text-text-main focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all w-full"
                required={input.required}
                disabled={disabled || isEditMode}
            >
                <option value="true">True</option>
                <option value="false">False</option>
            </select>
        </FieldWrapper>
    );
};
