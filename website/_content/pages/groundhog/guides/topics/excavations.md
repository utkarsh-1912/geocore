---
title: Excavations
slug: groundhog/guides/topics/excavations
section: Groundhog Guides
description: Overview of groundhog's excavations functionality with links to the API reference.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/docs/excavations/excavations_toplevel.rst
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Upstream toctree/autodoc structure restructured into a single topic page that links to the API reference instead of duplicating it.
upstream_docs_url: https://groundhog.readthedocs.io/en/main/excavations/excavations_toplevel.html
---

This page follows the structure of the upstream groundhog documentation for *Excavations*. For each function it gives the method summary and key formulas from the groundhog docstrings, with a link to the full API reference.

## Earth pressure coefficients

Upstream page: [Earth pressure coefficients](https://groundhog.readthedocs.io/en/main/excavations/basic.html)

Module [`groundhog.excavations.basic`](/docs/groundhog/api/excavations/basic). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### earthpressurecoefficients_frictionangle

Function [`earthpressurecoefficients_frictionangle`](/docs/groundhog/api/excavations/basic#earthpressurecoefficients_frictionangle).

Calculates coefficient of active and passive earth pressure based on a construction with Mohr's circle.

$$
K_a = \frac{1 - \sin \varphi^{\prime}}{1 + \sin \varphi^{\prime}}
$$

$$
K_p = \frac{1 + \sin \varphi^{\prime}}{1 - \sin \varphi^{\prime}}
$$

*2 more formulas in the full reference.*

*Reference:* Budhu (2011). Soil mechanics and foundations. John Wiley and Sons.

### earthpressurecoefficients_poncelet

Function [`earthpressurecoefficients_poncelet`](/docs/groundhog/api/excavations/basic#earthpressurecoefficients_poncelet).

Calculates the active and passive earth pressure coefficients for a retaining wall with friction (characterised by an interface friction angle) and an inclination to the vertical.

$$
K_{aC} = \frac{\cos ^2 (\varphi^{\prime} - \eta)}{\cos ^2 \eta \cos (\eta + \delta) \left[  1 + \left( \frac{\sin (\varphi^{\prime} + \delta) \sin (\varphi^{\prime} - \beta)}{\cos (\eta + \delta) \cos (\eta - \beta)}\right)^{0.5} \right]^2}
$$

$$
K_{pC} = \frac{\cos ^2 (\varphi^{\prime} + \eta)}{\cos ^2 \eta \cos (\eta - \delta) \left[  1 - \left( \frac{\sin (\varphi^{\prime} + \delta) \sin (\varphi^{\prime} + \beta)}{\cos (\eta - \delta) \cos (\eta - \beta)}\right)^{0.5} \right]^2}
$$

*Reference:* Budhu (2011). Soil mechanics and foundations. John Wiley and Sons.

### earthpressurecoefficients_rankine

Function [`earthpressurecoefficients_rankine`](/docs/groundhog/api/excavations/basic#earthpressurecoefficients_rankine).

The expressions for an inclined wall with sloping ground are developed by Rankine (1857) and Chu (1991).

$$
K_{aR} = \frac{\cos (\beta - \eta) \sqrt{1 + \sin ^2 \varphi^{\prime} - 2 \sin \varphi^{\prime} \cos \omega_a }}{\cos ^2 \eta \left( \cos \beta + \sqrt{\sin ^2 \varphi^{\prime} - \sin ^2 \beta} \right)}
$$

$$
K_{pR} = \frac{\cos (\beta - \eta) \sqrt{1 + \sin ^2 \varphi^{\prime} + 2 \sin \varphi^{\prime} \cos \omega_p }}{\cos ^2 \eta \left( \cos \beta - \sqrt{\sin ^2 \varphi^{\prime} - \sin ^2 \beta} \right)}
$$

*8 more formulas in the full reference.*

*Reference:* Budhu (2011). Soil mechanics and foundations. John Wiley and Sons.
