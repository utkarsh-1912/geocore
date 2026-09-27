/** Author: Utkarsh Gupta, License: GPL v3 */

import {
    Database, ScanSearch, Columns3, Component, Droplets, Shovel, Activity,
    BookCheck, Layers, Anchor, FileText
} from 'lucide-react';

/** Icon per top-level module category (ids from config/geotechnicalModules.js). */
export const CATEGORY_ICONS = {
    general: Database,
    site_investigation: ScanSearch,
    piles: Columns3,
    shallow: Component,
    consolidation: Droplets,
    excavations: Shovel,
    dynamics: Activity,
    eurocode7: BookCheck,
    constitutive: Layers,
    pipelines: Anchor,
};

export const getCategoryIcon = (id) => CATEGORY_ICONS[id] || FileText;
