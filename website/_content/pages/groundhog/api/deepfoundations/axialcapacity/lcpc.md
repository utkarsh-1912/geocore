---
title: lcpc
slug: groundhog/api/deepfoundations/axialcapacity/lcpc
section: Groundhog API Reference
description: 'API reference for groundhog.deepfoundations.axialcapacity.lcpc: 0 functions, 1 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/deepfoundations/axialcapacity/lcpc.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.deepfoundations.axialcapacity.lcpc
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/piles/lcpc.html
geocore_available: true
geocore_functions:
- LCPC_Calculation
---

Module `groundhog.deepfoundations.axialcapacity.lcpc` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/deepfoundations/axialcapacity/lcpc.py).

Upstream documentation: [LCPC pile resistance calculations](https://groundhog.readthedocs.io/en/main/piles/lcpc.html).

**Classes:** [`LCPCAxcapCalculation`](#lcpcaxcapcalculation)

<a id="lcpcaxcapcalculation"></a>

## class `LCPCAxcapCalculation`

<span class="gc-badge gc-available" data-geocore-function="LCPC_Calculation">Available in GeoCore</span> [Pile calculations › LCPC pile resistance › LCPC Calculation](/docs/geocore/using/modules#lcpc_calculation)

```python
LCPCAxcapCalculation(depth, qc, diameter_pile, group_base, group_shaft, diameter_shaft=nan)
```

<a id="lcpcaxcapcalculation-__init__"></a>

### `LCPCAxcapCalculation.__init__`

```python
__init__(depth, qc, diameter_pile, group_base, group_shaft, diameter_shaft=nan)
```

Initializes a pile base resistance calculation according to LCPC method Bustamante and Gianeselli (1982). Lists or Numpy arrays of depth and cone resistance need to be supplied to the routine as well as the diameter of the pile.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `depth` | m |  | required | List or Numpy array with depths |
| `qc` | MPa |  | required | List or Numpy array with cone resistance values same list length as depth array |
| `diameter_pile` | m |  | required | Diameter of the pile |
| `group_base` | "IA", "IB", "IIA", "IIB" |  | required | Pile group used for the shaft factors (select from ` `, factors for micropiles IIIa and IIIb are not encoded) |
| `group_shaft` |  |  | required | No upstream documentation. |
| `diameter_shaft` | m |  | `nan` | Diameter of the pile shaft, specify this only if it is different from the base diameter |

<a id="lcpcaxcapcalculation-soiltype_lcpc"></a>

### `LCPCAxcapCalculation.soiltype_lcpc`

```python
soiltype_lcpc(qc, soiltype)
```

No upstream documentation.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc` |  |  | required | No upstream documentation. |
| `soiltype` |  |  | required | No upstream documentation. |

<a id="lcpcaxcapcalculation-set_soil_layers"></a>

### `LCPCAxcapCalculation.set_soil_layers`

```python
set_soil_layers(soilprofile, soiltypecolumn='Soil type', water_level=0, **kwargs)
```

Sets the soil type for the pile resistance calculation. For the shaft resistance calculation, a column `"Soil type"` is required.

The calculation of overburden pressure is included in this routine.

The soil type should be one of the following:

- `'Clay'`
- `'Silt'`
- `'Sand'`
- `'Chalk'`
- `'Gravel'`

The routine checks the cone resistance at a given depth to check for the soil type according to the LCPC method tables.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `soilprofile` |  |  | required | SoilProfile object containing the layer definitions. The SoilProfile should con |
| `soiltypecolumn` |  |  | `'Soil type'` | Name of the column containing the soil type |
| `water_level` | m |  | `0` | Water level used for the effective stress calculation , default = 0 for water level at surface |

<a id="lcpcaxcapcalculation-qca_calculation"></a>

### `LCPCAxcapCalculation.qca_calculation`

```python
qca_calculation()
```

Calculates the depth-averaged cone resistance for the LCPC method.

The average cone resistance in an window 1.5OD above and below the considered is calculated. Points which are higher than 1.3 times the average or lower than 0.7 time the average are left out. The average is recalculated using only the left-over points

![Cone resistance averaging procedure](/docs/assets/groundhog/docs/piles/images/qc_averaging.png)

*Cone resistance averaging procedure*

:returns Stored the average cone resistance for the end bearing calculation in the dataframe with calculation data

<a id="lcpcaxcapcalculation-calculate_base_resistance"></a>

### `LCPCAxcapCalculation.calculate_base_resistance`

```python
calculate_base_resistance()
```

Calculates the base resistance.

$$
q_b = k_c \cdot q_{ca}
$$

$$
Q_b = A_b \cdot q_b
$$

The factors are taken according to the soil and pile type specified.

![Factors on average cone resistance for base resistance calculation.](/docs/assets/groundhog/docs/piles/images/base_factors_LCPC.png)

*Factors on average cone resistance for base resistance calculation.*

**Returns**

Adds columns `"qb [MPa]"` and `"Qb [kN]"` to the dataframe with calculation results.

<a id="lcpcaxcapcalculation-calculate_shaft_resistance"></a>

### `LCPCAxcapCalculation.calculate_shaft_resistance`

```python
calculate_shaft_resistance(careful_execution=False)
```

Calculates the shaft resistance. A Boolean `careful_execution` can be set to `True` to take the factors for careful execution (default=`False`).

The user can enter depth ranges where unit skin friction is ignored.

$$
f_s = \min( f_{s,lim}, \frac{q_c}{\alpha_{\text{LCPC}}})
$$

$$
Q_s = \pi D \int_{0}^{z} f_s(z) dz
$$

The factors are taken according to the soil and pile type specified.

![Factors on cone resistance for shaft resistance calculation.](/docs/assets/groundhog/docs/piles/images/shaft_factors_LCPC.png)

*Factors on cone resistance for shaft resistance calculation.*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `careful_execution` |  |  | `False` | No upstream documentation. |

**Returns**

Adds columns `"fs [kPa]"`, `"Fs [kN/m]"` and `"Qs [kN]"` to the dataframe with calculation results.

<a id="lcpcaxcapcalculation-get_axialpileresistance"></a>

### `LCPCAxcapCalculation.get_axialpileresistance`

```python
get_axialpileresistance(pile_penetration)
```

Returns a dictionary with shaft resistance, base resistance and total resistance at the selected depth.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `pile_penetration` |  |  | required | No upstream documentation. |

<a id="lcpcaxcapcalculation-plot_fs_qb"></a>

### `LCPCAxcapCalculation.plot_fs_qb`

```python
plot_fs_qb(
    return_fig=False,
    plot_height=600,
    plot_width=700,
    fillcolordict={'Sand': 'yellow', 'Clay': 'brown', 'Silt': 'orange', 'Gravel': 'grey', 'Chalk': 'taupe'},
    fs_lim=(0, 150),
    fs_tick=20,
    qb_lim=(0, 30),
    qb_tick=5,
)
```

Plots the profile of unit skin friction and unit end bearing.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `return_fig` |  |  | `False` | No upstream documentation. |
| `plot_height` |  |  | `600` | No upstream documentation. |
| `plot_width` |  |  | `700` | No upstream documentation. |
| `fillcolordict` |  |  | `{'Sand': 'yellow', 'Clay': 'brown', 'Silt': 'orange', 'Gravel': 'grey', 'Chalk': 'taupe'}` | No upstream documentation. |
| `fs_lim` |  |  | `(0, 150)` | No upstream documentation. |
| `fs_tick` |  |  | `20` | No upstream documentation. |
| `qb_lim` |  |  | `(0, 30)` | No upstream documentation. |
| `qb_tick` |  |  | `5` | No upstream documentation. |

<a id="lcpcaxcapcalculation-plot_axcap"></a>

### `LCPCAxcapCalculation.plot_axcap`

```python
plot_axcap(
    return_fig=False,
    plot_height=600,
    plot_width=900,
    fillcolordict={'Sand': 'yellow', 'Clay': 'brown', 'Silt': 'orange', 'Gravel': 'grey', 'Chalk': 'taupe'},
    rs_tick=500,
    rb_tick=500,
    rc_tick=500,
)
```

Plots the result of the axial capacity analysis

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `return_fig` |  |  | `False` | No upstream documentation. |
| `plot_height` |  |  | `600` | No upstream documentation. |
| `plot_width` |  |  | `900` | No upstream documentation. |
| `fillcolordict` |  |  | `{'Sand': 'yellow', 'Clay': 'brown', 'Silt': 'orange', 'Gravel': 'grey', 'Chalk': 'taupe'}` | No upstream documentation. |
| `rs_tick` |  |  | `500` | No upstream documentation. |
| `rb_tick` |  |  | `500` | No upstream documentation. |
| `rc_tick` |  |  | `500` | No upstream documentation. |
