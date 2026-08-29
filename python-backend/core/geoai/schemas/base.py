"""
GeoAI Base Schema Definitions and Field Validators
"""
from typing import Any, Optional, Dict, List, Union
import math
from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator


class GeoAIBaseModel(BaseModel):
    """
    Base model for all GeoAI calculation input and output schemas.
    - Strips whitespace
    - Intercepts invalid sentinel strings ('-', 'N/A', 'null', 'undefined')
    - Rejects NaN / Inf
    - Extra fields forbidden for strict validation
    """
    model_config = ConfigDict(
        extra='forbid',
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True
    )

    @model_validator(mode='before')
    @classmethod
    def pre_validate_and_sanitize(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
            
        from core.geoai.units import normalize_parameter_value, parse_value_with_unit, GeoAIUnitError
        
        sanitized = {}
        sentinel_strings = {'-', '--', 'n/a', 'na', 'null', 'nil', 'undefined', 'none', ''}
        
        # Map field units and string field types
        unit_map: Dict[str, str] = {}
        str_fields = set()
        if hasattr(cls, 'model_fields'):
            for f_name, field_info in cls.model_fields.items():
                unit = None
                if field_info.json_schema_extra and isinstance(field_info.json_schema_extra, dict):
                    unit = field_info.json_schema_extra.get('unit')
                if unit and unit != "-":
                    unit_map[f_name] = unit

                # Check if field is string
                if field_info.annotation in (str, Optional[str]):
                    str_fields.add(f_name)

                # Map validation aliases if present
                if field_info.validation_alias:
                    try:
                        aliases = []
                        if hasattr(field_info.validation_alias, 'choices'):
                            aliases = list(field_info.validation_alias.choices)
                        elif isinstance(field_info.validation_alias, (list, tuple, set)):
                            aliases = list(field_info.validation_alias)
                        elif isinstance(field_info.validation_alias, str):
                            aliases = [field_info.validation_alias]
                        
                        for alias in aliases:
                            if unit and unit != "-":
                                unit_map[alias] = unit
                            if field_info.annotation in (str, Optional[str]):
                                str_fields.add(alias)
                    except Exception:
                        pass
        
        for k, v in data.items():
            if isinstance(v, str):
                v_clean = v.strip()
                if v_clean.lower() in sentinel_strings:
                    sanitized[k] = None
                elif k in str_fields:
                    sanitized[k] = v_clean
                else:
                    # Deterministic unit normalization if target unit exists for this field
                    expected_unit = unit_map.get(k)
                    if expected_unit:
                        try:
                            sanitized[k] = normalize_parameter_value(v_clean, expected_unit=expected_unit, field_name=k)
                        except GeoAIUnitError:
                            raise
                        except Exception:
                            # Fallback numeric coercion
                            try:
                                if '.' in v_clean or 'e' in v_clean.lower() or 'E' in v_clean:
                                    sanitized[k] = float(v_clean)
                                else:
                                    sanitized[k] = int(v_clean)
                            except ValueError:
                                sanitized[k] = v_clean
                    else:
                        # No unit specified: attempt numeric coercion, else preserve string
                        try:
                            if '.' in v_clean or 'e' in v_clean.lower() or 'E' in v_clean:
                                sanitized[k] = float(v_clean)
                            else:
                                sanitized[k] = int(v_clean)
                        except ValueError:
                            sanitized[k] = v_clean
            elif isinstance(v, (int, float)):
                if math.isnan(v) or math.isinf(v):
                    raise ValueError(f"Parameter '{k}' cannot be NaN or Infinity.")
                sanitized[k] = v
            elif isinstance(v, list):
                sanitized[k] = v
            else:
                sanitized[k] = v
                
        return sanitized


class GeoAIOutputModel(GeoAIBaseModel):
    """
    Base model for calculation outputs.
    Allows extra auxiliary/intermediate fields returned by Groundhog without error.
    """
    model_config = ConfigDict(
        extra='ignore',
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True
    )


# Reusable Geotechnical Annotated Field Types
def GeotechnicalField(
    default: Any = ...,
    *,
    unit: str = "-",
    description: str = "",
    ge: Optional[float] = None,
    le: Optional[float] = None,
    gt: Optional[float] = None,
    lt: Optional[float] = None,
    **extra_kwargs: Any
) -> Any:
    """Helper to define a geotechnical parameter with standard engineering metadata."""
    schema_extra = {"unit": unit}
    return Field(
        default=default,
        description=description,
        ge=ge,
        le=le,
        gt=gt,
        lt=lt,
        json_schema_extra=schema_extra,
        **extra_kwargs
    )
