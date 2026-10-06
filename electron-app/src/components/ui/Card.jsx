/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React from 'react';

export const Card = ({ children, title, className = '' }) => {
    return (
        <div className={`min-w-0 max-w-full bg-surface rounded-md border border-border p-4 shadow-card ${className}`}>
            {title && (
                <div className="mb-4 border-b border-border/70 pb-2.5">
                    <h3 className="text-lg font-semibold text-text-main">{title}</h3>
                </div>
            )}
            {children}
        </div>
    );
};
