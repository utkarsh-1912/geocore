---
title: Shallow foundation capacity
slug: groundhog/api/shallowfoundations/capacity
section: Groundhog API Reference
description: 'API reference for groundhog.shallowfoundations.capacity: 13 functions, 3 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/shallowfoundations/capacity.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.shallowfoundations.capacity
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/shallowfoundations/capacity.html
geocore_available: true
geocore_functions:
- effectivearea_circle_api
- effectivearea_rectangle_api
- envelope_drained_api
- envelope_undrained_api
- failuremechanism_prandtl
- ngamma_frictionangle_davisbooker
- ngamma_frictionangle_meyerhof
- ngamma_frictionangle_vesic
- nq_frictionangle_sand
- shallow_foundation_capacity_drained
- shallow_foundation_capacity_undrained
- slidingcapacity_drained_api
- slidingcapacity_undrained_api
- verticalcapacity_drained_api
- verticalcapacity_undrained_api
---

Module `groundhog.shallowfoundations.capacity` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/shallowfoundations/capacity.py).

Upstream documentation: [Shallow foundation capacity](https://groundhog.readthedocs.io/en/main/shallowfoundations/capacity.html).

**Classes:** [`ShallowFoundationCapacity`](#shallowfoundationcapacity), [`ShallowFoundationCapacityUndrained`](#shallowfoundationcapacityundrained), [`ShallowFoundationCapacityDrained`](#shallowfoundationcapacitydrained)

**Functions:** [`verticalcapacity_undrained_api`](#verticalcapacity_undrained_api), [`verticalcapacity_drained_api`](#verticalcapacity_drained_api), [`slidingcapacity_undrained_api`](#slidingcapacity_undrained_api), [`slidingcapacity_drained_api`](#slidingcapacity_drained_api), [`effectivearea_rectangle_api`](#effectivearea_rectangle_api), [`effectivearea_circle_api`](#effectivearea_circle_api), [`envelope_drained_api`](#envelope_drained_api), [`envelope_undrained_api`](#envelope_undrained_api), [`nq_frictionangle_sand`](#nq_frictionangle_sand), [`ngamma_frictionangle_vesic`](#ngamma_frictionangle_vesic), [`ngamma_frictionangle_meyerhof`](#ngamma_frictionangle_meyerhof), [`ngamma_frictionangle_davisbooker`](#ngamma_frictionangle_davisbooker), [`failuremechanism_prandtl`](#failuremechanism_prandtl)

<a id="shallowfoundationcapacity"></a>

## class `ShallowFoundationCapacity`

```python
ShallowFoundationCapacity(title)
```

<a id="shallowfoundationcapacity-__init__"></a>

### `ShallowFoundationCapacity.__init__`

```python
__init__(title)
```

Generates a ShallowFoundationCapacity object. All shared functionality for drained and undrained analysis is set in this class. The drained and undrained capacity analyses inherit from this class.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `title` |  |  | required | Title for the analysis |

<a id="shallowfoundationcapacity-set_geometry"></a>

### `ShallowFoundationCapacity.set_geometry`

```python
set_geometry(
    option='rectangle',
    length=nan,
    width=nan,
    diameter=nan,
    depth=0,
    skirted=False,
)
```

Sets the geometry of the shallow foundation.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `option` |  |  | `'rectangle'` | Geometrical option. Choose from `'rectangle'` and `'circle'` |
| `length` | m |  | `nan` | Largest foundation dimension, specify for rectangular foundation ($L$) |
| `width` | m |  | `nan` | Shortest foundation dimension, specify for rectangular foundation ($B$) |
| `diameter` | m |  | `nan` | Diameter of the foundation, specify for circular foundation ($2 \ cdot R$) |
| `depth` | m |  | `0` | Depth from the soil surface to the base of the foundation (default=0m) ($D$) |
| `skirted` |  |  | `False` | Boolean determining whether seabed penetrating skirts are used or not (default=False) |

**Returns**

Sets the geometrical properties of the analysis

<a id="shallowfoundationcapacity-set_eccentricity"></a>

### `ShallowFoundationCapacity.set_eccentricity`

```python
set_eccentricity(eccentricity_width, eccentricity_length=nan)
```

When a foundation is loaded out of its center, it will lose some of its bearing capacity. For a rectangular foundation, eccentricity can be measured in the direction of the width ($e_B$) and in the direction of the length ($e_L$). For a circular foundation, only the eccentricty in the direction of the width needs to be specified.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `eccentricity_width` |  |  | required | Eccentricity in width direction for rectangular foundation or eccentricity for a circular foundation |
| `eccentricity_length` |  |  | `nan` | Eccentricity in length direction for rectangular foundation, ignored for circular foundation |

**Returns**

Calculates the effective area of the foundation

<a id="shallowfoundationcapacity-plot_envelope"></a>

### `ShallowFoundationCapacity.plot_envelope`

```python
plot_envelope(
    show_factored=True,
    show_uncorrected=False,
    xaxis_layout=None,
    yaxis_layout=None,
    general_layout=None,
)
```

Plot the bearing capacity envelope using Plotly. This method contains the shared code for drained and undrained bearing capacity envelope plotting.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `show_factored` |  |  | `True` | Boolean determining whether the factored envelope is shown |
| `show_uncorrected` |  |  | `False` | Boolean determining whether the uncorrected envelope is shown |
| `xaxis_layout` |  |  | `None` | Dictionary with custom layout for the X-axis |
| `yaxis_layout` |  |  | `None` | Dictionary with custom layout for the Y-axis |
| `general_layout` |  |  | `None` | Dictionary with custom general layout |
| `showfig` |  |  |  | Boolean determining whether the figure is shown or not |

**Returns**

Returns a Plotly figure with the bearing capacity envelopes

<a id="shallowfoundationcapacityundrained"></a>

## class `ShallowFoundationCapacityUndrained`

<span class="gc-badge gc-available" data-geocore-function="shallow_foundation_capacity_undrained">Available in GeoCore</span> [Shallow foundations › Shallow foundation capacity › Undrained Capacity Analysis](/docs/geocore/using/modules#shallow_foundation_capacity_undrained)

```python
ShallowFoundationCapacityUndrained(...)
```

No upstream documentation.

<a id="shallowfoundationcapacityundrained-set_soilparameters_undrained"></a>

### `ShallowFoundationCapacityUndrained.set_soilparameters_undrained`

```python
set_soilparameters_undrained(unit_weight, su_base, su_increase=0.0, su_above_base=nan)
```

Sets the soil parameters for undrained vertical bearing capacity and horizontal sliding analysis. Note that unit weight is used to assess the stress at base level, so the average unit weight above base level should be used

If the average undrained shear strength above base level is unspecified, the undrained shear strength at base level is used.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `unit_weight` | kN/m3 | 12<=unit_weight<=22 | required | Unit weight of the soil, used to calculate stress at base level ($\gamma$) |
| `su_base` | kPa | 0.0<=su_base | required | Undrained shear strength at foundation base level ($S_{uo}$) |
| `su_increase` | kPa/m | 0.0<=su_increase | `0.0` | Linear increase in undrained shear strength (optional, default=0.0) ($\kappa$) |
| `su_above_base` | kPa | 0.0<=su_above_base | `nan` | Average undrained shear strength above base level (optional, default=np.nan) ($s_{u,ave}$) |

**Returns**

Sets the soil parameters for the analysis

<a id="shallowfoundationcapacityundrained-calculate_bearing_capacity"></a>

### `ShallowFoundationCapacityUndrained.calculate_bearing_capacity`

```python
calculate_bearing_capacity(**kwargs)
```

Calculates the vertical bearing capacity for undrained (short term) conditions

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `kwargs` |  |  |  | Additional arguments for the `verticalcapacity_undrained_api` function (see function documentation) |

**Returns**

`capacity` attribute contains the results of the analysis, `ultimate_capacity` gives the ultimate capacity in kN, `net_bearing_pressure` gives the net ultimate bearing pressure $q_u$ in kPa

<a id="shallowfoundationcapacityundrained-calculate_sliding_capacity"></a>

### `ShallowFoundationCapacityUndrained.calculate_sliding_capacity`

```python
calculate_sliding_capacity(**kwargs)
```

Calculates the sliding capacity for undrained (short term) conditions

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `kwargs` |  |  |  | Additional arguments for the `slidingcapacity_undrained_api` function (see function documentation) |

**Returns**

`sliding` attribute contains the results of the analysis, `sliding_base_only` gives the sliding capacity at the foundation base $H_d$ in kN, `sliding_full` gives the ultimate sliding resistance considering both base sliding and passive resistance $H_d + \Delta H$ in kN

<a id="shallowfoundationcapacityundrained-calculate_envelope"></a>

### `ShallowFoundationCapacityUndrained.calculate_envelope`

```python
calculate_envelope(factor_sliding=1.5, factor_bearing=2, **kwargs)
```

Calculates the bearing capacity envelope for undrained (short term conditions). This envelope describes the interaction between vertical and horizontal load and the resulting VH capacity. The envelope is factored with a factor for vertical bearing capacity (default=2) and a factor for sliding capacity (default=1.5).

This method applied the `envelope_undrained_api` function.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `factor_sliding` |  |  | `1.5` | Safety factor for vertical bearing capacity (default=2) |
| `factor_bearing` |  |  | `2` | Safety factor for sliding capacity (default=1.5) |
| `kwargs` |  |  |  | Optional keyword arguments for the `envelope_undrained_api` function |

**Returns**

Sets a number of attributes

| Key | Unit | Description |
|---|---|---|
| ```envelope_V_unfactored``` |  | V points for the unfactored envelope [kN] |
| ```envelope_H_unfactored``` |  | H points for the unfactored envelope [kN] |
| ```envelope_V_factored``` |  | V points for the factored envelope [kN] |
| ```envelope_H_factored``` |  | H points for the factored envelope [kN] |
| ```envelope_V_uncorrected``` |  | V points for the uncorrected envelope (not accounting for effective area component only) [kN] |
| ```envelope_H_uncorrected``` |  | H points for the uncorrected envelope (not accounting for effective area component only) [kN] |

<a id="shallowfoundationcapacityundrained-plot_envelope"></a>

### `ShallowFoundationCapacityUndrained.plot_envelope`

```python
plot_envelope(showfig=True, plot_title='Undrained bearing capacity envelope', **kwargs)
```

Plot the undrained bearing capacity envelope using Plotly.

Supplements the method from the parent class with specific statements for undrained conditions.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `showfig` |  |  | `True` | No upstream documentation. |
| `plot_title` |  |  | `'Undrained bearing capacity envelope'` | No upstream documentation. |

<a id="shallowfoundationcapacitydrained"></a>

## class `ShallowFoundationCapacityDrained`

<span class="gc-badge gc-available" data-geocore-function="shallow_foundation_capacity_drained">Available in GeoCore</span> [Shallow foundations › Shallow foundation capacity › Drained Capacity Analysis](/docs/geocore/using/modules#shallow_foundation_capacity_drained)

```python
ShallowFoundationCapacityDrained(...)
```

No upstream documentation.

<a id="shallowfoundationcapacitydrained-set_soilparameters_drained"></a>

### `ShallowFoundationCapacityDrained.set_soilparameters_drained`

```python
set_soilparameters_drained(effective_unit_weight, friction_angle, effective_stress_base)
```

Sets the soil parameters for drained vertical bearing capacity and horizontal sliding analysis. Note that effective unit weight is used. Because the vertical effective stress at base level can be different from the virgin effective stress, it is specified directly

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `effective_unit_weight` | kN/m3 | 2<=effective_unit_weight<=12 | required | Effective unit weight of the soil ($\gamma^{\prime}$) |
| `friction_angle` | deg | 20<=friction_angle<=50 | required | Effective friction angle for the soil below foundation base level ($\varphi^{\prime}$) |
| `effective_stress_base` | kPa | 0.0<=effective_stress_base | required | Vertical effective stress at base (or skirt tip) level ($\sigma_{v0}^{\prime}$) |

**Returns**

Sets the soil parameters for the analysis

<a id="shallowfoundationcapacitydrained-calculate_bearing_capacity"></a>

### `ShallowFoundationCapacityDrained.calculate_bearing_capacity`

```python
calculate_bearing_capacity(**kwargs)
```

Calculates the vertical bearing capacity for drained (long term) conditions

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `kwargs` |  |  |  | Additional arguments for the `verticalcapacity_drained_api` function (see function documentation) |

**Returns**

`capacity` attribute contains the results of the analysis, `ultimate_capacity` gives the ultimate capacity in kN, `net_bearing_pressure` gives the net ultimate bearing pressure $q_u$ in kPa

<a id="shallowfoundationcapacitydrained-calculate_sliding_capacity"></a>

### `ShallowFoundationCapacityDrained.calculate_sliding_capacity`

```python
calculate_sliding_capacity(vertical_load, interface_frictionangle=nan, **kwargs)
```

Calculates the sliding capacity for drained (long term) conditions

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `vertical_load` |  |  | required | No upstream documentation. |
| `interface_frictionangle` |  |  | `nan` | No upstream documentation. |
| `kwargs` |  |  |  | Additional arguments for the `slidingcapacity_drained_api` function (see function documentation) |

**Returns**

`sliding` attribute contains the results of the analysis, `sliding_base_only` gives the sliding capacity at the foundation base $H_d$ in kN, `sliding_full` gives the ultimate sliding resistance considering both base sliding and passive resistance $H_d + \Delta H$ in kN

<a id="shallowfoundationcapacitydrained-calculate_envelope"></a>

### `ShallowFoundationCapacityDrained.calculate_envelope`

```python
calculate_envelope(factor_sliding=1.5, factor_bearing=2, **kwargs)
```

Calculates the bearing capacity envelope for drained (long term conditions). This envelope describes the interaction between vertical and horizontal load and the resulting VH capacity. The envelope is factored with a factor for vertical bearing capacity (default=2) and a factor for sliding capacity (default=1.5).

This method applied the `envelope_drained_api` function.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `factor_sliding` |  |  | `1.5` | Safety factor for vertical bearing capacity (default=2) |
| `factor_bearing` |  |  | `2` | Safety factor for sliding capacity (default=1.5) |
| `kwargs` |  |  |  | Optional keyword arguments for the `envelope_undrained_api` function |

**Returns**

Sets a number of attributes

| Key | Unit | Description |
|---|---|---|
| ```envelope_V_unfactored``` |  | V points for the unfactored envelope [kN] |
| ```envelope_H_unfactored``` |  | H points for the unfactored envelope [kN] |
| ```envelope_V_factored``` |  | V points for the factored envelope [kN] |
| ```envelope_H_factored``` |  | H points for the factored envelope [kN] |
| ```envelope_V_uncorrected``` |  | V points for the uncorrected envelope (not accounting for effective area component only) [kN] |
| ```envelope_H_uncorrected``` |  | H points for the uncorrected envelope (not accounting for effective area component only) [kN] |
| ```sliding_cutoff_V``` |  | V points for the sliding cutoff [kN] |
| ```sliding_cutoff_H``` |  | H points for the sliding cutoff [kN] |
| ```sliding_cutoff_V_factored``` |  | V points for the sliding cutoff factored [kN] |
| ```sliding_cutoff_H_factored``` |  | H points for the sliding cutoff factored [kN] |

<a id="shallowfoundationcapacitydrained-plot_envelope"></a>

### `ShallowFoundationCapacityDrained.plot_envelope`

```python
plot_envelope(
    showfig=True,
    show_cutoff=True,
    plot_title='Drained bearing capacity envelope',
    **kwargs,
)
```

Plot the drained bearing capacity envelope using Plotly.

Supplements the method from the parent class with specific statements for undrained conditions.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `showfig` |  |  | `True` | No upstream documentation. |
| `show_cutoff` |  |  | `True` | No upstream documentation. |
| `plot_title` |  |  | `'Drained bearing capacity envelope'` | No upstream documentation. |

<a id="verticalcapacity_undrained_api"></a>

## `verticalcapacity_undrained_api`

<span class="gc-badge gc-available" data-geocore-function="verticalcapacity_undrained_api">Available in GeoCore</span> [Shallow foundations › Shallow foundation capacity › Vertical Capacity (Undrained)](/docs/geocore/using/modules#verticalcapacity_undrained_api)

```python
verticalcapacity_undrained_api(
    effective_length,
    effective_width,
    su_base,
    su_increase=0.0,
    su_above_base=nan,
    base_depth=0.0,
    skirted=True,
    base_sigma_v=0.0,
    roughness=0.67,
    horizontal_load=0.0,
    foundation_inclination=0.0,
    ground_surface_inclination=0.0,
    bearing_capacity_factor=5.14,
    factor_f_override=nan,
    **kwargs,
)
```

Calculates the vertical capacity for a shallow foundation in clay with constant or linearly increasing undrained shear strength according to API RP 2GEO.

The correction factor consists of a shape factor, a depth factor and three inclination factors. In the case of linearly increasing shear strenght, an additional factor F is used which can either be calculated from the foundation roughness (default) or specified directly.

NOTE:  The relevancy of using the depth factor ($d_c$) should be evaluated in each case. If the installation procedure and/or other foundation aspects, such as scour, do not allow for the required mobilization of shear stresses in the soil above foundation base level, it is recommended that ($d_c$) = 0. In particular, it is recommended that ($d_c$) = 0 if the horizontal load leads to mobilization of significant passive earth pressure between seafloor and foundation base level.

NOTE: ($H^{\prime}$) in the equation for inclination factor refers to the load applied to the effective area component of the base only. This corresponds to the total lateral load applied to the foundation minus any soil resistance acting on the foundation above skirt tip level as outlined in A.7.2.1, and minus any lateral resistance that may be carried by shearing at skirt tip level outside the effective area. This value is an input to the function.

NOTE: For embedded foundations, the eccentricity is affected by the load inclination and increases with embedment. The modified eccentricity is found by calculating the intersection between the loading direction and the base depth level.

NOTE: For skirted foundations, a separate assessment is required to check whether the skirt spacing is small enough to rely on the undrained shear strenght at skirt tip level.

NOTE: In the assessment for non-skirted, base embedded foundation, the overburden pressure needs to be included in the vertical capacity assessment

$$
q_u = s_u \cdot N_c \cdot K_c \quad \text{ (constant)}
$$

$$
q_u = F \cdot \left( s_{uo} \cdot N_c + \frac{\kappa \cdot B^{\prime}}{4} \right) \cdot K_c  \quad \text{ (linearly increasing) }
$$

$$
Q_d = (s_u \cdot N_c \cdot K_c + \sigma_{vo}) \cdot A^{\prime} \quad \text{ (constant)}
$$

$$
Q_d = \left[ F \cdot \left( s_{uo} \cdot N_c + \frac{\kappa \cdot B^{\prime}}{4} \right) \cdot K_c + \sigma_{vo} \right] \cdot A^{\prime}  \quad \text{ (linearly increasing) }
$$

$$
\text{Exclude the }  \sigma_{vo} \text{ term for skirted foundations}
$$

$$
K_c = 1 + s_c + d_c  - i_c - b_c - g_c
$$

$$
\text{Correction factors constant undrained shear strength}
$$

$$
s_c = 0.18 \cdot (1 - 2 \cdot i_c) \cdot (B^{\prime} / L^{\prime})
$$

$$
d_c = 0.3 \cdot \arctan ( D / B^{\prime})
$$

$$
i_c = 0.5 - 0.5 \cdot [1 - H^{\prime} / (A^{\prime} \cdot s_u)]^{0.5}
$$

$$
b_c = 2 \cdot \nu / (\pi + 2) \approx 0.4 \cdot \nu
$$

$$
g_c = 2 \cdot \beta / (\pi + 2) \approx 0.4 \cdot \beta
$$

$$
\text{Correction factors linearly increasing undrained shear strength}
$$

$$
F \approx a + b \cdot x - ((c + b \cdot x)^2 + d^2)^{0.5}
$$

$$
x = \frac{\kappa \cdot B^{\prime}}{s_{uo}}
$$

$$
s_c = s_{cv} (1 - 2 \cdot i_c) (B^{\prime} / L^{\prime})
$$

$$
d_c = 0.3 \cdot (s_{u,ave} / s_{u,2}) \cdot \arctan( D / B^{\prime})
$$

$$
s_{u,2} = F \cdot (N_c \cdot s_{uo} + \kappa \cdot B^{\prime} / 4) / N_c
$$

$$
i_c = 0.5 - 0.5 \cdot [1 -H^{\prime}/(A^{\prime} \cdot s_u)]^{0.5}
$$

$$
b_c = 2 \cdot \nu / (\pi + 2) \approx 0.4 \cdot \nu
$$

$$
g_c = 2 \cdot \beta / (\pi + 2) \approx 0.4 \cdot \beta
$$

$$
\text{Correction for horizontal load}
$$

$$
H^{\prime} = H_{total} - H_{d,outside} / \gamma_{sliding} - \Delta H / \gamma_{sliding}
$$

![API correction factors for linear shear strength increase](/docs/assets/groundhog/docs/shallowfoundations/images/api_correction_factor_undrained_linear.png)

*API correction factors for linear shear strength increase*

![API inclination factor definition](/docs/assets/groundhog/docs/shallowfoundations/images/api_inclination_factors.png)

*API inclination factor definition*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `effective_length` | m | 0.0<=effective_length | required | Effective length of the foundation ($L^{\prime}$) |
| `effective_width` | m | 0.0<=effective_width | required | Minimum effective lateral dimension ($B^{\prime}$) |
| `su_base` | kPa | 0.0<=su_base | required | Undrained shear strength at foundation base level ($S_{uo}$) |
| `su_increase` | kPa/m | 0.0<=su_increase | `0.0` | Linear increase in undrained shear strength (optional, default=0.0) ($\kappa$) |
| `su_above_base` | kPa | 0.0<=su_above_base | `nan` | Average undrained shear strength above base level (optional, default=np.nan) ($s_{u,ave}$) |
| `base_depth` | m | 0.0<=base_depth | `0.0` | Depth to the base of the foundation (optional, default=0.0) ($D$) |
| `skirted` |  |  | `True` | Determines whether a foundation is skirted or base-embedded without skirts |
| `base_sigma_v` | kPa | base_sigma_v >= 0.0 | `0.0` | Vertical total stress at base level. Only used for non-skirted base-embedded foundations ($\sigma_{vo}$) |
| `roughness` | - | 0.0<=roughness<=1.0 | `0.67` | Value for roughness (0.0 for fully smooth, 1.0 for fully rough) (optional, default=0.67) ($-$) |
| `horizontal_load` | kN | 0.0<=horizontal_load | `0.0` | Horizontal load acting on effective area of foundation (optional, default=0.0) ($H^{\prime}$) |
| `foundation_inclination` | deg | -90.0<=foundation_inclination<=90.0 | `0.0` | Foundation inclination as defined in figure (optional, default=0.0) ($\nu$) |
| `ground_surface_inclination` | deg | -90.0<=ground_surface_inclination<=90.0 | `0.0` | Ground surface inclination as defined in figure (optional, default=0.0) ($\beta$) |
| `bearing_capacity_factor` | - | 3.0<=bearing_capacity_factor<=12.0 | `5.14` | Bearing capacity factor (optional, default=5.14) ($N_c$) |
| `factor_f_override` | - | 0.0<=factor_f_override<=2.0 | `nan` | Direct specification of the factor F (optional, default=np.nan) ($F$) |

**Returns**

Net bearing pressure ($q_u$) [$kPa$], Vertical capacity ($Q_d$) [$kN$], Combined correction factor ($K_c$) [$-$], Shape factor ($s_c$) [$-$], Depth factor ($d_c$) [$-$], Load inclination factor ($i_c$) [$-$], Foundation inclination factor ($b_c$) [$-$], Ground inclination factor ($g_c$) [$-$], Correction factor for shear strength increase ($F$) [$-$]

Return type: `Python dictionary with keys ['qu [kPa]', 'vertical_capacity [kN]','K_c [-]','s_c [-]','d_c [-]','i_c [-]','b_c [-]','g_c [-]','F [-]']`

**References**

- API RP 2GEO, 2011. API RP 2GEO Geotechnical and Foundation Design Considerations

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="verticalcapacity_drained_api"></a>

## `verticalcapacity_drained_api`

<span class="gc-badge gc-available" data-geocore-function="verticalcapacity_drained_api">Available in GeoCore</span> [Shallow foundations › Shallow foundation capacity › Vertical Capacity (Drained)](/docs/geocore/using/modules#verticalcapacity_drained_api)

```python
verticalcapacity_drained_api(
    vertical_effective_stress,
    effective_friction_angle,
    effective_unit_weight,
    effective_length,
    effective_width,
    base_depth=0.0,
    skirted=True,
    load_inclination=0.0,
    foundation_inclination=0.0,
    ground_surface_inclination=0.0,
    **kwargs,
)
```

Calculates the vertical capacity for a shallow foundation in sand with effective friction angle characterized from drained triaxial tests. For constructing an envelope, this value needs to be multiplied by the tangent of the inclination to obtain the H-coordinate of the envelope point.

The correction factor consists of a shape factor, a depth factor and three inclination factors for both $K_q$ and $K_gamma$.

NOTE: $H/Q$ corresponds to the tangent of the load inclination. For constructing an envelope, load inclinations should be varied from 0.0 to 90.0

NOTE:  The relevancy of using the depth factors should be evaluated in each case. If the installation procedure and/or other foundation aspects, such as scour, do not allow for the required mobilization of shear stresses in the soil above foundation base level, it is recommended that depth factors are set to zero. In particular, it is recommended that d = 0 if the horizontal load leads to mobilization of significant passive earth pressure between seafloor and foundation base level.

NOTE: $H$ in the equation for inclination factor refers to the load applied to the effective area component of the base only. This corresponds to the total lateral load applied to the foundation minus any soil resistance acting on the foundation above skirt tip level as outlined in A.7.2.1, and minus any lateral resistance that may be carried by shearing at skirt tip level outside the effective area.

NOTE: For embedded foundations, the eccentricity is affected by the load inclination and increases with embedment. The modified eccentricity is found by calculating the intersection between the loading direction and the base depth level.

NOTE: For non-skirted, base embedded foundations, the contribution of overburden pressure needs to be taken into account. In the equations in the standard, (Nq - 1) needs to be replaced by Nq

$$
q_u = p_o^{\prime} (N_q - 1) K_q + 0.5 \gamma^{\prime} B^{\prime} N_{\gamma} K_{\gamma}
$$

$$
Q_d^{\prime} = \left[ p_o^{\prime} (N_q - 1) K_q + 0.5 \gamma^{\prime} B^{\prime} N_{\gamma} K_{\gamma} \right] A^{\prime}
$$

$$
\text{Use }  N_q \text{ instead of } (N_q - 1) \text{ for non-skirted, base embedded foundations}
$$

$$
N_q = \exp \left [ \pi \tan \phi^{\prime} \right ] (\tan^2 (45^{\circ} + \phi^{\prime}/2))
$$

$$
N_{\gamma} = 1.5 \left ( N_q - 1 \right) \tan \phi^{\prime}
$$

$$
K_q = i_q \cdot s_q \cdot d_q \cdot b_q \cdot g_q
$$

$$
K_{\gamma} = i_{\gamma} \cdot s_{\gamma} \cdot d_{\gamma} \cdot b_{\gamma} \cdot g_{\gamma}
$$

$$
i_q = \left [ 1 -0.5 (H/Q) \right]^5
$$

$$
i_{\gamma} = \left[ 1-0.7 (H/Q) \right]^5
$$

$$
s_q = 1+i_q ( B^{\prime} / L^{\prime} ) \sin \phi^{\prime}
$$

$$
s_{\gamma} = 1 - 0.4 i_{\gamma} ( B^{\prime} / L^{\prime} )
$$

$$
d_q = 1 + 1.2 (D/B^{\prime}) \tan \phi^{\prime} (1 - \sin \phi^{\prime})^2
$$

$$
d_{\gamma} = 1
$$

$$
b_q = e^{-2 \nu \tan \phi^{\prime}}
$$

$$
b_{\gamma} = e^{-2.7 \nu \tan \phi^{\prime}}
$$

$$
g_q = g_{\gamma} = (1 - 0.5 \tan \beta)^5
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `vertical_effective_stress` | kPa | 0.0<=vertical_effective_stress | required | Vertical effect stress at depth corresponding to foundation base ($p_o^{\prime}$) |
| `effective_friction_angle` | deg | 20.0<=effective_friction_angle<=50.0 | required | Effective friction angle (for appropriate stress level at foundatoin base) ($\phi^{\prime}$) |
| `effective_unit_weight` | kN/m3 | 3.0<=effective_unit_weight<=12.0 | required | Effective unit weight at foundation base ($\gamma^{\prime}$) |
| `effective_length` | m | 0.0<=effective_length | required | Effective length of the footing ($L^{\prime}$) |
| `effective_width` | m | 0.0<=effective_width | required | Minimum effective lateral dimension ($B^{\prime}$) |
| `base_depth` | m | 0.0<=base_depth | `0.0` | Depth of the foundation base (optional, default=0.0) ($D$) |
| `skirted` |  |  | `True` | Determines whether a foundation is skirted or base-embedded without skirts |
| `load_inclination` | deg | 0.0<=load_inclination | `0.0` | Inclination of the load taking into account horizontal load on effective area of base only (optional, default=0.0) ($H^{\prime}$) |
| `foundation_inclination` | deg | -90.0<=foundation_inclination<=90.0 | `0.0` | Foundation inclination as defined in figure (optional, default=0.0) ($\nu$) |
| `ground_surface_inclination` | deg | -90.0<=ground_surface_inclination<=90.0 | `0.0` | Ground surface inclination as defined in figure (optional, default=0.0) ($\beta$) |

**Returns**

Vertical capacity of the footing ($Q_d$) [$kN$], Bearing capacity factor for frictional resistance ($N_q$) [$-$], Bearing capacity factor for unit weight ($N_{\gamma}$) [$-$], Combined correction factor for frictional resistance ($K_q$) [$-$], Combined correction factor for unit weight ($K_{\gamma}$) [$-$], Shape factor frictional ($s_q$) [$-$], Shape factor unit weight ($s_{\gamma}$) [$-$], Depth factor frictional ($d_q$) [$-$], Depth factor unit weight ($d_{\gamma}$) [$-$], Inclination factor frictional ($i_q$) [$-$], Inclination factor unit weight ($i_{\gamma}$) [$-$], Foundation inclination factor frictional ($b_q$) [$-$], Foundation inclination factor unit weight ($b_{\gamma}$) [$-$], Soil surface inclination factor frictional ($g_q$) [$-$], Soil surface inclination factor unit weight ($g_gamma$) [$-$]

Return type: `Python dictionary with keys ['vertical_capacity [kN]','N_q [-]','N_gamma [-]','K_q [-]','K_gamma [-]','s_q [-]','s_gamma [-]','d_q [-]','d_gamma [-]','i_q [-]','i_gamma [-]','b_q [-]','b_gamma [-]','g_q [-]','g_gamma [-]']`

**References**

- API RP 2GEO, 2011. API RP 2GEO Geotechnical and Foundation Design Considerations

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="slidingcapacity_undrained_api"></a>

## `slidingcapacity_undrained_api`

<span class="gc-badge gc-available" data-geocore-function="slidingcapacity_undrained_api">Available in GeoCore</span> [Shallow foundations › Shallow foundation capacity › Sliding Capacity (Undrained)](/docs/geocore/using/modules#slidingcapacity_undrained_api)

```python
slidingcapacity_undrained_api(
    su_base,
    foundation_area,
    su_above_base=0.0,
    embedded_section_area=0.0,
    soil_reaction_coefficient=4.0,
    **kwargs,
)
```

Calculates the undrained sliding capacity for a shallow foundation on clay, the contribution of skirt resistance is taken into account.

$$
H_d = S_{uo} \cdot A
$$

$$
\Delta H = K_{ru} \cdot (S_{u,ave}) \cdot A_h
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `su_base` | kPa | 0.0<=su_base | required | Undrained shear strength at foundation base level ($S_{uo}$) |
| `foundation_area` | m2 | 0.0<=foundation_area | required | Actual foundation area (not the effective area!) ($A$) |
| `su_above_base` | kPa | 0.0<=su_skirts | `0.0` | Average undrained shear strength along the skirt depth (optional, default=0.0) ($S_{u,ave}$) |
| `embedded_section_area` | m2 | 0.0<=embedded_section_area | `0.0` | Embedded vertical cross-sectional area of foundation (optional, default=0.0) ($A_h$) |
| `soil_reaction_coefficient` | - | 1.0<=soil_reaction_coefficient<=6.0 | `4.0` | Soil reaction coefficient Kru. A value of 4 is recommended for full contact. If active soil resistance cannot be relied upon, the factor should be reduced to 2 (optional, default=4.0) ($K_{ru}$) |

**Returns**

Sliding capacity (combined) ($H_d + \Delta H$) [$kN$], Sliding resistance on the foundation base ($H_d$) [$kN$], Sliding resistance due to active and passive resistance of the skirts ($\Delta H$) [$kN$]

Return type: `Python dictionary with keys ['sliding_capacity [kN]','base_resistance [kN]','skirt_resistance [kN]']`

**References**

- API RP 2GEO, 2011. API RP 2GEO Geotechnical and Foundation Design Considerations

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="slidingcapacity_drained_api"></a>

## `slidingcapacity_drained_api`

<span class="gc-badge gc-available" data-geocore-function="slidingcapacity_drained_api">Available in GeoCore</span> [Shallow foundations › Shallow foundation capacity › Sliding Capacity (Drained)](/docs/geocore/using/modules#slidingcapacity_drained_api)

```python
slidingcapacity_drained_api(
    vertical_load,
    effective_friction_angle,
    effective_unit_weight,
    embedded_section_area=0.0,
    depth_to_base=0.0,
    reaction_factor_override=nan,
    **kwargs,
)
```

Calculates the drained sliding capacity for a shallow foundation. The base resistance is increased for passive and active soil resistance derived from skirts.

$$
H_d^{\prime} = Q \cdot \tan \phi^{\prime}
$$

$$
\Delta H = 0.5 \cdot K_{rd} \cdot \gamma^{\prime} \cdot D_b \cdot A_h
$$

$$
K_{rd} = K_p - (1/K_p)
$$

$$
K_p = \tan^2 (45^{\circ} + 0.5 \phi^{\prime})
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `vertical_load` | kN | 0.0<=vertical_load | required | Actual vertical load during relevant loading condition ($Q$) |
| `effective_friction_angle` | deg | 20.0<=effective_friction_angle<=50.0 | required | Effective friction angle (for appropriate stress level at foundation base) ($\phi^{\prime}$) |
| `effective_unit_weight` | kN/m3 | 3.0<=effective_unit_weight<=12.0 | required | Effective unit weight ($\gamma^{\prime}$) |
| `embedded_section_area` | m2 | 0.0<=embedded_section_area | `0.0` | Embedded vertical cross-sectional area of foundation (optional, default=0.0) ($A_h$) |
| `depth_to_base` | m | 0.0<=depth_to_base | `0.0` | Depth below seafloor to base level (optional, default=0.0) ($D_b$) |
| `reaction_factor_override` | - | 0.0<=reaction_factor_override | `nan` | Drained horizontal reaction factor (optional, default=np.nan) ($K_{rd}$) |

**Returns**

Combined sliding capacity due to base and skirt resistance ($H_d + \Delta H$) [$kN$], Sliding resistance due to base friction ($H_d$) [$kN$], Sliding resistance due to active and passive resistance of the skirts ($\Delta H$) [$kN$], Reaction factor ($K_{rd}$) [$-$], Passive resistance factor ($K_p$) [$-$]

Return type: `Python dictionary with keys ['sliding_capacity [kN]','base_capacity [kN]','skirt_capacity [kN]','K_rd [-]','K_p [-]']`

**References**

- API RP 2GEO, 2011. API RP 2GEO Geotechnical and Foundation Design Considerations

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="effectivearea_rectangle_api"></a>

## `effectivearea_rectangle_api`

<span class="gc-badge gc-available" data-geocore-function="effectivearea_rectangle_api">Available in GeoCore</span> [Shallow foundations › Shallow foundation capacity › Effective Area (Rectangular)](/docs/geocore/using/modules#effectivearea_rectangle_api)

```python
effectivearea_rectangle_api(
    length,
    width,
    vertical_load=nan,
    moment_length=nan,
    moment_width=nan,
    eccentricity_length=nan,
    eccentricity_width=nan,
    **kwargs,
)
```

Calculates the reduced area of a rectangular footing to account for eccentricty of the load. Eccentricities can either be specified from a moment or defined directly.

NOTE: In the assessment of eccentricity for shallow foundations on undrained soil, the V can include the weight of soil plug inside the skirts

$$
e_1 = \frac{M_1}{Q}
$$

$$
e_2 = \frac{M_2}{Q}
$$

$$
L^{\prime} = L - 2 \cdot e_1
$$

$$
B^{\prime} = B - 2 \cdot e_2
$$

$$
A^{\prime} = B^{\prime} \cdot L^{\prime}
$$

![Effective area of a rectangular mudmat](/docs/assets/groundhog/docs/shallowfoundations/images/api_reduced_area_rectangle.png)

*Effective area of a rectangular mudmat*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `length` | m | 0.0<=length | required | Longest foundation dimension ($L$) |
| `width` | m | 0.0<=width | required | Shortest foundation dimension ($B$) |
| `vertical_load` | kN | 0.001<=vertical_load | `nan` | Actual vertical load during relevant loading condition (optional, default=np.nan) ($Q$) |
| `moment_length` | kNm | 0.0<=moment_length | `nan` | Overturning moment aligned with longest foundation dimension (optional, default=np.nan) ($M_1$) |
| `moment_width` | kNm | 0.0<=moment_width | `nan` | Overturning moment aligned with shortest foundation dimension (optional, default=np.nan) ($M_2$) |
| `eccentricity_length` | m | 0.0<=eccentricity_length | `nan` | Eccentricity (direct specification) in the longest foundation direction (optional, default=np.nan) ($e_1$) |
| `eccentricity_width` | m | 0.0<=eccentricity_width | `nan` | Eccentricity (direct specification) in the shortest foundation direction (optional, default=np.nan) ($e_2$) |

**Returns**

Effective area used to calculate mudmat capacity ($A^{\prime}$) [$m2$], Effective length ($L^{\prime}$) [$m$], Effective width ($B^{\prime}$) [$m$], Eccentricity in the length direction ($e_1$) [$m$], Eccentricity in the width direction ($e_2$) [$m$]

Return type: `Python dictionary with keys ['effective_area [m2]','effective_length [m]','effective_width [m]','eccentricity_length [m]','eccentricity_width [m]']`

**References**

- API RP 2GEO, 2011. API RP 2GEO Geotechnical and Foundation Design Considerations

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="effectivearea_circle_api"></a>

## `effectivearea_circle_api`

<span class="gc-badge gc-available" data-geocore-function="effectivearea_circle_api">Available in GeoCore</span> [Shallow foundations › Shallow foundation capacity › Effective Area (Circular)](/docs/geocore/using/modules#effectivearea_circle_api)

```python
effectivearea_circle_api(
    foundation_radius,
    vertical_load=nan,
    overturning_moment=nan,
    eccentricity=nan,
    **kwargs,
)
```

Calculates the reduced area for a circular foundation to account for load eccentricity. Eccentricity can either be specified through an overturning moment or with direct specification of eccentricity.

NOTE: In the assessment of eccentricity for shallow foundations on undrained soil, the V can include the weight of soil plug inside the skirts

$$
A^{\prime} = 2s=B^{\prime} L^{\prime}
$$

$$
L^{\prime}=\left( 2s \sqrt{\frac{R+e_2}{R-e_2}} \right)^{1/2}
$$

$$
B^{\prime} = L^{\prime} \sqrt{\frac{R-e_2}{R+e_2}}
$$

$$
s = \frac{\pi R^2}{2}-[e_2 \cdot (\sqrt{R^2-e_2^2}) + R^2 \arcsin(\frac{e_2}{R})]
$$

![Reduced area for a circular foundation](/docs/assets/groundhog/docs/shallowfoundations/images/api_reduced_area_circle.png)

*Reduced area for a circular foundation*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `foundation_radius` | m | 0.01<=foundation_radius | required | Radius of the circular foundation ($R$) |
| `vertical_load` | kN | 0.01<=vertical_load | `nan` | Actual vertical load during relevant loading condition (optional, default=np.nan) ($Q$) |
| `overturning_moment` | kNm | 0.0<=overturning_moment | `nan` | Overturning moment acting on the foundation (optional, default=np.nan) ($M$) |
| `eccentricity` | m | 0.0<=eccentricity | `nan` | Eccentricity (direct specification) (optional, default=np.nan) ($e_2$) |

**Returns**

Effective area used for capacity calculation ($A^{\prime}$) [$m2$], Effective length  ($L^{\prime}$) [$m$], Effective width ($B^{\prime}$) [$m$], Parameter s ($s$) [$m2$], Eccentricity used for the calculation ($e_2$) [$m$]

Return type: `Python dictionary with keys ['effective_area [m2]','effectve length [m]','effective_width [m]','s [m2]','eccentricity [m]']`

**References**

- API RP 2GEO, 2011. API RP 2GEO Geotechnical and Foundation Design Considerations

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="envelope_drained_api"></a>

## `envelope_drained_api`

<span class="gc-badge gc-available" data-geocore-function="envelope_drained_api">Available in GeoCore</span> [Shallow foundations › Shallow foundation capacity › Envelope (Drained)](/docs/geocore/using/modules#envelope_drained_api)

```python
envelope_drained_api(
    vertical_effective_stress,
    effective_friction_angle,
    effective_unit_weight,
    effective_length,
    effective_width,
    full_area,
    factor_sliding=1.5,
    factor_bearing=2.0,
    effective_friction_angle_sliding=nan,
    **kwargs,
)
```

Calculates a drained failure envelope for shallow foundations according to API RP 2GEO. Note that optional keyword arguments can be specified as documented in the function `verticalcapacity_drained_api`.

The envelope is calculated be varying the inclination of the load. Note that the equation for inclination factor will become negative for large inclinations. These values are filtered from the envelope.

We derive the ultimate horizontal load in bearing from the equation for inclination but need to remember that this should only account for the horizontal capacity on the effective area.

A sliding cut-off is also calculated based on the ultimate sliding resistance.

$$
\tan(\text{inclination}) = \frac{H_{eff}}{Q} = \frac{H - H_{\text{outside eff}} - \Delta H}{Q}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `vertical_effective_stress` | kPa | 0.0<=vertical_effective_stress | required | Vertical effect stress at depth corresponding to foundation base ($p_o^{\prime}$) |
| `effective_friction_angle` | deg | 20.0<=effective_friction_angle<=50.0 | required | Effective friction angle for bearing failure (for appropriate stress level at foundation base) ($\phi^{\prime}$) |
| `effective_unit_weight` | kN/m3 | 3.0<=effective_unit_weight<=12.0 | required | Effective unit weight at foundation base ($\gamma^{\prime}$) |
| `effective_length` | m | 0.0<=effective_length | required | Effective length of the footing ($L^{\prime}$) |
| `effective_width` | m | 0.0<=effective_width | required | Minimum effective lateral dimension ($B^{\prime}$) |
| `full_area` | $m^2$ | 0.0<=full_area | required | Full base area of the foundation ($A_b$) |
| `factor_sliding` | - | factor_sliding >= 1.0 | `1.5` | Resistance factor for sliding, applied to the H component of the sliding cutoff ($\gamma_{sliding}$) |
| `factor_bearing` | - | factor_bearing >= 1.0 | `2.0` | Resistance factor for bearing failure, applied to the V component of the envelope ($\gamma_{bearing}$) |
| `effective_friction_angle_sliding` | deg | 15.0<=effective_friction_angle<=45.0 | `nan` | Effective friction angle for sliding failure (for appropriate stress level at foundation base). If unspecified, the effective friction angle of soil - 5° is used ($\delta^{\prime}$) |
| `width` | m | 0.0<=width |  | Minimum true lateral dimension ($B$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Envelope V unfactored [kN]` | kN | Unfactored vertical capacities for the envelope ($V$) |
| `Envelope H unfactored [kN]` | kN | Unfactored horizontal capacities for the envelope ($H^{\prime}$) |
| `Envelope V factored [kN]` | kN | Factored vertical capacities for the envelope ($V / \gamma_v$) |
| `Envelope H factored [kN]` | kN | Factored horizontal capacities for the envelope ($H / \gamma_h$) |
| `Envelope V uncorrected [kN]` | kN | Vertical capacities for the envelope without accounting for effective area component only ($V$) |
| `Envelope H uncorrected [kN]` | kN | Horizontal capacities for the envelope without accounting for effective area component only ($H$) |
| `Sliding cutoff V [kN]` | kN | Vertical capacities for sliding cutoff |
| `Sliding cutoff H [kN]` | kN | Horizontal capacities for sliding cutoff |

**References**

- API RP 2GEO

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="envelope_undrained_api"></a>

## `envelope_undrained_api`

<span class="gc-badge gc-available" data-geocore-function="envelope_undrained_api">Available in GeoCore</span> [Shallow foundations › Shallow foundation capacity › Envelope (Undrained)](/docs/geocore/using/modules#envelope_undrained_api)

```python
envelope_undrained_api(
    su_base,
    full_area,
    effective_length,
    effective_width,
    factor_sliding=1.5,
    factor_bearing=2.0,
    **kwargs,
)
```

Calculates the undrained failure envelope according to API RP 2GEO. It is important to note than only the horizontal load acting on the effective area is taken into account for the envelope. To achieve this, the horizontal load points for the envelope are selected between 0 and the total horizontal capacity (including contributions from skirt resistance and total base area).

Subsequently, a load inclination is calculated using only the effective area component of this horizontal load (subtract skirt resistance and horizontal capacity outside effective area). This inclination is used in the vertical capacity equation (through the inclination factor).

The envelope is calculated twice, first without correction for additional eccentricity at base level and next with a correction for this additional eccentricity. This two step approach is required since the load inclination is not known a priori.

To override the behaviour of the bearing and sliding capacity functions, use the optional keywords arguments defined in the function definitions of `slidingcapacity_undrained_api` and `verticalcapacity_undrained_api`

$$
\Delta e = D \cdot \tan \theta
$$

![Undrained failure envelope](/docs/assets/groundhog/docs/shallowfoundations/images/envelope_undrained_api_1.png)

*Undrained failure envelope*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `su_base` | kPa | 0.0 <= su_base <= 1000.0 | required | Undrained shear strength at the foundation base ($S_{uo}$) |
| `full_area` | $m^2$ | full_area >= 0.0 | required | Total area at the base length ($A_b$) |
| `effective_length` | m | effective_length >= 0.0 | required | Effective length ($L^{\prime}$) |
| `effective_width` | m | effective_width >= 0.0 | required | Effective width ($B^{\prime}$) |
| `factor_sliding` | - | factor_sliding >= 1.0 | `1.5` | Resistance factor for sliding, applied to the H component of the envelope ($\gamma_{sliding}$) |
| `factor_bearing` | - | factor_bearing >= 1.0 | `2.0` | Resistance factor for bearing failure, applied to the V component of the envelope ($\gamma_{bearing}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Envelope V unfactored [kN]` | kN | List with unfactored vertical capacities for the envelope ($V$) |
| `Envelope H unfactored [kN]` | kN | List with unfactored horizontal capacities for the envelope ($H$) |
| `Envelope V factored [kN]` | kN | List with factored vertical capacities for the envelope ($V_{factored}$) |
| `Envelope H factored [kN]` | kN | List with factored horizontal capacities for the envelope ($H_{factored}$) |
| `Envelope V uncorrected [kN]` | kN | List with vertical capacities for the envelope, not corrected for the additional eccentricity ($V_{uncorrected}$) |
| `Envelope H uncorrected [kN]` | kN | List with horizontal capacities for the envelope, not corrected for the additional eccentricity ($H_{uncorrected}$) |
| `Sliding capacity` |  | Dictionary with details for the sliding capacity calculation |
| `Bearing capacity` |  | Dictionary with details for the bearing capacity calculation for purely vertical load |

**References**

- API RP 2GEO, 2011. API RP 2GEO Geotechnical and Foundation Design Considerations

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="nq_frictionangle_sand"></a>

## `nq_frictionangle_sand`

<span class="gc-badge gc-available" data-geocore-function="nq_frictionangle_sand">Available in GeoCore</span> [Shallow foundations › Shallow foundation capacity › N_q (Sand)](/docs/geocore/using/modules#nq_frictionangle_sand)

```python
nq_frictionangle_sand(friction_angle, **kwargs)
```

Calculate the bearing capacity factor Nq from the friction angle

$$
N_q = e^{\pi \tan \phi_p^{\prime}} \tan^2 \left( 45^{\circ} + \frac{ \phi_p^{\prime}}{2} \right)
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `friction_angle` | deg | 20.0 <= friction_angle <= 50.0 | required | Peak effective friction angle ($\phi_p^{\prime}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Nq [-]` | - | Bearing capacity factor ($N_q$) |

**References**

- Budhu (2011) Introduction to soil mechanics and foundations

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="ngamma_frictionangle_vesic"></a>

## `ngamma_frictionangle_vesic`

<span class="gc-badge gc-available" data-geocore-function="ngamma_frictionangle_vesic">Available in GeoCore</span> [Shallow foundations › Shallow foundation capacity › N_gamma (Vesic)](/docs/geocore/using/modules#ngamma_frictionangle_vesic)

```python
ngamma_frictionangle_vesic(friction_angle, **kwargs)
```

Calculates the bearing capacity factor Ngamma according to the equation proposed by Vesic (1973). Note that alternative formulations are available.

$$
N_{\gamma} = 2 (N_q + 1) \tan \phi_p^{\prime}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `friction_angle` | deg | 20.0 <= friction_angle <= 50.0 | required | Peak drained friction angle ($\phi_p^{\prime}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Ngamma [-]` | - | Bearing capacity factor ($N_{\gamma}$) |

**References**

- Budhu (2011) Introduction to soil mechanics and foundations

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="ngamma_frictionangle_meyerhof"></a>

## `ngamma_frictionangle_meyerhof`

<span class="gc-badge gc-available" data-geocore-function="ngamma_frictionangle_meyerhof">Available in GeoCore</span> [Shallow foundations › Shallow foundation capacity › N_gamma (Meyerhof)](/docs/geocore/using/modules#ngamma_frictionangle_meyerhof)

```python
ngamma_frictionangle_meyerhof(friction_angle, frictionangle_multiplier=1.4, **kwargs)
```

Calculates the bearing capacity factor Ngamma according to the equation proposed by Meyerhof (1976). This formulation is more conservative compared to the Vesic formulation.

$$
N_{\gamma} = (N_q - 1) \tan (1.4 \phi_p^{\prime})
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `friction_angle` | deg | 20.0 <= friction_angle <= 50.0 | required | Peak drained friction angle ($\phi_p^{\prime}$) |
| `frictionangle_multiplier` | - |  | `1.4` | Multiplier on the friction angle ($\alpha_1$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Ngamma [-]` | - | Bearing capacity factor ($N_{\gamma}$) |

**References**

- Budhu (2011) Introduction to soil mechanics and foundations

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="ngamma_frictionangle_davisbooker"></a>

## `ngamma_frictionangle_davisbooker`

<span class="gc-badge gc-available" data-geocore-function="ngamma_frictionangle_davisbooker">Available in GeoCore</span> [Shallow foundations › Shallow foundation capacity › N_gamma (Davis & Booker)](/docs/geocore/using/modules#ngamma_frictionangle_davisbooker)

```python
ngamma_frictionangle_davisbooker(
    friction_angle,
    roughness_factor,
    multiplier_smooth=0.0663,
    multiplier_rough=0.1054,
    multiplier_exp_smooth=9.3,
    multiplier_exp_rough=9.6,
    **kwargs,
)
```

Calculates the bearing capacity factor Ngamma according to the equation proposed by Davis and Booker (1971). This formulation is based on a more refined plasticity method and takes the roughness into account. This method is preferred in principle.

$$
N_{\gamma} = \begin{cases}
    0.1054 \exp (9.6 \phi_p^{\prime})       & \quad \text{for rough footings}\\
    0.0663 \exp(9.3 \phi_p^{\prime})  & \quad \text{for smooth footings}
  \end{cases}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `friction_angle` | deg | 20.0 <= friction_angle <= 50.0 | required | Peak drained friction angle ($\phi_p^{\prime}$) |
| `roughness_factor` | - | 0.0 <= roughness_factor <= 1.0 | required | Footing roughness factor where 0 is fully smooth and 1 is fully rough ($R_{inter}$) |
| `multiplier_smooth` | - |  | `0.0663` | Multiplier for smooth footings ($\alpha_1$) |
| `multiplier_rough` | - |  | `0.1054` | Multiplier for rough footings ($\alpha_2$) |
| `multiplier_exp_smooth` | - |  | `9.3` | Multiplier on exponential term for smooth footings ($\alpha_3$) |
| `multiplier_exp_rough` | - |  | `9.6` | Multiplier on exponential term for roughfootings ($\alpha_4$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Ngamma [-]` | - | Bearing capacity factor ($N_{\gamma}$) |
| `Ngamma_smooth [-]` | - | Bearing capacity factor for smooth footing ($N_{\gamma,smooth}$) |
| `Ngamma_rough [-]` | - | Bearing capacity factor for rough footing ($N_{\gamma,rough}$) |

**References**

- Budhu (2011) Introduction to soil mechanics and foundations

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="failuremechanism_prandtl"></a>

## `failuremechanism_prandtl`

<span class="gc-badge gc-available" data-geocore-function="failuremechanism_prandtl">Available in GeoCore</span> [Shallow foundations › Shallow foundation capacity › Failure Mechanism (Prandtl)](/docs/geocore/using/modules#failuremechanism_prandtl)

```python
failuremechanism_prandtl(friction_angle, width, showfig=True, **kwargs)
```

Calculates the shape of the Prandtl failure mechanism for a given friction angle. The failure mechanisms consists of a cone-shaped wedge which is pushed into the soil and a log-spiral extending from the edge of the cone to a line perpendicular to it. Another triangular wedge is formed between the log-spiral and the surface.

This procedure calculates the failure mechanism as a series of (X, Y) points. Only the outer edge for the right-hand side of the figure is taken. The left-hand side can easily be obtained by flipping the figure along the Y-axis.

A Plotly plot with fixed aspect ratio is shown by default but the generation of this plot can be disables using the showfig boolean.

$$
\theta = \frac{\pi}{4} + \frac{\varphi^{\prime}}{2}
$$

$$
r = r_0 \cdot e^{\frac{\pi}{2} \tan \varphi^{\prime}}
$$

![Prandtl failure surface (after Budhu, 2010)](/docs/assets/groundhog/docs/shallowfoundations/images/failuremechanism_prandtl_1.png)

*Prandtl failure surface (after Budhu, 2010)*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `friction_angle` | deg | 0.0 <= friction_angle <= 60.0 | required | Sand angle of internal friction ($\varphi^{\prime}$) |
| `width` | m | width >= 0.0 | required | Width of the footing (full width) ($B$) |
| `showfig` |  |  | `True` | Boolean determining whether the plot of the failure surface is shown |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `X [m]` | m | List with X-coordinates of the points forming the failure surface ($X$) |
| `Y [m]` | m | List with Y-coordinates of the points forming the failure surface ($Y$) |
| `fig` |  | Plotly figure showing the failure surface |

**References**

- Budhu (2010). Soil Mechanics and Foundations

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
