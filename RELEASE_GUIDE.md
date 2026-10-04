# 📦 GeoCore Release, Listing, & Packaging Guide

This guide provides step-by-step instructions for listing, building, and releasing GeoCore binaries for **Windows (.exe)**, **macOS (.dmg / .app)**, and **Linux (.AppImage / .deb)**, as well as managing the documentation and product showcase website.

---

## 🛠️ 1. Release Process Overview

GeoCore utilizes an automated multi-platform release strategy powered by **GitHub Actions**, **PyInstaller**, and **electron-builder**.

```
    Tag Commit (e.g. `v1.0.0`)
               │
               ▼
      GitHub Actions Workflow
      ├── Windows Runner: Builds `main.exe` + `GeoCore-Setup.exe`
      ├── macOS Runner:   Builds `main` + `GeoCore.dmg`
      └── Linux Runner:   Builds `main` + `GeoCore.AppImage` + `geocore.deb`
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
   - `GeoCore-1.0.0.AppImage` (Linux, portable — auto-updates like Windows/macOS)
   - `geocore_1.0.0_amd64.deb` (Linux, Debian/Ubuntu package — **no auto-update**; reinstall the
     new `.deb` for each release, or use the AppImage instead if you want in-app updates)
   - `latest.yml`, `latest-mac.yml`, `latest-linux.yml`, `*.blockmap` (auto-update metadata — must stay attached to the release)

> **No portable build.** The Windows portable target was removed: it self-extracted the whole app
> (including the ~0.5 GB Python engine) to `%TEMP%` on every launch, which made startup very slow.
> The NSIS installer extracts once at install time and starts fast.

### Auto-updates
Installed builds check GitHub Releases (`utkarsh-1912/geocore`) ~15 s after launch using `electron-updater`,
download a newer version in the background and install it when the app quits. The check is skipped in
development, and any failure (offline machine, no release) is ignored — GeoCore keeps working offline.
Local builds never publish (`--publish never`); only the CI workflow uploads release assets.
Note: macOS auto-update requires a properly code-signed app; ad-hoc signed builds will not self-update.
Note: on Linux, only the AppImage self-updates through `electron-updater`; the `.deb` package has no
auto-update mechanism (this is a Linux/electron-updater limitation, not something GeoCore controls).

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

### Linux Executable Build
Run on a Linux machine (AppImage/deb cannot be cross-built from Windows or macOS):
```bash
# 1. Build Python Executable
cd python-backend
pyinstaller --clean main.spec

# 2. Build Electron App
cd ../electron-app
npm run build
npm run dist:linux
```
*Output location*: `electron-app/release/GeoCore-1.0.0.AppImage` and `geocore_1.0.0_amd64.deb`

> AppImage packaging needs no extra system packages on a typical desktop distro. The `.deb`
> target needs `fakeroot` and `dpkg` (present by default on Debian/Ubuntu; the CI workflow
> installs them explicitly on the `ubuntu-latest` runner via `apt-get`).

---

## 🌐 4. Website & Listing Deployment

The product website and the user documentation live in `website/` and are published by **Netlify** (`netlify.toml` sets `publish = "website"`). There is no framework runtime: a Python generator renders Jinja2 templates and the Markdown in `website/_content/` into plain HTML, and the generated HTML is **committed**. Netlify only publishes it.

After changing anything in `website/_templates/`, `website/_content/` or `website/assets/`, rebuild and commit the result:
```bash
python website/_build/build.py
```
Download buttons and the model list are filled from the code base at build time (app version from `electron-app/package.json`, function counts from `python-backend/core/function_manifest.json`). Rebuild the site as part of each release so these stay current. Details are in [website/README.md](website/README.md).

---

## 📚 5. Where the documentation lives

| Audience | Location |
| :--- | :--- |
| Users | `website/_content/` (published at the site's `/docs/`) |
| Contributors | [README.md](README.md), [electron-app/README.md](electron-app/README.md), [python-backend/README.md](python-backend/README.md), [python-backend/core/geoai/README.md](python-backend/core/geoai/README.md) |
| GeoAI design rules | [AGENTS.md](AGENTS.md) |
