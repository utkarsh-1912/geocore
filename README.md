# GeoCore

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](LICENSE)
[![CI](https://github.com/utkarsh-1912/geocore/actions/workflows/ci.yml/badge.svg)](https://github.com/utkarsh-1912/geocore/actions/workflows/ci.yml)
[![Build & Release](https://github.com/utkarsh-1912/geocore/actions/workflows/release.yml/badge.svg)](https://github.com/utkarsh-1912/geocore/actions/workflows/release.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green)](https://www.python.org/)

**GeoCore** is an open-source desktop application for geotechnical engineering: foundation design, CPT/SPT interpretation, AGS data, soil dynamics, Eurocode 7 checks and PDF reporting. Calculations are powered by the [Groundhog](https://github.com/snakesonabrain/groundhog) library.

GeoCore ships with **GeoAI**, a local engineering assistant. A small language model running on your machine interprets your question, picks the right GeoCore tool, and explains the result. The numbers always come from Groundhog, not from the model.

---

## Download

Installers are published on the [Releases page](https://github.com/utkarsh-1912/geocore/releases/latest).

| Platform | Package | Architecture |
| :--- | :--- | :--- |
| Windows | Setup `.exe` (per-user installer, auto-updates) | x64 |
| macOS | `.dmg` and `.zip` (auto-update needs a code-signed build) | Apple Silicon (arm64) and Intel (x64) |
| Linux | `.AppImage` (auto-updates) and `.deb` | x64 |

---

## Features

**Deep foundations**
- CPT-based axial pile capacity: LCPC (Bustamante & Gianeselli), Koppejan, De Beer
- Axial capacity profiles (compression and tension)
- Negative skin friction (Zeevaert–De Beer), single piles and groups
- Unit shaft friction and end bearing (API RP 2GEO, Alm & Hamre)
- Pile load–settlement curves and Chin–Kondner extrapolation of load tests

**Shallow foundations and settlement**
- Bearing capacity (Eurocode 7, Vesic, API RP 2GEO)
- Elastic and Schmertmann CPT-based settlement
- Stress distribution (Boussinesq, Westergaard, strip and circular loads)

**Site investigation**
- PCPT processing and correlations (Ic, Qtn, Fr, su, φ′, Dr, Gmax, Vs, …)
- SPT corrections and correlations (N60, (N1)60, relative density, …)
- Soil classification and phase relations
- AGS 3.1 / 4 import and conversion

**Soil dynamics and liquefaction**
- CPT-based liquefaction triggering (Boulanger & Idriss, Robertson & Wride, Robertson & Cabal)
- Cyclic accumulation (Andersen DSS/triaxial contour diagrams)
- Gmax and modulus-reduction curves (Darendeli, Ishibashi & Zhang)

**Eurocode 7**
- Characteristic value selection (5 % / 95 % fractiles, linear trends)
- Partial factors for DA1-1, DA1-2, DA2 and DA3

**Output**
- Interactive Plotly charts
- One-click PDF reports with inputs, charts and custom header
- CSV and JSON export

---

## GeoAI

GeoAI is fully local. There is no cloud LLM and no separate model server — the model is loaded in-process through `llama-cpp-python` from a GGUF file on disk.

```text
User question
     │
     ▼
Local SLM (GGUF via llama.cpp)   ← understands intent, picks a tool, extracts arguments
     │
     ▼
Tool selector                    ← retrieves a small, relevant subset of tools for the prompt
     │
     ▼
GeoAI Tool Registry              ← explicit schemas, unit-aware input validation
     │
     ▼
Groundhog / GeoCore calculation  ← deterministic result with provenance
     │
     ▼
Response guard + explanation     ← grounded answer that cites the tool, inputs and units
```

Design rules (see [AGENTS.md](AGENTS.md) for the full list):

- **The model reasons; Groundhog calculates.** The model never does the engineering arithmetic itself.
- **Whitelisted tools only.** The model cannot run arbitrary Python, shell, SQL or file operations.
- **No invented inputs.** Missing or invalid parameters come back as tool errors and GeoAI asks the user.
- **Compact context.** CPT, SPT and AGS data are parsed deterministically and exposed through query tools rather than pasted into the prompt.
- **Replaceable model.** Providers implement a common `ModelProvider` interface (`llama_cpp` for production, `heuristic` as a fallback and for tests).

### Models

Choose or download a GGUF model from the GeoAI settings panel in the app. Models and configuration are stored in:

| OS | Location |
| :--- | :--- |
| Windows | `%APPDATA%\GeoCore\` (models in `models\`) |
| macOS / Linux | `~/.geocore/` (models in `models/`) |

Useful environment variables for development:

| Variable | Purpose |
| :--- | :--- |
| `GEOAI_MODEL_PATH` | Path to a GGUF model |
| `GEOAI_PROVIDER` | `llama_cpp` or `heuristic` |
| `GEOAI_N_CTX` | Context window size |
| `GEOAI_GPU_LAYERS` | Layers offloaded to GPU |
| `GEOAI_N_THREADS`, `GEOAI_N_THREADS_BATCH` | CPU threads for generation / prompt processing |
| `GEOAI_MAX_TOOLS` | Maximum number of tools shown to the model per request |
| `GEOAI_CHAT_FORMAT` | `chatml-function-calling`, `native` or `prompted` |
| `GEOAI_LORA_PATH`, `GEOAI_LORA_SCALE` | Optional LoRA adapter |
| `GEOAI_THINKING` | Enable the model's thinking mode (off by default) |

### Reliability

The chat shows what it is doing (*Checking for tools*, *Interpreting input*, *Calling tool*, *Generating output*). A turn that produces no answer says so instead of staying blank, and the model is loaded in the background when the chat opens. Each turn's outcome is logged locally to `geoai_turns.jsonl` in the config directory (no prompt text) so failures can be counted by cause; see [the GeoAI README](python-backend/core/geoai/README.md#reliability-and-diagnostics).

### Evaluation

GeoAI has an offline evaluation suite for tool selection, argument extraction, clarification and grounding:

```bash
cd python-backend
python -m core.geoai.eval.runner --provider heuristic
python -m core.geoai.eval.runner --provider llama_cpp --model path/to/model.gguf --label my-model
```

Fine-tuning scripts (LoRA/QLoRA) live in [`python-backend/core/geoai/finetune`](python-backend/core/geoai/finetune/README.md).

---

## Architecture

```text
┌──────────────────────────────┬──────────────────────────────┐
│   Electron desktop shell     │   Python backend             │
│   React 19 + Vite            │   FastAPI + Uvicorn          │
│   Tailwind CSS, Plotly       │   Groundhog, NumPy, SciPy    │
│                              │   GeoAI (llama-cpp-python)   │
└──────────────┬───────────────┴──────────────┬───────────────┘
               └──────── HTTP 127.0.0.1:8000 ─┘
```

| Path | Contents |
| :--- | :--- |
| [`electron-app/`](electron-app/README.md) | Electron main process and React UI |
| [`python-backend/`](python-backend/README.md) | FastAPI entry point, calculation registry, wrappers and API routes |
| [`python-backend/core/geoai/`](python-backend/core/geoai/README.md) | Agent, model providers, tool registry, CPT/SPT/AGS tools, research, evaluation |
| `python-backend/tests/` | Backend test suite |
| [`website/`](website/README.md) | Product website and user documentation |
| [`AGENTS.md`](AGENTS.md) | GeoAI design rules and milestones |
| [`RELEASE_GUIDE.md`](RELEASE_GUIDE.md) | Building and publishing releases |

---

## Development

### Prerequisites

- Node.js 22 (CI's version; Vite 7 needs at least 20.19) and npm
- Python 3.10+ (CI runs on 3.10, so avoid syntax that needs a newer version)

### Backend

```bash
cd python-backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
python main.py
```

The API starts on `http://127.0.0.1:8000`.

### Frontend

In a second terminal:

```bash
cd electron-app
npm install
npm start
```

This runs the Vite dev server and opens Electron once it is ready.

### Tests

```bash
cd python-backend
pip install pytest httpx
python -m pytest tests/
```

---

## Building installers

Freeze the backend with PyInstaller, then package the desktop app:

```bash
cd python-backend
pyinstaller --clean main.spec
```

```bash
cd electron-app
npm run build
npm run dist:win    # Windows installer
npm run dist:mac    # macOS .dmg and .zip
npm run dist:linux  # Linux .AppImage and .deb (build on Linux)
```

Tagged pushes (`v*`) build and publish installers automatically through GitHub Actions. See [RELEASE_GUIDE.md](RELEASE_GUIDE.md) for the full release process.

---

## Disclaimer

GeoCore and GeoAI are engineering aids. Results depend on the input parameters and the chosen method, and must be reviewed by a qualified geotechnical engineer before being used in design.

## License

Copyright © Utkarsh Gupta. Released under the [GNU General Public License v3.0](LICENSE).
