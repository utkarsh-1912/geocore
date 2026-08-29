# Author: Utkarsh Gupta
# License: GPL v3
"""
Deterministic Geotechnical Unit Conversion and Normalization Engine.
Provides dimension verification, unit parsing, and conversion for all
standard geotechnical engineering calculations.
"""

import math
import re
from enum import Enum
from typing import Any, Dict, Optional, Set, Tuple, Union

from core.geoai.exceptions import GeoAIUnitError


class UnitDimension(str, Enum):
    PRESSURE = "pressure"                      # Base: kPa
    UNIT_WEIGHT = "unit_weight"                # Base: kN/m3
    FORCE = "force"                            # Base: kN
    FORCE_PER_LENGTH = "force_per_length"      # Base: kN/m
    LENGTH = "length"                          # Base: m
    ANGLE = "angle"                            # Base: deg
    VELOCITY = "velocity"                      # Base: m/s (includes permeability / hydraulic conductivity)
    PERMEABILITY = "velocity"                  # Alias for velocity dimension [L/T]
    TIME = "time"                              # Base: s
    AREA = "area"                              # Base: m2
    VOLUME = "volume"                          # Base: m3
    PERCENT = "percent"                        # Base: % (0-100) or ratio (0-1)
    DIMENSIONLESS = "dimensionless"            # Base: -


# Exact physical constants
GRAVITY_G = 9.80665              # m/s2
WATER_DENSITY_RHO = 1000.0       # kg/m3
WATER_UNIT_WEIGHT = 9.80665      # kN/m3


