---
title: indextests
slug: groundhog/api/siteinvestigation/labtesting/indextests
section: Groundhog API Reference
description: 'API reference for groundhog.siteinvestigation.labtesting.indextests: 0 functions, 2 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/siteinvestigation/labtesting/indextests.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.siteinvestigation.labtesting.indextests
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/site_investigation/indextests.html
geocore_available: true
geocore_functions:
- PSDChart
- PlasticityChart
---

Module `groundhog.siteinvestigation.labtesting.indextests` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/siteinvestigation/labtesting/indextests.py).

Upstream documentation: [Index tests](https://groundhog.readthedocs.io/en/main/site_investigation/indextests.html).

**Classes:** [`PlasticityChart`](#plasticitychart), [`PSDChart`](#psdchart)

<a id="plasticitychart"></a>

## class `PlasticityChart`

<span class="gc-badge gc-available" data-geocore-function="PlasticityChart">Available in GeoCore</span> [Site investigation › Laboratory: Index tests › PlasticityChart](/docs/geocore/using/modules#plasticitychart)

```python
PlasticityChart(plot_height=500, plot_width=800, plot_title=None)
```

Class for plasticity chart

<a id="plasticitychart-__init__"></a>

### `PlasticityChart.__init__`

```python
__init__(plot_height=500, plot_width=800, plot_title=None)
```

Initiates a plasticity chart

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `plot_height` |  |  | `500` | Height of the plot in pixels |
| `plot_width` |  |  | `800` | Width of the plot in pixels |
| `plot_title` |  |  | `None` | Title of the plot |

<a id="plasticitychart-add_trace"></a>

### `PlasticityChart.add_trace`

```python
add_trace(ll, pi, name, **kwargs)
```

Adds a trace to the plot. By default, markers are added but optional keyword arguments can be added for go.Scatter as `**kwargs`

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `ll` |  |  | required | Array with the Liquid Limit values (in percent) |
| `pi` |  |  | required | Array with the Plasticity Index values (in percent) |
| `name` |  |  | required | Name for the trace (LaTeX allowed, e.g. `r'$ \alpha $'`) |
| `kwargs` |  |  |  | Optional keyword arguments for the `go.Scatter` constructor |

**Returns**

Adds the trace to the specified panel

<a id="plasticitychart-show"></a>

### `PlasticityChart.show`

```python
show()
```

No upstream documentation.

<a id="psdchart"></a>

## class `PSDChart`

<span class="gc-badge gc-available" data-geocore-function="PSDChart">Available in GeoCore</span> [Site investigation › Laboratory: Index tests › PSDChart](/docs/geocore/using/modules#psdchart)

```python
PSDChart(
    plot_title=None,
    marginsettings={'l': 0, 'r': 0, 'b': 100, 't': 100, 'pad': 0},
    legendsettings={'x': 0.1, 'y': 0.9},
)
```

Class for plotting of grain size distribution data

<a id="psdchart-__init__"></a>

### `PSDChart.__init__`

```python
__init__(
    plot_title=None,
    marginsettings={'l': 0, 'r': 0, 'b': 100, 't': 100, 'pad': 0},
    legendsettings={'x': 0.1, 'y': 0.9},
)
```

Initiates a particle size distribution chart

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `plot_title` |  |  | `None` | Title of the plot |
| `marginsettings` |  |  | `{'l': 0, 'r': 0, 'b': 100, 't': 100, 'pad': 0}` | No upstream documentation. |
| `legendsettings` |  |  | `{'x': 0.1, 'y': 0.9}` | No upstream documentation. |
| `plot_height` |  |  |  | Height of the plot in pixels |
| `plot_width` |  |  |  | Width of the plot in pixels |

<a id="psdchart-add_trace"></a>

### `PSDChart.add_trace`

```python
add_trace(grainsize, pctpassing, name, **kwargs)
```

Adds a trace to the plot. By default, lines are added but optional keyword arguments can be added for go.Scatter as `**kwargs`

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `grainsize` |  |  | required | Array with the grain sizes (in mm) |
| `pctpassing` |  |  | required | Array with the percentages passing each sieze opening size (in percent) |
| `name` |  |  | required | Name for the trace (LaTeX allowed, e.g. `r'$ \alpha $'`) |
| `kwargs` |  |  |  | Optional keyword arguments for the `go.Scatter` constructor |

**Returns**

Adds the trace to the specified panel

<a id="psdchart-show"></a>

### `PSDChart.show`

```python
show()
```

No upstream documentation.
