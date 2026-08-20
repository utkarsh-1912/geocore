# Developer Packaging & Executable Generation Guide

This guide documents how to compile, bundle, and package GeoCore into native executables.

## Architecture

GeoCore packages a Python FastAPI backend into a single executable using **PyInstaller**, and embeds it inside an **Electron** shell using **electron-builder**.

## 1. PyInstaller Spec Configuration

The Python backend is packaged via `python-backend/main.spec`:

```bash
cd python-backend
pyinstaller --clean main.spec
```

## 2. Electron Packaging

```bash
cd electron-app

# Windows Installer (.exe)
npm run dist:win

# macOS Installer (.dmg)
npm run dist:mac
```

## 3. GitHub Actions Release Pipeline

Pushes to git release tags (`v*`) automatically trigger `.github/workflows/release.yml` to compile binaries on Windows (`windows-latest`) and macOS (`macos-latest`) runners and publish them directly to GitHub Releases.
