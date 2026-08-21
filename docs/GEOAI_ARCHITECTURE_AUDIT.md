# GeoAI Architecture Audit — Phase 0

**Date:** 2026-08-22
**Repository:** https://github.com/utkarsh-1912/geocore
**Scope:** Complete codebase audit for GeoAI infrastructure readiness

---

## Table of Contents

- [A. Existing Calculation Inventory](#a-existing-calculation-inventory)
  - [A1. Architecture Overview](#a1-architecture-overview)
  - [A2. Registry & Execution Engine](#a2-registry--execution-engine)
  - [A3. Special-Case Handlers](#a3-special-case-handlers)
  - [A4. Wrapper Functions](#a4-wrapper-functions)
  - [A5. Frontend Module Tree](#a5-frontend-module-tree)
  - [A6. Frontend Schema Definitions](#a6-frontend-schema-definitions)
- [B. Existing Data Inventory](#b-existing-data-inventory)
  - [B1. Project Data & State Management](#b1-project-data--state-management)
  - [B2. Soil Profile Data](#b2-soil-profile-data)
  - [B3. CPT Data Handling](#b3-cpt-data-handling)
  - [B4. Borehole & SPT Data Handling](#b4-borehole--spt-data-handling)
  - [B5. AGS Import](#b5-ags-import)
  - [B6. Report Generation & Export](#b6-report-generation--export)
  - [B7. Schema Override System](#b7-schema-override-system)
- [C. Existing Problems](#c-existing-problems)
  - [C1. None/null/NaN/Infinity Handling](#c1-nonenullnaninfinity-handling)
  - [C2. Empty Strings and Sentinel Values](#c2-empty-strings-and-sentinel-values)
  - [C3. Untyped Dicts and Missing Pydantic Models](#c3-untyped-dicts-and-missing-pydantic-models)
  - [C4. Unchecked Numeric Conversions](#c4-unchecked-numeric-conversions)
  - [C5. Implicit Unit Handling](#c5-implicit-unit-handling)
  - [C6. Missing Required Parameter Validation](#c6-missing-required-parameter-validation)
  - [C7. Functions Accepting Arbitrary Dicts](#c7-functions-accepting-arbitrary-dicts)
  - [C8. Frontend Validation Gaps](#c8-frontend-validation-gaps)
  - [C9. API Error Handling Gaps](#c9-api-error-handling-gaps)
  - [C10. Test Coverage Assessment](#c10-test-coverage-assessment)

---

## A. Existing Calculation Inventory

### A1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ Electron (main.cjs)                                             │
│   ├── Spawns python-backend/dist/main/main.exe (PyInstaller)    │
│   └── Loads React app (Vite, base: './')                        │
├─────────────────────────────────────────────────────────────────┤
│ React Frontend (electron-app/src/)                              │
│   ├── geotechnicalModules.js  → Module/category/function tree   │
│   ├── schemas/*.js            → Input field definitions         │
│   ├── SchemaForm.jsx          → Dynamic form renderer           │
│   ├── ResultsRenderer.jsx     → Plotly/table/image renderer     │
│   └── App.jsx                 → POST /api/execute dispatcher    │
├─────────────────────────────────────────────────────────────────┤
│ FastAPI Backend (python-backend/)                                │
│   ├── main.py                 → CORS, error handler, mount      │
│   ├── core/router.py          → POST /api/execute + CRUD        │
│   ├── core/registry.py        → 221 functions, dispatch engine  │
│   ├── core/wrappers.py        → 20 complex calculation wrappers │
│   ├── core/plotting_wrappers  → 3 visualization wrappers        │
│   ├── core/labtesting_wrappers→ 4 lab test wrappers             │
│   ├── core/state.py           → In-memory + disk state manager  │
│   └── core/schema_manager.py  → Override metadata system        │
├─────────────────────────────────────────────────────────────────┤
│ Groundhog Library (pip installed)                               │
│   └── 221 functions scanned via pkgutil.walk_packages()         │
└─────────────────────────────────────────────────────────────────┘
```

### A2. Registry & Execution Engine

**File:** `python-backend/core/registry.py` (~1030 lines)

The `Registry` class is the central execution engine:

| Component | Function | Description |
|-----------|----------|-------------|
| `_scan_library()` | Library discovery | Walks all `groundhog` submodules via `pkgutil.walk_packages()`, imports each, extracts public functions/classes via `inspect.getmembers()`, stores in `self.function_map` |
| `_sanitize(obj)` | Output serialization | Converts DataFrame→records, Series→dict, ndarray→list, np.generic→native, NaN/Inf→None, recursive dict/list sanitization |
| `_map_args(func, args)` | Input coercion | Inspects function signature, filters to expected params, coerces strings to float (except `Ngamma_theory`), parses comma-separated lists |
| `_parse_list(val)` | List parsing | Handles JSON arrays, comma-separated floats, comma-separated strings |
| `find_function(id)` | Lookup | Simple `self.function_map.get(function_id)` |
| `execute_function()` | Dispatch | Routes to special handlers or generic executor |

**Generic execution flow:**
1. Look up function → 2. Map args to signature → 3. Execute with `warnings.catch_warnings()` → 4. Sanitize output → 5. Attach warnings → 6. Return dict

### A3. Special-Case Handlers

These are hardcoded `if function_id == '...'` blocks in `execute_function()`:

| # | Function ID | Handler Category | Groundhog Dependency | Validation Present | State Access |
|---|-------------|-----------------|---------------------|-------------------|--------------|
| 1 | `SoilProfile` | Data object creation | `groundhog.general.soilprofile.SoilProfile` | File format check, column dedup, NaN fill | Stores in `state_manager` |
| 2 | `CalculationGrid` | Data object creation | `groundhog.general.soilprofile.CalculationGrid` | Profile existence check | Reads from `state_manager` |
| 3 | `PlasticityChart` | Lab test wrapper | `groundhog.siteinvestigation.labtesting.indextests` | List parsing | None |
| 4 | `PSDChart` | Lab test wrapper | `groundhog.siteinvestigation.labtesting.indextests` | List parsing | None |
| 5 | `roottimemethod` | Lab test wrapper | Custom (scipy) | List parsing, interactive mode | None |
| 6 | `logtimemethod` | Lab test wrapper | Custom (scipy) | List parsing, interactive mode | None |
| 7 | `PCPTProcessing` | Data object creation | `groundhog.siteinvestigation.insitutests.pcpt_processing` | ImportError fallback | Stores in `state_manager` |
| 8 | `SPTProcessing` | Data object creation | `groundhog.siteinvestigation.insitutests.spt_processing` | ImportError fallback | Stores in `state_manager` |
| 9 | `AGSConverter` | Data import | `groundhog.agsconversion` | File path validation | Stores in `state_manager` |
| 10 | `AGSConverter_convert_ags_group` | Data import | `groundhog.agsconversion` | Instance existence check | Reads from `state_manager` |
| 11 | `hardening_soil_drained_triaxial` | Constitutive model | `groundhog.constitutivemodels.HardeningSoil` | Warning capture | None |
| 12 | `parameter_selection_constant_value` | Eurocode 7 | `groundhog.standards.eurocode` | N≥2 check, CoV empty→NaN | None |
| 13 | `parameter_selection_linear_trend` | Eurocode 7 | `groundhog.standards.eurocode` | N≥2, len(data)==len(depths) | None |
| 14 | `eurocode7_factors` | Eurocode 7 | `groundhog.standards.eurocode` | None | None |
| 15 | `contactwidth` | Pipeline | `groundhog.pipelinescables.stability.penetration` | Numeric coercion | None |
| 16 | `embedment_drained` | Pipeline | Same | Numeric coercion, Ngamma_theory string | None |
| 17 | `embedment_undrained_method1` | Pipeline | Same | Numeric coercion | None |
| 18 | `embedment_undrained_method2` | Pipeline | Same | Numeric coercion | None |
| 19 | `lay_touchdown_factor` | Pipeline | Same | Numeric coercion | None |
| 20 | `penetratedarea` | Pipeline | Same | Numeric coercion | None |
| 21 | `consolidation_calculation` | Consolidation | `groundhog.consolidation.dissipation` | u₀ interpolation, node count | None |
| 22 | `consolidation_degree` | Consolidation | Same | Arg mapping | None |
| 23 | `pore_pressure_fourier` | Consolidation | Same | Arg mapping | None |
| 24 | `LogPlot` | Visualization | `core.plotting_wrappers` | Profile + column validation | Reads `state_manager` |
| 25 | `plot_with_log` | Visualization | `core.plotting_wrappers` | Profile validation | Reads `state_manager` |
| 26 | `LogPlotMatplotlib` | Visualization | `matplotlib` + `SoilProfile` | Column autodetect | Reads `state_manager` |
| 27 | `settlement_calculation` | Settlement | `groundhog.shallowfoundations.settlement` | Profile existence | Reads `state_manager` |
| 28-38 | Foundation/Pile IDs | Delegated wrappers | `core.wrappers.*` | Per-wrapper | Per-wrapper |

### A4. Wrapper Functions

**File:** `python-backend/core/wrappers.py` (~64KB, 20 wrappers)

| # | Wrapper Function | Groundhog Target | Input Validation | Null Checking | Error Handling |
|---|-----------------|-----------------|-----------------|---------------|----------------|
| 1 | `map_depth_properties_wrapper` | `parameter_mapping.map_depth_properties` | `isinstance` type check | State manager lookup | `ValueError` on wrong type |
| 2 | `offsets_wrapper` | `parameter_mapping.offsets` | `float()` cast (unguarded) | Default `False` for latlon | Propagates exceptions |
| 3 | `merge_two_dicts_wrapper` | `parameter_mapping.merge_two_dicts` | JSON parse | Default empty dict | Catches string inputs |
| 4 | `reverse_dict_wrapper` | `parameter_mapping.reverse_dict` | JSON parse | Default empty dict | Catches string inputs |
| 5 | `shallow_foundation_capacity_undrained_wrapper` | `ShallowFoundationCapacityUndrained` | Shape validation, float casts | Empty→`np.nan` for su_above | `warnings.catch_warnings()`, plot fallback |
| 6 | `shallow_foundation_capacity_drained_wrapper` | `ShallowFoundationCapacityDrained` | Shape validation, float casts | Defaults for factors | `warnings.catch_warnings()`, plot fallback |
| 7 | `effectivearea_circle_wrapper` | `effectivearea_circle_api` | Conflict resolution (e vs M/V) | Empty→`np.nan` | try/except → `{"error": ...}` |
| 8 | `effectivearea_rectangle_wrapper` | `effectivearea_rectangle_api` | Conflict resolution (e vs M) | Empty→`np.nan` | try/except → `{"error": ...}` |
| 9 | `axcap_calculation_wrapper` | `AxCapCalculation` | Profile existence | Empty→`np.nan` for optional | Stack trace on error |
| 10 | `debeer_calculation_wrapper` | `DeBeerCalculation` | Column existence, NaN drop | Full column validation | Per-depth try/except |
| 11 | `koppejan_calculation_wrapper` | `KoppejanCalculation` | Penetration ≤ zmax−4D | NaN drop, depth sort | Error on overpenetration |
| 12 | `lcpc_calculation_wrapper` | `LCPCAxcapCalculation` | Soil type classification | NaN drop, depth sort | `ValueError` guidance |
| 13 | `pile_settlement_curves_wrapper` | `pile_settlement_curves` | Float casts | ndarray/list handling | try/except → `{"error": ...}` |
| 14 | `pilegroupeffect_reesevanimpe_wrapper` | `pilegroupeffect_reesevanimpe` | `parse_float_list` helper | Defaults for all inputs | Catches exceptions |
| 15 | `reinforced_circularsection_inertia_wrapper` | `reinforced_circularsection_inertia` | Strict type casts (int/float) | Via type conversion | try/except → `{"error": ...}` |
| 16 | `expansion_cylinder_tresca_wrapper` | `expansion_cylinder_tresca` | Float/int coercion | Defaults for ν, radii | Formatted error on failure |
| 17 | `expansion_tresca_thicksphere_wrapper` | `expansion_tresca_thicksphere` | Float coercion | Defaults for ν, seed | Catches exceptions |
| 18 | `stress_cylinder_elastic_isotropic_wrapper` | `stress_cylinder_elastic_isotropic` | Single/array radius detection | Empty→`np.nan` for G | Formatted error on failure |
| 19 | `negativeskinfriction_pilegroup_zeevaertdebeer_wrapper` | `negativeskinfriction_pilegroup_zeevaertdebeer` | Column existence, array reversal | Profile emptiness check | JSON parse + ImportError |
| 20 | `piletest_chinkondler_wrapper` | `piletest_chinkondler` | Division-by-zero guard (Q > 1e-6) | Profile presence check | JSON parse + fitting errors |

**File:** `python-backend/core/plotting_wrappers.py` (297 lines, 3 wrappers)

| # | Wrapper | Purpose | Validation |
|---|---------|---------|------------|
| 1 | `find_soil_type_column` | Column autodetection | Searches 7 name variants, falls back to first object-dtype column |
| 2 | `plot_with_log_wrapper` | Multi-panel Plotly log | Profile existence, panel count padding, soil type column rename |
| 3 | `log_plot_wrapper` | Profile parameter plot | Parameter column existence validation with available columns listing |

**File:** `python-backend/core/labtesting_wrappers.py` (6KB, 4 wrappers)

| # | Wrapper | Purpose | Validation |
|---|---------|---------|------------|
| 1 | `plasticitychart_wrapper` | Plasticity chart (Casagrande) | List parsing for LL/PI |
| 2 | `psdchart_wrapper` | Particle size distribution | List parsing for grainsize/pctpassing |
| 3 | `roottimemethod_wrapper` | Taylor √t method | Interactive mode detection, scipy intersection |
| 4 | `logtimemethod_wrapper` | Casagrande log(t) method | Interactive mode detection, multi-point selection |

### A5. Frontend Module Tree

**File:** `electron-app/src/config/geotechnicalModules.js`

| Category | Sub-Modules | Functions | Total |
|----------|-------------|-----------|-------|
| **General** | Soil profiles, Plotting, AGS, Parameter mapping, Validation | 16 | 16 |
| **Site Investigation** | Phase relations (14), Categories (4), Correlations-All (3), Correlations-Cohesive (5), Correlations-Cohesionless (4), PCPT class (1), PCPT functions (34), SPT class (1), SPT functions (10), Lab sample prep (1), Lab index tests (2), Lab compressibility (2) | 81 | 81 |
| **Piles** | Unit skin friction (4), Unit end bearing (4), Axial capacity (1), De Beer (1), Koppejan (1), LCPC (1), Pile settlement (1), Lateral behaviour (2), Cavity expansion (3), Negative friction (1), Pile testing (1) | 20 | 20 |
| **Shallow Foundations** | Stress distributions (6), Capacity (15), Settlement (4) | 25 | 25 |
| **Consolidation** | Pumping tests (1), 1D consolidation (3) | 4 | 4 |
| **Excavations** | Earth pressure (3), Soilmix (2) | 5 | 5 |
| **Soil Dynamics** | Liquefaction (5), Cyclic behaviour (17), Dynamic properties (4), CPT liquefaction (14) | 40 | 40 |
| **Eurocode 7** | Parameter selection (2), Partial factors (1) | 3 | 3 |
| **Constitutive** | Cohesionless (1) | 1 | 1 |
| **Pipelines** | Pipeline stability (6) | 6 | 6 |
| **TOTAL** | | | **201** |

> [!NOTE]
> The frontend exposes 201 functions. The registry contains 221 functions. The 20 function gap consists of Groundhog functions scanned but not yet given frontend schemas/UI entries.

### A6. Frontend Schema Definitions

**Location:** `electron-app/src/features/calculations/schemas/`

21 schema files define input specifications for all 201 frontend-exposed functions:

| Schema File | Functions Covered | Input Format |
|-------------|-------------------|--------------|
| `general.js` | SoilProfile, CalculationGrid | `inputs[]` array |
| `ags.js` | AGSConverter, convert_ags_group | `inputs[]` array |
| `parameter_mapping.js` | get_projected_point, latlon_distance, map_depth_properties, offsets, merge/reverse dicts | `inputs[]` array |
| `validation.js` | check_layer_overlap, validate_* | `inputs[]` array |
| `plotting.js` | LogPlot, LogPlotMatplotlib, plot_with_log | `inputs[]` array |
| `classification.js` | 14 phase relation + 4 category functions | `properties{}` JSON Schema |
| `correlations.js` | 12 correlation functions | `properties{}` JSON Schema |
| `insitutests.js` | PCPTProcessing, SPTProcessing | `inputs[]` array |
| `siteinvestigation.js` | 44 PCPT + 10 SPT functions | `properties{}` JSON Schema (2600+ lines) |
| `labtesting.js` | PlasticityChart, PSDChart, undercompaction, root/logtime | `inputs[]` / `properties{}` |
| `deepfoundations.js` | 8 unit friction/bearing + AxCap, DeBeer, Koppejan, LCPC, pile settlement | `properties{}` / `inputs[]` |
| `cavity_expansion.js` | 3 cavity expansion functions | `properties{}` JSON Schema |
| `lateral.js` | pilegroupeffect, reinforced_circularsection | `properties{}` JSON Schema |
| `shallowfoundations.js` | 6 stress + 15 capacity functions | `properties{}` JSON Schema |
| `settlement.js` | 4 settlement functions | `properties{}` / `inputs[]` |
| `consolidation.js` | hydraulic conductivity, consolidation degree/calc, pore pressure | `properties{}` JSON Schema |
| `excavations.js` | 3 earth pressure + 2 soilmix functions | `properties{}` JSON Schema |
| `soildynamics.js` | 40 dynamics functions | `properties{}` JSON Schema |
| `eurocode.js` | constant_value, linear_trend, eurocode7_factors | `inputs[]` / `properties{}` |
| `constitutive.js` | hardening_soil_drained_triaxial | `properties{}` JSON Schema |
| `pipelines.js` | 6 pipeline functions | `properties{}` JSON Schema |

> [!IMPORTANT]
> Two schema formats coexist: `inputs[]` array (older) and `properties{}` JSON Schema (newer). `SchemaForm.jsx` normalizes both at render time. This duality must be resolved in Phase 2 when creating canonical schemas.

---

## B. Existing Data Inventory

### B1. Project Data & State Management

**File:** `python-backend/core/state.py`

| Aspect | Current Implementation |
|--------|----------------------|
| **Storage** | `self._objects` (dict: `obj_id → Object`) + `self._metadata` (dict: `obj_id → MetaDict`) |
| **Persistence** | JSON file `saved_objects.json` — only `SoilProfile` objects are persisted |
| **Object ID** | `str(uuid.uuid4())` generated on `store()` |
| **Metadata** | `{id, type, name, timestamp}` — no schema version, no units, no provenance |
| **Supported types** | `SoilProfile`, `CalculationGrid`, `PCPTProcessing`, `SPTProcessing`, `AGSConverter` |
| **Deserialization** | Reconstructs `SoilProfile(pd.DataFrame(raw_data))` from saved records |
| **Deletion** | Removes from memory and re-saves to disk |
| **No concurrency control** | Single-threaded FastAPI with synchronous dict operations |

### B2. Soil Profile Data

**Creation paths:**
1. **File upload** → `POST /api/objects/upload` → `registry.execute_function("general", "SoilProfile", {"data": tmp_path})`
2. **Raw data** → `POST /api/objects/create` → `registry.execute_function("general", "SoilProfile", {"raw_data": [...]})`
3. **Frontend modal** → `SoilProfileModal.jsx` → Interactive layer builder or file upload

**Column normalization (registry.py:198-226):**
- Renames `_kPa` → `[kPa]`, `_m` → `[m]`, `_kN_m3` → `[kN/m3]`, etc.
- Appends `[-]` to unitless numeric columns
- Deduplicates column names

**NaN handling:** `nan_strategy='fill'` → all NaN numeric values replaced with `0` (default behavior)

**Frontend layer builder columns:**
- Depth from [m], Depth to [m], Soil type, Unit weight [kN/m³], Total unit weight [kN/m³], Cohesion [kPa], Friction angle [deg], Water level [m]

### B3. CPT Data Handling

**Processing class:** `PCPTProcessing` → `groundhog.siteinvestigation.insitutests.pcpt_processing`
- Created with `title` and `waterunitweight` parameters
- Stored in `state_manager`
- 34 PCPT correlation functions available (normalisations, behaviour index, soil classification, shear strength, stiffness, Vs correlations)

**Column expectations for De Beer/Koppejan/LCPC calculations:**
- `qc [MPa]` — cone resistance
- `Depth [m]` or `Depth to [m]` — depth column
- `Soil type` — soil classification column
- `gamma [kN/m3]` — unit weight column

### B4. Borehole & SPT Data Handling

**Processing class:** `SPTProcessing` → `groundhog.siteinvestigation.insitutests.spt_processing`
- Created with `title` and `waterunitweight` parameters
- Stored in `state_manager`
- 10 SPT functions available (N60 correction, overburden correction, friction angle, relative density, undrained shear strength, Young's modulus)

### B5. AGS Import

**Two-step process:**
1. `AGSConverter` — Loads AGS file (v3.1 or v4), extracts group names, stores in `state_manager`
2. `AGSConverter_convert_ags_group` — Fetches stored instance, converts specific group to DataFrame records

**Frontend schema:** File upload (`.ags`), encoding selection, format version select

### B6. Report Generation & Export

**File:** `electron-app/src/utils/exportUtils.js`

| Export Type | Implementation |
|------------|----------------|
| **JSON** | `downloadJSON()` — Raw result blob |
| **CSV** | `downloadCSV()` — Papa.unparse with multi-trace Plotly→column conversion |
| **PDF** | `generatePDF()` — jsPDF with logo header, input parameter table, results tables, Plotly screenshot (html2canvas), warnings, engineering disclaimers, page numbering |

### B7. Schema Override System

**Files:** `python-backend/core/schema_manager.py` + `schema_overrides.json`

| Feature | Implementation |
|---------|----------------|
| **Per-field overrides** | label, description, unit, placeholder, imageUrl, validationRegex |
| **Per-function docs** | `_page_docs` key stores rich HTML documentation |
| **Asset upload** | Images stored to `assets/schema_images/`, served as static files |
| **Current overrides** | Circular Footing Stress, AxCap (annulus/circumference), Hardening Soil (constitutive model docs) |

---

## C. Existing Problems

### C1. None/null/NaN/Infinity Handling

> [!CAUTION]
> NaN values in soil profiles are silently replaced with `0` by default, which can produce physically meaningless calculations (e.g., zero friction angle, zero cohesion, zero unit weight).

| Location | Problem | Severity |
|----------|---------|----------|
| `registry.py:228-233` | `nan_strategy='fill'` replaces **all** NaN numeric values with `0` when creating SoilProfile | **CRITICAL** — zero friction angle/cohesion/unit weight silently accepted |
| `registry.py:99-101` | `_sanitize()` converts `NaN`→`None` and `Inf`→`None` silently | **MEDIUM** — information loss, downstream code may misinterpret |
| `wrappers.py:127-129` | Duplicate `_sanitize()` with same NaN→None conversion | **LOW** — redundant but consistent |
| `labtesting_wrappers.py:60-62` | `np.array(args.get('times'))` — if `times` is `None`, creates `np.array(None)` | **HIGH** — TypeError at calculation time |
| `labtesting_wrappers.py:124-126` | Same `None` vulnerability in `logtimemethod_wrapper` | **HIGH** |
| `nsf_wrapper_temp.py:27-30` | `float(layer.get('Depth [m]', 0))` — if value is explicit `None`, default `0` is bypassed | **MEDIUM** — `float(None)` raises TypeError |

### C2. Empty Strings and Sentinel Values

> [!WARNING]
> Empty strings from frontend form fields can reach calculation functions as-is. The only systematic guard is `if val is not None and val != ""` in `_map_args`, but whitespace-only strings pass through.

| Location | Problem | Severity |
|----------|---------|----------|
| `registry.py:128-137` | `_map_args`: whitespace-only strings (e.g. `"   "`) pass the `val != ""` check, `float("   ")` raises `ValueError`, raw whitespace string passed to Groundhog function | **HIGH** |
| `registry.py:485-489` | Manual `cov == '' or cov is None → float('nan')` check — reveals this is ad-hoc, not systematic | **MEDIUM** — pattern not generalized |
| Frontend `SchemaForm.jsx:368-397` | Non-required fields backspaced to empty send `""` to backend | **HIGH** — empty strings reach `_map_args` |
| Frontend `SchemaForm.jsx:265-276` | Typing `-` in number field sets `formData[name] = "-"` — submitting sends `"-"` as string | **HIGH** — `float("-")` raises ValueError in backend |
| Frontend `SchemaForm.jsx:522-526` | `column_select` default is `""` ("Select a column...") — can be submitted | **MEDIUM** |

### C3. Untyped Dicts and Missing Pydantic Models

> [!IMPORTANT]
> The entire API accepts unvalidated `dict` payloads. `pydantic.create_model` is imported but **never used** to create static models. No request or response schemas exist.

| Location | Problem | Severity |
|----------|---------|----------|
| `registry.py:9` | `from pydantic import create_model` — imported but unused | **INFO** |
| `router.py:15` | `POST /api/execute` accepts `request: dict = Body(...)` — no schema validation | **CRITICAL** — arbitrary JSON accepted |
| `router.py:80` | `POST /api/objects/create` accepts `data: dict = Body(...)` | **HIGH** |
| `router.py:99` | `POST /api/schema/override` accepts `data: dict = Body(...)` | **MEDIUM** |
| All wrappers | Input `args` is untyped `dict` — no compile-time or runtime type enforcement | **HIGH** |
| All responses | No response models — `_sanitize()` output is ad-hoc dict construction | **HIGH** |

### C4. Unchecked Numeric Conversions

> [!CAUTION]
> Numerous `float()` calls on user-provided values have no try/except protection. If the frontend sends `""`, `None`, `"-"`, or non-numeric strings, these raise unhandled `TypeError`/`ValueError` that propagate to the global 500 handler.

| File | Line(s) | Code | Risk |
|------|---------|------|------|
| `labtesting_wrappers.py` | 62 | `float(args.get('drainagelength'))` | `None`→TypeError |
| `labtesting_wrappers.py` | 126 | `float(args.get('drainagelength'))` | `None`→TypeError |
| `nsf_wrapper_temp.py` | 18-20 | `float(args.get('surcharge', 0))` | `""`→ValueError |
| `wrappers.py` | 54-56 | `float(args.get('x1'))` (6 calls) | `None`→TypeError |
| `registry.py` | 254 | `float(args.get('dz', 0.5))` | `""`→ValueError |
| `registry.py` | 294 | `float(args.get('waterunitweight', 10.25))` | `""`→ValueError |
| `registry.py` | 314 | `float(args.get('waterunitweight', 10.0))` | `""`→ValueError |
| `labtesting_wrappers.py` | 89-90, 158-163 | Direct `xy[0][0]` indexing | Shape not validated |

### C5. Implicit Unit Handling

> [!WARNING]
> Units are declared in frontend schema labels and Groundhog docstrings but are **never enforced programmatically**. No unit conversion or unit consistency checks exist anywhere in the pipeline.

| Aspect | Current State |
|--------|--------------|
| **Frontend schemas** | Units in `unit:` field or embedded in `title:` (e.g., `"Footing Radius (R) [m]"`) — display only |
| **Backend** | Column headers contain units (e.g., `qc [MPa]`, `Depth [m]`) — convention only |
| **Column normalization** | `registry.py:198-226` reformats suffixes to `[unit]` notation — cosmetic |
| **Runtime conversion** | Only 2 instances: `cv * 3600 * 24 * 365` in `labtesting_wrappers.py:108,185` (m²/s → m²/yr) — hardcoded |
| **Cross-function consistency** | Nothing prevents passing kPa where MPa is expected, or m where mm is expected |
| **Groundhog functions** | Assume specific units in docstrings but do not validate at runtime |

### C6. Missing Required Parameter Validation

| Location | Problem | Severity |
|----------|---------|----------|
| `_map_args()` | Only filters to expected parameter names — does not check if required params are present | **HIGH** |
| Generic handler | Calls `func(**func_args)` — missing required params raise Python `TypeError` at execution time, not at validation time | **HIGH** |
| Special handlers | Each has ad-hoc validation (some check profile existence, some don't check param presence) | **MEDIUM** — inconsistent |
| Frontend `handleSubmit` | Only checks `required` fields via HTML5 and custom regex — no range validation enforced | **HIGH** |

### C7. Functions Accepting Arbitrary Dicts

| Entry Point | What It Accepts | Risk |
|-------------|-----------------|------|
| `POST /api/execute` | `{"moduleId": any, "functionId": any, "args": any_dict}` | Arbitrary function invocation on any registered Groundhog function |
| `registry.execute_function()` | `args: dict` — no schema, no type checking | Type errors at runtime only |
| All wrappers | `args: dict` — per-wrapper ad-hoc `.get()` with inconsistent defaults | Missing keys cause KeyError or silent None propagation |
| `state_manager.store()` | `obj: Any, type_name: str` — stores any Python object | No type verification |

### C8. Frontend Validation Gaps

| Location | Problem | Severity |
|----------|---------|----------|
| `SchemaForm.jsx:636-645` | `min` and `max` attributes from schema are **never applied** to `<input>` elements — users can enter negative dimensions, friction angles > 90°, etc. | **CRITICAL** |
| `SchemaForm.jsx:203-219` | Optional inputs default to `undefined` or `""` — no coercion to `null` | **HIGH** |
| `SchemaForm.jsx:599-608` | List textareas allow empty strings, trailing commas, non-numeric content | **MEDIUM** |
| `SchemaForm.jsx:368-397` | `handleSubmit` only validates regex patterns — no range/type/completeness validation | **HIGH** |
| `SoilProfileModal.jsx` | Manual layer builder has no validation on entered values (can type "abc" for depth) | **HIGH** |

### C9. API Error Handling Gaps

| Location | Problem | Severity |
|----------|---------|----------|
| `SchemaForm.jsx:34-44` | `ObjectSelector` `fetch().then(res => res.json())` — does not check `res.ok`, 500 responses parsed as object lists | **HIGH** |
| `SchemaForm.jsx:136-149` | `fetchOverrides` does not check `res.ok` | **MEDIUM** |
| `SchemaForm.jsx:169-178` | `handleSaveOverride` ignores response entirely | **LOW** |
| `SchemaForm.jsx:240-248` | `fetchObjectDetails` does not check `res.ok` | **MEDIUM** |
| `App.jsx` `handleCalculate` | Wraps in try/catch but error message is generic `err.message` — no structured error handling | **MEDIUM** |

### C10. Test Coverage Assessment

| Test File | Coverage | What's Missing |
|-----------|----------|----------------|
| `tests/test_core.py` | 4 tests: registry loading, manual function, health endpoint, modules list | No calculation validation, no wrapper tests, no error path tests, no integration tests |
| `test_lab_testing.py` | 3 standalone tests: undercompaction, PlasticityChart, roottimemethod | Not integrated into pytest suite |
| `verify_registration.py` | Registration verification for 5 lab wrappers | Not a test — verification script |
| `verify_shallow_settlement.py` | Settlement workflow end-to-end | Not a test — verification script |
| **Frontend** | `electron-app/tests/` is empty | **Zero frontend tests** |

> [!CAUTION]
> **Test coverage is minimal.** Only 4 automated tests exist in the pytest suite, none of which test actual calculation correctness, error handling, or invalid input behavior. The frontend has zero tests.

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total registered Groundhog functions | 221 |
| Frontend-exposed functions | 201 |
| Special-case handlers in registry | 38 |
| Wrapper functions (wrappers.py) | 20 |
| Plotting wrappers | 3 |
| Lab testing wrappers | 4 |
| API endpoints | 9 |
| Frontend schema files | 21 |
| Automated tests | 4 |
| Pydantic models defined | 0 |
| Unit conversion functions | 0 |
| Unguarded `float()` calls | 10+ |
| Functions accepting untyped `dict` | All |

---

## Phase 0 Complete — Awaiting Review

> [!IMPORTANT]
> This audit is the Phase 0 deliverable. **No code changes have been made.** Awaiting user review and approval before proceeding to Phase 1 (Parameter Inventory).
>
> **Key findings requiring design decisions in Phase 1:**
> 1. The `nan_strategy='fill'` replacing NaN with 0 is the most dangerous default — should it be changed to error-on-NaN?
> 2. Two schema formats coexist (inputs[] and properties{}) — which becomes canonical?
> 3. No Pydantic models exist — should they be generated from existing schemas or written fresh?
> 4. 221 functions have no parameter contracts — prioritization strategy needed for Phase 2 (2-3 pilot functions).
> 5. The `POST /api/execute` endpoint accepts arbitrary function IDs — this is the GeoAI security boundary that Phase 6 (Tool Registry) must address.
