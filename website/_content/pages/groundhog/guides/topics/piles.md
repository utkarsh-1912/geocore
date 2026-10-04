---
title: Pile calculations
slug: groundhog/guides/topics/piles
section: Groundhog Guides
description: Overview of groundhog's pile calculations functionality with links to the API reference.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/docs/piles/piles_toplevel.rst
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Upstream toctree/autodoc structure restructured into a single topic page that links to the API reference instead of duplicating it, with a short note on how to run this in GeoCore prepended.
upstream_docs_url: https://groundhog.readthedocs.io/en/main/piles/piles_toplevel.html
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, these functions run through the [calculation catalogue](/docs/geocore/using/modules) or through **GeoAI**, which selects and calls them through its validated Tool Registry — you never need to install Python or groundhog yourself.

This page follows the structure of the upstream groundhog documentation for *Pile calculations*. For each function it gives the method summary and key formulas from the groundhog docstrings, with a link to the full API reference.

## Unit skin friction

Upstream page: [Unit skin friction](https://groundhog.readthedocs.io/en/main/piles/skinfriction.html)

Module [`groundhog.deepfoundations.axialcapacity.skinfriction`](/docs/groundhog/api/deepfoundations/axialcapacity/skinfriction). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### API_unit_shaft_friction_sand_rp2geo

Function [`API_unit_shaft_friction_sand_rp2geo`](/docs/groundhog/api/deepfoundations/axialcapacity/skinfriction#api_unit_shaft_friction_sand_rp2geo).

Calculates unit skin friction according to the beta method in API RP 2GEO.

$$
f(z) = \beta \cdot p'_o(z)
$$

*Reference:* API RP 2GEO, API RP 2GEO Geotechnical and Foundation Design Considerations, 2011

### API_unit_shaft_friction_clay

Function [`API_unit_shaft_friction_clay`](/docs/groundhog/api/deepfoundations/axialcapacity/skinfriction#api_unit_shaft_friction_clay).

Calculates unit skin friction according to the alpha method in API RP 2GEO.

$$
f(z) = \alpha \cdot S_u
$$

$$
\alpha = 0.5 \cdot \psi^{-0.5} & \quad \text{for } \psi \leq 1.0
$$

*2 more formulas in the full reference.*

*Reference:* API RP 2GEO, API RP 2GEO Geotechnical and Foundation Design Considerations, 2011.

### unitskinfriction_sand_almhamre

Function [`unitskinfriction_sand_almhamre`](/docs/groundhog/api/deepfoundations/axialcapacity/skinfriction#unitskinfriction_sand_almhamre).

Calculates the unit skin friction in sand according to the method by Alm & Hamre.

$$
f_s = f_{s,res} + (f_{s,i} - f_{s,res}) \cdot e^{k \cdot (z-z_{tip})}
$$

$$
k = \frac{\sqrt{q_t / \sigma_{vo}^{\prime}}}{80}
$$

*4 more formulas in the full reference.*

*Reference:* Alm, T., Hamre, L., 2001. Soil model for pile driveability predictions based on CPT interpretations. Presented at the International Conference On Soil Mechanics and Foundation Engineering. Alm, T., Hamre, L., 1998. Soil model for driveability predictions. Presented at the OTC 8835, Annual Offshore Technology Conference, Houston, Texas, p. 13.

### unitskinfriction_clay_almhamre

Function [`unitskinfriction_clay_almhamre`](/docs/groundhog/api/deepfoundations/axialcapacity/skinfriction#unitskinfriction_clay_almhamre).

Calculates the unit skin friction in clay according to the method by Alm & Hamre.

$$
f_s = f_{s,res} + (f_{s,i} - f_{s,res}) \cdot e^{k \cdot (z-z_{tip})}
$$

$$
k = \frac{\sqrt{q_t / \sigma_{vo}^{\prime}}}{80}
$$

*4 more formulas in the full reference.*

*Reference:* Alm, T., Hamre, L., 2001. Soil model for pile driveability predictions based on CPT interpretations. Presented at the International Conference On Soil Mechanics and Foundation Engineering. Alm, T., Hamre, L., 1998. Soil model for driveability predictions. Presented at the OTC 8835, Annual Offshore Technology Conference, Houston, Texas, p. 13.

## Unit end bearing

Upstream page: [Unit end bearing](https://groundhog.readthedocs.io/en/main/piles/endbearing.html)

Module [`groundhog.deepfoundations.axialcapacity.endbearing`](/docs/groundhog/api/deepfoundations/axialcapacity/endbearing). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### API_unit_end_bearing_clay

Function [`API_unit_end_bearing_clay`](/docs/groundhog/api/deepfoundations/axialcapacity/endbearing#api_unit_end_bearing_clay).

Calculates unit end bearing in clay according to API RP 2 GEO.

$$
q = N_c \cdot S_u
$$

*Reference:* API RP 2GEO, API RP 2GEO Geotechnical and Foundation Design Considerations, 2011

### API_unit_end_bearing_sand_rp2geo

Function [`API_unit_end_bearing_sand_rp2geo`](/docs/groundhog/api/deepfoundations/axialcapacity/endbearing#api_unit_end_bearing_sand_rp2geo).

Calculates unit end bearing in sand according to API RP2 GEO.

$$
q = N_q \cdot p'_{o,tip}
$$

*Reference:* API RP 2GEO, API RP 2GEO Geotechnical and Foundation Design Considerations, 2011

### unitendbearing_sand_almhamre

Function [`unitendbearing_sand_almhamre`](/docs/groundhog/api/deepfoundations/axialcapacity/endbearing#unitendbearing_sand_almhamre).

Calculates unit end bearing in sand according to Alm & Hamre.

$$
q_{b,sand} = 0.15 \cdot q_t \cdot \left( \frac{q_t}{\sigma_{vo}^{\prime}} \right)^{0.2}
$$

*Reference:* Alm, T., Hamre, L., 2001. Soil model for pile driveability predictions based on CPT interpretations. Presented at the International Conference On Soil Mechanics and Foundation Engineering. Alm, T., Hamre, L., 1998. Soil model for driveability predictions. Presented at the OTC 8835, Annual Offshore Technology Conference, Houston, Texas, p. 13.

### unitendbearing_clay_almhamre

Function [`unitendbearing_clay_almhamre`](/docs/groundhog/api/deepfoundations/axialcapacity/endbearing#unitendbearing_clay_almhamre).

Calculates unit end bearing in clay according to Alm & Hamre.

$$
q_{b,clay} = 0.6 \cdot q_t
$$

*Reference:* Alm, T., Hamre, L., 2001. Soil model for pile driveability predictions based on CPT interpretations. Presented at the International Conference On Soil Mechanics and Foundation Engineering. Alm, T., Hamre, L., 1998. Soil model for driveability predictions. Presented at the OTC 8835, Annual Offshore Technology Conference, Houston, Texas, p. 13.

## Axial capacity calculations

Upstream page: [Axial capacity calculations](https://groundhog.readthedocs.io/en/main/piles/axcap.html)

### AxCapCalculation

Class [`AxCapCalculation`](/docs/groundhog/api/deepfoundations/axialcapacity/axcap#axcapcalculation).

## De Beer and Eurocode 7 calculations

Upstream page: [De Beer and Eurocode 7 calculations](https://groundhog.readthedocs.io/en/main/piles/debeer.html)

### DeBeerCalculation

Class [`DeBeerCalculation`](/docs/groundhog/api/deepfoundations/axialcapacity/debeer#debeercalculation).

## Koppejan pile resistance calculations

Upstream page: [Koppejan pile resistance calculations](https://groundhog.readthedocs.io/en/main/piles/koppejan.html)

### KoppejanCalculation

Class [`KoppejanCalculation`](/docs/groundhog/api/deepfoundations/axialcapacity/koppejan#koppejancalculation).

## Pile settlement

Upstream page: [Pile settlement](https://groundhog.readthedocs.io/en/main/piles/settlement.html)

Module [`groundhog.deepfoundations.axialresponse.settlement`](/docs/groundhog/api/deepfoundations/axialresponse/settlement). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### pile_settlement_curves

Function [`pile_settlement_curves`](/docs/groundhog/api/deepfoundations/axialresponse/settlement#pile_settlement_curves).

Calculates the pile settlement curve for pile shaft and pile base from empirical trends established based on axial pile load tests.

$$
F_{mob} = a + \frac{b-a}{1 + \left( \frac{\delta_{pile} \ \text{or} \ \delta_{pile}/D}{c} \right)^d}
$$

*Reference:* Syllabus geotechnics

## Cavity expansion methods for cast in-situ piles

Upstream page: [Cavity expansion methods for cast in-situ piles](https://groundhog.readthedocs.io/en/main/piles/cavityexpansion.html)

Module [`groundhog.deepfoundations.boreholestability.cavityexpansion`](/docs/groundhog/api/deepfoundations/boreholestability/cavityexpansion). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### stress_cylinder_elastic_isotropic

Function [`stress_cylinder_elastic_isotropic`](/docs/groundhog/api/deepfoundations/boreholestability/cavityexpansion#stress_cylinder_elastic_isotropic).

Calculates the radial and tangential stress around a cylindrical borehole under internal pressure, in a soil mass with isotropic virgin stress conditions in the given plane

$$
\frac{d \sigma_{r}}{dr} + \frac{\left(\sigma_{r} - \sigma_{\theta} \right)}{r} = 0
$$

$$
\sigma_r | _{r=a} = p \\
\sigma_r | _{r=a} = p_0
$$

*2 more formulas in the full reference.*

*Reference:* Yu, H.-S., 2000. Cavity Expansion Methods in Geomechanics. Springer-Science+Business Media, B.V.

### expansion_tresca_thicksphere

Function [`expansion_tresca_thicksphere`](/docs/groundhog/api/deepfoundations/boreholestability/cavityexpansion#expansion_tresca_thicksphere).

Calculates the stresses for cavity expansion around a thick-walled sphere in Tresca material.

$$
\text{Elastic solutions}
$$

$$
\sigma_r = -p_0 - (p - p_0) \frac{\left( \frac{b_0}{r} \right)^3 - 1}{\left( \frac{b_0}{a_0} \right)^3 - 1}
$$

*20 more formulas in the full reference.*

*Reference:* Yu, H.-S., 2000. Cavity Expansion Methods in Geomechanics. Springer-Science+Business Media, B.V.

### expansion_cylinder_tresca

Function [`expansion_cylinder_tresca`](/docs/groundhog/api/deepfoundations/boreholestability/cavityexpansion#expansion_cylinder_tresca).

Calculates the cavity expansion for a cylinder in Tresca material.

$$
\text{Elastic properties}
$$

$$
n = \frac{4 \cdot S_u \cdot (1 - \nu^2) }{E}
$$

*17 more formulas in the full reference.*

*Reference:* Yu, H.-S., 2000. Cavity Expansion Methods in Geomechanics. Springer-Science+Business Media, B.V.

## Negative skin friction

Upstream page: [Negative skin friction](https://groundhog.readthedocs.io/en/main/piles/negativeskinfriction.html)

Module [`groundhog.deepfoundations.axialcapacity.negativeskinfriction`](/docs/groundhog/api/deepfoundations/axialcapacity/negativeskinfriction). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### negativeskinfriction_pilegroup_zeevaertdebeer

Function [`negativeskinfriction_pilegroup_zeevaertdebeer`](/docs/groundhog/api/deepfoundations/axialcapacity/negativeskinfriction#negativeskinfriction_pilegroup_zeevaertdebeer).

Calculates the negative skin friction for a pile in a pile group according to the method of Zeevaert en De Beer.

$$
\frac{d \sigma_v^{\prime}}{dz} = \gamma^{\prime} - \tau \cdot \frac{O_s}{A}
$$

$$
m = K_0 \cdot \tan \delta^{\prime} \cdot \frac{O_s}{A}
$$

*4 more formulas in the full reference.*

*Reference:* Zeevaert - De Beer (1966)
