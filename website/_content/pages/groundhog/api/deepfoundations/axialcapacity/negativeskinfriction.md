---
title: Negative skin friction
slug: groundhog/api/deepfoundations/axialcapacity/negativeskinfriction
section: Groundhog API Reference
description: 'API reference for groundhog.deepfoundations.axialcapacity.negativeskinfriction: 1 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/deepfoundations/axialcapacity/negativeskinfriction.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.deepfoundations.axialcapacity.negativeskinfriction
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/piles/negativeskinfriction.html
geocore_available: true
geocore_functions:
- negativeskinfriction_pilegroup_zeevaertdebeer
---

Module `groundhog.deepfoundations.axialcapacity.negativeskinfriction` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/deepfoundations/axialcapacity/negativeskinfriction.py).

Upstream documentation: [Negative skin friction](https://groundhog.readthedocs.io/en/main/piles/negativeskinfriction.html).

**Functions:** [`negativeskinfriction_pilegroup_zeevaertdebeer`](#negativeskinfriction_pilegroup_zeevaertdebeer)

<a id="negativeskinfriction_pilegroup_zeevaertdebeer"></a>

## `negativeskinfriction_pilegroup_zeevaertdebeer`

<span class="gc-badge gc-available" data-geocore-function="negativeskinfriction_pilegroup_zeevaertdebeer">Available in GeoCore</span> [Pile calculations › Negative skin friction › Zeevaert & De Beer (Pile Group)](/docs/geocore/using/modules#negativeskinfriction_pilegroup_zeevaertdebeer)

```python
negativeskinfriction_pilegroup_zeevaertdebeer(
    depths,
    effective_unit_weights,
    lateral_earth_pressure_coefficients,
    interface_friction_angles,
    surcharge,
    diameter,
    diameter_influence,
    **kwargs,
)
```

Calculates the negative skin friction for a pile in a pile group according to the method of Zeevaert en De Beer. To allow any unit weight profile, the differential equation is solved in finite difference form.

$$
\frac{d \sigma_v^{\prime}}{dz} = \gamma^{\prime} - \tau \cdot \frac{O_s}{A}
$$

$$
m = K_0 \cdot \tan \delta^{\prime} \cdot \frac{O_s}{A}
$$

$$
\frac{\Delta \sigma_{v,i+1}^{\prime}}{\Delta z} - \gamma^{\prime} + m \cdot \sigma_{v,i}^{\prime} = 0
$$

$$
\sigma_{v,0}^{\prime} = p_0^{\prime}
$$

$$
O_s = \pi \cdot D_p
$$

$$
A = \frac{\pi}{4} \cdot \left( D_n^2 - D_p^2 \right)
$$

![Pile group with contributing soil and equilibrium of infinitesimal soil slice](/docs/assets/groundhog/docs/piles/images/negativeskinfriction_pilegroup_zeevaertdebeer_1.png)

*Pile group with contributing soil and equilibrium of infinitesimal soil slice*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `depths` | m |  | required | Array with depths used for the calculation Elementtype: float, order: ascending, unique: True, empty entries allowed: False ($z$) |
| `effective_unit_weights` | kN/m3 |  | required | Array with effective unit weights used for the calculation Elementtype: float, order: None, unique: False, empty entries allowed: False ($\gamma^{\prime}$) |
| `lateral_earth_pressure_coefficients` | - |  | required | Array with lateral earth pressure coefficient at each depth Elementtype: float, order: None, unique: False, empty entries allowed: False ($K_0$) |
| `interface_friction_angles` | deg |  | required | Array with interface friction angles Elementtype: float, order: None, unique: False, empty entries allowed: False ($\delta^{\prime}$) |
| `surcharge` | kPa | surcharge >= 0.0 | required | Amount of stress applied on top of the soil mass ($p_0^{\prime}$) |
| `diameter` | m | 0.01 <= diameter <= 10.0 | required | Pile diameter ($D_p$) |
| `diameter_influence` | m | diameter_influence >= 0.0 | required | Diameter of the zone of influence for negative skin friction ($D_n$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `virgin_effective_stress [kPa]` | kPa | Effective stress profile in the absence of surcharge ($\sigma_{vo}^{\prime}$) |
| `group_effective_stress [kPa]` | kPa | Effective stress accounting for the effect of soil hanging on the pile ($\sigma_{v}^{\prime}$) |
| `negative_skin_friction_profile_single [kN]` | kN | Cumulative negative skin friction for a single pile ($F_{n}$) |
| `negative_skin_friction_profile_group [kN]` | kN | Cumulative negative skin friction for pile in the group ($F_{n, group}$) |
| `negative_skin_friction [kN]` | kN | Total value of negative skin friction for a single pile ($F_{n,tot}$) |
| `negative_skin_friction_group [kN]` | kN | Total value of negative skin friction for a pile in a group ($F_{n,tot,group}$) |

**References**

- Zeevaert - De Beer (1966)

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
