---
title: Demo - De Beer pile resistance calculation
slug: groundhog/tutorials/demo-de-beer-pile-resistance-calculation
section: Groundhog Guides
description: In this demo, the pile shaft and base resistance is calculation according to De Beer's method (Belgian practice).
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/notebooks/Demo%20-%20De%20Beer%20pile%20resistance%20calculation.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted, with a short note on how to run this in GeoCore prepended.'
notebook: notebooks/Demo - De Beer pile resistance calculation.ipynb
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, run the same calculation through a [calculation form](/docs/geocore/using/modules) or by asking **GeoAI**, which calls the same groundhog function through its validated Tool Registry. This notebook is kept for anyone who wants to call groundhog directly from their own Python code instead.

In this demo, the pile shaft and base resistance is calculation according to De Beer's method (Belgian practice).

## Library imports

We will import the necessary libraries first.

```python
import numpy as np
import os
from IPython.display import HTML
import pandas as pd
```

```python
from plotly import tools, subplots
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
import plotly.figure_factory as ff
from plotly.colors import DEFAULT_PLOTLY_COLORS
from plotly.offline import init_notebook_mode
init_notebook_mode()
pio.templates.default = 'plotly_white'
```

```python
from groundhog.deepfoundations.axialcapacity.debeer import DeBeerCalculation
from groundhog.siteinvestigation.insitutests.pcpt_processing import PCPTProcessing
from groundhog.general.soilprofile import SoilProfile
```

## Pile capacity

Eurocode 7 in Belgium is applied with pile capacity calculated with De Beer's method. We can apply this method to provide the entry values for the Eurocode 7 factoring procedure. With need to calculate the pile capacity for each CPT trace.

### Pile base capacity

#### Unit end bearing

The unit end bearing is calculated by processing the CPT trace using the De Beer end bearing calculation encoded in the Python package ```groundhog```.

De Beer's method accounts for scaling from a CPT to a pile in a rigorous manner. The CPT is treated as a model pile and the following effects are corrected for:

   - The pile "feels" the presence of the free surface up to deeper depths
   - The stress level on the failure surface induced by the pile is higher than on that for the CPT
   - The pile "feels" the effects of stronger and weaker layers before the CPT does

We can run the calculation and derive the value of unit end bearing $ q_{DeBeer} $ at 12m depth.

First, we can load the CPT data.

```python
cpt = PCPTProcessing(title="CPT")
cpt.load_excel("Data/Koppejan_DeBeer_demo.xlsx")
```

The CPT data can be plotted:

```python
cpt.plot_raw_pcpt(qc_range=(0, 20), qc_tick=2)
```

We can now create a De Beer calculation for a 0.4m diameter pile:

```python
debeer_cpt = DeBeerCalculation(
    depth=cpt.data["z [m]"],
    qc=cpt.data["qc [MPa]"],
    diameter_pile=0.4)
```

We shouldn't forget to resample the data to a 20cm grid, since De Beer's method is based on data obtained with the mechanical cone.

```python
debeer_cpt.resample_data(spacing=0.2)
```

Based on the CPT visualisation, a layering can be assigned to both traces. Note that the soil types have to be the ones defined in Table 4 of the paper <i>Design of piles - Belgian practice</i>.

```python
soilprofile = SoilProfile({
    "Depth from [m]": [0, 2, 8.5],
    "Depth to [m]": [2, 8.5, 14],
    'Soil type': ['Sand', 'Clay', 'Sand']
})
debeer_cpt.set_soil_layers(soilprofile)
```

De Beer's algorithm is then simply executed using the ```groundhog``` code:

```python
debeer_cpt.calculate_base_resistance()
```

The unit base resistance at 12m depth can be interpolated from the results:

```python
qb = np.interp(12, debeer_cpt.depth_qb, debeer_cpt.qb)
qb
```

The construction can be plotted:

```python
debeer_cpt.plot_base_resistance(selected_depth=12)
```

```python
HTML("""
The unit end bearing is %.2fMPa.""" % (qb))
```

#### Pile base area

The pile is an open-ended tubular pile and the questions arises whether the pile is plugged or unplugged. Because the pile terminates in sand and research has shows that arching effects lead to plugging in sand, we can assume that the pile will be plugged. Therefore the base area is simply the full cross-sectional area of the pile.

