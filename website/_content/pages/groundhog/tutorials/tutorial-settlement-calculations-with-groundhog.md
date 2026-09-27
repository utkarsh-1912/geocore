---
title: Tutorial - Settlement calculations with ```groundhog```
slug: groundhog/tutorials/tutorial-settlement-calculations-with-groundhog
section: Groundhog Guides
description: 'groundhog tutorial notebook: Tutorial - Settlement calculations with groundhog.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/notebooks/Tutorial%20-%20Settlement%20calculations%20with%20groundhog.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted.'
notebook: notebooks/Tutorial - Settlement calculations with groundhog.ipynb
---

```groundhog``` contains functionality to analyse the settlement of foundations under applied loads. Elastic stress solutions are available for strip foundation, circular foundations and rectangular foundations.

Moreover, the basic functionality of ```groundhog``` for working with soil profiles and rapidly deriving correlations can be illustrated in this tutorial.

In this example, we will derive the compression index $ C_c $ and the recompression index $ C_r $ based on measured unit weights for a saturated cohesive soil. We will use these values to calculate the primary consolidation settlement beneath a strip footing, circular footing and rectangular footing.

## Library imports

```python
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
```

```python
import plotly.graph_objs as go
from plotly.offline import init_notebook_mode
init_notebook_mode()
```

## Selection of soil parameters

### Loading unit weight data

Two data files are provided to specify a distribution of unit weight vs depth. Bulk unit weight $ \gamma $ has been derived from a volume mass calculation and has also been derived from water content (for a saturated soil) using the following relation:

$$ \gamma = \left( \frac{G_s \cdot (1 + w)}{1 + w \cdot G_s} \right) \cdot \gamma_w $$

```python
uw_data = pd.read_excel("Data/demo_settlement_uw.xlsx")
```

We can plot this data vs depth. We can see there is a reasonable amount of scatter in the first 0.5m.

```python
import plotly.express as px
fig = px.scatter(uw_data, x='Bulk unit weight [kN/m3]', y='z [m]', color='Method')
fig['layout']['xaxis1'].update(title='Bulk unit weight [kN/m3]', side='top', anchor='y', range=(12, 20))
fig['layout']['yaxis1'].update(title='Depth below mudline [m]', autorange='reversed')
fig.show()
```

### Definition of a soil profile and bulk unit weight selection

```groundhog``` allows soil profile manipulations through the ```SoilProfile``` object. We can create a ```SoilProfile``` for soil parameter selection.

Initially, we will model a profile with a 1m thick top layer overlying a layer extending to 2m depth. Below 2m, the unit weight increases further, so another layer transition is selected at 2m depth.

```python
from groundhog.general.soilprofile import SoilProfile
```

We can define the soil profile from a Python dictionary containing an array with the depths of the top of each layer, an array with the bottom of each layer and an array with the soil type of each layer.

```python
sp = SoilProfile({
    "Depth from [m]": [0, 0.5, 2],
    "Depth to [m]": [0.5, 2, 3.5],
    "Soil type": ["CLAY", "CLAY", "CLAY"]
})
sp
```

The ```SoilProfile``` object has a ```selection_soilparameter``` which allows an automatic first eastimate of soil parameters in a profile. 

We will make an estimate based on the test data provided. By default, the average trend will be selected.

```python
sp.selection_soilparameter(
    'Total unit weight [kN/m3]', depths=uw_data['z [m]'], values=uw_data['Bulk unit weight [kN/m3]'])
```

The selection provided by the software can be used as an initial guess and the engineer can then modify the selected values.

The choice of the program looks reasonable in the first layer. However, as this is normally consolidated clay, decreases of unit weight with depth are unlikely. So we will amend the first guess.

```python
from groundhog.general.plotting import LogPlot
```

