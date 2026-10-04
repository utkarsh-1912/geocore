---
title: Tutorial - Soil profile objects in Groundhog
slug: groundhog/tutorials/tutorial-soil-profile-objects-in-groundhog
section: Groundhog Guides
description: A soil profile is a table with several layers where the bottom depth of the previous layer corresponds to the top depth of the next layer.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/notebooks/Tutorial%20-%20Soil%20profile%20objects%20in%20Groundhog.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted, with a short note on how to run this in GeoCore prepended.'
notebook: notebooks/Tutorial - Soil profile objects in Groundhog.ipynb
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, run the same calculation through a [calculation form](/docs/geocore/using/modules) or by asking **GeoAI**, which calls the same groundhog function through its validated Tool Registry. This notebook is kept for anyone who wants to call groundhog directly from their own Python code instead.

A soil profile is a table with several layers where the bottom depth of the previous layer corresponds to the top depth of the next layer.

Because a soil profile is a dataframe with additional functionality, the ```SoilProfile``` class inherits from the ```DataFrame``` class.

Additional functionality is implemented to enable all common soil profile manipulations such:
   - Retrieving minimum and maximum depth;
   - Changing depth coordinate signs;
   - Changing the mudline level;
   - Retrieving the soil parameters available in the dataframe;
   - Mapping the soil parameters to a grid;
   - Plotting the soil profile;
   
This tutorial demonstrates this functionality.

```python
import numpy as np
from groundhog.general import soilprofile as sp
from groundhog.general.plotting import LogPlot
from groundhog.__version__ import __version__
__version__
```

```text
'0.13.0'
```

```groundhog``` uses Plotly as the plotting backend. Please note that you may still need to install Plotly in your Python environment.

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

*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*

## 1. Soil profile creation

There are a couple of standard scenarios for creating soil profiles:

   - Soil profile definition based on a Python dictionary;
   - Soil profile reading from Excel file
  
These two scenarios are demonstrated here.

### 1.1. Soil profile creation from Excel file

When a soil profile is created from Excel, the layer are encoded as rows and soil parameters names are put on the first row. The coordinate of the top of the next layer should always correspond to the coordinate of the bottom of the previous layer. There is one all-important convention for soil parameters:

   - Numerical soil parameters have units between square brackets (e.g. ```qc [MPa]```)
   - Numerical soil parameters can have linear variations using the ```from``` and ```to``` words in the title (e.g. ```qc from [MPa]``` and ```qc to [MPa]```)
   - String soil parameters are specified without units, square brackets should not be used in the title
   
The user can use several names for the depth from and depth to columns. ```Depth from [m]``` and ```Depth to [m]``` are used by default but different names and units can be used by specifying the ```depth_key``` and ```unit``` keyword arguments.

As an example a file with depth (z) specified in imperial units can be read.

```python
profile_1 = sp.read_excel("Data/soilprofile_basic.xlsx")
profile_1
```

```text
   Depth from [m]  Depth to [m] Soil type Relative density  qc from [MPa]  \
0               0             3      SAND            Loose              3   
1               3             9      CLAY              NaN              1   
2               9            12      SILT     Medium dense              4   
3              12            30      SAND            Dense             40   

   qc to [MPa]  qt [MPa]  Total unit weight [kN/m3]  
0          4.0      3.50                         19  
1          1.5      1.25                         18  
2          8.0      6.00                         19  
3         50.0     45.00                         20  
```

```python
profile_1.calculate_overburden()
profile_1[['Depth from [m]', 'Depth to [m]',
           'Vertical effective stress from [kPa]', 'Vertical effective stress to [kPa]',
           'Vertical total stress from [kPa]', 'Vertical total stress to [kPa]']]
```

```text
   Depth from [m]  Depth to [m]  Vertical effective stress from [kPa]  \
0               0             3                                   0.0   
1               3             9                                  27.0   
2               9            12                                  75.0   
3              12            30                                 102.0   

   Vertical effective stress to [kPa]  Vertical total stress from [kPa]  \
0                                27.0                               0.0   
1                                75.0                              57.0   
2                               102.0                             165.0   
3                               282.0                             222.0   

   Vertical total stress to [kPa]  
0                            57.0  
1                           165.0  
2                           222.0  
3                           582.0  
```

