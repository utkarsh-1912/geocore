---
title: Settlement
slug: groundhog/api/shallowfoundations/settlement
section: Groundhog API Reference
description: 'API reference for groundhog.shallowfoundations.settlement: 3 functions, 1 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/shallowfoundations/settlement.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.shallowfoundations.settlement
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/shallowfoundations/settlement.html
geocore_available: true
geocore_functions:
- consolidationsettlement_mv
- primaryconsolidationsettlement_nc
- primaryconsolidationsettlement_oc
- settlement_calculation
---

Module `groundhog.shallowfoundations.settlement` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/shallowfoundations/settlement.py).

Upstream documentation: [Settlement](https://groundhog.readthedocs.io/en/main/shallowfoundations/settlement.html).

**Classes:** [`SettlementCalculation`](#settlementcalculation)

**Functions:** [`primaryconsolidationsettlement_nc`](#primaryconsolidationsettlement_nc), [`primaryconsolidationsettlement_oc`](#primaryconsolidationsettlement_oc), [`consolidationsettlement_mv`](#consolidationsettlement_mv)

<a id="settlementcalculation"></a>

## class `SettlementCalculation`

<span class="gc-badge gc-available" data-geocore-function="settlement_calculation">Available in GeoCore</span> [Shallow foundations › Settlement › Settlement Calculation (Profile)](/docs/geocore/using/modules#settlement_calculation)

```python
SettlementCalculation(soilprofile)
```

Calculates shallow foundation settlement under a certain distributed load

<a id="settlementcalculation-__init__"></a>

### `SettlementCalculation.__init__`

```python
__init__(soilprofile)
```

Initializes the settlement calculation with a certain `SoilProfile` object. The `SoilProfile` object is checked for the presence of the required columns: (`'Total unit weight [kN/m3]'`, `'Cc [-]'`, `'Cr [-]'`, `'OCR [-]'`). Optionally, a column with the saturation `S [-]` can be defined (ranging from 0 to 1). If a saturation is defined, it will be taken into account for the calculation of the void ratio.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `soilprofile` |  |  | required | No upstream documentation. |

<a id="settlementcalculation-calculate_initial_state"></a>

### `SettlementCalculation.calculate_initial_state`

```python
calculate_initial_state(
    waterlevel,
    specific_gravity=2.65,
    unitweight_water=10.0,
    **kwargs,
)
```

Calculates the initial stress distribution and void ratio. The water level needs to be set for every calculation (z-axis positive downward).

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `waterlevel` |  |  | required | No upstream documentation. |
| `specific_gravity` |  |  | `2.65` | No upstream documentation. |
| `unitweight_water` |  |  | `10.0` | No upstream documentation. |

<a id="settlementcalculation-plot_initial_state"></a>

### `SettlementCalculation.plot_initial_state`

```python
plot_initial_state(
    plot_title='',
    e0_range=(0, 3),
    fillcolordict={'SAND': 'yellow', 'CLAY': 'brown'},
    latex_titles=True,
    **kwargs,
)
```

Plots the initial stress vs depth and the initial void ratio vs depth

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `plot_title` |  |  | `''` | No upstream documentation. |
| `e0_range` |  |  | `(0, 3)` | No upstream documentation. |
| `fillcolordict` |  |  | `{'SAND': 'yellow', 'CLAY': 'brown'}` | No upstream documentation. |
| `latex_titles` |  |  | `True` | No upstream documentation. |

<a id="settlementcalculation-set_foundation"></a>

### `SettlementCalculation.set_foundation`

```python
set_foundation(width, shape='strip', length=nan, skirt_depth=0)
```

Sets the size and shape of the foundation. Length only needs to be defined when `shape='rectangular'`.

TODO: When a skirt depth is defined, the stress increase is transferred to the base of the skirts. Compression of the soil inside the skirt is then not taken into account.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `width` | m |  | required | Width of the foundation (diameter for circular foundations) |
| `shape` |  |  | `'strip'` | Shape of the foundation: `'strip'` (default), `'circular'` or `'rectangular'` |
| `length` |  |  | `nan` | Out-of-plane length (only required for a rectangular foundation) |
| `skirt_depth` | m |  | `0` | Depth of skirts . The skirts are assumed to transfer the load to the base level of the skirts |

<a id="settlementcalculation-create_grid"></a>

### `SettlementCalculation.create_grid`

```python
create_grid(dz=0.5, custom_nodes=None, **kwargs)
```

Creates a grid for calculation

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `dz` |  |  | `0.5` | No upstream documentation. |
| `custom_nodes` |  |  | `None` | No upstream documentation. |

<a id="settlementcalculation-calculate_foundation_stress"></a>

### `SettlementCalculation.calculate_foundation_stress`

```python
calculate_foundation_stress(applied_stress, offset=0, poissonsratio=0.3, **kwargs)
```

Calculates the vertical stress increase below the foundation. By default, the calculation happens below the center of the foundation (`offset=0`). The Boussinesq solution for the selected foundation shape is used.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `applied_stress` |  |  | required | No upstream documentation. |
| `offset` |  |  | `0` | No upstream documentation. |
| `poissonsratio` |  |  | `0.3` | No upstream documentation. |

<a id="settlementcalculation-plot_stress_increase"></a>

### `SettlementCalculation.plot_stress_increase`

```python
plot_stress_increase(
    plot_title='',
    fillcolordict={'SAND': 'yellow', 'CLAY': 'brown'},
    latex_titles=True,
    **kwargs,
)
```

Plots the initial stress vs depth and the stress increase

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `plot_title` |  |  | `''` | No upstream documentation. |
| `fillcolordict` |  |  | `{'SAND': 'yellow', 'CLAY': 'brown'}` | No upstream documentation. |
| `latex_titles` |  |  | `True` | No upstream documentation. |

<a id="settlementcalculation-calculate"></a>

### `SettlementCalculation.calculate`

```python
calculate(**kwargs)
```

Calculates the consolidation settlement using the specified grid, foundation shape and loading

<a id="settlementcalculation-calculate_mv"></a>

### `SettlementCalculation.calculate_mv`

```python
calculate_mv(**kwargs)
```

Calculates the consolidation settlement using the specified grid, foundation shape and loading. Instead of using the compression index and recompression index, the modulus of volumetric compressibility $m_v$ is used.

<a id="settlementcalculation-plot_result"></a>

### `SettlementCalculation.plot_result`

```python
plot_result(
    plot_title='',
    fillcolordict={'SAND': 'yellow', 'CLAY': 'brown'},
    latex_titles=True,
    **kwargs,
)
```

Plots the settlement resulting from the stress increase

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `plot_title` |  |  | `''` | No upstream documentation. |
| `fillcolordict` |  |  | `{'SAND': 'yellow', 'CLAY': 'brown'}` | No upstream documentation. |
| `latex_titles` |  |  | `True` | No upstream documentation. |

<a id="primaryconsolidationsettlement_nc"></a>

## `primaryconsolidationsettlement_nc`

<span class="gc-badge gc-available" data-geocore-function="primaryconsolidationsettlement_nc">Available in GeoCore</span> [Shallow foundations › Settlement › Primary Settlement (NC)](/docs/geocore/using/modules#primaryconsolidationsettlement_nc)

```python
primaryconsolidationsettlement_nc(
    initial_height,
    initial_voidratio,
    initial_effective_stress,
    effective_stress_increase,
    compression_index,
    e_min=0.3,
    **kwargs,
)
```

Calculates the primary consolidation settlement for normally consolidated fine grained soil.

$$
\Delta z = \frac{H_0}{1 + e_0} C_c \log_{10} \frac{\sigma_{v0}^{\prime} + \Delta \sigma_v^{\prime}}{\sigma_{v0}^{\prime}}
$$

$$
\Delta e = C_c \log_{10} \frac{\sigma_{v0}^{\prime} + \Delta \sigma_v^{\prime}}{\sigma_{v0}^{\prime}}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `initial_height` | m | initial_height >= 0.0 | required | Initial thickness of the layer ($H_0$) |
| `initial_voidratio` | - | 0.1 <= initial_voidratio <= 5.0 | required | Initial void ratio of the layer ($e_0$) |
| `initial_effective_stress` | kPa | initial_effective_stress >= 0.0 | required | Initial vertical effective stress in the center of the layer ($\sigma_{v0}^{\prime}$) |
| `effective_stress_increase` | kPa | effective_stress_increase >= 0.0 | required | Increase in vertical effective stress under the given load ($\Delta sigma_{v}^{\prime}$) |
| `compression_index` | - | 0.1 <= compression_index <= 0.8 (derived using logarithm with base 10) | required | Compression index derived from oedometer tests ($C_c$) |
| `e_min` | - | e_min >= 0.1 | `0.3` | Minimum void ratio below which no further consolidation occurs Default=0.3 ($e_{min}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `delta z [m]` | m | Primary consolidation settlement for normally consolidated soil ($\Delta z$) |
| `delta e [-]` | - | Decrease in void ratio for the normally consolidated soil ($\delta e$) |
| `e final [-]` | - | Final void ratio after consolidation ($e_{final}$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="primaryconsolidationsettlement_oc"></a>

## `primaryconsolidationsettlement_oc`

<span class="gc-badge gc-available" data-geocore-function="primaryconsolidationsettlement_oc">Available in GeoCore</span> [Shallow foundations › Settlement › Primary Settlement (OC)](/docs/geocore/using/modules#primaryconsolidationsettlement_oc)

```python
primaryconsolidationsettlement_oc(
    initial_height,
    initial_voidratio,
    initial_effective_stress,
    preconsolidation_pressure,
    effective_stress_increase,
    compression_index,
    recompression_index,
    e_min=0.3,
    **kwargs,
)
```

Calculates the primary consolidation settlement for an overconsolidated clay. This material is characterised using a compression index and a recompression index which can be derived from oedometer tests.

The settlement depends on whether the stress increase loads the layer beyond the preconsolidation pressure. If stresses remain below the preconsolidation pressure, the recompression index applies. If stresses go beyond the preconsolidation pressure, the compression index will apply for the increase beyond the preconsolidation pressure.

Note that a minimum void ratio is set to prevent calculated void ratios from dropping below the minimum.

$$
\Delta z = \frac{H_0}{1 + e_0} C_r \log_{10} \frac{\sigma_{v0}^{\prime} + \Delta \sigma_v^{\prime}}{\sigma_{v0}^{\prime}}; \ \sigma_{v0}^{\prime} + \Delta \sigma_v^{\prime} < p_c^{\prime}
$$

$$
\Delta z = \frac{H_0}{1 + e_0} \left( C_r \log_{10} \frac{p_c^{\prime}}{\sigma_{v0}^{\prime}} + C_c \log_{10} \frac{\sigma_{v0}^{\prime} + \Delta \sigma_v^{\prime}}{p_c^{\prime}} \right); \ \sigma_{v0}^{\prime} + \Delta \sigma_v^{\prime} > p_c^{\prime}
$$

$$
\Delta e = C_r \log_{10} \frac{\sigma_{v0}^{\prime} + \Delta \sigma_v^{\prime}}{\sigma_{v0}^{\prime}}; \ \sigma_{v0}^{\prime} + \Delta \sigma_v^{\prime} < p_c^{\prime}
$$

$$
\Delta e = C_r \log_{10} \frac{p_c^{\prime}}{\sigma_{v0}^{\prime}} + C_c \log_{10} \frac{\sigma_{v0}^{\prime} + \Delta \sigma_v^{\prime}}{p_c^{\prime}} ; \ \sigma_{v0}^{\prime} + \Delta \sigma_v^{\prime} > p_c^{\prime}
$$

![Cases for calculating the primary consolidation settlement](/docs/assets/groundhog/docs/shallowfoundations/images/primaryconsolidation_settlement.png)

*Cases for calculating the primary consolidation settlement*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `initial_height` | m | initial_height >= 0.0 | required | Initial thickness of the layer ($H_0$) |
| `initial_voidratio` | - | 0.1 <= initial_voidratio <= 5.0 | required | Initial void ratio of the layer ($e_0$) |
| `initial_effective_stress` | kPa | initial_effective_stress >= 0.0 | required | Initial vertical effective stress in the center of the layer ($\sigma_{v0)^{\prime}$) |
| `preconsolidation_pressure` | kPa | preconsolidation_pressure >= 0.0 | required | Preconsolidation pressure, maximum vertical stress to which the layer has been subjected ($p_c^{\prime}$) |
| `effective_stress_increase` | kPa | effective_stress_increase >= 0.0 | required | Increase in vertical effective stress under the given load ($\Delta sigma_{v}^{\prime}$) |
| `compression_index` | - | 0.1 <= compression_index <= 0.8 | required | Compression index derived from oedometer tests ($C_c$) |
| `recompression_index` | - | 0.015 <= recompression_index <= 0.35 | required | Recompression index derived from the unloading step in oedometer tests ($C_r$) |
| `e_min` | - | e_min >= 0.1 | `0.3` | Minimum void ratio below which no further consolidation occurs Default=0.3 ($e_{min}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `delta z [m]` | m | Primary consolidation settlement for the overconsolidated soil ($\delta z$) |
| `delta e [-]` | - | Decrease in void ratio for the overconsolidated soil ($\delta e$) |
| `e final [-]` | - | Final void ratio after consolidation ($e_{final}$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="consolidationsettlement_mv"></a>

## `consolidationsettlement_mv`

<span class="gc-badge gc-available" data-geocore-function="consolidationsettlement_mv">Available in GeoCore</span> [Shallow foundations › Settlement › Consolidation Settlement (mv)](/docs/geocore/using/modules#consolidationsettlement_mv)

```python
consolidationsettlement_mv(
    initial_height,
    effective_stress_increase,
    compressibility,
    **kwargs,
)
```

Calculates the consolidation settlement using the compressibility $m_v$ (inverse of constrained modulus $M$).

The constrained modulus is stress-dependent and therefore the relation between $M$ and $C_c$ is also stress-dependent.

$$
\Delta \epsilon = m_v \cdot \Delta \sigma_v^{\prime}
$$

$$
\Delta z = \Delta \epsilon \cdot H_0
$$

$$
m_v = \frac{C_c}{2.3 \cdot (1 + e_0) \cdot \sigma_{v0}^{\prime}}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `initial_height` | m | initial_height >= 0.0 | required | Initial thickness of the layer ($H_0$) |
| `effective_stress_increase` | kPa | effective_stress_increase >= 0.0 | required | Increase in vertical effective stress under the given load ($\Delta sigma_{v}^{\prime}$) |
| `compressibility` | - | 1e-4 <= compressibility <= 10 (note that the compressibility is stress-dependent) | required | Modulus of volumetric compressibility derived from oedometer tests ($m_v$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `delta z [m]` | m | Consolidation settlement ($\Delta z$) |
| `delta epsilon [-]` | - | Change in strain caused by consolidation ($\delta \epsilon$) |

**References**

- Budhu (2011). Soil mechanics and foundation engineering

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
