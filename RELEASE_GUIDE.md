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
3. Once completed, a draft release will be automatically created under `https://github.com/utkarsh-1912/geocore/releases` containing:
   - `GeoCore-Setup-1.0.0.exe` (Windows Installer)
   - `GeoCore-1.0.0.portable.exe` (Windows Portable)
   - `GeoCore-1.0.0.dmg` (macOS Installer)
   - `GeoCore-1.0.0-mac.zip` (macOS Compressed Application)

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
*Output location*: `electron-app/release/GeoCore Setup 1.0.0.exe`

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
*Output location*: `electron-app/release/GeoCore-1.0.0.dmg`

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
