---
title: SPT corrections and correlations
slug: groundhog/api/siteinvestigation/insitutests/spt_correlations
section: Groundhog API Reference
description: 'API reference for groundhog.siteinvestigation.insitutests.spt_correlations: 10 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/siteinvestigation/insitutests/spt_correlations.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.siteinvestigation.insitutests.spt_correlations
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/site_investigation/spt_correlations.html
geocore_available: true
geocore_functions:
- frictionangle_spt_PHT
- frictionangle_spt_kulhawymayne
- overburdencorrection_spt_ISO
- overburdencorrection_spt_liaowhitman
- relativedensity_spt_kulhawymayne
- relativedensityclass_spt_terzaghipeck
- spt_N60_correction
- undrainedshearstrength_spt_salgado
- undrainedshearstrengthclass_spt_terzaghipeck
- youngsmodulus_spt_AASHTO
---

Module `groundhog.siteinvestigation.insitutests.spt_correlations` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/siteinvestigation/insitutests/spt_correlations.py).

Upstream documentation: [SPT corrections and correlations](https://groundhog.readthedocs.io/en/main/site_investigation/spt_correlations.html).

**Functions:** [`overburdencorrection_spt_liaowhitman`](#overburdencorrection_spt_liaowhitman), [`spt_N60_correction`](#spt_n60_correction), [`relativedensity_spt_kulhawymayne`](#relativedensity_spt_kulhawymayne), [`undrainedshearstrength_spt_salgado`](#undrainedshearstrength_spt_salgado), [`frictionangle_spt_kulhawymayne`](#frictionangle_spt_kulhawymayne), [`relativedensityclass_spt_terzaghipeck`](#relativedensityclass_spt_terzaghipeck), [`overburdencorrection_spt_ISO`](#overburdencorrection_spt_iso), [`frictionangle_spt_PHT`](#frictionangle_spt_pht), [`youngsmodulus_spt_AASHTO`](#youngsmodulus_spt_aashto), [`undrainedshearstrengthclass_spt_terzaghipeck`](#undrainedshearstrengthclass_spt_terzaghipeck)

<a id="overburdencorrection_spt_liaowhitman"></a>

## `overburdencorrection_spt_liaowhitman`

<span class="gc-badge gc-available" data-geocore-function="overburdencorrection_spt_liaowhitman">Available in GeoCore</span> [Site investigation › In-situ: SPT corrections & correlations › Liao & Whitman Overburden Correction (SPT N)](/docs/geocore/using/modules#overburdencorrection_spt_liaowhitman)

```python
overburdencorrection_spt_liaowhitman(
    N,
    sigma_vo_eff,
    granular=True,
    atmospheric_pressure=100.0,
    **kwargs,
)
```

Applies a correction to the SPT N value to account for the effect of effective overburden pressure in granular soils. The relation given by Liao and Whitman (1986) is one of the most commonly used. Increasing overburden pressure will lead to less penetration at deeper depths for the same soil type. By applying the correction, the field value of N is corrected to a standard effective overburden pressure of 100kPa.

The standard penetration number corrected for field condition ($N_{60}$) can also be used as an input in which case $\left( N_1 \right)_{60}$ is obtained.

$$
N_1 = C_N \cdot N
$$

$$
C_N = \left[ \frac{1}{ \left( \frac{\sigma_{vo}^{\prime}}{P_a} \right) } \right]^{0.5}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `N` | - | N >= 0.0 | required | Field value of SPT N number or corrected value $N_{60}$ ($N$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Effective overburden pressure ($\sigma_{vo}^{\prime}$) |
| `granular` |  |  | `True` | Boolean defining whether the soil behaves in a granular or not. If the behaviour is not granular, the correction factor is taken equal to 1. |
| `atmospheric_pressure` | kPa |  | `100.0` | Atmospheric pressure ($P_a$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `CN [-]` | - | Correction factor ($C_N$) |
| `N1 [-]` | - | Value of SPT N number corrected to an effective overburden pressure of 100kPa ($N_1$ or $\left( N_1 \right)_{60}$ in case $N_{60}$ is used as input) |

**References**

- Liao SSC, Whitman RV (1986) Overburden correction factors for SPT in sand. J Geotech Eng ASCE 112(3):373–377

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="spt_n60_correction"></a>

## `spt_N60_correction`

<span class="gc-badge gc-available" data-geocore-function="spt_N60_correction">Available in GeoCore</span> [Site investigation › In-situ: SPT corrections & correlations › SPT N60 Energy Correction](/docs/geocore/using/modules#spt_n60_correction)

```python
spt_N60_correction(
    N,
    borehole_diameter,
    rod_length,
    country,
    hammertype,
    hammerrelease,
    samplertype='Standard sampler',
    eta_H=nan,
    eta_B=nan,
    eta_S=nan,
    eta_R=nan,
    **kwargs,
)
```

The performance of the SPT in a given soil type depends on the efficiency of energy transmission to the soil. It is common practice to correct the field value of SPT N number to an equivalent number of blows at an energy ratio of 60% (ratio of energy delivered to the sampler divided by the input energy). The hammer efficiency ($\eta_H$), borehole diameter ($\eta_B$), sampler type ($\eta_S$) and rod length ($\eta_R$) are corrected for.

The recommendations by Seed et al (1985) and Skempton (1986) as presented by Ameratunga et al (2016) are used by default. The user can specify overrides for each correction factor. If overrides are specified, they take precedence.

```text
+---------------+-------------+-----------------+----------------------+
|    Country    | Hammer type |  Hammer release | \eta_H [pct] |
+===============+=============+=================+======================+
|     Japan     |    Donut    |    Free fall    |          78          |
|               +-------------+-----------------+----------------------+
|               |    Donut    | Rope and pulley |          67          |
+---------------+-------------+-----------------+----------------------+
| United States |    Safety   | Rope and pulley |          60          |
|               +-------------+-----------------+----------------------+
|               |    Donut    | Rope and pulley |          45          |
+---------------+-------------+-----------------+----------------------+
|   Argentina   |    Donut    | Rope and pulley |          45          |
+---------------+-------------+-----------------+----------------------+
|     China     |    Donut    |    Free fall    |          60          |
|               +-------------+-----------------+----------------------+
|               |    Donut    | Rope and pulley |          50          |
+---------------+-------------+-----------------+----------------------+
```

```text
+---------------+---------------------+
| Diameter [mm] | \eta_B [-]  |
+===============+=====================+
|     60-120    |          1          |
+---------------+---------------------+
|      150      |         1.05        |
+---------------+---------------------+
|      200      |         1.15        |
+---------------+---------------------+
```

```text
+------------------------------------+---------------------+
|            Sampler type            | \eta_S [-]  |
+====================================+=====================+
|          Standard sampler          |         1.0         |
+------------------------------------+---------------------+
| With liner for dense sand and clay |         0.8         |
+------------------------------------+---------------------+
|      With liner for loose sand     |         0.9         |
+------------------------------------+---------------------+
```

```text
+----------------+---------------------+
| Rod length [m] | \eta_R [-]  |
+================+=====================+
|       >10      |         1.0         |
+----------------+---------------------+
|      6-10      |         0.95        |
+----------------+---------------------+
|       4-6      |         0.85        |
+----------------+---------------------+
|       0-4      |         0.75        |
+----------------+---------------------+
```

$$
N_{60} = \frac{N \cdot \eta_H \cdot \eta_B \cdot \eta_S \cdot \eta_R}{60}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `N` | - | N >= 0.0 | required | Field value of SPT N number ($N$) |
| `borehole_diameter` | mm | 60.0 <= borehole_diameter <= 200.0 | required | Diameter of the borehole ($D$) |
| `rod_length` | m | rod_length >= 0.0 | required | Length of rods connecting hammer with sampler ($L$) |
| `country` |  | one of `Japan`, `United States`, `Argentina`, `China`, `Other` | required | Country where SPT test is executed - Options: ('Japan', 'United States', 'Argentina', 'China', 'Other'). If 'Other' is chosen, an override for $\eta_H$ should be specified |
| `hammertype` |  | one of `Donut`, `Safety` | required | Type of hammer used - Options: ('Donut', 'Safety') |
| `hammerrelease` |  | one of `Free fall`, `Rope and pulley` | required | Release mechanism for the hammer - Options: ('Free fall', 'Rope and pulley') |
| `samplertype` |  | one of `Standard sampler`, `With liner for dense sand and clay`, `With liner for loose sand` | `'Standard sampler'` | Type of sampler used |
| `eta_H` | pct | 0.0 <= eta_H <= 100.0 | `nan` | Correction factor for hammer efficiency ($\eta_H$) |
| `eta_B` | - | 1.0 <= eta_B <= 1.2 | `nan` | Correction factor for borehole diameter ($\eta_B$) |
| `eta_S` | - | 0.8 <= eta_S <= 1.0 | `nan` | Correction factor for sampler type ($\eta_S$) |
| `eta_R` | - | 0.75 <= eta_R <= 1.0 | `nan` | Correction factor for rod length ($\eta_R$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `N60 [-]` | - | SPT N number corrected to 60pct efficiency ($N_{60}$) |
| `eta_H [%]` | pct | Correction factor for hammer efficiency ($\eta_H$) |
| `eta_H [-]` | - | : Correction factor for hammer efficiency ($\eta_H$) |
| `eta_B [-]` | - | Correction factor for borehole diameter ($\eta_B$) |
| `eta_S [-]` | - | Correction factor for sampler type ($\eta_S$) |
| `eta_R [-]` | - | Correction factor for rod length ($\eta_R$) |

**References**

- J. Ameratunga et al., Correlations of Soil and Rock Properties in Geotechnical Engineering, Developments in Geotechnical Engineering, DOI 10.1007/978-81-322-2629-1_4

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="relativedensity_spt_kulhawymayne"></a>

## `relativedensity_spt_kulhawymayne`

<span class="gc-badge gc-available" data-geocore-function="relativedensity_spt_kulhawymayne">Available in GeoCore</span> [Site investigation › In-situ: SPT corrections & correlations › Kulhawy & Mayne Relative Density (SPT)](/docs/geocore/using/modules#relativedensity_spt_kulhawymayne)

```python
relativedensity_spt_kulhawymayne(
    N1_60,
    d_50,
    calibration_factor_1=60.0,
    calibration_factor_2=25.0,
    time_since_deposition=1.0,
    ocr=1.0,
    ca_override=nan,
    cocr_override=nan,
    **kwargs,
)
```

Estimates relative density from SPT test. Although initially proposed based on the results of tests on non-aged, normally consolidated sands, the correlation can account for the effect of ageing and overconsolidation through correction factors. The parameters for these correction factors are not always easy to estimate.

Note that stress and energy corrections need to be applied to the raw SPT data before applying the correlation.

$$
\text{Unaged, normally consolidated sand}
$$

$$
D_r = \sqrt{\frac{(N_1)_{60}}{60 + 25 \cdot \log_{10} ( d_{50} )}}
$$

$$
\text{With corrections for overconsolidation and ageing}
$$

$$
D_r = \sqrt{\frac{(N_1)_{60}}{\left( 60 + 25 \cdot \log d_{50} \right) \cdot C_A \cdot C_{OCR}}}
$$

$$
C_A = 1.2 + 0.05 \cdot \log_{10} \left( \frac{t}{100} \right)
$$

$$
C_{OCR} = (OCR)^{0.18}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `N1_60` | - | 0.0 <= N_1_60 <= 100.0 | required | SPT number corrected for overburden stress and energy ($(N_1)_{60}$) |
| `d_50` | mm | 0.002 <= d_50 <= 20.0 | required | Median grain size ($d_{50}$) |
| `calibration_factor_1` | - |  | `60.0` | First calibration factor |
| `calibration_factor_2` | - |  | `25.0` | Second calibration factor |
| `time_since_deposition` | years | time_since_deposition >= 1.0 | `1.0` | Time since deposition ($t$) |
| `ocr` | - | 1.0 <= ocr <= 50.0 | `1.0` | Overconsolidation ratio ($OCR$) |
| `ca_override` | - | ca_override >= 1.0 | `nan` | Direct specification of factor CA ($C_A$) |
| `cocr_override` | - | cocr_override >= 1.0 | `nan` | Direct specification of factor COCR ($C_{OCR}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Dr [-]` | - | Relative density (unitless) ($D_r$) |
| `Dr [pct]` | pct | Relative density (percent) ($D_r$) |
| `C_A [-]` | - | Correction factor for ageing ($C_A$) |
| `C_OCR [-]` | - | Correction factor for overconsolidation ($C_{OCR}$) |

**References**

- Kulhawy FH, Mayne PW (1990) Manual on estimating soil properties for foundation design. Electric Power Research Institute, Palo Alto

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="undrainedshearstrength_spt_salgado"></a>

## `undrainedshearstrength_spt_salgado`

<span class="gc-badge gc-available" data-geocore-function="undrainedshearstrength_spt_salgado">Available in GeoCore</span> [Site investigation › In-situ: SPT corrections & correlations › Salgado Undrained Shear Strength (SPT)](/docs/geocore/using/modules#undrainedshearstrength_spt_salgado)

```python
undrainedshearstrength_spt_salgado(
    pi,
    N_60,
    atmospheric_pressure=100.0,
    alpha_prime_override=nan,
    **kwargs,
)
```

Calculates undrained shear strength based on plasticity index and SPT number (corrected to 60% energy ratio).

```text
+--------+-------------------------------+
| PI [%] | \alpha^{\prime} [-]   |
+========+===============================+
|   15   |             0.068             |
+--------+-------------------------------+
|   20   |             0.055             |
+--------+-------------------------------+
|   25   |             0.048             |
+--------+-------------------------------+
|   30   |             0.045             |
+--------+-------------------------------+
|   40   |             0.044             |
+--------+-------------------------------+
|   60   |             0.043             |
+--------+-------------------------------+
```

$$
\frac{S_u}{P_a} = \alpha^{\prime} \cdot N_{60}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `pi` | pct | 15.0 <= plasticity_index <= 60.0 | required | Plasticity index (difference between liquid and plastic limit) ($PI$) |
| `N_60` | - | 0.0 <= N_60 <= 100.0 | required | SPT number corrected to 60% energy ratio ($N_{60}$) |
| `atmospheric_pressure` | kPa | 90.0 <= atmospheric_pressure <= 110.0 | `100.0` | Atmospheric pressure ($P_a$) |
| `alpha_prime_override` | - | alpha_prime_override >= 0.0 | `nan` | Override for direct specification of the alpha prime factor ($\alpha^{\prime}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `alpha_prime [-]` | - | Factor based on plasticity index ($\alpha^{\prime}$) |
| `Su [kPa]` | kPa | Undrained shear strength ($S_u$) |

**References**

- Salgado R (2008) The engineering of foundations. McGraw-Hill, New York

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="frictionangle_spt_kulhawymayne"></a>

## `frictionangle_spt_kulhawymayne`

<span class="gc-badge gc-available" data-geocore-function="frictionangle_spt_kulhawymayne">Available in GeoCore</span> [Site investigation › In-situ: SPT corrections & correlations › Kulhawy & Mayne Friction Angle (SPT)](/docs/geocore/using/modules#frictionangle_spt_kulhawymayne)

```python
frictionangle_spt_kulhawymayne(
    N,
    sigma_vo_eff,
    atmospheric_pressure=100.0,
    coefficient_1=12.2,
    coefficient_2=20.3,
    coefficient_3=0.34,
    **kwargs,
)
```

Kulhawy and Mayne approximated the chart for friction angle selection from SPT using the formula given below. The friction angle depends on the effective overburden stress and SPT N number.

$$
\phi = \tan^{-1} \left[ \frac{N}{12.2 +20.3 \cdot \left( \frac{\sigma_{v0}^{\prime}}{P_a} \right)} \right]^{0.34}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `N` | - | 0.0 <= N <= 60.0 | required | SPT N number ($N$) |
| `sigma_vo_eff` | kPa | 0.0 <= sigma_vo_eff <= 1000.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `atmospheric_pressure` | kPa | 90.0 <= atmospheric_pressure <= 110.0 | `100.0` | Atmospheric pressure ($P_a$) |
| `coefficient_1` | - |  | `12.2` | First calibration coefficient |
| `coefficient_2` | - |  | `20.3` | Second calibration coefficient |
| `coefficient_3` | - |  | `0.34` | Third calibration coefficient |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Phi [deg]` | deg | Effective internal friction angle of the soil ($\phi$) |

**References**

- Kulhawy FH, Mayne PW (1990) Manual on estimating soil properties for foundation design. Electric Power Research Institute, Palo Alto

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="relativedensityclass_spt_terzaghipeck"></a>

## `relativedensityclass_spt_terzaghipeck`

<span class="gc-badge gc-available" data-geocore-function="relativedensityclass_spt_terzaghipeck">Available in GeoCore</span> [Site investigation › In-situ: SPT corrections & correlations › Terzaghi & Peck Relative Density Class (SPT)](/docs/geocore/using/modules#relativedensityclass_spt_terzaghipeck)

```python
relativedensityclass_spt_terzaghipeck(N, **kwargs)
```

Defines the relative density class for SPT measurements in cohesionless soils based on the uncorrected N-number

```text
+-----------------+-----------------------------+
| N (uncorrected) | Relative density category   |
+=================+=============================+
|   <= 4          |         Very loose          |
+-----------------+-----------------------------+
|   4 < N <= 10   |         Loose               |
+-----------------+-----------------------------+
|   10 < N <= 30  |         Medium dense        |
+-----------------+-----------------------------+
|   30 < N <= 50  |         Dense               |
+-----------------+-----------------------------+
|   N <= 50       |         Very dense          |
+-----------------+-----------------------------+
```

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `N` | - | 0.0 <= N <= 60.0 | required | Uncorrected SPT N number ($N$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Dr class` |  | Relative density class ($D_r$) |

**References**

- Terzaghi K, Peck RB (1967) Soil mechanics in engineering practice, 2nd edn. Wiley, New York

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="overburdencorrection_spt_iso"></a>

## `overburdencorrection_spt_ISO`

<span class="gc-badge gc-available" data-geocore-function="overburdencorrection_spt_ISO">Available in GeoCore</span> [Site investigation › In-situ: SPT corrections & correlations › ISO Overburden Correction (SPT N)](/docs/geocore/using/modules#overburdencorrection_spt_iso)

```python
overburdencorrection_spt_ISO(N, sigma_vo_eff, granular=True, **kwargs)
```

Corrects the SPT N number or corrected N number ($N_{60}$) for the effect of overburden pressure in granular soils. The multiplier $C_N$ is calculated and applied to N or $N_{60}$. Note that $C_N$ should be limited to 2 and preferably be kept below 1.5. In the function, a lower limit on the vertical effective stress of 25kPa is used in the validation to achieve this.

$$
C_N = \sqrt{\frac{98}{\sigma_{v0}^{\prime}}}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `N` | - | 0.0 <= N <= 60.0 | required | Uncorrected or corrected SPT N number ($N or N_{60}$) |
| `sigma_vo_eff` | kPa | 25.0 <= sigma_vo_eff <= 400.0 | required | Vertical effective stress ($\sigma_{v0}^{\prime}$) |
| `granular` |  |  | `True` | Boolean defining whether the soil is granular or not. If the soil is not granular, the correction factor is taken equal to 1 |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `CN [-]` | - | Multiplier on SPT N number [-] ($C_N$) |
| `N1 [-]` | - | Corrected N number [-] ($N_1 or \left( N_1 \right)_{60}$) |

**References**

- BS EN ISO 22476-3

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="frictionangle_spt_pht"></a>

## `frictionangle_spt_PHT`

<span class="gc-badge gc-available" data-geocore-function="frictionangle_spt_PHT">Available in GeoCore</span> [Site investigation › In-situ: SPT corrections & correlations › Peck, Hanson & Thornburn (1974) Friction Angle](/docs/geocore/using/modules#frictionangle_spt_pht)

```python
frictionangle_spt_PHT(
    N1_60,
    intercept=27.1,
    multiplier=0.3,
    multiplier_quadratic=0.00054,
    **kwargs,
)
```

Correlation proposed by Peck, Hanson and Thornburn (1974) and mentioned by Wolff (1989)

$$
\varphi^{\prime} = 27.1 + 0.3 \cdot \left( N_1 \right)_{60} - 0.00054 \cdot \left( N_1 \right)_{60}^2
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `N1_60` | - | 0.0 <= N1_60 <= 60.0 | required | Corrected SPT N value ($\left( N_1 \right)_{60}$) |
| `intercept` | deg | 23.0 <= intercept <= 35.0 | `27.1` | Intercept at N=0 ($-$) |
| `multiplier` | deg/blow | 0.1 <= multiplier <= 0.7 | `0.3` | Multiplier on linear term ($-$) |
| `multiplier_quadratic` | $deg/blow^2$ | 0.0001 <= multiplier_quadratic <= 0.001 | `0.00054` | Multiplier on the quadratic term ($-$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Phi [deg]` | deg | Friction angle derived from SPT [deg] ($\varphi^{\prime}$) |

**References**

- Peck, Hanson and Thornburn (1974). Foundation Engineering.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="youngsmodulus_spt_aashto"></a>

## `youngsmodulus_spt_AASHTO`

<span class="gc-badge gc-available" data-geocore-function="youngsmodulus_spt_AASHTO">Available in GeoCore</span> [Site investigation › In-situ: SPT corrections & correlations › AASHTO Young's Modulus (SPT)](/docs/geocore/using/modules#youngsmodulus_spt_aashto)

```python
youngsmodulus_spt_AASHTO(
    N1_60,
    soiltype,
    multiplier_silts=0.4,
    multiplier_cleansand=0.7,
    multiplier_coarsesand=1.0,
    multiplier_gravel=1.1,
    **kwargs,
)
```

Calculates the Young's modulus based on corrected SPT number for various soil types.

```text
+-----------------------------------------------------+------------------------+---------------------------+
| Soil type                                           | Soil type (short name) | E_s [MPa]         |
+=====================================================+========================+===========================+
| Silts, sandy silts, slightly cohesive mixtures      | Silts                  |  0.4 ( N_1 )_{60} |
+-----------------------------------------------------+------------------------+---------------------------+
| Clean fine to medium sands and slightly silty sands | Clean sands            |  0.7 ( N_1 )_{60} |
+-----------------------------------------------------+------------------------+---------------------------+
| Coarse sands and sands with little gravel           | Coarse sands           |  1.0 ( N_1 )_{60} |
+-----------------------------------------------------+------------------------+---------------------------+
| Sandy gravel and gravels                            | Gravels                |  1.1 ( N_1 )_{60} |
+-----------------------------------------------------+------------------------+---------------------------+
```

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `N1_60` | - | 0.0 <= N1_60 <= 60.0 | required | Corrected SPT N number ($\left( N_1 \right)_{60}$) |
| `soiltype` |  | one of `Silts`, `Clean sands`, `Coarse sands`, `Gravels` | required | Soil type - Options: ("Silts", "Clean sands", "Coarse sands", "Gravels") |
| `multiplier_silts` | - |  | `0.4` | Multiplier on the silty soils ($-$) |
| `multiplier_cleansand` | - |  | `0.7` | Multiplier on the clean find sands ($-$) |
| `multiplier_coarsesand` | - |  | `1.0` | Multiplier on the coarse sands ($-$) |
| `multiplier_gravel` | - |  | `1.1` | Multiplier on the gravels ($-$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Es [MPa]` | MPa | Young's modulus [MPa] ($E_s$) |

**References**

- AASHTO 1997 - LRFD

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="undrainedshearstrengthclass_spt_terzaghipeck"></a>

## `undrainedshearstrengthclass_spt_terzaghipeck`

<span class="gc-badge gc-available" data-geocore-function="undrainedshearstrengthclass_spt_terzaghipeck">Available in GeoCore</span> [Site investigation › In-situ: SPT corrections & correlations › Terzaghi & Peck Strength Class (SPT)](/docs/geocore/using/modules#undrainedshearstrengthclass_spt_terzaghipeck)

```python
undrainedshearstrengthclass_spt_terzaghipeck(N, **kwargs)
```

Defines the relative density class for SPT measurements in cohesionless soils based on the uncorrected N-number

```text
+-----------------+-------------+-------------------+
| N (uncorrected) | Consistency | q_u [kPa] |
+=================+=============+===================+
|   <= 2          | Very soft   | < 25              |
+-----------------+-------------+-------------------+
|   2 < N <= 4    | Soft        | 25 - 50           |
+-----------------+-------------+-------------------+
|   4 < N <= 8    | Medium      | 50 - 100          |
+-----------------+-------------+-------------------+
|   8 < N <= 15   | Stiff       | 100 - 200         |
+-----------------+-------------+-------------------+
|   15 < N <= 30  | Very stiff  | 200 - 400         |
+-----------------+-------------+-------------------+
|   N > 30        | Hard        | > 400             |
+-----------------+-------------+-------------------+
```

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `N` | - | 0.0 <= N <= 60.0 | required | Uncorrected SPT N number ($N$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Consistency class` |  | Consistency class |
| `qu min [kPa]` | kPa | Minimum value for ultimate axial stress in a UCS test |
| `qu max [kPa]` | kPa | Maximum value for ultimate axial stress in a UCS test |

**References**

- Terzaghi K, Peck RB (1967) Soil mechanics in engineering practice, 2nd edn. Wiley, New York

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