### 1.2. Soil profile from dictionary

A soil profile can be directly specified in the notebook through a dictionary. Note that ```Depth from [m]``` and ```Depth to [m]``` are required here. Other soil parameter columns can be added. Both strings and numerical values are allowed.

Linear variations of numerical soil parameters can be encoded using ``to`` and ``from`` after the soil parameter name and before the unit specification.

```python
profile_2 = sp.SoilProfile({
    'Depth from [m]': [0, 1, 3, 4],
    'Depth to [m]': [1, 3, 4, 10],
    'Soil type': ['SAND', 'CLAY', 'SILT', 'SAND'],
    'Relative density': ['Loose', None, 'Medium dense', 'Dense'],
    'qc from [MPa]': [3, 1, 4, 40],
    'qc to [MPa]': [4, 1.5, 8, 50],
    'qt [MPa]': [3.5, 1.25, 6, 45],
    'Total unit weight [kN/m3]': [19, 18, 19, 20]
})
logplot = LogPlot(profile_2, no_panels=2, fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green'})
logplot.add_soilparameter_trace(
    parametername="Total unit weight [kN/m3]",
    panel_no=1)
logplot.add_soilparameter_trace(
    parametername="qc [MPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="qt [MPa]",
    panel_no=2)
logplot.set_xaxis(title='Total unit weight [kN/m3]', panel_no=1, range=(15, 23))
logplot.set_xaxis(title='qc, qt [MPa]', panel_no=2)
logplot.set_zaxis(title='z [m]', range=(10, 0))
logplot.set_size(width=900, height=600)
logplot.show()
```

*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*

## 2. Retrieving information from ```SoilProfile``` objects

```SoilProfile``` objects have properties which allow the user to quickly assess the contents of the soil profile.

### 2.1. Top and bottom depth

The minimum and maximum depth of the soil profile can be retrieved using ```min_depth``` and ```max_depth``` attributes.

```python
profile_2.min_depth, profile_2.max_depth
```

```text
(0, 10)
```

### 2.2. Soil parameters

The ```SoilProfile``` objects has a method to retrieve the numerical and string soil parameters.

```python
profile_2.numerical_soil_parameters()
```

```text
['qc [MPa]', 'qt [MPa]', 'Total unit weight [kN/m3]']
```

```python
profile_2.string_soil_parameters()
```

```text
['Soil type', 'Relative density']
```

For the numerical soil parameters, the method ```check_linear_variation``` allows to check whether the parameter is constant in the layer or whether is has a linear variation. Linear variations are encoded in the soil profile by using the ```to``` and ```from``` column keys (e.g. ```qc from [MPa]``` and ```qc to [MPa] ```).

```python
for _param in profile_2.numerical_soil_parameters():
    if profile_2.check_linear_variation(_param):
        print("Parameter %s shows a linear variation" % _param)
    else:
        print("Parameter %s is constant in each layer" % _param)
```

```text
Parameter qc [MPa] shows a linear variation
Parameter qt [MPa] is constant in each layer
Parameter Total unit weight [kN/m3] is constant in each layer
```

## 3. Selection of soil parameters

The ```SoilProfile``` object has a method for automatic selection of design lines based on parameter values in the layer. This can be demonstrated using a couple of randomly selected value for the undrained shear strength.

```python
depths = np.linspace(1.1, 2.9, 25)
su_values = 20 + 20 * np.random.rand(25)
```

```python
profile_2.selection_soilparameter(
    parameter='Su [kPa]',
    depths=depths,
    values=su_values,
    rule='mean',
    linearvariation=True)
profile_2
```

```text
   Depth from [m]  Depth to [m] Soil type Relative density  qc from [MPa]  \
0               0             1      SAND            Loose              3   
1               1             3      CLAY             None              1   
2               3             4      SILT     Medium dense              4   
3               4            10      SAND            Dense             40   

   qc to [MPa]  qt [MPa]  Total unit weight [kN/m3]  Su from [kPa]  \
0          4.0      3.50                         19            NaN   
1          1.5      1.25                         18      31.754843   
2          8.0      6.00                         19            NaN   
3         50.0     45.00                         20            NaN   

   Su to [kPa]  
0          NaN  
1    30.253007  
2          NaN  
3          NaN  
```

