# Author: Utkarsh Gupta
# License: GPL v3
"""
IS 2131:1981 (Reaffirmed) - Method for standard penetration test for soils, clause 3.6 corrections.

* 3.6.1  overburden correction of N in cohesionless soil, Fig. 1. The figure is the Peck, Hanson &
         Thornburn (1974) curve CN = 0.77 log10(20 / sigma'v), sigma'v in kgf/cm2, limited to 2.0
         (checked against the digitised figure at 0.25-5 kgf/cm2). Fig. 1 spans 0-5 kgf/cm2.
* 3.6.2  dilatancy correction for fine sand and silt below the water table: N'' = 15 + (N' - 15) / 2
         when N' > 15.

IS 2131 was revised in 2025 (second revision, 14 July 2025), which is reported to add an energy
correction. Its text could not be verified, so the optional normalisation here is the generic
N60 = N x ER / 60 (ISO 22476-3, ASTM D6066), clearly labelled, and applied only when the measured
energy ratio is supplied.
"""
import math
from typing import Any, Dict, List, Optional

from core.standards.bis._common import KGF_PER_CM2_IN_KPA, BISInputError, require_positive, round_sig

STANDARD = "IS 2131:1981 (Reaffirmed)"
CN_MAX = 2.0
FIG1_MAX_STRESS_KGF = 5.0


def overburden_correction_factor_is2131(effective_overburden_pressure: float) -> float:
    """CN of IS 2131 Fig. 1 for an effective vertical overburden pressure in kPa."""
    sigma_kgf = require_positive(effective_overburden_pressure, "effective_overburden_pressure") / KGF_PER_CM2_IN_KPA
    return min(CN_MAX, 0.77 * math.log10(20.0 / sigma_kgf))


def spt_correction_is2131(n_observed: float, effective_overburden_pressure: float,
                          fine_sand_or_silt_below_water_table: bool = False,
                          energy_ratio: Optional[float] = None) -> Dict[str, Any]:
    """
    Corrected SPT N for cohesionless soil to IS 2131:1981 cl. 3.6 (overburden, then dilatancy).

    :param n_observed: Observed N value, blows per 300 mm penetration [-]
    :param effective_overburden_pressure: Effective vertical overburden pressure at the test depth [kPa]
    :param fine_sand_or_silt_below_water_table: True if the stratum is fine sand or silt below the water table (cl. 3.6.2)
    :param energy_ratio: Measured hammer energy ratio; if given N is first normalised to 60 % energy (not part of IS 2131:1981) [%]
    :returns: Overburden factor CN, N after each correction and the corrected N.
    """
    n = require_positive(n_observed, "n_observed", allow_zero=True)
    sigma = require_positive(effective_overburden_pressure, "effective_overburden_pressure")
    warnings: List[str] = ["IS 2131 cl. 3.6 corrections apply to cohesionless soil."]
    result: Dict[str, Any] = {"Observed N [-]": n}

    if energy_ratio is not None:
        er = require_positive(energy_ratio, "energy_ratio")
        if er > 100.0:
            raise BISInputError("'energy_ratio' is a percentage of the theoretical free-fall energy (0-100 %).")
        n = n * er / 60.0
        result["Energy ratio [%]"] = er
        result["N60 [-]"] = round_sig(n)
        warnings.append("Energy normalisation N60 = N x ER / 60 (ISO 22476-3 / ASTM D6066) is not part of IS 2131:1981; "
                        "check it against the energy correction of IS 2131:2025 before use.")

    sigma_kgf = sigma / KGF_PER_CM2_IN_KPA
    cn = overburden_correction_factor_is2131(sigma)
    if sigma_kgf > FIG1_MAX_STRESS_KGF:
        warnings.append(f"Effective overburden {sigma:g} kPa is beyond the {FIG1_MAX_STRESS_KGF:g} kgf/cm2 "
                        f"({FIG1_MAX_STRESS_KGF * KGF_PER_CM2_IN_KPA:.0f} kPa) range of IS 2131 Fig. 1; CN is extrapolated.")
    if cn >= CN_MAX:
        warnings.append("CN limited to 2.0, the maximum of IS 2131 Fig. 1.")
    n_prime = cn * n
    result.update({
        "Effective overburden [kgf/cm2]": round_sig(sigma_kgf),
        "Overburden correction CN [-]": round_sig(cn),
        "N' after overburden correction [-]": round_sig(n_prime),
    })
    n_corr = n_prime
    if fine_sand_or_silt_below_water_table and n_prime > 15.0:
        n_corr = 15.0 + 0.5 * (n_prime - 15.0)
        result["N'' after dilatancy correction [-]"] = round_sig(n_corr)
    elif fine_sand_or_silt_below_water_table:
        warnings.append("Dilatancy correction not applied: N' does not exceed 15 (IS 2131 cl. 3.6.2).")
    result["Corrected N [-]"] = round_sig(n_corr)
    result["Standard"] = f"{STANDARD}, cl. 3.6, Fig. 1"
    result["warnings"] = warnings
    return result
