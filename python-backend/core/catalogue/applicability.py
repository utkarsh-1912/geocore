# Author: Utkarsh Gupta
# License: GPL v3
"""
Applicability of calculation methods (Phase 6): when a method's inputs are outside the range the method is
defined for, say so instead of letting a result through that looks valid (e.g. Groundhog's Rankine returns NaN
when the backfill slope exceeds phi').

Deterministic and explicit: one small check per function id, on the Groundhog parameters (the names the forms
and ``registry.execute_function`` use; GeoAI tools pass theirs through ``form_arg_map``). Checks never change a
result; callers attach the messages as warnings. ``NOTES`` are standing conditions of a method, shown with it.
"""
from typing import Any, Callable, Dict, List, Optional


def _number(args: Dict[str, Any], key: str) -> Optional[float]:
    try:
        return float(args[key])
    except (KeyError, TypeError, ValueError):
        return None


def _rankine(args: Dict[str, Any]) -> List[str]:
    phi, slope = _number(args, "phi_eff"), _number(args, "top_angle")
    if phi is None or slope is None or abs(slope) <= phi:
        return []
    return [f"Rankine earth pressure is undefined when the backfill slope ({slope:g} deg) is steeper than the "
            f"friction angle ({phi:g} deg): the coefficients are not real numbers."]


def _relative_density(args: Dict[str, Any]) -> List[str]:
    # Groundhog's naming: e_min is the void ratio at MINIMUM density (the loosest state, conventionally e_max)
    # and e_max the one at maximum density (the densest state, conventionally e_min).
    e, loosest, densest = _number(args, "void_ratio"), _number(args, "e_min"), _number(args, "e_max")
    if None in (e, loosest, densest):
        return []
    if loosest <= densest:
        return [f"The loosest-state void ratio ({loosest:g}) must be larger than the densest-state void ratio "
                f"({densest:g}); check that the two limits are not swapped."]
    if not densest <= e <= loosest:
        return [f"The void ratio ({e:g}) is outside the range between the densest ({densest:g}) and loosest "
                f"({loosest:g}) states, so the relative density is outside 0-100 %."]
    return []


CHECKS: Dict[str, Callable[[Dict[str, Any]], List[str]]] = {
    "earthpressurecoefficients_rankine": _rankine,
    "relative_density": _relative_density,
}

NOTES: Dict[str, str] = {
    "relative_density": "Defined for coarse-grained (granular) soils; e_min and e_max come from standard "
                        "minimum and maximum density tests.",
    "earthpressurecoefficients_rankine": "Assumes a frictionless wall (no wall friction) and cohesionless backfill; "
                                         "valid for backfill slopes up to phi'.",
}


def check(function_id: str, args: Dict[str, Any]) -> List[str]:
    """Messages for inputs outside the range ``function_id``'s method applies to ([] = applicable or no check)."""
    rule = CHECKS.get(function_id)
    if rule is None or not isinstance(args, dict):
        return []
    try:
        return rule(args)
    except Exception:  # a check must never break a calculation
        return []
