---
title: cohesionless
slug: groundhog/api/constitutivemodels/cohesionless
section: Groundhog API Reference
description: 'API reference for groundhog.constitutivemodels.cohesionless: 0 functions, 1 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/constitutivemodels/cohesionless.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.constitutivemodels.cohesionless
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/constitutivemodels/cohesionless.html
geocore_available: true
geocore_functions:
- hardening_soil_drained_triaxial
---

Module `groundhog.constitutivemodels.cohesionless` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/constitutivemodels/cohesionless.py).

Upstream documentation: [Cohesionless materials](https://groundhog.readthedocs.io/en/main/constitutivemodels/cohesionless.html).

**Classes:** [`HardeningSoil`](#hardeningsoil)

<a id="hardeningsoil"></a>

## class `HardeningSoil`

<span class="gc-badge gc-available" data-geocore-function="hardening_soil_drained_triaxial">Available in GeoCore</span> [Constitutive models › Cohesionless materials › Hardening Soil (Drained Triaxial)](/docs/geocore/using/modules#hardening_soil_drained_triaxial)

```python
HardeningSoil(friction_angle, cohesion, Rf=0.9)
```

Class for setting up the equations for the hardening soil model and performing fitting of drained triaxial tests.

<a id="hardeningsoil-__init__"></a>

### `HardeningSoil.__init__`

```python
__init__(friction_angle, cohesion, Rf=0.9)
```

Sets up the material using the strength parameters friction angle ($\varphi_p$), cohesion ($c$) and failure ratio ($R_f$)

In absence of other guidance, $R_f$=0.9 is a good default setting.

$$
q_a = \frac{q_f}{R_f}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `friction_angle` |  |  | required | No upstream documentation. |
| `cohesion` |  |  | required | No upstream documentation. |
| `Rf` |  |  | `0.9` | No upstream documentation. |

<a id="hardeningsoil-set_reference_moduli"></a>

### `HardeningSoil.set_reference_moduli`

```python
set_reference_moduli(E50_ref, Eur_ref, Eoed_ref, p_ref)
```

Sets the stiffnesses for the hardening soil model using moduli identified at a reference pressure (typically 100kPa).

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `E50_ref` | kPa |  | required | $E_{50}^{ref}$ is the secant modulus at 50% of the maximum deviator stress for a drained triaxial test carried out at $p_{ref}$ |
| `Eur_ref` | kPa |  | required | $E_{ur}^{ref}$ is the unloading reloading stiffness for a drained triaxial test carried out at $p_{ref}$ |
| `Eoed_ref` |  |  | required | No upstream documentation. |
| `p_ref` | kPa |  | required | $p_{ref}$ is the reference pressure at which the tests are carried out. Note that the same pressure is used for all tests. |
| `Eoef_ref` | kPa |  |  | $E_{oed}^{ref}$ is the tangent stiffness for primary oedometric loading at $p_{ref}$ |

<a id="hardeningsoil-calculate_stiffnesses"></a>

### `HardeningSoil.calculate_stiffnesses`

```python
calculate_stiffnesses(
    sigma_3,
    sigma_1,
    m,
    cohesion,
    friction_angle,
    E50_ref,
    Eur_ref,
    Eoed_ref,
    p_ref,
)
```

Calculates the stiffnesses $E_{50}$, $E_{ur}$ and $E_{oed}$ for a given consolidation pressure $\sigma_{3}$.

$$
E_{50} = E_{50}^{ref} \left( \frac{\sigma_3 + c \cot \varphi}{p_{ref} + c \cot \varphi} \right)^m
$$

$$
E_{ur} = E_{ur}^{ref} \left( \frac{\sigma_3 + c \cot \varphi}{p_{ref} + c \cot \varphi} \right)^m
$$

$$
E_{oed} = E_{oed}^{ref} \left( \frac{\sigma_1 + c \cot \varphi}{p_{ref} + c \cot \varphi} \right)^m
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `sigma_3` |  |  | required | Consolidation pressure considered for shearing behaviour |
| `sigma_1` |  |  | required | Consolidation pressure considered for volumetric compression behaviour |
| `m` |  |  | required | Stress exponent governing the stress dependence of the moduli. |
| `cohesion` |  |  | required | No upstream documentation. |
| `friction_angle` |  |  | required | No upstream documentation. |
| `E50_ref` |  |  | required | No upstream documentation. |
| `Eur_ref` |  |  | required | No upstream documentation. |
| `Eoed_ref` |  |  | required | No upstream documentation. |
| `p_ref` |  |  | required | No upstream documentation. |

<a id="hardeningsoil-calculate_drainedtriaxial"></a>

### `HardeningSoil.calculate_drainedtriaxial`

```python
calculate_drainedtriaxial(sigma3, sigma1_0, m, N=100)
```

Calculates the response in a drained triaxial tests based on the parameters entered by the user.

$$
q_f = \frac{6 \sin \varphi}{3 - \sin \varphi} \left( p + c \cot \varphi \right)
$$

$$
q_a = \frac{q_f}{R_f}
$$

$$
\epsilon_1 = \frac{q_a}{2 E_{50}} \frac{(\sigma_1 - \sigma_3)}{q_a - (\sigma_1 - \sigma_3)} \\ \text{for} \\ q \leq q_f
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `sigma3` | kPa |  | required | Radial consolidation stress |
| `sigma1_0` | kPa |  | required | Initial vertical consolidation stress |
| `m` | - |  | required | Stress exponent governing the stress dependency of the stiffness |
| `N` |  |  | `100` | Number of points where $q$ is calculated ($\sigma_1$ is spaced evenly between $\sigma_{1,0}$ and $\sigma_{1,f}$) |
