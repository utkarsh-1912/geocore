/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};

export const ThemeProvider = ({ children }) => {
    // Default to dark mode
    const [isDarkMode, setIsDarkMode] = useState(true);

    // Load from local storage on mount
    useEffect(() => {
        const saved = localStorage.getItem('geocore_theme');
        if (saved) {
            try {
                setIsDarkMode(JSON.parse(saved));
            } catch (e) {
                console.error("Failed to parse theme", e);
            }
        }
    }, []);

    // Save to local storage on change
    useEffect(() => {
        localStorage.setItem('geocore_theme', JSON.stringify(isDarkMode));
    }, [isDarkMode]);

    const toggleTheme = () => {
        setIsDarkMode(prev => !prev);
    };

    return (
        <ThemeContext.Provider value={{ isDarkMode, toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
};
