/** Author: Utkarsh Gupta, License: GPL v3 */

import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';

/**
 * Starred methods (calculation functions, by function id) and folders (a module's group of calculations, by
 * "moduleId/groupId"), kept in this browser profile. Saved as [{type, id, added}]; an older plain list of
 * function ids is read as methods. Folder ids come from folderKey (config/navigation).
 */
const FavoritesContext = createContext();
const STORAGE_KEY = 'geocore_favorites';

const readSaved = () => {
    try {
        const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        if (!Array.isArray(saved)) return [];
        return saved
            .map((f) => (typeof f === 'string' ? { type: 'method', id: f, added: 0 } : f))
            .filter((f) => f && (f.type === 'method' || f.type === 'folder') && f.id);
    } catch (e) {
        console.error('Failed to load favorites', e);
        return [];
    }
};

export function FavoritesProvider({ children }) {
    const [entries, setEntries] = useState(readSaved);

    useEffect(() => {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
        } catch (e) {
            console.error('Failed to save favorites', e);
        }
    }, [entries]);

    const isFavorite = useCallback((id, type = 'method') => entries.some((f) => f.type === type && f.id === id), [entries]);

    const toggleFavorite = useCallback((id, type = 'method') => {
        setEntries((prev) => (prev.some((f) => f.type === type && f.id === id)
            ? prev.filter((f) => !(f.type === type && f.id === id))
            : [...prev, { type, id, added: Date.now() }]));
    }, []);

    const value = useMemo(() => ({
        entries,
        // Starred method ids, as before (callers that only know methods).
        favorites: entries.filter((f) => f.type === 'method').map((f) => f.id),
        isFavorite,
        toggleFavorite,
    }), [entries, isFavorite, toggleFavorite]);

    return <FavoritesContext.Provider value={value}>{children}</FavoritesContext.Provider>;
}

export function useFavorites() {
    const context = useContext(FavoritesContext);
    if (context === undefined) {
        throw new Error('useFavorites must be used within a FavoritesProvider');
    }
    return context;
}
