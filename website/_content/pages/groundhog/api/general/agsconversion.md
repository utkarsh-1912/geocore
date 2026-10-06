---
title: agsconversion
slug: groundhog/api/general/agsconversion
section: Groundhog API Reference
description: 'API reference for groundhog.general.agsconversion: 0 functions, 1 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/general/agsconversion.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.general.agsconversion
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/general/agsconversion.html
geocore_available: true
geocore_functions:
- AGSConverter
- AGSConverter_convert_ags_group
---

Module `groundhog.general.agsconversion` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/general/agsconversion.py).

Upstream documentation: [AGS to Pandas converter reference](https://groundhog.readthedocs.io/en/main/general/agsconversion.html).

**Classes:** [`AGSConverter`](#agsconverter)

<a id="agsconverter"></a>

## class `AGSConverter`

<span class="gc-badge gc-available" data-geocore-function="AGSConverter">Available in GeoCore</span> [General and utility functions › AGS Conversion › AGSConverter](/docs/geocore/using/modules#agsconverter)

```python
AGSConverter(
    path,
    encoding='utf8',
    errors='replace',
    removedoublequotes=True,
    removeheadinglinebreaks=True,
    agsformat='4',
    **kwargs,
)
```

<a id="agsconverter-__init__"></a>

### `AGSConverter.__init__`

```python
__init__(
    path,
    encoding='utf8',
    errors='replace',
    removedoublequotes=True,
    removeheadinglinebreaks=True,
    agsformat='4',
    **kwargs,
)
```

Initializes an AGS conversion object using the path to the AGS file. The AGS file needs to properly formatted with at least one blank line between each group. Each group should have four lines before the data starts:

- A line with the group name;
- A line with column headers;
- A line with the units of the values in the columns;
- A line with the data type of the columns

The functionality is developed for AGS4.x files but support for AGS3.1 files is also available using `agsformat="3.1"` as optional keyword argument.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `path` |  |  | required | Path to the AGS 4.0 file |
| `encoding` |  |  | `'utf8'` | Encoding of the file (default=utf-8) |
| `errors` |  |  | `'replace'` | Specify file reading behaviour in case of encoding errors |
| `removedoublequotes` |  |  | `True` | Boolean determining whether doublequotes need to be removed after file loading (default=True) |
| `removeheadinglinebreaks` |  |  | `True` | Boolean determining whether line breaks in heading rows need to be removed after file loading (default=True) |
| `agsformat` |  |  | `'4'` | Format of the AGS file (default=`"4"`). AGS 3.1 (`"3.1"`) is also available |

<a id="agsconverter-remove_doublequotes"></a>

### `AGSConverter.remove_doublequotes`

```python
remove_doublequotes(replace_by='')
```

Remove double quotes which are not preceded by a comma ("") and replace by a the value defined in `replace_by` and a single quote. This is done because the `read_csv` function of Pandas will be used in a later stage and there can be errors when reading double quotes. Such expressions are common when coordinates in ° ' " format are included in the ags file.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `replace_by` |  |  | `''` | String to replace the first quote of the double quote with |

**Returns**

<a id="agsconverter-remove_heading_linebreaks"></a>

### `AGSConverter.remove_heading_linebreaks`

```python
remove_heading_linebreaks()
```

Removes line breaks in header rows which would prevent further AGS parsing If a comma is followed by a line break (`, `), it is replaced by a comma without line break

<a id="agsconverter-extract_groupnames"></a>

### `AGSConverter.extract_groupnames`

```python
extract_groupnames()
```

Scans the AGS file and extracts all group names

**Returns**

Sets the attribute `groupnames` of the `AGSConverter` object

<a id="agsconverter-convert_ags_headers"></a>

### `AGSConverter.convert_ags_headers`

```python
convert_ags_headers(df, agsformat)
```

Converts the headers of an AGS-based dataframes from the three rows in the AGS to a single column header. Numerical data is also converted into the correct datatype.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `df` |  |  | required | Dataframe with the group data |
| `agsformat` |  |  | required | No upstream documentation. |

**Returns**

Dataframe with updated headers

<a id="agsconverter-convert_ags_group"></a>

### `AGSConverter.convert_ags_group`

<span class="gc-badge gc-available" data-geocore-function="AGSConverter_convert_ags_group">Available in GeoCore</span> [General and utility functions › AGS Conversion › Convert AGS Group to Table](/docs/geocore/using/modules#agsconverter_convert_ags_group)

```python
convert_ags_group(
    groupname,
    verbose_keys=False,
    additional_keys={},
    use_shorthands=False,
    drop_heading_col=True,
    **kwargs,
)
```

Isolate the data for a certain group and convert it to a Pandas dataframe.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `groupname` |  |  | required | Name of the group to be converted |
| `verbose_keys` |  |  | `False` | Boolean determining whether AGS code keys or their verbose equivalents are used. Conversion happens using the dictionaries in tables.py (default=False for AGS code keys) |
| `additional_keys` |  |  | `{}` | Additional custom keys used in dataframe column name conversion |
| `use_shorthands` |  |  | `False` | Boolean determining whether shorthand codes should be used. If True, a first pass is done using these. |
| `drop_heading_col` |  |  | `True` | No upstream documentation. |

**Returns**

Returns a dataframe with the requested data

<a id="agsconverter-create_dataframes"></a>

### `AGSConverter.create_dataframes`

```python
create_dataframes(
    selectedgroups=None,
    verbose_keys=False,
    use_shorthands=False,
    drop_heading_col=True,
    **kwargs,
)
```

Create a dictionary with Pandas dataframes for each groupname. The groups can be finetuned through the `selectedgroups` argument.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `selectedgroups` |  |  | `None` | List of groupnames to limit the conversion to (default is None leading to all groups being converted) |
| `verbose_keys` |  |  | `False` | Boolean determining whether AGS code keys or their verbose equivalents are used. Conversion happens using the dictionaries in tables.py (default=False for AGS code keys) |
| `use_shorthands` |  |  | `False` | Boolean determining whether shorthand codes should be used. If True, a first pass is done using these. |
| `drop_heading_col` | UNIT |  | `True` | Boolean determining is the column `HEADING ` should be dropped (default=True) |

**Returns**

Sets the `data` attribute for the `AGSConverter` object
