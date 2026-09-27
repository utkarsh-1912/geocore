---
title: Groundhog parameter selection example
slug: groundhog/tutorials/tutorial-groundhog-parameter-selection-example
section: Groundhog Guides
description: This notebook illustrates how geotechnical parameters can be selected with groundhog using the automatic selection and the LogPlotMatplotlib functionality.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/notebooks/Tutorial%20-%20Groundhog%20parameter%20selection%20example.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted.'
notebook: notebooks/Tutorial - Groundhog parameter selection example.ipynb
---

This notebook illustrates how geotechnical parameters can be selected with ``groundhog`` using the automatic selection and the ``LogPlotMatplotlib`` functionality.

## Stratigraphy

We will need to use the ``qt`` plotting backend to allow interactive plotting.

```python
%matplotlib qt
```

We will read a ``SoilProfile`` object using the ``read_excel`` method from the ``soilprofile`` module. This methods reads Excel files with a proper definition of stratigraphy and imports them as a ``SoilProfile`` object.

```python
from groundhog.general.soilprofile import read_excel
```

A ``SoilProfile`` with the name ``sp`` is loaded from the Excel file ``bh_log.xlsx``.

```python
sp = read_excel('Data/bh_log.xlsx')
sp
```

## Undrained shear strength data

We can import undrained shear strength data from various sources; hand-held tools, UU and CU triaxial and DSS. Undrained shear strength can also be calculated from CPT data using a cone factor $N_{kt}$.

### Data from hand-held 

We will import the data using the Pandas library. The data from measurements with hand-held tools is stored in the file ``su_handtools_1.xlsx``.

```python
import pandas as pd
```

```python
su_handtools_results = pd.read_excel('Data/su_handtools_1.xlsx')
su_handtools_results.head()
```

### From CU tests

The data from consolidated undrained triaxial tests is stored in the file ``cu_1.xlsx``.

```python
su_cu_results = pd.read_excel('Data/cu_1.xlsx')
su_cu_results.head()
```

### UU tests

Import the data for unconsolidated undrained triaxial testing from the file ``uu_1.xlsx``.

```python
su_uu_results = pd.read_excel('Data/uu_1.xlsx')
su_uu_results.head()
```

### DSS tests

For constant volume direct simple shear testing, used ``dss_cv_1.xlsx``.

```python
su_dss_results = pd.read_excel('Data/dss_cv_1.xlsx')
su_dss_results.head()
```

### CPT tests

CPT data can be used to calculate the undrained strength. We will import CPT data for which the undrained shear strength has already been calculated.

Note that Python is also very useful to determine the $N_{kt}$ factor for undrained shear strength calculation from CPT data, but this is beyond the scope of this tutorial.

```python
from groundhog.siteinvestigation.insitutests.pcpt_processing import PCPTProcessing
```

The CPT data can be imported from the file ``cpt.xlsx``.

```python
pcpt = PCPTProcessing('CPT')
pcpt.load_excel('Data/cpt.xlsx')
pcpt.plot_raw_pcpt(latex_titles=False)
```

Based on the CPT data, we can see that there are clay layers in the profile. We will work on the data from the clay layer between 8.2m and 49m.

We can select the $ S_u $ data for this clay layer only.

```python
cpt_su = pcpt.data[
    (pcpt.data['z [m]'] >= 8.2) & 
    (pcpt.data['z [m]'] <= 49)][['z [m]', 'Su [kPa]']].reset_index(drop=True)
cpt_su.head()
```

### Plotting all data

To allow parameter selection, we need to open the ``LogPlotMatplotlib`` object in a separate window.

We will create the plot from the available ``SoilProfile`` (``sp``) and will add traces for each each of the data sources. Axis titles and ranges are also customised.

