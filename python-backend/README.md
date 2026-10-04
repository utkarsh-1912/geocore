# GeoCore backend

FastAPI service that exposes the Groundhog calculation library to the desktop app and hosts GeoAI. It binds to `127.0.0.1:8000`.

## Run

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
python main.py
```

Interactive API docs: `http://127.0.0.1:8000/docs`. Health: `GET /health`, `GET /health/details`.

Python 3.10+ (CI runs 3.10, so avoid newer syntax).

## Layout

| Path | Contents |
| :--- | :--- |
| `main.py` | App entry point; starts a background import warm-up so the first calculation is not slow |
| `core/registry.py`, `wrappers.py`, `plotting_wrappers.py`, `labtesting_wrappers.py`, `manual_functions.py` | The calculation registry: one wrapper per Groundhog function, input conversion and result sanitising |
| `core/function_manifest.json` | Generated list of exposed functions; `function_manifest.py` builds and checks it |
| `core/router.py` | `/api/execute`, saved objects, schemas, file upload |
| `core/state.py` | Saved objects (soil profiles, CPTs) persisted per user |
| `core/paths.py` | Per-user storage; `GEOCORE_CONFIG_DIR` overrides it (tests use this) |
| `core/schema_manager.py`, `schema_overrides.json`, `module_info_structured.json` | Form schemas and manual overrides; `generate_schemas.py` regenerates them |
| `core/geoai/` | GeoAI: see [core/geoai/README.md](core/geoai/README.md) |
| `tests/` | Test suite |
| `main.spec` | PyInstaller spec for the packaged backend |

User data lives outside the repository: `%APPDATA%\GeoCore\` on Windows, `~/.geocore/` elsewhere (saved objects, GeoAI config, models, research index, chat turn log).

## Tests

```bash
pip install pytest httpx
python -m pytest tests/
python -m pytest tests/ -k geoai      # GeoAI only
```

The suite does not need a model or network access: GeoAI tests use scripted providers. Numerical tests compare against deterministic expected values, never against model output.

## Build

```bash
pyinstaller --clean main.spec
```

Output goes to `dist/` (git-ignored). Check the result with `python smoke_test_frozen.py dist/main/main.exe` (the release workflow does this on every platform; it needs port 8000 free). `llama_cpp` must be installed when freezing, or the packaged app falls back to the heuristic provider; see [../RELEASE_GUIDE.md](../RELEASE_GUIDE.md).
