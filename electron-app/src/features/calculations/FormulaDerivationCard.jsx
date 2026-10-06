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
import { Tex } from './UserGuideTemplate';

const formatValue = (v) => {
  if (typeof v === 'number') return Number.isInteger(v) ? String(v) : v.toFixed(4).replace(/0+$/, '').replace(/\.$/, '');
  if (v !== null && typeof v === 'object') return JSON.stringify(v); // never "[object Object]"
  return String(v);
};

/** "Relative density (D_r)": label with its documented symbol, or the spaced-out key. */
const QuantityName = ({ q }) => (
  <span className="text-text-muted">
    {q.label || q.key.replace(/\s*\[[^\]]*\]$/, '').replace(/_/g, ' ')}
    {q.symbol && <> (<Tex tex={q.symbol} />)</>}
  </span>
);

const QuantityRow = ({ q }) => (
  <div className="flex flex-wrap items-center justify-between p-2 rounded-md bg-surface/50 border border-border/50 text-[11px] gap-2">
    <QuantityName q={q} />
    <span className="font-bold text-text-main font-mono">{formatValue(q.value)}{q.unit && q.unit !== '-' ? ` ${q.unit}` : ''}</span>
  </div>
);

/**
 * One step of the worked derivation (objective, given, governing equation, result). Everything in
 * a step comes from the backend explainer: groundhog's docstring plus the actual inputs/outputs.
 */
const DerivationStep = ({ index, step }) => (
  <div className="flex gap-2.5">
    <div className="shrink-0 w-5 h-5 rounded-full bg-primary/10 text-primary border border-primary/20 text-[10px] font-bold flex items-center justify-center">
      {index + 1}
    </div>
    <div className="flex-1 min-w-0 space-y-1.5">
      <div className="text-[10px] font-bold text-text-muted uppercase tracking-wide pt-0.5">{step.title}</div>
      {step.text && <div className="text-[11px] text-text-main">{step.text}</div>}
      {step.formula && (
        <div className="p-2.5 rounded-md bg-background border border-border text-primary overflow-x-auto">
          <Tex tex={step.formula} />
        </div>
      )}
      {step.where && step.where.length > 0 && (
        <div className="text-[11px] text-text-muted space-y-0.5">
          <span>where</span>
          {step.where.map((w) => (
            <div key={w.symbol} className="pl-3">
              <Tex tex={w.symbol} /> = <span className="font-mono font-bold text-text-main">{formatValue(w.value)}{w.unit && w.unit !== '-' ? ` ${w.unit}` : ''}</span>
              {w.label && <span> ({w.label})</span>}
            </div>
          ))}
        </div>
      )}
      {(step.items || []).map((q) => <QuantityRow key={q.key} q={q} />)}
    </div>
  </div>
);

export const FormulaDerivationCard = ({ functionName, functionId, formData = {}, results = {}, className = '' }) => {
  // The explainer looks the calculation up by its groundhog id; the title ("API RP2 GEO (Sand)")
  // is ambiguous and unknown to the backend, which then falls back to generic text.
  const explainId = functionId || functionName;
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
    if (!explainId || !hasResults) return;

    let cancelled = false;
    api.geoaiExplain(explainId, formData, results)
      .then((data) => { if (!cancelled) setExplanation(data); })
      .catch(() => { if (!cancelled) setExplanation(null); });

    const controller = new AbortController();
    abortRef.current = controller;
    setNarrationState('loading');
    api.geoaiExplainNarrate(explainId, formData, results, controller.signal)
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
  }, [explainId, JSON.stringify(formData), JSON.stringify(results)]);

  if (!hasResults || !explainId) return null;

  return (
    <div className={`geo-card bg-surface/80 border border-border rounded-md overflow-hidden ${className}`}>
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-background border-b border-border text-left hover:bg-surface-elevated transition-colors"
      >
        <div className="flex items-center gap-2">
          <div className="p-1 rounded-md bg-primary/10 text-primary border border-primary/20">
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
              {/* Worked derivation, step by step. Nothing here is invented: the steps come from
                  groundhog's own docstring and the values exactly as computed. */}
              {explanation.steps && explanation.steps.length > 0 ? (
                <div className="space-y-3">
                  {explanation.steps.map((step, idx) => <DerivationStep key={step.title} index={idx} step={step} />)}
                </div>
              ) : (
                <div className="space-y-1.5 pt-1">
                  {(explanation.outputs || []).map((o) => <QuantityRow key={o.key} q={o} />)}
                </div>
              )}

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
