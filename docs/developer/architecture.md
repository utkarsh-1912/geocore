# GeoCore System Architecture

GeoCore is designed around a decoupled, microservice-inspired desktop architecture.

```
┌─────────────────────────────────────────────────────────────┐
│                       Electron Shell                        │
│   (Main Process: electron/main.cjs -> Preload: preload.js)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ IPC / Subprocess Control
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    React Web Application                    │
│   (Vite + React 19 + Tailwind CSS + Framer Motion + Plotly) │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP REST API (port 8000)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Python FastAPI Engine (Uvicorn)             │
│   (Registry -> Router -> Wrappers -> Groundhog Library)     │
└─────────────────────────────────────────────────────────────┘
```

## Backend Component Architecture

1. **`main.py`**: Entry point starting Uvicorn server on `127.0.0.1:8000`.
2. **`core/registry.py`**: Scans the `groundhog` package and dynamic schemas, registering execution endpoints.
3. **`core/router.py`**: Dynamic FastAPI routing mapping front-end JSON payloads to Python wrapper functions.
4. **`core/state.py`**: In-memory and disk state manager persisting `SoilProfile` and `CalculationGrid` objects across sessions.
5. **`core/manual_functions.py`**: User extension directory allowing custom Python algorithms to be added on the fly.
