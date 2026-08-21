# Author: Utkarsh Gupta
# License: GPL v2

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys

# Add the current directory to path to ensure modules are found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
