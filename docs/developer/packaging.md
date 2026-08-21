# Packaging & Executable Distribution

GeoCore uses **PyInstaller (one-folder mode)** for compiling the Python backend and **electron-builder** for packaging the desktop installer.

---

## 🛠️ Step 1: Building the Python Backend

In one-folder mode, PyInstaller generates a standalone `python-backend/dist/main/` folder containing the Python executable, shared C-extensions (`.pyd` / `.dll`), and runtime assets without causing antivirus false-positives.

```bash
cd python-backend

# Build with PyInstaller spec
python -m PyInstaller main.spec --clean --noconfirm
```

---

## 📦 Step 2: Packaging the Electron Application

Once the backend is built in `python-backend/dist/main/`, package the full installer:

```bash
cd electron-app

# Install dependencies
npm install

# Build Vite frontend assets
npm run build

# Package Electron executable for your host OS
npm run build:exe
```

The output installer (`GeoCore-Setup-1.0.0.exe` or `.dmg` / `.AppImage`) will be generated inside `electron-app/dist/`.
