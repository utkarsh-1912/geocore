---
title: Changelog
slug: changelog
section: Changelog
description: GeoCore's own release history.
origin: geocore
source_url: https://github.com/utkarsh-1912/geocore/blob/main/website/_content/geocore/changelog.md
license: GPL-3.0
author: Utkarsh Gupta
attribution: GeoCore documentation by Utkarsh Gupta, licensed under the GNU GPL v3.
groundhog_version: 0.16.0
edited_by_geocore: false
sources:
- RELEASE_GUIDE.md
- electron-app/package.json
- stage/plan.md
- .github/scripts/changelog.py
---

Release history for GeoCore itself — the desktop application, GeoAI and the integration around groundhog.
groundhog is a separate project with its own version history; see its [release notes on GitHub](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/CHANGES.txt) or the version this build ships, noted on the [License & Credits](/docs/license) page.

## Unreleased

### Added

- **Calculations by engineering task.** Calculators are now organised as a catalogue of 192 calculations in
  10 areas (site investigation, foundations, settlement, dynamics, …), each with one or more methods
  (214 in total). A sidebar switch keeps the classic groundhog-library grouping ("Library").
- **Methods and suggestions.** The ⋯ menu on a calculator lists its other methods with their status and
  standards, and suggests a method from the data you have (for pile axial capacity: a CPT-based method
  when CPT data is loaded, the soil-profile method otherwise).
- **Compare methods.** Run every method of a calculation on the same inputs and see the results side by
  side, with the spread between them.
- **Phase-relations solver.** Enter any consistent set of phase quantities (unit weight, void ratio, water
  content, saturation, …) and GeoCore solves the rest with groundhog's functions. Assumed values such as
  Gs or Sr are used only when you tick them.
- **Verified methods.** A method is marked *verified* only when it reproduces independent closed-form
  benchmark cases (32 cases, run with the test suite); everything else stays *unverified*.
- **Project ground model.** Project values for a location and depth range are taken from saved soil
  profiles, CPT data and imported AGS files, and offered as form inputs with their source shown.
  **Import AGS** reads locations (LOCA/HOLE), layers (GEOL) and SPT N values (averaged per layer, with the
  test depths listed as the source).
- **Saved runs, reports and sign-off.** Save a calculation to the project, see when it is out of date
  because its inputs changed, export an HTML or PDF report, and sign a run off as reviewed; the reviewer
  and date appear in the report. Values you type over a project value are recorded as overrides.
- **Command palette filters** by data type (CPT, SPT, AGS, soil profile, lab tests) and by standard.
- **GeoAI project inputs.** The `get_project_inputs` tool gives GeoAI the project values for a calculation
  at a location and depth range, with sources, instead of asking for numbers already in the project.
- **GeoAI Explain.** An *Explain* action on a result asks the local model for a worked solution (problem,
  method, governing equation, substitution, result) grounded in the calculation's guide and its actual
  inputs and outputs. The model does not recalculate. GeoCore checks the answer and warns when it quotes
  a number that is not in the calculation or writes an equation different from the documented one.
- **Applicability warnings** on GeoAI tool results, for example Rankine with a backfill slope steeper
  than φ, or a relative density outside its limits.
- **Guide & Theory for the Indian Standard calculators** (IS 6403, IS 1498, IS 2131, IS 1892, IS 1904,
  IS 2950, IS 2720): governing equations, factor tables, clause references, parameters with symbols,
  units and ranges, and limitations, written from what GeoCore implements.
- **Indian Standard calculations in the online docs**: a new *Using GeoCore › Indian Standard (BIS)
  calculations* page with the same theory, equations and inputs as the app's guides.
- Contributor guide, code of conduct, security policy, citation file (`CITATION.cff`) and issue and pull
  request templates.
- Local API: `POST /api/calculations/{id}/run`, `POST /api/calculations/{id}/compare`,
  `GET /api/calculations/{id}/suggest`, `GET /api/catalogue` and the `/api/project/...` routes for the
  project model, runs, reviews and reports.
- Mohr-Coulomb triaxial compression and extension calculators (Constitutive models › General): Mohr's
  circle at failure, the stresses at failure and the orientation of the failure plane, from groundhog.
- Burland (1990) intrinsic and sedimentation compression lines calculator (Site investigation ›
  Correlations: Cohesive soils): the ICL and SCL plotted against vertical effective stress, with the
  intrinsic compression index C\*c and the void ratio e\*100.
