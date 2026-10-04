# Author: Utkarsh Gupta
# License: GPL v3
"""
IS 6403:1981 (Reaffirmed, incl. Amendment 1, 1984) - Determination of bearing capacity of
shallow foundations. Net ultimate bearing capacity on the shear criterion (clause 5.1-5.3).

Implemented clauses
-------------------
* 5.1.1 / 5.1.2  qd  = c Nc sc dc ic + q (Nq - 1) sq dq iq + 1/2 B gamma Ngamma sgamma dgamma igamma W'
                 q'd = 2/3 c N'c ... + q (N'q - 1) ... + 1/2 B gamma N'gamma ... W'   (local shear)
* Table 1        Nq = e^(pi tan phi) tan^2(45 + phi/2), Nc = (Nq - 1) cot phi, Ngamma = 2 (Nq + 1) tan phi
                 (these closed forms reproduce Table 1; Nc = 5.14 at phi = 0). N'c, N'q, N'gamma are read
                 at phi' = atan(0.67 tan phi).
* Table 2        shape factors; 5.1.2.2 depth factors (only with properly compacted backfill);
                 5.1.2.3 inclination factors; 5.1.2.4 water table factor W'.
* Table 3        failure mode from relative density (> 70 % general, < 20 % local, interpolate between).
* 5.3.1.1        phi = 0: qd = c Nc sc dc ic with Nc = 5.14 (the general equation reduces to this).
* 5.0.1          effective dimensions B' = B - 2 eB, L' = L - 2 eL for eccentric loads.

Not implemented: the SPT chart (Fig. 1), static-cone chart (Fig. 2), two-layer clay (Fig. 3) and
desiccated clay (Table 4) methods, which are graphical. IS 6403 is under revision (BIS CED 43/WG 7).

The result is a net ultimate value on the shear criterion only. Clause 6.1 takes the allowable
bearing capacity as the lesser of (net ultimate / factor of safety) and the pressure that keeps
settlement within IS 1904 limits; the factor of safety is the designer's choice.
"""
import math
from typing import Any, Dict, List, Optional, Tuple

from core.standards.bis._common import BISInputError, choice, require_positive, round_sig

STANDARD = "IS 6403:1981 (Reaffirmed)"
SHAPES = ("strip", "square", "circle", "rectangle")
FAILURE_MODES = ("general", "local", "from_relative_density")
#: Groundhog's bearing-factor functions are validated for this range of friction angle.
_GROUNDHOG_PHI_RANGE = (20.0, 50.0)
#: Table 1 is tabulated up to 50 degrees.
MAX_FRICTION_ANGLE = 50.0
#: IS 1904:2021 clause 7.2 minimum founding depth below natural ground level.
IS1904_MIN_DEPTH = 0.5


def bearing_capacity_factors(friction_angle: float) -> Dict[str, Any]:
    """
    IS 6403 Table 1 bearing capacity factors for a friction angle [deg] (0-50).

    Nq and Ngamma come from Groundhog (``nq_frictionangle_sand``, ``ngamma_frictionangle_vesic``,
    which use the same equations as Table 1) inside Groundhog's validated range of 20-50 deg;
    below 20 deg the identical closed forms are evaluated here. Nc = (Nq - 1) cot(phi), or
    2 + pi = 5.14 at phi = 0.
    """
    phi = float(friction_angle)
    if not 0.0 <= phi <= MAX_FRICTION_ANGLE:
        raise BISInputError(f"Friction angle must be within 0-{MAX_FRICTION_ANGLE:g} deg for IS 6403 Table 1 (got {phi:g}).")
    t = math.tan(math.radians(phi))
    if phi == 0.0:
        return {"Nc": 2.0 + math.pi, "Nq": 1.0, "Ngamma": 0.0, "source": "IS 6403 Table 1 / cl. 5.3.1.1 (phi = 0)"}
    if _GROUNDHOG_PHI_RANGE[0] <= phi <= _GROUNDHOG_PHI_RANGE[1]:
        from groundhog.shallowfoundations.capacity import nq_frictionangle_sand, ngamma_frictionangle_vesic
        nq = float(nq_frictionangle_sand(phi)['Nq [-]'])
        ngamma = float(ngamma_frictionangle_vesic(phi)['Ngamma [-]'])
        source = "Groundhog nq_frictionangle_sand / ngamma_frictionangle_vesic"
    else:
        nq = math.exp(math.pi * t) * math.tan(math.radians(45.0 + phi / 2.0)) ** 2
        ngamma = 2.0 * (nq + 1.0) * t
        source = "Closed form of IS 6403 Table 1 (below Groundhog's 20-50 deg range)"
    nc = (nq - 1.0) / t
    return {"Nc": nc, "Nq": nq, "Ngamma": ngamma, "source": source}


