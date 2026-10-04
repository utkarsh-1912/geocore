---
title: Parameter selection
slug: groundhog/api/standards/eurocode7/parameter_selection
section: Groundhog API Reference
description: 'API reference for groundhog.standards.eurocode7.parameter_selection: 2 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/standards/eurocode7/parameter_selection.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.standards.eurocode7.parameter_selection
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/standards/parameter_selection.html
geocore_available: true
geocore_functions:
- parameter_selection_constant_value
- parameter_selection_linear_trend
---

Module `groundhog.standards.eurocode7.parameter_selection` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/standards/eurocode7/parameter_selection.py).

Upstream documentation: [Parameter selection](https://groundhog.readthedocs.io/en/main/standards/parameter_selection.html).

**Functions:** [`constant_value`](#constant_value), [`linear_trend`](#linear_trend)

<a id="constant_value"></a>

## `constant_value`

<span class="gc-badge gc-available" data-geocore-function="parameter_selection_constant_value">Available in GeoCore</span> [EuroCode7 › Parameter selection › Characteristic Value (Constant)](/docs/geocore/using/modules#parameter_selection_constant_value)

```python
constant_value(data, mode='Low', cov=nan, confidence=0.95, **kwargs)
```

Selects the characteristic value from a set of measurements using Eurocode 7 rules. For a local low value, the 5% fractile is taken. For a mean value, a 95% confidence value or the mean is taken. The selection process assumes that the parameter under consideration is stationary and is normally distributed. For lognormally distributed parameters a transformation to the logarithm is required.

$$
X_k = X_{mean} \cdot \left( 1 - k_n \cdot V_x \right)
$$

$$
V_x \text{unknown}: k_{n,mean} = t_{n-1}^{0.95} \sqrt{ \frac{1}{n} }, \ k_{n,low} = t_{n-1}^{0.95} \sqrt{ \frac{1}{n} + 1}
$$

$$
V_x \text{known}: k_{n,mean} = 1.64 \sqrt{ \frac{1}{n} }, \ k_{n,low} = 1.64 \sqrt{ \frac{1}{n} + 1}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `data` |  |  | required | List or numpy array with the measurements. The number of measurements is derived from the length. |
| `mode` |  | one of `Low`, `Mean` | `'Low'` | Determines whether a local low value `"Low"` or mean vaue `"Mean"` needs to be taken |
| `cov` |  | 0 <= cov <= 10.0 | `nan` | Coefficient of variation (given as the ratio of standard deviation to the mean, not in percent). If CoV is unknown, leave blank. ($V_x = \sigma / \mu$) |
| `confidence` |  | 0.1 <= confidence <= 0.99999 | `0.95` | Confidence level used for calculations (default = 95%) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `n` |  | Number of datapoints |
| `t_nminus1` |  | Student-t factor |
| `kn` |  | kn value |
| `Xk` |  | Characteristic value of the parameter under consideration |

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="linear_trend"></a>

## `linear_trend`

<span class="gc-badge gc-available" data-geocore-function="parameter_selection_linear_trend">Available in GeoCore</span> [EuroCode7 › Parameter selection › Characteristic Value (Linear Trend)](/docs/geocore/using/modules#parameter_selection_linear_trend)

```python
linear_trend(data, depths, requested_depths, mode='Low', confidence=0.95, **kwargs)
```

Selects the characteristic value from a set of measurements using Eurocode 7 rules. A linear trend is assumed in the data. For a local low value, the 5% fractile is taken. For a mean value, a 95% confidence value or the mean is taken. The selection process assumes that the parameter under consideration is stationary and, when de-trended, is normally distributed. For lognormally distributed parameters a transformation to the logarithm is required.

$$
x^{*} = \bar{x} + b ( z - \bar{z} )
$$

$$
\bar{x} = \frac{1}{n} \left( x_1 + x_2 + ... + x_n \right)
$$

$$
\bar{z} = \frac{1}{n} \left( z_1 + z_2 + ... + z_n \right)
$$

$$
b = \frac{\sum_{i=1}^n (x_i - \bar{x}) (z_i - \bar{z})}{\sum_{i=1}^n (z_i - \bar{z})^2}
$$

$$
\text{Mean value}
$$

$$
s_1 = \sqrt{ \frac{1}{n-2} \left( \frac{1}{n} + \frac{(z- \bar{z})^2}{\sum_{i=1}^{n} (z_i - \bar{z})^2} \right) \sum_{i=1}^n \left[ (x_i - \bar{x}) - b (z_i - \bar{z}) \right]^2 }
$$

$$
X_k = \left[ \bar{x} + b (z - \bar{z}) \right] - t_{n-2}^{0.95} s_1
$$

$$
\text{Local low value}
$$

$$
s_2 = \sqrt{ \frac{1}{n-2} \left(1+ \frac{1}{n} + \frac{(z- \bar{z})^2}{\sum_{i=1}^{n} (z_i - \bar{z})^2} \right) \sum_{i=1}^n \left[ (x_i - \bar{x}) - b (z_i - \bar{z}) \right]^2 }
$$

$$
X_k = \left[ \bar{x} + b (z - \bar{z}) \right] - t_{n-2}^{0.95} s_2
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `data` |  |  | required | List or numpy array with the measurements. The number of measurements is derived from the length. |
| `depths` |  |  | required | List or numpy array with the depths. The number of depths needs to be identical to the number of measurements. |
| `requested_depths` |  |  | required | List or numpy array with the depths where the characteristic value is requested. |
| `mode` |  | one of `Low`, `Mean` | `'Low'` | Determines whether a local low value `"Low"` or mean vaue `"Mean"` needs to be taken |
| `confidence` |  | 0.1 <= confidence <= 0.99999 | `0.95` | Confidence level used for calculations (default = 95%) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `n` |  | Number of datapoints |
| `t_nminus1` |  | Student-t factor |
| `kn` |  | kn value |
| `Xk` |  | Characteristic values (Numpy array) of the parameter under consideration at the requested depths |

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
