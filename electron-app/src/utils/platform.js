// Host OS as reported by the Electron preload. Falls back to the browser's
// user agent when running in a plain browser (e.g. `npm run dev` without Electron).
const electronPlatform = typeof window !== 'undefined' ? window.electronAPI?.platform : undefined;

export const IS_ELECTRON = Boolean(electronPlatform);

export const IS_MAC = electronPlatform
  ? electronPlatform === 'darwin'
  : typeof navigator !== 'undefined' && /Mac/i.test(navigator.platform || navigator.userAgent);
