/** Author: Utkarsh Gupta, License: GPL v3 */

import {
    DraftingCompass, Layers, Hammer, Building2, Hourglass, Shovel, AudioWaveform,
    Scale, ScrollText, ChartSpline, Waypoints, FileText
} from 'lucide-react';

/** Icon per top-level module category (ids from config/geotechnicalModules.js), chosen for civil / geotechnical meaning. */
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
};

export const getCategoryIcon = (id) => CATEGORY_ICONS[id] || FileText;
