---
title: Demo - Pile base resistance calculation according to De Beer's method
slug: groundhog/tutorials/demo-de-beer-unit-base-resistance-calculation
section: Groundhog Guides
description: A tutorial for the application of De Beer's method is given in this notebook.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/notebooks/Demo%20-%20De%20Beer%20unit%20base%20resistance%20calculation.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted.'
notebook: notebooks/Demo - De Beer unit base resistance calculation.ipynb
---

A tutorial for the application of De Beer's method is given in this notebook. This notebook can be used to apply to other CPT profiles and possibly make modifications to gain further insight in the data and solutions.

## Loading Python libraries

This notebook makes use of the ```groundhog``` Python library to load and manipulate data, visualise data and execute geotechnical calculations. The installation of these libraries is described in the [groundhog installation guide](http://snakesonabrain.com/docs/groundhog/gettingstarted.html).

```python
# Import of standard libraries for data manipulation
import numpy as np
import os
from IPython.display import HTML
import pandas as pd
```

```python
# Import of plotting libraries
from plotly import tools, subplots
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
import plotly.figure_factory as ff
from plotly.colors import DEFAULT_PLOTLY_COLORS
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode()
pio.templates.default = 'plotly_white'
pio.templates['plotly'].layout['autosize'] = False
for key in pio.templates.keys():
    pio.templates[key].layout['autosize'] = False
```

```python
# Import of geotechnical libraries
from groundhog.siteinvestigation.insitutests.pcpt_processing import PCPTProcessing
from groundhog.general.soilprofile import SoilProfile
```

The pile base resistance method according to De Beer is routinely applied in Belgian geotechnical practice to determine the base resistance of piles. The methods is based on scaling the results of CPT cone resistance data to the size of the full pile. Due to the increased size of the pile compared to the CPT, it will average out the resistance measured by the cone. Stronger layers will be mobilised more slowly and weaker layers will be <i>felt</i> later by the pile.

<img src="/docs/assets/groundhog/notebooks/Images/debeer_scaling.png" width=500>
<br><center><b>Figure 1: Illustration of critical depth differences when scaling from CPT to pile</b></center>

## Loading CPT data

The CPT data can be loaded from the Excel file ```Koppejan_DeBeer_demo.xlsx```. The data can be visualised. Only cone tip resistance data is available.

```python
cpt = PCPTProcessing(title='De Beer')
cpt.load_excel("Data/Koppejan_DeBeer_demo.xlsx")
cpt.plot_raw_pcpt(qc_range=(0, 20))
```

## Setting up the base resistance calculation according to De Beer

The ```groundhog``` Python library contains a ```DeBeerCalculation``` class which implements the cone resistance correction and averaging methods. When initialising the calculation, the depth values, the cone resistance values and the diameter of the pile need to be provided.

```python
from groundhog.deepfoundations.axialcapacity.debeer import DeBeerCalculation
```

```python
calc = DeBeerCalculation(
    depth=cpt.data['z [m]'],
    qc=cpt.data['qc [MPa]'],
    diameter_pile=0.5)
```

De Beer’s method was developed for mechanical cones with data at 0.2m intervals. If data is supplied on a finer grid, the resample_data method needs to be applied, which resamples the data to the desired spacing.

In this notebook, you can investigate the effect of different sampling intervals to see the effect on the calculated unit base resistance.

```python
calc.resample_data(spacing=0.2)
```

## Soil layering

We need to specify a soil layering to allow the calculation of vertical effective stress and further axial shaft resistance calculations using the methods according to Belgian practice. Note the the soil types are slightly different and need to be specified in according with Table 4 of the paper <i>Design of piles - Belgian practice</i>.

```python
layering = SoilProfile({
    "Depth from [m]": [0, 2, 8.5],
    "Depth to [m]": [2, 8.5, 14],
    'Soil type': ['Sand', 'Clay', 'Sand']
})
```

This soil layering can be attached to the ```DeBeerCalculation``` object.

```python
calc.set_soil_layers(layering)
```

## 4. Base resistance calculation

The base resistance calculation is then carried out by simply applying the method calculate_base_resistance on the calculation object. This method performs the three-step CPT averaging procedure with a stress correction, diameter correction and upward correction. Optionally, the correction according to Van Impe (which is less conservative) can be applied by setting the boolean ```vanimpecorrection``` to True.

The method calculates the based resistance $ q_b $ which can be used for further calculation. Note that the calculation might raise a warning as zero divisions are encountered for very shallow depth (where no $ q_c $ data is available).

Not that the complexity of the calculations are hidden inside the routine. The theoretical background of these calculations needs to be known for the geotechnics course.

```python
calc.calculate_base_resistance()
```

The $ q_b $ trace can be plotted.

```python
from groundhog.general.plotting import LogPlot
```

```python
# Plot the cone resistance trace
qb_plot = LogPlot(layering, no_panels=1, fillcolordict={'Sand': 'yellow', 'Clay': 'brown'})
qb_plot.add_trace(
    x=cpt.data['qc [MPa]'],
    z=cpt.data['z [m]'],
    name='qc',
    showlegend=True,
    panel_no=1)
qb_plot.add_trace(
    x=calc.qb,
    z=calc.depth_qb,
    name='qb',
    showlegend=True,
    panel_no=1)
qb_plot.set_xaxis(title=r'$ q_c, \ q_b \ \text{[MPa]} $', panel_no=1, range=(0, 20))
qb_plot.set_zaxis(title=r'$ z \ \text{[m]} $', range=(15, 0))
qb_plot.set_size(width=600, height=600)
qb_plot.show()
```

## Base resistance at pile tip

The base resistance at the pile tip can be interpolated. This value is lower than the value calculated with Koppejan's method.

```python
HTML("""
The base resistance at the pile tip = %.2fMPa.""" % (np.interp(12, calc.depth_qb, calc.qb)))
```
