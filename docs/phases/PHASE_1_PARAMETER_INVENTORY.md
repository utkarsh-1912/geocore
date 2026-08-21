# Phase 1: Parameter Inventory & Metadata Specification

## 1. Objective
Extract and catalog every calculation parameter across the GeoCore and Groundhog library into a structured, machine-readable parameter inventory.

## 2. Requirements & Deliverables
- Scan all registered functions from Groundhog and custom wrappers.
- For each parameter, capture:
  - `module_id`: Category or submodule path.
  - `function_id`: Function or calculation identifier.
  - `parameter_name`: Exact Python argument identifier.
  - `python_type`: Inferred or documented type (`float`, `int`, `str`, `bool`, `list[float]`, `dict`, `SoilProfile`, etc.).
  - `canonical_unit`: SI / standard geotechnical unit (e.g. `kN/m3`, `kPa`, `MPa`, `deg`, `m`, `s`, `-`).
  - `display_unit`: Frontend presentation unit.
  - `allowed_range`: Minimum and maximum physically plausible bounds (e.g., friction angle `[0, 60]`, depth `[0, 2000]`).
  - `is_nullable`: Whether the parameter can be omitted or `None`.
  - `default_value`: Default value if defined.
  - `physical_meaning`: Concise engineering definition.
- Output formats:
  - `docs/PARAMETER_INVENTORY.csv`
  - `python-backend/core/geoai/parameter_inventory.json`

## 3. Implementation Steps
1. Create introspection script using AST and `inspect` on Groundhog functions and wrappers.
2. Cross-reference `module_info_structured.json` and existing frontend schemas for unit and range annotations.
3. Generate structured CSV and JSON inventories.
4. Verify coverage against all 221 functions in `Registry`.
