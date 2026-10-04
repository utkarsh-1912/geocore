---
title: All soil types
slug: groundhog/api/siteinvestigation/correlations/general
section: Groundhog API Reference
description: 'API reference for groundhog.siteinvestigation.correlations.general: 3 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/siteinvestigation/correlations/general.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.siteinvestigation.correlations.general
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/site_investigation/correlations_general.html
geocore_available: true
geocore_functions:
- acousticimpedance_bulkunitweight_chen
- k0_frictionangle_mesri
- shearwavevelocity_compressionindex_cha
---

Module `groundhog.siteinvestigation.correlations.general` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/siteinvestigation/correlations/general.py).

Upstream documentation: [All soil types](https://groundhog.readthedocs.io/en/main/site_investigation/correlations_general.html).

**Functions:** [`acousticimpedance_bulkunitweight_chen`](#acousticimpedance_bulkunitweight_chen), [`shearwavevelocity_compressionindex_cha`](#shearwavevelocity_compressionindex_cha), [`k0_frictionangle_mesri`](#k0_frictionangle_mesri)

<a id="acousticimpedance_bulkunitweight_chen"></a>

## `acousticimpedance_bulkunitweight_chen`

<span class="gc-badge gc-available" data-geocore-function="acousticimpedance_bulkunitweight_chen">Available in GeoCore</span> [Site investigation › Correlations: All soil types › Chen Acoustic Impedance–Porosity Correlation](/docs/geocore/using/modules#acousticimpedance_bulkunitweight_chen)

```python
acousticimpedance_bulkunitweight_chen(
    bulkunitweight,
    specific_gravity=2.65,
    saturation=1.0,
    gamma_w=10.0,
    calibration_factor_4=0.0001315,
    calibration_factor_3=-0.03776,
    calibration_factor_2=4.201,
    calibration_factor_1=-245.0,
    calibration_factor_0=8603.0,
    **kwargs,
)
```

Several authors have researched the correlation between porosity and acoustic impedance. Chen et al compiled available measurements for sand and clay and supplemented them with deepwater measurements with the multi-sensor core logger.

Since porosity is not a parameter which is commonly used, the user can enter bulk unit weight instead which is then converted to porosity for a saturated soil.

The correlation shows a tight relation between acoustic impedance and porosity. However, soils with in-situ excess pore pressure are not included in this dataset.

$$
I =1.315 \cdot 10^{-4} \cdot n^4 - 3.776 \cdot 10^{-2} \cdot n^3 + 4.201 \cdot n^2 - 2.450 \cdot 10^2 \cdot n + 8.603 \cdot 10^3
$$

$$
e = \frac{\gamma_w G_s - \gamma}{\gamma - S \gamma_w}
$$

$$
w = \frac{S e}{G_s}
$$

$$
n = \frac{e}{e+1}
$$

![Compiled data from Chen et al](/docs/assets/groundhog/docs/site_investigation/images/acousticimpedance_bulkunitweight_chen_1.png)

*Compiled data from Chen et al*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `bulkunitweight` | kN/m3 | 12.0 <= bulkunitweight <= 22.0 | required | Bulk (total) unit weight ($\gamma$) |
| `specific_gravity` | - | 1.0 <= specific_gravity <= 3.0 | `2.65` | Specific gravity of the soil ($G_s$) |
| `saturation` | - | 0.0 <= saturation <= 1.0 | `1.0` | Saturation of the soil (fully saturated for offshore soils) ($S$) |
| `gamma_w` | kN/m3 | 9.5 <= gamma_w <= 10.5 | `10.0` | Unit weight of water ($\gamma_w$) |
| `calibration_factor_4` | - |  | `0.0001315` | Calibration factor on the fourth order term |
| `calibration_factor_3` | - |  | `-0.03776` | Calibration factor on the third order term |
| `calibration_factor_2` | - |  | `4.201` | Calibration factor on the second order term |
| `calibration_factor_1` | - |  | `-245.0` | Calibration factor on the first order term |
| `calibration_factor_0` | - |  | `8603.0` | Calibration factor on the zero order term |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `e [-]` | - | Void ratio ($e$) |
| `we [-]` | - | Water content ($w$) |
| `n [-]` | - | Porosity ($n$) |
| `I [(m/s).(g/cm3)]` | (m/s).(g/cm3) | Acoustic impedance ($I$) |

**References**

- Chen et al (2021). Machine Learning Based Digital Integration of Geotechnical and Ultra-High Frequency Geophysical Data for Offshore Site Characterizations. Journal of Geotechnical and Geoenvironmental Engineering.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="shearwavevelocity_compressionindex_cha"></a>

## `shearwavevelocity_compressionindex_cha`

<span class="gc-badge gc-available" data-geocore-function="shearwavevelocity_compressionindex_cha">Available in GeoCore</span> [Site investigation › Correlations: All soil types › Cha Vs–Compression Index Correlation](/docs/geocore/using/modules#shearwavevelocity_compressionindex_cha)

```python
shearwavevelocity_compressionindex_cha(
    Cc,
    sigma_eff_particle_motion,
    sigma_eff_wave_propagation,
    alpha=nan,
    beta=nan,
    calibration_factor_alpha_1=13.5,
    calibration_factor_alpha_2=-0.63,
    calibration_factor_beta_1=0.17,
    calibration_factor_beta_2=0.43,
    **kwargs,
)
```

Shear wave velocity is dependent on the stiffness of the soil skeleton which is in turn affected by the compression index $C_c$. Cha et al (2014) reported a series of oedometer tests with bender elements to establish the coefficients of a power law equation. Note that $C_c$ itself is also stress-dependent and requires the selection of appropriate points in $e-\log p^{\prime}$ space.

The relations proposed by Cha et al (2014) are used here by default, but the user can also enter custom values for $\alpha$ and $\beta$ Since porosity is not a parameter which is commonly used, the user can enter bulk unit weight instead which is then converted to porosity for a saturated soil.

For application to field cases, the effective stress in the direction of particle motion and wave propagation needs to be estimated. This usually involves estimation of the coefficient of lateral earth pressure.

$$
V_s = \sqrt{\frac{G}{\rho}} = \alpha \left( \frac{\sigma_{\perp}^{\prime} + \sigma_{\parallel}^{\prime}}{2 \ \text{kPa}} \right)^{\beta}
$$

$$
\alpha = 13.5 (\text{m/s}) \cdot C_c^{-0.63}
$$

$$
\beta = 0.17 \log_{10} C_c + 0.43
$$

![Compiled data from Cha et al](/docs/assets/groundhog/docs/site_investigation/images/chaetal_data.png)

*Compiled data from Cha et al*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `Cc` | - | 0.005 <= Cc <= 1.2 | required | Compression index ($C_c$) |
| `sigma_eff_particle_motion` | kPa | 10 <= sigma_eff_particle_motion <= 1200 | required | Effective stress in the direction of particle motion ($\sigma_{\perp}^{\prime}$) |
| `sigma_eff_wave_propagation` | kPa | 10 <= sigma_eff_wave_propagation <= 1200 | required | Effective stress in the direction of wave propagation ($\sigma_{\parallel}^{\prime}$) |
| `alpha` | - | 5 <= alpha <= 1000 | `nan` | Custom alpha-factor in the power law ($\alpha$) |
| `beta` | - | 0.0 <= beta <= 0.6 | `nan` | Custom beta-factor in the power law ($\beta$) |
| `calibration_factor_alpha_1` | - |  | `13.5` | First calibration factor for alpha |
| `calibration_factor_alpha_2` | - |  | `-0.63` | Second calibration factor for alpha |
| `calibration_factor_beta_1` | - |  | `0.17` | First calibration factor for beta |
| `calibration_factor_beta_2` | - |  | `0.43` | First calibration factor for alpha |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Vs [m/s]` | $\text{m/s}$ | Shear wave velocity ($V_s$) |
| `alpha [-]` | - | Alpha-factor (multiplier) ($\alpha$) |
| `beta [-]` | - | Beta-factor (exponent) ($\beta$) |

**References**

- Cha et al (2014). Small-Strain Stiffness, Shear-Wave Velocity and Soil Compressibilitys. Journal of Geotechnical and Geoenvironmental Engineering.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="k0_frictionangle_mesri"></a>

## `k0_frictionangle_mesri`

<span class="gc-badge gc-available" data-geocore-function="k0_frictionangle_mesri">Available in GeoCore</span> [Site investigation › Correlations: All soil types › Mesri K0 (Normally/Overconsolidated Soils)](/docs/geocore/using/modules#k0_frictionangle_mesri)

```python
k0_frictionangle_mesri(phi_cs, ocr=1, **kwargs)
```

Calculates the coefficient of lateral earthpressure at rest for normally and overconsolidated sand and clay. Mesri and Hayat (1993) showed that the equation by Jaky (1944) only applied for sedimented, normally consolidated young clays and sands. The effect of overconsolidation was captured by multiplying the value for normally consolidated soil with the OCR raised to an exponent. This exponent is independent of the soil's initial density and thus needs to be related to the critical state friction angle, rather than the peak friction angle of the soil. By adjusting for the effect of overconsolidation, reasonable predictions are obtained for overconsolidated and pre-sheared soils.

$$
K_0 = \left( 1 - \sin \varphi_{cv}^{\prime} \right) \text{OCR}^{\sin \varphi_{cv}^{\prime}}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `phi_cs` | deg | 0.01 <= grain_size <= 2.0 | required | Critical state friction angle ($\varphi_{cs}^{\prime}$) |
| `ocr` | - | 1 <= ocr <= 30 | `1` | Overconsolidation ratio ($\text{OCR}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `K0 [-]` | - | Coefficient of lateral earth pressure at rest ($K_0$) |

**References**

- Mesri and Hayat (1993) The coefficient of earth pressure at rest. Canadian Geotechnical Journal. 30(4), 647-666

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
