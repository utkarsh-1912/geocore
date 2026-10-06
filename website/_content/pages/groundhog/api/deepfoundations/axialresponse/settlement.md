---
title: Pile settlement
slug: groundhog/api/deepfoundations/axialresponse/settlement
section: Groundhog API Reference
description: 'API reference for groundhog.deepfoundations.axialresponse.settlement: 1 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/deepfoundations/axialresponse/settlement.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.deepfoundations.axialresponse.settlement
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/piles/settlement.html
geocore_available: true
geocore_functions:
- PileSettlementCurves
---

Module `groundhog.deepfoundations.axialresponse.settlement` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/deepfoundations/axialresponse/settlement.py).

Upstream documentation: [Pile settlement](https://groundhog.readthedocs.io/en/main/piles/settlement.html).

**Functions:** [`pile_settlement_curves`](#pile_settlement_curves)

<a id="pile_settlement_curves"></a>

## `pile_settlement_curves`

<span class="gc-badge gc-available" data-geocore-function="PileSettlementCurves">Available in GeoCore</span> [Pile calculations › Pile settlement › Pile Settlement Curves](/docs/geocore/using/modules#pilesettlementcurves)

```python
pile_settlement_curves(diameter, shaft_resistance, base_resistance, pile_type, **kwargs)
```

Calculates the pile settlement curve for pile shaft and pile base from empirical trends established based on axial pile load tests. These curves take into account the pile type (driven, bored or CFA) and the fact that shaft resistance mobilisation distance does not appear to be proportional to the pile diameter, while the base resistance mobilisation distance is. The empirical curves are approximated by a mathematical relation. The function returns both the normalised and denormalised curves. Not that the function returns the pile settlement in m which the empirical shaft mobilisation curves mention mm.

Finally, the overall curve is calculated by summing both curves

$$
F_{mob} = a + \frac{b-a}{1 + \left( \frac{\delta_{pile} \ \text{or} \ \delta_{pile}/D}{c} \right)^d}
$$

![Normalised shaft and base resistance mobilisation curves](/docs/assets/groundhog/docs/piles/images/pile_settlement_curves_1.png)

*Normalised shaft and base resistance mobilisation curves*

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `diameter` | m | diameter >= 0.0 | required | Pile diameter ($D$) |
| `shaft_resistance` | kN | shaft_resistance >= 0.0 | required | Shaft resistance used to denormalise the curve ($F_s$) |
| `base_resistance` | kN | base_resistance >= 0.0 | required | Base resistance used to denormalise the curve ($F_b$) |
| `pile_type` |  | one of `driven`, `CFA`, `bored` | required | Pile type - Options: ('driven', 'CFA', 'bored') |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `shaft_normalised` |  | Normalised shaft mobilisation curve as a dictionary with keys 'w [m]' and 'Fs/Fsmax [-]' |
| `shaft_denormalised` |  | Shaft mobilisation curve as a dictionary with keys 'w [m]' and 'Fs [kN]' |
| `base_normalised` |  | Normalised base mobilisation curve as a dictionary with keys 'w/D [-]' and 'Fb/Fbmax [-]' |
| `base_denormalised` |  | Base mobilisation curve as a dictionary with keys 'w [m]' and 'Fb [kN]' |
| `total` |  | Pile tip settlement vs total load with keys 'w [m]' and 'F [kN]' |

**References**

- Syllabus geotechnics

*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its error output (typically `NaN` values) instead of raising.
