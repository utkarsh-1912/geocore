---
title: Soil classes and categories
slug: groundhog/api/siteinvestigation/classification/categories
section: Groundhog API Reference
description: 'API reference for groundhog.siteinvestigation.classification.categories: 4 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/siteinvestigation/classification/categories.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.siteinvestigation.classification.categories
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/site_investigation/categories.html
geocore_available: true
geocore_functions:
- relativedensity_categories
- samplequality_voidratio_lunne
- su_categories
- uscs_categories
---

Module `groundhog.siteinvestigation.classification.categories` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/siteinvestigation/classification/categories.py).

Upstream documentation: [Soil classes and categories](https://groundhog.readthedocs.io/en/main/site_investigation/categories.html).

**Functions:** [`relativedensity_categories`](#relativedensity_categories), [`su_categories`](#su_categories), [`uscs_categories`](#uscs_categories), [`samplequality_voidratio_lunne`](#samplequality_voidratio_lunne)

<a id="relativedensity_categories"></a>

## `relativedensity_categories`

<span class="gc-badge gc-available" data-geocore-function="relativedensity_categories">Available in GeoCore</span> [Site investigation › Classification: Classes & categories › Relative Density Classification](/docs/geocore/using/modules#relativedensity_categories)

```python
relativedensity_categories(relative_density, **kwargs)
```

Categorizes relative densities according to the following definition:

- 0 - 0.15: Very loose
- 0.15 - 0.35: Loose
- 0.35 - 0.65: Medium dense
- 0.65 - 0.85: Dense
- 0.85 - 1: Very dense

$$
D_r = \frac{e - e_{min}}{e_{max} - e_{min}}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `relative_density` | - | 0.0 <= relative_density <= 1.0 | required | Relative density of cohesionless material ($D_r$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Relative density` |  | Relative density class |

**References**

- API RP2 GEO

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="su_categories"></a>

## `su_categories`

<span class="gc-badge gc-available" data-geocore-function="su_categories">Available in GeoCore</span> [Site investigation › Classification: Classes & categories › Undrained Shear Strength Classification](/docs/geocore/using/modules#su_categories)

```python
su_categories(undrained_shear_strength, standard='BS 5930:2015', **kwargs)
```

Classifies undrained shear strength in a number of categories. The classification system can be selected but the default is BS 5930:2015. Classification according to ASTM D-2488 is also available.

According to BS 5930:2015:

- Extremely low: < 10kPa
- Very low: 10 - 20kPa
- Low: 20 - 40kPa
- Medium: 40 - 75kPa
- High: 75 - 150kPa
- Very high: 150 - 300kPa
- Extremely high: > 300kPa

According to ASTM D-2488:

- Very soft: 0 - 12.5kPa
- Soft: 12.5 - 25kPa
- Firm: 25 - 50kPa
- Stiff: 50 - 100kPa
- Very stiff: 100 - 200kPa
- Hard: 200 - 400kPa
- Very hard: > 400kPa

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `undrained_shear_strength` | kPa | 0.0 <= undrained_shear_strength <= 1000.0 | required | Undrained shear strength of the cohesive sample ($S_u$) |
| `standard` |  | one of `BS 5930:2015`, `ASTM D-2488` | `'BS 5930:2015'` | Standard used for the classification |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `strength class` |  | Strength class for the selected classification system |

**References**

- BS 5930:2015, ASTM D-2488

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="uscs_categories"></a>

## `uscs_categories`

<span class="gc-badge gc-available" data-geocore-function="uscs_categories">Available in GeoCore</span> [Site investigation › Classification: Classes & categories › USCS Soil Type Descriptions](/docs/geocore/using/modules#uscs_categories)

```python
uscs_categories(symbol, **kwargs)
```

Provides the verbose description for soil type codes according to USCS. The `USCS_DICTIONARY` can also be used in workflows.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `symbol` |  | one of `GW`, `GP`, `GM`, `GC`, `SW`, `SP`, `SM`, `SC`, `ML`, `CL`, `OL`, `MH`, `CH`, `OH` | required | Two character symbol for the soil type according to USCS |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Soil type` |  | Verbose description of the soil type |

**References**

- USCS

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="samplequality_voidratio_lunne"></a>

## `samplequality_voidratio_lunne`

<span class="gc-badge gc-available" data-geocore-function="samplequality_voidratio_lunne">Available in GeoCore</span> [Site investigation › Classification: Classes & categories › Lunne Sample Quality (Void Ratio Change)](/docs/geocore/using/modules#samplequality_voidratio_lunne)

```python
samplequality_voidratio_lunne(voidratio, voidratio_change, ocr, **kwargs)
```

Determines the sample quality for clays based on the change in void ratio when consolidating the sample back to the initial vertical effective stress. The classification is based on testing of soft marine clays sampled with different methods.

```text
+-------+-----------------------------------------------------------------+
| OCR   |                    \Delta e / e_0                       |
|       +------------------------+--------------+-------------+-----------+
|       | Very good to excellent | Good to fair | Poor        | Very poor |
+-------+------------------------+--------------+-------------+-----------+
| 1 - 2 |         < 0.04         |  0.04 - 0.07 | 0.07 - 0.14 |   > 0.14  |
+-------+------------------------+--------------+-------------+-----------+
| 2 - 4 |         < 0.03         |  0.03 - 0.05 | 0.05 - 0.10 |   > 0.10  |
+-------+------------------------+--------------+-------------+-----------+
```

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `voidratio` | - | 0.3 <= voidratio <= 3.0 | required | Initial void ratio ($e_0$) |
| `voidratio_change` | - | -1 <= voidratio <= 1 | required | Change in void ratio when consolidating to in-situ stress ($\Delta e$) |
| `ocr` | - | 1 <= voidratio <= 4.0 | required | Overconsolidation ratio ($\text{OCR}$) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `delta e/e0 [-]` | - | Ratio used for classification |
| `Quality category` |  | Quality category according to Lunne et al. |

**References**

- Lunne, T., et al. "Effects of sample disturbance on consolidation behaviour of soft marine Norwegian clays." Geotechnical and geophysical site characterization: proceedings of the third international conference on site characterization ISC. Vol. 3. 2008.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
