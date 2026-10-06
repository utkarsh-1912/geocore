---
title: PCPT functions
slug: groundhog/api/siteinvestigation/insitutests/pcpt_correlations
section: Groundhog API Reference
description: 'API reference for groundhog.siteinvestigation.insitutests.pcpt_correlations: 34 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/siteinvestigation/insitutests/pcpt_correlations.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.siteinvestigation.insitutests.pcpt_correlations
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/site_investigation/pcpt_functions.html
geocore_available: true
geocore_functions:
- behaviourindex_pcpt_nonnormalised
- behaviourindex_pcpt_robertsonwride
- clippingdepths_qc1N_tianlehane
- coneresistance_ocsand_baldi
- constrainedmodulus_pcpt_robertson
- dissipation_test_teh
- drainedsecantmodulus_sand_bellotti
- frictionangle_overburden_kleven
- frictionangle_sand_kulhawymayne
- gmax_clay_maynerix
- gmax_cpt_puechen
- gmax_sand_rixstokoe
- gmax_voidratio_maynerix
- ic_soilclass_robertson
- k0_sand_mayne
- ocr_cpt_lunne
- pcpt_normalisations
- relativedensity_ncsand_baldi
- relativedensity_ocsand_baldi
- relativedensity_sand_jamiolkowski
- sensitivity_frictionratio_lunne
- soilclass_robertson
- soiltype_vs_longodonohue
- undrainedshearstrength_clay_radlunne
- unitweight_mayne
- vs_cpt_andrus
- vs_cpt_hegazymayne
- vs_cpt_longdonohue
- vs_cpt_mcgannetal
- vs_cpt_tonniandsimonini
- vs_cpt_wrideetal
- vs_cptd50_karrayetal
- vs_ic_robertsoncabal
- vs_stressdependent_stuyts
---

Module `groundhog.siteinvestigation.insitutests.pcpt_correlations` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/siteinvestigation/insitutests/pcpt_correlations.py).

