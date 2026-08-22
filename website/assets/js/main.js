/**
 * GeoCore Website Core JavaScript
 * Author: Utkarsh Gupta
 * Copyright (c) 2026 GeoCore. All Rights Reserved.
 */

// Theme Management
const themeToggleBtns = document.querySelectorAll('#theme-toggle, .mobile-theme-toggle');
const root = document.documentElement;

function getInitialTheme() {
  const saved = localStorage.getItem('geocore_theme');
  if (saved) return saved;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function setTheme(theme) {
  root.setAttribute('data-theme', theme);
  localStorage.setItem('geocore_theme', theme);
  updateThemeIcons(theme);
}

function updateThemeIcons(theme) {
  const sunIcons = document.querySelectorAll('.theme-sun-icon');
  const moonIcons = document.querySelectorAll('.theme-moon-icon');
  if (theme === 'dark') {
    sunIcons.forEach(el => el.classList.remove('hidden'));
    moonIcons.forEach(el => el.classList.add('hidden'));
  } else {
    sunIcons.forEach(el => el.classList.add('hidden'));
    moonIcons.forEach(el => el.classList.remove('hidden'));
  }
}

// Initialize Theme
setTheme(getInitialTheme());

themeToggleBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const current = root.getAttribute('data-theme') || 'light';
    setTheme(current === 'dark' ? 'light' : 'dark');
  });
});

// Mobile Navigation Drawer with Backdrop
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileMenuCloseBtn = document.getElementById('mobile-menu-close-btn');
const mobileMenu = document.getElementById('mobile-menu');
const mobileMenuBackdrop = document.getElementById('mobile-menu-backdrop');

function openMobileMenu() {
  if (mobileMenu && mobileMenuBackdrop) {
    mobileMenu.classList.remove('translate-x-full');
    mobileMenuBackdrop.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    if (window.lucide) window.lucide.createIcons();
  }
}

function closeMobileMenu() {
  if (mobileMenu && mobileMenuBackdrop) {
    mobileMenu.classList.add('translate-x-full');
    mobileMenuBackdrop.classList.add('hidden');
    document.body.style.overflow = '';
  }
}

if (mobileMenuBtn) {
  mobileMenuBtn.addEventListener('click', openMobileMenu);
}
if (mobileMenuCloseBtn) {
  mobileMenuCloseBtn.addEventListener('click', closeMobileMenu);
}
if (mobileMenuBackdrop) {
  mobileMenuBackdrop.addEventListener('click', closeMobileMenu);
}

// Close mobile menu on clicking any navigation link
document.querySelectorAll('#mobile-menu a').forEach(link => {
  link.addEventListener('click', closeMobileMenu);
});

