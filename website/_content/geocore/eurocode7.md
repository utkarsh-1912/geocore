---
title: Eurocode 7 partial factors
slug: geocore/using/eurocode7
section: Using GeoCore
nav_order: 30
description: Default EN 1997-1 partial factor sets and design-approach combinations used by GeoCore's Eurocode 7 calculator.
sources:
- python-backend/core/registry.py
- groundhog/standards/eurocode7/factors.py
---

GeoCore's **Eurocode 7 factors** calculator runs groundhog's [`Eurocode7_factoring_STR_GEO`](/docs/groundhog/api/standards/eurocode7/factors#eurocode7_factoring_str_geo) class. You choose a design approach and a foundation type, and GeoCore returns the selected factors on actions, soil parameters and resistances.

The tables below are generated directly from groundhog's default values, which follow EN 1997-1 Annex A. National Annexes may prescribe different values (Nationally Determined Parameters); groundhog provides override methods for these, but the GeoCore calculator returns the defaults. Always check which values apply to your project.

<!-- geocore:generated eurocode7-factors -->

## Parameter selection

The **constant value** and **linear trend** calculators run groundhog's [`parameter_selection`](/docs/groundhog/api/standards/eurocode7/parameter_selection) functions to derive characteristic values from test data. The constant-value method needs at least two data points unless a coefficient of variation is supplied; the linear-trend method needs at least two data points with matching depths.
