/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * LaTeX math in a GeoAI answer, rendered by KaTeX (loaded on first use, as in the calculation guides).
 * KaTeX builds the markup from the TeX source itself with `trust` off, so model text cannot inject HTML;
 * a formula it cannot parse is shown in red rather than throwing. Until KaTeX has loaded the source is shown.
 */
import React, { useEffect, useState } from 'react';
import { loadKatex } from '../calculations/guide/functionDocs';

export const MathTex = ({ tex, display = false }) => {
    const [html, setHtml] = useState(null);
    useEffect(() => {
        let cancelled = false;
        loadKatex()
            .then(({ katex }) => {
                if (!cancelled) setHtml(katex.renderToString(tex, { throwOnError: false, displayMode: display, trust: false }));
            })
            .catch(() => {});
        return () => { cancelled = true; };
    }, [tex, display]);
    if (!html) return <span className="font-mono">{tex}</span>;
    return display
        ? <div className="overflow-x-auto py-1" dangerouslySetInnerHTML={{ __html: html }} />
        : <span dangerouslySetInnerHTML={{ __html: html }} />;
};

export default MathTex;
