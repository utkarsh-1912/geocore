---
title: Shallow foundations
slug: groundhog/guides/topics/shallowfoundations
section: Groundhog Guides
description: Overview of groundhog's shallow foundations functionality with links to the API reference.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/docs/shallowfoundations/shallowfoundations_toplevel.rst
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Upstream toctree/autodoc structure restructured into a single topic page that links to the API reference instead of duplicating it.
upstream_docs_url: https://groundhog.readthedocs.io/en/main/shallowfoundations/shallowfoundations_toplevel.html
---

This page mirrors the structure of the upstream groundhog documentation for *Shallow foundations* and links each topic to the API reference.

## Stress distributions

Upstream page: [Stress distributions](https://groundhog.readthedocs.io/en/main/shallowfoundations/stressdistribution.html)

- Module [`groundhog.shallowfoundations.stressdistribution`](/docs/groundhog/api/shallowfoundations/stressdistribution): [`stresses_pointload`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_pointload), [`stresses_stripload`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_stripload), [`stresses_circle`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_circle), [`stresses_rectangle`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_rectangle), [`stresses_lineload_retainingwall`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_lineload_retainingwall), [`stresses_stripload_retainingwall`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_stripload_retainingwall)

## Shallow foundation capacity

Upstream page: [Shallow foundation capacity](https://groundhog.readthedocs.io/en/main/shallowfoundations/capacity.html)

- Class [`ShallowFoundationCapacityUndrained`](/docs/groundhog/api/shallowfoundations/capacity#shallowfoundationcapacityundrained) (`groundhog.shallowfoundations.capacity`)
- Class [`ShallowFoundationCapacityDrained`](/docs/groundhog/api/shallowfoundations/capacity#shallowfoundationcapacitydrained) (`groundhog.shallowfoundations.capacity`)
- Module [`groundhog.shallowfoundations.capacity`](/docs/groundhog/api/shallowfoundations/capacity): [`verticalcapacity_undrained_api`](/docs/groundhog/api/shallowfoundations/capacity#verticalcapacity_undrained_api), [`verticalcapacity_drained_api`](/docs/groundhog/api/shallowfoundations/capacity#verticalcapacity_drained_api), [`slidingcapacity_undrained_api`](/docs/groundhog/api/shallowfoundations/capacity#slidingcapacity_undrained_api), [`slidingcapacity_drained_api`](/docs/groundhog/api/shallowfoundations/capacity#slidingcapacity_drained_api), [`effectivearea_rectangle_api`](/docs/groundhog/api/shallowfoundations/capacity#effectivearea_rectangle_api), [`effectivearea_circle_api`](/docs/groundhog/api/shallowfoundations/capacity#effectivearea_circle_api), [`envelope_drained_api`](/docs/groundhog/api/shallowfoundations/capacity#envelope_drained_api), [`envelope_undrained_api`](/docs/groundhog/api/shallowfoundations/capacity#envelope_undrained_api), [`nq_frictionangle_sand`](/docs/groundhog/api/shallowfoundations/capacity#nq_frictionangle_sand), [`ngamma_frictionangle_vesic`](/docs/groundhog/api/shallowfoundations/capacity#ngamma_frictionangle_vesic), [`ngamma_frictionangle_meyerhof`](/docs/groundhog/api/shallowfoundations/capacity#ngamma_frictionangle_meyerhof), [`ngamma_frictionangle_davisbooker`](/docs/groundhog/api/shallowfoundations/capacity#ngamma_frictionangle_davisbooker), [`failuremechanism_prandtl`](/docs/groundhog/api/shallowfoundations/capacity#failuremechanism_prandtl), [`ShallowFoundationCapacity`](/docs/groundhog/api/shallowfoundations/capacity#shallowfoundationcapacity), [`ShallowFoundationCapacityUndrained`](/docs/groundhog/api/shallowfoundations/capacity#shallowfoundationcapacityundrained), [`ShallowFoundationCapacityDrained`](/docs/groundhog/api/shallowfoundations/capacity#shallowfoundationcapacitydrained)

## Settlement

Upstream page: [Settlement](https://groundhog.readthedocs.io/en/main/shallowfoundations/settlement.html)

- Module [`groundhog.shallowfoundations.settlement`](/docs/groundhog/api/shallowfoundations/settlement): [`primaryconsolidationsettlement_nc`](/docs/groundhog/api/shallowfoundations/settlement#primaryconsolidationsettlement_nc), [`primaryconsolidationsettlement_oc`](/docs/groundhog/api/shallowfoundations/settlement#primaryconsolidationsettlement_oc), [`consolidationsettlement_mv`](/docs/groundhog/api/shallowfoundations/settlement#consolidationsettlement_mv), [`SettlementCalculation`](/docs/groundhog/api/shallowfoundations/settlement#settlementcalculation)
- Class [`SettlementCalculation`](/docs/groundhog/api/shallowfoundations/settlement#settlementcalculation) (`groundhog.shallowfoundations.settlement`)
