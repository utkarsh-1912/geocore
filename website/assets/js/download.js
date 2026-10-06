/*
 * GeoCore download page.
 * Reads the latest release from the public GitHub API, detects the visitor's OS/architecture
 * and offers the matching installer. Assets are matched by pattern (not exact names) so the
 * page keeps working as file naming evolves. Everything degrades to the static
 * "GitHub Releases" link already in the HTML.
 */
(function () {
  'use strict';

  var app = document.getElementById('download-app');
  if (!app) return;

  var API = app.getAttribute('data-api');
  var RELEASES = app.getAttribute('data-releases');
  var CACHE_KEY = 'geocore-release-cache-v1';
  var CACHE_MS = 10 * 60 * 1000;

  // Release notes and the asset table sit outside #download-app, so look up in the whole document.
  var $ = function (sel) { return document.querySelector(sel); };

  // ------------------------------------------------------------------ platform detection
  function detectPlatform() {
    var ua = navigator.userAgent || '';
    var uaData = navigator.userAgentData;
    var os = 'unknown';
    var platform = uaData && uaData.platform ? uaData.platform : '';

    if (/Windows/i.test(platform) || /Windows NT/i.test(ua)) os = 'windows';
    else if (/iPhone|iPad|iPod/i.test(ua) || (/Macintosh/i.test(ua) && navigator.maxTouchPoints > 1)) os = 'ios';
    else if (/macOS/i.test(platform) || /Macintosh|Mac OS X/i.test(ua)) os = 'mac';
    else if (/Android/i.test(platform) || /Android/i.test(ua)) os = 'android';
    else if (/Linux|Chrome OS|CrOS/i.test(platform) || /Linux|X11|CrOS/i.test(ua)) os = 'linux';

    var result = { os: os, arch: 'unknown' };
    if (uaData && uaData.getHighEntropyValues) {
      return uaData.getHighEntropyValues(['architecture', 'bitness']).then(function (h) {
        if (h.architecture === 'arm') result.arch = 'arm64';
        else if (h.architecture === 'x86') result.arch = 'x64';
        return result;
      }, function () { return result; });
    }
    if (/arm64|aarch64/i.test(ua)) result.arch = 'arm64';
    return Promise.resolve(result);
  }

  // ------------------------------------------------------------------ asset classification
  function archOf(name) {
    if (/arm64|aarch64/i.test(name)) return 'arm64';
    if (/universal/i.test(name)) return 'universal';
    if (/x64|x86[_-]64|amd64|intel/i.test(name)) return 'x64';
    return 'x64'; // electron-builder omits the arch suffix for the default x64 build
  }

  function classify(asset) {
    var n = asset.name;
    if (/\.blockmap$/i.test(n) || /\.ya?ml$/i.test(n)) return { platform: 'meta', kind: 'meta', label: 'Auto-update metadata' };
    if (/\.exe$/i.test(n)) {
      if (/setup|install/i.test(n)) return { platform: 'windows', kind: 'installer', arch: 'x64', label: 'Windows installer (x64)' };
      return { platform: 'windows', kind: 'portable', arch: 'x64', label: 'Windows portable (legacy build)' };
    }
    if (/\.dmg$/i.test(n)) {
      var a = archOf(n);
      return { platform: 'mac', kind: 'dmg', arch: a, label: 'macOS disk image — ' + archLabel('mac', a) };
    }
    if (/\.zip$/i.test(n) && /mac|darwin|osx/i.test(n)) {
      var z = archOf(n);
      return { platform: 'mac', kind: 'zip', arch: z, label: 'macOS app archive (.zip) — ' + archLabel('mac', z) };
    }
    if (/\.zip$/i.test(n) && /win/i.test(n)) return { platform: 'windows', kind: 'zip', arch: 'x64', label: 'Windows archive (.zip)' };
    if (/\.appimage$/i.test(n)) return { platform: 'linux', kind: 'appimage', arch: archOf(n), label: 'Linux AppImage (portable, self-updating)' };
    if (/\.deb$/i.test(n)) return { platform: 'linux', kind: 'deb', arch: archOf(n), label: 'Linux .deb package (Debian/Ubuntu)' };
    return { platform: 'other', kind: 'other', label: 'Other file' };
  }

  function archLabel(os, arch) {
    if (os === 'mac') return arch === 'arm64' ? 'Apple silicon (M-series)' : arch === 'universal' ? 'Universal' : 'Intel';
    return arch === 'arm64' ? 'Arm64' : 'x64';
  }

  function pick(assets, platform, kind, arch) {
    for (var i = 0; i < assets.length; i++) {
      var c = assets[i].info;
      if (c.platform === platform && c.kind === kind && (!arch || c.arch === arch || c.arch === 'universal')) return assets[i];
    }
    return null;
  }

  // ------------------------------------------------------------------ formatting
  function formatSize(bytes) {
    if (!bytes && bytes !== 0) return '—';
    var mb = bytes / (1024 * 1024);
    return mb >= 1024 ? (mb / 1024).toFixed(2) + ' GB' : mb >= 10 ? Math.round(mb) + ' MB' : mb.toFixed(1) + ' MB';
  }
  function formatDate(iso) {
    if (!iso) return '—';
    var d = new Date(iso);
    if (isNaN(d.getTime())) return iso;
    try { return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }); }
    catch (e) { return iso.slice(0, 10); }
  }
  function versionOf(release, assets) {
    if (/^v?\d+\.\d+/.test(release.tag_name || '')) return (release.tag_name || '').replace(/^v/, '');
    for (var i = 0; i < assets.length; i++) {
      var m = /(\d+\.\d+\.\d+)/.exec(assets[i].name);
      if (m) return m[1];
    }
    return release.tag_name || release.name || '—';
  }

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === 'text') node.textContent = attrs[k];
      else if (k === 'class') node.className = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { if (c) node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return node;
  }
  function icon(name) {
    var ns = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('class', 'icon');
    svg.setAttribute('aria-hidden', 'true');
    var use = document.createElementNS(ns, 'use');
    use.setAttribute('href', app.getAttribute('data-icons') + '#i-' + name);
    svg.appendChild(use);
    return svg;
  }

  // ------------------------------------------------------------------ minimal, safe Markdown (text nodes only)
  function safeUrl(u) { return /^https:\/\//i.test(u) ? u : null; }

  function inline(text) {
    var frag = document.createDocumentFragment();
    var re = /\[([^\]]+)\]\(([^)\s]+)\)|\*\*([^*]+)\*\*|`([^`]+)`|(https:\/\/[^\s<)]+)|@([A-Za-z0-9-]{1,39})\b/g;
    var last = 0, m;
    while ((m = re.exec(text))) {
      if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
      if (m[1]) {
        var href = safeUrl(m[2]);
        frag.appendChild(href ? el('a', { href: href, rel: 'noopener noreferrer nofollow', text: m[1] }) : document.createTextNode(m[1]));
      } else if (m[3]) frag.appendChild(el('strong', { text: m[3] }));
      else if (m[4]) frag.appendChild(el('code', { text: m[4] }));
      else if (m[5]) {
        var url = m[5].replace(/[.,;:]+$/, '');
        var shown = url.replace(/^https:\/\/github\.com\/[^/]+\/[^/]+\/(pull|compare)\//, function (_, t) { return t === 'pull' ? '#' : ''; });
        frag.appendChild(el('a', { href: url, rel: 'noopener noreferrer nofollow', text: shown }));
        if (url.length < m[5].length) frag.appendChild(document.createTextNode(m[5].slice(url.length)));
      } else if (m[6]) frag.appendChild(document.createTextNode('@' + m[6]));
      last = re.lastIndex;
    }
    if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
    return frag;
  }

  function renderMarkdown(md, target) {
    target.textContent = '';
    var lines = String(md || '').replace(/<!--[\s\S]*?-->/g, '').replace(/\r\n?/g, '\n').split('\n');
    var list = null, para = [];
    function flushPara() {
      if (para.length) { var p = el('p'); p.appendChild(inline(para.join(' '))); target.appendChild(p); para = []; }
    }
    function flushList() { list = null; }
    lines.forEach(function (raw) {
      var line = raw.trimEnd ? raw.trimEnd() : raw.replace(/\s+$/, '');
      var h = /^(#{1,6})\s+(.*)$/.exec(line);
      var li = /^\s*[-*+]\s+(.*)$/.exec(line);
      if (!line.trim()) { flushPara(); flushList(); return; }
      if (h) {
        flushPara(); flushList();
        var node = el(h[1].length <= 2 ? 'h3' : 'h4');
        node.appendChild(inline(h[2]));
        target.appendChild(node);
      } else if (li) {
        flushPara();
        if (!list) { list = el('ul'); target.appendChild(list); }
        var item = el('li'); item.appendChild(inline(li[1])); list.appendChild(item);
      } else {
        flushList();
        para.push(line.trim());
      }
    });
    flushPara();
    if (!target.childNodes.length) target.appendChild(el('p', { class: 'muted', text: 'No release notes were published for this release.' }));
  }

  // ------------------------------------------------------------------ data
  function readCache() {
    try {
      var c = JSON.parse(sessionStorage.getItem(CACHE_KEY) || 'null');
      if (c && Date.now() - c.t < CACHE_MS) return c.data;
    } catch (e) { /* ignore */ }
    return null;
  }
  function writeCache(data) {
    try { sessionStorage.setItem(CACHE_KEY, JSON.stringify({ t: Date.now(), data: data })); } catch (e) { /* ignore */ }
  }

  function fetchRelease() {
    var cached = readCache();
    if (cached) return Promise.resolve(cached);
    var ctrl = window.AbortController ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 10000);
    return fetch(API, {
      headers: { Accept: 'application/vnd.github+json' },
      signal: ctrl ? ctrl.signal : undefined,
      referrerPolicy: 'no-referrer',
      credentials: 'omit'
    }).then(function (res) {
      clearTimeout(timer);
      if (res.status === 403 || res.status === 429) {
        var err = new Error('GitHub API rate limit reached');
        err.rateLimited = true;
        throw err;
      }
      if (res.status === 404) throw new Error('No published release was found');
      if (!res.ok) throw new Error('GitHub API returned HTTP ' + res.status);
      return res.json();
    }).then(function (data) {
      var slim = {
        tag_name: data.tag_name, name: data.name, html_url: data.html_url,
        published_at: data.published_at, body: data.body || '',
        assets: (data.assets || []).map(function (a) {
          return { name: a.name, size: a.size, browser_download_url: a.browser_download_url };
        })
      };
      writeCache(slim);
      return slim;
    }, function (e) { clearTimeout(timer); throw e; });
  }

  // ------------------------------------------------------------------ rendering
  function setStatus(text, state) {
    var s = $('[data-dl-status]');
    if (!s) return;
    s.textContent = text;
    if (state) s.setAttribute('data-state', state); else s.removeAttribute('data-state');
  }

  function render(release, env) {
    var assets = release.assets
      .filter(function (a) { return /^https:\/\//i.test(a.browser_download_url || ''); })
      .map(function (a) { a.info = classify(a); return a; });
    var version = versionOf(release, assets);

    var primary = null, alternatives = [], osLabel = '', note = '';
    var win = pick(assets, 'windows', 'installer');
    var macArm = pick(assets, 'mac', 'dmg', 'arm64');
    var macIntel = pick(assets, 'mac', 'dmg', 'x64');
    var linuxAppImage = pick(assets, 'linux', 'appimage');
    var linuxDeb = pick(assets, 'linux', 'deb');

    if (env.os === 'windows') {
      osLabel = 'Windows 10 / 11 (64-bit)';
      primary = win;
      if (env.arch === 'arm64') note = 'GeoCore is built for x64. Windows 11 on Arm runs x64 apps through emulation; this combination has not been tested.';
      alternatives = [macArm, macIntel, linuxAppImage, linuxDeb];
    } else if (env.os === 'mac') {
      if (env.arch === 'x64') { primary = macIntel; osLabel = 'macOS — Intel'; alternatives = [macArm]; }
      else {
        primary = macArm || macIntel;
        osLabel = env.arch === 'arm64' ? 'macOS — Apple silicon' : 'macOS';
        alternatives = [macIntel];
        if (env.arch === 'unknown') note = 'Your browser does not report the processor type. This is the Apple silicon (M-series) build; on an Intel Mac use the Intel build below.';
      }
      alternatives.push(win, linuxAppImage, linuxDeb);
    } else if (env.os === 'linux') {
      osLabel = 'Linux (x64)';
      primary = linuxAppImage || linuxDeb;
      note = linuxAppImage
        ? 'AppImage: make it executable (chmod +x) and run it directly — no installation needed, and it auto-updates in place. Prefer a system package instead? Use the .deb download below (no auto-update).'
        : linuxDeb
          ? 'The .deb package (Debian/Ubuntu) does not auto-update; reinstall it for each new release.'
          : '';
      alternatives = [primary === linuxAppImage ? linuxDeb : linuxAppImage, win, macArm, macIntel];
    } else {
      osLabel = env.os === 'ios' || env.os === 'android' ? 'Mobile device' : 'Your system';
      note = env.os === 'ios' || env.os === 'android'
        ? 'GeoCore is a desktop application for Windows, macOS and Linux. Pick an installer below to download it on your computer.'
        : 'We could not detect your operating system. Pick an installer below.';
      alternatives = [win, macArm, macIntel, linuxAppImage, linuxDeb];
    }

    // Primary card
    $('[data-dl-os]').textContent = osLabel;
    $('[data-dl-version]').textContent = version;
    $('[data-dl-version-meta]').textContent = version;
    $('[data-dl-date]').textContent = formatDate(release.published_at);
    var btn = $('[data-dl-button]');
    var fileEl = $('[data-dl-file]');
    var KIND_LABEL = { installer: 'installer', dmg: 'disk image', appimage: 'AppImage', deb: '.deb package' };
    if (primary) {
      btn.setAttribute('href', primary.browser_download_url);
      btn.querySelector('[data-dl-button-label]').textContent = 'Download ' + (KIND_LABEL[primary.info.kind] || 'file');
      $('[data-dl-size]').textContent = formatSize(primary.size);
      $('[data-dl-arch]').textContent = archLabel(primary.info.platform, primary.info.arch);
      fileEl.textContent = primary.name;
    } else {
      btn.setAttribute('href', release.html_url || RELEASES);
      btn.querySelector('[data-dl-button-label]').textContent = 'Choose a file on GitHub';
      $('[data-dl-size]').textContent = '—';
      $('[data-dl-arch]').textContent = '—';
      fileEl.textContent = env.os === 'windows' || env.os === 'mac' || env.os === 'linux'
        ? 'No matching installer was found in the latest release.'
        : '';
    }
    var noteEl = $('[data-dl-note]');
    noteEl.textContent = note;
    noteEl.hidden = !note;
    $('[data-dl-release-link]').setAttribute('href', release.html_url || RELEASES);

    // Alternatives
    var alt = $('[data-dl-alternatives]');
    alt.textContent = '';
    alternatives.filter(function (a, i, arr) { return a && a !== primary && arr.indexOf(a) === i; }).forEach(function (a) {
      var label = a.info.platform === 'windows' ? 'Windows (x64)'
        : a.info.platform === 'mac' ? 'macOS — ' + archLabel('mac', a.info.arch)
        : 'Linux — ' + (a.info.kind === 'appimage' ? 'AppImage' : '.deb package');
      var iconName = a.info.platform === 'windows' ? 'monitor' : a.info.platform === 'mac' ? 'laptop' : 'package';
      alt.appendChild(el('a', { class: 'dl-other', href: a.browser_download_url }, [
        icon(iconName),
        el('span', { class: 'grow' }, [label, el('small', { text: a.name + ' · ' + formatSize(a.size) })]),
        icon('download')
      ]));
    });
    if (!alt.childNodes.length) alt.appendChild(el('p', { class: 'muted small', text: 'No other installers in this release.' }));

    // All assets table
    var tbody = $('[data-dl-assets]');
    tbody.textContent = '';
    var order = { windows: 0, mac: 1, linux: 2, other: 3, meta: 4 };
    assets.slice().sort(function (a, b) {
      return (order[a.info.platform] - order[b.info.platform]) || a.name.localeCompare(b.name);
    }).forEach(function (a) {
      var link = el('a', { href: a.browser_download_url, text: a.name });
      tbody.appendChild(el('tr', null, [
        el('td', { class: 'dl-file' }, [link]),
        el('td', { text: a.info.label }),
        el('td', { class: 'num', text: formatSize(a.size) })
      ]));
    });
    if (!assets.length) tbody.appendChild(el('tr', null, [el('td', { colspan: '3', text: 'This release has no downloadable files.' })]));

    renderMarkdown(release.body, $('[data-dl-notes]'));
    $('[data-dl-notes-title]').textContent = 'Release notes — ' + (release.name || version);

    app.setAttribute('data-state', 'ready');
    setStatus('Latest release from GitHub · checked ' + new Date().toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }));
  }

  function fail(err) {
    app.setAttribute('data-state', 'error');
    var msg = err && err.rateLimited
      ? 'GitHub’s API rate limit was reached for your network, so release details could not be loaded.'
      : 'Release details could not be loaded from GitHub' + (err && err.message ? ' (' + err.message + ')' : '') + '.';
    setStatus(msg + ' Use the button to download from the GitHub releases page.', 'error');
    ['[data-dl-version-meta]', '[data-dl-date]', '[data-dl-size]', '[data-dl-arch]'].forEach(function (s) {
      var n = $(s); if (n) { n.textContent = '—'; n.classList.remove('skeleton'); }
    });
    var v = $('[data-dl-version]');
    if (v) { v.textContent = 'latest release'; v.classList.remove('skeleton'); }
    var notes = $('[data-dl-notes]');
    if (notes) {
      notes.textContent = '';
      var p = el('p', null, ['Release notes are available on ']);
      p.appendChild(el('a', { href: RELEASES, text: 'GitHub Releases' }));
      p.appendChild(document.createTextNode('.'));
      notes.appendChild(p);
    }
    var tbody = $('[data-dl-assets]');
    if (tbody) {
      tbody.textContent = '';
      var td = el('td', { colspan: '3' }, ['See all files on ']);
      td.appendChild(el('a', { href: RELEASES, text: 'GitHub Releases' }));
      td.appendChild(document.createTextNode('.'));
      tbody.appendChild(el('tr', null, [td]));
    }
    var alt = $('[data-dl-alternatives]');
    if (alt) alt.textContent = '';
  }

  if (!window.fetch || !window.Promise) return; // static fallback stays in place

  Promise.all([detectPlatform(), fetchRelease()])
    .then(function (r) {
      document.querySelectorAll('.skeleton').forEach(function (n) { n.classList.remove('skeleton'); });
      render(r[1], r[0]);
    })
    .catch(fail);
})();
