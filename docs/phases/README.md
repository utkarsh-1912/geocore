# GeoAI Implementation — Phase Instructions

This folder contains the step-by-step instruction specifications for each phase of the GeoAI architecture implementation.

---

## Phase Roadmap

- [Phase 1: Parameter Inventory](file:///C:/Users/utkar/Downloads/Geocore/docs/phases/PHASE_1_PARAMETER_INVENTORY.md)
  - Generate full parameter inventory across all calculations with types, units, ranges, and nullability.
- [Phase 2: Canonical Schemas](file:///C:/Users/utkar/Downloads/Geocore/docs/phases/PHASE_2_CANONICAL_SCHEMAS.md)
  - Define strict Pydantic v2 schemas for pilot calculations with physics-based validation.
- [Phase 3: Validation Layer](file:///C:/Users/utkar/Downloads/Geocore/docs/phases/PHASE_3_VALIDATION_LAYER.md)
  - Implement the universal validation and sanitization boundary in Python backend.
- [Phase 4: Automated Testing](file:///C:/Users/utkar/Downloads/Geocore/docs/phases/PHASE_4_TESTS.md)
  - Implement comprehensive pytest suites for valid, invalid, sentinel, and boundary values.
- [Phase 5: Lazy Data Access Layer](file:///C:/Users/utkar/Downloads/Geocore/docs/phases/PHASE_5_DATA_ACCESS_LAYER.md)
  - Create on-demand project context and parameter resolver for soil profiles, CPT, and borehole data.
- [Phase 6: Tool Registry & Security Boundary](file:///C:/Users/utkar/Downloads/Geocore/docs/phases/PHASE_6_TOOL_REGISTRY.md)
  - Implement secure `@geoai_tool` registry preventing arbitrary code execution.
- [Phase 7: GeoAI Tool Schemas](file:///C:/Users/utkar/Downloads/Geocore/docs/phases/PHASE_7_GEOAI_SCHEMAS.md)
  - Generate standard tool-calling specifications for Gemma/SLM integration.
- [Phase 8: Expanded Coverage & Verification](file:///C:/Users/utkar/Downloads/Geocore/docs/phases/PHASE_8_EXPAND_COVERAGE.md)
  - Broaden schema coverage across all categories, end-to-end integration, and documentation.
