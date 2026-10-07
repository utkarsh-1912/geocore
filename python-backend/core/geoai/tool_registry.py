"""
GeoAI Tool Registry & Security Boundary
Provides strict, whitelisted registration and safe execution of geotechnical calculation tools.
Prohibits arbitrary Python, shell, SQL, or filesystem execution.
"""
from typing import Dict, Any, Callable, Optional, Type, List
import functools
import inspect
from pydantic import BaseModel, ValidationError

from core.geoai.schemas.base import GeoAIBaseModel
from core.geoai.exceptions import GeoAIValidationError


# A DataFrame up to this many rows goes to the model whole (as records); a longer one only as columns and a
# row count, so a plotted curve of hundreds of points cannot flood a small model's context (AGENTS.md section 9).
_MODEL_TABLE_ROWS = 50
_DISPLAY_MAX_TRACE_POINTS = 400


def _is_plotly(value: Any) -> bool:
    return hasattr(value, "to_plotly_json")


def _is_image(value: Any) -> bool:
    return _is_plotly(value) or hasattr(value, "savefig")


def _image_placeholder(key: Any, value: Any) -> Dict[str, Any]:
    """
    What the model reads in place of a figure object (which cannot be JSON-encoded): an id it can cite to have
    the UI render the image, and a description of what the image shows. The agent replaces ``image_id``
    with a turn-unique id when it has the image to show (GeoAIAgent._execute_tool_call).
    """
    if _is_plotly(value):
        from core.geoai.visuals import figure_details
        return {"image_id": str(key) if key is not None else None, "details": figure_details(value)}
    return {"image_id": None, "details": "Matplotlib figure (not available in chat)"}


def _json_safe(value: Any, key: Any = None) -> Any:
    """
    The tool result with the objects JSON cannot encode converted; everything JSON can already encode is
    returned unchanged. A figure becomes ``{"image_id", "details"}``, numpy numbers/arrays become plain Python,
    a DataFrame becomes records (or, past ``_MODEL_TABLE_ROWS`` rows, its columns and row count).
    """
    import numpy as np
    import pandas as pd

    if value is None or isinstance(value, (str, bool)):
        return value
    if _is_image(value):
        return _image_placeholder(key, value)
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return float(value)
    if isinstance(value, pd.DataFrame):
        if len(value) > _MODEL_TABLE_ROWS:
            return {"columns": [str(c) for c in value.columns], "n_rows": int(len(value))}
        return _json_safe(value.to_dict(orient="records"))
    if isinstance(value, pd.Series):
        return _json_safe(value.tolist())
    if isinstance(value, np.ndarray):
        return _json_safe(value.tolist())
    if isinstance(value, dict):
        return {k if isinstance(k, str) else str(k): _json_safe(v, k) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]
    return str(value)


def extract_display(res: Any) -> Dict[str, Any]:
    """
    The Plotly figures of a raw Groundhog result as JSON, for the UI only (the model gets an image id and details
    instead). Traces are decimated to a display size. Returns {"figures": {key: {"data", "layout"}}} or {}.
    """
    import json
    import numpy as np

    if not isinstance(res, dict):
        return {}
    figures: Dict[str, Any] = {}
    for key, value in res.items():
        if not _is_plotly(value):
            continue
        try:
            import plotly.io
            fig = json.loads(plotly.io.to_json(value))
        except Exception:
            continue
        for trace in fig.get("data", []):
            x, y = trace.get("x"), trace.get("y")
            if isinstance(x, list) and isinstance(y, list) and len(x) == len(y) > _DISPLAY_MAX_TRACE_POINTS:
                idx = np.unique(np.linspace(0, len(x) - 1, _DISPLAY_MAX_TRACE_POINTS).round().astype(int))
                trace["x"], trace["y"] = [x[i] for i in idx], [y[i] for i in idx]
        figures[str(key)] = {"data": fig.get("data", []), "layout": fig.get("layout", {})}
    return {"figures": figures} if figures else {}


