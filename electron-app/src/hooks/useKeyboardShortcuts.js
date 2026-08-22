/** Author: Utkarsh Gupta, License: GPL v3 */

import { useEffect } from 'react';

export function useKeyboardShortcuts(shortcuts) {
    useEffect(() => {
        const handleGlobalKeyDown = (e) => {
            // Ctrl+H (or Cmd+H on Mac) to toggle history
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'h') {
                e.preventDefault();
                if (shortcuts.toggleHistory) shortcuts.toggleHistory();
            }

            // '/' to focus search bar if not already in an input
            if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
                e.preventDefault();
                if (shortcuts.focusSearch) {
                    shortcuts.focusSearch();
                } else {
                    const searchInput = document.querySelector('input[placeholder="Search..."]');
                    if (searchInput) searchInput.focus();
                }
            }

            // Ctrl + Shift + A to toggle GeoAI Copilot
            if (e.ctrlKey && e.shiftKey && (e.key === 'A' || e.key === 'a')) {
                e.preventDefault();
                if (shortcuts.toggleCopilot) shortcuts.toggleCopilot();
            }

            // Escape to close all modals/panels
            if (e.key === 'Escape') {
                if (shortcuts.closeAll) shortcuts.closeAll();
            }
        };

        window.addEventListener('keydown', handleGlobalKeyDown);
        return () => window.removeEventListener('keydown', handleGlobalKeyDown);
    }, [shortcuts]);
}
