# Author: Utkarsh Gupta
# License: GPL v3
"""
IS 2720 - Methods of test for soils: calculations from laboratory readings.

* Part 3/Sec 1:1980  specific gravity G = (m2 - m1) / ((m4 - m1) - (m3 - m2)), referred to 27 degC by
                     G27 = G x (density of water at T / density of water at 27 degC) (cl. 5).
* Part 5:1985        flow index If = (w1 - w2) / log10(N2 / N1) (cl. 3.5.2); one-point liquid limit,
                     Casagrande wL = wN / (1.3215 - 0.23 log10 N), 15-35 blows (cl. 5.6), cone
                     wL = wN / (0.77 log10 D) or wN / (0.65 + 0.0175 D), D 16-26 mm (cl. 6.5);
                     Ip = wL - wP (0 when wP >= wL, cl. 8), It = Ip / If (cl. 9),
                     IL = (w - wP) / Ip (cl. 10), Ic = (wL - w) / Ip (cl. 11).
* Part 17:1986       constant head kT = Q L / (A h t); falling head kT = 2.303 a L / (A t) log10(h1 / h2);
                     k27 = kT x viscosity(T) / viscosity(27 degC) (cl. 5.4, 6.3).
Water density and viscosity are not tabulated in IS 2720; standard correlations are used (see _common).
"""
import math
from typing import Any, Dict, List, Optional

from core.standards.bis._common import (BISInputError, choice, require_positive, round_sig, water_density,
                                        water_viscosity)

REFERENCE_TEMPERATURE = 27.0


def specific_gravity_is2720(mass_bottle: float, mass_bottle_soil: float, mass_bottle_soil_water: float,
                            mass_bottle_water: float, temperature: float = 27.0) -> Dict[str, Any]:
    """
    Specific gravity of soil particles by density bottle, IS 2720 (Part 3/Sec 1):1980 cl. 5.

    :param mass_bottle: m1, mass of the empty density bottle [g]
    :param mass_bottle_soil: m2, mass of bottle and dry soil [g]
    :param mass_bottle_soil_water: m3, mass of bottle, soil and water [g]
    :param mass_bottle_water: m4, mass of bottle full of water only [g]
    :param temperature: Room/test temperature [degC]
    :returns: G at the test temperature and G corrected to 27 degC.
    """
    m1, m2, m3, m4 = (float(v) for v in (mass_bottle, mass_bottle_soil, mass_bottle_soil_water, mass_bottle_water))
    soil = m2 - m1
    displaced = (m4 - m1) - (m3 - m2)
    if soil <= 0 or displaced <= 0:
        raise BISInputError("Masses are inconsistent: need m2 > m1 and (m4 - m1) > (m3 - m2).")
    g = soil / displaced
    ratio = water_density(temperature) / water_density(REFERENCE_TEMPERATURE)
    warnings: List[str] = ["Report the average of two determinations to 0.01; repeat if they differ by more than 0.03 (cl. 6.1)."]
    if not 2.0 <= g <= 3.2:
        warnings.append(f"G = {g:.3f} is outside the usual 2.0-3.2 range for soils; check the readings.")
    return {
        "Specific gravity at test temperature [-]": round_sig(g),
        "Temperature correction factor K [-]": round_sig(ratio, 6),
        "Specific gravity at 27 degC [-]": round_sig(g * ratio),
        "Standard": "IS 2720 (Part 3/Sec 1):1980, cl. 5",
        "warnings": warnings,
    }


