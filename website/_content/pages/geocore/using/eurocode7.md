---
title: Eurocode 7 partial factors
slug: geocore/using/eurocode7
section: Using GeoCore
description: Default EN 1997-1 partial factor sets and design-approach combinations used by GeoCore's Eurocode 7 calculator.
origin: geocore
source_url: https://github.com/utkarsh-1912/geocore/blob/main/website/_content/geocore/eurocode7.md
license: GPL-3.0
author: Utkarsh Gupta
attribution: GeoCore documentation by Utkarsh Gupta, licensed under the GNU GPL v3.
groundhog_version: 0.16.0
edited_by_geocore: false
sources:
- python-backend/core/registry.py
- groundhog/standards/eurocode7/factors.py
---

GeoCore's **Eurocode 7 factors** calculator runs groundhog's [`Eurocode7_factoring_STR_GEO`](/docs/groundhog/api/standards/eurocode7/factors#eurocode7_factoring_str_geo) class. You choose a design approach and a foundation type, and GeoCore returns the selected factors on actions, soil parameters and resistances.

The tables below are generated directly from groundhog's default values, which follow EN 1997-1 Annex A. National Annexes may prescribe different values (Nationally Determined Parameters); groundhog provides override methods for these, but the GeoCore calculator returns the defaults. Always check which values apply to your project.

## Partial factors on actions (A1, A2)

| Action | A1 | A2 |
|---|---|---|
| Permanent unfavourable | 1.35 | 1.0 |
| Permanent favourable | 1.0 | 1.0 |
| Variable unfavourable | 1.5 | 1.3 |
| Variable favourable | 0 | 0 |

## Partial factors on soil parameters (M1, M2)

| Soil parameter | M1 | M2 |
|---|---|---|
| Angle of shearing resistance | 1.0 | 1.25 |
| Effective cohesion | 1.0 | 1.25 |
| Undrained shear strength | 1.0 | 1.4 |
| Unconfined strength | 1.0 | 1.4 |
| Weight density | 1.0 | 1.0 |

## Partial factors on resistances (R1 to R4)

### Spread foundation

| Component | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Bearing | 1.0 | 1.4 | 1.0 | – |
| Sliding | 1.0 | 1.1 | 1.0 | – |

### Driven pile

| Component | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Base | 1.0 | 1.1 | 1.0 | 1.3 |
| Shaft | 1.0 | 1.1 | 1.0 | 1.3 |
| Total compression | 1.0 | 1.1 | 1.0 | 1.3 |
| Shaft tension | 1.25 | 1.15 | 1.1 | 1.6 |

### Bored pile

| Component | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Base | 1.25 | 1.1 | 1.0 | 1.6 |
| Shaft | 1.0 | 1.1 | 1.0 | 1.3 |
| Total compression | 1.15 | 1.1 | 1.0 | 1.5 |
| Shaft tension | 1.25 | 1.15 | 1.1 | 1.6 |

### CFA pile

| Component | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Base | 1.1 | 1.1 | 1.0 | 1.45 |
| Shaft | 1.0 | 1.1 | 1.0 | 1.3 |
| Total compression | 1.1 | 1.1 | 1.0 | 1.4 |
| Shaft tension | 1.25 | 1.15 | 1.1 | 1.6 |

### Prestressed anchorage

| Component | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Temporary | 1.1 | 1.1 | 1.0 | 1.1 |
| Permanent | 1.1 | 1.1 | 1.0 | 1.1 |

### Retaining structure

| Component | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Bearing capacity | 1.0 | 1.4 | 1.0 | – |
| Sliding resistance | 1.0 | 1.1 | 1.0 | – |
| Earth resistance | 1.0 | 1.4 | 1.0 | – |

### Slopes

| Component | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Earth resistance | 1.0 | 1.1 | 1.0 | – |

## Design approaches

`select_design_approach` combines the factor sets as follows:

| Design approach | Actions | Soil | Resistances |
|---|---|---|---|
| DA1-1 | A1 | M1 | R1 |
| DA1-2 | A2 | M2 | R1 |
| DA2 | A1 | M1 | R2 |
| DA3-1 | A1 | M2 | R3 |
| DA3-2 | A2 | M2 | R3 |


## Parameter selection

The **constant value** and **linear trend** calculators run groundhog's [`parameter_selection`](/docs/groundhog/api/standards/eurocode7/parameter_selection) functions to derive characteristic values from test data. The constant-value method needs at least two data points unless a coefficient of variation is supplied; the linear-trend method needs at least two data points with matching depths.
