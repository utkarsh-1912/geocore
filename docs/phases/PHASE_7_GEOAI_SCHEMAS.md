# Phase 7: GeoAI Tool Calling Schemas for Gemma / SLM

## 1. Objective
Generate standard OpenAPI / JSON Schema function-calling definitions formatted for Gemma, Gemini, and local Small Language Models (SLMs).

## 2. Requirements & Formats
- Generates standard OpenAI/Gemini/Gemma tool-calling definitions:
  - `name`: Tool identifier.
  - `description`: Plaintext engineering description including relevant theory, equations, and constraints.
  - `parameters`: JSON Schema object with properties, types, descriptions, units, and required fields.
- Endpoints:
  - `GET /api/geoai/tools`: Returns catalog of all available GeoAI tools.
  - `GET /api/geoai/tools/{tool_name}`: Returns specific schema.
  - `POST /api/geoai/invoke`: Invokes tool with strict validation and formatted response.

## 3. Deliverables
- `python-backend/core/geoai/slm_schema_generator.py`: Generates standardized tool schemas.
- `python-backend/core/geoai/api.py`: GeoAI FastAPI routes for tool discovery and execution.
