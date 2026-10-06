---
title: Pile lateral behaviour
slug: groundhog/api/deepfoundations/lateralresponse/lateral
section: Groundhog API Reference
description: 'API reference for groundhog.deepfoundations.lateralresponse.lateral: 2 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/deepfoundations/lateralresponse/lateral.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.deepfoundations.lateralresponse.lateral
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/piles/lateral.html
geocore_available: true
geocore_functions:
- pilegroupeffect_reesevanimpe
- reinforced_circularsection_inertia
---

Module `groundhog.deepfoundations.lateralresponse.lateral` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/deepfoundations/lateralresponse/lateral.py).

Upstream documentation: [Pile lateral behaviour](https://groundhog.readthedocs.io/en/main/piles/lateral.html).

**Functions:** [`reinforced_circularsection_inertia`](#reinforced_circularsection_inertia), [`pilegroupeffect_reesevanimpe`](#pilegroupeffect_reesevanimpe)

<a id="reinforced_circularsection_inertia"></a>

## `reinforced_circularsection_inertia`

<span class="gc-badge gc-available" data-geocore-function="reinforced_circularsection_inertia">Available in GeoCore</span> [Pile calculations › Pile lateral behaviour › Reinforced Circular Section Inertia](/docs/geocore/using/modules#reinforced_circularsection_inertia)

```python
reinforced_circularsection_inertia(
    diameter,
    modulus_ratio,
    n_bars,
    offset,
    rebar_diameter,
    maximum_resistance=True,
    **kwargs,
)
```

Calculates the combined inertia of a circular section, reinforced with rebar rods at equal center-to-center distance from the concrete section center. Steiner's theorem is applied using the center-to-center distance between the center of the concrete section and the center of the rebar rod. The positioning of the rebar rods for maximum or minimum bending resistance can be taken. Their offset from the bending axis can then be derived.

$$
I_s = \frac{\pi d^4}{64}
$$

$$
A_s = \frac{\pi d^2}{4}
$$

$$
A_{\text{s,transformed}} = n \cdot A_s
$$

$$
I_c = \frac{\pi D^4}{64}
$$

$$
I_{\text{combined}} = I_c + \sum_{i=1}^N \left( I_s + A_{\text{s,transformed}} r^2 \right)
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `diameter` | m | diameter >= 0.0 | required | Diameter of the concrete section ($D$) |
| `modulus_ratio` | - | modulus_ratio >= 0.0 | required | Ratio of Young's modulus of steel to Young's modulus of concrete ($n$) |
| `n_bars` | - | n_bars >= 1.0 | required | Number of rebar rods ($N$) |
| `offset` | m | offset >= 0.0 | required | Center-to-center distance between rebar rods and concrete section center ($r$) |
| `rebar_diameter` | m | rebar_diameter >= 0.0 | required | Diameter of the rebar rods ($d$) |
| `maximum_resistance` |  |  | `True` | Determines whether the rebar rods should be positioned for maximum bending resistance (if true) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `Start angle [deg]` | deg | Angle between the bending axis and the first rebar rod [deg] |
| `Rebar angles [deg]` | deg | Angles between rebar rods and the bending axis [deg] |
| `Offsets [m]` | m | Offsets of the rebar rods to the bending axis [m] |
| `Rebar inertia [m4]` | m4 | Total inertia of the rebar [m4] ($\sum_{i=1}^N \left( I_s + A_s r^2 \right)$) |
| `Ic [m4]` | m4 | Concrete section inertia [m4] |
| `I combined [m4]` | m4 | Combined inertia of the reinforced section [m4] |

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.

<a id="pilegroupeffect_reesevanimpe"></a>

## `pilegroupeffect_reesevanimpe`

<span class="gc-badge gc-available" data-geocore-function="pilegroupeffect_reesevanimpe">Available in GeoCore</span> [Pile calculations › Pile lateral behaviour › Pile Group Effect (Reese & Van Impe)](/docs/geocore/using/modules#pilegroupeffect_reesevanimpe)

```python
pilegroupeffect_reesevanimpe(
    pile_x,
    pile_y,
    pile_diameters,
    load_x,
    load_y,
    show_fig=True,
    plot_height=600,
    plot_width=400,
    **kwargs,
)
```

When piles are arranged in a group, they influence one another and the lateral reaction for a given displacement can be less than that for a single pile. Reese and Van Impe suggest a method for calculating the efficiency of each pile. A distinction is made between in-line leading piles, in-line trailing piles and side-by-side piles. Based on the direction of loading and inter-pile distance, a reduction factor (p-multiplier) is calculated for each pile pair. The efficiency factors for each pile pair are multiplied to provide the overall efficiency for the pile considered. In this function, the centers of the piles are defined using their (X,Y) coordinates. The direction of loading is defined using the X- and Y-component of the loading vector. Note that the magnitude of this loading vector (norm) does not play a role in the calculation. The diameter of the pile is also required to determine the normalised pile spacing. For piles which is neither perfectly inline or side-by-side, the inline and side-by-side efficiencies are combined using the angle to the loading direction.

$$
\text{Side by side piles: } e = 0.64 \left( \frac{s}{D} \right)^{0.34} \text{ for } 1 \leq \frac{s}{D} \leq 3.75, e=1 \text{ for } \frac{s}{D} > 3.75
$$

$$
\text{In-line leading piles: } e = 0.70 \left( \frac{s}{D} \right)^{0.26} \text{ for } 1 \leq \frac{s}{D} \leq 4 , e=1 \text{ for } \frac{s}{D} > 4
$$

$$
\text{In-line trailing piles: } e = 0.48 \left( \frac{s}{D} \right)^{0.38} \text{ for } 1 \leq \frac{s}{D} \leq 7 , e=1 \text{ for } \frac{s}{D} > 7
$$

$$
\text{Oblique orientation: } e = \sqrt{e_{\text{inline}}^2 \cos^2 \varphi + e_{\text{side-by-side}}^2 \sin^2 \varphi}
$$

$$
p_{\text{group}} = p_{\text{single}} e_{\text{combined}} = p_{\text{single}} \Pi_j e_j
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `pile_x` | m |  | required | List of X-coordinates of the pile centers ($x$) |
| `pile_y` | m |  | required | List of Y-coordinates of the pile centers ($y$) |
| `pile_diameters` | m |  | required | List of pile diameters ($y$) |
| `load_x` |  |  | required | X-component of the load vector ($x_{\text{load}}$) |
| `load_y` |  |  | required | Y-component of the load vector ($x_{\text{load}}$) |
| `show_fig` |  |  | `True` | Boolean determining whether the figures for the Chin-Kondler construction need to be plotted (default behaviour) or returned in the output dictionary. |
| `plot_height` |  |  | `600` | No upstream documentation. |
| `plot_width` |  |  | `400` | No upstream documentation. |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `efficiency_matrix` |  | Matrix with the efficiency of each pile vis-à-vis the others (row i, column j quantifies the influence of pile j on pile i) |
| `efficiencies` |  | List with the combined efficiencies of each pile (list with an element for each pile) |
| `pile_fig` |  | Figure with the dimensions of the piles. |

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