```python
from groundhog.general.plotting import LogPlotMatplotlib

logplot = LogPlotMatplotlib(
   soilprofile=sp,
   no_panels=1,
   fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SAND/CLAY': 'orange'})
logplot.add_trace(
    x=su_handtools_results['Su [kPa]'],
    z=su_handtools_results['Depth [m]'], name='Handtools', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_cu_results['Su peak q [kPa]'],
    z=su_cu_results['Depth [m]'], name='CU', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_uu_results['Su peak [kPa]'],
    z=su_uu_results['Depth [m]'], name='UU', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_dss_results['Failure shear stress [kPa]'],
    z=su_dss_results['Depth [m]'], name='DSS', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=cpt_su['Su [kPa]'],
    z=cpt_su['z [m]'], name='From CPT', panel_no=1, showlegend=True)

logplot.set_xaxis_title(title='$ S_u $ [kPa]', panel_no=1, size=15)
logplot.set_zaxis_title(title='$ z $ [m]')
logplot.set_xaxis_range(min_value=0, max_value=350, panel_no=1)
logplot.set_zaxis_range(min_depth=0, max_depth=50)
logplot.show()
```

You can close the plot after inspecting it.

## Automatic selection with ``selection_soilparameter``

We can run the ``.selection_soilparameter`` method on the CPT data for fully automated soil parameter selection. This will select a trend based on the conditions set by the keyword arguments. Constant values or linear variations can be used. A minimum, mean or maximum can be selected.

Note that automated selections are not always the best choice, so always inspect the results of an automated parameter selection process.

### Mean constant value

First, we select a mean value in each layer based on the $ S_u $ values from the CPT.

```python
sp.selection_soilparameter(
    parameter='Su [kPa]',
    depths=cpt_su['z [m]'],
    values=cpt_su['Su [kPa]'])
```

The selected values can be plotted in the ``LogPlotMatplotlib``.

```python
logplot = LogPlotMatplotlib(
   soilprofile=sp,
   no_panels=1,
   fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SAND/CLAY': 'orange'})
logplot.add_trace(
    x=su_handtools_results['Su [kPa]'],
    z=su_handtools_results['Depth [m]'], name='Handtools', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_cu_results['Su peak q [kPa]'],
    z=su_cu_results['Depth [m]'], name='CU', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_uu_results['Su peak [kPa]'],
    z=su_uu_results['Depth [m]'], name='UU', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_dss_results['Failure shear stress [kPa]'],
    z=su_dss_results['Depth [m]'], name='DSS', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=cpt_su['Su [kPa]'],
    z=cpt_su['z [m]'], name='From CPT', panel_no=1, showlegend=True)
logplot.add_soilparameter_trace(parametername='Su [kPa]', panel_no=1, ls='--')
logplot.set_xaxis_title(title='$ S_u $ [kPa]', panel_no=1, size=15)
logplot.set_zaxis_title(title='$ z $ [m]')
logplot.set_xaxis_range(min_value=0, max_value=350, panel_no=1)
logplot.set_zaxis_range(min_depth=0, max_depth=50)
logplot.show()
```

You can close this plot after inspecting it.

You can also see the numerical values of the selected $ S_u $ in each layer:

```python
sp
```

We remove this column with automatically selected $ S_u $ values again to demonstrate alternative selection methods.

```python
sp.remove_parameter('Su [kPa]')
```

### Linearly varying mean value

``groundhog`` can also fit linear relations in each layer with the following code:

```python
sp.selection_soilparameter(
    parameter='Su [kPa]',
    depths=cpt_su['z [m]'],
    values=cpt_su['Su [kPa]'],
    linearvariation=True)
```

The results can again be displayed.

```python
logplot = LogPlotMatplotlib(
   soilprofile=sp,
   no_panels=1,
   fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SAND/CLAY': 'orange'})
logplot.add_trace(
    x=su_handtools_results['Su [kPa]'],
    z=su_handtools_results['Depth [m]'], name='Handtools', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_cu_results['Su peak q [kPa]'],
    z=su_cu_results['Depth [m]'], name='CU', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_uu_results['Su peak [kPa]'],
    z=su_uu_results['Depth [m]'], name='UU', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_dss_results['Failure shear stress [kPa]'],
    z=su_dss_results['Depth [m]'], name='DSS', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=cpt_su['Su [kPa]'],
    z=cpt_su['z [m]'], name='From CPT', panel_no=1, showlegend=True)
logplot.add_soilparameter_trace(parametername='Su [kPa]', panel_no=1, ls='--')
logplot.set_xaxis_title(title='$ S_u $ [kPa]', panel_no=1, size=15)
logplot.set_zaxis_title(title='$ z $ [m]')
logplot.set_xaxis_range(min_value=0, max_value=350, panel_no=1)
logplot.set_zaxis_range(min_depth=0, max_depth=50)
logplot.show()
```

