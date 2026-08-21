"""
Universal Geotechnical Input Sanitizer & Validator
"""
import math
from typing import Dict, Any, Tuple, Optional
from pydantic import ValidationError

from core.geoai.exceptions import GeoAIValidationError
from core.geoai.schemas import get_schema

SENTINEL_STRINGS = {'-', '--', 'n/a', 'na', 'null', 'nil', 'undefined', 'none', ''}

def sanitize_raw_input(raw_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize raw dictionary payload before validation or legacy execution.
    - Strips string whitespace
    - Removes sentinel strings ('-', 'N/A', 'null', etc.)
    - Rejects NaN and Infinite float values
    """
    if not isinstance(raw_args, dict):
        return raw_args

    clean_args = {}
    for k, v in raw_args.items():
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.lower() in SENTINEL_STRINGS:
                clean_args[k] = None
            else:
                clean_args[k] = v_stripped
        elif isinstance(v, float):
            if math.isnan(v) or math.isinf(v):
                raise GeoAIValidationError(f"Invalid numeric input for '{k}': {v} (NaN or Inf not allowed)")
            clean_args[k] = v
        else:
            clean_args[k] = v
    return clean_args


def validate_and_coerce_inputs(function_id: str, raw_args: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Any]]:
    """
    Validate and coerce input arguments for a geotechnical calculation.
    
    If a canonical Pydantic schema is registered for `function_id`:
      - Runs strict Pydantic validation
      - Returns (dict_of_validated_args, pydantic_instance)
    
    If no canonical schema is registered:
      - Runs baseline sanitization (stripping whitespace, eliminating sentinel strings)
      - Returns (sanitized_args, None)
    """
    # 1. Baseline sanitization
    sanitized = sanitize_raw_input(raw_args)
    
    # 2. Check for canonical schema
    schema_pair = get_schema(function_id)
    if not schema_pair:
        return sanitized, None

    input_cls, _ = schema_pair
    try:
        instance = input_cls(**sanitized)
        # Convert back to dict for Groundhog execution
        # Exclude unset only if default values should take precedence
        validated_dict = instance.model_dump(exclude_unset=False)
        return validated_dict, instance
    except ValidationError as e:
        error_details = []
        for err in e.errors():
            loc = " -> ".join(str(x) for x in err.get('loc', []))
            msg = err.get('msg', 'Validation error')
            input_val = err.get('input', None)
            error_details.append({
                "field": loc,
                "message": msg,
                "input_value": str(input_val) if input_val is not None else None,
                "type": err.get('type')
            })
        summary_msg = f"Validation failed for '{function_id}': " + "; ".join(
            f"{d['field']}: {d['message']}" for d in error_details
        )
        raise GeoAIValidationError(summary_msg, errors=error_details)