def flow_index_is2720(water_content_1: float, blows_1: float, water_content_2: float, blows_2: float) -> Dict[str, Any]:
    """
    Flow index from two points of the flow curve, IS 2720 (Part 5):1985 cl. 3.5.2.

    :param water_content_1: Water content w1 at N1 drops [%]
    :param blows_1: Number of drops N1 [-]
    :param water_content_2: Water content w2 at N2 drops [%]
    :param blows_2: Number of drops N2 [-]
    :returns: Flow index If (percent water content per log cycle of drops).
    """
    n1 = require_positive(blows_1, "blows_1")
    n2 = require_positive(blows_2, "blows_2")
    if n1 == n2:
        raise BISInputError("The two points need different numbers of drops.")
    i_f = (float(water_content_1) - float(water_content_2)) / math.log10(n2 / n1)
    return {"Flow index If [%]": round_sig(i_f), "Standard": "IS 2720 (Part 5):1985, cl. 3.5.2", "warnings": []}


def liquid_limit_one_point_is2720(water_content: float, method: str = "casagrande", blows: Optional[float] = None,
                                  cone_penetration: Optional[float] = None) -> Dict[str, Any]:
    """
    Liquid limit by the one-point method, IS 2720 (Part 5):1985 cl. 5 (Casagrande) or cl. 6 (cone).

    :param water_content: Water content wN of the accepted trial [%]
    :param method: Apparatus. Options: casagrande, cone
    :param blows: Casagrande: number of drops to close the groove, 15-35 [-]
    :param cone_penetration: Cone: penetration D of the accepted trial, 16-26 [mm]
    :returns: Liquid limit (cone: both relationships of cl. 6.5).
    """
    kind = choice(method, "method", ("casagrande", "cone"))
    w = require_positive(water_content, "water_content")
    warnings = ["The one-point method is not for highly organic soils; its constants are regional, and national/"
                "international reports should use the multi-point or cone method (cl. 1.1.1)."]
    if kind == "casagrande":
        n = require_positive(blows, "blows")
        if not 15.0 <= n <= 35.0:
            raise BISInputError("The Casagrande one-point formula applies to 15-35 drops (IS 2720 Part 5 cl. 5.6).")
        wl = w / (1.3215 - 0.23 * math.log10(n))
        result = {"Liquid limit wL [%]": round_sig(wl), "Standard": "IS 2720 (Part 5):1985, cl. 5.6"}
    else:
        dpen = require_positive(cone_penetration, "cone_penetration")
        if not 16.0 <= dpen <= 26.0:
            raise BISInputError("The cone one-point relationships apply to 16-26 mm penetration (IS 2720 Part 5 cl. 6.4).")
        wl_log = w / (0.77 * math.log10(dpen))
        wl_lin = w / (0.65 + 0.0175 * dpen)
        result = {"Liquid limit wL, log relation [%]": round_sig(wl_log),
                  "Liquid limit wL, linear relation [%]": round_sig(wl_lin),
                  "Standard": "IS 2720 (Part 5):1985, cl. 6.5"}
    result["warnings"] = warnings
    return result


def consistency_indices_is2720(liquid_limit: float, plastic_limit: float,
                               natural_water_content: Optional[float] = None,
                               flow_index: Optional[float] = None) -> Dict[str, Any]:
    """
    Plasticity, liquidity, consistency and toughness indices, IS 2720 (Part 5):1985 cl. 8-11.

    :param liquid_limit: Liquid limit wL [%]
    :param plastic_limit: Plastic limit wP [%]
    :param natural_water_content: Natural water content w0 [%]
    :param flow_index: Flow index If, for the toughness index [%]
    :returns: Ip and, as inputs allow, IL, Ic and It.
    """
    wl = require_positive(liquid_limit, "liquid_limit")
    wp = require_positive(plastic_limit, "plastic_limit", allow_zero=True)
    ip = max(0.0, wl - wp)
    result: Dict[str, Any] = {"Plasticity index Ip [%]": round_sig(ip)}
    warnings: List[str] = []
    if ip == 0.0:
        warnings.append("Plastic limit >= liquid limit: Ip reported as zero (cl. 8.2 b); IL, Ic and It are undefined.")
    else:
        if natural_water_content is not None:
            w0 = require_positive(natural_water_content, "natural_water_content", allow_zero=True)
            result["Liquidity index IL [-]"] = round_sig((w0 - wp) / ip)
            result["Consistency index Ic [-]"] = round_sig((wl - w0) / ip)
        if flow_index is not None:
            i_f = require_positive(flow_index, "flow_index")
            result["Toughness index It [-]"] = round_sig(ip / i_f)
    result["Standard"] = "IS 2720 (Part 5):1985, cl. 8-11"
    result["warnings"] = warnings
    return result


