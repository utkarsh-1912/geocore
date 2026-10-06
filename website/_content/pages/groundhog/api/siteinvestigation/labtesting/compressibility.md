---
title: Compressibility
slug: groundhog/api/siteinvestigation/labtesting/compressibility
section: Groundhog API Reference
description: 'API reference for groundhog.siteinvestigation.labtesting.compressibility: 3 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/siteinvestigation/labtesting/compressibility.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.siteinvestigation.labtesting.compressibility
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/site_investigation/compressibility.html
geocore_available: true
geocore_functions:
- logtimemethod
- roottimemethod
---

Module `groundhog.siteinvestigation.labtesting.compressibility` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/siteinvestigation/labtesting/compressibility.py).

Upstream documentation: [Compressibility](https://groundhog.readthedocs.io/en/main/site_investigation/compressibility.html).

**Functions:** [`selectpoints`](#selectpoints), [`roottimemethod`](#roottimemethod), [`logtimemethod`](#logtimemethod)

<a id="selectpoints"></a>

## `selectpoints`

```python
selectpoints(nopoints, timeout=60)
```

No upstream documentation.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `nopoints` |  |  | required | No upstream documentation. |
| `timeout` |  |  | `60` | No upstream documentation. |

<a id="roottimemethod"></a>

## `roottimemethod`

<span class="gc-badge gc-available" data-geocore-function="roottimemethod">Available in GeoCore</span> [Site investigation › Laboratory: Compressibility › Root-Time Method (Coefficient of Consolidation)](/docs/geocore/using/modules#roottimemethod)

```python
roottimemethod(
    times,
    settlements,
    drainagelength,
    initialguess_override=nan,
    xrange=(0, 100),
    showfig=True,
    **kwargs,
)
```

Calculates the root-time construction for determining the coefficient of consolidation for an oedometer test (or any other soil mechanical test involving consolidation).

The following procedure is applied:

#. Plot the displacement gage readings versus square root of times. #. Draw the best straight line through the initial part of the curve intersecting the ordinate (displacement reading) at $O$ and the abscissa ($\sqrt{\text{time}}$) at  $A$. #. Note the time at point $A$; let us say it is $\sqrt{t_A}$. #. Locate a point $B$, $1.15 \sqrt{t_A}$, on the abscissa. #. Join $OB$. #. The intersection of the line $OB$ with the curve, point $C$, gives the displacement gage reading and the time for 90% consolidation ($t_{90}$). You should note that the value read off the abscissa is $\sqrt{t_{90}}$. Now when $U$ = 90%,  $T_v$ = 0.848 and from one-dimensional consolidation equation, we obtain:

$$
c_v = \frac{0.848 H_{dr}^2}{t_{90}}
$$

Because the construction relies heavily on the laboratory data and the judgement of the user, a semi-automated procedure is followed in which the user selects the origin $O$ and point $A$ in an interactive matplotlib plot. Any notebook needs to ensure that matplotlib plots are generated with the `qt` backend using the following magic command:

```python
%matplotlib qt
```

The following input parameters are expected:

![Root-time construction](/docs/assets/groundhog/docs/site_investigation/images/root_time.png)

*Root-time construction*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `times` |  |  | required | Array with time values in seconds, increasing from 0s at the start of the test |
| `settlements` |  |  | required | Array with settlement values, increasing from 0 at the origin. The units are not important as only the time for 90% consolidation is determined. |
| `drainagelength` | m | drainagelength > 0 | required | Drainage length for the consolidation ($H_{dr}$) |
| `initialguess_override` |  | initialguess_override >= 0.0 | `nan` | Override for the initial guess for $\sqrt{t_{90}}$, default=np.nan |
| `xrange` |  |  | `(0, 100)` | No upstream documentation. |
| `showfig` |  |  | `True` | No upstream documentation. |

**References**

- Budhu (2011). Soil mechanics and foundations. John Wiley and Sons.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="logtimemethod"></a>

## `logtimemethod`

<span class="gc-badge gc-available" data-geocore-function="logtimemethod">Available in GeoCore</span> [Site investigation › Laboratory: Compressibility › Log-Time Method (Coefficient of Consolidation)](/docs/geocore/using/modules#logtimemethod)

```python
logtimemethod(
    times,
    settlements,
    drainagelength,
    initialguess_override=nan,
    ignore_warnings=True,
    showfig=True,
    **kwargs,
)
```

Calculates the log-time construction for determining the coefficient of consolidation for an oedometer test (or any other soil mechanical test involving consolidation).

The following steps need to be performed:

#. Project the straight portions of the primary consolidation and secondary compression to intersect at $A$. The ordinate of A, $d_{100}$, is the displacement gage reading for 100% primary consolidation. #. Correct the initial portion of the curve to make it a parabola. Select a time $t_1$, point $B$, near the head of the initial portion of the curve ($U < 60%$) and then another time $t_2$, point $C$, such that $t_2$ = 4 $t_1$. #. Calculate the difference in displacement reading, $\Delta d = d_2 - d_1$, between $t_2$ and $t_1$. Plot a point $D$ at a vertical distance $\Delta d$ from $B$. The ordinate of point $D$ is the corrected initial displacement gage reading, $d_o$, at the beginning of primary consolidation. #. Calculate the ordinate for 50% consolidation as $d_{50} = (d_{100} + d_o)/2$. Draw a horizontal line through this point to intersect the curve at $E$. The abscissa of point $E$ is the time for 50% consolidation, $t_{50}$. #. You will recall that the time factor for 50% consolidation is 0.197, and from the one-dimensional consolidation equation we obtain:

$$
c_v = \frac{0.197 H_{dr}^2}{t_{50}}
$$

Because the construction relies heavily on the laboratory data and the judgement of the user, a semi-automated procedure is followed in which the user first selects two points on primary consolidation part, then two points on the secondary consolidation part and finally a point B close to the origin of the curve. Any notebook needs to ensure that matplotlib plots are generated with the `qt` backend using the following magic command:

```python
%matplotlib qt
```

The following input parameters are expected:

![Log-time construction](/docs/assets/groundhog/docs/site_investigation/images/log_time.png)

*Log-time construction*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `times` |  |  | required | Array with time values in seconds, increasing from 0s at the start of the test |
| `settlements` |  |  | required | Array with settlement values, increasing from 0 at the origin. The units are not important as only the time for 90% consolidation is determined. |
| `drainagelength` | m | drainagelength > 0 | required | Drainage length for the consolidation ($H_{dr}$) |
| `initialguess_override` |  | initialguess_override >= 0.0 | `nan` | Override for the initial guess for $\sqrt{t_{100}}$, default=np.nan |
| `ignore_warnings` |  |  | `True` | No upstream documentation. |
| `showfig` |  |  | `True` | No upstream documentation. |

**References**

- Budhu (2011). Soil mechanics and foundations. John Wiley and Sons.

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
