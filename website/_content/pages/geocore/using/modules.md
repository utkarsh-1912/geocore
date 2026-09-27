---
title: Calculation catalogue
slug: geocore/using/modules
section: Using GeoCore
description: Every calculator available in GeoCore, with links to the underlying groundhog API reference.
origin: geocore
source_url: https://github.com/utkarsh-1912/geocore/blob/main/electron-app/src/config/geotechnicalModules.js
license: GPL-3.0
author: Utkarsh Gupta
attribution: GeoCore documentation by Utkarsh Gupta, licensed under the GNU GPL v3.
groundhog_version: 0.15.0
edited_by_geocore: false
geocore_available: true
---

GeoCore's calculation browser groups its calculators into the categories below. This list is generated from the application's module configuration: 204 calculators, of which 204 link to the groundhog function or class they run.

## General and utility functions


### Soil profiles and grids

- <a id="soilprofile"></a>**SoilProfile** (`SoilProfile`) — [groundhog `SoilProfile`](/docs/groundhog/api/general/soilprofile#soilprofile)
- <a id="calculationgrid"></a>**CalculationGrid** (`CalculationGrid`) — [groundhog `CalculationGrid`](/docs/groundhog/api/general/soilprofile#calculationgrid)

### Plotting

- <a id="logplot"></a>**LogPlot** (`LogPlot`) — [groundhog `LogPlot`](/docs/groundhog/api/general/plotting#logplot)
- <a id="logplotmatplotlib"></a>**LogPlotMatplotlib** (`LogPlotMatplotlib`) — [groundhog `LogPlotMatplotlib`](/docs/groundhog/api/general/plotting#logplotmatplotlib)
- <a id="plot_with_log"></a>**plot_with_log()** (`plot_with_log`) — [groundhog `plot_with_log`](/docs/groundhog/api/general/plotting#plot_with_log)

### AGS Conversion

- <a id="agsconverter"></a>**AGSConverter** (`AGSConverter`) — [groundhog `AGSConverter`](/docs/groundhog/api/general/agsconversion#agsconverter)
- <a id="agsconverter_convert_ags_group"></a>**convert_ags_group()** (`AGSConverter_convert_ags_group`) — [groundhog `AGSConverter.convert_ags_group`](/docs/groundhog/api/general/agsconversion#agsconverter-convert_ags_group)

### Parameter Mapping

- <a id="get_projected_point"></a>**get_projected_point()** (`get_projected_point`) — [groundhog `get_projected_point`](/docs/groundhog/api/general/parameter_mapping#get_projected_point)
- <a id="latlon_distance"></a>**latlon_distance()** (`latlon_distance`) — [groundhog `latlon_distance`](/docs/groundhog/api/general/parameter_mapping#latlon_distance)
- <a id="map_depth_properties"></a>**map_depth_properties()** (`map_depth_properties`) — [groundhog `map_depth_properties`](/docs/groundhog/api/general/parameter_mapping#map_depth_properties)
- <a id="offsets_api"></a>**offsets()** (`offsets_api`) — [groundhog `offsets`](/docs/groundhog/api/general/parameter_mapping#offsets)
- <a id="merge_two_dicts"></a>**merge_two_dicts()** (`merge_two_dicts`) — [groundhog `merge_two_dicts`](/docs/groundhog/api/general/parameter_mapping#merge_two_dicts)
- <a id="reverse_dict"></a>**reverse_dict()** (`reverse_dict`) — [groundhog `reverse_dict`](/docs/groundhog/api/general/parameter_mapping#reverse_dict)

### Validation

- <a id="check_layer_overlap"></a>**check_layer_overlap()** (`check_layer_overlap`) — [groundhog `check_layer_overlap`](/docs/groundhog/api/general/validation#check_layer_overlap)
- <a id="validate_boolean"></a>**validate_boolean()** (`validate_boolean`) — [groundhog `validate_boolean`](/docs/groundhog/api/general/validation#validate_boolean)
- <a id="validate_float"></a>**validate_float()** (`validate_float`) — [groundhog `validate_float`](/docs/groundhog/api/general/validation#validate_float)
- <a id="validate_integer"></a>**validate_integer()** (`validate_integer`) — [groundhog `validate_integer`](/docs/groundhog/api/general/validation#validate_integer)
- <a id="validate_list"></a>**validate_list()** (`validate_list`) — [groundhog `validate_list`](/docs/groundhog/api/general/validation#validate_list)
- <a id="validate_string"></a>**validate_string()** (`validate_string`) — [groundhog `validate_string`](/docs/groundhog/api/general/validation#validate_string)

## Site investigation


### Classification: Phase relations

- <a id="bulkunitweight"></a>**bulkunitweight()** (`bulkunitweight`) — [groundhog `bulkunitweight`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#bulkunitweight)
- <a id="bulkunitweight_dryunitweight"></a>**bulkunitweight_dryunitweight()** (`bulkunitweight_dryunitweight`) — [groundhog `bulkunitweight_dryunitweight`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#bulkunitweight_dryunitweight)
- <a id="density_unitweight"></a>**density_unitweight()** (`density_unitweight`) — [groundhog `density_unitweight`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#density_unitweight)
- <a id="dryunitweight_watercontent"></a>**dryunitweight_watercontent()** (`dryunitweight_watercontent`) — [groundhog `dryunitweight_watercontent`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#dryunitweight_watercontent)
- <a id="porosity_voidratio"></a>**porosity_voidratio()** (`porosity_voidratio`) — [groundhog `porosity_voidratio`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#porosity_voidratio)
- <a id="relative_density"></a>**relative_density()** (`relative_density`) — [groundhog `relative_density`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#relative_density)
- <a id="saturation_watercontent"></a>**saturation_watercontent()** (`saturation_watercontent`) — [groundhog `saturation_watercontent`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#saturation_watercontent)
- <a id="unitweight_density"></a>**unitweight_density()** (`unitweight_density`) — [groundhog `unitweight_density`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#unitweight_density)
- <a id="unitweight_watercontent_saturated"></a>**unitweight_watercontent_saturated()** (`unitweight_watercontent_saturated`) — [groundhog `unitweight_watercontent_saturated`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#unitweight_watercontent_saturated)
- <a id="voidratio_bulkunitweight"></a>**voidratio_bulkunitweight()** (`voidratio_bulkunitweight`) — [groundhog `voidratio_bulkunitweight`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#voidratio_bulkunitweight)
- <a id="voidratio_drydensity"></a>**voidratio_drydensity()** (`voidratio_drydensity`) — [groundhog `voidratio_drydensity`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#voidratio_drydensity)
- <a id="voidratio_porosity"></a>**voidratio_porosity()** (`voidratio_porosity`) — [groundhog `voidratio_porosity`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#voidratio_porosity)
- <a id="voidratio_watercontent"></a>**voidratio_watercontent()** (`voidratio_watercontent`) — [groundhog `voidratio_watercontent`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#voidratio_watercontent)
- <a id="watercontent_voidratio"></a>**watercontent_voidratio()** (`watercontent_voidratio`) — [groundhog `watercontent_voidratio`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#watercontent_voidratio)

### Classification: Classes & categories

- <a id="relativedensity_categories"></a>**relativedensity_categories()** (`relativedensity_categories`) — [groundhog `relativedensity_categories`](/docs/groundhog/api/siteinvestigation/classification/categories#relativedensity_categories)
- <a id="samplequality_voidratio_lunne"></a>**samplequality_voidratio_lunne()** (`samplequality_voidratio_lunne`) — [groundhog `samplequality_voidratio_lunne`](/docs/groundhog/api/siteinvestigation/classification/categories#samplequality_voidratio_lunne)
- <a id="su_categories"></a>**su_categories()** (`su_categories`) — [groundhog `su_categories`](/docs/groundhog/api/siteinvestigation/classification/categories#su_categories)
- <a id="uscs_categories"></a>**uscs_categories()** (`uscs_categories`) — [groundhog `uscs_categories`](/docs/groundhog/api/siteinvestigation/classification/categories#uscs_categories)

### Correlations: All soil types

- <a id="acousticimpedance_bulkunitweight_chen"></a>**acousticimpedance_bulkunitweight_chen()** (`acousticimpedance_bulkunitweight_chen`) — [groundhog `acousticimpedance_bulkunitweight_chen`](/docs/groundhog/api/siteinvestigation/correlations/general#acousticimpedance_bulkunitweight_chen)
- <a id="k0_frictionangle_mesri"></a>**k0_frictionangle_mesri()** (`k0_frictionangle_mesri`) — [groundhog `k0_frictionangle_mesri`](/docs/groundhog/api/siteinvestigation/correlations/general#k0_frictionangle_mesri)
- <a id="shearwavevelocity_compressionindex_cha"></a>**shearwavevelocity_compressionindex_cha()** (`shearwavevelocity_compressionindex_cha`) — [groundhog `shearwavevelocity_compressionindex_cha`](/docs/groundhog/api/siteinvestigation/correlations/general#shearwavevelocity_compressionindex_cha)

### Correlations: Cohesive soils

- <a id="compressionindex_watercontent_koppula"></a>**compressionindex_watercontent_koppula()** (`compressionindex_watercontent_koppula`) — [groundhog `compressionindex_watercontent_koppula`](/docs/groundhog/api/siteinvestigation/correlations/cohesive#compressionindex_watercontent_koppula)
- <a id="cv_liquidlimit_usnavy"></a>**cv_liquidlimit_usnavy()** (`cv_liquidlimit_usnavy`) — [groundhog `cv_liquidlimit_usnavy`](/docs/groundhog/api/siteinvestigation/correlations/cohesive#cv_liquidlimit_usnavy)
- <a id="frictionangle_plasticityindex"></a>**frictionangle_plasticityindex()** (`frictionangle_plasticityindex`) — [groundhog `frictionangle_plasticityindex`](/docs/groundhog/api/siteinvestigation/correlations/cohesive#frictionangle_plasticityindex)
- <a id="gmax_plasticityocr_andersen"></a>**gmax_plasticityocr_andersen()** (`gmax_plasticityocr_andersen`) — [groundhog `gmax_plasticityocr_andersen`](/docs/groundhog/api/siteinvestigation/correlations/cohesive#gmax_plasticityocr_andersen)
- <a id="k0_plasticity_kenney"></a>**k0_plasticity_kenney()** (`k0_plasticity_kenney`) — [groundhog `k0_plasticity_kenney`](/docs/groundhog/api/siteinvestigation/correlations/cohesive#k0_plasticity_kenney)

### Correlations: Cohesionless soils

- <a id="gmax_sand_hardinblack"></a>**gmax_sand_hardinblack()** (`gmax_sand_hardinblack`) — [groundhog `gmax_sand_hardinblack`](/docs/groundhog/api/siteinvestigation/correlations/cohesionless#gmax_sand_hardinblack)
- <a id="hssmall_parameters_sand"></a>**hssmall_parameters_sand()** (`hssmall_parameters_sand`) — [groundhog `hssmall_parameters_sand`](/docs/groundhog/api/siteinvestigation/correlations/cohesionless#hssmall_parameters_sand)
- <a id="permeability_d10_hazen"></a>**permeability_d10_hazen()** (`permeability_d10_hazen`) — [groundhog `permeability_d10_hazen`](/docs/groundhog/api/siteinvestigation/correlations/cohesionless#permeability_d10_hazen)
- <a id="stress_dilatancy_bolton"></a>**stress_dilatancy_bolton()** (`stress_dilatancy_bolton`) — [groundhog `stress_dilatancy_bolton`](/docs/groundhog/api/siteinvestigation/correlations/cohesionless#stress_dilatancy_bolton)

### In-situ: PCPT processing class

- <a id="pcptprocessing"></a>**PCPTProcessing** (`PCPTProcessing`) — [groundhog `PCPTProcessing`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_processing#pcptprocessing)

### In-situ: PCPT functions

- <a id="behaviourindex_pcpt_nonnormalised"></a>**behaviourindex_pcpt_nonnormalised()** (`behaviourindex_pcpt_nonnormalised`) — [groundhog `behaviourindex_pcpt_nonnormalised`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#behaviourindex_pcpt_nonnormalised)
- <a id="behaviourindex_pcpt_robertsonwride"></a>**behaviourindex_pcpt_robertsonwride()** (`behaviourindex_pcpt_robertsonwride`) — [groundhog `behaviourindex_pcpt_robertsonwride`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#behaviourindex_pcpt_robertsonwride)
- <a id="clippingdepths_qc1n_tianlehane"></a>**clippingdepths_qc1N_tianlehane()** (`clippingdepths_qc1N_tianlehane`) — [groundhog `clippingdepths_qc1N_tianlehane`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#clippingdepths_qc1n_tianlehane)
- <a id="coneresistance_ocsand_baldi"></a>**coneresistance_ocsand_baldi()** (`coneresistance_ocsand_baldi`) — [groundhog `coneresistance_ocsand_baldi`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#coneresistance_ocsand_baldi)
- <a id="constrainedmodulus_pcpt_robertson"></a>**constrainedmodulus_pcpt_robertson()** (`constrainedmodulus_pcpt_robertson`) — [groundhog `constrainedmodulus_pcpt_robertson`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#constrainedmodulus_pcpt_robertson)
- <a id="dissipation_test_teh"></a>**dissipation_test_teh()** (`dissipation_test_teh`) — [groundhog `dissipation_test_teh`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#dissipation_test_teh)
- <a id="drainedsecantmodulus_sand_bellotti"></a>**drainedsecantmodulus_sand_bellotti()** (`drainedsecantmodulus_sand_bellotti`) — [groundhog `drainedsecantmodulus_sand_bellotti`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#drainedsecantmodulus_sand_bellotti)
- <a id="frictionangle_overburden_kleven"></a>**frictionangle_overburden_kleven()** (`frictionangle_overburden_kleven`) — [groundhog `frictionangle_overburden_kleven`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#frictionangle_overburden_kleven)
- <a id="frictionangle_sand_kulhawymayne"></a>**frictionangle_sand_kulhawymayne()** (`frictionangle_sand_kulhawymayne`) — [groundhog `frictionangle_sand_kulhawymayne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#frictionangle_sand_kulhawymayne)
- <a id="gmax_clay_maynerix"></a>**gmax_clay_maynerix()** (`gmax_clay_maynerix`) — [groundhog `gmax_clay_maynerix`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#gmax_clay_maynerix)
- <a id="gmax_cpt_puechen"></a>**gmax_cpt_puechen()** (`gmax_cpt_puechen`) — [groundhog `gmax_cpt_puechen`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#gmax_cpt_puechen)
- <a id="gmax_sand_rixstokoe"></a>**gmax_sand_rixstokoe()** (`gmax_sand_rixstokoe`) — [groundhog `gmax_sand_rixstokoe`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#gmax_sand_rixstokoe)
- <a id="gmax_voidratio_maynerix"></a>**gmax_voidratio_maynerix()** (`gmax_voidratio_maynerix`) — [groundhog `gmax_voidratio_maynerix`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#gmax_voidratio_maynerix)
- <a id="ic_soilclass_robertson"></a>**ic_soilclass_robertson()** (`ic_soilclass_robertson`) — [groundhog `ic_soilclass_robertson`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#ic_soilclass_robertson)
- <a id="k0_sand_mayne"></a>**k0_sand_mayne()** (`k0_sand_mayne`) — [groundhog `k0_sand_mayne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#k0_sand_mayne)
- <a id="ocr_cpt_lunne"></a>**ocr_cpt_lunne()** (`ocr_cpt_lunne`) — [groundhog `ocr_cpt_lunne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#ocr_cpt_lunne)
- <a id="pcpt_normalisations"></a>**pcpt_normalisations()** (`pcpt_normalisations`) — [groundhog `pcpt_normalisations`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#pcpt_normalisations)
- <a id="relativedensity_ncsand_baldi"></a>**relativedensity_ncsand_baldi()** (`relativedensity_ncsand_baldi`) — [groundhog `relativedensity_ncsand_baldi`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#relativedensity_ncsand_baldi)
- <a id="relativedensity_ocsand_baldi"></a>**relativedensity_ocsand_baldi()** (`relativedensity_ocsand_baldi`) — [groundhog `relativedensity_ocsand_baldi`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#relativedensity_ocsand_baldi)
- <a id="relativedensity_sand_jamiolkowski"></a>**relativedensity_sand_jamiolkowski()** (`relativedensity_sand_jamiolkowski`) — [groundhog `relativedensity_sand_jamiolkowski`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#relativedensity_sand_jamiolkowski)
- <a id="sensitivity_frictionratio_lunne"></a>**sensitivity_frictionratio_lunne()** (`sensitivity_frictionratio_lunne`) — [groundhog `sensitivity_frictionratio_lunne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#sensitivity_frictionratio_lunne)
- <a id="soilclass_robertson"></a>**soilclass_robertson()** (`soilclass_robertson`) — [groundhog `soilclass_robertson`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#soilclass_robertson)
- <a id="soiltype_vs_longodonohue"></a>**soiltype_vs_longodonohue()** (`soiltype_vs_longodonohue`) — [groundhog `soiltype_vs_longodonohue`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#soiltype_vs_longodonohue)
- <a id="undrainedshearstrength_clay_radlunne"></a>**undrainedshearstrength_clay_radlunne()** (`undrainedshearstrength_clay_radlunne`) — [groundhog `undrainedshearstrength_clay_radlunne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#undrainedshearstrength_clay_radlunne)
- <a id="unitweight_mayne"></a>**unitweight_mayne()** (`unitweight_mayne`) — [groundhog `unitweight_mayne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#unitweight_mayne)
- <a id="vs_cpt_andrus"></a>**vs_cpt_andrus()** (`vs_cpt_andrus`) — [groundhog `vs_cpt_andrus`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_andrus)
- <a id="vs_cpt_hegazymayne"></a>**vs_cpt_hegazymayne()** (`vs_cpt_hegazymayne`) — [groundhog `vs_cpt_hegazymayne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_hegazymayne)
- <a id="vs_cpt_longdonohue"></a>**vs_cpt_longdonohue()** (`vs_cpt_longdonohue`) — [groundhog `vs_cpt_longdonohue`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_longdonohue)
- <a id="vs_cpt_mcgannetal"></a>**vs_cpt_mcgannetal()** (`vs_cpt_mcgannetal`) — [groundhog `vs_cpt_mcgannetal`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_mcgannetal)
- <a id="vs_cpt_tonniandsimonini"></a>**vs_cpt_tonniandsimonini()** (`vs_cpt_tonniandsimonini`) — [groundhog `vs_cpt_tonniandsimonini`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_tonniandsimonini)
- <a id="vs_cpt_wrideetal"></a>**vs_cpt_wrideetal()** (`vs_cpt_wrideetal`) — [groundhog `vs_cpt_wrideetal`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_wrideetal)
- <a id="vs_cptd50_karrayetal"></a>**vs_cptd50_karrayetal()** (`vs_cptd50_karrayetal`) — [groundhog `vs_cptd50_karrayetal`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cptd50_karrayetal)
- <a id="vs_ic_robertsoncabal"></a>**vs_ic_robertsoncabal()** (`vs_ic_robertsoncabal`) — [groundhog `vs_ic_robertsoncabal`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_ic_robertsoncabal)
- <a id="vs_stressdependent_stuyts"></a>**vs_stressdependent_stuyts()** (`vs_stressdependent_stuyts`) — [groundhog `vs_stressdependent_stuyts`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_stressdependent_stuyts)

### In-situ: SPT processing class

- <a id="sptprocessing"></a>**SPTProcessing** (`SPTProcessing`) — [groundhog `SPTProcessing`](/docs/groundhog/api/siteinvestigation/insitutests/spt_processing#sptprocessing)

### In-situ: SPT corrections & correlations

- <a id="frictionangle_spt_pht"></a>**frictionangle_spt_PHT()** (`frictionangle_spt_PHT`) — [groundhog `frictionangle_spt_PHT`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#frictionangle_spt_pht)
- <a id="frictionangle_spt_kulhawymayne"></a>**frictionangle_spt_kulhawymayne()** (`frictionangle_spt_kulhawymayne`) — [groundhog `frictionangle_spt_kulhawymayne`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#frictionangle_spt_kulhawymayne)
- <a id="overburdencorrection_spt_iso"></a>**overburdencorrection_spt_ISO()** (`overburdencorrection_spt_ISO`) — [groundhog `overburdencorrection_spt_ISO`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#overburdencorrection_spt_iso)
- <a id="overburdencorrection_spt_liaowhitman"></a>**overburdencorrection_spt_liaowhitman()** (`overburdencorrection_spt_liaowhitman`) — [groundhog `overburdencorrection_spt_liaowhitman`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#overburdencorrection_spt_liaowhitman)
- <a id="relativedensity_spt_kulhawymayne"></a>**relativedensity_spt_kulhawymayne()** (`relativedensity_spt_kulhawymayne`) — [groundhog `relativedensity_spt_kulhawymayne`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#relativedensity_spt_kulhawymayne)
- <a id="relativedensityclass_spt_terzaghipeck"></a>**relativedensityclass_spt_terzaghipeck()** (`relativedensityclass_spt_terzaghipeck`) — [groundhog `relativedensityclass_spt_terzaghipeck`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#relativedensityclass_spt_terzaghipeck)
- <a id="spt_n60_correction"></a>**spt_N60_correction()** (`spt_N60_correction`) — [groundhog `spt_N60_correction`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#spt_n60_correction)
- <a id="undrainedshearstrength_spt_salgado"></a>**undrainedshearstrength_spt_salgado()** (`undrainedshearstrength_spt_salgado`) — [groundhog `undrainedshearstrength_spt_salgado`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#undrainedshearstrength_spt_salgado)
- <a id="undrainedshearstrengthclass_spt_terzaghipeck"></a>**undrainedshearstrengthclass_spt_terzaghipeck()** (`undrainedshearstrengthclass_spt_terzaghipeck`) — [groundhog `undrainedshearstrengthclass_spt_terzaghipeck`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#undrainedshearstrengthclass_spt_terzaghipeck)
- <a id="youngsmodulus_spt_aashto"></a>**youngsmodulus_spt_AASHTO()** (`youngsmodulus_spt_AASHTO`) — [groundhog `youngsmodulus_spt_AASHTO`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#youngsmodulus_spt_aashto)

### Laboratory: Sample preparation

- <a id="undercompaction_cohesionless_ladd"></a>**undercompaction_cohesionless_ladd()** (`undercompaction_cohesionless_ladd`) — [groundhog `undercompaction_cohesionless_ladd`](/docs/groundhog/api/siteinvestigation/labtesting/samplepreparation#undercompaction_cohesionless_ladd)

### Laboratory: Index tests

- <a id="plasticitychart"></a>**PlasticityChart** (`PlasticityChart`) — [groundhog `PlasticityChart`](/docs/groundhog/api/siteinvestigation/labtesting/indextests#plasticitychart)
- <a id="psdchart"></a>**PSDChart** (`PSDChart`) — [groundhog `PSDChart`](/docs/groundhog/api/siteinvestigation/labtesting/indextests#psdchart)

### Laboratory: Compressibility

- <a id="logtimemethod"></a>**logtimemethod()** (`logtimemethod`) — [groundhog `logtimemethod`](/docs/groundhog/api/siteinvestigation/labtesting/compressibility#logtimemethod)
- <a id="roottimemethod"></a>**roottimemethod()** (`roottimemethod`) — [groundhog `roottimemethod`](/docs/groundhog/api/siteinvestigation/labtesting/compressibility#roottimemethod)

## Pile calculations


### Unit skin friction

- <a id="api_unit_shaft_friction_clay"></a>**API (Clay)** (`API_unit_shaft_friction_clay`) — [groundhog `API_unit_shaft_friction_clay`](/docs/groundhog/api/deepfoundations/axialcapacity/skinfriction#api_unit_shaft_friction_clay)
- <a id="api_unit_shaft_friction_sand_rp2geo"></a>**API RP2 GEO (Sand)** (`API_unit_shaft_friction_sand_rp2geo`) — [groundhog `API_unit_shaft_friction_sand_rp2geo`](/docs/groundhog/api/deepfoundations/axialcapacity/skinfriction#api_unit_shaft_friction_sand_rp2geo)
- <a id="unitskinfriction_clay_almhamre"></a>**Alm & Hamre (Clay)** (`unitskinfriction_clay_almhamre`) — [groundhog `unitskinfriction_clay_almhamre`](/docs/groundhog/api/deepfoundations/axialcapacity/skinfriction#unitskinfriction_clay_almhamre)
- <a id="unitskinfriction_sand_almhamre"></a>**Alm & Hamre (Sand)** (`unitskinfriction_sand_almhamre`) — [groundhog `unitskinfriction_sand_almhamre`](/docs/groundhog/api/deepfoundations/axialcapacity/skinfriction#unitskinfriction_sand_almhamre)

### Unit end bearing

- <a id="api_unit_end_bearing_clay"></a>**API (Clay)** (`API_unit_end_bearing_clay`) — [groundhog `API_unit_end_bearing_clay`](/docs/groundhog/api/deepfoundations/axialcapacity/endbearing#api_unit_end_bearing_clay)
- <a id="api_unit_end_bearing_sand_rp2geo"></a>**API RP2 GEO (Sand)** (`API_unit_end_bearing_sand_rp2geo`) — [groundhog `API_unit_end_bearing_sand_rp2geo`](/docs/groundhog/api/deepfoundations/axialcapacity/endbearing#api_unit_end_bearing_sand_rp2geo)
- <a id="unitendbearing_clay_almhamre"></a>**Alm & Hamre (Clay)** (`unitendbearing_clay_almhamre`) — [groundhog `unitendbearing_clay_almhamre`](/docs/groundhog/api/deepfoundations/axialcapacity/endbearing#unitendbearing_clay_almhamre)
- <a id="unitendbearing_sand_almhamre"></a>**Alm & Hamre (Sand)** (`unitendbearing_sand_almhamre`) — [groundhog `unitendbearing_sand_almhamre`](/docs/groundhog/api/deepfoundations/axialcapacity/endbearing#unitendbearing_sand_almhamre)

### Axial capacity calculations

- <a id="axcapcalculation"></a>**Axial Capacity (AxCap)** (`AxCapCalculation`) — [groundhog `AxCapCalculation`](/docs/groundhog/api/deepfoundations/axialcapacity/axcap#axcapcalculation)

### De Beer and Eurocode 7 calculations

- <a id="debeercalculation"></a>**De Beer Calculation** (`DeBeerCalculation`) — [groundhog `DeBeerCalculation`](/docs/groundhog/api/deepfoundations/axialcapacity/debeer#debeercalculation)

### Koppejan pile resistance

- <a id="koppejancalculation"></a>**Koppejan Calculation** (`KoppejanCalculation`) — [groundhog `KoppejanCalculation`](/docs/groundhog/api/deepfoundations/axialcapacity/koppejan#koppejancalculation)

### LCPC pile resistance

- <a id="lcpc_calculation"></a>**LCPC Calculation** (`LCPC_Calculation`) — [groundhog `LCPCAxcapCalculation`](/docs/groundhog/api/deepfoundations/axialcapacity/lcpc#lcpcaxcapcalculation)

### Pile settlement

- <a id="pilesettlementcurves"></a>**Pile Settlement Curves** (`PileSettlementCurves`) — [groundhog `pile_settlement_curves`](/docs/groundhog/api/deepfoundations/axialresponse/settlement#pile_settlement_curves)

### Pile lateral behaviour

- <a id="pilegroupeffect_reesevanimpe"></a>**Pile Group Effect (Reese & Van Impe)** (`pilegroupeffect_reesevanimpe`) — [groundhog `pilegroupeffect_reesevanimpe`](/docs/groundhog/api/deepfoundations/lateralresponse/lateral#pilegroupeffect_reesevanimpe)
- <a id="reinforced_circularsection_inertia"></a>**Reinforced Circular Section Inertia** (`reinforced_circularsection_inertia`) — [groundhog `reinforced_circularsection_inertia`](/docs/groundhog/api/deepfoundations/lateralresponse/lateral#reinforced_circularsection_inertia)

### Cavity expansion methods

- <a id="expansion_cylinder_tresca"></a>**Cylinder Expansion (Tresca)** (`expansion_cylinder_tresca`) — [groundhog `expansion_cylinder_tresca`](/docs/groundhog/api/deepfoundations/boreholestability/cavityexpansion#expansion_cylinder_tresca)
- <a id="expansion_tresca_thicksphere"></a>**Thick Sphere Expansion (Tresca)** (`expansion_tresca_thicksphere`) — [groundhog `expansion_tresca_thicksphere`](/docs/groundhog/api/deepfoundations/boreholestability/cavityexpansion#expansion_tresca_thicksphere)
- <a id="stress_cylinder_elastic_isotropic"></a>**Elastic Cylinder Stress (Isotropic)** (`stress_cylinder_elastic_isotropic`) — [groundhog `stress_cylinder_elastic_isotropic`](/docs/groundhog/api/deepfoundations/boreholestability/cavityexpansion#stress_cylinder_elastic_isotropic)

### Negative skin friction

- <a id="negativeskinfriction_pilegroup_zeevaertdebeer"></a>**Zeevaert & De Beer (Pile Group)** (`negativeskinfriction_pilegroup_zeevaertdebeer`) — [groundhog `negativeskinfriction_pilegroup_zeevaertdebeer`](/docs/groundhog/api/deepfoundations/axialcapacity/negativeskinfriction#negativeskinfriction_pilegroup_zeevaertdebeer)

### Pile testing functionality

- <a id="piletest_chinkondler"></a>**Chin-Kondler Extrapolation** (`piletest_chinkondler`) — [groundhog `piletest_chinkondler`](/docs/groundhog/api/deepfoundations/axialcapacity/piletesting#piletest_chinkondler)

## Shallow foundations


### Stress distributions

- <a id="stresses_circle"></a>**Circular Footing Stress** (`stresses_circle`) — [groundhog `stresses_circle`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_circle)
- <a id="stresses_lineload_retainingwall"></a>**Line Load Stress (Retaining Wall)** (`stresses_lineload_retainingwall`) — [groundhog `stresses_lineload_retainingwall`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_lineload_retainingwall)
- <a id="stresses_pointload"></a>**Point Load Stress** (`stresses_pointload`) — [groundhog `stresses_pointload`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_pointload)
- <a id="stresses_rectangle"></a>**Rectangular Footing Stress** (`stresses_rectangle`) — [groundhog `stresses_rectangle`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_rectangle)
- <a id="stresses_stripload"></a>**Strip Load Stress** (`stresses_stripload`) — [groundhog `stresses_stripload`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_stripload)
- <a id="stresses_stripload_retainingwall"></a>**Strip Load Stress (Retaining Wall)** (`stresses_stripload_retainingwall`) — [groundhog `stresses_stripload_retainingwall`](/docs/groundhog/api/shallowfoundations/stressdistribution#stresses_stripload_retainingwall)

### Shallow foundation capacity

- <a id="shallow_foundation_capacity_undrained"></a>**Undrained Capacity Analysis** (`shallow_foundation_capacity_undrained`) — [groundhog `ShallowFoundationCapacityUndrained`](/docs/groundhog/api/shallowfoundations/capacity#shallowfoundationcapacityundrained)
- <a id="shallow_foundation_capacity_drained"></a>**Drained Capacity Analysis** (`shallow_foundation_capacity_drained`) — [groundhog `ShallowFoundationCapacityDrained`](/docs/groundhog/api/shallowfoundations/capacity#shallowfoundationcapacitydrained)
- <a id="effectivearea_circle_api"></a>**Effective Area (Circular)** (`effectivearea_circle_api`) — [groundhog `effectivearea_circle_api`](/docs/groundhog/api/shallowfoundations/capacity#effectivearea_circle_api)
- <a id="effectivearea_rectangle_api"></a>**Effective Area (Rectangular)** (`effectivearea_rectangle_api`) — [groundhog `effectivearea_rectangle_api`](/docs/groundhog/api/shallowfoundations/capacity#effectivearea_rectangle_api)
- <a id="envelope_drained_api"></a>**Envelope (Drained)** (`envelope_drained_api`) — [groundhog `envelope_drained_api`](/docs/groundhog/api/shallowfoundations/capacity#envelope_drained_api)
- <a id="envelope_undrained_api"></a>**Envelope (Undrained)** (`envelope_undrained_api`) — [groundhog `envelope_undrained_api`](/docs/groundhog/api/shallowfoundations/capacity#envelope_undrained_api)
- <a id="failuremechanism_prandtl"></a>**Failure Mechanism (Prandtl)** (`failuremechanism_prandtl`) — [groundhog `failuremechanism_prandtl`](/docs/groundhog/api/shallowfoundations/capacity#failuremechanism_prandtl)
- <a id="ngamma_frictionangle_davisbooker"></a>**N_gamma (Davis & Booker)** (`ngamma_frictionangle_davisbooker`) — [groundhog `ngamma_frictionangle_davisbooker`](/docs/groundhog/api/shallowfoundations/capacity#ngamma_frictionangle_davisbooker)
- <a id="ngamma_frictionangle_meyerhof"></a>**N_gamma (Meyerhof)** (`ngamma_frictionangle_meyerhof`) — [groundhog `ngamma_frictionangle_meyerhof`](/docs/groundhog/api/shallowfoundations/capacity#ngamma_frictionangle_meyerhof)
- <a id="ngamma_frictionangle_vesic"></a>**N_gamma (Vesic)** (`ngamma_frictionangle_vesic`) — [groundhog `ngamma_frictionangle_vesic`](/docs/groundhog/api/shallowfoundations/capacity#ngamma_frictionangle_vesic)
- <a id="nq_frictionangle_sand"></a>**N_q (Sand)** (`nq_frictionangle_sand`) — [groundhog `nq_frictionangle_sand`](/docs/groundhog/api/shallowfoundations/capacity#nq_frictionangle_sand)
- <a id="slidingcapacity_drained_api"></a>**Sliding Capacity (Drained)** (`slidingcapacity_drained_api`) — [groundhog `slidingcapacity_drained_api`](/docs/groundhog/api/shallowfoundations/capacity#slidingcapacity_drained_api)
- <a id="slidingcapacity_undrained_api"></a>**Sliding Capacity (Undrained)** (`slidingcapacity_undrained_api`) — [groundhog `slidingcapacity_undrained_api`](/docs/groundhog/api/shallowfoundations/capacity#slidingcapacity_undrained_api)
- <a id="verticalcapacity_drained_api"></a>**Vertical Capacity (Drained)** (`verticalcapacity_drained_api`) — [groundhog `verticalcapacity_drained_api`](/docs/groundhog/api/shallowfoundations/capacity#verticalcapacity_drained_api)
- <a id="verticalcapacity_undrained_api"></a>**Vertical Capacity (Undrained)** (`verticalcapacity_undrained_api`) — [groundhog `verticalcapacity_undrained_api`](/docs/groundhog/api/shallowfoundations/capacity#verticalcapacity_undrained_api)

### Settlement

- <a id="settlement_calculation"></a>**Settlement Calculation (Profile)** (`settlement_calculation`) — [groundhog `SettlementCalculation`](/docs/groundhog/api/shallowfoundations/settlement#settlementcalculation)
- <a id="consolidationsettlement_mv"></a>**Consolidation Settlement (mv)** (`consolidationsettlement_mv`) — [groundhog `consolidationsettlement_mv`](/docs/groundhog/api/shallowfoundations/settlement#consolidationsettlement_mv)
- <a id="primaryconsolidationsettlement_nc"></a>**Primary Settlement (NC)** (`primaryconsolidationsettlement_nc`) — [groundhog `primaryconsolidationsettlement_nc`](/docs/groundhog/api/shallowfoundations/settlement#primaryconsolidationsettlement_nc)
- <a id="primaryconsolidationsettlement_oc"></a>**Primary Settlement (OC)** (`primaryconsolidationsettlement_oc`) — [groundhog `primaryconsolidationsettlement_oc`](/docs/groundhog/api/shallowfoundations/settlement#primaryconsolidationsettlement_oc)

## Consolidation functions


### Pumping tests

- <a id="hydraulicconductivity_unconfinedaquifer"></a>**Hydraulic Conductivity (Unconfined Aquifer)** (`hydraulicconductivity_unconfinedaquifer`) — [groundhog `hydraulicconductivity_unconfinedaquifer`](/docs/groundhog/api/consolidation/groundwaterflow/pumpingtests#hydraulicconductivity_unconfinedaquifer)

### One-dimensional consolidation

- <a id="consolidation_calculation"></a>**Consolidation Calculation (Numerical)** (`consolidation_calculation`) — [groundhog `ConsolidationCalculation`](/docs/groundhog/api/consolidation/dissipation/onedimensionalconsolidation#consolidationcalculation)
- <a id="consolidation_degree"></a>**Degree of Consolidation** (`consolidation_degree`) — [groundhog `consolidation_degree`](/docs/groundhog/api/consolidation/dissipation/onedimensionalconsolidation#consolidation_degree)
- <a id="pore_pressure_fourier"></a>**Excess Pore Pressure (Fourier)** (`pore_pressure_fourier`) — [groundhog `pore_pressure_fourier`](/docs/groundhog/api/consolidation/dissipation/onedimensionalconsolidation#pore_pressure_fourier)

## Excavations


### Earth pressure coefficients

- <a id="earthpressurecoefficients_frictionangle"></a>**Earth Pressure (Friction Angle)** (`earthpressurecoefficients_frictionangle`) — [groundhog `earthpressurecoefficients_frictionangle`](/docs/groundhog/api/excavations/basic#earthpressurecoefficients_frictionangle)
- <a id="earthpressurecoefficients_poncelet"></a>**Earth Pressure (Poncelet)** (`earthpressurecoefficients_poncelet`) — [groundhog `earthpressurecoefficients_poncelet`](/docs/groundhog/api/excavations/basic#earthpressurecoefficients_poncelet)
- <a id="earthpressurecoefficients_rankine"></a>**Earth Pressure (Rankine)** (`earthpressurecoefficients_rankine`) — [groundhog `earthpressurecoefficients_rankine`](/docs/groundhog/api/excavations/basic#earthpressurecoefficients_rankine)

### Soilmix

- <a id="bendingstiffness_soilmix_method1"></a>**Bending Stiffness (Method 1)** (`bendingstiffness_soilmix_method1`) — [groundhog `bendingstiffness_soilmix_method1`](/docs/groundhog/api/excavations/soilmix#bendingstiffness_soilmix_method1)
- <a id="bendingstiffness_soilmix_method2"></a>**Bending Stiffness (Method 2)** (`bendingstiffness_soilmix_method2`) — [groundhog `bendingstiffness_soilmix_method2`](/docs/groundhog/api/excavations/soilmix#bendingstiffness_soilmix_method2)

## Soil dynamics


### Liquefaction

- <a id="cyclicstressratio_moss"></a>**Moss (2006) Cyclic Stress Ratio** (`cyclicstressratio_moss`) — [groundhog `cyclicstressratio_moss`](/docs/groundhog/api/soildynamics/liquefaction#cyclicstressratio_moss)
- <a id="cyclicstressratio_youd"></a>**Youd (2001) Cyclic Stress Ratio** (`cyclicstressratio_youd`) — [groundhog `cyclicstressratio_youd`](/docs/groundhog/api/soildynamics/liquefaction#cyclicstressratio_youd)
- <a id="liquefaction_robertsonfear"></a>**Robertson & Fear (1995) Liquefaction** (`liquefaction_robertsonfear`) — [groundhog `liquefaction_robertsonfear`](/docs/groundhog/api/soildynamics/liquefaction#liquefaction_robertsonfear)
- <a id="liquefactionprobability_moss"></a>**Moss (2006) Liquefaction Probability** (`liquefactionprobability_moss`) — [groundhog `liquefactionprobability_moss`](/docs/groundhog/api/soildynamics/liquefaction#liquefactionprobability_moss)
- <a id="liquefactionprobability_saye"></a>**Saye (2017) Liquefaction Probability** (`liquefactionprobability_saye`) — [groundhog `liquefactionprobability_saye`](/docs/groundhog/api/soildynamics/liquefaction#liquefactionprobability_saye)

### Cyclic behaviour

- <a id="cycliccontours_dssclay_andersen"></a>**AC Cyclic Contours (DSS Clay)** (`cycliccontours_dssclay_andersen`) — [groundhog `cycliccontours_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#cycliccontours_dssclay_andersen)
- <a id="cycliccontours_triaxialclay_andersen"></a>**AC Cyclic Contours (Triaxial Clay)** (`cycliccontours_triaxialclay_andersen`) — [groundhog `cycliccontours_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#cycliccontours_triaxialclay_andersen)
- <a id="cyclicstrength_dsssand_relativedensity"></a>**AC Cyclic Strength (DSS Sand - Dr)** (`cyclicstrength_dsssand_relativedensity`) — [groundhog `cyclicstrength_dsssand_relativedensity`](/docs/groundhog/api/soildynamics/cyclicbehaviour#cyclicstrength_dsssand_relativedensity)
- <a id="cyclicstrength_dsssand_watercontent"></a>**AC Cyclic Strength (DSS Sand - w)** (`cyclicstrength_dsssand_watercontent`) — [groundhog `cyclicstrength_dsssand_watercontent`](/docs/groundhog/api/soildynamics/cyclicbehaviour#cyclicstrength_dsssand_watercontent)
- <a id="plotcycliccontours_dssclay_andersen"></a>**Plot Cyclic Contours (DSS Clay)** (`plotcycliccontours_dssclay_andersen`) — [groundhog `plotcycliccontours_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotcycliccontours_dssclay_andersen)
- <a id="plotcycliccontours_triaxialclay_andersen"></a>**Plot Cyclic Contours (Triaxial Clay)** (`plotcycliccontours_triaxialclay_andersen`) — [groundhog `plotcycliccontours_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotcycliccontours_triaxialclay_andersen)
- <a id="plotporepressureaccumulation_dssclay_andersen"></a>**Plot Pore Pressure (DSS Clay)** (`plotporepressureaccumulation_dssclay_andersen`) — [groundhog `plotporepressureaccumulation_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotporepressureaccumulation_dssclay_andersen)
- <a id="plotporepressureaccumulation_dsssand_andersen"></a>**Plot Pore Pressure (DSS Sand)** (`plotporepressureaccumulation_dsssand_andersen`) — [groundhog `plotporepressureaccumulation_dsssand_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotporepressureaccumulation_dsssand_andersen)
- <a id="plotporepressureaccumulation_triaxialclay_andersen"></a>**Plot Pore Pressure (Triaxial Clay)** (`plotporepressureaccumulation_triaxialclay_andersen`) — [groundhog `plotporepressureaccumulation_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotporepressureaccumulation_triaxialclay_andersen)
- <a id="plotstrainaccumulation_dssclay_andersen"></a>**Plot Strain Accum. (DSS Clay)** (`plotstrainaccumulation_dssclay_andersen`) — [groundhog `plotstrainaccumulation_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotstrainaccumulation_dssclay_andersen)
- <a id="plotstrainaccumulation_dsssand_andersen"></a>**Plot Strain Accum. (DSS Sand)** (`plotstrainaccumulation_dsssand_andersen`) — [groundhog `plotstrainaccumulation_dsssand_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotstrainaccumulation_dsssand_andersen)
- <a id="plotstrainaccumulation_triaxialclay_andersen"></a>**Plot Strain Accum. (Triaxial Clay)** (`plotstrainaccumulation_triaxialclay_andersen`) — [groundhog `plotstrainaccumulation_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotstrainaccumulation_triaxialclay_andersen)
- <a id="porepressureaccumulation_dssclay_andersen"></a>**Pore Pressure Accum. (DSS Clay)** (`porepressureaccumulation_dssclay_andersen`) — [groundhog `porepressureaccumulation_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#porepressureaccumulation_dssclay_andersen)
- <a id="porepressureaccumulation_triaxialclay_andersen"></a>**Pore Pressure Accum. (Triaxial Clay)** (`porepressureaccumulation_triaxialclay_andersen`) — [groundhog `porepressureaccumulation_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#porepressureaccumulation_triaxialclay_andersen)
- <a id="strainaccumulation_dssclay_andersen"></a>**Strain Accum. (DSS Clay)** (`strainaccumulation_dssclay_andersen`) — [groundhog `strainaccumulation_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#strainaccumulation_dssclay_andersen)
- <a id="strainaccumulation_dsssand_andersen"></a>**Strain Accum. (DSS Sand)** (`strainaccumulation_dsssand_andersen`) — [groundhog `strainaccumulation_dsssand_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#strainaccumulation_dsssand_andersen)
- <a id="strainaccumulation_triaxialclay_andersen"></a>**Strain Accum. (Triaxial Clay)** (`strainaccumulation_triaxialclay_andersen`) — [groundhog `strainaccumulation_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#strainaccumulation_triaxialclay_andersen)

### Dynamic soil property correlations

- <a id="dampingratio_sandgravel_seed"></a>**Seed & Idriss (1970) Damping Ratio** (`dampingratio_sandgravel_seed`) — [groundhog `dampingratio_sandgravel_seed`](/docs/groundhog/api/soildynamics/soilproperties#dampingratio_sandgravel_seed)
- <a id="gmax_shearwavevelocity"></a>**Gmax from Shear Wave Velocity** (`gmax_shearwavevelocity`) — [groundhog `gmax_shearwavevelocity`](/docs/groundhog/api/soildynamics/soilproperties#gmax_shearwavevelocity)
- <a id="modulusreduction_darendeli"></a>**Darendeli (2001) Modulus Reduction** (`modulusreduction_darendeli`) — [groundhog `modulusreduction_darendeli`](/docs/groundhog/api/soildynamics/soilproperties#modulusreduction_darendeli)
- <a id="modulusreduction_plasticity_ishibashi"></a>**Ishibashi & Zhang (1993) Modulus Reduction** (`modulusreduction_plasticity_ishibashi`) — [groundhog `modulusreduction_plasticity_ishibashi`](/docs/groundhog/api/soildynamics/soilproperties#modulusreduction_plasticity_ishibashi)

### CPT Liquefaction

- <a id="qtn_cs_boulanger_idriss_2014"></a>**B&I (2014) Qtn,cs** (`Qtn_cs_boulanger_idriss_2014`) — [groundhog `Qtn_cs_boulanger_idriss_2014`](/docs/groundhog/api/soildynamics/cptliquefaction#qtn_cs_boulanger_idriss_2014)
- <a id="qtn_cs_idriss_boulanger_2008"></a>**I&B (2008) Qtn,cs** (`Qtn_cs_idriss_boulanger_2008`) — [groundhog `Qtn_cs_idriss_boulanger_2008`](/docs/groundhog/api/soildynamics/cptliquefaction#qtn_cs_idriss_boulanger_2008)
- <a id="qtn_cs_robertson_cabal_2022"></a>**R&C (2022) Qtn,cs** (`Qtn_cs_robertson_cabal_2022`) — [groundhog `Qtn_cs_robertson_cabal_2022`](/docs/groundhog/api/soildynamics/cptliquefaction#qtn_cs_robertson_cabal_2022)
- <a id="qtn_cs_robertson_wride_1998"></a>**R&W (1998) Qtn,cs** (`Qtn_cs_robertson_wride_1998`) — [groundhog `Qtn_cs_robertson_wride_1998`](/docs/groundhog/api/soildynamics/cptliquefaction#qtn_cs_robertson_wride_1998)
- <a id="crr_boulanger_idriss_2014"></a>**B&I (2014) CRR** (`crr_boulanger_idriss_2014`) — [groundhog `crr_boulanger_idriss_2014`](/docs/groundhog/api/soildynamics/cptliquefaction#crr_boulanger_idriss_2014)
- <a id="crr_idriss_boulanger_2008"></a>**I&B (2008) CRR** (`crr_idriss_boulanger_2008`) — [groundhog `crr_idriss_boulanger_2008`](/docs/groundhog/api/soildynamics/cptliquefaction#crr_idriss_boulanger_2008)
- <a id="crr_robertson_cabal_2022"></a>**R&C (2022) CRR** (`crr_robertson_cabal_2022`) — [groundhog `crr_robertson_cabal_2022`](/docs/groundhog/api/soildynamics/cptliquefaction#crr_robertson_cabal_2022)
- <a id="crr_robertson_wride_1998"></a>**R&W (1998) CRR** (`crr_robertson_wride_1998`) — [groundhog `crr_robertson_wride_1998`](/docs/groundhog/api/soildynamics/cptliquefaction#crr_robertson_wride_1998)
- <a id="csr_boulanger_idriss_2014"></a>**B&I (2014) CSR** (`csr_boulanger_idriss_2014`) — [groundhog `csr_boulanger_idriss_2014`](/docs/groundhog/api/soildynamics/cptliquefaction#csr_boulanger_idriss_2014)
- <a id="csr_idriss_boulanger_2008"></a>**I&B (2008) CSR** (`csr_idriss_boulanger_2008`) — [groundhog `csr_idriss_boulanger_2008`](/docs/groundhog/api/soildynamics/cptliquefaction#csr_idriss_boulanger_2008)
- <a id="csr_robertson_cabal_2022"></a>**R&C (2022) CSR** (`csr_robertson_cabal_2022`) — [groundhog `csr_robertson_cabal_2022`](/docs/groundhog/api/soildynamics/cptliquefaction#csr_robertson_cabal_2022)
- <a id="csr_robertson_wride_1998"></a>**R&W (1998) CSR** (`csr_robertson_wride_1998`) — [groundhog `csr_robertson_wride_1998`](/docs/groundhog/api/soildynamics/cptliquefaction#csr_robertson_wride_1998)
- <a id="fos_liquefaction"></a>**Factor of Safety (Liquefaction)** (`fos_liquefaction`) — [groundhog `fos_liquefaction`](/docs/groundhog/api/soildynamics/cptliquefaction#fos_liquefaction)
- <a id="liquefaction_strains_zhang"></a>**Zhang (2002) Liquefaction Strains** (`liquefaction_strains_zhang`) — [groundhog `liquefaction_strains_zhang`](/docs/groundhog/api/soildynamics/cptliquefaction#liquefaction_strains_zhang)

## EuroCode7


### Parameter selection

- <a id="parameter_selection_constant_value"></a>**constant_value()** (`parameter_selection_constant_value`) — [groundhog `constant_value`](/docs/groundhog/api/standards/eurocode7/parameter_selection#constant_value)
- <a id="parameter_selection_linear_trend"></a>**linear_trend()** (`parameter_selection_linear_trend`) — [groundhog `linear_trend`](/docs/groundhog/api/standards/eurocode7/parameter_selection#linear_trend)

### Partial factor selection

- <a id="eurocode7_factors"></a>**Eurocode7_factoring_STR_GEO** (`eurocode7_factors`) — [groundhog `Eurocode7_factoring_STR_GEO`](/docs/groundhog/api/standards/eurocode7/factors#eurocode7_factoring_str_geo)

## Constitutive models


### Cohesionless materials

- <a id="hardening_soil_drained_triaxial"></a>**Hardening Soil (Drained Triaxial)** (`hardening_soil_drained_triaxial`) — [groundhog `HardeningSoil`](/docs/groundhog/api/constitutivemodels/cohesionless#hardeningsoil)

## Pipelines and cables


### Pipeline and cable stability

- <a id="contactwidth"></a>**Contact Width** (`contactwidth`) — [groundhog `contactwidth`](/docs/groundhog/api/pipelinescables/stability/penetration#contactwidth)
- <a id="embedment_drained"></a>**Embedment (Drained)** (`embedment_drained`) — [groundhog `embedment_drained`](/docs/groundhog/api/pipelinescables/stability/penetration#embedment_drained)
- <a id="embedment_undrained_method1"></a>**Embedment (Undrained Method 1)** (`embedment_undrained_method1`) — [groundhog `embedment_undrained_method1`](/docs/groundhog/api/pipelinescables/stability/penetration#embedment_undrained_method1)
- <a id="embedment_undrained_method2"></a>**Embedment (Undrained Method 2)** (`embedment_undrained_method2`) — [groundhog `embedment_undrained_method2`](/docs/groundhog/api/pipelinescables/stability/penetration#embedment_undrained_method2)
- <a id="lay_touchdown_factor"></a>**Lay Touchdown Factor** (`lay_touchdown_factor`) — [groundhog `lay_touchdown_factor`](/docs/groundhog/api/pipelinescables/stability/penetration#lay_touchdown_factor)
- <a id="penetratedarea"></a>**Penetrated Area** (`penetratedarea`) — [groundhog `penetratedarea`](/docs/groundhog/api/pipelinescables/stability/penetration#penetratedarea)