The selected line can be plotted by adding a trace to a plot with a mini-log.

```python
logplot = LogPlot(profile_2, no_panels=3, fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green'})
logplot.add_soilparameter_trace(
    parametername="Total unit weight [kN/m3]",
    panel_no=1)
logplot.add_soilparameter_trace(
    parametername="qc [MPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="qt [MPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="Su [kPa]",
    panel_no=3)
logplot.add_trace(
    x=su_values,
    z=depths,
    name='Su data',
    mode='markers',
    showlegend=True,
    panel_no=3)
logplot.set_xaxis(title='Total unit weight [kN/m3]', panel_no=1, range=(15, 23))
logplot.set_xaxis(title='qc, qt [MPa]', panel_no=2)
logplot.set_xaxis(title='Su [kPa]', panel_no=3)
logplot.set_zaxis(title='z [m]', range=(10, 0))
logplot.set_size(width=900, height=600)
logplot.show()
```

*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*

## 4. Soil profile manipulations

A number of manipulations with soil profiles are possible using the ```SoilProfile``` class.

### 4.1. Shifting vs depth

The profile can be shifted vs depth using the ```shift_depths``` method. For example we can move the profile up by 5m. Note: Moving up requires a negative offset to be specified (depth axis is positive in the downward direction).

```python
profile_2.shift_depths(offset=-4)
logplot = LogPlot(profile_2, no_panels=3, fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green'})
logplot.add_soilparameter_trace(
    parametername="Total unit weight [kN/m3]",
    panel_no=1)
logplot.add_soilparameter_trace(
    parametername="qc [MPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="qt [MPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="Su [kPa]",
    panel_no=3)
logplot.add_trace(
    x=su_values,
    z=depths,
    name='Su data',
    mode='markers',
    showlegend=True,
    panel_no=3)
logplot.set_xaxis(title='Total unit weight [kN/m3]', panel_no=1, range=(15, 23))
logplot.set_xaxis(title='qc, qt [MPa]', panel_no=2)
logplot.set_xaxis(title='Su [kPa]', panel_no=3)
logplot.set_zaxis(title='z [m]', range=(6, -4))
logplot.set_size(width=900, height=600)
logplot.show()
```

*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*

Each time the ```shift_depths``` method is applied, a further shift is applied, so be careful not to repeat code containing this method inadvertently.

### 4.2. Flipping the depth axis

In certain cases (e.g. when working with depths in mLAT), flipping of the depth axis is required. This can be done using the ```convert_depth_sign```.

```python
profile_2.convert_depth_sign()
logplot = LogPlot(profile_2, no_panels=3, fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green'})
logplot.add_soilparameter_trace(
    parametername="Total unit weight [kN/m3]",
    panel_no=1)
logplot.add_soilparameter_trace(
    parametername="qc [MPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="qt [MPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="Su [kPa]",
    panel_no=3)
logplot.add_trace(
    x=su_values,
    z=depths,
    name='Su data',
    mode='markers',
    showlegend=True,
    panel_no=3)
logplot.set_xaxis(title='Total unit weight [kN/m3]', panel_no=1, range=(15, 23))
logplot.set_xaxis(title='qc, qt [MPa]', panel_no=2)
logplot.set_xaxis(title='Su [kPa]', panel_no=3)
logplot.set_zaxis(title='z [m]', range=(-6, 4))
logplot.set_size(width=900, height=600)
logplot.show()
```

*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*

This statement can also be repeated. Note that most other methods of the ```SoilProfile``` object expect depths increasing downward!

For the further demonstrations of the functionality, we will reset the depth reference:

