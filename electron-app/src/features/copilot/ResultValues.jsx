/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * The scalar values of a GeoAI tool result as name / value / unit tiles.
 *
 * Names, symbols and units come from the app's standard quantity directory (utils/quantities.js, the same
 * one the calculation results use): a Groundhog output key such as "sigma_1_f [kPa]" is shown as the quantity's
 * name with its symbol and the unit beside the value, spelled the standard way ("kPa", "kN/m³", "°"). A name the
 * directory does not know keeps the function's own key (without the bracketed unit), and the unit the function
 * documents always wins. Unit text is never case-transformed: "kPa" stays "kPa".
 */
import React from 'react';
import { resultRows, formatResultValue } from './resultRows';

export const ResultValues = ({ results, functionId, outputUnits }) => (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-1.5 bg-background p-2 rounded-md border border-border">
        {resultRows(results, functionId, outputUnits).map((row) => (
            <div key={row.key} className="min-w-0 p-1.5 rounded-md bg-surface border border-border/50">
                <div className="flex items-baseline justify-between gap-1.5 text-[10px] font-semibold text-text-muted">
                    <span className="truncate" title={row.label}>{row.label}</span>
                    {row.symbol && <span className="shrink-0 font-mono text-primary">{row.symbol}</span>}
                </div>
                <div className="text-xs font-semibold tabular-nums text-text-main break-words">
                    {formatResultValue(row.value)}
                    {row.unit && <span className="ml-1 font-normal text-text-muted">{row.unit}</span>}
                </div>
            </div>
        ))}
    </div>
);

export default ResultValues;
