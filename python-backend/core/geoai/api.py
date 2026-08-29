# Author: Utkarsh Gupta
# License: GPL v3
"""
FastAPI Endpoints for GeoAI Tool Discovery, Schema Export, Tool Invocation,
Agent Chat (with SSE streaming), Model Registry Management, and Memory Lifecycle.
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Body, BackgroundTasks
from fastapi.responses import StreamingResponse

from core.geoai.tool_registry import tool_registry
from core.geoai.slm_schema_generator import generate_openai_tool_definitions, generate_gemini_tool_definitions
from core.geoai.exceptions import GeoAIValidationError
from core.geoai.lifecycle import lifecycle_manager
from core.geoai.model_downloader import list_available_models, download_model
from core.geoai.model_config import load_config, save_config
from core.geoai.agent import GeoAIAgent

# Ensure standard tool definitions are registered
import core.geoai.tool_definitions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/geoai", tags=["GeoAI"])


def _get_agent() -> GeoAIAgent:
    """Gets the GeoAI agent backed by the lifecycle-managed provider."""
    provider = lifecycle_manager.get_provider()
    return GeoAIAgent(provider=provider, registry=tool_registry)


# --- Tool Discovery & Schema Export Endpoints ---

@router.get("/tools")
def list_available_tools():
    """List all whitelisted geotechnical calculation tools with their schemas."""
    return {"tools": tool_registry.list_tools()}


@router.get("/tools/format/{format_type}")
def export_tool_schemas(format_type: str):
    """
    Export tool schemas in standardized LLM/SLM tool calling formats.
    Supported formats: 'openai', 'gemini', 'raw'.
    """
    if format_type == "openai":
        return {"tools": generate_openai_tool_definitions()}
    elif format_type == "gemini":
        return generate_gemini_tool_definitions()
    elif format_type == "raw":
        return {"tools": tool_registry.list_tools()}
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{format_type}'. Choose from: 'openai', 'gemini', 'raw'."
        )


# --- Tool Invocation Endpoint ---

@router.post("/invoke")
def invoke_geoai_tool(payload: Dict[str, Any] = Body(...)):
    """
    Execute a whitelisted GeoAI tool with validated parameters.
    Body format: {"tool_name": str, "args": dict}
    """
    tool_name = payload.get("tool_name")
    args = payload.get("args", {})

    if not tool_name:
        raise HTTPException(status_code=400, detail="Field 'tool_name' is required.")

    try:
        result = tool_registry.invoke_tool(tool_name, args)
        return {
            "status": "success",
            "tool_name": tool_name,
            "result": result
        }
    except GeoAIValidationError as ve:
        raise HTTPException(status_code=422, detail=ve.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


# --- Agent Chat Endpoint (with optional SSE streaming) ---

@router.post("/chat")
async def geoai_chat(payload: Dict[str, Any] = Body(...), stream: bool = Query(False)):
    """
    GeoAI Agent chat endpoint.
    Uses the configured ModelProvider (llama.cpp SLM or heuristic fallback)
    to reason over tools and generate grounded engineering responses.

    Body format: {"prompt": str, "context": Optional[dict]}
    Query params: stream=true for SSE streaming
    """
    prompt = payload.get("prompt", "")
    context = payload.get("context")

    if not prompt:
        raise HTTPException(status_code=400, detail="Field 'prompt' is required.")

    lifecycle_manager.touch()
    agent = _get_agent()

    if stream:
        def event_generator():
            try:
                for event in agent.run_stream(user_message=prompt, context=context):
                    yield event.to_sse()
            except Exception as e:
                logger.error(f"Streaming error in GeoAI chat: {e}")
                import json
                err_data = json.dumps({"type": "error", "content": str(e)})
                yield f"data: {err_data}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    else:
        response = agent.run(user_message=prompt, context=context)
        return response.to_dict()


# --- Model Management & Memory Lifecycle Endpoints ---

@router.get("/status")
def get_geoai_status():
    """Returns the current status of the GeoAI model provider and loaded weights."""
    provider = lifecycle_manager.get_provider()
    return {
        "status": "ready",
        "loaded": provider.is_loaded(),
        "model_info": provider.model_info(),
        "tools_registered": len(tool_registry.list_tools())
    }


@router.get("/models")
def get_available_models():
    """List all curated and installed local GGUF models."""
    return {"models": list_available_models()}


@router.post("/models/download")
def trigger_model_download(
    background_tasks: BackgroundTasks,
    payload: Dict[str, Any] = Body(...)
):
    """Triggers download of a curated model in the background."""
    model_id = payload.get("model_id", "qwen2.5-1.5b-instruct")
    set_active = payload.get("set_active", True)

    def _do_download():
        try:
            download_model(model_id, set_as_active=set_active)
            lifecycle_manager.unload()  # Reload on next access
        except Exception as e:
            logger.error(f"Background download failed for {model_id}: {e}")

    background_tasks.add_task(_do_download)
    return {"status": "download_started", "model_id": model_id}


@router.get("/models/download/status")
def get_model_download_status():
    """Returns the current background model download status."""
    from core.geoai.model_downloader import get_download_status
    return get_download_status()


@router.post("/models/autolink")
def trigger_auto_link():
    """Scans all desktop and system directories to auto-link any bundled or pre-installed GGUF model."""
    from core.geoai.model_config import auto_link_installed_model, find_gguf_models
    linked_path = auto_link_installed_model()
    all_found = [str(p) for p in find_gguf_models()]
    if linked_path:
        lifecycle_manager.unload()
        return {"status": "linked", "active_model": linked_path, "discovered_models": all_found}
    return {"status": "none_found", "discovered_models": []}



@router.post("/models/select")
def select_active_model(payload: Dict[str, Any] = Body(...)):
    """Switches the active local model path in configuration."""
    model_path = payload.get("model_path")
    provider = payload.get("provider", "llama_cpp")

    config = load_config()
    if model_path:
        config.model_path = model_path
    config.provider = provider
    save_config(config)

    # Unload previous provider instance to reload with new config
    lifecycle_manager.unload()

    return {"status": "model_selected", "config": config.__dict__}


@router.get("/memory")
def get_memory_info():
    """Returns desktop process RAM usage and model load status."""
    return lifecycle_manager.get_memory_status()


@router.post("/unload")
def unload_model():
    """Explicitly releases local model weights from RAM / VRAM."""
    return lifecycle_manager.unload()
