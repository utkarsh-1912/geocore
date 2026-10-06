---
title: read_site_data
slug: groundhog/api/siteinvestigation/insitutests/read_site_data
section: Groundhog API Reference
description: 'API reference for groundhog.siteinvestigation.insitutests.read_site_data: 1 functions, 0 classes.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/siteinvestigation/insitutests/read_site_data.py
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: Generated from the docstrings of the installed groundhog package; RST converted to Markdown and parameter/return tables derived from the docstrings.
module: groundhog.siteinvestigation.insitutests.read_site_data
geocore_available: false
---

Module `groundhog.siteinvestigation.insitutests.read_site_data` (groundhog 0.16.0). [View source](https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/groundhog/siteinvestigation/insitutests/read_site_data.py).

**Functions:** [`read_ags`](#read_ags)

<a id="read_ags"></a>

## `read_ags`

```python
read_ags(file_path, groupname, combine_headers=True, includes_type=True)
```

Reads AGS data from a file and extracts the data for a given groupname into a DataFrame. All data with type "DP" is converted to float format

**Parameters**

| Parameter | Unit | Suggested range | Default | Description |
|---|---|---|---|---|
| `file_path` |  |  | required | Path (absolute or relative to the ags file) |
| `groupname` |  |  | required | Name of the AGS group exactly as it is written in the AGS file |
| `combine_headers` |  |  | `True` | Boolean determining whether the units are included in the header or not |
| `includes_type` |  |  | `True` | Boolean determining whether a TYPE is included with the data |

**Returns**

Dataframe with data for the given group
