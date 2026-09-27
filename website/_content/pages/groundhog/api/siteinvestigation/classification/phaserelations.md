---
title: Phase relations
slug: groundhog/api/siteinvestigation/classification/phaserelations
section: Groundhog API Reference
description: 'API reference for groundhog.siteinvestigation.classification.phaserelations: 14 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/siteinvestigation/classification/phaserelations.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.siteinvestigation.classification.phaserelations
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/site_investigation/phaserelations.html
geocore_available: true
geocore_functions:
- bulkunitweight
- bulkunitweight_dryunitweight
- density_unitweight
- dryunitweight_watercontent
- porosity_voidratio
- relative_density
- saturation_watercontent
- unitweight_density
- unitweight_watercontent_saturated
- voidratio_bulkunitweight
- voidratio_drydensity
- voidratio_porosity
- voidratio_watercontent
- watercontent_voidratio
---

Module `groundhog.siteinvestigation.classification.phaserelations` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/siteinvestigation/classification/phaserelations.py).

Upstream documentation: [Phase relations](https://groundhog.readthedocs.io/en/main/site_investigation/phaserelations.html).

**Functions:** [`voidratio_porosity`](#voidratio_porosity), [`porosity_voidratio`](#porosity_voidratio), [`saturation_watercontent`](#saturation_watercontent), [`bulkunitweight`](#bulkunitweight), [`dryunitweight_watercontent`](#dryunitweight_watercontent), [`voidratio_drydensity`](#voidratio_drydensity), [`bulkunitweight_dryunitweight`](#bulkunitweight_dryunitweight), [`relative_density`](#relative_density), [`voidratio_bulkunitweight`](#voidratio_bulkunitweight), [`unitweight_watercontent_saturated`](#unitweight_watercontent_saturated), [`density_unitweight`](#density_unitweight), [`unitweight_density`](#unitweight_density), [`watercontent_voidratio`](#watercontent_voidratio), [`voidratio_watercontent`](#voidratio_watercontent)

<a id="voidratio_porosity"></a>

## `voidratio_porosity`

<span class="gc-badge gc-available" data-geocore-function="voidratio_porosity">Available in GeoCore</span> [Site investigation › Classification: Phase relations › voidratio_porosity()](/docs/geocore/using/modules#voidratio_porosity)

```python
voidratio_porosity(porosity, **kwargs)
```

Converts a void ratio into a porosity

$$
e = \frac{V_{voids}}{V_{solids}}
$$

$$
n = \frac{V_{voids}}{V_{total}}
$$

$$
e = \frac{n}{1-n}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `porosity` | - | 0.0 <= porosity <= 1.0 | required | Porosity of the sample defined as the ratio of volume of voids to total volume ($n$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `voidratio [-]` | - | Void ratio defined as the ratio of volume of voids to volume of solids ($e$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="porosity_voidratio"></a>

## `porosity_voidratio`

<span class="gc-badge gc-available" data-geocore-function="porosity_voidratio">Available in GeoCore</span> [Site investigation › Classification: Phase relations › porosity_voidratio()](/docs/geocore/using/modules#porosity_voidratio)

```python
porosity_voidratio(voidratio, **kwargs)
```

Calculates the porosity of sample from the void ratio

$$
n = \frac{e}{e+1}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `voidratio` | - | 0.0 <= voidratio <= 5.0 | required | Void ratio defined as the ratio of volume of voids to volume of solids ($e$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `porosity [-]` | - | Porosity defined as the ratio of the volume of voids to the total volume ($n$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="saturation_watercontent"></a>

## `saturation_watercontent`

<span class="gc-badge gc-available" data-geocore-function="saturation_watercontent">Available in GeoCore</span> [Site investigation › Classification: Phase relations › saturation_watercontent()](/docs/geocore/using/modules#saturation_watercontent)

```python
saturation_watercontent(water_content, voidratio, specific_gravity=2.65, **kwargs)
```

Calculates the saturation of a sample from the water content, the specific gravity and the void ratio

$$
S = \frac{V_{water}}{V_{voids}} = \frac{w \cdot G_s}{e}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `water_content` | - | 0.0 <= water_content <= 4.0 | required | Water content of the soil defined as the ratio of weight of water to weight of solids ($w$) |
| `voidratio` | - | 0.0 <= voidratio <= 4.0 | required | Ratio of volume of voids to volume of solids ($e$) |
| `specific_gravity` | - | 1.0 <= specific_gravity <= 3.0 | `2.65` | Specific gravity of the soil grains ($G_s$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `saturation [-]` | - | Saturation of the sample defined as the ratio of volume of water to volume of voids ($S$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="bulkunitweight"></a>

## `bulkunitweight`

<span class="gc-badge gc-available" data-geocore-function="bulkunitweight">Available in GeoCore</span> [Site investigation › Classification: Phase relations › bulkunitweight()](/docs/geocore/using/modules#bulkunitweight)

```python
bulkunitweight(
    saturation,
    voidratio,
    specific_gravity=2.65,
    unitweight_water=10.0,
    **kwargs,
)
```

Calculates the bulk unit weight from specific gravity, void ratio and saturation

$$
\gamma = \frac{W}{V} = \left( \frac{G_s + S \cdot e}{1+e} \right) \cdot \gamma_w
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `saturation` | - | 0.0 <= saturation <= 1.0 | required | Saturation of the sample, ratio of volume of water to volume of voids ($S$) |
| `voidratio` | - | 0.0 <= voidratio <= 4.0 | required | Void ratio, ratio of volume of voids to volume of solids ($e$) |
| `specific_gravity` | - | 1.0 <= specific_gravity <= 3.0 | `2.65` | Specific gravity of solid particles ($G_s$) |
| `unitweight_water` | kN/m3 | 9.0 <= unitweight_water <= 11.0 | `10.0` | Unit weight of water ($\gamma_w$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `bulk unit weight [kN/m3]` | kN/m3 | Bulk unit weight of the material ($\gamma$) |
| `effective unit weight [kN/m3]` | kN/m3 | Effective unit weight of the material ($\gamma^{\prime}$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="dryunitweight_watercontent"></a>

## `dryunitweight_watercontent`

<span class="gc-badge gc-available" data-geocore-function="dryunitweight_watercontent">Available in GeoCore</span> [Site investigation › Classification: Phase relations › dryunitweight_watercontent()](/docs/geocore/using/modules#dryunitweight_watercontent)

```python
dryunitweight_watercontent(watercontent, bulkunitweight, **kwargs)
```

Calculates the dry unit weight of the sample from the water content and the bulk unit weight

$$
\gamma_d = \frac{W_s}{V} = \left( \frac{G_s}{1+e} \right) \cdot \gamma_w = \frac{\gamma}{1 + w}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `watercontent` | - | 0.0 <= watercontent <= 4.0 | required | Water content of the sample, ratio of weight of water to weight of solids ($w$) |
| `bulkunitweight` | kN/m3 | 10.0 <= bulkunitweight <= 25.0 | required | Bulk unit weight of the sample ($\gamma$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `dry unit weight [kN/m3]` | kN/m3 | Dry unit weight, ratio of weight of solids to total volume ($\gamma_d$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="voidratio_drydensity"></a>

## `voidratio_drydensity`

<span class="gc-badge gc-available" data-geocore-function="voidratio_drydensity">Available in GeoCore</span> [Site investigation › Classification: Phase relations › voidratio_drydensity()](/docs/geocore/using/modules#voidratio_drydensity)

```python
voidratio_drydensity(dry_density, specific_gravity=2.65, water_density=1000.0, **kwargs)
```

Calculates void ratio when the specific gravity and the dry density are known

$$
e = G_s \cdot \frac{\rho_w}{\rho_d} - 1
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `dry_density` | kg/m3 | 1000.0 <= dry_density <= 2000.0 | required | Dry density of the sample ($\rho_d$) |
| `specific_gravity` | - | 2.4 <= specific_gravity <= 2.9 | `2.65` | Specific gravity ($G_s$) |
| `water_density` | kg/m3 | 900.0 <= water_density <= 1100.0 | `1000.0` | Density of water ($\rho_w$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Void ratio [-]` | - | Void ratio [-] ($e$) |

**References**

- Budhu (2011) Introduction to soil mechanics and foundations.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="bulkunitweight_dryunitweight"></a>

## `bulkunitweight_dryunitweight`

<span class="gc-badge gc-available" data-geocore-function="bulkunitweight_dryunitweight">Available in GeoCore</span> [Site investigation › Classification: Phase relations › bulkunitweight_dryunitweight()](/docs/geocore/using/modules#bulkunitweight_dryunitweight)

```python
bulkunitweight_dryunitweight(
    dryunitweight,
    watercontent,
    unitweight_water=10.0,
    **kwargs,
)
```

Calculates the bulk unit weight from the dry unit weight and the water content

$$
\gamma = (1+w) \cdot \gamma_d
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `dryunitweight` | kN/m3 | 1.0 <= dryunitweight <= 15.0 | required | Dry unit weight, ratio of weight of solids to total volume ($\gamma_d$) |
| `watercontent` | - | 0.0 <= watercontent <= 4.0 | required | Water content, ratio of weight of water to weight of solids ($w$) |
| `unitweight_water` | kN/m3 | 9.0 <= unitweight_water <= 11.0 | `10.0` | Unit weight of water ($\gamma_w$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `bulk unit weight [kN/m3]` | kN/m3 | Bulk unit weight ($\gamma$) |
| `effective unit weight [kN/m3]` | kN/m3 | Effective unit weight ($\gamma^{\prime}$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="relative_density"></a>

## `relative_density`

<span class="gc-badge gc-available" data-geocore-function="relative_density">Available in GeoCore</span> [Site investigation › Classification: Phase relations › relative_density()](/docs/geocore/using/modules#relative_density)

```python
relative_density(void_ratio, e_min, e_max, **kwargs)
```

Calculates the relative density for a cohesionless sample from the measured void ratio, comparing it to the void ratio at minimum and maximum density.

$$
D_r = \frac{e - e_{min}}{e_{max} - e_{min}}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `void_ratio` | - | 0.0 <= void_ratio <= 5.0 | required | Void ratio of the sample ($e$) |
| `e_min` | - | 0.0 <= e_min <= 5.0 | required | Void ratio at the minimum density ($e_{min}$) |
| `e_max` | - | 0.0 <= e_max <= 5.0 | required | Void ratio at the maximum density ($e_{max}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Dr [-]` | - | Relative density ($D_r$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="voidratio_bulkunitweight"></a>

## `voidratio_bulkunitweight`

<span class="gc-badge gc-available" data-geocore-function="voidratio_bulkunitweight">Available in GeoCore</span> [Site investigation › Classification: Phase relations › voidratio_bulkunitweight()](/docs/geocore/using/modules#voidratio_bulkunitweight)

```python
voidratio_bulkunitweight(
    bulkunitweight,
    saturation=1.0,
    specific_gravity=2.65,
    unitweight_water=10.0,
    **kwargs,
)
```

Calculates the void ratio from the bulk unit weight for a soil with varying saturation.

Since unit weight is generally better known or measured than void ratio, this conversion can be useful to derive the in-situ void ratio in a soil profile.

The default behaviour of this function assumes saturated soil but the saturation can be changed for dry or partially saturated soil.

The water content is also returned.

$$
\gamma = \left( \frac{G_s + S e}{1 + e} \right) \gamma_w
$$

$$
\implies e = \frac{\gamma_w G_s - \gamma}{\gamma - S \gamma_w}
$$

$$
w = \frac{S e}{G_s}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `bulkunitweight` | kN/m3 | 10.0 <= bulkunitweight <= 25.0 | required | The bulk unit weight of the soil (ratio of weight of water and solids to volume) ($\gamma$) |
| `saturation` | - | 0.0 <= saturation <= 1.0 | `1.0` | Saturation of the soil as a number between 0 (dry) and fully saturated (1) ($S$) |
| `specific_gravity` | - | 2.4 <= specific_gravity <= 2.9 | `2.65` | Specific gravity or the ratio of the weight of soil solids to the weight of an equal volume of water ($G_s$) |
| `unitweight_water` | kN/m3 | 9.0 <= unitweight_water <= 11.0 | `10.0` | Unit weight of water ($\gamma_w$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `e [-]` | - | Void ratio of the soil ($e$) |
| `w [-]` | - | Water content of the soil ($w$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="unitweight_watercontent_saturated"></a>

## `unitweight_watercontent_saturated`

<span class="gc-badge gc-available" data-geocore-function="unitweight_watercontent_saturated">Available in GeoCore</span> [Site investigation › Classification: Phase relations › unitweight_watercontent_saturated()](/docs/geocore/using/modules#unitweight_watercontent_saturated)

```python
unitweight_watercontent_saturated(
    water_content,
    specific_gravity=2.65,
    gamma_w=10.0,
    **kwargs,
)
```

Calculates the bulk unit weight from water content for a saturated soil. A specific gravity needs to be assumed or derived from pycnometer test results.

$$
S \cdot e = w \cdot G_s
$$

$$
\gamma = \left( \frac{G_s + S \cdot e}{1 + e} \right) \cdot \gamma_w
$$

$$
\gamma = \left( \frac{G_s \cdot (1 + w)}{1 + w \cdot G_s} \right) \cdot \gamma_w
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `water_content` | - | 0.0 <= water_content <= 2.0 | required | Water content of the sample ($w$) |
| `specific_gravity` | - | 2.5 <= specific_gravity <= 2.8 | `2.65` | Specific gravity of the soil ($G_s$) |
| `gamma_w` | kN/m3 | 9.5 <= gamma_w <= 10.5 | `10.0` | Unit weight of water ($\gamma_w$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `gamma [kN/m3]` | kN/m3 | Bulk unit weight of the saturated sample ($\gamma$) |

**References**

- UGent In-house practice

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="density_unitweight"></a>

## `density_unitweight`

<span class="gc-badge gc-available" data-geocore-function="density_unitweight">Available in GeoCore</span> [Site investigation › Classification: Phase relations › density_unitweight()](/docs/geocore/using/modules#density_unitweight)

```python
density_unitweight(gamma, g=9.81, **kwargs)
```

Converts unit weight (in kN/m3) to density (in kg/m3)

$$
\rho = \frac{\gamma}{g}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `gamma` | kN/m3 | 0.0 <= gamma <= 30.0 | required | Unit weight ($\gamma$) |
| `g` | m/s2 | 9.7 <= g <= 10.0 | `9.81` | Acceleration of gravity ($g$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Density [kg/m3]` | kg/m3 | Density [kg/m3] ($\rho$) |

**References**

- Budhu (2011) Introduction to soil mechanics and foundations.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="unitweight_density"></a>

## `unitweight_density`

<span class="gc-badge gc-available" data-geocore-function="unitweight_density">Available in GeoCore</span> [Site investigation › Classification: Phase relations › unitweight_density()](/docs/geocore/using/modules#unitweight_density)

```python
unitweight_density(density, g=9.81, **kwargs)
```

Converts density (in kg/m3) to unit weight (kN/m3)

$$
\gamma = \rho \cdot g
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `density` | kg/m3 | 0.0 <= density <= 3000.0 | required | Density of the sample ($\rho$) |
| `g` | m/s2 | 9.7 <= g <= 11.0 | `9.81` | Acceleration due to gravity ($g$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Unit weight [kN/m3]` | kN/m3 | Unit weight of the sample [kN/m3] ($\gamma$) |

**References**

- Budhu (2011) Introduction to soil mechanics and foundations.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="watercontent_voidratio"></a>

## `watercontent_voidratio`

<span class="gc-badge gc-available" data-geocore-function="watercontent_voidratio">Available in GeoCore</span> [Site investigation › Classification: Phase relations › watercontent_voidratio()](/docs/geocore/using/modules#watercontent_voidratio)

```python
watercontent_voidratio(voidratio, saturation=1.0, specific_gravity=2.65, **kwargs)
```

Calculates the water content of a sample from it's void ratio. By default, full saturation is assumed.

$$
w = \frac{S \cdot e}{G_s}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `voidratio` | - | voidratio >= 0.0 | required | Void ratio of the sample ($e$) |
| `saturation` | - | 0.0 <= saturation <= 1.0 | `1.0` | Saturation of the sample ($S$) |
| `specific_gravity` | - | 2.4 <= specific_gravity <= 3.0 | `2.65` | Specific gravity ($G_s$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Water content [-]` | - | Water content of the sample [-] ($w$) |
| `Water content [%]` | % | Water content of the sample [%] ($w$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="voidratio_watercontent"></a>

## `voidratio_watercontent`

<span class="gc-badge gc-available" data-geocore-function="voidratio_watercontent">Available in GeoCore</span> [Site investigation › Classification: Phase relations › voidratio_watercontent()](/docs/geocore/using/modules#voidratio_watercontent)

```python
voidratio_watercontent(water_content, saturation=1.0, specific_gravity=2.65, **kwargs)
```

Calculates the void ratio of a sample from the water content. By default, full saturation is assumed but this can be modified

$$
e = \frac{w \cdot G_s}{S}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `water_content` | - | 0.0 <= water_content <= 2.0 | required | Water content of the sample ($w$) |
| `saturation` | - | 0.0 <= saturation <= 1.0 | `1.0` | Saturation of the sample ($S$) |
| `specific_gravity` | - | 2.3 <= specific_gravity <= 3.0 | `2.65` | Specific gravity of the sample ($G_s$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Void ratio [-]` | - | Void ratio of the sample [-] ($e$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
