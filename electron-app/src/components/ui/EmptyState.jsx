/** Author: Utkarsh Gupta, License: GPL v3 */
import React from 'react';

export function EmptyState({ 
  icon: Icon, 
  title, 
  description, 
  action,
  className = '' 
}) {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center ${className}`}>
      {Icon && (
        <div className="mb-4 rounded-full bg-background p-3 text-text-muted">
          <Icon size={32} />
        </div>
      )}
      <h3 className="mb-1 text-lg font-medium text-text-main">{title}</h3>
      {description && (
        <p className="mb-4 max-w-sm text-sm text-text-muted">{description}</p>
      )}
      {action && (
        <div>{action}</div>
      )}
    </div>
  );
}
