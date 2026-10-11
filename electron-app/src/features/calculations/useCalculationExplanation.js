/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * The explanation of one already-computed result (POST /api/geoai/explain): method, standard and the worked
 * steps - given inputs, governing equation from the Groundhog docstring with each symbol's value, results. A short
 * plain-language narration is fetched separately from the local model (/explain/narrate) so the facts show at once
 * and the narration fills in later, or not at all without a model.
 *
 * `explainId` is a GeoCore function id or a GeoAI tool name (the backend maps the tool to its function and
 * argument names). Used by the results Formula card and by the GeoAI chat "Explain" bubble.
 */
import { useEffect, useRef, useState } from 'react';
import { api } from '@/api/client';

export const useCalculationExplanation = (explainId, args = {}, results = {}) => {
    const [explanation, setExplanation] = useState(null);
    const [narration, setNarration] = useState(null);
    const [narrationState, setNarrationState] = useState('idle'); // idle | loading | done | unavailable
    const [failed, setFailed] = useState(false);
    const abortRef = useRef(null);
    const hasResults = !!results && Object.keys(results).length > 0;
    const argsKey = JSON.stringify(args || {});
    const resultsKey = JSON.stringify(results || {});

    useEffect(() => {
        abortRef.current?.abort();
        if (!explainId || !hasResults) return undefined;
        let cancelled = false;
        const reset = () => {
            setExplanation(null);
            setNarration(null);
            setFailed(false);
            setNarrationState('loading');
        };
        Promise.resolve().then(() => { if (!cancelled) reset(); });
        api.geoaiExplain(explainId, args, results)
            .then((data) => { if (!cancelled) setExplanation(data); })
            .catch(() => { if (!cancelled) { setExplanation(null); setFailed(true); } });

        const controller = new AbortController();
        abortRef.current = controller;
        api.geoaiExplainNarrate(explainId, args, results, controller.signal)
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
    }, [explainId, argsKey, resultsKey]);

    return { explanation, narration, narrationState, failed, hasResults };
};
