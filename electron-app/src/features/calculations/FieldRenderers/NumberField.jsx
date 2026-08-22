/** Author: Utkarsh Gupta, License: GPL v3 */
import React from 'react';
import { FieldWrapper } from './FieldWrapper';
import { Input } from '@/components/ui/Input';

export const NumberField = ({ input, value, onChange, isEditMode, onEditField, validationError, disabled }) => {
  return (
    <FieldWrapper
      input={input}
      isEditMode={isEditMode}
      onEditField={onEditField}
      validationError={validationError}
    >
      <Input
        type={input.type === 'number' ? 'number' : 'text'}
        value={value || ''}
        onChange={(e) => onChange(input.type === 'number' ? Number(e.target.value) : e.target.value)}
        disabled={disabled}
        placeholder={input.placeholder || `Enter ${input.name}`}
        className="w-full"
      />
    </FieldWrapper>
  );
};
