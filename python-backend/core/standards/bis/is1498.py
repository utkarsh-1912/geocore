# Author: Utkarsh Gupta
# License: GPL v3
"""
IS 1498:1970 (Reaffirmed) - Classification and identification of soils for general engineering
purposes: laboratory classification (clause 3.5).

* 3.1 / 3.2   coarse-grained if more than half is retained on the 75-micron sieve; gravel if more than
              half of the coarse fraction is retained on the 4.75 mm sieve; fine-grained soils are
              split by liquid limit into L (< 35), I (35-50) and H (> 50).
* Table 3     GW: Cu > 4 and Cc 1-3; SW: Cu > 6 and Cc 1-3; fines < 5 % clean, > 12 % dirty,
              5-12 % borderline (dual symbol); M below the A-line or Ip < 4, C above it with Ip > 7,
              above the A-line with Ip 4-7 dual (GM-GC, SM-SC).
* 3.5.2       a borderline case of a borderline case favours the non-plastic symbol (GW-GM, not GW-GC).
* 3.5.3       A-line Ip = 0.73 (wL - 20); 3.5.3.1 organic if the oven-dried liquid limit is below 3/4 of
              the liquid limit before drying; 3.5.4 boundary symbols on the A-line and wL = 35 / 50
              lines, ML-CL above the A-line with Ip 4-7.
Highly organic soils (Pt) are identified visually, so they are flagged by the caller.
"""
from typing import Any, Dict, List, Optional

from core.standards.bis._common import BISInputError, require_positive, round_sig

STANDARD = "IS 1498:1970 (Reaffirmed)"

GROUP_NAMES = {
    "GW": "Well graded gravel", "GP": "Poorly graded gravel", "GM": "Silty gravel", "GC": "Clayey gravel",
    "SW": "Well graded sand", "SP": "Poorly graded sand", "SM": "Silty sand", "SC": "Clayey sand",
    "ML": "Inorganic silt of low compressibility", "CL": "Inorganic clay of low compressibility",
    "OL": "Organic silt / clay of low compressibility",
    "MI": "Inorganic silt of medium compressibility", "CI": "Inorganic clay of medium compressibility",
    "OI": "Organic silt / clay of medium compressibility",
    "MH": "Inorganic silt of high compressibility", "CH": "Inorganic clay of high compressibility",
    "OH": "Organic clay of medium to high compressibility",
    "Pt": "Peat and other highly organic soil",
}


def a_line(liquid_limit: float) -> float:
    """Plasticity index on the A-line, Ip = 0.73 (wL - 20) (IS 1498 cl. 3.5.3)."""
    return 0.73 * (liquid_limit - 20.0)


def _name(symbol: str) -> str:
    return " / ".join(GROUP_NAMES[s] for s in symbol.split("-"))


def _plasticity(liquid_limit: Optional[float], plastic_limit: Optional[float], non_plastic: bool,
                what: str) -> Optional[float]:
    if non_plastic:
        return 0.0
    if liquid_limit is None or plastic_limit is None:
        raise BISInputError(f"Liquid and plastic limits are required to classify {what} "
                            "(or set non_plastic = true when the plastic limit cannot be determined).")
    return max(0.0, float(liquid_limit) - float(plastic_limit))  # IS 2720 Part 5 cl. 8.2(b)


def _fines_symbol(ip: float, ll: Optional[float]) -> str:
    """M / C / M-C for the fines of a coarse-grained soil (Table 3)."""
    if ll is None:  # non-plastic fines
        return "M"
    above = ip > a_line(ll)
    if not above or ip < 4.0:
        return "M"
    if ip > 7.0:
        return "C"
    return "M-C"


