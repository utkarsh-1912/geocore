# Author: Utkarsh Gupta
# License: GPL v3
"""
IS 2950 (Part 1):1981 (Reaffirmed, incl. Amendment 1) - Design and construction of raft foundations:
choice of the analysis method (clauses 5.1.1, 5.2.1 and Appendix C).

* C-2  relative stiffness factor: rectangular raft K = E / (12 Es) (d / b)^3, circular raft
       K = E / (12 Es) (d / 2R)^3; K > 0.5 rigid (C-2.1.1), K < 0.5 flexible (cl. 5.2.1 a, Amendment 1).
* C-3  lambda = (k B / (4 Ec I))^(1/4); the conventional (rigid) method may be used when the column
       spacing is less than 1.75 / lambda (cl. 5.1.1 b).
Cl. 5.1.1 allows the rigid method when either condition holds. Cl. 5.1.3 / 5.2.1 b) additionally need
adjacent column loads and spacings to vary by no more than 20 %, which is the engineer's check.
"""
import math
from typing import Any, Dict, List, Optional

from core.standards.bis._common import BISInputError, choice, require_positive, round_sig

STANDARD = "IS 2950 (Part 1):1981 (Reaffirmed)"
SHAPES = ("rectangular", "circular")
RIGID_K = 0.5
CRITICAL_SPACING_FACTOR = 1.75


def raft_rigidity_is2950(shape: str, raft_thickness: float, concrete_modulus: float, soil_modulus: float,
                         raft_length: Optional[float] = None, raft_radius: Optional[float] = None,
                         subgrade_modulus: Optional[float] = None, raft_width: Optional[float] = None,
                         moment_of_inertia: Optional[float] = None,
                         column_spacing: Optional[float] = None) -> Dict[str, Any]:
    """
    Rigid or flexible raft to IS 2950 (Part 1) Appendix C (relative stiffness K, critical column spacing).

    :param shape: Raft shape. Options: rectangular, circular
    :param raft_thickness: Raft thickness d [m]
    :param concrete_modulus: Modulus of elasticity of the raft concrete E [kPa]
    :param soil_modulus: Modulus of compressibility of the foundation soil Es [kPa]
    :param raft_length: Rectangular raft: length b of the section in the bending axis [m]
    :param raft_radius: Circular raft: radius R [m]
    :param subgrade_modulus: Modulus of subgrade reaction k for the raft width (IS 2950 App. B, IS 9214) [kN/m3]
    :param raft_width: Raft width B for lambda [m]
    :param moment_of_inertia: Moment of inertia I of the raft over width B; default B d^3 / 12 (solid slab) [m4]
    :param column_spacing: Column spacing to compare with 1.75 / lambda [m]
    :returns: K, the K criterion, and (with subgrade modulus) lambda and the critical column spacing.
    """
    kind = choice(shape, "shape", SHAPES)
    d = require_positive(raft_thickness, "raft_thickness")
    e_c = require_positive(concrete_modulus, "concrete_modulus")
    e_s = require_positive(soil_modulus, "soil_modulus")
    if kind == "rectangular":
        span = require_positive(raft_length, "raft_length")
        k_rel = e_c / (12.0 * e_s) * (d / span) ** 3
    else:
        span = 2.0 * require_positive(raft_radius, "raft_radius")
        k_rel = e_c / (12.0 * e_s) * (d / span) ** 3
    warnings: List[str] = []
    result: Dict[str, Any] = {
        "Shape": kind,
        "Relative stiffness factor K [-]": round_sig(k_rel),
        "K criterion": "rigid (K > 0.5)" if k_rel > RIGID_K else "flexible (K <= 0.5)",
    }
    rigid_by_spacing = None
    if subgrade_modulus is not None:
        k_s = require_positive(subgrade_modulus, "subgrade_modulus")
        if moment_of_inertia is not None:
            inertia = require_positive(moment_of_inertia, "moment_of_inertia")
            width = require_positive(raft_width, "raft_width")
        else:
            width = require_positive(raft_width, "raft_width") if raft_width is not None else 1.0
            inertia = width * d ** 3 / 12.0
            warnings.append("I taken as B d^3 / 12 (solid slab of uniform thickness); lambda is then independent of B.")
        lam = (k_s * width / (4.0 * e_c * inertia)) ** 0.25
        critical = CRITICAL_SPACING_FACTOR / lam
        result.update({"lambda [1/m]": round_sig(lam), "Critical column spacing 1.75/lambda [m]": round_sig(critical)})
        if column_spacing is not None:
            spacing = require_positive(column_spacing, "column_spacing")
            rigid_by_spacing = spacing < critical
            result["Column spacing [m]"] = spacing
            result["Spacing criterion"] = "rigid (spacing < 1.75/lambda)" if rigid_by_spacing else "flexible (spacing >= 1.75/lambda)"
    elif column_spacing is not None:
        raise BISInputError("'subgrade_modulus' is required to compare the column spacing with 1.75/lambda.")

    if k_rel > RIGID_K or rigid_by_spacing:
        method = "Rigid foundation (conventional method, cl. 5.1) may be used"
    elif rigid_by_spacing is None:
        method = "Flexible on the K criterion; check the column spacing criterion (needs subgrade modulus) before choosing the method"
    else:
        method = "Flexible foundation (cl. 5.2) - simplified method if adjacent column loads vary by <= 20 %, else plate theory"
    result["Analysis method"] = method
    warnings.append("Cl. 5.1.3 / 5.2.1 also require adjacent column loads (and spacings) to vary by no more than 20 % "
                    "for the strip / simplified methods; check this separately.")
    result["Standard"] = f"{STANDARD}, cl. 5.1-5.2, Appendix C"
    result["warnings"] = warnings
    return result
