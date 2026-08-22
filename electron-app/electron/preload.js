const { contextBridge, ipcRenderer, webUtils } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    isDev: process.env.NODE_ENV === 'development' || !process.resourcesPath?.includes('app.asar'),
    getPathForFile: (file) => webUtils.getPathForFile(file),
    setTitleBarTheme: (isDark) => ipcRenderer.send('set-title-bar-overlay', { isDark })
});
