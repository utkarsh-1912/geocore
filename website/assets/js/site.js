/* GeoCore website — shared behaviour: theme toggle, mobile navigation, docs sidebar toggle. */
(function () {
  'use strict';

  var root = document.documentElement;
  var KEY = 'geocore-theme';
  var media = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  function systemTheme() { return media && media.matches ? 'dark' : 'light'; }
  function currentTheme() { return root.getAttribute('data-theme') || systemTheme(); }

  function store(value) {
    try {
      if (value) localStorage.setItem(KEY, value); else localStorage.removeItem(KEY);
    } catch (e) { /* ignore */ }
  }

  function updateToggles() {
    var next = currentTheme() === 'dark' ? 'light' : 'dark';
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      btn.setAttribute('aria-label', 'Switch to ' + next + ' theme');
      btn.setAttribute('title', 'Switch to ' + next + ' theme');
    });
  }

  document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      if (next === systemTheme()) {
        // Choosing the OS theme means "follow the OS" again.
        root.removeAttribute('data-theme');
        store(null);
      } else {
        root.setAttribute('data-theme', next);
        store(next);
      }
      updateToggles();
    });
  });
  if (media && media.addEventListener) media.addEventListener('change', updateToggles);
  updateToggles();

  // Disclosure pattern shared by the mobile menu and the docs sidebar.
  function disclosure(button, panel, closeOnEscape) {
    if (!button || !panel) return;
    function set(open) {
      button.setAttribute('aria-expanded', String(open));
      panel.hidden = !open;
      var label = button.getAttribute(open ? 'data-label-close' : 'data-label-open');
      if (label) button.setAttribute('aria-label', label);
      button.querySelectorAll('[data-when]').forEach(function (el) {
        el.style.display = (el.getAttribute('data-when') === (open ? 'open' : 'closed')) ? '' : 'none';
      });
    }
    set(false);
    button.addEventListener('click', function () { set(button.getAttribute('aria-expanded') !== 'true'); });
    if (closeOnEscape) {
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') { set(false); button.focus(); }
      });
      panel.addEventListener('click', function (e) { if (e.target.closest('a')) set(false); });
    }
  }

  disclosure(document.querySelector('[data-nav-toggle]'), document.getElementById('mobile-nav'), true);
  disclosure(document.querySelector('[data-sidebar-toggle]'), document.getElementById('docs-sidebar-panel'), false);
})();