def _refer_to_27(k_t: float, temperature: float) -> Dict[str, Any]:
    ratio = water_viscosity(temperature) / water_viscosity(REFERENCE_TEMPERATURE)
    return {"Viscosity ratio eta_T/eta_27 [-]": round_sig(ratio, 5),
            "Permeability at 27 degC k27 [cm/s]": round_sig(k_t * ratio)}


def permeability_constant_head_is2720(discharge_volume: float, specimen_length: float, specimen_area: float,
                                      head_loss: float, time: float, temperature: float = 27.0) -> Dict[str, Any]:
    """
    Coefficient of permeability by the constant head test, IS 2720 (Part 17):1986 cl. 5.4.

    :param discharge_volume: Quantity of water Q collected [cm3]
    :param specimen_length: Length of specimen L between head measuring points [cm]
    :param specimen_area: Cross-sectional area of specimen A [cm2]
    :param head_loss: Head loss h over length L [cm]
    :param time: Collection time t [s]
    :param temperature: Water temperature T [degC]
    :returns: Hydraulic gradient, kT and k27.
    """
    q = require_positive(discharge_volume, "discharge_volume")
    length = require_positive(specimen_length, "specimen_length")
    area = require_positive(specimen_area, "specimen_area")
    h = require_positive(head_loss, "head_loss")
    t = require_positive(time, "time")
    k_t = q * length / (area * h * t)
    return {"Hydraulic gradient i [-]": round_sig(h / length),
            "Permeability at test temperature kT [cm/s]": round_sig(k_t),
            **_refer_to_27(k_t, temperature),
            "Standard": "IS 2720 (Part 17):1986, cl. 5.4",
            "warnings": _permeability_warnings(k_t)}


def permeability_falling_head_is2720(standpipe_area: float, specimen_length: float, specimen_area: float,
                                     initial_head: float, final_head: float, time: float,
                                     temperature: float = 27.0) -> Dict[str, Any]:
    """
    Coefficient of permeability by the falling head test, IS 2720 (Part 17):1986 cl. 6.3.

    :param standpipe_area: Cross-sectional area of the stand-pipe a [cm2]
    :param specimen_length: Length of specimen L [cm]
    :param specimen_area: Cross-sectional area of specimen A [cm2]
    :param initial_head: Initial head h1 [cm]
    :param final_head: Final head h2 [cm]
    :param time: Elapsed time tf - ti [s]
    :param temperature: Water temperature T [degC]
    :returns: kT and k27.
    """
    a = require_positive(standpipe_area, "standpipe_area")
    length = require_positive(specimen_length, "specimen_length")
    area = require_positive(specimen_area, "specimen_area")
    h1 = require_positive(initial_head, "initial_head")
    h2 = require_positive(final_head, "final_head")
    t = require_positive(time, "time")
    if h2 >= h1:
        raise BISInputError("In a falling head test the final head must be lower than the initial head.")
    k_t = 2.303 * a * length / (area * t) * math.log10(h1 / h2)
    return {"Permeability at test temperature kT [cm/s]": round_sig(k_t),
            **_refer_to_27(k_t, temperature),
            "Standard": "IS 2720 (Part 17):1986, cl. 6.3",
            "warnings": _permeability_warnings(k_t)}


def _permeability_warnings(k_t: float) -> List[str]:
    if not 1e-7 <= k_t <= 1e-3:
        return [f"k = {k_t:.2e} cm/s is outside the 1e-3 to 1e-7 cm/s range recommended for this test (IS 2720 Part 17 cl. 1.1)."]
    return []
