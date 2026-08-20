/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

import React, { createContext, useContext, useState, useEffect } from 'react';

const HistoryContext = createContext();

export const useHistory = () => {
    const context = useContext(HistoryContext);
    if (!context) {
        throw new Error('useHistory must be used within a HistoryProvider');
    }
    return context;
};

export const HistoryProvider = ({ children }) => {
    const [history, setHistory] = useState([]);

    // Load from local storage on mount
    useEffect(() => {
        const saved = localStorage.getItem('geocore_history');
        if (saved) {
            try {
                setHistory(JSON.parse(saved));
            } catch (e) {
                console.error("Failed to parse history", e);
            }
        }
    }, []);

    // Save to local storage on change
    useEffect(() => {
        try {
            localStorage.setItem('geocore_history', JSON.stringify(history));
        } catch (e) {
            console.error("Failed to save history to localStorage", e);
            // Optional: If quota exceeded, could trim older entries
        }
    }, [history]);

    const addToHistory = (item) => {
        console.log("HistoryContext: Adding item", item);
        const newItem = {
            id: Date.now().toString(),
            timestamp: new Date().toISOString(),
            ...item
        };
        // Limit to last 50 items to prevent storage overflow
        setHistory(prev => [newItem, ...prev].slice(0, 50));
    };

    const removeFromHistory = (id) => {
        setHistory(prev => prev.filter(item => item.id !== id));
    };

    const clearHistory = () => {
        setHistory([]);
    };

    return (
        <HistoryContext.Provider value={{ history, addToHistory, removeFromHistory, clearHistory }}>
            {children}
        </HistoryContext.Provider>
    );
};
