---
title: Excavations
slug: groundhog/guides/topics/excavations
section: Groundhog Guides
description: Overview of groundhog's excavations functionality with links to the API reference.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/docs/excavations/excavations_toplevel.rst
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Upstream toctree/autodoc structure restructured into a single topic page that links to the API reference instead of duplicating it, with a short note on how to run this in GeoCore prepended.
upstream_docs_url: https://groundhog.readthedocs.io/en/main/excavations/excavations_toplevel.html
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, these functions run through the [calculation catalogue](/docs/geocore/using/modules) or through **GeoAI**, which selects and calls them through its validated Tool Registry — you never need to install Python or groundhog yourself.

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

## Soilmix

Upstream page: [Soilmix](https://groundhog.readthedocs.io/en/main/excavations/soilmix.html)

Module [`groundhog.excavations.soilmix`](/docs/groundhog/api/excavations/soilmix). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### bendingstiffness_soilmix_method1

Function [`bendingstiffness_soilmix_method1`](/docs/groundhog/api/excavations/soilmix#bendingstiffness_soilmix_method1).

Calculates the bending stiffness of a soilmix wall (for use in geotechnical retaining wall calculations) using the combined stiffness of reinforcements and the soilmix material itself.

$$
EI\text{-eff} = \frac{EI\text{-1} + EI\text{-2}}{2}
$$

$$
EI\text{-1}=E_a I_a + E_{sm}(I_{sm} - I_a)=E_{sm} \left[ (n-1) I_a + I_{sm}\right] \quad \text{where } n=E_a/E_{sm}
$$

*12 more formulas in the full reference.*

*Reference:* Denies, N. and Huybrechts, N. (2016). Handboek soimix-wanden - Ontwerp en uitvoering, SBRCURnet

### bendingstiffness_soilmix_method2

Function [`bendingstiffness_soilmix_method2`](/docs/groundhog/api/excavations/soilmix#bendingstiffness_soilmix_method2).

Calculates the bending stiffness of a soilmix wall with internal reinforcements according to a simplified method.

$$
EI\text{-eff} = E_a I_a + E_{sm} \left[ \frac{b_{c1} \cdot \left( \frac{h_{sm}}{2} \right)^3}{3} \right]
$$

$$
EI\text{-eff} / m^{\prime} = EI\text{-eff} / a=\frac{E_a I_a}{a} + E_{sm} \left[ \frac{\left( \frac{h_{sm}}{2} \right)^3}{3} \right]
$$

*Reference:* Denies, N. and Huybrechts, N. (2016). Handboek soimix-wanden - Ontwerp en uitvoering, SBRCURnet
