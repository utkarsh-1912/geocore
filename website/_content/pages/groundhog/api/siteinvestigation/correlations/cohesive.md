---
title: Cohesive soils
slug: groundhog/api/siteinvestigation/correlations/cohesive
section: Groundhog API Reference
description: 'API reference for groundhog.siteinvestigation.correlations.cohesive: 6 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/siteinvestigation/correlations/cohesive.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.siteinvestigation.correlations.cohesive
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/site_investigation/cohesive.html
geocore_available: true
geocore_functions:
- compressionindex_watercontent_koppula
- cv_liquidlimit_usnavy
- frictionangle_plasticityindex
- gmax_plasticityocr_andersen
- icl_scl_burland
- k0_plasticity_kenney
---

Module `groundhog.siteinvestigation.correlations.cohesive` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/siteinvestigation/correlations/cohesive.py).

Upstream documentation: [Cohesive soils](https://groundhog.readthedocs.io/en/main/site_investigation/cohesive.html).

**Functions:** [`compressionindex_watercontent_koppula`](#compressionindex_watercontent_koppula), [`frictionangle_plasticityindex`](#frictionangle_plasticityindex), [`cv_liquidlimit_usnavy`](#cv_liquidlimit_usnavy), [`gmax_plasticityocr_andersen`](#gmax_plasticityocr_andersen), [`k0_plasticity_kenney`](#k0_plasticity_kenney), [`icl_scl_burland`](#icl_scl_burland)

<a id="compressionindex_watercontent_koppula"></a>

## `compressionindex_watercontent_koppula`

<span class="gc-badge gc-available" data-geocore-function="compressionindex_watercontent_koppula">Available in GeoCore</span> [Site investigation › Correlations: Cohesive soils › Koppula (1981) Compression Index](/docs/geocore/using/modules#compressionindex_watercontent_koppula)

```python
compressionindex_watercontent_koppula(water_content, cc_cr_ratio=7.5, **kwargs)
```

Based on an evaluation of the compression index of clays and eight other soil mechanics parameters, Koppula (1981) concluded that the best fit was obtain using a direct relation with natural water content.

The recompression index is also calculated using a user-defined ratio of $C_c$ and $C_r$. This ratio is generally between 5 and 10.

$$
C_c = w_n
$$

$$
C_c / C_r = 5 \ \text{to} \ 10
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `water_content` | - | 0.0 <= water_content <= 4.0 | required | In-situ natural water content of the clay ($w_n$) |
| `cc_cr_ratio` | - | 5.0 <= cc_cr_ratio <= 10.0 | `7.5` | Ratio of compression index and recompression index ($C_r / C_c$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Cc [-]` | - | Compression index ($C_c$) |
| `Cr [-]` | - | Recompression index ($C_r$) |

**References**

- Koppula SD (1981) Statistical evaluation of compression index. Geotech Test J ASTM 4(2):68–73

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="frictionangle_plasticityindex"></a>

## `frictionangle_plasticityindex`

<span class="gc-badge gc-available" data-geocore-function="frictionangle_plasticityindex">Available in GeoCore</span> [Site investigation › Correlations: Cohesive soils › Drained Friction Angle (from Plasticity Index)](/docs/geocore/using/modules#frictionangle_plasticityindex)

```python
frictionangle_plasticityindex(plasticity_index, **kwargs)
```

Based on a dataset of soft to stiff clays, a correlation between plasticity index and drained friction angle of clay is proposed. It should be noted that the friction angle of overconsolidated depends strongly on the in-situ condition. If the overconsolidated is fissured, the available shearing resistance will be lower than the value resulting from the correlation.

![Dataset used for the correlation](/docs/assets/groundhog/docs/site_investigation/images/frictionangle_plasticityindex_1.png)

*Dataset used for the correlation*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `plasticity_index` | pct | 5.0 <= plasticity_index <= 1000.0 | required | Plasticity index of the clay as determined from Atterberg limit tests ($PI$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Effective friction angle [deg]` | deg | Drained friction angle of the clay ($\varphi^{\prime}$) |

**References**

- Terzaghi, K., Peck, R. B., & Mesri, G. (1996). Soil mechanics in engineering practice. John Wiley & Sons.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="cv_liquidlimit_usnavy"></a>

## `cv_liquidlimit_usnavy`

<span class="gc-badge gc-available" data-geocore-function="cv_liquidlimit_usnavy">Available in GeoCore</span> [Site investigation › Correlations: Cohesive soils › US Navy Cv from Liquid Limit](/docs/geocore/using/modules#cv_liquidlimit_usnavy)

```python
cv_liquidlimit_usnavy(liquid_limit, trend='NC', **kwargs)
```

Calculates an estimate of the coefficient of consolidation based on the liquid limit of a clay. Three trends are available; an upper bound trend for remoulded clays, a trend for normally consolidated and a lower bound trend for undisturbed overconsolidated clay. Note that sample disturbance can lead to a reduced coefficient of consolidation.

![Proposed relation between coefficient of consolidation and liquid limit](/docs/assets/groundhog/docs/site_investigation/images/cv_liquidlimit_usnavy_1.png)

*Proposed relation between coefficient of consolidation and liquid limit*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `liquid_limit` | pct | 20.0 <= liquid_limit <= 160.0 | required | Liquid limit of the clay ($LL$) |
| `trend` |  | one of `Remoulded`, `NC`, `OC` | `'NC'` | Choice of trend, choose between trends for remoulded, NC and OC clay |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `cv [m2/yr]` | m2/yr | Coefficient of consolidation ($c_v$) |

**References**

- U.S. Navy (1982) Soil mechanics – design manual 7.1, Department of the Navy, Naval Facilities Engineering Command, U.S. Government Printing Office, Washington, DC

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="gmax_plasticityocr_andersen"></a>

## `gmax_plasticityocr_andersen`

<span class="gc-badge gc-available" data-geocore-function="gmax_plasticityocr_andersen">Available in GeoCore</span> [Site investigation › Correlations: Cohesive soils › Andersen Gmax (Plasticity & OCR)](/docs/geocore/using/modules#gmax_plasticityocr_andersen)

```python
gmax_plasticityocr_andersen(
    pi,
    ocr,
    sigma_vo_eff,
    atmospheric_pressure=100.0,
    coefficient_1=30.0,
    coefficient_2=75.0,
    coefficient_3=0.03,
    coefficient_4=0.5,
    coefficient_5=0.9,
    **kwargs,
)
```

Calculates the small-strain shear modulus for cohesive soils based on plasticity index, effective overburden pressure and OCR. The proposed relation is calibrated on a number of shear wave velocity tests on clay samples with different plasticity index and OCR.

$$
\frac{G_{max}}{\sigma_{ref}^{\prime}} = \left( 30 + \frac{75}{\frac{I_p}{100} + 0.03} \right) \cdot OCR^{0.5}
$$

$$
\sigma_{ref}^{\prime} = P_a \cdot \left( \sigma_{0}^{\prime}  / P_a \right)^{0.9}
$$

*Figure `images/gmax_plasticityocr_andersen_1.png` is referenced by the docstring but is not present in the groundhog repository at `dc7d554c6b8986bae30f518304546a911b1ca5ab`.*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `pi` | pct | 0.0 <= PI <= 160.0 | required | Plasticity index (difference between liquid limit and plastic limit) ($PI$) |
| `ocr` | - | 1.0 <= OCR <= 40.0 | required | Overconsolidation ratio of the clay ($OCR$) |
| `sigma_vo_eff` | kPa | 0.0 <= sigma_vo_eff <= 1000.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `atmospheric_pressure` | kPa | 90.0 <= atmospheric_pressure <= 110.0 | `100.0` | Atmospheric pressure ($P_a$) |
| `coefficient_1` | - |  | `30.0` | First calibration coefficient |
| `coefficient_2` | - |  | `75.0` | Second calibration coefficient |
| `coefficient_3` | - |  | `0.03` | Third calibration coefficient |
| `coefficient_4` | - |  | `0.5` | Fourth calibration coefficient (exponent for OCR) |
| `coefficient_5` | - |  | `0.9` | Fifth calibration coefficient (exponent for sigma_ref) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `sigma_0_ref [kPa]` | kPa | Reference stress ($\sigma_{ref}^{\prime}$) |
| `Gmax [kPa]` | kPa | Small-strain shear modulus ($G_{max}$) |

**References**

- Andersen KH. Cyclic soil parameters for offshore foundation design. The Third ISSMGE McClelland Lecture. In: Meyer V, editor. Proc. Int. Symp. Frontiers in offshore geotechnics, ISFOG 2015. London: Taylor and Francis; 2015. 5–82.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="k0_plasticity_kenney"></a>

## `k0_plasticity_kenney`

<span class="gc-badge gc-available" data-geocore-function="k0_plasticity_kenney">Available in GeoCore</span> [Site investigation › Correlations: Cohesive soils › Kenney K0 (from Plasticity, Clay)](/docs/geocore/using/modules#k0_plasticity_kenney)

```python
k0_plasticity_kenney(
    pi,
    ocr=1,
    coeff_1=0.19,
    coeff_2=0.233,
    coeff_3=-281,
    coeff_4=1.85,
    **kwargs,
)
```

Calculates the coefficient of lateral earthpressure at rest for normally and overconsolidated clay. Kenney (1959) presented a formula for coefficient of lateral earth pressure at rest for normally consolidated clay. The plasticity index $\text{PI}$ was used as a basis for this correlation. This relation was modified for the effect of overconsolidation as shown by Alpan (1967). The exponent on OCR shows a linear variation with plasticity index.

$$
K_{0,NC} = 0.19 + 0.233 \log_{10} I_p
$$

$$
I_p = -281 \log_{10} \left( 1.85 \lambda \right)
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `pi` | pct | 5 <= PI <= 80 | required | Plasticity index ($\text{PI}$) |
| `ocr` | - | 1 <= ocr <= 30 | `1` | Overconsolidation ratio ($\text{OCR}$) |
| `coeff_1` |  |  | `0.19` | First calibration coefficient |
| `coeff_2` |  |  | `0.233` | Second calibration coefficient |
| `coeff_3` |  |  | `-281` | First calibration coefficient |
| `coeff_4` |  |  | `1.85` | Second calibration coefficient |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `K0 NC [-]` | - | Coefficient of lateral earth pressure at rest for normally consolidated conditions ($K_{0,NC}$) |
| `K0 [-]` | - | Coefficient of lateral earth pressure at rest ($K_0$) |

**References**

- Alpan (1967) THE EMPIRICAL EVALUATION OF THE COEFFICIENT K0 AND K0R. Soils and Foundations. Volume 7, Issue 1

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="icl_scl_burland"></a>

## `icl_scl_burland`

<span class="gc-badge gc-available" data-geocore-function="icl_scl_burland">Available in GeoCore</span> [Site investigation › Correlations: Cohesive soils › Burland (1990) Intrinsic & Sedimentation Compression Lines](/docs/geocore/using/modules#icl_scl_burland)

```python
icl_scl_burland(
    eL,
    coefficient_1=2.45,
    coefficient_2=-1.285,
    coefficient_3=0.015,
    coefficient_4=0.109,
    coefficient_5=0.679,
    coefficient_6=-0.089,
    coefficient_7=0.016,
    coefficient_8=0.256,
    coefficient_9=-0.04,
    e100star_override=nan,
    Ccstaroverride=nan,
    **kwargs,
)
```

Calculates the Intrinsic Compression Line (ICL), representing void ratios of clays deposited from a slurry (mixed at a water content of at least 125% of the liquid limit). The void ratios at different pressures are calculated. The ICL is a useful reference for any material as it represents the states of a fully destructured clay.

The Sedimentation Compression Line (SCL) represents the state of a naturally deposited clay. Clays deposited in a very calm environment (slurrylike deposition) can have natural states below the SCL. Clays deposited in environments leading to high amounts of structure (e.g. quick clays) can plot well above the SCL.

Note that the void ratio on the ICL for a pressure of 100kPa can be correlated from the liquid limit of the material. The correlation was developed based on measurements on numerous clays but the plasticity limits need to plot above the A-line for the correlation to apply. This correlation is included in the formulation, but this void ratio can also be specified directly.

$$
I_v = \frac{e - e_{100}^*}{e_{100}^* - e_{1000}^*}
$$

$$
I_v = 2.45 - 1.285 \log \sigma_{v}^{\prime} + 0.015 \left(\log \sigma_{v}^{\prime} \right)^3
$$

$$
e = I_v \left( e_{100}^* - e_{1000}^* \right) + e_{100}^*
$$

$$
e_{100}^* = 0.109 + 0.679 e_L - 0.089 e_L^2 + 0.016 e_L^3
$$

$$
C_c^* = 0.256 e_L - 0.04
$$

![ICL and SCL with associated data based on Burland (1990)](/docs/assets/groundhog/docs/site_investigation/images/icl_scl_burland.png)

*ICL and SCL with associated data based on Burland (1990)*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `eL` | - | 0.6 <= eL <= 4.5 | required | Void ratio at the liquid limit ($e_L$) |
| `coefficient_1` | - |  | `2.45` | First calibration coefficient ($-$) |
| `coefficient_2` | - |  | `-1.285` | Second calibration coefficient ($-$) |
| `coefficient_3` | - |  | `0.015` | Third calibration coefficient ($-$) |
| `coefficient_4` | - |  | `0.109` | Fourth calibration coefficient ($-$) |
| `coefficient_5` | - |  | `0.679` | Fifth calibration coefficient ($-$) |
| `coefficient_6` | - |  | `-0.089` | Sixth calibration coefficient ($-$) |
| `coefficient_7` | - |  | `0.016` | Seventh calibration coefficient ($-$) |
| `coefficient_8` | - |  | `0.256` | Eighth calibration coefficient ($-$) |
| `coefficient_9` | - |  | `-0.04` | Ninth calibration coefficient ($-$) |
| `e100star_override` | - |  | `nan` | Override value of void ratio on the ICL at 100kPa ($-$) |
| `Ccstaroverride` | - |  | `nan` | Override value of intrinsic compression index ($-$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Ccstar [-]` | - | Intrinsic compression index [-] ($C_c^*$) |
| `e100star [-]` | - | Intrinsic void ratio at 100kPa [-] ($e_{100}^*$) |
| `pressures_icl [kPa]` | kPa | Array with pressures for the ICL [kPa] ($\sigma_v^{\prime}$) |
| `pressures_scl [kPa]` | kPa | Array with pressures for the SCL [kPa] ($\sigma_v^{\prime}$) |
| `Iv_icl [-]` | - | Iv values for ICL [-] ($I_v$) |
| `Iv_scl [-]` | - | Iv values for SCL [-] ($I_v$) |
| `e_icl [-]` | - | Void ratios for ICL [-] ($e_{ICL}$) |
| `e_scl [-]` | - | Void ratios for SCL [-] ($e_{SCL}$) |

**References**

- Burland (1990). On the compressibility and shear strength of natural clays. Géotechnique.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
