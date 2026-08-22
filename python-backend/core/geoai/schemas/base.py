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
            
        sanitized = {}
        sentinel_strings = {'-', '--', 'n/a', 'na', 'null', 'nil', 'undefined', 'none', ''}
        
        for k, v in data.items():
            if isinstance(v, str):
                v_clean = v.strip()
                if v_clean.lower() in sentinel_strings:
                    sanitized[k] = None
                else:
                    # Attempt numeric coercion for strings like '.35', '3', '-6'
                    try:
                        if '.' in v_clean or 'e' in v_clean.lower() or 'E' in v_clean:
                            sanitized[k] = float(v_clean)
                        else:
                            sanitized[k] = int(v_clean)
                    except ValueError:
                        sanitized[k] = v_clean
            elif isinstance(v, (float, int)):
                if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                    raise ValueError(f"Parameter '{k}' cannot be NaN or Infinity.")
                sanitized[k] = v
            elif isinstance(v, list):
                sanitized[k] = v
            else:
                sanitized[k] = v
                
        return sanitized


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
