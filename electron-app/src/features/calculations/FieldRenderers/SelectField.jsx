/** Author: Utkarsh Gupta, License: GPL v3 */
import React from 'react';
import { FieldWrapper } from './FieldWrapper';

export const SelectField = ({ input, value, onChange, isEditMode, onEditField, validationError, disabled }) => {
  return (
    <FieldWrapper
      input={input}
      isEditMode={isEditMode}
      onEditField={onEditField}
      validationError={validationError}
    >
      <select
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="w-full p-2 rounded bg-surface border border-border text-text-main"
      >
        <option value="">Select an option</option>
        {input.options?.map((opt, idx) => (
          <option key={idx} value={opt.value || opt}>
            {opt.label || opt}
          </option>
        ))}
      </select>
    </FieldWrapper>
  );
};