def classify_soil_is1498(percent_fines: float, percent_gravel: float = 0.0,
                         liquid_limit: Optional[float] = None, plastic_limit: Optional[float] = None,
                         non_plastic: bool = False, d10: Optional[float] = None, d30: Optional[float] = None,
                         d60: Optional[float] = None, liquid_limit_oven_dried: Optional[float] = None,
                         highly_organic: bool = False, boundary_tolerance: float = 0.0) -> Dict[str, Any]:
    """
    Indian Standard Soil Classification (IS 1498:1970 laboratory method, cl. 3.5).

    :param percent_fines: Percentage passing the 75-micron IS sieve [%]
    :param percent_gravel: Percentage retained on the 4.75 mm IS sieve (gravel, 80-4.75 mm) [%]
    :param liquid_limit: Liquid limit wL [%]
    :param plastic_limit: Plastic limit wP [%]
    :param non_plastic: True when the plastic limit cannot be determined (Ip reported as NP)
    :param d10: Particle size with 10 percent finer [mm]
    :param d30: Particle size with 30 percent finer [mm]
    :param d60: Particle size with 60 percent finer [mm]
    :param liquid_limit_oven_dried: Liquid limit after oven drying, to identify organic fines [%]
    :param highly_organic: True for peat / highly organic soil identified visually (Pt)
    :param boundary_tolerance: Distance from the A-line or the wL = 35 / 50 lines within which a soil is treated as lying on the line [%]
    :returns: Group symbol, group name, fractions, gradation coefficients and plasticity data.
    """
    fines = require_positive(percent_fines, "percent_fines", allow_zero=True)
    gravel = require_positive(percent_gravel, "percent_gravel", allow_zero=True)
    tol = require_positive(boundary_tolerance, "boundary_tolerance", allow_zero=True)
    if fines > 100.0 or gravel > 100.0 or fines + gravel > 100.0 + 1e-9:
        raise BISInputError("percent_fines + percent_gravel must not exceed 100 %.")
    sand = 100.0 - fines - gravel
    notes: List[str] = []
    result: Dict[str, Any] = {}

    if highly_organic:
        symbol, division = "Pt", "Highly organic soil"
        result.update({"Group symbol": symbol, "Group name": _name(symbol), "Division": division})
        result["Standard"] = f"{STANDARD}, cl. 3.1.3"
        result["warnings"] = ["Highly organic soils are identified by colour, odour and fibrous texture, not by laboratory limits."]
        return result

    ll = float(liquid_limit) if liquid_limit is not None else None
    if ll is not None and not 0.0 < ll <= 1000.0:
        raise BISInputError("'liquid_limit' must be a percentage above 0.")
    if fines <= 50.0:
        division = "Coarse-grained"
        is_gravel = gravel > sand
        prefix = "G" if is_gravel else "S"
        cu = cc = None
        grading = None
        if fines <= 12.0:
            if None in (d10, d30, d60):
                raise BISInputError("D10, D30 and D60 are required to grade a coarse-grained soil with 12 % fines or less (IS 1498 Table 3).")
            d10v, d30v, d60v = (require_positive(v, n) for v, n in ((d10, "d10"), (d30, "d30"), (d60, "d60")))
            if not d10v <= d30v <= d60v:
                raise BISInputError("Grain sizes must satisfy D10 <= D30 <= D60.")
            cu = d60v / d10v
            cc = d30v ** 2 / (d10v * d60v)
            well = cu > (4.0 if is_gravel else 6.0) and 1.0 <= cc <= 3.0
            grading = "W" if well else "P"
        if fines < 5.0:
            symbol = prefix + grading
        else:
            ip = _plasticity(ll, plastic_limit, non_plastic, "the fines")
            fines_sym = _fines_symbol(ip, None if non_plastic else ll)
            if fines <= 12.0:
                # Borderline clean/dirty; a borderline-of-borderline favours the non-plastic symbol (cl. 3.5.2)
                second = "M" if fines_sym == "M-C" else fines_sym
                symbol = f"{prefix}{grading}-{prefix}{second}"
                notes.append("5-12 % fines: borderline between clean and dirty soil, dual symbol (IS 1498 cl. 3.5.2).")
                if fines_sym == "M-C":
                    notes.append("Ip between 4 and 7 above the A-line: the non-plastic symbol is favoured (cl. 3.5.2).")
            else:
                symbol = f"{prefix}M-{prefix}C" if fines_sym == "M-C" else prefix + fines_sym
            result["Plasticity index Ip [%]"] = "NP" if non_plastic else round_sig(ip)
        result.update({"Gravel [%]": round_sig(gravel), "Sand [%]": round_sig(sand), "Fines [%]": round_sig(fines)})
        if cu is not None:
            result["Uniformity coefficient Cu [-]"] = round_sig(cu)
            result["Coefficient of curvature Cc [-]"] = round_sig(cc)
    else:
        division = "Fine-grained"
        ip = _plasticity(ll, plastic_limit, non_plastic, "a fine-grained soil")
        if ll is None:
            raise BISInputError("'liquid_limit' is required to classify a fine-grained soil.")
        ip_a = a_line(ll)
        comp = ["L"] if ll < 35.0 else (["I"] if ll <= 50.0 else ["H"])
        if abs(ll - 35.0) <= tol:
            comp = ["L", "I"]
        elif abs(ll - 50.0) <= tol:
            comp = ["I", "H"]
        organic = None
        if liquid_limit_oven_dried is not None:
            organic = float(liquid_limit_oven_dried) < 0.75 * ll
        silt_letter = "O" if organic else "M"
        if ip > ip_a + tol and 4.0 <= ip <= 7.0:
            symbol = "ML-CL"
            notes.append("Above the A-line with Ip between 4 and 7: ML-CL (IS 1498 cl. 3.5.4).")
        elif abs(ip - ip_a) <= tol and not non_plastic:
            symbol = "-".join(f"{silt_letter}{c}" for c in comp) + "-" + "-".join(f"C{c}" for c in comp)
            notes.append("Plots on the A-line: boundary classification (IS 1498 cl. 3.5.4).")
        elif ip > ip_a:
            symbol = "-".join(f"C{c}" for c in comp)
        else:
            symbol = "-".join(f"{silt_letter}{c}" for c in comp)
            if organic is None:
                notes.append("Below the A-line the group may be organic (O) instead of M; an oven-dried liquid "
                             "limit below 3/4 of wL identifies organic soil (IS 1498 cl. 3.5.3.1).")
        if len(comp) == 2:
            notes.append(f"Liquid limit on the wL = {35 if 'L' in comp else 50} line: boundary classification (cl. 3.5.4).")
        result.update({"Gravel [%]": round_sig(gravel), "Sand [%]": round_sig(sand), "Fines [%]": round_sig(fines),
                       "Liquid limit wL [%]": round_sig(ll),
                       "Plasticity index Ip [%]": "NP" if non_plastic else round_sig(ip),
                       "A-line Ip at this wL [%]": round_sig(ip_a)})
        if organic is not None:
            result["Organic (oven-dried wL < 0.75 wL)"] = organic

    result = {"Group symbol": symbol, "Group name": _name(symbol), "Division": division, **result}
    result["Standard"] = f"{STANDARD}, cl. 3.5, Table 3, Fig. 1"
    result["warnings"] = notes
    return result