def _shape_factors(shape: str, b: float, l: Optional[float]) -> Tuple[float, float, float]:
    if shape == "strip":
        return 1.0, 1.0, 1.0
    if shape == "square":
        return 1.3, 1.2, 0.8
    if shape == "circle":
        return 1.3, 1.2, 0.6
    ratio = b / l
    return 1.0 + 0.2 * ratio, 1.0 + 0.2 * ratio, 1.0 - 0.4 * ratio


def _depth_factors(phi: float, depth: float, width: float) -> Tuple[float, float, float]:
    root_nphi = math.tan(math.radians(45.0 + phi / 2.0))  # sqrt(N_phi), N_phi = tan^2(45 + phi/2)
    dc = 1.0 + 0.2 * depth / width * root_nphi
    dq = 1.0 if phi < 10.0 else 1.0 + 0.1 * depth / width * root_nphi
    return dc, dq, dq


def _inclination_factors(alpha: float, phi: float) -> Tuple[float, float, float]:
    ic = (1.0 - alpha / 90.0) ** 2
    igamma = 0.0 if phi <= 0.0 or alpha >= phi else (1.0 - alpha / phi) ** 2
    return ic, ic, igamma


def _water_table_factor(water_table_depth: float, depth: float, width: float) -> float:
    if water_table_depth >= depth + width:
        return 1.0
    if water_table_depth <= depth:
        return 0.5
    return 0.5 + 0.5 * (water_table_depth - depth) / width


def _effective_surcharge(depth: float, water_table_depth: float, unit_weight: float,
                         saturated_unit_weight: Optional[float], unit_weight_water: float) -> float:
    """IS 6403 cl. 2.2.2: total unit weight above the water table, submerged unit weight below it."""
    if water_table_depth >= depth:
        return unit_weight * depth
    if saturated_unit_weight is None:
        raise BISInputError("The water table is above the foundation base, so 'saturated_unit_weight' is required "
                            "to compute the effective surcharge q (IS 6403 cl. 2.2.2).")
    submerged = saturated_unit_weight - unit_weight_water
    if submerged <= 0:
        raise BISInputError("'saturated_unit_weight' must exceed 'unit_weight_water'.")
    return unit_weight * max(water_table_depth, 0.0) + submerged * (depth - max(water_table_depth, 0.0))


def _net_ultimate(c: float, phi: float, mode: str, *, shape: str, b: float, l: Optional[float], depth: float,
                  width_for_depth: float, alpha: float, q: float, gamma: float, w_prime: float,
                  apply_depth_factors: bool) -> Dict[str, Any]:
    """One evaluation of cl. 5.1.2 for general or local shear."""
    if mode == "local":
        c_used = 2.0 / 3.0 * c
        phi_used = math.degrees(math.atan(0.67 * math.tan(math.radians(phi))))
    else:
        c_used, phi_used = c, phi
    factors = bearing_capacity_factors(phi_used)
    sc, sq, sg = _shape_factors(shape, b, l)
    dc, dq, dg = _depth_factors(phi_used, depth, width_for_depth) if apply_depth_factors else (1.0, 1.0, 1.0)
    ic, iq, ig = _inclination_factors(alpha, phi_used)
    cohesion_term = c_used * factors["Nc"] * sc * dc * ic
    surcharge_term = q * (factors["Nq"] - 1.0) * sq * dq * iq
    gamma_term = 0.5 * b * gamma * factors["Ngamma"] * sg * dg * ig * w_prime
    return {
        "phi_used": phi_used, "c_used": c_used, "factors": factors,
        "shape": (sc, sq, sg), "depth": (dc, dq, dg), "inclination": (ic, iq, ig),
        "terms": (cohesion_term, surcharge_term, gamma_term),
        "qnu": cohesion_term + surcharge_term + gamma_term,
    }


