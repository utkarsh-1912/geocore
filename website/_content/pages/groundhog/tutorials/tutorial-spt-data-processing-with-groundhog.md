---
title: Tutorial - SPT data processing with Groundhog
slug: groundhog/tutorials/tutorial-spt-data-processing-with-groundhog
section: Groundhog Guides
description: Since version v0.6.0 an SPT processing tool has been created within the
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/notebooks/Tutorial%20-%20SPT%20data%20processing%20with%20Groundhog.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted.'
notebook: notebooks/Tutorial - SPT data processing with Groundhog.ipynb
---

Since version v0.6.0 an SPT processing tool has been created within the ```groundhog``` package. This tool is made available to allow rapid import of SPT data, basic processing and checking of the sensitivity to processing parameters. Moreover, correlations between SPT properties and other soil mechanical parameters can easily be applied.

In this tutorial, the processing of SPT data is covered. This consists of stress and energy corrections and application of soil parameter correlations.

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
from groundhog.siteinvestigation.insitutests.spt_processing import SPTProcessing
from groundhog.general.soilprofile import SoilProfile
```

## SPT import

We will work with SPT data specified in an Excel file. This is the result of data imported from gINT. See ```Tutorial - gINT data import```.

The data is loaded using the ```load_excel``` method. A dataframe is created from Excel data and added as the ```.data``` attribute of the ```SPTProcessing``` object.

Note that the depth column is expected as ```'z [m]'``` by default. If this is not the case, the column key of the column containing depth values needs to be supplied (```'Depth'```) in this case. Depths are given in ft in this case. To convert to meters, a multiplier of 0.3048 needs to be specified for ```z_multiplier```.

The raw SPT N number (uncorrected) is expected as ```'N [-]'```. If this is not the case, the argument ```N_key``` can be specified to tell ```groundhog``` where to find the SPT N number.

```python
spt = SPTProcessing(title="Example SPT")
```

```python
spt.load_excel(path="Output/spt_example.xlsx", z_key='Depth', z_multiplier=0.3048, N_key='SPT N')
spt.data.head()
```

The raw SPT data can be visualized with the ```plot_raw_spt``` method.

```python
spt.plot_raw_spt()
```

## Setting SPT sampler and layer properties

The SPT sampler and layer properties can be set based on the SPT system used and the layering identified. A ```SoilProfile``` object can be created for these properties. A basic structure with SPT sampler properties is available in the ```groundhog``` package.

```python
from groundhog.siteinvestigation.insitutests.spt_processing import DEFAULT_SPT_PROPERTIES
DEFAULT_SPT_PROPERTIES
```

The SPT sampler properties can be customised or an entirely new ```SoilProfile``` object can be defined. Here, we will keep the default properties.

Note that direct specification of the factor $ \eta_H, \ \eta_B, \ \eta_S $ and $ \eta_R $ will override the rule-based selection described in the documentation of the function ```spt_N60_correction```.

A layering definition also needs to be defined through a ```SoilProfile``` object. The total unit weight needs to be specified for the vertical stress calculation. Note that linear variations over the layers are possible through the use of ```from``` and ```to``` in the column keys.

Note that we need to specify the unit used in case of a ```SoilProfile``` with depths defined in feet.

```python
from groundhog.general.soilprofile import read_excel
```

```python
layering = read_excel('Data/spt_example_layering.xlsx', unit='ft')
layering
```

The depth reference needs to be changed to meters. This is easily done using the method ```.convert_depth_reference``` for which the new unit (meters in this case) and the conversion factor needs to be specified.

```python
layering.convert_depth_reference(newunit='m', multiplier=0.3048)
layering
```

The spt sampler and layer properties can be mapped to the cone data grid using the ```map_properties``` method:

```python
spt.map_properties(layer_profile=layering, spt_profile=DEFAULT_SPT_PROPERTIES)
```

Following mapping of the layering, the plot with raw SPT data will also include the selected layers.

```python
spt.plot_raw_spt()
```

The data also contains vertical total and effective stress.

```python
spt.data
```

## Correcting SPT data

SPT can be corrected using two different corrections:

   - Corrections for vertical effective stress in granular soils ($ N_1 $). The correction according to Liao & Whitman  (1986) is encoded.
   - Corrections for energy ratio: If a different energy ratio is used, the measured values are corrected to an SPT number for an energy ratio of 60 ($ N_{60} $). Recommendations according to Seed et al. (1985) and Skempton (1986) are calculated based on the properties of the SPT testing. However, the correction factors can also be specified directly.
   
Note that the energy correction is applied after the correction for vertical effective stress in granular soils. The resulting quantity is calculated as $ (N_1)_{60} $.

These corrections are applied as correlations using the ```.apply_correlation``` method.

### Correction for stress level according to Liao & Whitman (1986)

The correction is defined as:

$$ N_1 = C_N \cdot N $$

$$ C_N = \left[ \frac{1}{ \left( \frac{\sigma_{vo}^{\prime}}{P_a} \right) } \right]^{0.5} $$

We will save both $ N_1 $ and $ C_N $ in the ```.data``` attribute. We will only apply this for the granular soil (silt and possibly siltstone in this case).

```python
spt.apply_correlation(
    name='Overburden correction Liao and Whitman (1986)',
    outputs={'CN [-]': 'CN [-]', 'N1 [-]': 'N1 [-]'}, apply_for_soiltypes=['SILT', 'SILTSTONE'])
