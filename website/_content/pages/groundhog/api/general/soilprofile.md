---
title: soilprofile
slug: groundhog/api/general/soilprofile
section: Groundhog API Reference
description: 'API reference for groundhog.general.soilprofile: 6 functions, 2 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/general/soilprofile.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.general.soilprofile
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/general/soilprofiles.html
geocore_available: true
geocore_functions:
- CalculationGrid
- SoilProfile
---

Module `groundhog.general.soilprofile` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/general/soilprofile.py).

Upstream documentation: [Soil profiles and gridscd](https://groundhog.readthedocs.io/en/main/general/soilprofiles.html).

**Classes:** [`SoilProfile`](#soilprofile), [`CalculationGrid`](#calculationgrid)

**Functions:** [`create_blank_soilprofile`](#create_blank_soilprofile), [`read_excel`](#read_excel), [`profile_from_dataframe`](#profile_from_dataframe), [`plot_fence_diagram`](#plot_fence_diagram), [`retrieve_geological_profile_dov`](#retrieve_geological_profile_dov), [`retrieve_geological_profile_bro`](#retrieve_geological_profile_bro)

<a id="soilprofile"></a>

## class `SoilProfile`

<span class="gc-badge gc-available" data-geocore-function="SoilProfile">Available in GeoCore</span> [General and utility functions › Soil profiles and grids › SoilProfile](/docs/geocore/using/modules#soilprofile)

```python
SoilProfile(*args, **kwargs)
```

A SoilProfile object is a Pandas dataframe with specific functionality for geotechnical calculations. There is a column syntax requirement in which the columns with the top and bottom depth need to be defined for each layer. By default 'Depth from [m]' and 'Depth to [m]' are expected but this can be customised.

<a id="soilprofile-__init__"></a>

### `SoilProfile.__init__`

```python
__init__(*args, **kwargs)
```

Overrides the init method of a dataframe to check the correctness of the layering and to set the depth column names.

<a id="soilprofile-set_depthcolumn_name"></a>

### `SoilProfile.set_depthcolumn_name`

```python
set_depthcolumn_name(name='Depth', unit='m')
```

No upstream documentation.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `name` |  |  | `'Depth'` | No upstream documentation. |
| `unit` |  |  | `'m'` | No upstream documentation. |

<a id="soilprofile-convert_depth_reference"></a>

### `SoilProfile.convert_depth_reference`

```python
convert_depth_reference(newname='Depth', newunit='m', multiplier=1)
```

Converts the depth reference for a soil profile between one set of units (e.g. ft) to another (e.g. m)

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `newname` |  |  | `'Depth'` | New name for the depth reference (default='Depth') |
| `newunit` |  |  | `'m'` | Name of the new unit (default=m) |
| `multiplier` |  |  | `1` | Multiplier to go from old to new depth unit (e.g. 0.3 to go from ft to m) |

**Returns**

<a id="soilprofile-check_profile"></a>

### `SoilProfile.check_profile`

```python
check_profile()
```

Check if the SoilProfile meets the requirements for calculations

<a id="soilprofile-set_position"></a>

### `SoilProfile.set_position`

```python
set_position(easting, northing, elevation, srid=4326, datum='mLAT')
```

Sets the position of a soil profile top in a given coordinate system.

By default, srid 4326 is used which means easting is longitude and northing is latitude.

The elevation is referenced to a chart datum for which mLAT (Lowest Astronomical Tide) is the default.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `easting` |  |  | required | X-coordinate of the CPT position |
| `northing` |  |  | required | Y-coordinate of the CPT position |
| `elevation` |  |  | required | Elevation of the CPT position |
| `srid` |  |  | `4326` | SRID of the coordinate system (see http://epsg.io) |
| `datum` |  |  | `'mLAT'` | Chart datum used for the elevation |

**Returns**

Sets the corresponding attributes of the `PCPTProcessing` object

<a id="soilprofile-layer_transitions"></a>

### `SoilProfile.layer_transitions`

```python
layer_transitions(include_top=False, include_bottom=False)
```

Returns a Numpy array with the layer transition depths. Use the booleans include_top and include_bottom to in/exclude the top and bottom of the profile

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `include_top` |  |  | `False` | No upstream documentation. |
| `include_bottom` |  |  | `False` | No upstream documentation. |

<a id="soilprofile-adjust_layertransition"></a>

### `SoilProfile.adjust_layertransition`

```python
adjust_layertransition(currentdepth, newdepth, tolerance=0.001)
```

Adjusts the depth of a layer transition.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `currentdepth` |  |  | required | Current depth of the layer transition |
| `newdepth` |  |  | required | Desired new depth of the layer transition |
| `tolerance` |  |  | `0.001` | Offset above and below `currentdepth` in which a layer transition is sought (to cope with number precision issues) |

<a id="soilprofile-calculate_layerthickness"></a>

### `SoilProfile.calculate_layerthickness`

```python
calculate_layerthickness(layerthicknesscol='Layer thickness [m]')
```

Adds a column with the layer thickness to the soil profile

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `layerthicknesscol` |  |  | `'Layer thickness [m]'` | Name of the column with the layer thickness |

**Returns**

Adds a column with the layer thickness

<a id="soilprofile-calculate_center"></a>

### `SoilProfile.calculate_center`

```python
calculate_center(layercentercol='Depth center [m]')
```

Adds a column with the layer center depth to the soil profile

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `layercentercol` |  |  | `'Depth center [m]'` | Name of the column with the layer center |

**Returns**

Adds a column with the layer center

<a id="soilprofile-soil_parameters"></a>

### `SoilProfile.soil_parameters`

```python
soil_parameters(condense_linear=True)
```

Returns a list of soil parameters available in the soil profile. Soil parameters with linear variations are returned as a single soil parameter when the boolean `condense_linear` is set to True

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `condense_linear` |  |  | `True` | No upstream documentation. |

**Returns**

Returns a list of the soil parameters in the SoilProfile

<a id="soilprofile-numerical_soil_parameters"></a>

### `SoilProfile.numerical_soil_parameters`

```python
numerical_soil_parameters(condense_linear=True)
```

Returns a list of numerical soil parameters available in the soil profile. Numerical soil parameters have units between square brackets. Soil parameters with linear variations are returned as a single soil parameter when the boolean `condense_linear` is set to True

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `condense_linear` |  |  | `True` | No upstream documentation. |

**Returns**

Returns a list with the numerical soil parameters in the SoilProfile

<a id="soilprofile-string_soil_parameters"></a>

### `SoilProfile.string_soil_parameters`

```python
string_soil_parameters()
```

Returns a list of string soil parameters available in the soil profile. String soil parameters have no square brackets.

**Returns**

Returns a list with the string soil parameters in the SoilProfile

<a id="soilprofile-check_linear_variation"></a>

### `SoilProfile.check_linear_variation`

```python
check_linear_variation(parameter)
```

Check if a soil parameter varies linearly or not.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `parameter` |  |  | required | No upstream documentation. |

**Returns**

Boolean determining whether a soil parameter has a linear variation or not

<a id="soilprofile-insert_layer_transition"></a>

### `SoilProfile.insert_layer_transition`

```python
insert_layer_transition(depth)
```

Inserts a layer transition in the soil profile at a specific depth The profile layer is simply split and the properties of the given layer are assigned to the new layers above and below the transition. For linearly varying parameters, an interpolation is performed.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `depth` |  |  | required | No upstream documentation. |

<a id="soilprofile-convert_depth_sign"></a>

### `SoilProfile.convert_depth_sign`

```python
convert_depth_sign()
```

Inverts the sign of the depth from and depth to column. This function is useful when the profiles needs to be examined relative to LAT

<a id="soilprofile-shift_depths"></a>

### `SoilProfile.shift_depths`

```python
shift_depths(offset)
```

Shifts all layer coordinates downward or upward, depending on the sign of the given offset. The offset is added to the given coordinates

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `offset` |  |  | required | No upstream documentation. |

<a id="soilprofile-soilparameter_series"></a>

### `SoilProfile.soilparameter_series`

```python
soilparameter_series(parameter)
```

Returns two lists (depths and corresponding parameter values) for plotting of a soil parameter vs depth. The routine first checks whether a valid parameter is provided. The lists are formatted such that variations at a layer interface are adequately plotted.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `parameter` |  |  | required | A valid soil parameter with units |

**Returns**

Two lists (depths and corresponding parameter values)

<a id="soilprofile-map_soilprofile"></a>

### `SoilProfile.map_soilprofile`

```python
map_soilprofile(
    nodalcoords,
    target_depthkey='z [m]',
    keys_to_map=None,
    invert_sign=False,
    offset=0,
    include_layertransitions=False,
)
```

Maps the soilprofile to a grid. The depth coordinates to the grid are specified in a list or Numpy array (`nodalcoords`). The depth coordinates should be strictly ascending (no duplicates) and the minimum and maximum should be contained inside the soil profile bounds. Layer transitions can be included in the grid when `include_layertransitions=True`. All soil parameters are interpolated onto this grid.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `nodalcoords` |  |  | required | List or Numpy array with the nodal coordinates of the grid |
| `target_depthkey` |  |  | `'z [m]'` | Name of the depth key in the resulting dataframe |
| `keys_to_map` |  |  | `None` | List with the soilprofile keys to map |
| `invert_sign` |  |  | `False` | Boolean determining whether to invert the sign after interpolation |
| `offset` |  |  | `0` | Offset by which the depth is shifted (added to the depth after sign conversion) |
| `include_layertransitions` |  |  | `False` | Boolean to determine whether the layer transitions needs to be included in the grid (default=False) |

**Returns**

Returns a dataframe with the full grid with soil parameters

<a id="soilprofile-plot_profile"></a>

### `SoilProfile.plot_profile`

```python
plot_profile(parameters, soiltypecolumn='Soil type', **kwargs)
```

Generates a Plotly plot of the soil parameters vs depth. The panel on which the parameter is plotted is determined by how the parameters are passed to the function.

`parameters=(('qc [MPa]',), ('Dr [%]',))` will plot cone resistance in panel 1 and relative density in panel 2

`parameters=(('qc [MPa]', 'qt [MPa]'), ('Dr [%]'))` will plot cone resistance and total cone resistance in panel 1 and relative density in panel 2

A column wihh the soil type is expected for the plotting of the log

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `parameters` |  |  | required | List of parameters tuples for plotting |
| `soiltypecolumn` |  |  | `'Soil type'` | No upstream documentation. |
| `kwargs` |  |  |  | Additional keyword arguments for the `plot_with_log` function in the `general.plotting` module |

**Returns**

Plotly plot with mini-log and parameter values

<a id="soilprofile-selection_soilparameter"></a>

### `SoilProfile.selection_soilparameter`

```python
selection_soilparameter(parameter, depths, values, rule='mean', linearvariation=False)
```

Function for automatic selection of a soil parameters in the layers of a soil profile based an a list of provided values. The selection can either be done for a constant value in the layer or a linear variation over the layer. Selection of a minimum, mean or average trend can be performed using the `rule` keyword

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `parameter` |  |  | required | Name of the parameter being selected (including unit in square brackets) |
| `depths` |  |  | required | Depths at which a measurement is available (list or Numpy array) |
| `values` |  |  | required | Values corresponding to the given depths (list or Numpy array) |
| `rule` |  |  | `'mean'` | Which rule to use for the selection (select from `min`, `mean` and `max` |
| `linearvariation` |  |  | `False` | Boolean determining whether a linear variation needs to happen over the layer or not |

**Returns**

Adds one (constant value) or two (linear variation) columns to the dataframe

<a id="soilprofile-merge_layers"></a>

### `SoilProfile.merge_layers`

```python
merge_layers(layer_ids, keep='top')
```

Merges two layers. Depending on the `keep` keyword, the top or bottom properties are retained for the merged layer

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `layer_ids` |  |  | required | List with the 2 IDs of the layers to be merged |
| `keep` |  |  | `'top'` | String determining whether to retain the parameters of the top or bottom layer for the merged layer (select 'top' or 'bottom') |

**Returns**

Reduces the number of layers of the `SoilProfile` object

<a id="soilprofile-merge_soiltypes"></a>

### `SoilProfile.merge_soiltypes`

```python
merge_soiltypes()
```

Merge adjacent layers with same soil type

<a id="soilprofile-remove_parameter"></a>

### `SoilProfile.remove_parameter`

```python
remove_parameter(parameter)
```

Removes a soil parameter from the dataframe

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `parameter` | unit |  | required | Soil parameter to remove. For linear variations, simple use the expression `parameter `. The routine takes care of removing both the 'to' and 'from' columns |

**Returns**

Removes the requested soil parameter from the `SoilProfile` objec

<a id="soilprofile-convert_to_constant"></a>

### `SoilProfile.convert_to_constant`

```python
convert_to_constant(parameter, rule='mean')
```

Converts a linearly varying soil parameter to a parameter with constant value.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `parameter` | kN/m3 |  | required | Soil parameter to convert. Specify `Total unit weight ` if the `SoilProfile` contains columns `Total unit weight from [kN/m3]` and `Total unit weight to [kN/m3]`. |
| `rule` | 'min', 'mean', 'max' |  | `'mean'` | Select from ` ` to convert the linear variation to a constant value (default='mean') |

**Returns**

Creates a column for the soil parameter with constant value and removes the column with the linear variation

<a id="soilprofile-calculate_parameter_center"></a>

### `SoilProfile.calculate_parameter_center`

```python
calculate_parameter_center(parameter, suffix='center')
```

Calculates the value of a soil parameter at the center. The soil parameter needs to be a linearly varying numerical soil parameter.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `parameter` |  |  | required | Numerical soil parameter for which the value at the center needs to be computed. |
| `suffix` |  |  | `'center'` | Suffix to use instead of `from` or `to` |

**Returns**

Adds an extra column with `from` or `to` in the column name replaced by the chosen suffix

<a id="soilprofile-cut_profile"></a>

### `SoilProfile.cut_profile`

```python
cut_profile(top_depth, bottom_depth)
```

Returns a deep copy of the `SoilProfile` between the specified bounds

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `top_depth` |  |  | required | Top depth for cutting |
| `bottom_depth` |  |  | required | Bottom depth for cutting |

**Returns**

Deep copy of the `SoilProfile` between the specified bounds

<a id="soilprofile-depth_integration"></a>

### `SoilProfile.depth_integration`

```python
depth_integration(parameter, outputparameter, start_value=0)
```

Integrate a certain parameter vs depth (e.g. unit weight to obtain vertical stress) Note: This routine is only implemented for parameters with a constant value in the layer.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `parameter` |  |  | required | Parameter to be integrated |
| `outputparameter` |  |  | required | Name of the output parameter (with units) |
| `start_value` |  |  | `0` | Value at the top of the profile (default=0) |

**Returns**

Adds a column to the `SoilProfile` object for the integrated parameter

<a id="soilprofile-calculate_overburden"></a>

### `SoilProfile.calculate_overburden`

```python
calculate_overburden(
    waterlevel=0,
    waterunitweight=10,
    initial_vertical_total_stress=0,
    totalunitweightcolumn='Total unit weight [kN/m3]',
    effectiveunitweightcolumn='Effective unit weight [kN/m3]',
    waterunitweightcolumn='Water unit weight [kN/m3]',
    totalverticalstresscolumn='Vertical total stress [kPa]',
    effectiveverticalstresscolumn='Vertical effective stress [kPa]',
    hydrostaticpressurecolumn='Hydrostatic pressure [kPa]',
)
```

Calculates the overburden pressure (total and effective) for a `SoilProfile` object. The `SoilProfile` object needs to contain a column with the total unit weight. By default, this is `Total unit weight [kN/m3]`. If the water level does not correspond with a layer interface, an additional layer interface is created. Total and effective unit weights are calculated for each layer and the method `depth_integration` is used to calculate the total vertical stress, effective vertical stress and hydrostatic pressure.

Note that vertical stress calculations in other units are possible, but the water unit weight then needs to be specified in consistent units.

An initial value can be added to the total vertical stress to simulate the effect of e.g. surcharging.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `waterlevel` | m |  | `0` | Water level (default 0m) |
| `waterunitweight` | kN/m3 |  | `10` | Unit weight of the pore water (default=10kN/m3) |
| `initial_vertical_total_stress` | kPa |  | `0` | Initial value of vertical total stress (default=0kPa) |
| `totalunitweightcolumn` | kN/m3 |  | `'Total unit weight [kN/m3]'` | Column name containing total unit weights (default='Total unit weight ' |
| `effectiveunitweightcolumn` |  |  | `'Effective unit weight [kN/m3]'` | No upstream documentation. |
| `waterunitweightcolumn` | kN/m3 |  | `'Water unit weight [kN/m3]'` | Output column with the water unit weight (default='Water unit weight ') |
| `totalverticalstresscolumn` | kPa |  | `'Vertical total stress [kPa]'` | Total vertical stress column name (default='Total vertical stress ') |
| `effectiveverticalstresscolumn` | kPa |  | `'Vertical effective stress [kPa]'` | Effective vertical stress column name (default='Vertical effective stress ') |
| `hydrostaticpressurecolumn` | kPa |  | `'Hydrostatic pressure [kPa]'` | Hydrostatic pressure column name (default='Hydrostatic pressure ') |

**Returns**

Adds the column names from `totalverticalstresscolumn`, `effectiveverticalstresscolumn` and `hydrostaticpressurecolumn` to the `SoilProfile` object

<a id="soilprofile-applyfunction"></a>

### `SoilProfile.applyfunction`

```python
applyfunction(function, resultkey, outputkey, parametermapping={}, **kwargs)
```

Applies a groundhog function to a soil profile. The function is applied to each row of the soilprofile. The result is stored in a column with name `output`. `resultkey` determines which key of the function output dictionary is used as the result.

The parameters of the function are mapped to columns of the soil profile using the parametermapping dictionary. The keys of this dictionary are the function arguments, the values are the corresponding columns of the soilprofile. For parameters with linear variation, this method only needs to be applied once and the soil parameter name (without from or to) needs to be supplied in the `parametermapping` dictionary.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `function` |  |  | required | Function to be applied |
| `resultkey` |  |  | required | Column name for the result (for parameters with linear variation, two result columns are created) |
| `outputkey` |  |  | required | The key of the function output dictionary to be used for the result |
| `parametermapping` |  |  | `{}` | Dictionary mapping parameters of the function to column names |
| `applyatcenter` |  |  |  | Boolean determining whether the function needs to be applied at the center of the layer for a linearly varying parameter. A single output column will then be returned (default=False). |
| `kwargs` |  |  |  | Additional keyword arguments of the function which are not mapped to soil profile columns |

**Returns**

<a id="soilprofile-parameter_at_depth"></a>

### `SoilProfile.parameter_at_depth`

```python
parameter_at_depth(depth, parameter, shallowest=True)
```

Calculates the value for one of the `SoilProfile` parameters at a selected depth

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `depth` | m |  | required | Selected depth |
| `parameter` |  |  | required | String or Numerical soil parameter (linear interpolation for linearly varying parameters) |
| `shallowest` |  |  | `True` | Boolean determining whether at a layer interface, the shallowest value needs to be used (default=True). |

**Returns**

The value of the parameter at the selected depth

<a id="soilprofile-select_soiltype"></a>

### `SoilProfile.select_soiltype`

```python
select_soiltype(robertson=True)
```

Method for assigning soil types to layers. User input is expected. By default, this method works with Robertson soil types (`robertson=True`) which maps numbers from the Robertson charts to soil types and puts these descriptions in the `'Soil Type'` column. When `robertson=False`, the user can just type a self-chosen soil type name.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `robertson` |  |  | `True` | No upstream documentation. |

<a id="calculationgrid"></a>

## class `CalculationGrid`

<span class="gc-badge gc-available" data-geocore-function="CalculationGrid">Available in GeoCore</span> [General and utility functions › Soil profiles and grids › CalculationGrid](/docs/geocore/using/modules#calculationgrid)

```python
CalculationGrid(soilprofile, dz, custom_nodes=None, include_layertransitions=True)
```

A `CalculationGrid` is an object which consist of a dataframe with nodes `.nodes` and a dataframe with elements `.elements`. Properties of the soil profile are mapped to the nodes and the elements to allow subsequent calculation. At layer transition nodes, the properties of the layer below are always assigned to the node.

<a id="calculationgrid-__init__"></a>

### `CalculationGrid.__init__`

```python
__init__(soilprofile, dz, custom_nodes=None, include_layertransitions=True)
```

Initializes the `CalculationGrid` object from a `SoilProfile` object. A nodes offset `dz` needs to be specified. Additional nodes are inserted at layer transitions by default (`include_layertransitions=True`). The user can also specify a NumPy array with custom_nodes (None by default). After initialization, the dataframes of nodal and elemental information are created. For properties varying linearly across a layer, the value of the property at the element center is also calculated and is given the name of the parameter (without from and to).

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `soilprofile` |  |  | required | No upstream documentation. |
| `dz` |  |  | required | No upstream documentation. |
| `custom_nodes` |  |  | `None` | No upstream documentation. |
| `include_layertransitions` |  |  | `True` | No upstream documentation. |

<a id="calculationgrid-set_nodes"></a>

### `CalculationGrid.set_nodes`

```python
set_nodes(dz, custom_nodes=None, include_layertransitions=True, **kwargs)
```

No upstream documentation.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `dz` |  |  | required | No upstream documentation. |
| `custom_nodes` |  |  | `None` | No upstream documentation. |
| `include_layertransitions` |  |  | `True` | No upstream documentation. |

<a id="calculationgrid-set_elements"></a>

### `CalculationGrid.set_elements`

```python
set_elements()
```

Create a dataframe with elements. Each element has a top and bottom node. The soil property value at bottom and top are calculated, as well as the values at the center of the element.

<a id="calculationgrid-soilparameter_series"></a>

### `CalculationGrid.soilparameter_series`

```python
soilparameter_series(parameter, ignore_linearvariation=False)
```

Returns two lists (depths and corresponding parameter values) for plotting of a soil parameter vs depth. The routine first checks whether a valid parameter is provided. The lists are formatted such that variations at a layer interface are adequately plotted.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `parameter` |  |  | required | A valid soil parameter with units |
| `ignore_linearvariation` |  |  | `False` | Boolean determining if linear variations need to be ignored |

**Returns**

Two lists (depths and corresponding parameter values)

<a id="create_blank_soilprofile"></a>

## `create_blank_soilprofile`

```python
create_blank_soilprofile(max_depth, min_depth=0, soiltype='Unknown', bulkunitweight=20)
```

Creates a SoilProfile object with a single layer. By default the soil type is set to `'Unknown'` and the bulk unit weight to 20kN/m3.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `max_depth` | m |  | required | Maximum depth for the SoilProfile object |
| `min_depth` | m |  | `0` | Minimum depth for the SoilProfile object |
| `soiltype` |  |  | `'Unknown'` | Soil type for the layer |
| `bulkunitweight` | kN/m3 |  | `20` | Bulk unit weight for the layer |

<a id="read_excel"></a>

## `read_excel`

```python
read_excel(
    path,
    title='',
    depth_key='Depth',
    unit='m',
    column_mapping={},
    depth_multiplier=1,
    **kwargs,
)
```

The method to read from Excel needs to be redefined for SoilProfile objects. The method allows for different depth keys (using the 'depth_key' and 'unit' keyword arguments Columns can also be renamed using the 'column_mapping' dictionary. The keys in this dictionary are the old column names and the values are the new column names.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `path` |  |  | required | No upstream documentation. |
| `title` |  |  | `''` | No upstream documentation. |
| `depth_key` |  |  | `'Depth'` | No upstream documentation. |
| `unit` |  |  | `'m'` | No upstream documentation. |
| `column_mapping` |  |  | `{}` | No upstream documentation. |
| `depth_multiplier` |  |  | `1` | No upstream documentation. |

<a id="profile_from_dataframe"></a>

## `profile_from_dataframe`

```python
profile_from_dataframe(df, title='', depth_key='Depth', unit='m', column_mapping={})
```

Creates a soil profile from a Pandas dataframe

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `df` |  |  | required | Dataframe to be converted |
| `title` |  |  | `''` | No upstream documentation. |
| `depth_key` |  |  | `'Depth'` | Column key to be used for depth (default = 'Depth') |
| `unit` |  |  | `'m'` | Unit for the depth (default = 'm') |
| `column_mapping` |  |  | `{}` | Dictionary for renaming columns. The keys in this dictionary are the old column names and the values are the new column names. |

**Returns**

`SoilProfile` object created as a deep copy of the dataframe

<a id="plot_fence_diagram"></a>

## `plot_fence_diagram`

```python
plot_fence_diagram(
    profiles=[],
    latlon=False,
    option='name',
    start=None,
    end=None,
    band=1000,
    extend_profile=False,
    soiltypekey='Soil type',
    plotmap=False,
    fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green', 'ROCK': 'grey'},
    opacity=1,
    logwidth=1,
    distance_unit='m',
    return_layers=False,
    showfig=True,
    xaxis_layout=None,
    yaxis_layout=None,
    general_layout=None,
    show_annotations=True,
)
```

Creates a longitudinal profile along selected soil profiles. A line is drawn from the first (smallest distance from origin) to the last location (greatest distance from origin) and the plot of the mini-logs with soil types is projected onto this line.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `profiles` |  |  | `[]` | List with SoilProfile objects for which a log needs to be plotted |
| `latlon` |  |  | `False` | Boolean defining whether coordinates are specified in latitude and longitude (defaulte=False). If this is the case, offsets are calculated using the `pyproj` package |
| `option` |  |  | `'name'` | Determines whether soil profile names (`option='name'`) or tuples with coordinates (`option='coords'`) are used for the `start` and `end` arguments |
| `start` |  |  | `None` | Soil profile name for the starting point or tuple of coordinates. If a SoilProfile name is used, the selected SoilProfile must be contained in `profiles`. |
| `end` |  |  | `None` | Soil profile name for the end point or tuple of coordinates. If a SoilProfile name is used, the selected SoilProfile must be contained in `profiles`. |
| `band` |  |  | `1000` | Offset from the line connecting start and end points in which soil profiles are considered for plotting (default=1000m) |
| `extend_profile` |  |  | `False` | Boolean determining whether the profile needs to be extended beyond the start and end points (default=False) |
| `soiltypekey` |  |  | `'Soil type'` | Key for the soil type in the dataframes with layering (default="Soil type") |
| `plotmap` |  |  | `False` | Boolean determining whether a map of locations needs to be plotted next to the profile (default=False) |
| `fillcolordict` |  |  | `{'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green', 'ROCK': 'grey'}` | Dictionary with fill colours (default yellow for 'SAND', brown from 'CLAY' and grey for 'ROCK') |
| `opacity` |  |  | `1` | Opacity of the layers (default = 1 for non-transparent behaviour) |
| `logwidth` |  |  | `1` | Width of the soil logs as an absolute value (default = 1) |
| `distance_unit` |  |  | `'m'` | Unit for coordinates and elevation (default='m') |
| `return_layers` |  |  | `False` | Boolean determining whether layers need to be returned. These layers can be used to updata another plot (e.g. CPT longitudinal profile) (default=False) |
| `showfig` |  |  | `True` | Boolean determining whether the figure is shown (default=True) |
| `xaxis_layout` |  |  | `None` | Dictionary with layout for the xaxis (default=None) |
| `yaxis_layout` |  |  | `None` | Dictionary with layout for the xaxis (default=None) |
| `general_layout` |  |  | `None` | Dictionary with general layout options |
| `show_annotations` |  |  | `True` | Boolean determining whether annotations need to be shown (default=True) |

**Returns**

Plotly figure object

<a id="retrieve_geological_profile_dov"></a>

## `retrieve_geological_profile_dov`

```python
retrieve_geological_profile_dov(x, y, model='g3dv3_L', namecutoff=30, **kwargs)
```

Retrieves a geological profile at a location with given coordinates (x,y Lambert L72). The routine creates a soil profile, starting from the ground surface, with depth increasing downwards. The fillcolors for the geological layers are also returned.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `x` |  |  | required | X-coordinate of the location in Lambert72 coordinates |
| `y` |  |  | required | Y-coordinate of the location in Lambert72 coordinates |
| `model` |  |  | `'g3dv3_L'` | Type of model for stratigraphic information (see https://www.milieuinfo.be/confluence/display/DDOV/Virtuele+Boring+-+Virtueel+Profiel+API) |
| `namecutoff` |  |  | `30` | Maximum number of characters for the geological units |

**Returns**

soilprofile, fillcolors

<a id="retrieve_geological_profile_bro"></a>

## `retrieve_geological_profile_bro`

```python
retrieve_geological_profile_bro(x, y, zmin, zmax, model='lithok', namecutoff=30)
```

Retrieves a geological profile at a location with given coordinates (x,y EPSG 28992). The routine creates a soil profile, starting from the ground surface, with depth increasing downwards. The fillcolors for the geological layers are also returned.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `x` |  |  | required | X-coordinate of the location in EPSG 28992 (RD) coordinates |
| `y` |  |  | required | Y-coordinate of the location in EPSG 28992 (RD) coordinates |
| `zmin` |  |  | required | Minimum z coordinate in NAP |
| `zmax` |  |  | required | Maximum z coordinate in NAP |
| `model` |  |  | `'lithok'` | Type of model for stratigraphic information (choose from `'lithok'` or `'strat'`) |
| `namecutoff` |  |  | `30` | Maximum number of characters for the geological units |

**Returns**

soilprofile, fillcolors_plotly, fillcolors_matplotlib
