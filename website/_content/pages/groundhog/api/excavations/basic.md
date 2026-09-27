---
title: Earth pressure coefficients
slug: groundhog/api/excavations/basic
section: Groundhog API Reference
description: 'API reference for groundhog.excavations.basic: 3 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/excavations/basic.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.excavations.basic
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/excavations/basic.html
geocore_available: true
geocore_functions:
- earthpressurecoefficients_frictionangle
- earthpressurecoefficients_poncelet
- earthpressurecoefficients_rankine
---

Module `groundhog.excavations.basic` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/excavations/basic.py).

Upstream documentation: [Earth pressure coefficients](https://groundhog.readthedocs.io/en/main/excavations/basic.html).

**Functions:** [`earthpressurecoefficients_frictionangle`](#earthpressurecoefficients_frictionangle), [`earthpressurecoefficients_poncelet`](#earthpressurecoefficients_poncelet), [`earthpressurecoefficients_rankine`](#earthpressurecoefficients_rankine)

<a id="earthpressurecoefficients_frictionangle"></a>

## `earthpressurecoefficients_frictionangle`

<span class="gc-badge gc-available" data-geocore-function="earthpressurecoefficients_frictionangle">Available in GeoCore</span> [Excavations › Earth pressure coefficients › Earth Pressure (Friction Angle)](/docs/geocore/using/modules#earthpressurecoefficients_frictionangle)

```python
earthpressurecoefficients_frictionangle(phi_eff, **kwargs)
```

Calculates coefficient of active and passive earth pressure based on a construction with Mohr's circle. Wall friction and wall inclination are not taken into account. The angle of the slip plane with the horizontal for the active and passive wedge are also provided.

$$
K_a = \frac{1 - \sin \varphi^{\prime}}{1 + \sin \varphi^{\prime}}
$$

$$
K_p = \frac{1 + \sin \varphi^{\prime}}{1 - \sin \varphi^{\prime}}
$$

$$
\theta_a = \frac{\pi}{4} + \frac{\varphi^{\prime}}{2}
$$

$$
\theta_p = \frac{\pi}{4} - \frac{\varphi^{\prime}}{2}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `phi_eff` | deg | 20.0 <= effective_friction_angle <= 50.0 | required | Effective friction of the soil ($\varphi^{\prime}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Ka [-]` | - | Coefficient of active earth pressure ($K_a$) |
| `Kp [-]` | - | Coefficient of passive earth pressure ($K_p$) |
| `theta_a [radians]` | radians | Angle of the active slip plane with the horizontal ($\theta_a$) |
| `theta_p [radians]` | radians | Angle of the passive slip plane with the horizontal ($\theta_p$) |

**References**

- Budhu (2011). Soil mechanics and foundations. John Wiley and Sons.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="earthpressurecoefficients_poncelet"></a>

## `earthpressurecoefficients_poncelet`

<span class="gc-badge gc-available" data-geocore-function="earthpressurecoefficients_poncelet">Available in GeoCore</span> [Excavations › Earth pressure coefficients › Earth Pressure (Poncelet)](/docs/geocore/using/modules#earthpressurecoefficients_poncelet)

```python
earthpressurecoefficients_poncelet(
    phi_eff,
    interface_friction_angle,
    wall_angle,
    top_angle,
    **kwargs,
)
```

Calculates the active and passive earth pressure coefficients for a retaining wall with friction (characterised by an interface friction angle) and an inclination to the vertical. Inclination of the ground surface on top of the retaining wall is also taken into account. Poncelet used Coulombs limit equilibrium approach to obtain expressions for coefficients of active and passive earth pressure. Note that these coefficients are applied to the effective stress and not to total stresses as used in Coulomb's limit equilibrium analysis.

$$
K_{aC} = \frac{\cos ^2 (\varphi^{\prime} - \eta)}{\cos ^2 \eta \cos (\eta + \delta) \left[  1 + \left( \frac{\sin (\varphi^{\prime} + \delta) \sin (\varphi^{\prime} - \beta)}{\cos (\eta + \delta) \cos (\eta - \beta)}\right)^{0.5} \right]^2}
$$

$$
K_{pC} = \frac{\cos ^2 (\varphi^{\prime} + \eta)}{\cos ^2 \eta \cos (\eta - \delta) \left[  1 - \left( \frac{\sin (\varphi^{\prime} + \delta) \sin (\varphi^{\prime} + \beta)}{\cos (\eta - \delta) \cos (\eta - \beta)}\right)^{0.5} \right]^2}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `phi_eff` | deg | 20.0 <= effective_friction_angle <= 50.0 | required | Effective friction angle of the soil ($\varphi^{\prime}$) |
| `interface_friction_angle` | deg | 15.0 <= interface_friction_angle <= 40.0 | required | Interface friction angle of the wall-soil interaction ($\delta$) |
| `wall_angle` | deg | 0.0 <= wall_angle <= 70.0 | required | Angle to the vertical of the portion of the wall in contact with the soil ($\eta$) |
| `top_angle` | deg | 0.0 <= top_angle <= 70.0 | required | Angle to the horizontal of the slope on top of the wall ($\beta$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `KaC [-]` | - | Poncelet's coefficient of active earth pressure ($K_{aC}$) |
| `KpC [-]` | - | Poncelet's coefficient of passive earth pressure ($K_{pC}$) |

**References**

- Budhu (2011). Soil mechanics and foundations. John Wiley and Sons.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="earthpressurecoefficients_rankine"></a>

## `earthpressurecoefficients_rankine`

<span class="gc-badge gc-available" data-geocore-function="earthpressurecoefficients_rankine">Available in GeoCore</span> [Excavations › Earth pressure coefficients › Earth Pressure (Rankine)](/docs/geocore/using/modules#earthpressurecoefficients_rankine)

```python
earthpressurecoefficients_rankine(phi_eff, wall_angle, top_angle, **kwargs)
```

The expressions for an inclined wall with sloping ground are developed by Rankine (1857) and Chu (1991). The angles of the slip planes to the horizontal can also be calculated as well as the inclinations of the resultant forces to the normal to the inclined face. Note that the wall friction is not taken into account.

$$
K_{aR} = \frac{\cos (\beta - \eta) \sqrt{1 + \sin ^2 \varphi^{\prime} - 2 \sin \varphi^{\prime} \cos \omega_a }}{\cos ^2 \eta \left( \cos \beta + \sqrt{\sin ^2 \varphi^{\prime} - \sin ^2 \beta} \right)}
$$

$$
K_{pR} = \frac{\cos (\beta - \eta) \sqrt{1 + \sin ^2 \varphi^{\prime} + 2 \sin \varphi^{\prime} \cos \omega_p }}{\cos ^2 \eta \left( \cos \beta - \sqrt{\sin ^2 \varphi^{\prime} - \sin ^2 \beta} \right)}
$$

$$
\omega_a = \sin ^{-1} \left( \frac{\sin \beta}{\sin \varphi^{\prime}} \right) - \beta + 2 \eta
$$

$$
\omega_p = \sin ^{-1} \left( \frac{\sin \beta}{\sin \varphi^{\prime}} \right) + \beta - 2 \eta
$$

$$
\theta_a = \frac{\pi}{4} + \frac{\varphi^{\prime}}{2} + \frac{\beta}{2} - \frac{1}{2} \sin ^{-1} \left( \frac{\sin \beta}{\sin \varphi^{\prime}} \right)
$$

$$
\theta_p = \frac{\pi}{4} - \frac{\varphi^{\prime}}{2} + \frac{\beta}{2} + \frac{1}{2} \sin ^{-1} \left( \frac{\sin \beta}{\sin \varphi^{\prime}} \right)
$$

$$
P_a = \frac{1}{2} K_{aR} \gamma^{\prime} H_0^2
$$

$$
P_p = \frac{1}{2} K_{pR} \gamma^{\prime} H_0^2
$$

$$
\xi_a = \tan ^{-1} \left( \frac{\sin \varphi^{\prime} \sin \theta_a}{1 - \sin \varphi^{\prime} \cos \theta_a} \right)
$$

$$
\xi_p = \tan ^{-1} \left( \frac{\sin \varphi^{\prime} \sin \theta_p}{1 + \sin \varphi^{\prime} \cos \theta_a} \right)
$$

![Sketch of the problem (after Budhu, 2011)](/docs/assets/groundhog/docs/excavations/images/earthpressurecoefficients_rankine_1.png)

*Sketch of the problem (after Budhu, 2011)*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `phi_eff` | deg | 20.0 <= effective_friction_angle <= 50.0 | required | Effective friction angle of the soil ($\varphi^{\prime}$) |
| `wall_angle` | deg | 0.0 <= wall_angle <= 70.0 | required | Angle to the vertical of the portion of the wall in contact with the soil ($\eta$) |
| `top_angle` | deg | 0.0 <= top_angle <= 70.0 | required | Angle to the horizontal of the slope on top of the wall ($\beta$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `KaR [-]` | - | Rankine coefficient of active earth pressure ($K_{aR}$) |
| `KpR [-]` | - | Rankine coefficient of passive earth pressure ($K_{pR}$) |
| `omega_a [-]` | - | Helper variable for active earth pressure ($\omega_a$) |
| `omega_p [-]` | - | Helper variable for passive earth pressure ($\omega_p$) |
| `theta_a [radians]` | radians | Angle of active slip plane to the horizontal ($\theta_a$) |
| `theta_p [radians]` | radians | Angle of passive slip plane to the horizontal ($\theta_p$) |
| `ksi_a [radians]` | radians | Angle of active resultant to the normal to the wall face ($\xi_a$) |
| `ksi_p [radians]` | radians | Angle of passive resultant to the normal to the wall face ($\xi_p$) |

**References**

- Budhu (2011). Soil mechanics and foundations. John Wiley and Sons.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
