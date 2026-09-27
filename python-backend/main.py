import sys
import os

# Add the current directory to path to ensure modules are found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Early import of core numeric libraries to prevent circular import in PyInstaller
import numpy as np
import scipy
import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.registry import Registry
from core.router import create_dynamic_router

app = FastAPI(title="Groundhog Desktop Backend", version="1.0.0")

# Allow CORS for Electron
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import logging
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("groundhog-backend")

# Global exception handler for CORS robustness
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception caught: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true"
        }
    )

# Initialize Registry (scans groundhog)
registry = Registry()

@app.get("/")
def root():
    return {"status": "Geotechnical Analysis Engine Running"}

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.get("/health/details")
def health_details():
    """Diagnostics for the System Health panel (cheap; never loads the GeoAI model)."""
    from core.diagnostics import collect_diagnostics
    return collect_diagnostics(functions_registered=len(registry.function_map))

@app.get("/modules")
def list_modules():
    return {k: v.__name__ if hasattr(v, '__name__') else str(v) for k, v in registry.function_map.items()}

from fastapi.staticfiles import StaticFiles
from core.geoai.api import router as geoai_router

app.include_router(create_dynamic_router(), prefix="/api")
app.include_router(geoai_router, prefix="/api")

# Mount assets directory
assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
if not os.path.exists(assets_dir):
    os.makedirs(assets_dir)
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

def _warm_heavy_imports():
    """Deferred start-up imports, run in the background once the server is listening.

    Same modules the backend used to import before listening: the calculation
    wrappers, every groundhog module in the registry, then the saved objects.
    """
    import importlib
    from core.function_manifest import warm_imports
    from core.state import state_manager

    for name in ("core.wrappers", "core.plotting_wrappers", "core.labtesting_wrappers"):
        try:
            importlib.import_module(name)
        except Exception as e:
            logger.warning(f"Warm-up import of {name} failed: {e}")
    warm_imports()
    state_manager.ensure_loaded()


def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Equivalent to uvicorn.run(app, host, port), plus background warm-up after listening."""
    from core.warmup import start_background_warmup

    server = uvicorn.Server(uvicorn.Config(app, host=host, port=port))
    start_background_warmup(_warm_heavy_imports, ready=lambda: server.started)
    try:
        server.run()
    except KeyboardInterrupt:
        pass
    if not server.started:
        sys.exit(3)  # uvicorn's STARTUP_FAILURE exit code, as uvicorn.run() does


if __name__ == "__main__":
    run_server()
