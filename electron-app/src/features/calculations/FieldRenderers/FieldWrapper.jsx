import React from 'react';
import { Info } from 'lucide-react';
import { getParameterNotation } from '@/utils/geoNotation';
import { UnitBadge } from '@/components/ui/UnitBadge';

const FieldLabel = ({ input, currentValue, onConvertValue }) => {
  const notation = getParameterNotation(input.id || input.name, input.name);

  return (
    <div className="flex items-center justify-between mb-1 gap-1.5">
      <label className="text-xs sm:text-sm font-medium text-text-main flex items-center gap-1.5 truncate">
        {notation?.symbol && (
          <span className="px-1 py-0.2 rounded bg-primary/10 border border-primary/20 text-primary font-mono text-xs font-bold shrink-0" title={notation.label}>
            {notation.symbol}
          </span>
        )}
        <span className="truncate">{input.name || input.id}</span>
        {input.description && (
          <span className="text-text-muted hover:text-text-main cursor-help shrink-0" title={input.description}>
            <Info size={12} />
          </span>
        )}
      </label>

      {input.unit && (
        <UnitBadge
          unit={input.unit}
          currentValue={currentValue}
          onConvertValue={onConvertValue}
          className="shrink-0"
        />
      )}
    </div>
  );
};

export const FieldWrapper = ({ input, value, onChange, isEditMode, onEditField, validationError, className, children }) => {
  const handleUnitConvert = (newVal) => {
    if (onChange) {
      onChange(newVal);
    }
  };

  return (
    <div className={`relative ${isEditMode ? 'border border-dashed border-primary/20 rounded-md p-2' : ''} ${className || ''}`}>
      {isEditMode && <div className="absolute inset-0 z-10 cursor-pointer" onClick={() => onEditField && onEditField(input)} />}
      <div className="flex flex-col">
        <FieldLabel input={input} currentValue={value} onConvertValue={handleUnitConvert} />
        {children}
        {validationError && <span className="text-xs text-red-500 mt-1">{validationError}</span>}
      </div>
    </div>
  );
};

