# Author: Utkarsh Gupta
# License: GPL v3
"""Shared helpers for the Indian Standard (BIS) calculations."""
import math
from typing import Any, Iterable, Optional

#: 1 kgf/cm2 in kPa (standard gravity). The 1970s-80s IS codes state charts in kgf/cm2.
KGF_PER_CM2_IN_KPA = 98.0665


class BISInputError(ValueError):
    """Inputs outside the scope of the clause being applied (reported to the user, never patched)."""


def require_positive(value: Optional[float], name: str, allow_zero: bool = False) -> float:
    if value is None:
        raise BISInputError(f"'{name}' is required.")
    value = float(value)
    if not math.isfinite(value) or value < 0 or (value == 0 and not allow_zero):
        raise BISInputError(f"'{name}' must be {'>= 0' if allow_zero else '> 0'} (got {value}).")
    return value


def choice(value: Any, name: str, options: Iterable[str]) -> str:
    """Normalise a text option (case/space/hyphen-insensitive) or raise listing the valid options."""
    options = list(options)
    key = str(value).strip().lower().replace('-', '_').replace(' ', '_')
    for opt in options:
        if key == opt:
            return opt
    raise BISInputError(f"'{name}' must be one of {', '.join(options)} (got '{value}').")


def round_sig(value: float, digits: int = 4) -> float:
    """Round to significant figures for reporting (calculations use full precision)."""
    if value == 0 or not math.isfinite(value):
        return value
    return round(value, digits - 1 - int(math.floor(math.log10(abs(value)))))


# Water properties at atmospheric pressure, used to refer laboratory results to 27 degC as
# IS 2720 requires. IS 2720 does not tabulate them; these are standard reference correlations.
WATER_TEMPERATURE_RANGE = (0.0, 40.0)


def _check_water_temperature(temperature: float) -> float:
    lo, hi = WATER_TEMPERATURE_RANGE
    temperature = float(temperature)
    if not lo <= temperature <= hi:
        raise BISInputError(f"Water temperature must be within {lo:g}-{hi:g} degC (got {temperature:g}).")
    return temperature


def water_viscosity(temperature: float) -> float:
    """
    Dynamic viscosity of water [Pa s]: Vogel equation mu = A 10^(B / (T - C)),
    A = 2.414e-5 Pa s, B = 247.8 K, C = 140 K (within about 0.5 % of IAPWS values for 0-40 degC).
    """
    t_kelvin = _check_water_temperature(temperature) + 273.15
    return 2.414e-5 * 10 ** (247.8 / (t_kelvin - 140.0))


def water_density(temperature: float) -> float:
    """Density of air-free water [kg/m3]: Tanaka et al. (2001), Metrologia 38, 301-309."""
    t = _check_water_temperature(temperature)
    a1, a2, a3, a4, a5 = -3.983035, 301.797, 522528.9, 69.34881, 999.974950
    return a5 * (1.0 - (t + a1) ** 2 * (t + a2) / (a3 * (t + a4)))
