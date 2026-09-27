# 📦 GeoCore Release, Listing, & Packaging Guide

This guide provides step-by-step instructions for listing, building, and releasing GeoCore binaries for **Windows (.exe)** and **macOS (.dmg / .app)**, as well as managing the documentation and product showcase website.

---

## 🛠️ 1. Release Process Overview

GeoCore utilizes an automated multi-platform release strategy powered by **GitHub Actions**, **PyInstaller**, and **electron-builder**.

```
    Tag Commit (e.g. `v1.0.0`)
               │
               ▼
      GitHub Actions Workflow
      ├── Windows Runner: Builds `main.exe` + `GeoCore-Setup.exe`
      └── macOS Runner: Builds `main` + `GeoCore.dmg`
               │
               ▼
     GitHub Release Artifacts
```

---

## 🚀 2. How to Create a New Release

### Step 1: Update Version Numbers
Update the version string in `electron-app/package.json` and `python-backend/main.py`:
```json
{
  "name": "geocore",
  "version": "1.0.0"
}
```

### Step 2: Tag & Push to GitHub
```bash
git add .
git commit -m "Chore: prepare v1.0.0 release"
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin main --tags
```

### Step 3: Automated Build Verification
1. Navigate to your repository on GitHub: `https://github.com/utkarsh-1912/geocore/actions`
2. Select the **Build & Release GeoCore** workflow.
3. Once completed, a release will be automatically created under `https://github.com/utkarsh-1912/geocore/releases` containing:
   - `GeoCore-Setup-1.0.0.exe` (Windows Installer, per-user, no admin required)
   - `GeoCore-1.0.0-<arch>.dmg` (macOS Installer)
   - `GeoCore-1.0.0-<arch>-mac.zip` (macOS Compressed Application)
   - `latest.yml`, `latest-mac.yml`, `*.blockmap` (auto-update metadata — must stay attached to the release)

> **No portable build.** The Windows portable target was removed: it self-extracted the whole app
> (including the ~0.5 GB Python engine) to `%TEMP%` on every launch, which made startup very slow.
> The NSIS installer extracts once at install time and starts fast.

### Auto-updates
Installed builds check GitHub Releases (`utkarsh-1912/geocore`) ~15 s after launch using `electron-updater`,
download a newer version in the background and install it when the app quits. The check is skipped in
development, and any failure (offline machine, no release) is ignored — GeoCore keeps working offline.
Local builds never publish (`--publish never`); only the CI workflow uploads release assets.
Note: macOS auto-update requires a properly code-signed app; ad-hoc signed builds will not self-update.

### Local LLM runtime (GeoAI)
The release workflow installs the prebuilt CPU wheel of `llama-cpp-python` before `requirements.txt`
and `main.spec` bundles `llama_cpp` plus its native `ggml`/`llama` libraries. To reproduce locally:
```bash
cd python-backend
venv/Scripts/python.exe -m pip install llama-cpp-python --prefer-binary --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```
If `llama_cpp` is not installed when running PyInstaller, the build prints a warning and GeoAI falls back to
the heuristic provider. Models (`.gguf`) are not bundled; they are downloaded to `%APPDATA%\GeoCore\models`.

---

## 💻 3. Building Locally (Manual Build)

### Windows Executable Build
Run on a Windows PC or Virtual Machine:
```bash
# 1. Build Python Executable
cd python-backend
pyinstaller --clean main.spec

# 2. Build Electron App
cd ../electron-app
npm run build
npm run dist:win
```
*Output location*: `electron-app/release/GeoCore-Setup-1.0.0.exe`

### macOS Executable Build
Run on a Mac (Intel or Apple Silicon):
```bash
# 1. Build Python Executable
cd python-backend
pyinstaller --clean main.spec

# 2. Build Electron App
cd ../electron-app
npm run build
npm run dist:mac
```
*Output location*: `electron-app/release/GeoCore-1.0.0-<arch>.dmg`

---

## 🌐 4. Website & Listing Deployment

The GeoCore product showcase website is located in `website/index.html`. It provides:
- Live download buttons for Windows & Mac
- Visual module browser & calculation showcases
- Direct links to Open Source MkDocs documentation

### Deploying to GitHub Pages (Free Hosting)
1. In your GitHub repository settings, navigate to **Pages**.
2. Set Source to `Deploy from a branch`.
3. Select branch `main` and folder `/website` (or `/docs`).
4. Click **Save**. Your site will be published live at `https://utkarsh-1912.github.io/geocore`.

---

## 📚 5. Open Source Documentation (MkDocs Material)

GeoCore documentation is structured using **MkDocs Material**, the standard open-source documentation manager for Python and engineering projects.

### Local Documentation Server
```bash
pip install mkdocs-material
mkdocs serve
```
Visit `http://127.0.0.1:8000` to preview docs.

### Build Documentation for Web
```bash
mkdocs build
```
*Output location*: `site/` directory (can be deployed to GitHub Pages, Vercel, or Netlify).