Upstream documentation: [PCPT functions](https://groundhog.readthedocs.io/en/main/site_investigation/pcpt_functions.html).

**Functions:** [`pcpt_normalisations`](#pcpt_normalisations), [`soilclass_robertson`](#soilclass_robertson), [`ic_soilclass_robertson`](#ic_soilclass_robertson), [`behaviourindex_pcpt_robertsonwride`](#behaviourindex_pcpt_robertsonwride), [`gmax_sand_rixstokoe`](#gmax_sand_rixstokoe), [`gmax_clay_maynerix`](#gmax_clay_maynerix), [`relativedensity_ncsand_baldi`](#relativedensity_ncsand_baldi), [`relativedensity_ocsand_baldi`](#relativedensity_ocsand_baldi), [`coneresistance_ocsand_baldi`](#coneresistance_ocsand_baldi), [`relativedensity_sand_jamiolkowski`](#relativedensity_sand_jamiolkowski), [`frictionangle_sand_kulhawymayne`](#frictionangle_sand_kulhawymayne), [`undrainedshearstrength_clay_radlunne`](#undrainedshearstrength_clay_radlunne), [`frictionangle_overburden_kleven`](#frictionangle_overburden_kleven), [`ocr_cpt_lunne`](#ocr_cpt_lunne), [`sensitivity_frictionratio_lunne`](#sensitivity_frictionratio_lunne), [`unitweight_mayne`](#unitweight_mayne), [`vs_ic_robertsoncabal`](#vs_ic_robertsoncabal), [`k0_sand_mayne`](#k0_sand_mayne), [`gmax_cpt_puechen`](#gmax_cpt_puechen), [`behaviourindex_pcpt_nonnormalised`](#behaviourindex_pcpt_nonnormalised), [`drainedsecantmodulus_sand_bellotti`](#drainedsecantmodulus_sand_bellotti), [`gmax_voidratio_maynerix`](#gmax_voidratio_maynerix), [`vs_cpt_andrus`](#vs_cpt_andrus), [`vs_cpt_hegazymayne`](#vs_cpt_hegazymayne), [`vs_cpt_longdonohue`](#vs_cpt_longdonohue), [`soiltype_vs_longodonohue`](#soiltype_vs_longodonohue), [`vs_cptd50_karrayetal`](#vs_cptd50_karrayetal), [`vs_cpt_wrideetal`](#vs_cpt_wrideetal), [`vs_cpt_tonniandsimonini`](#vs_cpt_tonniandsimonini), [`vs_cpt_mcgannetal`](#vs_cpt_mcgannetal), [`constrainedmodulus_pcpt_robertson`](#constrainedmodulus_pcpt_robertson), [`vs_stressdependent_stuyts`](#vs_stressdependent_stuyts), [`dissipation_test_teh`](#dissipation_test_teh), [`clippingdepths_qc1N_tianlehane`](#clippingdepths_qc1n_tianlehane)

<a id="pcpt_normalisations"></a>

## `pcpt_normalisations`

<span class="gc-badge gc-available" data-geocore-function="pcpt_normalisations">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › PCPT Normalisation & Correction](/docs/geocore/using/modules#pcpt_normalisations)

```python
pcpt_normalisations(
    measured_qc,
    measured_fs,
    measured_u2,
    sigma_vo_tot,
    sigma_vo_eff,
    depth,
    cone_area_ratio,
    start_depth=0.0,
    unitweight_water=10.25,
    atmospheric_pressure=100,
    ic_min=1.0,
    ic_max=4.0,
    zhang_multiplier_1=0.381,
    zhang_multiplier_2=0.05,
    zhang_subtraction=0.15,
    robertsonwride_coefficient1=3.47,
    robertsonwride_coefficient2=1.22,
    cn_capping=1.7,
    **kwargs,
)
```

Carried out the necessary normalisation and correction on PCPT data to allow calculation of derived parameters and soil type classification.

For a downhole test, the depth of the test and the unit weight of water can optionally be provided. If no start depth is specified, a continuous test starting from the surface is assumed. The measurements are corrected for this effect.

Next, the cone resistance is corrected for the unequal area effect using the cone area ratio. The correction for total sleeve friction is not included as it is more uncommon. The procedure assumes that the pore pressure are measured at the shoulder of the cone. If this is not the case, corrections can be used which are not included in this function.

During normalisation, the friction ratio and pore pressure ratio are calculated. Note that the total cone resistance is used for the friction ratio and pore pressure ratio calculation, the pore pressure ratio calculation also used the total vertical effective stress. The normalised cone resistance and normalised friction ratio are also calculated.

Finally the net cone resistance is calculated.

$$
q_c = q_c^* + d \cdot a \cdot \gamma_w
$$

$$
q_t = q_c + u_2 \cdot (1 - a)
$$

$$
u_2 = u_2^* + \gamma_w \cdot d
$$

$$
\Delta u_2 = u_2 - u_o
$$

$$
R_f = \frac{f_s}{q_t}
$$

$$
B_q = \frac{\Delta u_2}{q_t - \sigma_{vo}}
$$

$$
Q_t = \frac{q_t - \sigma_{vo}}{\sigma_{vo}^{\prime}}
$$

$$
Cn = \min(1.7, \left(\frac{P_a}{\sigma_{vo}^{\prime}}\right)^n)
$$

$$
Q_{tn} = \frac{q_t - \sigma_{vo}}{P_a} \cdot Cn
$$

$$
n = 0.381 \cdot I_c + 0.05 \cdot \frac{\sigma_{vo}^{\prime}}{P_a} - 0.15 \ \text{where} \ n \leq 1
$$

$$
F_r = \frac{f_s}{q_t - \sigma_{vo}}
$$

$$
q_{net} = q_t - \sigma_{vo}
$$

![Pore water pressure effects on measured parameters](/docs/assets/groundhog/docs/site_investigation/images/pcpt_normalisations_1.png)

*Pore water pressure effects on measured parameters*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `measured_qc` | MPa | 0.0 <= measured_qc <= 150.0 | required | Measured cone resistance ($q_c^*$) |
| `measured_fs` | MPa | 0.0 <= measured_fs <= 10.0 | required | Measured sleeve friction ($f_s^*$) |
| `measured_u2` | MPa | -10.0 <= measured_u2 <= 10.0 | required | Pore pressure measured at the shoulder ($u_2^*$) |
| `sigma_vo_tot` | kPa | sigma_vo_tot >= 0.0 | required | Total vertical stress ($\sigma_{vo}$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Effective vertical stress ($\sigma_{vo}^{\prime}$) |
| `depth` | m | depth >= 0.0 | required | Depth below surface (for saturated soils) where measurement is taken. For onshore tests, use the depth below the watertable. ($z$) |
| `cone_area_ratio` | - | 0.0 <= cone_area_ratio <= 1.0 | required | Ratio between the cone rod area and the maximum cone area ($a$) |
| `start_depth` | m | start_depth >= 0.0 | `0.0` | Start depth of the test, specify this for a downhole test. Leave at zero for a test starting from surface ($d$) |
| `unitweight_water` | kN/m3 | 9.0 <= unitweight_water <= 11.0 | `10.25` | Unit weight of water, default is for seawater ($\gamma_w$) |
| `atmospheric_pressure` | kPa |  | `100` | Atmospheric pressure (used for normalisation) ($P_a$) |
| `ic_min` | - |  | `1.0` | Minimum value for soil behaviour type index used in the optimisation routine ($I_{c,min}$) |
| `ic_max` | - |  | `4.0` | Maximum value for soil behaviour type index used in the optimisation routine ($I_{c,max}$) |
| `zhang_multiplier_1` | - |  | `0.381` | First multiplier in the equation for exponent n |
| `zhang_multiplier_2` | - |  | `0.05` | Second multiplier in the equation for exponent n |
| `zhang_subtraction` | - |  | `0.15` | Term subtracted in the equation for exponent n |
| `robertsonwride_coefficient1` | - |  | `3.47` | First coefficient in the equation by Robertson and Wride |
| `robertsonwride_coefficient2` | - |  | `1.22` | Second coefficient in the equation by Robertson and Wride |
| `cn_capping` |  |  | `1.7` | No upstream documentation. |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `qt [MPa]` | MPa | Total cone resistance ($q_t$) |
| `qc [MPa]` | MPa | Cone resistance corrected for downhole effect ($q_c$) |
| `u2 [MPa]` | MPa | Pore pressure at the shoulder corrected for downhole effect ($u_2$) |
| `Delta u2 [MPa]` | MPa | Difference between measured pore pressure at the shoulder and hydrostatic pressure ($\Delta u_2$) |
| `Rf [pct]` | pct | Ratio of sleeve friction to total cone resistance (note that it is expressed as a percentage) ($R_f$) |
| `Bq [-]` | - | Pore pressure ratio ($B_q$) |
| `Qt [-]` | - | Normalised cone resistance ($Q_t$) |
| `Fr [-]` | - | Normalised friction ratio ($F_r$) |
| `qnet [MPa]` | MPa | Net cone resistance ($q_{net}$) |
| `exponent_zhang [-]` | - | Exponent n according to Zhang et al ($n$) |
| `Qtn [-]` | - | Normalised cone resistance ($Q_{tn}$) |
| `Fr [%]` | % | Normalised friction ratio ($F_r$) |
| `Ic [-]` | - | Soil behaviour type index ($I_c$) |
| `Ic class number [-]` | - | Soil behaviour type class number according to the Robertson chart |
| `Ic class` |  | Soil behaviour type class description according to the Robertson chart |

**References**

- Lunne, T., Robertson, P.K., Powell, J.J.M., 1997. Cone penetration testing in geotechnical practice. E & FN Spon.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="soilclass_robertson"></a>

## `soilclass_robertson`

<span class="gc-badge gc-available" data-geocore-function="soilclass_robertson">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Robertson & Wride Soil Classification](/docs/geocore/using/modules#soilclass_robertson)

```python
soilclass_robertson(ic_class_number, **kwargs)
```

Provides soil type classification according to the soil behaviour type index by Robertson and Wride.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `ic_class_number` | - | ic = 1 to 9 | required | Soil behaviour type index class number ($I_c$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Soil type` |  | Description of the soil type in the Robertson chart |

**References**

- Fugro guidance on PCPT interpretation

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="ic_soilclass_robertson"></a>

## `ic_soilclass_robertson`

<span class="gc-badge gc-available" data-geocore-function="ic_soilclass_robertson">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Robertson & Wride Soil Classification (Ic)](/docs/geocore/using/modules#ic_soilclass_robertson)

```python
ic_soilclass_robertson(ic, **kwargs)
```

Provides soil type classification according to the soil behaviour type index by Robertson and Wride.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `ic` | - | 1.0 <= ic <= 5.0 | required | Soil behaviour type index ($I_c$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Soil type number [-]` | - | Number of the soil type in the Robertson chart |
| `Soil type` |  | Description of the soil type in the Robertson chart |

**References**

- Fugro guidance on PCPT interpretation

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="behaviourindex_pcpt_robertsonwride"></a>

## `behaviourindex_pcpt_robertsonwride`

<span class="gc-badge gc-available" data-geocore-function="behaviourindex_pcpt_robertsonwride">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Robertson & Wride (1998) Soil Behaviour Index](/docs/geocore/using/modules#behaviourindex_pcpt_robertsonwride)

```python
behaviourindex_pcpt_robertsonwride(
    qt,
    fs,
    sigma_vo,
    sigma_vo_eff,
    atmospheric_pressure=100.0,
    ic_min=1.0,
    ic_max=4.0,
    zhang_multiplier_1=0.381,
    zhang_multiplier_2=0.05,
    zhang_subtraction=0.15,
    robertsonwride_coefficient1=3.47,
    robertsonwride_coefficient2=1.22,
    cn_capping=1.7,
    **kwargs,
)
```

Calculates the soil behaviour index according to Robertson and Wride (1998). This index is a measure for the behaviour of soils. Soils with a value below 2.5 are generally cohesionless and coarse grained whereas a value above 2.7 indicates cohesive, fine-grained sediments. Between 2.5 and 2.7, partially drained behaviour is expected. The exponent n in the equations is used to account for different cone resistance normalisation in non-clayey soils (lower exponent). Because the exponent n is defined implicitly, an iterative approach is required to calculate the soil behaviour type index.

When used with `apply_correlation`, use `'Ic Robertson and Wride (1998)'` as correlation name.

$$
Cn = \min(1.7, \left(\frac{P_a}{\sigma_{vo}^{\prime}}\right)^n)
Q_{tn} = \frac{q_t - \sigma_{vo}}{P_a} \cdot Cn
\\
n = 0.381 \cdot I_c + 0.05 \cdot \frac{\sigma_{vo}^{\prime}}{P_a} - 0.15 \ \text{where} \ n \leq 1
\\
I_c = \sqrt{ \left( 3.47 - \log_{10} Q_{tn} \right)^2 + \left( \log_{10} F_r + 1.22 \right)^2 }
$$

![Contour lines for soil behaviour type index](/docs/assets/groundhog/docs/site_investigation/images/behaviourindex_pcpt_robertsonwride_1.png)

*Contour lines for soil behaviour type index*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qt` | MPa | 0.0 <= qt <= 120.0 | required | Corrected cone resistance ($q_t$) |
| `fs` | MPa | fs >= 0.0 | required | Sleeve friction ($f_s$) |
| `sigma_vo` | kPa | sigma_vo >= 0.0 | required | Total vertical stress ($\sigma_{vo}$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 9.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `atmospheric_pressure` | kPa |  | `100.0` | Atmospheric pressure (used for normalisation) ($P_a$) |
| `ic_min` | - |  | `1.0` | Minimum value for soil behaviour type index used in the optimisation routine ($I_{c,min}$) |
| `ic_max` | - |  | `4.0` | Maximum value for soil behaviour type index used in the optimisation routine ($I_{c,max}$) |
| `zhang_multiplier_1` | - |  | `0.381` | First multiplier in the equation for exponent n |
| `zhang_multiplier_2` | - |  | `0.05` | Second multiplier in the equation for exponent n |
| `zhang_subtraction` | - |  | `0.15` | Term subtracted in the equation for exponent n |
| `robertsonwride_coefficient1` | - |  | `3.47` | First coefficient in the equation by Robertson and Wride |
| `robertsonwride_coefficient2` | - |  | `1.22` | Second coefficient in the equation by Robertson and Wride |
| `cn_capping` |  |  | `1.7` | No upstream documentation. |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `exponent_zhang [-]` | - | Exponent n according to Zhang et al ($n$) |
| `Qtn [-]` | - | Normalised cone resistance ($Q_{tn}$) |
| `Fr [%]` | % | Normalised friction ratio ($F_r$) |
| `Ic [-]` | - | Soil behaviour type index ($I_c$) |
| `Ic class number [-]` | - | Soil behaviour type class number according to the Robertson chart |
| `Ic class` |  | Soil behaviour type class description according to the Robertson chart |

**References**

- Fugro guidance on PCPT interpretation

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="gmax_sand_rixstokoe"></a>

## `gmax_sand_rixstokoe`

<span class="gc-badge gc-available" data-geocore-function="gmax_sand_rixstokoe">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Rix & Stokoe Gmax (Sand, CPT)](/docs/geocore/using/modules#gmax_sand_rixstokoe)

```python
gmax_sand_rixstokoe(
    qc,
    sigma_vo_eff,
    multiplier=1634.0,
    qc_exponent=0.25,
    stress_exponent=0.375,
    **kwargs,
)
```

Calculates the small-strain shear modulus for uncemented silica sand based on cone resistance and vertical effective stress. The correlation is based on calibration chamber tests compared to results from PCPT, S-PCPT and cross-hole tests reported by Baldi et al (1989).

When used with `apply_correlation`, use `'Gmax Rix and Stokoe (1991)'` as correlation name.

$$
G_{max} = 1634 \cdot (q_c)^{0.25} \cdot (\sigma_{vo}^{\prime})^{0.375}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc` | MPa | 0.0 <= qc <= 120.0 | required | Cone tip resistance ($q_c$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `multiplier` | - |  | `1634.0` | Multiplier in the correlation equation |
| `qc_exponent` | - |  | `0.25` | Exponent applied on the cone tip resistance |
| `stress_exponent` | - |  | `0.375` | Exponent applied on the vertical effective stress |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Gmax [kPa]` | kPa | Small-strain shear modulus ($G_{max}$) |

**References**

- Rix, G.J. and Stokoe, K.H. (II) (1991), “Correlation of Initial Tangent Modulus and Cone Penetration Resistance”, in Huang, A.B. (Ed.), Calibration Chamber Testing: Proceedings of the First International Symposium on Calibration Chamber Testing ISOCCTI, Potsdam, New York, 28-29 June 1991, Elsevier Science Publishing Company, New York, pp. 351-362.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="gmax_clay_maynerix"></a>

## `gmax_clay_maynerix`

<span class="gc-badge gc-available" data-geocore-function="gmax_clay_maynerix">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Mayne & Rix (1993) Gmax for Clay](/docs/geocore/using/modules#gmax_clay_maynerix)

```python
gmax_clay_maynerix(qc, multiplier=2.78, exponent=1.335, **kwargs)
```

Mayne and Rix (1993) determined a relationship between small-strain shear modulus and cone tip resistance by studying 481 data sets from 31 sites all over the world. Gmax ranged between about 0.7 MPa and 800 MPa.

When used with `apply_correlation`, use `'Gmax Mayne and Rix (1993)'` as correlation name.

$$
G_{max} = 2.78 \cdot q_c^{1.335}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc` | MPa | 0.0 <= qc <= 120.0 | required | Cone tip resistance ($q_c$) |
| `multiplier` | - |  | `2.78` | Multiplier in the equation |
| `exponent` | - |  | `1.335` | Exponent in the equation |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Gmax [kPa]` | kPa | Small-strain shear modulus ($G_{max}$) |

**References**

- Mayne, P.W. and Rix, G.J. (1993), “Gmax-qc Relationships for Clays”, Geotechnical Testing Journal, Vol. 16, No. 1, pp. 54-60.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="relativedensity_ncsand_baldi"></a>

## `relativedensity_ncsand_baldi`

<span class="gc-badge gc-available" data-geocore-function="relativedensity_ncsand_baldi">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Baldi Relative Density (NC Sand)](/docs/geocore/using/modules#relativedensity_ncsand_baldi)

```python
relativedensity_ncsand_baldi(
    qc,
    sigma_vo_eff,
    coefficient_0=157.0,
    coefficient_1=0.55,
    coefficient_2=2.41,
    **kwargs,
)
```

Calculates the relative density for normally consolidated sand based on calibration chamber tests on silica sand. It should be noted that this correlation provides an approximative estimate of relative density and the sand at the site should be compared to the sands used in the calibration chamber tests. The correlation will always be sensitive to variations in compressibility and horizontal stress.

When used with `apply_correlation`, use `'Dr Baldi et al (1986) - NC sand'` as correlation name.

$$
D_r = \frac{1}{2.41} \cdot \ln \left[ \frac{q_c}{157 \cdot \left( \sigma_{vo}^{\prime} \right)^{0.55} } \right]
$$

![Relationship between cone tip resistance, vertical effective stress and relative density for normally consolidated Ticino sand](/docs/assets/groundhog/docs/site_investigation/images/relativedensity_ncsand_baldi_1.png)

*Relationship between cone tip resistance, vertical effective stress and relative density for normally consolidated Ticino sand*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc` | MPa | 0.0 <= qc <= 120.0 | required | Cone tipe resistance ($q_c$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `coefficient_0` | - |  | `157.0` | Coefficient C0 ($C_0$) |
| `coefficient_1` | - |  | `0.55` | Coefficient C1 ($C_1$) |
| `coefficient_2` | - |  | `2.41` | Coefficient C2 ($C_2$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Dr [-]` | - | Relative density as a number between 0 and 1 ($D_r$) |

**References**

- Baldi et al 1986.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="relativedensity_ocsand_baldi"></a>

## `relativedensity_ocsand_baldi`

<span class="gc-badge gc-available" data-geocore-function="relativedensity_ocsand_baldi">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Baldi Relative Density (OC Sand)](/docs/geocore/using/modules#relativedensity_ocsand_baldi)

```python
relativedensity_ocsand_baldi(
    qc,
    sigma_vo_eff,
    k0,
    coefficient_0=181.0,
    coefficient_1=0.55,
    coefficient_2=2.61,
    **kwargs,
)
```

Calculates the relative density for overconsolidated sand based on calibration chamber tests on silica sand. It should be noted that this correlation provides an approximative estimate of relative density and the sand at the site should be compared to the sands used in the calibration chamber tests. The correlation will always be sensitive to variations in compressibility and horizontal stress. Note that this correlation requires an estimate of the coefficient of lateral earth pressure.

When used with `apply_correlation`, use `'Dr Baldi et al (1986) - OC sand'` as correlation name.

$$
D_r = \frac{1}{2.61} \cdot \ln \left[ \frac{q_c}{181 \cdot \left( \sigma_{m}^{\prime} \right)^{0.55} } \right]
$$

$$
\sigma_{m}^{\prime} = \frac{\sigma_{vo}^{\prime} + 2 \cdot K_o \ cdot \sigma_{h0}^{\prime}}{3}
$$

![Relationship between cone tip resistance, vertical effective stress and relative density for overconsolidated Ticino sand](/docs/assets/groundhog/docs/site_investigation/images/relativedensity_ocsand_baldi_1.png)

*Relationship between cone tip resistance, vertical effective stress and relative density for overconsolidated Ticino sand*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc` | MPa | 0.0 <= qc <= 120.0 | required | Cone tip resistance ($q_c$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `k0` | - | 0.3 <= k0 <= 5.0 | required | Coefficient of lateral earth pressure ($K_o$) |
| `coefficient_0` | - |  | `181.0` | Coefficient C0 ($C_0$) |
| `coefficient_1` | - |  | `0.55` | Coefficient C1 ($C_1$) |
| `coefficient_2` | - |  | `2.61` | Coefficient C2 ($C_2$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Dr [-]` | - | Relative density as a number between 0 and 1 ($D_r$) |

**References**

- Baldi et al 1986.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="coneresistance_ocsand_baldi"></a>

## `coneresistance_ocsand_baldi`

<span class="gc-badge gc-available" data-geocore-function="coneresistance_ocsand_baldi">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Baldi Cone Resistance (Overconsolidated Sand)](/docs/geocore/using/modules#coneresistance_ocsand_baldi)

```python
coneresistance_ocsand_baldi(
    dr,
    sigma_vo_eff,
    k0,
    coefficient_0=181.0,
    coefficient_1=0.55,
    coefficient_2=2.61,
    **kwargs,
)
```

Calculates the cone resistance for a given relative density for overconsolidated sand based on calibration chamber tests on silica sand. It should be noted that this correlation provides an approximative estimate of relative density and the sand at the site should be compared to the sands used in the calibration chamber tests. The correlation will always be sensitive to variations in compressibility and horizontal stress. Note that this correlation requires an estimate of the coefficient of lateral earth pressure.

$$
D_r = \frac{1}{2.61} \cdot \ln \left[ \frac{q_c}{181 \cdot \left( \sigma_{m}^{\prime} \right)^{0.55} } \right]
$$

$$
\sigma_{m}^{\prime} = \frac{\sigma_{vo}^{\prime} + 2 \cdot K_o \cdot \sigma_{m}^{\prime}}{3}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `dr` | - | 0.0 <= dr <= 1.0 | required | Relative density ($D_r$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `k0` | - | 0.3 <= k0 <= 5.0 | required | Coefficient of lateral earth pressure ($K_o$) |
| `coefficient_0` | - |  | `181.0` | Coefficient C0 ($C_0$) |
| `coefficient_1` | - |  | `0.55` | Coefficient C1 ($C_1$) |
| `coefficient_2` | - |  | `2.61` | Coefficient C2 ($C_2$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `qc [MPa]` | MPa | Cone resistance corresponding to the given relative density ($q_c$) |

**References**

- Baldi et al 1986.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="relativedensity_sand_jamiolkowski"></a>

## `relativedensity_sand_jamiolkowski`

<span class="gc-badge gc-available" data-geocore-function="relativedensity_sand_jamiolkowski">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Jamiolkowski Relative Density (Sand, CPT)](/docs/geocore/using/modules#relativedensity_sand_jamiolkowski)

```python
relativedensity_sand_jamiolkowski(
    qc,
    sigma_vo_eff,
    k0,
    atmospheric_pressure=100.0,
    coefficient_1=2.96,
    coefficient_2=24.94,
    coefficient_3=0.46,
    coefficient_4=-1.87,
    coefficient_5=2.32,
    **kwargs,
)
```

Jamiolkowksi et al formulated a correlation for the relative density of dry sand based on calibration chamber tests. The correlation can be modified for saturated sands by applying a correction factor and results in relative densities which can be up to 10% higher. Note that calibration chamber testing is carried out on sands with vertical effective stress between 50kPa and 400kPa and coefficients of lateral earth pressure Ko between 0.4 and 1.5. Relative densities for stress conditions outside this range (e.g. shallow soils) should be assessed with care.

When used with `apply_correlation`, use `'Dr Jamiolkowski et al (2003)'` as correlation name.

$$
D_{r,dry} = \frac{1}{2.96} \cdot \ln \left[ \frac{q_c / P_a}{24.94 \cdot \left( \frac{\sigma_{m}^{\prime}}{P_a} \right)^{0.46} } \right]
$$

$$
D_{r,sat} = \left( 1 + \frac{-1.87 + 2.32 \cdot \ln \left[ \frac{q_c}{\sqrt{P_a + \sigma_{vo}^{\prime}}} \right] }{100} \right) \cdot D_{r,dry}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc` | MPa | 0.0 <= qc <= 120.0 | required | Cone tip resistance ($q_c$) |
| `sigma_vo_eff` | kPa | 50.0 <= sigma_vo_eff <= 400.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `k0` | - | 0.4 <= k0 <= 1.5 | required | Coefficient of lateral earth pressure ($K_o$) |
| `atmospheric_pressure` | kPa |  | `100.0` | Atmospheric pressure used for normalisation ($P_a$) |
| `coefficient_1` | - |  | `2.96` | First calibration coefficient |
| `coefficient_2` | - |  | `24.94` | Second calibration coefficient |
| `coefficient_3` | - |  | `0.46` | Third calibration coefficient |
| `coefficient_4` | - |  | `-1.87` | Fourth calibration coefficient |
| `coefficient_5` | - |  | `2.32` | Fifth calibration coefficient |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Dr dry [-]` | - | Relative density for dry sand as a number between 0 and 1 ($D_{r,dry}$) |
| `Dr sat [-]` | - | Relative density for saturated sand as a number between 0 and 1 ($D_{r,sat}$) |

**References**

- Jamiolkowski, M., Lo Presti, D.C.F. and Manassero, M. (2003), "Evaluation of Relative Density and Shear Strength of Sands from CPT and DMT", in Germaine, J.T., Sheahan, T.C. and Whitman, R.V. (Eds.), Soil Behavior and Soft Ground Construction: Proceedings of the Symposium, October 5-6, 2001, Cambridge, Massachusetts, Geotechnical Special Publication, No. 119, American Society of Civil Engineers, Reston, pp. 201-238.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="frictionangle_sand_kulhawymayne"></a>

## `frictionangle_sand_kulhawymayne`

<span class="gc-badge gc-available" data-geocore-function="frictionangle_sand_kulhawymayne">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Kulhawy & Mayne Friction Angle (Sand, CPT)](/docs/geocore/using/modules#frictionangle_sand_kulhawymayne)

```python
frictionangle_sand_kulhawymayne(
    qt,
    sigma_vo_eff,
    atmospheric_pressure=100.0,
    coefficient_1=17.6,
    coefficient_2=11.0,
    **kwargs,
)
```

Determines the friction angle for sand based on calibration chamber tests.

When used with `apply_correlation`, use `'Friction angle Kulhawy and Mayne (1990)'` as correlation name.

$$
\varphi^{\prime} = 17.6 + 11.0 \cdot \log_{10} \left[  \frac{q_t / P_a}{ \sqrt{\sigma_{vo}^{\prime} / P_a}} \right]
$$

![Data and interpretation chart according to Kulhawy and Mayne 1990)](/docs/assets/groundhog/docs/site_investigation/images/kulhawy_mayne_data.png)

*Data and interpretation chart according to Kulhawy and Mayne 1990)*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qt` | MPa | 0.0 <= qt <= 120.0 | required | Total cone resistance ($q_t$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `atmospheric_pressure` | kPa |  | `100.0` | Atmospheric pressure used for normalisation ($P_a$) |
| `coefficient_1` | - |  | `17.6` | First calibration coefficient |
| `coefficient_2` | - |  | `11.0` | Second calibration coefficient |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Phi [deg]` | deg | Effective friction angle for sand ($\varphi$) |

**References**

- Kulhawy, F.H. and Mayne, P.H. (1990), “Manual on Estimating Soil Properties for Foundation Design”, Electric Power Research Institute EPRI, Palo Alto, EPRI Report, EL-6800.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="undrainedshearstrength_clay_radlunne"></a>

## `undrainedshearstrength_clay_radlunne`

<span class="gc-badge gc-available" data-geocore-function="undrainedshearstrength_clay_radlunne">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Rad & Lunne Undrained Shear Strength (Net qt)](/docs/geocore/using/modules#undrainedshearstrength_clay_radlunne)

```python
undrainedshearstrength_clay_radlunne(qnet, Nk, **kwargs)
```

Calculates the undrained shear strength of clay from net cone tip resistance. The correlation is empirical and the cone factor needs to be adjusted to fit CIU or other high-quality laboratory tests for undrained shear strength.

When used with `apply_correlation`, use `'Su Rad and Lunne (1988)'` as correlation name.

$$
S_u = \frac{q_{net}}{N_k}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qnet` | MPa | 0.0 <= qnet <= 120.0 | required | Net cone resistance (corrected for area ratio and total stress at the depth of the cone) ($q_{net}$) |
| `Nk` | - | 8.0 <= Nk <= 30.0 | required | Empirical factor ($N_k$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Su [kPa]` | kPa | Undrained shear strength inferred from PCPT data ($S_u$) |

**References**

- Rad, N.S. and Lunne, T. (1988), "Direct Correlations between Piezocone Test Results and Undrained Shear Strength of Clay", in De Ruiter, J. (Ed.), Penetration Testing 1988: Proceedings of the First International Symposium on Penetration Testing, ISOPT-1, Orlando, 20-24 March 1988, Vol. 2, A.A. Balkema, Rotterdam, pp. 911-917.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="frictionangle_overburden_kleven"></a>

## `frictionangle_overburden_kleven`

<span class="gc-badge gc-available" data-geocore-function="frictionangle_overburden_kleven">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Kleven (1986) Friction Angle Chart](/docs/geocore/using/modules#frictionangle_overburden_kleven)

```python
frictionangle_overburden_kleven(
    sigma_vo_eff,
    relative_density,
    Ko=0.5,
    max_friction_angle=45.0,
    **kwargs,
)
```

This function calculates the friction angle according to the chart proposed by Kleven (1986). The function takes into account the effective confining pressure of the sand and its relative density. The function was calibrated on North Sea sand tests with confining pressures ranging from 10 to 800kPa. Lower confinement clearly leads to higher friction angles. The fit to the data is not excellent and this function should be compared to site-specific testing or other correlations.

When used with `apply_correlation`, use `'Friction angle Kleven (1986)'` as correlation name.

![Data and interpretation chart according to Kleven (Lunne et al (1997))](/docs/assets/groundhog/docs/site_investigation/images/Phi_Kleven.png)

*Data and interpretation chart according to Kleven (Lunne et al (1997))*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `sigma_vo_eff` | kPa | 10.0<=sigma_vo_eff<=800.0 | required | Effective vertical stress ($\sigma \prime _{vo}$) |
| `relative_density` | Percent | 40.0<=relative_density<=100.0 | required | Relative density of sand ($D_r$) |
| `Ko` | - | 0.3<=Ko<=2.0 | `0.5` | Coefficient of lateral earth pressure at rest (optional, default=0.5) ($K_o$) |
| `max_friction_angle` | deg |  | `45.0` | The maximum allowable effective friction angle ($\phi \prime _{max}$) |

**Returns**

Peak drained friction angle ($\phi_d$) [$deg$], Mean effective stress ($\sigma \prime _m$) [$kPa$]

Return type: `Python dictionary with keys ['phi [deg]','sigma_m [kPa]']`

**Example**

```python
>>>phi = friction_angle_kleven(sigma_vo_eff=100.0,relative_density=60.0,Ko=1.0)['phi [deg]']
35.8
```

**References**

- Lunne, T., Robertson, P.K., Powell, J.J.M. (1997). Cone penetration testing in geotechnical practice.  SPON press

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="ocr_cpt_lunne"></a>

## `ocr_cpt_lunne`

<span class="gc-badge gc-available" data-geocore-function="ocr_cpt_lunne">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Lunne OCR (CPT, Clay)](/docs/geocore/using/modules#ocr_cpt_lunne)

```python
ocr_cpt_lunne(Qt, Bq=nan, **kwargs)
```

Calculates the overconsolidation ratio (OCR) for clay based on normalised CPT properties. A low estimate, best estimate and high estimate of OCR is provided. The data is based on testing of high-quality undisturbed samples by the Norwegian Geotechnical Institute.

Both normalised cone resistance Qt and pore pressure ratio Bq can be used as inputs. If only one of the two inputs is specified, NaN is returned for the other.

The implementation of the formulation is based on digitisation of the graphs.

When used with `apply_correlation`, use `'OCR Lunne (1989)'` as correlation name.

![Data used for correlations according to Lunne et al](/docs/assets/groundhog/docs/site_investigation/images/ocr_cpt_lunne.png)

*Data used for correlations according to Lunne et al*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `Qt` | - | 2.0 <= Qt <= 34.0 | required | Normalised cone resistance ($Q_t$) |
| `Bq` | - | 0.0 <= Bq <= 1.4 | `nan` | Pore pressure ratio ($B_q$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `OCR_Qt_LE [-]` | - | Low estimate OCR based on Qt ($OCR_{Q_t,LE}$) |
| `OCR_Qt_BE [-]` | - | Best estimate OCR based on Qt ($OCR_{Q_t,BE}$) |
| `OCR_Qt_HE [-]` | - | High estimate OCR based on Qt ($OCR_{Q_t,HE}$) |
| `OCR_Bq_LE [-]` | - | Low estimate OCR based on Bq ($OCR_{B_q,LE}$) |
| `OCR_Bq_BE [-]` | - | Best estimate OCR based on Bq ($OCR_{B_q,BE}$) |
| `OCR_Bq_HE [-]` | - | High estimate OCR based on Bq ($OCR_{B_q,HE}$) |

**References**

- Lunne, T., Robertson, P.K., Powell, J.J.M., 1997. Cone penetration testing in geotechnical practice. E & FN Spon.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="sensitivity_frictionratio_lunne"></a>

## `sensitivity_frictionratio_lunne`

<span class="gc-badge gc-available" data-geocore-function="sensitivity_frictionratio_lunne">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Rad & Lunne (1986) Sensitivity (Friction Ratio)](/docs/geocore/using/modules#sensitivity_frictionratio_lunne)

```python
sensitivity_frictionratio_lunne(Rf, **kwargs)
```

Calculates the sensitivity of clay from the friction ratio according to Rad and Lunne (1986). The correlation is derived based on measurements on Norwegian clays.

Ideally, the sleeve friction corrected for pore pressure effects should be used to calculate the friction ratio but if this is not available (when pore pressures are not measured on both ends of the friction sleeve), the ratio of sleeve friction to cone tip resistance (in percent) can be used.

The function returns a low estimate, best estimate and high estimate value.

When used with `apply_correlation`, use `'Sensitivity Rad and Lunne (1986)'` as correlation name.

![Data used to derive correlation according to Rad & Lunne (1986)](/docs/assets/groundhog/docs/site_investigation/images/sensitivity_frictionratio_lunne_1.png)

*Data used to derive correlation according to Rad & Lunne (1986)*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `Rf` | percent | 0.5 <= Rf <= 2.2 | required | Friction ratio ($R_f = f_t / q_t$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `St LE [-]` | - | Low estimate sensitivity ($S_{t,LE}$) |
| `St BE [-]` | - | Best estimate sensitivity ($S_{t,BE}$) |
| `St HE [-]` | - | High estimate sensitivity ($S_{t,HE}$) |

**References**

- Lunne, T., Robertson, P.K., Powell, J.J.M., 1997. Cone penetration testing in geotechnical practice. E & FN Spon.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="unitweight_mayne"></a>

## `unitweight_mayne`

<span class="gc-badge gc-available" data-geocore-function="unitweight_mayne">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Mayne Total Unit Weight (CPT)](/docs/geocore/using/modules#unitweight_mayne)

```python
unitweight_mayne(
    ft,
    sigma_vo_eff,
    unitweight_water=10.25,
    atmospheric_pressure=100.0,
    coefficient_1=1.95,
    exponent_1=0.06,
    exponent_2=0.06,
    **kwargs,
)
```

Estimates the total unit weight for sand, clay and silt from CPT measurements. A correlation with sleeve friction and vertical effective stress showed the best fit across a range of soil types. The correlation does not apply for cemented soils. An error band of +-2kN/m3 seems to encompass the data rather well.

For the sake of accuracy, the corrected total sleeve friction is used instead of the uncorrected sleeve friction. PCPT normalisation is required before applying the correlation. If sleeve dimensions are not available, the uncorrected sleeve friction will be used.

When used with `apply_correlation`, use `'Unit weight Mayne et al (2010)'` as correlation name.

$$
\gamma = 1.95 \cdot \gamma_w \cdot \left( \frac{\sigma_{vo}^{\prime}}{P_a} \right)^{0.06} \cdot \left( \frac{f_t}{P_a} \right)^{0.06}
$$

![Calibration with soil data used](/docs/assets/groundhog/docs/site_investigation/images/unitweight_mayne_1.png)

*Calibration with soil data used*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `ft` | MPa | 0.0 <= ft <= 10.0 | required | Total sleeve friction ($f_t$) |
| `sigma_vo_eff` | kPa | 0.0 <= sigma_vo_eff <= 500.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `unitweight_water` | kN/m3 | 9.0 <= unitweight_water <= 11.0 | `10.25` | Unit weight of water ($\gamma_w$) |
| `atmospheric_pressure` | kPa |  | `100.0` | Atmospheric pressure ($P_a$) |
| `coefficient_1` | - |  | `1.95` | First coefficient in the calibrated equation |
| `exponent_1` | - |  | `0.06` | First exponent in the calibrated equation |
| `exponent_2` | - |  | `0.06` | Second exponent in the calibrated equation |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `gamma [kN/m3]` | kN/m3 | Total unit weight ($\gamma$) |

**References**

- P.W. Mayne ; J. Peuchen ; D. Bouwmeester (2010). Soil unit weight estimation from CPTs - 2nd International Symposium on Cone Penetration Testing, Huntington Beach, CA, USA. Volume 2&3: Technical Papers, Session 2: Interpretation, Paper No. 5

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="vs_ic_robertsoncabal"></a>

## `vs_ic_robertsoncabal`

<span class="gc-badge gc-available" data-geocore-function="vs_ic_robertsoncabal">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Robertson & Cabal Shear Wave Velocity (Ic)](/docs/geocore/using/modules#vs_ic_robertsoncabal)

```python
vs_ic_robertsoncabal(
    qt,
    ic,
    sigma_vo,
    atmospheric_pressure=100.0,
    gamma=19,
    g=9.81,
    exponent=0.5,
    calibration_coefficient_1=0.55,
    calibration_coefficient_2=1.68,
    **kwargs,
)
```

Calculates shear wave velocity based on a correlation with total cone resistance and soil behaviour type index. Shear wave velocity is sensitive to age and cementation, where older deposits of the same soil have higher shear wave velocity (i.e. higher stiffness) than younger deposits. The correlation is based on measured shear wave velocity data for uncemented Holocene to Pleistocene age soils. Since the small-strain shear modulus can be derived from the shear wave velocity and the bulk density of the soil, is it also calculated. The bulk density of the soil can be specified as an optional argument.

Unfortunately, no plots on the background data to the calibrated equation are available.

When used with `apply_correlation`, use `'Shear wave velocity Robertson and Cabal (2015)'` as correlation name.

$$
V_s = \left[ \alpha_{vs} (q_t - \sigma_{vo}) / P_a \right]^{0.5}
$$

$$
\alpha_{vs} = 10^{0.55 \cdot I_c + 1.68}
$$

$$
G_{max} = \rho \cdot V_s^2
$$

$$
\rho = \gamma / g
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qt` | MPa | 0.0 <= qt <= 100.0 | required | Total cone resistance ($q_t$) |
| `ic` | - | 1.0 <= ic <= 4.0 | required | Soil behaviour type index according to Robertson and Wride ($I_c$) |
| `sigma_vo` | kPa | 0.0 <= sigma_vo <= 800.0 | required | Total vertical stress ($sigma_{vo}$) |
| `atmospheric_pressure` | kPa |  | `100.0` | Atmospheric pressure ($P_a$) |
| `gamma` | kN/m3 | 12.0 <= gamma <= 22.0 | `19` | Bulk unit weight ($\gamma$) |
| `g` | m/s2 | 9.7 <= g <= 10.2 | `9.81` | Acceleration due to gravity ($g$) |
| `exponent` | - |  | `0.5` | Exponent in equation for shear wave velocity |
| `calibration_coefficient_1` | - |  | `0.55` | First calibration coefficient in equation for alpha_s |
| `calibration_coefficient_2` | - |  | `1.68` | Second calibration coefficient in equation for alpha_s |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `alpha_vs [-]` | - | Coefficient to the shear wave velocity calculation, capturing the influence of the soil behaviour ($\alpha_{vs}$) |
| `Vs [m/s]` | m/s | Shear wave velocity ($V_s$) |
| `Gmax [kPa]` | kPa | Small-strain shear modulus ($G_{max}$) |

**References**

- Robertson, P.K. and Cabal, K.L. (2015). Guide to Cone Penetration Testing for Geotechnical Engineering. 6th edition. Gregg Drilling & Testing, Inc.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="k0_sand_mayne"></a>

## `k0_sand_mayne`

<span class="gc-badge gc-available" data-geocore-function="k0_sand_mayne">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Mayne K0 (Clean Sand, CPT)](/docs/geocore/using/modules#k0_sand_mayne)

```python
k0_sand_mayne(
    qt,
    sigma_vo_eff,
    ocr,
    atmospheric_pressure=100.0,
    multiplier=0.192,
    exponent_1=0.22,
    exponent_2=0.31,
    exponent_3=0.27,
    friction_angle=32.0,
    **kwargs,
)
```

Calculates the lateral coefficient of earth pressure at rest based on calibration chamber tests on clean sands. The values calculated from the equation need to be compared to values obtained using friction angle and OCR (see equations).

When used with `apply_correlation`, use `'K0 Mayne (2007) - sand'` as correlation name.

$$
K_0 = 0.192 \cdot \left( \frac{q_t}{P_a} \right)^{0.22} \cdot \left( \frac{P_a}{\sigma_{vo}^{\prime}} \right)^{0.31} \cdot \text{OCR}^{0.27}
$$

$$
\text{The maximum value for } K_0 \text{ can be obtained as}:
$$

$$
K_p = \tan^2 \left( \frac{\pi}{4} + \frac{\varphi^{\prime}}{2} \right) = \frac{1 + \sin \varphi^{\prime}}{1 - \sin \varphi^{\prime}}
$$

$$
\text{These values need to be compared to}:
$$

$$
K_0 = (1 - \sin \varphi^{\prime}) \cdot \text{OCR} ^{\sin \varphi^{\prime}}
$$

![Dataset used for calibration](/docs/assets/groundhog/docs/site_investigation/images/k0_sand_mayne_1.png)

*Dataset used for calibration*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qt` | MPa | 0.0 <= qt <= 100.0 | required | Total cone resistance ($q_t$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `ocr` | - | 1.0 <= ocr <= 20.0 | required | Overconsolidation ratio ($OCR$) |
| `atmospheric_pressure` | kPa | 90.0 <= atmospheric_pressure <= 110.0 | `100.0` | Atmospheric pressure ($P_a$) |
| `multiplier` | - |  | `0.192` | Multiplier in equation |
| `exponent_1` | - |  | `0.22` | First exponent in equation |
| `exponent_2` | - |  | `0.31` | Second exponent in equation |
| `exponent_3` | - |  | `0.27` | Third exponent in equation |
| `friction_angle` | deg | 25.0 <= friction_angle <= 45.0 | `32.0` | Effective friction angle of the sand ($\varphi^{\prime}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `K0 CPT [-]` | - | Coefficient of lateral earth pressure at rest derived from CPT ($K_{0,CPT}$) |
| `K0 conventional [-]` | - | Value derived from the conventional equation ($K_{0,\text{conventional}}$) |
| `Kp [-]` | - | Limiting value of coefficient of lateral earth pressure based on Rankine passive earth pressure ($K_p$) |

**References**

- Mayne (2007) NCHRP SYNTHESIS 368. Cone Penetration Testing. A Synthesis of Highway Practice.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="gmax_cpt_puechen"></a>

## `gmax_cpt_puechen`

<span class="gc-badge gc-available" data-geocore-function="gmax_cpt_puechen">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Puechen Gmax (CPT)](/docs/geocore/using/modules#gmax_cpt_puechen)

```python
gmax_cpt_puechen(
    qc,
    sigma_vo_eff,
    Bq,
    coefficient_b=1.0,
    coefficient_Bq=4.0,
    multiplier_qc=1.634,
    exponent_1=0.25,
    exponent_2=0.375,
    Bq_min=0,
    Bq_max=0.5,
    **kwargs,
)
```

Calculates the small-strain modulus based on CPT data. The correlation by Rix and Stokoe is modified to include the importance of the pore pressure ratio.

The calibration coefficient b has recommended values between 0.5 and 2, with a suggested best estimate of 1.

When used with `apply_correlation`, use `'Gmax Puechen (2020)'` as correlation name.

$$
G_{max} = b \cdot \left( 1 + 4 \cdot B_q \right) \cdot 1.634 \cdot q_c^{0.25} \cdot \sigma_{vo}^{\prime \ 0.375}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc` | MPa | 0.0 <= qc <= 70.0 | required | Cone tip resistance ($q_c$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `Bq` | - | -0.2 <= Bq <= 0.5 | required | Pore pressure ratio ($B_q$) |
| `coefficient_b` | - |  | `1.0` | Calibration coefficient b ($b$) |
| `coefficient_Bq` | - |  | `4.0` | Multiplier on Bq |
| `multiplier_qc` | - |  | `1.634` | Multiplier applied on qc |
| `exponent_1` | - |  | `0.25` | Exponent on qc |
| `exponent_2` | - |  | `0.375` | Exponent on vertical effective stress |
| `Bq_min` | - |  | `0` | Minimum value of Bq. If Bq is lower than this value, the minimum will be used for the calculation |
| `Bq_max` | - |  | `0.5` | Maximum value of Bq. If Bq is higher than this value, the maximum will be used for the calculation |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Gmax [kPa]` | kPa | Small-strain shear modulus ($G_{max}$) |

**References**

- Puechen et al (2020). Characteristic values for geotechnical design of offshore monopiles in sandy soils - Case study. ISFOG2020

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="behaviourindex_pcpt_nonnormalised"></a>

## `behaviourindex_pcpt_nonnormalised`

<span class="gc-badge gc-available" data-geocore-function="behaviourindex_pcpt_nonnormalised">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Non-Normalised Soil Behaviour Index](/docs/geocore/using/modules#behaviourindex_pcpt_nonnormalised)

```python
behaviourindex_pcpt_nonnormalised(qc, Rf, atmospheric_pressure=100.0, **kwargs)
```

Calculates the non-normalised soil behaviour type index. For vertical effective stresses between 50 and 150kPa, the non-normalised index is almost equal to the normalised soil behaviour type index.

When used with `apply_correlation`, use `'Isbt Robertson (2010)'` as correlation name.

$$
I_{SBT} = \sqrt{ \left( 3.47 - \log ( q_c / P_a ) \right)^2 + \left( \log R_f + 1.22 \right)^2}
$$

![Contours of non-normalised soil behaviour type index](/docs/assets/groundhog/docs/site_investigation/images/behaviourindex_pcpt_nonnormalised_1.png)

*Contours of non-normalised soil behaviour type index*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc` | MPa | 0.0 <= qc <= 100.0 | required | Cone tip resistance ($q_c$) |
| `Rf` | pct | 0.1 <= Rf <= 10.0 | required | Friction rato ($R_f$) |
| `atmospheric_pressure` | kPa | 90.0 <= atmospheric_pressure <= 110.0 | `100.0` | Atmospheric pressure ($P_a$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Isbt [-]` | - | Non-normalised soil behaviour type index ($I_{SBT}$) |

**References**

- Fugro guidance on PCPT interpretation

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="drainedsecantmodulus_sand_bellotti"></a>

## `drainedsecantmodulus_sand_bellotti`

<span class="gc-badge gc-available" data-geocore-function="drainedsecantmodulus_sand_bellotti">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Bellotti Drained Secant Modulus (Sand)](/docs/geocore/using/modules#drainedsecantmodulus_sand_bellotti)

```python
drainedsecantmodulus_sand_bellotti(
    qc,
    sigma_vo_eff,
    K0,
    sandtype,
    atmospheric_pressure=100.0,
    **kwargs,
)
```

Calculates the drained secant modulus for various types of sand for an average strain of 0.1 percent. This stress range should be representative for well-designed foundations (with sufficient safety against excessive deformations).

Bands for mean effective stress from 50kPa to 300kPa are provided. Note that the correlation will not return values outside that range.

Ageing and overconsolidation are beneficial effects, leading to increased stiffness.

When used with `apply_correlation`, use `'Es Bellotti (1989) - sand'` as correlation name.

$$
q_{c1} = \left( \frac{q_c}{P_a} \right) \cdot \sqrt{ \frac{P_a}{\sigma_{vo}^{\prime}} }
$$

$$
\sigma_{mo}^{\prime} = \frac{(1 + 2 \cdot K_0) \cdot \sigma_{vo}^{\prime}}{3}
$$

![Visualisation of correlation](/docs/assets/groundhog/docs/site_investigation/images/drainedsecantmodulus_sand__1.png)

*Visualisation of correlation*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc` | MPa | 0.0 <= qc <= 100.0 | required | Cone tip resistance ($q_c$) |
| `sigma_vo_eff` | kPa | 50.0 <= sigma_vo_eff <= 300.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `K0` | - | 0.5 <= K0 <= 2.0 | required | Coefficient of lateral earth pressure at rest ($K_0$) |
| `sandtype` |  | one of `NC`, `Aged NC`, `OC` | required | Type of sand - Options: ("NC", "Aged NC", "OC") |
| `atmospheric_pressure` | kPa | 90.0 <= atmospheric_pressure <= 110.0 | `100.0` | Atmospheric pressure ($P_a$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `qc1 [-]` | - | Normalised cone resistance ($q_{c1}$) |
| `Es_qc [-]` | - | Ratio of drained secant modulus to cone resistance ($E_s^{\prime} / q_c$) |
| `Es [kPa]` | kPa | Drained secant modulus at strain level of 0.1 percent ($E_s^{\prime}$) |

**References**

- Bellotti, R., Ghionna, V. N., Jamiolkowski, M., Lancellotta, R., & Robertson, P. K. (1989). Shear strength of sand from CPT. In Congrès international de mécanique des sols et des travaux de fondations. 12 (pp. 179-184).

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="gmax_voidratio_maynerix"></a>

## `gmax_voidratio_maynerix`

<span class="gc-badge gc-available" data-geocore-function="gmax_voidratio_maynerix">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Mayne & Rix Gmax (from Void Ratio)](/docs/geocore/using/modules#gmax_voidratio_maynerix)

```python
gmax_voidratio_maynerix(
    qc,
    void_ratio,
    atmospheric_pressure=100.0,
    coefficient_1=99.5,
    coefficient_2=0.305,
    coefficient_3=0.695,
    coefficient_4=1.13,
    **kwargs,
)
```

Calculates the small-strain shear modulus for clay based on the void ratio of the material. The relation between Gmax and qc presented in the CPT book (`gmax_clay_maynerix` function) shows an inferior fit (r2 = 0.713) to the clay data than the correlation which is finally proposed by the authors (r2 = 0.901). This correlation also takes the void ratio of the material into account.

The correlation is developed based on a database of in-situ testing for Gmax at 31 sites with seismic cone, SASW, cross-hole and downhole tests. The main difficulty in applying this correlation is the requirement for companion profiles of void ratio. Void ratio can be estimated using a CPT correlation for unit weight (`unitweight_mayne`) but this correlation has a rather high uncertainty associated with it.

When used with `apply_correlation`, use `'Gmax void ratio Mayne and Rix (1993)'` as correlation name.

$$
G_{max} = 99.5 \cdot (P_a)^{0.305} \cdot \frac{q_c^{0.695}}{e_0^{1.130}}
$$

![Comparison of measured vs predicted Gmax](/docs/assets/groundhog/docs/site_investigation/images/gmax_voidratio_maynerix_1.png)

*Comparison of measured vs predicted Gmax*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc` | MPa | 0.1 <= qc <= 10.0 | required | Cone tip resistance ($q_c$) |
| `void_ratio` | - | 0.2 <= void_ratio <= 10.0 | required | Void ratio of the clay determined from index tests or CPT-based correlations ($e_0$) |
| `atmospheric_pressure` | kPa | 90.0 <= atmospheric_pressure <= 110.0 | `100.0` | Atmospheric pressure ($P_a$) |
| `coefficient_1` | - |  | `99.5` | First calibration coefficient |
| `coefficient_2` | - |  | `0.305` | Second calibration coefficient |
| `coefficient_3` | - |  | `0.695` | Third calibration coefficient |
| `coefficient_4` | - |  | `1.13` | Fourth calibration coefficient |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Gmax [kPa]` | kPa | Small-strain shear modulus ($G_{max}$) |

**References**

- Mayne, P.W. and Rix, G.J. (1993), “Gmax-qc Relationships for Clays”, Geotechnical Testing Journal, Vol. 16, No. 1, pp. 54-60.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="vs_cpt_andrus"></a>

## `vs_cpt_andrus`

<span class="gc-badge gc-available" data-geocore-function="vs_cpt_andrus">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Andrus Shear Wave Velocity (CPT)](/docs/geocore/using/modules#vs_cpt_andrus)

```python
vs_cpt_andrus(
    qt,
    depth,
    ic,
    SF=1.0,
    age='Holocene',
    holocene_multiplier=2.27,
    holocene_qt_exponent=0.412,
    holocene_ic_exponent=0.989,
    holocene_z_exponent=0.033,
    pleistocene_multiplier=2.62,
    pleistocene_qt_exponent=0.395,
    pleistocene_ic_exponent=0.912,
    pleistocene_z_exponent=0.124,
    tertiary_multiplier=13.0,
    tertiary_qt_exponent=0.382,
    tertiary_z_exponent=0.099,
    **kwargs,
)
```

Calculates shear wave velocity from CPT measurements based on a relation calibrated on 229 measurements of which the majority are S-PCPT with some cross-hole tests and suspension logger measurements.

Correlations for Holocene/Pleistocene soils and Tertiary soils are developed separately but it should be noted that the only Tertiary soil used for calibration is a marl which has different mineralogy from silica soils.

When used with `apply_correlation`, use `'Vs CPT Andrus (2007)'` as correlation name.

$$
\text{Holocene}
$$

$$
V_s = 2.27 \cdot q_t^{0.412} \cdot I_c^{0.989} \cdot z^{0.033} \cdot ASF
$$

$$
\text{Pleistocene}
$$

$$
V_s = 2.62 \cdot q_t^{0.395} \cdot I_c^{0.912} \cdot z^{0.124} \cdot SF
$$

$$
\text{Tertiary}
$$

$$
V_s = 13 \cdot q_t^{0.382} \cdot z^{0.099}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qt` | MPa | 0.0 <= qt <= 100.0 | required | Corrected cone tip resistance (note that formula is based on qt in kPa) ($q_t$) |
| `depth` | m | 0.0 <= depth <= 100.0 | required | Depth below mudline ($z$) |
| `ic` | - | 1.0 <= ic <= 5.0 | required | Soil behaviour type index ($I_c$) |
| `SF` | - | 1.0 <= SF <= 3.0 | `1.0` | Scaling factor. In case of Holocene soils, this is an age scaling factor ($SF, ASF$) |
| `age` |  | one of `Holocene`, `Pleistocene`, `Tertiary` | `'Holocene'` | Age of soils |
| `holocene_multiplier` | - |  | `2.27` | Multiplier on holocene equation |
| `holocene_qt_exponent` | - |  | `0.412` | Exponent on qt in holocene equation |
| `holocene_ic_exponent` | - |  | `0.989` | Exponent on Ic in holocene equation |
| `holocene_z_exponent` | - |  | `0.033` | Exponent on depth in holocene equation |
| `pleistocene_multiplier` | - |  | `2.62` | Multiplier on pleistocene equation |
| `pleistocene_qt_exponent` | - |  | `0.395` | Exponent on qt in pleistocene equation |
| `pleistocene_ic_exponent` | - |  | `0.912` | Exponent on Ic in pleistocene equation |
| `pleistocene_z_exponent` | - |  | `0.124` | Exponent on depth in pleistocene equation |
| `tertiary_multiplier` | - |  | `13.0` | Multiplier on tertiary equation |
| `tertiary_qt_exponent` | - |  | `0.382` | Exponent on qt in tertiary equation |
| `tertiary_z_exponent` | - |  | `0.099` | Exponent on depth in tertiary equation |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Vs [m/s]` | m/s | Shear wave velocity ($V_s$) |

**References**

- Andrus, R.D., Mohanan, N.P., Piratheepan, P., Ellis, B.S., Holzer, T.L., 2007. Predicting Shear-wave velocity from cone penetration resistance, in: Paper No. 1454. Presented at the 4th International Conference on Earthquake Geotechnical Engineering, Thessaloniki, Greece.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="vs_cpt_hegazymayne"></a>

## `vs_cpt_hegazymayne`

<span class="gc-badge gc-available" data-geocore-function="vs_cpt_hegazymayne">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Hegazy & Mayne Shear Wave Velocity (CPT)](/docs/geocore/using/modules#vs_cpt_hegazymayne)

```python
vs_cpt_hegazymayne(
    qt,
    fs,
    sigma_vo_eff,
    sigma_vo,
    atmospheric_pressure=100.0,
    zhang=True,
    multiplier=0.0831,
    exponent_stress=0.25,
    multiplier_ic=1.786,
    **kwargs,
)
```

The correlation between shear wave velocity and CPT properties developed by Hegazy and Mayne was based on a global databased from 73 sites with different soil conditions including sands, clays, soil mixtures and mine tailings. The correlation includes the 30 clay sites used for the Mayne and Rix (1993) correlation as well as 30 cohesive and cohesionless sites from Hegazy and Mayne (1995). 12 new sites were added in the 2006 paper. A total of 558 data points are included in the database. A coefficient of determiniaton (r2) of 0.85 is obtained using all data.

Shear wave velocity was measured using S-PCPT, downhole testing, cross-hole testing and SASW. No comment is made on the measurement uncertainty and the obtained values are used as such.

The correlation shows a good fit of the ratio of corrected Vs to normalised cone tip resistance. Note that the normalised cone tip resistance is calculated by default using the Zhang exponent (`zhang=True`). The suggested formulation in the original paper by Hegazy and Mayne is included by setting the boolean zhang to False.

Note that all stresses in the equation are given in kPa.

When used with `apply_correlation`, use `'Vs CPT Hegazy and Mayne (2006)'` as correlation name.

$$
Q_{t,N} = \frac{q_t - \sigma_{vo}}{\sigma_{vo}^{\prime}}
$$

$$
I_c = \left[ (3.47 - \log Q_{t,N} )^2 + ( \log F_r + 1.22 )^2 \right]^{0.5}
$$

$$
\text{if } I_c \leq 2.6
$$

$$
q_{c1N} = \left( \frac{q_t}{P_a} \right) \cdot \left( \frac{P_a}{\sigma_{vo}^{\prime}} \right)^{0.5}
$$

$$
\text{if } I_c > 2.6
$$

$$
q_{c1N} = \left( \frac{q_t}{P_a} \right) \cdot \left( \frac{P_a}{\sigma_{vo}^{\prime}} \right)^{0.75}
$$

$$
V_s = 0.0831 \cdot q_{c1N} \cdot \left( \frac{\sigma_{vo}^{\prime}}{P_a} \right)^{0.25} \cdot e^{1.786 \cdot I_c}
$$

![Comparison between proposed trend and data](/docs/assets/groundhog/docs/site_investigation/images/vs_cpt_hegazy_1.png)

*Comparison between proposed trend and data*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qt` | MPa | 0.0 <= qt <= 100.0 | required | Corrected cone tip resistance ($q_t$) |
| `fs` | MPa | 0.0 <= fs <= 10.0 | required | Sleeve friction ($f_s$) |
| `sigma_vo_eff` | kPa | 0.0 <= sigma_vo_eff <= 1000.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `sigma_vo` | kPa | 0.0 <= sigma_vo <= 2000.0 | required | Vertical total stress ($\sigma_{vo}$) |
| `atmospheric_pressure` | kPa |  | `100.0` | Atmospheric pressure ($P_a$) |
| `zhang` |  |  | `True` | Boolean determining whether the Zhang exponent (default groundhog implementation) needs to be used |
| `multiplier` | - |  | `0.0831` | Multiplier in Equation 6 |
| `exponent_stress` | - |  | `0.25` | Exponent on the normalised stresses |
| `multiplier_ic` | - |  | `1.786` | Multiplier on soil behaviour type index |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Ic uncorrected [-]` | - | Soil behaviour type index according to equation 2a ($I_{c,uncorrected}$) |
| `qc1N [-]` | - | Corrected normalised cone tip resistance based on Ic criterion ($q_{c1N}$) |
| `Ic [-]` | - | Corrected soil behaviour type index as used in Equation 6 from the paper ($I_c$) |
| `Vs [m/s]` | m/s | Shear wave velocity ($V_s$) |

**References**

- Hegazy and Mayne (2006). A Global Statistical Correlation between Shear Wave Velocity and Cone Penetration Data.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="vs_cpt_longdonohue"></a>

## `vs_cpt_longdonohue`

<span class="gc-badge gc-available" data-geocore-function="vs_cpt_longdonohue">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Long & Donohue Shear Wave Velocity (CPT)](/docs/geocore/using/modules#vs_cpt_longdonohue)

```python
vs_cpt_longdonohue(
    qt,
    u2,
    u0,
    Bq,
    sigma_vo_eff,
    atmospheric_pressure=100.0,
    multiplier=1.961,
    exponent_qt=0.579,
    exponent_Bq=1.202,
    **kwargs,
)
```

The authors propose a correlation between shear wave velocity and CPT properties based on high-quality CPT tests and Gmax obtained from S-PCPT, MASW, cross-hole and block sampling. The formula for Vs only applies to soft marine clays.

The overconsolidation ratio of the material can be differentiated by plotting the normalised excess pore pressure vs the normalised shear wave velocity.

Note that stresses have units of kPa in the formula.

When used with `apply_correlation`, use `'Vs CPT Long and Donohue (2010)'` as correlation name.

$$
V_s = 1.961 \cdot q_t^{0.579} \cdot \left( 1 + B_q \right)^{1.202}
$$

![Differentiation of OCR based on shear wave velocity](/docs/assets/groundhog/docs/site_investigation/images/vs_cpt_longdonohue_1.png)

*Differentiation of OCR based on shear wave velocity*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qt` | MPa | 0.0 <= qt <= 2.0 | required | Corrected cone resistance ($q_t$) |
| `u2` | MPa | -1.0 <= u2 <= 1.0 | required | Pore pressure at the shoulder ($u_2$) |
| `u0` | kPa | 0.0 <= u0 <= 1000.0 | required | Hydrostatic pressure ($u_0$) |
| `Bq` | - | -0.6 <= Bq <= 1.4 | required | Pore pressure ratio ($B_q$) |
| `sigma_vo_eff` | kPa | 0.0 <= sigma_vo_eff <= 1000.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `atmospheric_pressure` | kPa |  | `100.0` | Atmospheric pressure ($P_a$) |
| `multiplier` | - |  | `1.961` | Multiplier in expression for Vs |
| `exponent_qt` | - |  | `0.579` | Exponent on qt |
| `exponent_Bq` | - |  | `1.202` | Exponent on 1 + Bq |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Vs [m/s]` | m/s | Shear wave velocity according to Equation 15 from paper ($V_s$) |
| `Vs1 [m/s]` | m/s | Normalised shear wave velocity ($V_{s,1}$) |
| `ocr_class` |  | OCR class based on Figure 9 from the paper |

**References**

- Long, M. and Donohue, S. (2010). Characterisation of Norwegian marine clays with combined shear wave velocity and CPTU data. Canadian Geotechnical Journal.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="soiltype_vs_longodonohue"></a>

## `soiltype_vs_longodonohue`

<span class="gc-badge gc-available" data-geocore-function="soiltype_vs_longodonohue">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Long & Donohue Soil Type (Vs, CPT)](/docs/geocore/using/modules#soiltype_vs_longodonohue)

```python
soiltype_vs_longodonohue(Vs, Qt, sigma_vo_eff, atmospheric_pressure=100.0, **kwargs)
```

Determines the soil type based on measured shear wave velocity and normalised cone resistance. The underlying dataset consists of soft clays (Long and Donohue, 2010), sands (Mayne, 2006) and stiff clays (Lunne et al, 2007).

The chart of Qt vs Vs1 allows determination of the soil type.

When used with `apply_correlation`, use `'Soiltype Vs Long and Donohue (2010)'` as correlation name.

$$
V_{s,1} = \frac{V_s}{\left( \frac{\sigma_{vo}^{\prime}}{P_a} \right)^{0.5}}
$$

![Comparison between soil types](/docs/assets/groundhog/docs/site_investigation/images/soiltype_vs_longodonohue_1.png)

*Comparison between soil types*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `Vs` | m/s | 0.0 <= Vs <= 600.0 | required | Shear wave velocity ($V_s$) |
| `Qt` | - | 0.0 <= Qt <= 200.0 | required | Normalised cone resistance ($Q_t$) |
| `sigma_vo_eff` | kPa | 0.0 <= sigma_vo_eff <= 1000.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `atmospheric_pressure` | kPa |  | `100.0` | Atmospheric pressure ($P_a$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Vs1 [m/s]` | m/s | Normalised shear wave velocity ($V_{s1}$) |
| `soiltype` |  | Soil type class based on Figure 10 from the paper |

**References**

- Long and Donohue (2010). Characterisation of Norwegian marine clays with combined shear wave velocity and CPTU data.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="vs_cptd50_karrayetal"></a>

## `vs_cptd50_karrayetal`

<span class="gc-badge gc-available" data-geocore-function="vs_cptd50_karrayetal">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Karray et al. Shear Wave Velocity (CPT, D50)](/docs/geocore/using/modules#vs_cptd50_karrayetal)

```python
vs_cptd50_karrayetal(
    qc,
    sigma_vo_eff,
    d50,
    atmospheric_pressure=100.0,
    exponent_vs1=0.25,
    multiplier=125.5,
    exponent_qc1=0.25,
    exponent_d50=0.115,
    **kwargs,
)
```

This correlation between Vs and normalised cone tip resistance takes into account the influence of median grain size. The data was obtained from the Peribonka site where vibrocompaction was performed for soil improvement. Tests before and after compaction were performed. The shear wave velocity was derived from surface wave testing. The soil type at the Peribonka site was gravelly coarse sand with an average median grain size of 1.9mm.

The correlation applies to uncemented holocene granular soils.

When used with `apply_correlation`, use `'Vs CPT d50 Karray et al (2011)'` as correlation name.

$$
q_{c1} = q_c \cdot \left( \frac{P_a}{\sigma_{vo}^{\prime}} \right)^{0.5}
$$

$$
V_{s1} = V_s \cdot \left( \frac{P_a}{\sigma_{vo}^{\prime}} \right)^{0.25}
$$

$$
V_{s1} = 125.5 \cdot \left( q_{c1} \right)^{0.25} \cdot d_{50}^{0.115}
$$

![Comparison between proposed trend and measured data](/docs/assets/groundhog/docs/site_investigation/images/vs_cptd50_karrayetal_1.png)

*Comparison between proposed trend and measured data*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc` | MPa | 0.0 <= qc <= 100.0 | required | Cone tip resistance ($q_c$) |
| `sigma_vo_eff` | kPa | 0.0 <= sigma_vo_eff <= 1000.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `d50` | mm | 0.1 <= d50 <= 10.0 | required | Median grain size ($d_{50}$) |
| `atmospheric_pressure` | kPa |  | `100.0` | Atmospheric pressure ($P_a$) |
| `exponent_vs1` | - |  | `0.25` | Exponent on stresses in Vs1 formula |
| `multiplier` | - |  | `125.5` | Multiplier in Equation 15 |
| `exponent_qc1` | - |  | `0.25` | Exponent on qc1 in Equation 15 |
| `exponent_d50` | - |  | `0.115` | Exponent on median grain size in Equation 15 |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `qc1 [MPa]` | MPa | Cone tip resistance corrected for stress level ($q_{c1}$) |
| `Vs1 [m/s]` | m/s | Shear wave velocity corrected for stress level ($V_{s1}$) |
| `Vs [m/s]` | m/s | Shear wave velocity ($V_s$) |

**References**

- Karray, M., Lefebvre, G., Ethier, Y., Bigras, A. (2011). Influence of particle size on the correlation between shear wave velocity and cone tip resistance. Canadian Geotechnical Journal.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="vs_cpt_wrideetal"></a>

## `vs_cpt_wrideetal`

<span class="gc-badge gc-available" data-geocore-function="vs_cpt_wrideetal">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Wride et al. Shear Wave Velocity (CPT)](/docs/geocore/using/modules#vs_cpt_wrideetal)

```python
vs_cpt_wrideetal(
    qc,
    sigma_vo_eff,
    atmospheric_pressure=100.0,
    multiplier=103.2,
    exponent_qc1=0.25,
    **kwargs,
)
```

Calculates shear wave velocity based on normalised cone tip resistance based on test data from the CANLEX project.

The Canadian Liquefaction Experiment (CANLEX) consists of in-situ testing at six sandy sites. The sand was fine sand with median grain size ranging from 0.16 to 0.25mm. The shear wave velocity measurements were recorded predominantely from downhole testing.

A general formula was established relating stress-corrected values of the cone tip resistance and shear wave velocity. The average value of the multiplier Y proposed by Karray et al (2011) was used as a default.

The authors do not present a chart comparing the calculated shear wave velocities to the measured ones, making it impossible to make statements on the accuracy of the correlation.

When used with `apply_correlation`, use `'Vs CPT Wride et al (2000)'` as correlation name.

$$
q_{c1} = q_c \cdot \left( \frac{P_a}{\sigma_{vo}^{\prime}} \right)^{0.5}
$$

$$
V_{s1} = V_s \cdot \left( \frac{P_a}{\sigma_{vo}^{\prime}} \right)^{0.25}
$$

$$
V_{s1} = Y \cdot q_{c1}^{0.25}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc` | MPa | 0.0 <= qc <= 100.0 | required | Cone tip resistance ($q_c$) |
| `sigma_vo_eff` | kPa | 0.0 <= sigma_vo_eff <= 1000.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `atmospheric_pressure` | kPa |  | `100.0` | Atmospheric pressure ($P_a$) |
| `multiplier` | - | 95.6 <= multiplier <= 110.8 | `103.2` | Multiplier on corrected cone resistance ($Y$) |
| `exponent_qc1` | - | 0.23 <= exponent_qc1 <= 0.25 | `0.25` | Exponent on stress-corrected cone resistance |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `qc1 [MPa]` | MPa | Stress-corrected cone tip resistance ($q_{c1}$) |
| `Vs1 [m/s]` | m/s | Stress-corrected shear wave velocity ($V_{s1}$) |
| `Vs [m/s]` | m/s | Shear wave velocity ($V_s$) |

**References**

- C.E. (Fear) Wride, P.K. Robertson, K.W. Biggar, R.G. Campanella, B.A. Hofmann, J.M.O. Hughes, A. Küpper, and D.J. Woeller (2000). Interpretation of in situ test results from the CANLEX sites. Canadian Geotechnical Journal.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="vs_cpt_tonniandsimonini"></a>

## `vs_cpt_tonniandsimonini`

<span class="gc-badge gc-available" data-geocore-function="vs_cpt_tonniandsimonini">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Tonni & Simonini Shear Wave Velocity (CPT)](/docs/geocore/using/modules#vs_cpt_tonniandsimonini)

```python
vs_cpt_tonniandsimonini(
    qt,
    ic,
    sigma_vo,
    sigma_vo_eff,
    atmospheric_pressure=100.0,
    coefficient_1=0.8,
    coefficient_2=1.17,
    **kwargs,
)
```

The authors propose a correlation between CPT properties and shear wave velocity for the Treporti site near Venice, Italy which consist mostly of silty sediments.

CPT and dilatometer (DMT) tests were conducted as well as seismic CPT and DMT tests at the site of a test embankment. Testing was conducted before and after placement of the embankment.

The authors highlight the importance of using the soil behaviour type index for obtaining a correlation which performs well across the different soil types encountered at the site. The authors finally propose different forms of the general equation proposed by Robertson and Cabal but accounting for stress correction.

The authors observe that stress corrections improve the accuracy of the correlations.

When used with `apply_correlation`, use `'Vs CPT Tonni and Simonini (2013)'` as correlation name.

$$
V_{s1} = 10^{ \left( 0.80 \cdot I_c - 1.17 \right) } \cdot Q_{tn}
$$

$$
V_{s1} = V_s \cdot \left( \frac{P_a}{\sigma_{vo}^{\prime}} \right)^{0.25}
$$

$$
Q_{tn} = \frac{q_t - \sigma_{vo}}{P_a}
$$

![Comparison between predicted and measured shear wave velocity](/docs/assets/groundhog/docs/site_investigation/images/vs_cpt_tonniandsimonini_1.png)

*Comparison between predicted and measured shear wave velocity*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qt` | MPa | 0.0 <= qt <= 100.0 | required | Corrected cone tip resistance ($q_t$) |
| `ic` | - | 1.0 <= ic <= 5.0 | required | Soil behaviour type index ($I_c$) |
| `sigma_vo` | kPa | 0.0 <= sigma_vo <= 2000.0 | required | Total vertical stress ($\sigma_{vo}$) |
| `sigma_vo_eff` | kPa | 0.0 <= sigma_vo_eff <= 1000.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `atmospheric_pressure` | kPa |  | `100.0` | Atmospheric pressure ($P_a$) |
| `coefficient_1` | - |  | `0.8` | Multiplier on Ic in Equation 12 |
| `coefficient_2` | - |  | `1.17` | Value after minus sign in Equation 12 |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Qtn [-]` | - | Normalised cone resistance ($Q_{tn}$) |
| `Vs1 [m/s]` | m/s | Stress-corrected shear wave velocity ($V_{s1}$) |
| `Vs [m/s]` | m/s | Shear wave velocity ($V_s$) |

**References**

- Tonni, L., Simonini, P. (2013). Shear wave velocity as function of cone penetration test measurements in sand and silt mixtures. Engineering Geology.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="vs_cpt_mcgannetal"></a>

## `vs_cpt_mcgannetal`

<span class="gc-badge gc-available" data-geocore-function="vs_cpt_mcgannetal">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › McGann et al. Shear Wave Velocity (CPT)](/docs/geocore/using/modules#vs_cpt_mcgannetal)

```python
vs_cpt_mcgannetal(
    qt,
    fs,
    depth,
    coefficient1_general=18.4,
    coefficient2_general=0.144,
    coefficient3_general=0.083,
    coefficient4_general=0.278,
    coefficient1_loess=103.6,
    coefficient2_loess=0.0074,
    coefficient3_loess=0.13,
    coefficient4_loess=0.253,
    loess=False,
    **kwargs,
)
```

The authors develop a correlation between shear wave velocity and CPT properties based on Christchurch-specific general soils. The soils were predominantly sand and silty sand. While the original formula uses the raw cone tip resistance, the authors suggest that the corrected cone resistance can be used without changes to the formula and prediction standard deviation.

Further work on the Banks Peninsula where loess soils are present, showed a significant underprediction of the shear wave velocity. The correlation was adjusted for these soils.

Note that all stresses in the equation are given in kPa.

When used with `apply_correlation`, use `'Vs CPT McGann et al (2018)'` as correlation name.

$$
\text{Christchurch general soils}
$$

$$
V_s = 18.4 \cdot q_t^{0.144} \cdot f_s^{0.083} \cdot z^{0.278}
$$

$$
\sigma_{\ln(V_s)} = \begin{cases}
0.162 \ \text{for } z \leq 5m,\\
0.216 - 0.0108 \cdot z \ \text{for } 5m < z < 10m \\
0.108 \ \text{for } z \geq 10m
\end{cases}
$$

$$
\text{Loess soils}
$$

$$
V_s = 103.6 \cdot q_t^{0.0074} \cdot f_s^{0.130} \cdot z^{0.253}
$$

$$
\sigma_{\ln(V_s)} = 0.2367
$$

$$
\epsilon = \frac{\ln (V_{sM}) - \ln (V_{sP})}{\sigma_{\ln(V_{sP})}}
$$

![Comparison of measured and calculated values for general correlation](/docs/assets/groundhog/docs/site_investigation/images/vs_CPT_mcgannetal_1.png)

*Comparison of measured and calculated values for general correlation*

![Residuals for loess-specific correlation](/docs/assets/groundhog/docs/site_investigation/images/vs_CPT_mcgannetal_2.png)

*Residuals for loess-specific correlation*

McGann, Christopher R., Brendon A. Bradley, and Seokho Jeong. "Empirical correlation for estimating shear-wave velocity from cone penetration test data for banks Peninsula loess soils in Canterbury, New Zealand." Journal of Geotechnical and Geoenvironmental Engineering 144.9 (2018): 04018054.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qt` | MPa | 0.0 <= qt <= 100.0 | required | Corrected cone tip resistance ($q_t$) |
| `fs` | MPa | 0.0 <= fs <= 10.0 | required | Sleeve friction ($f_s$) |
| `depth` | m | 0.0 <= depth <= 100.0 | required | Depth below ground surface ($z$) |
| `coefficient1_general` | - |  | `18.4` | First calibration coefficient in general equation |
| `coefficient2_general` | - |  | `0.144` | Second calibration coefficient in general equation |
| `coefficient3_general` | - |  | `0.083` | Third calibration coefficient in general equation |
| `coefficient4_general` | - |  | `0.278` | Fourth calibration coefficient in general equation |
| `coefficient1_loess` | - |  | `103.6` | First calibration coefficient in loess equation |
| `coefficient2_loess` | - |  | `0.0074` | Second calibration coefficient in loess equation |
| `coefficient3_loess` | - |  | `0.13` | Third calibration coefficient in loess equation |
| `coefficient4_loess` | - |  | `0.253` | Fourth calibration coefficient in loess equation |
| `loess` |  |  | `False` | Boolean determining whether the loess equation needs to be used |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Vs [m/s]` | m/s | Shear wave velocity ($V_s$) |
| `sigma_lnVs [-]` | - | Standard deviation on natural logarithm of Vs ($\sigma_{\ln (V_s)}$) |

**References**

- McGann, Christopher R., et al. "Development of an empirical correlation for predicting shear wave velocity of Christchurch soils from cone penetration test data." Soil Dynamics and Earthquake Engineering 75 (2015): 66-75.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="constrainedmodulus_pcpt_robertson"></a>

## `constrainedmodulus_pcpt_robertson`

<span class="gc-badge gc-available" data-geocore-function="constrainedmodulus_pcpt_robertson">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Robertson Constrained Modulus (CPT)](/docs/geocore/using/modules#constrainedmodulus_pcpt_robertson)

```python
constrainedmodulus_pcpt_robertson(
    qt,
    ic,
    sigma_vo,
    sigma_vo_eff,
    coefficient1=0.0188,
    coefficient2=0.55,
    coefficient3=1.68,
    qt_pivot=14,
    **kwargs,
)
```

Calculates the one-dimensional constrained modulus. The constrained modulus is compared to direct measurements for different clays. The Bothkennar clay which is a soft silty estuarine clay is an outlier which shows an overprediction of $M$ with the CPT.

When used with `apply_correlation`, use `'M Robertson (2009)'` as correlation name.

$$
M = \alpha_M \cdot \left( q_t - \sigma_{v0} \right)
$$

$$
\text{when } I_c > 2.2 \text{:}
$$

$$
\alpha_M = Q_t \ \text{when } Q_t \leq 14
$$

$$
\alpha_M = 14 \ \text{when } Q_t > 14
$$

$$
\text{when } I_c \leq 2.2
$$

$$
\alpha_M = 0.0188 \cdot \left[ 10^{0.55 I_c  + 1.68} \right]
$$

$$
Q_{t} = \frac{q_t - \sigma_{vo}}{\sigma_{vo}^{\prime}}
$$

![Comparison of measured and calculated values for constrained modulus for various soils](/docs/assets/groundhog/docs/site_investigation/images/constrainedmodulus_pcpt_robertson.png)

*Comparison of measured and calculated values for constrained modulus for various soils*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qt` | MPa | 0.0 <= qt <= 100.0 | required | Corrected cone tip resistance ($q_t$) |
| `ic` | - | 1.0 <= ic <= 5.0 | required | Soil behaviour type index ($I_c$) |
| `sigma_vo` | kPa | 0.0 <= sigma_vo <= 2000.0 | required | Total vertical stress ($\sigma_{vo}$) |
| `sigma_vo_eff` | kPa | 0.0 <= sigma_vo_eff <= 1000.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `coefficient1` |  |  | `0.0188` | First calibration coefficient (default=0.0188) |
| `coefficient2` |  |  | `0.55` | Second calibration coefficient (default=0.55) |
| `coefficient3` |  |  | `1.68` | Third calibration coefficient (default=1.68) |
| `qt_pivot` |  |  | `14` | Value of $Q_t$ when the formula for $\alpha_M$ changes (default=14) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `alphaM [-]` | - | Multiplier on net cone resistance [-] ($\alpha_M$) |
| `M [kPa]` | kPa | Contrained modulus for one-dimensional compression [kPa] ($M$) |
| `mv [1/kPa]` | 1/kPa | Modulus of volumetric compressiblity [1/kPa] ($m_v$) |

**References**

- CPT guide - 7th edition - Robertson and Cabal (2022)

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="vs_stressdependent_stuyts"></a>

## `vs_stressdependent_stuyts`

<span class="gc-badge gc-available" data-geocore-function="vs_stressdependent_stuyts">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Stuyts (2024) Stress-Dependent Shear Wave Velocity](/docs/geocore/using/modules#vs_stressdependent_stuyts)

```python
vs_stressdependent_stuyts(
    sigma_vo_eff,
    ic,
    a0=2.075,
    a1=-0.213,
    a2=0.77,
    a3=-0.25,
    **kwargs,
)
```

Calculates the shear wave velocity using the calibrated power-law expression proposed by Stuyts et al (2024). The correlation is calibrated on shear wave velocity measurements with the seismic CPT for sedimentary soils from the Southern North Sea. The correlation includes a dependency on the effective stress conditions and on the soil type through Robertson's soil behaviour type index. The correlations shows neutral bias and a coefficient of variation of 0.188 for the calibration dataset.

$$
V_s = {\alpha} \left( \frac{\sigma_{vo}^{\prime}}{1 \text{kPa}} \right)^{\beta} = 10^{a_0 + a_1 \cdot I_c} \left( \frac{\sigma_{vo}^{\prime}}{1 \text{kPa}} \right)^{a_2 + a_3 \cdot \log_{10}(\alpha)}
$$

$$
V_s = 10^{2.075 - 0.213 \cdot I_c} \left( \frac{\sigma_{vo}^{\prime}}{1 \text{kPa}} \right)^{0.77 - 0.25 \cdot \log_{10}(\alpha)}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `sigma_vo_eff` | kPa | 50.0 <= sigma_vo_eff <= 800.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `ic` | - | 1.0 <= ic <= 4.0 | required | Soil behaviour type index ($I_c$) |
| `a0` | - | 1.7 <= a0 <= 2.5 | `2.075` | Calibration coefficient 0 ($a_0$) |
| `a1` | - | -0.5 <= a1 <= -0.05 | `-0.213` | Calibration coefficient 1 ($a_1$) |
| `a2` | - | 0.5 <= a2 <= 1.0 | `0.77` | Calibration coefficient 2 ($a_2$) |
| `a3` | - | -0.5 <= a3 <= -0.1 | `-0.25` | Calibration coefficient 3 ($a_3$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Vs [m/s]` | m/s | Shear wave velocity [m/s] ($V_s$) |

**References**

- Stuyts, B.; Weijtjens, W.; Jurado, C.S.; Devriendt, C.; Kheffache, A. A Critical Review of Cone Penetration Test-Based Correlations for Estimating Small-Strain Shear Modulus in North Sea Soils. Geotechnics 2024, 4, 604-635. https://doi.org/10.3390/geotechnics4020033

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="dissipation_test_teh"></a>

## `dissipation_test_teh`

<span class="gc-badge gc-available" data-geocore-function="dissipation_test_teh">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Teh & Houlsby (1991) Dissipation Curve](/docs/geocore/using/modules#dissipation_test_teh)

```python
dissipation_test_teh(
    ch,
    shearmodulus,
    undrained_shear_strength,
    u_initial,
    cone_area=10.0,
    sensor_location='u2',
    **kwargs,
)
```

Calculates the pore pressure dissipation from a dissipation tests in clay according to the normalised dissipation curves proposed by Teh & Houlsby (1991).

$$
T^{*} = \frac{c_h \cdot t}{a^2 \cdot \sqrt{I_r}}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `ch` | m2/yr | 0.0 <= ch <= 100.0 | required | Horizontal coefficient of consolidation ($c_h$) |
| `shearmodulus` | kPa | 0.0 <= shearmodulus <= 500000.0 | required | Shear modulus of the soil ($G$) |
| `undrained_shear_strength` | kPa | 1.0 <= undrained_shear_strength <= 500.0 | required | Undrained shear strength ($S_u$) |
| `u_initial` | kPa | 0.0 <= u_initial <= 2000.0 | required | Initial excess pore pressure ($\Delta u_i$) |
| `cone_area` | cm2 | 2.0 <= cone_area <= 15.0 | `10.0` | Cone area ($\pi a^2$) |
| `sensor_location` |  | one of `u1`, `u2` | `'u2'` | Location of the pore pressure sensor |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `delta u [kPa]` | kPa | List with excess pore pressures [kPa] ($\Delta u$) |
| `t [s]` | s | List with times for excess pore pressure dissipation [s] ($t$) |
| `delta u / delta u_i [-]` | - | Normalised excess pore pressure decay [-] ($\Delta u \Delta u_i$) |
| `T* [-]` | - | Time factors [-] ($T^*$) |
| `Ir [-]` | - | Rigidity index (G/Su) [-] |
| `Cone radius [m]` | m | Radius of the cone [m] |

**References**

- Teh, C. I., & Houlsby, G. T. (1991). An analytical study of the cone penetration test in clay. Geotechnique, 41(1), 17-34.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="clippingdepths_qc1n_tianlehane"></a>

## `clippingdepths_qc1N_tianlehane`

<span class="gc-badge gc-available" data-geocore-function="clippingdepths_qc1N_tianlehane">Available in GeoCore</span> [Site investigation › In-situ: PCPT functions › Tian & Lehane (2025) Layer Clipping Depths](/docs/geocore/using/modules#clippingdepths_qc1n_tianlehane)

```python
clippingdepths_qc1N_tianlehane(qc1NW, qc1NS, cone_diameter=0.03568, tolerance=0.05)
```

Calculates the depths where the normalised cone resistance reaches steady values in weak over strong layer systems based on the equations proposed by Tian and Lehane (2025). These depths can be used to filter CPT data which belongs to a layer transition. The equations were developed based on centrifuge and pressure chamber testing with various two-layer systems (denser sand over looser sand, looser sand over denser sand, sand over clay). Note that the equations provided by Tian and Lehane only work for weaker layers (lower normalised cone resistance) overlying stronger layers (higher normalised cone resistance).

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

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc1NW` | - | 0.0 <= qc1NW <= 1000.0 | required | Steady-state normalised cone resistance in the weaker layer ($q_{c1N,W}$) |
| `qc1NS` | - | 0.0 <= qc1NS <= 1000.0 | required | Steady-state normalised cone resistance in the stronger layer ($q_{c1N,S}$) |
| `cone_diameter` | m | 0.001 <= cone_diameter <= 1000.0 | `0.03568` | Cone diameter ($d_c$) |
| `tolerance` | - | 0.001 <= tolerance <= 0.999 | `0.05` | Defines the multiplier to detect which data needs to be clipped |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `r` |  | Ratio of weak to strong normalised cone resistance [-] ($r$) |
| `eta` |  | Multiplier on the normalised cone resistance of the strongest layer defining the normalised cone resistance at the interface [-] ($\eta$) |
| `qc1N0` |  | Normalised cone tip resistance at the interface [-] ($q_{c1N0}$) |
| `as` |  | Fitting parameter for strong layer [-] ($a_s$) |
| `aw` |  | Fitting parameter for weak layer [-] ($a_w$) |
| `z*W` |  | Array of normalised depths in the weak layer [-] ($z^*_W$) |
| `z*S` |  | Array of normalised depths in the strong layer [-] ($z^*_S$) |
| `qc1N weak` |  | Array of normalised cone resistances in the weak layer [-] ($q_{c1N,W}$) |
| `qc1N strong` |  | Array of normalised cone resistances in the strong layer [-] ($q_{c1N,S}$) |
| `qc1N weak function` |  | Interpolation function providing normalised depth as a function of normalised cone resistance for the weak layer |
| `qc1N strong function` |  | Interpolation function providing normalised depth as a function of normalised cone resistance for the strong layer |
| `z* clipping weak` |  | Normalised offset from the interface in the weak layer below which CPT data needs to be clipped because it belongs to the layer transition [-] |
| `z* clipping strong` |  | Normalised offset from the interface in the weak layer above which CPT data needs to be clipped because it belongs to the layer transition [-] |
| `z clipping weak` |  | Absolute offset from the interface in the weak layer below which CPT data needs to be clipped because it belongs to the layer transition [m] |
| `z clipping strong` |  | Absolute offset from the interface in the weak layer above which CPT data needs to be clipped because it belongs to the layer transition [m] |

**References**

- Tian, Y. and Lehane, B. (2025). The influence of soil layering and penetrometer diameter on penetration resistance. Canadian Geotechnical Journal, DOI: 10.1139/cgj-2024-0491

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
