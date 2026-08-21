# Phase 6: Tool Registry & Security Boundary

## 1. Objective
Establish a secure, explicitly whitelisted tool registry for GeoAI function calling that strictly prohibits arbitrary shell, Python, SQL, or filesystem execution.

## 2. Security Boundaries & Constraints
- **Strict Whitelist**: Only functions explicitly registered via `@geoai_tool` or in `GeoAIToolRegistry` can be invoked through the AI interface.
- **Forbidden Actions**:
  - Arbitrary Python `eval()` / `exec()`.
  - Shell / command line subprocess execution.
  - Arbitrary filesystem file writes or deletion outside designated scratch spaces.
  - Unsanitized dynamic database or SQL queries.
- **Deterministic Execution**:
  - Every tool has explicit typed input model, typed output model, description, and unit requirements.
  - Execution occurs through validated Pydantic models before passing to Groundhog.

## 3. Deliverables
- `python-backend/core/geoai/tool_registry.py`: `GeoAIToolRegistry`, `@geoai_tool` decorator, permission guards.
- Integration tests verifying security boundaries and execution isolation.
