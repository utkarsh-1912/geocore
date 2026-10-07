/* GeoCore website — tutorial page player.
   Nothing is requested from YouTube until the visitor presses play (or a chapter). The poster is a local image;
   play swaps in a youtube-nocookie.com embed. A chapter (re)loads the embed at that time, which needs no
   YouTube script and works the same whether or not the video is already playing.
   Author: Utkarsh Gupta. License: GPL v3. */
(function () {
  'use strict';

  var player = document.querySelector('[data-yt]');
  if (!player) return;
  var id = player.getAttribute('data-yt');
  var slot = player.querySelector('[data-yt-frame]');
  var chapters = Array.prototype.slice.call(document.querySelectorAll('[data-yt-seek]'));
  var frame = null;

  function embedUrl(start) {
    var q = 'autoplay=1&rel=0&playsinline=1&modestbranding=1';
    if (start > 0) q += '&start=' + Math.floor(start);
    return 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?' + q;
  }

  function play(start) {
    if (!id) return;
    if (!frame) {
      frame = document.createElement('iframe');
      frame.title = player.getAttribute('data-title') || 'Tutorial video';
      frame.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      frame.allowFullscreen = true;
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      slot.appendChild(frame);
      player.classList.add('is-playing');
    }
    frame.src = embedUrl(start || 0);
    frame.focus();
  }

  var playBtn = player.querySelector('[data-yt-play]');
  if (playBtn) playBtn.addEventListener('click', function () { play(0); });

  chapters.forEach(function (btn) {
    btn.addEventListener('click', function () {
      chapters.forEach(function (b) { b.removeAttribute('aria-current'); });
      btn.setAttribute('aria-current', 'true');
      play(parseFloat(btn.getAttribute('data-yt-seek')) || 0);
      if (player.getBoundingClientRect().top < 0) player.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  var copy = document.querySelector('[data-copy-link]');
  if (copy && navigator.clipboard) {
    var label = copy.querySelector('span');
    copy.addEventListener('click', function () {
      navigator.clipboard.writeText(location.href.split('#')[0]).then(function () {
        label.textContent = 'Link copied';
        setTimeout(function () { label.textContent = 'Copy link'; }, 2000);
      });
    });
  } else if (copy) {
    copy.hidden = true;
  }
})();
