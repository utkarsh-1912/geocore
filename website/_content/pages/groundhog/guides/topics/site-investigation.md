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

This page follows the structure of the upstream groundhog documentation for *Site investigation*. For each function it gives the method summary and key formulas from the groundhog docstrings, with a link to the full API reference.

## Soil classification

Upstream page: [Soil classification](https://groundhog.readthedocs.io/en/main/site_investigation/classification_toplevel.html)

### Phase relations

Upstream page: [Phase relations](https://groundhog.readthedocs.io/en/main/site_investigation/phaserelations.html)

Module [`groundhog.siteinvestigation.classification.phaserelations`](/docs/groundhog/api/siteinvestigation/classification/phaserelations). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

#### voidratio_porosity

Function [`voidratio_porosity`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#voidratio_porosity).

Converts a void ratio into a porosity

$$
e = \frac{V_{voids}}{V_{solids}}
$$

$$
n = \frac{V_{voids}}{V_{total}}
$$

*1 more formula in the full reference.*

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

#### porosity_voidratio

Function [`porosity_voidratio`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#porosity_voidratio).

Calculates the porosity of sample from the void ratio

$$
n = \frac{e}{e+1}
$$

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

#### saturation_watercontent

Function [`saturation_watercontent`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#saturation_watercontent).

Calculates the saturation of a sample from the water content, the specific gravity and the void ratio

$$
S = \frac{V_{water}}{V_{voids}} = \frac{w \cdot G_s}{e}
$$

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

#### bulkunitweight

Function [`bulkunitweight`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#bulkunitweight).

Calculates the bulk unit weight from specific gravity, void ratio and saturation

$$
\gamma = \frac{W}{V} = \left( \frac{G_s + S \cdot e}{1+e} \right) \cdot \gamma_w
$$

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

#### dryunitweight_watercontent

Function [`dryunitweight_watercontent`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#dryunitweight_watercontent).

Calculates the dry unit weight of the sample from the water content and the bulk unit weight

$$
\gamma_d = \frac{W_s}{V} = \left( \frac{G_s}{1+e} \right) \cdot \gamma_w = \frac{\gamma}{1 + w}
$$

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

#### voidratio_drydensity

Function [`voidratio_drydensity`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#voidratio_drydensity).

Calculates void ratio when the specific gravity and the dry density are known

$$
e = G_s \cdot \frac{\rho_w}{\rho_d} - 1
$$

*Reference:* Budhu (2011) Introduction to soil mechanics and foundations.

#### bulkunitweight_dryunitweight

Function [`bulkunitweight_dryunitweight`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#bulkunitweight_dryunitweight).

Calculates the bulk unit weight from the dry unit weight and the water content

$$
\gamma = (1+w) \cdot \gamma_d
$$

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

#### relative_density

Function [`relative_density`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#relative_density).

Calculates the relative density for a cohesionless sample from the measured void ratio, comparing it to the void ratio at minimum and maximum density.

$$
D_r = \frac{e - e_{min}}{e_{max} - e_{min}}
$$

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

#### voidratio_bulkunitweight

Function [`voidratio_bulkunitweight`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#voidratio_bulkunitweight).

Calculates the void ratio from the bulk unit weight for a soil with varying saturation.

$$
\gamma = \left( \frac{G_s + S e}{1 + e} \right) \gamma_w
$$

$$
\implies e = \frac{\gamma_w G_s - \gamma}{\gamma - S \gamma_w}
$$

*1 more formula in the full reference.*

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

#### unitweight_watercontent_saturated

Function [`unitweight_watercontent_saturated`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#unitweight_watercontent_saturated).

Calculates the bulk unit weight from water content for a saturated soil.

$$
S \cdot e = w \cdot G_s
$$

$$
\gamma = \left( \frac{G_s + S \cdot e}{1 + e} \right) \cdot \gamma_w
$$

*1 more formula in the full reference.*

*Reference:* UGent In-house practice

#### density_unitweight

Function [`density_unitweight`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#density_unitweight).

Converts unit weight (in kN/m3) to density (in kg/m3)

$$
\rho = \frac{\gamma}{g}
$$

*Reference:* Budhu (2011) Introduction to soil mechanics and foundations.

#### unitweight_density

Function [`unitweight_density`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#unitweight_density).

Converts density (in kg/m3) to unit weight (kN/m3)

$$
\gamma = \rho \cdot g
$$

*Reference:* Budhu (2011) Introduction to soil mechanics and foundations.

#### watercontent_voidratio

Function [`watercontent_voidratio`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#watercontent_voidratio).

Calculates the water content of a sample from it's void ratio.

$$
w = \frac{S \cdot e}{G_s}
$$

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

#### voidratio_watercontent

Function [`voidratio_watercontent`](/docs/groundhog/api/siteinvestigation/classification/phaserelations#voidratio_watercontent).

Calculates the void ratio of a sample from the water content.

$$
e = \frac{w \cdot G_s}{S}
$$

*Reference:* Budhu (2011). Soil mechanics and foundation engineering

### Soil classes and categories

Upstream page: [Soil classes and categories](https://groundhog.readthedocs.io/en/main/site_investigation/categories.html)

Module [`groundhog.siteinvestigation.classification.categories`](/docs/groundhog/api/siteinvestigation/classification/categories). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

#### relativedensity_categories

Function [`relativedensity_categories`](/docs/groundhog/api/siteinvestigation/classification/categories#relativedensity_categories).

Categorizes relative densities according to the following definition:

$$
D_r = \frac{e - e_{min}}{e_{max} - e_{min}}
$$

*Reference:* API RP2 GEO

#### su_categories

Function [`su_categories`](/docs/groundhog/api/siteinvestigation/classification/categories#su_categories).

Classifies undrained shear strength in a number of categories.

*Reference:* BS 5930:2015, ASTM D-2488

#### uscs_categories

Function [`uscs_categories`](/docs/groundhog/api/siteinvestigation/classification/categories#uscs_categories).

Provides the verbose description for soil type codes according to USCS.

*Reference:* USCS

#### samplequality_voidratio_lunne

Function [`samplequality_voidratio_lunne`](/docs/groundhog/api/siteinvestigation/classification/categories#samplequality_voidratio_lunne).

Determines the sample quality for clays based on the change in void ratio when consolidating the sample back to the initial vertical effective stress.

*Reference:* Lunne, T., et al. "Effects of sample disturbance on consolidation behaviour of soft marine Norwegian clays." Geotechnical and geophysical site characterization: proceedings of the third international conference on site characterization ISC. Vol. 3. 2008.

## Soil parameter correlations

Upstream page: [Soil parameter correlations](https://groundhog.readthedocs.io/en/main/site_investigation/correlations_toplevel.html)

### All soil types

Upstream page: [All soil types](https://groundhog.readthedocs.io/en/main/site_investigation/correlations_general.html)

Module [`groundhog.siteinvestigation.correlations.general`](/docs/groundhog/api/siteinvestigation/correlations/general). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

#### acousticimpedance_bulkunitweight_chen

Function [`acousticimpedance_bulkunitweight_chen`](/docs/groundhog/api/siteinvestigation/correlations/general#acousticimpedance_bulkunitweight_chen).

Several authors have researched the correlation between porosity and acoustic impedance.

$$
I =1.315 \cdot 10^{-4} \cdot n^4 - 3.776 \cdot 10^{-2} \cdot n^3 + 4.201 \cdot n^2 - 2.450 \cdot 10^2 \cdot n + 8.603 \cdot 10^3
$$

$$
e = \frac{\gamma_w G_s - \gamma}{\gamma - S \gamma_w}
$$

*2 more formulas in the full reference.*

*Reference:* Chen et al (2021). Machine Learning Based Digital Integration of Geotechnical and Ultra-High Frequency Geophysical Data for Offshore Site Characterizations. Journal of Geotechnical and Geoenvironmental Engineering.

#### shearwavevelocity_compressionindex_cha

Function [`shearwavevelocity_compressionindex_cha`](/docs/groundhog/api/siteinvestigation/correlations/general#shearwavevelocity_compressionindex_cha).

Shear wave velocity is dependent on the stiffness of the soil skeleton which is in turn affected by the compression index C_c.

$$
V_s = \sqrt{\frac{G}{\rho}} = \alpha \left( \frac{\sigma_{\perp}^{\prime} + \sigma_{\parallel}^{\prime}}{2 \ \text{kPa}} \right)^{\beta}
$$

$$
\alpha = 13.5 (\text{m/s}) \cdot C_c^{-0.63}
$$

*1 more formula in the full reference.*

*Reference:* Cha et al (2014). Small-Strain Stiffness, Shear-Wave Velocity and Soil Compressibilitys. Journal of Geotechnical and Geoenvironmental Engineering.

#### k0_frictionangle_mesri

Function [`k0_frictionangle_mesri`](/docs/groundhog/api/siteinvestigation/correlations/general#k0_frictionangle_mesri).

Calculates the coefficient of lateral earthpressure at rest for normally and overconsolidated sand and clay.

$$
K_0 = \left( 1 - \sin \varphi_{cv}^{\prime} \right) \text{OCR}^{\sin \varphi_{cv}^{\prime}}
$$

*Reference:* Mesri and Hayat (1993) The coefficient of earth pressure at rest. Canadian Geotechnical Journal. 30(4), 647-666

### Cohesive soils

Upstream page: [Cohesive soils](https://groundhog.readthedocs.io/en/main/site_investigation/cohesive.html)

Module [`groundhog.siteinvestigation.correlations.cohesive`](/docs/groundhog/api/siteinvestigation/correlations/cohesive). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

#### compressionindex_watercontent_koppula

Function [`compressionindex_watercontent_koppula`](/docs/groundhog/api/siteinvestigation/correlations/cohesive#compressionindex_watercontent_koppula).

Based on an evaluation of the compression index of clays and eight other soil mechanics parameters, Koppula (1981) concluded that the best fit was obtain using a direct relation with natural water content.

$$
C_c = w_n
$$

$$
C_c / C_r = 5 \ \text{to} \ 10
$$

*Reference:* Koppula SD (1981) Statistical evaluation of compression index. Geotech Test J ASTM 4(2):68–73

#### frictionangle_plasticityindex

Function [`frictionangle_plasticityindex`](/docs/groundhog/api/siteinvestigation/correlations/cohesive#frictionangle_plasticityindex).

Based on a dataset of soft to stiff clays, a correlation between plasticity index and drained friction angle of clay is proposed.

*Reference:* Terzaghi, K., Peck, R. B., & Mesri, G. (1996). Soil mechanics in engineering practice. John Wiley & Sons.

#### cv_liquidlimit_usnavy

Function [`cv_liquidlimit_usnavy`](/docs/groundhog/api/siteinvestigation/correlations/cohesive#cv_liquidlimit_usnavy).

Calculates an estimate of the coefficient of consolidation based on the liquid limit of a clay.

*Reference:* U.S. Navy (1982) Soil mechanics – design manual 7.1, Department of the Navy, Naval Facilities Engineering Command, U.S. Government Printing Office, Washington, DC

#### gmax_plasticityocr_andersen

Function [`gmax_plasticityocr_andersen`](/docs/groundhog/api/siteinvestigation/correlations/cohesive#gmax_plasticityocr_andersen).

Calculates the small-strain shear modulus for cohesive soils based on plasticity index, effective overburden pressure and OCR.

$$
\frac{G_{max}}{\sigma_{ref}^{\prime}} = \left( 30 + \frac{75}{\frac{I_p}{100} + 0.03} \right) \cdot OCR^{0.5}
$$

$$
\sigma_{ref}^{\prime} = P_a \cdot \left( \sigma_{0}^{\prime}  / P_a \right)^{0.9}
$$

*Reference:* Andersen KH. Cyclic soil parameters for offshore foundation design. The Third ISSMGE McClelland Lecture. In: Meyer V, editor. Proc. Int. Symp. Frontiers in offshore geotechnics, ISFOG 2015. London: Taylor and Francis; 2015. 5–82.

#### k0_plasticity_kenney

Function [`k0_plasticity_kenney`](/docs/groundhog/api/siteinvestigation/correlations/cohesive#k0_plasticity_kenney).

Calculates the coefficient of lateral earthpressure at rest for normally and overconsolidated clay.

$$
K_{0,NC} = 0.19 + 0.233 \log_{10} I_p
$$

$$
I_p = -281 \log_{10} \left( 1.85 \lambda \right)
$$

*Reference:* Alpan (1967) THE EMPIRICAL EVALUATION OF THE COEFFICIENT K0 AND K0R. Soils and Foundations. Volume 7, Issue 1

### Cohesionless soils

Upstream page: [Cohesionless soils](https://groundhog.readthedocs.io/en/main/site_investigation/cohesionless.html)

Module [`groundhog.siteinvestigation.correlations.cohesionless`](/docs/groundhog/api/siteinvestigation/correlations/cohesionless). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

#### gmax_sand_hardinblack

Function [`gmax_sand_hardinblack`](/docs/groundhog/api/siteinvestigation/correlations/cohesionless#gmax_sand_hardinblack).

Calculates the small-strain shear modulus of sand based on the correlation proposed with initial void ratio and stress level suggested by Hardin and Black (1968).

$$
G_{max} = \frac{B p_{ref}^{\prime}}{0.3 + 0.7 e_0^2} \sqrt{\frac{p^{\prime}}{p_{ref}^{\prime}}}
$$

*Reference:* Hardin, B.O. and Black W.L. 1968. Vibration modulus of normally consolidated clay Journal of Soil Mechanics and Foundations Div, 94(SM2), 353-369.

#### permeability_d10_hazen

Function [`permeability_d10_hazen`](/docs/groundhog/api/siteinvestigation/correlations/cohesionless#permeability_d10_hazen).

Calculates the permeability of a granular soil based on its grain size.

$$
k = C_{10} \cdot D_{10}^2
$$

*Reference:* Terzaghi, K., Peck, R. B., & Mesri, G. (1996). Soil mechanics in engineering practice. John Wiley & Sons.

#### hssmall_parameters_sand

Function [`hssmall_parameters_sand`](/docs/groundhog/api/siteinvestigation/correlations/cohesionless#hssmall_parameters_sand).

Calculates the constitutive parameters for the HS Small model in PLAXIS as a function of relative density.

$$
\gamma_{unsat} = 15 + 4 \cdot \frac{D_r}{100}
$$

$$
\gamma_{sat} = 19 + 1.6 \cdot \frac{D_r}{100}
$$

*9 more formulas in the full reference.*

*Reference:* Brinkgreve, R. B. J., Engin, E., & Engin, H. K. (2010). Validation of empirical formulas to derive model parameters for sands. Numerical methods in geotechnical engineering, 137- 142.

#### stress_dilatancy_bolton

Function [`stress_dilatancy_bolton`](/docs/groundhog/api/siteinvestigation/correlations/cohesionless#stress_dilatancy_bolton).

Cohesionless soils with sufficiently high relative density will tend to dilate but dilation can be suppressed by the stress on the sample.

$$
I_R = D_r \left( Q - \ln p^{\prime} \right) - R
$$

$$
\varphi_{max}^{\prime} - \varphi_{crit}^{\prime} = 0.8 \phi_{max} = 5 I_R \ \ \text{plane strain}
$$

*2 more formulas in the full reference.*

*Reference:* Bolton, M. D. "The strength and dilatancy of sands." Geotechnique 36.1 (1986): 65-78.

## In-situ tests

Upstream page: [In-situ tests](https://groundhog.readthedocs.io/en/main/site_investigation/insitutests_toplevel.html)

### PCPT processing class

Upstream page: [PCPT processing class](https://groundhog.readthedocs.io/en/main/site_investigation/pcpt_class.html)

#### PCPTProcessing

Class [`PCPTProcessing`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_processing#pcptprocessing).

The PCPTProcessing class implements methods for reading, processing and presentation of PCPT data.

### PCPT functions

Upstream page: [PCPT functions](https://groundhog.readthedocs.io/en/main/site_investigation/pcpt_functions.html)

Module [`groundhog.siteinvestigation.insitutests.pcpt_correlations`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

#### pcpt_normalisations

Function [`pcpt_normalisations`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#pcpt_normalisations).

Carried out the necessary normalisation and correction on PCPT data to allow calculation of derived parameters and soil type classification.

$$
q_c = q_c^* + d \cdot a \cdot \gamma_w
$$

$$
q_t = q_c + u_2 \cdot (1 - a)
$$

*10 more formulas in the full reference.*

*Reference:* Lunne, T., Robertson, P.K., Powell, J.J.M., 1997. Cone penetration testing in geotechnical practice. E & FN Spon.

#### soilclass_robertson

Function [`soilclass_robertson`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#soilclass_robertson).

Provides soil type classification according to the soil behaviour type index by Robertson and Wride.

*Reference:* Fugro guidance on PCPT interpretation

#### ic_soilclass_robertson

Function [`ic_soilclass_robertson`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#ic_soilclass_robertson).

Provides soil type classification according to the soil behaviour type index by Robertson and Wride.

*Reference:* Fugro guidance on PCPT interpretation

#### behaviourindex_pcpt_robertsonwride

Function [`behaviourindex_pcpt_robertsonwride`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#behaviourindex_pcpt_robertsonwride).

Calculates the soil behaviour index according to Robertson and Wride (1998).

$$
Cn = \min(1.7, \left(\frac{P_a}{\sigma_{vo}^{\prime}}\right)^n)
Q_{tn} = \frac{q_t - \sigma_{vo}}{P_a} \cdot Cn
\\
n = 0.381 \cdot I_c + 0.05 \cdot \frac{\sigma_{vo}^{\prime}}{P_a} - 0.15 \ \text{where} \ n \leq 1
\\
I_c = \sqrt{ \left( 3.47 - \log_{10} Q_{tn} \right)^2 + \left( \log_{10} F_r + 1.22 \right)^2 }
$$

*Reference:* Fugro guidance on PCPT interpretation

#### gmax_sand_rixstokoe

Function [`gmax_sand_rixstokoe`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#gmax_sand_rixstokoe).

Calculates the small-strain shear modulus for uncemented silica sand based on cone resistance and vertical effective stress.

$$
G_{max} = 1634 \cdot (q_c)^{0.25} \cdot (\sigma_{vo}^{\prime})^{0.375}
$$

*Reference:* Rix, G.J. and Stokoe, K.H. (II) (1991), “Correlation of Initial Tangent Modulus and Cone Penetration Resistance”, in Huang, A.B. (Ed.), Calibration Chamber Testing: Proceedings of the First International Symposium on Calibration Chamber Testing ISOCCTI, Potsdam, New York, 28-29 June 1991, Elsevier Science Publishing Company, New York, pp. 351-362.

#### gmax_clay_maynerix

Function [`gmax_clay_maynerix`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#gmax_clay_maynerix).

Mayne and Rix (1993) determined a relationship between small-strain shear modulus and cone tip resistance by studying 481 data sets from 31 sites all over the world.

$$
G_{max} = 2.78 \cdot q_c^{1.335}
$$

*Reference:* Mayne, P.W. and Rix, G.J. (1993), “Gmax-qc Relationships for Clays”, Geotechnical Testing Journal, Vol. 16, No. 1, pp. 54-60.

#### relativedensity_ncsand_baldi

Function [`relativedensity_ncsand_baldi`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#relativedensity_ncsand_baldi).

Calculates the relative density for normally consolidated sand based on calibration chamber tests on silica sand.

$$
D_r = \frac{1}{2.41} \cdot \ln \left[ \frac{q_c}{157 \cdot \left( \sigma_{vo}^{\prime} \right)^{0.55} } \right]
$$

*Reference:* Baldi et al 1986.

#### relativedensity_ocsand_baldi

Function [`relativedensity_ocsand_baldi`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#relativedensity_ocsand_baldi).

Calculates the relative density for overconsolidated sand based on calibration chamber tests on silica sand.

$$
D_r = \frac{1}{2.61} \cdot \ln \left[ \frac{q_c}{181 \cdot \left( \sigma_{m}^{\prime} \right)^{0.55} } \right]
$$

$$
\sigma_{m}^{\prime} = \frac{\sigma_{vo}^{\prime} + 2 \cdot K_o \ cdot \sigma_{h0}^{\prime}}{3}
$$

*Reference:* Baldi et al 1986.

#### coneresistance_ocsand_baldi

Function [`coneresistance_ocsand_baldi`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#coneresistance_ocsand_baldi).

Calculates the cone resistance for a given relative density for overconsolidated sand based on calibration chamber tests on silica sand.

$$
D_r = \frac{1}{2.61} \cdot \ln \left[ \frac{q_c}{181 \cdot \left( \sigma_{m}^{\prime} \right)^{0.55} } \right]
$$

$$
\sigma_{m}^{\prime} = \frac{\sigma_{vo}^{\prime} + 2 \cdot K_o \cdot \sigma_{m}^{\prime}}{3}
$$

*Reference:* Baldi et al 1986.

#### relativedensity_sand_jamiolkowski

Function [`relativedensity_sand_jamiolkowski`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#relativedensity_sand_jamiolkowski).

Jamiolkowksi et al formulated a correlation for the relative density of dry sand based on calibration chamber tests.

$$
D_{r,dry} = \frac{1}{2.96} \cdot \ln \left[ \frac{q_c / P_a}{24.94 \cdot \left( \frac{\sigma_{m}^{\prime}}{P_a} \right)^{0.46} } \right]
$$

$$
D_{r,sat} = \left( 1 + \frac{-1.87 + 2.32 \cdot \ln \left[ \frac{q_c}{\sqrt{P_a + \sigma_{vo}^{\prime}}} \right] }{100} \right) \cdot D_{r,dry}
$$

*Reference:* Jamiolkowski, M., Lo Presti, D.C.F. and Manassero, M. (2003), "Evaluation of Relative Density and Shear Strength of Sands from CPT and DMT", in Germaine, J.T., Sheahan, T.C. and Whitman, R.V. (Eds.), Soil Behavior and Soft Ground Construction: Proceedings of the Symposium, October 5-6, 2001, Cambridge, Massachusetts, Geotechnical Special Publication, No. 119, American Society of Civil Engineers, Reston, pp. 201-238.

#### frictionangle_sand_kulhawymayne

Function [`frictionangle_sand_kulhawymayne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#frictionangle_sand_kulhawymayne).

Determines the friction angle for sand based on calibration chamber tests.

$$
\varphi^{\prime} = 17.6 + 11.0 \cdot \log_{10} \left[  \frac{q_t / P_a}{ \sqrt{\sigma_{vo}^{\prime} / P_a}} \right]
$$

*Reference:* Kulhawy, F.H. and Mayne, P.H. (1990), “Manual on Estimating Soil Properties for Foundation Design”, Electric Power Research Institute EPRI, Palo Alto, EPRI Report, EL-6800.

#### undrainedshearstrength_clay_radlunne

Function [`undrainedshearstrength_clay_radlunne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#undrainedshearstrength_clay_radlunne).

Calculates the undrained shear strength of clay from net cone tip resistance.

$$
S_u = \frac{q_{net}}{N_k}
$$

*Reference:* Rad, N.S. and Lunne, T. (1988), "Direct Correlations between Piezocone Test Results and Undrained Shear Strength of Clay", in De Ruiter, J. (Ed.), Penetration Testing 1988: Proceedings of the First International Symposium on Penetration Testing, ISOPT-1, Orlando, 20-24 March 1988, Vol. 2, A.A. Balkema, Rotterdam, pp. 911-917.

#### frictionangle_overburden_kleven

Function [`frictionangle_overburden_kleven`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#frictionangle_overburden_kleven).

This function calculates the friction angle according to the chart proposed by Kleven (1986).

*Reference:* Lunne, T., Robertson, P.K., Powell, J.J.M. (1997). Cone penetration testing in geotechnical practice.  SPON press

#### ocr_cpt_lunne

Function [`ocr_cpt_lunne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#ocr_cpt_lunne).

Calculates the overconsolidation ratio (OCR) for clay based on normalised CPT properties.

*Reference:* Lunne, T., Robertson, P.K., Powell, J.J.M., 1997. Cone penetration testing in geotechnical practice. E & FN Spon.

#### sensitivity_frictionratio_lunne

Function [`sensitivity_frictionratio_lunne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#sensitivity_frictionratio_lunne).

Calculates the sensitivity of clay from the friction ratio according to Rad and Lunne (1986).

*Reference:* Lunne, T., Robertson, P.K., Powell, J.J.M., 1997. Cone penetration testing in geotechnical practice. E & FN Spon.

#### unitweight_mayne

Function [`unitweight_mayne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#unitweight_mayne).

Estimates the total unit weight for sand, clay and silt from CPT measurements.

$$
\gamma = 1.95 \cdot \gamma_w \cdot \left( \frac{\sigma_{vo}^{\prime}}{P_a} \right)^{0.06} \cdot \left( \frac{f_t}{P_a} \right)^{0.06}
$$

*Reference:* P.W. Mayne ; J. Peuchen ; D. Bouwmeester (2010). Soil unit weight estimation from CPTs - 2nd International Symposium on Cone Penetration Testing, Huntington Beach, CA, USA. Volume 2&3: Technical Papers, Session 2: Interpretation, Paper No. 5

#### vs_ic_robertsoncabal

Function [`vs_ic_robertsoncabal`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_ic_robertsoncabal).

Calculates shear wave velocity based on a correlation with total cone resistance and soil behaviour type index.

$$
V_s = \left[ \alpha_{vs} (q_t - \sigma_{vo}) / P_a \right]^{0.5}
$$

$$
\alpha_{vs} = 10^{0.55 \cdot I_c + 1.68}
$$

*2 more formulas in the full reference.*

*Reference:* Robertson, P.K. and Cabal, K.L. (2015). Guide to Cone Penetration Testing for Geotechnical Engineering. 6th edition. Gregg Drilling & Testing, Inc.

#### k0_sand_mayne

Function [`k0_sand_mayne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#k0_sand_mayne).

Calculates the lateral coefficient of earth pressure at rest based on calibration chamber tests on clean sands.

$$
K_0 = 0.192 \cdot \left( \frac{q_t}{P_a} \right)^{0.22} \cdot \left( \frac{P_a}{\sigma_{vo}^{\prime}} \right)^{0.31} \cdot \text{OCR}^{0.27}
$$

$$
\text{The maximum value for } K_0 \text{ can be obtained as}:
$$

*3 more formulas in the full reference.*

*Reference:* Mayne (2007) NCHRP SYNTHESIS 368. Cone Penetration Testing. A Synthesis of Highway Practice.

#### gmax_cpt_puechen

Function [`gmax_cpt_puechen`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#gmax_cpt_puechen).

Calculates the small-strain modulus based on CPT data.

$$
G_{max} = b \cdot \left( 1 + 4 \cdot B_q \right) \cdot 1.634 \cdot q_c^{0.25} \cdot \sigma_{vo}^{\prime \ 0.375}
$$

*Reference:* Puechen et al (2020). Characteristic values for geotechnical design of offshore monopiles in sandy soils - Case study. ISFOG2020

#### behaviourindex_pcpt_nonnormalised

Function [`behaviourindex_pcpt_nonnormalised`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#behaviourindex_pcpt_nonnormalised).

Calculates the non-normalised soil behaviour type index.

$$
I_{SBT} = \sqrt{ \left( 3.47 - \log ( q_c / P_a ) \right)^2 + \left( \log R_f + 1.22 \right)^2}
$$

*Reference:* Fugro guidance on PCPT interpretation

#### drainedsecantmodulus_sand_bellotti

Function [`drainedsecantmodulus_sand_bellotti`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#drainedsecantmodulus_sand_bellotti).

Calculates the drained secant modulus for various types of sand for an average strain of 0.1 percent.

$$
q_{c1} = \left( \frac{q_c}{P_a} \right) \cdot \sqrt{ \frac{P_a}{\sigma_{vo}^{\prime}} }
$$

$$
\sigma_{mo}^{\prime} = \frac{(1 + 2 \cdot K_0) \cdot \sigma_{vo}^{\prime}}{3}
$$

*Reference:* Bellotti, R., Ghionna, V. N., Jamiolkowski, M., Lancellotta, R., & Robertson, P. K. (1989). Shear strength of sand from CPT. In Congrès international de mécanique des sols et des travaux de fondations. 12 (pp. 179-184).

#### gmax_voidratio_maynerix

Function [`gmax_voidratio_maynerix`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#gmax_voidratio_maynerix).

Calculates the small-strain shear modulus for clay based on the void ratio of the material.

$$
G_{max} = 99.5 \cdot (P_a)^{0.305} \cdot \frac{q_c^{0.695}}{e_0^{1.130}}
$$

*Reference:* Mayne, P.W. and Rix, G.J. (1993), “Gmax-qc Relationships for Clays”, Geotechnical Testing Journal, Vol. 16, No. 1, pp. 54-60.

#### vs_cpt_andrus

Function [`vs_cpt_andrus`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_andrus).

Calculates shear wave velocity from CPT measurements based on a relation calibrated on 229 measurements of which the majority are S-PCPT with some cross-hole tests and suspension logger measurements.

$$
\text{Holocene}
$$

$$
V_s = 2.27 \cdot q_t^{0.412} \cdot I_c^{0.989} \cdot z^{0.033} \cdot ASF
$$

*4 more formulas in the full reference.*

*Reference:* Andrus, R.D., Mohanan, N.P., Piratheepan, P., Ellis, B.S., Holzer, T.L., 2007. Predicting Shear-wave velocity from cone penetration resistance, in: Paper No. 1454. Presented at the 4th International Conference on Earthquake Geotechnical Engineering, Thessaloniki, Greece.

#### vs_cpt_hegazymayne

Function [`vs_cpt_hegazymayne`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_hegazymayne).

The correlation between shear wave velocity and CPT properties developed by Hegazy and Mayne was based on a global databased from 73 sites with different soil conditions including sands, clays, soil mixtures and mine ta…

$$
Q_{t,N} = \frac{q_t - \sigma_{vo}}{\sigma_{vo}^{\prime}}
$$

$$
I_c = \left[ (3.47 - \log Q_{t,N} )^2 + ( \log F_r + 1.22 )^2 \right]^{0.5}
$$

*5 more formulas in the full reference.*

*Reference:* Hegazy and Mayne (2006). A Global Statistical Correlation between Shear Wave Velocity and Cone Penetration Data.

#### vs_cpt_longdonohue

Function [`vs_cpt_longdonohue`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_longdonohue).

The authors propose a correlation between shear wave velocity and CPT properties based on high-quality CPT tests and Gmax obtained from S-PCPT, MASW, cross-hole and block sampling.

$$
V_s = 1.961 \cdot q_t^{0.579} \cdot \left( 1 + B_q \right)^{1.202}
$$

*Reference:* Long, M. and Donohue, S. (2010). Characterisation of Norwegian marine clays with combined shear wave velocity and CPTU data. Canadian Geotechnical Journal.

#### soiltype_vs_longodonohue

Function [`soiltype_vs_longodonohue`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#soiltype_vs_longodonohue).

Determines the soil type based on measured shear wave velocity and normalised cone resistance.

$$
V_{s,1} = \frac{V_s}{\left( \frac{\sigma_{vo}^{\prime}}{P_a} \right)^{0.5}}
$$

*Reference:* Long and Donohue (2010). Characterisation of Norwegian marine clays with combined shear wave velocity and CPTU data.

#### vs_cptd50_karrayetal

Function [`vs_cptd50_karrayetal`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cptd50_karrayetal).

This correlation between Vs and normalised cone tip resistance takes into account the influence of median grain size.

$$
q_{c1} = q_c \cdot \left( \frac{P_a}{\sigma_{vo}^{\prime}} \right)^{0.5}
$$

$$
V_{s1} = V_s \cdot \left( \frac{P_a}{\sigma_{vo}^{\prime}} \right)^{0.25}
$$

*1 more formula in the full reference.*

*Reference:* Karray, M., Lefebvre, G., Ethier, Y., Bigras, A. (2011). Influence of particle size on the correlation between shear wave velocity and cone tip resistance. Canadian Geotechnical Journal.

#### vs_cpt_wrideetal

Function [`vs_cpt_wrideetal`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_wrideetal).

Calculates shear wave velocity based on normalised cone tip resistance based on test data from the CANLEX project.

$$
q_{c1} = q_c \cdot \left( \frac{P_a}{\sigma_{vo}^{\prime}} \right)^{0.5}
$$

$$
V_{s1} = V_s \cdot \left( \frac{P_a}{\sigma_{vo}^{\prime}} \right)^{0.25}
$$

*1 more formula in the full reference.*

*Reference:* C.E. (Fear) Wride, P.K. Robertson, K.W. Biggar, R.G. Campanella, B.A. Hofmann, J.M.O. Hughes, A. Küpper, and D.J. Woeller (2000). Interpretation of in situ test results from the CANLEX sites. Canadian Geotechnical Journal.

#### vs_cpt_tonniandsimonini

Function [`vs_cpt_tonniandsimonini`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_tonniandsimonini).

The authors propose a correlation between CPT properties and shear wave velocity for the Treporti site near Venice, Italy which consist mostly of silty sediments.

$$
V_{s1} = 10^{ \left( 0.80 \cdot I_c - 1.17 \right) } \cdot Q_{tn}
$$

$$
V_{s1} = V_s \cdot \left( \frac{P_a}{\sigma_{vo}^{\prime}} \right)^{0.25}
$$

*1 more formula in the full reference.*

*Reference:* Tonni, L., Simonini, P. (2013). Shear wave velocity as function of cone penetration test measurements in sand and silt mixtures. Engineering Geology.

#### vs_cpt_mcgannetal

Function [`vs_cpt_mcgannetal`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_cpt_mcgannetal).

The authors develop a correlation between shear wave velocity and CPT properties based on Christchurch-specific general soils.

$$
\text{Christchurch general soils}
$$

$$
V_s = 18.4 \cdot q_t^{0.144} \cdot f_s^{0.083} \cdot z^{0.278}
$$

*5 more formulas in the full reference.*

*Reference:* McGann, Christopher R., et al. "Development of an empirical correlation for predicting shear wave velocity of Christchurch soils from cone penetration test data." Soil Dynamics and Earthquake Engineering 75 (2015): 66-75.

#### constrainedmodulus_pcpt_robertson

Function [`constrainedmodulus_pcpt_robertson`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#constrainedmodulus_pcpt_robertson).

Calculates the one-dimensional constrained modulus.

$$
M = \alpha_M \cdot \left( q_t - \sigma_{v0} \right)
$$

$$
\text{when } I_c > 2.2 \text{:}
$$

*5 more formulas in the full reference.*

*Reference:* CPT guide - 7th edition - Robertson and Cabal (2022)

#### vs_stressdependent_stuyts

Function [`vs_stressdependent_stuyts`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#vs_stressdependent_stuyts).

Calculates the shear wave velocity using the calibrated power-law expression proposed by Stuyts et al (2024).

$$
V_s = {\alpha} \left( \frac{\sigma_{vo}^{\prime}}{1 \text{kPa}} \right)^{\beta} = 10^{a_0 + a_1 \cdot I_c} \left( \frac{\sigma_{vo}^{\prime}}{1 \text{kPa}} \right)^{a_2 + a_3 \cdot \log_{10}(\alpha)}
$$

$$
V_s = 10^{2.075 - 0.213 \cdot I_c} \left( \frac{\sigma_{vo}^{\prime}}{1 \text{kPa}} \right)^{0.77 - 0.25 \cdot \log_{10}(\alpha)}
$$

*Reference:* Stuyts, B.; Weijtjens, W.; Jurado, C.S.; Devriendt, C.; Kheffache, A. A Critical Review of Cone Penetration Test-Based Correlations for Estimating Small-Strain Shear Modulus in North Sea Soils. Geotechnics 2024, 4, 604-635. https://doi.org/10.3390/geotechnics4020033

#### dissipation_test_teh

Function [`dissipation_test_teh`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#dissipation_test_teh).

Calculates the pore pressure dissipation from a dissipation tests in clay according to the normalised dissipation curves proposed by Teh & Houlsby (1991).

$$
T^{*} = \frac{c_h \cdot t}{a^2 \cdot \sqrt{I_r}}
$$

*Reference:* Teh, C. I., & Houlsby, G. T. (1991). An analytical study of the cone penetration test in clay. Geotechnique, 41(1), 17-34.

#### clippingdepths_qc1N_tianlehane

Function [`clippingdepths_qc1N_tianlehane`](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#clippingdepths_qc1n_tianlehane).

Calculates the depths where the normalised cone resistance reaches steady values in weak over strong layer systems based on the equations proposed by Tian and Lehane (2025).

$$
q_{c1N}=q_{c1N,0} - \tanh \left[ a_w z^* \right] \left( q_{c1N,0} - q_{c1N,W} \right) \quad \text{in weak layer} \\
q_{c1N}=q_{c1N,0} + \tanh \left[ a_s z^* \right] \left( q_{c1N,S} - q_{c1N,0} \right) \quad \text{in strong layer} \\
a_s = 0.7 r^2 + 0.15 \\
a_w = a_s + 0.4r < 1 \\
r = \frac{q_{c1N,W}}{q_{c1N,S}} \\
z^* = \frac{z-H_t}{d_c} \\
q_{c1N,0} = \eta q_{c1N,S} \\
\eta = 0.96 r^{0.64} \quad 0<r<0.95
$$

*Reference:* Tian, Y. and Lehane, B. (2025). The influence of soil layering and penetrometer diameter on penetration resistance. Canadian Geotechnical Journal, DOI: 10.1139/cgj-2024-0491

### SPT processing class

Upstream page: [SPT processing class](https://groundhog.readthedocs.io/en/main/site_investigation/spt_processing.html)

#### SPTProcessing

Class [`SPTProcessing`](/docs/groundhog/api/siteinvestigation/insitutests/spt_processing#sptprocessing).

The SPTProcessing class implements methods for reading, processing and presentation of Standard Penetration Test (SPT) data.

### SPT corrections and correlations

Upstream page: [SPT corrections and correlations](https://groundhog.readthedocs.io/en/main/site_investigation/spt_correlations.html)

Module [`groundhog.siteinvestigation.insitutests.spt_correlations`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

#### overburdencorrection_spt_liaowhitman

Function [`overburdencorrection_spt_liaowhitman`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#overburdencorrection_spt_liaowhitman).

Applies a correction to the SPT N value to account for the effect of effective overburden pressure in granular soils.

$$
N_1 = C_N \cdot N
$$

$$
C_N = \left[ \frac{1}{ \left( \frac{\sigma_{vo}^{\prime}}{P_a} \right) } \right]^{0.5}
$$

*Reference:* Liao SSC, Whitman RV (1986) Overburden correction factors for SPT in sand. J Geotech Eng ASCE 112(3):373–377

#### spt_N60_correction

Function [`spt_N60_correction`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#spt_n60_correction).

The performance of the SPT in a given soil type depends on the efficiency of energy transmission to the soil.

$$
N_{60} = \frac{N \cdot \eta_H \cdot \eta_B \cdot \eta_S \cdot \eta_R}{60}
$$

*Reference:* J. Ameratunga et al., Correlations of Soil and Rock Properties in Geotechnical Engineering, Developments in Geotechnical Engineering, DOI 10.1007/978-81-322-2629-1_4

#### relativedensity_spt_kulhawymayne

Function [`relativedensity_spt_kulhawymayne`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#relativedensity_spt_kulhawymayne).

Estimates relative density from SPT test.

$$
\text{Unaged, normally consolidated sand}
$$

$$
D_r = \sqrt{\frac{(N_1)_{60}}{60 + 25 \cdot \log_{10} ( d_{50} )}}
$$

*4 more formulas in the full reference.*

*Reference:* Kulhawy FH, Mayne PW (1990) Manual on estimating soil properties for foundation design. Electric Power Research Institute, Palo Alto

#### undrainedshearstrength_spt_salgado

Function [`undrainedshearstrength_spt_salgado`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#undrainedshearstrength_spt_salgado).

Calculates undrained shear strength based on plasticity index and SPT number (corrected to 60% energy ratio).

$$
\frac{S_u}{P_a} = \alpha^{\prime} \cdot N_{60}
$$

*Reference:* Salgado R (2008) The engineering of foundations. McGraw-Hill, New York

#### frictionangle_spt_kulhawymayne

Function [`frictionangle_spt_kulhawymayne`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#frictionangle_spt_kulhawymayne).

Kulhawy and Mayne approximated the chart for friction angle selection from SPT using the formula given below.

$$
\phi = \tan^{-1} \left[ \frac{N}{12.2 +20.3 \cdot \left( \frac{\sigma_{v0}^{\prime}}{P_a} \right)} \right]^{0.34}
$$

*Reference:* Kulhawy FH, Mayne PW (1990) Manual on estimating soil properties for foundation design. Electric Power Research Institute, Palo Alto

#### relativedensityclass_spt_terzaghipeck

Function [`relativedensityclass_spt_terzaghipeck`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#relativedensityclass_spt_terzaghipeck).

Defines the relative density class for SPT measurements in cohesionless soils based on the uncorrected N-number

*Reference:* Terzaghi K, Peck RB (1967) Soil mechanics in engineering practice, 2nd edn. Wiley, New York

#### overburdencorrection_spt_ISO

Function [`overburdencorrection_spt_ISO`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#overburdencorrection_spt_iso).

Corrects the SPT N number or corrected N number (N_{60}) for the effect of overburden pressure in granular soils.

$$
C_N = \sqrt{\frac{98}{\sigma_{v0}^{\prime}}}
$$

*Reference:* BS EN ISO 22476-3

#### frictionangle_spt_PHT

Function [`frictionangle_spt_PHT`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#frictionangle_spt_pht).

Correlation proposed by Peck, Hanson and Thornburn (1974) and mentioned by Wolff (1989)

$$
\varphi^{\prime} = 27.1 + 0.3 \cdot \left( N_1 \right)_{60} - 0.00054 \cdot \left( N_1 \right)_{60}^2
$$

*Reference:* Peck, Hanson and Thornburn (1974). Foundation Engineering.

#### youngsmodulus_spt_AASHTO

Function [`youngsmodulus_spt_AASHTO`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#youngsmodulus_spt_aashto).

Calculates the Young's modulus based on corrected SPT number for various soil types.

*Reference:* AASHTO 1997 - LRFD

#### undrainedshearstrengthclass_spt_terzaghipeck

Function [`undrainedshearstrengthclass_spt_terzaghipeck`](/docs/groundhog/api/siteinvestigation/insitutests/spt_correlations#undrainedshearstrengthclass_spt_terzaghipeck).

Defines the relative density class for SPT measurements in cohesionless soils based on the uncorrected N-number

*Reference:* Terzaghi K, Peck RB (1967) Soil mechanics in engineering practice, 2nd edn. Wiley, New York

## Laboratory testing

Upstream page: [Laboratory testing](https://groundhog.readthedocs.io/en/main/site_investigation/labtests_toplevel.html)

### Sample preparation

Upstream page: [Sample preparation](https://groundhog.readthedocs.io/en/main/site_investigation/samplepreparation.html)

Module [`groundhog.siteinvestigation.labtesting.samplepreparation`](/docs/groundhog/api/siteinvestigation/labtesting/samplepreparation). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

#### undercompaction_cohesionless_ladd

Function [`undercompaction_cohesionless_ladd`](/docs/groundhog/api/siteinvestigation/labtesting/samplepreparation#undercompaction_cohesionless_ladd).

When soil sample have to be reconstituted to a specific relative density, the sample is generally prepared in several layers of equal mass and tamping or vibration is used to obtain the desired volume in the sample moul…

$$
U_i = U_1 - \left[ \frac{U_1 - U_N}{N - 1} \cdot (i - 1) \right]
$$

$$
h_i = \frac{H_0}{N} \left[ (i - 1) + (1 + U_i) \right]
$$

*Reference:* R. Ladd, "Preparing Test Specimens Using Undercompaction," Geotechnical Testing Journal 1, no. 1 (1978): 16-23. https://doi.org/10.1520/GTJ10364J

### Index tests

Upstream page: [Index tests](https://groundhog.readthedocs.io/en/main/site_investigation/indextests.html)

#### PlasticityChart

Class [`PlasticityChart`](/docs/groundhog/api/siteinvestigation/labtesting/indextests#plasticitychart).

Class for plasticity chart

#### PSDChart

Class [`PSDChart`](/docs/groundhog/api/siteinvestigation/labtesting/indextests#psdchart).

Class for plotting of grain size distribution data

### Compressibility

Upstream page: [Compressibility](https://groundhog.readthedocs.io/en/main/site_investigation/compressibility.html)

Module [`groundhog.siteinvestigation.labtesting.compressibility`](/docs/groundhog/api/siteinvestigation/labtesting/compressibility). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

#### selectpoints

Function [`selectpoints`](/docs/groundhog/api/siteinvestigation/labtesting/compressibility#selectpoints).

#### roottimemethod

Function [`roottimemethod`](/docs/groundhog/api/siteinvestigation/labtesting/compressibility#roottimemethod).

Calculates the root-time construction for determining the coefficient of consolidation for an oedometer test (or any other soil mechanical test involving consolidation).

$$
c_v = \frac{0.848 H_{dr}^2}{t_{90}}
$$

*Reference:* Budhu (2011). Soil mechanics and foundations. John Wiley and Sons.

#### logtimemethod

Function [`logtimemethod`](/docs/groundhog/api/siteinvestigation/labtesting/compressibility#logtimemethod).

Calculates the log-time construction for determining the coefficient of consolidation for an oedometer test (or any other soil mechanical test involving consolidation).

$$
c_v = \frac{0.197 H_{dr}^2}{t_{50}}
$$

*Reference:* Budhu (2011). Soil mechanics and foundations. John Wiley and Sons.
