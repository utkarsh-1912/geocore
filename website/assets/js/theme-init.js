/* Runs in <head> before first paint: apply a stored theme choice (no flash). No stored choice = follow the OS. */
(function () {
  var root = document.documentElement;
  root.classList.add('js');
  try {
    var t = localStorage.getItem('geocore-theme');
    if (t === 'light' || t === 'dark') root.setAttribute('data-theme', t);
  } catch (e) { /* storage unavailable: follow the OS */ }
})();
