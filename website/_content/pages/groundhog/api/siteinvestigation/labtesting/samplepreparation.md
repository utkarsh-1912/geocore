---
title: Sample preparation
slug: groundhog/api/siteinvestigation/labtesting/samplepreparation
section: Groundhog API Reference
description: 'API reference for groundhog.siteinvestigation.labtesting.samplepreparation: 1 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/siteinvestigation/labtesting/samplepreparation.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.siteinvestigation.labtesting.samplepreparation
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/site_investigation/samplepreparation.html
geocore_available: true
geocore_functions:
- undercompaction_cohesionless_ladd
---

Module `groundhog.siteinvestigation.labtesting.samplepreparation` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/siteinvestigation/labtesting/samplepreparation.py).

Upstream documentation: [Sample preparation](https://groundhog.readthedocs.io/en/main/site_investigation/samplepreparation.html).

**Functions:** [`undercompaction_cohesionless_ladd`](#undercompaction_cohesionless_ladd)

<a id="undercompaction_cohesionless_ladd"></a>

## `undercompaction_cohesionless_ladd`

<span class="gc-badge gc-available" data-geocore-function="undercompaction_cohesionless_ladd">Available in GeoCore</span> [Site investigation › Laboratory: Sample preparation › undercompaction_cohesionless_ladd()](/docs/geocore/using/modules#undercompaction_cohesionless_ladd)

```python
undercompaction_cohesionless_ladd(
    sample_height,
    no_layers,
    undercompaction_deepest,
    undercompaction_shallowest=0,
    **kwargs,
)
```

When soil sample have to be reconstituted to a specific relative density,  the sample is generally prepared in several layers of equal mass and tamping or vibration is used to obtain the desired volume in the sample mould.

If each layer is however compacted to the desired relative density, a non-uniform density profile will be obtained as the lower layers will still be compacted to a certain degree by the tamping or vibration on the upper layers.

To address this shortcoming, the undercompaction method is used (Ladd, 1978) which compacts the deeper layers to a lesser degree than the higher layers. The degree of undercompaction of the deepest layer is chosen based on experience (e.g. from density profiling using core loggers) and the undercompaction degree is then chosen to vary linearly from the bottom to the top of the sample.

This function calculates the undercompaction degrees for each layer (using a linear variation) and the height to the top of each layer for the given undercompaction degrees.

$$
U_i = U_1 - \left[ \frac{U_1 - U_N}{N - 1} \cdot (i - 1) \right]
$$

$$
h_i = \frac{H_0}{N} \left[ (i - 1) + (1 + U_i) \right]
$$

![Density profiles of triaxial silt samples using different undercompaction degrees](/docs/assets/groundhog/docs/site_investigation/images/undercompaction_cohesionless_ladd_1.png)

*Density profiles of triaxial silt samples using different undercompaction degrees*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `sample_height` | m | 0.0 <= sample_height <= 1.0 | required | Total height of the sample ($H_0$) |
| `no_layers` | - | 1.0 <= no_layers <= 10.0 | required | Number of layers for the sample ($N$) |
| `undercompaction_deepest` | pct | 0.0 <= undercompaction_deepest <= 10.0 | required | Chosen undercompaction degree of the deepest layer ($U_1$) |
| `undercompaction_shallowest` | pct | 0.0 <= undercompaction_deepest <= 10.0 | `0` | Chosen undercompaction degree of the shallowest layer (default=0pct) ($U_N$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `U [-]` | - | Undercompaction degrees of each layer starting from the deepest layer ($U$) |
| `h [m]` | m | Height to the top of each layer ($h$) |

**References**

- R. Ladd, "Preparing Test Specimens Using Undercompaction," Geotechnical Testing Journal 1, no. 1 (1978): 16-23. https://doi.org/10.1520/GTJ10364J

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
