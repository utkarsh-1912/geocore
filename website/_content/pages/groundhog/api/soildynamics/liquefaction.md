---
title: Liquefaction
slug: groundhog/api/soildynamics/liquefaction
section: Groundhog API Reference
description: 'API reference for groundhog.soildynamics.liquefaction: 5 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/soildynamics/liquefaction.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.soildynamics.liquefaction
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/soildynamics/liquefaction.html
geocore_available: true
geocore_functions:
- cyclicstressratio_moss
- cyclicstressratio_youd
- liquefaction_robertsonfear
- liquefactionprobability_moss
- liquefactionprobability_saye
---

Module `groundhog.soildynamics.liquefaction` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/soildynamics/liquefaction.py).

Upstream documentation: [Liquefaction](https://groundhog.readthedocs.io/en/main/soildynamics/liquefaction.html).

**Functions:** [`cyclicstressratio_moss`](#cyclicstressratio_moss), [`liquefaction_robertsonfear`](#liquefaction_robertsonfear), [`liquefactionprobability_moss`](#liquefactionprobability_moss), [`liquefactionprobability_saye`](#liquefactionprobability_saye), [`cyclicstressratio_youd`](#cyclicstressratio_youd)

<a id="cyclicstressratio_moss"></a>

## `cyclicstressratio_moss`

<span class="gc-badge gc-available" data-geocore-function="cyclicstressratio_moss">Available in GeoCore</span> [Soil dynamics › Liquefaction › Moss (2006) Cyclic Stress Ratio](/docs/geocore/using/modules#cyclicstressratio_moss)

```python
cyclicstressratio_moss(
    sigma_vo,
    sigma_vo_eff,
    magnitude,
    acceleration,
    depth,
    gravity=9.81,
    rd_override=nan,
    DWF_override=nan,
    **kwargs,
)
```

Calculates the equivalent uniform cyclic stress ratio (CSR) based on the technique by Seed and Idriss (1971). Earthquake events are scaled to an equivalent event with magnitude of 7.5 using a magnitude-correlated duration weighting factor (DWF).

The formulation of DWF from Cetin et al (2004) is used which is based on a SPT-based liquefaction database with the formulation being valid for magnitudes between 5.5 and 8.5.

The non-linear shear mass participation factor formulation from Cetin et al (2004) is used. This depends on the depth of the layer of interest, the earthquake magnitude and the maximum horizontal ground acceleration. The formula uses the acceleration in units of gravity.

The paper on which this equation is based offers a discussion on the variability on each of the terms.

$$
CSR = \frac{\tau_{avg}}{\sigma_v^{\prime}} = 0.65 \cdot \frac{a_{max}}{g} \cdot \frac{\sigma_v}{\sigma_v^{\prime}} \cdot r_d
$$

$$
CSR^{*} = CSR_{M_w=7.5}=\frac{CSR}{DWF_{M_w}}
$$

$$
DWF_{M_w} = 17.84 \cdot M_w^{-1.43}
$$

$$
r_d = \frac{\left[ 1 + \frac{-9.147 - 4.173 \cdot a_{max} + 0.652 \cdot M_w}{10.567 + 0.089 \cdot e^{0.089 \cdot \left( -z \cdot 3.28 - 7.760 \cdot a_{max} + 78.576 \right)}} \right]}{\left[ 1 + \frac{-9.147 - 4.173 \cdot a_{max} + 0.652 \cdot M_w}{10.567 + 0.089 \cdot e^{0.089 \cdot (-7.760 \cdot a_{max} + 78.576)}} \right]} \\ z \geq 20m
$$

$$
r_d = \frac{\left[ 1 + \frac{-9.147 - 4.173 \cdot a_{max} + 0.652 \cdot M_w}{10.567 + 0.089 \cdot e^{0.089 \cdot \left( -z \cdot 3.28 - 7.760 \cdot a_{max} + 78.576 \right)}} \right]}{\left[ 1 + \frac{-9.147 - 4.173 \cdot a_{max} + 0.652 \cdot M_w}{10.567 + 0.089 \cdot e^{0.089 \cdot (-7.760 \cdot a_{max} + 78.576)}} \right]} - 0.0014 \cdot (z \cdot 3.28 - 65) \\ z < 20m
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `sigma_vo` | kPa | sigma_vo >= 0.0 | required | Total vertical stress at the depth of interest ($\sigma_v$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Effective vertical stress at the depth of interest ($\sigma_v^{\prime}$) |
| `magnitude` | - | 5.5 <= magnitude <= 8.5 | required | Earthquake magnitude ($M_w$) |
| `acceleration` | m/s2 | acceleration >= 0.0 | required | Maximum horizontal acceleration at the soil surface ($a_{max}$) |
| `depth` | m | depth >= 0.0 | required | Depth at which CSR is calculated ($z$) |
| `gravity` | m/s2 | 9.8 <= gravity <= 10.0 | `9.81` | Acceleration due to gravity ($g$) |
| `rd_override` | - |  | `nan` | Override for direct specification of rd ($r_d$) |
| `DWF_override` | - |  | `nan` | Override for direct specification of DWF ($DWF$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `CSR [-]` | - | Uncorrected cyclic stress ratio ($CSR$) |
| `CSR* [-]` | - | Equivalent uniform cyclic stress ratio (for magnitude 7.5 event) ($CSR^{*}$) |
| `DWF [-]` | - | Magnitude-correlated duration weighting factor ($DWF$) |
| `rd [-]` | - | Nonlinear shear mass participation factor ($r_d$) |

**References**

- Moss et al (2006) CPT-Based Probabilistic and Deterministic Assessment of In Situ Seismic Soil Liquefaction Potential. Journal of Geotechnical & Geoenvironmental Engineering, 132(8)

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="liquefaction_robertsonfear"></a>

## `liquefaction_robertsonfear`

<span class="gc-badge gc-available" data-geocore-function="liquefaction_robertsonfear">Available in GeoCore</span> [Soil dynamics › Liquefaction › Robertson & Fear (1995) Liquefaction](/docs/geocore/using/modules#liquefaction_robertsonfear)

```python
liquefaction_robertsonfear(qc, sigma_vo_eff, CSR, atmospheric_pressure=100.0, **kwargs)
```

Calculates whether cyclic liquefaction can be triggered based on the normalised cone tip resistance and the cyclic shear stress ratio imposed on the soil by the earthquake event.

For earthquake magnitudes different from 7.5, CSR$^*$ should be used.

Note that this correlation was developed for clean sands and does not include any modifications for fines content.

It should also be noted that the correlation is based on averaged cone resistance values from field cases. So it applied to raw cone resistance data, they might be too conservative.

$$
q_{c1} = (q_c / p_a) ( p_a /  \sigma_{vo}^{\prime} )^{0.5}
$$

![Dataset supporting the liquefaction triggering function](/docs/assets/groundhog/docs/soildynamics/images/liquefaction_robertsonfear_1.png)

*Dataset supporting the liquefaction triggering function*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc` | MPa | 0.0 <= qc <= 120.0 | required | Cone tip resistance ($q_c$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `CSR` | - | 0.073 <= CSR <= 0.49 | required | Seismic shear stress ratio ($CSR = \tau_{avg} / \sigma_{vo}^{\prime}$) |
| `atmospheric_pressure` | kPa | 90.0 <= atmospheric_pressure <= 110.0 | `100.0` | Atmospheric pressure used for normalisation ($p_a$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `qc1 [-]` | - | Normalised dimensionless cone resistance ($q_{c1}$) |
| `qc1 liquefaction [-]` | - | Normalised dimensionless cone tip resistance for which liquefaction is just triggered at the given CSR ($q_{c1,liq}$) |
| `qc liquefaction [MPa]` | MPa | Cone tip resistance for which liquefaction is just triggered at the given CSR ($q_{c,liq}$) |
| `liquefaction` |  | Liquefaction occurs? |

**References**

- Robertson, P. K., and C. E. Fear. "Application of CPT to evaluate liquefaction potential." CPT’95, Linkoping (1995): 57-79.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="liquefactionprobability_moss"></a>

## `liquefactionprobability_moss`

<span class="gc-badge gc-available" data-geocore-function="liquefactionprobability_moss">Available in GeoCore</span> [Soil dynamics › Liquefaction › Moss (2006) Liquefaction Probability](/docs/geocore/using/modules#liquefactionprobability_moss)

```python
liquefactionprobability_moss(
    qc,
    sigma_vo_eff,
    Rf,
    CSR,
    CSR_star,
    Pa=100.0,
    delta_qc_override=nan,
    c_override=nan,
    x1=0.78,
    x2=-0.33,
    y1=-0.32,
    y2=-0.35,
    y3=0.49,
    z1=1.21,
    **kwargs,
)
```

Calculates the probability of liquefaction according to Moss et al. The cone tip resistance is normalised to a standard effective overburden pressure of 100kPa.

The liquefaction probability is based on a database of case studies using Bayesian updating. The probability contours are digitised from the published figure and interpolation between the different values of normalised tip resistance for a given CSR is performed.

The calculation of the normalisation exponent $c$ is performed iteratively, or an override can be specified. While a normalisation exponent of 0.5 is generally assumed, performing the calculation results in a much better statistical fit.

Soils with an increased friction ratio shows less potential for liquefaction. This is accounted for by modifying the normalised cone resistance using the friction ratio. The bound for modifying the friction ratio are 0.5 - 5%. Below 0.5%, there is no correction and above 5%, the correction for Rf=5% is applied.

It should also be noted that the correlation is based on averaged cone resistance values from field cases. So it applied to raw cone resistance data, they might be too conservative.

$$
q_{c,1} = q_c \left( \frac{p_a}{\sigma_{vo}^{\prime}} \right)^{c}
$$

$$
c = f_1 \cdot \left( \frac{R_f}{f_3} \right)^{f_2}
$$

$$
f_1 = x_1 \cdot q_c^{x_2}
$$

$$
f_2 = -(y_1 \cdot q_c^{y_2} + y_3 )
$$

$$
f_3 = abs( \log_{10}(10 + q_c )^{z_1}
$$

$$
\Delta q_c = \alpha_1 \cdot \ln (CSR) + \alpha_2
$$

$$
\alpha_1 = 0.38 \cdot R_f - 0.19
$$

$$
\alpha_2 = 1.46 \cdot R_f - 0.73
$$

![Contours of liquefaction probability according to Moss et al (2006)](/docs/assets/groundhog/docs/soildynamics/images/liquefactionprobability_moss_1.png)

*Contours of liquefaction probability according to Moss et al (2006)*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc` | MPa | 0.0 <= qc <= 120.0 | required | Cone tip resistance ($q_c$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Vertical effective stress at depth of interest ($\sigma_{vo}^{\prime}$) |
| `Rf` | pct | 0.0 <= Rf <= 10.0 | required | Friction ratio ($R_f$) |
| `CSR` | - | 0.0 <= CSR <= 0.6 | required | Cyclic shear stress ratio ($CSR$) |
| `CSR_star` | - | 0.0 <= CSR_star <= 0.6 | required | Equivalent uniform cyclic stress ratio (for magnitude 7.5 event) ($CSR^{*}$) |
| `Pa` | kPa | 90.0 <= Pa <= 110.0 | `100.0` | Atmospheric pressure ($p_a$) |
| `delta_qc_override` | MPa |  | `nan` | Override for the correction to the normalised cone tip resistance ($\Delta q_c$) |
| `c_override` | - |  | `nan` | Override for the normalisation exponent ($c$) |
| `x1` | - |  | `0.78` | Factor x1 ($x_1$) |
| `x2` | - |  | `-0.33` | Factor x2 ($x_2$) |
| `y1` | - |  | `-0.32` | Factor y1 ($y_1$) |
| `y2` | - |  | `-0.35` | Factor y2 ($y_2$) |
| `y3` | - |  | `0.49` | Factor y3 ($y_3$) |
| `z1` | - |  | `1.21` | Factor z1 ($z_1$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Pl [pct]` | pct | Liquefaction probability ($P_L$) |
| `qc_5 [MPa]` | MPa | Cone tip resistance for 5% probability of liquefaction ($q_{c,P_{L,5\%}}$) |
| `qc_95 [MPa]` | MPa | Cone tip resistance for 95% probability of liquefaction ($q_{c,P_{L,95\%}}$) |
| `qc1 [MPa]` | MPa | Normalised cone tip resistance ($q_{c,1}$) |
| `qc1mod [MPa]` | MPa | Modified normalised cone tip resistance ($q_{c,1} + \Delta q_c$) |
| `c [-]` | - | Normalisation exponent |

**References**

- Moss et al (2006) CPT-Based Probabilistic and Deterministic Assessment of In Situ Seismic Soil Liquefaction Potential. Journal of Geotechnical & Geoenvironmental Engineering, 132(8)

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="liquefactionprobability_saye"></a>

## `liquefactionprobability_saye`

<span class="gc-badge gc-available" data-geocore-function="liquefactionprobability_saye">Available in GeoCore</span> [Soil dynamics › Liquefaction › Saye (2017) Liquefaction Probability](/docs/geocore/using/modules#liquefactionprobability_saye)

```python
liquefactionprobability_saye(
    Qt,
    qc,
    sigma_vo_eff,
    CSR,
    fs,
    atmospheric_pressure=100.0,
    deltaQ_nominator=10.0,
    deltaQ_denominator=0.67,
    exponent_qcnormalised=0.5,
    Cq_limit=1.7,
    mcrr_coefficient1=178.0,
    mcrr_coefficient2=3.349,
    mcrr_limit=0.1,
    deltaQ_limit=20.0,
    Pl_coefficient1=1.34,
    exactsoildata=True,
    **kwargs,
)
```

Current engineering practice employs clean sand-based procedures to evaluate liquefaction triggering in nonplastic, coarse-grained soils and low-plasticity, fine-grained soils below level or mildly-sloping ground. Furthermore, existing empirical liquefaction triggering procedures treat all clean sands (fines content <5%) as identical.

Saye et al propose an alternative approach in which the slope of the CPT data in Qt vs fs/sigma_voprime space is used to assess the liquefaction probability. This approach has been shown to produce more meaningful results in soils with significant fines content

$$
\Delta_Q = \frac{Q_t + 10}{\frac{f_s}{\sigma_{vo}^{\prime}} + 0.67}
$$

$$
\hat{m}_{CRR} = \frac{\hat{\Delta}_Q}{178 \cdot \hat{\Delta}_Q - 3.349} \leq 0.1 \ \text{for} \ \Delta_Q \geq 20
$$

$$
\frac{q_{c1}}{P_a} = C_q \cdot \left( \frac{q_c}{P_a} \right)
$$

$$
C_q = \left( \frac{P_a}{\sigma_{vo}^{\prime}} \right)^n \leq 1.7
$$

$$
P_L = \Phi \left[ - \frac{ \left( \hat{m}_{CRR} \cdot \left( \frac{q_{c1}}{P_a} \right) - 1.34 \right) - \log_{10} \left(  CSR_{7.5} \right) }{\sigma} \right]
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `Qt` | - | 1.0 <= Qt <= 1000.0 | required | Normalised cone tip resistance ($Q_t$) |
| `qc` | MPa | 0.0 <= qc <= 100.0 | required | Cone tip resistance ($q_c$) |
| `sigma_vo_eff` | kPa | 0.0 <= sigma_vo_eff <= 1000.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `CSR` | - | 0.0 <= CSR <= 1.0 | required | Cyclic stress ratio for magnitude 7.5 event ($CSR_{7.5}$) |
| `fs` | MPa | 0.0 <= fs <= 10.0 | required | Sleeve friction ($f_s$) |
| `atmospheric_pressure` | kPa |  | `100.0` | Atmospheric pressure ($P_a$) |
| `deltaQ_nominator` | - |  | `10.0` | Term in the nominator for deltaQ |
| `deltaQ_denominator` | - |  | `0.67` | Term in the denominator for deltaQ |
| `exponent_qcnormalised` | - |  | `0.5` | Exponent in the normalisation for qc ($n$) |
| `Cq_limit` | - |  | `1.7` | Maximum value for Cq |
| `mcrr_coefficient1` | - |  | `178.0` | First calibration coefficient in the formula for mCRR |
| `mcrr_coefficient2` | - |  | `3.349` | Second calibration coefficient in the formula for mCRR |
| `mcrr_limit` | - |  | `0.1` | Maximum value for mCRR |
| `deltaQ_limit` | - |  | `20.0` | Minimum value for DeltaQ |
| `Pl_coefficient1` | - |  | `1.34` | Coefficient in the equation for liquefaction probability |
| `exactsoildata` |  |  | `True` | Boolean determining whether the standard deviation for exact or uncertain soil data needs to be used |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `DeltaQ [-]` | - | Value for DeltaQ ($\Delta_Q$) |
| `qc1 [-]` | - | Normalised cone tip resistance ($q_{c1}$) |
| `Cq [-]` | - | Value for multiplier in qc normalisation ($C_q$) |
| `mCRR [-]` | - | Median estimate for mCRR, slope in graph of normalised cone resistance vs CSR ($\hat{m}_{CRR}$) |
| `PL [-]` | - | Estimated liquefaction probability based on the common origin approach ($P_L$) |

**References**

- Saye, Steven R., Scott M. Olson, and Kevin W. Franke. "Common-Origin Approach to Assess Level-Ground Liquefaction Susceptibility and Triggering in CPT-Compatible Soils Using Δ Q." Journal of Geotechnical and Geoenvironmental Engineering 147.7 (2021): 04021046.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="cyclicstressratio_youd"></a>

## `cyclicstressratio_youd`

<span class="gc-badge gc-available" data-geocore-function="cyclicstressratio_youd">Available in GeoCore</span> [Soil dynamics › Liquefaction › Youd (2001) Cyclic Stress Ratio](/docs/geocore/using/modules#cyclicstressratio_youd)

```python
cyclicstressratio_youd(
    acceleration,
    sigma_vo,
    sigma_vo_eff,
    depth,
    magnitude,
    gravity=9.81,
    msf_exponent_nominator=2.24,
    msf_exponent_denominator=2.56,
    rd_factor1=1.0,
    rd_factor2=0.00765,
    rd_factor3=1.174,
    rd_factor4=0.0267,
    rd_transitiondepth=9.15,
    rd_maxdepth=23.0,
    **kwargs,
)
```

Calculates the cyclic stress ratio adjusted to a magnitude 7.5 earthquake using the simplified equation (Seed and Idriss 1971; Whitman 1971) and the adjustments recommended by Youd et al. (2001).

This formulation is used in the common-origin approach by Saye et al (2021) to calculate the adjusted cyclic shear stress ratio for assessment of liquefaction probability.

$$
CSR_{7.5} = \frac{CSR}{MSF} = \frac{\tau_{avg} / \sigma_{vo}^{\prime}}{MSF} = \frac{0.65 \cdot \left(
\frac{a_{max}}{g} \right) \cdot \left( \frac{\sigma_{vo}}{\sigma_{vo}^{\prime}} \right) \cdot r_d}{MSF}
$$

$$
MSF = \frac{10^{2.24}}{M^{2.56}}
$$

$$
r_d = \begin{cases}
    1.0 - 0.00765 \cdot z, & \text{for } z < 9.15m \\
    1.174 - 0.0267 \cdot z, & \text{for } 9.15m \leq z < 23m
\end{cases}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `acceleration` | m/s2 | acceleration >= 0.0 | required | Maximum horizontal acceleration at the soil surface ($a_{max}$) |
| `sigma_vo` | kPa | 0.0 <= sigma_vo <= 500.0 | required | Vertical total stress at the depth considered ($\sigma_{vo}$) |
| `sigma_vo_eff` | kPa | 0.0 <= sigma_vo_eff <= 250.0 | required | Vertical effective stress at the depth considered ($\sigma_{vo}^{\prime}$) |
| `depth` | m | 0.0 <= depth <= 23.0 | required | Depth considered for the assessment ($z$) |
| `magnitude` | - | 0.0 <= magnitude <= 8.5 | required | Earthquake magnitude ($M$) |
| `gravity` | m/s2 | 9.8 <= gravity <= 10.0 | `9.81` | Acceleration due to gravity ($g$) |
| `msf_exponent_nominator` | - |  | `2.24` | Exponent in the nominator of the equation for MSF |
| `msf_exponent_denominator` | - |  | `2.56` | Exponent in the denominator of the equation for MSF |
| `rd_factor1` | - |  | `1.0` | First calibration factor for shallow portion of rd |
| `rd_factor2` | - |  | `0.00765` | Second calibration factor for shallow portion of rd |
| `rd_factor3` | - |  | `1.174` | First calibration factor for deep portion of rd |
| `rd_factor4` | - |  | `0.0267` | Second calibration factor for deep portion of rd |
| `rd_transitiondepth` | - |  | `9.15` | Transition depth for rd |
| `rd_maxdepth` | - |  | `23.0` | Max depth for rd |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `CSR [-]` | - | Cyclic stress ratio (uncorrected) ($CSR$) |
| `CSR* [-]` | - | Cyclic stress ratio corrected to 7.5 magnitude event ($CSR_{7.5}$) |
| `MSF [-]` | - | Magnitude scaling factor ($MSF$) |
| `rd [-]` | - | Depth reduction factor ($r_d$) |

**References**

- Youd, T. L., et al. 2001. Liquefaction resistance of soils: Summary report from the 1996 NCEER and 1998 NCEER=NSF workshops on evaluation of liquefaction resistance of soils.” J. Geotech. Geoenviron. Eng. 127 (10): 817–833. https://doi.org/10.1061/(ASCE)1090-0241(2001)127:10(817).

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
