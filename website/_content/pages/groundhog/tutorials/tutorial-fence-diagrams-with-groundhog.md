---
title: Tutorial - Fence diagrams with ```groundhog```
slug: groundhog/tutorials/tutorial-fence-diagrams-with-groundhog
section: Groundhog Guides
description: Since version 0.3.0,
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/notebooks/Tutorial%20-%20Fence%20diagrams%20with%20groundhog.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted.'
notebook: notebooks/Tutorial - Fence diagrams with groundhog.ipynb
---

Since version 0.3.0, ```groundhog``` offers the possibility to plot CPT data and ```SoilProfile``` objects along a profile line.

The profile line is defined either by the name of a start and endpoint or through the specification of coordinates. To make use of the fence diagram plotting functionality, ```groundhog``` requires ```SoilProfile``` and ```PCPTProcessing``` objects to be georeferenced.

A list of georeferenced ```SoilProfile``` or ```PCPTProcessing``` objects is passed to the the plotting functions and the routine will plot only the locations within a certain band around the profile line. The locations are projected on the profile line and the offsets from the profile line are indicated in the plot.

This notebook demonstrates how the fence diagram plotting functionality works, based on the publically available data from Borssele I. This data is made available by RVO under a Creative Commons NC-BY-SA license.

## 1. Library imports

The necessary functions for plotting the fence diagrams need to be imported from the ```groundhog.general.soilprofile``` and ```groundhog.siteinvestigation.insitutests.pcpt_processing``` modules. Since the CPT data is given in AGS 4.0 format, we need to load the ```AGSConverter```.

```python
from groundhog.general.soilprofile import SoilProfile, read_excel, plot_fence_diagram
from groundhog.siteinvestigation.insitutests.pcpt_processing import PCPTProcessing, plot_longitudinal_profile, \
    plot_combined_longitudinal_profile
from groundhog.general.agsconversion import AGSConverter
```

Since Plotly figures will be rendered in the notebook, we need to call the ```init_notebook_mode``` function of Plotly.

```python
from plotly.offline import init_notebook_mode
init_notebook_mode()
```

*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*

## 2. Profile line location

The profile line is drawn in the Souternmost portion of the windfarm.

<img src="/docs/assets/groundhog/notebooks/Images/BorsseleI_locations.png">
<br><center><b>Figure 1: CPT and borehole locations</b></center>

We will plot data on two profiles, one from BH-WFS1-3 to BH-WFS1-6 and one defined based on the coordinates of a start and end point.

The coordinates of the start and end point are defined.

```python
start_point = (499000, 5733000)
end_point = (510000, 5728000)
```

## 3. PCPT data

The PCPT data can be read from the .asc data for locations, BH-WFS1-3, BH-WFS1-2A, BH-WFS1-5A and BH-WFS1-6. In this tutorial, we will plot the cone tip resistance from the downhole PCPTs along the profile.

We can create a ```PCPTProcessing``` object for each of the downhole PCPTs.

```python
locations = ['BH-WFS1-3', 'BH-WFS1-2A', 'BH-WFS1-5A', 'BH-WFS1-6']
```

Note that a loop could easily be written but we will leave this as a code optimisation for advanced Python users.

```python
cpt_3 = PCPTProcessing(title='PCPT BH-WFS1-3')
converter = AGSConverter(path="Data/N6016_BH_WFS1-3_AGS4_150909.ags")
converter.create_dataframes(selectedgroups=['SCPT'], verbose_keys=True, use_shorthands=True)
cpt_3.load_pandas(
    df=converter.data['SCPT'],
    z_key="Depth [m]",
    qc_key="qc [MN/m2]",
    fs_key="fs [kN/m2]",
    u2_key="u2 [kN/m2]",
    push_key="Test reference or push number",
    fs_multiplier=0.001, u2_multiplier=0.001)

cpt_2A = PCPTProcessing(title='PCPT BH-WFS1-2A')
converter = AGSConverter(path="Data/N6016_BH_WFS1-2A_AGS4_150909.ags")
converter.create_dataframes(selectedgroups=['SCPT'], verbose_keys=True, use_shorthands=True)
cpt_2A.load_pandas(
    df=converter.data['SCPT'],
    z_key="Depth [m]",
    qc_key="qc [MN/m2]",
    fs_key="fs [kN/m2]",
    u2_key="u2 [kN/m2]",
    push_key="Test reference or push number",
    fs_multiplier=0.001, u2_multiplier=0.001)

cpt_5A = PCPTProcessing(title='PCPT BH-WFS1-5A')
converter = AGSConverter(path="Data/N6016_BH_WFS1-5A_AGS4_150909.ags")
converter.create_dataframes(selectedgroups=['SCPT'], verbose_keys=True, use_shorthands=True)
cpt_5A.load_pandas(
    df=converter.data['SCPT'],
    z_key="Depth [m]",
    qc_key="qc [MN/m2]",
    fs_key="fs [kN/m2]",
    u2_key="u2 [kN/m2]",
    push_key="Test reference or push number",
    fs_multiplier=0.001, u2_multiplier=0.001)

cpt_6 = PCPTProcessing(title='PCPT BH-WFS1-6')
converter = AGSConverter(path="Data/N6016_BH_WFS1-6_AGS4_150909.ags")
converter.create_dataframes(selectedgroups=['SCPT'], verbose_keys=True, use_shorthands=True)
cpt_6.load_pandas(
    df=converter.data['SCPT'],
    z_key="Depth [m]",
    qc_key="qc [MN/m2]",
    fs_key="fs [kN/m2]",
    u2_key="u2 [kN/m2]",
    push_key="Test reference or push number",
    fs_multiplier=0.001, u2_multiplier=0.001)
```

