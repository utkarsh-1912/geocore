"""
Universal Geotechnical Input Sanitizer & Validator
"""
import difflib
import math
from typing import Dict, Any, List, Tuple, Optional
from pydantic import ValidationError

from core.geoai.exceptions import GeoAIValidationError
from core.geoai.schemas import get_schema

SENTINEL_STRINGS = {'-', '--', 'n/a', 'na', 'null', 'nil', 'undefined', 'none', ''}

def sanitize_raw_input(raw_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize raw dictionary payload before validation or legacy execution.
    - Strips string whitespace
    - Removes sentinel strings ('-', 'N/A', 'null', etc.)
    - Coerces numeric strings (e.g. '.35', '10', '2.5') to float/int
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
                # Attempt numeric coercion so strings like '.35' or '10' don't fail ge/le constraints
                try:
                    if '.' in v_stripped or 'e' in v_stripped.lower() or 'E' in v_stripped:
                        clean_args[k] = float(v_stripped)
                    else:
                        clean_args[k] = int(v_stripped)
                except ValueError:
                    clean_args[k] = v_stripped
        elif isinstance(v, float):
            if math.isnan(v) or math.isinf(v):
                raise GeoAIValidationError(f"Invalid numeric input for '{k}': {v} (NaN or Inf not allowed)")
            clean_args[k] = v
        else:
            clean_args[k] = v
    return clean_args


def accepted_parameter_keys(input_model: Any) -> Dict[str, str]:
    """{accepted key (field name or validation alias): canonical field name} for an input model."""
    if hasattr(input_model, 'geoai_accepted_keys'):
        return input_model.geoai_accepted_keys()
    return {name: name for name in getattr(input_model, 'model_fields', {})}


def unknown_parameter_details(input_model: Any, unknown_keys: List[str]) -> List[Dict[str, Any]]:
    """Structured 'unknown_parameter' error entries with the valid names and close matches."""
    accepted = accepted_parameter_keys(input_model)
    valid = list(getattr(input_model, 'model_fields', {}).keys())
    details = []
    for key in unknown_keys:
        suggestions = [accepted[m] for m in difflib.get_close_matches(str(key), list(accepted), n=3, cutoff=0.6)]
        details.append({
            "field": str(key),
            "message": f"Unknown parameter '{key}'",
            "input_value": None,
            "type": "unknown_parameter",
            "did_you_mean": list(dict.fromkeys(suggestions)),
            "valid_parameters": valid,
        })
    return details


def build_validation_error(function_id: str, input_model: Any, exc: ValidationError,
                           prefix: Optional[str] = None) -> GeoAIValidationError:
    """
    Convert a Pydantic ValidationError into a structured GeoAIValidationError.

    Unknown keys (``extra_forbidden``) are reported with the list of valid parameter
    names and close-match suggestions, so the agent/model can correct the call (§17).
    """
    unknown: List[str] = []
    details: List[Dict[str, Any]] = []
    for err in exc.errors():
        loc = err.get('loc', ())
        if err.get('type') == 'extra_forbidden' and loc:
            unknown.append(str(loc[0]))
            continue
        input_val = err.get('input', None)
        details.append({
            "field": " -> ".join(str(x) for x in loc),
            "message": err.get('msg', 'Validation error'),
            "input_value": str(input_val) if input_val is not None else None,
            "type": err.get('type'),
        })

    parts = []
    if unknown:
        unknown_details = unknown_parameter_details(input_model, unknown)
        hints = []
        for d in unknown_details:
            hint = f"'{d['field']}'"
            if d["did_you_mean"]:
                hint += " (did you mean " + " or ".join(f"'{s}'" for s in d["did_you_mean"]) + "?)"
            hints.append(hint)
        valid = unknown_details[0]["valid_parameters"]
        parts.append(f"unknown parameter(s) {', '.join(hints)}. "
                     f"Valid parameters: {', '.join(valid) if valid else '(none)'}")
        details = unknown_details + details
    parts.extend(f"{d['field']}: {d['message']}" for d in details if d.get("type") != "unknown_parameter")
    head = prefix or f"Validation failed for '{function_id}'"
    return GeoAIValidationError(f"{head}: " + "; ".join(parts), errors=details)


def validate_and_coerce_inputs(function_id: str, raw_args: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Any]]:
    """
    Validate and coerce input arguments for a geotechnical calculation (desktop UI path).

    Legacy compatibility: for schemas auto-generated from Groundhog signatures, keys that are
    not schema parameters are passed through unchanged (the UI special-case handlers in
    core.registry read extra keys such as 'raw_data' or 'nan_strategy'). The model-facing
    GeoAI Tool Registry (GeoAITool.invoke) is strict and rejects them.
    """
    # 1. Baseline sanitization & numeric coercion
    sanitized = sanitize_raw_input(raw_args)

    # 2. Check for canonical schema
    schema_pair = get_schema(function_id)
    if not schema_pair:
        return sanitized, None

    input_cls, _ = schema_pair
    passthrough: Dict[str, Any] = {}
    if getattr(input_cls, 'geoai_autogenerated', False) and isinstance(sanitized, dict):
        accepted = accepted_parameter_keys(input_cls)
        passthrough = {k: v for k, v in sanitized.items() if k not in accepted}
        sanitized = {k: v for k, v in sanitized.items() if k in accepted}
    try:
        instance = input_cls(**sanitized)
        # Convert back to dict for Groundhog execution
        validated_dict = instance.geoai_call_kwargs()
        validated_dict.update(passthrough)
        return validated_dict, instance
    except GeoAIValidationError:
        raise
    except ValidationError as e:
        raise build_validation_error(function_id, input_cls, e)
    except (TypeError, ValueError) as e:
        raise GeoAIValidationError(f"Validation failed for '{function_id}': {str(e)}")
