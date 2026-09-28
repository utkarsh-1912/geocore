const { app, BrowserWindow, ipcMain, nativeImage } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Set Application User Model ID for Windows Taskbar icon grouping
if (process.platform === 'win32') {
  app.setAppUserModelId('com.geocore.app');
}

let mainWindow;
let pythonProcess;

// Must match the renderer header: `h-13` (52px) including its 1px bottom
// border. The overlay stops 1px short so the header border stays visible
// under the native window controls.
const TITLE_BAR_HEIGHT = 52;
const TITLE_BAR_OVERLAY_HEIGHT = TITLE_BAR_HEIGHT - 1;

// Mirrors --color-surface / --color-text-muted in src/index.css so the native
// minimise / maximise / close buttons blend into the header.
const TITLE_BAR_THEMES = {
  dark: { color: '#151c18', symbolColor: '#a1aca5' },
  light: { color: '#ffffff', symbolColor: '#56625b' },
};

// macOS traffic lights are ~14px tall; centre them in the header.
const MAC_TRAFFIC_LIGHT_POSITION = { x: 18, y: Math.round((TITLE_BAR_HEIGHT - 14) / 2) };

function titleBarOverlayFor(isDark) {
  return { ...(isDark ? TITLE_BAR_THEMES.dark : TITLE_BAR_THEMES.light), height: TITLE_BAR_OVERLAY_HEIGHT };
}

// Keep the native window-controls overlay in sync with the app theme.
// Registered once so re-creating the window (macOS `activate`) does not stack listeners.
ipcMain.on('set-title-bar-overlay', (event, { isDark } = {}) => {
  if (process.platform !== 'win32' || !mainWindow || mainWindow.isDestroyed()) return;
  try {
    mainWindow.setTitleBarOverlay(titleBarOverlayFor(Boolean(isDark)));
  } catch (e) {
    console.error('Failed to update titleBarOverlay:', e);
  }
});

function createWindow() {
  const isWin = process.platform === 'win32';
  const isMac = process.platform === 'darwin';
  const iconCandidates = isWin
    ? [
        path.join(__dirname, '../public/icon.ico'),
        path.join(__dirname, '../dist/icon.ico'),
        path.join(__dirname, '../public/logoIcon.ico'),
        path.join(__dirname, '../public/logoIcon.png'),
        path.join(__dirname, '../dist/logoIcon.png'),
      ]
    : [
        path.join(__dirname, '../public/logoIcon.png'),
        path.join(__dirname, '../dist/logoIcon.png'),
      ];

  const resolvedIconPath = iconCandidates.find(p => fs.existsSync(p)) || path.join(__dirname, '../public/logoIcon.png');
  const appIcon = nativeImage.createFromPath(resolvedIconPath);

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 968,
    minHeight: 480,
    show: false,
    backgroundColor: '#0e1311',
    icon: appIcon,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
    // Custom title bar: macOS draws traffic lights on the left, Windows overlays native
    // controls on the right. titleBarOverlay has no Linux support and there is no custom
    // control UI in the renderer to fall back on, so Linux keeps the native frame instead.
    ...(isMac
      ? { titleBarStyle: 'hidden', trafficLightPosition: MAC_TRAFFIC_LIGHT_POSITION }
      : isWin
      ? { titleBarStyle: 'hidden', titleBarOverlay: titleBarOverlayFor(true) }
      : {}),
  });

  // BrowserWindow#setIcon exists only on Windows/Linux; macOS uses the bundle icon.
  if (!isMac) mainWindow.setIcon(appIcon);

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  const isDev = !app.isPackaged;

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startPythonBackend() {
  const isDev = !app.isPackaged;
  const isWin = process.platform === 'win32';
  const exeName = isWin ? 'main.exe' : 'main';
  let scriptPath;
  let pythonPath;

  if (isDev) {
    scriptPath = path.join(__dirname, '../../python-backend/main.py');
    const venvBin = isWin 
      ? path.join(__dirname, '../../python-backend/venv/Scripts/python.exe')
      : path.join(__dirname, '../../python-backend/venv/bin/python');
    const dotVenvBin = isWin
      ? path.join(__dirname, '../../.venv/Scripts/python.exe')
      : path.join(__dirname, '../../.venv/bin/python');

    if (fs.existsSync(venvBin)) {
      pythonPath = venvBin;
    } else if (fs.existsSync(dotVenvBin)) {
      pythonPath = dotVenvBin;
    } else {
      pythonPath = isWin ? 'python' : 'python3';
    }
  } else {
    // Production: PyInstaller one-folder output is at dist/main/<exeName>
    // The folder must be the CWD so all sibling .dll / .so files resolve.
    const pyFolder = path.join(process.resourcesPath, 'python-backend', 'dist', 'main');
    pythonPath = path.join(pyFolder, exeName);

    // Ensure executable permissions on macOS / Linux
    if (!isWin && fs.existsSync(pythonPath)) {
      try {
        fs.chmodSync(pythonPath, 0o755);
      } catch (err) {
        console.error('Failed to set executable permissions on Python binary:', err);
      }
    }
  }

  if (isDev) {
    pythonProcess = spawn(pythonPath, [scriptPath]);
  } else {
    // Production: run from inside the one-folder dist so DLLs are found
    const pyFolder = path.join(process.resourcesPath, 'python-backend', 'dist', 'main');
    if (fs.existsSync(pythonPath)) {
      pythonProcess = spawn(pythonPath, [], {
        cwd: pyFolder,
        env: { ...process.env, PATH: `${pyFolder}${path.delimiter}${process.env.PATH}` }
      });
    } else {
      console.error(`Python production binary not found: ${pythonPath}`);
      console.error(`Expected folder: ${pyFolder}`);
    }
  }

  if (pythonProcess) {
    pythonProcess.stdout.on('data', (data) => {
      console.log(`Python: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`Python Error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
      console.log(`Python process exited with code ${code}`);
    });
  }
}

// Background update check against GitHub Releases (packaged builds only).
// GeoCore must work fully offline: any failure here (no network, no release,
// unsigned mac build, etc.) is logged and ignored. No telemetry is sent.
const UPDATE_CHECK_DELAY_MS = 15000;

function scheduleUpdateCheck() {
  if (!app.isPackaged) return;

  setTimeout(() => {
    try {
      const { autoUpdater } = require('electron-updater');
      autoUpdater.autoDownload = true;
      autoUpdater.autoInstallOnAppQuit = true;
      autoUpdater.on('error', (err) => {
        console.warn('Auto-update unavailable:', err && err.message ? err.message : err);
      });
      autoUpdater.checkForUpdatesAndNotify().catch((err) => {
        console.warn('Auto-update check failed:', err && err.message ? err.message : err);
      });
    } catch (err) {
      console.warn('Auto-updater could not be initialised:', err);
    }
  }, UPDATE_CHECK_DELAY_MS);
}

// Single instance lock to prevent multiple clicks spawning competing instances
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', (event, commandLine, workingDirectory) => {
    // Focus the existing window if user clicks the app icon again
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });

  app.whenReady().then(() => {
    const isDev = !app.isPackaged;
    if (!isDev) {
      startPythonBackend();
    } else {
      console.log("Dev Mode: Skipping auto-start of Python backend. Run 'python main.py' manually.");
    }
    createWindow();
    scheduleUpdateCheck();

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
      }
    });
  });

  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
      app.quit();
    }
  });

  app.on('will-quit', () => {
    if (pythonProcess) {
      pythonProcess.kill();
    }
  });
}
