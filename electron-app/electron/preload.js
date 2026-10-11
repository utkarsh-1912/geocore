const { contextBridge, ipcRenderer, webUtils } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    isDev: process.env.NODE_ENV === 'development' || !process.resourcesPath?.includes('app.asar'),
    platform: process.platform,
    getPathForFile: (file) => webUtils.getPathForFile(file),
    setTitleBarTheme: (isDark) => ipcRenderer.send('set-title-bar-overlay', { isDark }),
    // Save a report (HTML) as a PDF where the user chooses; resolves to the path, or null when cancelled.
    reportToPdf: (html, fileName) => ipcRenderer.invoke('report-to-pdf', { html, fileName })
});
