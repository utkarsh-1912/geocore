# Phase 5: Lazy Geotechnical Data Access Layer

## 1. Objective
Provide on-demand, lazy geotechnical project context resolution without loading entire monolithic datasets into calculation memory.

## 2. Requirements & Capabilities
- **`ProjectDataAccessor` / `ProjectContext`**:
  - Encapsulates access to soil stratigraphy, CPT soundings, borehole records, water levels, and structural definitions.
  - Queries layer properties at arbitrary depths `z` via interpolation or step lookup.
  - Slices depth intervals on demand (e.g. `get_interval(z_top, z_bottom)`).
  - Caches resolved properties in memory with LRU or lazy evaluation.
  - Prevents data mutation of underlying project state.
- **Integration with `StateManager`**:
  - Wrap existing `SoilProfile`, `CalculationGrid`, `PCPTProcessing`, and `SPTProcessing` objects in `ProjectDataAccessor` facades.

## 3. Deliverables
- `python-backend/core/geoai/data_access.py`: `ProjectContext`, `LayerSlice`, `CPTAccessor`, `BoreholeAccessor`.
- `python-backend/core/geoai/context_resolver.py`: Resolves calculation arguments directly from a project context ID.
