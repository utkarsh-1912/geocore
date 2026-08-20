/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

import React from 'react';

export const Button = ({ children, onClick, variant = 'primary', className = '', ...props }) => {
    const baseStyles = "px-4 py-2 rounded font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-background";

    const variants = {
        primary: "bg-primary hover:bg-primary-dark text-white focus:ring-primary",
        secondary: "bg-secondary hover:opacity-90 text-white focus:ring-secondary",
        outline: "border border-border text-text-muted hover:border-text-main hover:text-text-main",
        ghost: "text-text-muted hover:text-text-main hover:bg-background"
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
