const { contextBridge, ipcRenderer, webUtils } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    // Expose specific IPC methods here if needed
    // For now, we use HTTP to talk to Python, so we might not need much IPC
    getPathForFile: (file) => webUtils.getPathForFile(file)
});
