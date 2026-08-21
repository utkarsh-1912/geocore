"""
GeoAI Schema Factory & Complete Coverage Generator
Dynamically creates canonical Pydantic schemas and Tool Registry entries for 100% of Groundhog & GeoCore functions.
"""
import os
import json
import inspect
from typing import Dict, Any, Type, Optional, Tuple, List, Union
from pydantic import create_model, Field, ConfigDict

from core.geoai.schemas.base import GeoAIBaseModel
from core.geoai.schemas import SCHEMA_REGISTRY
from core.geoai.tool_registry import tool_registry, GeoAITool

# Load inventory metadata
_INVENTORY_PATH = os.path.join(os.path.dirname(__file__), 'parameter_inventory.json')
_INVENTORY_BY_FUNC: Dict[str, List[Dict[str, Any]]] = {}

if os.path.exists(_INVENTORY_PATH):
    try:
        with open(_INVENTORY_PATH, 'r', encoding='utf-8') as f:
            _inv_data = json.load(f)
            for item in _inv_data:
                _INVENTORY_BY_FUNC.setdefault(item['function_id'], []).append(item)
    except Exception:
        pass


def _map_python_type(type_str: str) -> Type:
    type_lower = (type_str or '').lower()
    if 'int' in type_lower:
        return int
    elif 'bool' in type_lower:
        return bool
    elif 'str' in type_lower or 'string' in type_lower:
        return str
    elif 'list' in type_lower or 'array' in type_lower:
        return Union[List[float], List[str], str]
    elif 'dict' in type_lower or 'json' in type_lower:
        return Union[Dict[str, Any], str]
    else:
        # Default numeric
        return Union[float, int, str]


def build_schema_for_function(func_name: str, func_obj: Any) -> Type[GeoAIBaseModel]:
    """Dynamically generate a canonical Pydantic model for any function."""
    fields: Dict[str, Any] = {}
    inv_params = {p['parameter_name']: p for p in _INVENTORY_BY_FUNC.get(func_name, [])}
    
    try:
        sig = inspect.signature(func_obj)
        parameters = sig.parameters
    except Exception:
        parameters = {}

    for p_name, param in parameters.items():
        if p_name in ('self', 'cls', 'args', 'kwargs'):
            continue

        inv_p = inv_params.get(p_name, {})
        py_type = _map_python_type(inv_p.get('python_type', 'float'))
        unit = inv_p.get('canonical_unit', '-')
        desc = inv_p.get('physical_meaning', f"{p_name.replace('_', ' ').title()}")
        
        # Determine default
        default_val = ...
        if param.default != inspect.Parameter.empty:
            default_val = param.default
            if isinstance(default_val, float) and (default_val != default_val):
                default_val = None
        elif inv_p.get('default_value'):
            default_val = inv_p.get('default_value')
            if default_val in ('null', 'nan', 'NaN'):
                default_val = None

        # Determine min / max bounds
        min_v = float(inv_p['min_value']) if inv_p.get('min_value') != '' else None
        max_v = float(inv_p['max_value']) if inv_p.get('max_value') != '' else None

        field_kwargs = {
            "description": desc,
            "json_schema_extra": {"unit": unit}
        }
        if min_v is not None:
            field_kwargs["ge"] = min_v
        if max_v is not None:
            field_kwargs["le"] = max_v

        # Nullable support
        if inv_p.get('is_nullable') or default_val is None:
            py_type = Optional[py_type]

        fields[p_name] = (py_type, Field(default=default_val, **field_kwargs))

    model_name = f"{''.join(w.capitalize() for w in func_name.split('_'))}Input"
    
    # Create dynamic model inheriting GeoAIBaseModel
    dyn_model = create_model(
        model_name,
        __base__=GeoAIBaseModel,
        __config__=ConfigDict(extra='allow'),  # Allow extra kwargs for dynamic Groundhog compatibility
        **fields
    )
    return dyn_model


def populate_full_coverage(registry_obj: Any):
    """
    Scans entire function_map and registers schemas and tools for 100% of functions.
    """
    for func_name, func_obj in registry_obj.function_map.items():
        # 1. Register in SCHEMA_REGISTRY if not already present
        if func_name not in SCHEMA_REGISTRY:
            try:
                dyn_input_model = build_schema_for_function(func_name, func_obj)
                SCHEMA_REGISTRY[func_name] = (dyn_input_model, None)
            except Exception as e:
                pass

        # 2. Register in Tool Registry if not already present
        if not tool_registry.get_tool(func_name):
            try:
                schema_pair = SCHEMA_REGISTRY.get(func_name)
                input_model = schema_pair[0] if schema_pair else build_schema_for_function(func_name, func_obj)
                output_model = schema_pair[1] if schema_pair else None
                
                module_name = getattr(func_obj, '__module__', 'groundhog')
                cat = module_name.split('.')[-1] if '.' in module_name else module_name
                doc = inspect.getdoc(func_obj) or f"Calculates {func_name.replace('_', ' ')} using Groundhog."
                # Extract first paragraph of docstring
                first_paragraph = doc.split('\n\n')[0].replace('\n', ' ').strip()

                tool = GeoAITool(
                    name=func_name,
                    description=first_paragraph,
                    category=cat,
                    input_model=input_model,
                    output_model=output_model,
                    func=func_obj
                )
                tool_registry._tools[func_name] = tool
            except Exception as e:
                pass
