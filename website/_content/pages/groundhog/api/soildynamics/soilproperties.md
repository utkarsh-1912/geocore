---
title: Dynamic soil property correlations
slug: groundhog/api/soildynamics/soilproperties
section: Groundhog API Reference
description: 'API reference for groundhog.soildynamics.soilproperties: 4 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/soildynamics/soilproperties.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.soildynamics.soilproperties
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/soildynamics/soilproperties.html
geocore_available: true
geocore_functions:
- dampingratio_sandgravel_seed
- gmax_shearwavevelocity
- modulusreduction_darendeli
- modulusreduction_plasticity_ishibashi
---

Module `groundhog.soildynamics.soilproperties` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/soildynamics/soilproperties.py).

Upstream documentation: [Dynamic soil property correlations](https://groundhog.readthedocs.io/en/main/soildynamics/soilproperties.html).

**Functions:** [`modulusreduction_plasticity_ishibashi`](#modulusreduction_plasticity_ishibashi), [`gmax_shearwavevelocity`](#gmax_shearwavevelocity), [`dampingratio_sandgravel_seed`](#dampingratio_sandgravel_seed), [`modulusreduction_darendeli`](#modulusreduction_darendeli)

<a id="modulusreduction_plasticity_ishibashi"></a>

## `modulusreduction_plasticity_ishibashi`

<span class="gc-badge gc-available" data-geocore-function="modulusreduction_plasticity_ishibashi">Available in GeoCore</span> [Soil dynamics › Dynamic soil property correlations › Ishibashi & Zhang (1993) Modulus Reduction](/docs/geocore/using/modules#modulusreduction_plasticity_ishibashi)

```python
modulusreduction_plasticity_ishibashi(
    strain,
    pi,
    sigma_m_eff,
    multiplier_1=0.000102,
    exponent_1=0.492,
    multiplier_2=0.000556,
    exponent_2=0.4,
    multiplier_3=-0.0145,
    exponent_3=1.3,
    **kwargs,
)
```

Calculates the modulus reduction curve (G/Gmax) as a function of shear strain. The curve depends on the plasticity of the material (plasticity index) and the mean effective stress at the depth of interest.

The curve for cohesionless soils can be established by using a plasticity index of 0. At low plasticity, the effect of confining pressure on the modulus reduction curve is more pronounced.

Also calculates the damping ratio of plastic and non-plastic soils based on a fit to empirical data.

$$
\frac{G}{G_{max}} = K \left( \gamma, \text{PI} \right) \left( \sigma_m^{\prime} \right)^{m \left( \gamma, \text{PI} \right) - m_0}
$$

$$
K \left( \gamma, \text{PI} \right) = 0.5 \left[ 1 + \tanh \left[ \ln \left( \frac{0.000102 + n ( \text{PI} )}{\gamma} \right)^{0.492} \right] \right]
$$

$$
m \left( \gamma, \text{PI} \right) - m_0 = 0.272 \left[ 1 - \tanh \left[ \ln \left( \frac{0.000556}{\gamma} \right)^{0.4} \right] \right] \exp \left( -0.0145 \text{PI}^{1.3} \right)
$$

$$
n ( \text{PI} ) = \begin{cases}
    0.0       & \quad \text{for PI } = 0 \\
    3.37 \times 10^{-6} \text{PI}^{1.404}  & \quad \text{for } 0 < \text{PI} \leq 15 \\
    7.0 \times 10^{-7} \text{PI}^{1.976}  & \quad \text{for } 15 < \text{PI} \leq 70 \\
    2.7 \times 10^{-5} \text{PI}^{1.115}  & \quad \text{for } \text{PI} > 70
  \end{cases}
$$

$$
\xi = 0.333 \frac{1 + \exp(-0.0145 PI^{1.3})}{2} \left[ 0.586 \left( \frac{G}{G_{max}} \right)^2 - 1.547 \frac{G}{G_{max}} + 1 \right]
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `strain` | pct | 0.0 <= strain <= 10.0 | required | Strain amplitude ($\gamma$) |
| `pi` |  | 0.0 <= pi <= 200.0 | required | No upstream documentation. |
| `sigma_m_eff` | kPa | 0.0 <= sigma_m_eff <= 400.0 | required | Mean effective pressure ($\sigma_m^{\prime}$) |
| `multiplier_1` | - |  | `0.000102` | Multiplier in equation for K |
| `exponent_1` | - |  | `0.492` | Exponent in equation for K |
| `multiplier_2` | - |  | `0.000556` | First multiplier in equation for m |
| `exponent_2` | - |  | `0.4` | First exponent in equation for m |
| `multiplier_3` | - |  | `-0.0145` | Second multiplier in equation for m |
| `exponent_3` | - |  | `1.3` | Second exponent in equation for m |
| `PI` | pct | 0.0 <= PI <= 200.0 |  | Plasticity index ($PI$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `G/Gmax [-]` | - | Modulus reduction ratio ($G / G_{max}$) |
| `K [-]` | - | Factor K in the equation ($K ( \gamma, \text{PI} )$) |
| `m [-]` | - | Exponent m in the equation ($m \left( \gamma, \text{PI} \right) - m_0$) |
| `n [-]` | - | Factor n in equations ($n ( \text{PI} )$) |
| `dampingratio [pct]` | pct | Damping ratio ($\xi$) |

**References**

- Ishibashi, I., & Zhang, X. (1993). Unified dynamic shear moduli and damping ratios of sand and clay. Soils and foundations, 33(1), 182-191.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="gmax_shearwavevelocity"></a>

## `gmax_shearwavevelocity`

<span class="gc-badge gc-available" data-geocore-function="gmax_shearwavevelocity">Available in GeoCore</span> [Soil dynamics › Dynamic soil property correlations › Gmax from Shear Wave Velocity](/docs/geocore/using/modules#gmax_shearwavevelocity)

```python
gmax_shearwavevelocity(Vs, gamma, g=9.81, **kwargs)
```

Calculates the small-strain shear modulus (shear strain < 1e-4%) from the shear wave velocity and the bulk unit weight if the soil based on elastic theory.

Often, the result of an in-situ or laboratory test will provide the shear wave velocity, which is then converted to the small-strain shear modulus using this function.

$$
G_{max} = \rho \cdot V_s^2
$$

$$
\rho = \gamma / g
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `Vs` | m/s | 0.0 <= Vs <= 600.0 | required | Shear wave velocity ($V_s$) |
| `gamma` | kN/m3 | 12.0 <= gamma <= 22.0 | required | Bulk unit weight ($\gamma$) |
| `g` | m/s2 | 9.7 <= g <= 10.2 | `9.81` | Acceleration due to gravity ($g$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `rho [kg/m3]` | kg/m3 | Density of the material ($\rho$) |
| `Gmax [kPa]` | kPa | Small-strain shear modulus ($G_{max}$) |

**References**

- Robertson, P.K. and Cabal, K.L. (2015). Guide to Cone Penetration Testing for Geotechnical Engineering. 6th edition. Gregg Drilling & Testing, Inc.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="dampingratio_sandgravel_seed"></a>

## `dampingratio_sandgravel_seed`

<span class="gc-badge gc-available" data-geocore-function="dampingratio_sandgravel_seed">Available in GeoCore</span> [Soil dynamics › Dynamic soil property correlations › Seed & Idriss (1970) Damping Ratio](/docs/geocore/using/modules#dampingratio_sandgravel_seed)

```python
dampingratio_sandgravel_seed(cyclic_shear_strain, **kwargs)
```

Damping ratios for sand are compiled from a dataset comprising several sands and gravels. Average values and upper and lower bounds are provided. The comparison of the trends proposed for sand with the datapoints measured on gravel suggests that the trend is applicable for gravels too.

![Proposed trends and measurement data on gravels](/docs/assets/groundhog/docs/soildynamics/images/dampingratio_sandgravel_seed_1.png)

*Proposed trends and measurement data on gravels*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `cyclic_shear_strain` | pct | 0.0001 <= cyclic_shear_strain <= 1.0 | required | Cyclic shear strain ($\gamma_{cyc}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `D LE [pct]` | pct | Low estimate damping ratio ($D_{LE}$) |
| `D BE [pct]` | pct | Average or best estimate damping ratio ($D_{BE}$) |
| `D HE [pct]` | pct | High estimate damping ratio ($D_{HE}$) |

**References**

- Seed, H. B., Wong, R. T., Idriss, I. M., & Tokimatsu, K. (1986). Moduli and damping factors for dynamic analyses of cohesionless soils. Journal of geotechnical engineering, 112(11), 1016-1032.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="modulusreduction_darendeli"></a>

## `modulusreduction_darendeli`

<span class="gc-badge gc-available" data-geocore-function="modulusreduction_darendeli">Available in GeoCore</span> [Soil dynamics › Dynamic soil property correlations › Darendeli (2001) Modulus Reduction](/docs/geocore/using/modules#modulusreduction_darendeli)

```python
modulusreduction_darendeli(
    mean_effective_stress,
    pi,
    ocr,
    N,
    frequency,
    soiltype,
    min_strain=0.0001,
    max_strain=1.0,
    no_points=250,
    custom_coefficients=None,
    **kwargs,
)
```

Darendeli (2001) proposed a comprehensive framework for estimating the modulus reduction curve and damping curve for sand, fine sand, silt and clay based on extensive laboratory testing. The framework is initially based on the work by Hardin and Drnevich but extends the formulation to include the effect of soil type, plasticity, overconsolidation ratio, stress ratio, loading frequency and number of cycles applied.

The author used a Bayesian approach to calibrate the parameters of the parametric equations and also formulated expressions to estimate the standard deviation on the estimates. Parameters for individual soil types can be used as well as parameters calibrated to the entire credible dataset (using `'all'` for `soiltype`).

The formulation is based on Masing damping but takes into account the damping at small strains, which  is not zero but difficult to estimate from resonant column or cyclic DSS tests. The Masing damping at large strains is also adjusted to be in line with experimental observations (Masing damping overestimates the damping ratio at large strains).

$$
\frac{G}{G_{max}} = \frac{1}{1 + \left( \frac{\gamma}{\gamma_r} \right)^a}
$$

$$
\gamma_r = \left( \phi_1 + \phi_2 \cdot PI \cdot OCR^{\phi_3} \right) \cdot \sigma_0^{\prime \phi_4}
$$

$$
a = \phi_5
$$

$$
D_{\text{adjusted}} = b \cdot \left( \frac{G}{G_{max}} \right)^{0.1} \cdot D_{\text{Masing}} + D_{\text{min}}
$$

$$
D_{\text{min}} = \left( \phi_6 + \phi_7 \cdot PI \cdot OCR^{\phi_8} \right) \cdot \sigma_0^{\prime \phi_9} \cdot \left[1 + \phi_{10} \cdot \ln(f) \right]
$$

$$
b = \phi_{11} + \phi_{12} \cdot \ln(N)
$$

$$
\sigma_{\text{NG}} = \exp(\phi_{13}) + \sqrt{\frac{0.25}{\exp(\phi_{14})} - \frac{\left(G / G_{max} - 0.5 \right)^2}{\exp(\phi_{14})}}
$$

$$
\sigma_D = \exp (\phi_{15} ) + \exp (\phi_{16} ) \cdot \sqrt{D}
$$

$$
\rho_{i,j} = \exp \left( \frac{-1}{\exp ( \phi_{17} )} \right) \cdot \exp \left( \frac{- | \ln \gamma_i - \ln \gamma_j |}{\exp ( \phi_{18} )} \right)
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `mean_effective_stress` | kPa | 0.0 <= mean_effective_stress <= 1000.0 | required | Mean effective stress at the depth under consideration ($\sigma_0^{\prime}$) |
| `pi` | pct | 0.0 <= plasticity_index <= 60.0 | required | Plasticity index (difference between liquid limit and plastic limit) ($PI$) |
| `ocr` | - | 1.0 <= OCR <= 20.0 | required | Overconsolidation ratio of the soil ($OCR$) |
| `N` | - | N >= 1.0 | required | Number of cycles ($N$) |
| `frequency` | Hz | 0.05 <= frequency <= 20.0 | required | Loading frequency ($f$) |
| `soiltype` |  | one of `sand`, `fine sand`, `silt`, `clay`, `all` | required | Soil type used for calculating modulus reduction and damping curves - Options: ('sand', 'fine sand', 'silt', 'clay', 'all') |
| `min_strain` | pct |  | `0.0001` | Minimum value for the strain ($\gamma_{min}$) |
| `max_strain` | pct |  | `1.0` | Maximum value for the strain ($\gamma_{max}$) |
| `no_points` | - | no_points >= 10.0 | `250` | Number of points used for the strain curve calculation |
| `custom_coefficients` | - |  | `None` | Dictionary with custom calibration coefficients (optional, default= None)- Elementtype: float, order: ascending, unique: True, empty entries allowed: False |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `strains [pct]` | pct | List of strains for the modulus reduction curve ($\gamma$) |
| `G/Gmax [-]` | - | Modulus ratio for given strains ($G / G_{max}$) |
| `D [pct]` | pct | Damping ratios for given strains ($D$) |
| `sigma_ND [-]` | - | Standard deviation for the modulus reduction curve ($\sigma_{ND}$) |
| `sigma_D [pct]` | pct | Standard deviation for the damping curve ($\sigma_D$) |

**References**

- Darendeli, M. B. (2001). Development of a new family of normalized modulus reduction and material damping curves. The university of Texas at Austin.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
