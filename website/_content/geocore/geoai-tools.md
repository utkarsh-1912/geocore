---
title: GeoAI tools
slug: geoai/tools
section: GeoAI
nav_order: 30
description: The validated calculation and research tools GeoAI can call, and the GeoAI API endpoints.
sources:
- python-backend/core/geoai/tool_definitions.py
- python-backend/core/geoai/tools_cpt_piles.py
- python-backend/core/geoai/tools_shallow.py
- python-backend/core/geoai/tool_registry.py
- python-backend/core/geoai/schema_factory.py
- python-backend/core/geoai/validator.py
- python-backend/core/geoai/units.py
- python-backend/core/geoai/api.py
- python-backend/core/geoai/exposure_policy.py
- python-backend/core/geoai/model_config.py
---

GeoAI can only act through **tools** in GeoCore's tool registry. Each tool has an explicit input schema; inputs are validated before the tool runs, and results are returned as structured data with a provenance record.

## Curated tools

These tools have hand-written schemas with units, bounds and accepted aliases for each input. The table is generated from `tool_definitions.py`, `tools_cpt_piles.py` and `tools_shallow.py`.

<!-- geocore:generated geoai-tools -->

The CPT and SPT tools use GeoCore's own deterministic routines:

- `classify_cpt_soil_behavior` computes normalised CPT parameters ($q_t$, $Q_t$, $F_r$, $B_q$, $I_c$) and the soil behaviour type zone after Robertson (1990/2009) at a single depth.
- `derive_cpt_parameters` estimates $s_u$ from the net cone resistance with a cone factor $N_{kt}$ (default 15), $\phi'$ and $D_r$ in coarse-grained soils, and $G_{max}$ after Robertson (2009).
- `normalize_spt_test` computes $N_{60}$ with energy, rod-length, borehole and liner corrections (Skempton, 1986), $(N_1)_{60}$ with the Liao and Whitman (1986) overburden correction, and correlated $D_r$ and $\phi'$.

Each result states the method used. These routines are separate from groundhog's own CPT and SPT functions documented in the [API reference](/docs/groundhog/api/siteinvestigation/insitutests).

## Calculator tools

In addition to the curated tools, GeoCore registers every calculator in the [calculation catalogue](/docs/geocore/using/modules) as a tool, with a schema generated from the groundhog function signature and GeoCore's parameter inventory (units and bounds where known). The tool description is the first paragraph of the groundhog docstring. Only the most relevant tools (5 by default, see [model settings](/docs/geoai/model-setup#settings)) are offered to the model for any one request.

Calculators that need stored objects, return only a figure, or read files (soil profile construction, stateful pile and foundation workflows, plotting, AGS file reading) are not offered to the model; they remain available in the calculation forms.

## Input validation and units

Before a tool runs:

- placeholder values such as `-`, `N/A` or `null` are treated as missing, and `NaN`/infinite numbers are rejected;
- values are checked against the schema bounds; failures are returned to the model as a validation error, not silently corrected;
- for curated tools, values given as text with units (for example `"1.5 MPa"`) are converted deterministically to the unit the tool expects, and a value with the wrong kind of unit (for example a pressure given for a unit weight) is rejected.

## Provenance

Every tool result includes a `_provenance` record with the tool name, the validated inputs, the method and reference standard (a generic label when no specific method is catalogued for the tool), output units, assumptions, the calculation engine and a UTC timestamp.

## API endpoints

The GeoAI endpoints are served by the local calculation engine under `http://127.0.0.1:8000/api/geoai`.

| Endpoint | Purpose |
|---|---|
| `GET /tools` | List all registered tools with input and output schemas. |
| `GET /tools/format/{openai\|gemini\|raw}` | Tool schemas in common function-calling formats. |
| `POST /invoke` | Run one tool: `{"tool_name": "...", "args": {...}}`. Validation errors return HTTP 422. |
| `POST /chat` | Ask GeoAI: `{"prompt": "...", "context": {...}}`. Add `?stream=true` for server-sent events. |
| `POST /cancel` | Stop the request in progress; the model stays loaded. |
| `POST /explain` | Method, reference and formula for an already computed result, with the inputs substituted: `{"function_id": "...", "args": {...}, "results": {...}}`. No model is used. |
| `POST /explain/narrate` | A short plain-language explanation of the same result, written by the local model. |
| `GET /project/groundwater`, `PUT /project/groundwater` | Read or record the project groundwater depth: `{"groundwater_depth_m": 2.5}` (m below ground level; `null` clears it). |
| `GET /project/context` | What GeoAI reads from the project: groundwater level, layered soil profiles and a listing of CPTs. |
| `GET /status` | Active provider, whether a model is loaded, number of tools. |
| `GET /models` | Curated and installed models. |
| `POST /models/download`, `GET /models/download/status` | Download a curated model in the background and follow progress. |
| `POST /models/select` | Activate a model file or provider. |
| `POST /models/autolink` | Find installed `.gguf` files and activate one. |
| `POST /warmup` | Load the model in the background (no effect when it is already loaded or loading). |
| `GET /memory` | Engine memory use and model load state. |
| `POST /unload` | Release the model from memory. |
