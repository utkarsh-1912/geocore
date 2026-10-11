/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Offline Guide & Theory content for each calculator, generated from the groundhog docstrings by
 * website/_build/app_docs.py (functionDocs.json). Loaded lazily so the ~650 KB of docs is only
 * fetched the first time a guide is opened.
 */

let docsPromise = null;

export const loadFunctionDocs = () => {
    if (!docsPromise) {
        docsPromise = import('./functionDocs.json')
            .then((m) => m.default)
            .catch((err) => {
                docsPromise = null;
                throw err;
            });
    }
    return docsPromise;
};

let katexPromise = null;

/** KaTeX core + auto-render + stylesheet, loaded on first use. */
export const loadKatex = () => {
    if (!katexPromise) {
        katexPromise = Promise.all([
            import('katex'),
            import('katex/contrib/auto-render'),
            import('katex/dist/katex.min.css'),
        ]).then(([katex, autoRender]) => ({ katex: katex.default, renderMathInElement: autoRender.default }));
    }
    return katexPromise;
};

/**
 * Groundhog docstrings write multi-line equations as bare rows ("a = b \\ c = d & \quad \text{for } ...")
 * with no environment around them, which KaTeX rejects: `&` is only legal inside an alignment and `\\`
 * is ignored outside one. Wrap such source in `aligned` so it renders as stacked, aligned rows.
 */
export const normalizeTex = (tex) => {
    if (typeof tex !== 'string') return tex;
    const src = tex.trim();
    if (/\\begin\{/.test(src)) return src;
    const hasRowBreak = /\\\\/.test(src);
    const hasAlignTab = /(^|[^\\])&/.test(src);
    if (!hasRowBreak && !hasAlignTab) return src;
    return `\\begin{aligned}${src.replace(/(\\\\\s*)+$/, '')}\\end{aligned}`;
};

// Units written as math ("kN/m^3") are set upright, not as italic variables; a lone single letter (m, s, N) may be
// a variable and is left alone. Same rule as the docs build (website/_build/docs_content.py is_unit_tex).
const UNIT_ATOM = '(?:kN|MN|N|kPa|MPa|GPa|Pa|kg|g|t|mm|cm|km|m|s|min|hr|h|yr|day|deg|rad|Hz|kJ|J)';
const UNIT_POW = '(?:\\^\\{?-?\\d+(?:\\.\\d+)?\\}?)?';
const UNIT_RE = new RegExp(`^\\s*${UNIT_ATOM}${UNIT_POW}(?:\\s*(?:/|\\\\cdot|\\*)\\s*${UNIT_ATOM}${UNIT_POW})*\\s*$`);

export const isUnitTex = (tex) => {
    const src = String(tex || '').trim();
    return UNIT_RE.test(src) && (src.replace(/[^A-Za-z]/g, '').length > 1 || /[/^]/.test(src));
};

/** A unit for display: upright when it is a unit, otherwise unchanged. */
export const unitTex = (tex) => (isUnitTex(tex) ? `\\mathrm{${String(tex).trim()}}` : tex);

/** Mends a subscript closed with ')' instead of '}' ("D_{r)"), a typo in several Groundhog docstrings. */
const fixBraces = (tex) => {
    let out = tex;
    for (let i = 0; i < 5 && (out.match(/\{/g) || []).length > (out.match(/\}/g) || []).length; i += 1) {
        const fixed = out.replace(/([_^])\{([^{}()]*)\)/, '$1{$2}');
        if (fixed === out) break;
        out = fixed;
    }
    return out;
};

/** Everything KaTeX needs before rendering docstring math: brace typos, bare multi-row equations. */
export const tidyTex = (tex) => (typeof tex === 'string' ? normalizeTex(fixBraces(tex)) : tex);

const GREEK_SYMBOL = /^(alpha|beta|gamma|delta|epsilon|eta|theta|kappa|lambda|mu|nu|xi|rho|sigma|tau|phi|varphi|chi|psi|omega|Delta|Gamma|Sigma|Phi|Psi|Omega)(?:_([A-Za-z0-9]{1,6}))?$/;

const escapeHtml = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

/**
 * Plain text that may hold math (parameter descriptions, ranges, summaries), as HTML with \( .. \) delimiters
 * for renderMathHtml: "$...$" spans, and symbols in parentheses written as bare TeX - "(\gamma_w)", "(K_{\sigma})",
 * "(q_c)". Snake-case names such as "e_min" are left as text.
 */
export const textToMathHtml = (text) => {
    if (typeof text !== 'string' || !text) return '';
    let s = escapeHtml(fixBraces(text));
    s = s.replace(/\$([^$\n]+?)\$/g, (_, tex) => `\\(${unitTex(tex)}\\)`);
    // Bare symbols in parentheses, only in the text between math that is already delimited.
    return s.split(/(\\\([\s\S]*?\\\))/).map((part, i) => (i % 2 ? part : markBareSymbols(part))).join('');
};

/** "(\gamma_w)", "(K_{\sigma})", "(q_c)", "(gamma_w)" in plain text -> the symbol as \( .. \) math. */
function markBareSymbols(s) {
    return s.replace(/\(([^()]{1,40})\)/g, (whole, inner) => {
        // A Greek letter written as a word, alone or with one subscript: "(gamma)", "(gamma_w)", "(sigma_vo)".
        const greek = GREEK_SYMBOL.exec(inner.trim());
        if (greek) return `(\\(\\${greek[1]}${greek[2] ? `_{${greek[2]}}` : ''}\\))`;
        const tex = /\\[A-Za-z]+|[A-Za-z]_\{|^\s*[A-Za-z]_[A-Za-z0-9](?![A-Za-z0-9_])/.test(inner);
        return tex ? `(\\(${inner.trim()}\\))` : whole;
    });
}

/**
 * Return `html` with its \( .. \) and \[ .. \] math (the delimiters emitted by the docs build) rendered by
 * KaTeX. Works on a detached element, so React only ever receives the finished string.
 */
export const renderMathHtml = async (html) => {
    const { renderMathInElement } = await loadKatex();
    const el = document.createElement('div');
    el.innerHTML = html;
    renderMathInElement(el, {
        delimiters: [
            { left: '\\[', right: '\\]', display: true },
            { left: '\\(', right: '\\)', display: false },
        ],
        throwOnError: false,
        preProcess: tidyTex,
    });
    return el.innerHTML;
};
