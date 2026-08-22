/** Author: Utkarsh Gupta, License: GPL v3 */
import React from 'react';

export function Textarea({ 
  value, 
  onChange, 
  placeholder, 
  rows = 4, 
  label, 
  error,
  className = '',
  ...props 
}) {
  return (
    <div className={`flex flex-col gap-1.5 ${className}`}>
      {label && (
        <label className="text-sm font-medium text-text-main">
          {label}
        </label>
      )}
      <textarea
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        rows={rows}
        className={`w-full rounded-md border bg-surface px-3 py-2 text-sm text-text-main placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-primary ${
          error ? 'border-error focus:ring-error' : 'border-border'
        }`}
        {...props}
      />
      {error && (
        <span className="text-xs text-error">{error}</span>
      )}
    </div>
  );
}
