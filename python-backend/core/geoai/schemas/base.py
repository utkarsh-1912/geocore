"""
GeoAI Base Schema Definitions and Field Validators
"""
from typing import Any, Optional, Dict, List, Tuple, Union, get_args, get_origin
import math
import weakref
from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator

# Field kinds used by the input sanitiser
_KIND_STR = "str"          # pure text field: strip only
_KIND_NUMERIC = "numeric"  # float / int (optionally Optional): unit-normalised
_KIND_TEXT = "text"        # anything else (unions with str/Any, bool, Literal, lists...)

_FIELD_SPEC_CACHE: "weakref.WeakKeyDictionary[type, Dict[str, Tuple[str, Optional[str], str]]]" = weakref.WeakKeyDictionary()


def _field_kind(annotation: Any) -> str:
    if annotation in (str, Optional[str]):
        return _KIND_STR
    args = [a for a in (get_args(annotation) if get_origin(annotation) is Union else (annotation,))
            if a is not type(None)]
    if args and all(a in (float, int) for a in args):
        return _KIND_NUMERIC
    return _KIND_TEXT


def _alias_names(field_info: Any) -> List[str]:
    alias = field_info.validation_alias
    if not alias:
        return []
    if hasattr(alias, 'choices'):
        return [c for c in alias.choices if isinstance(c, str)]
    if isinstance(alias, (list, tuple, set)):
        return [c for c in alias if isinstance(c, str)]
    if isinstance(alias, str):
        return [alias]
    return []


def _field_specs(cls: type) -> Dict[str, Tuple[str, Optional[str], str]]:
    """{accepted key (name or alias): (field name, unit or None, kind)} for an input model."""
    cached = _FIELD_SPEC_CACHE.get(cls)
    if cached is not None:
        return cached
    from core.geoai.units import normalize_unit_str
    specs: Dict[str, Tuple[str, Optional[str], str]] = {}
    for f_name, field_info in getattr(cls, 'model_fields', {}).items():
        unit = None
        if isinstance(field_info.json_schema_extra, dict):
            unit = field_info.json_schema_extra.get('unit')
        if not unit or normalize_unit_str(unit) in ('-', 'dimensionless'):
            unit = None
        spec = (f_name, unit, _field_kind(field_info.annotation))
        specs[f_name] = spec
        for alias in _alias_names(field_info):
            specs.setdefault(alias, spec)
    _FIELD_SPEC_CACHE[cls] = specs
    return specs


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

    @classmethod
    def geoai_accepted_keys(cls) -> Dict[str, str]:
        """Map every accepted input key (field name + validation aliases) to its field name."""
        return {k: spec[0] for k, spec in _field_specs(cls).items()}

    @model_validator(mode='before')
    @classmethod
    def pre_validate_and_sanitize(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        from core.geoai.units import normalize_parameter_value, parse_value_with_unit, GeoAIUnitError

        sanitized = {}
        sentinel_strings = {'-', '--', 'n/a', 'na', 'null', 'nil', 'undefined', 'none', ''}
        specs = _field_specs(cls)

        for k, v in data.items():
            if isinstance(v, str):
                v_clean = v.strip()
                _, unit, kind = specs.get(k, (None, None, _KIND_TEXT))
                if v_clean.lower() in sentinel_strings:
                    sanitized[k] = None
                elif kind == _KIND_STR:
                    sanitized[k] = v_clean
                elif kind == _KIND_NUMERIC or unit:
                    # Deterministic unit normalisation (units.py). Unparseable text is left for
                    # Pydantic to reject (numeric fields) or kept as text (text-capable fields).
                    try:
                        parse_value_with_unit(v_clean)
                    except GeoAIUnitError:
                        sanitized[k] = v_clean
                        continue
                    sanitized[k] = normalize_parameter_value(v_clean, expected_unit=unit or "-", field_name=k)
                else:
                    # Text-capable field without a unit: attempt numeric coercion, else preserve string
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
