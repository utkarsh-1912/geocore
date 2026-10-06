/** Author: Utkarsh Gupta, License: GPL v3 */
import React from 'react';

export function KBD({ children, className = '' }) {
  return (
    <kbd className={`inline-flex items-center justify-center rounded-md border border-border bg-surface-muted px-1.5 py-0.5 font-mono text-[10px] font-medium text-text-muted shadow-sm ${className}`}>
      {children}
    </kbd>
  );
}
