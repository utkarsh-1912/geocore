/*
 * GeoCore docs — client-side search over docs/search-index.json and "On this page" highlighting.
 * The index is fetched lazily the first time the search box is used.
 * Index format: { "version": 1, "generated": "YYYY-MM-DD", "docs": [ { id, title, url, section, summary, headings[], body } ] }
 * where url is relative to the site root (e.g. "docs/calculations/shallow-foundations.html").
 */
(function () {
  'use strict';

  // ------------------------------------------------------------------ search
  document.querySelectorAll('[data-docs-search]').forEach(function (form) {
    var input = form.querySelector('input[type="search"]');
    var list = form.querySelector('[data-search-results]');
    var live = form.querySelector('[data-search-status]');
    var root = form.getAttribute('data-root') || '';
    var indexUrl = form.getAttribute('data-index');
    var docs = null, loading = null;

    function load() {
      if (docs) return Promise.resolve(docs);
      if (!loading) {
        loading = fetch(indexUrl, { credentials: 'same-origin' })
          .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
          .then(function (data) {
            docs = (data.docs || []).map(function (d) {
              return {
                d: d,
                title: (d.title || '').toLowerCase(),
                heads: (d.headings || []).join(' ').toLowerCase(),
                summary: (d.summary || '').toLowerCase(),
                body: ((d.body || '') + ' ' + (d.section || '')).toLowerCase()
              };
            });
            return docs;
          })
          .catch(function (e) { loading = null; throw e; });
      }
      return loading;
    }

    function score(entry, terms) {
      var total = 0;
      for (var i = 0; i < terms.length; i++) {
        var t = terms[i], s = 0;
        if (entry.title.indexOf(t) === 0) s += 12;
        else if (entry.title.indexOf(t) > -1) s += 8;
        if (entry.heads.indexOf(t) > -1) s += 4;
        if (entry.summary.indexOf(t) > -1) s += 3;
        if (entry.body.indexOf(t) > -1) s += 1;
        if (!s) return 0; // every term must match somewhere
        total += s;
      }
      return total;
    }

    function hide() { list.hidden = true; input.setAttribute('aria-expanded', 'false'); }

    function show(results, q) {
      list.textContent = '';
      if (!results.length) {
        var li = document.createElement('li');
        li.className = 'empty';
        li.textContent = 'No results for “' + q + '”.';
        list.appendChild(li);
      }
      results.forEach(function (r) {
        var li = document.createElement('li');
        var a = document.createElement('a');
        a.href = /^[a-z]+:/i.test(r.url) ? r.url : root + r.url;
        a.textContent = r.title;
        var small = document.createElement('small');
        small.textContent = [r.section, r.summary].filter(Boolean).join(' — ');
        a.appendChild(small);
        li.appendChild(a);
        list.appendChild(li);
      });
      list.hidden = false;
      input.setAttribute('aria-expanded', 'true');
      live.textContent = results.length ? results.length + ' results' : 'No results';
    }

    function run() {
      var q = input.value.trim();
      if (q.length < 2) { hide(); live.textContent = ''; return; }
      var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
      load().then(function (all) {
        var results = all
          .map(function (e) { return { e: e, s: score(e, terms) }; })
          .filter(function (x) { return x.s > 0; })
          .sort(function (a, b) { return b.s - a.s; })
          .slice(0, 8)
          .map(function (x) { return x.e.d; });
        show(results, q);
      }, function () {
        list.textContent = '';
        var li = document.createElement('li');
        li.className = 'empty';
        li.textContent = 'Search is unavailable right now.';
        list.appendChild(li);
        list.hidden = false;
      });
    }

    var timer;
    input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(run, 120); });
    input.addEventListener('focus', function () { load().catch(function () {}); });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var first = list.querySelector('a');
      if (first) window.location.href = first.href;
    });
    form.addEventListener('keydown', function (e) {
      var links = Array.prototype.slice.call(list.querySelectorAll('a'));
      var i = links.indexOf(document.activeElement);
      if (e.key === 'ArrowDown' && links.length) { e.preventDefault(); (links[i + 1] || links[0]).focus(); }
      else if (e.key === 'ArrowUp' && links.length) { e.preventDefault(); if (i <= 0) input.focus(); else links[i - 1].focus(); }
      else if (e.key === 'Escape') { hide(); input.focus(); }
    });
    document.addEventListener('click', function (e) { if (!form.contains(e.target)) hide(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === '/' && document.activeElement && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) {
        e.preventDefault();
        input.focus();
      }
    });
  });

  // ------------------------------------------------------------------ table of contents highlight
  var toc = document.querySelector('[data-toc]');
  if (toc && 'IntersectionObserver' in window) {
    var links = {};
    toc.querySelectorAll('a[href^="#"]').forEach(function (a) { links[decodeURIComponent(a.getAttribute('href').slice(1))] = a; });
    var headings = Object.keys(links).map(function (id) { return document.getElementById(id); }).filter(Boolean);
    var visible = {};
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { visible[en.target.id] = en.isIntersecting; });
      var active = null;
      for (var i = 0; i < headings.length; i++) { if (visible[headings[i].id]) { active = headings[i].id; break; } }
      if (!active) return;
      Object.keys(links).forEach(function (id) { links[id].classList.toggle('is-active', id === active); });
    }, { rootMargin: '-72px 0px -60% 0px' });
    headings.forEach(function (h) { obs.observe(h); });
  }
})();