class GeoAITool:
    """Encapsulates a verified geotechnical calculation tool."""
    def __init__(
        self,
        name: str,
        description: str,
        category: str,
        input_model: Type[GeoAIBaseModel],
        output_model: Optional[Type[GeoAIBaseModel]],
        func: Callable[..., Any],
        form_function: Optional[str] = None,
        interpretive: bool = False
    ):
        self.name = name
        self.description = description
        self.category = category
        self.input_model = input_model
        self.output_model = output_model
        self.func = func
        # Id of the matching GeoCore calculation form (the Groundhog function
        # name), so the UI can open the tool's call in the right form.
        self.form_function = form_function
        # The result is a classification/interpretation that needs a short explanation even when
        # the user did not ask for one (see agent._wants_model_explanation).
        self.interpretive = interpretive

    def target_callable(self) -> Callable[..., Any]:
        """
        The callable whose signature the input schema must match: the Groundhog function
        for thin forwarders built with ``groundhog_forwarder``, otherwise ``self.func``.
        """
        target = getattr(self.func, '__geoai_target__', None)
        if target:
            import importlib
            module_name, attr = target
            return getattr(importlib.import_module(module_name), attr)
        return self.func

    def invoke(self, raw_args: Dict[str, Any], include_display: bool = False) -> Dict[str, Any]:
        """
        Execute tool with strict validation boundary and attach complete provenance.
        With ``include_display`` the result also carries ``_display`` (see ``extract_display``): data for
        the UI that the caller must remove before the result reaches the model.
        Arbitrary Python execution, subprocesses, and filesystem modifications are strictly forbidden.
        """
        from core.geoai.provenance import create_calculation_provenance
        from core.geoai.validator import build_validation_error

        # 1. Validate inputs strictly via Pydantic model (unknown keys rejected, units normalised)
        try:
            validated_inputs = self.input_model(**raw_args)
        except ValidationError as e:
            raise build_validation_error(self.name, self.input_model, e,
                                         prefix=f"Tool '{self.name}' input validation failed")
        except GeoAIValidationError as e:  # includes GeoAIUnitError (dimension mismatch): keep its type
            e.message = f"Tool '{self.name}' input validation failed: {e.message}"
            e.args = (e.message,)
            raise
        except Exception as e:
            raise GeoAIValidationError(f"Tool '{self.name}' input validation failed: {str(e)}")

        call_args = validated_inputs.geoai_call_kwargs()

        # 2. Execute authoritative Groundhog function
        res = self.func(**call_args)

        # 3. Format / validate output if output model is defined
        output_data: Dict[str, Any] = {}
        if self.output_model:
            try:
                if isinstance(res, dict):
                    output_instance = self.output_model(**res)
                    output_data = output_instance.model_dump()
                else:
                    output_data = {"result": res}
            except Exception:
                output_data = dict(res) if isinstance(res, dict) else {"result": res}
        else:
            output_data = dict(res) if isinstance(res, dict) else {"result": res}
        display = extract_display(res) if include_display else {}
        output_data = _json_safe(output_data)
        if display:
            output_data["_display"] = display

        # 4. Attach calculation provenance metadata
        provenance = create_calculation_provenance(self.name, call_args)
        output_data["_provenance"] = provenance.to_dict()
        return output_data


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
        output_model: Optional[Type[GeoAIBaseModel]] = None,
        form_function: Optional[str] = None,
        interpretive: bool = False
    ) -> Callable:
        """Decorator to register a function as an authorized GeoAI tool."""
        def decorator(func: Callable) -> Callable:
            tool = GeoAITool(
                name=name,
                description=description,
                category=category,
                input_model=input_model,
                output_model=output_model,
                func=func,
                form_function=form_function,
                interpretive=interpretive
            )
            self._tools[name] = tool

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def get_tool(self, name: str) -> Optional[GeoAITool]:
        return self._tools.get(name)

    def tool_count(self) -> int:
        """Number of registered tools (cheap; list_tools() builds every JSON schema)."""
        return len(self._tools)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "form_function": t.form_function,
                "form_arg_map": dict(getattr(t.func, '__geoai_arg_map__', None) or {}),
                "input_schema": _clean_json_schema(t.input_model.model_json_schema()) if t.input_model else None,
                "output_schema": _clean_json_schema(t.output_model.model_json_schema()) if t.output_model else None
            }
            for t in self._tools.values()
        ]

    def invoke_tool(self, tool_name: str, args: Dict[str, Any], include_display: bool = False) -> Dict[str, Any]:
        """Invoke a tool by name with security checks."""
        tool = self.get_tool(tool_name)
        if not tool:
            raise GeoAIValidationError(f"Tool '{tool_name}' is not in the authorized GeoAI Tool Registry.")
        return tool.invoke(args, include_display=include_display)


def groundhog_forwarder(tool_name: str, module_name: str, func_name: str,
                        arg_map: Optional[Dict[str, str]] = None) -> Callable[..., Any]:
    """
    Build a thin tool function that forwards validated kwargs to a Groundhog function.
    Groundhog is imported lazily; the target is recorded so tests can check the tool's
    input schema against the real Groundhog signature (GeoAITool.target_callable).
    ``arg_map`` renames tool fields to Groundhog parameters where their meanings differ.
    """
    arg_map = dict(arg_map or {})

    def forward(**kwargs):
        import importlib
        target_kwargs = {arg_map.get(k, k): v for k, v in kwargs.items()}
        return getattr(importlib.import_module(module_name), func_name)(**target_kwargs)

    forward.__name__ = forward.__qualname__ = tool_name
    forward.__doc__ = f"Forwards to {module_name}.{func_name}."
    forward.__geoai_target__ = (module_name, func_name)
    forward.__geoai_arg_map__ = arg_map
    return forward


tool_registry = GeoAIToolRegistry()
geoai_tool = tool_registry.register