spt.data[['z [m]', 'Soil type', 'N [-]', 'CN [-]', 'N1 [-]']]
```

We can see that the biggest corrections happen for the shallowest data.

### Energy corrections

The energy correctios happen according to the following formula:

$$ N_{60} = \frac{N \cdot \eta_H \cdot \eta_B \cdot \eta_S \cdot \eta_R}{60} $$

The $ \eta $ factors can either be derived from the properties of the SPT system or by direct specification of the factors in the SPT properties profile.

The energy correction is again applied using the ```.apply_correlation``` method.

```python
spt.apply_correlation(
    name='N60 correction',
    outputs={'N60 [-]': 'N60 [-]'})
spt.data[['z [m]', 'Soil type', 'N [-]', 'CN [-]', 'N1 [-]', 'N60 [-]']]
```

The data shows that the correction is mainly influenced by the rod length.

We can also calculate $ (N_1)_{60} $ according to the following formula:

$$ (N_1)_{60} = C_N \cdot N_{60} $$

```python
spt.data['N1_60 [-]'] = spt.data['CN [-]'] * spt.data['N60 [-]']
spt.data[['z [m]', 'Soil type', 'N [-]', 'CN [-]', 'N1 [-]', 'N60 [-]', 'N1_60 [-]']]
```

## Applying correlations to SPT data

Correlations can be applied to the processed SPT data using method ```apply_correlation``` with the keys outlined in the documentation. For example ```'Relative density Kulhawy and Mayne (1990)'``` calculates the relative density of granular soil according to Kulhawy & Mayne (1990). ```'Undrained shear strength Salgado (2008)'``` calculates undrained shear strength according to Salgado (2008). 

Note that these correlations often take into account an index property measured in the laboratory (e.g. $ d_{50} $ for relative density and plasticity index for undrained shear strength). These properties can be specified either in the Excel file with data which is imported. 

The method argument ```outkey``` is the name of the column in the resulting dataframe. The method argument ```resultkey``` is the key in the output dictionary of the function which needs to be taken. For example, the function ```relativedensity_spt_kulhawymayne``` has the key ```Dr [pct]``` in the result dictionary. This key needs to be selected.

Using the ```apply_for_soiltypes``` keyword arguments, we can limit the application of the correlation to specific soil types. Here, we will apply the correlation of the undrained shear strength correlation to clay and the relative density correlation to silt and siltstone.

Full explanation on the different correlations is provided in the ```groundhog``` documentation. We can list the available correlations. More correlations are being added to ```groundhog``` with each new release.

```python
from groundhog.siteinvestigation.insitutests.spt_processing import CORRELATIONS
list(CORRELATIONS.keys())
```

We will first specify $ d_{50} $ and plasticity index.

```python
spt.data.loc[1, 'PI [%]'] = 30
spt.data.loc[2:, 'd50 [mm]'] = 0.01

spt.data
```

We can now apply the relative density correlation.

```python
spt.apply_correlation(
    'Relative density Kulhawy and Mayne (1990)', outputs={'Dr [pct]': 'Dr [pct]'},
    apply_for_soiltypes=['SILT', 'SILTSTONE'])
spt.apply_correlation(
    'Undrained shear strength Salgado (2008)', outputs={'Su [kPa]': 'Su [kPa]'},
    apply_for_soiltypes=['CLAY',])
```

The calculated properties can be visualized with a ```LogPlot```. The keys to be plotted in each panel need to be provided in the ``add_trace`` method. In the example below, the first panel contains ```N [-]```, ```N60 [-]``` and ``N1_60 [-]``, the second ```Dr [pct]```. The third panel contains $ S_{u} $.

```python
from groundhog.general.plotting import LogPlot
```

```python
spt_processed_plot = LogPlot(layering, no_panels=3, fillcolordict={
        'Asphalt': 'black', 'GRAVEL': 'lightgray', 'CLAY': 'brown', 'SILT': 'lightyellow', 'SILTSTONE': 'grey'})
spt_processed_plot.add_trace(
    x=spt.data['N [-]'],
    z=spt.data['z [m]'],
    name='N',
    showlegend=True,
    mode='markers',
    panel_no=1)
spt_processed_plot.add_trace(
    x=spt.data['N60 [-]'],
    z=spt.data['z [m]'],
    name='N60',
    showlegend=True,
    mode='markers',
    panel_no=1)
spt_processed_plot.add_trace(
    x=spt.data['N1_60 [-]'],
    z=spt.data['z [m]'],
    name='N1_60',
    showlegend=True,
    mode='markers',
    panel_no=1)
spt_processed_plot.add_trace(
    x=spt.data['Dr [pct]'],
    z=spt.data['z [m]'],
    name='Dr',
    showlegend=False,
    mode='markers',
    panel_no=2)
spt_processed_plot.add_trace(
    x=spt.data['Su [kPa]'],
    z=spt.data['z [m]'],
    name='Su',
    showlegend=False,
    mode='markers',
    panel_no=3)
spt_processed_plot.set_xaxis(title=r'$ N, \ N_{60} \ \text{[-]} $', panel_no=1)
spt_processed_plot.set_xaxis(title=r'$ D_r \ \text{[%]} $', panel_no=2)
spt_processed_plot.set_xaxis(title=r'$ S_u \ \text{[kPa]} $', panel_no=3)
spt_processed_plot.set_zaxis(title=r'$ z \ \text{[m]} $', range=(11, 0))
spt_processed_plot.show()
```

## Conclusions and outlook

The ```groundhog``` package allows processing of SPT data. In the future, more correlations will be added. Feel free to suggest additional functionality by contacting the package the author.
