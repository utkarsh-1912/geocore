---
title: axcap
slug: groundhog/api/deepfoundations/axialcapacity/axcap
section: Groundhog API Reference
description: 'API reference for groundhog.deepfoundations.axialcapacity.axcap: 0 functions, 1 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/deepfoundations/axialcapacity/axcap.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.deepfoundations.axialcapacity.axcap
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/piles/axcap.html
geocore_available: true
geocore_functions:
- AxCapCalculation
---

Module `groundhog.deepfoundations.axialcapacity.axcap` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/deepfoundations/axialcapacity/axcap.py).

Upstream documentation: [Axial capacity calculations](https://groundhog.readthedocs.io/en/main/piles/axcap.html).

**Classes:** [`AxCapCalculation`](#axcapcalculation)

<a id="axcapcalculation"></a>

## class `AxCapCalculation`

<span class="gc-badge gc-available" data-geocore-function="AxCapCalculation">Available in GeoCore</span> [Pile calculations › Axial capacity calculations › Axial Capacity (AxCap)](/docs/geocore/using/modules#axcapcalculation)

```python
AxCapCalculation(soilprofile)
```

<a id="axcapcalculation-__init__"></a>

### `AxCapCalculation.__init__`

```python
__init__(soilprofile)
```

Sets up an axial capacity calculation by taking in a `SoilProfile` object. The `SoilProfile` object needs to have the columns `Unit skin friction` and `Unit end bearing` specified.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `soilprofile` |  |  | required | No upstream documentation. |

<a id="axcapcalculation-check_methods"></a>

### `AxCapCalculation.check_methods`

```python
check_methods(raise_errors=False)
```

Checks the given `SoilProfile` object for the presence of the required soil parameters. Errors are printed by default but error raising can also be requested by setting `raise_errors=True`

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `raise_errors` |  |  | `False` | No upstream documentation. |

<a id="axcapcalculation-create_grid"></a>

### `AxCapCalculation.create_grid`

```python
create_grid(dz=1, **kwargs)
```

Sets the `CalculationGrid` for the pile capacity calculation.

A default node spacing of 1m is used but finer or coarser grids can be specified with the argument `dz`. Layer transitions not coinciding with the grid nodes are added as additional nodes by default.

For additional options (`**kwargs`), check the documentation of `CalculationGrid`

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `dz` |  |  | `1` | No upstream documentation. |

<a id="axcapcalculation-set_pilepenetration"></a>

### `AxCapCalculation.set_pilepenetration`

```python
set_pilepenetration(pile_penetration)
```

Sets a certain pile penetration for calculation. A deep copy of the `grid.elements` attribute is created, `output` which can be used for further calculation.

The pile penetration is checked (needs to be above the maximum depth of the `SoilProfile`)

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `pile_penetration` |  |  | required | Pile penetration below surface in meters |

**Returns**

Sets the `output` attribute, a deep copy of the `grid.elements` attribute between surface (0m) and the selected pile penetration

<a id="axcapcalculation-calculate_unitskinfriction"></a>

### `AxCapCalculation.calculate_unitskinfriction`

```python
calculate_unitskinfriction(**kwargs)
```

Calculates unit skin friction for the selected method and soil parameters. Note that not all parameter combinations will return valid outputs. Therefore a check is performed to see if the output contains NaN values.

The unit skin friction in compression and tension on the outside and inside (for tubulars) is returned in the `grid.elements` dataframe. The unit skin friction method used determines whether there are differences in these values.

<a id="axcapcalculation-calculate_unitendbearing"></a>

### `AxCapCalculation.calculate_unitendbearing`

```python
calculate_unitendbearing(**kwargs)
```

Calculates unit end bearing for the selected method and soil parameters. Note that not all parameter combinations will return valid outputs. Therefore a check is performed to see if the output contains NaN values.

The unit end bearing for plugged and coring conditions is returned in the `grid.elements` dataframe. The unit end bearing method used determines whether there are differences in these values.

<a id="axcapcalculation-calculate_pilecapacity"></a>

### `AxCapCalculation.calculate_pilecapacity`

```python
calculate_pilecapacity(
    circumference,
    base_area,
    internal_circumference=nan,
    annulus_area=nan,
    pile_weight=0,
    soilplug_weight=0,
)
```

Calculates the shaft friction of the pile by summing the unit shaft friction over all pile elements.

The shaft friction can be calculated for the following modes:

- Plugged compression (`plugged=True` and `compression=True`, default): Outside skin friction and end bearing over the full base area of the pile
- Plugged tension (`plugged=True` and `compression=False`): Outside skin friction in tension + weight of the pile material and/or internal soil plug
- Coring compression (`plugged=False` and `compression=True`): Outside skin friction + inside skin friction + annular end bearing.
- Coring tension: (`plugged=False` and `compression=False`) Outside skin friction in tension + inside skin friction in tension.

The pile circumference and base cross-sectional area need to be known. For coring conditions, the argument `internal_circumference` needs to be specified. For plugged conditions `base_area` is the full end area, for coring conditions, `annulus_area` is the steel annulus area.

Because pile shapes and sizes may differ, the weight of the pile and/or internal soil plug is not calculated automatically but needs to be specified as `pile_weight` and `soilplug_weight`. Calculating these components with a separate calculation is straightforward.

The total capacity for plugged and coring conditions is calculated. A simple plugging criterion is also included, which for compression assesses whether the end bearing on the internal pile area is greater than the inside shaft friction. If the shaft friction is greater than the internal end bearing, the pile should behave plugged. For tension, plugging is expected to occur when the internal shaft friction is greater than the soil plug weight.

$$
F_{s,outside} = \sum f_{s,out,i} \cdot \chi_{outside} \cdot \Delta z \\ \text{for compression and tension}
$$

$$
F_{s,inside} = \sum f_{s,in,i} \cdot \chi_{inside} \cdot \Delta z \\ \text{for compression and tension}
$$

$$
Q_{b,plugged} = A_{base,full} \cdot q_{b,plugged,base}
$$

$$
Q_{b,coring} = A_{base,annulus} \cdot q_{b,coring,base}
$$

$$
R_{plugged,compression} = F_{s,outside,compression} + Q_{b,plugged}
$$

$$
R_{coring,compression} = F_{s,outside,compression} + F_{s,inside,compression} + Q_{b,coring}
$$

$$
R_{plugged,tension} = F_{s,outside,tension} + W_{pile} + W_{\text{soil plug}}
$$

$$
R_{coring,tension} = F_{s,outside, tension} + F_{s,inside,tension}
$$

The columns `'Fs compression outside [kN]', 'Fs compression inside [kN]', 'Fs tension outside [kN]', 'Fs tension inside [kN]', 'Qb plugged [kN]', 'Qb coring'` are added to the `output` attribute. `'Fs compression outside [kN]'`, `'Fs compression inside [kN]'`, `'Fs tension outside [kN]'` and `'Fs tension inside [kN]'` are cumulative sums. `'Qb plugged [kN]'` and `'Qb coring'` are multiplied by the local value.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `circumference` | m |  | required | Pile circumference . |
| `base_area` | m2 |  | required | Pile base area . Full end area used for plugged conditions. |
| `internal_circumference` |  |  | `nan` | Internal pile circumference used when `plugged=False` |
| `annulus_area` | m2 |  | `nan` | Pile annular base area . Use annulus area for coring conditions. |
| `pile_weight` | kN |  | `0` | Pile weight in used for plugged tension capacity (default = 0kN) |
| `soilplug_weight` | kN |  | `0` | Soil plug weight in used for the plugged tension capacity (default = 0kN) |

<a id="axcapcalculation-calculate_capacity_profile"></a>

### `AxCapCalculation.calculate_capacity_profile`

```python
calculate_capacity_profile(
    circumference,
    base_area,
    internal_circumference=nan,
    annulus_area=nan,
    pile_weight_permeter=0,
    soilplug_weight_permeter=0,
)
```

Calculates compression and tension capacity vs pile penetration. Due to the possible dependence of unit skin friction and unit end bearing on pile penetration (e.g. friction fatigue effects), The pile capacity profile is calculated for every nodal position (except 0m) and stored in a dataframe.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `circumference` | m |  | required | Pile circumference . |
| `base_area` | m2 |  | required | Pile base area . Full end area used for plugged conditions. |
| `internal_circumference` |  |  | `nan` | Internal pile circumference used when `plugged=False` |
| `annulus_area` | m2 |  | `nan` | Pile annular base area . Use annulus area for coring conditions. |
| `pile_weight_permeter` | kN/m |  | `0` | Pile weight in used for plugged tension capacity (default = 0kN/m). This value is multiplied by the actual pile penetration to obtain the total pile weight at the considered penetration. |
| `soilplug_weight_permeter` | kN/m |  | `0` | Soil plug weight in used for the plugged tension capacity (default = 0kN/m). This value is multiplied by the actual pile penetration to obtain the total soil plug weight at the considered penetration. |

<a id="axcapcalculation-plot_single_penetration"></a>

### `AxCapCalculation.plot_single_penetration`

```python
plot_single_penetration(
    return_fig=False,
    plot_title=None,
    fillcolordict={'SAND': 'yellow', 'CLAY': 'brown'},
    latex_titles=True,
)
```

Plots unit skin friction, unit end bearing, the integration of unit skin friction over the shaft and the value of end bearing at the tip

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `return_fig` |  |  | `False` | No upstream documentation. |
| `plot_title` |  |  | `None` | No upstream documentation. |
| `fillcolordict` |  |  | `{'SAND': 'yellow', 'CLAY': 'brown'}` | No upstream documentation. |
| `latex_titles` |  |  | `True` | No upstream documentation. |

<a id="axcapcalculation-plot_all_penetrations"></a>

### `AxCapCalculation.plot_all_penetrations`

```python
plot_all_penetrations(
    return_fig=False,
    plot_title=None,
    fillcolordict={'SAND': 'yellow', 'CLAY': 'brown'},
    latex_titles=True,
)
```

Plots shaft resistance, tip resistance and total pile resistance for all pile penetrations.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `return_fig` |  |  | `False` | No upstream documentation. |
| `plot_title` |  |  | `None` | No upstream documentation. |
| `fillcolordict` |  |  | `{'SAND': 'yellow', 'CLAY': 'brown'}` | No upstream documentation. |
| `latex_titles` |  |  | `True` | No upstream documentation. |