```python
uw_fig = LogPlot(sp, no_panels=1, fillcolordict={'SAND': 'yellow', 'CLAY': 'brown'})
uw_fig.add_trace(
    x=uw_data['Bulk unit weight [kN/m3]'],
    z=uw_data['z [m]'],
    mode='markers',
    name='data',
    showlegend=False,
    panel_no=1)
uw_fig.add_trace(
    x=sp.soilparameter_series('Total unit weight [kN/m3]')[1],
    z=sp.soilparameter_series('Total unit weight [kN/m3]')[0],
    name='selection',
    showlegend=False,
    panel_no=1)
uw_fig.set_xaxis(title=r'$ \gamma \ \text{[kN/m} ^3 \text{]} $', panel_no=1, range=(12, 20))
uw_fig.set_zaxis(title=r'$ z \ \text{[m]} $', range=(3.5, 0))
uw_fig.show()
```

We can have a look at the selected values:

```python
sp
```

We can modify the unit weight in the layers. The syntax for this is Pandas syntax. Several tutorials are available online to start working with Pandas. The code below modifies the unit weight in the deepest layer by specifying a new user-defined bulk unit weight.

```python
sp['Total unit weight [kN/m3]'].iloc[2] = 17.5
```

We can replot the selection. This shows that this is a reasonable selection.

```python
uw_fig = LogPlot(sp, no_panels=1, fillcolordict={'SAND': 'yellow', 'CLAY': 'brown'})
uw_fig.add_trace(
    x=uw_data['Bulk unit weight [kN/m3]'],
    z=uw_data['z [m]'],
    mode='markers',
    name='data',
    showlegend=False,
    panel_no=1)
uw_fig.add_trace(
    x=sp.soilparameter_series('Total unit weight [kN/m3]')[1],
    z=sp.soilparameter_series('Total unit weight [kN/m3]')[0],
    name='selection',
    showlegend=False,
    panel_no=1)
uw_fig.set_xaxis(title=r'$ \gamma \ \text{[kN/m} ^3 \text{]} $', panel_no=1, range=(12, 20))
uw_fig.set_zaxis(title=r'$ z \ \text{[m]} $', range=(3.5, 0))
uw_fig.show()
```

### Calculation of initial void ratio and water content

The initial void ratio and water content can be derived from the bulk unit weight using the function ```voidratio_bulkunitweight``` in ```groundhog```. This function calculates the void ratio and water content from bulk unit weight for a saturated soil using the following formulae.

$$ \gamma = \left( \frac{G_s + S e}{1 + e} \right) \gamma_w $$

$$ \implies e = \frac{\gamma_w G_s - \gamma}{\gamma - S \gamma_w} $$

$$ w = \frac{S e}{G_s} $$

```SoilProfile``` objects in ```groundhog``` have a method ```applyfunction``` which can apply any function to the rows of a soil profile. The parameters of the function are mapped to soil parameters in the dictionary ```parametermapping```.

We can apply this function twice, once for the calculation of void ratio (result key ```'e [-]'``` in the result of ```voidratio_bulkunitweight```) and once for the calculation of water content (result key ```'w [-]'``` in the result of ```voidratio_bulkunitweight```).

We can print the resulting soil profile to the notebook.

```python
from groundhog.siteinvestigation.classification.phaserelations import voidratio_bulkunitweight
```

```python
?voidratio_bulkunitweight
```

```python
sp.applyfunction(
    function=voidratio_bulkunitweight,
    outputkey="Void ratio [-]", resultkey="e [-]",
    parametermapping={
        'bulkunitweight': "Total unit weight [kN/m3]"
    })
sp.applyfunction(
    function=voidratio_bulkunitweight,
    outputkey="Water content [-]", resultkey="w [-]",
    parametermapping={
        'bulkunitweight': "Total unit weight [kN/m3]"
    })
sp
```

The initial void ratio is required to calculate the settlements.

### Selection of $ C_c $ and $ C_r $

The compression index $ C_c $ and recompression index $ C_r $ describe the slope of the virgin compression line and the recompression line respectively in $ e - \log_{10} ( \sigma_v^{\prime} ) $ space:

