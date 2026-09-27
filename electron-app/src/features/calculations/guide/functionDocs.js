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
    });
    return el.innerHTML;
};