You can close the plot after inspecting it.

When showing the table for the ``SoilProfile``, you can see that two columns are created; one with the value at the top of the layer (``Su from [kPa]``), the other with the value at the bottom of the layer (``Su to [kPa]``).

```python
sp
```

We will again remove these columns with selected values to demonstrate alternative methods of selection.

```python
sp.remove_parameter('Su [kPa]')
```

### Constant minimum value

``groundhog`` can also estimate conservative values by taking the minimum in each layer.

```python
sp.selection_soilparameter(
    parameter='Su [kPa]',
    depths=cpt_su['z [m]'],
    values=cpt_su['Su [kPa]'],
    rule='min')
```

We can visualise this selection:

```python
logplot = LogPlotMatplotlib(
   soilprofile=sp,
   no_panels=1,
   fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SAND/CLAY': 'orange'})
logplot.add_trace(
    x=su_handtools_results['Su [kPa]'],
    z=su_handtools_results['Depth [m]'], name='Handtools', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_cu_results['Su peak q [kPa]'],
    z=su_cu_results['Depth [m]'], name='CU', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_uu_results['Su peak [kPa]'],
    z=su_uu_results['Depth [m]'], name='UU', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_dss_results['Failure shear stress [kPa]'],
    z=su_dss_results['Depth [m]'], name='DSS', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=cpt_su['Su [kPa]'],
    z=cpt_su['z [m]'], name='From CPT', panel_no=1, showlegend=True)
logplot.add_soilparameter_trace(parametername='Su [kPa]', panel_no=1, ls='--')
logplot.set_xaxis_title(title='$ S_u $ [kPa]', panel_no=1, size=15)
logplot.set_zaxis_title(title='$ z $ [m]')
logplot.set_xaxis_range(min_value=0, max_value=350, panel_no=1)
logplot.set_zaxis_range(min_depth=0, max_depth=50)
logplot.show()
```

The parameters chosen in this way can be very sensitive to local minima. Close the plot after inspecting it.

The numerical values of the selection can also be shown.

```python
sp
```

Remove the column with selected minimum values before proceeding to manual $ S_u $ selection.

```python
sp.remove_parameter('Su [kPa]')
```

## Manual selection

The user can click on a plot with $ S_u $ data to create their own parameter profiles.

First generate the ``LogPlotMatplotlib``with the available $ S_u $ data on it.

Don't close this plot window as it needs to stay open for the parameter selection.

```python
logplot = LogPlotMatplotlib(
   soilprofile=sp,
   no_panels=1,
   fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SAND/CLAY': 'orange'})
logplot.add_trace(
    x=su_handtools_results['Su [kPa]'],
    z=su_handtools_results['Depth [m]'], name='Handtools', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_cu_results['Su peak q [kPa]'],
    z=su_cu_results['Depth [m]'], name='CU', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_uu_results['Su peak [kPa]'],
    z=su_uu_results['Depth [m]'], name='UU', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_dss_results['Failure shear stress [kPa]'],
    z=su_dss_results['Depth [m]'], name='DSS', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=cpt_su['Su [kPa]'],
    z=cpt_su['z [m]'], name='From CPT', panel_no=1, showlegend=True)

logplot.set_xaxis_title(title='$ S_u $ [kPa]', panel_no=1, size=15)
logplot.set_zaxis_title(title='$ z $ [m]')
logplot.set_xaxis_range(min_value=0, max_value=350, panel_no=1)
logplot.set_zaxis_range(min_depth=0, max_depth=80.9)
logplot.show()
```

