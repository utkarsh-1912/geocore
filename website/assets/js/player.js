/*
 * GeoCore tutorial player: custom controls over the YouTube IFrame API.
 *
 * Privacy: nothing from YouTube is requested until the visitor presses play. The video then loads from
 * youtube-nocookie.com. Chapters come from the page (buttons with data-t inside [data-gc-chapters]).
 * Deep link to a moment with #t=83 (seconds) or #t=1m23s.
 */
(function () {
  'use strict';

  var root = document.querySelector('[data-gc-player]');
  if (!root) return;

  var STORE = 'geocore-player';
  var VIDEO_ID = root.getAttribute('data-video-id');
  var TITLE = root.getAttribute('data-title') || 'Tutorial';
  var NEXT_URL = root.getAttribute('data-next-url');
  var NEXT_TITLE = root.getAttribute('data-next-title');
  var stage = root.querySelector('.gc-player__stage');
  var videoHost = root.querySelector('[data-gc-video]');
  var startBtn = root.querySelector('[data-gc-start]');
  var chapterBtns = Array.prototype.slice.call(document.querySelectorAll('[data-gc-chapters] [data-t]'));
  var chapters = chapterBtns.map(function (b) {
    return { t: Number(b.getAttribute('data-t')), title: b.querySelector('.tut-chapter__title').textContent };
  });

  var muted = false;
  var yt = null, ready = false, started = false, playing = false, scrubbing = false;
  var duration = Number(root.getAttribute('data-duration')) || 0;
  var timer = null, idleTimer = null, clickTimer = null, startAt = 0;
  var prefs = load();

  /* ---------- helpers ---------- */
  function load() {
    try { return JSON.parse(localStorage.getItem(STORE)) || {}; } catch (e) { return {}; }
  }
  function save() {
    try { localStorage.setItem(STORE, JSON.stringify(prefs)); } catch (e) { /* storage unavailable */ }
  }
  function clock(s) {
    s = Math.max(0, Math.floor(s || 0));
    var h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), sec = s % 60;
    return (h ? h + ':' + (m < 10 ? '0' : '') : '') + m + ':' + (sec < 10 ? '0' : '') + sec;
  }
  function parseTime(v) {
    if (!v) return 0;
    if (/^\d+$/.test(v)) return Number(v);
    var m = /^(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?$/.exec(v);
    return m ? (Number(m[1] || 0) * 3600 + Number(m[2] || 0) * 60 + Number(m[3] || 0)) : 0;
  }
  function startFromUrl() {
    var m = /(?:^|&)t=([^&]+)/.exec(location.hash.slice(1)) || /[?&]t=([^&]+)/.exec(location.search);
    return m ? parseTime(m[1]) : 0;
  }
  var NS = 'http://www.w3.org/2000/svg';
  function svg(path, extra) {
    var s = document.createElementNS(NS, 'svg');
    s.setAttribute('viewBox', '0 0 24 24');
    s.setAttribute('aria-hidden', 'true');
    s.setAttribute('focusable', 'false');
    var p = document.createElementNS(NS, 'path');
    p.setAttribute('d', path);
    s.appendChild(p);
    if (extra) {
      var q = document.createElementNS(NS, 'path');
      q.setAttribute('d', extra);
      q.setAttribute('fill', 'none');
      q.setAttribute('stroke', 'currentColor');
      q.setAttribute('stroke-width', '2');
      q.setAttribute('stroke-linecap', 'round');
      s.appendChild(q);
    }
    return s;
  }
  function setIcon(btn, path, extra) {
    btn.textContent = '';
    btn.appendChild(svg(path, extra));
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;
    return e;
  }
  function btn(label, cls) {
    var b = el('button', 'gc-btn' + (cls ? ' ' + cls : ''));
    b.type = 'button';
    b.setAttribute('aria-label', label);
    b.title = label;
    return b;
  }

  var ICON = {
    play: 'M8 5v14l11-7z',
    pause: 'M6 5h4v14H6zM14 5h4v14h-4z',
    vol: 'M3 9v6h4l5 5V4L7 9zM16 8.5a5 5 0 0 1 0 7l-1.4-1.4a3 3 0 0 0 0-4.2z',
    mute: 'M3 9v6h4l5 5V4L7 9z',
    muteX: 'M16 9l5 6M21 9l-5 6',
    full: 'M7 14H5v5h5v-2H7zm-2-4h2V7h3V5H5zm12 7h-3v2h5v-5h-2zM14 5v2h3v3h2V5z',
    exit: 'M5 16h3v3h2v-5H5zm3-8H5v2h5V5H8zm6 11h2v-3h3v-2h-5zm2-11V5h-2v5h5V8z',
    replay: 'M12 5V1L7 6l5 5V7a6 6 0 1 1-6 6H4a8 8 0 1 0 8-8z'
  };

  /* ---------- controls ---------- */
  var shield = el('div', 'gc-player__shield');
  var flash = el('div', 'gc-player__flash');
  var spinner = el('div', 'gc-player__spinner');
  var bar = el('div', 'gc-bar');

  var seekWrap = el('div', 'gc-seekwrap');
  var fill = el('div', 'gc-fill');
  var seek = el('input', 'gc-seek');
  seek.type = 'range'; seek.min = '0'; seek.max = '1000'; seek.step = '1'; seek.value = '0';
  seek.setAttribute('aria-label', 'Seek');
  var tip = el('div', 'gc-tip');
  seekWrap.appendChild(fill);
  chapters.forEach(function (c) {
    if (c.t <= 0) return;
    var tick = el('div', 'gc-tick');
    tick.style.setProperty('--at', String(duration ? c.t / duration : 0));
    seekWrap.appendChild(tick);
  });
  seekWrap.appendChild(seek);
  seekWrap.appendChild(tip);

  var row = el('div', 'gc-row');
  var playBtn = btn('Play (k)');
  setIcon(playBtn, ICON.play);
  var volWrap = el('div', 'gc-volwrap');
  var muteBtn = btn('Mute (m)');
  setIcon(muteBtn, ICON.vol);
  var vol = el('input', 'gc-vol');
  vol.type = 'range'; vol.min = '0'; vol.max = '100'; vol.step = '1'; vol.value = String(prefs.vol != null ? prefs.vol : 100);
  vol.setAttribute('aria-label', 'Volume');
  volWrap.appendChild(muteBtn); volWrap.appendChild(vol);
  var timeEl = el('span', 'gc-time', '0:00 / ' + clock(duration));
  var grow = el('span', 'gc-grow');
  var menuWrap = el('div', 'gc-menuwrap');
  var speedBtn = btn('Playback speed', 'gc-speed');
  speedBtn.textContent = '1x';
  speedBtn.setAttribute('aria-haspopup', 'true');
  speedBtn.setAttribute('aria-expanded', 'false');
  var menu = el('ul', 'gc-menu');
  menu.hidden = true;
  menu.setAttribute('role', 'menu');
  menuWrap.appendChild(speedBtn); menuWrap.appendChild(menu);
  var fsBtn = btn('Fullscreen (f)');
  setIcon(fsBtn, ICON.full);

  [playBtn, volWrap, timeEl, grow, menuWrap, fsBtn].forEach(function (n) { row.appendChild(n); });
  bar.appendChild(seekWrap); bar.appendChild(row);

  var endCard = el('div', 'gc-end');
  endCard.setAttribute('role', 'dialog');
  endCard.setAttribute('aria-label', 'Video finished');
  endCard.appendChild(el('h2', '', 'Nice work'));
  endCard.appendChild(el('p', '', NEXT_TITLE ? 'Up next: ' + NEXT_TITLE : 'Download GeoCore and repeat the steps with your own data.'));
  var actions = el('div', 'gc-end__actions');
  var replay = el('button', 'btn btn--secondary', 'Replay');
  replay.type = 'button';
  actions.appendChild(replay);
  var nextLink = el('a', 'btn btn--primary', NEXT_URL ? 'Next tutorial' : 'Download');
  nextLink.href = NEXT_URL || (root.querySelector('a[href$="download.html"]') || { href: '#' }).href;
  actions.appendChild(nextLink);
  endCard.appendChild(actions);

  stage.appendChild(shield); stage.appendChild(flash); stage.appendChild(spinner); stage.appendChild(bar); stage.appendChild(endCard);

  /* ---------- API ---------- */
  var apiPromise = null;
  function loadApi() {
    if (apiPromise) return apiPromise;
    apiPromise = new Promise(function (resolve, reject) {
      if (window.YT && window.YT.Player) return resolve(window.YT);
      var prev = window.onYouTubeIframeAPIReady;
      window.onYouTubeIframeAPIReady = function () { if (prev) prev(); resolve(window.YT); };
      var s = document.createElement('script');
      s.src = 'https://www.youtube.com/iframe_api';
      s.async = true;
      s.onerror = function () { reject(new Error('script')); };
      document.head.appendChild(s);
      setTimeout(function () { reject(new Error('timeout')); }, 12000);
    });
    return apiPromise;
  }

  function fail() {
    root.classList.remove('is-loading');
    spinner.style.opacity = '0';
    if (stage.querySelector('.gc-error')) return;
    var box = el('div', 'gc-error');
    box.setAttribute('role', 'alert');
    box.appendChild(document.createTextNode('The video could not be loaded (offline, or YouTube is blocked). '));
    var a = el('a', '', 'Watch on YouTube');
    a.href = 'https://www.youtube.com/watch?v=' + VIDEO_ID;
    a.rel = 'noopener';
    box.appendChild(a);
    stage.appendChild(box);
  }

  function begin(at) {
    if (started) {
      if (typeof at === 'number') seekTo(at, true);
      play();
      return;
    }
    started = true;
    startAt = typeof at === 'number' ? at : 0;
    root.classList.add('is-started', 'is-loading');
    stage.focus({ preventScroll: true });
    loadApi().then(function (YT) {
      var mount = document.createElement('div');
      videoHost.appendChild(mount);
      yt = new YT.Player(mount, {
        host: 'https://www.youtube-nocookie.com',
        videoId: VIDEO_ID,
        width: '100%',
        height: '100%',
        playerVars: { controls: 0, disablekb: 1, fs: 0, rel: 0, playsinline: 1, iv_load_policy: 3, modestbranding: 1, autoplay: 1, start: Math.floor(startAt), origin: location.origin },
        events: { onReady: onReady, onStateChange: onState, onPlaybackRateChange: function () { syncSpeedUi(); }, onError: fail }
      });
    }).catch(fail);
  }

  function onReady() {
    ready = true;
    root.classList.add('is-ready');
    var d = yt.getDuration && yt.getDuration();
    if (d) { duration = d; }
    yt.setVolume(Number(vol.value));
    muted = !!prefs.muted;
    if (muted) yt.mute();
    if (prefs.rate) yt.setPlaybackRate(prefs.rate);
    syncVolumeUi();
    buildSpeedMenu();
    syncSpeedUi();
    yt.playVideo();
    setTimeout(function () { if (!playing) root.classList.remove('is-loading'); }, 2500);
    tick();
  }

  function onState(e) {
    var S = window.YT.PlayerState;
    playing = e.data === S.PLAYING;
    root.classList.toggle('is-playing', playing);
    root.classList.toggle('is-loading', e.data === S.BUFFERING || e.data === S.UNSTARTED);
    root.classList.toggle('is-ended', e.data === S.ENDED);
    setIcon(playBtn, playing ? ICON.pause : (e.data === S.ENDED ? ICON.replay : ICON.play));
    var label = playing ? 'Pause (k)' : 'Play (k)';
    playBtn.setAttribute('aria-label', label); playBtn.title = label;
    var d = yt.getDuration && yt.getDuration();
    if (d) duration = d;
    if (playing) { startTimer(); wake(); } else { stopTimer(); tick(); root.classList.remove('is-idle'); }
    if (e.data === S.ENDED) { root.classList.remove('is-idle'); try { replay.focus({ preventScroll: true }); } catch (err) { /* ignore */ } }
  }

  /* ---------- transport ---------- */
  function play() { if (ready) yt.playVideo(); }
  function pause() { if (ready) yt.pauseVideo(); }
  function toggle() {
    if (!started) return begin();
    if (!ready) return;
    if (root.classList.contains('is-ended')) return replayVideo();
    playing ? pause() : play();
    pulse(playing ? ICON.pause : ICON.play);
  }
  function replayVideo() { root.classList.remove('is-ended'); seekTo(0, true); play(); }
  function seekTo(t, ahead) {
    if (!ready) return;
    t = Math.min(Math.max(0, t), duration || t);
    yt.seekTo(t, ahead !== false);
    paint(t);
  }
  function skip(delta) {
    if (!ready) return;
    seekTo(yt.getCurrentTime() + delta, true);
    wake();
  }
  function pulse(path) {
    setIcon(flash, path);
    flash.classList.remove('is-on');
    void flash.offsetWidth;
    flash.classList.add('is-on');
  }

  /* ---------- progress ---------- */
  function startTimer() { stopTimer(); timer = setInterval(tick, 250); }
  function stopTimer() { if (timer) { clearInterval(timer); timer = null; } }
  function chapterAt(t) {
    var idx = -1;
    for (var i = 0; i < chapters.length; i++) if (chapters[i].t <= t + 0.25) idx = i;
    return idx;
  }
  function paint(t) {
    var d = duration || 1;
    var p = Math.min(1, t / d);
    root.style.setProperty('--p', p.toFixed(4));
    if (!scrubbing) seek.value = String(Math.round(p * 1000));
    timeEl.textContent = clock(t) + ' / ' + clock(d);
    seek.setAttribute('aria-valuetext', clock(t) + ' of ' + clock(d));
    var active = chapterAt(t);
    chapterBtns.forEach(function (b, i) { b.classList.toggle('is-active', i === active); if (i === active) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current'); });
  }
  function tick() {
    if (!ready || !yt.getCurrentTime) return;
    paint(yt.getCurrentTime());
  }
  seek.addEventListener('input', function () {
    scrubbing = true;
    var t = (Number(seek.value) / 1000) * (duration || 0);
    paint(t);
    if (ready) yt.seekTo(t, false);
  });
  seek.addEventListener('change', function () {
    var t = (Number(seek.value) / 1000) * (duration || 0);
    scrubbing = false;
    seekTo(t, true);
  });
  seekWrap.addEventListener('mousemove', function (e) {
    var r = seekWrap.getBoundingClientRect();
    var f = Math.min(1, Math.max(0, (e.clientX - r.left) / r.width));
    var t = f * (duration || 0);
    var c = chapterAt(t);
    tip.textContent = clock(t) + (c >= 0 ? ' · ' + chapters[c].title : '');
    seekWrap.style.setProperty('--hover', f.toFixed(4));
  });

  /* ---------- volume ---------- */
  function syncVolumeUi() {
    var v = Number(vol.value);
    if (muted || v === 0) setIcon(muteBtn, ICON.mute, ICON.muteX); else setIcon(muteBtn, ICON.vol);
    muteBtn.setAttribute('aria-label', muted ? 'Unmute (m)' : 'Mute (m)');
  }
  function toggleMute() {
    if (!ready) return;
    if (muted) { yt.unMute(); if (Number(vol.value) === 0) { vol.value = '60'; yt.setVolume(60); } muted = false; }
    else { yt.mute(); muted = true; }
    prefs.muted = muted;
    save(); syncVolumeUi(); wake();
  }
  muteBtn.addEventListener('click', toggleMute);
  vol.addEventListener('input', function () {
    var v = Number(vol.value);
    prefs.vol = v; muted = v === 0; prefs.muted = muted;
    if (ready) { yt.setVolume(v); if (v > 0) yt.unMute(); else yt.mute(); }
    save(); syncVolumeUi();
  });

  /* ---------- speed ---------- */
  function buildSpeedMenu() {
    var rates = (yt.getAvailablePlaybackRates && yt.getAvailablePlaybackRates()) || [0.75, 1, 1.25, 1.5, 2];
    rates = rates.filter(function (r) { return r >= 0.5 && r <= 2; });
    menu.textContent = '';
    rates.forEach(function (r) {
      var li = el('li');
      li.setAttribute('role', 'none');
      var b = el('button', '', r === 1 ? 'Normal' : r + 'x');
      b.type = 'button';
      b.setAttribute('role', 'menuitemradio');
      b.setAttribute('data-rate', r);
      b.addEventListener('click', function () {
        yt.setPlaybackRate(r); prefs.rate = r; save(); syncSpeedUi(r); closeMenu();
      });
      li.appendChild(b);
      menu.appendChild(li);
    });
  }
  function syncSpeedUi(rate) {
    var r = typeof rate === 'number' ? rate : (ready ? yt.getPlaybackRate() : 1);
    speedBtn.textContent = r + 'x';
    Array.prototype.forEach.call(menu.querySelectorAll('button'), function (b) {
      b.setAttribute('aria-checked', String(Number(b.getAttribute('data-rate')) === r));
    });
  }
  function closeMenu() { menu.hidden = true; speedBtn.setAttribute('aria-expanded', 'false'); }
  speedBtn.addEventListener('click', function () {
    if (!ready) return;
    syncSpeedUi();
    menu.hidden = !menu.hidden;
    speedBtn.setAttribute('aria-expanded', String(!menu.hidden));
    if (!menu.hidden) { var c = menu.querySelector('[aria-checked="true"]') || menu.querySelector('button'); if (c) c.focus(); }
  });
  document.addEventListener('click', function (e) { if (!menuWrap.contains(e.target)) closeMenu(); });

  /* ---------- fullscreen ---------- */
  function fsElement() { return document.fullscreenElement || document.webkitFullscreenElement; }
  function toggleFullscreen() {
    if (fsElement()) { (document.exitFullscreen || document.webkitExitFullscreen).call(document); return; }
    var req = stage.requestFullscreen || stage.webkitRequestFullscreen;
    if (req) req.call(stage);
  }
  function onFs() {
    var on = fsElement() === stage;
    root.classList.toggle('is-fullscreen', on);
    setIcon(fsBtn, on ? ICON.exit : ICON.full);
    fsBtn.setAttribute('aria-label', on ? 'Exit fullscreen (f)' : 'Fullscreen (f)');
  }
  document.addEventListener('fullscreenchange', onFs);
  document.addEventListener('webkitfullscreenchange', onFs);
  if (!(stage.requestFullscreen || stage.webkitRequestFullscreen)) fsBtn.hidden = true;

  /* ---------- idle controls ---------- */
  function wake() {
    root.classList.remove('is-idle');
    clearTimeout(idleTimer);
    idleTimer = setTimeout(function () { if (playing && menu.hidden && !bar.matches(':focus-within')) root.classList.add('is-idle'); }, 2600);
  }
  ['mousemove', 'pointerdown', 'touchstart', 'focusin'].forEach(function (n) { stage.addEventListener(n, wake, { passive: true }); });

  /* ---------- wiring ---------- */
  startBtn.addEventListener('click', function () { begin(startFromUrl()); });
  playBtn.addEventListener('click', toggle);
  fsBtn.addEventListener('click', toggleFullscreen);
  replay.addEventListener('click', replayVideo);
  shield.addEventListener('click', function () {
    if (clickTimer) return;
    clickTimer = setTimeout(function () { clickTimer = null; toggle(); }, 230);
  });
  shield.addEventListener('dblclick', function () {
    clearTimeout(clickTimer); clickTimer = null;
    toggleFullscreen();
  });

  chapterBtns.forEach(function (b) {
    b.addEventListener('click', function () {
      var t = Number(b.getAttribute('data-t'));
      try { history.replaceState(null, '', '#t=' + t); } catch (e) { /* ignore */ }
      if (!started) begin(t); else { seekTo(t, true); play(); }
      stage.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    });
  });

  var copyBtn = document.querySelector('[data-gc-copy-link]');
  if (copyBtn) copyBtn.addEventListener('click', function () {
    var t = ready ? Math.floor(yt.getCurrentTime()) : 0;
    var url = location.origin + location.pathname + (t > 5 ? '#t=' + t : '');
    function done() { copyBtn.textContent = 'Copied'; setTimeout(function () { copyBtn.textContent = 'Copy link'; }, 1800); }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(done, function () { window.prompt('Copy this link', url); });
    else window.prompt('Copy this link', url);
  });

  document.addEventListener('keydown', function (e) {
    if (!started || e.ctrlKey || e.metaKey || e.altKey) return;
    var t = e.target;
    var inside = root.contains(t) || t === document.body;
    if (!inside) return;
    var tag = (t.tagName || '').toLowerCase();
    if (tag === 'input' && t.type !== 'range') return;
    if (tag === 'textarea' || tag === 'select' || t.isContentEditable) return;
    var onRange = tag === 'input' && t.type === 'range';
    var onButton = tag === 'button' || tag === 'a';
    var k = e.key, handled = true;
    if ((k === ' ' || k === 'Enter') && onButton) return;
    if (k === ' ' || k === 'k' || k === 'K') toggle();
    else if ((k === 'ArrowLeft' || k === 'ArrowRight') && !onRange) skip(k === 'ArrowLeft' ? -5 : 5);
    else if (k === 'j' || k === 'J') skip(-10);
    else if (k === 'l' || k === 'L') skip(10);
    else if (k === 'f' || k === 'F') toggleFullscreen();
    else if (k === 'm' || k === 'M') toggleMute();
    else if (k === 'Home' && !onRange) seekTo(0, true);
    else if (k === 'End' && !onRange) seekTo(duration, true);
    else if (/^[0-9]$/.test(k)) seekTo(duration * Number(k) / 10, true);
    else if (k === 'Escape' && !menu.hidden) { closeMenu(); speedBtn.focus(); }
    else handled = false;
    if (handled) { e.preventDefault(); wake(); }
  });

  window.addEventListener('pagehide', function () { stopTimer(); });
  paint(0);
})();
