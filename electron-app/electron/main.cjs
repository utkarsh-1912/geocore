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

function createWindow() {
  const isWin = process.platform === 'win32';
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
    backgroundColor: '#080c14',
    icon: appIcon,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
    titleBarStyle: 'hidden', // Custom title bar
    titleBarOverlay: {
      color: '#080c14',
      symbolColor: '#ffffff',
      height: 48
    },
  });

  mainWindow.setIcon(appIcon);

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

app.whenReady().then(() => {
  const isDev = !app.isPackaged;
  // In Dev, we run python manually to see logs. In Prod, we run it automatically.
  if (!isDev) {
    startPythonBackend();
  } else {
    console.log("Dev Mode: Skipping auto-start of Python backend. Run 'python main.py' manually.");
  }
  createWindow();

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
