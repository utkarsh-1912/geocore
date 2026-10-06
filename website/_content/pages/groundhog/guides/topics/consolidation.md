---
title: Consolidation functions
slug: groundhog/guides/topics/consolidation
section: Groundhog Guides
description: Overview of groundhog's consolidation functions functionality with links to the API reference.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/docs/consolidation/consolidation_toplevel.rst
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Upstream toctree/autodoc structure restructured into a single topic page that links to the API reference instead of duplicating it, with a short note on how to run this in GeoCore prepended.
upstream_docs_url: https://groundhog.readthedocs.io/en/main/consolidation/consolidation_toplevel.html
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, these functions run through the [calculation catalogue](/docs/geocore/using/modules) or through **GeoAI**, which selects and calls them through its validated Tool Registry — you never need to install Python or groundhog yourself.

This page follows the structure of the upstream groundhog documentation for *Consolidation functions*. For each function it gives the method summary and key formulas from the groundhog docstrings, with a link to the full API reference.

## Groundwater flow

Upstream page: [Groundwater flow](https://groundhog.readthedocs.io/en/main/consolidation/groundwaterflow_toplevel.html)

### Pumping tests

Upstream page: [Pumping tests](https://groundhog.readthedocs.io/en/main/consolidation/pumpingtests.html)

Module [`groundhog.consolidation.groundwaterflow.pumpingtests`](/docs/groundhog/api/consolidation/groundwaterflow/pumpingtests). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

#### hydraulicconductivity_unconfinedaquifer

Function [`hydraulicconductivity_unconfinedaquifer`](/docs/groundhog/api/consolidation/groundwaterflow/pumpingtests#hydraulicconductivity_unconfinedaquifer).

Calculates the hydraulic conductivity from observing two standpipes in the vicinity of a pumping well.

$$
i = \frac{dz}{dr}
$$

$$
A = 2 \pi r z
$$

*3 more formulas in the full reference.*

*Reference:* Budhu (2011). Soil mechanics and foundations. John Wiley and Sons.

## Pore pressure dissipation analysis

Upstream page: [Pore pressure dissipation analysis](https://groundhog.readthedocs.io/en/main/consolidation/dissipation_toplevel.html)

### One-dimensional consolidation

Upstream page: [One-dimensional consolidation](https://groundhog.readthedocs.io/en/main/consolidation/onedimensionalconsolidation.html)

Module [`groundhog.consolidation.dissipation.onedimensionalconsolidation`](/docs/groundhog/api/consolidation/dissipation/onedimensionalconsolidation). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

#### pore_pressure_fourier

Function [`pore_pressure_fourier`](/docs/groundhog/api/consolidation/dissipation/onedimensionalconsolidation#pore_pressure_fourier).

The function returns the excess pore pressure distribution at the specified depths for a given time.

$$
\Delta u (z,t) = \sum_{m=0}^{\infty} \frac{2 \Delta u_0}{M} \sin \left( \frac{M \cdot z}{H_{dr}} \right) \exp \left( -M^2 T_v \right)
$$

$$
M = \frac{\pi}{2} \left( 2m + 1 \right)
$$

*1 more formula in the full reference.*

*Reference:* Budhu (2011). Soil mechanics and foundations. John Wiley and Sons.

#### consolidation_degree

Function [`consolidation_degree`](/docs/groundhog/api/consolidation/dissipation/onedimensionalconsolidation#consolidation_degree).

Returns the degree of consolidation for a certain time and initial distribution of excess pore pressure.

$$
T_v = \frac{c_v t}{H_{dr}^2}
$$

*Reference:* Budhu (2011). Soil mechanics and foundations. John Wiley and Sons.

#### ConsolidationCalculation

Class [`ConsolidationCalculation`](/docs/groundhog/api/consolidation/dissipation/onedimensionalconsolidation#consolidationcalculation).

The consolidation equation can be discretised as follows:

$$
u_{i,j+1} = u_{i,j} + \frac{c_v \Delta t}{( \Delta z )^2} \left( u_{i-1,j} - 2 u_{i,j} + u_{i+1,j} \right)
$$

$$
\frac{\partial u}{\partial z} = 0 = \frac{1}{2 \Delta z} \left( u_{i-1,j} - u_{i+1,j} \right) = 0
$$

*3 more formulas in the full reference.*

#### ConsolidationCalculation

Class [`ConsolidationCalculation`](/docs/groundhog/api/consolidation/dissipation/onedimensionalconsolidation#consolidationcalculation).

The consolidation equation can be discretised as follows:

$$
u_{i,j+1} = u_{i,j} + \frac{c_v \Delta t}{( \Delta z )^2} \left( u_{i-1,j} - 2 u_{i,j} + u_{i+1,j} \right)
$$

$$
\frac{\partial u}{\partial z} = 0 = \frac{1}{2 \Delta z} \left( u_{i-1,j} - u_{i+1,j} \right) = 0
$$

*3 more formulas in the full reference.*