You can select additional layers by clicking on the positions where you want to place additional layers. The ``select_layering`` method has a ``stop_threshold`` parameter which defines where you need to click to stop the layer selection process. If you click where $ S_u $ > 25kPa, additional layers will get selected. If you click below that value, the layer selection will stop.

Try it out by running the following command and clicking on the plot.

```python
logplot.select_layering(stop_threshold=25)
```

You can now also select the values of $ S_u $ manually in each layer. The ``select_linear`` method allows the selection of linear trends in each layer. Click through all the layers from top to bottom. Click first on the value at the top of the layer and then on the value at the bottom of the layer. If you click below the ``nan_tolerance``, NaN will be selected (e.g. for $ S_u $ in a sand layer).

Try it out by running the following command and clicking on the plot.

```python
logplot.select_linear(panel_no=1, parametername='Su', units='kPa', nan_tolerance=25)
```

You can now show the numerical values of the manually selected $ S_u $ trend.

```python
sp
```

To demonstrate the selection of constant values, we first remove the selected $ S_u $ profile from the previous step.

```python
sp.remove_parameter('Su [kPa]')
```

Then, we regenerate the plot in which we will select $ S_u $ (note that the additional layers do not disappear).

```python
logplot = LogPlotMatplotlib(
   soilprofile=sp,
   no_panels=1,
   fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SAND/CLAY': 'orange'})
logplot.add_trace(
    x=su_handtools_results['Su [kPa]'],
    z=su_handtools_results['Depth [m]'], name='Handtools', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_cu_results['Su peak q [kPa]'],
    z=su_cu_results['Depth [m]'], name='CU', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_uu_results['Su peak [kPa]'],
    z=su_uu_results['Depth [m]'], name='UU', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_dss_results['Failure shear stress [kPa]'],
    z=su_dss_results['Depth [m]'], name='DSS', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=cpt_su['Su [kPa]'],
    z=cpt_su['z [m]'], name='From CPT', panel_no=1, showlegend=True)

logplot.set_xaxis_title(title='$ S_u $ [kPa]', panel_no=1, size=15)
logplot.set_zaxis_title(title='$ z $ [m]')
logplot.set_xaxis_range(min_value=0, max_value=350, panel_no=1)
logplot.set_zaxis_range(min_depth=0, max_depth=80.9)
logplot.show()
```

The ``select_constant`` method works in the same way as the ``select_linear`` method but we only need to click once in each layer.

```python
logplot.select_constant(panel_no=1, parametername='Su', units='kPa', nan_tolerance=25)
```

```python
sp
```

## Visualization of selected parameters

Finally, we can create summary plot of the selected geotechnical parameters.

```python
logplot = LogPlotMatplotlib(
   soilprofile=sp,
   no_panels=1,
   fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SAND/CLAY': 'orange'})
logplot.add_trace(
    x=su_handtools_results['Su [kPa]'],
    z=su_handtools_results['Depth [m]'], name='Handtools', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_cu_results['Su peak q [kPa]'],
    z=su_cu_results['Depth [m]'], name='CU', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_uu_results['Su peak [kPa]'],
    z=su_uu_results['Depth [m]'], name='UU', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=su_dss_results['Failure shear stress [kPa]'],
    z=su_dss_results['Depth [m]'], name='DSS', panel_no=1, line=False, showlegend=True)
logplot.add_trace(
    x=cpt_su['Su [kPa]'],
    z=cpt_su['z [m]'], name='From CPT', panel_no=1, showlegend=True)
logplot.add_soilparameter_trace(parametername='Su [kPa]', panel_no=1, ls='--')
logplot.set_xaxis_title(title='$ S_u $ [kPa]', panel_no=1, size=15)
logplot.set_zaxis_title(title='$ z $ [m]')
logplot.set_xaxis_range(min_value=0, max_value=350, panel_no=1)
logplot.set_zaxis_range(min_depth=0, max_depth=50)
logplot.show()
```

## Export of selection

```python
sp.to_excel('Data/selected_su.xlsx', index=False, engine='openpyxl')
```

```text
: 
```
