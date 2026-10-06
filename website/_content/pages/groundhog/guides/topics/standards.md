---
title: Standards
slug: groundhog/guides/topics/standards
section: Groundhog Guides
description: Overview of groundhog's standards functionality with links to the API reference.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/docs/standards/standards_toplevel.rst
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Upstream toctree/autodoc structure restructured into a single topic page that links to the API reference instead of duplicating it, with a short note on how to run this in GeoCore prepended.
upstream_docs_url: https://groundhog.readthedocs.io/en/main/standards/standards_toplevel.html
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, these functions run through the [calculation catalogue](/docs/geocore/using/modules) or through **GeoAI**, which selects and calls them through its validated Tool Registry — you never need to install Python or groundhog yourself.

This page follows the structure of the upstream groundhog documentation for *Standards*. For each function it gives the method summary and key formulas from the groundhog docstrings, with a link to the full API reference.

## Eurocode 7

Upstream page: [Eurocode 7](https://groundhog.readthedocs.io/en/main/standards/eurocode7_toplevel.html)

### Parameter selection

Upstream page: [Parameter selection](https://groundhog.readthedocs.io/en/main/standards/parameter_selection.html)

Module [`groundhog.standards.eurocode7.parameter_selection`](/docs/groundhog/api/standards/eurocode7/parameter_selection). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

#### constant_value

Function [`constant_value`](/docs/groundhog/api/standards/eurocode7/parameter_selection#constant_value).

Selects the characteristic value from a set of measurements using Eurocode 7 rules.

$$
X_k = X_{mean} \cdot \left( 1 - k_n \cdot V_x \right)
$$

$$
V_x \text{unknown}: k_{n,mean} = t_{n-1}^{0.95} \sqrt{ \frac{1}{n} }, \ k_{n,low} = t_{n-1}^{0.95} \sqrt{ \frac{1}{n} + 1}
$$

*1 more formula in the full reference.*

#### linear_trend

Function [`linear_trend`](/docs/groundhog/api/standards/eurocode7/parameter_selection#linear_trend).

Selects the characteristic value from a set of measurements using Eurocode 7 rules.

$$
x^{*} = \bar{x} + b ( z - \bar{z} )
$$

$$
\bar{x} = \frac{1}{n} \left( x_1 + x_2 + ... + x_n \right)
$$

*8 more formulas in the full reference.*

### Partial factor selection

Upstream page: [Partial factor selection](https://groundhog.readthedocs.io/en/main/standards/factors.html)

#### Eurocode7_factoring_STR_GEO

Class [`Eurocode7_factoring_STR_GEO`](/docs/groundhog/api/standards/eurocode7/factors#eurocode7_factoring_str_geo).