// Interactive Live Geotechnical Calculator
function initLiveCalculator() {
  const tabRankine = document.getElementById('calc-tab-rankine');
  const tabGmax = document.getElementById('calc-tab-gmax');
  const tabVoid = document.getElementById('calc-tab-void');

  const panelRankine = document.getElementById('calc-panel-rankine');
  const panelGmax = document.getElementById('calc-panel-gmax');
  const panelVoid = document.getElementById('calc-panel-void');

  const tabs = [
    { btn: tabRankine, panel: panelRankine },
    { btn: tabGmax, panel: panelGmax },
    { btn: tabVoid, panel: panelVoid }
  ];

  tabs.forEach(t => {
    if (!t.btn) return;
    t.btn.addEventListener('click', () => {
      tabs.forEach(item => {
        if (item.btn) {
          item.btn.classList.remove('active-calc-tab', 'bg-primary', 'text-white');
          item.btn.classList.add('bg-surface', 'text-text-muted');
        }
        if (item.panel) item.panel.classList.add('hidden');
      });
      t.btn.classList.add('active-calc-tab', 'bg-primary', 'text-white');
      t.btn.classList.remove('bg-surface', 'text-text-muted');
      if (t.panel) {
        t.panel.classList.remove('hidden');
        t.panel.classList.add('animate-fade-in');
      }
    });
  });

  // Rankine Calculation Logic
  const rankinePhi = document.getElementById('rankine-phi');
  const rankineGamma = document.getElementById('rankine-gamma');
  const rankineZ = document.getElementById('rankine-z');
  const rankineC = document.getElementById('rankine-c');

  function calculateRankine() {
    if (!rankinePhi) return;
    const phiDeg = parseFloat(rankinePhi.value) || 0;
    const gamma = parseFloat(rankineGamma.value) || 0;
    const z = parseFloat(rankineZ.value) || 0;
    const c = parseFloat(rankineC.value) || 0;

    const phiRad = (phiDeg * Math.PI) / 180;
    const Ka = Math.pow(Math.tan((Math.PI / 4) - (phiRad / 2)), 2);
    const Kp = Math.pow(Math.tan((Math.PI / 4) + (phiRad / 2)), 2);

    const sigmaV = gamma * z;
    const sigmaA = Math.max(0, (Ka * sigmaV) - (2 * c * Math.sqrt(Ka)));
    const sigmaP = (Kp * sigmaV) + (2 * c * Math.sqrt(Kp));

    const resKa = document.getElementById('res-ka');
    const resKp = document.getElementById('res-kp');
    const resSigmaA = document.getElementById('res-sigma-a');
    const resSigmaP = document.getElementById('res-sigma-p');

    if (resKa) resKa.innerText = Ka.toFixed(3);
    if (resKp) resKp.innerText = Kp.toFixed(3);
    if (resSigmaA) resSigmaA.innerText = sigmaA.toFixed(2) + ' kPa';
    if (resSigmaP) resSigmaP.innerText = sigmaP.toFixed(2) + ' kPa';
  }

  [rankinePhi, rankineGamma, rankineZ, rankineC].forEach(input => {
    if (input) {
      input.addEventListener('input', calculateRankine);
      input.addEventListener('focus', () => input.select());
    }
  });
  calculateRankine();

  // Gmax Calculation Logic
  const gmaxVs = document.getElementById('gmax-vs');
  const gmaxGamma = document.getElementById('gmax-gamma');

  function calculateGmax() {
    if (!gmaxVs) return;
    const vs = parseFloat(gmaxVs.value) || 0;
    const gamma = parseFloat(gmaxGamma.value) || 0;

    const rho = (gamma * 1000) / 9.81; // kg/m3
    const GmaxPa = rho * Math.pow(vs, 2); // Pa
    const GmaxMPa = GmaxPa / 1e6; // MPa

    const resGmax = document.getElementById('res-gmax');
    const resRho = document.getElementById('res-rho');

    if (resGmax) resGmax.innerText = GmaxMPa.toFixed(2) + ' MPa';
    if (resRho) resRho.innerText = rho.toFixed(1) + ' kg/m³';
  }

  [gmaxVs, gmaxGamma].forEach(input => {
    if (input) {
      input.addEventListener('input', calculateGmax);
      input.addEventListener('focus', () => input.select());
    }
  });
  calculateGmax();

  // Void Ratio Calculation Logic
  const voidPorosity = document.getElementById('void-porosity');
  const voidGs = document.getElementById('void-gs');

  function calculateVoid() {
    if (!voidPorosity) return;
    const n = parseFloat(voidPorosity.value) || 0;
    const Gs = parseFloat(voidGs.value) || 2.65;

    let e = 0;
    if (n < 1 && n > 0) {
      e = n / (1 - n);
    }
    const gammaDry = (Gs * 9.81) / (1 + e);

    const resE = document.getElementById('res-e');
    const resGammaDry = document.getElementById('res-gamma-dry');

    if (resE) resE.innerText = e.toFixed(3);
    if (resGammaDry) resGammaDry.innerText = gammaDry.toFixed(2) + ' kN/m³';
  }

  [voidPorosity, voidGs].forEach(input => {
    if (input) {
      input.addEventListener('input', calculateVoid);
      input.addEventListener('focus', () => input.select());
    }
  });
  calculateVoid();
}

