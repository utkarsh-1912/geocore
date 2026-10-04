# Author: Utkarsh Gupta
# License: GPL v3
"""
IS 1904:2021 (fourth revision) - Design and construction of foundations in soils: general requirements.

* Table 1 (cl. 16.3.4)  permissible maximum settlement, differential settlement and angular distortion
                        for shallow foundations. The 2021 table equals the 1986 table except that the
                        maximum settlement of rafts for RC structures on plastic clay is 125 mm (was 100 mm).
                        The code notes that the values are a guide; the designer decides the limits.
* 16.3.5                differential settlement = max - min settlement; tilt = differential / distance.
* 17.1                  factor of safety against sliding >= 1.5 with wind/seismic, >= 1.75 without;
                        against overturning >= 1.5 with wind/seismic, >= 2.0 without.
* 7.2                   foundations at least 500 mm below natural ground level (checked in bearing capacity).
"""
from typing import Any, Dict, List, Optional, Tuple

from core.standards.bis._common import BISInputError, choice, require_positive, round_sig

STANDARD = "IS 1904:2021"
FOUNDATION_TYPES = ("isolated", "raft")
STRUCTURE_TYPES = ("steel", "reinforced_concrete", "multistorey_framed", "load_bearing_walls", "water_tower_silo")
SOIL_TYPES = ("sand_hard_clay", "plastic_clay")
CHECKS = ("sliding", "overturning")

# (maximum settlement [mm], differential settlement coefficient (x L), angular distortion denominator)
_Limit = Tuple[float, float, float]
TABLE_1: Dict[Tuple[str, str, str], _Limit] = {
    ("isolated", "steel", "sand_hard_clay"): (50, 0.0033, 300),
    ("isolated", "steel", "plastic_clay"): (50, 0.0033, 300),
    ("isolated", "reinforced_concrete", "sand_hard_clay"): (50, 0.0015, 666),
    ("isolated", "reinforced_concrete", "plastic_clay"): (75, 0.0015, 666),
    ("isolated", "multistorey_framed", "sand_hard_clay"): (60, 0.002, 500),
    ("isolated", "multistorey_framed", "plastic_clay"): (75, 0.002, 500),
    ("isolated", "water_tower_silo", "sand_hard_clay"): (50, 0.0015, 666),
    ("isolated", "water_tower_silo", "plastic_clay"): (75, 0.0015, 666),
    ("raft", "steel", "sand_hard_clay"): (75, 0.0033, 300),
    ("raft", "steel", "plastic_clay"): (100, 0.0033, 300),
    ("raft", "reinforced_concrete", "sand_hard_clay"): (75, 0.0021, 500),
    ("raft", "reinforced_concrete", "plastic_clay"): (125, 0.002, 500),
    ("raft", "multistorey_framed", "sand_hard_clay"): (75, 0.0025, 400),
    ("raft", "multistorey_framed", "plastic_clay"): (125, 0.0033, 300),
    ("raft", "water_tower_silo", "sand_hard_clay"): (100, 0.0025, 400),
    ("raft", "water_tower_silo", "plastic_clay"): (125, 0.0025, 400),
}
# Isolated foundations of load bearing walls, same for both soil groups, at L/H = 2 and 7 (interpolate).
LOAD_BEARING_WALLS: Dict[float, _Limit] = {2.0: (60, 0.0002, 5000), 7.0: (60, 0.0004, 2500)}


def _load_bearing_wall_limits(length_height_ratio: Optional[float]) -> _Limit:
    if length_height_ratio is None:
        raise BISInputError("'length_height_ratio' (L/H of the wall) is required for load bearing walls.")
    r = float(length_height_ratio)
    if not 2.0 <= r <= 7.0:
        raise BISInputError("IS 1904 Table 1 gives load bearing wall limits for L/H from 2 to 7 only "
                            f"(got {r:g}); decide the limits by engineering judgement.")
    (s2, c2, a2), (s7, c7, a7) = LOAD_BEARING_WALLS[2.0], LOAD_BEARING_WALLS[7.0]
    w = (r - 2.0) / 5.0
    # Interpolate the differential coefficient; the angular distortion follows as 1 / coefficient.
    coeff = c2 + w * (c7 - c2)
    return s2 + w * (s7 - s2), coeff, 1.0 / coeff


