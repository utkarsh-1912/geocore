/**
 * Author: Utkarsh Gupta
 * License: GPL v3
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
                className={`bg-input border border-border-strong rounded-md px-3 py-2 text-text-main placeholder-text-subtle focus:outline-none focus:border-primary/70 focus:ring-4 focus:ring-primary/15 transition-all ${error ? 'border-error' : ''}`}
                {...props}
            />
            {error && <span className="text-xs text-error">{error}</span>}
        </div>
    );
};
