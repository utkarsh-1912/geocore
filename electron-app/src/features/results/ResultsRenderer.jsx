/**
 * Author: Utkarsh Gupta
 * License: GPL v3 / GeoCore
 */

import React, { useState, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '../../components/ui/Card';
import { ChevronDown, ChevronUp, Database, Layers, CheckCircle2 } from 'lucide-react';
import Papa from 'papaparse';
import { getParameterNotation } from '@/utils/geoNotation';
import { FormulaDerivationCard } from '../calculations/FormulaDerivationCard';

const Plot = React.lazy(() => import('react-plotly.js'));

export const ResultsRenderer = ({ results, functionName = '', formData = {} }) => {
    const [expandedSections, setExpandedSections] = useState({
        nodes: false,
        elements: false,
        profile: false
    });

    if (!results) return null;

    const toggleSection = (section) => {
        setExpandedSections(prev => ({
            ...prev,
            [section]: !prev[section]
        }));
    };

    // Check if we have warnings wrapped in the response or directly in the object
    const warnings = results.warnings || (results.result && results.result.warnings) || [];

    // Flatten result if it was wrapped
    const displayData = results.result !== undefined ? results.result : results;

    const renderContent = () => {
        // 1. Handle Error State
        if (displayData && displayData.error) {
            const errorMsg = typeof displayData.error === 'object'
                ? (displayData.error.error || displayData.error.message || JSON.stringify(displayData.error))
                : String(displayData.error);
            const errorDetails = displayData.details || (typeof displayData.error === 'object' && displayData.error.details) || [];

            return (
                <div className="p-4 border-l-4 border-red-500 bg-red-500/10 rounded-r-md">
                    <h4 className="text-red-500 font-bold mb-1 flex items-center gap-2">
                        Validation / Calculation Error
                    </h4>
                    <p className="text-sm text-text-main font-medium mb-2">{errorMsg}</p>
                    {errorDetails && errorDetails.length > 0 && (
                        <div className="mt-2 space-y-1">
                            <span className="text-xs font-bold text-text-muted uppercase">Invalid Parameters:</span>
                            <ul className="list-disc list-inside text-xs text-text-muted">
                                {errorDetails.map((d, i) => (
                                    <li key={i}>
                                        <span className="font-semibold text-text-main">{d.field || d.name}</span>: {d.message} {d.input_value !== undefined && d.input_value !== null ? `(received: ${JSON.stringify(d.input_value)})` : ''}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            );
        }

        // 2. Handle SoilProfile Object
        if (displayData && (displayData.type === 'SoilProfile' || (displayData.preview && displayData.layers !== undefined))) {
            const previewData = displayData.preview || [];
            const isExpanded = expandedSections.profile;
            const displayedRows = isExpanded ? previewData : previewData.slice(0, 5);

            return (
                <div className="space-y-4">
                    <div className="bg-surface p-4 rounded-md border border-border">
                        <h4 className="font-bold text-lg mb-2 flex items-center gap-2 text-primary">
                            <Database size={20} />
                            {displayData.name || "Soil Profile"}
                        </h4>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div className="p-2 bg-background/50 rounded border border-border/50">
                                <span className="text-text-muted">Status:</span>
                                <span className="ml-2 font-medium text-green-500">{displayData.message || "Profile Ready"}</span>
                            </div>
                            <div className="p-2 bg-background/50 rounded border border-border/50">
                                <span className="text-text-muted">Total Layers:</span>
                                <span className="ml-2 font-bold text-text-main">{displayData.layers}</span>
                            </div>
                        </div>
                    </div>
                    {/* Preview Table */}
                    {previewData.length > 0 && (
                        <div className="space-y-2">
                            <div className="flex items-center justify-between px-1">
                                <h5 className="text-sm font-semibold text-text-muted uppercase tracking-wider">Layers Preview</h5>
                                {previewData.length > 5 && (
                                    <button
                                        onClick={() => toggleSection('profile')}
                                        className="text-primary hover:text-primary-hover text-xs font-bold flex items-center gap-1 transition-colors"
                                    >
                                        {isExpanded ? <><ChevronUp size={14} /> Collapse</> : <><ChevronDown size={14} /> View All ({previewData.length})</>}
                                    </button>
                                )}
                            </div>
                            <div className="overflow-x-auto rounded-lg border border-border bg-background shadow-sm max-h-96">
                                <table className="w-full text-xs text-left border-collapse">
                                    <thead className="bg-surface/50 text-text-muted font-medium border-b border-border sticky top-0">
                                        <tr>
                                            {Object.keys(previewData[0]).map(k => <th key={k} className="p-3 whitespace-nowrap">{k}</th>)}
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-border">
                                        {displayedRows.map((row, i) => (
                                            <tr key={i} className="hover:bg-primary/5 transition-colors">
                                                {Object.values(row).map((val, j) => (
                                                    <td key={j} className="p-3 text-text-main whitespace-nowrap">
                                                        {typeof val === 'number' ? val.toFixed(2) : String(val)}
                                                    </td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </div>
            );
        }

        // 3. Handle CalculationGrid Object
        if (displayData && (displayData.type === 'CalculationGrid' || (Array.isArray(displayData.nodes) && Array.isArray(displayData.elements)))) {
            const nodes = displayData.nodes || [];
            const elements = displayData.elements || [];
            const nodesExpanded = expandedSections.nodes;
            const elementsExpanded = expandedSections.elements;

            const displayedNodes = nodesExpanded ? nodes : nodes.slice(0, 10);
            const displayedElements = elementsExpanded ? elements : elements.slice(0, 10);

            return (
                <div className="space-y-6">
                    <div className="bg-surface p-4 rounded-md border border-border flex items-center justify-between flex-wrap gap-4">
                        <div>
                            <h4 className="font-bold text-lg text-primary flex items-center gap-2">
                                <Layers size={20} />
                                Calculation Grid
                            </h4>
                            <p className="text-text-muted text-sm">{displayData.message || "Discretized Grid Ready"}</p>
                        </div>
                        <div className="flex gap-4">
                            <div className="text-center px-4 py-2 bg-background/50 rounded border border-border/50">
                                <div className="text-xl font-bold text-text-main">{displayData.nodes_count || nodes.length}</div>
                                <div className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Nodes</div>
                            </div>
                            <div className="text-center px-4 py-2 bg-background/50 rounded border border-border/50">
                                <div className="text-xl font-bold text-text-main">{displayData.elements_count || elements.length}</div>
                                <div className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Elements</div>
                            </div>
                        </div>
                    </div>

                    {/* Nodes Table */}
                    {nodes.length > 0 && (
                        <div className="space-y-3">
                            <div className="flex items-center justify-between px-1">
                                <h5 className="font-semibold text-text-main flex items-center gap-2 text-sm">
                                    <div className="w-2 h-2 rounded-full bg-primary" />
                                    Nodes (Depth & Boundary State)
                                    {!nodesExpanded && nodes.length > 10 && (
                                        <span className="text-[10px] text-text-muted font-normal italic ml-2">
                                            (Showing first 10 of {nodes.length})
                                        </span>
                                    )}
                                </h5>
                                {nodes.length > 10 && (
                                    <button
                                        onClick={() => toggleSection('nodes')}
                                        className="text-primary hover:text-primary-hover text-xs font-bold flex items-center gap-1 transition-colors"
                                    >
                                        {nodesExpanded ? <><ChevronUp size={14} /> Collapse</> : <><ChevronDown size={14} /> View All ({nodes.length})</>}
                                    </button>
                                )}
                            </div>
                            <div className="overflow-x-auto rounded-lg border border-border bg-background shadow-sm max-h-96">
                                <table className="w-full text-xs text-left border-collapse">
                                    <thead className="bg-surface/60 text-text-muted font-semibold border-b border-border sticky top-0">
                                        <tr>
                                            {Object.keys(nodes[0]).map(k => (
                                                <th key={k} className="p-2.5 whitespace-nowrap">{k}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-border">
                                        {displayedNodes.map((row, i) => (
                                            <tr key={i} className="hover:bg-primary/5 transition-colors">
                                                {Object.values(row).map((v, j) => (
                                                    <td key={j} className="p-2.5 text-text-main whitespace-nowrap">
                                                        {typeof v === 'number' ? v.toFixed(3) : String(v)}
                                                    </td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {/* Elements Table */}
                    {elements.length > 0 && (
                        <div className="space-y-3">
                            <div className="flex items-center justify-between px-1">
                                <h5 className="font-semibold text-text-main flex items-center gap-2 text-sm">
                                    <div className="w-2 h-2 rounded-full bg-secondary" />
                                    Elements (Layer Strata & Properties)
                                    {!elementsExpanded && elements.length > 10 && (
                                        <span className="text-[10px] text-text-muted font-normal italic ml-2">
                                            (Showing first 10 of {elements.length})
                                        </span>
                                    )}
                                </h5>
                                {elements.length > 10 && (
                                    <button
                                        onClick={() => toggleSection('elements')}
                                        className="text-primary hover:text-primary-hover text-xs font-bold flex items-center gap-1 transition-colors"
                                    >
                                        {elementsExpanded ? <><ChevronUp size={14} /> Collapse</> : <><ChevronDown size={14} /> View All ({elements.length})</>}
                                    </button>
                                )}
                            </div>
                            <div className="overflow-x-auto rounded-lg border border-border bg-background shadow-sm max-h-96">
                                <table className="w-full text-xs text-left border-collapse">
                                    <thead className="bg-surface/60 text-text-muted font-semibold border-b border-border sticky top-0">
                                        <tr>
                                            {Object.keys(elements[0]).map(k => (
                                                <th key={k} className="p-2.5 whitespace-nowrap">{k}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-border">
                                        {displayedElements.map((row, i) => (
                                            <tr key={i} className="hover:bg-primary/5 transition-colors">
                                                {Object.values(row).map((v, j) => (
                                                    <td key={j} className="p-2.5 text-text-main whitespace-nowrap">
                                                        {typeof v === 'number' ? v.toFixed(3) : String(v)}
                                                    </td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </div>
            );
        }

        // 4. Handle Multi-Plot Results
        if (displayData && displayData.type === 'multi_plot' && Array.isArray(displayData.plots)) {
            return (
                <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3 }}
                    className="space-y-6 w-full"
                    id="results-visualization"
                >
                    {displayData.plots.map((plot, index) => {
                        const plotData = plot.data || [];
                        const plotLayout = plot.layout || {};
                        const finalLayout = {
                            autosize: true,
                            paper_bgcolor: 'rgba(0,0,0,0)',
                            plot_bgcolor: 'rgba(0,0,0,0)',
                            font: { family: 'Inter, sans-serif', color: 'var(--color-text-main, #333)' },
                            margin: { t: 40, r: 20, l: 50, b: 40 },
                            ...plotLayout
                        };

                        return (
                            <Card key={index} title={plot.title || plotLayout?.title?.text || plotLayout?.title || `Plot ${index + 1}`} className="w-full">
                                <div className="w-full h-[500px]">
                                    <Suspense fallback={<div className="w-full h-full flex items-center justify-center bg-background/50 rounded"><span className="text-text-muted text-sm">Loading chart engine...</span></div>}>
                                        <Plot
                                            data={plotData}
                                            layout={finalLayout}
                                            useResizeHandler={true}
                                            style={{ width: "100%", height: "100%" }}
                                            config={{ responsive: true, displayModeBar: true }}
                                        />
                                    </Suspense>
                                </div>
                            </Card>
                        );
                    })}

                    {displayData.results && displayData.results.type === 'dataframe' && displayData.results.data && (
                        <div className="overflow-x-auto rounded-lg border border-border bg-background shadow-sm">
                            <table className="w-full text-xs text-left border-collapse">
                                <thead className="bg-surface/50 text-text-muted font-medium border-b border-border sticky top-0">
                                    <tr>
                                        {displayData.results.columns.map(k => <th key={k} className="p-3 whitespace-nowrap">{k}</th>)}
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-border">
                                    {displayData.results.data.map((row, i) => (
                                        <tr key={i} className="hover:bg-primary/5 transition-colors">
                                            {displayData.results.columns.map((col, j) => (
                                                <td key={j} className="p-3 text-text-main whitespace-nowrap">
                                                    {typeof row[col] === 'number' ? row[col].toFixed(4) : String(row[col])}
                                                </td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </motion.div>
            );
        }

        // 5. Handle Single Plotly Chart
        if (displayData.type === 'plotly' || displayData.type === 'plot') {
            const plotData = displayData.data || [];
            const plotLayout = displayData.layout || {};

            const finalLayout = {
                autosize: true,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: {
                    family: 'Inter, sans-serif',
                    color: 'var(--color-text-main, #333)'
                },
                xaxis: {
                    gridcolor: 'rgba(128, 128, 128, 0.15)',
                    zerolinecolor: 'rgba(128, 128, 128, 0.25)',
                    ...plotLayout.xaxis
                },
                yaxis: {
                    gridcolor: 'rgba(128, 128, 128, 0.15)',
                    zerolinecolor: 'rgba(128, 128, 128, 0.25)',
                    ...plotLayout.yaxis
                },
                margin: { t: 40, r: 20, l: 50, b: 40 },
                ...plotLayout
            };

            return (
                <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3 }}
                    className="w-full"
                    id="results-visualization"
                >
                    <div className="w-full bg-surface p-4 rounded-lg border border-border min-h-[420px] flex items-center justify-center">
                        <Suspense fallback={<div className="text-text-muted text-sm flex items-center gap-2"><div className="w-4 h-4 rounded-full border-2 border-primary border-t-transparent animate-spin"></div> Loading Interactive Chart...</div>}>
                            <Plot
                                data={plotData}
                                layout={finalLayout}
                                useResizeHandler={true}
                                style={{ width: '100%', height: '100%', minHeight: '400px' }}
                                config={{ responsive: true, displayModeBar: true }}
                            />
                        </Suspense>
                    </div>
                </motion.div>
            );
        }

        // 6. Handle Matplotlib Base64 Image
        if (displayData.type === 'image' || displayData.image) {
            const imgData = displayData.data || displayData.image;
            return (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3 }}
                    className="w-full flex justify-center"
                    id="results-visualization"
                >
                    <Card title="Plot (Static)" className="w-full max-w-4xl">
                        <div className="flex justify-center p-4 bg-white rounded-lg">
                            <img
                                src={`data:image/png;base64,${imgData}`}
                                alt="Matplotlib Plot"
                                className="max-w-full h-auto shadow-sm"
                            />
                        </div>
                    </Card>
                </motion.div>
            );
        }

        // 7. Handle Generic DataFrame
        if (displayData.type === 'dataframe' && displayData.data && displayData.data.length > 0) {
            const columns = displayData.columns || Object.keys(displayData.data[0]);
            return (
                <div className="overflow-x-auto rounded-lg border border-border bg-background shadow-sm">
                    <table className="w-full text-xs text-left border-collapse">
                        <thead className="bg-surface/50 text-text-muted font-medium border-b border-border sticky top-0">
                            <tr>
                                {columns.map(k => <th key={k} className="p-3 whitespace-nowrap">{k}</th>)}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {displayData.data.map((row, i) => (
                                <tr key={i} className="hover:bg-primary/5 transition-colors">
                                    {columns.map((col, j) => (
                                        <td key={j} className="p-3 text-text-main whitespace-nowrap">
                                            {typeof row[col] === 'number' ? row[col].toFixed(4) : (typeof row[col] === 'object' ? JSON.stringify(row[col]) : String(row[col]))}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            );
        }

        // 8. Default: Render KPI cards, dedicated Unit column table & Formula derivations
        if (typeof displayData === 'object' && displayData !== null) {
            const entries = Object.entries(displayData).filter(([k]) => k !== 'warnings' && k !== 'type');
            const numericEntries = entries.filter(([, val]) => typeof val === 'number');

            return (
                <div className="space-y-4">
                    {/* Top KPI Metric Badges */}
                    {numericEntries.length > 0 && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                            {numericEntries.slice(0, 3).map(([key, val]) => {
                                const not = getParameterNotation(key);
                                return (
                                    <div key={key} className="p-3.5 rounded-lg bg-surface border border-primary/20 shadow-sm flex flex-col justify-between">
                                        <div className="flex items-center justify-between text-xs text-text-muted">
                                            <span className="font-medium truncate">{not?.label || key.replace(/_/g, ' ')}</span>
                                            {not?.symbol && <span className="px-1.5 py-0.5 rounded bg-primary/10 text-primary font-mono text-[11px] font-bold">{not.symbol}</span>}
                                        </div>
                                        <div className="text-xl font-mono font-extrabold text-text-main mt-1">
                                            {Number(val).toLocaleString(undefined, { maximumFractionDigits: 4 })}
                                            {not?.unit && <span className="text-xs text-text-muted font-normal ml-1.5">{not.unit}</span>}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}

                    {/* Detailed Key-Value Table */}
                    <div className="overflow-x-auto rounded-lg border border-border bg-background">
                        <table className="w-full text-left border-collapse text-xs">
                            <thead className="bg-surface/60 text-text-muted font-semibold border-b border-border">
                                <tr>
                                    <th className="py-2.5 px-4">Parameter Output</th>
                                    <th className="py-2.5 px-4">Symbol</th>
                                    <th className="py-2.5 px-4">Computed Value</th>
                                    <th className="py-2.5 px-4">Unit</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border">
                                {entries.map(([key, value]) => {
                                    const not = getParameterNotation(key);
                                    // Strip embedded [unit] from title if present
                                    const match = key.match(/^(.*?)\s*\[(.*?)\]$/);
                                    const cleanTitle = match ? match[1].trim().replace(/_/g, ' ') : (not?.label || key.replace(/_/g, ' '));
                                    const cleanUnit = match ? match[2].trim() : (not?.unit || '-');

                                    return (
                                        <tr key={key} className="hover:bg-primary/5 transition-colors">
                                            <td className="py-2.5 px-4 font-medium text-text-main">
                                                {cleanTitle}
                                            </td>
                                            <td className="py-2.5 px-4 font-mono text-primary font-bold">
                                                {not?.symbol || '-'}
                                            </td>
                                            <td className="py-2.5 px-4 text-text-main font-mono font-semibold">
                                                {typeof value === 'number'
                                                    ? value.toLocaleString(undefined, { maximumFractionDigits: 5 })
                                                    : (typeof value === 'object' ? JSON.stringify(value) : String(value))}
                                            </td>
                                            <td className="py-2.5 px-4 text-text-muted font-mono">
                                                {cleanUnit && cleanUnit !== '-' ? (
                                                    <span className="px-1.5 py-0.5 rounded bg-surface border border-border text-[11px] font-semibold text-text-muted">
                                                        [{cleanUnit}]
                                                    </span>
                                                ) : '-'}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>

                    {/* Step-by-step formula breakdown */}
                    <FormulaDerivationCard
                        functionName={functionName}
                        formData={formData}
                        results={displayData}
                    />
                </div>
            );
        }

        return <pre className="text-xs p-4 bg-background overflow-auto">{JSON.stringify(displayData, null, 2)}</pre>;
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="mt-6 space-y-4"
        >
            <Card>
                {/* Warnings */}
                {warnings && warnings.length > 0 && (
                    <div className="mb-4 p-4 border-l-4 border-yellow-500 bg-yellow-500/10 rounded-r-md">
                        <h4 className="text-yellow-500 font-bold mb-1 flex items-center gap-2">
                            Note
                        </h4>
                        <ul className="list-disc list-inside text-sm text-text-main">
                            {warnings.map((w, i) => <li key={i}>{w}</li>)}
                        </ul>
                    </div>
                )}

                {renderContent()}
            </Card>
        </motion.div>
    );
};
