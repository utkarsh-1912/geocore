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
geocore_edit_note: Upstream toctree/autodoc structure restructured into a single topic page that links to the API reference instead of duplicating it, with a short note on how to run this in GeoCore prepended.
upstream_docs_url: https://groundhog.readthedocs.io/en/main/soildynamics/soildynamics_toplevel.html
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, these functions run through the [calculation catalogue](/docs/geocore/using/modules) or through **GeoAI**, which selects and calls them through its validated Tool Registry — you never need to install Python or groundhog yourself.

This page follows the structure of the upstream groundhog documentation for *Soil dynamics*. For each function it gives the method summary and key formulas from the groundhog docstrings, with a link to the full API reference.

## Liquefaction

Upstream page: [Liquefaction](https://groundhog.readthedocs.io/en/main/soildynamics/liquefaction.html)

Module [`groundhog.soildynamics.liquefaction`](/docs/groundhog/api/soildynamics/liquefaction). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### cyclicstressratio_moss

Function [`cyclicstressratio_moss`](/docs/groundhog/api/soildynamics/liquefaction#cyclicstressratio_moss).

Calculates the equivalent uniform cyclic stress ratio (CSR) based on the technique by Seed and Idriss (1971).

$$
CSR = \frac{\tau_{avg}}{\sigma_v^{\prime}} = 0.65 \cdot \frac{a_{max}}{g} \cdot \frac{\sigma_v}{\sigma_v^{\prime}} \cdot r_d
$$

$$
CSR^{*} = CSR_{M_w=7.5}=\frac{CSR}{DWF_{M_w}}
$$

*3 more formulas in the full reference.*

*Reference:* Moss et al (2006) CPT-Based Probabilistic and Deterministic Assessment of In Situ Seismic Soil Liquefaction Potential. Journal of Geotechnical & Geoenvironmental Engineering, 132(8)

### liquefaction_robertsonfear

Function [`liquefaction_robertsonfear`](/docs/groundhog/api/soildynamics/liquefaction#liquefaction_robertsonfear).

Calculates whether cyclic liquefaction can be triggered based on the normalised cone tip resistance and the cyclic shear stress ratio imposed on the soil by the earthquake event.

$$
q_{c1} = (q_c / p_a) ( p_a /  \sigma_{vo}^{\prime} )^{0.5}
$$

*Reference:* Robertson, P. K., and C. E. Fear. "Application of CPT to evaluate liquefaction potential." CPT’95, Linkoping (1995): 57-79.

### liquefactionprobability_moss

Function [`liquefactionprobability_moss`](/docs/groundhog/api/soildynamics/liquefaction#liquefactionprobability_moss).

Calculates the probability of liquefaction according to Moss et al.

$$
q_{c,1} = q_c \left( \frac{p_a}{\sigma_{vo}^{\prime}} \right)^{c}
$$

$$
c = f_1 \cdot \left( \frac{R_f}{f_3} \right)^{f_2}
$$

*6 more formulas in the full reference.*

*Reference:* Moss et al (2006) CPT-Based Probabilistic and Deterministic Assessment of In Situ Seismic Soil Liquefaction Potential. Journal of Geotechnical & Geoenvironmental Engineering, 132(8)

### liquefactionprobability_saye

Function [`liquefactionprobability_saye`](/docs/groundhog/api/soildynamics/liquefaction#liquefactionprobability_saye).

Current engineering practice employs clean sand-based procedures to evaluate liquefaction triggering in nonplastic, coarse-grained soils and low-plasticity, fine-grained soils below level or mildly-sloping ground.

$$
\Delta_Q = \frac{Q_t + 10}{\frac{f_s}{\sigma_{vo}^{\prime}} + 0.67}
$$

$$
\hat{m}_{CRR} = \frac{\hat{\Delta}_Q}{178 \cdot \hat{\Delta}_Q - 3.349} \leq 0.1 \ \text{for} \ \Delta_Q \geq 20
$$

*3 more formulas in the full reference.*

*Reference:* Saye, Steven R., Scott M. Olson, and Kevin W. Franke. "Common-Origin Approach to Assess Level-Ground Liquefaction Susceptibility and Triggering in CPT-Compatible Soils Using Δ Q." Journal of Geotechnical and Geoenvironmental Engineering 147.7 (2021): 04021046.

### cyclicstressratio_youd

Function [`cyclicstressratio_youd`](/docs/groundhog/api/soildynamics/liquefaction#cyclicstressratio_youd).

Calculates the cyclic stress ratio adjusted to a magnitude 7.5 earthquake using the simplified equation (Seed and Idriss 1971; Whitman 1971) and the adjustments recommended by Youd et al.

$$
CSR_{7.5} = \frac{CSR}{MSF} = \frac{\tau_{avg} / \sigma_{vo}^{\prime}}{MSF} = \frac{0.65 \cdot \left(
\frac{a_{max}}{g} \right) \cdot \left( \frac{\sigma_{vo}}{\sigma_{vo}^{\prime}} \right) \cdot r_d}{MSF}
$$

$$
MSF = \frac{10^{2.24}}{M^{2.56}}
$$

*1 more formula in the full reference.*

*Reference:* Youd, T. L., et al. 2001. Liquefaction resistance of soils: Summary report from the 1996 NCEER and 1998 NCEER=NSF workshops on evaluation of liquefaction resistance of soils.” J. Geotech. Geoenviron. Eng. 127 (10): 817–833. https://doi.org/10.1061/(ASCE)1090-0241(2001)127:10(817).

## Cyclic behaviour

Upstream page: [Cyclic behaviour](https://groundhog.readthedocs.io/en/main/soildynamics/cyclicbehaviour.html)

Module [`groundhog.soildynamics.cyclicbehaviour`](/docs/groundhog/api/soildynamics/cyclicbehaviour). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### cycliccontours_dssclay_andersen

Function [`cycliccontours_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#cycliccontours_dssclay_andersen).

Calculates the number of cycles to failure for a cyclic DSS test with a given combination of average and cyclic shear stress for a sample with a given undrained shear strength.

*Reference:* Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

### plotcycliccontours_dssclay_andersen

Function [`plotcycliccontours_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotcycliccontours_dssclay_andersen).

Returns a Plotly figure with the cyclic contours for DSS tests on normally consolidated Drammen clay

### cycliccontours_triaxialclay_andersen

Function [`cycliccontours_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#cycliccontours_triaxialclay_andersen).

Calculates the number of cycles to failure for cyclic triaxial test with a given combination of average and cyclic shear stress for a sample with a given undrained shear strength.

*Reference:* Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

### plotcycliccontours_triaxialclay_andersen

Function [`plotcycliccontours_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotcycliccontours_triaxialclay_andersen).

Returns a Plotly figure with the cyclic contours for triaxial tests on normally consolidated Drammen clay

### strainaccumulation_dssclay_andersen

Function [`strainaccumulation_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#strainaccumulation_dssclay_andersen).

Calculates the strain accumulation for a normally consolidated clay sample under symmetrical cyclic loading (no average shear stress) in a DSS test.

*Reference:* Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

### plotstrainaccumulation_dssclay_andersen

Function [`plotstrainaccumulation_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotstrainaccumulation_dssclay_andersen).

Returns a Plotly figure with the strain accumulation contours for DSS tests on normally consolidated Drammen clay

### strainaccumulation_triaxialclay_andersen

Function [`strainaccumulation_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#strainaccumulation_triaxialclay_andersen).

Calculates the cyclic and average strain accumulation for a normally consolidated clay sample under symmetrical cyclic loading (no average shear stress) in a cyclic triaxial test.

*Reference:* Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

### plotstrainaccumulation_triaxialclay_andersen

Function [`plotstrainaccumulation_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotstrainaccumulation_triaxialclay_andersen).

Returns a Plotly figure with the strain accumulation contours for triaxial tests on normally consolidated Drammen clay with symmetrical loading

### porepressureaccumulation_dssclay_andersen

Function [`porepressureaccumulation_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#porepressureaccumulation_dssclay_andersen).

Calculates the excess pore pressure accumulation for a normally consolidated clay sample under symmetrical cyclic loading (no average shear stress) in a DSS test.

*Reference:* Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

### plotporepressureaccumulation_dssclay_andersen

Function [`plotporepressureaccumulation_dssclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotporepressureaccumulation_dssclay_andersen).

Returns a Plotly figure with the excess pore pressure accumulation contours for cyclic DSS tests on normally consolidated Drammen clay with symmetrical loading

### porepressureaccumulation_triaxialclay_andersen

Function [`porepressureaccumulation_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#porepressureaccumulation_triaxialclay_andersen).

Calculates the excess pore pressure accumulation for a normally consolidated clay sample under symmetrical cyclic loading (no average shear stress) in a cyclic triaxial test.

*Reference:* Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

### plotporepressureaccumulation_triaxialclay_andersen

Function [`plotporepressureaccumulation_triaxialclay_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotporepressureaccumulation_triaxialclay_andersen).

Returns a Plotly figure with the excess pore pressure accumulation contours for cyclic triaxial tests on normally consolidated Drammen clay with symmetrical loading

### strainaccumulation_dsssand_andersen

Function [`strainaccumulation_dsssand_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#strainaccumulation_dsssand_andersen).

Calculates the strain accumulation as a function of the cyclic shear stress level and the number of cycles for normally consolidated sand and silt in a symmetrical cyclic DSS test (no average shear stress) for different…

$$
\sigma_{ref}^{\prime} = p_a \cdot ( \sigma_{vc}^{\prime} / p_a ) ^ n
$$

*Reference:* Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

### plotstrainaccumulation_dsssand_andersen

Function [`plotstrainaccumulation_dsssand_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotstrainaccumulation_dsssand_andersen).

Returns a Plotly figure with the cyclic strain accumulation contours for cyclic DSS tests on normally consolidated sand or silt with symmetrical loading

### plotporepressureaccumulation_dsssand_andersen

Function [`plotporepressureaccumulation_dsssand_andersen`](/docs/groundhog/api/soildynamics/cyclicbehaviour#plotporepressureaccumulation_dsssand_andersen).

Returns a Plotly figure with the permanent excess pore pressure accumulation contours for cyclic DSS tests on normally consolidated sand or silt with symmetrical loading

### cyclicstrength_dsssand_relativedensity

Function [`cyclicstrength_dsssand_relativedensity`](/docs/groundhog/api/soildynamics/cyclicbehaviour#cyclicstrength_dsssand_relativedensity).

Calculates the DSS cyclic strength of sand, defined as the ratio of cyclic shear stress to reference normal stress for failure at 10 cycles.

$$
\sigma_{ref}^{\prime} = p_a \cdot ( \sigma_{ref}^{\prime} / p_a )^n
$$

*Reference:* Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

### cyclicstrength_dsssand_watercontent

Function [`cyclicstrength_dsssand_watercontent`](/docs/groundhog/api/soildynamics/cyclicbehaviour#cyclicstrength_dsssand_watercontent).

Calculates the DSS cyclic strength of sand, defined as the ratio of cyclic shear stress to reference normal stress for failure at 10 cycles.

$$
\sigma_{ref}^{\prime} = p_a \cdot ( \sigma_{ref}^{\prime} / p_a )^n
$$

*Reference:* Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

## Dynamic soil property correlations

Upstream page: [Dynamic soil property correlations](https://groundhog.readthedocs.io/en/main/soildynamics/soilproperties.html)

Module [`groundhog.soildynamics.soilproperties`](/docs/groundhog/api/soildynamics/soilproperties). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### modulusreduction_plasticity_ishibashi

Function [`modulusreduction_plasticity_ishibashi`](/docs/groundhog/api/soildynamics/soilproperties#modulusreduction_plasticity_ishibashi).

Calculates the modulus reduction curve (G/Gmax) as a function of shear strain.

$$
\frac{G}{G_{max}} = K \left( \gamma, \text{PI} \right) \left( \sigma_m^{\prime} \right)^{m \left( \gamma, \text{PI} \right) - m_0}
$$

$$
K \left( \gamma, \text{PI} \right) = 0.5 \left[ 1 + \tanh \left[ \ln \left( \frac{0.000102 + n ( \text{PI} )}{\gamma} \right)^{0.492} \right] \right]
$$

*3 more formulas in the full reference.*

*Reference:* Ishibashi, I., & Zhang, X. (1993). Unified dynamic shear moduli and damping ratios of sand and clay. Soils and foundations, 33(1), 182-191.

### gmax_shearwavevelocity

Function [`gmax_shearwavevelocity`](/docs/groundhog/api/soildynamics/soilproperties#gmax_shearwavevelocity).

Calculates the small-strain shear modulus (shear strain < 1e-4%) from the shear wave velocity and the bulk unit weight if the soil based on elastic theory.

$$
G_{max} = \rho \cdot V_s^2
$$

$$
\rho = \gamma / g
$$

*Reference:* Robertson, P.K. and Cabal, K.L. (2015). Guide to Cone Penetration Testing for Geotechnical Engineering. 6th edition. Gregg Drilling & Testing, Inc.

### dampingratio_sandgravel_seed

Function [`dampingratio_sandgravel_seed`](/docs/groundhog/api/soildynamics/soilproperties#dampingratio_sandgravel_seed).

Damping ratios for sand are compiled from a dataset comprising several sands and gravels.

*Reference:* Seed, H. B., Wong, R. T., Idriss, I. M., & Tokimatsu, K. (1986). Moduli and damping factors for dynamic analyses of cohesionless soils. Journal of geotechnical engineering, 112(11), 1016-1032.

### modulusreduction_darendeli

Function [`modulusreduction_darendeli`](/docs/groundhog/api/soildynamics/soilproperties#modulusreduction_darendeli).

Darendeli (2001) proposed a comprehensive framework for estimating the modulus reduction curve and damping curve for sand, fine sand, silt and clay based on extensive laboratory testing.

$$
\frac{G}{G_{max}} = \frac{1}{1 + \left( \frac{\gamma}{\gamma_r} \right)^a}
$$

$$
\gamma_r = \left( \phi_1 + \phi_2 \cdot PI \cdot OCR^{\phi_3} \right) \cdot \sigma_0^{\prime \phi_4}
$$

*7 more formulas in the full reference.*

*Reference:* Darendeli, M. B. (2001). Development of a new family of normalized modulus reduction and material damping curves. The university of Texas at Austin.

## CPT Liquefaction

Upstream page: [CPT Liquefaction](https://groundhog.readthedocs.io/en/main/soildynamics/cptliquefaction.html)

Module [`groundhog.soildynamics.cptliquefaction`](/docs/groundhog/api/soildynamics/cptliquefaction). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### fos_liquefaction

Function [`fos_liquefaction`](/docs/groundhog/api/soildynamics/cptliquefaction#fos_liquefaction).

Calculates the Factor of Safety (FoS) for liquefaction assessment.

$$
FoS = \min \left( \frac{CRR}{CSR} \cdot MSF \cdot K_{\sigma}, 5 \right)
$$

$$
\text{If } \sigma_v^{\prime} = \sigma_v, \text{ then } FoS = 5
$$

*Reference:* Youd, T. L., et al. (2001). Liquefaction Resistance of Soils: Summary Report from the 1996 NCEER and 1998 NCEER/NSF Workshops on Evaluation of Liquefaction Resistance of Soils. Journal of Geotechnical and Geoenvironmental Engineering, 127(10).; Idriss, I. M., & Boulanger, R. W. (2008). Soil Liquefaction During Earthquakes. Earthquake Engineering Research Institute.

### csr_robertson_cabal_2022

Function [`csr_robertson_cabal_2022`](/docs/groundhog/api/soildynamics/cptliquefaction#csr_robertson_cabal_2022).

Calculates the Cyclic Stress Ratio (CSR) and Magnitude Scaling Factor (MSF) following the methodology outlined by Robertson and Cabal (2022).

$$
CSR = 0.65 \cdot a_{max} \cdot \frac{\sigma_v}{\sigma_v^{\prime}} \cdot r_d
$$

$$
r_d = \begin{cases}
1.0 - 0.00765 \cdot z & \text{if } z < 9.15 \, m \\
1.174 - 0.0267 \cdot z & \text{if } 9.15 \, m \leq z < 23 \, m \\
0.744 - 0.008 \cdot z & \text{if } 23 \, m \leq z < 30 \, m \\
0.5 & \text{if } z \geq 30 \, m
\end{cases}
$$

*1 more formula in the full reference.*

*Reference:* Robertson, P. K., & Cabal, K. L. (2022). Guide to Cone Penetration Testing for Geotechnical Engineering. Gregg Drilling & Testing, Inc.; Seed, H. B., & Idriss, I. M. (1971). Simplified Procedure for Evaluating Soil Liquefaction Potential. Journal of the Soil Mechanics and Foundations Division, 97(9).

### csr_robertson_wride_1998

Function [`csr_robertson_wride_1998`](/docs/groundhog/api/soildynamics/cptliquefaction#csr_robertson_wride_1998).

Calculates the Cyclic Stress Ratio (CSR) and Magnitude Scaling Factor (MSF) following the methodology outlined by Robertson and Wride (1998).

$$
CSR = 0.65 \cdot a_{max} \cdot \frac{\sigma_v}{\sigma_v^{\prime}} \cdot r_d
$$

$$
r_d = \begin{cases}
1.0 - 0.00765 \cdot z & \text{if } z < 9.15 \, m \\
1.174 - 0.0267 \cdot z & \text{if } 9.15 \, m \leq z < 23 \, m \\
0.744 - 0.008 \cdot z & \text{if } 23 \, m \leq z < 30 \, m \\
0.5 & \text{if } z \geq 30 \, m
\end{cases}
$$

*1 more formula in the full reference.*

*Reference:* Robertson, P. K., & Wride, C. E. (1998). Evaluating Cyclic Liquefaction Potential Using the Cone Penetration Test. Canadian Geotechnical Journal, 35(3).; Seed, H. B., & Idriss, I. M. (1971). Simplified Procedure for Evaluating Soil Liquefaction Potential. Journal of the Soil Mechanics and Foundations Division, 97(9).

### csr_idriss_boulanger_2008

Function [`csr_idriss_boulanger_2008`](/docs/groundhog/api/soildynamics/cptliquefaction#csr_idriss_boulanger_2008).

Calculates the Cyclic Stress Ratio (CSR) and Magnitude Scaling Factor (MSF) following the methodology outlined by Idriss and Boulanger (2008).

$$
CSR = 0.65 \cdot a_{max} \cdot \frac{\sigma_v}{\sigma_v^{\prime}} \cdot r_d
$$

$$
MSF = \min \left( 6.9 \cdot e^{-M_w / 4} - 0.058, 1.8 \right)
$$

*3 more formulas in the full reference.*

*Reference:* Idriss, I. M., & Boulanger, R. W. (2008). Soil Liquefaction During Earthquakes. Earthquake Engineering Research Institute.; Seed, H. B., & Idriss, I. M. (1971). Simplified Procedure for Evaluating Soil Liquefaction Potential. Journal of the Soil Mechanics and Foundations Division, 97(9).

### csr_boulanger_idriss_2014

Function [`csr_boulanger_idriss_2014`](/docs/groundhog/api/soildynamics/cptliquefaction#csr_boulanger_idriss_2014).

Calculates the Cyclic Stress Ratio (CSR) and Magnitude Scaling Factor (MSF) following the methodology outlined by Boulanger and Idriss (2014).

$$
CSR = 0.65 \cdot a_{max} \cdot \frac{\sigma_v}{\sigma_v^{\prime}} \cdot r_d
$$

$$
\alpha = -1.012 - 1.126 \cdot \sin \left( \frac{z}{11.73} + 5.133 \right)
$$

*4 more formulas in the full reference.*

*Reference:* Boulanger, R. W., & Idriss, I. M. (2014). CPT and SPT Liquefaction Triggering Procedures. Report No. UCD/CGM-14/01, University of California, Davis.; Seed, H. B., & Idriss, I. M. (1971). Simplified Procedure for Evaluating Soil Liquefaction Potential. Journal of the Soil Mechanics and Foundations Division, 97(9).

### crr_robertson_cabal_2022

Function [`crr_robertson_cabal_2022`](/docs/groundhog/api/soildynamics/cptliquefaction#crr_robertson_cabal_2022).

Calculates the Cyclic Resistance Ratio (CRR) and Overburden Correction Factor (K_{\sigma}) based on the methodology outlined by Robertson and Cabal (2022).

$$
CRR = \begin{cases}
0.833 \cdot \left( \frac{Q_{tn,cs}}{1000} \right) + 0.05 & \text{if } Q_{tn,cs} < 50 \\
93 \cdot \left( \frac{Q_{tn,cs}}{1000} \right)^3 + 0.08 & \text{if } 50 \leq Q_{tn,cs} < 160 \\
\infty & \text{if } Q_{tn,cs} \geq 160
\end{cases}
$$

$$
K_{\sigma} = 1
$$

*Reference:* Robertson, P. K., & Cabal, K. L. (2022). Guide to Cone Penetration Testing for Geotechnical Engineering. Gregg Drilling & Testing, Inc.

### crr_robertson_wride_1998

Function [`crr_robertson_wride_1998`](/docs/groundhog/api/soildynamics/cptliquefaction#crr_robertson_wride_1998).

Calculates the Cyclic Resistance Ratio (CRR) and Overburden Correction Factor (K_{\sigma}) based on the methodology outlined by Robertson and Wride (1998).

$$
CRR = \begin{cases}
0.833 \cdot \left( \frac{Q_{tn,cs}}{1000} \right) + 0.05 & \text{if } Q_{tn,cs} < 50 \\
93 \cdot \left( \frac{Q_{tn,cs}}{1000} \right)^3 + 0.08 & \text{if } 50 \leq Q_{tn,cs} < 160 \\
\infty & \text{if } Q_{tn,cs} \geq 160
\end{cases}
$$

$$
K_{\sigma} = \begin{cases}
1.0 & \text{if } \sigma_v^{\prime} < 100 \, kPa \\
\min \left( \left( \frac{\sigma_v^{\prime}}{P_a} \right)^{f_{K_{\sigma}} - 1}, 1 \right) & \text{otherwise}
\end{cases}
$$

*2 more formulas in the full reference.*

*Reference:* Robertson, P. K., & Wride, C. E. (1998). Evaluating Cyclic Liquefaction Potential Using the Cone Penetration Test. Canadian Geotechnical Journal, 35(3).; Youd, T. L., et al. (2001). Liquefaction Resistance of Soils: Summary Report from the 1996 NCEER and 1998 NCEER/NSF Workshops on Evaluation of Liquefaction Resistance of Soils. Journal of Geotechnical and Geoenvironmental Engineering, 127(10).

### crr_idriss_boulanger_2008

Function [`crr_idriss_boulanger_2008`](/docs/groundhog/api/soildynamics/cptliquefaction#crr_idriss_boulanger_2008).

Calculates the Cyclic Resistance Ratio (CRR) and Overburden Correction Factor (K_{\sigma}) based on the methodology outlined by Idriss and Boulanger (2008).

$$
CRR = \min \left( \exp \left( \frac{Q_{tn,cs}}{540} + \left( \frac{Q_{tn,cs}}{67} \right)^2 - \left( \frac{Q_{tn,cs}}{80} \right)^3 + \left( \frac{Q_{tn,cs}}{114} \right)^4 - 3 \right), 0.6 \right)
$$

$$
C_{\sigma} = \min \left( \frac{1}{37.3 - 8.27 \cdot \min(Q_{tn,cs}, 211)^{0.264}}, 0.3 \right)
$$

*1 more formula in the full reference.*

*Reference:* Idriss, I. M., & Boulanger, R. W. (2008). Soil Liquefaction During Earthquakes. Earthquake Engineering Research Institute.

### crr_boulanger_idriss_2014

Function [`crr_boulanger_idriss_2014`](/docs/groundhog/api/soildynamics/cptliquefaction#crr_boulanger_idriss_2014).

Calculates the Cyclic Resistance Ratio (CRR) and Overburden Correction Factor (K_{\sigma}) based on the methodology outlined by Boulanger and Idriss (2014).

$$
CRR = \min \left( \exp \left( \frac{Q_{tn,cs}}{113} + \left( \frac{Q_{tn,cs}}{1000} \right)^2 - \left( \frac{Q_{tn,cs}}{140} \right)^3 + \left( \frac{Q_{tn,cs}}{137} \right)^4 - 2.80 \right), 0.6 \right)
$$

$$
C_{\sigma} = \frac{1}{37.3 - 8.27 \cdot \min(Q_{tn,cs}, 211)^{0.264}}
$$

*1 more formula in the full reference.*

*Reference:* Boulanger, R. W., & Idriss, I. M. (2014). CPT and SPT Liquefaction Triggering Procedures. Report No. UCD/CGM-14/01, University of California, Davis.

### Qtn_cs_robertson_cabal_2022

Function [`Qtn_cs_robertson_cabal_2022`](/docs/groundhog/api/soildynamics/cptliquefaction#qtn_cs_robertson_cabal_2022).

Calculates the normalized cone penetration resistance with fines correction (Q_{tn,cs}) based on the methodology outlined by Robertson and Cabal (2022).

$$
K_c = \begin{cases}
1.0 & \text{if } I_c \leq 1.7 \\
1.0 & \text{if } 1.7 < I_c < 2.36 \text{ and } F_r < 0.5 \\
15 - \frac{14}{1 + \left( \frac{I_c}{2.95} \right)^{11}} & \text{otherwise}
\end{cases}
$$

$$
n = \min \left( 1, 0.381 \cdot I_c + 0.05 \cdot \left( \frac{\sigma_v^{\prime}}{P_a} \right) - 0.15 \right)
$$

*2 more formulas in the full reference.*

*Reference:* Robertson, P. K., & Cabal, K. L. (2022). Guide to Cone Penetration Testing for Geotechnical Engineering. Gregg Drilling & Testing, Inc.

### Qtn_cs_robertson_wride_1998

Function [`Qtn_cs_robertson_wride_1998`](/docs/groundhog/api/soildynamics/cptliquefaction#qtn_cs_robertson_wride_1998).

Calculates the normalized cone penetration resistance with fines correction (Q_{tn,cs}) based on the methodology outlined by Robertson and Wride (1998).

$$
C_Q = \min \left( \left( \frac{P_a}{\sigma_v} \right)^{0.5}, 2 \right)
$$

$$
q_{c1N} = \frac{q_c}{0.001 P_a} \cdot C_Q
$$

*2 more formulas in the full reference.*

*Reference:* Robertson, P. K., & Wride, C. E. (1998). Evaluating cyclic liquefaction potential using the cone penetration test. Canadian Geotechnical Journal, 35(3), 442-459.

### Qtn_cs_idriss_boulanger_2008

Function [`Qtn_cs_idriss_boulanger_2008`](/docs/groundhog/api/soildynamics/cptliquefaction#qtn_cs_idriss_boulanger_2008).

Calculates the normalized cone penetration resistance with fines correction (Q_{tn,cs}) based on the methodology outlined by Idriss and Boulanger (2008).

$$
q_{c1N} = \max \left( \min \left( \frac{q_c}{0.001 P_a}, 254 \right), 21 \right)
$$

$$
m = 1.338 - 0.249 \cdot (q_{c1N})^{0.264}
$$

*4 more formulas in the full reference.*

*Reference:* Idriss, I. M., & Boulanger, R. W. (2008). Soil liquefaction during earthquakes. Earthquake Engineering Research Institute.

### Qtn_cs_boulanger_idriss_2014

Function [`Qtn_cs_boulanger_idriss_2014`](/docs/groundhog/api/soildynamics/cptliquefaction#qtn_cs_boulanger_idriss_2014).

Calculates the normalized cone penetration resistance with fines correction (Q_{tn,cs}) based on the methodology outlined by Boulanger and Idriss (2014).

$$
FC = \min \left( \max \left( 80 \cdot (I_c + C_{FC}) - 137, 0 \right), 100 \right)
$$

$$
C_N = \min \left( \left( \frac{P_a}{\sigma_v^{\prime}} \right)^m, 1.7 \right)
$$

*3 more formulas in the full reference.*

*Reference:* Boulanger, R. W., & Idriss, I. M. (2014). CPT and SPT liquefaction triggering procedures. Report No. UCD/CGM-14/01, Center for Geotechnical Modeling, Department of Civil & Environmental Engineering, University of California, Davis.

### liquefaction_strains_zhang

Function [`liquefaction_strains_zhang`](/docs/groundhog/api/soildynamics/cptliquefaction#liquefaction_strains_zhang).

Calculates liquefaction-induced strains (volumetric and lateral) for level ground and lateral spreading based on the methodologies of Zhang et al.

$$
\epsilon_{liq} =
\begin{cases}
102 \cdot Q_{tn,cs}^{-0.82}, & 0.0 \leq FoS_{liq} \leq 0.55, 33 \leq Q_{tn,cs} \leq 200 \\
2411 \cdot Q_{tn,cs}^{-1.45}, & 0.55 < FoS_{liq} \leq 0.65, 147 < Q_{tn,cs} \leq 200 \\
1690 \cdot Q_{tn,cs}^{-1.46}, & 0.75 < FoS_{liq} \leq 0.85, 80 < Q_{tn,cs} \leq 200 \\
5.8, & Q_{tn,cs} < 33, FoS_{liq} < 1 \\
\end{cases}
$$

$$
\gamma_{liq} =
\begin{cases}
3.26 \cdot FoS_{liq}^{-1.80}, & D_r \geq 0.8, 0.7 \leq FoS_{liq} < 2.0 \\
6.2, & D_r \geq 0.8, FoS_{liq} < 0.7 \\
3.58 \cdot FoS_{liq}^{-4.42}, & D_r \geq 0.5, 0.66 \leq FoS_{liq} < 2.0 \\
250 (1 - FoS_{liq}) + 3.5, & 0.81 \leq FoS_{liq} < 1.0 \\
51.2, & FoS_{liq} < 0.81 \\
0, & \text{otherwise}
\end{cases}
$$

*Reference:* Zhang, L., Robertson, P. K., & Brachman, R. W. I. (2002). Estimating liquefaction-induced ground settlements from CPT for level ground. *Canadian Geotechnical Journal, 39*(5), 1168-1180.; Zhang, L., Robertson, P. K., & Brachman, R. W. I. (2004). Estimating liquefaction-induced lateral displacements using the standard penetration test or cone penetration test. *Journal of Geotechnical and Geoenvironmental Engineering, 130*(8), 861-871.
