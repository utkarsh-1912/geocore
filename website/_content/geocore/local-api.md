---
title: Local calculation engine API
slug: geocore/using/local-api
section: Using GeoCore
nav_order: 50
description: The HTTP endpoints the desktop app uses to talk to GeoCore's local calculation engine.
sources:
- python-backend/main.py
- python-backend/core/router.py
- python-backend/core/geoai/api.py
---

The desktop frontend talks to the calculation engine over HTTP on `127.0.0.1:8000`. The engine only listens on the local loopback address. The endpoints are an internal interface of the desktop app and may change between versions, but they are useful for scripting and debugging while GeoCore is running.

## Running a calculation

`POST /api/execute`

```json
{
  "moduleId": "insitutests",
  "functionId": "relativedensity_sand_jamiolkowski",
  "args": {"qc": 20, "sigma_vo_eff": 100, "k0": 0.8}
}
```

`functionId` is the calculator id shown in the [calculation catalogue](/docs/geocore/using/modules). For most calculators it is the groundhog function name, and `args` are that function's parameters in the units given in the [API reference](/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations#relativedensity_sand_jamiolkowski).

The response is the result dictionary returned by groundhog (for this example the keys `Dr dry [-]` and `Dr sat [-]`), with any warnings under `warnings`. Invalid inputs return HTTP 422 with the list of failing fields; calculation errors return HTTP 500 with a message.

```python
import requests

r = requests.post("http://127.0.0.1:8000/api/execute", json={
    "moduleId": "insitutests",
    "functionId": "relativedensity_sand_jamiolkowski",
    "args": {"qc": 20, "sigma_vo_eff": 100, "k0": 0.8},
})
print(r.json())
```

## Other endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | Engine status and version. |
| `GET /modules` | Map of all calculator ids known to the engine. |
| `GET /api/objects/{type}` | List stored objects of a type (for example `SoilProfile`). |
| `GET /api/objects/{type}/{id}` | Columns and data of a stored object. |
| `POST /api/objects/upload?type_name=SoilProfile` | Create a soil profile from an uploaded CSV/Excel file. |
| `POST /api/objects/create?type_name=SoilProfile` | Create a soil profile from JSON rows (`raw_data`). |
| `DELETE /api/objects/{type}/{id}` | Delete a stored object. |
| `GET /api/schema/overrides`, `POST /api/schema/override` | Read or save [form customisations](/docs/geocore/using/parameter-overrides). |
| `/api/geoai/...` | GeoAI endpoints, see [GeoAI tools](/docs/geoai/tools#api-endpoints). |
