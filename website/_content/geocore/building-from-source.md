---
title: Running and building from source
slug: geocore/building-from-source
section: Getting Started
nav_order: 30
description: Set up a GeoCore development environment, run the tests, build the desktop installers and rebuild these docs.
sources:
- README.md
- RELEASE_GUIDE.md
- .github/workflows/ci.yml
- .github/workflows/release.yml
- electron-app/package.json
- website/README.md
---

## Prerequisites

- Node.js 22 (the version CI uses; Vite 7 needs at least 20.19) and npm
- Python 3.10 or newer with `pip` and virtual environment support. CI runs on 3.10, so avoid syntax that needs a newer version.

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
pip install pytest httpx
python -m pytest tests/
```

The GeoAI tests use scripted model providers, so they need no language model: `python -m pytest tests/ -k geoai`.

### Local LLM runtime for GeoAI (optional)

GeoAI runs local models through `llama-cpp-python`. To install the prebuilt CPU wheel:

```bash
cd python-backend
venv/Scripts/python.exe -m pip install llama-cpp-python --prefer-binary --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

On macOS and Linux use `venv/bin/python` instead of `venv/Scripts/python.exe`. If `llama_cpp` is not installed, GeoAI uses its keyword-based fallback.

## Desktop frontend

In a second terminal:

```bash
cd electron-app
npm install
npm start
```

This runs the Vite dev server and opens Electron once it is ready. Running from source enables development-only tools such as [form customisation](/docs/geocore/using/parameter-overrides).

## Building installers

Freeze the calculation engine with PyInstaller, then package the desktop app with electron-builder. Build each platform on that platform: Linux packages cannot be built on Windows or macOS.

```bash
# 1. Calculation engine (output: python-backend/dist/main)
cd python-backend
python -m core.function_manifest   # refresh the start-up cache of groundhog functions
pyinstaller --clean main.spec

# 2. Desktop app
cd ../electron-app
npm run build
npm run dist:win     # electron-app/release/GeoCore-Setup-<version>.exe
npm run dist:mac     # GeoCore-<version>[-arm64].dmg and -mac.zip
npm run dist:linux   # GeoCore-<version>.AppImage and geocore_<version>_amd64.deb
```

The `.deb` target needs `fakeroot` and `dpkg`, which Debian and Ubuntu include.

To check a frozen engine before packaging it, run `python smoke_test_frozen.py dist/main/main.exe` (or `dist/main/main` on macOS and Linux) while nothing else uses port 8000.

`main.spec` bundles `llama_cpp` and its native libraries when they are installed; otherwise the build prints a warning and the resulting app uses the GeoAI fallback. It also bundles the text of these docs for GeoAI. Model files (`.gguf`) are never bundled.

Local builds never publish anything. Official releases are built by the GitHub Actions workflow when a version tag (`v*`) is pushed. It first runs the CI checks and confirms that the tag matches the version in `electron-app/package.json`, `python-backend/main.py` and `python-backend/core/diagnostics.py`.

## Rebuilding the website and these docs

The website and this documentation are static pages generated from `website/_content` and committed to the repository.

```bash
# from the repository root; needs jinja2, markdown and pyyaml
python website/_build/build.py
```

The groundhog reference pages, guides and tutorials are extracted from groundhog itself: the API reference from the groundhog installed in `python-backend/venv`, the guides and tutorials from a clone of the groundhog repository. Both must be at the commit pinned in `python-backend/requirements.txt`; GeoCore uses modules that are not in the 0.15.0 release.

```bash
pip install -r python-backend/requirements.txt   # in the backend venv
git clone https://github.com/snakesonabrain/groundhog.git <tmp>/groundhog
git -C <tmp>/groundhog checkout dc7d554c6b8986bae30f518304546a911b1ca5ab
python website/_content/extract_docs.py --groundhog-repo <tmp>/groundhog
```

CI fails if the committed marketing pages differ from a fresh build. Details are in `website/README.md` and `website/_content/README.md`.