$$ C_c = - \frac{e_2 - e_1}{\log_{10} \left( \frac{\sigma^{\prime}_{v,2}}{\sigma^{\prime}_{v,1}} \right)} \quad \text{Virgin compression line} \\ C_r = - \frac{e_2 - e_1}{\log_{10} \left( \frac{\sigma^{\prime}_{v,2}}{\sigma^{\prime}_{v,1}} \right)} \quad \text{Recompression line}
$$

Several correlations exist which correlate the compression and recompression indices with water content, void ratio, ...

```groundhog``` implements the correlation ```compressionindex_watercontent_koppula``` which is based on a study by Koppula (1981) which found a direct relation between the compression index $ C_c $ and the natural water content $ w $. The compression index is between 5 and 10 times higher than the recompression index $ C_r $. Here, we assume a ratio of 7.5 between both indices.

We can again determine the indices using the ```applyfunction``` method on the ```SoilProfile``` object.

```python
from groundhog.siteinvestigation.correlations.cohesive import compressionindex_watercontent_koppula
```

```python
sp.applyfunction(
    function=compressionindex_watercontent_koppula,
    outputkey="Cc [-]", resultkey="Cc [-]",
    parametermapping={
        'water_content': "Water content [-]"
    })
sp.applyfunction(
    function=compressionindex_watercontent_koppula,
    outputkey="Cr [-]", resultkey="Cr [-]",
    parametermapping={
        'water_content': "Water content [-]"
    })
sp
```

Note that this choice of indices should be benchmarked against or replaced by values obtained from oedometer tests.

### Selection of OCR

For the settlement calculation, an OCR also needs to be selected. Here, we will just assume a slightly overconsolidated clay (OCR=3) throughout the profile.

```python
sp.loc[:, 'OCR [-]'] = 3
```

## Settlement calculation

Settlement calculations can be performed in `` groundhog`` using the ``SettlementCalculation`` class. This class implements the necessary functionality to set up the calculation, calculate the additional total stress due to the imposed surcharge and compute the settlements.

### Calculation setup

The starting point of the calculation is the soil profile.

```python
sp
```

The calculation can be set up using this soil profile:

```python
from groundhog.shallowfoundations.settlement import SettlementCalculation
```

```python
calc = SettlementCalculation(sp)
```

### Calculation of the initial stress state

To initiate the calculation, the overburden stress needs to be calculated. This can be done by selecting the position of the watertable. Here, we selected a water table at surface (depth=0m).

```python
calc.calculate_initial_state(waterlevel=0)
```

We can plot this initial state:

```python
calc.plot_initial_state(fillcolordict={'SAND': 'yellow', 'CLAY': 'brown'})
```

### Calculation discretisation

To perform the settlement calculation, a grid needs to be set up with a certain node spacing. Here, we will set a node spacing of 0.1m.

```python
calc.create_grid(dz=0.1)
```

The properties are automatically mapped to the grid. We can check the nodal properties:

```python
calc.grid.nodes.head()
```

### Foundation shape and dimensions

The shape and dimensions of the foundation can be set. Here a circular foundation with 1m diameter is specified.

```python
calc.set_foundation(shape='circular', width=1)
```

### Stress increase

The vertical effective stress increases for elastic halfspaces can be obtained using the formulae derived by Boussinesq.

```groundhog``` implements the calculation of vertical effective stress increases below strip footings, the center of circular footings and the corner of a rectangular footing. The module ```groundhog.shallowfoundations.stressdistribution``` contains the necessary functions.

The functions are applied to the selected grid with the foundation shape parameters as specified above by running the ``calculate_foundation_stress`` method. Here, a stress increase of 10kPa is imposed.

```python
calc.calculate_foundation_stress(applied_stress=10)
```

### Settlement calculation

When the initial and final stress state are known, the calculation can be executed. The settlement of each element is computed and is summed to provide the surface settlement.

```python
calc.calculate()
```

The calculation output can be tabulated for checking:

```python
calc.grid.elements.head()
```

However, plotting results is always more instructive. The results plot has two panels, the leftmost one showing the vertical effective stress at the start and end of the consolidation, the second showing the cumulative settlement in the soil. At the surface, the settlement value is the sum of settlements computed in each element.

```python
calc.plot_result()
```
