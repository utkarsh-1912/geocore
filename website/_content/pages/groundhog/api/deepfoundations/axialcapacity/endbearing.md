---
title: Unit end bearing
slug: groundhog/api/deepfoundations/axialcapacity/endbearing
section: Groundhog API Reference
description: 'API reference for groundhog.deepfoundations.axialcapacity.endbearing: 4 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/deepfoundations/axialcapacity/endbearing.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.deepfoundations.axialcapacity.endbearing
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/piles/endbearing.html
geocore_available: true
geocore_functions:
- API_unit_end_bearing_clay
- API_unit_end_bearing_sand_rp2geo
- unitendbearing_clay_almhamre
- unitendbearing_sand_almhamre
---

Module `groundhog.deepfoundations.axialcapacity.endbearing` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/deepfoundations/axialcapacity/endbearing.py).

Upstream documentation: [Unit end bearing](https://groundhog.readthedocs.io/en/main/piles/endbearing.html).

**Functions:** [`API_unit_end_bearing_clay`](#api_unit_end_bearing_clay), [`API_unit_end_bearing_sand_rp2geo`](#api_unit_end_bearing_sand_rp2geo), [`unitendbearing_sand_almhamre`](#unitendbearing_sand_almhamre), [`unitendbearing_clay_almhamre`](#unitendbearing_clay_almhamre)

<a id="api_unit_end_bearing_clay"></a>

## `API_unit_end_bearing_clay`

<span class="gc-badge gc-available" data-geocore-function="API_unit_end_bearing_clay">Available in GeoCore</span> [Pile calculations › Unit end bearing › API (Clay)](/docs/geocore/using/modules#api_unit_end_bearing_clay)

```python
API_unit_end_bearing_clay(undrained_shear_strength, N_c=9.0, **kwargs)
```

Calculates unit end bearing in clay according to API RP 2 GEO. For piles considered to be plugged, the bearing pressure may be assumed to act over the entire cross-section of the pile. For unplugged piles, the bearing pressure acts on the pile wall annulus only. That a pile is considered plugged or unplugged shall be based on static calculations. A pile can be driven in an unplugged condition but behave as plugged under static loads.

Use the string `'API RP2 GEO Clay'` to define this method in a `SoilProfile`.

$$
q = N_c \cdot S_u
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `undrained_shear_strength` | kPa | 0.0<=undrained_shear_strength<=400.0 | required | Undrained shear strenght at the pile tip ($S_u$) |
| `N_c` | - | 7.0<=N_c<=12.0 | `9.0` | Bearing capacity factor (optional, default=9.0) ($N_c$) |

**Returns**

Unit end bearing ($q$) [$kPa$]

Return type: `Python dictionary with keys ['q_b [kPa]']`

**References**

- API RP 2GEO, API RP 2GEO Geotechnical and Foundation Design Considerations, 2011

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="api_unit_end_bearing_sand_rp2geo"></a>

## `API_unit_end_bearing_sand_rp2geo`

<span class="gc-badge gc-available" data-geocore-function="API_unit_end_bearing_sand_rp2geo">Available in GeoCore</span> [Pile calculations › Unit end bearing › API RP2 GEO (Sand)](/docs/geocore/using/modules#api_unit_end_bearing_sand_rp2geo)

```python
API_unit_end_bearing_sand_rp2geo(
    api_relativedensity,
    api_soildescription,
    sigma_vo_eff,
    qb_limit=False,
    **kwargs,
)
```

Calculates unit end bearing in sand according to API RP2 GEO.

Use the string `'API RP2 GEO Sand'` to define this method in a `SoilProfile`.

$$
q = N_q \cdot p'_{o,tip}
$$

![API RP 2 GEO values (TODO: Add figure file in docs)](/docs/assets/groundhog/docs/piles/images/API_unit_end_bearing_sand_1.PNG)

*API RP 2 GEO values (TODO: Add figure file in docs)*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `api_relativedensity` | - | one of `Very loose`, `Loose`, `Medium dense`, `Dense`, `Very dense` | required | Relative density of the sand Options: ("Very loose","Loose","Medium dense","Dense","Very dense"), regex: None ($D_r$) |
| `api_soildescription` | - | one of `Sand`, `Sand-silt` | required | Description of the soil type Options: ("Sand","Sand-silt"), regex: None ($-$) |
| `sigma_vo_eff` | kPa | 0.0<=vertical_effective_stress | required | In-situ vertical effective stress at the pile tip ($p'_{o,tip}$) |
| `qb_limit` |  |  | `False` | No upstream documentation. |

**Returns**

Unit end bearing ($q_b$) [$kPa$], Unit end bearing (limited) ($q_{b,limited}$) [$kPa$], Unit end bearing limit ($q_{b,lim}$) [$kPa$]

Return type: `Python dictionary with keys ['q_b [kPa]','q_b_with_lim [kPa]','q_b_lim [kPa]']`

**References**

- API RP 2GEO, API RP 2GEO Geotechnical and Foundation Design Considerations, 2011

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="unitendbearing_sand_almhamre"></a>

## `unitendbearing_sand_almhamre`

<span class="gc-badge gc-available" data-geocore-function="unitendbearing_sand_almhamre">Available in GeoCore</span> [Pile calculations › Unit end bearing › Alm & Hamre (Sand)](/docs/geocore/using/modules#unitendbearing_sand_almhamre)

```python
unitendbearing_sand_almhamre(qt, sigma_vo_eff, multiplier=0.15, exponent=0.2, **kwargs)
```

Calculates unit end bearing in sand according to Alm & Hamre.

$$
q_{b,sand} = 0.15 \cdot q_t \cdot \left( \frac{q_t}{\sigma_{vo}^{\prime}} \right)^{0.2}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qt` | MPa | 0.0 <= qt <= 120.0 | required | Total cone resistance ($q_t$) |
| `sigma_vo_eff` | kPa | sigma_vo_eff >= 0.0 | required | Vertical effective stress ($\sigma_{vo}^{\prime}$) |
| `multiplier` | - |  | `0.15` | Multipier for unit end bearing |
| `exponent` | - |  | `0.2` | Exponent for unit end bearing |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `q_b_coring [kPa]` | kPa | Unit end bearing for pile driving ($q_{b,sand}$) |
| `q_b_plugged [kPa]` | kPa | Taken equal to the coring unit end bearing but tubular piles are not assumed to be driven in a plugged manner |
| `plugged []` |  | Determines whether the pile is plugged (False for driving piles) |
| `internal_friction []` |  | Determines whether internal friction is taken into account (True by default for Alm & Hamre formula) |

**References**

- Alm, T., Hamre, L., 2001. Soil model for pile driveability predictions based on CPT interpretations. Presented at the International Conference On Soil Mechanics and Foundation Engineering. Alm, T., Hamre, L., 1998. Soil model for driveability predictions. Presented at the OTC 8835, Annual Offshore Technology Conference, Houston, Texas, p. 13.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="unitendbearing_clay_almhamre"></a>

## `unitendbearing_clay_almhamre`

<span class="gc-badge gc-available" data-geocore-function="unitendbearing_clay_almhamre">Available in GeoCore</span> [Pile calculations › Unit end bearing › Alm & Hamre (Clay)](/docs/geocore/using/modules#unitendbearing_clay_almhamre)

```python
unitendbearing_clay_almhamre(qt, multiplier=0.6, **kwargs)
```

Calculates unit end bearing in clay according to Alm & Hamre.

$$
q_{b,clay} = 0.6 \cdot q_t
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qt` | MPa | 0.0 <= qt <= 120.0 | required | Total cone resistance ($q_t$) |
| `multiplier` | - |  | `0.6` | Multipier for unit end bearing |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `q_b_coring [kPa]` | kPa | Unit end bearing for pile driving ($q_{b,sand}$) |
| `q_b_plugged [kPa]` | kPa | Not applicable |
| `plugged []` |  | Determines whether the pile is plugged (False for driving piles) |
| `internal_friction []` |  | Determines whether internal friction is taken into account (True by default for Alm & Hamre formula) |

**References**

- Alm, T., Hamre, L., 2001. Soil model for pile driveability predictions based on CPT interpretations. Presented at the International Conference On Soil Mechanics and Foundation Engineering. Alm, T., Hamre, L., 1998. Soil model for driveability predictions. Presented at the OTC 8835, Annual Offshore Technology Conference, Houston, Texas, p. 13.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
