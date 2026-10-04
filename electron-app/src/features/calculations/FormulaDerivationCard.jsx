/**
 * Author: Utkarsh Gupta
 * License: Proprietary / GeoCore
 *
 * Explains one already-computed result: method, standard and formula come straight from the
 * backend (Groundhog's own TOOL_METADATA and docstrings — see core/geoai/calculation_explainer.py),
 * never guessed in the browser. A short plain-language narration is fetched separately from the
 * local GeoAI model in the background, so the deterministic facts render immediately and the
 * narration fills in a moment later (or not at all, if no model is installed).
 */

import React, { useEffect, useRef, useState } from 'react';
import { Sigma, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';
import { api } from '../../api/client';

const formatValue = (v) => {
  if (typeof v === 'number') return Number.isInteger(v) ? String(v) : v.toFixed(4).replace(/0+$/, '').replace(/\.$/, '');
  return String(v);
};

export const FormulaDerivationCard = ({ functionName, formData = {}, results = {}, className = '' }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [explanation, setExplanation] = useState(null);
  const [narration, setNarration] = useState(null);
  const [narrationState, setNarrationState] = useState('idle'); // idle | loading | done | unavailable
  const abortRef = useRef(null);

  const hasResults = results && Object.keys(results).length > 0;

  useEffect(() => {
    abortRef.current?.abort();
    setExplanation(null);
    setNarration(null);
    setNarrationState('idle');
    if (!functionName || !hasResults) return;

    let cancelled = false;
    api.geoaiExplain(functionName, formData, results)
      .then((data) => { if (!cancelled) setExplanation(data); })
      .catch(() => { if (!cancelled) setExplanation(null); });

    const controller = new AbortController();
    abortRef.current = controller;
    setNarrationState('loading');
    api.geoaiExplainNarrate(functionName, formData, results, controller.signal)
      .then((data) => {
        if (cancelled) return;
        if (data?.narration) {
          setNarration(data.narration);
          setNarrationState('done');
        } else {
          setNarrationState('unavailable');
        }
      })
      .catch(() => { if (!cancelled) setNarrationState('unavailable'); });

    return () => { cancelled = true; controller.abort(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [functionName, JSON.stringify(formData), JSON.stringify(results)]);

  if (!hasResults || !functionName) return null;

  return (
    <div className={`geo-card bg-surface/80 border border-border rounded-md overflow-hidden ${className}`}>
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-background border-b border-border text-left hover:bg-surface-elevated transition-colors"
      >
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-primary/10 text-primary border border-primary/20">
            <Sigma size={15} />
          </div>
          <div>
            <span className="text-xs font-bold text-text-main block">
              {explanation?.method || 'Calculation method'}
            </span>
            <span className="text-[10px] font-mono text-text-muted">
              {explanation?.standard || 'Loading method and standard…'}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-1 text-text-muted">
          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </button>

      {isExpanded && (
        <div className="p-4 space-y-3 text-xs animate-fade-in">
          {!explanation ? (
            <div className="text-text-muted">Loading…</div>
          ) : (
            <>
              {explanation.formula && (
                <div className="p-2.5 rounded bg-background border border-border font-mono text-[11px] text-primary overflow-x-auto">
                  <span className="font-bold text-text-muted block mb-1">Formula (from groundhog's own documentation):</span>
                  <code>{explanation.formula}</code>
                </div>
              )}

              {/* Substituted inputs and outputs, exactly as computed — nothing here is invented */}
              <div className="space-y-1.5 pt-1">
                {explanation.inputs && Object.entries(explanation.inputs).length > 0 && (
                  <div className="text-[10px] font-bold text-text-muted uppercase tracking-wide">Inputs</div>
                )}
                {Object.entries(explanation.inputs || {}).map(([k, v]) => (
                  <div key={`in-${k}`} className="flex flex-wrap items-center justify-between p-2 rounded bg-surface/50 border border-border/50 font-mono text-[11px] gap-2">
                    <span className="text-text-muted">{k.replace(/_/g, ' ')}:</span>
                    <span className="font-bold text-text-main">{formatValue(v)}</span>
                  </div>
                ))}
                {explanation.outputs && explanation.outputs.length > 0 && (
                  <div className="text-[10px] font-bold text-text-muted uppercase tracking-wide pt-1">Outputs</div>
                )}
                {(explanation.outputs || []).map((o) => (
                  <div key={`out-${o.key}`} className="flex flex-wrap items-center justify-between p-2 rounded bg-surface/50 border border-border/50 font-mono text-[11px] gap-2">
                    <span className="text-text-muted">{o.key.replace(/_/g, ' ')}:</span>
                    <span className="font-bold text-text-main">{formatValue(o.value)}{o.unit ? ` ${o.unit}` : ''}</span>
                  </div>
                ))}
              </div>

              {explanation.assumptions && explanation.assumptions.length > 0 && (
                <div className="pt-1">
                  <div className="text-[10px] font-bold text-text-muted uppercase tracking-wide mb-1">Assumptions</div>
                  <ul className="list-disc list-inside space-y-0.5 text-[11px] text-text-muted">
                    {explanation.assumptions.map((a, idx) => <li key={idx}>{a}</li>)}
                  </ul>
                </div>
              )}

              {/* AI narration: loaded in the background, never replaces the facts above */}
              <div className="flex items-start gap-1.5 text-[11px] text-text-muted pt-2 border-t border-border/40">
                <Sparkles size={12} className="text-primary shrink-0 mt-0.5" />
                {narrationState === 'loading' && <span className="italic">GeoAI is writing a plain-language explanation…</span>}
                {narrationState === 'done' && <span>{narration}</span>}
                {narrationState === 'unavailable' && <span className="italic">No plain-language narration available (install a local model in the GeoAI model manager to get one).</span>}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};
