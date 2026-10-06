---
title: gINT data import in Python for Windows
slug: groundhog/tutorials/tutorial-gint-data-import-in-python-for-windows
section: Groundhog Guides
description: gINT is a widely used geodatabase.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/notebooks/Tutorial%20-%20gINT%20data%20import%20in%20Python%20for%20Windows.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted, with a short note on how to run this in GeoCore prepended.'
notebook: notebooks/Tutorial - gINT data import in Python for Windows.ipynb
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, run the same calculation through a [calculation form](/docs/geocore/using/modules) or by asking **GeoAI**, which calls the same groundhog function through its validated Tool Registry. This notebook is kept for anyone who wants to call groundhog directly from their own Python code instead.

gINT is a widely used geodatabase. While the application is widely used in the geotechnical community, the file-based data storage does not facilite use of data across projects and data is often locked in a database file and not used further when the project finishes.

Combining data from different projects can lead to improved insights and having past experience readily available can help geotechnical engineers make better decision.

To unlock gINT data for engineers, importing the data in Python can be very useful. Once the data is available in Python, it allows further processing or calculations.

## Installation of Access Drivers

gINT stores geotechnical data in Microsoft Access databases. To make a connection with Access files, the Microsoft Windows Access drivers needs to be installed. Download and install them from here: https://www.microsoft.com/en-us/download/details.aspx?id=13255.

## Installation of pyodbc

We also need the package ```pyodbc``` to make connection to databases, which can be installed with pip:

```sh
> pip install pyodbc
```

```python
import os
import pandas as pd
```

## Reading database tables

A gINT project file (```.gpj``` extension) contains a number of tables with data. The names of these tables can be read using the ```.list_tables``` function. The path to the gINT file needs to be supplied as an argument.

An example file from a highway repair operation in the US is used as an example.

We first need to make a connection to the database file. We can do this by creating a connection string which specifies the driver to use and the path to the database file. Note that absolute paths need to be provided on Windows machines. To avoid having the write the full path, we can make use of the ```os``` library and get the current working directory (```os.getcwd()```). We can then add the Data subdirectory and the filename to the path using the ```os.path.join``` method. This path is then filled in

```python
import pyodbc
path = os.path.join(os.getcwd(), 'Data', '9724000.gpj')

connStr = (
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    r"DBQ=%s;" % path
    )
cnxn = pyodbc.connect(connStr)
```

```python
path
```

```cnxn``` now contains a connection to the database which we can use to retrieve data. For example, we can loop over all tables in the database and print the name of the tables:

```python
cursor = cnxn.cursor()
for row in cursor.tables():
    print(row.table_name)
```

We can see that several table names are returned. Some (e.g. ```PROJECT```) speak for themselves, whereas others required additional inspection to know the data contained in them.

## Reading table data

Reading the data from the tables is straightforward using the ```.read_sql``` function from Pandas. This function returns a Pandas dataframe which can be used for further filtering of the data. A valid SQL statement needs to be supplied.

SQL (Structured Query Language) can be used to interrogate several types of databases and learning the language requires some training. However, we can retrieve most data we need with the following simple query:

```sql
Select * from [<TABLENAME>]
```

This statement retrieves all data from a specific table. We can use this statement to retrieve all data and use Pandas for further filtering.

```python
sql = "Select * From [PROJECT]"
project_data = pd.read_sql(sql,cnxn)
project_data
```

We can thus loop over all the tables containing data and print the contents. We need to be careful since the tables starting with MSys have restricted access. This is not an issue as they do not contain relevant project data, so we can just skip them.

```python
cursor = cnxn.cursor()
for row in cursor.tables():
    if "MSys" in row.table_name:
        pass
    else:
        _df = pd.read_sql("Select * From [%s]" % row.table_name, cnxn)
        print('-------%s-------' % row.table_name)
        print(_df.head())
```

## Exporting gINT data to Excel 

Once gINT data is available in dataframes, it can easily be exported to Excel as a workbook with multiple sheets. Although Excel is not recommended for data processing tasks (Python is much better at this), exporting can be useful for visually inspecting the data.

```python
import pandas as pd
writer = pd.ExcelWriter('Output/9724000.xlsx', engine='xlsxwriter')
# Write each dataframe to a different worksheet.
for row in cursor.tables():
    if "MSys" in row.table_name:
        pass
    else:
        _df = pd.read_sql("Select * From [%s]" % row.table_name, cnxn)
        _df.to_excel(writer, sheet_name=row.table_name[:30], index=False)
# Close the Pandas Excel writer and output the Excel file.
writer.save()
```

## Case study: SPT data for a selected location

The use of gINT data reading is illustrated for reporting SPT blowcount for a given location.

### Retrieval of test locations

The locations of tests are given in the ```POINT``` table:

```python
point_df = pd.read_sql("Select * From [POINT]", cnxn)
point_df
```

As an example, the SPT blowcount will be reported for PointID 6, with a depth of 36.5ft.

### Retrieval of SPT data

The SPT data is included in the ```SAMPLE``` table. We can import all the data first:

```python
sample_df = pd.read_sql("Select * From [SAMPLE]", cnxn)
sample_df.head()
```

A common problem with data imported from external files is that the data does not have the correct data type. We can check this with the ```.dtypes``` function in Pandas.

```python
sample_df.dtypes
```

We can see that SPT numbers are indeed not numeric (```object``` data type). We can convert these columns as follows:

```python
for key in ['SPT 1', 'SPT 2', 'SPT 3']:
    sample_df[key] = pd.to_numeric(sample_df[key], errors='coerce')
```

```python
sample_df.head()
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

These numbers can be used for further processing using the ```SPTProcessing``` class in [```groundhog```](https://github.com/snakesonabrain/groundhog).

## Closing remarks: Using gINT library files for data interpretation

This article shows how gINT project files can be read using ```mdbtools``` and ```pandas_access```. The Microsoft Access database files are readily imported in Python which can greatly facilitate further processing.

Certain gINT project files are also connected to a gINT library file (```.glb``` extension). These files contain e.g. possible choices for soil types, hammer types, ... In the example above, such a file would contain a table which says that ```GRAB``` stands for a grab sample and ```SS``` for a split-spoon sample. The methods described above can just as easily be used to import these ```.glb``` files.
