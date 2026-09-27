---
title: Unit skin friction
slug: groundhog/api/deepfoundations/axialcapacity/skinfriction
section: Groundhog API Reference
description: 'API reference for groundhog.deepfoundations.axialcapacity.skinfriction: 4 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/deepfoundations/axialcapacity/skinfriction.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.deepfoundations.axialcapacity.skinfriction
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/piles/skinfriction.html
geocore_available: true
geocore_functions:
- API_unit_shaft_friction_clay
- API_unit_shaft_friction_sand_rp2geo
- unitskinfriction_clay_almhamre
- unitskinfriction_sand_almhamre
---

Module `groundhog.deepfoundations.axialcapacity.skinfriction` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/deepfoundations/axialcapacity/skinfriction.py).

Upstream documentation: [Unit skin friction](https://groundhog.readthedocs.io/en/main/piles/skinfriction.html).

**Functions:** [`API_unit_shaft_friction_sand_rp2geo`](#api_unit_shaft_friction_sand_rp2geo), [`API_unit_shaft_friction_clay`](#api_unit_shaft_friction_clay), [`unitskinfriction_sand_almhamre`](#unitskinfriction_sand_almhamre), [`unitskinfriction_clay_almhamre`](#unitskinfriction_clay_almhamre)

<a id="api_unit_shaft_friction_sand_rp2geo"></a>

## `API_unit_shaft_friction_sand_rp2geo`

<span class="gc-badge gc-available" data-geocore-function="API_unit_shaft_friction_sand_rp2geo">Available in GeoCore</span> [Pile calculations › Unit skin friction › API RP2 GEO (Sand)](/docs/geocore/using/modules#api_unit_shaft_friction_sand_rp2geo)

```python
API_unit_shaft_friction_sand_rp2geo(
    api_relativedensity,
    api_soildescription,
    sigma_vo_eff,
    fs_limit=False,
    tension_modifier=1.0,
    **kwargs,
)
```

Calculates unit skin friction according to the beta method in API RP 2GEO. The main difference is that the beta-parameter is defined directly in API RP 2GEO whereas API RP 2A WSD (2000) works with a soil pile friction angle.

Use the string `'API RP2 GEO Sand'` to define this method in a `SoilProfile`.

$$
f(z) = \beta \cdot p'_o(z)
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `api_relativedensity` | - | one of `Very loose`, `Loose`, `Medium dense`, `Dense`, `Very dense` | required | Relative density of the sand Options: ("Very loose","Loose","Medium dense","Dense","Very dense"), regex: None ($D_r$) |
| `api_soildescription` | - | one of `Sand`, `Sand-silt`, `Silt`, `Gravel` | required | Description of the soil type Options: ("Sand","Sand-silt"), regex: None ($-$) |
| `sigma_vo_eff` | kPa | 0.0<=vertical_effective_stress | required | In-situ vertical effective stress ($p'_o$) |
| `fs_limit` |  |  | `False` | No upstream documentation. |
| `tension_modifier` |  | 0.0 <= tension_modifier <= 1.0 | `1.0` | No upstream documentation. |

**Returns**

Unit skin friction ($f_s$) [$kPa$], Unit skin friction limit ($f_{s,lim}$) [$kPa$], Coefficient beta ($\beta$) [$-$]

Return type: `Python dictionary with keys ['f_s [kPa]','f_s_lim [kPa]','beta [-]']`

**References**

- API RP 2GEO, API RP 2GEO Geotechnical and Foundation Design Considerations, 2011

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="api_unit_shaft_friction_clay"></a>

## `API_unit_shaft_friction_clay`

<span class="gc-badge gc-available" data-geocore-function="API_unit_shaft_friction_clay">Available in GeoCore</span> [Pile calculations › Unit skin friction › API (Clay)](/docs/geocore/using/modules#api_unit_shaft_friction_clay)

```python
API_unit_shaft_friction_clay(undrained_shear_strength, sigma_vo_eff, **kwargs)
```

Calculates unit skin friction according to the alpha method in API RP 2GEO. Caution should be exercised in its application as there are many more variables which affect pile capacity than the ones accounted for in this equation. Due to the shortage of pile load tests in soils having ratios of undrained shear strenght to vertical effective stress greater than three. The function should be applied with considerable care for these high ratios. Similar judgment should be applied for deep penetrating piles in soils with high undrained shear strength. Low plasticity clays should be treated with particular caution. For very long piles some reduction in capacity may be warranted, particularly where the shaft friction degrades on continued displacement.

Use the string `'API RP2 GEO Clay'` to define this method in a `SoilProfile`.

$$
f(z) = \alpha \cdot S_u
$$

$$
\alpha = 0.5 \cdot \psi^{-0.5} & \quad \text{for } \psi \leq 1.0
$$

$$
\alpha = 0.5 \cdot \psi^{-0.25} & \quad \text{for } \psi > 1.0
$$

$$
\psi = \frac{S_u}{p'_o(z)}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `undrained_shear_strength` | kPa | 0.0<=undrained_shear_strength<=400.0 | required | Undrained shear strength ($S_u$) |
| `sigma_vo_eff` | kPa | 0.0<=vertical_effective_stress | required | In-situ vertical effective stress ($p'_o(z)$) |

**Returns**

Unit shaft friction ($f(z)$) [$kPa$], Ratio of undrained shear strength to vertical effective stress ($\psi$) [$-$], Alpha factor ($\alpha$) [$-$]

Return type: `Python dictionary with keys ['f_s [kPa]','psi [-]','alpha [-]']`

**References**

- API RP 2GEO, API RP 2GEO Geotechnical and Foundation Design Considerations, 2011.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="unitskinfriction_sand_almhamre"></a>

## `unitskinfriction_sand_almhamre`

<span class="gc-badge gc-available" data-geocore-function="unitskinfriction_sand_almhamre">Available in GeoCore</span> [Pile calculations › Unit skin friction › Alm & Hamre (Sand)](/docs/geocore/using/modules#unitskinfriction_sand_almhamre)

```python
unitskinfriction_sand_almhamre(
    qt,
    sigma_vo_eff,
    interface_friction_angle,
    depth,
    embedded_length,
    shape_factor_multiplier=80.0,
    atmospheric_pressure=101.325,
    fsi_sand_multiplier=0.0132,
    fsi_sand_exponent=0.13,
    multiplier_fsres=0.2,
    multiplier_outside=0.5,
    multiplier_inside=0.5,
    **kwargs,
)
```

Calculates the unit skin friction in sand according to the method by Alm & Hamre. The unit skin friction includes the effect of friction fatigue based on back-analysis from a number of jacket piles from North Sea Oil & Gas platforms. The authors recommend applying 50% of the calculated unit skin friction on the outside of the pile and 50% on the inside.

$$
f_s = f_{s,res} + (f_{s,i} - f_{s,res}) \cdot e^{k \cdot (z-z_{tip})}
$$

$$
k = \frac{\sqrt{q_t / \sigma_{vo}^{\prime}}}{80}
$$

$$
f_{s,i,sand} = 0.0132 \cdot q_t \cdot \left( \frac{\sigma_{vo}^{\prime}}{P_a} \right)^{0.13} \cdot \tan \delta
$$

$$
f_{s,res,sand} = 0.2 \cdot f_{s,i,sand}
$$

$$
f_{s,out} = 0.5 \cdot f_s
$$

$$
f_{s,in} = 0.5 \cdot f_s
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qt` | MPa | 0.0 <= qt <= 120.0 | required | Total cone resistance ($q_t$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Vertical effective stress ($\\sigma_vo^{\\prime}$) |
| `interface_friction_angle` | deg | 10.0 <= interface_friction_angle <= 50.0 | required | Interface friction angle for sand (ICP recommendations can be used in absence of other data) ($\\delta$) |
| `depth` | m | depth >= 0.0 | required | Depth at which unit skin friction is calculated ($z$) |
| `embedded_length` | m | embedded_length >= 0.0 | required | Depth of the pile tip below mudline ($z_{tip}$) |
| `shape_factor_multiplier` | - |  | `80.0` | Factor by which to divide for the shape factor k |
| `atmospheric_pressure` | kPa |  | `101.325` | Atmospheric pressure ($P_a$) |
| `fsi_sand_multiplier` | - |  | `0.0132` | Multiplier for initial unit skin friction in sand |
| `fsi_sand_exponent` | - |  | `0.13` | Exponent for initial unit skin friction in sand |
| `multiplier_fsres` | - |  | `0.2` | Multiplier on initial skin friction to obtain residual skin friction |
| `multiplier_outside` | - |  | `0.5` | Multiplier on calculated unit skin friction to obtain outside unit skin friction (default is 50%) |
| `multiplier_inside` | - |  | `0.5` | Multiplier on calculated unit skin friction to obtain inside unit skin friction (default is 50%) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `f_s_comp_out [kPa]` | kPa | Unit skin friction on the outside (with multiplier applied) ($f_{s,out}$) |
| `f_s_comp_in [kPa]` | kPa | Unit skin friction on the inside (with multiplier applied) ($f_{s,in}$) |
| `f_s_tens_out [kPa]` | kPa | Not applicable |
| `f_s_tens_in [kPa]` | kPa | Not applicable |
| `f_s_initial [kPa]` | kPa | Initial unit skin friction in sand (without multiplier for inside/outside) ($f_{s,i,sand}$) |
| `f_s_res [kPa]` | kPa | Residual unit skin friction in sand (without multiplier for inside/outside) ($f_{s,res,sand}$) |

**References**

- Alm, T., Hamre, L., 2001. Soil model for pile driveability predictions based on CPT interpretations. Presented at the International Conference On Soil Mechanics and Foundation Engineering. Alm, T., Hamre, L., 1998. Soil model for driveability predictions. Presented at the OTC 8835, Annual Offshore Technology Conference, Houston, Texas, p. 13.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="unitskinfriction_clay_almhamre"></a>

## `unitskinfriction_clay_almhamre`

<span class="gc-badge gc-available" data-geocore-function="unitskinfriction_clay_almhamre">Available in GeoCore</span> [Pile calculations › Unit skin friction › Alm & Hamre (Clay)](/docs/geocore/using/modules#unitskinfriction_clay_almhamre)

```python
unitskinfriction_clay_almhamre(
    depth,
    embedded_length,
    qt,
    fs,
    sigma_vo_eff,
    shape_factor_multiplier=80.0,
    multiplier_fsres_1=0.004,
    multiplier_fsres_2=0.0025,
    multiplier_fs_initial=1.0,
    multiplier_outside=1.0,
    multiplier_inside=1.0,
    **kwargs,
)
```

Calculates the unit skin friction in clay according to the method by Alm & Hamre. The unit skin friction includes the effect of friction fatigue based on back-analysis from a number of jacket piles from North Sea Oil & Gas platforms. The authors recommend applying 100% of the calculated unit skin friction on the outside of the pile and 100% on the inside.

$$
f_s = f_{s,res} + (f_{s,i} - f_{s,res}) \cdot e^{k \cdot (z-z_{tip})}
$$

$$
k = \frac{\sqrt{q_t / \sigma_{vo}^{\prime}}}{80}
$$

$$
f_{s,i,clay} = f_{s,CPT}
$$

$$
f_{s,res,clay} = 0.004 \cdot q_t \cdot \left( 1 - 0.0025 \cdot \frac{q_t}{\sigma_{vo}^{\prime}} \right)
$$

$$
f_{s,out} = f_s
$$

$$
f_{s,in} = f_s
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `depth` | m | depth >= 0.0 | required | Depth at which the unit skin friction is calculated ($z$) |
| `embedded_length` | m | embedded_length >= 0.0 | required | Pile tip depth below mudline ($z_{tip}$) |
| `qt` | MPa | 0.0 <= qt <= 120.0 | required | Total cone resistance ($q_t$) |
| `fs` | MPa | sleeve_friction >= 0.0 | required | Sleeve friction from the CPT ($f_{s,CPT}$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Vertical effective stress ($\\sigma_{vo}^{\\prime}$) |
| `shape_factor_multiplier` | - |  | `80.0` | Factor by which to divide for the shape factor k |
| `multiplier_fsres_1` | - |  | `0.004` | First multiplier on residual skin friction |
| `multiplier_fsres_2` | - |  | `0.0025` | Second multiplier on residual skin friction |
| `multiplier_fs_initial` | - |  | `1.0` | Multiplier on initial unit skin friction |
| `multiplier_outside` | - |  | `1.0` | Multiplier on calculated unit skin friction to obtain outside unit skin friction (default is 50%) |
| `multiplier_inside` | - |  | `1.0` | Multiplier on calculated unit skin friction to obtain inside unit skin friction (default is 50%) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `f_s_comp_out [kPa]` | kPa | Unit skin friction on the outside (with multiplier applied) ($f_{s,out}$) |
| `f_s_comp_in [kPa]` | kPa | Unit skin friction on the inside (with multiplier applied) ($f_{s,in}$) |
| `f_s_tens_out [kPa]` | kPa | Not applicable |
| `f_s_tens_in [kPa]` | kPa | Not applicable |
| `f_s_initial [kPa]` | kPa | Initial unit skin friction in sand (without multiplier for inside/outside) ($f_{s,i,sand}$) |
| `f_s_res [kPa]` | kPa | Residual unit skin friction in sand (without multiplier for inside/outside) ($f_{s,res,sand}$) |

**References**

- Alm, T., Hamre, L., 2001. Soil model for pile driveability predictions based on CPT interpretations. Presented at the International Conference On Soil Mechanics and Foundation Engineering. Alm, T., Hamre, L., 1998. Soil model for driveability predictions. Presented at the OTC 8835, Annual Offshore Technology Conference, Houston, Texas, p. 13.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
