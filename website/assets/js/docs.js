/*
 * GeoCore docs — client-side search over docs/search-index.json.
 * "On this page" highlighting is shared with the other pages and lives in site.js.
 * The index is fetched lazily the first time the search box is used.
 * Index format: { "version": 1, "generated": "YYYY-MM-DD", "docs": [ { id, title, url, section, summary, headings[], body } ] }
 * where url is relative to the site root (e.g. "docs/calculations/shallow-foundations.html").
 */
(function () {
  'use strict';

  // ------------------------------------------------------------------ search
  // Identifiers such as "ShallowFoundationCapacityDrained.calculate_bearing_capacity" are split into
  // words so "bearing capacity" matches them. The unsplit form is kept too, so "geoai" still finds
  // "GeoAI". Every field is padded with spaces so " term" means "starts a word".
  function normalise(text) {
    var plain = String(text || '').replace(/[_.\-/#:()]+/g, ' ');
    var split = plain.replace(/([a-z0-9])([A-Z])/g, '$1 $2');
    return (' ' + plain + (split !== plain ? ' ' + split : '') + ' ').toLowerCase().replace(/\s+/g, ' ');
  }

  function sectionLabel(section) {
    // "groundhog.shallowfoundations.capacity" -> "Groundhog API · shallowfoundations.capacity"
    if (/^groundhog\./.test(section || '')) return 'Groundhog API · ' + section.replace(/^groundhog\./, '');
    return section || '';
  }

  // Weight per field: [name, word-start match, substring match]
  var FIELDS = [['title', 12, 6], ['heads', 4, 2], ['summary', 3, 1], ['body', 1, 0.5]];

  function score(entry, terms, phrase) {
    var total = 0, inTitle = 0;
    for (var i = 0; i < terms.length; i++) {
      var t = terms[i], best = 0;
      for (var f = 0; f < FIELDS.length; f++) {
        var text = entry[FIELDS[f][0]];
        var s = text.indexOf(' ' + t) > -1 ? FIELDS[f][1] : (text.indexOf(t) > -1 ? FIELDS[f][2] : 0);
        if (s > best) best = s;
      }
      if (!best) return 0; // every term must match somewhere
      if (best >= FIELDS[0][2]) inTitle++;
      total += best;
    }
    if (inTitle === terms.length) total += 10;                   // whole query is in the title
    if (terms.length > 1) {
      if (entry.title.indexOf(phrase) > -1) total += 12;          // ...as a phrase
      else if (entry.heads.indexOf(phrase) > -1 || entry.summary.indexOf(phrase) > -1) total += 4;
    }
    if (entry.guide) total += 2;                                  // prefer written guides over API members
    return total - Math.min(entry.title.length, 120) / 60;        // shorter titles win ties
  }

  // Append `text` to `el`, wrapping the query terms in <mark>. Built with DOM nodes, never innerHTML.
  function appendHighlighted(el, text, terms) {
    text = String(text || '');
    if (!terms.length) { el.appendChild(document.createTextNode(text)); return; }
    var escaped = terms.map(function (t) { return t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); });
    var re = new RegExp('(' + escaped.join('|') + ')', 'ig');
    var last = 0, m;
    while ((m = re.exec(text))) {
      if (m.index > last) el.appendChild(document.createTextNode(text.slice(last, m.index)));
      var mark = document.createElement('mark');
      mark.textContent = m[0];
      el.appendChild(mark);
      last = m.index + m[0].length;
      if (!m[0].length) re.lastIndex++;
    }
    if (last < text.length) el.appendChild(document.createTextNode(text.slice(last)));
  }

  document.querySelectorAll('[data-docs-search]').forEach(function (form) {
    var input = form.querySelector('input[type="search"]');
    var list = form.querySelector('[data-search-results]');
    var live = form.querySelector('[data-search-status]');
    var root = form.getAttribute('data-root') || '';
    var indexUrl = form.getAttribute('data-index');
    var docs = null, loading = null, active = -1, seq = 0;

    function load() {
      if (docs) return Promise.resolve(docs);
      if (!loading) {
        loading = fetch(indexUrl, { credentials: 'same-origin' })
          .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
          .then(function (data) {
            docs = (data.docs || []).map(function (d) {
              return {
                d: d,
                title: normalise(d.title),
                heads: normalise((d.headings || []).join(' ')),
                summary: normalise(d.summary),
                body: normalise((d.body || '') + ' ' + (d.section || '')),
                guide: !/^groundhog\./.test(d.section || '') && d.section !== 'Groundhog API Reference'
              };
            });
            return docs;
          })
          .catch(function (e) { loading = null; throw e; });
      }
      return loading;
    }

    function options() { return Array.prototype.slice.call(list.querySelectorAll('[role="option"]')); }

    function setActive(i) {
      var opts = options();
      if (!opts.length) { active = -1; input.removeAttribute('aria-activedescendant'); return; }
      active = (i + opts.length) % opts.length;
      opts.forEach(function (o, j) { o.setAttribute('aria-selected', String(j === active)); });
      input.setAttribute('aria-activedescendant', opts[active].id);
      opts[active].scrollIntoView({ block: 'nearest' });
    }

    function hide() {
      list.hidden = true;
      active = -1;
      input.setAttribute('aria-expanded', 'false');
      input.removeAttribute('aria-activedescendant');
    }

    function message(text) {
      list.textContent = '';
      var li = document.createElement('li');
      li.className = 'empty';
      li.textContent = text;
      list.appendChild(li);
      list.hidden = false;
      input.setAttribute('aria-expanded', 'true');
    }

    function show(results, q, terms) {
      if (!results.length) { message('No results for “' + q + '”.'); live.textContent = 'No results'; return; }
      list.textContent = '';
      results.forEach(function (r, i) {
        var li = document.createElement('li');
        var a = document.createElement('a');
        a.id = 'docs-search-opt-' + i;
        a.setAttribute('role', 'option');
        a.setAttribute('aria-selected', 'false');
        a.tabIndex = -1;
        a.href = /^[a-z]+:/i.test(r.url) ? r.url : root + r.url;
        var title = document.createElement('span');
        title.className = 'sr-title';
        // Let long identifiers wrap at '.', '_' and camelCase joins instead of mid-word.
        appendHighlighted(title, String(r.title || '').replace(/([._])/g, '$1\u200B').replace(/([a-z])([A-Z])/g, '$1\u200B$2'), terms);
        a.appendChild(title);
        var section = sectionLabel(r.section);
        if (section) {
          var sec = document.createElement('span');
          sec.className = 'sr-section';
          sec.textContent = section;
          a.appendChild(sec);
        }
        if (r.summary) {
          var small = document.createElement('small');
          appendHighlighted(small, r.summary, terms);
          a.appendChild(small);
        }
        li.appendChild(a);
        list.appendChild(li);
      });
      list.hidden = false;
      list.scrollTop = 0;
      input.setAttribute('aria-expanded', 'true');
      setActive(0);
      live.textContent = results.length + (results.length === 1 ? ' result' : ' results');
    }

    function run() {
      var q = input.value.trim();
      if (q.length < 2) { hide(); live.textContent = ''; return; }
      var terms = normalise(q).trim().split(' ').filter(Boolean);
      var phrase = terms.join(' ');
      var mine = ++seq;
      if (!docs) message('Searching…');
      load().then(function (all) {
        if (mine !== seq) return; // a newer query is already running
        var results = all
          .map(function (e) { return { e: e, s: score(e, terms, phrase) }; })
          .filter(function (x) { return x.s > 0; })
          .sort(function (a, b) { return b.s - a.s; })
          .slice(0, 12)
          .map(function (x) { return x.e.d; });
        show(results, q, terms);
      }, function () {
        if (mine === seq) message('Search is unavailable right now.');
      });
    }

    var timer;
    input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(run, 100); });
    input.addEventListener('focus', function () {
      load().catch(function () {});
      if (input.value.trim().length >= 2 && list.hidden) run();
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var opts = options();
      var target = opts[active] || opts[0];
      if (target) window.location.href = target.href;
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); if (list.hidden) run(); else setActive(active + 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(active - 1); }
      else if (e.key === 'Escape') {
        if (!list.hidden) { e.preventDefault(); hide(); }
        else if (input.value) { e.preventDefault(); input.value = ''; live.textContent = ''; }
        else input.blur();
      }
    });
    list.addEventListener('mousemove', function (e) {
      var opt = e.target.closest('[role="option"]');
      if (opt) setActive(options().indexOf(opt));
    });
    document.addEventListener('click', function (e) { if (!form.contains(e.target)) hide(); });
    document.addEventListener('keydown', function (e) {
      var el = document.activeElement;
      var typing = el && (/INPUT|TEXTAREA|SELECT/.test(el.tagName) || el.isContentEditable);
      if (typing) return;
      if (e.key === '/' || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k')) {
        e.preventDefault();
        input.focus();
        input.select();
      }
    });
  });
})();
