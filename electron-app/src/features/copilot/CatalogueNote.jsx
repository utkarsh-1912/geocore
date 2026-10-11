/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Under a GeoAI calculation result: the catalogue calculation and method the tool ran, a known issue if it has one
 * (verified/corrected are internal QA states and are not shown), the method's standing conditions, and applicability
 * warnings for the inputs used (python-backend/core/catalogue/applicability.py). Renders nothing without either.
 */
import React from 'react';
import { AlertTriangle } from 'lucide-react';

export const CatalogueNote = ({ catalogue, warnings }) => {
    const list = Array.isArray(warnings) ? warnings : [];
    if (!catalogue && !list.length) return null;
    return (
        <div className="space-y-1 text-[11px]" data-catalogue-note>
            {catalogue && (
                <p className="text-text-muted">
                    {catalogue.calculation}{catalogue.method !== catalogue.calculation ? ` · ${catalogue.method}` : ''}
                    {catalogue.status === 'known_issue' && <>{' · '}<span className="text-warning font-semibold">Known issue</span></>}
                    {catalogue.standards?.length ? ` · ${catalogue.standards.join(', ')}` : ''}
                    {catalogue.applicability && <span className="block">{catalogue.applicability}</span>}
                </p>
            )}
            {list.map((w) => (
                <p key={w} className="flex gap-1.5 text-text-main" role="alert">
                    <AlertTriangle size={12} className="mt-0.5 shrink-0 text-warning" />{w}
                </p>
            ))}
        </div>
    );
};

export default CatalogueNote;
