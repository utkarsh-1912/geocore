# Author: Utkarsh Gupta
# License: GPL v3
"""
FastAPI Endpoints for GeoAI Tool Discovery, Schema Export, Tool Invocation,
Agent Chat (with SSE streaming), Model Registry Management, and Memory Lifecycle.
"""
import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Body, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool

from core.geoai.tool_registry import tool_registry
from core.geoai.slm_schema_generator import generate_openai_tool_definitions, generate_gemini_tool_definitions
from core.geoai.exceptions import GeoAIValidationError
from core.geoai.lifecycle import lifecycle_manager
from core.geoai.model_downloader import list_available_models, download_model, DEFAULT_MODEL_ID
from core.geoai.model_config import load_config, save_config
from core.geoai.agent import GeoAIAgent
from core.geoai.multi_agent import MultiAgentOrchestrator
from core.geoai.model_provider import GenerationCancelled

# Ensure standard tool definitions are registered
import core.geoai.tool_definitions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/geoai", tags=["GeoAI"])

# How often a streaming chat checks whether its client is still connected (seconds).
DISCONNECT_POLL_S = 0.5
# A streaming chat sends an SSE comment this often while the model is busy (seconds).
HEARTBEAT_S = 5.0


def _get_agent():
    """Gets the GeoAI agent backed by the lifecycle-managed provider (multi-agent unless disabled)."""
    provider = lifecycle_manager.get_provider()
    if load_config().multi_agent:
        return MultiAgentOrchestrator(provider=provider, registry=tool_registry)
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


# --- Calculation Explanation Endpoints (for the "Formula & Derivation" card, not the chat) ---

@router.post("/explain")
def explain_calculation_result(payload: Dict[str, Any] = Body(...)):
    """
    Deterministic explanation of one already-computed result: method/standard (from
    TOOL_METADATA), the formula straight from the groundhog function's docstring, and the
    substituted inputs/outputs. No model call, always available, never fabricated.

    Body format: {"function_id": str, "args": dict, "results": dict}
    """
    from core.geoai.calculation_explainer import explain_calculation
    function_id = payload.get("function_id")
    if not function_id:
        raise HTTPException(status_code=400, detail="Field 'function_id' is required.")
    return explain_calculation(function_id, payload.get("args"), payload.get("results"))


@router.post("/explain/narrate")
def narrate_calculation_result(payload: Dict[str, Any] = Body(...)):
    """
    Short plain-language narration of an /explain result, from the lifecycle-managed local model.
    Meant to be called separately from (and after) /explain so the deterministic card renders
    immediately; this one can take a few seconds on a cold or CPU-bound model.

    Body format: same as /explain.
    """
    from core.geoai.calculation_explainer import explain_calculation, narrate_explanation
    function_id = payload.get("function_id")
    if not function_id:
        raise HTTPException(status_code=400, detail="Field 'function_id' is required.")

    provider = lifecycle_manager.get_provider()
    if provider.model_info().get("provider") == "heuristic":
        return {"narration": None, "reason": "No local model is installed — install one in the GeoAI model manager to get a plain-language narration."}

    lifecycle_manager.touch()
    explanation = explain_calculation(function_id, payload.get("args"), payload.get("results"))
    try:
        narration = narrate_explanation(explanation, provider)
    except GenerationCancelled:
        return {"narration": None, "reason": "cancelled"}
    return {"narration": narration or None}


# --- Agent Chat Endpoint (with optional SSE streaming) ---

