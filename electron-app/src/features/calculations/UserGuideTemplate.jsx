/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React from 'react';
import { Book, Info, Layers, CheckCircle2, FileText } from 'lucide-react';

export const generateDefaultDocumentation = (functionName, schema, normalizedInputs = []) => {
    const desc = schema?.description || `Engineering calculation routine for ${functionName}.`;
    
    let paramsHtml = '';
    if (normalizedInputs && normalizedInputs.length > 0) {
        paramsHtml = `
    <h3>Parameter Reference</h3>
    <ul>
` + normalizedInputs.map(input => `        <li><b>${input.label || input.name}</b> (<code>${input.name}</code>): ${input.description || 'Geotechnical parameter'}${input.unit ? ` [${input.unit}]` : ''} — <i>${input.required ? 'Required' : 'Optional'}</i>.</li>`).join('\n') + `
    </ul>`;
    }

    return `
<div class="space-y-4">
    <h3>Overview</h3>
    <p>${desc}</p>

    <h3>Methodology & Theoretical Background</h3>
    <p>This module implements analytical and empirical formulations from the Groundhog geotechnical library. Calculations follow established international geotechnical standards (Eurocode 7, API RP 2A, ASTM, and DNV guidelines).</p>
${paramsHtml}

    <h3>Assumptions & Limitations</h3>
    <ul>
        <li>Ensure all input parameters are specified in the required SI dimensions.</li>
        <li>Layer stratification and groundwater elevations should be confirmed from geotechnical borehole logs.</li>
        <li>Review material safety factors and characteristic design approaches according to local project specifications.</li>
    </ul>
</div>
`.trim();
};

export const UserGuideTemplate = ({ functionName, pageDocs, schema, normalizedInputs = [], overrides = {} }) => {
    const activeDocs = pageDocs || generateDefaultDocumentation(functionName, schema, normalizedInputs);
    const hasHtmlDocs = Boolean(activeDocs && activeDocs.trim());

    return (
        <div className="space-y-6 text-text-main pb-8">
            {/* Header Hero Banner */}
            <div className="bg-gradient-to-br from-primary/10 via-surface to-primary-light/5 border border-border rounded-md p-5 shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
                    <div className="flex items-center gap-3">
                        <div className="p-2.5 rounded bg-primary/15 text-primary border border-primary/20">
                            <Book size={22} />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-text-main">{functionName}</h2>
                            <p className="text-xs text-text-muted mt-0.5">Geotechnical calculation routine & parameter reference guide</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-background border border-border text-primary font-medium">
                            Groundhog Core
                        </span>
                        <span className="text-[11px] px-2.5 py-1 rounded bg-primary/10 text-primary border border-primary/20 font-medium">
                            {normalizedInputs.length} Parameters
                        </span>
                    </div>
                </div>
            </div>

            {/* Theory / Formulation Content */}
            {hasHtmlDocs ? (
                <div className="bg-surface border border-border rounded-md p-6 shadow-sm">
                    <div className="flex items-center gap-2 text-primary font-bold mb-4 pb-2 border-b border-border text-xs uppercase tracking-wider">
                        <Info size={15} />
                        <span>Methodology & Theoretical Formulation</span>
                    </div>
                    <div
                        className="doc-content prose dark:prose-invert max-w-none text-text-main"
                        dangerouslySetInnerHTML={{ __html: pageDocs }}
                    />
                </div>
            ) : (
                <div className="bg-surface border border-border rounded-md p-6 shadow-sm text-sm text-text-muted flex items-center gap-3">
                    <FileText size={18} className="text-primary shrink-0" />
                    <span>Standard calculation documentation configured from Groundhog specification. Refer to input parameter definitions below.</span>
                </div>
            )}

            {/* Input Parameters Reference Table */}
            {normalizedInputs && normalizedInputs.length > 0 && (
                <div className="bg-surface border border-border rounded-md p-6 shadow-sm space-y-4">
                    <div className="flex items-center justify-between pb-2 border-b border-border">
                        <div className="flex items-center gap-2 text-primary font-bold text-xs uppercase tracking-wider">
                            <Layers size={15} />
                            <span>Input Parameters Specification</span>
                        </div>
                        <span className="text-xs text-text-muted">
                            Required: <strong className="text-amber-600 dark:text-amber-400">{normalizedInputs.filter(i => i.required).length}</strong> | Optional: <strong className="text-text-main">{normalizedInputs.filter(i => !i.required).length}</strong>
                        </span>
                    </div>

                    <div className="overflow-x-auto border border-border rounded-md">
                        <table className="w-full text-left text-xs divide-y divide-border">
                            <thead className="bg-background text-text-main font-semibold">
                                <tr>
                                    <th className="px-3.5 py-2.5">Parameter</th>
                                    <th className="px-3.5 py-2.5">Symbol / Key</th>
                                    <th className="px-3.5 py-2.5">Type</th>
                                    <th className="px-3.5 py-2.5">Unit</th>
                                    <th className="px-3.5 py-2.5">Default</th>
                                    <th className="px-3.5 py-2.5">Status</th>
                                    <th className="px-3.5 py-2.5">Description & Physical Meaning</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border bg-surface">
                                {normalizedInputs.map((baseInput) => {
                                    const override = overrides?.[functionName]?.[baseInput.name] || {};
                                    const input = { ...baseInput, ...override };
                                    const isReq = Boolean(input.required);

                                    return (
                                        <tr key={input.name} className="hover:bg-background/50 transition-colors">
                                            <td className="px-3.5 py-3 font-semibold text-text-main">
                                                {input.label || input.name}
                                            </td>
                                            <td className="px-3.5 py-3">
                                                <code className="font-mono text-primary bg-primary/10 border border-primary/20 px-1.5 py-0.5 rounded text-[11px]">
                                                    {input.name}
                                                </code>
                                            </td>
                                            <td className="px-3.5 py-3 text-text-muted font-mono text-[11px]">
                                                {input.type || 'float'}
                                            </td>
                                            <td className="px-3.5 py-3 font-medium text-text-main">
                                                {input.unit || '—'}
                                            </td>
                                            <td className="px-3.5 py-3 font-mono text-text-muted text-[11px]">
                                                {input.default !== undefined && input.default !== null && input.default !== '' ? String(input.default) : '—'}
                                            </td>
                                            <td className="px-3.5 py-3">
                                                <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium ${
                                                    isReq
                                                        ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20'
                                                        : 'bg-background text-text-muted border border-border'
                                                }`}>
                                                    {isReq ? 'Required' : 'Optional'}
                                                </span>
                                            </td>
                                            <td className="px-3.5 py-3 text-text-muted max-w-sm leading-relaxed">
                                                {input.description || 'No description provided.'}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Engineering Notes & Verification Box */}
            <div className="bg-primary/5 border border-primary/20 border-l-4 border-l-primary rounded-r-md p-4 text-xs space-y-1.5 shadow-sm">
                <div className="flex items-center gap-2 font-bold text-primary text-sm">
                    <CheckCircle2 size={16} />
                    <span>Engineering Verification & Numerical Consistency</span>
                </div>
                <p className="text-text-muted leading-relaxed">
                    Calculations are evaluated via the Groundhog geotechnical library. Formulations comply with standardized industry methodologies (Eurocode 7, API RP 2A, ASTM, and DNV standards). Verify boundary units and layer elevations before finalizing reports.
                </p>
            </div>
        </div>
    );
};
