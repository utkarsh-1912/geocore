---
title: Soil dynamics
slug: groundhog/guides/topics/soildynamics
section: Groundhog Guides
description: Overview of groundhog's soil dynamics functionality with links to the API reference.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/docs/soildynamics/soildynamics_toplevel.rst
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Upstream toctree/autodoc structure restructured into a single topic page that links to the API reference instead of duplicating it.
upstream_docs_url: https://groundhog.readthedocs.io/en/main/soildynamics/soildynamics_toplevel.html
---

This page mirrors the structure of the upstream groundhog documentation for *Soil dynamics* and links each topic to the API reference.

## Liquefaction

Upstream page: [Liquefaction](https://groundhog.readthedocs.io/en/main/soildynamics/liquefaction.html)

- Module [`groundhog.soildynamics.liquefaction`](/docs/groundhog/api/soildynamics/liquefaction): [`cyclicstressratio_moss`](/docs/groundhog/api/soildynamics/liquefaction#cyclicstressratio_moss), [`liquefaction_robertsonfear`](/docs/groundhog/api/soildynamics/liquefaction#liquefaction_robertsonfear), [`liquefactionprobability_moss`](/docs/groundhog/api/soildynamics/liquefaction#liquefactionprobability_moss), [`liquefactionprobability_saye`](/docs/groundhog/api/soildynamics/liquefaction#liquefactionprobability_saye), [`cyclicstressratio_youd`](/docs/groundhog/api/soildynamics/liquefaction#cyclicstressratio_youd)

## Cyclic behaviour

Upstream page: [Cyclic behaviour](https://groundhog.readthedocs.io/en/main/soildynamics/cyclicbehaviour.html)

- Module [`groundhog.soildynamics.cyclicbehaviour`](/docs/groundhog/api/soildynamics/cyclicbehaviour): [`cycliccontours_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#cycliccontours_dssclay_andersen), [`plotcycliccontours_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotcycliccontours_dssclay_andersen), [`cycliccontours_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#cycliccontours_triaxialclay_andersen), [`plotcycliccontours_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotcycliccontours_triaxialclay_andersen), [`strainaccumulation_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#strainaccumulation_dssclay_andersen), [`plotstrainaccumulation_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotstrainaccumulation_dssclay_andersen), [`strainaccumulation_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#strainaccumulation_triaxialclay_andersen), [`plotstrainaccumulation_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotstrainaccumulation_triaxialclay_andersen), [`porepressureaccumulation_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#porepressureaccumulation_dssclay_andersen), [`plotporepressureaccumulation_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotporepressureaccumulation_dssclay_andersen), [`porepressureaccumulation_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#porepressureaccumulation_triaxialclay_andersen), [`plotporepressureaccumulation_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotporepressureaccumulation_triaxialclay_andersen), [`strainaccumulation_dsssand_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#strainaccumulation_dsssand_andersen), [`plotstrainaccumulation_dsssand_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotstrainaccumulation_dsssand_andersen), [`plotporepressureaccumulation_dsssand_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotporepressureaccumulation_dsssand_andersen), [`cyclicstrength_dsssand_relativedensity`](/docs/groundhog/api/soildynamics/cyclicbehaviour#cyclicstrength_dsssand_relativedensity), [`cyclicstrength_dsssand_watercontent`](/docs/groundhog/api/soildynamics/cyclicbehaviour#cyclicstrength_dsssand_watercontent)

## Dynamic soil property correlations

Upstream page: [Dynamic soil property correlations](https://groundhog.readthedocs.io/en/main/soildynamics/soilproperties.html)

- Module [`groundhog.soildynamics.soilproperties`](/docs/groundhog/api/soildynamics/soilproperties): [`modulusreduction_plasticity_ishibashi`](/docs/groundhog/api/soildynamics/soilproperties#modulusreduction_plasticity_ishibashi), [`gmax_shearwavevelocity`](/docs/groundhog/api/soildynamics/soilproperties#gmax_shearwavevelocity), [`dampingratio_sandgravel_seed`](/docs/groundhog/api/soildynamics/soilproperties#dampingratio_sandgravel_seed), [`modulusreduction_darendeli`](/docs/groundhog/api/soildynamics/soilproperties#modulusreduction_darendeli)

## CPT Liquefaction

Upstream page: [CPT Liquefaction](https://groundhog.readthedocs.io/en/main/soildynamics/cptliquefaction.html)

- Module [`groundhog.soildynamics.cptliquefaction`](/docs/groundhog/api/soildynamics/cptliquefaction): [`fos_liquefaction`](/docs/groundhog/api/soildynamics/cptliquefaction#fos_liquefaction), [`csr_robertson_cabal_2022`](/docs/groundhog/api/soildynamics/cptliquefaction#csr_robertson_cabal_2022), [`csr_robertson_wride_1998`](/docs/groundhog/api/soildynamics/cptliquefaction#csr_robertson_wride_1998), [`csr_idriss_boulanger_2008`](/docs/groundhog/api/soildynamics/cptliquefaction#csr_idriss_boulanger_2008), [`csr_boulanger_idriss_2014`](/docs/groundhog/api/soildynamics/cptliquefaction#csr_boulanger_idriss_2014), [`crr_robertson_cabal_2022`](/docs/groundhog/api/soildynamics/cptliquefaction#crr_robertson_cabal_2022), [`crr_robertson_wride_1998`](/docs/groundhog/api/soildynamics/cptliquefaction#crr_robertson_wride_1998), [`crr_idriss_boulanger_2008`](/docs/groundhog/api/soildynamics/cptliquefaction#crr_idriss_boulanger_2008), [`crr_boulanger_idriss_2014`](/docs/groundhog/api/soildynamics/cptliquefaction#crr_boulanger_idriss_2014), [`Qtn_cs_robertson_cabal_2022`](/docs/groundhog/api/soildynamics/cptliquefaction#qtn_cs_robertson_cabal_2022), [`Qtn_cs_robertson_wride_1998`](/docs/groundhog/api/soildynamics/cptliquefaction#qtn_cs_robertson_wride_1998), [`Qtn_cs_idriss_boulanger_2008`](/docs/groundhog/api/soildynamics/cptliquefaction#qtn_cs_idriss_boulanger_2008), [`Qtn_cs_boulanger_idriss_2014`](/docs/groundhog/api/soildynamics/cptliquefaction#qtn_cs_boulanger_idriss_2014), [`liquefaction_strains_zhang`](/docs/groundhog/api/soildynamics/cptliquefaction#liquefaction_strains_zhang)
