---
title: Cavity expansion methods for cast in-situ piles
slug: groundhog/api/deepfoundations/boreholestability/cavityexpansion
section: Groundhog API Reference
description: 'API reference for groundhog.deepfoundations.boreholestability.cavityexpansion: 3 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/deepfoundations/boreholestability/cavityexpansion.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.deepfoundations.boreholestability.cavityexpansion
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/piles/cavityexpansion.html
geocore_available: true
geocore_functions:
- expansion_cylinder_tresca
- expansion_tresca_thicksphere
- stress_cylinder_elastic_isotropic
---

Module `groundhog.deepfoundations.boreholestability.cavityexpansion` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/deepfoundations/boreholestability/cavityexpansion.py).

Upstream documentation: [Cavity expansion methods for cast in-situ piles](https://groundhog.readthedocs.io/en/main/piles/cavityexpansion.html).

**Functions:** [`stress_cylinder_elastic_isotropic`](#stress_cylinder_elastic_isotropic), [`expansion_tresca_thicksphere`](#expansion_tresca_thicksphere), [`expansion_cylinder_tresca`](#expansion_cylinder_tresca)

<a id="stress_cylinder_elastic_isotropic"></a>

## `stress_cylinder_elastic_isotropic`

<span class="gc-badge gc-available" data-geocore-function="stress_cylinder_elastic_isotropic">Available in GeoCore</span> [Pile calculations › Cavity expansion methods › Elastic Cylinder Stress (Isotropic)](/docs/geocore/using/modules#stress_cylinder_elastic_isotropic)

```python
stress_cylinder_elastic_isotropic(
    radius,
    internal_pressure,
    farfield_pressure,
    borehole_radius,
    shear_modulus=nan,
    **kwargs,
)
```

Calculates the radial and tangential stress around a cylindrical borehole under internal pressure, in a soil mass with isotropic virgin stress conditions in the given plane

$$
\frac{d \sigma_{r}}{dr} + \frac{\left(\sigma_{r} - \sigma_{\theta} \right)}{r} = 0
$$

$$
\sigma_r | _{r=a} = p \\
\sigma_r | _{r=a} = p_0
$$

$$
\sigma_{r} = p_0 + \left( p - p_0 \right) \cdot \left( \frac{a}{r} \right)^2
$$

$$
\sigma_{\theta} = p_0 - \left( p - p_0 \right) \cdot \left( \frac{a}{r} \right)^2
$$

![Basic sketch of the cavity expansion problem](/docs/assets/groundhog/docs/piles/images/stress_elastic_isotropic.png)

*Basic sketch of the cavity expansion problem*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `radius` | m | radius >= 0.0 | required | Radius or radii at which to calculate the stresses (float or NumPy array) ($r$) |
| `internal_pressure` | kPa | internal_pressure >= 0.0 | required | Internal pressure on the borehole ($p$) |
| `farfield_pressure` | kPa | farfield_pressure >= 0.0 | required | Far-field pressure, equal to the virgin horizontal stress ($p_0$) |
| `borehole_radius` | m | borehole_radius >= 0.0 | required | Radius of the borehole ($a$) |
| `shear_modulus` | kPa | shear_modulus >= 0.0 (optional, default=np.nan). If unspecified, radial displacements are not calculated | `nan` | Shear modulus used to calculate the radial displacement ($G$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `radial stress [kPa]` | kPa | Radial stress at the specified radii ($\sigma_r$) |
| `tangential stress [kPa]` | kPa | Tangential stress at the specified radii ($\sigma_{\theta}$) |
| `radial displacement [m]` | m | Radial displacement (calculated if shear modulus is specified) ($u$) |

**References**

- Yu, H.-S., 2000. Cavity Expansion Methods in Geomechanics. Springer-Science+Business Media, B.V.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="expansion_tresca_thicksphere"></a>

## `expansion_tresca_thicksphere`

<span class="gc-badge gc-available" data-geocore-function="expansion_tresca_thicksphere">Available in GeoCore</span> [Pile calculations › Cavity expansion methods › Thick Sphere Expansion (Tresca)](/docs/geocore/using/modules#expansion_tresca_thicksphere)

```python
expansion_tresca_thicksphere(
    undrained_shear_strength,
    internal_radius,
    external_radius,
    internal_pressure,
    external_pressure,
    youngs_modulus,
    poissons_ratio,
    seed=100,
    **kwargs,
)
```

Calculates the stresses for cavity expansion around a thick-walled sphere in Tresca material.

The plastic radius is first calculated from the pressure boundary conditions. Using this plastic radius, the stresses in the elastic and plastic region are calculated.

$$
\text{Elastic solutions}
$$

$$
\sigma_r = -p_0 - (p - p_0) \frac{\left( \frac{b_0}{r} \right)^3 - 1}{\left( \frac{b_0}{a_0} \right)^3 - 1}
$$

$$
\sigma_{\theta} = \sigma_{\phi} = -p_0 + (p - p_0) \frac{\frac{1}{2} \left( \frac{b_0}{r} \right)^3 - 1}{\left( \frac{b_0}{a_0} \right)^3 - 1}
$$

$$
u = r - r_0 = \frac{p - p_0}{E} \frac{(1 - 2 \nu) r + \frac{(1 + \nu) b_0^3}{2 r^2}}{\left( \frac{b_0}{a_0} \right)^3 - 1}
$$

$$
\text{Yield criterion}
$$

$$
\sigma_1 - \sigma_3 = 2 \cdot S_u
$$

$$
\text{Internal pressure for yielding } (\sigma_1 = \sigma_{\theta}, \sigma_3 = \sigma_r)
$$

$$
p = p_{1y} = p_0 + \frac{4 \cdot S_u}{3} \left[ 1 - \left( \frac{a_0}{b_0} \right)^3 \right]
$$

$$
\text{Displacement at internal and external boundaries}
$$

$$
u |_{r=a_0} = \frac{2 \cdot S_u \cdot a_0}{E} \left[ \frac{2 \cdot (1 - 2 \nu) \cdot a_0^3 }{3 \cdot b_0^3} + \frac{1 + \nu}{3} \right]
$$

$$
u |_{r=b_0} = \frac{2 \cdot S_u \cdot (1 - \nu) \cdot a_0 }{E \cdot b_0^2}
$$

$$
\text{Stresses and displacements in the elastic region after yielding}
$$

$$
\sigma_r = - \frac{4 \cdot S_u \cdot c^3}{3 \cdot b_0^3} \left[ \left( \frac{b_0}{r} \right)^3 - 1 \right] - p_0
$$

$$
\sigma_{\theta} = \sigma_{\phi} = \frac{4 \cdot S_u \cdot c^3}{3 \cdot b_0^3} \left[ \frac{1}{2} \left( \frac{b_0}{r} \right)^3 + 1 \right] - p_0
$$

$$
u = \frac{4 \cdot S_u \cdot c^3}{3 \cdot E \cdot b_0^3} \left[ (1 - 2 \nu) \cdot r + \frac{(1 + \nu) b_0^3}{2 \cdot r^2} \right]
$$

$$
\text{Stresses in the plastic region}
$$

$$
\sigma_r = - 4 \cdot S_u \cdot \ln \left( \frac{c}{r} \right) - \frac{4 \cdot S_u}{3} \left[ 1 - \left( \frac{c}{b_0} \right)^3 \right] - p_0
$$

$$
\sigma_{\theta} = 2 \cdot S_u - 4 \cdot S_u \cdot \ln \left( \frac{c}{r} \right) - \frac{4 \cdot S_u}{3} \cdot \left[ 1 - \left( \frac{c}{b_0} \right)^3 \right] - p_0
$$

$$
\text{The pressure required to generate a plastic radius is thus}
$$

$$
p = 4 \cdot S_u \cdot \ln \left( \frac{c}{a} \right) + \frac{4 \cdot S_u}{3} \left[ 1 - \left( \frac{c}{b_0} \right)^3 \right] + p_0
$$

$$
\text{Expansion of the boundary}
$$

$$
\left( \frac{a}{a_0} \right)^3 = 1 + \frac{6 (1 - \nu) S_u c^3}{E \cdot a_0^3} - \frac{4 (1 - 2 \nu) S_u}{E} \left[ 3 \ln \left( \frac{c}{a_0} \right) + 1 - \left( \frac{c}{b_0} \right)^3 \right]
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `undrained_shear_strength` | kPa | undrained_shear_strength >= 0.0 | required | Undrained shear strength of the material surrounding the spherical cavity ($S_u$) |
| `internal_radius` | m | internal_radius >= 0.0 | required | Initial internal radius of the spherical cavity ($a_0$) |
| `external_radius` | m | external_radius >= 0.0 | required | Initial external radius of the region ($b_0$) |
| `internal_pressure` | kPa | internal_pressure >= 0.0 | required | Internal pressure applied on the inside of the sphere ($p$) |
| `external_pressure` | kPa | external_pressure >= 0.0 | required | External pressure on the outside of the sphere ($p_0$) |
| `youngs_modulus` | kPa | youngs_modulus >= 0.0 | required | Young's modulus of the material ($E$) |
| `poissons_ratio` | - | 0 <= poissons_ratio <= 0.5 | required | Poisson's ratio of the material ($\nu$) |
| `seed` | - |  | `100` | Number of radii at which stresses and displacements are calculated |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `elastic radii [m]` | m | Radii at which elastic stresses are calculated |
| `elastic_radial_stress [kPa]` | kPa | Radial stresses for purely elastic deformation ($\sigma_{r,elastic}$) |
| `elastic_tangential_stress [kPa]` | kPa | Tangential stresses for purely elastic deformation ($\sigma_{\theta,elastic}$) |
| `elastic_radial_displacement [m]` | m | Radial displacement for purely elastic deformation ($u_{elastic}$) |
| `yielding_pressure [kPa]` | kPa | Internal pressure which initiates yield ($p_{1y}$) |
| `plastic_radius [m]` | m | Radius of the plastic zone for the given internal and external pressures ($c$) |
| `elastoplastic_radii [m]` | m | Radii at which elastoplastic stresses are calculated (equal amount of point inside and outside the plastic radius) |
| `elastoplastic_radial_stress [kPa]` | kPa | Radial stresses for Tresca soil ($\sigma_r$) |
| `elastoplastic_tangential_stress [kPa]` | kPa | Tangential stresses for Tresca soil ($\sigma_{\theta}$) |
| `expanded_radius [m]` | m | Radius of the internal wall after expansion ($a$) |

**References**

- Yu, H.-S., 2000. Cavity Expansion Methods in Geomechanics. Springer-Science+Business Media, B.V.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="expansion_cylinder_tresca"></a>

## `expansion_cylinder_tresca`

<span class="gc-badge gc-available" data-geocore-function="expansion_cylinder_tresca">Available in GeoCore</span> [Pile calculations › Cavity expansion methods › Cylinder Expansion (Tresca)](/docs/geocore/using/modules#expansion_cylinder_tresca)

```python
expansion_cylinder_tresca(
    insitu_pressure,
    borehole_pressure,
    diameter,
    undrained_shear_strength,
    shear_modulus,
    poissons_ratio=0.5,
    max_radius_multiplier=10.0,
    number_radii=250,
    **kwargs,
)
```

Calculates the cavity expansion for a cylinder in Tresca material. The relation between borehole radius + plastic radius and pressure differential is calculated first.

This relation is then used to evaluate where the imposed pressure lies, whether it causes any plasticity around the borehole and whether it does not cause overall borehole failure.

The stresses for the given pressure are then calculated.

$$
\text{Elastic properties}
$$

$$
n = \frac{4 \cdot S_u \cdot (1 - \nu^2) }{E}
$$

$$
E = 2 \cdot G \cdot (1 + \nu)
$$

$$
\text{Plastic radius and wall radius expansion during plastic deformation}
$$

$$
\left( \frac{c}{a} \right)^2 = \left( \frac{a_0}{a} \right)^2 + \frac{1}{n} \cdot \left[ 1 - \left( \frac{a_0}{a} \right)^2 \right]
$$

$$
\frac{p - p_0}{2 \cdot S_u} = \frac{1}{2} + \frac{1}{2} \cdot \ln \left[ \frac{G}{S_u} \cdot \left( 1 - \left( \frac{a_0}{a} \right)^2 \right) + \left( \frac{a_0}{a} \right)^2 \right]
$$

$$
\text{Elastic stresses and displacements can be calculated by taking the limit for the outer radius going to infinity}
$$

$$
\sigma_r = - p_0 - (p - p_0) \cdot \frac{\frac{b_0^2}{r^2} - 1}{\frac{b_0^2}{a_0^2} - 1}  \implies \sigma_r = -p_0 - (p - p_0) \cdot \frac{a_0^2}{r^2}
$$

$$
\sigma_{\theta} = -p_0 + (p - p_0) \cdot \frac{\frac{b_0^2}{r^2} + 1}{\frac{b_0^2}{a_0^2} - 1} \implies \sigma_{\theta} = -p_0 + (p - p_0) \cdot \frac{a_0^2}{r^2}
$$

$$
u = \frac{(1 + \nu) \cdot (p - p_0)}{E} \cdot \frac{a_0^2}{b_0^2 - a_0^2} \cdot \left[ (1 - 2 \cdot \nu) \cdot r + \frac{b_0^2}{r} \right] \implies u = \frac{(1 + \nu) \cdot (p - p_0)}{E} \cdot \frac{a_0^2}{r}
$$

$$
\text{The plasticity critertion can be expressed as:}
$$

$$
\sigma_{r,r=a_0} - \sigma_{theta,r=a_0} = 2 \cdot S_u \implies -(p - p_0)  = S_u
$$

$$
\text{The elastic stresses and displacements outside of the plastic zone can be written as:}
$$

$$
\sigma_r = -\frac{S_u \cdot c^2}{b_0^2} \cdot \left( \frac{b_0^2}{r^2} - 1 \right) - p_0 \implies \sigma_r = -\frac{S_u \cdot c^2}{r^2} - p_0
$$

$$
\sigma_{\theta} = \frac{S_u \cdot c^2}{b_0^2} \cdot \left( \frac{b_0^2}{r^2} + 1 \right) - p_0 \implies \sigma_{\theta} = \frac{S_u \cdot c^2}{r^2} - p_0
$$

$$
u = \frac{(1 + \nu) \cdot S_u \cdot c^2}{E \cdot b_0^2} \cdot \left[ (1 - 2 \cdot \nu) \cdot r + \frac{b_0^2}{r} \right] \implies u = \frac{(1 + \nu) \cdot S_u \cdot c^2}{E} \cdot \frac{1}{r}
$$

$$
\text{Stresses in the plastic zone:}
$$

$$
\sigma_r = -p_0 - S_u - 2 \cdot S_u \cdot \ln \left( \frac{c}{r} \right)
$$

$$
\sigma_{\theta} = -p_0 + S_u - 2 \cdot S_u \cdot \ln \left( \frac{c}{r} \right)
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `insitu_pressure` | kPa | insitu_pressure >= 0.0 | required | Isotropic horizontal stress in the soil mass before borehole excavation ($p_0$) |
| `borehole_pressure` | kPa | borehole_pressure >= 0.0 | required | Pressure on the borehole wall due to drilling fluids or concrete ($p$) |
| `diameter` | m | diameter >= 0.0 | required | Borehole initial diameter (equations are formulated in terms of radius but diameter is more convenient as input) ($2 \cdot a_0$) |
| `undrained_shear_strength` | kPa | undrained_shear_strength >= 0.0 | required | Undrained shear strength of the material surrounding the borehole ($S_u$) |
| `shear_modulus` | kPa | shear_modulus >= 0.0 | required | Shear modulus of the material surrounding the borehole ($G$) |
| `poissons_ratio` | - | 0.0 <= poissons_ratio <= 0.5 | `0.5` | Poissons ratio of the material surrounding the borehole (default for undrained material)) ($\nu$) |
| `max_radius_multiplier` | - | max_radius_multiplier >= 1.0 | `10.0` | Multiplier on borehole radius for determining the maximum extent of the calculation |
| `number_radii` | - |  | `250` | Number of radii considered for the calculation |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `yielding` |  | Boolean determining whether plastic deformation is taking place or not |
| `pressure expansion function` |  | Dictionary with the pressure-expansion relation with keys `expansion [m]` and `pressure difference [kPa]` |
| `yielding pressure [kPa]` | kPa | Borehole pressure at which yield occurs |
| `radii [m]` | m | Numpy array with radii used for the stress and displacement calculation |
| `radial stresses [kPa]` | kPa | Numpy array with the radial stresses around the borehole |
| `tangential stresses [kPa]` | kPa | Numpy array with the tangential stresses around the borehole |
| `elastic wall expansion [m]` | m | Borehole elastic wall expansion |
| `plastic wall expansion [m]` | m | Borehole plastic wall expansion ($a - a_0$) |
| `plastic radius [m]` | m | Radius of the plastic zone ($c$) |

**References**

- Yu, H.-S., 2000. Cavity Expansion Methods in Geomechanics. Springer-Science+Business Media, B.V.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
