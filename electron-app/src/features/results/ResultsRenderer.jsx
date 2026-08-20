/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '../../components/ui/Card';
import { ChevronDown, ChevronUp, Database, Layers } from 'lucide-react';
import Papa from 'papaparse';

import Plot from 'react-plotly.js';

export const ResultsRenderer = ({ results }) => {
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
        // Handle specific result types
        if (displayData && displayData.type === 'SoilProfile') {
            const previewData = displayData.preview || [];
            const isExpanded = expandedSections.profile;
            const displayedRows = isExpanded ? previewData : previewData.slice(0, 5);

            return (
                <div className="space-y-4">
                    <div className="bg-surface p-4 rounded-md border border-border">
                        <h4 className="font-bold text-lg mb-2 flex items-center gap-2 text-primary">
                            <Database size={20} />
                            {displayData.name}
                        </h4>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div className="p-2 bg-background/50 rounded border border-border/50">
                                <span className="text-text-muted">Status:</span>
                                <span className="ml-2 font-medium text-green-500">{displayData.message}</span>
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
                            <div className="overflow-x-auto rounded-lg border border-border bg-background">
                                <table className="w-full text-xs text-left">
                                    <thead className="bg-surface/50 text-text-muted font-medium border-b border-border">
                                        <tr>
                                            {Object.keys(previewData[0]).map(k => <th key={k} className="p-3">{k}</th>)}
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-border">
                                        {displayedRows.map((row, i) => (
                                            <tr key={i} className="hover:bg-primary/5 transition-colors">
                                                {Object.values(row).map((v, j) => <td key={j} className="p-3 text-text-main">{v}</td>)}
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

        if (displayData && displayData.type === 'CalculationGrid') {
            const nodes = displayData.nodes || [];
            const elements = displayData.elements || [];
            const nodesExpanded = expandedSections.nodes;
            const elementsExpanded = expandedSections.elements;

            const displayedNodes = nodesExpanded ? nodes : nodes.slice(0, 10);
            const displayedElements = elementsExpanded ? elements : elements.slice(0, 10);

            return (
                <div className="space-y-6">
                    <div className="bg-surface p-4 rounded-md border border-border flex items-center justify-between">
                        <div>
                            <h4 className="font-bold text-lg text-primary flex items-center gap-2">
                                <Layers size={20} />
                                Calculation Grid
                            </h4>
                            <p className="text-text-muted text-sm">{displayData.message}</p>
                        </div>
                        <div className="flex gap-4">
                            <div className="text-center px-4 py-2 bg-background/50 rounded border border-border/50">
                                <div className="text-xl font-bold text-text-main">{displayData.nodes_count}</div>
                                <div className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Nodes</div>
                            </div>
                            <div className="text-center px-4 py-2 bg-background/50 rounded border border-border/50">
                                <div className="text-xl font-bold text-text-main">{displayData.elements_count}</div>
                                <div className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Elements</div>
                            </div>
                        </div>
                    </div>

                    {/* Nodes Preview */}
                    {nodes.length > 0 && (
                        <div className="space-y-3">
                            <div className="flex items-center justify-between px-1">
                                <h5 className="font-semibold text-text-main flex items-center gap-2 text-sm">
                                    <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                                    Nodes (Depth & Parameters)
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
                            <div className="overflow-x-auto rounded-lg border border-border bg-background shadow-sm">
                                <table className="w-full text-[11px] text-left border-collapse">
                                    <thead className="bg-surface/50 text-text-muted uppercase tracking-wider font-semibold">
                                        <tr>
                                            {Object.keys(nodes[0]).map(k => (
                                                <th key={k} className="p-3 border-b border-border">{k}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-border">
                                        {displayedNodes.map((row, i) => (
                                            <tr key={i} className="hover:bg-primary/5 transition-colors">
                                                {Object.values(row).map((v, j) => (
                                                    <td key={j} className="p-3 text-text-main whitespace-nowrap">
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

                    {/* Elements Preview */}
                    {elements.length > 0 && (
                        <div className="space-y-3">
                            <div className="flex items-center justify-between px-1">
                                <h5 className="font-semibold text-text-main flex items-center gap-2 text-sm">
                                    <div className="w-1.5 h-1.5 rounded-full bg-secondary" />
                                    Elements (Tributary Area & Logic)
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
                            <div className="overflow-x-auto rounded-lg border border-border bg-background shadow-sm">
                                <table className="w-full text-[11px] text-left border-collapse">
                                    <thead className="bg-surface/50 text-text-muted uppercase tracking-wider font-semibold">
                                        <tr>
                                            {Object.keys(elements[0]).map(k => (
                                                <th key={k} className="p-3 border-b border-border">{k}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-border">
                                        {displayedElements.map((row, i) => (
                                            <tr key={i} className="hover:bg-primary/5 transition-colors">
                                                {Object.values(row).map((v, j) => (
                                                    <td key={j} className="p-3 text-text-main whitespace-nowrap">
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

        if (displayData && displayData.type === 'LogPlot') {
            return (
                <div className="bg-surface p-4 rounded-md border border-border">
                    <h4 className="font-bold text-lg mb-2">Log Plot Result</h4>
                    <p>{displayData.message}</p>
                    <pre className="text-xs mt-2 p-2 bg-background rounded overflow-auto">
                        {JSON.stringify(displayData, null, 2)}
                    </pre>
                </div>
            );
        }

        // Handle Image results (base64)
        if (displayData && displayData.image) {
            return (
                <div className="flex flex-col items-center">
                    <img
                        src={`data:image/png;base64,${displayData.image}`}
                        alt="Calculation Plot"
                        className="max-w-full rounded-lg shadow-lg"
                    />
                </div>
            );
        }

        if (displayData.type === 'plotly' || displayData.type === 'plot') {
            return (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                    className="mt-6 w-full"
                    id="results-visualization"
                >
                    <Card title={displayData.layout?.title?.text || displayData.layout?.title || "Plot"} className="w-full">
                        <div className="w-full h-[600px]">
                            <Plot
                                data={displayData.data}
                                layout={{
                                    ...displayData.layout,
                                    autosize: true,
                                    height: 600,
                                    paper_bgcolor: 'rgba(0,0,0,0)',
                                    plot_bgcolor: 'rgba(0,0,0,0)',
                                    font: { color: '#888' }
                                }}
                                useResizeHandler={true}
                                style={{ width: "100%", height: "100%" }}
                                config={{ responsive: true }}
                            />
                        </div>
                    </Card>
                </motion.div>
            );
        }

        if (displayData.type === 'multi_plot') {
            return (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                    className="mt-6 w-full space-y-8"
                    id="results-visualization"
                >
                    {displayData.plots.map((plot, index) => (
                        <Card key={index} title={plot.title || plot.layout?.title?.text || `Plot ${index + 1}`} className="w-full">
                            <div className="w-full h-[600px]">
                                <Plot
                                    data={plot.data}
                                    layout={{
                                        ...plot.layout,
                                        autosize: true,
                                        height: 600,
                                        paper_bgcolor: 'rgba(0,0,0,0)',
                                        plot_bgcolor: 'rgba(0,0,0,0)',
                                        font: { color: '#888' }
                                    }}
                                    useResizeHandler={true}
                                    style={{ width: "100%", height: "100%" }}
                                    config={{ responsive: true }}
                                />
                            </div>
                        </Card>
                    ))}

                    {/* Render specific results table if present in multi_plot */}
                    {displayData.results && displayData.results.type === 'dataframe' && (
                        <Card title="Results Data" className="w-full overflow-hidden">
                            <div className="overflow-x-auto max-h-[500px]">
                                <table className="w-full text-xs text-left">
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
                                                        {typeof row[col] === 'number' ? row[col].toFixed(4) : row[col]}
                                                    </td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </Card>
                    )}
                </motion.div>
            );
        }

        if (displayData.type === 'image') {
            return (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                    className="mt-6 w-full flex justify-center"
                    id="results-visualization"
                >
                    <Card title="Plot (Static)" className="w-full max-w-4xl">
                        <div className="flex justify-center p-4 bg-white rounded-lg">
                            <img
                                src={`data:image/png;base64,${displayData.data}`}
                                alt="Matplotlib Plot"
                                className="max-w-full h-auto shadow-sm"
                            />
                        </div>
                    </Card>
                </motion.div>
            );
        }

        // Generic DataFrame Support
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

        // Default: Render as Table for Key-Value pairs
        if (typeof displayData === 'object' && displayData !== null) {
            return (
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="border-b border-border">
                                <th className="py-2 px-4 font-semibold text-text-muted">Parameter</th>
                                <th className="py-2 px-4 font-semibold text-text-muted">Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            {Object.entries(displayData).map(([key, value]) => {
                                if (key === 'warnings') return null;
                                return (
                                    (
                                        <tr key={key} className="border-b border-border hover:bg-white/5 transition-colors">
                                            <td className="py-2 px-4 font-medium text-text-main">{key}</td>
                                            <td className="py-2 px-4 text-text-muted font-mono text-sm">
                                                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                            </td>
                                        </tr>
                                    ))
                            })}
                        </tbody>
                    </table>
                </div>
            );
        }


        return <pre className="text-xs p-4 bg-background overflow-auto">{JSON.stringify(displayData, null, 2)}</pre>;
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mt-6"
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