# Multipliers to convert a given unit TO the base unit for its dimension
# value_in_base = raw_value * CONVERSION_TO_BASE[unit]
UNIT_TAXONOMY: Dict[UnitDimension, Dict[str, float]] = {
    UnitDimension.PRESSURE: {
        "kpa": 1.0,
        "kn/m2": 1.0,
        "kn/m^2": 1.0,
        "mpa": 1000.0,
        "mn/m2": 1000.0,
        "mn/m^2": 1000.0,
        "gpa": 1000000.0,
        "pa": 0.001,
        "n/m2": 0.001,
        "n/m^2": 0.001,
        "n/mm2": 1000.0,
        "n/mm^2": 1000.0,
        "bar": 100.0,
        "mbar": 0.1,
        "atm": 101.325,
        "psi": 6.894757293168361,
        "lb/in2": 6.894757293168361,
        "lb/in^2": 6.894757293168361,
        "lbf/in2": 6.894757293168361,
        "lbf/in^2": 6.894757293168361,
        "psf": 0.04788025898033584,
        "lb/ft2": 0.04788025898033584,
        "lb/ft^2": 0.04788025898033584,
        "lbf/ft2": 0.04788025898033584,
        "lbf/ft^2": 0.04788025898033584,
        "ksf": 47.88025898033584,
        "kip/ft2": 47.88025898033584,
        "kip/ft^2": 47.88025898033584,
        "kips/ft2": 47.88025898033584,
        "tsf": 95.76051796067168,
        "ton/ft2": 95.76051796067168,
        "tons/ft2": 95.76051796067168,
    },
    UnitDimension.UNIT_WEIGHT: {
        "kn/m3": 1.0,
        "kn/m^3": 1.0,
        "mn/m3": 1000.0,
        "mn/m^3": 1000.0,
        "n/m3": 0.001,
        "n/m^3": 0.001,
        "kg/m3": GRAVITY_G / 1000.0,            # 1 kg/m3 = 0.00980665 kN/m3
        "kg/m^3": GRAVITY_G / 1000.0,
        "g/cm3": GRAVITY_G,                    # 1 g/cm3 = 1000 kg/m3 = 9.80665 kN/m3
        "g/cm^3": GRAVITY_G,
        "t/m3": GRAVITY_G,                     # 1 t/m3 = 9.80665 kN/m3
        "t/m^3": GRAVITY_G,
        "tonne/m3": GRAVITY_G,
        "tonnes/m3": GRAVITY_G,
        "pcf": 0.1570874638462462,             # 1 lbf/ft3 ~ 0.1571 kN/m3
        "lb/ft3": 0.1570874638462462,
        "lb/ft^3": 0.1570874638462462,
        "lbf/ft3": 0.1570874638462462,
        "lbf/ft^3": 0.1570874638462462,
        "kcf": 157.0874638462462,
        "kip/ft3": 157.0874638462462,
        "kips/ft3": 157.0874638462462,
    },
    UnitDimension.FORCE: {
        "kn": 1.0,
        "mn": 1000.0,
        "n": 0.001,
        "gn": 1000000.0,
        "kip": 4.4482216152605,
        "kips": 4.4482216152605,
        "lb": 0.0044482216152605,
        "lbs": 0.0044482216152605,
        "lbf": 0.0044482216152605,
        "ton": 8.896443230521,                 # US Short ton force = 2000 lbf
        "tons": 8.896443230521,
        "tonne": 9.80665,                      # Metric tonne force = 1000 kg * 9.80665
        "tonnes": 9.80665,
        "t": 9.80665,
    },
    UnitDimension.FORCE_PER_LENGTH: {
        "kn/m": 1.0,
        "mn/m": 1000.0,
        "n/m": 0.001,
        "n/mm": 1.0,                           # 1 N/mm = 1000 N/m = 1 kN/m
        "kn/mm": 1000.0,
        "plf": 0.014593902937206365,           # lb/ft
        "lb/ft": 0.014593902937206365,
        "lbf/ft": 0.014593902937206365,
        "klf": 14.593902937206365,             # kip/ft
        "kip/ft": 14.593902937206365,
        "kips/ft": 14.593902937206365,
    },
    UnitDimension.LENGTH: {
        "m": 1.0,
        "meter": 1.0,
        "meters": 1.0,
        "metre": 1.0,
        "metres": 1.0,
        "mm": 0.001,
        "millimeter": 0.001,
        "millimeters": 0.001,
        "cm": 0.01,
        "centimeter": 0.01,
        "centimeters": 0.01,
        "dm": 0.1,
        "km": 1000.0,
        "kilometer": 1000.0,
        "kilometers": 1000.0,
        "ft": 0.3048,
        "foot": 0.3048,
        "feet": 0.3048,
        "'": 0.3048,
        "in": 0.0254,
        "inch": 0.0254,
        "inches": 0.0254,
        "\"": 0.0254,
        "yd": 0.9144,
        "yard": 0.9144,
        "yards": 0.9144,
    },
    UnitDimension.ANGLE: {
        "deg": 1.0,
        "degree": 1.0,
        "degrees": 1.0,
        "°": 1.0,
        "rad": 180.0 / math.pi,                # 1 rad = 57.2957795 deg
        "radian": 180.0 / math.pi,
        "radians": 180.0 / math.pi,
        "grad": 0.9,
        "gon": 0.9,
    },
    UnitDimension.VELOCITY: {
        "m/s": 1.0,
        "m/sec": 1.0,
        "cm/s": 0.01,
        "cm/sec": 0.01,
        "mm/s": 0.001,
        "km/h": 1.0 / 3.6,
        "km/hr": 1.0 / 3.6,
        "kph": 1.0 / 3.6,
        "ft/s": 0.3048,
        "fps": 0.3048,
        "ft/sec": 0.3048,
        "m/day": 1.0 / 86400.0,
        "m/d": 1.0 / 86400.0,
        "m/year": 1.0 / (86400.0 * 365.25),
        "m/yr": 1.0 / (86400.0 * 365.25),
        "ft/day": 0.3048 / 86400.0,
        "ft/d": 0.3048 / 86400.0,
    },
    UnitDimension.TIME: {
        "s": 1.0,
        "sec": 1.0,
        "second": 1.0,
        "seconds": 1.0,
        "min": 60.0,
        "minute": 60.0,
        "minutes": 60.0,
        "h": 3600.0,
        "hr": 3600.0,
        "hour": 3600.0,
        "hours": 3600.0,
        "d": 86400.0,
        "day": 86400.0,
        "days": 86400.0,
        "yr": 86400.0 * 365.25,
        "year": 86400.0 * 365.25,
        "years": 86400.0 * 365.25,
    },
    UnitDimension.AREA: {
        "m2": 1.0,
        "m^2": 1.0,
        "mm2": 1e-6,
        "mm^2": 1e-6,
        "cm2": 1e-4,
        "cm^2": 1e-4,
        "ft2": 0.09290304,
        "ft^2": 0.09290304,
        "sqft": 0.09290304,
        "in2": 0.00064516,
        "in^2": 0.00064516,
        "sqin": 0.00064516,
    },
    UnitDimension.VOLUME: {
        "m3": 1.0,
        "m^3": 1.0,
        "liter": 0.001,
        "liters": 0.001,
        "l": 0.001,
        "dm3": 0.001,
        "cm3": 1e-6,
        "cc": 1e-6,
        "ml": 1e-6,
        "ft3": 0.028316846592,
        "ft^3": 0.028316846592,
        "cuft": 0.028316846592,
    },
    UnitDimension.PERCENT: {
        "%": 1.0,
        "pct": 1.0,
        "percent": 1.0,
        "ratio": 100.0,                        # 1.0 ratio = 100%
        "fraction": 100.0,
        "-": 100.0,
    },
    UnitDimension.DIMENSIONLESS: {
        "-": 1.0,
        "": 1.0,
        "dimensionless": 1.0,
    }
}


