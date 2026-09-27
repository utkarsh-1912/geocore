---
title: GeoAI tools
slug: geoai/tools
section: GeoAI
description: The validated calculation and research tools GeoAI can call, and the GeoAI API endpoints.
origin: geocore
source_url: https://github.com/utkarsh-1912/geocore/blob/main/website/_content/geocore/geoai-tools.md
license: GPL-3.0
author: Utkarsh Gupta
attribution: GeoCore documentation by Utkarsh Gupta, licensed under the GNU GPL v3.
groundhog_version: 0.15.0
edited_by_geocore: false
sources:
- python-backend/core/geoai/tool_definitions.py
- python-backend/core/geoai/tool_registry.py
- python-backend/core/geoai/schema_factory.py
- python-backend/core/geoai/validator.py
- python-backend/core/geoai/units.py
- python-backend/core/geoai/api.py
---

GeoAI can only act through **tools** in GeoCore's tool registry. Each tool has an explicit input schema; inputs are validated before the tool runs, and results are returned as structured data with a provenance record.

## Curated tools

These tools have hand-written schemas with units, bounds and accepted aliases for each input. The table is generated from `tool_definitions.py`.

| Tool | Category | What it does |
|---|---|---|
| `calculate_bulk_unit_weight` | classification | Calculates bulk unit weight (gamma) and effective unit weight from specific gravity (Gs), void ratio (e), and degree of saturation (Sr). |
| `calculate_void_ratio_from_porosity` | classification | Calculates void ratio (e) from porosity (n) using phase relations: e = n / (1 - n). |
| `calculate_relative_density` | classification | Calculates soil relative density (Dr) from current void ratio (e), minimum void ratio (e_min), and maximum void ratio (e_max). |
| `calculate_stresses_circular_footing` | shallow_foundations | Calculates vertical and horizontal elastic stress increments in a soil half-space under the center of a circular loaded area. |
| `calculate_stresses_point_load` | shallow_foundations | Calculates 3D elastic stress distribution (sigma_z, sigma_r, sigma_theta, tau_rz) from a concentrated surface point load using Boussinesq theory. |
| `calculate_gmax_from_shear_wave_velocity` | soil_dynamics | Calculates small-strain shear modulus Gmax [kPa] from shear wave velocity Vs [m/s] and unit weight gamma [kN/m3]. |
| `calculate_earth_pressure_rankine` | excavations | Calculates active (Ka) and passive (Kp) lateral earth pressure coefficients for inclined or vertical walls using Rankine theory. |
| `calculate_pipeline_contact_width` | pipelines | Calculates contact width between a subsea pipeline and seabed from outer diameter and embedment depth. |
| `calculate_hydraulic_conductivity_unconfined` | consolidation | Calculates aquifer hydraulic conductivity k [m/s] from unconfined steady-state pumping test data using the Dupuit-Thiem solution. |
| `normalize_spt_test` | in_situ | Normalizes raw SPT blow count N to standard N60 and overburden-corrected (N1)60, and estimates relative density Dr and friction angle phi'. |
| `classify_cpt_soil_behavior` | in_situ | Classifies soil behavior type (SBT) and calculates normalized CPT indices (Qt, Fr, Bq, Ic) using Robertson (1990/2009). |
| `derive_cpt_parameters` | in_situ | Derives geotechnical design parameters (undrained shear strength su, friction angle phi', relative density Dr, small-strain shear modulus Gmax) from CPT measurements. |
| `search_local_documents` | research | Searches local project documents, technical notes, papers, and standards using BM25 full-text retrieval. |
| `index_document_text` | research | Indexes raw text or markdown technical content into the local SQLite full-text search index. |

The CPT and SPT tools use GeoCore's own deterministic routines:

- `classify_cpt_soil_behavior` computes normalised CPT parameters ($q_t$, $Q_t$, $F_r$, $B_q$, $I_c$) and the soil behaviour type zone after Robertson (1990/2009) at a single depth.
- `derive_cpt_parameters` estimates $s_u$ from the net cone resistance with a cone factor $N_{kt}$ (default 15), $\phi'$ and $D_r$ in coarse-grained soils, and $G_{max}$ after Robertson (2009).
- `normalize_spt_test` computes $N_{60}$ with energy, rod-length, borehole and liner corrections (Skempton, 1986), $(N_1)_{60}$ with the Liao and Whitman (1986) overburden correction, and correlated $D_r$ and $\phi'$.

Each result states the method used. These routines are separate from groundhog's own CPT and SPT functions documented in the [API reference](/docs/groundhog/api/siteinvestigation/insitutests).

## Calculator tools

In addition to the curated tools, GeoCore registers every calculator in the [calculation catalogue](/docs/geocore/using/modules) as a tool, with a schema generated from the groundhog function signature and GeoCore's parameter inventory (units and bounds where known). The tool description is the first paragraph of the groundhog docstring. Only a relevant subset of tools (at most 20) is offered to the model for any one request.

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
| `GET /status` | Active provider, whether a model is loaded, number of tools. |
| `GET /models` | Curated and installed models. |
| `POST /models/download`, `GET /models/download/status` | Download a curated model in the background and follow progress. |
| `POST /models/select` | Activate a model file or provider. |
| `POST /models/autolink` | Find installed `.gguf` files and activate one. |
| `GET /memory` | Engine memory use and model load state. |
| `POST /unload` | Release the model from memory. |
