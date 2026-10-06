---
title: CPT retrieval from BRO (DINOLoket)
slug: groundhog/tutorials/demo-bro-cpt-retrieval
section: Groundhog Guides
description: 'groundhog tutorial notebook: Demo - BRO CPT retrieval.'
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/dc7d554c6b8986bae30f518304546a911b1ca5ab/notebooks/Demo%20-%20BRO%20CPT%20retrieval.ipynb
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.16.0
edited_by_geocore: true
geocore_edit_note: 'Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, text and image outputs reproduced, interactive Plotly/HTML outputs omitted, with a short note on how to run this in GeoCore prepended.'
notebook: notebooks/Demo - BRO CPT retrieval.ipynb
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, run the same calculation through a [calculation form](/docs/geocore/using/modules) or by asking **GeoAI**, which calls the same groundhog function through its validated Tool Registry. This notebook is kept for anyone who wants to call groundhog directly from their own Python code instead.

```python
import numpy as np
import os
import re
from IPython.display import HTML
import pandas as pd
#import xmltodict
import requests
pd.options.display.max_columns = 200
pd.options.display.max_rows = 1000
```

```python
from plotly import tools, subplots
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
import plotly.figure_factory as ff
from plotly.colors import DEFAULT_PLOTLY_COLORS
from plotly.offline import init_notebook_mode
init_notebook_mode()
pio.templates.default = 'plotly_white'
```

```python
import xml.etree.ElementTree as ET
```

## Location-based query

First, all CPTs around a certain point can be retrieved (in lat/lon).

```python
url = "https://publiek.broservices.nl/sr/cpt/v1/characteristics/searches?requestReference=request"
```

```python
# setup the query params (literal copy of the bro example in the docs)
my_obj = {
    "registrationPeriod": {"beginDate": "2017-01-01", "endDate": "2021-01-01"},
    "area": {
        "enclosingCircle": {
            "center": {"lat": 52.038297852, "lon": 5.31447958948},
            "radius": 0.5,
        }
    },
}

# get it..
x = requests.post(url, json=my_obj)
```

The XML response contains information on the CPTs found in the area. Multiple CPTs can be returned. Note that detailed CPT data is not included in the response.

```python
x.text
```

The response can be parsed to get to IDs for the CPTs found.

```python
root = ET.fromstring(x.text)
```

The names of the CPTs and the locations are parsed from the XML response.

```python
broIds = []
srids = []
eastings = []
northings = []
for child in root:
    if child.tag == "{http://www.broservices.nl/xsd/dscpt/1.1}dispatchDocument":
        for elem in child:
            for e in elem.findall("{http://www.broservices.nl/xsd/brocommon/3.0}broId"):
                broIds.append(e.text)
            for e in elem.findall("{http://www.broservices.nl/xsd/brocommon/3.0}deliveredLocation"):
                srids.append(e.attrib['srsName'][-5:])
                for _t in e:
                    eastings.append(float(re.split(' ', _t.text)[0]))
                    northings.append(float(re.split(' ', _t.text)[1]))
            
broIds, srids, eastings, northings
```

For plotting purposes, the coordinates are converted to lat/lon pairs and stored in a Pandas dataframe.

```python
from pyproj import Transformer
location_data = pd.DataFrame()
for i, _test in enumerate(broIds):
    transformer = Transformer.from_crs('epsg:%s' % (srids[i]), 'epsg:4326')
    lat, lon = transformer.transform(eastings[i], northings[i])
    location_data.loc[i, "Location"]  = _test
    location_data.loc[i, "easting"] = lon
    location_data.loc[i, "northing"] = lat
```

A map with the retrieved CPTs can be plotted.

```python
fig = px.scatter_mapbox(location_data, lat='northing', lon='easting', hover_name='Location',
    hover_data=['Location'], zoom=15, height=500)
fig.update_layout(mapbox_style='open-street-map')
fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
fig.show()
```

## Retrieval of detailed CPT data

We can select one of the CPTs in the response and retrieve the details using the ```geotexxx``` library developed by Thomas van der Linden.

We can first load the ``Cpt`` class.

```python
from geotexxx.gefxml_reader import Cpt
```

Next, the URL for retrieving the CPT data is built up using the ``broId`` of the CPT under consideration:

```python
detail_url = f"https://publiek.broservices.nl/sr/cpt/v1/objects/%s" % broIds[1]
detail_url
```

A ``GET`` request to this URL is performed to retrieve the XML data:

```python
resp = requests.get(detail_url)
```

The XML is stored in the ``.text`` attribute:

```python
resp.text
```

We can instantiate a ``Cpt`` object and load the XML data using the ``load_xml`` method.

```python
cpt_detail = Cpt()

cpt_detail.load_xml(resp.text, fromFile=False)
```

The CPT data is stored in the ``.data`` attribute.

```python
cpt_detail.data.head()
```

## Loading data into ``groundhog``

The CPT processing functionality in ``groundhog`` can be used with the BRO CPT data. 

``groundhog`` expects a pore pressure column ``'u2 [MPa]'``. This data is not present in the XML response, so an additional column with NaN values is created:

```python
cpt_detail.data.loc[:, 'u2 [MPa]'] = np.nan
```

We can instantiate a ``PCPTProcessing`` object:

```python
from groundhog.siteinvestigation.insitutests.pcpt_processing import PCPTProcessing
groundhogcpt = PCPTProcessing("BRO CPT")
```

As the CPT data is already available in a dataframe, we can use the ``.load_pandas`` method to load this data into the ``PCPTProcessing`` object.

```python
groundhogcpt.load_pandas(cpt_detail.data, z_key="penetrationLength", qc_key="coneResistance", fs_key="localFriction")
```

The CPT data can be plotted:

```python
groundhogcpt.plot_raw_pcpt(plot_friction_ratio=True)
```
