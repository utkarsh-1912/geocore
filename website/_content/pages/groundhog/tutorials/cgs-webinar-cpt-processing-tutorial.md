---
title: CGS webinar - CPT processing tutorial
slug: groundhog/tutorials/cgs-webinar-cpt-processing-tutorial
section: Groundhog Guides
description: CGS webinar - CPT processing tutorial This notebook presents the workflow for CPT processing with
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/notebooks/CGS%20webinar%20-%20CPT%20processing%20tutorial.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted, with a short note on how to run this in GeoCore prepended.'
notebook: notebooks/CGS webinar - CPT processing tutorial.ipynb
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, run the same calculation through a [calculation form](/docs/geocore/using/modules) or by asking **GeoAI**, which calls the same groundhog function through its validated Tool Registry. This notebook is kept for anyone who wants to call groundhog directly from their own Python code instead.

# CGS webinar - CPT processing tutorial

This notebook presents the workflow for CPT processing with ```groundhog```, presented during a webinar of the Canadian Geotechnical Society eduction committee on the Future of Geotechnical Engineering Education.

This notebook shows how ```groundhog``` functionality can be used to easily load, process and present CPT data. The abilities of Python and ```groundhog``` to automate processing and present results from several CPTs are also illustrated.

The CPT information used in this tutorial is from the [Borssele offshore windfarm site](https://offshorewind.rvo.nl/studiesborsseleI) which is used under a Creative Commons 4.0 license.

## User inputs

```python
NKT = 15
```

## Loading libraries

For the processing of CPT data, we will need the ```PCPTProcessing``` class from ```groundhog```. This class encodes all required functionality to perform CPT processing. We can import it as follows:

```python
from groundhog.siteinvestigation.insitutests.pcpt_processing import PCPTProcessing
```

We will also import the Pandas library for data processing.

```python
import pandas as pd
```

The Plotly libraries can also be loaded.

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

## Data loading

We will process CPT data for test location WFS1-2 at the Borssele offshore wind farm site. The data for this CPT is provided in AGS 4.0 format, a common data transfer format in geotechnical engineering.

```groundhog``` allows import of CPT data from many different sources. We will start be creating a ```PCPTProcessing``` object for the selected PCPT.

```python
cpt = PCPTProcessing(title="WFS1-2")
```

Loading the data can happen using the ```load_ags``` method. Internally, this makes use of the AGS conversion functionality in ```groundhog``` which generates a dataframe from an AGS file.

When looking at the AGS file, you can see that the headers are not very straightforward. When loading CPT data, ```groundhog``` expects the following columns:

   - Depth in m - Default column key = ```z [m]```
   - Cone tip resistance in MPa - Default column key = ```qc [MPa]```
   - Sleeve friction in MPa (optional) - Default column key = ```fs [MPa]```
   - Pore pressure at the shoulder in MPa (optional) - Default column key = ```u2 [MPa]```
   
For CPTs with multiple pushes, we also need to tell ```groundhog``` which column contains the identifier for the push. Here, there is only one push.
   
The AGS files has different names for these required keys, so we need to tell ```groundhog``` what they are. Moreover, $ f_s $ and $ u_2 $ have units of kPa so we need to convert to MPa by specifying the appropriate multiplier.

```python
cpt.load_ags(
    path="Data/N6016_BH_WFS1-2_AGS4_150909.ags",
    z_key="SCPT_DPTH [m]", qc_key="SCPT_RES [MN/m2]", fs_key="SCPT_FRES [kN/m2]", u2_key="SCPT_PWP2 [kN/m2]",
    fs_multiplier=0.001, u2_multiplier=0.001,
    push_key="SCPG_TESN")
```

Plotting the raw CPT data is then simply achieved using the ```plot_raw_pcpt``` methods. Note that plotting ranges and tick mark intervals can be customised (as shown here for the pore pressure).

```python
cpt.plot_raw_pcpt(u2_range=(-0.5, 2), u2_tick=0.25)
```

The CPT data itself is contained in the ```.data``` attribute, which we can print to the notebook (```.head()``` only plots the first five rows).

```python
cpt.data.head()
```

## Data correction and normalisation

Since the CPT data has a pore pressure sensor at the shoulder, we need to correct for the unequal area effect. Since the pore water is also pushing on the rear of the cone, the total cone resistance $ q_t $ is less than the measured cone tip resistance $ q_c $.

### Cone properties

To apply this correction, we need to know the cone properties. ```groundhog``` expects the cone properties in a standard format, which we can load:

```python
from groundhog.siteinvestigation.insitutests.pcpt_processing import DEFAULT_CONE_PROPERTIES
DEFAULT_CONE_PROPERTIES
```

This table contains the required cone properties. We can either create a similar table in Excel and load it, or replace the values in the dataframe.

The AGS file also contains the cone properties, so we can load them.

```python
from groundhog.general.agsconversion import AGSConverter
converter = AGSConverter(path="Data/N6016_BH_WFS1-2_AGS4_150909.ags")
converter.create_dataframes(selectedgroups=['SCPG'], verbose_keys=True, use_shorthands=True)
converter.data['SCPG'].head()
```

```python
from groundhog.general.soilprofile import read_excel
```

The cone properties can either be converted from the dataframe above, or they can be read from an Excel file. Note that the cone properties need to be loaded as a ```groundhog``` ```SoilProfile``` object to make use of the functionality embedded in the object.

```python
cone_props = read_excel("Data/WFS1-2_cone_props.xlsx")
cone_props
```

### Layering

We also need to specify a (preliminary) layering with the associated total unit weights and soil types. We can encode this programmatically or load from Excel.

```python
layering = read_excel("Data/WFS1-2_layering_b.xlsx")
layering
```

### Mapping cone properties and layering

Once the layering and cone properties are known, we can map them to the cone data. This means that each data point (i.e. each depth) will get a cone properties and a layer assigned to it. This will allow us to do further calculations.

In addition to the mapping, a vertical stress calculation is also performed. By default, the water level is assumed at the surface, but we can put it at another level to represent a soil profile where the phreatic surface is some distance below the ground. Since this is an offshore CPT, the water level is indeed at 0m.

```python
cpt.map_properties(layer_profile=layering, cone_profile=cone_props, waterlevel=0)
```

```python
cpt.data.head()
```

```python
cpt.plot_raw_pcpt(u2_range=(-0.5, 2), u2_tick=0.25)
```

### Normalisation

With the cone properties and stresses being known for each depth, the normalisation formulae can be applied. These formulae are encoded in ```groundhog``` and explained in the documentation. The method ```normalise_pcpt``` applies them all at once.

Columns with the normalised properties are added to the ```.data``` attribute of our ```PCPTProcessing``` object.

```python
cpt.normalise_pcpt()
```

```python
cpt.data.head()
```

We can also plot the normalised properties and check the validity of our layering selection.

```python
cpt.plot_normalised_pcpt()
```

### Data export

The processing we have just done can be saved in an Excel file which contains the CPT data, selected layering, cone properties and the location of the CPT.

```python
cpt.to_excel(output_path="Data/Excel export.xlsx")
```

## Soil type classification

### Robertson charts

The Robertson chart allows us to classify soil types based on the combination of normalised cone tip resistance and normalised friction ratio or pore pressure ratio.

```groundhog``` does this automatically and plots the combinations for the selected layers into a Robertson chart. This also shows that this data is often scattered and judgement needs to be applied.

```python
cpt.plot_robertson_chart()
```

## Soil parameter correlations

Correlation between CPT properties and other soil mechanics parameters can be applied to obtain parameters for geotechnical calculation. 

A common example is to derive the relative density for sand and the undrained shear strength for cohesive soils.

```groundhog``` implements a number of soil parameter correlations and provides a standard interface for applying them.

Each soil parameter correlation is implemented as a Python function in the module ```groundhog.siteinvestigation.insitutests.pcpt_correlations```. Each function is fully documented and validation is applied. We can check which correlations are available:

```python
from groundhog.siteinvestigation.insitutests.pcpt_processing import CORRELATIONS
CORRELATIONS.keys()
```

Here, we will apply the following correlations:

   - ```'Dr Jamiolkowski et al (2003)'``` for relative density in cohesionless soils
   - ```'Su Rad and Lunne (1988)'``` for undrained shear strength of cohesive soils
   
When looking at our layering, we can see that we have a interbedded ```SAND/CLAY``` layer for which we need to determine whether the behaviour will be cohesionless or cohesive. Due to the excess pore pressures measured, we will treat the layer as cohesive.

### Relative density

The relative density is calculated with the following formulae (see docs):

$$ D_{r,dry} = \frac{1}{2.96} \cdot \ln \left[ \frac{q_c / P_a}{24.94 \cdot \left( \frac{\sigma_{m}^{\prime}}{P_a} \right)^{0.46} } \right]\\D_{r,sat} = \left(  \frac{-1.87 + 2.32 \cdot \ln \left[ \frac{q_c}{\sqrt{P_a + \sigma_{vo}^{\prime}}} \right] }{100} \right) \cdot \frac{D_{r,dry}}{100} $$

The function requires cone tip resistance $ q_c $, vertical effective stress $ \sigma_{vo}^{\prime} $ and also the coefficient of lateral earth pressure $ K_0 $ to calculate the mean effective stress $ \sigma_m^{\prime} $

The function returns a dictionary with the keys ```Dr dry [-]``` for relative density in dry soil and ```Dr sat [-]``` for relative density in saturated soil.

We can apply the correlation with the ```apply_correlation``` method and then need to enter the following information:

   - The title of the correlation to be used (```'Dr Jamiolkowski et al (2003)'```)
   - A dictionary containing the keys in the function output as keys (```'Dr sat [-]'```) and the desired column names (```'Dr [-]'```) as values
   - The coefficient of lateral earth pressure (```k0```) which is an argument for the correlation
   - Which soil types to apply the correlation to. Here, we will only apply it to ```SAND```. Note that we need to supply a Python list here.
   
Note that ```groundhog``` will issue warnings when we go outside the validation ranges of the function, but the calculation will not break down.

```python
cpt.apply_correlation('Dr Jamiolkowski et al (2003)', outputs={'Dr sat [-]': 'Dr [-]'},
                      k0=0.8,
                      apply_for_soiltypes=['SAND',])
```

We can check the numerical output:

```python
cpt.data.head()
```

### Undrained shear strength

The undrained shear strength can be derived from the net cone resistance ($ q_{net} = q_t - \sigma_{vo} $) as follows:

$$ S_u = \frac{q_{net}}{N_k} $$

The factor $ N_k $ is usually determined based on correlations between the CPT and laboratory measurements. For North Sea soils, this value is typically between 15 and 20. We will apply an average factor of 17.5 here.

The correlation is applied using the same syntax as for the relative density, but here we will apply it to ```CLAY``` and ```SAND/CLAY```.

```python
cpt.apply_correlation('Su Rad and Lunne (1988)', outputs={'Su [kPa]': 'Su [kPa]'},
                      Nk=NKT,
                      apply_for_soiltypes=['CLAY', 'SAND/CLAY'])
```

### Visualising soil parameter correlations

```groundhog``` contains functionality for visualising CPT data using a relatively simple syntax. It is always instructive to show a color-coded soil profile next to soil parameter plots and that's what the class ```LogPlot``` does.

We first need to defined a Python dictionary with the colors for each soil type:

```python
fillcolors = {
    "SAND": "yellow",
    "CLAY": "brown",
    "SAND/CLAY": "orange",
    "SILT": "green"
}
```

Then we need to tell the method which parameters to plot. The argument ```prop_keys``` takes a list of soil parameter title lists. In the example, we will plot three panels, one for $ q_c $, one for $ D_r $ and one for $ S_u $. Each panel only contains one trace, so we have lists of one element.

We can specify whether to show the legend or not (```showlegends``` argument), what the ranges for our X-axes are (```plot_ranges``` argument) and the tick intervals on our X-axes (```plot_ticks``` argument). The X-axis titles can be specified (```axis_titles``` argument, note the $ \LaTeX $ syntax).

Finally, we set the z-range of our plot (```zrange``` argument) and can customise the layout using Plotly syntax (```layout``` argument). The colors for the soil profile are passed in the ```fillcolordict``` argument.

```python
from groundhog.general.plotting import LogPlot
```

```python
cpt_processed_plot = LogPlot(layering, no_panels=3, fillcolordict=fillcolors)
cpt_processed_plot.add_trace(
    x=cpt.data['qc [MPa]'],
    z=cpt.data['z [m]'],
    name='qc',
    showlegend=True,
    panel_no=1)
cpt_processed_plot.add_trace(
    x=cpt.data['qt [MPa]'],
    z=cpt.data['z [m]'],
    name='qt',
    showlegend=True,
    panel_no=1)
cpt_processed_plot.add_trace(
    x=cpt.data['Dr [-]'],
    z=cpt.data['z [m]'],
    name='Dr',
    showlegend=False,
    panel_no=2)
cpt_processed_plot.add_trace(
    x=cpt.data['Su [kPa]'],
    z=cpt.data['z [m]'],
    name='Su',
    showlegend=False,
    panel_no=3)
cpt_processed_plot.set_xaxis(title=r'$ q_c, \ q_t \ \text{[MPa]} $', panel_no=1)
cpt_processed_plot.set_xaxis(title=r'$ D_r \ \text{[-]} $', panel_no=2, range=(0, 1.2))
cpt_processed_plot.set_xaxis(title=r'$ S_u \ \text{[kPa]} $', panel_no=3)
cpt_processed_plot.set_zaxis(title=r'$ z \ \text{[m]} $', range=(30, 0))
cpt_processed_plot.show()
```

## Visualising spatial variability

```groundhog``` allows the rapid creation of profile lines which plot multiple CPT traces along a profile. For this purpose, we need to set the position of the CPTs using the ```set_position``` method.

We will load 4 CPTs from their AGS files and plot the CPT traces on one profile.

This example also demonstrates the automation possibilities of Python and ```groundhog```. We can first create a list of the locations for the profile.

```python
locations = ['WFS1-3', 'WFS1-2A', 'WFS1-5A', 'WFS1-6']
```

We will create an empty list to store the CPTs:

```python
profile_cpts = []
```

We can then loop over the locations and create ```PCPTProcessing``` objects for each. The path is made parametric to allow reading the different files.

Once the data is read, the ```PCPTProcessing``` object is appended to the list ```profile_cpts```.

```python
for _loc in locations:
    _profile_cpt = PCPTProcessing(title=_loc)
    _profile_cpt.load_ags(
        path="Data/N6016_BH_%s_AGS4_150909.ags" % _loc,
        z_key="SCPT_DPTH [m]", qc_key="SCPT_RES [MN/m2]", fs_key="SCPT_FRES [kN/m2]", u2_key="SCPT_PWP2 [kN/m2]",
        push_key="SCPG_TESN",
        fs_multiplier=0.001, u2_multiplier=0.001)
    profile_cpts.append(_profile_cpt)
```

We can of course check the output for an individual CPT by using Python's syntax for accessing list elements.

```python
profile_cpts[0].plot_raw_pcpt()
```

We then need to fix the locations of our CPTs in space. Coordinates and elevations can be retrieved from survey reports. It is important to add the correct coordinate system. Note that the longitudinale profiles will not work with latitude and longitude information.

```python
eastings = [499081.02, 502763.64, 505926.68, 508454.6]
northings = [5732354.88, 5732537.58, 5730101.12, 5728133.69]
elevations = [-32.8, -24.6, -25.5, -31.6]
SRID = 25831
```

We can loop over each CPT and set its position. The ```enumerate``` operator is very handy in this respect.

```python
for i, _cpt in enumerate(profile_cpts):
    _cpt.set_position(easting=eastings[i], northing=northings[i], elevation=elevations[i], srid=SRID)
```

Plotting of the longitudinal profile is done by the ```plot_longitudinal_profile``` method. This method returns a Plotly figure and visualizes the CPT information along the profile.

```python
from groundhog.siteinvestigation.insitutests.pcpt_processing import plot_longitudinal_profile
```

We need to determine the start and the end point of the profile and the band in which the algorithm will search for locations. The offset from the profile line is rendered in the plot. The CPT trace can be made bigger or smaller using the ```scale_factor``` argument.

```python
pcpt_fig = plot_longitudinal_profile(
    cpts=profile_cpts,
    start='WFS1-3', end='WFS1-6',
    band=2000, scale_factor=10
    )
```

<img src="/docs/assets/groundhog/notebooks/Images/groundhog_banner_wide.png">