# Precompute reverse lookup map: normalized_unit_string -> (UnitDimension, to_base_factor)
_UNIT_LOOKUP: Dict[str, Tuple[UnitDimension, float]] = {}
for dim, mapping in UNIT_TAXONOMY.items():
    for u_str, factor in mapping.items():
        _UNIT_LOOKUP[u_str] = (dim, factor)


def normalize_unit_str(raw_unit: Optional[str]) -> str:
    """Normalize unit string representation (strip brackets, whitespace, lowercase)."""
    if not raw_unit:
        return "-"
    u = str(raw_unit).strip().lower()
    # Remove surrounding brackets e.g. '[kPa]' -> 'kpa'
    u = re.sub(r'^[\[\(\{\<](.*)[\]\)\}\>]$', r'\1', u).strip()
    return u or "-"


def get_unit_dimension(unit_str: str) -> Optional[UnitDimension]:
    """Identify physical dimension for a given unit string."""
    clean_u = normalize_unit_str(unit_str)
    if clean_u in _UNIT_LOOKUP:
        return _UNIT_LOOKUP[clean_u][0]
    return None


def parse_value_with_unit(raw_input: Union[str, float, int]) -> Tuple[float, Optional[str]]:
    """
    Parses numeric input with optional natural language unit suffix.
    
    Examples:
        '18.5 kN/m3' -> (18.5, 'kN/m3')
        '32 deg' -> (32.0, 'deg')
        '1.5 MPa' -> (1.5, 'MPa')
        12.0 -> (12.0, None)
    """
    if isinstance(raw_input, (float, int)):
        if isinstance(raw_input, float) and (math.isnan(raw_input) or math.isinf(raw_input)):
            raise GeoAIUnitError(f"Invalid non-finite number: {raw_input}")
        return float(raw_input), None

    if not isinstance(raw_input, str):
        raise GeoAIUnitError(f"Unsupported value type for unit parsing: {type(raw_input)}")

    clean_str = raw_input.strip()
    if not clean_str:
        raise GeoAIUnitError("Empty string provided for numeric value")

    # Match numeric portion followed by optional unit string
    # Regex handles scientific notation, negative numbers, decimals
    pattern = r'^([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*(.*)$'
    match = re.match(pattern, clean_str)

    if not match:
        raise GeoAIUnitError(f"Could not parse numeric value from '{raw_input}'")

    num_str, unit_str = match.groups()
    try:
        val = float(num_str)
    except ValueError as e:
        raise GeoAIUnitError(f"Invalid numeric string '{num_str}': {e}") from e

    unit_clean = unit_str.strip() or None
    return val, unit_clean