```python
profile_2.convert_depth_sign()
profile_2.shift_depths(offset=4)
logplot = LogPlot(profile_2, no_panels=3, fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green'})
logplot.add_soilparameter_trace(
    parametername="Total unit weight [kN/m3]",
    panel_no=1)
logplot.add_soilparameter_trace(
    parametername="qc [MPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="qt [MPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="Su [kPa]",
    panel_no=3)
logplot.add_trace(
    x=su_values,
    z=depths,
    name='Su data',
    mode='markers',
    showlegend=True,
    panel_no=3)
logplot.set_xaxis(title='Total unit weight [kN/m3]', panel_no=1, range=(15, 23))
logplot.set_xaxis(title='qc, qt [MPa]', panel_no=2)
logplot.set_xaxis(title='Su [kPa]', panel_no=3)
logplot.set_zaxis(title='z [m]', range=(10, 0))
logplot.set_size(width=900, height=600)
logplot.show()
```

*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*

### 4.3. Inserting a layer transition

Inserting a layer transition is easily achieved using the ```insert_layer_transition``` method.

```python
profile_2.insert_layer_transition(depth=8)

logplot = LogPlot(profile_2, no_panels=3, fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green'})
logplot.add_soilparameter_trace(
    parametername="Total unit weight [kN/m3]",
    panel_no=1)
logplot.add_soilparameter_trace(
    parametername="qc [MPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="qt [MPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="Su [kPa]",
    panel_no=3)
logplot.add_trace(
    x=su_values,
    z=depths,
    name='Su data',
    mode='markers',
    showlegend=True,
    panel_no=3)
logplot.set_xaxis(title='Total unit weight [kN/m3]', panel_no=1, range=(15, 23))
logplot.set_xaxis(title='qc, qt [MPa]', panel_no=2)
logplot.set_xaxis(title='Su [kPa]', panel_no=3)
logplot.set_zaxis(title='z [m]', range=(10, 0))
logplot.set_size(width=900, height=600)
logplot.show()
```

```text
/opt/anaconda3/lib/python3.12/site-packages/groundhog/general/soilprofile.py:265: UserWarning:

Specified depth is already at a layer transition, it will be ignored
```

*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*

### 4.4. Merging layers

Layers can be merged using their index (starting from 0 for the top layer). Note that the functionality still needs to be completed for layers with linearly varying properties. By default, the properties of the top layer are kept.

```python
profile_2.merge_layers(layer_ids=(3, 4))

logplot = LogPlot(profile_2, no_panels=3, fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green'})
logplot.add_soilparameter_trace(
    parametername="Total unit weight [kN/m3]",
    panel_no=1)
logplot.add_soilparameter_trace(
    parametername="qc [MPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="qt [MPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="Su [kPa]",
    panel_no=3)
logplot.add_trace(
    x=su_values,
    z=depths,
    name='Su data',
    mode='markers',
    showlegend=True,
    panel_no=3)
logplot.set_xaxis(title='Total unit weight [kN/m3]', panel_no=1, range=(15, 23))
logplot.set_xaxis(title='qc, qt [MPa]', panel_no=2)
logplot.set_xaxis(title='Su [kPa]', panel_no=3)
logplot.set_zaxis(title='z [m]', range=(10, 0))
logplot.set_size(width=900, height=600)
logplot.show()
```

*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*

### 4.5. Removing soil parameters

A soil parameter can be removed using its name.

```python
profile_2.remove_parameter(parameter="qt [MPa]")
profile_2
```

```text
   Depth from [m]  Depth to [m] Soil type Relative density  qc from [MPa]  \
0             0.0           1.0      SAND            Loose            3.0   
1             1.0           3.0      CLAY             None            1.0   
2             3.0           4.0      SILT     Medium dense            4.0   
3             4.0          10.0      SAND            Dense           40.0   

   qc to [MPa]  Total unit weight [kN/m3]  Su from [kPa]  Su to [kPa]  
0     4.000000                       19.0            NaN          NaN  
1     1.500000                       18.0      31.754843    30.253007  
2     8.000000                       19.0            NaN          NaN  
3    46.666667                       20.0            NaN          NaN  
```

### 4.6. Cutting a soil profile

A specific section of the soil profile can be ```cut_profile``` method. A deep copy of the soil profile is then returned which is a ```SoilProfile``` object in itself. The cutting process takes linearly varying parameters into consideration.

