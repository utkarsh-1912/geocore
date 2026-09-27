---
title: What is GeoCore
slug: geocore/overview
section: Getting Started
description: GeoCore is a desktop geotechnical engineering workstation that runs groundhog calculations locally.
origin: geocore
source_url: https://github.com/utkarsh-1912/geocore/blob/main/website/_content/geocore/overview.md
license: GPL-3.0
author: Utkarsh Gupta
attribution: GeoCore documentation by Utkarsh Gupta, licensed under the GNU GPL v3.
groundhog_version: 0.15.0
edited_by_geocore: false
sources:
- README.md
- website/docs.html
- python-backend/main.py
- electron-app/package.json
---

GeoCore is an open-source desktop application for geotechnical calculations. It puts a form-based interface on top of [groundhog](/docs/groundhog/guides/introduction), the geotechnical Python library by Bruno Stuyts, so that groundhog's correlations and design methods can be run without writing code.

Calculations run on your own computer. The application starts a local calculation engine on `127.0.0.1` and never needs a server to compute a result. An internet connection is only used for optional things: checking for application updates and downloading GeoAI models.

## What you can do

- Run the calculators listed in the [calculation catalogue](/docs/geocore/using/modules): phase relations, CPT and SPT correlations, pile capacity (De Beer, Koppejan, LCPC, API-style unit skin friction and end bearing), shallow foundation capacity and stress distribution, settlement, consolidation, soil dynamics and liquefaction, excavations, pipelines, and Eurocode 7 factors and parameter selection.
- Build [soil profiles](/docs/geocore/using/soil-profiles) from CSV or Excel files and reuse them in calculations that need a stratigraphy.
- Load AGS files and extract individual AGS groups as tables.
- Inspect results as tables and interactive Plotly charts, and [export them](/docs/geocore/using/calculations#exporting-results) to PDF, CSV or JSON.
- Ask [GeoAI](/docs/geoai/overview), the built-in assistant, to pick a calculator and fill in its inputs from a plain-language request.

Every calculator documents its inputs with units and suggested ranges. The underlying groundhog documentation is part of these docs: see the [Groundhog API Reference](/docs/groundhog/api).

## How GeoCore is built

```text
┌──────────────────────────────────────────────────────────┐
│               GeoCore desktop application                │
├───────────────────────────┬──────────────────────────────┤
│ Electron + React frontend │ Python calculation engine    │
│  - calculation forms      │  - FastAPI (local only)      │
│  - results & Plotly charts│  - groundhog 0.15.0          │
│  - soil profile manager   │  - input validation          │
│  - GeoAI panel            │  - GeoAI agent & tools       │
└─────────────┬─────────────┴───────────────┬──────────────┘
              └──── HTTP on 127.0.0.1:8000 ─┘
```

- The **frontend** is an Electron shell with a React user interface. It renders a form for each calculator, shows results and charts, and keeps a local calculation history.
- The **calculation engine** is a Python process started by the desktop app. It maps each calculator to its groundhog function or class, validates the inputs and returns the results. In packaged builds it is a frozen PyInstaller executable, so no separate Python installation is needed.

## Input handling

Before a calculation runs, GeoCore cleans the inputs:

- empty fields and placeholder text such as `-`, `--`, `N/A`, `null` or `none` are treated as "not supplied";
- numbers typed as text (for example `.35` or `10`) are converted to numbers;
- `NaN` and infinite values are rejected with an error;
- for calculators with a GeoCore input schema, each field is also checked against its bounds, and every failing field is reported.

groundhog then applies its own validation ranges. If an input lies outside the range for which a correlation was developed, groundhog issues a warning and returns empty results; GeoCore then reports the calculation as failed and shows groundhog's warning message. Warnings raised during a successful calculation are returned with the result.

## Engineering responsibility

GeoCore reports what the selected method calculates from the inputs you supply. It does not decide whether a design is acceptable. Check the method's assumptions and validity range (shown in the [API reference](/docs/groundhog/api) for each function) and apply engineering judgement.
