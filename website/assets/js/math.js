/* Render LaTeX in docs pages with the vendored KaTeX (assets/vendor/katex). Loaded only on pages with math.
 * The build emits math as \( ... \) and \[ ... \]; only those delimiters are used, so a stray "$" in prose is safe.
 *
 * CSP note: the site's policy is style-src 'self' (no inline style attributes). KaTeX sets a few styles with
 * element.setAttribute('style', ...) (SVG widths, error colour), which that policy blocks. Styles applied through
 * the CSSOM (element.style.cssText) are allowed, so while KaTeX renders we route setAttribute('style', v) to
 * style.cssText. The shim is removed as soon as rendering finishes. */
(function () {
  'use strict';

  function withCssomStyles(fn) {
    var proto = Element.prototype;
    var original = proto.setAttribute;
    proto.setAttribute = function (name, value) {
      if (typeof name === 'string' && name.toLowerCase() === 'style' && this.style) {
        this.style.cssText = String(value);
        return undefined;
      }
      return original.apply(this, arguments);
    };
    try { fn(); } finally { proto.setAttribute = original; }
  }

  function run() {
    if (!window.renderMathInElement) return;
    var target = document.querySelector('.docs-body') || document.body;
    withCssomStyles(function () {
      window.renderMathInElement(target, {
        delimiters: [
          { left: '\\[', right: '\\]', display: true },
          { left: '\\(', right: '\\)', display: false }
        ],
        ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'option'],
        throwOnError: false,
        strict: 'ignore',
        trust: false
      });
    });
    document.documentElement.setAttribute('data-math', 'rendered');
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run);
  else run();
})();
