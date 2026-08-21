# 🌍 GeoCore - Advanced Geotechnical Engineering Desktop Application

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](LICENSE)
[![Build & Release](https://github.com/utkarsh-1912/geocore/actions/workflows/release.yml/badge.svg)](https://github.com/utkarsh-1912/geocore/actions/workflows/release.yml)
[![Electron Version](https://img.shields.io/badge/Electron-v40.2.1-blue)](https://www.electronjs.org/)
[![Python Backend](https://img.shields.io/badge/Python-3.10%2B-green)](https://www.python.org/)
[![GeoAI Tool Registry](https://img.shields.io/badge/GeoAI%20Tools-213%20Whitelisted-purple)](#-geoai-architecture--tool-layer)

**GeoCore** is an enterprise-grade, open-source desktop application engineered for geotechnical calculations, site investigation analysis, structural foundation verification, automated PDF reporting, and secure GeoAI integration. Powered by **Groundhog**, **FastAPI**, **React**, and **Electron**.

---

## 🚀 Download GeoCore

Get the latest native installer for your operating system:

| Platform | Download Link | Architecture |
| :--- | :--- | :--- |
| **Windows** | [📥 Download GeoCore Setup (.exe)](https://github.com/utkarsh-1912/geocore/releases/latest) | x64 (Installer & Portable) |
| **macOS** | [📥 Download GeoCore Disk Image (.dmg)](https://github.com/utkarsh-1912/geocore/releases/latest) | Apple Silicon (arm64) & Intel (x64) |

---

## ✨ Key Features & Geotechnical Modules

- 🧱 **Deep Foundations & Axial Capacity**:
  - **LCPC Method** (Bustamante & Gianeselli) CPT-based pile capacity calculation.
  - **Koppejan Method** with automated construction depth window filtering & NaN safety.
  - **De Beer Method** (Eurocode 7) for base and shaft resistance.
  - **Axial Capacity Profile (AxCap)** for compression and tension load distribution.
  - **Negative Skin Friction** (Zeevaert & De Beer) for single and pile group scenarios.
  - **Unit Skin Friction & Unit End Bearing** (API RP 2GEO & Alm & Hamre methods for sand/clay).
  - **Pile Settlement Curves** (load-settlement prediction for driven, CFA, and bored piles).
  - **Chin-Kondler Extrapolation** for static pile load testing.

- 📐 **Shallow Foundations & Settlement**:
  - Elastic settlement calculation (Janbu, Christian & Carrier methods).
  - Schmertmann CPT-based settlement estimation.
  - Bearing capacity according to Eurocode 7, Vesic, and API RP 2GEO.
  - 3D elastic stress distributions (Boussinesq, Westergaard, circular footings, strip loads).

- 🔬 **Site Investigation & In-Situ Correlations**:
  - 34 PCPT correlations ($I_c$, $Q_{tn}$, $F_r$, $s_u$, $\phi'$, $D_r$, $G_{max}$, $V_s$).
  - 10 SPT corrections and correlations ($N_{60}$, $(N_1)_{60}$, overburden corrections, relative density).
  - Soil classification and phase relations (14 fundamental phase relation models).

- 🌊 **Soil Dynamics & Liquefaction**:
  - CPT-based liquefaction trigger evaluation (Boulanger & Idriss, Robertson & Wride, Robertson & Cabal).
  - Cyclic accumulation curves (Andersen DSS and Triaxial models).
  - Small-strain shear modulus $G_{max}$ and dynamic modulus reduction curves (Darendeli, Ishibashi & Zhang).

- 📊 **Eurocode 7 & Standards**:
  - Parameter selection (Constant value 5% & 95% fractiles, linear trend analysis).
  - Partial factor calculator for Design Approaches (DA1-1, DA1-2, DA2, DA3).

- 📂 **AGS File Converter**:
  - Native parser and extractor for AGS (Association of Geotechnical and Geoenvironmental Specialists) v3.1 and v4 files.

- 📈 **Interactive Plotting & PDF Reports**:
  - Embedded high-resolution Plotly chart rendering.
  - One-click PDF generation with auto-captured visual charts, inputs table, and custom header branding.
  - Export capabilities to CSV and JSON formats.

---

## 🤖 GeoAI Architecture & Tool Layer

GeoCore incorporates an enterprise-grade **GeoAI Tool & Validation Layer** designed for secure, structured calculation execution and future Gemma/SLM integration:

```
┌─────────────────────────────────────────────────────────────┐
│                    User / UI / Gemma SLM                    │
└──────────────────────────────┬──────────────────────────────┘
                               │
               [Strict Parameter Validation]
             (Intercepts '-', 'N/A', null, NaN)
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  Whitelisted Tool Registry                  │
│       213 Authorized Tools • Pydantic v2 Contracts          │
│    (Prohibits arbitrary shell, python, SQL execution)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                 [Lazy Data Access Layer]
              (On-demand layer/depth slicing)
                               │
┌──────────────────────────────▼──────────────────────────────┐
│           Groundhog Geotechnical Calculation Engine         │
└─────────────────────────────────────────────────────────────┘
```

1. **Parameter Contracts**: 1,043 parameters cataloged across 213 functions with physical bounds, SI units, and sentinel filtering.
2. **Security Boundary**: Whitelisted tool registry (`@geoai_tool`) strictly preventing arbitrary code, shell, or filesystem execution.
3. **Lazy Data Access**: Slices stratigraphy and in-situ sounding data on demand without copying monolithic datasets.
4. **SLM Tool Calling**: Standard OpenAI (`/api/geoai/tools/format/openai`) and Google Gemini/Gemma function declarations for autonomous engineering agents.

---

## 🛠️ Architecture Overview

GeoCore utilizes a decoupled two-tier architecture for high performance:

```
┌─────────────────────────────────────────────────────────────┐
│                 GeoCore Desktop Application                 │
├──────────────────────────────┬──────────────────────────────┤
│    Electron Frontend Shell   │     Python Engine Backend    │
│  - React 19 + Vite           │  - FastAPI + Uvicorn         │
│  - Tailwind CSS + Lucide     │  - Groundhog Geotechnical Lib│
│  - Plotly + Framer Motion    │  - Pydantic v2 + GeoAI Layer │
│                              │  - Pandas + NumPy + SciPy    │
└──────────────┬───────────────┴──────────────┬───────────────┘
               │                              │
               └────────────── HTTP ──────────┘
                         (127.0.0.1:8000)
```

---

## 💻 Developer Quick Start

### Prerequisites
- **Node.js** v18+ and **npm** v9+
- **Python** 3.10+ (with `pip` and virtual environment support)

### 1. Clone Repository
```bash
git clone https://github.com/utkarsh-1912/geocore.git
cd geocore
```

### 2. Setup Python Backend
```bash
cd python-backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
python main.py
```
*The backend server will launch on `http://127.0.0.1:8000`.*

### 3. Run Automated Tests
```bash
cd python-backend
pytest tests -v
```

### 4. Setup Electron Frontend
In a new terminal window:
```bash
cd electron-app
npm install
npm start
```
*The desktop shell will start in development mode.*

---

## 📦 Building Native Installers

### Freeze Python Backend (PyInstaller)
```bash
cd python-backend
pyinstaller --clean main.spec
```
*Outputs standalone binary to `python-backend/dist/main`.*

### Package Desktop App (Electron Builder)
```bash
cd electron-app

# Build Windows Setup (.exe) & Portable
npm run dist:win

# Build macOS Disk Image (.dmg) & Zip
npm run dist:mac
```

---

## 📄 License & Author

- **Author**: Utkarsh Gupta
- **License**: GNU General Public License v3.0 ([GPL-3.0](LICENSE))