// OS Auto-Detection for Downloads (macOS and Windows)
function detectUserOS() {
  const userAgent = window.navigator.userAgent || '';
  const platform = window.navigator.platform || '';
  
  if (/Mac|iPhone|iPod|iPad/i.test(platform) || /Macintosh|Mac OS X/i.test(userAgent)) {
    return 'mac';
  }
  return 'windows';
}

function updateDownloadElements() {
  const os = detectUserOS();
  const releaseUrl = 'https://github.com/utkarsh-1912/geocore/releases';

  const heroDownloadBtn = document.getElementById('hero-download-btn');
  const heroDownloadSubtext = document.getElementById('hero-download-subtext');
  const navDownloadBtn = document.getElementById('nav-download-btn');
  const drawerDownloadBtn = document.getElementById('drawer-download-btn');
  const winCard = document.getElementById('download-card-win');
  const macCard = document.getElementById('download-card-mac');

  if (os === 'mac') {
    if (heroDownloadBtn) {
      heroDownloadBtn.href = releaseUrl;
      heroDownloadBtn.innerHTML = '<i data-lucide="apple" class="w-4 h-4"></i><span>Download for macOS (.dmg)</span>';
    }
    if (heroDownloadSubtext) {
      heroDownloadSubtext.innerText = 'Auto-detected: macOS (Apple Silicon & Intel) • v1.0.0';
    }
    if (navDownloadBtn) {
      navDownloadBtn.href = releaseUrl;
      navDownloadBtn.innerHTML = '<i data-lucide="apple" class="w-3.5 h-3.5"></i> Download for Mac';
    }
    if (drawerDownloadBtn) {
      drawerDownloadBtn.href = releaseUrl;
      drawerDownloadBtn.innerHTML = '<i data-lucide="apple" class="w-3.5 h-3.5"></i> Download for macOS';
    }

    if (macCard) {
      macCard.classList.add('border-primary', 'ring-2', 'ring-primary/20');
      const badge = macCard.querySelector('.detected-badge');
      if (badge) badge.classList.remove('hidden');
    }
    if (winCard) {
      winCard.classList.remove('border-primary', 'ring-2', 'ring-primary/20');
      const badge = winCard.querySelector('.detected-badge');
      if (badge) badge.classList.add('hidden');
    }
  } else {
    // Windows
    if (heroDownloadBtn) {
      heroDownloadBtn.href = releaseUrl;
      heroDownloadBtn.innerHTML = '<i data-lucide="download" class="w-4 h-4"></i><span>Download for Windows (.exe)</span>';
    }
    if (heroDownloadSubtext) {
      heroDownloadSubtext.innerText = 'Auto-detected: Windows 10/11 (64-bit) • v1.0.0';
    }
    if (navDownloadBtn) {
      navDownloadBtn.href = releaseUrl;
      navDownloadBtn.innerHTML = '<i data-lucide="download" class="w-3.5 h-3.5"></i> Download for Windows';
    }
    if (drawerDownloadBtn) {
      drawerDownloadBtn.href = releaseUrl;
      drawerDownloadBtn.innerHTML = '<i data-lucide="download" class="w-3.5 h-3.5"></i> Download for Windows';
    }

    if (winCard) {
      winCard.classList.add('border-primary', 'ring-2', 'ring-primary/20');
      const badge = winCard.querySelector('.detected-badge');
      if (badge) badge.classList.remove('hidden');
    }
    if (macCard) {
      macCard.classList.remove('border-primary', 'ring-2', 'ring-primary/20');
      const badge = macCard.querySelector('.detected-badge');
      if (badge) badge.classList.add('hidden');
    }
  }

  // Update all release links
  document.querySelectorAll('a[data-release-link]').forEach(a => {
    a.href = releaseUrl;
  });

  if (window.lucide) window.lucide.createIcons();
}

document.addEventListener('DOMContentLoaded', () => {
  initLiveCalculator();
  updateDownloadElements();
});
