/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React from 'react';

export const Button = ({ children, onClick, variant = 'primary', className = '', ...props }) => {
    const baseStyles = "px-4 py-2 rounded-md font-medium transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed";

    const variants = {
        primary: "btn-brand font-semibold focus-visible:ring-primary",
        secondary: "bg-secondary hover:opacity-90 text-white focus:ring-secondary",
        outline: "border border-border bg-surface/60 text-text-muted hover:border-primary/50 hover:text-text-main",
        ghost: "text-text-muted hover:text-text-main hover:bg-surface-muted"
    };

    return (
        <button
            className={`${baseStyles} ${variants[variant]} ${className}`}
            onClick={onClick}
            {...props}
        >
            {children}
        </button>
    );
};
