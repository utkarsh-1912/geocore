# Author: Utkarsh Gupta
# License: GPL v3
"""
Independent numeric oracles for registered GeoAI tools (AGENTS.md §25).

Each case calls a tool through the Tool Registry and compares every expected output with a value
computed here from the textbook closed form, using only ``math``. The oracles never call
Groundhog or GeoAI code, so they catch a wrong Groundhog result, a wrong unit or argument mapping
in a tool wrapper, and regressions when Groundhog is upgraded. They are also usable as
``EvalExample.expected_result`` sources.

    python -m core.geoai.eval.numeric_oracles
"""

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

GAMMA_W = 9.81   # kN/m3, the Groundhog default for unit weight of water
G = 9.81         # m/s2
P_ATM = 100.0    # kPa


@dataclass
class OracleCase:
    id: str
    tool: str
    args: Dict[str, Any]
    expected: Dict[str, float]          # output key -> independently computed value
    source: str                          # reference for the closed form
    rel_tol: float = 1e-6
    abs_tol: float = 1e-9


def _relative_density() -> OracleCase:
    e, e_min, e_max = 0.62, 0.48, 0.91
    return OracleCase("dr_sand", "calculate_relative_density",
                      dict(void_ratio=e, e_min=e_min, e_max=e_max),
                      {"Dr [-]": (e_max - e) / (e_max - e_min)}, "Dr = (e_max - e) / (e_max - e_min)")


def _bulk_unit_weight() -> OracleCase:
    gs, e, sr = 2.65, 0.8, 1.0
    gamma = (gs + sr * e) * GAMMA_W / (1 + e)
    return OracleCase("gamma_saturated", "calculate_bulk_unit_weight",
                      dict(saturation=sr, voidratio=e, specific_gravity=gs),
                      {"bulk unit weight [kN/m3]": gamma, "effective unit weight [kN/m3]": gamma - GAMMA_W},
                      "gamma = (Gs + Sr e) gamma_w / (1 + e)")


def _void_ratio() -> OracleCase:
    n = 0.38
    return OracleCase("e_from_n", "calculate_void_ratio_from_porosity", dict(porosity=n),
                      {"voidratio [-]": n / (1 - n)}, "e = n / (1 - n)")


def _rankine() -> OracleCase:
    phi = math.radians(30)
    return OracleCase("rankine_30", "calculate_earth_pressure_rankine", dict(phi_eff=30),
                      {"Ka": (1 - math.sin(phi)) / (1 + math.sin(phi)),
                       "Kp": (1 + math.sin(phi)) / (1 - math.sin(phi))},
                      "Rankine: Ka = (1 - sin phi) / (1 + sin phi), Kp = 1 / Ka (vertical smooth wall, level backfill)")


def _gmax() -> OracleCase:
    vs, gamma = 200.0, 18.0
    rho = gamma / G * 1000.0
    return OracleCase("gmax_vs", "calculate_gmax_from_shear_wave_velocity", dict(Vs=vs, gamma=gamma),
                      {"Gmax": rho * vs ** 2 / 1000.0, "rho": rho}, "Gmax = rho Vs^2, rho = gamma / g")


def _boussinesq() -> OracleCase:
    q, z, r, nu = 1000.0, 2.0, 0.0, 0.3
    big_r = math.hypot(r, z)
    sig_z = 3 * q * z ** 3 / (2 * math.pi * big_r ** 5)
    sig_r = q / (2 * math.pi) * (3 * r ** 2 * z / big_r ** 5 - (1 - 2 * nu) / (big_r * (big_r + z)))
    sig_t = -q / (2 * math.pi) * (1 - 2 * nu) * (z / big_r ** 3 - 1 / (big_r * (big_r + z)))
    tau = 3 * q * r * z ** 2 / (2 * math.pi * big_r ** 5)
    return OracleCase("boussinesq_axis", "calculate_stresses_point_load",
                      dict(pointload=q, z=z, r=r, poissonsratio=nu),
                      {"delta sigma z [kPa]": sig_z, "delta sigma r [kPa]": sig_r,
                       "delta sigma theta [kPa]": sig_t, "delta tau rz [kPa]": tau},
                      "Boussinesq (Poulos & Davis 1974), compression positive")


