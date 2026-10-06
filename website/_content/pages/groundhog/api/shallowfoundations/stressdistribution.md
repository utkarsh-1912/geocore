---
title: Stress distributions
slug: groundhog/api/shallowfoundations/stressdistribution
section: Groundhog API Reference
description: 'API reference for groundhog.shallowfoundations.stressdistribution: 6 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/shallowfoundations/stressdistribution.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.shallowfoundations.stressdistribution
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/shallowfoundations/stressdistribution.html
geocore_available: true
geocore_functions:
- stresses_circle
- stresses_lineload_retainingwall
- stresses_pointload
- stresses_rectangle
- stresses_stripload
- stresses_stripload_retainingwall
---

Module `groundhog.shallowfoundations.stressdistribution` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/shallowfoundations/stressdistribution.py).

Upstream documentation: [Stress distributions](https://groundhog.readthedocs.io/en/main/shallowfoundations/stressdistribution.html).

**Functions:** [`stresses_pointload`](#stresses_pointload), [`stresses_stripload`](#stresses_stripload), [`stresses_circle`](#stresses_circle), [`stresses_rectangle`](#stresses_rectangle), [`stresses_lineload_retainingwall`](#stresses_lineload_retainingwall), [`stresses_stripload_retainingwall`](#stresses_stripload_retainingwall)

<a id="stresses_pointload"></a>

## `stresses_pointload`

<span class="gc-badge gc-available" data-geocore-function="stresses_pointload">Available in GeoCore</span> [Shallow foundations › Stress distributions › Point Load Stress](/docs/geocore/using/modules#stresses_pointload)

```python
stresses_pointload(pointload, z, r, poissonsratio, **kwargs)
```

Calculates the stresses at a point below a line load according the solution proposed by Boussinesq (1885). The vertical stress increase is calculated as well as the increases in radial and tangential stress

$$
\Delta \sigma_z = \frac{3Q}{2 \pi z^2 \left[ 1 + \left( \frac{r}{z} \right)^2 \right]^{5/2}}
$$

$$
\Delta \sigma_r = \frac{Q}{2 \pi} \left( \frac{3 r^2 z}{(r^2 + z^2)^{5/2}} - \frac{1 - 2 \nu}{r^2 + z^2 + z \left( r^2 + z^2 \right)^{1/2}}\right)
$$

$$
\Delta \sigma_{\theta} = \frac{Q}{2 \pi} \left( 1 - 2 \nu \right) \left( \frac{z}{\left( r^2 + z^2 \right)^{3/2}} - \frac{1}{r^2 + z^2 + z \left( r^2 + z^2 \right)^{1/2} } \right)
$$

$$
\Delta \tau_{rz} = \frac{3 Q}{2 \pi} \left[ \frac{r z^2}{\left( r^2 + z^2 \right)^{5/2}} \right]
$$

![Nomenclature used for point load stress calculation (Budhu, 2011)](/docs/assets/groundhog/docs/shallowfoundations/images/stresses_pointload_1.png)

*Nomenclature used for point load stress calculation (Budhu, 2011)*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `pointload` | kN |  | required | Magnitude of the point load ($Q$) |
| `z` | m |  | required | Vertical distance from the surface to the point where the stresses are calculated ($z$) |
| `r` | m |  | required | Radial distance from the surface to the point where the stresses are calculated ($r$) |
| `poissonsratio` | - | 0.0 <= poissonsratio <= 0.5 | required | Poisson's ratio ($\nu$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `delta sigma z [kPa]` | kPa | Increase in vertical normal stress ($\Delta \sigma_z$) |
| `delta sigma r [kPa]` | kPa | Increase in radial normal stress ($\Delta \sigma_r$) |
| `delta sigma theta [kPa]` | kPa | Increase in tangential normal stress ($\Delta \sigma_{\theta}$) |
| `delta tau rz [kPa]` | kPa | Increase in shear stress in the rz plane ($\Delta \tau_{rz}$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="stresses_stripload"></a>

## `stresses_stripload`

<span class="gc-badge gc-available" data-geocore-function="stresses_stripload">Available in GeoCore</span> [Shallow foundations › Stress distributions › Strip Load Stress](/docs/geocore/using/modules#stresses_stripload)

```python
stresses_stripload(z, x, width, imposedstress, triangular=False, **kwargs)
```

Calculates the stress redistribution at a point in the subsoil due to a strip load with a given width, applied at the surface.

Two cases can be specified. By default, a uniform load is specified, but the stresses under a triangular load can also be calculated.

$$
R_1 = \sqrt{x^2 + z^2}
$$

$$
R_2 = \sqrt{(x - B)^2 + z^2}
$$

$$
\cos \left(\alpha + \beta \right) = z / R_1
$$

$$
\cos \beta = z / R_2
$$

$$
\text{Uniform load}
$$

$$
\Delta \sigma_z = \frac{q_s}{\pi} \left[ \alpha + \sin \alpha \cos \left( \alpha + 2 \beta \right) \right]
$$

$$
\Delta \sigma_x = \frac{q_s}{\pi} \left[ \alpha - \sin \alpha \cos \left( \alpha + 2 \beta \right) \right]
$$

$$
\Delta \tau_{zx} = \frac{q_s}{\pi} \left[ \sin \alpha \sin \left( \alpha + 2 \beta \right) \right]
$$

$$
\text{Triangular load}
$$

$$
\Delta \sigma_z = \frac{q_s}{\pi} \left( \frac{x}{B} \alpha - \frac{1}{2} \sin 2 \beta \right)
$$

$$
\Delta \sigma_x = \frac{q_s}{\pi} \left( \frac{x}{B} \alpha - \frac{z}{B} \ln \frac{R_1^2}{R_2^2} + \frac{1}{2} \sin 2 \beta \right)
$$

$$
\Delta \tau_zx = \frac{q_s}{2 \pi} \left( 1 + \cos 2 \beta - 2 \frac{z}{B} \alpha \right)
$$

![Nomenclature for inputs in stress calculation due to a strip footing](/docs/assets/groundhog/docs/shallowfoundations/images/stresses_stripload_1.png)

*Nomenclature for inputs in stress calculation due to a strip footing*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `z` | m | z >= 0.0 | required | Vertical distance from the soil surface ($z$) |
| `x` | m |  | required | Horizontal offset from the leftmost corner of the strip footing ($x$) |
| `width` | m | width >= 0.0 | required | Width of the strip footing ($B$) |
| `imposedstress` | $kN/m^2$ |  | required | Maximum value of the imposed force per unit area ($q_s$) |
| `triangular` |  |  | `False` | Boolean determining whether a triangular load pattern is applied |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `delta sigma z [kPa]` | kPa | Increase in vertical stress due to surface load ($\Delta \sigma_z$) |
| `delta sigma x [kPa]` | kPa | Increase in horizontal stress due to surface load ($\Delta \sigma_x$) |
| `delta tau zx [kPa]` | kPa | Increase in shear stress due to surface load ($\Delta \tau_{zx}$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="stresses_circle"></a>

## `stresses_circle`

<span class="gc-badge gc-available" data-geocore-function="stresses_circle">Available in GeoCore</span> [Shallow foundations › Stress distributions › Circular Footing Stress](/docs/geocore/using/modules#stresses_circle)

```python
stresses_circle(z, footing_radius, imposedstress, poissonsratio, **kwargs)
```

Calculates the stress distribution below a uniformly loaded circular foundation. The stresses are calculated below the center of the circular foundation

$$
\Delta \sigma_z = q_s \left[ 1 - \left( \frac{1}{1 + (r_0 / z)^2} \right)^{3/2} \right]
$$

$$
\Delta \sigma_r = \Delta \sigma_{\theta} = \frac{q_s}{2} \left[ (1 + 2 \nu) - \frac{4 (1 + \nu)}{\sqrt{1 + (r_0 / z)^2}} + \frac{1}{\left[ 1 + (r_0 / z)^2 \right]^{3/2}} \right]
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `z` | m | z >= 0.0 | required | Depth below the base of the foundation ($z$) |
| `footing_radius` | m | footing_radius >= 0.0 | required | Radius of the circular foundation ($r_0$) |
| `imposedstress` | kPa |  | required | Applied uniform stress to the circular footing ($q_s$) |
| `poissonsratio` | - | 0.0 <= poissonsratio <= 0.5 | required | Poissons ratio for the soil material ($\nu$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `delta sigma z [kPa]` | kPa | Vertical stress increase ($\Delta \sigma_z$) |
| `delta sigma r [kPa]` | kPa | Radial stress increase ($\Delta \sigma_r$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="stresses_rectangle"></a>

## `stresses_rectangle`

<span class="gc-badge gc-available" data-geocore-function="stresses_rectangle">Available in GeoCore</span> [Shallow foundations › Stress distributions › Rectangular Footing Stress](/docs/geocore/using/modules#stresses_rectangle)

```python
stresses_rectangle(imposedstress, length, width, z, **kwargs)
```

Calculates the stresses under the corner of a uniformly loaded rectangular area. Stresses under other points can be calculated by subdividing the rectangular in smaller sub-rectangles and using superposition stresses (justified because the solution is elastic). E.g. the stresses under the center of a rectangle is calculated by subdividing the rectangle into four equal sub-areas and calculating the stress below the corner of each and summing them.

$$
\Delta \sigma_z = \frac{q_s}{2 \pi} \left[ \tan^{-1} \frac{L B}{z R_3} + \frac{L B z}{R_3} \left( \frac{1}{R_1^2} + \frac{1}{R_2^2} \right) \right]
$$

$$
\Delta \sigma_x = \frac{q_s}{2 \pi} \left[ \tan^{-1} \frac{L B}{z R_3} - \frac{L B z}{R_1^2 R_3} \right]
$$

$$
\Delta \sigma_y = \frac{q_s}{2 \pi} \left[ \tan^{-1} \frac{L B}{z R_3} - \frac{L B z}{R_2^2 R_3} \right]
$$

$$
\Delta \tau_{zx} = \frac{q_s}{2 \pi} \left[ \frac{B}{R_2} - \frac{z^2 B}{R_1^2 R_3} \right]
$$

$$
\text{where}
$$

$$
R_1 = \sqrt{L^2 + z^2}
$$

$$
R_2 = \sqrt{B^2 + z^2}
$$

$$
R_3 = \sqrt{L^2 + B^2 + z^2}
$$

![Nomenclature used for calculation of stresses below the corner of a uniformly loaded rectangle](/docs/assets/groundhog/docs/shallowfoundations/images/stresses_rectangle_1.png)

*Nomenclature used for calculation of stresses below the corner of a uniformly loaded rectangle*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `imposedstress` | kPa |  | required | Stress applied to the uniformly loaded area ($q_s$) |
| `length` | m | length >= 0.0 | required | Dimension of the longest edge of the rectangle ($L$) |
| `width` | m | width >= 0.0 | required | Dimension of the shortest edge of the rectangle ($B$) |
| `z` | m | z >= 0.0 | required | Depth below the footing ($z$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `delta sigma z [kPa]` | kPa | Increase in vertical stress below the corner of the footing ($\Delta \sigma_z$) |
| `delta sigma x [kPa]` | kPa | Increase in horizontal stress in the width direction below the corner of the footing ($\Delta \sigma_x$) |
| `delta sigma y [kPa]` | kPa | Increase in horizontal stress in the length direction below the corner of the footing ($\Delta \sigma_y$) |
| `delta tau zx [kPa]` | kPa | Increase in shear stress in the zx plane below the corner of the footing ($\Delta \tau_{zx}$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="stresses_lineload_retainingwall"></a>

## `stresses_lineload_retainingwall`

<span class="gc-badge gc-available" data-geocore-function="stresses_lineload_retainingwall">Available in GeoCore</span> [Shallow foundations › Stress distributions › Line Load Stress (Retaining Wall)](/docs/geocore/using/modules#stresses_lineload_retainingwall)

```python
stresses_lineload_retainingwall(lineload, toe_depth, horizontal_offset, depth, **kwargs)
```

Calculates the elastic stress increase due to a line load (infinitely long out of plane) next to a buried earth-retaining structure.

$$
\Delta \sigma_x = \frac{4 Q a^2 b}{\pi H_0 \left( a^2 + b^2 \right)^2}
$$

$$
\Delta P_x = \frac{2 Q}{\pi \left( a^2 + 1 \right)}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `lineload` | kN/m | lineload >= 0.0 | required | Magnitude of the applied line load ($Q$) |
| `toe_depth` | m | toe_depth >= 0.0 | required | Depth of the toe of the retaining wall ($H_0$) |
| `horizontal_offset` | m | horizontal_offset >= 0.0 | required | Offset between the line load and the retaining structure ($a H_0$) |
| `depth` | m | depth >= 0.0 | required | Depth considered for the calculation (cannot be deeper than the toe depth) ($b H_0$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `delta sigma x [kPa]` | kPa | Increase of horizontal stress [kPa] ($\Delta \sigma_x$) |
| `delta P x [kN/m]` | kN/m | Increase of horizontal force [kN/m] ($\Delta P_x$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="stresses_stripload_retainingwall"></a>

## `stresses_stripload_retainingwall`

<span class="gc-badge gc-available" data-geocore-function="stresses_stripload_retainingwall">Available in GeoCore</span> [Shallow foundations › Stress distributions › Strip Load Stress (Retaining Wall)](/docs/geocore/using/modules#stresses_stripload_retainingwall)

```python
stresses_stripload_retainingwall(
    imposedstress,
    width,
    offset,
    toe_depth,
    depth,
    **kwargs,
)
```

Calculates the elastic stress increase due to a strip load (infinitely long out of plane) at an offset from a buried earth-retaining structure.

Note that all angles in the formulae are given in degrees.

$$
\Delta \sigma_x = \frac{2 q_s}{\pi} \left( \beta - \sin \beta \cos 2 \alpha \right)
$$

$$
\Delta P_x = \frac{q_s}{90} \left[ H_0 \left( \theta_2 - \theta_1 \right) \right]
$$

$$
\bar{z} = \frac{H_0^2 \left( \theta_2 - \theta_1 \right) - \left( R_1 - R_2 \right) + 57.3 B H_0}{2 H_0 \left( \theta_2 - \theta_1 \right)}
$$

$$
\theta_1 = \tan^{-1} \left( \frac{a}{H_0} \right)
$$

$$
\theta_2 = \tan^{-1} \left( \frac{a + B}{H_0} \right)
$$

$$
R_1 = \left( a + B \right)^2 \left(90 -\theta_2 \right)
$$

$$
R_2 = a^2 \left( 90 - \theta_1 \right)
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `imposedstress` | kPa | imposedstress >= 0.0 | required | Applied stress for the strip load ($q_s$) |
| `width` | m | width >= 0.0 | required | Width of the strip load ($B$) |
| `offset` | m | offset >= 0.0 | required | Shortest horizontal offset between the strip load and the retaining wall ($a$) |
| `toe_depth` | m | toe_depth >= 0.0 | required | Toe depth of the retaining structure ($H_0$) |
| `depth` | m | depth >= 0.0 | required | Depth for the stress calculation ($z$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `delta sigma x [kPa]` | kPa | Increase of the lateral stress [kPa] ($\Delta \sigma_x$) |
| `delta P x [kN/m]` | kN/m | Increase of lateral force [kN/m] ($\Delta P_x$) |
| `z bar [m]` | m | Application depth of the force [m] ($\bar{z}$) |
| `theta 1 [deg]` | deg | Angle theta 1 [deg] ($\theta_1$) |
| `theta 2 [deg]` | deg | Angle theta 2 [deg] ($\theta_2$) |
| `R 1 [m]` | m | First offset [m] ($R_1$) |
| `R 2 [m]` | m | Second offset [m] ($R_2$) |
| `alpha [deg]` | deg | Angle alpha [deg] ($\alpha$) |
| `beta [deg]` | deg | Angle beta [deg] ($\beta$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