We can set the positions of the ```PCPTProcessing``` objects using the ```set_position``` method. This requires the easting, northing and elevation (negative for water depth) of the test location. Horizontal positions are defined in a coordinate system with a given ```srid``` (more info on https://epsg.io/). The vertical datum can also be set. This is in mLAT by default.

```python
cpt_3.set_position(easting=499081.02, northing=5732354.88, elevation=-32.8, srid=25831)
cpt_2A.set_position(easting=502763.64, northing=5732537.58, elevation=-24.6, srid=25831)
cpt_5A.set_position(easting=505926.68, northing=5730101.12, elevation=-25.5, srid=25831)
cpt_6.set_position(easting=508454.6, northing=5728133.69, elevation=-31.6, srid=25831)
```

Plotting the cone tip resistance vs depth along the profile line between location BH-WFS1-3 and BH-WFS1-6 is a matter of filling in the correct arguments in the ```plot_longitudinal_profile``` function.

First, a list with the ```PCPTProcessing``` objects is provided. These have a title and are georeferenced. The routine first check whether the locations are within a specified band surrounding the profile line. Since location BH-WFS1-2A is at an offset greater than 1000m (default for ```band```), we can increase this value.

The ```scale_factor``` argument controls the magnitude of the $ q_c $ values on the longitudinal profile. This scale factor can be adjusted until the desired information is well visualised in the plot.

```python
pcpt_fig = plot_longitudinal_profile(
    cpts=[cpt_3, cpt_2A, cpt_5A, cpt_6],
    start='PCPT BH-WFS1-3', end='PCPT BH-WFS1-6',
    band=2000, scale_factor=10
    )
```

![Notebook output 1](/docs/assets/groundhog/notebooks/outputs/tutorial-fence-diagrams-with-groundhog-1.png)

We can see that the different water depths of the CPTs are taken into account. Lateral continuity of the layers can be inspected.

## 4. Soil profile

A borehole log is available for the identified locations. We can import the borehole log information using the ```read_excel``` function. This function returns a ```SoilProfile``` objects.

```python
profile_3 = read_excel('Data/profile_BorsseleI_3.xlsx', title="BH-WFS1-3")
profile_2A = read_excel('Data/profile_BorsseleI_2A.xlsx', title="BH-WFS1-2A")
profile_5A = read_excel('Data/profile_BorsseleI_5A.xlsx', title="BH-WFS1-5A")
profile_6 = read_excel('Data/profile_BorsseleI_6.xlsx', title="BH-WFS1-6")
```

We can also georeference this boreholes using the ```set_position``` method of the ```SoilProfile``` object.

```python
profile_3.set_position(easting=499081.02, northing=5732354.88, elevation=-32.8, srid=25831)
profile_2A.set_position(easting=502763.64, northing=5732537.58, elevation=-24.6, srid=25831)
profile_5A.set_position(easting=505926.68, northing=5730101.12, elevation=-25.5, srid=25831)
profile_6.set_position(easting=508454.6, northing=5728133.69, elevation=-31.6, srid=25831)
```

For plotting the different soiltypes, we need to create a dictionary in which we assign a color to each soil type. We will use Hex color codes for this.

```python
color_dict = {
    'SAND': '#ffe300', # Yellow
    'Silty SAND': '#fff5a3', # Light yellow
    'Clayey SAND': '#c2ae0c', # Dark yellow
    'Gravelly SAND': '#868a44', # Yellow with a shade of grey
    'CLAY': '#af7337' # Brown
}
```

We can now plot the profile by filling the correct arguments in the ```plot_fence_diagram``` function.

A list with ```SoilProfile``` objects is provided as well as the start and end point name through the name of the corresponding soil profile title. The colors of each soil type are defined through the ```fillcolordict``` dictionary.

The ```opacity``` argument can be varied from 0 to 1 and the ```logwidth``` argument can be adjusted until the logs are wide enough for good visual presentation.

```python
profile_fig = plot_fence_diagram(
    profiles=[profile_3, profile_2A, profile_5A, profile_6],
    start='BH-WFS1-3', end='BH-WFS1-6', band=2000,
    fillcolordict=color_dict,
    opacity=0.8, logwidth=250)
```

![Notebook output 2](/docs/assets/groundhog/notebooks/outputs/tutorial-fence-diagrams-with-groundhog-2.png)

The different water depths of the boreholes are again taken into account. Lateral continuity can be inspected although the interpretation of the soil type plays a role in the interpretation. Going back to the actual borehole logs is always a good idea.

## 5. Combined PCPT + soil profile plot

PCPT data (cone tip resistance) and the layering can be visualised on the same profile plot through the ```plot_combined_longitudinal_profile``` function.

Here, we will use the profile between the two speficied points by using the ```options='coords'``` argument. Instead of a now, a pair of coordinates is now passed to the function.

```python
cpt_profile_fig = plot_combined_longitudinal_profile(
    cpts=[cpt_3, cpt_2A, cpt_5A, cpt_6],
    profiles=[profile_3, profile_2A, profile_5A, profile_6],
    option='coords', start=start_point, end=end_point, band=1000,
    fillcolordict=color_dict,
    opacity=0.8, logwidth=250, scale_factor=10)
```

![Notebook output 3](/docs/assets/groundhog/notebooks/outputs/tutorial-fence-diagrams-with-groundhog-3.png)

This demonstrates that the borehole logs are based on the CPT data to an important degree. Offsets are now different since the offsets have been calculated in relation to the coordinate-based profile line and not the line between BH-WFS1-3 and BH-WFS1-6.
