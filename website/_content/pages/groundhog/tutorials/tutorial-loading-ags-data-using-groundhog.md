---
title: Tutorial - Loading AGS data using ```groundhog```
slug: groundhog/tutorials/tutorial-loading-ags-data-using-groundhog
section: Groundhog Guides
description: This tutorial outlines how an AGS 4.0 file can be converted to Python-compatible data structures (Pandas Dataframes) using
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/notebooks/Tutorial%20-%20Loading%20ags%20data%20using%20groundhog.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted, with a short note on how to run this in GeoCore prepended.'
notebook: notebooks/Tutorial - Loading ags data using groundhog.ipynb
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, run the same calculation through a [calculation form](/docs/geocore/using/modules) or by asking **GeoAI**, which calls the same groundhog function through its validated Tool Registry. This notebook is kept for anyone who wants to call groundhog directly from their own Python code instead.

This tutorial outlines how an AGS 4.0 file can be converted to Python-compatible data structures (Pandas Dataframes) using ```groundhog```.

A file with geotechnical data from the Borssele I offshore wind farm is used to demonstrate the principles. This file is used under a Creative Commons 4.0 license.

## 1. Importing libraries

We can import the ```AGSConverter``` class. This class will convert the AGS data to Pandas dataframes which can be used for further data processing.

```python
from groundhog.general.agsconversion import AGSConverter
```

## 2. Reading data

We can read data from an AGS file by creating an ```AGSConverter``` object. We will use the file ```N6016_BH-WFS1-2A_AGS4_150703.AGS```. ```groundhog``` performs some initial processing on the file. The AGS groupnames are extracted and any double-quotes which would hinder import (e.g. in latitude or longitude values) are removed.

```python
agsdata = AGSConverter(path='Data/N6016_BH-WFS1-2A_AGS4_150703.AGS')
```

We can check which groupnames are available by printing the ```groupnames``` property of the ```AGSConverter``` object.

```python
agsdata.groupnames
```

```text
['PROJ',
 'UNIT',
 'TYPE',
 'ABBR',
 'User-defined data group',
 'DICT',
 'LOCA',
 'GEOL',
 'DETL',
 'SAMP',
 'CONG',
 'GCHM',
 'GRAG',
 'GRAT',
 'LDEN',
 'LLPL',
 'LNMC',
 'LPDN',
 'LPEN',
 'TREG',
 'TRIG',
 'TRIT']
```

The groupnames are four character abbreviations which defines which data the group contains. We can convert these groupnames to a more verbose format using the ```GROUP_NAMES``` dictionary.

```python
from groundhog.general.agsconversion import GROUP_NAMES
```

Currently, only the most common group names for geotechnical tests in the AGS 4.0 standard are encoded. Different group names can easily be added in the future.

```python
GROUP_NAMES
```

```text
{'PROJ': 'Project Information',
 'ABBR': 'Abbreviation Definitions',
 'DICT': 'User Defined Groups and Headings',
 'FILE': 'Associated Files',
 'TRAN': 'Data File Transmission Information / Data Status',
 'TYPE': 'Definition of Data Types',
 'UNIT': 'Definition of Units',
 'CLSS': 'Classification tests',
 'CONG': 'Consolidation Tests - General',
 'CONS': 'Consolidation Tests - Data',
 'CORE': 'Coring Information',
 'GEOL': 'Field Geological Descriptions',
 'GRAG': 'Particle Size Distribution Analysis - General',
 'GRAT': 'Particle Size Distribution Analysis - Data',
 'SCPG': 'Static Cone Penetration Tests - General',
 'SCPT': 'Static Cone Penetration Tests - Data',
 'SCPP': 'Static Cone Penetration Tests - Derived Parameters',
 'LOCA': 'Location Details',
 'DETL': 'Stratum Detail Descriptions',
 'SAMP': 'Sample Information',
 'GCHM': 'Geotechnical Chemistry Testing',
 'LDEN': 'Density tests',
 'LLPL': 'Liquid and Plastic Limit Tests',
 'LNMC': 'Water/Moisture Content Tests',
 'LPDN': 'Particle Density Tests',
 'LPEN': 'Laboratory Hand Penetrometer Tests',
 'TREG': 'Triaxial Tests - Effective Stress - General',
 'TRET': 'Triaxial Tests - Effective Stress - Data',
 'TRIG': 'Triaxial Tests - Total Stress - General',
 'TRIT': 'Triaxial Tests - Total Stress - Data',
... (output truncated)
```

## 3. Converting AGS data to Pandas dataframes

### 3.1. Converting all groups

Converting the AGS data to Pandas dataframes is a matter of running the ```create_dataframes``` method. This creates a dictionary of dataframes for all group names. If groups cannot be converted, a warning will be raised but the code will continue. Dataframe creation for this group is simply skipped.

```python
agsdata.create_dataframes()
```

```text
/Users/profound/opt/anaconda3/lib/python3.7/site-packages/groundhog-0.2.0-py3.7.egg/groundhog/general/agsconversion.py:1025: UserWarning: Group User-defined data group could not be converted - index 0 is out of bounds for axis 0 with size 0
  warnings.warn("Group %s could not be converted - %s" % (_groupname, str(err)))
```