```python
profile_extract = profile_2.cut_profile(top_depth=0.5, bottom_depth=8)
logplot = LogPlot(profile_2, no_panels=3, fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green'})
logplot.add_soilparameter_trace(
    parametername="Total unit weight [kN/m3]",
    panel_no=1)
logplot.add_soilparameter_trace(
    parametername="qc [MPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="Su [kPa]",
    panel_no=3)
logplot.add_trace(
    x=su_values,
    z=depths,
    name='Su data',
    mode='markers',
    showlegend=True,
    panel_no=3)
logplot.set_xaxis(title='Total unit weight [kN/m3]', panel_no=1, range=(15, 23))
logplot.set_xaxis(title='qc [MPa]', panel_no=2)
logplot.set_xaxis(title='Su [kPa]', panel_no=3)
logplot.set_zaxis(title='z [m]', range=(10, 0))
logplot.set_size(width=900, height=600)
logplot.show()
```

*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*

### 4.7. Integration of a soil parameter vs depth

A soil parameter can be integrated over the depth and the resulting property can be added to the ```SoilProfile``` dataframe. This only works for soil parameters with a constant value in each layer and with properties specified in each layer (no NaN values). This can be demonstrated for the vertical effective stress, as integrated from the effective unit weight.

```python
profile_2.depth_integration(parameter='Total unit weight [kN/m3]', outputparameter='Vertical total stress [kPa]')
logplot = LogPlot(profile_2, no_panels=4, fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green'})
logplot.add_soilparameter_trace(
    parametername="Total unit weight [kN/m3]",
    panel_no=1)
logplot.add_soilparameter_trace(
    parametername="Vertical total stress [kPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="qc [MPa]",
    panel_no=3)
logplot.add_soilparameter_trace(
    parametername="Su [kPa]",
    panel_no=4)
logplot.set_xaxis(title='Total unit weight [kN/m3]', panel_no=1, range=(15, 23))
logplot.set_xaxis(title='sigmav0 [kPa]', panel_no=2)
logplot.set_xaxis(title='qc [MPa]', panel_no=3)
logplot.set_xaxis(title='Su [kPa]', panel_no=4)
logplot.set_zaxis(title='z [m]', range=(10, 0))
logplot.set_size(width=900, height=600)
logplot.show()
```

*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*

Since calculation of overburden is a recurring task in geotechnical analyses, the method ```calculate_overburden``` is implemented to calculate hydrostatic water pressure, total and effective vertical stress with a single statement.

The water level can be adjusted. If a layer interface is not present at the location of the water level, an additional interface is created. The soil profile needs to contain a column with the total unit weight to allow the calculation to happen. In layers above the water level, the total unit weight is the dry unit weight and the effective unit weight is equal to this value. In the layers below the water table, the effective unit weight is obtained by subtracting the water unit weight (default 10kN/m$^3$) from the total unit weight.

```python
profile_2.calculate_overburden(waterlevel=2.5)
```

```python
profile_2.depth_integration(parameter='Total unit weight [kN/m3]', outputparameter='Vertical total stress [kPa]')
logplot = LogPlot(profile_2, no_panels=4, fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green'})
logplot.add_soilparameter_trace(
    parametername="Total unit weight [kN/m3]",
    panel_no=1)
logplot.add_soilparameter_trace(
    parametername="Vertical total stress [kPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="Vertical effective stress [kPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="qc [MPa]",
    panel_no=3)
logplot.add_soilparameter_trace(
    parametername="Su [kPa]",
    panel_no=4)
logplot.set_xaxis(title='Total unit weight [kN/m3]', panel_no=1, range=(15, 23))
logplot.set_xaxis(title='sigmav0 [kPa]', panel_no=2)
logplot.set_xaxis(title='qc [MPa]', panel_no=3)
logplot.set_xaxis(title='Su [kPa]', panel_no=4)
logplot.set_zaxis(title='z [m]', range=(10, 0))
logplot.set_size(width=900, height=600)
logplot.show()
```

*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*

## 5. Gridding functionality

The ```SoilProfile``` object can be mapped onto a grid. All that is required is a list or Numpy array with the depth coordinates of the grid. The method ```map_soilprofile``` returns a dataframe with the mapped soil parameters.

```python
grid = profile_2.map_soilprofile(
    nodalcoords=np.linspace(0, 10, 21))
```

