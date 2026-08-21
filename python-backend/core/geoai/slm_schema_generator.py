import math
from typing import Dict, Any, List
from core.geoai.tool_registry import tool_registry


def _clean_json_schema(obj: Any) -> Any:
    """Recursively clean JSON schema dicts of NaN / Inf values."""
    if isinstance(obj, dict):
        return {k: _clean_json_schema(v) for k, v in obj.items() if not (isinstance(v, float) and (math.isnan(v) or math.isinf(v)))}
    elif isinstance(obj, list):
        return [_clean_json_schema(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj


def generate_openai_tool_definitions() -> List[Dict[str, Any]]:
    """
    Generate OpenAI-compatible tool specifications for Function Calling.
    Compatible with Gemma, vLLM, Ollama, and OpenAI API.
    """
    tools = []
    for tool in tool_registry._tools.values():
        param_schema = _clean_json_schema(tool.input_model.model_json_schema())
        # Clean up JSON schema for LLMs
        param_schema.pop("title", None)
        
        tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": param_schema
            }
        })
    return tools


def generate_gemini_tool_definitions() -> Dict[str, Any]:
    """
    Generate Google Gemini / Gemma function declarations.
    """
    declarations = []
    for tool in tool_registry._tools.values():
        param_schema = _clean_json_schema(tool.input_model.model_json_schema())
        declarations.append({
            "name": tool.name,
            "description": tool.description,
            "parameters": param_schema
        })
    return {"function_declarations": declarations}
