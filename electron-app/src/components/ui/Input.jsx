/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

import React from 'react';

export const Input = ({ label, type = 'text', value, onChange, placeholder, error, className = '', ...props }) => {
    return (
        <div className={`flex flex-col gap-1 ${className}`}>
            {label && <label className="text-sm text-text-muted">{label}</label>}
            <input
                type={type}
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                className={`bg-background border border-border rounded px-3 py-2 text-text-main placeholder-text-muted focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all ${error ? 'border-red-500' : ''}`}
                {...props}
            />
            {error && <span className="text-xs text-red-500">{error}</span>}
        </div>
    );
};
