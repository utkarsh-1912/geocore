---
title: Validation
slug: groundhog/api/general/validation
section: Groundhog API Reference
description: 'API reference for groundhog.general.validation: 7 functions, 1 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/general/validation.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.general.validation
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/general/validation.html
geocore_available: true
geocore_functions:
- check_layer_overlap
- validate_boolean
- validate_float
- validate_integer
- validate_list
- validate_string
---

Module `groundhog.general.validation` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/general/validation.py).

Upstream documentation: [Validation](https://groundhog.readthedocs.io/en/main/general/validation.html).

**Classes:** [`Validator`](#validator)

**Functions:** [`validate_float`](#validate_float), [`validate_integer`](#validate_integer), [`validate_boolean`](#validate_boolean), [`validate_string`](#validate_string), [`validate_list`](#validate_list), [`map_args`](#map_args), [`check_layer_overlap`](#check_layer_overlap)

<a id="validator"></a>

## class `Validator`

```python
Validator(validationspec, outputonerrorspec)
```

The Validator has the following features

- Automatic handling of validation errors
- Automatic handling of function output upon errors
- Possibility to override the default validation dictionary with custom validation

<a id="validator-__init__"></a>

### `Validator.__init__`

```python
__init__(validationspec, outputonerrorspec)
```

No upstream documentation.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `validationspec` |  |  | required | No upstream documentation. |
| `outputonerrorspec` |  |  | required | No upstream documentation. |

<a id="validate_float"></a>

## `validate_float`

<span class="gc-badge gc-available" data-geocore-function="validate_float">Available in GeoCore</span> [General and utility functions › Validation › validate_float()](/docs/geocore/using/modules#validate_float)

```python
validate_float(var_name, value, min_value=None, max_value=None)
```

Validates whether a variable can be used as a floating point number and whether it is within specified bounds If a value equals one of the bounds, the validation passes

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `var_name` |  |  | required | No upstream documentation. |
| `value` |  |  | required | No upstream documentation. |
| `min_value` |  |  | `None` | No upstream documentation. |
| `max_value` |  |  | `None` | No upstream documentation. |

<a id="validate_integer"></a>

## `validate_integer`

<span class="gc-badge gc-available" data-geocore-function="validate_integer">Available in GeoCore</span> [General and utility functions › Validation › validate_integer()](/docs/geocore/using/modules#validate_integer)

```python
validate_integer(var_name, value, min_value=None, max_value=None)
```

Validates whether a variable can be used as an integer and whether it is within specified bounds If a value equals one of the bounds, the validation passes

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `var_name` |  |  | required | No upstream documentation. |
| `value` |  |  | required | No upstream documentation. |
| `min_value` |  |  | `None` | No upstream documentation. |
| `max_value` |  |  | `None` | No upstream documentation. |

<a id="validate_boolean"></a>

## `validate_boolean`

<span class="gc-badge gc-available" data-geocore-function="validate_boolean">Available in GeoCore</span> [General and utility functions › Validation › validate_boolean()](/docs/geocore/using/modules#validate_boolean)

```python
validate_boolean(var_name, value)
```

Validates whether a variable can be used as a boolean

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `var_name` |  |  | required | No upstream documentation. |
| `value` |  |  | required | No upstream documentation. |

<a id="validate_string"></a>

## `validate_string`

<span class="gc-badge gc-available" data-geocore-function="validate_string">Available in GeoCore</span> [General and utility functions › Validation › validate_string()](/docs/geocore/using/modules#validate_string)

```python
validate_string(var_name, value, options=None, regex=None)
```

Validates whether a variable can be used as a string. The routine also allows checking whether the string is in a list of strings or whether it matches a specific regex pattern

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `var_name` |  |  | required | No upstream documentation. |
| `value` |  |  | required | No upstream documentation. |
| `options` |  |  | `None` | No upstream documentation. |
| `regex` |  |  | `None` | No upstream documentation. |

<a id="validate_list"></a>

## `validate_list`

<span class="gc-badge gc-available" data-geocore-function="validate_list">Available in GeoCore</span> [General and utility functions › Validation › validate_list()](/docs/geocore/using/modules#validate_list)

```python
validate_list(
    var_name,
    value,
    elementtype=None,
    order=None,
    unique=None,
    empty_allowed=None,
)
```

Validates whether a list contains numbers. It allows checking whether these numbers are ascending or descending and whether non-unique values exist

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `var_name` |  |  | required | No upstream documentation. |
| `value` |  |  | required | No upstream documentation. |
| `elementtype` |  |  | `None` | No upstream documentation. |
| `order` |  |  | `None` | No upstream documentation. |
| `unique` |  |  | `None` | No upstream documentation. |
| `empty_allowed` |  |  | `None` | No upstream documentation. |

<a id="map_args"></a>

## `map_args`

```python
map_args(method, var, *args, **kwargs)
```

Constructs a data structure with all parameters, their values and the validation parameters which need to be used during validation.

:returns dictionary var_validation which is a copy of the validation data structure it is possible to override __min and __max arguments

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `method` |  |  | required | The function for which validation will be applied |
| `var` |  |  | required | The validation data structure, entered as argument of the function decorator |
| `args` |  |  |  | function arguments |
| `kwargs` |  |  |  | function keyword arguments |

<a id="check_layer_overlap"></a>

## `check_layer_overlap`

<span class="gc-badge gc-available" data-geocore-function="check_layer_overlap">Available in GeoCore</span> [General and utility functions › Validation › check_layer_overlap()](/docs/geocore/using/modules#check_layer_overlap)

```python
check_layer_overlap(df, raise_error=True, z_from_key=None, z_to_key=None)
```

Checks possible overlap on a dataframe

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `df` | m |  | required | Dataframe with keys 'z from ' and 'z to [m]'. Other keys can be used but then the arguments `z_from_key` and `z_to_key` need to be provided. |
| `raise_error` |  |  | `True` | Boolean determining whether an error needs to be raised or whether a warning is sufficient (default behaviour is to raise an error warning) |
| `z_from_key` |  |  | `None` | Key for start depth of the layer |
| `z_to_key` |  |  | `None` | Key for end depth of the layer |

**Returns**

Default behaviour: raises a warning if there are overlaps or gaps.
