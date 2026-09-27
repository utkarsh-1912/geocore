---
title: Site investigation
slug: groundhog/guides/topics/site-investigation
section: Groundhog Guides
description: Overview of groundhog's site investigation functionality with links to the API reference.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/docs/site_investigation/site_investigation_toplevel.rst
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Upstream toctree/autodoc structure restructured into a single topic page that links to the API reference instead of duplicating it.
upstream_docs_url: https://groundhog.readthedocs.io/en/main/site_investigation/site_investigation_toplevel.html
---

This page mirrors the structure of the upstream groundhog documentation for *Site investigation* and links each topic to the API reference.

## Soil classification

Upstream page: [Soil classification](https://groundhog.readthedocs.io/en/main/site_investigation/classification_toplevel.html)

### Phase relations

Upstream page: [Phase relations](https://groundhog.readthedocs.io/en/main/site_investigation/phaserelations.html)

- Module [`groundhog.siteinvestigation.classification.phaserelations`](/docs/groundhog/api/siteinvestigation/classification/phaserelations): [`voidratio_porosity`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#voidratio_porosity), [`porosity_voidratio`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#porosity_voidratio), [`saturation_watercontent`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#saturation_watercontent), [`bulkunitweight`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#bulkunitweight), [`dryunitweight_watercontent`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#dryunitweight_watercontent), [`voidratio_drydensity`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#voidratio_drydensity), [`bulkunitweight_dryunitweight`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#bulkunitweight_dryunitweight), [`relative_density`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#relative_density), [`voidratio_bulkunitweight`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#voidratio_bulkunitweight), [`unitweight_watercontent_saturated`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#unitweight_watercontent_saturated), [`density_unitweight`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#density_unitweight), [`unitweight_density`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#unitweight_density), [`watercontent_voidratio`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#watercontent_voidratio), [`voidratio_watercontent`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#voidratio_watercontent)

### Soil classes and categories

Upstream page: [Soil classes and categories](https://groundhog.readthedocs.io/en/main/site_investigation/categories.html)

- Module [`groundhog.siteinvestigation.classification.categories`](/docs/groundhog/api/siteinvestigation/classification/categories): [`relativedensity_categories`](/docs/groundhog/api/siteinvestigation/classification/categories#relativedensity_categories), [`su_categories`](/docs/groundhog/api/siteinvestigation/classification/categories#su_categories), [`uscs_categories`](/docs/groundhog/api/siteinvestigation/classification/categories#uscs_categories), [`samplequality_voidratio_lunne`](/docs/groundhog/api/siteinvestigation/classification/categories#samplequality_voidratio_lunne)

## Soil parameter correlations

Upstream page: [Soil parameter correlations](https://groundhog.readthedocs.io/en/main/site_investigation/correlations_toplevel.html)

### All soil types

Upstream page: [All soil types](https://groundhog.readthedocs.io/en/main/site_investigation/correlations_general.html)

- Module [`groundhog.siteinvestigation.correlations.general`](/docs/groundhog/api/siteinvestigation/correlations/general): [`acousticimpedance_bulkunitweight_chen`](/docs/groundhog/api/siteinvestigation/correlations/general#acousticimpedance_bulkunitweight_chen), [`shearwavevelocity_compressionindex_cha`](/docs/groundhog/api/siteinvestigation/correlations/general#shearwavevelocity_compressionindex_cha), [`k0_frictionangle_mesri`](/docs/groundhog/api/siteinvestigation/correlations/general#k0_frictionangle_mesri)

### Cohesive soils

Upstream page: [Cohesive soils](https://groundhog.readthedocs.io/en/main/site_investigation/cohesive.html)

- Module [`groundhog.siteinvestigation.correlations.cohesive`](/docs/groundhog/api/siteinvestigation/correlations/cohesive): [`compressionindex_watercontent_koppula`](/docs/groundhog/api/siteinvestigation/correlations/cohesive#compressionindex_watercontent_koppula), [`frictionangle_plasticityindex`](/docs/groundhog/api/siteinvestigation/correlations/cohesive#frictionangle_plasticityindex), [`cv_liquidlimit_usnavy`](/docs/groundhog/api/siteinvestigation/correlations/cohesive#cv_liquidlimit_usnavy), [`gmax_plasticityocr_andersen`](/docs/groundhog/api/siteinvestigation/correlations/cohesive#gmax_plasticityocr_andersen), [`k0_plasticity_kenney`](/docs/groundhog/api/siteinvestigation/correlations/cohesive#k0_plasticity_kenney)

### Cohesionless soils

Upstream page: [Cohesionless soils](https://groundhog.readthedocs.io/en/main/site_investigation/cohesionless.html)

- Module [`groundhog.siteinvestigation.correlations.cohesionless`](/docs/groundhog/api/siteinvestigation/correlations/cohesionless): [`gmax_sand_hardinblack`](/docs/groundhog/api/siteinvestigation/correlations/cohesionless#gmax_sand_hardinblack), [`permeability_d10_hazen`](/docs/groundhog/api/siteinvestigation/correlations/cohesionless#permeability_d10_hazen), [`hssmall_parameters_sand`](/docs/groundhog/api/siteinvestigation/correlations/cohesionless#hssmall_parameters_sand), [`stress_dilatancy_bolton`](/docs/groundhog/api/siteinvestigation/correlations/cohesionless#stress_dilatancy_bolton)

## In-situ tests

Upstream page: [In-situ tests](https://groundhog.readthedocs.io/en/main/site_investigation/insitutests_toplevel.html)

### PCPT processing class

Upstream page: [PCPT processing class](https://groundhog.readthedocs.io/en/main/site_investigation/pcpt_class.html)

- Class [`PCPTProcessing`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_processing#pcptprocessing) (`groundhog.siteinvestigation.insitutests.pcpt_processing`)

### PCPT functions

Upstream page: [PCPT functions](https://groundhog.readthedocs.io/en/main/site_investigation/pcpt_functions.html)

- Module [`groundhog.siteinvestigation.insitutests.pcpt_correlations`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations): [`pcpt_normalisations`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#pcpt_normalisations), [`soilclass_robertson`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#soilclass_robertson), [`ic_soilclass_robertson`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#ic_soilclass_robertson), [`behaviourindex_pcpt_robertsonwride`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#behaviourindex_pcpt_robertsonwride), [`gmax_sand_rixstokoe`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#gmax_sand_rixstokoe), [`gmax_clay_maynerix`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#gmax_clay_maynerix), [`relativedensity_ncsand_baldi`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#relativedensity_ncsand_baldi), [`relativedensity_ocsand_baldi`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#relativedensity_ocsand_baldi), [`coneresistance_ocsand_baldi`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#coneresistance_ocsand_baldi), [`relativedensity_sand_jamiolkowski`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#relativedensity_sand_jamiolkowski), [`frictionangle_sand_kulhawymayne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#frictionangle_sand_kulhawymayne), [`undrainedshearstrength_clay_radlunne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#undrainedshearstrength_clay_radlunne), [`frictionangle_overburden_kleven`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#frictionangle_overburden_kleven), [`ocr_cpt_lunne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#ocr_cpt_lunne), [`sensitivity_frictionratio_lunne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#sensitivity_frictionratio_lunne), [`unitweight_mayne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#unitweight_mayne), [`vs_ic_robertsoncabal`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_ic_robertsoncabal), [`k0_sand_mayne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#k0_sand_mayne), [`gmax_cpt_puechen`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#gmax_cpt_puechen), [`behaviourindex_pcpt_nonnormalised`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#behaviourindex_pcpt_nonnormalised), [`drainedsecantmodulus_sand_bellotti`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#drainedsecantmodulus_sand_bellotti), [`gmax_voidratio_maynerix`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#gmax_voidratio_maynerix), [`vs_cpt_andrus`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_andrus), [`vs_cpt_hegazymayne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_hegazymayne), [`vs_cpt_longdonohue`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_longdonohue), [`soiltype_vs_longodonohue`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#soiltype_vs_longodonohue), [`vs_cptd50_karrayetal`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cptd50_karrayetal), [`vs_cpt_wrideetal`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_wrideetal), [`vs_cpt_tonniandsimonini`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_tonniandsimonini), [`vs_cpt_mcgannetal`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_mcgannetal), [`constrainedmodulus_pcpt_robertson`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#constrainedmodulus_pcpt_robertson), [`vs_stressdependent_stuyts`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_stressdependent_stuyts), [`dissipation_test_teh`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#dissipation_test_teh), [`clippingdepths_qc1N_tianlehane`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#clippingdepths_qc1n_tianlehane)

### SPT processing class

Upstream page: [SPT processing class](https://groundhog.readthedocs.io/en/main/site_investigation/spt_processing.html)

- Class [`SPTProcessing`](/docs/groundhog/api/siteinvestigation/insitutests/spt_processing#sptprocessing) (`groundhog.siteinvestigation.insitutests.spt_processing`)

### SPT corrections and correlations

Upstream page: [SPT corrections and correlations](https://groundhog.readthedocs.io/en/main/site_investigation/spt_correlations.html)

- Module [`groundhog.siteinvestigation.insitutests.spt_correlations`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations): [`overburdencorrection_spt_liaowhitman`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#overburdencorrection_spt_liaowhitman), [`spt_N60_correction`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#spt_n60_correction), [`relativedensity_spt_kulhawymayne`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#relativedensity_spt_kulhawymayne), [`undrainedshearstrength_spt_salgado`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#undrainedshearstrength_spt_salgado), [`frictionangle_spt_kulhawymayne`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#frictionangle_spt_kulhawymayne), [`relativedensityclass_spt_terzaghipeck`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#relativedensityclass_spt_terzaghipeck), [`overburdencorrection_spt_ISO`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#overburdencorrection_spt_iso), [`frictionangle_spt_PHT`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#frictionangle_spt_pht), [`youngsmodulus_spt_AASHTO`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#youngsmodulus_spt_aashto), [`undrainedshearstrengthclass_spt_terzaghipeck`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#undrainedshearstrengthclass_spt_terzaghipeck)

## Laboratory testing

Upstream page: [Laboratory testing](https://groundhog.readthedocs.io/en/main/site_investigation/labtests_toplevel.html)

### Sample preparation

Upstream page: [Sample preparation](https://groundhog.readthedocs.io/en/main/site_investigation/samplepreparation.html)

- Module [`groundhog.siteinvestigation.labtesting.samplepreparation`](/docs/groundhog/api/siteinvestigation/labtesting/samplepreparation): [`undercompaction_cohesionless_ladd`](/docs/groundhog/api/siteinvestigation/labtesting/samplepreparation#undercompaction_cohesionless_ladd)

### Index tests

Upstream page: [Index tests](https://groundhog.readthedocs.io/en/main/site_investigation/indextests.html)

- Class [`PlasticityChart`](/docs/groundhog/api/siteinvestigation/labtesting/indextests#plasticitychart) (`groundhog.siteinvestigation.labtesting.indextests`)
- Class [`PSDChart`](/docs/groundhog/api/siteinvestigation/labtesting/indextests#psdchart) (`groundhog.siteinvestigation.labtesting.indextests`)

### Compressibility

Upstream page: [Compressibility](https://groundhog.readthedocs.io/en/main/site_investigation/compressibility.html)

- Module [`groundhog.siteinvestigation.labtesting.compressibility`](/docs/groundhog/api/siteinvestigation/labtesting/compressibility): [`selectpoints`](/docs/groundhog/api/siteinvestigation/labtesting/compressibility#selectpoints), [`roottimemethod`](/docs/groundhog/api/siteinvestigation/labtesting/compressibility#roottimemethod), [`logtimemethod`](/docs/groundhog/api/siteinvestigation/labtesting/compressibility#logtimemethod)
