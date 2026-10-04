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

Nothing recorded yet.

## v1.0.0 — 2026-08-21

### Added

- GeoCore desktop application (Electron front end, local Python/FastAPI backend) running groundhog's
  geotechnical calculations entirely offline, with calculators grouped by domain: site investigation,
  shallow and deep foundations, pipelines and cables, soil dynamics, consolidation, excavations and
  retaining structures, and Eurocode 7 factors.
- GeoAI: a local assistant integrated into GeoCore. A small language model running on-device
  (llama.cpp / GGUF) selects and calls GeoCore's calculation tools through a validated Tool Registry —
  groundhog performs the actual calculation; the model never computes results itself.
- CPT, SPT and AGS (3.1 / 4.0) data ingestion, with deterministic soil behaviour type classification and
  parameter derivation feeding into GeoAI's project context.
- Local document research (RAG) for GeoAI, with evidence tiered by source (project data, calculation
  result, literature, standards/guidance, model interpretation, assumption) so a literature answer is
  never shown as if it were a project measurement.
- Windows, macOS and Linux desktop builds, with auto-updating installer and AppImage targets.

