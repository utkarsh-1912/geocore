---
title: Running calculations
slug: geocore/using/calculations
section: Using GeoCore
description: Find a calculator, enter inputs, read the results and export them.
origin: geocore
source_url: https://github.com/utkarsh-1912/geocore/blob/main/website/_content/geocore/calculations.md
license: GPL-3.0
author: Utkarsh Gupta
attribution: GeoCore documentation by Utkarsh Gupta, licensed under the GNU GPL v3.
groundhog_version: 0.15.0
edited_by_geocore: false
sources:
- electron-app/src/App.jsx
- electron-app/src/components/HelpModal.jsx
- electron-app/src/features/command/CommandPalette.jsx
- electron-app/src/context/HistoryContext.jsx
- electron-app/src/utils/exportUtils.js
- electron-app/src/features/calculations/FormulaDerivationCard.jsx
- python-backend/core/registry.py
- python-backend/core/calculation_history.py
---

## Workflow

1. Pick a category in the sidebar or on the dashboard.
2. Choose a calculator. The full list is in the [calculation catalogue](/docs/geocore/using/modules).
3. Fill in the inputs. Field labels show the expected unit and, where groundhog defines one, the suggested range.
4. Click **Calculate** to see the results as tables and, for calculators that produce them, interactive Plotly charts.

Each calculator has a **Guide & Theory** panel with the method's theory, formulas, parameters and references, taken from the groundhog documentation and available offline. Figures are left out of the app; they are in the [API reference](/docs/groundhog/api) entry for each function.

Under the results, the **Formula & Derivation** card shows the method, the standard or reference and the formula behind the result, with your inputs. These come from the calculation engine, not from a language model. If a GeoAI model is installed, a short plain-language explanation is added a moment later.

## Finding calculators

- **Command palette** (`Ctrl+K`, or `/` when no text field is focused): search across categories, sub-modules and calculators, and run actions such as toggling dark mode, opening the calculation history or opening help.
- **Favourites:** calculators can be marked as favourites for quick access. Favourites are stored locally on your computer.

## Units and inputs

Enter values in the units shown for each field; GeoCore does not convert units in the calculation forms. groundhog functions mix units deliberately (for example CPT cone resistance in MPa but stresses in kPa), so check each label.

Inputs that require an object, such as a soil profile, are selected from the objects you have created (see [Soil profiles](/docs/geocore/using/soil-profiles)).

## Results and errors

- Numerical results are shown with the keys returned by groundhog, which include the unit in square brackets (for example `Dr sat [-]`).
- If the inputs are outside the range groundhog accepts for a method, groundhog returns empty results and GeoCore shows the calculation as failed together with groundhog's warning.
- Validation errors list each field that failed and the value received.

## Exporting results

Use the export menu on the results view:

| Export | Content |
|---|---|
| **PDF report** | Inputs table, results and, when available, a captured image of the chart. |
| **CSV data** | Tabular results. |
| **JSON data** | The full result returned by the calculation engine. |

## Calculation history

GeoCore keeps the 50 most recent calculations in a history panel (`Ctrl+H`). The history is stored locally by the desktop app. Individual entries can be deleted, or the whole history cleared.

Separately, the calculation engine keeps an audit trail of the last 500 successful calculations (calculator, inputs, a short summary of the result and the time), stored with your project data. Entries can be marked as checked. It is available through the [local API](/docs/geocore/using/local-api#calculation-history).

## Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+K` (`Cmd+K` on macOS) | Command palette |
| `/` | Open the command palette when no text field is focused |
| `Ctrl+H` (`Cmd+H` on macOS) | Toggle calculation history |
| `Ctrl+Shift+A` (`Cmd+Shift+A` on macOS) | Toggle the GeoAI assistant panel |
| `↑` / `↓` | Move through list selections |
| `Enter` | Confirm the selection |
| `Esc` | Close dialogs and panels |
