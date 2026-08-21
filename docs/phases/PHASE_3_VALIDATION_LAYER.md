# Phase 3: Validation & Sanitization Layer

## 1. Objective
Implement a universal validation and sanitization boundary that protects calculation engines from invalid, corrupt, or unphysical inputs.

## 2. Requirements & Rules
- Intercept and reject sentinel invalid values:
  - Strings: `"-"`, `"--"`, `"N/A"`, `"n/a"`, `"nil"`, `"null"`, `"undefined"`, whitespace strings.
  - Floating point anomalies: `NaN`, `+Inf`, `-Inf`.
  - Type errors: string passed for numeric field when not parseable.
- Enforce physical geotechnical boundaries:
  - Friction angle: `0° <= phi <= 60°`
  - Poisson's ratio: `-1.0 < nu <= 0.5`
  - Void ratio: `e > 0`
  - Depths & dimensions: `>= 0`
  - Unit weights: `5.0 <= gamma <= 30.0 kN/m³` (with configurable bounds)
- Seamless integration:
  - Hook into `core/registry.py` (`execute_function`) and `core/router.py` (`POST /api/execute`).
  - Transparent fallback to legacy parameter mapper if no canonical schema is yet registered for a function, ensuring 100% backward compatibility.
  - Clear, structured validation error responses (`ValidationErrorDetail` with field name, bad value, expected type/range, and error message).

## 3. Deliverables
- `python-backend/core/geoai/validator.py`: Sanitizer, validator, and registry integration hooks.
- `python-backend/core/geoai/exceptions.py`: Custom validation exception hierarchy.
- Hook in `python-backend/core/registry.py` to validate before execution.