def bearing_capacity_is6403(width: float, depth: float, water_table_depth: float, unit_weight: float,
                            cohesion: float = 0.0, friction_angle: float = 0.0, shape: str = "strip",
                            length: Optional[float] = None, failure_mode: str = "general",
                            relative_density: Optional[float] = None, load_inclination: float = 0.0,
                            eccentricity_width: float = 0.0, eccentricity_length: float = 0.0,
                            saturated_unit_weight: Optional[float] = None, apply_depth_factors: bool = False,
                            factor_of_safety: Optional[float] = None,
                            unit_weight_water: float = 9.81) -> Dict[str, Any]:
    """
    Net ultimate bearing capacity of a shallow foundation to IS 6403:1981 (shear criterion).

    qd = c Nc sc dc ic + q (Nq - 1) sq dq iq + 0.5 B gamma Ngamma sgamma dgamma igamma W' (cl. 5.1.2), with
    local shear (c' = 2c/3, phi' = atan(0.67 tan phi)) or Table 3 interpolation on relative density.
    For phi = 0 it reduces to qd = c Nc sc dc ic with Nc = 5.14 (cl. 5.3.1.1).

    :param width: Footing width B; diameter for a circle [m]
    :param depth: Founding depth Df below the surrounding ground level [m]
    :param water_table_depth: Depth of the (highest likely) water table below ground level [m]
    :param unit_weight: Bulk unit weight gamma of the foundation soil [kN/m3]
    :param cohesion: Cohesion c (undrained cohesion for phi = 0 analysis) [kPa]
    :param friction_angle: Angle of shearing resistance phi, 0-50 [deg]
    :param shape: Footing shape. Options: strip, square, circle, rectangle
    :param length: Footing length L, required for a rectangle (L >= B) [m]
    :param failure_mode: Shear failure mode. Options: general, local, from_relative_density
    :param relative_density: Relative density for failure_mode = from_relative_density [%]
    :param load_inclination: Inclination alpha of the resultant load to the vertical [deg]
    :param eccentricity_width: Load eccentricity along the width eB [m]
    :param eccentricity_length: Load eccentricity along the length eL [m]
    :param saturated_unit_weight: Saturated unit weight, needed when the water table is above the base [kN/m3]
    :param apply_depth_factors: Apply cl. 5.1.2.2 depth factors (only if backfill is properly compacted)
    :param factor_of_safety: Factor of safety on net ultimate capacity for the net safe value [-]
    :param unit_weight_water: Unit weight of water [kN/m3]
    :returns: Bearing capacity factors, modifying factors, the three terms, qnu and (optionally) qns.
    """
    shape = choice(shape, "shape", SHAPES)
    mode = choice(failure_mode, "failure_mode", FAILURE_MODES)
    b = require_positive(width, "width")
    depth = require_positive(depth, "depth", allow_zero=True)
    gamma = require_positive(unit_weight, "unit_weight")
    c = require_positive(cohesion, "cohesion", allow_zero=True)
    phi = require_positive(friction_angle, "friction_angle", allow_zero=True)
    if water_table_depth is None:
        raise BISInputError("'water_table_depth' is required (IS 6403 cl. 5.1.2.4); give the highest level the water table is likely to reach.")
    dw = float(water_table_depth)
    alpha = require_positive(load_inclination, "load_inclination", allow_zero=True)
    e_b = require_positive(eccentricity_width, "eccentricity_width", allow_zero=True)
    e_l = require_positive(eccentricity_length, "eccentricity_length", allow_zero=True)
    gamma_w = require_positive(unit_weight_water, "unit_weight_water")
    if c == 0.0 and phi == 0.0:
        raise BISInputError("Both cohesion and friction_angle are zero; give the soil shear strength parameters.")
    if alpha >= 90.0:
        raise BISInputError("'load_inclination' must be below 90 deg.")
    warnings: List[str] = []

    # Geometry and effective dimensions (cl. 5.0.1)
    if shape == "rectangle":
        if length is None:
            raise BISInputError("'length' is required for a rectangular footing.")
        l = require_positive(length, "length")
        if l < b:
            raise BISInputError("For a rectangle give width B as the shorter side (length >= width).")
    elif shape == "square":
        l = b
    else:
        l = None
        if e_l:
            raise BISInputError(f"'eccentricity_length' does not apply to a {shape} footing.")
    if shape == "circle" and e_b:
        raise BISInputError("IS 6403 cl. 5.0.1 gives effective dimensions for rectangular footings only; "
                            "eccentric loading of a circular footing is outside its scope.")
    b_eff = b - 2.0 * e_b
    l_eff = (l - 2.0 * e_l) if l is not None else None
    if b_eff <= 0 or (l_eff is not None and l_eff <= 0):
        raise BISInputError("The eccentricity leaves no effective footing area (B - 2eB or L - 2eL <= 0).")
    shape_used = shape
    if l_eff is not None and (e_b or e_l):
        shape_used = "rectangle"  # eccentric square becomes a B' x L' rectangle
        if b_eff > l_eff:
            b_eff, l_eff = l_eff, b_eff
            warnings.append("Effective width and length were swapped so that B' <= L'.")
        if shape == "square":
            warnings.append("Eccentric square footing treated as a B' x L' rectangle (Table 2 rectangle formulae).")
    area_eff = math.pi * b * b / 4.0 if shape == "circle" else (b_eff * l_eff if l_eff is not None else b_eff)

    q = _effective_surcharge(depth, dw, gamma, saturated_unit_weight, gamma_w)
    w_prime = _water_table_factor(dw, depth, b)

    common = dict(shape=shape_used, b=b_eff, l=l_eff, depth=depth, width_for_depth=b, alpha=alpha,
                  q=q, gamma=gamma, w_prime=w_prime, apply_depth_factors=apply_depth_factors)
    if mode == "from_relative_density":
        if relative_density is None:
            raise BISInputError("'relative_density' [%] is required for failure_mode = from_relative_density (IS 6403 Table 3).")
        dr = float(relative_density)
        if not 0.0 <= dr <= 100.0:
            raise BISInputError("'relative_density' must be within 0-100 %.")
        general = _net_ultimate(c, phi, "general", **common)
        local = _net_ultimate(c, phi, "local", **common)
        if dr > 70.0:
            weight, mode_used = 1.0, "general (Dr > 70 %)"
        elif dr < 20.0:
            weight, mode_used = 0.0, "local (Dr < 20 %)"
        else:
            weight, mode_used = (dr - 20.0) / 50.0, f"interpolated between local and general (Dr = {dr:g} %)"
        governing = general if weight >= 0.5 else local
        qnu = local["qnu"] + weight * (general["qnu"] - local["qnu"])
    else:
        governing = _net_ultimate(c, phi, mode, **common)
        general = local = None
        qnu = governing["qnu"]
        mode_used = mode

    if governing["phi_used"] != phi:
        warnings.append(f"Local shear: factors read at phi' = atan(0.67 tan phi) = {governing['phi_used']:.2f} deg "
                        "(depth and inclination factors are also evaluated with phi').")
    if apply_depth_factors:
        warnings.append("Depth factors applied: IS 6403 cl. 5.1.2.2 allows them only when backfill is done with proper compaction.")
    if depth < IS1904_MIN_DEPTH:
        warnings.append(f"Founding depth {depth:g} m is less than the {IS1904_MIN_DEPTH * 1000:.0f} mm minimum of IS 1904:2021 cl. 7.2 "
                        "(except on rock or similar weather-resisting ground).")
    if depth > b:
        warnings.append("Df > B: IS 6403 applies to shallow foundations (width greater than depth, cl. 2.2.5).")
    warnings.append("Net ultimate bearing capacity on the shear criterion only. The allowable bearing capacity is the lesser "
                    "of this divided by a factor of safety and the pressure for permissible settlement (IS 6403 cl. 6.1, IS 1904).")

    f = governing["factors"]
    sc, sq, sg = governing["shape"]
    dc, dq, dg = governing["depth"]
    ic, iq, ig = governing["inclination"]
    c_term, q_term, g_term = governing["terms"]
    load_unit = "kN/m" if shape == "strip" else "kN"
    result: Dict[str, Any] = {
        "Failure mode": mode_used,
        "Shape": shape_used,
        "phi used [deg]": round_sig(governing["phi_used"]),
        "c used [kPa]": round_sig(governing["c_used"]),
        "Nc [-]": round_sig(f["Nc"]), "Nq [-]": round_sig(f["Nq"]), "Ngamma [-]": round_sig(f["Ngamma"]),
        "sc [-]": round_sig(sc), "sq [-]": round_sig(sq), "sgamma [-]": round_sig(sg),
        "dc [-]": round_sig(dc), "dq [-]": round_sig(dq), "dgamma [-]": round_sig(dg),
        "ic [-]": round_sig(ic), "iq [-]": round_sig(iq), "igamma [-]": round_sig(ig),
        "W' [-]": round_sig(w_prime),
        "Effective surcharge q [kPa]": round_sig(q),
        "Effective width B' [m]": round_sig(b_eff),
    }
    if l_eff is not None:
        result["Effective length L' [m]"] = round_sig(l_eff)
    result.update({
        "Cohesion term [kPa]": round_sig(c_term),
        "Surcharge term [kPa]": round_sig(q_term),
        "Unit weight term [kPa]": round_sig(g_term),
    })
    if general is not None:
        result["qnu general shear [kPa]"] = round_sig(general["qnu"])
        result["qnu local shear [kPa]"] = round_sig(local["qnu"])
    result["Net ultimate bearing capacity qnu [kPa]"] = round_sig(qnu)
    result[f"Net ultimate load on effective area [{load_unit}]"] = round_sig(qnu * area_eff)
    if factor_of_safety is not None:
        fs = require_positive(factor_of_safety, "factor_of_safety")
        if fs < 1.0:
            raise BISInputError("'factor_of_safety' must be at least 1.")
        result["Factor of safety [-]"] = fs
        result["Net safe bearing capacity qns [kPa]"] = round_sig(qnu / fs)
    result["Bearing factor source"] = f["source"]
    result["Standard"] = f"{STANDARD}, cl. 5.1-5.3, Tables 1-3"
    result["warnings"] = warnings
    return result
