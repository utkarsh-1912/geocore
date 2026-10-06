---
title: Pile testing functionality
slug: groundhog/api/deepfoundations/axialcapacity/piletesting
section: Groundhog API Reference
description: 'API reference for groundhog.deepfoundations.axialcapacity.piletesting: 1 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/deepfoundations/axialcapacity/piletesting.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.deepfoundations.axialcapacity.piletesting
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/piles/piletesting.html
geocore_available: true
geocore_functions:
- piletest_chinkondler
---

Module `groundhog.deepfoundations.axialcapacity.piletesting` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/deepfoundations/axialcapacity/piletesting.py).

Upstream documentation: [Pile testing functionality](https://groundhog.readthedocs.io/en/main/piles/piletesting.html).

**Functions:** [`piletest_chinkondler`](#piletest_chinkondler)

<a id="piletest_chinkondler"></a>

## `piletest_chinkondler`

<span class="gc-badge gc-available" data-geocore-function="piletest_chinkondler">Available in GeoCore</span> [Pile calculations › Pile testing functionality › Chin-Kondler Extrapolation](/docs/geocore/using/modules#piletest_chinkondler)

```python
piletest_chinkondler(
    loads,
    settlements,
    no_discard_points=1,
    max_settlement=50,
    selected_settlement=40,
    show_fig=True,
    **kwargs,
)
```

Extrapotates a pile head load-settlement curve based on the procedure by Chin-Kondler. The settlements are divided by the corresponding loads. This yields a straight line in a graph of this fraction vs settlement. The user selects how many points to discard and the fitting happens using `np.polyfit`. An extrapolated load-settlement curve is calculated and plotted for the user to check the results.

$$
\frac{s}{Q} = a + b \cdot s
$$

$$
Q_{\text{ult}} = 1 / b
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `loads` | kN |  | required | List of loads recorded during the load test. Note that unload-reload loops should be removed before running the algorithm ($Q$) |
| `settlements` | mm |  | required | List of settlements recorded during the load test. Should be the same length as the list with loads ($s$) |
| `no_discard_points` |  | no_discard_points >= 0 | `1` | Number of points at the start of the curve to discard for the fitting of the straight line. |
| `max_settlement` | mm | 0.0 <= max_settlement <= 1000.0 | `50` | Maximum settlement used for plotting the reconstructed pile head load-settlement curve . Optional, default=50mm. ($s_{max}$) |
| `selected_settlement` | kN | 0.0 <= selected_settlement <= 1000.0 | `40` | Settlement as which pile capacity is calculated (e.g. 10% of OD) . Optional, default=40mm. ($Q_{s=s_{\text{selected}}}$) |
| `show_fig` |  |  | `True` | Boolean determining whether the figures for the Chin-Kondler construction need to be plotted (default behaviour) or returned in the output dictionary. |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `intercept [mm/kN]` | mm/kN | Coefficient $a$ from the linear regression [mm/kN] |
| `slope [1/kN]` | 1/kN | Slope $b$ for the linear regression [1/kN] |
| `Correleation coefficient [-]` | - | Pearson correlation coefficient for the points used for the construction. |
| `Qmax [kN]` | kN | Ultimate pile resistance (fully mobilised shaft and base) [kN] ($Q_{\text{ult}}$) |
| `Qdisp [kN]` | kN | Pile resistance at the selected displacement level (e.g. 10% of OD) [kN] ($Q_{s=s_\text{selected}}$) |
| `Settlements [mm]` | mm | List with settlements for the load-displacement reconstruction [mm] |
| `Q [kN]` | kN | List with loads for the load-displacement reconstruction [kN] |
| `construction_fig` |  | Figure with the linear regression construction (for inspection of the goodness-of-fit) |

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