def _circular_footing() -> OracleCase:
    q, a, z, nu = 100.0, 1.5, 2.0, 0.3
    sig_z = q * (1 - (1 / (1 + (a / z) ** 2)) ** 1.5)
    c = z / math.hypot(a, z)
    sig_r = q / 2 * ((1 + 2 * nu) - 2 * (1 + nu) * c + c ** 3)
    return OracleCase("circle_axis", "calculate_stresses_circular_footing",
                      dict(z=z, footing_radius=a, imposedstress=q, poissonsratio=nu),
                      {"delta sigma z [kPa]": sig_z, "delta sigma r [kPa]": sig_r},
                      "Elastic stresses on the axis of a uniformly loaded circle (Poulos & Davis 1974)",
                      rel_tol=1e-6, abs_tol=1e-9)


def _dupuit_thiem() -> OracleCase:
    r1, r2, h1, h2, qf = 10.0, 50.0, 8.0, 10.0, 0.01
    k = qf * math.log(r2 / r1) / (math.pi * (h2 ** 2 - h1 ** 2))
    return OracleCase("dupuit_unconfined", "calculate_hydraulic_conductivity_unconfined",
                      dict(radius_1=r1, radius_2=r2, piezometric_height_1=h1, piezometric_height_2=h2, flowrate=qf),
                      {"hydraulic_conductivity": k}, "Dupuit-Thiem: k = Q ln(r2/r1) / (pi (h2^2 - h1^2))")


def _spt() -> OracleCase:
    n, er, cb, cr, cs = 20, 0.60, 1.05, 1.0, 1.0   # 150 mm borehole, rods >= 10 m, sampler with liner
    n60 = n * (er / 0.60) * cb * cr * cs
    cn = min(math.sqrt(P_ATM / 50.0), 1.7)
    return OracleCase("spt_skempton_liner", "normalize_spt_test",
                      dict(raw_n=n, depth=6.0, energy_ratio=er, rod_length=10.0, borehole_diameter_mm=150.0,
                           has_liner=True, overburden_kpa=50.0),
                      {"N60": n60, "N1_60": n60 * cn},
                      "Skempton (1986) N60 = N (ER/60) Cb Cr Cs; Liao & Whitman (1986) CN = sqrt(Pa / sigma'v), cap 1.7",
                      rel_tol=1e-3)


def build_cases() -> List[OracleCase]:
    return [f() for f in (_relative_density, _bulk_unit_weight, _void_ratio, _rankine, _gmax, _boussinesq,
                          _circular_footing, _dupuit_thiem, _spt)]


def run_cases(registry=None, cases: Optional[List[OracleCase]] = None) -> List[str]:
    """Run the cases; return one message per mismatch (empty list = all oracles agree)."""
    import core.geoai.tool_definitions  # noqa: F401  (registers the tools)
    from core.geoai.tool_registry import tool_registry
    reg = registry or tool_registry
    problems: List[str] = []
    for case in cases or build_cases():
        try:
            out = reg.invoke_tool(case.tool, case.args)
        except Exception as e:  # a failing tool is a mismatch, not a crash
            problems.append(f"{case.id}: {case.tool} raised {type(e).__name__}: {str(e)[:160]}")
            continue
        for key, want in case.expected.items():
            got = out.get(key)
            if got is None:
                problems.append(f"{case.id}: output has no '{key}' (keys: {sorted(k for k in out if not k.startswith('_'))})")
            elif not math.isclose(float(got), want, rel_tol=case.rel_tol, abs_tol=case.abs_tol):
                problems.append(f"{case.id}: {key} = {float(got):.8g}, oracle {want:.8g} ({case.source})")
    return problems


if __name__ == "__main__":
    found = run_cases()
    print("\n".join(found) if found else f"all {len(build_cases())} numeric oracles agree")
    raise SystemExit(1 if found else 0)
