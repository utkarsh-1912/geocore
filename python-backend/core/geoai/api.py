"""
FastAPI Endpoints for GeoAI Tool Discovery, Schema Export, and Tool Invocation
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from core.geoai.tool_registry import tool_registry
from core.geoai.slm_schema_generator import generate_openai_tool_definitions, generate_gemini_tool_definitions
from core.geoai.exceptions import GeoAIValidationError
# Ensure standard tool definitions are registered
import core.geoai.tool_definitions


router = APIRouter(prefix="/geoai", tags=["GeoAI"])


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


@router.post("/chat")
def geoai_chat(payload: Dict[str, Any] = Body(...)):
    """
    Offline Local Gemma Agent endpoint.
    Body format: {"prompt": str, "context": Optional[dict]}
    """
    from core.geoai.gemma_engine import gemma_engine
    prompt = payload.get("prompt", "")
    context = payload.get("context")

    if not prompt:
        raise HTTPException(status_code=400, detail="Field 'prompt' is required.")

    return gemma_engine.chat_and_execute(prompt, context)


@router.post("/autofill")
def geoai_autofill(payload: Dict[str, Any] = Body(...)):
    """
    Extracts structured parameters from unstructured text for a target calculation form.
    Body format: {"function_id": str, "raw_text": str}
    """
    from core.geoai.gemma_engine import gemma_engine
    function_id = payload.get("function_id", "")
    raw_text = payload.get("raw_text", "")

    if not function_id or not raw_text:
        raise HTTPException(status_code=400, detail="Fields 'function_id' and 'raw_text' are required.")

    return gemma_engine.autofill_form(function_id, raw_text)

