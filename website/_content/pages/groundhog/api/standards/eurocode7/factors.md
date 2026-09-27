---
title: factors
slug: groundhog/api/standards/eurocode7/factors
section: Groundhog API Reference
description: 'API reference for groundhog.standards.eurocode7.factors: 0 functions, 1 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/standards/eurocode7/factors.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.standards.eurocode7.factors
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/standards/factors.html
geocore_available: true
geocore_functions:
- eurocode7_factors
---

Module `groundhog.standards.eurocode7.factors` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/standards/eurocode7/factors.py).

Upstream documentation: [Partial factor selection](https://groundhog.readthedocs.io/en/main/standards/factors.html).

**Classes:** [`Eurocode7_factoring_STR_GEO`](#eurocode7_factoring_str_geo)

<a id="eurocode7_factoring_str_geo"></a>

## class `Eurocode7_factoring_STR_GEO`

<span class="gc-badge gc-available" data-geocore-function="eurocode7_factors">Available in GeoCore</span> [EuroCode7 › Partial factor selection › Eurocode7_factoring_STR_GEO](/docs/geocore/using/modules#eurocode7_factors)

```python
Eurocode7_factoring_STR_GEO()
```

<a id="eurocode7_factoring_str_geo-__init__"></a>

### `Eurocode7_factoring_STR_GEO.__init__`

```python
__init__()
```

This class sets the necessary factors for Eurocode 7 factoring of effects of actions and resistances for the STR and GEO limit states.

The initialisation sets four sets dictionaries for factors, each with sub-dictionaries for the case under consideration

- Effects of actions: Factor sets A1 and A2
  - Permanent unfavourable
  - Permanent favourable
  - Variable unfavourable
  - Variable favourable
- Soil parameters: Factor sets M1 and M2
  - Angle of shearing resistance
  - Effective cohesion
  - Undrained shear strength
  - Unconfined strength
  - Weight density
- Resistances: Factor sets R1, R2, R3 and R4 for different types of foundations and retaining structures
  - Spread foundation
    - Bearing
    - Sliding
  - Driven pile
    - Base
    - Shaft
    - Total compression
    - Shaft tension
  - Bored pile
    - Base
    - Shaft
    - Total compression
    - Shaft tension
  - CFA pile
    - Base
    - Shaft
    - Total compression
    - Shaft tension
  - Prestressed anchorage
    - Temporary
    - Permanent
  - Retaining structure
    - Bearing capacity
    - Sliding resistance
    - Earth resistance
  - Slopes
    - Earth resistance
- Correlation factors
  - $\xi_1,\xi_2$ for pile design based on results from static pile load tests (SLT)
  - $\xi_3,\xi_4$ for pile design based on results from geotechnical investigations
  - $\xi_5,\xi_6$ for pile design based on results from dynamic pile load tests (DPLT)

By default, the factors from EN 1997-1 Appendix A are adopted. If the user wants to override these using Nationally Determined Parameters, they need to use the overriding methods.

<a id="eurocode7_factoring_str_geo-select_design_approach"></a>

### `Eurocode7_factoring_STR_GEO.select_design_approach`

```python
select_design_approach(design_approach='DA1-1', foundation_type='Spread foundation')
```

The user selects the design approach (`"DA1-1"`, `"DA1-1"`, `"DA2"`, `"DA3-1"`, `"DA3-2"`) based on the design problem and national requirements. Note that design approach 1 is split in Combination 1 (`"DA1-1"`) and Combination 2 (`"DA1-2"`) as the two combinations need to be checked. A separate object needs to be created for each set. Design approach 3 is also split into two cases (`"DA3-1"` and `"DA3-2"`) depending on whether A1 or A2 is used.

The following combinations are stored in the `.selected_factors_actions`, `.selected_factors_soil` and `.selected_factors_resistance` attributes:

- DA1-1: A1 + M1 + R1
- DA1-2: A2 + M2 + R1
- DA2: A1 + M1 + R2
- DA3-1: A1 + M2 + R3
- DA3-2: A2 + M2 + R3

For the resistance factors, the user must also specify a foundation type from the following list:

- Spread foundation
- Driven pile
- Bored pile
- CFA pile
- Prestressed anchorage
- Retaining structure
- Slopes

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `design_approach` |  |  | `'DA1-1'` | No upstream documentation. |
| `foundation_type` |  |  | `'Spread foundation'` | No upstream documentation. |

<a id="eurocode7_factoring_str_geo-override_factors_actions"></a>

### `Eurocode7_factoring_STR_GEO.override_factors_actions`

```python
override_factors_actions(set, loadtype=None, value=None, override_dict=None)
```

Overrides the factor on effect of actions. An individual factor can be overridden by specifying its set, loadtype and value. Alternatively, an entire dictionary can be specified to override one of the sets, completely replacing the defaults

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `set` |  |  | required | No upstream documentation. |
| `loadtype` |  |  | `None` | No upstream documentation. |
| `value` |  |  | `None` | No upstream documentation. |
| `override_dict` |  |  | `None` | No upstream documentation. |

<a id="eurocode7_factoring_str_geo-override_factors_soil"></a>

### `Eurocode7_factoring_STR_GEO.override_factors_soil`

```python
override_factors_soil(set, soilparameter=None, value=None, override_dict=None)
```

Overrides the factor on soil properties. An individual factor can be overridden by specifying its set, soilparameter type and value. Alternatively, an entire dictionary can be specified to override one of the sets, completely replacing the defaults

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `set` |  |  | required | No upstream documentation. |
| `soilparameter` |  |  | `None` | No upstream documentation. |
| `value` |  |  | `None` | No upstream documentation. |
| `override_dict` |  |  | `None` | No upstream documentation. |

<a id="eurocode7_factoring_str_geo-override_factors_resistance"></a>

### `Eurocode7_factoring_STR_GEO.override_factors_resistance`

```python
override_factors_resistance(
    set,
    foundationtype,
    resistancecomponent=None,
    value=None,
    override_dict=None,
)
```

Overrides the factor on resistances. An individual factor can be overridden by specifying its set, foundation type, resistance component and value. Alternatively, an entire dictionary can be specified to override one of the sets for a given foundation type, completely replacing the defaults

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `set` |  |  | required | No upstream documentation. |
| `foundationtype` |  |  | required | No upstream documentation. |
| `resistancecomponent` |  |  | `None` | No upstream documentation. |
| `value` |  |  | `None` | No upstream documentation. |
| `override_dict` |  |  | `None` | No upstream documentation. |

<a id="eurocode7_factoring_str_geo-select_correlation_factors"></a>

### `Eurocode7_factoring_STR_GEO.select_correlation_factors`

```python
select_correlation_factors(testtype, no_tests, interpolate=False)
```

Selects the correlation factors for a given testtype ('Static load test', 'Ground investigation', 'Dynamic load test') If `interpolate` is set to True, interpolation between the two nearest categories is considered. A dictionary with the selected correlation factors is returned.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `testtype` |  |  | required | No upstream documentation. |
| `no_tests` |  |  | required | No upstream documentation. |
| `interpolate` |  |  | `False` | No upstream documentation. |
