# Indian Standards (BIS) in GeoCore

Deterministic calculations from Indian Standards that Groundhog does not cover. They are available
in the desktop app (sidebar → **Indian Standards (BIS)**) and to GeoAI as validated tools.

```text
core/standards/bis/*.py      calculations (SI units, clause-cited, BISInputError for out-of-scope input)
        │
        ├── core.registry.Registry.function_map   → desktop forms (electron-app/.../schemas/bis.js)
        └── core/geoai/schemas/bis.py (SCHEMA_REGISTRY) → GeoAI Tool Registry (same names, strict units)
                                    core/geoai/tool_metadata.py → provenance (method / standard / assumptions)
```

## Source verification

Each provision was read from the code text, not from secondary summaries. Scanned tables and figures
were read from rendered page images.

| Code | Edition implemented | Source read | Status |
|---|---|---|---|
| IS 6403 | 1981 (Reaffirmed) + Amdt 1 (1984) | Public.Resource.Org scan | Implemented. **Under revision** by BIS CED 43/WG 7 (active Sept 2024). |
| IS 1904 | 2021 (fourth revision) | Internet Archive | Implemented. Table 1 changed from 1986: RC raft on plastic clay, 100 → 125 mm. |
| IS 1892 | 2021 (second revision) | Internet Archive | Implemented (cl. 5.6.2 Table 2, cl. 5.6.3). |
| IS 2131 | 1981 (Reaffirmed) | Public.Resource.Org scan | Implemented (cl. 3.6, Fig. 1). **IS 2131:2025** (14 July 2025) could not be read. Its reported energy correction is *not* encoded; optional N60 = N·ER/60 is labelled as ISO 22476-3. |
| IS 1498 | 1970 (Reaffirmed) | Public.Resource.Org scan | Implemented (cl. 3.5, Table 3, Fig. 1). No newer revision found. |
| IS 2950 (Pt 1) | 1981 (Reaffirmed) + Amdt 1 | Public.Resource.Org scan | Implemented (cl. 5.1–5.2, App. C). |
| IS 2720 Pt 3/1, 5, 17 | 1980, 1985, 1986 | Public.Resource.Org scans | Implemented (specific gravity, one-point LL, indices, permeability). |

Interpretations the code does not settle, each stated in the results:
- IS 6403 local shear evaluates the depth and inclination factors with φ′.
- IS 2131 Fig. 1 is represented by the Peck–Hanson–Thornburn curve it plots (checked within ±0.04 at 0.5–5 kgf/cm²).
- Water density and viscosity for the 27 °C corrections come from Tanaka (2001) and Vogel correlations.
- IS 1892 grid counts assume a rectangular built-up area.

## Implemented (milestone 1)

| Function / GeoAI tool | Clause |
|---|---|
| `bearing_capacity_is6403` | IS 6403 cl. 5.1–5.3, Tables 1–3; Nq, Nγ from Groundhog for φ 20–50° |
| `classify_soil_is1498` | IS 1498 cl. 3.5 |
| `spt_correction_is2131` | IS 2131 cl. 3.6 |
| `investigation_depth_is1892`, `borehole_layout_is1892` | IS 1892 cl. 5.6 |
| `permissible_settlement_is1904`, `stability_check_is1904` | IS 1904 Table 1, cl. 17.1 |
| `raft_rigidity_is2950` | IS 2950 (Pt 1) App. C |
| `specific_gravity_is2720`, `flow_index_is2720`, `liquid_limit_one_point_is2720`, `consistency_indices_is2720`, `permeability_constant_head_is2720`, `permeability_falling_head_is2720` | IS 2720 Pt 3/1, 5, 17 |

Tests: `tests/test_bis_standards.py` covers IS 6403 Table 1 at every tabulated φ, hand calculations,
the IS 1498 cl. 3.5.2 worked example, digitised IS 2131 Fig. 1, IS 1904 Table 1 rows, error paths,
and the UI and GeoAI wiring.

## Roadmap

**Milestone 2: project-aware workflows** (AGENTS.md §28–29)
1. `spt_correction_is2131` over a whole borehole from project SPT/AGS data (reuse `core/geoai/spt.py`,
   `ags.py`), keeping per-depth provenance.
2. IS 6403 driven from the project soil profile and recorded groundwater (`ProjectSoil`,
   `data_access.recorded_groundwater_depth`), as `tools_shallow.py` does for API RP 2GEO.
3. One-call "allowable bearing pressure" check: IS 6403 net safe value, then IS 8009 (Part 1)
   settlement, then IS 1904 Table 1 limits, reporting the governing criterion (IS 6403 cl. 6.1).
4. IS 1498 classification over AGS laboratory groups (GRAG/LLPL).

**Milestone 3: more codes** (read each from source before encoding)
- IS 8009 (Part 1):1976 settlement of shallow foundations (needed for item 3 above).
- IS 2911 (Part 1/Sec 1–4) pile capacity (static formula; Kd/K/δ tables); IS 2911 (Part 3):2021 under-reamed piles.
- IS 1893 (Part 1):2016 liquefaction screening (with existing CPT liquefaction tools).
- Remaining IS 2720 parts: grain size (Part 4) hydrometer, compaction (Parts 7/8), consolidation (Part 15), free swell (Part 40), CBR (Part 16).
- IS 6403 graphical methods (SPT Fig. 1 φ–N, cone Fig. 2, two-layer clay Fig. 3), only from verified digitisation.

**Milestone 4: GeoAI**
- Add BIS requests to the evaluation dataset (correct, ambiguous, missing groundwater, wrong units,
  "as per IS code" phrasing) and check selector recall for "IS 6403" or "Indian code" queries.
- Index the code texts the user holds licences for into local RAG (`research/indexer.py`) so answers
  can cite clauses. BIS texts are copyrighted; do not bundle them.

**Revision watch**
- When IS 6403 (revision) and IS 2131:2025 text become available, compare them clause by clause, add the
  new edition as an option that keeps the 1981 results reproducible, and update the tables here.
