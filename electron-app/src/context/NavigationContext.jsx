/** Author: Utkarsh Gupta, License: GPL v3 */

import React, { createContext, useContext, useState, useMemo } from 'react';
import { getSchema } from '@/features/calculations/schemas';

const NavigationContext = createContext();

export function NavigationProvider({ children }) {
    const [viewState, setViewState] = useState('home');
    const [activeCategory, setActiveCategory] = useState(null);
    const [activeSubModule, setActiveSubModule] = useState(null);
    const [activeFunction, setActiveFunction] = useState(null);
    const [currentSchema, setCurrentSchema] = useState(null);

    const goHome = () => {
        setViewState('home');
        setActiveCategory(null);
        setActiveSubModule(null);
        setActiveFunction(null);
        setCurrentSchema(null);
    };

    const selectCategory = (category) => {
        setActiveCategory(category);
        setViewState('category');
        setActiveSubModule(null);
        setActiveFunction(null);
        setCurrentSchema(null);
    };

    const selectSubModule = (subModule) => {
        setActiveSubModule(subModule);
        setViewState('sub-module');
        setActiveFunction(null);
        setCurrentSchema(null);
    };

    const selectFunction = (func) => {
        setActiveFunction(func);
        setViewState('function');
        const schema = getSchema(func.id);
        setCurrentSchema(schema);
    };

    const breadcrumbs = useMemo(() => {
        const crumbs = [];
        if (activeCategory) crumbs.push({ label: activeCategory.title, action: () => selectCategory(activeCategory), state: 'category' });
        if (activeSubModule) crumbs.push({ label: activeSubModule.title, action: () => selectSubModule(activeSubModule), state: 'sub-module' });
        if (activeFunction) crumbs.push({ label: activeFunction.title, action: () => selectFunction(activeFunction), state: 'function' });
        return crumbs;
    }, [activeCategory, activeSubModule, activeFunction]);

    const value = {
        viewState,
        activeCategory,
        activeSubModule,
        activeFunction,
        currentSchema,
        goHome,
        selectCategory,
        selectSubModule,
        selectFunction,
        breadcrumbs,
        setViewState, // Exposing just in case but ideally use the specific select functions
        setActiveCategory,
        setActiveSubModule,
        setActiveFunction,
        setCurrentSchema
    };

    return (
        <NavigationContext.Provider value={value}>
            {children}
        </NavigationContext.Provider>
    );
}

export function useNavigation() {
    const context = useContext(NavigationContext);
    if (context === undefined) {
        throw new Error('useNavigation must be used within a NavigationProvider');
    }
    return context;
}