- GeoAI can read GeoCore's own documentation. The `get_function_documentation` tool returns a groundhog
  function's documented inputs (with units and suggested ranges), outputs, formulas and cited references,
  and the documentation is searchable through GeoAI's local document index, with links to these pages.

### Changed

- Calculator pages are simpler: one card with the inputs, and the extras (methods, project values,
  solver, compare) behind a single *More options* menu. Project values and Compare open as dialogs, with
  Sync and Import AGS beside the dialog title.
- Equations in the guides and docs render more cleanly. Units are set upright, math in parameter
  descriptions and tooltips is typeset, and unbalanced braces from groundhog docstrings are repaired.
- GeoAI tool details (method, standards) come from the calculation catalogue, so the chat shows the
  same names as the calculator pages.
- **Project** (project calculations and reports) moved from the title bar to the home screen's welcome card;
  it is also in the command palette.
- The README was rewritten, with the logo, a feature overview and the project's open-source policies.
- The website's home page combines the three principles (offline, deterministic, open source) with
  the calculations overview.
- Release notes on GitHub and on the download page now come from this changelog
  (`.github/scripts/changelog.py`), instead of an auto-generated "Full Changelog" link.

### Fixed

- Settlement calculation (profile): a profile without compressibility data now gets a clear message that
  names the missing columns (Cc, Cr and OCR, or mv) and the columns found, instead of a raw error.
  Common column names such as `UnitWeight [kN_m3]` and `SoilType` are recognised, the saved profile is
  no longer modified by the calculation, and a result that is not a number is reported as an error.
- Negative skin friction and pile-test forms now accept a saved soil profile. The log-time and root-time
  consolidation forms keep the drainage length. The relative-density form labels state groundhog's
  e_min / e_max convention.
- AGS files with commas inside quoted fields are read correctly.
- PDF export works for large reports (previously limited to about 2 MB).

- The documentation now describes the groundhog GeoCore actually ships: version 0.16.0 at the commit
  pinned in `python-backend/requirements.txt`, not the 0.15.0 release. Links to groundhog source code
  point at that commit; several (LCPC, pile testing, lateral response, soil mixing) previously led to
  files that do not exist in the 0.15.0 release.
- The AASHTO Young's modulus (SPT) calculator had no Guide & Theory text in the app and was not marked
  "Available in GeoCore" in these docs.
- The release workflow, when started by hand from a branch, published the release under the branch name
  (`main`) instead of the version tag. The in-app updater needs a version tag to recognise a release.

## v1.0.0 — 2026-10-04

First public release.

### Added

- GeoCore desktop application (Electron front end, local Python/FastAPI backend) running groundhog's
  geotechnical calculations entirely offline, with calculators grouped by domain: site investigation,
  shallow and deep foundations, pipelines and cables, soil dynamics, consolidation, excavations and
  retaining structures, constitutive models, and Eurocode 7 factors and parameter selection.
- Indian Standard (BIS) calculations implemented in GeoCore: IS 6403 bearing capacity, IS 1904
  settlement and stability checks, IS 2950 raft rigidity, IS 1892 investigation depth and borehole
  layout, IS 2131 SPT corrections, IS 1498 soil classification and IS 2720 laboratory tests.
- Offline Guide & Theory for each calculator (theory, formulas, parameters and references from the
  groundhog docstrings), and a Formula & Derivation card that explains a computed result.
- Soil profiles and CPT tables from CSV or Excel files, saved between sessions; calculation history,
  favourites, a command palette, and export of results to PDF, CSV and JSON.
- GeoAI: a local assistant integrated into GeoCore. A small language model running on-device
  (llama.cpp / GGUF) selects and calls GeoCore's calculation tools through a validated Tool Registry —
  groundhog performs the actual calculation; the model never computes results itself.
- CPT, SPT and AGS (3.1 / 4.0) data ingestion, with deterministic soil behaviour type classification and
  parameter derivation feeding into GeoAI's project context.
- Local document research (RAG) for GeoAI, with evidence tiered by source (project data, calculation
  result, literature, standards/guidance, model interpretation, assumption) so a literature answer is
  never shown as if it were a project measurement.
- GeoAI model manager: download a curated GGUF model or link one you already have; the model is loaded
  in the background when the chat opens and released after 15 minutes without use.
- Windows (installer), macOS (Intel and Apple Silicon `.dmg`/`.zip`) and Linux (`.AppImage`, `.deb`)
  builds. The Windows installer, macOS app and AppImage update themselves from GitHub Releases.
