---
title: Tutorial - PCPT data reading with Groundhog
slug: groundhog/tutorials/tutorial-pcpt-data-reading-with-groundhog
section: Groundhog Guides
description: A PCPT processing tool has been created within the
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/notebooks/Tutorial%20-%20PCPT%20data%20reading%20with%20Groundhog.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted.'
notebook: notebooks/Tutorial - PCPT data reading with Groundhog.ipynb
---

A PCPT processing tool has been created within the ```groundhog``` package. This tool is made available to allow rapid import of PCPT data, basic processing and checking of the sensitivity to processing parameters. Moreover, correlations between PCPT properties and other soil mechanical parameters an easily be applied.

In this tutorial, the import of PCPT data is covered for different file formats.

We need to import the ```PCPTProcessing``` class from ```groundhog```.

```python
from groundhog.siteinvestigation.insitutests.pcpt_processing import PCPTProcessing
```

```groundhog``` uses Plotly as plotting backend, we will load Plotly in notebook mode:

```python
from plotly.offline import init_notebook_mode
init_notebook_mode()
```

## Excel import

The first way to load data is from a Pandas dataframe using the ```load_excel``` method. A dataframe is be created from Excel data and added as the ```.data``` attribute of the PCPTProcessing object. Note that $ q_c $, $ f_s $ and $ u_2 $ need to have the dimension MPa. If they don't multipliers can be specified to convert them to these dimensions.

```python
pcpt_excel = PCPTProcessing(title="Example PCPT Excel")
```

```python
pcpt_excel.load_excel(path="Data/excel_example.xlsx",
    u2_key="u [kPa]", u2_multiplier=0.001)
pcpt_excel.data.tail()
```

The raw PCPT data can be visualized with the ```plot_raw_pcpt``` method.

```python
pcpt_excel.plot_raw_pcpt()
```

## Reading .asc data

The class also has the function ```load_asc``` for loading .asc data.

```python
pcpt_asc = PCPTProcessing(title="ASC PCPT")
pcpt_asc.load_asc(path="Data/acs_example.asc",
    column_widths=[5, 9, 10, 11, 11, 11, 11],
    z_key="Depth [m]", qc_key="Cone [MPa]", fs_key="Friction [MPa]", u2_key="Pore 2 [MPa]")
pcpt_asc.data.head()
```

```python
pcpt_asc.plot_raw_pcpt(u2_range=(-0.2, 2), u2_tick=0.2)
```

## Reading AGS data

AGS is a common data transfer for geotechnical data. Rapidly importing PCPT data from this format is useful to allow further processing.

The method  ```load_ags``` is available from the ```PCPTProcessing``` class in ```groundhog```. The CPT data is available in the ```SCPT``` group and the following keys are used in AGS 4.0:

   - $ q_c $: ```SCPT_RES [MN/m2]```
   - $ f_s $: ```SCPT_FRES [kN/m2]```
   - $ u_2 $: ```SCPT_PWP2 [kN/m2]```
   - $ z $: ```SCPT_DPTH [m]```
   
As $ f_s $ and $ u_2 $ are given in kPa, a multiplier of 0.001 needs to be specified to convert them to MPa.

For general processing of AGS files, the ```AGSConverter``` converter is available.

```python
pcpt_ags = PCPTProcessing(title="AGS example")
pcpt_ags.load_ags(
    path="Data/N6016_BH_WFS1-2A_AGS4_150909.ags",
    z_key="SCPT_DPTH [m]", qc_key="SCPT_RES [MN/m2]", fs_key="SCPT_FRES [kN/m2]", u2_key="SCPT_PWP2 [kN/m2]",
    fs_multiplier=0.001, u2_multiplier=0.001,
    push_key="SCPG_TESN")
```

We can plot the raw PCPT data.

```python
pcpt_ags.plot_raw_pcpt(u2_range=(-0.5, 2), u2_tick=0.5)
```

A full tutorial notebook on the use of the ```AGSConverter``` class is also available in the notebooks folder of the ```groundhog``` project.

## Reading from Databank Ondergrond Vlaanderen

Databank Ondergrond Vlaanderen contains all CPT data collected by the Flemish government. The ```pydov``` package allows direct access to this CPT data. The ```pydov``` package can be installed as follows:

```pip install pydov```

To import CPT data, all that is required is the name of the CPT. We can import CPT: GEO-13/147-S1. The name of the CPT can easily be retrieved from dov.vlaanderen.be.

```python
dov_cpt = PCPTProcessing(title="DOV CPT")
dov_cpt.load_pydov("GEO-13/147-S1")
dov_cpt.plot_raw_pcpt()
```

## Combining PCPT data

We can combine data from multiple sources (e.g. seabed PCPT + downhole PCPT) into one ```PCPTProcessing``` object. We do this using the ```combine_pcpt``` method. This method takes another ```PCPTProcessing``` object and merges its data into the ```data``` attribute of the original ```PCPTProcessing``` object. The user can select what to do in the areas where overlap exists using the ```keep``` keyword argument.

We can demonstrate this with an example where we load the seabed PCPT corresponding to the downhole PCPT loaded above.

```python
from groundhog.general.agsconversion import AGSConverter
converter_seabed = AGSConverter(path="Data/N6016_BH_WFS1-2_AGS4_150909.ags")
converter_seabed.create_dataframes(selectedgroups=['SCPT'], verbose_keys=True, use_shorthands=True)
converter_seabed.data['SCPT'].head()
```

Creation of a ```PCPTProcessing``` object happens as before.

```python
pcpt_ags_seabed = PCPTProcessing(title="AGS CPT")
pcpt_ags_seabed.load_pandas(
    df=converter_seabed.data['SCPT'],
    z_key="Depth [m]",
    qc_key="qc [MN/m2]",
    fs_key="fs [kN/m2]",
    u2_key="u2 [kN/m2]",
    push_key="Test reference or push number",
    fs_multiplier=0.001, u2_multiplier=0.001)
pcpt_ags.data.head(15)
```

We can plot the raw PCPT data for the seabed CPT. This data provides coverage in the shallow region where no data is availabl from the downhole PCPT, but it has a lower final penetration.

```python
pcpt_ags_seabed.plot_raw_pcpt(u2_range=(-0.5, 2), u2_tick=0.5)
```

Combining the PCPT data is simply done by apply the ```combine_pcpt``` method on one of the ```PCPTProcessing``` objects. In the region where there is overlap, we need to decide which data to keep. The default behaviour is to keep the data from the ```PCPTProcessing``` object on which the ```combine_pcpt``` method is applied (```keep='first'```).

```python
pcpt_ags_seabed.combine_pcpt(obj=pcpt_ags, keep='first')
```

We can plot the combined profile which now gives a more global picture of the soil profile.

```python
pcpt_ags_seabed.plot_raw_pcpt(u2_range=(-1, 5), u2_tick=0.5)
```

## Loading a00 data

The ```PCPTProcessing``` class has a method ```load_a00``` for loading .a00 files, another common PCPT data transfer format.

```python
a00_pcpt = PCPTProcessing(title='A00 example')
a00_pcpt.load_a00(
    path="Data/a00 example.A00",
    column_widths=[8, 10, 11, 11, 11, 11, 11],
    z_key='Depth [m]', qc_key='Cone [MPa]', fs_key='Friction [MPa]', u2_key='Pore 2 [MPa]')
```

```python
a00_pcpt.plot_raw_pcpt(u2_range=(-0.5, 1), u2_tick=0.25)
```

## Other file formats

```groundhog``` is under constant development. Participate in the development by developping a method for importing other formats or create a feature request and provide example files to the package authors.
