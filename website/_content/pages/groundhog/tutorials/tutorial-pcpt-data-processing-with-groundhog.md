---
title: Tutorial - PCPT data processing with Groundhog
slug: groundhog/tutorials/tutorial-pcpt-data-processing-with-groundhog
section: Groundhog Guides
description: A PCPT processing tool has been created within the
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/notebooks/Tutorial%20-%20PCPT%20data%20processing%20with%20Groundhog.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted.'
notebook: notebooks/Tutorial - PCPT data processing with Groundhog.ipynb
---

A PCPT processing tool has been created within the ```groundhog``` package. This tool is made available to allow rapid import of PCPT data, basic processing and checking of the sensitivity to processing parameters. Moreover, correlations between PCPT properties and other soil mechanical parameters an easily be applied.

In this tutorial, the processing of PCPT data is covered.

```python
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

In this tutorial, we will also make use of the ```SoilProfile``` class which encodes functionality for soil profile processing.

```python
from groundhog.siteinvestigation.insitutests.pcpt_processing import PCPTProcessing
from groundhog.general.soilprofile import SoilProfile
```

## PCPT import

We will work with PCPT data specified in an Excel file.

The data is loaded using the ```load_excel``` method. A dataframe is be created from Excel data and added as the ```.data``` attribute of the PCPTProcessing object. Note that $ q_c $, $ f_s $ and $ u_2 $ need to have the dimension MPa. If they don't multipliers can be specified to convert them to these dimensions.

```python
pcpt = PCPTProcessing(title="Example PCPT Excel")
```

```python
pcpt.load_excel(path="Data/excel_example.xlsx",
    u2_key="u [kPa]", u2_multiplier=0.001)
pcpt.data.head()
```

The raw PCPT data can be visualized with the ```plot_raw_pcpt``` method.

```python
pcpt.plot_raw_pcpt()
```

## Setting cone and layer properties

The cone and layer properties can be set based on the cone used and the layering identified. A ```SoilProfile``` object can be created for these properties. A basic structure with cone properties is available in the ```groundhog``` package.

```python
from groundhog.siteinvestigation.insitutests.pcpt_processing import DEFAULT_CONE_PROPERTIES
DEFAULT_CONE_PROPERTIES
```

The cone properties can be customised or an entirely new ```SoilProfile``` object can be defined. Here, we will keep the default properties.

A layering definition also needs to be defined through a ```SoilProfile``` object. The total unit weight needs to be specified for the vertical stress calculation. Note that linear variations over the layers are possible through the use of ```from``` and ```to``` in the column keys.

```python
layering = SoilProfile({
    "Depth from [m]": [0, 3.16, 5.9, 14.86, 15.7],
    "Depth to [m]": [3.16, 5.9, 14.86, 15.7, 20],
    "Total unit weight [kN/m3]": [18, 17, 19.5, 20, 20],
    'Soil type': ['SAND', 'CLAY', 'SAND', 'SAND', 'SAND']
})
layering.to_excel("Data/WFS1-2_layering.xlsx")
```

The cone and layer properties can be mapped to the cone data grid using the ```map_properties``` method:

```python
pcpt.map_properties(layer_profile=layering, cone_profile=DEFAULT_CONE_PROPERTIES)
```

Following mapping of the layering, the plot with raw cone data will also include the selected layers.

```python
pcpt.plot_raw_pcpt()
```

## 3. Normalising PCPT data

PCPT can be normalised using the equations for normalised cone resistance $ Q_t $, normalised sleeve friction $ F_r $ and the pore pressure parameter $ B_q $. The ```normalise_pcpt``` method of the ```PCPTProcessing``` class allows this normalisation to happen in one calculation step:

```python
pcpt.normalise_pcpt()
```

Plotting of the resulting properties can be executed with the ```plot_normalised_pcpt``` method.

```python
pcpt.plot_normalised_pcpt()
```

The data points can also be plotted in the Robertson chart per layer. 

We can see that the data points in the second layer are classified as overconsolidated cohesive material.

```python
pcpt.plot_robertson_chart()
```

## 5. Applying correlations to PCPT data

Correlations can be applied to the processed PCPT data using method ```apply_correlation``` with the keys outlined in the documentation. For example ```'Robertson and Wride (1998)'``` calculates the soil behaviour type index. The method argument ```outputs``` is a dictionary containing the keys from the function output as keys and the target column names as values. For example, the function ```gmax_clay_maynerix``` has the key ```Gmax [kPa]``` in the result dictionary. This key needs to be selected and can be assigned to the column ```Gmax clay [kPa]```.

Using the ```apply_for_soiltypes``` keyword arguments, we can limit the application of the correlation to specific soil types. Here, we will apply the correlation of Mayne & Rix to clay and Rix & Stokoe to sand.

Full explanation on the different correlations is provided in the ```groundhog``` documentation. We can list the available correlations. More correlations are being added to ```groundhog``` with each new release.

```python
from groundhog.siteinvestigation.insitutests.pcpt_processing import CORRELATIONS
list(CORRELATIONS.keys())
```

For the example, we can calculate the soil behaviour type index and the small-strain shear modulus.

```python
pcpt.apply_correlation('Ic Robertson and Wride (1998)', outputs={'Ic [-]':'Ic [-]'})

pcpt.apply_correlation(
    'Gmax Rix and Stokoe (1991)', outputs={'Gmax [kPa]': 'Gmax sand [kPa]'},
    apply_for_soiltypes=['SAND',])
pcpt.apply_correlation(
    'Gmax Mayne and Rix (1993)', outputs={'Gmax [kPa]': 'Gmax clay [kPa]'},
    apply_for_soiltypes=['CLAY',])
```

The calculated properties can be visualized with a ```LogPlot```. The keys to be plotted in each panel need to be provided in the ``add_trace`` method. In the example below, the first panel only contains ```qc [MPa]``` and the second ```Ic [-]```. The third panel contains $ G_{max} $ in sand and clay.

```python
from groundhog.general.plotting import LogPlot
```

```python
cpt_processed_plot = LogPlot(layering, no_panels=3, fillcolordict={'SAND': 'yellow', 'CLAY': 'brown'})
cpt_processed_plot.add_trace(
    x=pcpt.data['qc [MPa]'],
    z=pcpt.data['z [m]'],
    name='qc',
    showlegend=False,
    panel_no=1)
cpt_processed_plot.add_trace(
    x=pcpt.data['Ic [-]'],
    z=pcpt.data['z [m]'],
    name='Ic',
    showlegend=False,
    panel_no=2)
cpt_processed_plot.add_trace(
    x=pcpt.data['Gmax sand [kPa]'],
    z=pcpt.data['z [m]'],
    name='Gmax SAND',
    showlegend=True,
    panel_no=3)
cpt_processed_plot.add_trace(
    x=pcpt.data['Gmax clay [kPa]'],
    z=pcpt.data['z [m]'],
    name='Gmax CLAY',
    showlegend=True,
    panel_no=3)
cpt_processed_plot.set_xaxis(title=r'$ q_c \ \text{[MPa]} $', panel_no=1)
cpt_processed_plot.set_xaxis(title=r'$ I_c \ \text{[-]} $', panel_no=2, range=(1, 3.5))
cpt_processed_plot.set_xaxis(title=r'$ G_{max} \ \text{[kPa]} $', panel_no=3, range=(0, 200e3))
cpt_processed_plot.set_zaxis(title=r'$ z \ \text{[m]} $', range=(20, 0))
cpt_processed_plot.show()
```
