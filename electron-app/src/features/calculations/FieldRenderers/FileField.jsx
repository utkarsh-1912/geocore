/** Author: Utkarsh Gupta, License: GPL v3 */
import React from 'react';
import { FieldWrapper } from './FieldWrapper';
import { Upload } from 'lucide-react';

export const FileField = ({ input, value, onChange, isEditMode, onEditField, validationError, disabled }) => {
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onChange(file);
    }
  };

  return (
    <FieldWrapper
      input={input}
      isEditMode={isEditMode}
      onEditField={onEditField}
      validationError={validationError}
    >
      <div className="flex items-center gap-2">
        <label className="flex items-center gap-2 px-3 py-2 bg-surface border border-border rounded cursor-pointer hover:bg-surface/80">
          <Upload size={16} className="text-text-muted" />
          <span className="text-sm">{value ? value.name : 'Choose File'}</span>
          <input
            type="file"
            className="hidden"
            disabled={disabled}
            onChange={handleFileChange}
            accept={input.accept}
          />
        </label>
      </div>
    </FieldWrapper>
  );
};
