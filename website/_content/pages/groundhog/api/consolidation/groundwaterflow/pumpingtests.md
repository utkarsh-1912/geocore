---
title: Pumping tests
slug: groundhog/api/consolidation/groundwaterflow/pumpingtests
section: Groundhog API Reference
description: 'API reference for groundhog.consolidation.groundwaterflow.pumpingtests: 1 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/consolidation/groundwaterflow/pumpingtests.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.consolidation.groundwaterflow.pumpingtests
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/consolidation/pumpingtests.html
geocore_available: true
geocore_functions:
- hydraulicconductivity_unconfinedaquifer
---

Module `groundhog.consolidation.groundwaterflow.pumpingtests` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/consolidation/groundwaterflow/pumpingtests.py).

Upstream documentation: [Pumping tests](https://groundhog.readthedocs.io/en/main/consolidation/pumpingtests.html).

**Functions:** [`hydraulicconductivity_unconfinedaquifer`](#hydraulicconductivity_unconfinedaquifer)

<a id="hydraulicconductivity_unconfinedaquifer"></a>

## `hydraulicconductivity_unconfinedaquifer`

<span class="gc-badge gc-available" data-geocore-function="hydraulicconductivity_unconfinedaquifer">Available in GeoCore</span> [Consolidation functions › Pumping tests › Hydraulic Conductivity (Unconfined Aquifer)](/docs/geocore/using/modules#hydraulicconductivity_unconfinedaquifer)

```python
hydraulicconductivity_unconfinedaquifer(
    radius_1,
    radius_2,
    piezometric_height_1,
    piezometric_height_2,
    flowrate,
    **kwargs,
)
```

Calculates the hydraulic conductivity from observing two standpipes in the vicinity of a pumping well. The standpipes should be within the radius of influence of the pumping well.

The following conditions must be satisfied:

- Unconfined and non-leaking water layer
- Open base of the pumping well is below the groundwater level
- Homogeneous, isotropic soil mass of infinite size
- Darcy's law applies
- Radial flow
- Hydraulic gradient equal to slope of groundwater surface

$$
i = \frac{dz}{dr}
$$

$$
A = 2 \pi r z
$$

$$
q_z = 2 \pi r z k \frac{dz}{dr}
$$

$$
q_z \int_{r_1}^{r_2} \frac{dr}{r} = 2 k \pi \int_{h_1}^{h_2} z dz
$$

$$
k = \frac{q_z \ln \left( r_2 / r_1 \right)}{\pi \left( h_2^2 - h_1^2 \right)}
$$

*Figure `images/hydraulicconductivity_unconfinedaquifer_1.png` is referenced by the docstring but is not present in the groundhog repository at `dc7d554c6b8986bae30f518304546a911b1ca5ab`.*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `radius_1` | m | radius_1 >= 0.0 | required | Radial distance between the axis of the pumping well and the first standpipe ($r_1$) |
| `radius_2` | m | radius_2 >= 0.0 | required | Radial distance between the axis of the pumping well and the second standpipe ($r_2$) |
| `piezometric_height_1` | m | piezometric_height_1 >= 0.0 | required | Piezometric height in the first standpipe ($h_1$) |
| `piezometric_height_2` | m | piezometric_height_2 >= 0.0 | required | Piezometric height in the second standpipe ($h_2$) |
| `flowrate` | m3/s | flowrate >= 0.0 | required | Flowrate extracted from the pumping well ($q_z$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `hydraulic_conductivity [m/s]` | m/s | Hydraulic conductivity ($k$) |

**References**

- Budhu (2011). Soil mechanics and foundations. John Wiley and Sons.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
