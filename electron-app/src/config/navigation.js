/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Which navigation the app shows, and lookups that work for either.
 *
 *  - "catalogue": calculations grouped by engineering task, generated from the backend calculation catalogue
 *    (python-backend/core/catalogue -> catalogueNavigation.json, `python -m core.catalogue`).
 *  - "classic": the original grouping, which mirrors the Groundhog library (geotechnicalModules.js).
 *
 * Both have the same shape (modules -> items -> functions) and the same function ids, so forms, /api/execute,
 * history and favourites behave identically in either; only grouping and labels differ. The choice is a
 * per-machine preference kept in localStorage.
 */
import { GEOTECHNICAL_MODULES } from './geotechnicalModules';
import catalogueNavigation from './catalogueNavigation.json';

export const NAV_MODES = {
    catalogue: { label: 'By task', title: 'Calculations grouped by engineering task' },
    classic: { label: 'Library', title: 'Classic grouping, as in the Groundhog library' },
};
export const DEFAULT_NAV_MODE = 'catalogue';
const NAV_MODE_KEY = 'geocore-nav-mode';

export const readNavMode = () => {
    try {
        const stored = localStorage.getItem(NAV_MODE_KEY);
        return stored && Object.prototype.hasOwnProperty.call(NAV_MODES, stored) ? stored : DEFAULT_NAV_MODE;
    } catch {
        return DEFAULT_NAV_MODE;
    }
};

export const storeNavMode = (mode) => {
    try {
        localStorage.setItem(NAV_MODE_KEY, mode);
    } catch {
        // storage unavailable: the choice lasts for this session only
    }
};

export const modulesFor = (mode) => (mode === 'classic' ? GEOTECHNICAL_MODULES : catalogueNavigation.modules);

/** {fn, cat, sub} for a function id in the given navigation, or null. */
export const findFunction = (modules, funcId) => {
    for (const cat of modules || []) {
        for (const sub of cat.items || []) {
            for (const fn of sub.functions || []) {
                if (fn.id === funcId) return { fn, cat, sub };
            }
        }
    }
    return null;
};

/** Stable id of a folder (a module's group of calculations), e.g. for favourites: "moduleId/groupId". */
export const folderKey = (category, subModule) => `${category?.id}/${subModule?.id || subModule?.title}`;

// ---------------------------------------------------------------------------- catalogue lookups

const catalogueIndex = (() => {
    const byFunction = new Map();
    const byCalculation = new Map();
    for (const mod of catalogueNavigation.modules) {
        for (const group of mod.items) {
            for (const fn of group.functions) {
                const entry = { ...fn, moduleId: mod.id, moduleTitle: mod.title, groupTitle: group.title };
                byFunction.set(fn.id, entry);
                if (!byCalculation.has(fn.calculation)) byCalculation.set(fn.calculation, []);
                byCalculation.get(fn.calculation).push(entry);
            }
        }
    }
    return { byFunction, byCalculation };
})();

/**
 * The catalogue calculation a function id is a method of, in either navigation mode:
 * {calculation, title, method, status, standards, methods: [entries of all its methods]} or null (internal).
 */
export const catalogueEntry = (functionId) => {
    const entry = catalogueIndex.byFunction.get(functionId);
    if (!entry) return null;
    const methods = catalogueIndex.byCalculation.get(entry.calculation) || [entry];
    return {
        calculation: entry.calculation,
        title: entry.calculation_title || entry.title,
        method: entry.method,
        status: entry.status,
        standards: entry.standards || [],
        data: entry.data || [],
        methods,
    };
};
