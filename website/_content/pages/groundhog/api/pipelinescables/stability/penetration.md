---
title: Pipeline and cable penetration
slug: groundhog/api/pipelinescables/stability/penetration
section: Groundhog API Reference
description: 'API reference for groundhog.pipelinescables.stability.penetration: 6 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/pipelinescables/stability/penetration.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.pipelinescables.stability.penetration
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/pipelinescables/penetration.html
geocore_available: true
geocore_functions:
- contactwidth
- embedment_drained
- embedment_undrained_method1
- embedment_undrained_method2
- lay_touchdown_factor
- penetratedarea
---

Module `groundhog.pipelinescables.stability.penetration` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/pipelinescables/stability/penetration.py).

Upstream documentation: [Pipeline and cable penetration](https://groundhog.readthedocs.io/en/main/pipelinescables/penetration.html).

**Functions:** [`contactwidth`](#contactwidth), [`penetratedarea`](#penetratedarea), [`embedment_undrained_method1`](#embedment_undrained_method1), [`embedment_undrained_method2`](#embedment_undrained_method2), [`embedment_drained`](#embedment_drained), [`lay_touchdown_factor`](#lay_touchdown_factor)

<a id="contactwidth"></a>

## `contactwidth`

<span class="gc-badge gc-available" data-geocore-function="contactwidth">Available in GeoCore</span> [Pipelines and cables › Pipeline and cable stability › Contact Width](/docs/geocore/using/modules#contactwidth)

```python
contactwidth(diameter, penetration, **kwargs)
```

Calculates the contact width depending on the pipeline penetration. The contact width increases until the pipeline penetration reaches half of the diameter

$$
B = 2 \cdot \sqrt{D \cdot z - z^2} \quad \text{for } z < D/2
$$

$$
B=D \quad \text{for } z \geq D/2
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `diameter` | m | 0.0 <= diameter <= 2.0 | required | Pipeline or cable diameter ($D$) |
| `penetration` | m | 0.0 <= penetration <= 2.0 | required | Pipeline or cable penetration ($z$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `B [m]` | m | Contact width of the pipeline or cable with the soil [m] ($B$) |

**References**

- DNV-RP-F114

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="penetratedarea"></a>

## `penetratedarea`

<span class="gc-badge gc-available" data-geocore-function="penetratedarea">Available in GeoCore</span> [Pipelines and cables › Pipeline and cable stability › Penetrated Area](/docs/geocore/using/modules#penetratedarea)

```python
penetratedarea(diameter, penetration, **kwargs)
```

Calculates the penetrated area of the pipeline below the seabed. Note that for penetrations above half of the diameter, the entire displaced area of soil is counted, not just the submerged pipeline area.

$$
A_{bm} = \arcsin \left( \frac{B}{D} \right) \cdot \frac{D^2}{4} - B \cdot \frac{D}{4} \cdot \cos \left( \arcsin(B/D) \right) \quad \text{for } z<D/2
$$

$$
A_{bm} = \frac{\pi \cdot D^2}{8} + D \cdot \left( z - D/2 \right) \quad \text{for } z \geq D/2
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `diameter` | m | 0.0 <= diameter <= 2.0 | required | Pipeline or cable diameter ($D$) |
| `penetration` | m | 0.0 <= penetration <= 2.0 | required | Pipeline penetration ($z$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Abm [m2]` | m2 | Penetrated cross-sectional area of the pipeline or cable [m2] ($A_{bm}$) |
| `B [m]` | m | Contact width (intermediate output of the calculation) [m] ($B$) |

**References**

- DNV-RP-F114

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="embedment_undrained_method1"></a>

## `embedment_undrained_method1`

<span class="gc-badge gc-available" data-geocore-function="embedment_undrained_method1">Available in GeoCore</span> [Pipelines and cables › Pipeline and cable stability › Embedment (Undrained Method 1)](/docs/geocore/using/modules#embedment_undrained_method1)

```python
embedment_undrained_method1(
    diameter,
    undrained_shear_strength,
    k_su,
    gamma_eff,
    penetration,
    Nc=5.14,
    roughness=0.67,
    **kwargs,
)
```

Calculates pipeline embedment in soil which behaves in an undrained manner.

Method 1 uses bearing capacity theory to calculate the embedment where the submerged weight of the pipeline is in equilibrium with the vertical bearing capacity of the soil. The method works in soil with linearly increasing undrained strength. The method includes a depth correction factor and a buoyancy term.

Note that the method assumes quasi-static pipeline penetration. In reality load concentration effects at the touchdown point and dynamic lay effects will lead to increased penetration.

This formula calculates the bearing capacity for a specified depth. For determining the pipeline penetration, a root finding routine needs to be applied to find the penetration where the bearing capacity is in equilbrium with the submerged weight of the pipeline.

$$
Q_v = Q_{v0} \cdot \left( 1 + d_{ca} \right) + \gamma^{\prime} \cdot A_{bm}
$$

$$
Q_{v0} = F \cdot \left( N_c \cdot s_{u,0} + \rho \cdot B/4 \right) \cdot B
$$

$$
z_{su,0} = 0 \quad \text{for } z < \frac{D}{2} \cdot \left( 1 - \frac{\sqrt{2}}{2} \right)
$$

$$
z_{su,0} = z + \frac{D}{2} \cdot \left( \sqrt{2} - 1 \right) - \frac{B}{2} \quad \text{for } z \geq \frac{D}{2} \cdot \left( 1 - \frac{\sqrt{2}}{2} \right)
$$

$$
s_{u,0} = s_{u,z=0} + \rho \cdot z_{s_{u,0}}
$$

$$
d_{ca} = 0.3 \cdot \frac{s_{u,1}}{s_{u,2}} \cdot \arctan \left( \frac{z_{s_{u,0}}}{B} \right)
$$

$$
s_{u,1} = \frac{s_{u,z=0} + s_{u,0}}{2}
$$

$$
s_{u,2} = \frac{Q_{v0}}{B \cdot N_c}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `diameter` | m | 0.01 <= diameter <= 2.0 | required | Pipeline diameter ($D$) |
| `undrained_shear_strength` | kPa | 0.0 <= undrained_shear_strength <= 500.0 | required | Undrained shear strength at the seabed ($s_{u,z=0}$) |
| `k_su` | kPa/m | 0.0 <= k_su <= 10.0 | required | Linear rate of undrained shear strength increase ($\rho$) |
| `gamma_eff` | kN/m3 | 2.0 <= gamma_eff <= 12.0 | required | Submerged unit weight ($kN/m3$) |
| `penetration` | m | 0.0 <= penetration <= 2.0 | required | Penetration depth for which the pipeline penetration is calculated ($m$) |
| `Nc` | - | 4.0 <= Nc <= 9.0 | `5.14` | Bearing capacity factor ($N_c$) |
| `roughness` | - | 0.0 <= roughness <= 1.0 | `0.67` | Measure for the roughness of the pipe of cable ($r$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `F [-]` | - | Roughness correction factor [-] ($F$) |
| `z_su0 [m]` | m | Reference z-level for depth effects [m] ($z_{s_{u,0}}$) |
| `B [m]` | m | Contact width [m] ($B$) |
| `su0 [kPa]` | kPa | Undrained shear strength at the reference z-level [kPa] ($s_{u,0}$) |
| `Abm [m2]` | m2 | Penetrated cross-sectional area of the pipe [m2] ($A_{bm}$) |
| `Qv0 [kN/m]` | kN/m | Bearing capacity (excluding depth effects and buoyancy) [kN/m] ($Q_{v0}$) |
| `Qv [kN/m]` | kN/m | Bearing capacity (including depth and buoyancy effect) [kN/m] ($Q_v$) |

**References**

- DNV-RP-F114

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="embedment_undrained_method2"></a>

## `embedment_undrained_method2`

<span class="gc-badge gc-available" data-geocore-function="embedment_undrained_method2">Available in GeoCore</span> [Pipelines and cables › Pipeline and cable stability › Embedment (Undrained Method 2)](/docs/geocore/using/modules#embedment_undrained_method2)

```python
embedment_undrained_method2(
    diameter,
    penetration,
    undrained_shear_strength,
    gamma_eff,
    calibration_factor_1=6.0,
    calibration_factor_2=0.25,
    calibration_factor_3=3.4,
    calibration_factor_4=0.5,
    calibration_factor_5=1.5,
    **kwargs,
)
```

Calculates the pipeline penetration for deepwater soft clay. The formulation contains a component for soil resistance to pipeline penetration, the second term accounts for buoyancy effects with enhancement to fit the data.

For very high embedment (more than half of the diameter), the method may underestimate the penetration resistance.

Note that the undrained shear strength at the pipeline invert level is used, so this might have to be calculated or derived from e.g. T-bar tests.

This formula calculates the penetration resistance for a specified depth. For determining the pipeline penetration, a root finding routine needs to be applied to find the penetration where the penetration resistance is in equilbrium with the submerged weight of the pipeline.

$$
Q_v = \left[ \min \left( 6 \cdot \left( \frac{z}{D} \right)^{0.25}; 3.4 \cdot \left( \frac{10 \cdot z}{D} \right)^{0.5} \right) + 1.5 \cdot \frac{\gamma^{\prime} \cdot A_{bm}}{D \cdot s_u} \right] \cdot D \cdot s_u
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `diameter` | m | 0.0 <= diameter <= 2.0 | required | Pipeliine diameter ($D$) |
| `penetration` | m | 0.0 <= penetration <= 2.0 | required | Pipeline penetration ($z$) |
| `undrained_shear_strength` | kPa | 0.0 <= undrained_shear_strength <= 50.0 | required | Undrained shear strength at the pipeline invert level ($s_u$) |
| `gamma_eff` | kN/m3 | 2.0 <= gamma_eff <= 12.0 | required | Submerged unit weight of the soil ($\gamma^{\prime}$) |
| `calibration_factor_1` | - |  | `6.0` | First calibration factor ($-$) |
| `calibration_factor_2` | - |  | `0.25` | Second calibration factor ($-$) |
| `calibration_factor_3` | - |  | `3.4` | Third calibration factor ($-$) |
| `calibration_factor_4` | - |  | `0.5` | Fourth calibration factor ($-$) |
| `calibration_factor_5` | - |  | `1.5` | Calibration factor on then buoyancy term ($-$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Qv [kN/m]` | kN/m | Pipeline penetration resistance [kN/m] ($Q_v$) |

**References**

- DNV-RP-F114

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="embedment_drained"></a>

## `embedment_drained`

<span class="gc-badge gc-available" data-geocore-function="embedment_drained">Available in GeoCore</span> [Pipelines and cables › Pipeline and cable stability › Embedment (Drained)](/docs/geocore/using/modules#embedment_drained)

```python
embedment_drained(
    penetration,
    gamma_eff,
    phi_eff,
    diameter,
    roughness_factor=0.67,
    Ngamma_theory='Vesic',
    **kwargs,
)
```

Calculates pipeline embedment in drained conditions using bearing capacity theory. The vertical force required to penetrate the pipe to a given embedment is calculated.

Note that there is no embedment effect as long as the pipeline is within the active Rankine zone.

Bearing capacity factors are taken in accordance with shallow foundation theory.

$$
Q_v = 0.5 \cdot \gamma^{\prime} \cdot N_{\gamma} \cdot B^2 + z_0 \cdot \gamma^{\prime} \cdot N_q \cdot d_q \cdot B
$$

$$
z_0 = 0 \quad \text{for } z < \frac{D}{2} \cdot \left[ 1 - \cos \left( \frac{\pi}{4} + \frac{\varphi^{\prime}}{2} \right) \right]
$$

$$
z_0 = z - \frac{D}{2} + \left[ \frac{D/2}{\sin \left( \pi/4 + \varphi^{\prime}/2 \right)} - B/2 \right] \cdot \tan \left( \frac{\pi}{4} + \frac{\varphi^{\prime}}{2} \right)  \quad \text{for } z \geq \frac{D}{2} \cdot \left[ 1 - \cos \left( \frac{\pi}{4} + \frac{\varphi^{\prime}}{2} \right) \right]
$$

$$
d_q = 1 + 1.2 \cdot \frac{z_0}{B} \cdot \tan \varphi^{\prime} \cdot \left( 1 - \sin \varphi^{\prime} \right)^2
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `penetration` | m | 0.0 <= penetration <= 2.0 | required | Pipeline or cable penetration below virgin seabed ($z$) |
| `gamma_eff` | kN/m3 | 3.0 <= gamma_eff <= 12.0 | required | Submerged unit weight of the soil ($\gamma^{\prime}$) |
| `phi_eff` | deg | 15.0 <= phi_eff <= 50.0 | required | Effective friction angle of the soil ($\varphi^{\prime}$) |
| `diameter` | m | 0.0 <= diameter <= 2.0 | required | Pipeline or cable diameter ($D$) |
| `roughness_factor` | - | 0.0 <= roughness_factor <= 1.0 | `0.67` | Pipeline roughness factor where 0 is fully smooth and 1 is fully rough, used when theory for $N_{\gamma}$ is set to `'DavisBooker'` ($R_{inter}$) |
| `Ngamma_theory` |  | one of `Vesic`, `Meyerhof`, `DavisBooker` | `'Vesic'` | Select the theoretical formulate of bearing capacity factor Ngamma |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Nq [-]` | - | Bearing capacity factor for stress level [-] ($N_q$) |
| `Ngamma [-]` | - | Bearing capacity factor for unit weight [-] ($N_{\gamma}$) |
| `B [m]` | m | Pipe-soil contact width [m] ($B$) |
| `z0 [m]` | m | Reference depth level [m] ($z_0$) |
| `dq [-]` | - | Factor accounting for depth effects [-] ($d_q$) |
| `Qv [kN/m]` | kN/m | Vertical force required for penetration to depth z [kN/m] ($Q_v$) |

**References**

- DNV-RP-F114

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="lay_touchdown_factor"></a>

## `lay_touchdown_factor`

<span class="gc-badge gc-available" data-geocore-function="lay_touchdown_factor">Available in GeoCore</span> [Pipelines and cables › Pipeline and cable stability › Lay Touchdown Factor](/docs/geocore/using/modules#lay_touchdown_factor)

```python
lay_touchdown_factor(
    penetration,
    submerged_weight,
    seabed_stiffness,
    lay_tension,
    bending_stiffness,
    calibration_factor1=0.6,
    calibration_factor2=0.4,
    **kwargs,
)
```

Calculates the load concentration factor at the touchdown point. Load concentration at this point leads to additional pipeline embedment over the static embedment. Pipeline weight, bending stiffness and effective lay tension during pipelay contribute to this factor.

The equation is derived by modelling a catenary hanging off a vessel, touching down on a seabed with linearly increasing resistance with penetration depth. There is a minimum lay tension for this equation to apply (see Equations).

The lay tension can be uncertain, so it is best to consider a range of values.

The calculation is performed by first calculating seabed stiffness from the static penetration and then plugging this value into the amplification factor equation. Both curves are a function of pipeline embedment. The penetration depth accounting for amplification and the laydown factor are found at the intersection of both curves.

$$
k_{lay} = 0.6 + 0.4 \cdot \left( \frac{EI \cdot k \cdot W_i}{z_{ini} \cdot T_0^2} \right)^{0.25} \geq 1 \quad \text{for } T_0 > \left[ 3 \cdot \sqrt{EI} \cdot W_i \right]^{2/3}
$$

$$
k = Q_v \ W_i
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `penetration` | m | 0.0 <= penetration <= 2.0 | required | Pipeline penetration after laying ($z_{ini}$) |
| `submerged_weight` | kN/m | submerged_weight >= 0.0 | required | Submerged weight of the pipeline during installation ($W_i$) |
| `seabed_stiffness` | kN/m/m | seabed_stiffness >= 0.0 | required | Stiffness of the seabed (penetration resistance divided by penetration) ($k=Q_v/W_i$) |
| `lay_tension` | kN | lay_tension >= 0.0 | required | Lay tension during laydown ($T_0$) |
| `bending_stiffness` | kNm2 | bending_stiffness >= 0.0 | required | Bending stiffness of the pipeline ($EI$) |
| `calibration_factor1` | - |  | `0.6` | First calibration factor ($-$) |
| `calibration_factor2` | - |  | `0.4` | Second calibration factor ($-$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `k_lay [-]` | - | Lay amplification factor [-] ($k_{lay}$) |

**References**

- DNV-RP-F114

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
