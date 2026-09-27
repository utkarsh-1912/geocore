---
title: Parameter mapping
slug: groundhog/api/general/parameter_mapping
section: Groundhog API Reference
description: 'API reference for groundhog.general.parameter_mapping: 6 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/general/parameter_mapping.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.general.parameter_mapping
upstream_docs_urls:
- https://groundhog.readthedocs.io/en/main/general/parameter_mapping.html
geocore_available: true
geocore_functions:
- get_projected_point
- latlon_distance
- map_depth_properties
- merge_two_dicts
- offsets_api
- reverse_dict
---

Module `groundhog.general.parameter_mapping` (groundhog 0.15.0). [View source](https://github.com/snakesonabrain/groundhog/blob/v0.15.0/groundhog/general/parameter_mapping.py).

Upstream documentation: [Parameter mapping](https://groundhog.readthedocs.io/en/main/general/parameter_mapping.html).

**Functions:** [`map_depth_properties`](#map_depth_properties), [`merge_two_dicts`](#merge_two_dicts), [`reverse_dict`](#reverse_dict), [`latlon_distance`](#latlon_distance), [`get_projected_point`](#get_projected_point), [`offsets`](#offsets)

<a id="map_depth_properties"></a>

## `map_depth_properties`

<span class="gc-badge gc-available" data-geocore-function="map_depth_properties">Available in GeoCore</span> [General and utility functions › Parameter Mapping › map_depth_properties()](/docs/geocore/using/modules#map_depth_properties)

```python
map_depth_properties(
    target_df,
    layering_df,
    target_z_key=None,
    layering_zfrom_key=None,
    layering_zto_key=None,
)
```

Maps properties defined in a dataframe with layers to a dataframe with nodal depth positions.

Note that numerical parameters in the layering dataframe should contain a unit between square brackets (e.g. 'Friction angle [deg]'). String parameters don't have the square brackets (e.g. 'Soil type'). Do not use square brackets anywhere else in the column keys.

Note that if a node of the target dataframe corresponds to a layer change, the properties of the layer layer below the selected node are assigned.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `target_df` |  |  | required | Pandas dataframe to which the properties need to be mapped |
| `layering_df` |  |  | required | Pandas dataframe with the layering definition |
| `target_z_key` | m |  | `None` | Depth key in the target dataframe. If unspecified, 'z ' is used |
| `layering_zfrom_key` | m |  | `None` | Start depth key in the layering dataframe. If unspecified, 'z from ' is used |
| `layering_zto_key` | m |  | `None` | End depth key in the layering dataframe. If unspecified, 'z to ' is used |

**Returns**

<a id="merge_two_dicts"></a>

## `merge_two_dicts`

<span class="gc-badge gc-available" data-geocore-function="merge_two_dicts">Available in GeoCore</span> [General and utility functions › Parameter Mapping › merge_two_dicts()](/docs/geocore/using/modules#merge_two_dicts)

```python
merge_two_dicts(x, y)
```

Merges two dictionaries

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `x` |  |  | required | First dictionary |
| `y` |  |  | required | Second dictionary |

**Returns**

Updated dictionary

<a id="reverse_dict"></a>

## `reverse_dict`

<span class="gc-badge gc-available" data-geocore-function="reverse_dict">Available in GeoCore</span> [General and utility functions › Parameter Mapping › reverse_dict()](/docs/geocore/using/modules#reverse_dict)

```python
reverse_dict(input_dict)
```

Turn dictionary keys into values and values into keys

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `input_dict` |  |  | required | Dictionary with just 1 level |

**Returns**

Dictionary with keys turned into values and vice-versa

<a id="latlon_distance"></a>

## `latlon_distance`

<span class="gc-badge gc-available" data-geocore-function="latlon_distance">Available in GeoCore</span> [General and utility functions › Parameter Mapping › latlon_distance()](/docs/geocore/using/modules#latlon_distance)

```python
latlon_distance(lon1, lat1, lon2, lat2)
```

Calculates the offset in meters from two pairs of coordinates specified in longitude and latitude (WGS84)

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `lon1` |  |  | required | Longitude (easting) of the first point |
| `lat1` |  |  | required | Latitude (northing) of the first point |
| `lon2` |  |  | required | Longitude (easting) of the second point |
| `lat2` |  |  | required | Latitude (northing) of the second point |

**Returns**

distance in meters

<a id="get_projected_point"></a>

## `get_projected_point`

<span class="gc-badge gc-available" data-geocore-function="get_projected_point">Available in GeoCore</span> [General and utility functions › Parameter Mapping › get_projected_point()](/docs/geocore/using/modules#get_projected_point)

```python
get_projected_point(lon1, lat1, lon2, lat2, lon3, lat3)
```

Finds the coordinates of a point projected onto a line

Purpose - lon1,lat1,lon2,lat2 = Two points representing the ends of the line segment in lat/lon lon3,lat3 = The lat/lon of the point for which the offset needs to be known Returns - lon4,lat4, outsidebounds = Returns the Point on the line perpendicular to the offset and whether the projection is outside the line

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `lon1` |  |  | required | No upstream documentation. |
| `lat1` |  |  | required | No upstream documentation. |
| `lon2` |  |  | required | No upstream documentation. |
| `lat2` |  |  | required | No upstream documentation. |
| `lon3` |  |  | required | No upstream documentation. |
| `lat3` |  |  | required | No upstream documentation. |

<a id="offsets"></a>

## `offsets`

<span class="gc-badge gc-available" data-geocore-function="offsets_api">Available in GeoCore</span> [General and utility functions › Parameter Mapping › offsets()](/docs/geocore/using/modules#offsets_api)

```python
offsets(startpoint, endpoint, point, latlon=False)
```

Calculates the offset between a point and a line joining a given start- and endpoint. The offset from the projected point to the start and end point is also calculated. Through analytical calculations, the position of the point is also determined.

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `startpoint` |  |  | required | Tuple with x and y coordinates of the starting point |
| `endpoint` |  |  | required | Tuple with x and y coordinates of the end point |
| `point` |  |  | required | Point for which the offset to the section needs to be computed |
| `latlon` |  |  | `False` | Boolean defining whether coordinates are specified in latitude/longitude (default=False) |

**Returns**

Dictionary with the following keys:

| Key | Unit | Description |
|---|---|---|
| `offset start to point` |  | Distance between start point and point of interest |
| `offset end to point` |  | Distance between end point and point of interest |
| `offset to line` |  | Offset between point and the line joining start and end point |
| `offset to start projected` |  | Offset from the start point (negative is before the start point) |
| `offset to end projected` |  | Offset from the end point (negative is behing the end point) |
| `angle start [deg]` | deg | Angle between line joining start and end point and line joining point and start point |
| `angle end [deg]` | deg | Angle between line joining start and end point and line joining point and end point |
| `before start` |  | Boolean determining if point lies before the start point |
| `behind end` |  | Boolean determining if point lies behind the end point |
