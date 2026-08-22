import React from 'react';
import { Info } from 'lucide-react';

const FieldLabel = ({ input }) => (
  <label className="text-sm font-medium text-text-main mb-1 flex items-center gap-2">
    {input.name || input.id}
    {input.description && (
      <span className="text-text-muted hover:text-text-main cursor-help" title={input.description}>
        <Info size={13} />
      </span>
    )}
  </label>
);

export const FieldWrapper = ({ input, isEditMode, onEditField, validationError, className, children }) => (
  <div className={`relative ${isEditMode ? 'border border-dashed border-primary/20 rounded-md p-2' : ''} ${className || ''}`}>
    {isEditMode && <div className="absolute inset-0 z-10 cursor-pointer" onClick={() => onEditField(input)} />}
    <div className="flex flex-col">
      <FieldLabel input={input} />
      {children}
      {validationError && <span className="text-xs text-red-500 mt-1">{validationError}</span>}
    </div>
  </div>
);
