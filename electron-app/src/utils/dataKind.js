/** Author: Utkarsh Gupta, License: GPL v3 */
// What an uploaded table holds, recorded with the object (python-backend core/state.py DATA_KINDS).
// GeoAI reads 'cpt' tables through its CPT tools and 'soil_profile' tables as the project stratigraphy.

import Papa from 'papaparse';
import * as XLSX from 'xlsx';

export const DATA_KIND_OPTIONS = [
    { value: 'soil_profile', label: 'Layered soil profile' },
    { value: 'cpt', label: 'CPT sounding' },
];

export const dataKindLabel = (kind) =>
    DATA_KIND_OPTIONS.find((o) => o.value === kind)?.label || 'Kind not recorded';

// Default only: the user always sees and can change the choice. A cone resistance (qc)
// column suggests a CPT, but a layered profile may also carry a representative qc.
export const suggestDataKind = (columns = []) => {
    const base = (c) => String(c).split(/[[(]/)[0].toLowerCase().replace(/[^a-z0-9]/g, '');
    const qcBases = new Set(['qc', 'coneresistance', 'conetipresistance', 'tipresistance']);
    return columns.some((c) => qcBases.has(base(c))) ? 'cpt' : 'soil_profile';
};

// Header row of a .csv / .xlsx / .xls file (empty list when it cannot be read).
export const readFileColumns = async (file) => {
    if (!file) return [];
    const ext = file.name.split('.').pop().toLowerCase();
    try {
        if (ext === 'csv') {
            return await new Promise((resolve) => {
                Papa.parse(file, {
                    preview: 1,
                    complete: (res) => resolve((res.data?.[0] || []).map(String)),
                    error: () => resolve([]),
                });
            });
        }
        if (ext === 'xlsx' || ext === 'xls') {
            const workbook = XLSX.read(new Uint8Array(await file.arrayBuffer()), { type: 'array', sheetRows: 1 });
            const sheet = workbook.Sheets[workbook.SheetNames[0]];
            return (XLSX.utils.sheet_to_json(sheet, { header: 1 })[0] || []).map(String);
        }
    } catch (err) {
        console.warn('Could not read file columns', err);
    }
    return [];
};
