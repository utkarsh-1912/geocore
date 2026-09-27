---
title: Running and building from source
slug: geocore/building-from-source
section: Getting Started
description: Set up a GeoCore development environment, run the tests and build the desktop installers.
origin: geocore
source_url: https://github.com/utkarsh-1912/geocore/blob/main/website/_content/geocore/building-from-source.md
license: GPL-3.0
author: Utkarsh Gupta
attribution: GeoCore documentation by Utkarsh Gupta, licensed under the GNU GPL v3.
groundhog_version: 0.15.0
edited_by_geocore: false
sources:
- README.md
- RELEASE_GUIDE.md
---

## Prerequisites

- Node.js 18 or newer and npm 9 or newer
- Python 3.10 or newer with `pip` and virtual environment support

## Clone the repository

```bash
git clone https://github.com/utkarsh-1912/geocore.git
cd geocore
```

## Python calculation engine

```bash
cd python-backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

The engine listens on `http://127.0.0.1:8000`.

### Tests

```bash
cd python-backend
pytest tests -v
```

### Local LLM runtime for GeoAI (optional)

GeoAI runs local models through `llama-cpp-python`. To install the prebuilt CPU wheel:

```bash
cd python-backend
venv/Scripts/python.exe -m pip install llama-cpp-python --prefer-binary --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

If `llama_cpp` is not installed, GeoAI uses its keyword-based fallback.

## Desktop frontend

In a second terminal:

```bash
cd electron-app
npm install
npm start
```

This starts the desktop shell in development mode.

## Building installers

Freeze the calculation engine with PyInstaller, then package the desktop app with electron-builder.

```bash
# 1. Calculation engine (output: python-backend/dist/main)
cd python-backend
pyinstaller --clean main.spec

# 2. Desktop app
cd ../electron-app
npm run build
npm run dist:win   # Windows installer  -> electron-app/release/GeoCore-Setup-<version>.exe
npm run dist:mac   # macOS disk image   -> electron-app/release/GeoCore-<version>-<arch>.dmg
```

`main.spec` bundles `llama_cpp` and its native libraries when they are installed; otherwise the build prints a warning and the resulting app uses the GeoAI fallback. Model files (`.gguf`) are never bundled.

Local builds never publish anything. Official releases are built by the GitHub Actions workflow when a version tag is pushed.
