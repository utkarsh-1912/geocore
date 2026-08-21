"""
Tool Calling Schema Generator for Small Language Models (Gemma, Gemini, OpenAI compatible)
"""
from typing import Dict, Any, List
from core.geoai.tool_registry import tool_registry


def generate_openai_tool_definitions() -> List[Dict[str, Any]]:
    """
    Generate OpenAI-compatible tool specifications for Function Calling.
    Compatible with Gemma, vLLM, Ollama, and OpenAI API.
    """
    tools = []
    for tool in tool_registry._tools.values():
        param_schema = tool.input_model.model_json_schema()
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
        param_schema = tool.input_model.model_json_schema()
        declarations.append({
            "name": tool.name,
            "description": tool.description,
            "parameters": param_schema
        })
    return {"function_declarations": declarations}