def convert_unit(value: float, from_unit: str, to_unit: str, field_name: Optional[str] = None) -> float:
    """
    Convert a numeric value deterministically from one unit to another within the same dimension.
    
    Raises:
        GeoAIUnitError if units belong to incompatible dimensions or are unrecognized.
    """
    u_from = normalize_unit_str(from_unit)
    u_to = normalize_unit_str(to_unit)

    # Identical units or dimensionless pass-through
    if u_from == u_to:
        return value

    if u_from not in _UNIT_LOOKUP:
        raise GeoAIUnitError(
            message=f"Unrecognized source unit '{from_unit}'.",
            field=field_name,
            provided_unit=from_unit,
            expected_unit=to_unit
        )

    if u_to not in _UNIT_LOOKUP:
        raise GeoAIUnitError(
            message=f"Unrecognized target unit '{to_unit}'.",
            field=field_name,
            provided_unit=from_unit,
            expected_unit=to_unit
        )

    dim_from, factor_from = _UNIT_LOOKUP[u_from]
    dim_to, factor_to = _UNIT_LOOKUP[u_to]

    # Special handling for percent vs ratio dimensionless conversion
    if dim_from == UnitDimension.PERCENT and dim_to == UnitDimension.DIMENSIONLESS:
        # e.g. 50% -> 0.5 ratio
        return value / 100.0
    if dim_from == UnitDimension.DIMENSIONLESS and dim_to == UnitDimension.PERCENT:
        # e.g. 0.5 ratio -> 50%
        return value * 100.0

    if dim_from != dim_to:
        raise GeoAIUnitError(
            message=f"Unit dimension mismatch: '{from_unit}' is a {dim_from.value} unit, but target '{to_unit}' requires {dim_to.value}.",
            field=field_name,
            provided_unit=from_unit,
            expected_unit=to_unit
        )

    # Value in base dimension units
    val_base = value * factor_from
    # Value in target unit
    converted = val_base / factor_to
    return converted


def normalize_parameter_value(
    value: Any,
    expected_unit: Optional[str] = None,
    field_name: Optional[str] = None
) -> Any:
    """
    Normalizes a parameter input value against its expected unit.
    - If value is a string with units (e.g. '1.5 MPa'), parses and converts to expected unit (e.g. 'kPa' -> 1500.0).
    - If value is pure numeric and expected_unit is defined, verifies finite float and returns numeric value.
    - If unit mismatch is detected (e.g. '25 kPa' for unit weight), raises GeoAIUnitError with clear diagnostics.
    """
    if value is None:
        return None

    if not expected_unit or normalize_unit_str(expected_unit) in {"-", "dimensionless", ""}:
        # Pure numeric or string coercion without strict target dimension
        if isinstance(value, str):
            val, _ = parse_value_with_unit(value)
            return val
        return value

    target_dim = get_unit_dimension(expected_unit)
    if not target_dim:
        # Expected unit not in standard taxonomy (e.g. complex compound or custom string)
        if isinstance(value, str):
            try:
                val, _ = parse_value_with_unit(value)
                return val
            except GeoAIUnitError:
                return value
        return value

    if isinstance(value, (int, float)):
        # Pure numeric without explicit unit string; assumed to already be in target unit
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            raise GeoAIUnitError(f"Parameter '{field_name or 'value'}' cannot be NaN or Infinite.")
        return float(value)

    if isinstance(value, str):
        val, provided_unit = parse_value_with_unit(value)
        if provided_unit:
            return convert_unit(val, from_unit=provided_unit, to_unit=expected_unit, field_name=field_name)
        else:
            return float(val)

    return value
