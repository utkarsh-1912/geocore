/** Author: Utkarsh Gupta, License: GPL v3 */

import { useState, useEffect } from 'react';

export function useSearch(modules) {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [showSearch, setShowSearch] = useState(false);
    const [selectedIndex, setSelectedIndex] = useState(-1);

    useEffect(() => {
        if (!query.trim()) {
            setResults([]);
            return;
        }

        const searchQueryLower = query.toLowerCase();
        const foundResults = [];

        modules.forEach(category => {
            if (category.title.toLowerCase().includes(searchQueryLower)) {
                foundResults.push({ type: 'Category', item: category, category: category });
            }

            if (category.items) {
                category.items.forEach(subModule => {
                    if (subModule.title.toLowerCase().includes(searchQueryLower)) {
                        foundResults.push({ type: 'Module', item: subModule, category: category, subModule: subModule });
                    }

                    if (subModule.functions) {
                        subModule.functions.forEach(func => {
                            if (func.title.toLowerCase().includes(searchQueryLower)) {
                                foundResults.push({ type: 'Function', item: func, category: category, subModule: subModule, func: func });
                            }
                        });
                    }
                });
            }
        });

        setResults(foundResults.slice(0, 10)); // Limit results
        setSelectedIndex(-1);
    }, [query, modules]);

    const handleSelect = (result, navigateCallback) => {
        if (navigateCallback) {
            navigateCallback(result);
        }
        setQuery('');
    };

    const handleKeyDown = (e, navigateCallback) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setSelectedIndex(prev =>
                prev < results.length - 1 ? prev + 1 : prev
            );
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setSelectedIndex(prev => prev > 0 ? prev - 1 : 0);
        } else if (e.key === 'Enter') {
            if (selectedIndex >= 0 && selectedIndex < results.length) {
                handleSelect(results[selectedIndex], navigateCallback);
            }
        } else if (e.key === 'Escape') {
            setShowSearch(false);
            setQuery('');
        }
    };

    return { 
        query, 
        setQuery, 
        results, 
        selectedIndex, 
        setSelectedIndex, 
        showSearch, 
        setShowSearch, 
        handleKeyDown, 
        handleSelect 
    };
}
