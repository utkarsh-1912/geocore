/** Author: Utkarsh Gupta, License: GPL v3 */

import {
    DraftingCompass, Layers, Hammer, Building2, Hourglass, Shovel, AudioWaveform,
    Scale, ScrollText, ChartSpline, Waypoints, FileText
} from 'lucide-react';

/** Icon per top-level module (ids from config/geotechnicalModules.js and config/catalogueNavigation.json), chosen for civil / geotechnical meaning. */
export const CATEGORY_ICONS = {
    general: DraftingCompass,        // engineering utilities: profiles, grids, plotting, mapping
    site_investigation: Layers,      // ground stratigraphy: boreholes, CPT / SPT logs, lab results
    piles: Hammer,                   // pile driving
    shallow: Building2,              // structure founded on footings and rafts
    consolidation: Hourglass,        // settlement over time
    excavations: Shovel,
    dynamics: AudioWaveform,         // seismograph trace: earthquakes, cyclic loading
    eurocode7: Scale,                // limit states: actions balanced against resistances
    indian_standards: ScrollText,    // BIS codes
    constitutive: ChartSpline,       // stress-strain curves
    pipelines: Waypoints,            // pipeline / cable routes

    // Catalogue navigation (python-backend/core/catalogue/data): same icons as the classic modules they replace.
    ground_data: DraftingCompass,
    ground_characterisation: Layers,
    shallow_foundations: Building2,
    settlement_consolidation: Hourglass,
    deep_foundations: Hammer,
    retaining_excavations: Shovel,
    dynamics_liquefaction: AudioWaveform,
    material_models: ChartSpline,
    offshore_pipelines: Waypoints,
    design_basis: Scale,
};

export const getCategoryIcon = (id) => CATEGORY_ICONS[id] || FileText;