def _with_project_context(context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Attach the current project (compact stratigraphy + groundwater) unless the caller passed one.

    Only when the project has a soil profile or a recorded groundwater level: an empty summary
    would cost prompt tokens on a CPU for nothing.
    """
    context = dict(context or {})
    if "project_context" in context:
        return context
    try:
        from core.geoai.project_soil import load_project_context
        project = load_project_context()
    except Exception as e:
        logger.warning(f"GeoAI: project context unavailable: {e}")
        return context
    if project.list_profile_names() or getattr(project, "water_table_depth", None) is not None:
        context["project_context"] = project
    return context


@router.post("/chat")
def geoai_chat(request: Request, payload: Dict[str, Any] = Body(...), stream: bool = Query(False)):
    """
    GeoAI Agent chat endpoint.
    Uses the configured ModelProvider (llama.cpp SLM or heuristic fallback)
    to reason over tools and generate grounded engineering responses.

    Body format: {"prompt": str, "context": Optional[dict], "history": Optional[list]}
    history items: {"role": "user"|"assistant", "content": str, "tool": {"name", "arguments", "result"}?}
    Query params: stream=true for SSE streaming
    """
    prompt = payload.get("prompt", "")
    context = _with_project_context(payload.get("context"))
    history = payload.get("history")
    if history is not None and not isinstance(history, list):
        raise HTTPException(status_code=400, detail="Field 'history' must be a list.")

    if not prompt:
        raise HTTPException(status_code=400, detail="Field 'prompt' is required.")

    lifecycle_manager.touch()
    agent = _get_agent()

    if stream:
        def event_generator():
            try:
                for event in agent.run_stream(user_message=prompt, context=context, history=history):
                    yield event.to_sse()
            except GenerationCancelled as e:
                yield f"data: {json.dumps({'type': 'cancelled', 'content': str(e)})}\n\n"
            except Exception as e:
                logger.error(f"Streaming error in GeoAI chat: {e}")
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

        async def disconnect_aware_stream():
            # The server only notices a closed connection when it next sends a chunk, and the
            # model may compute for minutes before the first one (prompt processing on a laptop
            # CPU). Poll for the disconnect meanwhile and abort the model call, so a closed
            # window or Stop does not leave the CPU busy and the model locked for no one.
            events = event_generator()
            finished = False
            try:
                while True:
                    pending = asyncio.ensure_future(run_in_threadpool(next, events, None))
                    last_sent = time.monotonic()
                    while not pending.done():
                        await asyncio.wait({pending}, timeout=DISCONNECT_POLL_S)
                        if not pending.done() and await request.is_disconnected():
                            return
                        if not pending.done() and time.monotonic() - last_sent >= HEARTBEAT_S:
                            # SSE comment: keeps the connection visibly alive through a long
                            # model call, so the client can tell "busy" from "dead".
                            last_sent = time.monotonic()
                            yield ": ping\n\n"
                    chunk = pending.result()
                    if chunk is None:
                        finished = True
                        return
                    yield chunk
            finally:
                if not finished:
                    lifecycle_manager.cancel()

        return StreamingResponse(
            disconnect_aware_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    else:
        try:
            response = agent.run(user_message=prompt, context=context, history=history)
        except GenerationCancelled as e:
            raise HTTPException(status_code=409, detail=str(e))
        return response.to_dict()


@router.post("/cancel")
def cancel_geoai_chat():
    """Stops the GeoAI request in progress (Stop button); the model stays loaded."""
    return lifecycle_manager.cancel()


# --- Project Context Endpoints (recorded groundwater level, what GeoAI sees of the project) ---

def _groundwater_payload(depth: Optional[float]) -> Dict[str, Any]:
    from core.geoai.data_access import GROUNDWATER_PROVENANCE
    return {
        "groundwater_depth_m": depth,
        "unit": "m",
        "reference": "depth below ground level",
        "status": "recorded" if depth is not None else "not recorded",
        "provenance": GROUNDWATER_PROVENANCE if depth is not None else None,
    }


@router.get("/project/groundwater")
def get_project_groundwater():
    """The recorded project groundwater depth [m below ground level]; null when not recorded."""
    from core.geoai.data_access import recorded_groundwater_depth
    return _groundwater_payload(recorded_groundwater_depth())


@router.put("/project/groundwater")
def set_project_groundwater(payload: Dict[str, Any] = Body(...)):
    """
    Records the project groundwater depth.
    Body: {"groundwater_depth_m": number >= 0 or null, "unit": "m" (optional)}; null clears it
    back to "not recorded".
    """
    from core.geoai.data_access import record_groundwater_depth
    if "groundwater_depth_m" not in payload:
        raise HTTPException(status_code=422, detail={
            "status": "ValidationError",
            "error": "Field 'groundwater_depth_m' is required [m below ground level]; null clears the recorded level.",
            "details": [{"field": "groundwater_depth_m", "type": "missing_parameter", "unit": "m"}]})
    try:
        depth = record_groundwater_depth(payload["groundwater_depth_m"], payload.get("unit") or "m")
    except GeoAIValidationError as ve:
        raise HTTPException(status_code=422, detail=ve.to_dict())
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"The groundwater level could not be saved: {e}")
    return _groundwater_payload(depth)


@router.get("/project/context")
def get_project_context():
    """
    What GeoAI reads from the current project: the recorded groundwater level, the layered soil
    profiles, the CPTs (compact listing, no raw data) and the compact context text.
    """
    from core.geoai.project_soil import load_project_context
    import core.geoai.tools_cpt_piles as cpt_tools
    ctx = load_project_context()
    cpts = cpt_tools.list_project_cpts()
    return {
        "groundwater": _groundwater_payload(ctx.water_table_depth),
        "soil_profiles": ctx.list_profile_names(),
        "cpts": cpts["cpts"],
        "unusable_cpt_sources": cpts["unusable_sources"],
        "cpt_note": cpts["note"],
        "compact_context": ctx.get_compact_context_string(),
    }


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
    """List all curated and installed local GGUF models, and the path of the active one (may be a custom GGUF)."""
    from core.geoai.model_downloader import get_active_model_path
    return {"models": list_available_models(), "active_model_path": get_active_model_path()}


@router.post("/models/download")
def trigger_model_download(
    background_tasks: BackgroundTasks,
    payload: Dict[str, Any] = Body(...)
):
    """Triggers download of a curated model in the background."""
    model_id = payload.get("model_id", DEFAULT_MODEL_ID)
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


@router.post("/warmup")
def warm_up_model():
    """
    Loads the local model in the background (call when the GeoAI panel opens) so the first
    question does not wait for the model load. Returns immediately; the idle timeout still
    releases the weights when GeoAI is not used.
    """
    return lifecycle_manager.warm_up(background=True)


@router.get("/memory")
def get_memory_info():
    """Returns desktop process RAM usage and model load status."""
    return lifecycle_manager.get_memory_status()


@router.post("/unload")
def unload_model():
    """Explicitly releases local model weights from RAM / VRAM."""
    return lifecycle_manager.unload()
