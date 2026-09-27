/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React, { useEffect, useState } from 'react';
import { Book, Info, Layers, AlertTriangle, FileText, Library, Sigma, ListOrdered, RefreshCw } from 'lucide-react';
import { loadFunctionDocs, loadKatex, renderMathHtml } from './guide/functionDocs';

/**
 * Starting template for a GeoCore note in the (dev-only) guide editor. The theory itself comes from the
 * groundhog docstrings (guide/functionDocs.json), so this only scaffolds GeoCore-specific usage notes.
 */
export const generateDefaultDocumentation = (functionName, schema, normalizedInputs = []) => {
    const desc = schema?.description || `How to use ${functionName} in GeoCore.`;

    let paramsHtml = '';
    if (normalizedInputs && normalizedInputs.length > 0) {
        paramsHtml = `
    <h3>Inputs</h3>
    <ul>
` + normalizedInputs.map(input => `        <li><b>${input.label || input.name}</b> (<code>${input.name}</code>): ${input.description || ''}${input.unit ? ` [${input.unit}]` : ''} — <i>${input.required ? 'Required' : 'Optional'}</i>.</li>`).join('\n') + `
    </ul>`;
    }

    return `
<div class="space-y-4">
    <h3>Usage in GeoCore</h3>
    <p>${desc}</p>
${paramsHtml}
</div>
`.trim();
};

/** Inline LaTeX (parameter symbols, units); shows the source text until KaTeX has loaded. */
const Tex = ({ tex }) => {
    const [html, setHtml] = useState(null);
    useEffect(() => {
        let cancelled = false;
        loadKatex()
            .then(({ katex }) => {
                if (!cancelled) setHtml(katex.renderToString(tex, { throwOnError: false }));
            })
            .catch(() => {});
        return () => { cancelled = true; };
    }, [tex]);
    return html ? <span dangerouslySetInnerHTML={{ __html: html }} /> : <span className="font-mono">{tex}</span>;
};

