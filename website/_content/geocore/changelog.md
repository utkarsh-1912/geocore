---
title: Changelog
slug: changelog
section: Changelog
nav_order: 10
description: GeoCore's own release history.
sources:
- RELEASE_GUIDE.md
- electron-app/package.json
- stage/plan.md
---

Release history for GeoCore itself — the desktop application, GeoAI and the integration around groundhog.
groundhog is a separate project with its own version history; see its [release notes on GitHub](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/CHANGES.txt) or the version this build ships, noted on the [License & Credits](/docs/license) page.

## Unreleased

### Added

- Mohr-Coulomb triaxial compression and extension calculators (Constitutive models › General): Mohr's
  circle at failure, the stresses at failure and the orientation of the failure plane, from groundhog.
- GeoAI can read GeoCore's own documentation. The `get_function_documentation` tool returns a groundhog
  function's documented inputs (with units and suggested ranges), outputs, formulas and cited references,
  and the documentation is searchable through GeoAI's local document index, with links to these pages.

### Fixed

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

