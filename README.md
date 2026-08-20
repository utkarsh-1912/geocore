# 🌍 GeoCore - Advanced Geotechnical Engineering Desktop Application

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](LICENSE)
[![Build & Release](https://github.com/utkarsh-1912/geocore/actions/workflows/release.yml/badge.svg)](https://github.com/utkarsh-1912/geocore/actions/workflows/release.yml)
[![Electron Version](https://img.shields.io/badge/Electron-v40.2.1-blue)](https://www.electronjs.org/)
[![Python Backend](https://img.shields.io/badge/Python-3.10%2B-green)](https://www.python.org/)

**GeoCore** is an enterprise-grade, open-source desktop application engineered for geotechnical calculation, site investigation analysis, structural foundation verification, and automated reporting. Powered by **Groundhog**, **FastAPI**, **React**, and **Electron**.

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
  - Bearing capacity according to Eurocode 7 & Vesic.

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

## 🛠️ Architecture Overview

GeoCore utilizes a decoupled two-tier architecture for high performance:

```
┌─────────────────────────────────────────────────────────────┐
│                 GeoCore Desktop Application                 │
├──────────────────────────────┬──────────────────────────────┤
│    Electron Frontend Shell   │     Python Engine Backend    │
│  - React 19 + Vite           │  - FastAPI + Uvicorn         │
│  - Tailwind CSS + Lucide     │  - Groundhog Geotechnical Lib│
│  - Plotly + Framer Motion    │  - Pandas + NumPy + SciPy    │
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

### 3. Setup Electron Frontend
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
*Outputs standalone binary to `python-backend/dist/main` (or `main.exe` on Windows).*

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
- **License**: GNU General Public License v2.0 ([GPL-2.0](LICENSE))
