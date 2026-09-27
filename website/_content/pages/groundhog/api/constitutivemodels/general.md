---
title: general
slug: groundhog/api/constitutivemodels/general
section: Groundhog API Reference
description: 'API reference for groundhog.constitutivemodels.general: 2 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/constitutivemodels/general.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.constitutivemodels.general
geocore_available: false
---

Module `groundhog.constitutivemodels.general` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/constitutivemodels/general.py).

**Functions:** [`mohrcoulomb_triaxial_compression`](#mohrcoulomb_triaxial_compression), [`mohrcoulomb_triaxial_extension`](#mohrcoulomb_triaxial_extension)

<a id="mohrcoulomb_triaxial_compression"></a>

## `mohrcoulomb_triaxial_compression`

```python
mohrcoulomb_triaxial_compression(sigma_3, cohesion, phi, latex_titles=True, **kwargs)
```

Calculates Mohr's circle and the orientation of the failure plane for a situation in which the radial (effective) stress is kept constant. A Mohr-Coulomb failure criterion with (effective) cohesion and (effective) friction angle is used. The user needs to specify the value of the radial stress and the values of cohesion and friction angle. The axial stress at failure and the orientation of the failure plane are then calculated. A graphical construction of Mohr's circle is also made as a Plotly plot. Note that this construction can be used for both total stress and effective stress analysis, the user needs to make an appropriate choice.

$$
\tau_f = c + \sigma \tan \varphi
$$

$$
\text{Failure plane orientation (relative to vertical)} = \frac{1}{2} \left( \frac{\pi}{2} - \varphi \right)
$$

$$
\tau_f = \frac{\sigma_1 - \sigma_3}{2} \cdot \cos \varphi
$$

$$
\sigma_f = \frac{\sigma_1 + \sigma_3}{2} - \frac{\sigma_1 - \sigma_3}{2} \cdot \sin \varphi
$$

$$
\implies \frac{\sigma_1 - \sigma_3}{2} \cdot \cos \varphi = c + \left( \frac{\sigma_1 + \sigma_3}{2} - \frac{\sigma_1 - \sigma_3}{2} \cdot \sin \varphi \right) \tan \varphi
$$

![Illustration of the concepts of Mohr's circle](/docs/assets/groundhog/docs/constitutivemodels/images/mohrs_circle.png)

*Illustration of the concepts of Mohr's circle*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `sigma_3` | kPa | sigma_3 >= 0.0 | required | Radial stress (total or effective) ($\sigma_3$) |
| `cohesion` | kPa | cohesion >= 0.0 | required | Cohesion (total or effective) ($c$) |
| `phi` | deg | 0.0 <= phi <= 90.0 | required | Friction angle (total or effective) ($\varphi$) |
| `latex_titles` |  |  | `True` | Boolean determining whether axis titles should be shown as LaTeX (default = True) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `sigma_1_f [kPa]` | kPa | Axial stress at failure [kPa] ($\sigma_{1,f}$) |
| `sigma_3_f [kPa]` | kPa | Radial stress at failure as specified by the user [kPa] ($\sigma_{3,f}$) |
| `Failure angle [deg]` | deg | Orientation of the failure plane (relative to the vertical) [deg] ($\frac{\pi}{2} - \varphi$) |
| `tau_f [kPa]` | kPa | Shear stress at failure [kPa] ($\tau_f$) |
| `sigma_f [kPa]` | kPa | Normal stress on the failure plane at failure [kPa] ($\sigma_f$) |
| `center [kPa]` | kPa | Center of Mohr's circle [kPa] ($\frac{\sigma_1 + \sigma_3}{2}$) |
| `radius [kPa]` | kPa | Radius of Mohr's circle [kPa] ($\frac{\sigma_1 - \sigma_3}{2}$) |
| `Mohr circle` |  | Pandas dataframe with normal stresses and shear stresses for Mohrs circle |
| `Plot` |  | Plotly plot showing Mohr's circle, the failure criterion and the failure point |

**References**

- Budhu (2011) Introduction to soil mechanics and foundations.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="mohrcoulomb_triaxial_extension"></a>

## `mohrcoulomb_triaxial_extension`

```python
mohrcoulomb_triaxial_extension(sigma_1, cohesion, phi, latex_titles=True, **kwargs)
```

Calculates Mohr's circle and the orientation of the failure plane for a situation in which the axial (effective) stress is reduced and the radial stress is kept constant, the axial stress then becomes the minor principal stress. A Mohr-Coulomb failure criterion with (effective) cohesion and (effective) friction angle is used. The user needs to specify the value of the axial stress and the values of cohesion and friction angle. The radial stress at failure and the orientation of the failure plane are then calculated. A graphical construction of Mohr's circle is also made as a Plotly plot. Note that this construction can be used for both total stress and effective stress analysis, the user needs to make an appropriate choice.

$$
\tau_f = c + \sigma \tan \varphi
$$

$$
\text{Failure plane orientation (relative to vertical)} = \frac{1}{2} \left( \frac{\pi}{2} - \varphi \right)
$$

$$
\tau_f = \frac{\sigma_1 - \sigma_3}{2} \cdot \cos \varphi
$$

$$
\sigma_f = \frac{\sigma_1 + \sigma_3}{2} - \frac{\sigma_1 - \sigma_3}{2} \cdot \sin \varphi
$$

$$
\implies \left( \frac{\cos \varphi}{2} - \frac{\tan \varphi}{2} + \frac{\sin \varphi \tan \varphi}{2} \right) \sigma_1 - c = \sigma_3 \left( \frac{1}{2} \cos \varphi + \frac{\tan \varphi}{2} + \frac{\sin \varphi \tan \varphi}{2} \right)
$$

![Illustration of the concepts of Mohr's circle](/docs/assets/groundhog/docs/constitutivemodels/images/mohrs_circle.png)

*Illustration of the concepts of Mohr's circle*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `sigma_1` | kPa | sigma_1 >= 0.0 | required | Radial stress (total or effective) ($\sigma_1$) |
| `cohesion` | kPa | cohesion >= 0.0 | required | Cohesion (total or effective) ($c$) |
| `phi` | deg | 0.0 <= phi <= 90.0 | required | Friction angle (total or effective) ($\varphi$) |
| `latex_titles` |  |  | `True` | Boolean determining whether axis titles should be shown as LaTeX (default = True) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `sigma_1_f [kPa]` | kPa | Radial stress at failure, as specified by the user [kPa] ($\sigma_{1,f}$) |
| `sigma_3_f [kPa]` | kPa | Axial stress at failure [kPa] ($\sigma_{3,f}$) |
| `Failure angle [deg]` | deg | Orientation of the failure plane (relative to the vertical) [deg] ($\frac{\pi}{2} - \varphi$) |
| `tau_f [kPa]` | kPa | Shear stress at failure [kPa] ($\tau_f$) |
| `sigma_f [kPa]` | kPa | Normal stress on the failure plane at failure [kPa] ($\sigma_f$) |
| `center [kPa]` | kPa | Center of Mohr's circle [kPa] ($\frac{\sigma_1 + \sigma_3}{2}$) |
| `radius [kPa]` | kPa | Radius of Mohr's circle [kPa] ($\frac{\sigma_1 - \sigma_3}{2}$) |
| `Mohr circle` |  | Pandas dataframe with normal stresses and shear stresses for Mohrs circle |
| `Plot` |  | Plotly plot showing Mohr's circle, the failure criterion and the failure point |

**References**

- Budhu (2011) Introduction to soil mechanics and foundations.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