const isTex = (text) => /[\\^_{]/.test(text);

const Section = ({ icon: Icon, title, children, aside }) => (
    <div className="bg-surface border border-border rounded-md p-6 shadow-sm">
        <div className="flex items-center justify-between gap-2 text-primary font-bold mb-4 pb-2 border-b border-border text-xs uppercase tracking-wider">
            <span className="flex items-center gap-2">
                <Icon size={15} />
                <span>{title}</span>
            </span>
            {aside}
        </div>
        {children}
    </div>
);

/** HTML produced by the docs build (trusted, generated in-repo); shows the raw HTML until KaTeX has run. */
const MathHtml = ({ html, className = '' }) => {
    const [rendered, setRendered] = useState(null);
    useEffect(() => {
        let cancelled = false;
        setRendered(null);
        renderMathHtml(html)
            .then(out => { if (!cancelled) setRendered(out); })
            .catch(err => console.error('Math rendering failed:', err));
        return () => { cancelled = true; };
    }, [html]);
    return <div className={`doc-content max-w-none text-text-main ${className}`} dangerouslySetInnerHTML={{ __html: rendered ?? html }} />;
};

export const UserGuideTemplate = ({ functionId, functionName, pageDocs, schema, normalizedInputs = [], overrides = {} }) => {
    const [docs, setDocs] = useState(null);
    const [docsState, setDocsState] = useState('loading'); // 'loading' | 'ready' | 'error'

    useEffect(() => {
        let cancelled = false;
        setDocsState('loading');
        loadFunctionDocs()
            .then(data => {
                if (cancelled) return;
                setDocs(data);
                setDocsState('ready');
            })
            .catch(err => {
                console.error('Failed to load function documentation:', err);
                if (!cancelled) setDocsState('error');
            });
        return () => { cancelled = true; };
    }, []);

    const entry = docs?.functions?.[functionId] || null;
    const paramDocs = entry?.params || {};
    const hasNotes = Boolean(pageDocs && pageDocs.trim());

    return (
        <div className="space-y-6 text-text-main pb-8">
            {/* Header */}
            <div className="bg-gradient-to-br from-primary/10 via-surface to-primary-light/5 border border-border rounded-md p-5 shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3 min-w-0">
                        <div className="p-2.5 rounded bg-primary/15 text-primary border border-primary/20 shrink-0">
                            <Book size={22} />
                        </div>
                        <div className="min-w-0">
                            <h2 className="text-xl font-bold text-text-main truncate">{functionName}</h2>
                            <p className="text-xs text-text-muted mt-0.5">
                                {entry?.summary || schema?.description || 'Calculation guide and parameter reference.'}
                            </p>
                        </div>
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                        {entry && (
                            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-background border border-border text-primary font-medium" title="groundhog implementation">
                                {entry.module}.{entry.qualname}
                            </span>
                        )}
                        <span className="text-[11px] px-2.5 py-1 rounded bg-primary/10 text-primary border border-primary/20 font-medium">
                            {normalizedInputs.length} Parameters
                        </span>
                    </div>
                </div>
            </div>

            {/* Theory & formulation from the groundhog docstrings */}
            {docsState === 'loading' && (
                <div className="flex items-center gap-2 text-xs text-text-muted px-1">
                    <RefreshCw size={12} className="animate-spin text-primary" />
                    <span>Loading theory...</span>
                </div>
            )}
            {entry?.theory_html && (
                <Section icon={Sigma} title="Theory & Formulation">
                    <MathHtml html={entry.theory_html} />
                </Section>
            )}
            {docsState !== 'loading' && !entry && !hasNotes && (
                <div className="bg-surface border border-border rounded-md p-6 shadow-sm text-sm text-text-muted flex items-center gap-3">
                    <FileText size={18} className="text-primary shrink-0" />
                    <span>
                        {docsState === 'error'
                            ? 'The theory documentation could not be loaded. The parameter reference below is still available.'
                            : 'No upstream theory documentation is available for this calculation. Refer to the parameter reference below.'}
                    </span>
                </div>
            )}

            {/* GeoCore-specific usage notes (hand-written or edited in the guide editor) */}
            {hasNotes && (
                <Section icon={Info} title="Using this in GeoCore">
                    <div className="doc-content prose dark:prose-invert max-w-none text-text-main" dangerouslySetInnerHTML={{ __html: pageDocs }} />
                </Section>
            )}

            {/* Input Parameters */}
            {normalizedInputs && normalizedInputs.length > 0 && (
                <div className="bg-surface border border-border rounded-md p-6 shadow-sm space-y-4">
                    <div className="flex items-center justify-between pb-2 border-b border-border">
                        <div className="flex items-center gap-2 text-primary font-bold text-xs uppercase tracking-wider">
                            <Layers size={15} />
                            <span>Input Parameters</span>
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
                                    <th className="px-3.5 py-2.5">Symbol</th>
                                    <th className="px-3.5 py-2.5">Unit</th>
                                    <th className="px-3.5 py-2.5">Suggested range</th>
                                    <th className="px-3.5 py-2.5">Default</th>
                                    <th className="px-3.5 py-2.5">Status</th>
                                    <th className="px-3.5 py-2.5">Description</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border bg-surface">
                                {normalizedInputs.map((baseInput) => {
                                    const override = overrides?.[functionName]?.[baseInput.name] || {};
                                    const input = { ...baseInput, ...override };
                                    const pd = paramDocs[input.name] || {};
                                    const isReq = Boolean(input.required);
                                    const unit = input.unit || pd.unit;

                                    return (
                                        <tr key={input.name} className="hover:bg-background/50 transition-colors">
                                            <td className="px-3.5 py-3">
                                                <div className="font-semibold text-text-main">{input.label || input.name}</div>
                                                <code className="font-mono text-primary text-[10px]">{input.name}</code>
                                            </td>
                                            <td className="px-3.5 py-3 text-text-main">
                                                {pd.symbol ? <Tex tex={pd.symbol} /> : '—'}
                                            </td>
                                            <td className="px-3.5 py-3 font-medium text-text-main">
                                                {unit ? (isTex(unit) ? <Tex tex={unit} /> : unit) : '—'}
                                            </td>
                                            <td className="px-3.5 py-3 font-mono text-text-muted text-[11px]">
                                                {pd.range || '—'}
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
                                                {input.description || pd.description || 'No description provided.'}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                    {entry?.validated && (
                        <p className="text-[11px] text-text-muted leading-relaxed">
                            Suggested ranges come from the groundhog docstring or its input validator. Values outside
                            the validated range produce a warning and typically a <code className="font-mono">NaN</code> result
                            rather than an extrapolated value.
                        </p>
                    )}
                </div>
            )}

            {/* Outputs */}
            {entry?.returns_html && (
                <Section icon={ListOrdered} title="Outputs">
                    <MathHtml html={entry.returns_html} />
                </Section>
            )}

            {/* References */}
            {entry?.references?.length > 0 && (
                <Section icon={Library} title="References">
                    <MathHtml html={`<ul>${entry.references.map(r => `<li>${r}</li>`).join('')}</ul>`} />
                </Section>
            )}

            {/* Engineering caution + attribution */}
            <div className="bg-primary/5 border border-primary/20 border-l-4 border-l-primary rounded-r-md p-4 text-xs space-y-1.5 shadow-sm">
                <div className="flex items-center gap-2 font-bold text-primary text-sm">
                    <AlertTriangle size={16} />
                    <span>Applicability & Engineering Judgement</span>
                </div>
                <p className="text-text-muted leading-relaxed">
                    Results are computed by the groundhog library using the method described above. Check that the
                    method applies to your soil conditions, that inputs are in the stated units and within the
                    suggested ranges, and review results with engineering judgement before using them in design.
                </p>
                {entry && docs?.attribution && (
                    <p className="text-[10px] text-text-muted/80 pt-1 border-t border-primary/10">
                        {docs.attribution}
                        {entry.source_url && <> Source: <span className="font-mono select-all">{entry.source_url}</span></>}
                    </p>
                )}
            </div>
        </div>
    );
};
