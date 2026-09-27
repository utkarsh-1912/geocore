---
title: gINT data import in Python for Linux and Mac
slug: groundhog/tutorials/tutorial-gint-data-import-in-python-for-mac-and-linux
section: Groundhog Guides
description: gINT is a widely used geodatabase.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/notebooks/Tutorial%20-%20gINT%20data%20import%20in%20Python%20for%20Mac%20and%20Linux.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted.'
notebook: notebooks/Tutorial - gINT data import in Python for Mac and Linux.ipynb
---

gINT is a widely used geodatabase. While the application is widely used in the geotechnical community, the file-based data storage does not facilite use of data across projects and data is often locked in a database file and not used further when the project finishes.

Combining data from different projects can lead to improved insights and having past experience readily available can help geotechnical engineers make better decision.

To unlock gINT data for engineers, importing the data in Python can be very useful. Once the data is available in Python, it allows further processing or calculations.

gINT stores geotechnical data in Microsoft Access databases. The Microsoft Windows drivers for reading Access databases do not work on Linux and Mac but a workaround is possible using [MDBTools](https://github.com/mdbtools/mdbtools) and the [```pandas_access```](https://github.com/jbn/pandas_access) Python library.

## Installation of ```mdbtools```

### Linux

Install ```mdbtools``` on Linux by running the following command in a terminal window:

```sh
$ apt install mdbtools
```

### Mac

Install ```mdbtools``` on Mac using [Homebrew](http://brew.sh/). Run the following command in a terminal window:

```sh
$ brew install mdbtools
```

## Installation of ```pandas_access```

The ```pandas_access``` library can be installed using pip:

```sh
$ pip install pandas_access
```

Once installed, you can import the library in the notebook (note that you may need to restart Jupyter notebooks for the changes to take effect).

```python
import pandas_access as mdb
```

## Reading database tables

A gINT project file (```.gpj``` extension) contains a number of tables with data. The names of these tables can be read using the ```.list_tables``` function. The path to the gINT file needs to be supplied as an argument.

An example file from a highway repair operation in the US is used as an example.

```python
db_file = "Data/9724000.gpj"
```

```python
for tbl in mdb.list_tables(db_file):
    print(tbl)
```

```text
BOREHOLE
LOCATION
CPT
CPT
PLOT
SCALE
OVERRIDES
CPT
REPORT
SCALE
OVERRIDES
CPT-DATA
DRILLING
OPERATIONS
INTERPRETED
WATER
TABLE
ELEVATION
LAB
RESULT
UNITS
LITHOLOGY
LITHOLOGY
SOIL
LOG
OTHER
TESTS
POINT
PROJECT
REMARKS
... (output truncated)
```

Not all tables contain data. We can select the ones containing data using the ```.read_schema``` function. The database schema is returned as a dictionary:

```python
mdb.read_schema(db_file)
```

```text
{'CPT': {'GintRecID': 'Long Integer',
  'PointID': 'Text (510) NOT NULL',
  'Datafile': 'Text (510)',
  'Probe_ID': 'Text (510)',
  'Software': 'Text (510)',
  'Int_Stat_H20_Level': 'Single'},
 'LITHOLOGY': {'GintRecID': 'Long Integer',
  'PointID': 'Text (510) NOT NULL',
  'Depth': 'Double NOT NULL',
  'Bottom': 'Double'},
 'LOG': {'GintRecID': 'Long Integer NOT NULL',
  'PointID': 'Text (510) NOT NULL',
  'Site_Group': 'Text (510)',
  'Bridge_Number_or_Desc': 'Text (510)',
  'Structure_Type': 'Text (510)',
  'Sub_Group': 'Text (510)',
  'Crew_Chief': 'Text (510)'},
 'POINT': {'GintRecID': 'Long Integer',
  'PointID': 'Text (510) NOT NULL',
  'HoleDepth': 'Double NOT NULL',
  'Driller': 'Text (510)',
  'Logger': 'Text (510)',
  'Plunge': 'Double',
  'North': 'Double',
  'East': 'Double'},
 'PROJECT': {'GintRecID': 'Long Integer',
  'UPN': 'Text (510)',
  'Datum': 'Text (510)'},
 'REMARKS': {'GintRecID': 'Long Integer',
  'PointID': 'Text (510) NOT NULL',
... (output truncated)
```

We can store a list with the tables names containing data:

```python
data_tables = mdb.read_schema(db_file).keys()
data_tables
```

```text
dict_keys(['CPT', 'LITHOLOGY', 'LOG', 'POINT', 'PROJECT', 'REMARKS', 'SAMPLE', 'CPT_REMARKS'])
```

We can see that several table names are returned. Some (e.g. ```PROJECT```) speak for themselves, whereas others required additional inspection to know the data contained in them.

## Reading table data

Reading the data from the tables is straightforward using the ```.read_table``` function. This function returns a Pandas dataframe which can be used for further filtering of the data. The path to the database file and the name of the table need to be supplied.

```python
df = mdb.read_table(db_file, "PROJECT")
df
```

```text
   GintRecID             Project Name      UPN   Project Number Input Units  \
0          1  Slide Repair-N of Terry  9724000  STPS 253-1(24)2           E   

  Output Units  Datum  Depth Log Page UCS Soil Units UCS Rock Units  \
0            E  NAD83             NaN            psf            psi   

  Coordinate System  
0       MT S.P. (E)  
```

We can thus loop over all the tables containing data and print the contents:

```python
for tbl in data_tables:
    _df = mdb.read_table(db_file, tbl)
    print('-------%s-------' % tbl)
    print(_df.head())
```

```text
-------CPT-------
Empty DataFrame
Columns: [GintRecID, PointID, Datafile, Probe_ID, Software, Int_Stat_H20_Level, ASM_DNSTY]
Index: []
-------LITHOLOGY-------
   GintRecID PointID  Depth  Bottom  Graphic
0         10       1   0.00    0.75  ASPHALT
1         11       1   0.75    4.30       GP
2         12       1   4.30    5.80     FILL
3         13       1   5.80    7.00     FILL
4         14       1   7.00   15.00     FILL
-------LOG-------
Empty DataFrame
Columns: [GintRecID, PointID, Site_Group, Bridge_Number_or_Desc, Structure_Type, Sub_Group, Crew_Chief, Date_End]
Index: []
-------POINT-------
   GintRecID PointID  HoleDepth Drill Rig Driller          Logger  \
0          1       1       26.5  CME 1050  Duncan  Jaynes/Kettner   
1          2       2       26.5  CME 1050  Duncan  Jaynes/Kettner   
2          3       6       36.5  CME 1050  Duncan  Jaynes/Kettner   
3          4       7       21.5  CME 1050  Duncan  Jaynes/Kettner   
4          5       8       31.5  CME 1050  Duncan         Kettner   

  Boring Diameter Drilling Fluid Hammer Type       Date Started  \
0              8"           None        Auto  08/25/20 00:00:00   
1              8"           None        Auto  08/25/20 00:00:00   
2              8"           None        Auto  08/25/20 00:00:00   
3              8"           None        Auto  08/25/20 00:00:00   
4              8"           None        Auto  08/26/20 00:00:00   

... (output truncated)
```

## Exporting gINT data to Excel 

Once gINT data is available in dataframes, it can easily be exported to Excel as a workbook with multiple sheets. Although Excel is not recommended for data processing tasks (Python is much better at this), exporting can be useful for visually inspecting the data.

```python
import pandas as pd
writer = pd.ExcelWriter('Output/9724000.xlsx', engine='xlsxwriter')
# Write each dataframe to a different worksheet.
for tbl in data_tables:
    _df = mdb.read_table(db_file, tbl)
    _df.to_excel(writer, sheet_name=tbl, index=False)
# Close the Pandas Excel writer and output the Excel file.
writer.save()
```

## Case study: SPT data for a selected location

The use of gINT data reading is illustrated for reporting SPT blowcount for a given location.

### Retrieval of test locations

The locations of tests are given in the ```POINT``` table:

```python
point_df = mdb.read_table(db_file, 'POINT')
point_df
```

```text
   GintRecID PointID  HoleDepth Drill Rig Driller          Logger  \
0          1       1       26.5  CME 1050  Duncan  Jaynes/Kettner   
1          2       2       26.5  CME 1050  Duncan  Jaynes/Kettner   
2          3       6       36.5  CME 1050  Duncan  Jaynes/Kettner   
3          4       7       21.5  CME 1050  Duncan  Jaynes/Kettner   
4          5       8       31.5  CME 1050  Duncan         Kettner   
5          6       9       16.5  CME 1050  Duncan         Kettner   
6          7      10       41.5  CME 1050  Duncan         Kettner   

  Boring Diameter Drilling Fluid Hammer Type       Date Started  \
0              8"           None        Auto  08/25/20 00:00:00   
1              8"           None        Auto  08/25/20 00:00:00   
2              8"           None        Auto  08/25/20 00:00:00   
3              8"           None        Auto  08/25/20 00:00:00   
4              8"           None        Auto  08/26/20 00:00:00   
5              8"           None        Auto  08/26/20 00:00:00   
6              8"           None        Auto  08/26/20 00:00:00   

       Date Finished  Plunge  Borehole Azimuth Abandonment Method  \
0  08/25/20 00:00:00   -90.0               NaN           Cuttings   
1  08/25/20 00:00:00   -90.0               NaN           Cuttings   
2  08/25/20 00:00:00   -90.0               NaN           Cuttings   
3  08/25/20 00:00:00   -90.0               NaN           Cuttings   
4  08/26/20 00:00:00   -90.0               NaN           Cuttings   
5  08/26/20 00:00:00   -90.0               NaN           Cuttings   
6  08/26/20 00:00:00   -90.0               NaN           Cuttings   

   General Notes  Depth Log Page     North       East  Elevation  
0            NaN              30  963827.7  3019717.2    2326.12  
1            NaN              30  963960.7  3019749.4    2330.77  
... (output truncated)
```

As an example, the SPT blowcount will be reported for PointID 6, with a depth of 36.5ft.

### Retrieval of SPT data

The SPT data is included in the ```SAMPLE``` table. We can import all the data first:

```python
sample_df = mdb.read_table(db_file, 'SAMPLE')
sample_df.head()
```

```text
   GintRecID PointID  Depth  Length  Type  Sample Recovery SPT 1 SPT 2 SPT 3  \
0          1      10    2.0     1.0  GRAB              NaN   NaN   NaN   NaN   
1          2      10    5.0     1.5    SS             67.0     1     3     5   
2          3      10   10.0     1.5    SS             40.0     2     3     2   
3          4      10   15.0     1.5    SS             67.0    WH     1     2   
4          5      10   20.0     1.5    SS             53.0     2     3     3   

   Refusal Length  Sum of 4 inch Core Run  
0             NaN                     NaN  
1             NaN                     NaN  
2             NaN                     NaN  
3             NaN                     NaN  
4             NaN                     NaN  
```

A common problem with data imported from external files is that the data does not have the correct data type. We can check this with the ```.dtypes``` function in Pandas.

```python
sample_df.dtypes
```

```text
GintRecID                   int64
PointID                    object
Depth                     float64
Length                    float64
Type                       object
Sample Recovery           float64
SPT 1                      object
SPT 2                      object
SPT 3                      object
Refusal Length            float64
Sum of 4 inch Core Run    float64
dtype: object
```

We can see that SPT numbers are indeed not numeric (```object``` data type). We can convert these columns as follows:

```python
for key in ['SPT 1', 'SPT 2', 'SPT 3']:
    sample_df[key] = pd.to_numeric(sample_df[key], errors='coerce')
```

```python
sample_df.head()
```

```text
   GintRecID PointID  Depth  Length  Type  Sample Recovery  SPT 1  SPT 2  \
0          1      10    2.0     1.0  GRAB              NaN    NaN    NaN   
1          2      10    5.0     1.5    SS             67.0    1.0    3.0   
2          3      10   10.0     1.5    SS             40.0    2.0    3.0   
3          4      10   15.0     1.5    SS             67.0    NaN    1.0   
4          5      10   20.0     1.5    SS             53.0    2.0    3.0   

   SPT 3  Refusal Length  Sum of 4 inch Core Run  
0    NaN             NaN                     NaN  
1    5.0             NaN                     NaN  
2    2.0             NaN                     NaN  
3    2.0             NaN                     NaN  
4    3.0             NaN                     NaN  
```

We can see that three SPT numbers are available. ```SPT 1``` is the blowcount for the seating drive, ```SPT 2``` and ```SPT 3``` can be added to obtain the SPT $ N $ number.

```python
sample_df["SPT N"] = sample_df["SPT 2"] + sample_df["SPT 3"]
```

The SPT data for PointID 6 can be filtered using conventional Pandas syntax. Since the ```PointID``` field is an ```object```, we need to specify the PointID for filtering as a string.

```python
sample_6_df = sample_df[sample_df['PointID'] == '6']
sample_6_df
```

```text
    GintRecID PointID  Depth  Length  Type  Sample Recovery  SPT 1  SPT 2  \
18         19       6    1.4     1.6  GRAB              NaN    NaN    NaN   
19         20       6    5.0     1.5    SS             73.0    2.0    2.0   
20         21       6   10.0     1.5    SS             30.0    3.0    3.0   
21         22       6   15.0     1.5    SS             35.0    2.0    2.0   
22         23       6   20.0     1.5    SS             35.0    2.0    3.0   
23         24       6   25.0     1.5    SS             47.0    2.0    2.0   
24         25       6   30.0     1.5    SS             67.0    5.0    9.0   
25         26       6   35.0     1.5    SS            100.0   12.0   24.0   

    SPT 3  Refusal Length  Sum of 4 inch Core Run  SPT N  
18    NaN             NaN                     NaN    NaN  
19    5.0             NaN                     NaN    7.0  
20    3.0             NaN                     NaN    6.0  
21    2.0             NaN                     NaN    4.0  
22    2.0             NaN                     NaN    5.0  
23    2.0             NaN                     NaN    4.0  
24   14.0             NaN                     NaN   23.0  
25   29.0             NaN                     NaN   53.0  
```

These numbers can be used for further processing using the ```SPTProcessing``` class in [```groundhog```](https://github.com/snakesonabrain/groundhog).

## Closing remarks: Using gINT library files for data interpretation

This article shows how gINT project files can be read using ```mdbtools``` and ```pandas_access```. The Microsoft Access database files are readily imported in Python which can greatly facilitate further processing.

Certain gINT project files are also connected to a gINT library file (```.glb``` extension). These files contain e.g. possible choices for soil types, hammer types, ... In the example above, such a file would contain a table which says that ```GRAB``` stands for a grab sample and ```SS``` for a split-spoon sample. The methods described above can just as easily be used to import these ```.glb``` files.
