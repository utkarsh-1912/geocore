/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

import React from 'react';

export const Card = ({ children, title, className = '' }) => {
    return (
        <div className={`bg-surface rounded-lg border border-border p-4 shadow-lg ${className}`}>
            {title && (
                <div className="mb-4 border-b border-border pb-2">
                    <h3 className="text-lg font-semibold text-text-main">{title}</h3>
                </div>
            )}
            {children}
        </div>
    );
};
