---
title: License & Credits
slug: license
section: License & Credits
description: Licences and attribution for GeoCore and the groundhog documentation it includes.
origin: geocore
source_url: https://github.com/utkarsh-1912/geocore/blob/main/website/_content/extract_docs.py
license: GPL-3.0
author: Utkarsh Gupta
attribution: GeoCore documentation by Utkarsh Gupta, licensed under the GNU GPL v3.
groundhog_version: 0.15.0
edited_by_geocore: false
---

## GeoCore

GeoCore is developed by Utkarsh Gupta and licensed under the GNU General Public License v3.0. See the [LICENSE file](https://github.com/utkarsh-1912/geocore/blob/main/LICENSE).

## groundhog

GeoCore's engineering calculations are performed by [groundhog](https://github.com/snakesonabrain/groundhog), a general-purpose Python library for geotechnical engineering by Bruno Stuyts.

> groundhog. A general-purpose Python library for geotechnical engineering. Copyright (C) 2020-2025 Bruno Stuyts. This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

GeoCore ships groundhog 0.15.0. The groundhog API reference, guides and tutorials in these docs are derived from the groundhog package docstrings and the groundhog repository (https://github.com/snakesonabrain/groundhog, tag `v0.15.0`, commit `12a98f3f4330bf24b5443eb061ca00710420eaa0`) and are redistributed under the same licence. Each page lists its source, author and licence, and states whether GeoCore edited it. groundhog's own release history is not mirrored here — see the [Changelog](/docs/changelog) page for where to find it.

Upstream online documentation: [groundhog.readthedocs.io](https://groundhog.readthedocs.io).

### Content not imported

- `docs/Golden_rules.rst`: States that groundhog is provided under a Creative Commons 4.0 Attribution-ShareAlike licence, which conflicts with the repository LICENSE (GPLv3). The page is also not part of the published documentation toctree. Excluded until the licence statement is clarified upstream.
- `notebooks/Images/cgs.png`: Logo of a third-party organisation (webinar host); not groundhog content and not needed for the tutorial.
- `docs/tutorials/pcpt_processing.rst`: only states that the tutorial moved to the notebooks; the notebook is included instead.
- `docs/tutorials/pile_calculation.rst`: only states that the tutorial moved to the notebooks; the notebook is included instead.
- `docs/tutorials/soilprofiles.rst`: only states that the tutorial moved to the notebooks; the notebook is included instead.

### Figures

Figures are copied from the groundhog repository. Several figures reproduce charts from the publications cited in the corresponding function documentation; see those references for the original sources.

## Other GeoCore dependencies

GeoCore also uses open-source components such as FastAPI, Pydantic, NumPy, SciPy, pandas, Plotly, React and Electron, each under its own licence. GeoAI can optionally run local models through llama.cpp (llama-cpp-python); downloaded model weights are covered by their publishers' licences.
