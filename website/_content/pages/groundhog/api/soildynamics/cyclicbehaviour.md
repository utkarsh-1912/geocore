---
title: Cyclic behaviour
slug: groundhog/api/soildynamics/cyclicbehaviour
section: Groundhog API Reference
description: 'API reference for groundhog.soildynamics.cyclicbehaviour: 17 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/soildynamics/cyclicbehaviour.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.soildynamics.cyclicbehaviour
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/soildynamics/cyclicbehaviour.html
geocore_available: true
geocore_functions:
- cycliccontours_dssclay_andersen
- cycliccontours_triaxialclay_andersen
- cyclicstrength_dsssand_relativedensity
- cyclicstrength_dsssand_watercontent
- plotcycliccontours_dssclay_andersen
- plotcycliccontours_triaxialclay_andersen
- plotporepressureaccumulation_dssclay_andersen
- plotporepressureaccumulation_dsssand_andersen
- plotporepressureaccumulation_triaxialclay_andersen
- plotstrainaccumulation_dssclay_andersen
- plotstrainaccumulation_dsssand_andersen
- plotstrainaccumulation_triaxialclay_andersen
- porepressureaccumulation_dssclay_andersen
- porepressureaccumulation_triaxialclay_andersen
- strainaccumulation_dssclay_andersen
- strainaccumulation_dsssand_andersen
- strainaccumulation_triaxialclay_andersen
---

Module `groundhog.soildynamics.cyclicbehaviour` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/soildynamics/cyclicbehaviour.py).

