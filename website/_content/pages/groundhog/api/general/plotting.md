---
title: Plotting
slug: groundhog/api/general/plotting
section: Groundhog API Reference
description: 'API reference for groundhog.general.plotting: 2 functions, 2 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/general/plotting.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.general.plotting
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/general/plotting.html
geocore_available: true
geocore_functions:
- LogPlot
- LogPlotMatplotlib
- plot_with_log
---

Module `groundhog.general.plotting` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/general/plotting.py).

Upstream documentation: [Plotting](https://groundhog.readthedocs.io/en/main/general/plotting.html).

**Classes:** [`LogPlot`](#logplot), [`LogPlotMatplotlib`](#logplotmatplotlib)

**Functions:** [`plot_with_log`](#plot_with_log), [`peak_picker`](#peak_picker)

<a id="logplot"></a>

## class `LogPlot`

<span class="gc-badge gc-available" data-geocore-function="LogPlot">Available in GeoCore</span> [General and utility functions › Plotting › LogPlot](/docs/geocore/using/modules#logplot)

```python
LogPlot(
    soilprofile,
    secondaryprofile=None,
    no_panels=1,
    logwidth=0.05,
    fillcolordict={'Sand': 'yellow', 'Clay': 'brown', 'Rock': 'grey'},
    soiltypelegend=True,
    soiltypecolumn='Soil type',
    line_width=1,
    **kwargs,
)
```

Class for planneled plots with a minilog on the side.

<a id="logplot-__init__"></a>

### `LogPlot.__init__`

```python
__init__(
    soilprofile,
    secondaryprofile=None,
    no_panels=1,
    logwidth=0.05,
    fillcolordict={'Sand': 'yellow', 'Clay': 'brown', 'Rock': 'grey'},
    soiltypelegend=True,
    soiltypecolumn='Soil type',
    line_width=1,
    **kwargs,
)
```

Initializes a figure with a minilog on the side.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `soilprofile` |  |  | required | Soilprofile used for the minilog |
| `secondaryprofile` |  |  | `None` | A second Soilprofile used as an additional minilog. Note that only the `SoilProfile` provided in `soilprofile` will get update if layers and parameters are selected. |
| `no_panels` |  |  | `1` | Number of panels |
| `logwidth` |  |  | `0.05` | Width of the minilog as a ratio to the total width of the figure (default=0.05) |
| `fillcolordict` |  |  | `{'Sand': 'yellow', 'Clay': 'brown', 'Rock': 'grey'}` | Dictionary with fill colors for each of the soil types. Every unique `Soil type` needs to have a corresponding color. Default: `{"Sand": 'yellow', "Clay": 'brown', 'Rock': 'grey'}` |
| `soiltypelegend` |  |  | `True` | Boolean determining whether legend entries need to be shown for the soil types in the log |
| `soiltypecolumn` |  |  | `'Soil type'` | Column name used to identify the soil type. The entries in this column need to correspond to keys in `fillcolordict` |
| `line_width` |  |  | `1` | Line width for the boundary between layers |
| `kwargs` |  |  |  | Optional keyword arguments for the make_subplots method |

<a id="logplot-add_trace"></a>

### `LogPlot.add_trace`

```python
add_trace(x, z, name, panel_no, resetaxisrange=False, **kwargs)
```

Adds a trace to the plot. By default, lines are added but optional keyword arguments can be added for go.Scatter as `**kwargs`

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `x` |  |  | required | Array with the x-values |
| `z` |  |  | required | Array with the z-values |
| `name` |  |  | required | Name for the trace (LaTeX allowed, e.g. `r'$ \alpha $'`) |
| `panel_no` |  |  | required | Panel to plot the trace on (1-indexed) |
| `resetaxisrange` |  |  | `False` | Boolean determining whether the axis range needs to be reset to fit this trace |
| `kwargs` |  |  |  | Optional keyword arguments for the `go.Scatter` constructor |

**Returns**

Adds the trace to the specified panel

<a id="logplot-add_soilparameter_trace"></a>

### `LogPlot.add_soilparameter_trace`

```python
add_soilparameter_trace(
    parametername,
    panel_no,
    legendname=None,
    resetaxisrange=False,
    **kwargs,
)
```

Adds a trace to the plot based on a soil parameter available in the SoilProfile. By default, lines are added but optional keyword arguments can be added for go.Scatter as `**kwargs`

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `parametername` | kPa |  | required | Name of the soil parameter (with units) e.g. `'Su '` when `'Su from [kPa]'` and `'Su to [kPa]'` are available in the SoilProfile |
| `panel_no` |  |  | required | Panel to plot the trace on (1-indexed) |
| `legendname` |  |  | `None` | Name for the trace (LaTeX allowed, e.g. `r'$ \alpha $'`), default is None to use `parametername` |
| `resetaxisrange` |  |  | `False` | Boolean determining whether the axis range needs to be reset to fit this trace |
| `kwargs` |  |  |  | Optional keyword arguments for the `go.Scatter` constructor |

**Returns**

Adds the trace to the specified panel

<a id="logplot-set_xaxis"></a>

### `LogPlot.set_xaxis`

```python
set_xaxis(title, panel_no, **kwargs)
```

Changes the X-axis title of a panel

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `title` |  |  | required | Title to be set (LaTeX allowed, e.g. `r'$ \alpha $'`) |
| `panel_no` |  |  | required | Panel number (1-indexed) |
| `kwargs` |  |  |  | Additional keyword arguments for the axis layout update function, e.g. `range=(0, 100)` |

**Returns**

Adjusts the X-axis of the specified panel

<a id="logplot-set_zaxis"></a>

### `LogPlot.set_zaxis`

```python
set_zaxis(title, **kwargs)
```

Changes the Z-axis

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `title` |  |  | required | Title to be set (LaTeX allowed, e.g. `r'$ \alpha $'`) |
| `kwargs` |  |  |  | Additional keyword arguments for the axis layout update function, e.g. `range=(0, 100)` |

**Returns**

Adjusts the Z-axis

<a id="logplot-set_size"></a>

### `LogPlot.set_size`

```python
set_size(width, height)
```

Adjust the size of the plot

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `width` |  |  | required | Width of the plot in pixels |
| `height` |  |  | required | Height of the plot in pixels |

**Returns**

Adjust the height and width as specified

<a id="logplot-set_title"></a>

### `LogPlot.set_title`

```python
set_title(title)
```

Set a title for the plot

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `title` |  |  | required | Title for the plot |

**Returns**

Sets the title as specified

<a id="logplot-show"></a>

### `LogPlot.show`

```python
show()
```

No upstream documentation.

<a id="logplotmatplotlib"></a>

## class `LogPlotMatplotlib`

<span class="gc-badge gc-available" data-geocore-function="LogPlotMatplotlib">Available in GeoCore</span> [General and utility functions › Plotting › LogPlotMatplotlib](/docs/geocore/using/modules#logplotmatplotlib)

```python
LogPlotMatplotlib(
    soilprofile,
    secondaryprofile=None,
    no_panels=1,
    logwidth=0.05,
    fillcolordict={'Sand': 'yellow', 'Clay': 'brown', 'Rock': 'grey', 'Silt': 'green'},
    hatchpatterns={'Sand': '...', 'Clay': '////', 'Rock': 'oo', 'Silt': '|||'},
    soiltypelegend=True,
    soiltypecolumn='Soil type',
    edgecolor='black',
    figwidth=10,
    figheight=6,
    plot_layer_transitions=True,
    showgrid=True,
    **kwargs,
)
```

Class for planneled plots with a minilog on the side, using the Matplotlib plotting backend

<a id="logplotmatplotlib-__init__"></a>

### `LogPlotMatplotlib.__init__`

```python
__init__(
    soilprofile,
    secondaryprofile=None,
    no_panels=1,
    logwidth=0.05,
    fillcolordict={'Sand': 'yellow', 'Clay': 'brown', 'Rock': 'grey', 'Silt': 'green'},
    hatchpatterns={'Sand': '...', 'Clay': '////', 'Rock': 'oo', 'Silt': '|||'},
    soiltypelegend=True,
    soiltypecolumn='Soil type',
    edgecolor='black',
    figwidth=10,
    figheight=6,
    plot_layer_transitions=True,
    showgrid=True,
    **kwargs,
)
```

Initializes a figure with a minilog on the side.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `soilprofile` |  |  | required | Soilprofile used for the minilog |
| `secondaryprofile` |  |  | `None` | A second Soilprofile used as an additional minilog. Note that only the `SoilProfile` provided in `soilprofile` will get update if layers and parameters are selected. |
| `no_panels` |  |  | `1` | Number of panels |
| `logwidth` |  |  | `0.05` | Width of the minilog as a percentage of the total width (default=0.05) |
| `fillcolordict` |  |  | `{'Sand': 'yellow', 'Clay': 'brown', 'Rock': 'grey', 'Silt': 'green'}` | Dictionary with fill colors for each of the soil types. Every unique `Soil type` needs to have a corresponding color. Default: `{"Sand": 'yellow', "Clay": 'brown', 'Rock': 'grey'}` |
| `hatchpatterns` |  |  | `{'Sand': '...', 'Clay': '////', 'Rock': 'oo', 'Silt': '\|\|\|'}` | Matplotlib letters used for hatching of the soil types |
| `soiltypelegend` |  |  | `True` | Boolean determining whether legend entries need to be shown for the soil types in the log |
| `soiltypecolumn` |  |  | `'Soil type'` | Column name used to identify the soil type. The entries in this column need to correspond to keys in `fillcolordict` |
| `edgecolor` |  |  | `'black'` | Color of the edge of a layer |
| `figwidth` |  |  | `10` | No upstream documentation. |
| `figheight` |  |  | `6` | Figure height in inches (default=6in) |
| `plot_layer_transitions` |  |  | `True` | Boolean determining whether layer transitions need to be plotted or not |
| `showgrid` |  |  | `True` | Boolean determining whether a grid is shown on the plot panels or not (default=True) |
| `kwargs` |  |  |  | Optional keyword arguments for the make_subplots method |

<a id="logplotmatplotlib-add_trace"></a>

### `LogPlotMatplotlib.add_trace`

```python
add_trace(
    x,
    z,
    name,
    panel_no,
    resetaxisrange=False,
    line=True,
    showlegend=False,
    **kwargs,
)
```

Adds a trace to the plot. By default, lines are added but optional keyword arguments can be added for plt.plot as `**kwargs`

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `x` |  |  | required | Array with the x-values |
| `z` |  |  | required | Array with the z-values |
| `name` |  |  | required | Label for the trace (LaTeX allowed, e.g. `r'$ \alpha $'`) |
| `panel_no` |  |  | required | Panel to plot the trace on (1-indexed) |
| `resetaxisrange` |  |  | `False` | Boolean determining whether the axis range needs to be reset to fit this trace |
| `line` |  |  | `True` | Boolean determining whether the data needs to be shown as a line or as individual markers |
| `showlegend` |  |  | `False` | Boolean determining whether the trace name needs to be added to the legend entries |
| `kwargs` |  |  |  | Optional keyword arguments for the `go.Scatter` constructor |

**Returns**

Adds the trace to the specified panel

<a id="logplotmatplotlib-add_soilparameter_trace"></a>

### `LogPlotMatplotlib.add_soilparameter_trace`

```python
add_soilparameter_trace(
    parametername,
    panel_no,
    legendname=None,
    resetaxisrange=False,
    line=True,
    showlegend=False,
    **kwargs,
)
```

Adds a trace to the plot based on a soil parameter available in the SoilProfile. By default, lines are added but optional keyword arguments can be added for plt.plot as `**kwargs`

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `parametername` | kPa |  | required | Name of the soil parameter (with units) e.g. `'Su '` when `'Su from [kPa]'` and `'Su to [kPa]'` are available in the SoilProfile |
| `panel_no` |  |  | required | Panel to plot the trace on (1-indexed) |
| `legendname` |  |  | `None` | Label for the trace (LaTeX allowed, e.g. `r'$ \alpha $'`) |
| `resetaxisrange` |  |  | `False` | Boolean determining whether the axis range needs to be reset to fit this trace |
| `line` |  |  | `True` | Boolean determining whether the data needs to be shown as a line or as individual markers |
| `showlegend` |  |  | `False` | Boolean determining whether the trace name needs to be added to the legend entries |
| `kwargs` |  |  |  | Optional keyword arguments for the `go.Scatter` constructor |

**Returns**

Adds the trace to the specified panel

<a id="logplotmatplotlib-set_xaxis_title"></a>

### `LogPlotMatplotlib.set_xaxis_title`

```python
set_xaxis_title(title, panel_no, size=15, **kwargs)
```

Changes the X-axis title of a panel

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `title` |  |  | required | Title to be set (LaTeX allowed, e.g. `r'$ \alpha $'`) |
| `panel_no` |  |  | required | Panel number (1-indexed) |
| `size` |  |  | `15` | No upstream documentation. |
| `kwargs` |  |  |  | Additional keyword arguments for the axis layout update function, e.g. `range=(0, 100)` |

**Returns**

Adjusts the X-axis of the specified panel

<a id="logplotmatplotlib-set_xaxis_range"></a>

### `LogPlotMatplotlib.set_xaxis_range`

```python
set_xaxis_range(min_value, max_value, panel_no, ticks=None, **kwargs)
```

Changes the X-axis range of a panel

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `min_value` |  |  | required | Minimum value of the plot panel range |
| `max_value` |  |  | required | Maximum value of the plot panel range |
| `panel_no` |  |  | required | Panel number (1-indexed) |
| `ticks` |  |  | `None` | List of ticks to set (default=None for Matplotlib defaults) |
| `kwargs` |  |  |  | Additional keyword arguments for the `set_xlim` method |

**Returns**

Adjusts the X-axis range of the specified panel

<a id="logplotmatplotlib-set_zaxis_title"></a>

### `LogPlotMatplotlib.set_zaxis_title`

```python
set_zaxis_title(title, size=15, **kwargs)
```

Changes the Z-axis

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `title` |  |  | required | Title to be set (LaTeX allowed, e.g. `r'$ \alpha $'`) |
| `size` |  |  | `15` | No upstream documentation. |
| `kwargs` |  |  |  | Additional keyword arguments for the `set_label` method |

**Returns**

Adjusts the Z-axis title

<a id="logplotmatplotlib-set_zaxis_range"></a>

### `LogPlotMatplotlib.set_zaxis_range`

```python
set_zaxis_range(min_depth, max_depth, ticks=None, **kwargs)
```

Changes the Z-axis

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `min_depth` |  |  | required | Minimum depth of the plot |
| `max_depth` |  |  | required | Maximum depth of the plot |
| `ticks` |  |  | `None` | List of ticks to set (default=None for Matplotlib defaults) |
| `kwargs` |  |  |  | Additional keyword arguments for the `set_ylim` method |

**Returns**

Adjusts the Z-axis range

<a id="logplotmatplotlib-set_size"></a>

### `LogPlotMatplotlib.set_size`

```python
set_size(width, height)
```

Adjust the size of the plot

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `width` |  |  | required | Width of the plot in inches |
| `height` |  |  | required | Height of the plot in inches |

**Returns**

Adjust the height and width as specified

<a id="logplotmatplotlib-show_legend"></a>

### `LogPlotMatplotlib.show_legend`

```python
show_legend()
```

No upstream documentation.

<a id="logplotmatplotlib-plot_layers"></a>

### `LogPlotMatplotlib.plot_layers`

```python
plot_layers()
```

No upstream documentation.

<a id="logplotmatplotlib-show"></a>

### `LogPlotMatplotlib.show`

```python
show(showlegend=True, showfig=True)
```

No upstream documentation.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `showlegend` |  |  | `True` | No upstream documentation. |
| `showfig` |  |  | `True` | No upstream documentation. |

<a id="logplotmatplotlib-save_fig"></a>

### `LogPlotMatplotlib.save_fig`

```python
save_fig(path, dpi=250, bbox_inches='tight', pad_inches=1)
```

Exports the figure to png format

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `path` |  |  | required | Path of the figure (filename ends in .png) |
| `dpi` |  |  | `250` | Output resolution |
| `bbox_inches` |  |  | `'tight'` | Setting for the bounding box |
| `pad_inches` |  |  | `1` | Inches for padding |

<a id="logplotmatplotlib-select_additional_layers"></a>

### `LogPlotMatplotlib.select_additional_layers`

```python
select_additional_layers(no_additional_layers, panel_no=1, precision=2)
```

Allows for the selection of additional layer transitions for the `SoilProfile` object. The number of additional transition is controlled by the `no_additional_layers` argument. Click on the desired layer transition location in the specified panel (default `panel_no=1`) The depth of the layer transition is rounded according to the `precision` argument. Default=2 for cm accuracy.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `no_additional_layers` |  |  | required | No upstream documentation. |
| `panel_no` |  |  | `1` | No upstream documentation. |
| `precision` |  |  | `2` | No upstream documentation. |

<a id="logplotmatplotlib-select_layering"></a>

### `LogPlotMatplotlib.select_layering`

```python
select_layering(panel_no=1, precision=2, stop_threshold=0)
```

Allows for the selection of layer transitions for the `SoilProfile` object. The number of additional transition is controlled by how often the user clicks. Click on the desired layer transition location in the specified panel (default `panel_no=1`). The selection stops when the user clicks on a point with x-coordinate below the `stop_threshold`. The depth of the layer transition is rounded according to the `precision` argument. Default=2 for cm accuracy.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `panel_no` |  |  | `1` | No upstream documentation. |
| `precision` |  |  | `2` | No upstream documentation. |
| `stop_threshold` |  |  | `0` | No upstream documentation. |

<a id="logplotmatplotlib-select_constant"></a>

### `LogPlotMatplotlib.select_constant`

```python
select_constant(panel_no, parametername, units, nan_tolerance=0.1)
```

Selects a constant value in each layer. Click the desired value in each layer, working from the top down. If a nan value needs to be set in a layer, click sufficiently close to the minimum of the x axis. The `nan_tolerance` argument determines which values are interpreted as nan. The parameter is added to the `SoilProfile` object with the `'parametername [units]'` key.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `panel_no` |  |  | required | No upstream documentation. |
| `parametername` |  |  | required | No upstream documentation. |
| `units` |  |  | required | No upstream documentation. |
| `nan_tolerance` |  |  | `0.1` | No upstream documentation. |

<a id="logplotmatplotlib-select_linear"></a>

### `LogPlotMatplotlib.select_linear`

```python
select_linear(panel_no, parametername, units, nan_tolerance=0.1)
```

Selects a linear variation in each layer. Click the desired value at each layer boundary. Note that a value needs to be selected at the top and bottom of each layer (2 x no layers clicks). If a nan value needs to be set in a layer, click sufficiently close to the minimum of the x axis. The `nan_tolerance` argument determines which values are interpreted as nan. The parameter is added to the `SoilProfile` object with the `'parametername [units]'` key.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `panel_no` |  |  | required | No upstream documentation. |
| `parametername` |  |  | required | No upstream documentation. |
| `units` |  |  | required | No upstream documentation. |
| `nan_tolerance` |  |  | `0.1` | No upstream documentation. |

<a id="plot_with_log"></a>

## `plot_with_log`

<span class="gc-badge gc-available" data-geocore-function="plot_with_log">Available in GeoCore</span> [General and utility functions › Plotting › Multi-Trace Log Plot](/docs/geocore/using/modules#plot_with_log)

```python
plot_with_log(
    x=[[]],
    z=[[]],
    names=[[]],
    showlegends=None,
    hide_all_legends=False,
    modes=None,
    markerformats=None,
    soildata=None,
    fillcolordict={'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green', 'ROCK': 'grey'},
    depth_from_key='Depth from [m]',
    depth_to_key='Depth to [m]',
    colors=None,
    logwidth=0.05,
    xtitles=[],
    ztitle=None,
    xranges=None,
    zrange=None,
    ztick=None,
    dticks=None,
    layout={},
    showfig=True,
)
```

Plots a given number of traces in a plot with a soil mini-log on the left hand side. The traces are given as a list of lists, the traces are grouped per plotting panel. For example x=[[np.linspace(0, 1, 100), np.logspace(0,2,100)], [np.linspace(1, 3, 100), ]] leads to the first two traces plotted in the first panel and one trace in the second panel. The same goes for the z arrays, trace names, ...

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `x` |  |  | `[[]]` | List of lists of x-arrays for the traces |
| `z` |  |  | `[[]]` | List of lists of z-arrays for the traces |
| `names` |  |  | `[[]]` | List of lists of names for the traces (used in legend) |
| `showlegends` |  |  | `None` | Array of booleans determining whether or not to show the trace in the legend. Showing/hiding legends can be specified per trace. |
| `hide_all_legends` |  |  | `False` | Boolean indicating whether all legends need to be hidden (default=False). |
| `modes` |  |  | `None` | List of display modes for the traces (select from 'lines', 'markers' or 'lines+markers' |
| `markerformats` |  |  | `None` | List of formats for the markers (see Plotly docs for more info) |
| `soildata` | m |  | `None` | Pandas dataframe with keys 'Soil type': Array with soil type for each layer, 'Depth from ': Array with start depth for each layer, 'Depth to [m]': Array with bottom depth for each layer |
| `fillcolordict` |  |  | `{'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green', 'ROCK': 'grey'}` | Dictionary with fill colours (default yellow for 'SAND', brown from 'CLAY' and grey for 'ROCK') |
| `depth_from_key` |  |  | `'Depth from [m]'` | Key for the column with start depths of each layer |
| `depth_to_key` |  |  | `'Depth to [m]'` | Key for the column with end depths of each layer |
| `colors` |  |  | `None` | List of colours to be used for plotting (default = default Plotly colours) |
| `logwidth` |  |  | `0.05` | Width of the soil width as a ratio of the total plot with (default = 0.05) |
| `xtitles` |  |  | `[]` | Array with X-axis titles for the panels |
| `ztitle` |  |  | `None` | Depth axis title (Depth axis is shared between all panels) |
| `xranges` |  |  | `None` | List with ranges to be used for X-axes |
| `zrange` |  |  | `None` | Range to be used for Y-axis |
| `ztick` |  |  | `None` | Tick interval to be used for the Y-axis |
| `dticks` |  |  | `None` | List of tick intervals to be used for the X-axes |
| `layout` |  |  | `{}` | Dictionary with the layout settings |
| `showfig` |  |  | `True` | Boolean determining whether the figure needs to be shown |

**Returns**

Plotly figure object which can be further modified

<a id="peak_picker"></a>

## `peak_picker`

```python
peak_picker(x, y, correct_selected_point=True)
```

Generates an interactive Matplotlib plot which allows you to pick the peak from a graph with e.g. load-displacement data

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `x` |  |  | required | Array with x-values |
| `y` |  |  | required | Array with y-values |
| `correct_selected_point` |  |  | `True` | Boolean determining whether a correction is applied to interpolate the peak based on the selected value of X for the peak |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `x100` |  | x-coordinate of the peak |
| `y100` |  | y-coordinate of the peak |
| `x50` |  | x-coordinate where y reached 50% of its peak y |
| `y50` |  | y-coordinate with y equal to 50% of the peak y |
