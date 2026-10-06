---
title: pcpt_processing
slug: groundhog/api/siteinvestigation/insitutests/pcpt_processing
section: Groundhog API Reference
description: 'API reference for groundhog.siteinvestigation.insitutests.pcpt_processing: 2 functions, 2 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/siteinvestigation/insitutests/pcpt_processing.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.siteinvestigation.insitutests.pcpt_processing
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/site_investigation/pcpt_class.html
geocore_available: true
geocore_functions:
- PCPTProcessing
---

Module `groundhog.siteinvestigation.insitutests.pcpt_processing` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/siteinvestigation/insitutests/pcpt_processing.py).

Upstream documentation: [PCPT processing class](https://groundhog.readthedocs.io/en/main/site_investigation/pcpt_class.html).

**Classes:** [`InsituTestProcessing`](#insitutestprocessing), [`PCPTProcessing`](#pcptprocessing)

**Functions:** [`plot_longitudinal_profile`](#plot_longitudinal_profile), [`plot_combined_longitudinal_profile`](#plot_combined_longitudinal_profile)

<a id="insitutestprocessing"></a>

## class `InsituTestProcessing`

```python
InsituTestProcessing(title, waterunitweight=10.25)
```

Abstract base class for the processing of in-situ tests. Encodes shared functionality between different types of in-situ tests

<a id="insitutestprocessing-__init__"></a>

### `InsituTestProcessing.__init__`

```python
__init__(title, waterunitweight=10.25)
```

Initialises an in-situ test object

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `title` |  |  | required | No upstream documentation. |
| `waterunitweight` |  |  | `10.25` | No upstream documentation. |

<a id="insitutestprocessing-set_position"></a>

### `InsituTestProcessing.set_position`

```python
set_position(easting, northing, elevation, srid=4326, datum='mLAT')
```

Sets the position of an SPT test in a given coordinate system.

By default, srid 4326 is used which means easting is longitude and northing is latitude.

The elevation is referenced to a chart datum for which mLAT (Lowest Astronomical Tide) is the default.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `easting` |  |  | required | X-coordinate of the SPT position |
| `northing` |  |  | required | Y-coordinate of the SPT position |
| `elevation` |  |  | required | Elevation of the SPT position |
| `srid` |  |  | `4326` | SRID of the coordinate system (see http://epsg.io) |
| `datum` |  |  | `'mLAT'` | Chart datum used for the elevation |

**Returns**

Sets the corresponding attributes of the `SPTProcessing` object

<a id="insitutestprocessing-map_properties"></a>

### `InsituTestProcessing.map_properties`

```python
map_properties(
    layer_profile,
    initial_vertical_total_stress=0,
    vertical_total_stress=None,
    vertical_effective_stress=None,
    waterlevel=0,
    extend_layer_profile=True,
)
```

Maps the soil properties defined in the layering to the grid defined by the cone data. The procedure also calculates the total and effective vertical stress. Note that pre-calculated arrays with total and effective vertical stress can also be supplied to the routine. These needs to have the same length as the array with in-situ test depth data.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `layer_profile` | kN/m3 |  | required | `SoilProfile` object with the layer properties (need to contain the soil parameter `Total unit weight ` |
| `initial_vertical_total_stress` |  |  | `0` | Initial vertical total stress at the highest point of the soil profile |
| `vertical_total_stress` |  |  | `None` | Pre-calculated total vertical stress at in-situ test depth nodes (default=None which will lead to calculation of total stress inside the routine) |
| `vertical_effective_stress` |  |  | `None` | Pre-calculated effective vertical stress at in-situ test depth nodes (default=None which will lead to calculation of total stress inside the routine) |
| `waterlevel` | m |  | `0` | Waterlevel in the soil (measured from soil surface), default = 0m |
| `extend_layer_profile` |  |  | `True` | Boolean determining whether the layer profile needs to be extended to the bottom of the CPT (default = True) |

**Returns**

Expands the dataframe `.data` with additional columns for the cone and soil properties

<a id="pcptprocessing"></a>

## class `PCPTProcessing`

<span class="gc-badge gc-available" data-geocore-function="PCPTProcessing">Available in GeoCore</span> [Site investigation › In-situ: PCPT processing class › PCPTProcessing](/docs/geocore/using/modules#pcptprocessing)

```python
PCPTProcessing(title, waterunitweight=10.25)
```

The PCPTProcessing class implements methods for reading, processing and presentation of PCPT data. Common correlations are also encoded.

<a id="pcptprocessing-__init__"></a>

### `PCPTProcessing.__init__`

```python
__init__(title, waterunitweight=10.25)
```

Initialises a PCPTProcessing object based on a title. Optionally, a geographical position can be defined. A dictionary for dumping unstructured data (`additionaldata`) is also available.

An empty dataframe (``.data`) is created for storing the PCPT data`

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `title` |  |  | required | Title for the PCPT test |
| `waterunitweight` |  |  | `10.25` | Unit weight of water used for effective stress calculations (default=10.25kN/m3 for seawater) |

<a id="pcptprocessing-rename_columns"></a>

### `PCPTProcessing.rename_columns`

```python
rename_columns(z_key=None, qc_key=None, fs_key=None, u2_key=None, push_key=None)
```

No upstream documentation.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `z_key` |  |  | `None` | No upstream documentation. |
| `qc_key` |  |  | `None` | No upstream documentation. |
| `fs_key` |  |  | `None` | No upstream documentation. |
| `u2_key` |  |  | `None` | No upstream documentation. |
| `push_key` |  |  | `None` | No upstream documentation. |

<a id="pcptprocessing-convert_columns"></a>

### `PCPTProcessing.convert_columns`

```python
convert_columns(qc_multiplier=1, fs_multiplier=1, u2_multiplier=1)
```

No upstream documentation.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc_multiplier` |  |  | `1` | No upstream documentation. |
| `fs_multiplier` |  |  | `1` | No upstream documentation. |
| `u2_multiplier` |  |  | `1` | No upstream documentation. |

<a id="pcptprocessing-add_zerodepth_row"></a>

### `PCPTProcessing.add_zerodepth_row`

```python
add_zerodepth_row()
```

No upstream documentation.

<a id="pcptprocessing-dropna_rows"></a>

### `PCPTProcessing.dropna_rows`

```python
dropna_rows()
```

No upstream documentation.

<a id="pcptprocessing-load_excel"></a>

### `PCPTProcessing.load_excel`

```python
load_excel(
    path,
    z_key=None,
    qc_key=None,
    fs_key=None,
    u2_key=None,
    push_key='Push',
    qc_multiplier=1,
    fs_multiplier=1,
    u2_multiplier=1,
    add_zero_row=True,
    **kwargs,
)
```

Loads PCPT data from an Excel file. Specific column keys have to be provided for z, qc, fs and u2. If column keys are not specified, the following keys are used:

- 'z [m]' for depth below mudline
- 'qc [MPa]' for cone tip resistance
- 'fs [MPa]' for sleeve friction
- 'u2 [MPa]' for pore pressure at cone shoulder

Note that cone tip resistance, sleeve friction and pore pressure at the shoulder all need to be converted to MPa. Multipliers can be specified if a conversion from kPa to MPa is required. Optional keyword arguments for the `read_excel` function in Pandas can be specified as `**kwargs`.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `path` |  |  | required | Path to the Excel file |
| `z_key` | m |  | `None` | Column key for depth. Optional, default=None when 'z ' is the column key. |
| `qc_key` | MPa |  | `None` | Column key for cone tip resistance. Optional, default=None when 'qc ' is the column key. |
| `fs_key` | MPa |  | `None` | Column key for sleeve friction. Optional, default=None when 'fs ' is the column key. |
| `u2_key` | MPa |  | `None` | Column key for pore pressure at shoulder. Optional, default=None when 'u2 ' is the column key. |
| `push_key` |  |  | `'Push'` | Column key for the current push (for downhole PCPT). Optional, default=None for a continuous push. |
| `qc_multiplier` |  |  | `1` | Multiplier applied on cone tip resistance to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `fs_multiplier` |  |  | `1` | Multiplier applied on sleeve friction to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `u2_multiplier` |  |  | `1` | Multiplier applied on pore pressure at shoulder to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `add_zero_row` |  |  | `True` | Boolean determining whether a datapoint needs to be added at zero depth. |
| `kwargs` |  |  |  | Optional keyword arguments for the read_excel function in Pandas (e.g. sheet_name, header, ...) |

**Returns**

Sets the columns 'z [m]', 'qc [MPa]', 'fs [MPa]' and 'u2 [MPa]' of the `.data` attribute

<a id="pcptprocessing-load_pandas"></a>

### `PCPTProcessing.load_pandas`

```python
load_pandas(
    df,
    z_key=None,
    qc_key=None,
    fs_key=None,
    u2_key=None,
    push_key='Push',
    qc_multiplier=1,
    fs_multiplier=1,
    u2_multiplier=1,
    add_zero_row=True,
)
```

Loads PCPT from a Pandas dataframe. Specific column keys have to be provided for z, qc, fs and u2. If column keys are not specified, the following keys are used:

- 'z [m]' for depth below mudline
- 'qc [MPa]' for cone tip resistance
- 'fs [MPa]' for sleeve friction
- 'u2 [MPa]' for pore pressure at cone shoulder

Note that cone tip resistance, sleeve friction and pore pressure at the shoulder all need to be converted to MPa

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `df` |  |  | required | Pandas dataframe with required column keys |
| `z_key` | m |  | `None` | Column key for depth. Optional, default=None when 'z ' is the column key. |
| `qc_key` | MPa |  | `None` | Column key for cone tip resistance. Optional, default=None when 'qc ' is the column key. |
| `fs_key` | MPa |  | `None` | Column key for sleeve friction. Optional, default=None when 'fs ' is the column key. |
| `u2_key` | MPa |  | `None` | Column key for pore pressure at shoulder. Optional, default=None when 'u2 ' is the column key. |
| `push_key` |  |  | `'Push'` | Column key for the current push (for downhole PCPT). Optional, default=None for a continuous push. |
| `qc_multiplier` |  |  | `1` | Multiplier applied on cone tip resistance to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `fs_multiplier` |  |  | `1` | Multiplier applied on sleeve friction to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `u2_multiplier` |  |  | `1` | Multiplier applied on pore pressure at shoulder to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `add_zero_row` |  |  | `True` | Boolean determining whether a datapoint needs to be added at zero depth. |

**Returns**

Sets the columns 'z [m]', 'qc [MPa]', 'fs [MPa]' and 'u2 [MPa]' of the `.data` attribute

<a id="pcptprocessing-load_ags"></a>

### `PCPTProcessing.load_ags`

```python
load_ags(
    path,
    z_key=None,
    qc_key=None,
    fs_key=None,
    u2_key=None,
    push_key='Push',
    qc_multiplier=1,
    fs_multiplier=1,
    u2_multiplier=1,
    add_zero_row=True,
    ags_group='SCPT',
    verbose_keys=False,
    use_shorthands=False,
    **kwargs,
)
```

Loads PCPT data from an AGS file. Specific column keys have to be provided for z, qc, fs and u2. If column keys are not specified, the following keys are used:

- 'z [m]' for depth below mudline
- 'qc [MPa]' for cone tip resistance
- 'fs [MPa]' for sleeve friction
- 'u2 [MPa]' for pore pressure at cone shoulder

Note that cone tip resistance, sleeve friction and pore pressure at the shoulder all need to be converted to MPa. Multipliers can be specified if a conversion from kPa to MPa is required. Optional keyword arguments for the `read_ags` function in Pandas can be specified as `**kwargs`.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `path` |  |  | required | Path to the ags file |
| `z_key` | m |  | `None` | Column key for depth. Optional, default=None when 'z ' is the column key. |
| `qc_key` | MPa |  | `None` | Column key for cone tip resistance. Optional, default=None when 'qc ' is the column key. |
| `fs_key` | MPa |  | `None` | Column key for sleeve friction. Optional, default=None when 'fs ' is the column key. |
| `u2_key` | MPa |  | `None` | Column key for pore pressure at shoulder. Optional, default=None when 'u2 ' is the column key. |
| `push_key` |  |  | `'Push'` | Column key for the current push (for downhole PCPT). Optional, default=None for a continuous push. |
| `qc_multiplier` |  |  | `1` | Multiplier applied on cone tip resistance to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `fs_multiplier` |  |  | `1` | Multiplier applied on sleeve friction to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `u2_multiplier` |  |  | `1` | Multiplier applied on pore pressure at shoulder to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `add_zero_row` |  |  | `True` | Boolean determining whether a datapoint needs to be added at zero depth. |
| `ags_group` |  |  | `'SCPT'` | Name of the AGS group with the CPT data (default= `"SCPT"`) |
| `verbose_keys` |  |  | `False` | Boolean for using verbose keys in the AGS converter (default=True) |
| `use_shorthands` |  |  | `False` | Boolean for using shorthands in the AGS converter (default=True) |
| `kwargs` |  |  |  | Optional keyword arguments for the read_excel function in Pandas (e.g. sheet_name, header, ...) |

**Returns**

Sets the columns 'z [m]', 'qc [MPa]', 'fs [MPa]' and 'u2 [MPa]' of the `.data` attribute

<a id="pcptprocessing-load_asc"></a>

### `PCPTProcessing.load_asc`

```python
load_asc(
    path,
    column_widths=[],
    skiprows=None,
    custom_headers=None,
    z_key=None,
    qc_key=None,
    fs_key=None,
    u2_key=None,
    push_key='Push',
    qc_multiplier=1,
    fs_multiplier=1,
    u2_multiplier=1,
    add_zero_row=True,
    **kwargs,
)
```

Reads PCPT data from a Uniplot .asc file The widths of the columns for the .asc file need to be specified.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `path` |  |  | required | Path to the .asc file |
| `column_widths` |  |  | `[]` | Column widths to use for the import (compulsory) |
| `skiprows` |  |  | `None` | Number of rows to skip |
| `custom_headers` |  |  | `None` | Custom headers to be used (default=None for auto-detection) |
| `z_key` | m |  | `None` | Column key for depth. Optional, default=None when 'z ' is the column key. |
| `qc_key` | MPa |  | `None` | Column key for cone tip resistance. Optional, default=None when 'qc ' is the column key. |
| `fs_key` | MPa |  | `None` | Column key for sleeve friction. Optional, default=None when 'fs ' is the column key. |
| `u2_key` | MPa |  | `None` | Column key for pore pressure at shoulder. Optional, default=None when 'u2 ' is the column key. |
| `push_key` |  |  | `'Push'` | Column key for the current push (for downhole PCPT). Optional, default=None for a continuous push. |
| `qc_multiplier` |  |  | `1` | Multiplier applied on cone tip resistance to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `fs_multiplier` |  |  | `1` | Multiplier applied on sleeve friction to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `u2_multiplier` |  |  | `1` | Multiplier applied on pore pressure at shoulder to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `add_zero_row` |  |  | `True` | Boolean determining whether a datapoint needs to be added at zero depth. |
| `kwargs` |  |  |  | Optional keyword arguments for reading the datafile |

**Returns**

<a id="pcptprocessing-load_gef"></a>

### `PCPTProcessing.load_gef`

```python
load_gef(
    path,
    inverse_depths=False,
    override_title=True,
    z_key=None,
    qc_key=None,
    fs_key=None,
    u2_key=None,
    push_key='Push',
    qc_multiplier=1,
    fs_multiplier=1,
    u2_multiplier=1,
    add_zero_row=True,
    separator=' ',
    **kwargs,
)
```

Reads PCPT data from a Geotechnical Exchange Format (.gef) file. The file is parsed using regular expressions to provide the necessary data. If location data is provided, this data is also

https://publicwiki.deltares.nl/download/attachments/102204314/GEFCR100.pdf?version=1&modificationDate=1411129283000&api=v2

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `path` |  |  | required | Path to the .asc file |
| `inverse_depths` |  |  | `False` | Boolean indicating whether depths need to be inverted. A positive downward z-axis is expected. |
| `override_title` |  |  | `True` | Boolean indicating if the title specified needs to be replaced by the test id (default = True). |
| `z_key` | m |  | `None` | Column key for depth. Optional, default=None when 'z ' is the column key. |
| `qc_key` | MPa |  | `None` | Column key for cone tip resistance. Optional, default=None when 'qc ' is the column key. |
| `fs_key` | MPa |  | `None` | Column key for sleeve friction. Optional, default=None when 'fs ' is the column key. |
| `u2_key` | MPa |  | `None` | Column key for pore pressure at shoulder. Optional, default=None when 'u2 ' is the column key. |
| `push_key` |  |  | `'Push'` | Column key for the current push (for downhole PCPT). Optional, default=None for a continuous push. |
| `qc_multiplier` |  |  | `1` | Multiplier applied on cone tip resistance to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `fs_multiplier` |  |  | `1` | Multiplier applied on sleeve friction to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `u2_multiplier` |  |  | `1` | Multiplier applied on pore pressure at shoulder to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `add_zero_row` |  |  | `True` | Boolean determining whether a datapoint needs to be added at zero depth. |
| `separator` |  |  | `' '` | Separator used for the gef file (default is `' '`) |
| `kwargs` |  |  |  | Optional keyword arguments for reading the datafile (using `read_csv` from Pandas) |

**Returns**

<a id="pcptprocessing-load_multi_asc"></a>

### `PCPTProcessing.load_multi_asc`

```python
load_multi_asc(
    path,
    column_widths=[],
    skiprows=None,
    custom_headers=None,
    z_key=None,
    qc_key=None,
    fs_key=None,
    u2_key=None,
    push_key='Push',
    qc_multiplier=1,
    fs_multiplier=1,
    u2_multiplier=1,
    add_zero_row=True,
    start_string='Data table',
    end_string='UNICAS data file',
    **kwargs,
)
```

Reads PCPT data from a Uniplot .asc file with multiple pushes The widths of the columns for the .asc file need to be specified.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `path` |  |  | required | Path to the .asc file |
| `column_widths` |  |  | `[]` | Column widths to use for the import (compulsory) |
| `skiprows` |  |  | `None` | Number of rows to skip |
| `custom_headers` |  |  | `None` | Custom headers to be used (default=None for auto-detection) |
| `z_key` | m |  | `None` | Column key for depth. Optional, default=None when 'z ' is the column key. |
| `qc_key` | MPa |  | `None` | Column key for cone tip resistance. Optional, default=None when 'qc ' is the column key. |
| `fs_key` | MPa |  | `None` | Column key for sleeve friction. Optional, default=None when 'fs ' is the column key. |
| `u2_key` | MPa |  | `None` | Column key for pore pressure at shoulder. Optional, default=None when 'u2 ' is the column key. |
| `push_key` |  |  | `'Push'` | Column key for the current push (for downhole PCPT). Optional, default=None for a continuous push. |
| `qc_multiplier` |  |  | `1` | Multiplier applied on cone tip resistance to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `fs_multiplier` |  |  | `1` | Multiplier applied on sleeve friction to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `u2_multiplier` |  |  | `1` | Multiplier applied on pore pressure at shoulder to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `add_zero_row` |  |  | `True` | Boolean determining whether a datapoint needs to be added at zero depth. |
| `start_string` |  |  | `'Data table'` | String showing the start of the data |
| `end_string` |  |  | `'UNICAS data file'` | String showing the end of the data |
| `kwargs` |  |  |  | Optional keyword arguments for reading the datafile |

**Returns**

<a id="pcptprocessing-load_a00"></a>

### `PCPTProcessing.load_a00`

```python
load_a00(
    path,
    column_widths=[],
    skiprows=None,
    custom_headers=None,
    z_key=None,
    qc_key=None,
    fs_key=None,
    u2_key=None,
    push_key='Push',
    qc_multiplier=1,
    fs_multiplier=1,
    u2_multiplier=1,
    add_zero_row=True,
    **kwargs,
)
```

Reads PCPT data from a Uniplot .a00 file The widths of the columns for the .a00 file need to be specified.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `path` |  |  | required | Path to the .a00 file |
| `column_widths` |  |  | `[]` | Column widths to use for the import (compulsory) |
| `skiprows` |  |  | `None` | Number of rows to skip |
| `custom_headers` |  |  | `None` | Custom headers to be used (default=None for auto-detection) |
| `z_key` | m |  | `None` | Column key for depth. Optional, default=None when 'z ' is the column key. |
| `qc_key` | MPa |  | `None` | Column key for cone tip resistance. Optional, default=None when 'qc ' is the column key. |
| `fs_key` | MPa |  | `None` | Column key for sleeve friction. Optional, default=None when 'fs ' is the column key. |
| `u2_key` | MPa |  | `None` | Column key for pore pressure at shoulder. Optional, default=None when 'u2 ' is the column key. |
| `push_key` |  |  | `'Push'` | Column key for the current push (for downhole PCPT). Optional, default=None for a continuous push. |
| `qc_multiplier` |  |  | `1` | Multiplier applied on cone tip resistance to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `fs_multiplier` |  |  | `1` | Multiplier applied on sleeve friction to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `u2_multiplier` |  |  | `1` | Multiplier applied on pore pressure at shoulder to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `add_zero_row` |  |  | `True` | Boolean determining whether a datapoint needs to be added at zero depth. |
| `kwargs` |  |  |  | Optional keyword arguments for reading the datafile |

**Returns**

<a id="pcptprocessing-load_multiple_asc"></a>

### `PCPTProcessing.load_multiple_asc`

```python
load_multiple_asc(
    folder,
    column_widths=[],
    skiprows=None,
    custom_headers=None,
    z_key=None,
    qc_key=None,
    fs_key=None,
    u2_key=None,
    push_key='Push',
    qc_multiplier=1,
    fs_multiplier=1,
    u2_multiplier=1,
    **kwargs,
)
```

A PCPT can be provided as multiple .asc files in one folder. This method loops over the individual files and creates a combined `data` attribute with PCPT data. The method assumes that all .asc files have the same format.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `folder` |  |  | required | Folder with the .asc files |
| `column_widths` |  |  | `[]` | Column widths to use for the import (compulsory) |
| `skiprows` |  |  | `None` | Number of rows to skip |
| `custom_headers` |  |  | `None` | Custom headers to be used (default=None for auto-detection) |
| `z_key` | m |  | `None` | Column key for depth. Optional, default=None when 'z ' is the column key. |
| `qc_key` | MPa |  | `None` | Column key for cone tip resistance. Optional, default=None when 'qc ' is the column key. |
| `fs_key` | MPa |  | `None` | Column key for sleeve friction. Optional, default=None when 'fs ' is the column key. |
| `u2_key` | MPa |  | `None` | Column key for pore pressure at shoulder. Optional, default=None when 'u2 ' is the column key. |
| `push_key` |  |  | `'Push'` | Column key for the current push (for downhole PCPT). Optional, default=None for a continuous push. |
| `qc_multiplier` |  |  | `1` | Multiplier applied on cone tip resistance to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `fs_multiplier` |  |  | `1` | Multiplier applied on sleeve friction to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `u2_multiplier` |  |  | `1` | Multiplier applied on pore pressure at shoulder to convert to MPa (e.g. 0.001 to convert from kPa to MPa) |
| `kwargs` |  |  |  | Optional keyword arguments for reading the datafiles |

**Returns**

Sets the `data` attribute of the PCPTProcessing object

<a id="pcptprocessing-load_pydov"></a>

### `PCPTProcessing.load_pydov`

```python
load_pydov(
    name,
    push_key='Push',
    add_zero_row=True,
    z_key='diepte',
    qc_key='qc',
    fs_key='fs',
    u2_key='u',
    qc_multiplier=1,
    fs_multiplier=0.001,
    u2_multiplier=0.001,
    **kwargs,
)
```

Load CPT data from Databank Ondergrond Vlaanderen based on the unique CPT name which can be found in DOV

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `name` |  |  | required | Unique identifier of the CPT in pydov |
| `push_key` |  |  | `'Push'` | No upstream documentation. |
| `add_zero_row` |  |  | `True` | No upstream documentation. |
| `z_key` |  |  | `'diepte'` | No upstream documentation. |
| `qc_key` |  |  | `'qc'` | No upstream documentation. |
| `fs_key` |  |  | `'fs'` | No upstream documentation. |
| `u2_key` |  |  | `'u'` | No upstream documentation. |
| `qc_multiplier` |  |  | `1` | No upstream documentation. |
| `fs_multiplier` |  |  | `0.001` | No upstream documentation. |
| `u2_multiplier` |  |  | `0.001` | No upstream documentation. |

**Returns**

Sets the `data` attribute of the PCPTProcessing object

<a id="pcptprocessing-get_stratigraphy_pydov"></a>

### `PCPTProcessing.get_stratigraphy_pydov`

```python
get_stratigraphy_pydov(**kwargs)
```

Retrieves stratigraphic info from the 3D geological model of Flanders based on a CPT loaded in pydov

<a id="pcptprocessing-load_bro"></a>

### `PCPTProcessing.load_bro`

```python
load_bro(name, **kwargs)
```

Load CPT data from BasisRegistratie Ondergrond (BRO) based on the unique CPT name which can be found in BRO. The data loading is handled by the geotexx package written by Thomas van der Linden (https://github.com/ic144/geotexxx_package).

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `name` |  |  | required | Unique identifier of the CPT in BRO (see https://www.dinoloket.nl/ondergrondgegevens) |

**Returns**

Sets the `data` attribute of the PCPTProcessing object

<a id="pcptprocessing-get_stratigraphy_bro"></a>

### `PCPTProcessing.get_stratigraphy_bro`

```python
get_stratigraphy_bro(**kwargs)
```

Retrieves stratigraphic info from the 3D geological model GeoTop of The Netherlands based on a CPT loaded from BRO

<a id="pcptprocessing-combine_pcpt"></a>

### `PCPTProcessing.combine_pcpt`

```python
combine_pcpt(obj, keep='first')
```

Combine PCPT data for two PCPTProcessing objects. The data of the second PCPT (`obj`) will be merged with the current object and the `data` attribute will be a combined dataframe. Only columns 'z [m]', 'qc [MPa]', 'fs [MPa]', 'u2 [MPa]' and 'Push' will be retained.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `obj` |  |  | required | PCPTProcessing object containing the second PCPT info |
| `keep` |  |  | `'first'` | Determines what to do in the area with overlap ("first", "second" or "both"). If "first" is chosen (default), the data from the first PCPT `self` is used in the area with overlap. For "second", data for the second PCPT `obj` is retained. If 'both' is selected, overlapping data will exist which might lead to presentation problems. |

**Returns**

Updates the `data` attribute of the current PCPTProcessing object

<a id="pcptprocessing-map_properties"></a>

### `PCPTProcessing.map_properties`

```python
map_properties(
    layer_profile,
    cone_profile=   Depth from [m]  ...  Sleeve cross-sectional area bottom [cm2]
0               0  ...                                       NaN

[1 rows x 8 columns],
    initial_vertical_total_stress=0,
    vertical_total_stress=None,
    vertical_effective_stress=None,
    waterlevel=0,
    extend_cone_profile=True,
    extend_layer_profile=True,
)
```

Maps the soil properties defined in the layering and the cone properties to the grid defined by the cone data. The procedure also calculates the total and effective vertical stress. Note that pre-calculated arrays with total and effective vertical stress can also be supplied to the routine. These needs to have the same length as the array with PCPT depth data.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `layer_profile` | kN/m3 |  | required | `SoilProfile` object with the layer properties (need to contain the soil parameter `Total unit weight ` |
| `cone_profile` |  |  | `   Depth from [m]  ...  Sleeve cross-sectional area bottom [cm2] 0               0  ...                                       NaN  [1 rows x 8 columns]` | `SoilProfile` object with the cone properties (default=`DEFAULT_CONE_PROPERTIES`) |
| `initial_vertical_total_stress` |  |  | `0` | Initial vertical total stress at the highest point of the soil profile |
| `vertical_total_stress` |  |  | `None` | Pre-calculated total vertical stress at PCPT depth nodes (default=None which will lead to calculation of total stress inside the routine) |
| `vertical_effective_stress` |  |  | `None` | Pre-calculated effective vertical stress at PCPT depth nodes (default=None which will lead to calculation of total stress inside the routine) |
| `waterlevel` | m |  | `0` | Waterlevel in the soil (measured from soil surface), default = 0m |
| `extend_cone_profile` |  |  | `True` | Boolean determining whether the cone profile needs to be extended to go to the bottom of the CPT (default = True) |
| `extend_layer_profile` |  |  | `True` | Boolean determining whether the layer profile needs to be extended to the bottom of the CPT (default = True) |

**Returns**

Expands the dataframe `.data` with additional columns for the cone and soil properties

<a id="pcptprocessing-downhole_pcpt_corrections"></a>

### `PCPTProcessing.downhole_pcpt_corrections`

```python
downhole_pcpt_corrections(area_ratio_override=nan)
```

Correct the PCPT for downhole effects. Select each push, find the start depth of the push and

$$
q_c = q_c^* + d \cdot a \cdot \gamma_w
$$

$$
u_2 = u_2^* + \gamma_w \cdot d
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `area_ratio_override` |  |  | `nan` | No upstream documentation. |

**Returns**

<a id="pcptprocessing-normalise_pcpt"></a>

### `PCPTProcessing.normalise_pcpt`

```python
normalise_pcpt(qc_for_rf=False, calculate_ic=True, **kwargs)
```

Carries out the necessary normalisation and correction on PCPT data to allow calculation of derived parameters and soil type classification.

First, the cone resistance is corrected for the unequal area effect using the cone area ratio. The correction for total sleeve friction is not included as it is more uncommon. The procedure assumes that the pore pressure are measured at the shoulder of the cone. If this is not the case, corrections can be used which are not included in this function.

During normalisation, the friction ratio and pore pressure ratio are calculated. Note that the total cone resistance is used for the friction ratio and pore pressure ratio calculation, the pore pressure ratio calculation also used the total vertical effective stress. The normalised cone resistance and normalised friction ratio are also calculated.

Finally the net cone resistance is calculated.

Note that the absence of pore water pressure measurements will lead to NaN values. Reasoning can be used (e.g. presence of rapidly draining layers) to edit the pore pressure data before running this method.

The total sleeve friction is also calculated. If the cross-sectional area of the friction sleeve is equal at the top and bottom of the sleeve, a correction is not required. This is the default behaviour (cross-sectional areas equal to NaN) but the areas can be entered to calculate the total sleeve friction.

Soil behaviour type index $I_c$ and the corrected normalised cone resistance $Q_{tn}$ are calculated if `calculate_ic` is set to `True`. For quicker calculation, set this boolean to False.

$$
q_c = q_c^* + d \cdot a \cdot \gamma_w
$$

$$
q_t = q_c + u_2 \cdot (1 - a)
$$

$$
u_2 = u_2^* + \gamma_w \cdot d
$$

$$
\Delta u_2 = u_2 - u_o
$$

$$
R_f = \frac{f_s}{q_t}
$$

$$
B_q = \frac{\Delta u_2}{q_t - \sigma_{vo}}
$$

$$
Q_t = \frac{q_t - \sigma_{vo}}{\sigma_{vo}^{\prime}}
$$

$$
Q_{tn} = \frac{q_t - \sigma_{vo}}{P_a} \left( \frac{P_a}{\sigma_{vo}^{\prime}} \right)^n
$$

$$
n = 0.381 \cdot I_c + 0.05 \cdot \frac{\sigma_{vo}^{\prime}}{P_a} - 0.15 \ \text{where} \ n \leq 1
$$

$$
F_r = \frac{f_s}{q_t - \sigma_{vo}}
$$

$$
q_{net} = q_t - \sigma_{vo}
$$

$$
f_t = f_s - u_2 \frac{A_{sb} - A_{st}}{A_s}
$$

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc_for_rf` |  |  | `False` | Boolean determining whether cone resistance instead of total cone resistance should be used for CPTs where pore pressures are not measured (default=False). If True, $q_t$ is replaced by $q_c$ in the formula for $R_f$. |
| `calculate_ic` |  |  | `True` | No upstream documentation. |

**Returns**

Supplements the PCPT data (`.data`) with the normalised properties (column keys 'qt [MPa]', 'Delta u2 [MPa]', 'Rf [%]', 'Bq [-]', 'Qt [-]', 'Fr [%]', 'qnet [MPa]', 'ft [MPa]'

<a id="pcptprocessing-plot_raw_pcpt"></a>

### `PCPTProcessing.plot_raw_pcpt`

```python
plot_raw_pcpt(
    qc_range=(0, 100),
    qc_tick=10,
    fs_range=(0, 1),
    fs_tick=0.1,
    u2_range=(-0.5, 2.5),
    u2_tick=0.5,
    z_range=None,
    z_tick=2,
    rf_range=(0, 5),
    rf_tick=0.5,
    show_hydrostatic=True,
    plot_friction_ratio=False,
    friction_ratio_panel=3,
    plot_height=700,
    plot_width=1000,
    return_fig=False,
    plot_title=None,
    plot_margin={'t': 100, 'l': 50, 'b': 50},
    color=None,
    hydrostaticcolor=None,
    show_hydrostatic_legend=False,
    waterlevel_override=0,
    latex_titles=True,
)
```

Plots the raw PCPT data using the Plotly package. This generates an interactive plot.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qc_range` |  |  | `(0, 100)` | Range for the cone tip resistance (default=(0, 100MPa)) |
| `qc_tick` |  |  | `10` | Tick interval for the cone tip resistance (default=10MPa) |
| `fs_range` |  |  | `(0, 1)` | Range for the sleeve friction (default=(0, 1MPa)) |
| `fs_tick` |  |  | `0.1` | Tick interval for sleeve friction (default=0.1MPa) |
| `u2_range` |  |  | `(-0.5, 2.5)` | Range for the pore pressure at the shoulder (default=(-0.1, 0.5MPa)) |
| `u2_tick` |  |  | `0.5` | Tick interval for the pore pressure at the shoulder (default=0.05MPa) |
| `z_range` |  |  | `None` | Range for the depth (default=None for plotting from zero to maximum cone penetration) |
| `z_tick` |  |  | `2` | Tick interval for depth (default=2m) |
| `rf_range` |  |  | `(0, 5)` | Range for the friction ratio, if used (default=None for plotting from zero to 5%) |
| `rf_tick` |  |  | `0.5` | Tick interval for friction ratio, if used (default=0.5%) |
| `show_hydrostatic` |  |  | `True` | Boolean determining whether hydrostatic pressure is shown on the pore pressure plot panel |
| `plot_friction_ratio` |  |  | `False` | Boolean determining whether friction ratio needs to be plotted (default=False) |
| `friction_ratio_panel` |  |  | `3` | Panel for plotting friction ratio (default=3 for pore pressure panel). Only used when `plot_friction_ratio=True` |
| `plot_height` |  |  | `700` | Height for the plot (default=700px) |
| `plot_width` |  |  | `1000` | Width for the plot (default=1000px) |
| `return_fig` |  |  | `False` | Boolean determining whether the figure needs to be returned (True) or plotted (False) |
| `plot_title` |  |  | `None` | Plot for the title (default=None) |
| `plot_margin` |  |  | `{'t': 100, 'l': 50, 'b': 50}` | Margin for the plot (default=dict(t=100, l=50, b=50)) |
| `color` |  |  | `None` | Color to be used for plotting the hydrostatic pressure (default=None for default plotly colors) |
| `hydrostaticcolor` |  |  | `None` | No upstream documentation. |
| `show_hydrostatic_legend` |  |  | `False` | Boolean determining whether to show the hydrostatic pressure in the legend |
| `waterlevel_override` |  |  | `0` | If a waterlevel is not specified in a soil profile which is mapped to the CPT, this can be used to get the water table at the correct elevation (default=0m for water level at the surface, >0 for water level below groundlevel) |
| `latex_titles` |  |  | `True` | Boolean determining whether axis titles should be shown as LaTeX (default = True) |

**Returns**

<a id="pcptprocessing-plot_raw_pcpt_withlog"></a>

### `PCPTProcessing.plot_raw_pcpt_withlog`

```python
plot_raw_pcpt_withlog(
    soilprofile,
    qc_range=(-10, 100),
    qc_tick=10,
    fs_range=(0, 1),
    fs_tick=0.1,
    u2_range=(-0.5, 2.5),
    u2_tick=0.5,
    z_range=None,
    z_tick=2,
    rf_range=(0, 5),
    rf_tick=0.5,
    plot_friction_ratio=False,
    plot_height=700,
    plot_width=1000,
    return_fig=False,
    plot_title=None,
    latex_titles=True,
    fillcolordict={'Sand': 'yellow', 'Clay': 'brown', 'Rock': 'grey'},
    **kwargs,
)
```

Plots the raw PCPT data using the Plotly package using a `groundhog` `LogPlot`. This generates an interactive plot.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `soilprofile` |  |  | required | `SoilProfile` object to use for the `LogPlot` |
| `qc_range` |  |  | `(-10, 100)` | Range for the cone tip resistance (default=(0, 100MPa)) |
| `qc_tick` |  |  | `10` | Tick interval for the cone tip resistance (default=10MPa) |
| `fs_range` |  |  | `(0, 1)` | Range for the sleeve friction (default=(0, 1MPa)) |
| `fs_tick` |  |  | `0.1` | Tick interval for sleeve friction (default=0.1MPa) |
| `u2_range` |  |  | `(-0.5, 2.5)` | Range for the pore pressure at the shoulder (default=(-0.1, 0.5MPa)) |
| `u2_tick` |  |  | `0.5` | Tick interval for the pore pressure at the shoulder (default=0.05MPa) |
| `z_range` |  |  | `None` | Range for the depth (default=None for plotting from zero to maximum cone penetration) |
| `z_tick` |  |  | `2` | Tick interval for depth (default=2m) |
| `rf_range` |  |  | `(0, 5)` | Range for the friction ratio, if used (default=None for plotting from zero to 5%) |
| `rf_tick` |  |  | `0.5` | Tick interval for friction ratio, if used (default=0.5%) |
| `plot_friction_ratio` |  |  | `False` | Boolean determining whether friction ratio needs to be plotted (default=False) |
| `plot_height` |  |  | `700` | Height for the plot (default=700px) |
| `plot_width` |  |  | `1000` | Width for the plot (default=1000px) |
| `return_fig` |  |  | `False` | Boolean determining whether the figure needs to be returned (True) or plotted (False) |
| `plot_title` |  |  | `None` | Plot for the title (default=None) |
| `latex_titles` |  |  | `True` | Boolean determining whether axis titles should be shown as LaTeX (default = True) |
| `fillcolordict` |  |  | `{'Sand': 'yellow', 'Clay': 'brown', 'Rock': 'grey'}` | Dictionary with fill colors for each of the soil types. Every unique `Soil type` needs to have a corresponding color. Default: `{"Sand": 'yellow', "Clay": 'brown', 'Rock': 'grey'}` |
| `show_hydrostatic` |  |  |  | Boolean determining whether hydrostatic pressure is shown on the pore pressure plot panel |
| `show_hydrostatic` |  |  |  | Boolean determining whether hydrostatic pressure is shown on the pore pressure plot panel |
| `friction_ratio_panel` |  |  |  | Panel for plotting friction ratio (default=3 for pore pressure panel). Only used when `plot_friction_ratio=True` |
| `plot_margin` |  |  |  | Margin for the plot (default=dict(t=100, l=50, b=50)) |
| `color` |  |  |  | Color to be used for plotting (default=None for default plotly colors) |
| `color` |  |  |  | Color to be used for plotting the hydrostatic pressure (default=None for default plotly colors) |
| `show_hydrostatic_legend` |  |  |  | Boolean determining whether to show the hydrostatic pressure in the legend |
| `waterlevel_override` |  |  |  | If a waterlevel is not specified in a soil profile which is mapped to the CPT, this can be used to get the water table at the correct elevation (default=0m for water level at the surface, >0 for water level below groundlevel) |

**Returns**

<a id="pcptprocessing-plot_raw_pcpt_withlog_matplotlib"></a>

### `PCPTProcessing.plot_raw_pcpt_withlog_matplotlib`

```python
plot_raw_pcpt_withlog_matplotlib(
    soilprofile,
    qc_range=(-10, 100),
    fs_range=(0, 1),
    u2_range=(-0.5, 2.5),
    z_range=None,
    rf_range=(0, 5),
    plot_friction_ratio=False,
    plot_height=8,
    plot_width=10,
    return_fig=False,
    latex_titles=True,
    fillcolordict={'Sand': 'yellow', 'Clay': 'brown', 'Rock': 'grey'},
    **kwargs,
)
```

Plots the raw PCPT data using the Matplotlib package using a `groundhog` `LogPlotMatplotlib`. This generates an Matplotlib plot.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `soilprofile` |  |  | required | `SoilProfile` object to use for the `LogPlot` |
| `qc_range` |  |  | `(-10, 100)` | Range for the cone tip resistance (default=(0, 100MPa)) |
| `fs_range` |  |  | `(0, 1)` | Range for the sleeve friction (default=(0, 1MPa)) |
| `u2_range` |  |  | `(-0.5, 2.5)` | Range for the pore pressure at the shoulder (default=(-0.1, 0.5MPa)) |
| `z_range` |  |  | `None` | Range for the depth (default=None for plotting from zero to maximum cone penetration) |
| `rf_range` |  |  | `(0, 5)` | Range for the friction ratio, if used (default=None for plotting from zero to 5%) |
| `plot_friction_ratio` |  |  | `False` | Boolean determining whether friction ratio needs to be plotted (default=False) |
| `plot_height` |  |  | `8` | Height for the plot (default=700px) |
| `plot_width` |  |  | `10` | Width for the plot (default=1000px) |
| `return_fig` |  |  | `False` | Boolean determining whether the figure needs to be returned (True) or plotted (False) |
| `latex_titles` |  |  | `True` | Boolean determining whether axis titles should be shown as LaTeX (default = True) |
| `fillcolordict` |  |  | `{'Sand': 'yellow', 'Clay': 'brown', 'Rock': 'grey'}` | Dictionary with fill colors for each of the soil types. Every unique `Soil type` needs to have a corresponding color. Default: `{"Sand": 'yellow', "Clay": 'brown', 'Rock': 'grey'}` |
| `qc_tick` |  |  |  | Tick interval for the cone tip resistance (default=10MPa) |
| `fs_tick` |  |  |  | Tick interval for sleeve friction (default=0.1MPa) |
| `u2_tick` |  |  |  | Tick interval for the pore pressure at the shoulder (default=0.05MPa) |
| `z_tick` |  |  |  | Tick interval for depth (default=2m) |
| `show_hydrostatic` |  |  |  | Boolean determining whether hydrostatic pressure is shown on the pore pressure plot panel |
| `rf_tick` |  |  |  | Tick interval for friction ratio, if used (default=0.5%) |
| `show_hydrostatic` |  |  |  | Boolean determining whether hydrostatic pressure is shown on the pore pressure plot panel |
| `friction_ratio_panel` |  |  |  | Panel for plotting friction ratio (default=3 for pore pressure panel). Only used when `plot_friction_ratio=True` |
| `plot_title` |  |  |  | Plot for the title (default=None) |
| `plot_margin` |  |  |  | Margin for the plot (default=dict(t=100, l=50, b=50)) |
| `color` |  |  |  | Color to be used for plotting (default=None for default plotly colors) |
| `color` |  |  |  | Color to be used for plotting the hydrostatic pressure (default=None for default plotly colors) |
| `show_hydrostatic_legend` |  |  |  | Boolean determining whether to show the hydrostatic pressure in the legend |
| `waterlevel_override` |  |  |  | If a waterlevel is not specified in a soil profile which is mapped to the CPT, this can be used to get the water table at the correct elevation (default=0m for water level at the surface, >0 for water level below groundlevel) |

**Returns**

<a id="pcptprocessing-plot_normalised_pcpt"></a>

### `PCPTProcessing.plot_normalised_pcpt`

```python
plot_normalised_pcpt(
    qt_range=(0, 3),
    fr_range=(-1, 1),
    bq_range=(-0.6, 1.4),
    bq_tick=0.2,
    z_range=None,
    z_tick=2,
    plot_height=700,
    plot_width=1000,
    color=None,
    return_fig=False,
    plot_title=None,
    latex_titles=True,
)
```

Plots the normalised PCPT properties vs depth.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `qt_range` |  |  | `(0, 3)` | Range for Qt (optional, default is (0, 3) for 1 to 1000 on log scale) |
| `fr_range` |  |  | `(-1, 1)` | Range for Fr (optional, default is (-1, 1) for 0.1 to 10 on log scale) |
| `bq_range` |  |  | `(-0.6, 1.4)` | Range for Bq (optional, default is (-0.6, 1.4)) |
| `bq_tick` |  |  | `0.2` | Tick mark interval for Bq |
| `z_range` |  |  | `None` | Range for depths (optional, default is (0, maximum PCPT depth) |
| `z_tick` |  |  | `2` | Tick mark distance for PCPT |
| `plot_height` |  |  | `700` | Height of the plot in pixels |
| `plot_width` |  |  | `1000` | Width of the plot in pixels |
| `color` |  |  | `None` | No upstream documentation. |
| `return_fig` |  |  | `False` | Boolean determining whether the figure is returned or the plot is generated; Default behaviour is to generate the plot. |
| `plot_title` |  |  | `None` | Plot title |
| `latex_titles` |  |  | `True` | Boolean determining whether axis titles should be shown as LaTeX (default = True) |

**Returns**

Returns the figure if return_fig=True. Otherwise the plot is displayed.

<a id="pcptprocessing-plot_properties"></a>

### `PCPTProcessing.plot_properties`

```python
plot_properties(
    prop_keys,
    plot_ranges,
    plot_ticks,
    z_range=None,
    z_tick=2,
    legend_titles=None,
    axis_titles=None,
    showlegends=None,
    plot_layers=True,
    plot_height=700,
    plot_width=1000,
    colors=None,
    return_fig=False,
    plot_title=None,
    latex_titles=True,
)
```

Plots the soil and/or PCPT properties vs depth.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `prop_keys` |  |  | required | Tuple of tuples with the keys to be plotted. Keys in the same tuple are plotted on the same panel |
| `plot_ranges` |  |  | required | Tuple of tuples with ranges for the panels of the plot |
| `plot_ticks` |  |  | required | Tuple with tick intervals for the plot panels |
| `z_range` |  |  | `None` | Range for depths (optional, default is (0, maximum PCPT depth) |
| `z_tick` |  |  | `2` | Tick mark distance for PCPT |
| `legend_titles` |  |  | `None` | Tuple with entries to be used in the legend. If left blank, the keys are used |
| `axis_titles` |  |  | `None` | Tuple with entries to be used as axis labels. If left blank, the keys are used |
| `showlegends` |  |  | `None` | Array of booleans determining whether or not to show the trace in the legend |
| `plot_layers` |  |  | `True` | Boolean determining whether layers are plotted (default=True) |
| `plot_height` |  |  | `700` | Height of the plot in pixels |
| `plot_width` |  |  | `1000` | Width of the plot in pixels |
| `colors` |  |  | `None` | No upstream documentation. |
| `return_fig` |  |  | `False` | Boolean determining whether the figure is returned or the plot is generated; Default behaviour is to generate the plot. |
| `plot_title` |  |  | `None` | Plot title |
| `latex_titles` |  |  | `True` | Boolean determining whether axis titles should be shown as LaTeX (default = True) |

**Returns**

Returns the figure if return_fig=True. Otherwise the plot is displayed.

<a id="pcptprocessing-plot_properties_withlog"></a>

### `PCPTProcessing.plot_properties_withlog`

```python
plot_properties_withlog(
    prop_keys,
    plot_ranges,
    plot_ticks,
    legend_titles=None,
    axis_titles=None,
    showfig=True,
    showlayers=True,
    **kwargs,
)
```

Plots CPT properties vs depth and includes a mini-log on the left-hand side. The minilog is composed based on the entries in the `Soil type` column of the layering

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `prop_keys` |  |  | required | Tuple of tuples with the keys to be plotted. Keys in the same tuple are plotted on the same panel |
| `plot_ranges` |  |  | required | Tuple of tuples with ranges for the panels of the plot |
| `plot_ticks` |  |  | required | Tuple with tick intervals for the plot panels |
| `legend_titles` |  |  | `None` | Tuple with entries to be used in the legend. If left blank, the keys are used |
| `axis_titles` |  |  | `None` | Tuple with entries to be used as axis labels. If left blank, the keys are used |
| `showfig` |  |  | `True` | Boolean determining whether the figure needs to be shown in the notebook (default=True) |
| `showlayers` |  |  | `True` | Boolean determining whether layer positions need to be plotted (default=True) |
| `z_range` |  |  |  | Range for depths (optional, default is (0, maximum PCPT depth) |
| `z_tick` |  |  | `2` | Tick mark distance for PCPT |

**Returns**

Plotly figure with mini-log

<a id="pcptprocessing-plot_robertson_chart"></a>

### `PCPTProcessing.plot_robertson_chart`

```python
plot_robertson_chart(
    charttype='combined',
    start_depth=None,
    end_depth=None,
    qt_range=(0, 3),
    fr_range=(-1, 1),
    modified=False,
    bq_range=(-0.6, 1.4),
    bq_tick=0.2,
    layerchangetolerance=0,
    plot_height=700,
    plot_width=1000,
    plot_width_single=600,
    return_fig=False,
    plot_title=None,
    backgroundimagedir='',
    latex_titles=True,
)
```

Plots the normalised PCPT points in the Robertson chart to distinguish the soil type. The display can be limited to a specific depth range (by specifying `start_depth` and `end_depth`. The color coding is based on the layer.

From v0.15.0, the Robertson chart can be split in two using the `charttype` argument. By default, both Qt-Fr and Qt-Bq plots are shown, but the user can also choose to display only the Qt-Fr plot (`charttype='QtFr'`) or only the Qt-Bq plot (`charttype='QtBq'`).

The modified Robertson chart can also be shown by setting the boolean `modified` to `True`.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `charttype` |  |  | `'combined'` | No upstream documentation. |
| `start_depth` |  |  | `None` | No upstream documentation. |
| `end_depth` |  |  | `None` | No upstream documentation. |
| `qt_range` |  |  | `(0, 3)` | No upstream documentation. |
| `fr_range` |  |  | `(-1, 1)` | No upstream documentation. |
| `modified` |  |  | `False` | No upstream documentation. |
| `bq_range` |  |  | `(-0.6, 1.4)` | No upstream documentation. |
| `bq_tick` |  |  | `0.2` | No upstream documentation. |
| `layerchangetolerance` |  |  | `0` | No upstream documentation. |
| `plot_height` |  |  | `700` | No upstream documentation. |
| `plot_width` |  |  | `1000` | No upstream documentation. |
| `plot_width_single` |  |  | `600` | No upstream documentation. |
| `return_fig` |  |  | `False` | No upstream documentation. |
| `plot_title` |  |  | `None` | No upstream documentation. |
| `backgroundimagedir` |  |  | `''` | No upstream documentation. |
| `latex_titles` |  |  | `True` | No upstream documentation. |

**Returns**

Returns the figure if return_fig=True. Otherwise the plot is displayed.

<a id="pcptprocessing-plot_schneider_chart"></a>

### `PCPTProcessing.plot_schneider_chart`

```python
plot_schneider_chart(
    start_depth=None,
    end_depth=None,
    layerchangetolerance=0,
    plot_height=700,
    plot_width=600,
    return_fig=False,
    plot_title=None,
    latex_titles=True,
)
```

Plots the normalised PCPT points in the Schneider (2008) chart to distinguish the soil type. The display can be limited to a specific depth range (by specifying `start_depth` and `end_depth`. The color coding is based on the layer.

The Schneider chart is especially useful to differentiate between different types of contractive fine-grained soil.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `start_depth` |  |  | `None` | No upstream documentation. |
| `end_depth` |  |  | `None` | No upstream documentation. |
| `layerchangetolerance` |  |  | `0` | No upstream documentation. |
| `plot_height` |  |  | `700` | No upstream documentation. |
| `plot_width` |  |  | `600` | No upstream documentation. |
| `return_fig` |  |  | `False` | No upstream documentation. |
| `plot_title` |  |  | `None` | No upstream documentation. |
| `latex_titles` |  |  | `True` | No upstream documentation. |

**Returns**

Returns the figure if return_fig=True. Otherwise the plot is displayed.

**References**

- Schneider, J.A., Randolph, M.F., Mayne, P.W. & Ramsey, N.R. 2008. Analysis of factors influencing soil classification using normalized piezocone tip resistance and pore pressure parameters. Journal Geotechnical and Geoenvironmental Engrg. 134 (11): 1569-1586.

<a id="pcptprocessing-apply_correlation"></a>

### `PCPTProcessing.apply_correlation`

```python
apply_correlation(name, outputs, apply_for_soiltypes='all', **kwargs)
```

Applies a correlation to the given PCPT data. The name of the correlation needs to be chosen from the following available correlations. Each correlation corresponds to a function in the `pcpt` module. By default, the correlation is applied to the entire depth range. However, a restriction on the soil types to which the correlation can be applied can be specified with the `apply_for_soiltypes` keyword argument. A list with the soil types for which the correlation needs to be applied can be provided.

- Ic Robertson and Wride (1998) (`behaviourindex_pcpt_robertsonwride`) - Calculation of soil behaviour type index from cone tip resistance and sleeve friction
- Isbt Robertson (2010) (`behaviourindex_pcpt_nonnormalised`) - Calculation of non-normalised soil behaviour type index from cone tip resistance and friction ratio
- Gmax Rix and Stokoe (1991) (`gmax_sand_rixstokoe`) - Calculation of small-strain shear modulus for uncemented silica sand from cone tip resistance and vertical effective stress
- Gmax Mayne and Rix (1993) (`gmax_clay_maynerix`) - Calculation of small-strain shear modulus for clay from cone tip resistance
- Dr Baldi et al (1986) - NC sand (`relativedensity_ncsand_baldi`) - Calculation of relative density of normally consolidated silica sand
- Dr Baldi et al (1986) - OC sand (`relativedensity_ocsand_baldi`) - Calculation of relative density of overconsolidated silica sand
- Dr Jamiolkowski et al (2003) (`relativedensity_sand_jamiolkowski`) - Calculation of relative density dry and saturated silica sand
- Friction angle Kulhawy and Mayne (1990) (`frictionangle_sand_kulhawymayne`) - Calculation of effective friction angle for sand
- Su Rad and Lunne (1988): (`undrainedshearstrength_clay_radlunne`) - Calculation of undrained shear strength for clay based on empirical cone factor Nk
- Friction angle Kleven (1986): (`frictionangle_overburden_kleven`) - Calculation of friction angle for North Sea sands at various stress levels and relative densities
- OCR Lunne (1989): (`ocr_cpt_lunne`) - Calculation of OCR for clay
- Sensitivity Rad and Lunne (1986): (`sensitivity_frictionratio_lunne`) - Calculation of sensitivity for clay
- Unit weight Mayne et al (2010): (`unitweight_mayne`) - Calculation of total unit weight
- Shear wave velocity Robertson and Cabal (2015): (`vs_ic_robertsoncabal`) - Calculation of shear wave velocity for all soil types
- K0 Mayne (2007) - sand: (`k0_sand_mayne`) - Calculation of coefficient of lateral earth pressure for sand
- Es Bellotti (1989) - sand: (`drainedsecantmodulus_sand_bellotti`) - Calculation of drained modulus at average strain of 0.1pct for sand

Note that certain correlations require either the calculation of normalised properties or application of preceding correlations

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `name` |  |  | required | Name of the correlation according to the list defined above |
| `outputs` |  |  | required | a dict of keys and values where keys are the same as the keys in the correlation, values are the table headers you want |
| `apply_for_soiltypes` |  |  | `'all'` | List with soil types to which the correlation needs the be applied. |
| `kwargs` |  |  |  | Optional keyword arguments for the correlation. |

**Returns**

Adds a column with key `outkey` to the dataframe with PCPT data

<a id="pcptprocessing-load_design_profile"></a>

### `PCPTProcessing.load_design_profile`

```python
load_design_profile(design_data)
```

Loads a design profile for the parameters available in the `data` attribute of the PCPTProcessing object. This design profile can then be plotted vs the PCPT data.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `design_data` | kPa |  | required | Pandas dataframe with design soil profile. Linear variation of numerical parameters is expected so for example, use columns `Su from ` and `Su to [kPa]` |

**Returns**

Sets the `designprofile` attribute of the PCPTProcessing object

<a id="pcptprocessing-plot_design_profile"></a>

### `PCPTProcessing.plot_design_profile`

```python
plot_design_profile(
    prop_keys,
    design_keys,
    plot_ranges,
    plot_ticks,
    z_range=None,
    z_tick=2,
    legend_titles=None,
    axis_titles=None,
    plot_height=700,
    plot_width=1000,
    colors=None,
    design_color='red',
    design_dash='dot',
    return_fig=False,
    plot_title=None,
    latex_titles=True,
)
```

Plots the soil and/or PCPT properties vs depth.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `prop_keys` |  |  | required | Tuple of tuples with the keys to be plotted. Keys in the same tuple are plotted on the same panel |
| `design_keys` | kPa |  | required | Tuple of tuples with the design profile keys to be plotted. Keys in the same tuple are plotted on the same panel (note that `()` is an empty tuple). The design keys need to be specified as for example `Gmax ` if the `designprofile` attribute contains keys `Gmax from [kPa]` and `Gmax to [kPa]` |
| `plot_ranges` |  |  | required | Tuple of tuples with ranges for the panels of the plot |
| `plot_ticks` |  |  | required | Tuple with tick intervals for the plot panels |
| `z_range` |  |  | `None` | Range for depths (optional, default is (0, maximum PCPT depth) |
| `z_tick` |  |  | `2` | Tick mark distance for PCPT |
| `legend_titles` |  |  | `None` | Tuple with entries to be used in the legend. If left blank, the keys are used |
| `axis_titles` |  |  | `None` | Tuple with entries to be used as axis labels. If left blank, the keys are used |
| `plot_height` |  |  | `700` | Height of the plot in pixels |
| `plot_width` |  |  | `1000` | Width of the plot in pixels |
| `colors` |  |  | `None` | Color list to be used in the plotting panels |
| `design_color` |  |  | `'red'` | Color to be used for the design lines |
| `design_dash` |  |  | `'dot'` | Dash style to be used for the design lines |
| `return_fig` |  |  | `False` | Boolean determining whether the figure is returned or the plot is generated; Default behaviour is to generate the plot. |
| `plot_title` |  |  | `None` | Plot title |
| `latex_titles` |  |  | `True` | Boolean determining whether axis titles should be shown as LaTeX (default = True) |

**Returns**

Returns the figure if return_fig=True. Otherwise the plot is displayed.

<a id="pcptprocessing-select_layering"></a>

### `PCPTProcessing.select_layering`

```python
select_layering(
    default_soil_type='Unknown',
    default_unit_weight=20,
    qc_range=(-10, 100),
    fs_range=(0, 1),
    u2_range=(-0.5, 2.5),
    plot_friction_ratio=False,
    rf_range=(0, 5),
    waterlevel=0,
    **kwargs,
)
```

Selects the layering for a CPT trace. The routine creates a LogPlotMatplotlib with which the layering can be selected interactively. Ensure that the plotting option is set to `%matplotlib qt` in Jupyter. Clicking below 0MPa in the cone tip resistance panel stops the selection. The SoilProfile with the layering is returned. The `Soil type` and `Total unit weight [kN/m3]` columns still need to be fine-tuned by the user after the selection process. Default values are assigned according to the `default_soil_type` and `default_unit_weight` arguments. The plotting ranges can be finetuned using the `qc_range`, `fs_range` and `u2_range` arguments. A hydrostatic line is plotted in the pore pressure panel. A water level (default=0m) can be added for plotting this line.

Keyword arguments for `LogPlotMatplotlib` can be specified by the user and are passed as **kwargs.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `default_soil_type` |  |  | `'Unknown'` | No upstream documentation. |
| `default_unit_weight` |  |  | `20` | No upstream documentation. |
| `qc_range` |  |  | `(-10, 100)` | No upstream documentation. |
| `fs_range` |  |  | `(0, 1)` | No upstream documentation. |
| `u2_range` |  |  | `(-0.5, 2.5)` | No upstream documentation. |
| `plot_friction_ratio` |  |  | `False` | No upstream documentation. |
| `rf_range` |  |  | `(0, 5)` | No upstream documentation. |
| `waterlevel` |  |  | `0` | No upstream documentation. |

<a id="pcptprocessing-to_json"></a>

### `PCPTProcessing.to_json`

```python
to_json(write_file=False, output_path=None)
```

Write the PCPT object to a JSON file. JSON can either be returned or a JSON file can be written.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `write_file` |  |  | `False` | Boolean determining whether a file is written or not (default=False). If True, a file is written to `output_path` |
| `output_path` |  |  | `None` | A valid path to the output .json file (include the file suffix). |

**Returns**

If no file is returned, the JSON containing the location and data of the PCPT is returned.

<a id="pcptprocessing-to_excel"></a>

### `PCPTProcessing.to_excel`

```python
to_excel(output_path)
```

Write the PCPT object to an Excel file. The Excel file contains multiple sheet for the location, layer data, cone properties and raw data.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `output_path` |  |  | required | A valid path to the output .xlsx file (include the file suffix). |

**Returns**

The file is written to the specified location

<a id="plot_longitudinal_profile"></a>

## `plot_longitudinal_profile`

```python
plot_longitudinal_profile(
    cpts=[],
    latlon=False,
    option='name',
    start=None,
    end=None,
    band=1000,
    extend_profile=False,
    plotmap=False,
    uniformcolor=None,
    prop='qc [MPa]',
    distance_unit='m',
    scale_factor=0.001,
    showfig=True,
    xaxis_layout=None,
    yaxis_layout=None,
    general_layout=None,
    legend_layout=None,
    show_annotations=True,
    mapbox_zoom=10,
)
```

Creates a longitudinal profile along selected CPTs. A line is drawn from the first (smallest distance from origin) to the last location (greatest distance from origin) and the plot of the selected parameter (`prop`) vs depth is projected onto this line.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `cpts` |  |  | `[]` | List with PCPTProcessing objects to be plotted |
| `latlon` |  |  | `False` | Boolean determining whether latitude and longitude are used or easting and northing in m (default=False for easting and northing in m) |
| `option` |  |  | `'name'` | Determines whether CPT names (`option='name'`) or tuples with coordinates (`option='coords'`) are used for the `start` and `end` arguments |
| `start` |  |  | `None` | CPT name for the starting point or tuple of coordinates. If a CPT name is used, the selected CPT must be contained in `cpts`. |
| `end` |  |  | `None` | CPT name for the end point or tuple of coordinates. If a CPT name is used, the selected CPT must be contained in `cpts`. |
| `band` |  |  | `1000` | Offset from the line connecting start and end points in which CPT are considered for plotting (default=1000m) |
| `extend_profile` |  |  | `False` | Boolean determining whether the profile needs to be extended beyond the start and end points (default=False) |
| `plotmap` |  |  | `False` | Boolean determining whether a map of locations needs to be plotted next to the profile (default=False) |
| `uniformcolor` |  |  | `None` | Uniform color to use for all CPT traces (default=None for different color for each trace) |
| `prop` | MPa |  | `'qc [MPa]'` | Selected property for plotting (default='qc ') |
| `distance_unit` |  |  | `'m'` | Unit for coordinates and elevation (default='m') |
| `scale_factor` |  |  | `0.001` | Scale factor for the property (default=0.001) |
| `showfig` |  |  | `True` | Boolean determining whether the figure is shown (default=True) |
| `xaxis_layout` |  |  | `None` | Dictionary with layout for the xaxis (default=None) |
| `yaxis_layout` |  |  | `None` | Dictionary with layout for the xaxis (default=None) |
| `general_layout` |  |  | `None` | Dictionary with general layout options (default=None) |
| `legend_layout` |  |  | `None` | Dictionary with legend layout options (default=None) |
| `show_annotations` |  |  | `True` | Boolean determining whether annotations need to be shown (default=True) |
| `mapbox_zoom` |  |  | `10` | Zoom factor for map (if plotted, default=10) |

**Returns**

Plotly figure object

<a id="plot_combined_longitudinal_profile"></a>

## `plot_combined_longitudinal_profile`

```python
plot_combined_longitudinal_profile(
    cpts=[],
    profiles=[],
    latlon=False,
    option='name',
    start=None,
    end=None,
    band=1000,
    extend_profile=False,
    plotmap=False,
    fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green', 'ROCK': 'grey'},
    uniformcolor=None,
    opacity=1,
    logwidth=1,
    prop='qc [MPa]',
    distance_unit='m',
    scale_factor=0.001,
    showfig=True,
    xaxis_layout=None,
    yaxis_layout=None,
    general_layout=None,
    legend_layout=None,
    show_annotations=True,
)
```

Creates a longitudinal profile along selected CPTs and `SoilProfile` objects. A line is drawn from the first to the last location and the plot of the selected parameter (`prop`) vs depth is projected onto this line.

This function also adds `SoilProfile` objects to the plot through mini-logs.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `cpts` |  |  | `[]` | List with PCPTProcessing objects to be plotted |
| `profiles` |  |  | `[]` | List with SoilProfile objects for which a log needs to be plotted |
| `latlon` |  |  | `False` | Boolean determining whether latitude and longitude are used or easting and northing in m (default=False for easting and northing in m) |
| `option` |  |  | `'name'` | Determines whether CPT names (`option='name'`) or tuples with coordinates (`option='coords'`) are used for the `start` and `end` arguments |
| `start` |  |  | `None` | CPT name for the starting point or tuple of coordinates. If a CPT name is used, the selected CPT must be contained in `cpts`. |
| `end` |  |  | `None` | CPT name for the end point or tuple of coordinates. If a CPT name is used, the selected CPT must be contained in `cpts`. |
| `band` |  |  | `1000` | Offset from the line connecting start and end points in which CPT are considered for plotting (default=1000m) |
| `extend_profile` |  |  | `False` | Boolean determining whether the profile needs to be extended beyond the start and end points (default=False) |
| `plotmap` |  |  | `False` | Boolean determining whether a map of locations needs to be plotted next to the profile (default=False) |
| `fillcolordict` |  |  | `{'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green', 'ROCK': 'grey'}` | Dictionary with fill colours (default yellow for 'SAND', brown from 'CLAY' and grey for 'ROCK') |
| `uniformcolor` |  |  | `None` | Uniform color to use for all CPT traces (default=None for different color for each trace) |
| `opacity` |  |  | `1` | Opacity of the layers (default = 1 for non-transparent behaviour) |
| `logwidth` |  |  | `1` | Width of the soil logs as an absolute value (default = 1) |
| `prop` | MPa |  | `'qc [MPa]'` | Selected property for plotting (default='qc ') |
| `distance_unit` |  |  | `'m'` | Unit for coordinates and elevation (default='m') |
| `scale_factor` |  |  | `0.001` | Scale factor for the property (default=0.001) |
| `showfig` |  |  | `True` | Boolean determining whether the figure is shown (default=True) |
| `xaxis_layout` |  |  | `None` | Dictionary with layout for the xaxis (default=None) |
| `yaxis_layout` |  |  | `None` | Dictionary with layout for the xaxis (default=None) |
| `general_layout` |  |  | `None` | Dictionary with general layout options (default=None) |
| `legend_layout` |  |  | `None` | Dictionary with legend layout options (default=None) |
| `show_annotations` |  |  | `True` | Boolean determining whether annotations need to be shown (default=True) |

**Returns**

Plotly figure object