Upstream documentation: [Cyclic behaviour](https://groundhog.readthedocs.io/en/main/soildynamics/cyclicbehaviour.html).

**Functions:** [`cycliccontours_dssclay_andersen`](#cycliccontours_dssclay_andersen), [`plotcycliccontours_dssclay_andersen`](#plotcycliccontours_dssclay_andersen), [`cycliccontours_triaxialclay_andersen`](#cycliccontours_triaxialclay_andersen), [`plotcycliccontours_triaxialclay_andersen`](#plotcycliccontours_triaxialclay_andersen), [`strainaccumulation_dssclay_andersen`](#strainaccumulation_dssclay_andersen), [`plotstrainaccumulation_dssclay_andersen`](#plotstrainaccumulation_dssclay_andersen), [`strainaccumulation_triaxialclay_andersen`](#strainaccumulation_triaxialclay_andersen), [`plotstrainaccumulation_triaxialclay_andersen`](#plotstrainaccumulation_triaxialclay_andersen), [`porepressureaccumulation_dssclay_andersen`](#porepressureaccumulation_dssclay_andersen), [`plotporepressureaccumulation_dssclay_andersen`](#plotporepressureaccumulation_dssclay_andersen), [`porepressureaccumulation_triaxialclay_andersen`](#porepressureaccumulation_triaxialclay_andersen), [`plotporepressureaccumulation_triaxialclay_andersen`](#plotporepressureaccumulation_triaxialclay_andersen), [`strainaccumulation_dsssand_andersen`](#strainaccumulation_dsssand_andersen), [`plotstrainaccumulation_dsssand_andersen`](#plotstrainaccumulation_dsssand_andersen), [`plotporepressureaccumulation_dsssand_andersen`](#plotporepressureaccumulation_dsssand_andersen), [`cyclicstrength_dsssand_relativedensity`](#cyclicstrength_dsssand_relativedensity), [`cyclicstrength_dsssand_watercontent`](#cyclicstrength_dsssand_watercontent)

<a id="cycliccontours_dssclay_andersen"></a>

## `cycliccontours_dssclay_andersen`

<span class="gc-badge gc-available" data-geocore-function="cycliccontours_dssclay_andersen">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › AC Cyclic Contours (DSS Clay)](/docs/geocore/using/modules#cycliccontours_dssclay_andersen)

```python
cycliccontours_dssclay_andersen(
    undrained_shear_strength,
    average_shear_stress,
    cyclic_shear_stress,
    **kwargs,
)
```

Calculates the number of cycles to failure for a cyclic DSS test with  a given combination of average and cyclic shear stress for a sample with a given undrained shear strength. Cyclic failure is defined as reaching a cyclic or average shear strain of 15%. Contours for N=10, N=100 and N=1000 are defined. Logarithmic interpolation is used between the contours. Three points are extracted from the digitised graphs and a logarithmic relation is fitted. If the number of cycles to failure is lower than 10 or greater than 1000, extrapolation is used but a warning is raised to the user.

The data used for this interaction diagram originates from cyclic tests on normally consolidated Drammen clay, a marine clay with a plasticity index of 27%. Average cyclic stresses were applied for 1 to 2hrs before starting the cyclic shearing and the cyclic loading period was 10s.

![Contour diagram for DSS tests on normally consolidated Drammen clay](/docs/assets/groundhog/docs/soildynamics/images/cycliccontours_dssclay_andersen_1.png)

*Contour diagram for DSS tests on normally consolidated Drammen clay*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `undrained_shear_strength` | kPa | 1.0 <= undrained_shear_strength <= 100.0 | required | Undrained shear strength of the normally consolidated clay measured with a DSS test ($S_u^{DSS}$) |
| `average_shear_stress` | kPa | 0.0 <= average_shear_stress <= 100.0 | required | Magnitude of the applied average shear stress ($\tau_a$) |
| `cyclic_shear_stress` | kPa | 0.0 <= cyclic_shear_stress <= 100.0 | required | Magnitude of the applied cyclic shear stress ($\tau_{cy}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Nf [-]` | - | Number of cycles to failure ($N_f$) |

**References**

- Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="plotcycliccontours_dssclay_andersen"></a>

## `plotcycliccontours_dssclay_andersen`

<span class="gc-badge gc-available" data-geocore-function="plotcycliccontours_dssclay_andersen">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › Plot Cyclic Contours (DSS Clay)](/docs/geocore/using/modules#plotcycliccontours_dssclay_andersen)

```python
plotcycliccontours_dssclay_andersen()
```

Returns a Plotly figure with the cyclic contours for DSS tests on normally consolidated Drammen clay

**Returns**

Plotly figure object which can be further customised and to which test data can be added.

<a id="cycliccontours_triaxialclay_andersen"></a>

## `cycliccontours_triaxialclay_andersen`

<span class="gc-badge gc-available" data-geocore-function="cycliccontours_triaxialclay_andersen">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › AC Cyclic Contours (Triaxial Clay)](/docs/geocore/using/modules#cycliccontours_triaxialclay_andersen)

```python
cycliccontours_triaxialclay_andersen(
    undrained_shear_strength,
    average_shear_stress,
    cyclic_shear_stress,
    **kwargs,
)
```

Calculates the number of cycles to failure for cyclic triaxial test with a given combination of average and cyclic shear stress for a sample with a given undrained shear strength. Cyclic failure is defined as reaching a cyclic or average shear strain of 15%. Contours for N=10, N=100 and N=1000 are defined. Logarithmic interpolation is used between the contours. Three points are extracted from the digitised graphs and a logarithmic relation is fitted. If the number of cycles to failure is lower than 10 or greater than 1000, extrapolation is used but a warning is raised to the user.

The data used for this interaction diagram originates from cyclic tests on normally consolidated Drammen clay, a marine clay with a plasticity index of 27%. Average cyclic stresses were applied for 1 to 2hrs before starting the cyclic shearing and the cyclic loading period was 10s.

![Contour diagram for cyclic triaxial tests on normally consolidated Drammen clay](/docs/assets/groundhog/docs/soildynamics/images/cycliccontours_triaxialclay_andersen_1.png)

*Contour diagram for cyclic triaxial tests on normally consolidated Drammen clay*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `undrained_shear_strength` | kPa | 1.0 <= undrained_shear_strength <= 100.0 | required | Undrained shear strength of the normally consolidated clay measured with a triaxial compression test ($S_u^C$) |
| `average_shear_stress` | kPa | -50.0 <= average_shear_stress <= 100.0 | required | Magnitude of the applied average shear stress ($\tau_a$) |
| `cyclic_shear_stress` | kPa | 0.0 <= cyclic_shear_stress <= 100.0 | required | Magnitude of the applied cyclic shear stress ($\tau_{cy}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Nf [-]` | - | Number of cycles to failure ($N_f$) |
| `tau_cy / Su_C [-]` | - | Ratios of cyclic shear stress to the compressive undrained shear strength used in interpolation |
| `Nf interpolated [-]` | - | Number of cycles to failure used in the interpolation |

**References**

- Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="plotcycliccontours_triaxialclay_andersen"></a>

## `plotcycliccontours_triaxialclay_andersen`

<span class="gc-badge gc-available" data-geocore-function="plotcycliccontours_triaxialclay_andersen">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › Plot Cyclic Contours (Triaxial Clay)](/docs/geocore/using/modules#plotcycliccontours_triaxialclay_andersen)

```python
plotcycliccontours_triaxialclay_andersen()
```

Returns a Plotly figure with the cyclic contours for triaxial tests on normally consolidated Drammen clay

**Returns**

Plotly figure object which can be further customised and to which test data can be added.

<a id="strainaccumulation_dssclay_andersen"></a>

## `strainaccumulation_dssclay_andersen`

<span class="gc-badge gc-available" data-geocore-function="strainaccumulation_dssclay_andersen">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › Strain Accum. (DSS Clay)](/docs/geocore/using/modules#strainaccumulation_dssclay_andersen)

```python
strainaccumulation_dssclay_andersen(
    cyclic_shear_stress,
    undrained_shear_strength,
    cycle_no,
    **kwargs,
)
```

Calculates the strain accumulation for a normally consolidated clay sample under symmetrical cyclic loading (no average shear stress) in a DSS test. The contours are based on cyclic DSS tests on Drammen clay.

Strain contours for cyclic shear strains of 0.5, 1, 3 and 15% are defined and logarithmic interpolation is used to obtain the accumulated strain for a sample tested at a certain ratio of cyclic shear stress to DSS shear strength with a given number of cycles.

![Strain contours for symmetrical cyclic DSS tests](/docs/assets/groundhog/docs/soildynamics/images/strainaccumulation_dssclay_andersen_1.png)

*Strain contours for symmetrical cyclic DSS tests*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `cyclic_shear_stress` | kPa | 0.0 <= cyclic_shear_stress <= 100.0 | required | Magnitude of the applied cyclic shear stress ($\tau_{cy}$) |
| `undrained_shear_strength` | kPa | 1.0 <= undrained_shear_strength <= 100.0 | required | Undrained shear strength of the normally consolidated clay measured with a DSS test ($S_u^{DSS}$) |
| `cycle_no` | - | 1.0 <= cycle_no <= 1500.0 | required | Number of applied cycles ($N$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `cyclic strain [%]` | % | Accumulated cyclic shear strain ($\gamma_{cy}$) |
| `shear strains interpolation [%]` | % | List of shear strains used for interpolation |
| `shearstress ratios interpolation [-]` | - | List of ratios of cyclic shear stress to undrained DSS shear strength used for interpolation |

**References**

- Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="plotstrainaccumulation_dssclay_andersen"></a>

## `plotstrainaccumulation_dssclay_andersen`

<span class="gc-badge gc-available" data-geocore-function="plotstrainaccumulation_dssclay_andersen">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › Plot Strain Accum. (DSS Clay)](/docs/geocore/using/modules#plotstrainaccumulation_dssclay_andersen)

```python
plotstrainaccumulation_dssclay_andersen()
```

Returns a Plotly figure with the strain accumulation contours for DSS tests on normally consolidated Drammen clay

**Returns**

Plotly figure object which can be further customised and to which test data can be added.

<a id="strainaccumulation_triaxialclay_andersen"></a>

## `strainaccumulation_triaxialclay_andersen`

<span class="gc-badge gc-available" data-geocore-function="strainaccumulation_triaxialclay_andersen">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › Strain Accum. (Triaxial Clay)](/docs/geocore/using/modules#strainaccumulation_triaxialclay_andersen)

```python
strainaccumulation_triaxialclay_andersen(
    cyclic_shear_stress,
    undrained_shear_strength,
    cycle_no,
    **kwargs,
)
```

Calculates the cyclic and average strain accumulation for a normally consolidated clay sample under symmetrical cyclic loading (no average shear stress) in a cyclic triaxial test. The contours are based on cyclic triaxial tests on Drammen clay.

Strain contours for cyclic shear strains of 0.05, 0.1, 0.25, 0.5, 1, 5 and 15% are defined and logarithmic interpolation is used to obtain the accumulated strain for a sample tested at a certain ratio of cyclic shear stress to triaxial compression shear strength with a given number of cycles.

Similarly strain contours for average shear strains of -0.5, -0.75, -1, -1.5 and -4% are defined for linear interpolation of the average strains.

![Strain contours for symmetrical cyclic triaxial tests](/docs/assets/groundhog/docs/soildynamics/images/strainaccumulation_triaxialclay_andersen_1.png)

*Strain contours for symmetrical cyclic triaxial tests*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `cyclic_shear_stress` | kPa | 0.0 <= cyclic_shear_stress <= 100.0 | required | Magnitude of the applied cyclic shear stress ($\tau_{cy}$) |
| `undrained_shear_strength` | kPa | 1.0 <= undrained_shear_strength <= 100.0 | required | Undrained shear strength of the normally consolidated clay measured with a triaxial compression test ($S_u^{C}$) |
| `cycle_no` | - | 1.0 <= cycle_no <= 1500.0 | required | Number of applied cycles ($N$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `cyclic strain [%]` | % | Accumulated cyclic shear strain ($\gamma_{cy}$) |
| `average strain [%]` | % | Accumulated average shear strain ($\gamma_{a}$) |
| `cyclic shear strains interpolation [%]` | % | List of cyclic shear strains used for interpolation |
| `shearstress ratios interpolation cyclic [-]` | - | List of ratios of cyclic shear stress to undrained triaxial compression shear strength used for interpolation of cyclic strain |
| `average shear strains interpolation [%]` | % | List of average shear strains used for interpolation |
| `shearstress ratios interpolation average [-]` | - | List of ratios of cyclic shear stress to undrained triaxial compression shear strength used for interpolation of average strain |

**References**

- Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="plotstrainaccumulation_triaxialclay_andersen"></a>

## `plotstrainaccumulation_triaxialclay_andersen`

<span class="gc-badge gc-available" data-geocore-function="plotstrainaccumulation_triaxialclay_andersen">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › Plot Strain Accum. (Triaxial Clay)](/docs/geocore/using/modules#plotstrainaccumulation_triaxialclay_andersen)

```python
plotstrainaccumulation_triaxialclay_andersen()
```

Returns a Plotly figure with the strain accumulation contours for triaxial tests on normally consolidated Drammen clay with symmetrical loading

**Returns**

Plotly figure object which can be further customised and to which test data can be added.

<a id="porepressureaccumulation_dssclay_andersen"></a>

## `porepressureaccumulation_dssclay_andersen`

<span class="gc-badge gc-available" data-geocore-function="porepressureaccumulation_dssclay_andersen">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › Pore Pressure Accum. (DSS Clay)](/docs/geocore/using/modules#porepressureaccumulation_dssclay_andersen)

```python
porepressureaccumulation_dssclay_andersen(
    cyclic_shear_stress,
    undrained_shear_strength,
    cycle_no,
    **kwargs,
)
```

Calculates the excess pore pressure accumulation for a normally consolidated clay sample under symmetrical cyclic loading (no average shear stress) in a DSS test. The contours are based on cyclic DSS tests on Drammen clay.

Excess pore pressure contours for excess pore pressure ratios of 0.05, 0.1, 0.25 and 0.6 are defined and logarithmic interpolation is used to obtain the accumulated excess pore pressure for a sample tested at a certain ratio of cyclic shear stress to DSS shear strength with a given number of cycles.

![Excess pore pressure contours for symmetrical cyclic DSS tests](/docs/assets/groundhog/docs/soildynamics/images/porepressureaccumulation_dssclay_andersen_1.png)

*Excess pore pressure contours for symmetrical cyclic DSS tests*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `cyclic_shear_stress` | kPa | 0.0 <= cyclic_shear_stress <= 100.0 | required | Magnitude of the applied cyclic shear stress ($\tau_{cy}$) |
| `undrained_shear_strength` | kPa | 1.0 <= undrained_shear_strength <= 100.0 | required | Undrained shear strength of the normally consolidated clay measured with a DSS test ($S_u^{DSS}$) |
| `cycle_no` | - | 1.0 <= cycle_no <= 1500.0 | required | Number of applied cycles ($N$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Excess pore pressure ratio [-]` | - | Ratio of accumulated excess pore pressure to vertical effective stress ($u_p / \sigma_{vc}^{\prime}$) |
| `pore pressure ratios interpolation [-]` | - | List of excess pore pressure ratios used for interpolation |
| `shearstress ratios interpolation [-]` | - | List of ratios of cyclic shear stress to undrained DSS shear strength used for interpolation |

**References**

- Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="plotporepressureaccumulation_dssclay_andersen"></a>

## `plotporepressureaccumulation_dssclay_andersen`

<span class="gc-badge gc-available" data-geocore-function="plotporepressureaccumulation_dssclay_andersen">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › Plot Pore Pressure (DSS Clay)](/docs/geocore/using/modules#plotporepressureaccumulation_dssclay_andersen)

```python
plotporepressureaccumulation_dssclay_andersen()
```

Returns a Plotly figure with the excess pore pressure accumulation contours for cyclic DSS tests on normally consolidated Drammen clay with symmetrical loading

**Returns**

Plotly figure object which can be further customised and to which test data can be added.

<a id="porepressureaccumulation_triaxialclay_andersen"></a>

## `porepressureaccumulation_triaxialclay_andersen`

<span class="gc-badge gc-available" data-geocore-function="porepressureaccumulation_triaxialclay_andersen">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › Pore Pressure Accum. (Triaxial Clay)](/docs/geocore/using/modules#porepressureaccumulation_triaxialclay_andersen)

```python
porepressureaccumulation_triaxialclay_andersen(
    cyclic_shear_stress,
    undrained_shear_strength,
    cycle_no,
    **kwargs,
)
```

Calculates the excess pore pressure accumulation for a normally consolidated clay sample under symmetrical cyclic loading (no average shear stress) in a cyclic triaxial test. The contours are based on cyclic triaxial tests on Drammen clay.

The accumulated excess pore pressure is corrected for the change in total octahedral normal stress, making the ratio independent on whether average shear stress is applied by increasing or decreasing the normal stress.

Excess pore pressure contours for excess pore pressure ratios of 0.01, 0.125, 0.15, 0.2 and 0.25 are defined and logarithmic interpolation is used to obtain the accumulated excess pore pressure for a sample tested at a certain ratio of cyclic shear stress to triaxial compression shear strength with a given number of cycles.

![Excess pore pressure contours for symmetrical cyclic triaxial tests](/docs/assets/groundhog/docs/soildynamics/images/porepressureaccumulation_triaxialclay_andersen_1.png)

*Excess pore pressure contours for symmetrical cyclic triaxial tests*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `cyclic_shear_stress` | kPa | 0.0 <= cyclic_shear_stress <= 100.0 | required | Magnitude of the applied cyclic shear stress ($\tau_{cy}$) |
| `undrained_shear_strength` | kPa | 1.0 <= undrained_shear_strength <= 100.0 | required | Undrained shear strength of the normally consolidated clay measured with a DSS test ($S_u^{DSS}$) |
| `cycle_no` | - | 1.0 <= cycle_no <= 1500.0 | required | Number of applied cycles ($N$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Excess pore pressure ratio [-]` | - | Ratio of accumulated excess pore pressure to vertical effective stress ($u_p / \sigma_{vc}^{\prime}$) |
| `pore pressure ratios interpolation [-]` | - | List of excess pore pressure ratios used for interpolation |
| `shearstress ratios interpolation [-]` | - | List of ratios of cyclic shear stress to undrained DSS shear strength used for interpolation |

**References**

- Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="plotporepressureaccumulation_triaxialclay_andersen"></a>

## `plotporepressureaccumulation_triaxialclay_andersen`

<span class="gc-badge gc-available" data-geocore-function="plotporepressureaccumulation_triaxialclay_andersen">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › Plot Pore Pressure (Triaxial Clay)](/docs/geocore/using/modules#plotporepressureaccumulation_triaxialclay_andersen)

```python
plotporepressureaccumulation_triaxialclay_andersen()
```

Returns a Plotly figure with the excess pore pressure accumulation contours for cyclic triaxial tests on normally consolidated Drammen clay with symmetrical loading

**Returns**

Plotly figure object which can be further customised and to which test data can be added.

<a id="strainaccumulation_dsssand_andersen"></a>

## `strainaccumulation_dsssand_andersen`

<span class="gc-badge gc-available" data-geocore-function="strainaccumulation_dsssand_andersen">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › Strain Accum. (DSS Sand)](/docs/geocore/using/modules#strainaccumulation_dsssand_andersen)

```python
strainaccumulation_dsssand_andersen(
    shearstress_ratio,
    cycle_no,
    failure_stress_ratio,
    **kwargs,
)
```

Calculates the strain accumulation as a function of the cyclic shear stress level and the number of cycles for normally consolidated sand and silt in a symmetrical cyclic DSS test (no average shear stress) for different levels of cyclic shear stress at failure. The contours have been compiled based on various tests in the NGI database and should be regarded as estimates.

Strain contours for 0.1, 0.25, 0.5, 1, 2.5, 5, 7.5, 10 and 15% cyclic shear strain are defined and logarithmic interpolation is used between the different contours to obtain the accumulated strain for a sample tested at a certain ratio of cyclic shear stress to vertical effective stress with a given number of cycles.

To calculate the cyclic stress ratio, the vertical effective stress needs to be normalised as follows:

$$
\sigma_{ref}^{\prime} = p_a \cdot ( \sigma_{vc}^{\prime} / p_a ) ^ n
$$

A shear stress exponent of 0.9 is suggested by Andersen (2015).

![Cyclic strain accumulation contours based on symmetrical cyclic DSS tests on normally consolidated sand](/docs/assets/groundhog/docs/soildynamics/images/strainaccumulation_dsssand_andersen_1.png)

*Cyclic strain accumulation contours based on symmetrical cyclic DSS tests on normally consolidated sand*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `shearstress_ratio` | - | 0.0 <= shearstress_ratio <= 2.0 | required | Ratio cyclic shear stress to reference effective stress ($\tau_{cy} / \sigma_{ref}^{\prime}$) |
| `cycle_no` | - | 1.0 <= cycle_no <= 1000.0 | required | Number of applied cycles ($N$) |
| `failure_stress_ratio` | - | failure_stress_ratio >= 0.19 | required | Ratio of cyclic shear stress to vertical effective stress for failure at N=10 Allowable value: [0.19, 0.25, 0.6, 1.0, 1.8] ($( \tau_{cy} / \sigma_{ref}^{\prime})_{N=10}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `cyclic strain [%]` | % | Accumulated cyclic shear strain ($\gamma_{cy}$) |
| `shear strains interpolation [%]` | % | List of shear strains used for the interpolation |
| `shearstress ratios interpolation [-]` | - | Shear stress ratios used for the interpolation |

**References**

- Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="plotstrainaccumulation_dsssand_andersen"></a>

## `plotstrainaccumulation_dsssand_andersen`

<span class="gc-badge gc-available" data-geocore-function="plotstrainaccumulation_dsssand_andersen">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › Plot Strain Accum. (DSS Sand)](/docs/geocore/using/modules#plotstrainaccumulation_dsssand_andersen)

```python
plotstrainaccumulation_dsssand_andersen(failure_stress_ratio)
```

Returns a Plotly figure with the cyclic strain accumulation contours for cyclic DSS tests on normally consolidated sand or silt with symmetrical loading

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `failure_stress_ratio` | - |  | required | Ratio of cyclic shear stress to vertical effective stress for failure at N=10 Allowable value: [0.19, 0.25, 0.6, 1.0, 1.8] ($( \tau_{cy} / \sigma_{ref}^{\prime})_{N=10}$) |

**Returns**

Plotly figure object which can be further customised and to which test data can be added.

<a id="plotporepressureaccumulation_dsssand_andersen"></a>

## `plotporepressureaccumulation_dsssand_andersen`

<span class="gc-badge gc-available" data-geocore-function="plotporepressureaccumulation_dsssand_andersen">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › Plot Pore Pressure (DSS Sand)](/docs/geocore/using/modules#plotporepressureaccumulation_dsssand_andersen)

```python
plotporepressureaccumulation_dsssand_andersen(failure_stress_ratio)
```

Returns a Plotly figure with the permanent excess pore pressure accumulation contours for cyclic DSS tests on normally consolidated sand or silt with symmetrical loading

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `failure_stress_ratio` | - |  | required | Ratio of cyclic shear stress to vertical effective stress for failure at N=10 Allowable value: [0.19, 0.25, 0.6, 1.0, 1.8] ($( \tau_{cy} / \sigma_{ref}^{\prime})_{N=10}$) |

**Returns**

Plotly figure object which can be further customised and to which test data can be added.

<a id="cyclicstrength_dsssand_relativedensity"></a>

## `cyclicstrength_dsssand_relativedensity`

<span class="gc-badge gc-available" data-geocore-function="cyclicstrength_dsssand_relativedensity">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › AC Cyclic Strength (DSS Sand - Dr)](/docs/geocore/using/modules#cyclicstrength_dsssand_relativedensity)

```python
cyclicstrength_dsssand_relativedensity(
    relative_density,
    vertical_effective_stress,
    fines_content=5.0,
    stress_exponent=0.9,
    atmospheric_pressure=100.0,
    **kwargs,
)
```

Calculates the DSS cyclic strength of sand, defined as the ratio of cyclic shear stress to reference normal stress for failure at 10 cycles. Cyclic failure is defined as reaching an accumulated cyclic shear strain of 15%. For certain very dense samples, this strain was not reached. The underlying dataset contains symmetrical DSS tests on normally consolidated sand.

The curves are most representative for vertical effective stresses between 100 and 250kPa. The vertical effective stress was normalised using an exponent of 0.9 for the test data. Most of the underlying cyclic DSS test data is from normally consolidated pre-sheared samples.

The function calculates the shear stress ratio at failure for <5% fines by default but fines content of 20% or 35% can also be entered. The trend for 35% fines content needs to be treated with caution as relative density determination for samples with high fines content is not straightforward.

$$
\sigma_{ref}^{\prime} = p_a \cdot ( \sigma_{ref}^{\prime} / p_a )^n
$$

![Underlying data and trend for cyclic strength calculation](/docs/assets/groundhog/docs/soildynamics/images/cyclicstrength_dsssand_relativedensity_1.png)

*Underlying data and trend for cyclic strength calculation*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `relative_density` | pct | 40.0 <= relative_density <= 110.0 | required | Relative density of the sand ($D_r$) |
| `vertical_effective_stress` | kPa | 100.0 <= vertical_effective_stress <= 250.0 | required | Vertical effective stress at the depth considered ($\sigma_{vc}^{\prime}$) |
| `fines_content` | pct | 5.0 <= fines_content <= 35.0 | `5.0` | Fines content of the soil ($FC$) |
| `stress_exponent` | - | 0.2 <= stress_exponent <= 1.0 | `0.9` | Stress exponent used for stress normalisation ($n$) |
| `atmospheric_pressure` | kPa |  | `100.0` | Atmospheric pressure ($p_a$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `cyclic strength ratio [-]` | - | Cyclic strength ratio for N=10 cycles ($\tau_f / \sigma_{ref}^{\prime}$) |
| `reference effective stress [kPa]` | kPa | Reference effective normal stress ($\sigma_{ref}^{\prime}$) |
| `cyclic shear strength [kPa]` | kPa | Cyclic shear stress for failure at 10 cycles ($\tau_f$) |

**References**

- Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="cyclicstrength_dsssand_watercontent"></a>

## `cyclicstrength_dsssand_watercontent`

<span class="gc-badge gc-available" data-geocore-function="cyclicstrength_dsssand_watercontent">Available in GeoCore</span> [Soil dynamics › Cyclic behaviour › AC Cyclic Strength (DSS Sand - w)](/docs/geocore/using/modules#cyclicstrength_dsssand_watercontent)

```python
cyclicstrength_dsssand_watercontent(
    water_content,
    vertical_effective_stress,
    fines_content=5.0,
    stress_exponent=0.9,
    atmospheric_pressure=100.0,
    **kwargs,
)
```

Calculates the DSS cyclic strength of sand, defined as the ratio of cyclic shear stress to reference normal stress for failure at 10 cycles. Cyclic failure is defined as reaching an accumulated cyclic shear strain of 15%. For certain very dense samples, this strain was not reached. The underlying dataset contains symmetrical DSS tests on normally consolidated sand.

The curves are most representative for vertical effective stresses between 100 and 250kPa. The vertical effective stress was normalised using an exponent of 0.9 for the test data. Most of the underlying cyclic DSS test data is from normally consolidated pre-sheared samples.

The function calculates the shear stress ratio at failure for <5% fines by default but fines content of 20% or 35% can also be entered. The trend for 35% fines content is slightly more reliable when formulated in terms of water content rather than relative density.

$$
\sigma_{ref}^{\prime} = p_a \cdot ( \sigma_{ref}^{\prime} / p_a )^n
$$

![Underlying data and trends for cyclic strength calculation](/docs/assets/groundhog/docs/soildynamics/images/cyclicstrength_dsssand_watercontent_1.png)

*Underlying data and trends for cyclic strength calculation*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `water_content` | pct | 15.0 <= water_content <= 40.0 | required | Water content of the sand after testing ($w_{after}$) |
| `vertical_effective_stress` | kPa | 100.0 <= vertical_effective_stress <= 250.0 | required | Vertical effective stress at the depth considered ($\sigma_{vc}^{\prime}$) |
| `fines_content` | pct | 5.0 <= fines_content <= 35.0 | `5.0` | Fines content of the soil ($FC$) |
| `stress_exponent` | - | 0.2 <= stress_exponent <= 1.0 | `0.9` | Stress exponent used for stress normalisation ($n$) |
| `atmospheric_pressure` | kPa |  | `100.0` | Atmospheric pressure ($p_a$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `cyclic strength ratio [-]` | - | Cyclic strength ratio for N=10 cycles ($\tau_f / \sigma_{ref}^{\prime}$) |
| `reference effective stress [kPa]` | kPa | Reference effective normal stress ($\sigma_{ref}^{\prime}$) |
| `cyclic shear strength [kPa]` | kPa | Cyclic shear stress for failure at 10 cycles ($\tau_f$) |

**References**

- Andersen, K.H. (2015). Cyclic soil parameters for offshore foundation design. The 3rd McClelland Lecture. Conference: Frontiers in Offshore Geotechnics III.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
