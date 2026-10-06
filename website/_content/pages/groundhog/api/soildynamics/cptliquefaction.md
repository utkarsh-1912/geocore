---
title: CPT Liquefaction
slug: groundhog/api/soildynamics/cptliquefaction
section: Groundhog API Reference
description: 'API reference for groundhog.soildynamics.cptliquefaction: 14 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/soildynamics/cptliquefaction.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.soildynamics.cptliquefaction
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/soildynamics/cptliquefaction.html
geocore_available: true
geocore_functions:
- Qtn_cs_boulanger_idriss_2014
- Qtn_cs_idriss_boulanger_2008
- Qtn_cs_robertson_cabal_2022
- Qtn_cs_robertson_wride_1998
- crr_boulanger_idriss_2014
- crr_idriss_boulanger_2008
- crr_robertson_cabal_2022
- crr_robertson_wride_1998
- csr_boulanger_idriss_2014
- csr_idriss_boulanger_2008
- csr_robertson_cabal_2022
- csr_robertson_wride_1998
- fos_liquefaction
- liquefaction_strains_zhang
---

Module `groundhog.soildynamics.cptliquefaction` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/soildynamics/cptliquefaction.py).

Upstream documentation: [CPT Liquefaction](https://groundhog.readthedocs.io/en/main/soildynamics/cptliquefaction.html).

**Functions:** [`fos_liquefaction`](#fos_liquefaction), [`csr_robertson_cabal_2022`](#csr_robertson_cabal_2022), [`csr_robertson_wride_1998`](#csr_robertson_wride_1998), [`csr_idriss_boulanger_2008`](#csr_idriss_boulanger_2008), [`csr_boulanger_idriss_2014`](#csr_boulanger_idriss_2014), [`crr_robertson_cabal_2022`](#crr_robertson_cabal_2022), [`crr_robertson_wride_1998`](#crr_robertson_wride_1998), [`crr_idriss_boulanger_2008`](#crr_idriss_boulanger_2008), [`crr_boulanger_idriss_2014`](#crr_boulanger_idriss_2014), [`Qtn_cs_robertson_cabal_2022`](#qtn_cs_robertson_cabal_2022), [`Qtn_cs_robertson_wride_1998`](#qtn_cs_robertson_wride_1998), [`Qtn_cs_idriss_boulanger_2008`](#qtn_cs_idriss_boulanger_2008), [`Qtn_cs_boulanger_idriss_2014`](#qtn_cs_boulanger_idriss_2014), [`liquefaction_strains_zhang`](#liquefaction_strains_zhang)

<a id="fos_liquefaction"></a>

## `fos_liquefaction`

<span class="gc-badge gc-available" data-geocore-function="fos_liquefaction">Available in GeoCore</span> [Soil dynamics › CPT Liquefaction › Factor of Safety (Liquefaction)](/docs/geocore/using/modules#fos_liquefaction)

```python
fos_liquefaction(sigma_vo, sigma_vo_eff, CRR, CSR, MSF, K_sigma, **kwargs)
```

Calculates the Factor of Safety (FoS) for liquefaction assessment. The FoS is a measure of the capacity of the soil to resist liquefaction relative to the demand imposed by seismic loading.

The FoS is computed as the ratio of the Cyclic Resistance Ratio (CRR) to the Cyclic Stress Ratio (CSR), adjusted for earthquake magnitude effects (MSF) and overburden stress effects (K_sigma). The FoS is capped at a maximum value of 5 to avoid unrealistic results.

If the effective vertical stress ($\sigma_v^{\prime}$) equals the total vertical stress ($\sigma_v$), the FoS is set to 5, indicating no risk of liquefaction.

$$
FoS = \min \left( \frac{CRR}{CSR} \cdot MSF \cdot K_{\sigma}, 5 \right)
$$

$$
\text{If } \sigma_v^{\prime} = \sigma_v, \text{ then } FoS = 5
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `sigma_vo` | kPa | sigma_vo >= 0.0 | required | Total vertical stress at the depth of interest ($\sigma_v$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Effective vertical stress at the depth of interest ($\sigma_v^{\prime}$) |
| `CRR` | - | 0.0 < CRR <= 1.0 | required | Cyclic Resistance Ratio ($CRR$) |
| `CSR` | - | CSR >= 0.0 | required | Cyclic Stress Ratio ($CSR$) |
| `MSF` | - | 0.0 < MSF <= 2.0 | required | Magnitude Scaling Factor ($MSF$) |
| `K_sigma` | - | 0.0 < K_sigma <= 2.0 | required | Overburden correction factor ($K_{\sigma}$) |

**Returns**

Dictionary with the following key:

| Key | Unit | Description |
|---|---|---|
| `FoS_liq [-]` | - | Factor of Safety for liquefaction assessment ($FoS$) |

**Example**

```python
>>> result = fos_liquefaction(
...     sigma_vo=100, sigma_vo_eff=80, CRR=0.25, CSR=0.15, MSF=1.2, K_sigma=1.1
... )
>>> print(result)
{'FoS_liq [-]': 2.2}
```

**References**

- Youd, T. L., et al. (2001). Liquefaction Resistance of Soils: Summary Report from the 1996 NCEER and 1998 NCEER/NSF Workshops on Evaluation of Liquefaction Resistance of Soils. Journal of Geotechnical and Geoenvironmental Engineering, 127(10).
- Idriss, I. M., & Boulanger, R. W. (2008). Soil Liquefaction During Earthquakes. Earthquake Engineering Research Institute.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="csr_robertson_cabal_2022"></a>

## `csr_robertson_cabal_2022`

<span class="gc-badge gc-available" data-geocore-function="csr_robertson_cabal_2022">Available in GeoCore</span> [Soil dynamics › CPT Liquefaction › R&C (2022) CSR](/docs/geocore/using/modules#csr_robertson_cabal_2022)

```python
csr_robertson_cabal_2022(
    sigma_vo,
    sigma_vo_eff,
    depth,
    magnitude,
    acceleration,
    MSF_userdefined=False,
    **kwargs,
)
```

Calculates the Cyclic Stress Ratio (CSR) and Magnitude Scaling Factor (MSF) following the methodology outlined by Robertson and Cabal (2022).

The CSR is computed using the simplified procedure by Seed and Idriss (1971), adjusted for depth and earthquake magnitude effects. The MSF is calculated based on the earthquake magnitude, with an option for a user-defined MSF that averages the formulations by Idriss and Andrus & Stokoe.

The depth-dependent stress reduction factor ($r_d$) is calculated using piecewise linear equations based on depth ranges.

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

$$
MSF = \begin{cases}
\frac{10^{2.24}}{M_w^{2.56}} + \left( \frac{M_w}{7.5} \right)^{-3.33} \cdot 0.5 & \text{if } MSF_{userdefined} = True \\
\frac{174}{M_w^{2.56}} & \text{if } MSF_{userdefined} = False
\end{cases}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `sigma_vo` | kPa | sigma_vo >= 0.0 | required | Total vertical stress at the depth of interest ($\sigma_v$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Effective vertical stress at the depth of interest ($\sigma_v^{\prime}$) |
| `depth` | m | depth >= 0.0 | required | Depth below the mudline at which CSR is calculated ($z$) |
| `magnitude` | - | 5.0 <= magnitude <= 8.5 | required | Earthquake magnitude ($M_w$) |
| `acceleration` | g | acceleration >= 0.0 | required | Maximum horizontal acceleration at the soil surface ($a_{max}$) |
| `MSF_userdefined` |  |  | `False` | If True, the MSF is calculated as the average of the Idriss and Andrus & Stokoe formulations. If False, the default Robertson and Cabal (2022) MSF is used. |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `MSF [-]` | - | Magnitude scaling factor ($MSF$) |
| `CSR [-]` | - | Cyclic stress ratio ($CSR$) |

**Example**

```python
>>> result = csr_robertson_cabal_2022(
...     sigma_vo=100, sigma_vo_eff=80, depth=10, magnitude=7.0, acceleration=0.3
... )
>>> print(result)
{'MSF [-]': 1.12, 'CSR [-]': 0.18}
```

**References**

- Robertson, P. K., & Cabal, K. L. (2022). Guide to Cone Penetration Testing for Geotechnical Engineering. Gregg Drilling & Testing, Inc.
- Seed, H. B., & Idriss, I. M. (1971). Simplified Procedure for Evaluating Soil Liquefaction Potential. Journal of the Soil Mechanics and Foundations Division, 97(9).

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="csr_robertson_wride_1998"></a>

## `csr_robertson_wride_1998`

<span class="gc-badge gc-available" data-geocore-function="csr_robertson_wride_1998">Available in GeoCore</span> [Soil dynamics › CPT Liquefaction › R&W (1998) CSR](/docs/geocore/using/modules#csr_robertson_wride_1998)

```python
csr_robertson_wride_1998(
    sigma_vo,
    sigma_vo_eff,
    depth,
    magnitude,
    acceleration,
    **kwargs,
)
```

Calculates the Cyclic Stress Ratio (CSR) and Magnitude Scaling Factor (MSF) following the methodology outlined by Robertson and Wride (1998).

The CSR is computed using the simplified procedure by Seed and Idriss (1971), adjusted for depth and earthquake magnitude effects. The MSF is calculated based on the earthquake magnitude using the Robertson and Wride (1998) formulation.

The depth-dependent stress reduction factor ($r_d$) is calculated using piecewise linear equations based on depth ranges.

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

$$
MSF = \frac{10^{2.24}}{M_w^{2.56}}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `sigma_vo` | kPa | sigma_vo >= 0.0 | required | Total vertical stress at the depth of interest ($\sigma_v$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Effective vertical stress at the depth of interest ($\sigma_v^{\prime}$) |
| `depth` | m | depth >= 0.0 | required | Depth below the mudline at which CSR is calculated ($z$) |
| `magnitude` | - | 5.0 <= magnitude <= 8.5 | required | Earthquake magnitude ($M_w$) |
| `acceleration` | g | acceleration >= 0.0 | required | Maximum horizontal acceleration at the soil surface ($a_{max}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `MSF [-]` | - | Magnitude scaling factor ($MSF$) |
| `CSR [-]` | - | Cyclic stress ratio ($CSR$) |

**Example**

```python
>>> result = csr_robertson_wride_1998(
...     sigma_vo=100, sigma_vo_eff=80, depth=10, magnitude=7.0, acceleration=0.3
... )
>>> print(result)
{'MSF [-]': 1.12, 'CSR [-]': 0.18}
```

**References**

- Robertson, P. K., & Wride, C. E. (1998). Evaluating Cyclic Liquefaction Potential Using the Cone Penetration Test. Canadian Geotechnical Journal, 35(3).
- Seed, H. B., & Idriss, I. M. (1971). Simplified Procedure for Evaluating Soil Liquefaction Potential. Journal of the Soil Mechanics and Foundations Division, 97(9).

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="csr_idriss_boulanger_2008"></a>

## `csr_idriss_boulanger_2008`

<span class="gc-badge gc-available" data-geocore-function="csr_idriss_boulanger_2008">Available in GeoCore</span> [Soil dynamics › CPT Liquefaction › I&B (2008) CSR](/docs/geocore/using/modules#csr_idriss_boulanger_2008)

```python
csr_idriss_boulanger_2008(
    sigma_vo,
    sigma_vo_eff,
    depth,
    magnitude,
    acceleration,
    **kwargs,
)
```

Calculates the Cyclic Stress Ratio (CSR) and Magnitude Scaling Factor (MSF) following the methodology outlined by Idriss and Boulanger (2008).

The CSR is computed using the simplified procedure by Seed and Idriss (1971), adjusted for depth and earthquake magnitude effects. The MSF is calculated based on the earthquake magnitude using the Idriss and Boulanger (2008) formulation.

The depth-dependent stress reduction factor ($r_d$) is calculated using an exponential function that depends on depth and earthquake magnitude.

$$
CSR = 0.65 \cdot a_{max} \cdot \frac{\sigma_v}{\sigma_v^{\prime}} \cdot r_d
$$

$$
MSF = \min \left( 6.9 \cdot e^{-M_w / 4} - 0.058, 1.8 \right)
$$

$$
\alpha = -1.012 - 1.126 \cdot \sin \left( \frac{z}{11.73} + 5.133 \right)
$$

$$
\beta = 0.106 + 0.118 \cdot \sin \left( \frac{z}{11.28} + 5.142 \right)
$$

$$
r_d = e^{\alpha + \beta \cdot M_w}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `sigma_vo` | kPa | sigma_vo >= 0.0 | required | Total vertical stress at the depth of interest ($\sigma_v$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Effective vertical stress at the depth of interest ($\sigma_v^{\prime}$) |
| `depth` | m | depth >= 0.0 | required | Depth below the mudline at which CSR is calculated ($z$) |
| `magnitude` | - | 5.0 <= magnitude <= 8.5 | required | Earthquake magnitude ($M_w$) |
| `acceleration` | g | acceleration >= 0.0 | required | Maximum horizontal acceleration at the soil surface ($a_{max}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `MSF [-]` | - | Magnitude scaling factor ($MSF$) |
| `CSR [-]` | - | Cyclic stress ratio ($CSR$) |

**Example**

```python
>>> result = csr_idriss_boulanger_2008(
...     sigma_vo=100, sigma_vo_eff=80, depth=10, magnitude=7.0, acceleration=0.3
... )
>>> print(result)
{'MSF [-]': 1.12, 'CSR [-]': 0.18}
```

**References**

- Idriss, I. M., & Boulanger, R. W. (2008). Soil Liquefaction During Earthquakes. Earthquake Engineering Research Institute.
- Seed, H. B., & Idriss, I. M. (1971). Simplified Procedure for Evaluating Soil Liquefaction Potential. Journal of the Soil Mechanics and Foundations Division, 97(9).

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="csr_boulanger_idriss_2014"></a>

## `csr_boulanger_idriss_2014`

<span class="gc-badge gc-available" data-geocore-function="csr_boulanger_idriss_2014">Available in GeoCore</span> [Soil dynamics › CPT Liquefaction › B&I (2014) CSR](/docs/geocore/using/modules#csr_boulanger_idriss_2014)

```python
csr_boulanger_idriss_2014(
    Qtn_cs,
    sigma_vo,
    sigma_vo_eff,
    depth,
    magnitude,
    acceleration,
    **kwargs,
)
```

Calculates the Cyclic Stress Ratio (CSR) and Magnitude Scaling Factor (MSF) following the methodology outlined by Boulanger and Idriss (2014).

The CSR is computed using the simplified procedure by Seed and Idriss (1971), adjusted for depth and earthquake magnitude effects. The MSF is calculated based on the earthquake magnitude and normalized cone penetration resistance ($Q_{tn,cs}$) using the Boulanger and Idriss (2014) formulation.

The depth-dependent stress reduction factor ($r_d$) is calculated using an exponential function that depends on depth and earthquake magnitude.

$$
CSR = 0.65 \cdot a_{max} \cdot \frac{\sigma_v}{\sigma_v^{\prime}} \cdot r_d
$$

$$
\alpha = -1.012 - 1.126 \cdot \sin \left( \frac{z}{11.73} + 5.133 \right)
$$

$$
\beta = 0.106 + 0.118 \cdot \sin \left( \frac{z}{11.28} + 5.142 \right)
$$

$$
r_d = e^{\alpha + \beta \cdot M_w}
$$

$$
MSF_{max} = \min \left( 1.09 + \left( \frac{Q_{tn,cs}}{180} \right)^3, 2.2 \right)
$$

$$
MSF = 1 + (MSF_{max} - 1) \cdot \left( 8.64 \cdot e^{-M_w / 4} - 1.325 \right)
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `Qtn_cs` | - | Qtn_cs >= 0.0 | required | Normalized cone penetration resistance ($Q_{tn,cs}$) |
| `sigma_vo` | kPa | sigma_vo >= 0.0 | required | Total vertical stress at the depth of interest ($\sigma_v$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Effective vertical stress at the depth of interest ($\sigma_v^{\prime}$) |
| `depth` | m | depth >= 0.0 | required | Depth below the mudline at which CSR is calculated ($z$) |
| `magnitude` | - | 5.0 <= magnitude <= 8.5 | required | Earthquake magnitude ($M_w$) |
| `acceleration` | g | acceleration >= 0.0 | required | Maximum horizontal acceleration at the soil surface ($a_{max}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `CSR [-]` | - | Cyclic stress ratio ($CSR$) |
| `MSF [-]` | - | Magnitude scaling factor ($MSF$) |

**Example**

```python
>>> result = csr_boulanger_idriss_2014(
...     Qtn_cs=100, sigma_vo=120, sigma_vo_eff=80, depth=10, magnitude=7.0, acceleration=0.3
... )
>>> print(result)
{'CSR [-]': 0.18, 'MSF [-]': 1.12}
```

**References**

- Boulanger, R. W., & Idriss, I. M. (2014). CPT and SPT Liquefaction Triggering Procedures. Report No. UCD/CGM-14/01, University of California, Davis.
- Seed, H. B., & Idriss, I. M. (1971). Simplified Procedure for Evaluating Soil Liquefaction Potential. Journal of the Soil Mechanics and Foundations Division, 97(9).

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="crr_robertson_cabal_2022"></a>

## `crr_robertson_cabal_2022`

<span class="gc-badge gc-available" data-geocore-function="crr_robertson_cabal_2022">Available in GeoCore</span> [Soil dynamics › CPT Liquefaction › R&C (2022) CRR](/docs/geocore/using/modules#crr_robertson_cabal_2022)

```python
crr_robertson_cabal_2022(Qtn_cs, **kwargs)
```

Calculates the Cyclic Resistance Ratio (CRR) and Overburden Correction Factor ($K_{\sigma}$) based on the methodology outlined by Robertson and Cabal (2022).

The CRR is computed using normalized cone penetration resistance ($Q_{tn,cs}$) with fines correction. The CRR is calculated differently for three ranges of $Q_{tn,cs}$:

- For $Q_{tn,cs} < 50$, a linear relationship is used.
- For $50 \leq Q_{tn,cs} < 160$, a cubic relationship is used.
- For $Q_{tn,cs} \geq 160$, the CRR is set to infinity, indicating no liquefaction risk.

The overburden correction factor ($K_{\sigma}$) is set to 1, as it is not required for this methodology.

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

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `Qtn_cs` | - | Qtn_cs >= 0.0 | required | Normalized cone penetration resistance with fines correction ($Q_{tn,cs}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `CRR [-]` | - | Cyclic resistance ratio ($CRR$) |
| `K_sigma [-]` | - | Overburden correction factor ($K_{\sigma}$) |

**Example**

```python
>>> result = crr_robertson_cabal_2022(Qtn_cs=120)
>>> print(result)
{'CRR [-]': 0.18, 'K_sigma [-]': 1.0}
```

**References**

- Robertson, P. K., & Cabal, K. L. (2022). Guide to Cone Penetration Testing for Geotechnical Engineering. Gregg Drilling & Testing, Inc.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="crr_robertson_wride_1998"></a>

## `crr_robertson_wride_1998`

<span class="gc-badge gc-available" data-geocore-function="crr_robertson_wride_1998">Available in GeoCore</span> [Soil dynamics › CPT Liquefaction › R&W (1998) CRR](/docs/geocore/using/modules#crr_robertson_wride_1998)

```python
crr_robertson_wride_1998(
    Qtn_cs,
    sigma_vo_eff,
    relative_density,
    atmospheric_pressure=100,
    **kwargs,
)
```

Calculates the Cyclic Resistance Ratio (CRR) and Overburden Correction Factor ($K_{\sigma}$) based on the methodology outlined by Robertson and Wride (1998).

The CRR is computed using normalized cone penetration resistance ($Q_{tn,cs}$) with fines correction. The CRR is calculated differently for three ranges of $Q_{tn,cs}$:

- For $Q_{tn,cs} < 50$, a linear relationship is used.
- For $50 \leq Q_{tn,cs} < 160$, a cubic relationship is used.
- For $Q_{tn,cs} \geq 160$, the CRR is set to infinity, indicating no liquefaction risk.

The overburden correction factor ($K_{\sigma}$) is calculated based on the effective vertical stress ($\sigma_v^{\prime}$) and relative density. If $\sigma_v^{\prime}$ is less than 100 kPa, $K_{\sigma}$ is set to 1. Otherwise, it is calculated using a power-law relationship.

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

$$
f_{K_{\sigma}} = 1 - \frac{D_r}{2}
$$

$$
f_{K_{\sigma}} = \min \left( \max \left( f_{K_{\sigma}}, 0.6 \right), 0.8 \right)
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `Qtn_cs` | - | Qtn_cs >= 0.0 | required | Normalized cone penetration resistance with fines correction ($Q_{tn,cs}$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Effective vertical stress at the depth of interest ($\sigma_v^{\prime}$) |
| `relative_density` | - | 0.0 <= relative_density <= 1.0 | required | Relative density of the soil ($D_r$) |
| `atmospheric_pressure` | kPa | atmospheric_pressure > 0.0 | `100` | Reference atmospheric pressure ($P_a$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `CRR [-]` | - | Cyclic resistance ratio ($CRR$) |
| `K_sigma [-]` | - | Overburden correction factor ($K_{\sigma}$) |

**Example**

```python
>>> result = crr_robertson_wride_1998(
...     Qtn_cs=120, sigma_vo_eff=80, relative_density=0.5
... )
>>> print(result)
{'CRR [-]': 0.18, 'K_sigma [-]': 1.0}
```

**References**

- Robertson, P. K., & Wride, C. E. (1998). Evaluating Cyclic Liquefaction Potential Using the Cone Penetration Test. Canadian Geotechnical Journal, 35(3).
- Youd, T. L., et al. (2001). Liquefaction Resistance of Soils: Summary Report from the 1996 NCEER and 1998 NCEER/NSF Workshops on Evaluation of Liquefaction Resistance of Soils. Journal of Geotechnical and Geoenvironmental Engineering, 127(10).

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="crr_idriss_boulanger_2008"></a>

## `crr_idriss_boulanger_2008`

<span class="gc-badge gc-available" data-geocore-function="crr_idriss_boulanger_2008">Available in GeoCore</span> [Soil dynamics › CPT Liquefaction › I&B (2008) CRR](/docs/geocore/using/modules#crr_idriss_boulanger_2008)

```python
crr_idriss_boulanger_2008(Qtn_cs, sigma_vo_eff, atmospheric_pressure=100, **kwargs)
```

Calculates the Cyclic Resistance Ratio (CRR) and Overburden Correction Factor ($K_{\sigma}$) based on the methodology outlined by Idriss and Boulanger (2008).

The CRR is computed using normalized cone penetration resistance ($Q_{tn,cs}$) with fines correction. The CRR is calculated using a polynomial function of $Q_{tn,cs}$ and is capped at a maximum value of 0.6.

The overburden correction factor ($K_{\sigma}$) is calculated based on the effective vertical stress ($\sigma_v^{\prime}$) and a stress correction coefficient ($C_{\sigma}$). The value of $K_{\sigma}$ is capped at 1.1.

$$
CRR = \min \left( \exp \left( \frac{Q_{tn,cs}}{540} + \left( \frac{Q_{tn,cs}}{67} \right)^2 - \left( \frac{Q_{tn,cs}}{80} \right)^3 + \left( \frac{Q_{tn,cs}}{114} \right)^4 - 3 \right), 0.6 \right)
$$

$$
C_{\sigma} = \min \left( \frac{1}{37.3 - 8.27 \cdot \min(Q_{tn,cs}, 211)^{0.264}}, 0.3 \right)
$$

$$
K_{\sigma} = \min \left( 1 - C_{\sigma} \cdot \ln \left( \frac{\sigma_v^{\prime}}{P_a} \right), 1.1 \right)
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `Qtn_cs` | - | Qtn_cs >= 0.0 | required | Normalized cone penetration resistance with fines correction ($Q_{tn,cs}$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Effective vertical stress at the depth of interest ($\sigma_v^{\prime}$) |
| `atmospheric_pressure` | kPa | atmospheric_pressure > 0.0 | `100` | Reference atmospheric pressure ($P_a$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `CRR [-]` | - | Cyclic resistance ratio ($CRR$) |
| `K_sigma [-]` | - | Overburden correction factor ($K_{\sigma}$) |

**Example**

```python
>>> result = crr_idriss_boulanger_2008(
...     Qtn_cs=120, sigma_vo_eff=80, atmospheric_pressure=100
... )
>>> print(result)
{'CRR [-]': 0.25, 'K_sigma [-]': 1.0}
```

**References**

- Idriss, I. M., & Boulanger, R. W. (2008). Soil Liquefaction During Earthquakes. Earthquake Engineering Research Institute.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="crr_boulanger_idriss_2014"></a>

## `crr_boulanger_idriss_2014`

<span class="gc-badge gc-available" data-geocore-function="crr_boulanger_idriss_2014">Available in GeoCore</span> [Soil dynamics › CPT Liquefaction › B&I (2014) CRR](/docs/geocore/using/modules#crr_boulanger_idriss_2014)

```python
crr_boulanger_idriss_2014(Qtn_cs, sigma_vo_eff, atmospheric_pressure=100, **kwargs)
```

Calculates the Cyclic Resistance Ratio (CRR) and Overburden Correction Factor ($K_{\sigma}$) based on the methodology outlined by Boulanger and Idriss (2014).

The CRR is computed using normalized cone penetration resistance ($Q_{tn,cs}$) with fines correction. The CRR is calculated using a polynomial function of $Q_{tn,cs}$ and is capped at a maximum value of 0.6.

The overburden correction factor ($K_{\sigma}$) is calculated based on the effective vertical stress ($\sigma_v^{\prime}$) and a stress correction coefficient ($C_{\sigma}$). The value of $K_{\sigma}$ is capped at 1.1.

$$
CRR = \min \left( \exp \left( \frac{Q_{tn,cs}}{113} + \left( \frac{Q_{tn,cs}}{1000} \right)^2 - \left( \frac{Q_{tn,cs}}{140} \right)^3 + \left( \frac{Q_{tn,cs}}{137} \right)^4 - 2.80 \right), 0.6 \right)
$$

$$
C_{\sigma} = \frac{1}{37.3 - 8.27 \cdot \min(Q_{tn,cs}, 211)^{0.264}}
$$

$$
K_{\sigma} = \min \left( 1 - C_{\sigma} \cdot \ln \left( \frac{\sigma_v^{\prime}}{P_a} \right), 1.1 \right)
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `Qtn_cs` | - | Qtn_cs >= 0.0 | required | Normalized cone penetration resistance with fines correction ($Q_{tn,cs}$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Effective vertical stress at the depth of interest ($\sigma_v^{\prime}$) |
| `atmospheric_pressure` | kPa | atmospheric_pressure > 0.0 | `100` | Reference atmospheric pressure ($P_a$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `CRR [-]` | - | Cyclic resistance ratio ($CRR$) |
| `K_sigma [-]` | - | Overburden correction factor ($K_{\sigma}$) |

**Example**

```python
>>> result = crr_boulanger_idriss_2014(
...     Qtn_cs=120, sigma_vo_eff=80, atmospheric_pressure=100
... )
>>> print(result)
{'CRR [-]': 0.25, 'K_sigma [-]': 1.0}
```

**References**

- Boulanger, R. W., & Idriss, I. M. (2014). CPT and SPT Liquefaction Triggering Procedures. Report No. UCD/CGM-14/01, University of California, Davis.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="qtn_cs_robertson_cabal_2022"></a>

## `Qtn_cs_robertson_cabal_2022`

<span class="gc-badge gc-available" data-geocore-function="Qtn_cs_robertson_cabal_2022">Available in GeoCore</span> [Soil dynamics › CPT Liquefaction › R&C (2022) Qtn,cs](/docs/geocore/using/modules#qtn_cs_robertson_cabal_2022)

```python
Qtn_cs_robertson_cabal_2022(
    ic,
    Fr,
    qt,
    sigma_vo_eff,
    sigma_vo,
    atmospheric_pressure=100,
    **kwargs,
)
```

Calculates the normalized cone penetration resistance with fines correction ($Q_{tn,cs}$) based on the methodology outlined by Robertson and Cabal (2022).

The calculation involves adjusting the cone tip resistance ($q_t$) for overburden stress effects and soil type using the soil behavior type index ($I_c$) and friction ratio ($F_r$). The normalization is performed using the exponent $n$, which depends on $I_c$ and effective vertical stress ($\sigma_v^{\prime}$).

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

$$
Q_{tn} = \left( \frac{q_t - \sigma_v}{P_a} \right) \cdot \left( \frac{P_a}{\sigma_v^{\prime}} \right)^n
$$

$$
Q_{tn,cs} = K_c \cdot Q_{tn}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `ic` | - | 1.0 <= ic <= 3.5 | required | Soil behavior type index ($I_c$) |
| `Fr` | - | 0.0 <= Fr <= 10.0 | required | Friction ratio ($F_r$) |
| `qt` | MPa | qt >= 0.0 | required | Total cone tip resistance ($q_t$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Effective vertical stress at the depth of interest ($\sigma_v^{\prime}$) |
| `sigma_vo` | kPa | sigma_vo >= 0.0 | required | Total vertical stress at the depth of interest ($\sigma_v$) |
| `atmospheric_pressure` | kPa | atmospheric_pressure > 0.0 | `100` | Reference atmospheric pressure ($P_a$) |

**Returns**

Dictionary with the following key:

| Key | Unit | Description |
|---|---|---|
| `Qtn_cs [-]` | - | Normalized cone resistance with fines correction ($Q_{tn,cs}$) |

**Example**

```python
>>> result = Qtn_cs_robertson_cabal_2022(
...     ic=2.0, Fr=0.3, qt=10, sigma_vo_eff=80, sigma_vo=100
... )
>>> print(result)
{'Qtn_cs [-]': 120.5}
```

**References**

- Robertson, P. K., & Cabal, K. L. (2022). Guide to Cone Penetration Testing for Geotechnical Engineering. Gregg Drilling & Testing, Inc.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="qtn_cs_robertson_wride_1998"></a>

## `Qtn_cs_robertson_wride_1998`

<span class="gc-badge gc-available" data-geocore-function="Qtn_cs_robertson_wride_1998">Available in GeoCore</span> [Soil dynamics › CPT Liquefaction › R&W (1998) Qtn,cs](/docs/geocore/using/modules#qtn_cs_robertson_wride_1998)

```python
Qtn_cs_robertson_wride_1998(sigma_vo, ic, qc, Fr, atmospheric_pressure=100, **kwargs)
```

Calculates the normalized cone penetration resistance with fines correction ($Q_{tn,cs}$) based on the methodology outlined by Robertson and Wride (1998).

The calculation involves normalizing the cone tip resistance ($q_c$) for overburden stress effects and adjusting for fines content using a fines correction factor ($K_c$). The stress normalization is performed using a correction factor ($C_Q$), which depends on total vertical stress ($\sigma_v$), and the final corrected resistance is obtained as $q_{c1N,cs}$.

$$
C_Q = \min \left( \left( \frac{P_a}{\sigma_v} \right)^{0.5}, 2 \right)
$$

$$
q_{c1N} = \frac{q_c}{0.001 P_a} \cdot C_Q
$$

$$
K_c = \begin{cases}
1.0 & \text{if } I_c \leq 1.64 \\
1.0 & \text{if } I_c < 2.36 \text{ and } F_r < 0.5 \\
-0.403 I_c^4 + 5.581 I_c^3 - 21.63 I_c^2 + 33.75 I_c - 17.88 & \text{otherwise}
\end{cases}
$$

$$
Q_{tn,cs} = K_c \cdot q_{c1N}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `sigma_vo` | kPa | sigma_vo > 0.0 | required | Total vertical stress at the depth of interest ($\sigma_v$) |
| `ic` | - | 1.0 <= ic <= 3.5 | required | Soil behavior type index ($I_c$) |
| `qc` | MPa | qc >= 0.0 | required | Total cone tip resistance ($q_c$) |
| `Fr` | - | 0.0 <= Fr <= 10.0 | required | Normalized friction ratio as a fraction ($F_r$) |
| `atmospheric_pressure` | kPa | atmospheric_pressure > 0.0 | `100` | Reference atmospheric pressure ($P_a$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff > 0.0 |  | Effective vertical stress at the depth of interest ($\sigma_v^{\prime}$) |

**Returns**

Dictionary with the following key:

| Key | Unit | Description |
|---|---|---|
| `Qtn_cs [-]` | - | Normalized cone resistance with fines correction ($Q_{tn,cs}$) |

**Example**

```python
>>> result = Qtn_cs_robertson_wride_1998(
...     sigma_vo=100, sigma_vo_eff=80, ic=2.0, qc=10, Fr=0.3
... )
>>> print(result)
{'Qtn_cs [-]': 95.4}
```

**References**

- Robertson, P. K., & Wride, C. E. (1998). Evaluating cyclic liquefaction potential using the cone penetration test. Canadian Geotechnical Journal, 35(3), 442-459.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="qtn_cs_idriss_boulanger_2008"></a>

## `Qtn_cs_idriss_boulanger_2008`

<span class="gc-badge gc-available" data-geocore-function="Qtn_cs_idriss_boulanger_2008">Available in GeoCore</span> [Soil dynamics › CPT Liquefaction › I&B (2008) Qtn,cs](/docs/geocore/using/modules#qtn_cs_idriss_boulanger_2008)

```python
Qtn_cs_idriss_boulanger_2008(sigma_vo_eff, qc, ic, atmospheric_pressure=100, **kwargs)
```

Calculates the normalized cone penetration resistance with fines correction ($Q_{tn,cs}$) based on the methodology outlined by Idriss and Boulanger (2008).

This method accounts for the effect of overburden stress, fines content, and stress normalization using an iterative approach to determine the exponent ($m$). The final normalized resistance ($q_{c1N,cs}$) is computed after applying fines content corrections.

$$
q_{c1N} = \max \left( \min \left( \frac{q_c}{0.001 P_a}, 254 \right), 21 \right)
$$

$$
m = 1.338 - 0.249 \cdot (q_{c1N})^{0.264}
$$

$$
C_N = \min \left( \left( \frac{P_a}{\sigma_v^{\prime}} \right)^m, 1.7 \right)
$$

$$
FC = 2.8 \cdot I_c^{2.6}
$$

$$
\Delta q_{c1N} = (5.4 + q_{c1N} / 16) \cdot \exp \left( 1.63 + \frac{9.7}{FC + 0.01} - \left( \frac{15.7}{FC + 0.01} \right)^2 \right)
$$

$$
Q_{tn,cs} = q_{c1N} + \Delta q_{c1N}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `sigma_vo_eff` | kPa | sigma_vo_eff > 0.0 | required | Effective vertical stress at the depth of interest ($\sigma_v^{\prime}$) |
| `qc` | MPa | qc >= 0.0 | required | Total cone tip resistance ($q_c$) |
| `ic` | - | 1.0 <= ic <= 3.5 | required | Soil behavior type index ($I_c$) |
| `atmospheric_pressure` | kPa | atmospheric_pressure > 0.0 | `100` | Reference atmospheric pressure ($P_a$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Qtn_cs [-]` | - | Normalized cone resistance with fines correction ($Q_{tn,cs}$) |
| `Fines [%]` | % | Estimated fines content as a percentage ($FC$) |

**Example**

```python
>>> result = Qtn_cs_idriss_boulanger_2008(
...     sigma_vo_eff=80, qc=10, ic=2.0
... )
>>> print(result)
{'Qtn_cs [-]': 85.2, 'Fines [%]': 14.7}
```

**References**

- Idriss, I. M., & Boulanger, R. W. (2008). Soil liquefaction during earthquakes. Earthquake Engineering Research Institute.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="qtn_cs_boulanger_idriss_2014"></a>

## `Qtn_cs_boulanger_idriss_2014`

<span class="gc-badge gc-available" data-geocore-function="Qtn_cs_boulanger_idriss_2014">Available in GeoCore</span> [Soil dynamics › CPT Liquefaction › B&I (2014) Qtn,cs](/docs/geocore/using/modules#qtn_cs_boulanger_idriss_2014)

```python
Qtn_cs_boulanger_idriss_2014(
    sigma_vo_eff,
    qc,
    ic,
    C_FC=0,
    atmospheric_pressure=100,
    **kwargs,
)
```

Calculates the normalized cone penetration resistance with fines correction ($Q_{tn,cs}$) based on the methodology outlined by Boulanger and Idriss (2014).

The calculation involves adjusting the cone tip resistance ($q_c$) for overburden stress effects and soil type using the soil behavior type index ($I_c$). The normalization is performed using the exponent $m$, which depends on $I_c$ and effective vertical stress ($\sigma_v^{\prime}$). Additionally, fines content ($FC$) is estimated as a function of $I_c$.

$$
FC = \min \left( \max \left( 80 \cdot (I_c + C_{FC}) - 137, 0 \right), 100 \right)
$$

$$
C_N = \min \left( \left( \frac{P_a}{\sigma_v^{\prime}} \right)^m, 1.7 \right)
$$

$$
Q_{tn} = C_N \cdot \frac{q_c}{0.001 P_a}
$$

$$
\Delta Q_{tn} = \left( 11.9 + \frac{Q_{tn}}{14.6} \right) \cdot
\exp \left( 1.63 - \frac{9.7}{FC + 2} - \left( \frac{15.7}{FC + 2} \right)^2 \right)
$$

$$
Q_{tn,cs} = Q_{tn} + \Delta Q_{tn}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `sigma_vo_eff` | kPa | $\sigma_v^{\prime} \geq 0.0$ | required | Effective vertical stress at the depth of interest ($\sigma_v^{\prime}$) |
| `qc` | MPa | $q_c \geq 0.0$ | required | Total cone tip resistance ($q_c$) |
| `ic` | - | $1.0 \leq I_c \leq 3.5$ | required | Soil behavior type index ($I_c$) |
| `C_FC` | - | Typically between -0.2 and 0.2 | `0` | Fitting parameter for fines content estimation ($C_{FC}$) |
| `atmospheric_pressure` | kPa | $P_a > 0.0$ | `100` | Reference atmospheric pressure ($P_a$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Qtn_cs [-]` | - | Normalized cone resistance with fines correction ($Q_{tn,cs}$) |
| `Fines [%]` | % | Estimated fines content ($FC$) |

**Example**

```python
>>> result = Qtn_cs_boulanger_idriss_2014(
...     sigma_vo_eff=80, qc=10, ic=2.0, C_FC=0
... )
>>> print(result)
{'Qtn_cs [-]': 120.5, 'Fines [%]': 25.3}
```

**References**

- Boulanger, R. W., & Idriss, I. M. (2014). CPT and SPT liquefaction triggering procedures. Report No. UCD/CGM-14/01, Center for Geotechnical Modeling, Department of Civil & Environmental Engineering, University of California, Davis.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="liquefaction_strains_zhang"></a>

## `liquefaction_strains_zhang`

<span class="gc-badge gc-available" data-geocore-function="liquefaction_strains_zhang">Available in GeoCore</span> [Soil dynamics › CPT Liquefaction › Zhang (2002) Liquefaction Strains](/docs/geocore/using/modules#liquefaction_strains_zhang)

```python
liquefaction_strains_zhang(FoS_liq, relative_density, Qtn_cs, **kwargs)
```

Calculates liquefaction-induced strains (volumetric and lateral) for level ground and lateral spreading based on the methodologies of Zhang et al. (2002, 2004).

The function estimates volumetric strain ($\epsilon_{liq}$) based on normalized cone penetration resistance ($Q_{tn,cs}$) and safety factor against liquefaction ($FoS_{liq}$). Lateral strain ($\gamma_{liq}$) is estimated using $FoS_{liq}$ and relative density ($D_r$).

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

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `FoS_liq` | - | $0.0 \leq FoS_{liq} \leq 5.0$ | required | Safety factor against liquefaction ($FoS_{liq}$) |
| `relative_density` | - | $0.0 \leq D_r \leq 2.0$ | required | Relative density ($D_r$) |
| `Qtn_cs` | - | $33 \leq Q_{tn,cs} \leq 200$ | required | Normalized cone resistance corrected for fines ($Q_{tn,cs}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `eps_liq [%]` | % | Volumetric strain as a percentage. ($\epsilon_{liq}$) |
| `gamma_liq [%]` | % | Lateral strain as a percentage. ($\gamma_{liq}$) |

**Example**

```python
>>> result = liquefaction_strains_zhang(FoS_liq=0.8, relative_density=0.6, Qtn_cs=100)
>>> print(result)
{'eps_liq [%]': 2.3, 'gamma_liq [%]': 14.5}
```

**References**

- Zhang, L., Robertson, P. K., & Brachman, R. W. I. (2002). Estimating liquefaction-induced ground settlements from CPT for level ground. *Canadian Geotechnical Journal, 39*(5), 1168-1180.
- Zhang, L., Robertson, P. K., & Brachman, R. W. I. (2004). Estimating liquefaction-induced lateral displacements using the standard penetration test or cone penetration test. *Journal of Geotechnical and Geoenvironmental Engineering, 130*(8), 861-871.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