def permissible_settlement_is1904(foundation_type: str, structure_type: str, soil_type: str,
                                  span_length: Optional[float] = None, length_height_ratio: Optional[float] = None,
                                  calculated_max_settlement: Optional[float] = None,
                                  calculated_differential_settlement: Optional[float] = None) -> Dict[str, Any]:
    """
    Permissible settlement, differential settlement and angular distortion to IS 1904:2021 Table 1.

    :param foundation_type: Foundation type. Options: isolated, raft
    :param structure_type: Structure type. Options: steel, reinforced_concrete, multistorey_framed, load_bearing_walls, water_tower_silo
    :param soil_type: Soil group of Table 1. Options: sand_hard_clay, plastic_clay
    :param span_length: L, length of the deflected part of wall/raft or centre-to-centre column distance [m]
    :param length_height_ratio: L/H of a load bearing wall (2 to 7) [-]
    :param calculated_max_settlement: Calculated maximum settlement to check [mm]
    :param calculated_differential_settlement: Calculated differential settlement over span_length to check [mm]
    :returns: Table 1 limits and, when calculated settlements are given, the comparison.
    """
    fnd = choice(foundation_type, "foundation_type", FOUNDATION_TYPES)
    struct = choice(structure_type, "structure_type", STRUCTURE_TYPES)
    soil = choice(soil_type, "soil_type", SOIL_TYPES)
    if struct == "load_bearing_walls":
        if fnd == "raft":
            raise BISInputError("IS 1904 Table 1: rafts under load bearing walls are 'not likely to be encountered'; no limits are given.")
        s_max, coeff, ad_den = _load_bearing_wall_limits(length_height_ratio)
    else:
        s_max, coeff, ad_den = TABLE_1[(fnd, struct, soil)]

    warnings: List[str] = ["IS 1904 Table 1 values are a guide; the permissible settlements in each case should be "
                           "decided as per the requirements of the designer."]
    result: Dict[str, Any] = {
        "Foundation type": fnd, "Structure type": struct, "Soil group": soil,
        "Permissible maximum settlement [mm]": round_sig(s_max),
        "Permissible differential settlement coefficient (x L) [-]": round_sig(coeff),
        "Permissible angular distortion [-]": f"1/{ad_den:.0f}",
    }
    if fnd == "raft" and struct == "reinforced_concrete" and soil == "plastic_clay":
        warnings.append("IS 1904:2021 raised this limit to 125 mm (100 mm in IS 1904:1986).")
    passes: List[bool] = []
    if span_length is not None:
        span = require_positive(span_length, "span_length")
        diff_limit = coeff * span * 1000.0
        result["Span length L [m]"] = span
        result["Permissible differential settlement [mm]"] = round_sig(diff_limit)
        if calculated_differential_settlement is not None:
            diff = require_positive(calculated_differential_settlement, "calculated_differential_settlement", allow_zero=True)
            ad = diff / (span * 1000.0)
            result["Calculated differential settlement [mm]"] = diff
            result["Calculated angular distortion [-]"] = f"1/{1.0 / ad:.0f}" if ad > 0 else "0"
            result["Differential settlement within limit"] = bool(diff <= diff_limit)
            passes.append(diff <= diff_limit)
    elif calculated_differential_settlement is not None:
        raise BISInputError("'span_length' is required to check a differential settlement.")
    if calculated_max_settlement is not None:
        s = require_positive(calculated_max_settlement, "calculated_max_settlement", allow_zero=True)
        result["Calculated maximum settlement [mm]"] = s
        result["Maximum settlement within limit"] = bool(s <= s_max)
        passes.append(s <= s_max)
    if passes:
        warnings.append("The comparison covers IS 1904 Table 1 settlement guidance only, not the overall adequacy of the foundation.")
    result["Standard"] = f"{STANDARD}, cl. 16.3, Table 1"
    result["warnings"] = warnings
    return result


def stability_check_is1904(check: str, resisting: float, disturbing: float,
                           wind_or_seismic: bool = False) -> Dict[str, Any]:
    """
    Factor of safety against sliding or overturning of a shallow foundation to IS 1904:2021 cl. 17.1.

    :param check: Stability check. Options: sliding, overturning
    :param resisting: Resisting force [kN] (sliding) or resisting moment [kNm] (overturning), in consistent units
    :param disturbing: Disturbing force or overturning moment, in the same units as resisting
    :param wind_or_seismic: True when wind load or seismic forces are included with dead, imposed and earth pressure loads
    :returns: Factor of safety, the clause minimum and the comparison.
    """
    kind = choice(check, "check", CHECKS)
    r = require_positive(resisting, "resisting", allow_zero=True)
    d = require_positive(disturbing, "disturbing")
    required = 1.5 if wind_or_seismic else (1.75 if kind == "sliding" else 2.0)
    fs = r / d
    return {
        "Check": kind,
        "Load case": "with wind or seismic forces" if wind_or_seismic else "dead, imposed and earth pressure only",
        "Factor of safety [-]": round_sig(fs),
        "Required minimum factor of safety [-]": required,
        "Meets IS 1904 minimum": bool(fs >= required),
        "Standard": f"{STANDARD}, cl. 17.1.{1 if kind == 'sliding' else 2}",
        "warnings": ["Checks the factor of safety against one IS 1904 cl. 17.1 requirement; the resisting and "
                     "disturbing actions must be computed by the engineer for the governing load combination."],
    }
