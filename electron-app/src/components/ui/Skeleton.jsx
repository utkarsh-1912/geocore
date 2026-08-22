/** Author: Utkarsh Gupta, License: GPL v3 */
import React from 'react';

export function Skeleton({ className = '', variant = 'rect' }) {
  const variantClasses = {
    text: 'h-4 rounded w-3/4',
    rect: 'rounded-md',
    circle: 'rounded-full',
  };

  return (
    <div 
      className={`animate-pulse bg-border/50 ${variantClasses[variant]} ${className}`} 
      aria-hidden="true"
    />
  );
}
