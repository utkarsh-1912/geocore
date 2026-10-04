---
title: Cohesionless soils
slug: groundhog/api/siteinvestigation/correlations/cohesionless
section: Groundhog API Reference
description: 'API reference for groundhog.siteinvestigation.correlations.cohesionless: 4 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/siteinvestigation/correlations/cohesionless.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.siteinvestigation.correlations.cohesionless
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/site_investigation/cohesionless.html
geocore_available: true
geocore_functions:
- gmax_sand_hardinblack
- hssmall_parameters_sand
- permeability_d10_hazen
- stress_dilatancy_bolton
---

Module `groundhog.siteinvestigation.correlations.cohesionless` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/siteinvestigation/correlations/cohesionless.py).

Upstream documentation: [Cohesionless soils](https://groundhog.readthedocs.io/en/main/site_investigation/cohesionless.html).

**Functions:** [`gmax_sand_hardinblack`](#gmax_sand_hardinblack), [`permeability_d10_hazen`](#permeability_d10_hazen), [`hssmall_parameters_sand`](#hssmall_parameters_sand), [`stress_dilatancy_bolton`](#stress_dilatancy_bolton)

<a id="gmax_sand_hardinblack"></a>

## `gmax_sand_hardinblack`

<span class="gc-badge gc-available" data-geocore-function="gmax_sand_hardinblack">Available in GeoCore</span> [Site investigation › Correlations: Cohesionless soils › Hardin & Black (1968) Gmax for Sand](/docs/geocore/using/modules#gmax_sand_hardinblack)

```python
gmax_sand_hardinblack(sigma_m0, void_ratio, coefficient_B=875.0, pref=100.0, **kwargs)
```

Calculates the small-strain shear modulus of sand based on the correlation proposed with initial void ratio and stress level suggested by Hardin and Black (1968).

The formulation was developed on a dataset of cohesive soils. However, the correlation was used in the PISA project to predict the small-strain shear modulus of sand.

The default calibration parameter is taken from the recent study on monopile lateral response for the PISA project (Taborda et al, 2019). This calibration applies for dense marine sand.

$$
G_{max} = \frac{B p_{ref}^{\prime}}{0.3 + 0.7 e_0^2} \sqrt{\frac{p^{\prime}}{p_{ref}^{\prime}}}
$$

Taborda, D.M.G., Zdravković, L., Potts, D.M., Burd, H.J., Byrne, B.W., Gavin, K., Houlsby, G.T., Jardine, R.J., Liu, T., Martin, C.M. and McAdam, R.A. 2018. Finite element modelling of laterally loaded piles in a dense marine sand at Dunkirk. Géotechnique, https://doi.org/10.1680/jgeot.18.pisa.006

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `sigma_m0` | kPa | 0.0 <= sigma_m0 <= 500.0 | required | Mean effective stress ($p^{\prime}$) |
| `void_ratio` | - | 0.0 <= void_ratio <= 4.0 | required | In-situ void ratio of the sand ($e_0$) |
| `coefficient_B` | - |  | `875.0` | Calibration coefficient ($B$) |
| `pref` | kPa |  | `100.0` | Reference pressure ($p_{ref}^{\prime}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Gmax [kPa]` | kPa | Small-strain shear modulus ($G_{max}$) |

**References**

- Hardin, B.O. and Black W.L. 1968. Vibration modulus of normally consolidated clay Journal of Soil Mechanics and Foundations Div, 94(SM2), 353-369.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="permeability_d10_hazen"></a>

## `permeability_d10_hazen`

<span class="gc-badge gc-available" data-geocore-function="permeability_d10_hazen">Available in GeoCore</span> [Site investigation › Correlations: Cohesionless soils › Hazen Permeability (from D10)](/docs/geocore/using/modules#permeability_d10_hazen)

```python
permeability_d10_hazen(grain_size, coefficient_C=0.01, **kwargs)
```

Calculates the permeability of a granular soil based on its grain size. Extensive investigation has shown that the fine particles have the greatest influence on permeability since they fill the voids between larger grains. The correlation by Hazen (1892) uses the 10th percentile grain size. Other authors have argues that the 5th percentile would be a better choice.

$$
k = C_{10} \cdot D_{10}^2
$$

![Data supporting the Hazen correlation](/docs/assets/groundhog/docs/site_investigation/images/permeability_d10_hazen_1.png)

*Data supporting the Hazen correlation*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `grain_size` | mm | 0.01 <= grain_size <= 2.0 | required | Grain size for which 10% of the particles are finer ($D_{10}$) |
| `coefficient_C` | - |  | `0.01` | Calibration coefficient containing the effect of the shape of pore channels ($C_{10)$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `k [m/s]` | m/s | Permeability of the granular soil ($k$) |

**References**

- Terzaghi, K., Peck, R. B., & Mesri, G. (1996). Soil mechanics in engineering practice. John Wiley & Sons.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="hssmall_parameters_sand"></a>

## `hssmall_parameters_sand`

<span class="gc-badge gc-available" data-geocore-function="hssmall_parameters_sand">Available in GeoCore</span> [Site investigation › Correlations: Cohesionless soils › HS Small Parameters (from Relative Density)](/docs/geocore/using/modules#hssmall_parameters_sand)

```python
hssmall_parameters_sand(relative_density, **kwargs)
```

Calculates the constitutive parameters for the HS Small model in PLAXIS as a function of relative density.

The formulae were calibrated against a high-quality laboratory testing dataset on Toyoura, Ham River, Hostun and Ticino sand.

$$
\gamma_{unsat} = 15 + 4 \cdot \frac{D_r}{100}
$$

$$
\gamma_{sat} = 19 + 1.6 \cdot \frac{D_r}{100}
$$

$$
E_{50}^{ref} = 6e4 \cdot \frac{D_r}{100}
$$

$$
E_{oed}^{ref} = 6e4 \cdot \frac{D_r}{100}
$$

$$
E_{ur}^{ref} = 18e4 \cdot \frac{D_r}{100}
$$

$$
G_0^{ref} = 6e4 + 6.8e4 \frac{D_r}{100}
$$

$$
m = 0.7 - \frac{D_r}{320}
$$

$$
\gamma_{0.7}= 10^{-4} \cdot \left( 2 - \frac{D_r}{100} \right)
$$

$$
\varphi^{\prime} = 28 + 12.5 \cdot \frac{D_r}{100}
$$

$$
\psi = -2 + 12.5 \cdot \frac{D_r}{100}
$$

$$
R_f = 1 - \frac{D_r}{800}
$$

![HS Small parameters as a function of relative density](/docs/assets/groundhog/docs/site_investigation/images/hssmall_parameters_sand_1.png)

*HS Small parameters as a function of relative density*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `relative_density` | pct | 10.0 <= relative_density <= 100.0 | required | Relative density of sand ($D_r$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `gamma_unsat [kN/m3]` | kN/m3 | Unsaturated unit weight ($\gamma_{unsat}$) |
| `gamma_sat [kN/m3]` | kN/m3 | Saturated unit weight ($\gamma_{sat}$) |
| `E50_ref [kPa]` | kPa | Reference secant stiffness ($E_{50}^{ref}$) |
| `Eoed_ref [kPa]` | kPa | Reference oedometric stiffness ($E_{oed}^{ref}$) |
| `Eur_ref [kPa]` | kPa | Reference unloading-reloading stiffness ($E_{ur}^{ref}$) |
| `G0_ref [kPa]` | kPa | Reference small-strain shear modulus ($G_{0}^{ref}$) |
| `m [-]` | - | Stiffness exponent ($m$) |
| `gamma_07 [-]` | - | Strain level where shear modulus has reduced to 70 percent of Gmax ($\gamma_{0.7}$) |
| `phi_eff [deg]` | deg | Effective friction angle ($\varphi^{\prime}$) |
| `psi [deg]` | deg | Dilation angle ($\psi$) |
| `Rf [-]` | - | Failure ratio ($-$) |

**References**

- Brinkgreve, R. B. J., Engin, E., & Engin, H. K. (2010). Validation of empirical formulas to derive model parameters for sands. Numerical methods in geotechnical engineering, 137- 142.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="stress_dilatancy_bolton"></a>

## `stress_dilatancy_bolton`

<span class="gc-badge gc-available" data-geocore-function="stress_dilatancy_bolton">Available in GeoCore</span> [Site investigation › Correlations: Cohesionless soils › Bolton Stress–Dilatancy Relation](/docs/geocore/using/modules#stress_dilatancy_bolton)

```python
stress_dilatancy_bolton(
    relative_density,
    p_eff,
    Q=10,
    R=1,
    stress_condition='triaxial strain',
    **kwargs,
)
```

Cohesionless soils with sufficiently high relative density will tend to dilate but dilation can be suppressed by the stress on the sample. The higher the stress, the lower the amount of dilation. Bolton (1986) formulated relations to calculated the difference between peak friction angle and critical state friction angle based on a series of plane strain and triaxial tests. A relative dilatancy index ($I_R$) is defined which has allows prediction of the dilation angle for plane strain and triaxial strain. This function predicts the value of the relative dilatancy index based on user input and applies this to calculate the difference between peak and residual friction angle, dilation angle and the maximum ratio of volumetric strain increment to first principal strain increment for a selected stress condition (plane strain or triaxial strain). The calibration factors in the equation for relative dilatancy index can be adjusted (e.g. for crushable soils). Note that the formulae apply for $0 < I_R < 4$.

$$
I_R = D_r \left( Q - \ln p^{\prime} \right) - R
$$

$$
\varphi_{max}^{\prime} - \varphi_{crit}^{\prime} = 0.8 \phi_{max} = 5 I_R \ \ \text{plane strain}
$$

$$
\varphi_{max}^{\prime} - \varphi_{crit}^{\prime} = 3 I_R \ \ \text{triaxial strain}
$$

$$
\left( - \frac{d \epsilon_v}{d \epsilon_1} \right)_{max} = 0.3 I_R
$$

![Stress-dilatancy theory applied to selected tests (Bolton, 1986)](/docs/assets/groundhog/docs/site_investigation/images/data_bolton.png)

*Stress-dilatancy theory applied to selected tests (Bolton, 1986)*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `relative_density` | - | 0.1 <= relative_density <= 1.0 | required | Relative density of the material ($D_{r)$) |
| `p_eff` | kPa | 20 <= p_eff <= 10000. In the discussion following the paper publication, a remark was made that using a minimum value of 150kPa for the effective pressure is prudent | required | Effective pressure ($p_{eff)^{\prime}$) |
| `Q` |  | 5 <= Q <= 10 | `10` | First calibration factor in the equation for relative dilatancy index (optional: Default = 10 for quartz and feldspar sands, See Table 2 in Bolton's paper for other grain types) ($Q$) |
| `R` |  |  | `1` | Second calibration factor in the equation for relative dilatancy index (optional: Default = 1) ($R$) |
| `stress_condition` |  | one of `triaxial strain`, `plane strain` | `'triaxial strain'` | Assumed stress condition: Choose between `'triaxial strain'` and `'plane strain'` |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Ir [-]` | - | Relative dilatancy index [-] ($I_R$) |
| `phi_max - phi_cs [deg]` | deg | Difference between peak and critical state friction angle [deg] ($\varphi_{max}^{\prime} - \varphi_{crit}^{\prime}$) |
| `Dilation angle [deg]` | deg | Calculated dilation angle for the selected stress condition [deg] ($\psi$) |
| `-depsilon_v/depsilon_1__max [-]` | - | Maximum ratio of volumetric to first principal strain increment [-] ($\left( - \frac{d \epsilon_v}{d \epsilon_1} \right)_{max}$) |

**References**

- Bolton, M. D. "The strength and dilatancy of sands." Geotechnique 36.1 (1986): 65-78.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