We now have a dictionary of dataframes in the ```data``` attribute. The keys of this dictionary are the groupnames.

```python
agsdata.data.keys()
```

```text
dict_keys(['PROJ', 'UNIT', 'TYPE', 'ABBR', 'DICT', 'LOCA', 'GEOL', 'DETL', 'SAMP', 'CONG', 'GCHM', 'GRAG', 'GRAT', 'LDEN', 'LLPL', 'LNMC', 'LPDN', 'LPEN', 'TREG', 'TRIG', 'TRIT'])
```

We can check the data for the density tests (we only print the first five rows using the ```head()``` method).

```python
agsdata.data['LDEN'].head()
```

```text
      LOCA_ID  SAMP_TOP [m] SAMP_REF  ... LDEN_BDEN [kN/m3] LDEN_DDEN [kN/m3] LDEN_LAB
0  BH-WFS1-2A           1.0       W2  ...              19.4              15.7      NaN
1  BH-WFS1-2A           1.0       W2  ...               NaN               NaN      NaN
2  BH-WFS1-2A           2.0       W3  ...              19.3              15.4      NaN
3  BH-WFS1-2A           2.0       W3  ...              19.2              15.5      NaN
4  BH-WFS1-2A           3.0       W4  ...              20.3              16.4      NaN

[5 rows x 11 columns]
```

The resulting dataframe has AGS codes as column headers, with the accompanying units. These column keys are not verbose, but the ```create_dataframes``` method can fix this as explained in the next section.

### 3.2. Converting selected groups

#### 3.2.1. Using AGS column headers

We often don't need all groups in the AGS file. We can only import selected groups by specifying a list of groupnames we want to convert in the keyword argument ```selectedgroups```.

As an example, we will convert only the sample information (```SAMP``` group). The resulting dictionary only contains one element.

```python
agsdata.create_dataframes(selectedgroups=['SAMP',])
agsdata.data.keys()
```

```text
dict_keys(['SAMP'])
```

We can visualise the content of the resulting dataframe. This dataframe has the AGS codes as the column headers.

```python
agsdata.data['SAMP'].head()
```

```text
      LOCA_ID  SAMP_TOP [m] SAMP_REF SAMP_TYPE  ... SAMP_WHY  SAMP_DESD [yyyy-mm-dd] SAMP_LOG    SAMP_COND
0  BH-WFS1-2A           0.0       W1         W  ...      NaN              2015-04-10      TAD  Undisturbed
1  BH-WFS1-2A           1.0       W2         W  ...      NaN              2015-04-10      TAD  Undisturbed
2  BH-WFS1-2A           2.0       W3         W  ...      NaN              2015-04-10      TAD  Undisturbed
3  BH-WFS1-2A           3.0       W4         W  ...      NaN              2015-04-10      TAD  Undisturbed
4  BH-WFS1-2A           4.0       W5         W  ...      NaN              2015-04-10      TAD  Undisturbed

[5 rows x 16 columns]
```

#### 3.2.2. Long verbose column headers

We can automatically convert AGS column headers by setting the ```verbose_keys``` boolean to True. The ```AGSConverter``` class will make use of the dictionary ```AGS_TABLES``` to perform the conversion. Currently, not all AGS groups are encoded in ```groundhog``` but this is expanded with each release.

```python
agsdata.create_dataframes(selectedgroups=['SAMP',], verbose_keys=True)
```

The resulting dataframe now has readable column headers. The downside for further coding is that these headers are rather long.

```python
agsdata.data['SAMP'].head()
```

```text
  Location identifier  ...  Condition and representativeness of sample
0          BH-WFS1-2A  ...                                 Undisturbed
1          BH-WFS1-2A  ...                                 Undisturbed
2          BH-WFS1-2A  ...                                 Undisturbed
3          BH-WFS1-2A  ...                                 Undisturbed
4          BH-WFS1-2A  ...                                 Undisturbed

[5 rows x 16 columns]
```

#### 3.2.3. Short verbose headers

Column header conversion using short verbose names is also possible using the ```use_shorthands``` boolean. This will still provide some verbosity to the column headers while keeping the columns short. The dictionary ```AGS_TABLES_SHORTHANDS``` contains the conversion keys.

```python
agsdata.create_dataframes(selectedgroups=['SAMP',], verbose_keys=True, use_shorthands=True)
```

The resulting dataframe now has shorter readable column headers.

```python
agsdata.data['SAMP'].head()
```

```text
  Location identifier  Depth from [m]  ... Logged by Condition and representativeness of sample
0          BH-WFS1-2A             0.0  ...       TAD                                Undisturbed
1          BH-WFS1-2A             1.0  ...       TAD                                Undisturbed
2          BH-WFS1-2A             2.0  ...       TAD                                Undisturbed
3          BH-WFS1-2A             3.0  ...       TAD                                Undisturbed
4          BH-WFS1-2A             4.0  ...       TAD                                Undisturbed

[5 rows x 16 columns]
```
