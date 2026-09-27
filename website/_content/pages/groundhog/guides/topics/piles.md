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
geocore_edit_note: Upstream toctree/autodoc structure restructured into a single topic page that links to the API reference instead of duplicating it.
upstream_docs_url: https://groundhog.readthedocs.io/en/main/piles/piles_toplevel.html
---

This page mirrors the structure of the upstream groundhog documentation for *Pile calculations* and links each topic to the API reference.

## Unit skin friction

Upstream page: [Unit skin friction](https://groundhog.readthedocs.io/en/main/piles/skinfriction.html)

- Module [`groundhog.deepfoundations.axialcapacity.skinfriction`](/docs/groundhog/api/deepfoundations/axialcapacity/skinfriction): [`API_unit_shaft_friction_sand_rp2geo`](/docs/groundhog/api/deepfoundations/axialcapacity/skinfriction#api_unit_shaft_friction_sand_rp2geo), [`API_unit_shaft_friction_clay`](/docs/groundhog/api/deepfoundations/axialcapacity/skinfriction#api_unit_shaft_friction_clay), [`unitskinfriction_sand_almhamre`](/docs/groundhog/api/deepfoundations/axialcapacity/skinfriction#unitskinfriction_sand_almhamre), [`unitskinfriction_clay_almhamre`](/docs/groundhog/api/deepfoundations/axialcapacity/skinfriction#unitskinfriction_clay_almhamre)

## Unit end bearing

Upstream page: [Unit end bearing](https://groundhog.readthedocs.io/en/main/piles/endbearing.html)

- Module [`groundhog.deepfoundations.axialcapacity.endbearing`](/docs/groundhog/api/deepfoundations/axialcapacity/endbearing): [`API_unit_end_bearing_clay`](/docs/groundhog/api/deepfoundations/axialcapacity/endbearing#api_unit_end_bearing_clay), [`API_unit_end_bearing_sand_rp2geo`](/docs/groundhog/api/deepfoundations/axialcapacity/endbearing#api_unit_end_bearing_sand_rp2geo), [`unitendbearing_sand_almhamre`](/docs/groundhog/api/deepfoundations/axialcapacity/endbearing#unitendbearing_sand_almhamre), [`unitendbearing_clay_almhamre`](/docs/groundhog/api/deepfoundations/axialcapacity/endbearing#unitendbearing_clay_almhamre)

## Axial capacity calculations

Upstream page: [Axial capacity calculations](https://groundhog.readthedocs.io/en/main/piles/axcap.html)

- Class [`AxCapCalculation`](/docs/groundhog/api/deepfoundations/axialcapacity/axcap#axcapcalculation) (`groundhog.deepfoundations.axialcapacity.axcap`)

## De Beer and Eurocode 7 calculations

Upstream page: [De Beer and Eurocode 7 calculations](https://groundhog.readthedocs.io/en/main/piles/debeer.html)

- Class [`DeBeerCalculation`](/docs/groundhog/api/deepfoundations/axialcapacity/debeer#debeercalculation) (`groundhog.deepfoundations.axialcapacity.debeer`)

## Koppejan pile resistance calculations

Upstream page: [Koppejan pile resistance calculations](https://groundhog.readthedocs.io/en/main/piles/koppejan.html)

- Class [`KoppejanCalculation`](/docs/groundhog/api/deepfoundations/axialcapacity/koppejan#koppejancalculation) (`groundhog.deepfoundations.axialcapacity.koppejan`)

## Pile settlement

Upstream page: [Pile settlement](https://groundhog.readthedocs.io/en/main/piles/settlement.html)

- Module [`groundhog.deepfoundations.axialresponse.settlement`](/docs/groundhog/api/deepfoundations/axialresponse/settlement): [`pile_settlement_curves`](/docs/groundhog/api/deepfoundations/axialresponse/settlement#pile_settlement_curves)

## Cavity expansion methods for cast in-situ piles

Upstream page: [Cavity expansion methods for cast in-situ piles](https://groundhog.readthedocs.io/en/main/piles/cavityexpansion.html)

- Module [`groundhog.deepfoundations.boreholestability.cavityexpansion`](/docs/groundhog/api/deepfoundations/boreholestability/cavityexpansion): [`stress_cylinder_elastic_isotropic`](/docs/groundhog/api/deepfoundations/boreholestability/cavityexpansion#stress_cylinder_elastic_isotropic), [`expansion_tresca_thicksphere`](/docs/groundhog/api/deepfoundations/boreholestability/cavityexpansion#expansion_tresca_thicksphere), [`expansion_cylinder_tresca`](/docs/groundhog/api/deepfoundations/boreholestability/cavityexpansion#expansion_cylinder_tresca)

## Negative skin friction

Upstream page: [Negative skin friction](https://groundhog.readthedocs.io/en/main/piles/negativeskinfriction.html)

- Module [`groundhog.deepfoundations.axialcapacity.negativeskinfriction`](/docs/groundhog/api/deepfoundations/axialcapacity/negativeskinfriction): [`negativeskinfriction_pilegroup_zeevaertdebeer`](/docs/groundhog/api/deepfoundations/axialcapacity/negativeskinfriction#negativeskinfriction_pilegroup_zeevaertdebeer)