```python
DIAMETER = 0.4  # m
area_base = 0.25 * np.pi * (DIAMETER ** 2.0)
HTML("The base area $ A_{base} $ = %.3fm$^2$" % area_base)
```

#### Toe quality and soil type

The pile terminates in sand, which is not the tertiary clay mentioned in the table with values for $ \alpha_b $. 

We have a steel open-ended pile with plugging. We can read from the table that $ \alpha_b $ = 1, both for tertiary clay and other soil types. For this pile type, the shaft factor $ \alpha_s $ = 0.6 for all soil types. We can set these factors for the pile calculations:

```python
alpha_b = 1
debeer_cpt.set_shaft_base_factors(
    alpha_b_tertiary_clay=alpha_b, alpha_b_other=alpha_b,
    alpha_s_tertiary_clay=0.6, alpha_s_other=0.6)
```

#### Scale-dependent soil shear strength

We are not in tertiary overconsolidated clay, so we can take $ \epsilon_b $ = 1. The methods of ```DeBeerCalculation``` check for this in each layer automatically.

```python
epsilon_b = 1.0
```

#### Toe shape in the horizontal plane

The toe shape is circular, so the coefficient $ \beta $ is also equal to 1.

```python
beta_b = 1.0
```

#### Toe shape in the vertical plane

The pile does not have an enlarged base and therefore the coefficient $ \lambda $ is simply equal to 1.

```python
lambda_b = 1.0
```

#### Base capacity

With all coefficients being defined, we can calculate the base capacity for each pile:

$$ R_b = \alpha_b \cdot \epsilon_b \cdot \beta \cdot \lambda \cdot A_b \cdot q_{DeBeer} $$

We can calculate the base resistance.

```python
Rb = alpha_b * epsilon_b * beta_b * lambda_b * area_base * (1000.0 * qb) # kN

HTML("""
The base resistance from the CPT trace $ R_{b} $ = %.1fkN""" % (Rb))
```

### Shaft capacity

The shaft capacity can be calculated with the following formula:

$$ R_s = \chi_s \cdot \sum \alpha_s \cdot \Delta h_i \cdot q_s $$

To apply this formula, we need to subdivide the $ q_c $ trace in layers with thicknesses $ \Delta h_i $ and determine the average $ q_c $ in each layer. We can then apply the conversion from $ q_c $ to unit skin friction $ q_c $ according to Table 1.

<br><center><b>Table 1: Conversion from $ q_c $ to $ q_s $</b></center>
<img src="/docs/assets/groundhog/notebooks/Images/skin_friction_DeBeer.png" width=600>

#### Layering and cone resistance averaging

The layering is already included in the ```DeBeerCalculation``` objects. We can simply execute the ```calculate_average_qc``` method. For, a correction of the cone resistance values for the cone type is carried out (See Table 1 of the publication <i>Design of piles - Belgian practice</i>).

Note that we will automate the calculations by looping over the ```DeBeerCalculation``` objects and executing the calculations for each one. This prevents us from having to write this code twice. This becomes especially useful when a large number of CPTs are being considered for the pile resistance calculation.

```python
debeer_cpt.correct_shaft_qc(cone_type='E')
debeer_cpt.calculate_average_qc()
debeer_cpt.calculate_unit_shaft_friction()
```

The unit shaft friction can be plotted vs depth.

```python
debeer_cpt.plot_unit_shaft_friction()
```

The shaft capacity is now obtained by integrating the unit shaft friction in each layer over the depth and the circumference.

The method ```calculate_pile_resistance``` performs this automatically and returns the pile resistance.

```python
debeer_cpt.calculate_pile_resistance(
    pile_penetration=12,
    base_area=area_base,
    circumference=np.pi * DIAMETER,
    beta_base=beta_b, lambda_base=lambda_b)
```

To verify the calculation numerically, we can show the calculation table for each CPT. The attribute ```layering``` contains the calculation of shaft resistance per layer.

```python
debeer_cpt.layering
```

The pile base, shaft and total calculated capacity can then be obtained from the calculation objects and printed to a table.

```python
HTML(
"""
Calculated shaft resistance is %.1fkN, Calculated base resistance is %.1fkN,
Calculated total resistance is %.1fkN, 
""" % (debeer_cpt.Rs, debeer_cpt.Rb, debeer_cpt.Rc))
```
