"""
GeoAI Tool Registry & Security Boundary
Provides strict, whitelisted registration and safe execution of geotechnical calculation tools.
Prohibits arbitrary Python, shell, SQL, or filesystem execution.
"""
from typing import Dict, Any, Callable, Optional, Type, List
import functools
import inspect
from pydantic import BaseModel

from core.geoai.schemas.base import GeoAIBaseModel
from core.geoai.exceptions import GeoAIValidationError


class GeoAITool:
    """Encapsulates a verified geotechnical calculation tool."""
    def __init__(
        self,
        name: str,
        description: str,
        category: str,
        input_model: Type[GeoAIBaseModel],
        output_model: Optional[Type[GeoAIBaseModel]],
        func: Callable[..., Any]
    ):
        self.name = name
        self.description = description
        self.category = category
        self.input_model = input_model
        self.output_model = output_model
        self.func = func

    def invoke(self, raw_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool with strict validation boundary.
        Arbitrary Python execution, subprocesses, and filesystem modifications are strictly forbidden.
        """
        # 1. Validate inputs strictly via Pydantic model
        try:
            validated_inputs = self.input_model(**raw_args)
        except Exception as e:
            raise GeoAIValidationError(f"Tool '{self.name}' input validation failed: {str(e)}")

        call_args = validated_inputs.model_dump(exclude_unset=False)

        # 2. Execute authoritative function
        res = self.func(**call_args)

        # 3. Format / validate output if output model is defined
        if self.output_model:
            try:
                # If res is dict with compatible fields
                if isinstance(res, dict):
                    output_instance = self.output_model(**res)
                    return output_instance.model_dump()
            except Exception:
                pass  # Fall back to raw sanitized dict

        if isinstance(res, dict):
            return res
        return {"result": res}


def _clean_json_schema(obj: Any) -> Any:
    import math
    if isinstance(obj, dict):
        return {k: _clean_json_schema(v) for k, v in obj.items() if not (isinstance(v, float) and (math.isnan(v) or math.isinf(v)))}
    elif isinstance(obj, list):
        return [_clean_json_schema(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj


class GeoAIToolRegistry:
    """Central whitelisted registry of GeoAI tools."""
    def __init__(self):
        self._tools: Dict[str, GeoAITool] = {}

    def register(
        self,
        name: str,
        description: str,
        category: str,
        input_model: Type[GeoAIBaseModel],
        output_model: Optional[Type[GeoAIBaseModel]] = None
    ) -> Callable:
        """Decorator to register a function as an authorized GeoAI tool."""
        def decorator(func: Callable) -> Callable:
            tool = GeoAITool(
                name=name,
                description=description,
                category=category,
                input_model=input_model,
                output_model=output_model,
                func=func
            )
            self._tools[name] = tool

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def get_tool(self, name: str) -> Optional[GeoAITool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "input_schema": _clean_json_schema(t.input_model.model_json_schema()) if t.input_model else None,
                "output_schema": _clean_json_schema(t.output_model.model_json_schema()) if t.output_model else None
            }
            for t in self._tools.values()
        ]

    def invoke_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a tool by name with security checks."""
        tool = self.get_tool(tool_name)
        if not tool:
            raise GeoAIValidationError(f"Tool '{tool_name}' is not in the authorized GeoAI Tool Registry.")
        return tool.invoke(args)


tool_registry = GeoAIToolRegistry()
geoai_tool = tool_registry.register
