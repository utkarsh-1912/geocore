# Phase 2: Canonical Pydantic Schemas

## 1. Objective
Establish standard, strict Pydantic models for geotechnical calculations, starting with selected pilot functions across different complexity tiers.

## 2. Pilot Calculation Functions
- **Tier 1 (Simple Scalar)**: `bulkunitweight` (Phase relations)
- **Tier 2 (Intermediate Mechanics)**: `stresses_circle` (Elastic stress distribution)
- **Tier 3 (Complex Wrapper / State)**: `shallow_foundation_capacity_undrained` (Bearing/sliding capacity)

## 3. Schema Architecture
- Base Model: `GeoAIBaseModel` with strict typing, extra fields forbidden, and sentinel filtering.
- Annotations: `Field(description=..., ge=..., le=..., json_schema_extra={"unit": "...", "symbol": "..."})`.
- Value pre-sanitization: Automatically intercept strings like `"-"`, `"N/A"`, `"null"`, `"undefined"`, whitespace strings before validation.
- Output Schemas: Typed result models replacing unstructured dicts for these pilot calculations.

## 4. Deliverables
- `python-backend/core/geoai/schemas/base.py`: Base class and common geotechnical field types (e.g., `Depth`, `Stress`, `UnitWeight`, `FrictionAngle`).
- `python-backend/core/geoai/schemas/classification.py`: Pilot schemas for phase relations.
- `python-backend/core/geoai/schemas/shallowfoundations.py`: Pilot schemas for stress distribution & capacity.
- `python-backend/core/geoai/schemas/__init__.py`: Schema exports and registry lookup.
