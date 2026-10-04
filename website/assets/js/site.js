/* GeoCore website — shared behaviour: theme toggle, mobile navigation, docs sidebar toggle, "On this page" rails. */
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

  // "On this page" rails (docs TOC and the About / Privacy / Download asides): highlight the
  // section being read and slide a marker along the rail to it.
  function scrollLine() {
    var pad = parseFloat(getComputedStyle(root).scrollPaddingTop);
    return (isNaN(pad) ? 72 : pad) + 8;
  }

  document.querySelectorAll('[data-toc], .aside-nav ul').forEach(function (list) {
    var links = Array.prototype.slice.call(list.querySelectorAll('a[href^="#"]'));
    var targets = links.map(function (a) {
      return document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)));
    });
    if (!targets.some(Boolean)) return;

    var marker = document.createElement('li');
    marker.className = 'toc-marker';
    marker.setAttribute('aria-hidden', 'true');
    list.appendChild(marker);
    list.classList.add('has-marker');
    var scroller = list.closest('.docs-toc');
    var current = null, queued = false;

    function place(i) {
      var a = links[i];
      marker.style.transform = 'translateY(' + a.offsetTop + 'px)';
      marker.style.height = a.offsetHeight + 'px';
      marker.style.opacity = '1';
      // Keep the active entry visible when the rail itself scrolls (long docs TOCs).
      if (scroller && scroller.scrollHeight > scroller.clientHeight) {
        var top = a.offsetTop, bottom = top + a.offsetHeight;
        if (top < scroller.scrollTop || bottom > scroller.scrollTop + scroller.clientHeight) {
          scroller.scrollTo({ top: Math.max(0, top - scroller.clientHeight / 3), behavior: 'smooth' });
        }
      }
    }

    function update(force) {
      queued = false;
      var line = scrollLine(), idx = -1;
      for (var i = 0; i < targets.length; i++) {
        if (targets[i] && targets[i].getBoundingClientRect().top <= line) idx = i;
      }
      // At the very bottom the last short sections can never reach the line; select the last one.
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) {
        for (var j = targets.length - 1; j >= 0; j--) { if (targets[j]) { idx = j; break; } }
      }
      if (idx === current && !force) return;
      current = idx;
      links.forEach(function (a, k) {
        a.classList.toggle('is-active', k === idx);
        if (k === idx) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current');
      });
      if (idx < 0) marker.style.opacity = '0'; else place(idx);
    }

    function queue() { if (!queued) { queued = true; requestAnimationFrame(function () { update(false); }); } }
    window.addEventListener('scroll', queue, { passive: true });
    window.addEventListener('resize', function () { update(true); });
    // Place the marker without animating it in from the top on first paint.
    marker.style.transition = 'none';
    update(true);
    requestAnimationFrame(function () { marker.style.transition = ''; });
  });

  // Hero entrance: staggered fade/rise, gated behind a class so nothing shifts if JS is slow.
  document.documentElement.classList.add('js-ready');
  document.querySelectorAll('.hero-in').forEach(function (el, i) {
    el.style.setProperty('--reveal-delay', (i * 90) + 'ms');
  });

  // Scroll reveals: fade/rise elements in as they enter the viewport, staggering siblings
  // that share a parent (a grid or list) so they don't all pop in at once.
  var revealEls = document.querySelectorAll('.reveal');
  if (revealEls.length) {
    var groupCounts = new Map();
    revealEls.forEach(function (el) {
      var parent = el.parentElement;
      var i = groupCounts.get(parent) || 0;
      el.style.setProperty('--reveal-delay', Math.min(i, 8) * 70 + 'ms');
      groupCounts.set(parent, i + 1);
    });
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-in');
            io.unobserve(entry.target);
          }
        });
      }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });
      revealEls.forEach(function (el) { io.observe(el); });
    } else {
      revealEls.forEach(function (el) { el.classList.add('is-in'); });
    }
  }

  // Count-up numbers: animate integers named in data-count once their element is revealed.
  var countEls = document.querySelectorAll('[data-count]');
  if (countEls.length) {
    var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function animateCount(el) {
      var target = parseInt(el.getAttribute('data-count'), 10);
      if (!isFinite(target)) return;
      if (reduceMotion) { el.textContent = String(target); return; }
      var start = performance.now(), duration = 900 + Math.min(target, 200) * 2;
      function tick(now) {
        var p = Math.min(1, (now - start) / duration);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = String(Math.round(target * eased));
        if (p < 1) requestAnimationFrame(tick); else el.textContent = String(target);
      }
      requestAnimationFrame(tick);
    }
    if ('IntersectionObserver' in window) {
      var countIo = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) { animateCount(entry.target); countIo.unobserve(entry.target); }
        });
      }, { threshold: 0.6 });
      countEls.forEach(function (el) { countIo.observe(el); });
    } else {
      countEls.forEach(function (el) { el.textContent = el.getAttribute('data-count'); });
    }
  }

  // GeoAI flow stepper: plays through the request pipeline once it scrolls into view,
  // and lets a reader jump to any step by click or keyboard to inspect it out of order.
  var flow = document.querySelector('.flow');
  if (flow) {
    var flowSteps = Array.prototype.slice.call(flow.children);
    var flowActive = 0, flowTimer = null, flowUserDriven = false;
    var flowReduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function flowSetActive(i) {
      flowActive = i;
      flowSteps.forEach(function (li, idx) {
        li.classList.toggle('is-active', idx === i);
        li.classList.toggle('is-done', idx < i);
        li.setAttribute('aria-current', idx === i ? 'step' : 'false');
      });
    }

    function flowStop() { if (flowTimer) { clearInterval(flowTimer); flowTimer = null; } }

    function flowPlay() {
      if (flowReduceMotion || flowUserDriven) return;
      flowStop();
      flowTimer = setInterval(function () {
        if (flowActive >= flowSteps.length - 1) { flowStop(); return; }
        flowSetActive(flowActive + 1);
      }, 1900);
    }

    flowSteps.forEach(function (li, idx) {
      function jump() { flowUserDriven = true; flowStop(); flowSetActive(idx); }
      li.addEventListener('click', jump);
      li.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); jump(); }
      });
    });

    flowSetActive(0);
    if ('IntersectionObserver' in window) {
      var flowIo = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) { flowPlay(); flowIo.unobserve(entry.target); }
        });
      }, { threshold: 0.4 });
      flowIo.observe(flow);
    } else {
      flowPlay();
    }
  }
})();
