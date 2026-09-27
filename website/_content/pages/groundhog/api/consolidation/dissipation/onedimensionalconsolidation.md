---
title: One-dimensional consolidation
slug: groundhog/api/consolidation/dissipation/onedimensionalconsolidation
section: Groundhog API Reference
description: 'API reference for groundhog.consolidation.dissipation.onedimensionalconsolidation: 2 functions, 1 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/consolidation/dissipation/onedimensionalconsolidation.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.consolidation.dissipation.onedimensionalconsolidation
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/consolidation/onedimensionalconsolidation.html
geocore_available: true
geocore_functions:
- consolidation_calculation
- consolidation_degree
- pore_pressure_fourier
---

Module `groundhog.consolidation.dissipation.onedimensionalconsolidation` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/consolidation/dissipation/onedimensionalconsolidation.py).

Upstream documentation: [One-dimensional consolidation](https://groundhog.readthedocs.io/en/main/consolidation/onedimensionalconsolidation.html).

**Classes:** [`ConsolidationCalculation`](#consolidationcalculation)

**Functions:** [`pore_pressure_fourier`](#pore_pressure_fourier), [`consolidation_degree`](#consolidation_degree)

<a id="consolidationcalculation"></a>

## class `ConsolidationCalculation`

<span class="gc-badge gc-available" data-geocore-function="consolidation_calculation">Available in GeoCore</span> [Consolidation functions › One-dimensional consolidation › Consolidation Calculation (Numerical)](/docs/geocore/using/modules#consolidation_calculation)

```python
ConsolidationCalculation(height, total_time, no_nodes)
```

The consolidation equation can be discretised as follows:

$$
u_{i,j+1} = u_{i,j} + \frac{c_v \Delta t}{( \Delta z )^2} \left( u_{i-1,j} - 2 u_{i,j} + u_{i+1,j} \right)
$$

At permeable boundaries, the excess pore pressure is 0 ($u = 0$). At impervious boundaries, the following boundary condition applies:

$$
\frac{\partial u}{\partial z} = 0 = \frac{1}{2 \Delta z} \left( u_{i-1,j} - u_{i+1,j} \right) = 0
$$

$$
\implies u_{i,j+1} = u_{i,j} + \frac{c_v \Delta t}{( \Delta z )^2}  \left( 2 u_{i-1,j} - 2 u_{i,j} \right)
$$

To ensure stability, the timestep needs to be chosen according to the following criterion:

$$
\alpha = \frac{c_v \Delta t}{(\Delta z)^2} < \frac{1}{2}
$$

Usually, $\alpha = 0.25$ is used to determine the timestep.

The discretisation in space and time is done as follows where the number of timesteps is usually calculated from a chosen node offset:

$$
\Delta z = \frac{H_0}{m}, \ \Delta t = \frac{t}{n}
$$

<a id="consolidationcalculation-__init__"></a>

### `ConsolidationCalculation.__init__`

```python
__init__(height, total_time, no_nodes)
```

Initialises the consolidation calculation with the height of the layer and the total time. Subdivision of the height in m elements is performed.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `height` |  |  | required | No upstream documentation. |
| `total_time` |  |  | required | No upstream documentation. |
| `no_nodes` |  |  | required | No upstream documentation. |

<a id="consolidationcalculation-set_cv"></a>

### `ConsolidationCalculation.set_cv`

```python
set_cv(cv, uniform=True, cv_depths=None)
```

Sets the coefficient of consolidation. A constant value or an array of cv varying with depth can be specified. cv is specified in m2/yr and is converted to m2/s inside the routine (all calcs happen in s)

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `cv` |  |  | required | No upstream documentation. |
| `uniform` |  |  | `True` | No upstream documentation. |
| `cv_depths` |  |  | `None` | No upstream documentation. |

<a id="consolidationcalculation-set_top_boundary"></a>

### `ConsolidationCalculation.set_top_boundary`

```python
set_top_boundary(freedrainage=True)
```

Sets the boundary condition at the top

Set `freedrainage=False` for an impervious top surface

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `freedrainage` |  |  | `True` | No upstream documentation. |

<a id="consolidationcalculation-set_bottom_boundary"></a>

### `ConsolidationCalculation.set_bottom_boundary`

```python
set_bottom_boundary(freedrainage=True)
```

Sets the boundary condition at the bottom

Set `freedrainage=False` for an impervious top surface

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `freedrainage` |  |  | `True` | No upstream documentation. |

<a id="consolidationcalculation-set_initial"></a>

### `ConsolidationCalculation.set_initial`

```python
set_initial(u0, u0_depths)
```

Sets the initial excess pore pressure distribution

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `u0` |  |  | required | NumPy array with initial excess pore pressure |
| `u0_depths` |  |  | required | NumPy array with the depths corresponding to the defined excess pore pressures |

<a id="consolidationcalculation-set_output_times"></a>

### `ConsolidationCalculation.set_output_times`

```python
set_output_times(output_times)
```

Sets the times at which output is requested. These are pasted into the array with computed times

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `output_times` |  |  | required | No upstream documentation. |

<a id="consolidationcalculation-calculate"></a>

### `ConsolidationCalculation.calculate`

```python
calculate()
```

Calculates the pore pressure dissipation until the specified output time

<a id="consolidationcalculation-plot_results"></a>

### `ConsolidationCalculation.plot_results`

```python
plot_results(
    plot_title='',
    showfig=True,
    xtitle='$ \\Delta u \\ \\text{[kPa]} $',
    ytitle='$ z \\ \\text{[m]} $',
    latex_titles=True,
)
```

No upstream documentation.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `plot_title` |  |  | `''` | No upstream documentation. |
| `showfig` |  |  | `True` | No upstream documentation. |
| `xtitle` |  |  | `'$ \\Delta u \\ \\text{[kPa]} $'` | No upstream documentation. |
| `ytitle` |  |  | `'$ z \\ \\text{[m]} $'` | No upstream documentation. |
| `latex_titles` |  |  | `True` | No upstream documentation. |

<a id="pore_pressure_fourier"></a>

## `pore_pressure_fourier`

<span class="gc-badge gc-available" data-geocore-function="pore_pressure_fourier">Available in GeoCore</span> [Consolidation functions › One-dimensional consolidation › Excess Pore Pressure (Fourier)](/docs/geocore/using/modules#pore_pressure_fourier)

```python
pore_pressure_fourier(delta_u_0, depths, time, cv, layer_thickness, no_terms=1000)
```

The function returns the excess pore pressure distribution at the specified depths for a given time. Note that the Fourier series solution only applies for uniform initial excess pore pressure distributions as commonly observed in thin layers. In thick clay layers, where triangular distributions are more common, this solution does not apply. If the stress distribution is irregular, a numerical solution should be applied.

As an infinite amount of terms cannot be evaluated, the sum is limited to a number of terms (1000 by default) which should be sufficient for convergence.

$$
\Delta u (z,t) = \sum_{m=0}^{\infty} \frac{2 \Delta u_0}{M} \sin \left( \frac{M \cdot z}{H_{dr}} \right) \exp \left( -M^2 T_v \right)
$$

$$
M = \frac{\pi}{2} \left( 2m + 1 \right)
$$

$$
T_v = \frac{c_v t}{H_{dr}^2}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `delta_u_0` | kPa | delta_u_0 >= 0.0 | required | Initial excess pore pressure ($\Delta u_0$) |
| `depths` | m |  | required | Numpy array with the depths for the excess pore pressures ($z$) |
| `time` | s | time >= 0.0 | required | Time at which excess pore pressures are computed ($t$) |
| `cv` | $m^2/yr$ | 0.1 <= cv <= 1000 | required | Coefficient of consolidation ($c_v$) |
| `layer_thickness` | m | layer_thickness >= 0.0 | required | Thickness of the layer considered ($2 \cdot H_{dr}$) |
| `no_terms` | - |  | `1000` | Number of terms for the Fourier series ($m$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `drainage length [m]` | m | Drainage length ($H_{dr}$) |
| `delta u [kPa]` | kPa | Numpy array with the calculated excess pore pressures [kPa] ($\Delta u (z,t)$) |
| `Tv [-]` | - | Time factor ($T_v$) |

**References**

- Budhu (2011). Soil mechanics and foundations. John Wiley and Sons.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="consolidation_degree"></a>

## `consolidation_degree`

<span class="gc-badge gc-available" data-geocore-function="consolidation_degree">Available in GeoCore</span> [Consolidation functions › One-dimensional consolidation › Degree of Consolidation](/docs/geocore/using/modules#consolidation_degree)

```python
consolidation_degree(time, cv, drainage_length, distribution='uniform')
```

Returns the degree of consolidation for a certain time and initial distribution of excess pore pressure.

The average degree of consolidation can be visualised as the area between the initial excess pore pressure distribution and the current isochrone.

The solutions are interpolated from published solutions.

$$
T_v = \frac{c_v t}{H_{dr}^2}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `time` | s | time >= 0.0 | required | Time at which excess pore pressures are computed ($t$) |
| `cv` | $m^2/yr$ | 0.1 <= cv <= 1000 | required | Coefficient of consolidation ($c_v$) |
| `drainage_length` | m | drainage_length >= 0.0 | required | Drainage length ($H_{dr}$) |
| `distribution` |  | one of `uniform`, `triangular` | `'uniform'` | Shape of the initial excess pore pressure distribution. Choose between `"uniform"` (default) and `"triangular"` |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `U [pct]` | pct | Degree of consolidation [%] ($U$) |
| `Tv [-]` | - | Time factor ($T_v$) |

**References**

- Budhu (2011). Soil mechanics and foundations. John Wiley and Sons.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