```python
logplot = LogPlot(profile_2, no_panels=4, fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green'})
logplot.add_soilparameter_trace(
    parametername="Total unit weight [kN/m3]",
    panel_no=1)
logplot.add_soilparameter_trace(
    parametername="Vertical total stress [kPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="Vertical effective stress [kPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="qc [MPa]",
    panel_no=3)
logplot.add_trace(
    x=grid['qc [MPa]'],
    z=grid['z [m]'],
    name='Gridded qc',
    mode='markers',
    showlegend=True,
    panel_no=3)
logplot.add_soilparameter_trace(
    parametername="Su [kPa]",
    panel_no=4)
logplot.set_xaxis(title='Total unit weight [kN/m3]', panel_no=1, range=(15, 23))
logplot.set_xaxis(title='sigmav0 [kPa]', panel_no=2)
logplot.set_xaxis(title='qc [MPa]', panel_no=3)
logplot.set_xaxis(title='Su [kPa]', panel_no=4)
logplot.set_zaxis(title='z [m]', range=(10, 0))
logplot.set_size(width=900, height=600)
logplot.show()
```

*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*

```python
grid.head()
```

```text
   z [m] Soil type Relative density  qc [MPa]  Total unit weight [kN/m3]  \
0    0.0      SAND            Loose     3.000                       19.0   
1    0.5      SAND            Loose     3.500                       19.0   
2    1.0      CLAY             None     1.000                       18.0   
3    1.5      CLAY             None     1.125                       18.0   
4    2.0      CLAY             None     1.250                       18.0   

    Su [kPa]  Vertical total stress [kPa]  Water unit weight [kN/m3]  \
0        NaN                          0.0                        0.0   
1        NaN                          9.5                        0.0   
2  31.754843                         19.0                        0.0   
3  31.379384                         28.0                        0.0   
4  31.003925                         37.0                        0.0   

   Effective unit weight [kN/m3]  Hydrostatic pressure [kPa]  \
0                           19.0                         0.0   
1                           19.0                         0.0   
2                           18.0                         0.0   
3                           18.0                         0.0   
4                           18.0                         0.0   

   Vertical effective stress [kPa]  
0                              0.0  
1                              9.5  
2                             19.0  
3                             28.0  
4                             37.0  
```

## 6. Changing the depth scale

When converting from metric to imperial units and vice versa, depth scales need to be converted from m to ft.

This can be done using the ```.convert_depth_reference``` method. The new unit name and the conversion factor need to be specified:

```python
profile_2.convert_depth_reference(newunit='ft', multiplier=1/0.3048)
```

```python
logplot = LogPlot(profile_2, no_panels=3, fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green'})
logplot.add_soilparameter_trace(
    parametername="Total unit weight [kN/m3]",
    panel_no=1)
logplot.add_soilparameter_trace(
    parametername="qc [MPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="Su [kPa]",
    panel_no=3)
logplot.set_xaxis(title='Total unit weight [kN/m]', panel_no=1, range=(15, 23))
logplot.set_xaxis(title='qc [MPa]', panel_no=2)
logplot.set_xaxis(title='Su [kPa]', panel_no=3)
logplot.set_zaxis(title='z [ft]', range=(10 / 0.3048, 0))
logplot.set_size(width=900, height=600)
logplot.show()
```

*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*

The depth scale can be converted back to meters again:

```python
profile_2.convert_depth_reference(newunit='m', multiplier=0.3048)
```

```python
logplot = LogPlot(profile_2, no_panels=3, fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green'})
logplot.add_soilparameter_trace(
    parametername="Total unit weight [kN/m3]",
    panel_no=1)
logplot.add_soilparameter_trace(
    parametername="qc [MPa]",
    panel_no=2)
logplot.add_soilparameter_trace(
    parametername="Su [kPa]",
    panel_no=3)
logplot.set_xaxis(title='Total unit weight [kN/m]', panel_no=1, range=(15, 23))
logplot.set_xaxis(title='qc [MPa]', panel_no=2)
logplot.set_xaxis(title='Su [kPa]', panel_no=3)
logplot.set_zaxis(title='z [m]', range=(10, 0))
logplot.set_size(width=900, height=600)
logplot.show()
```

*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*
