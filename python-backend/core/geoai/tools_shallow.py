# Author: Utkarsh Gupta
# License: GPL v3
"""
GeoAI shallow-foundation design tools (AGENTS.md §5-8, §14, §16-18).

* ``calculate_shallow_foundation_capacity`` drives Groundhog's stateful
  ``ShallowFoundationCapacityDrained`` / ``ShallowFoundationCapacityUndrained`` classes
  (API RP 2GEO bearing capacity equations) in one validated call.
* ``calculate_foundation_settlement`` sums Groundhog's one-dimensional consolidation settlement
  (``primaryconsolidationsettlement_nc`` / ``_oc`` or ``consolidationsettlement_mv``) over
  sublayers, with the vertical stress increase below the footing centre from Groundhog's
  Boussinesq solutions (``stresses_rectangle`` / ``stresses_circle`` / ``stresses_stripload``),
  i.e. the procedure of Groundhog's ``SettlementCalculation`` extended with footing embedment,
  user-given e0 / sigma'p and a reported discretisation.

Groundhog does every engineering calculation. This module only orchestrates: it resolves inputs
(user value, else the current project's soil profile with provenance, else a structured
missing-parameter error), computes geostatic stresses at base level (sum of gamma x thickness,
u = gamma_w x depth below the water table) and reports results. Values are ultimate / calculated;
factors of safety and limit-state checks are out of scope and said so in every result (§18).
"""
import math
import warnings
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

from core.geoai.exceptions import GeoAIValidationError
from core.geoai.project_soil import ProjectSoil, ResolvedValue, round_sig
from core.geoai.schemas.shallow_design import (
    FoundationSettlementInput, FoundationSettlementOutput,
    ShallowFoundationCapacityInput, ShallowFoundationCapacityOutput,
)
from core.geoai.tool_registry import geoai_tool

#: A strip is modelled as a rectangle this many times longer than wide (B/L = 0.001, so the
#: API shape factors differ from their strip values by < 0.1 %); loads are per metre run.
STRIP_LENGTH_FACTOR = 1000.0
#: Soil below the base that governs capacity: [Df, Df + 1.5 B] (as ContextResolver.resolve_layer_for_foundation).
INFLUENCE_DEPTH_FACTOR = 1.5
MIN_INFLUENCE_DEPTH = 0.5
MAX_BREAKDOWN_ROWS = 15
MAX_SUBLAYERS = 400
_TOL = 1e-9

CAPACITY_NOTE = ("Ultimate (unfactored) values. Partial factors or factors of safety, limit-state (ULS/SLS) checks, "
                 "settlement and the design decision are separate engineering steps; this result alone does not "
                 "show that a foundation is adequate.")
SETTLEMENT_NOTE = ("Calculated primary consolidation settlement for the stated inputs. Immediate (elastic) and "
                   "secondary compression settlement are not included, and allowable-settlement / serviceability "
                   "checks require engineering judgement.")


class GeoAIMissingParameterError(GeoAIValidationError):
    """Required inputs were neither given nor available in the current project (§17: ask the user)."""


# =============================================================================
# Shared helpers
# =============================================================================

@contextmanager
def _groundhog(label: str, warnings_out: List[str]) -> Iterator[None]:
    """Run Groundhog code: collect its warnings, turn its input errors into GeoAI validation errors."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            yield
        except (ValueError, TypeError, KeyError, ZeroDivisionError) as exc:
            raise GeoAIValidationError(f"Groundhog {label} rejected the inputs: {exc}") from exc
    for w in caught:
        msg = f"Groundhog: {w.message}"
        if msg not in warnings_out:
            warnings_out.append(msg)


def _finite(value: Any, what: str) -> float:
    if value is None or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise GeoAIValidationError(f"Groundhog returned no valid {what} for these inputs (result {value!r}).")
    return float(value)


class _Inputs:
    """Collects resolved inputs (with provenance) and the ones that are missing."""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.values: Dict[str, ResolvedValue] = {}
        self.missing: List[Dict[str, Any]] = []

    def resolve(self, key: str, user_value: Optional[float], unit: str, description: str,
                lookup: Optional[Callable[[], Tuple[Optional[ResolvedValue], str]]] = None,
                field: Optional[str] = None, required: bool = True) -> Optional[ResolvedValue]:
        if user_value is not None:
            resolved = ResolvedValue(float(user_value), unit, "user input")
        else:
            resolved, reason = lookup() if lookup else (None, "")
            if resolved is None:
                if required:
                    self.add_missing(field or key, unit, description, reason)
                return None
        self.values[key] = resolved
        return resolved

    def add_missing(self, field: str, unit: str, description: str, reason: str = "") -> None:
        if any(m["field"] == field for m in self.missing):
            return
        self.missing.append({"field": field, "unit": unit, "description": description,
                             "project_lookup": reason or "not looked up", "type": "missing_parameter"})

    def raise_if_missing(self) -> None:
        if not self.missing:
            return
        parts = [f"{m['field']} [{m['unit']}] ({m['description']}; project: {m['project_lookup']})"
                 for m in self.missing]
        raise GeoAIMissingParameterError(
            f"Missing input(s) for {self.tool_name} - ask the user for them, do not assume values: "
            + "; ".join(parts), errors=self.missing)

    def provenance(self) -> Dict[str, Any]:
        return {k: v.to_dict() for k, v in self.values.items()}


@dataclass
class _Footing:
    shape: str             # strip / square / rectangular / circular
    width: float           # B (diameter for circular) [m]
    length: float          # L used in Groundhog [m] (STRIP_LENGTH_FACTOR x B for a strip; nan for circular)
    per_metre: bool        # strip: loads and capacity per metre run

    @property
    def area(self) -> float:
        if self.shape == "circular":
            return 0.25 * math.pi * self.width ** 2
        return self.width * self.length

    def describe(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"shape": self.shape, "B_m": round_sig(self.width)}
        if self.shape in ("rectangular", "square"):
            d["L_m"] = round_sig(self.length)
            d["area_m2"] = round_sig(self.area)
        elif self.shape == "circular":
            d["diameter_m"] = round_sig(self.width)
            d["area_m2"] = round_sig(self.area)
        else:
            d["modelled_as"] = f"rectangle with L = {STRIP_LENGTH_FACTOR:g} B; values per metre run"
        return d


def _footing(shape: str, width: float, length: Optional[float], notes: List[str]) -> _Footing:
    if shape == "rectangular":
        if length is None:
            raise GeoAIMissingParameterError(
                "Missing input for a rectangular footing - ask the user: length_m [m] (footing length L).",
                errors=[{"field": "length_m", "unit": "m", "type": "missing_parameter",
                         "description": "footing length L"}])
        if length < width:
            notes.append(f"Length ({length:g} m) was smaller than width ({width:g} m); B and L were swapped "
                         f"so that B is the shorter side.")
            width, length = length, width
        return _Footing("rectangular", width, length, False)
    if length is not None and abs(length - width) > _TOL and shape != "circular":
        notes.append(f"length_m = {length:g} m ignored for a {shape} footing.")
    if shape == "square":
        return _Footing("square", width, width, False)
    if shape == "circular":
        return _Footing("circular", width, float("nan"), False)
    return _Footing("strip", width, STRIP_LENGTH_FACTOR * width, True)


def _influence_zone(depth: float, width: float) -> Tuple[float, float]:
    return depth, depth + max(MIN_INFLUENCE_DEPTH, INFLUENCE_DEPTH_FACTOR * width)


class _GeostaticStress:
    """Total stress, pore pressure and effective stress (kPa) versus depth below ground surface (m)."""

    def __init__(self, segments: List[Tuple[float, float, float]], groundwater_depth: Optional[float],
                 saturated_unit_weight: Optional[float], unit_weight_water: float):
        self.segments = sorted(segments)
        self.zw = groundwater_depth
        self.gamma_sat = saturated_unit_weight
        self.gamma_w = unit_weight_water

    def total(self, z: float) -> float:
        sigma = 0.0
        for top, bottom, gamma in self.segments:
            if top >= z:
                break
            bottom = min(bottom, z)
            if self.gamma_sat is None or self.zw is None:
                sigma += gamma * (bottom - top)
                continue
            dry = max(0.0, min(bottom, self.zw) - top)
            wet = (bottom - top) - dry
            sigma += gamma * dry + self.gamma_sat * wet
        return sigma

    def pore(self, z: float) -> float:
        return self.gamma_w * max(0.0, z - self.zw) if self.zw is not None else 0.0

    def effective(self, z: float) -> float:
        return self.total(z) - self.pore(z)


def _uniform_segments(gamma: float, z_bottom: float) -> List[Tuple[float, float, float]]:
    return [(0.0, max(z_bottom, _TOL), gamma)]


# =============================================================================
# Bearing capacity
# =============================================================================

def _eccentricities(ft: _Footing, V: Optional[float], H: float, Mb: float, Ml: float,
                    eB: float, eL: float, inputs: _Inputs, notes: List[str]) -> Tuple[float, float]:
    """(e_B, e_L) in metres from moments (e = M / V) or direct eccentricities."""
    if (Mb > 0 and eB > 0) or (Ml > 0 and el_positive(eL) and Ml > 0):
        raise GeoAIValidationError("Give either a moment or an eccentricity in each direction, not both.")
    if (Mb > 0 or Ml > 0 or H > 0) and V is None:
        inputs.add_missing("vertical_load_kn", "kN/m" if ft.per_metre else "kN",
                           "applied vertical load V, needed to convert moments to eccentricity / "
                           "horizontal load to load inclination", "not a soil parameter")
        return 0.0, 0.0
    e_b = Mb / V if Mb > 0 else eB
    e_l = Ml / V if Ml > 0 else eL
    if ft.shape == "circular":
        e = math.hypot(e_b, e_l)
        if e_l > 0:
            notes.append("Circular footing: eccentricities in both directions combined as e = sqrt(e_B^2 + e_L^2).")
        if e >= 0.5 * ft.width - _TOL:
            raise GeoAIValidationError(f"Eccentricity {e:.3g} m is at or beyond the footing edge (radius "
                                       f"{0.5 * ft.width:g} m); the load resultant must lie within the base.")
        return e, 0.0
    if ft.per_metre and e_l > 0:
        notes.append("Strip footing: eccentricity along the length ignored.")
        e_l = 0.0
    if e_b >= 0.5 * ft.width - _TOL or (not ft.per_metre and e_l >= 0.5 * ft.length - _TOL):
        raise GeoAIValidationError(f"Eccentricity (e_B = {e_b:.3g} m, e_L = {e_l:.3g} m) reaches the footing edge "
                                   f"(B/2 = {0.5 * ft.width:g} m); the load resultant must lie within the base.")
    return e_b, e_l


def el_positive(e: float) -> bool:
    return e > 0


def _choose_analysis(analysis: Optional[str], phi: Optional[float], su: Optional[float], inputs: _Inputs) -> str:
    if analysis:
        return analysis
    if phi is not None and su is None:
        return "drained"
    if su is not None and phi is None:
        return "undrained"
    reason = ("both phi' and su were given" if phi is not None
              else "no strength parameter was given")
    inputs.add_missing("analysis", "-", "'drained' (long-term, effective stress, phi') or 'undrained' "
                       "(short-term, total stress, su)", reason)
    inputs.raise_if_missing()
    return ""  # unreachable


def _set_up_groundhog_capacity(calc: Any, ft: _Footing, depth: float, skirted: bool, e_b: float, e_l: float,
                               warnings_out: List[str]) -> None:
    with _groundhog("shallow foundation geometry", warnings_out):
        if ft.shape == "circular":
            calc.set_geometry(option="circle", diameter=ft.width, depth=depth, skirted=skirted)
            calc.set_eccentricity(eccentricity_width=e_b)
        else:
            calc.set_geometry(option="rectangle", length=ft.length, width=ft.width, depth=depth, skirted=skirted)
            calc.set_eccentricity(eccentricity_width=e_b, eccentricity_length=e_l)
    _finite(calc.effective_area, "effective area")


def _footing_result(ft: _Footing, calc: Any, depth: float, e_b: float, e_l: float) -> Dict[str, Any]:
    d = ft.describe()
    d["Df_m"] = round_sig(depth)
    d["effective_width_m"] = round_sig(calc.effective_width)
    if ft.shape == "circular":
        d["eccentricity_m"] = round_sig(e_b)
        d["effective_length_m"] = round_sig(calc.effective_length)
    else:
        d["e_B_m"] = round_sig(e_b)
        if not ft.per_metre:
            d["e_L_m"] = round_sig(e_l)
            d["effective_length_m"] = round_sig(calc.effective_length)
    if not ft.per_metre:
        d["effective_area_m2"] = round_sig(calc.effective_area)
    return d


def _capacity_outputs(ft: _Footing, calc: Any) -> Dict[str, Any]:
    q = _finite(calc.capacity["qu [kPa]"], "ultimate bearing pressure")
    Q = _finite(calc.capacity["vertical_capacity [kN]"], "vertical capacity")
    out: Dict[str, Any] = {"q_ult_kpa": round_sig(q)}
    if ft.per_metre:
        out["Q_ult_kn_per_m"] = round_sig(Q / calc.effective_length)
    else:
        out["Q_ult_kn"] = round_sig(Q)
        out["effective_area_m2"] = round_sig(calc.effective_area)
    return out


def _capacity_drained(ft: _Footing, depth: float, skirted: bool, e_b: float, e_l: float,
                      V: Optional[float], H: float, gw: float, phi: Optional[float], c_eff: Optional[float],
                      gamma: Optional[float], gamma_sat: Optional[float], zw: Optional[float],
                      project: ProjectSoil, inputs: _Inputs, notes: List[str], warn: List[str]) -> Dict[str, Any]:
    z_top, z_bot = _influence_zone(depth, ft.width)
    inputs.resolve("friction_angle_deg", phi, "deg", "effective friction angle phi' below the base",
                   lambda: project.representative("friction_angle", z_top, z_bot, "deg"))
    if depth > 0:
        inputs.resolve("unit_weight_above_base_kn_m3", gamma, "kN/m3", "total unit weight above the base",
                       lambda: project.representative("unit_weight", 0.0, depth, "kN/m3"),
                       field="unit_weight_kn_m3")
    inputs.resolve("unit_weight_below_base_kn_m3", gamma, "kN/m3", "total unit weight below the base",
                   lambda: project.representative("unit_weight", z_top, z_bot, "kN/m3"),
                   field="unit_weight_kn_m3")
    inputs.resolve("groundwater_depth_m", zw, "m", "groundwater depth below ground surface",
                   project.groundwater_depth)
    inputs.resolve("saturated_unit_weight_kn_m3", gamma_sat, "kN/m3", "saturated unit weight",
                   lambda: project.representative("saturated_unit_weight", 0.0, z_bot, "kN/m3"), required=False)
    c_res = inputs.resolve("effective_cohesion_kpa", c_eff, "kPa", "effective cohesion c'",
                           lambda: project.representative("effective_cohesion", z_top, z_bot, "kPa"), required=False)
    inputs.raise_if_missing()

    v = inputs.values
    phi_v = v["friction_angle_deg"].value
    if not 20.0 <= phi_v <= 50.0:
        raise GeoAIValidationError(f"phi' = {phi_v:.3g} deg is outside the 20-50 deg range of the API RP 2GEO "
                                   f"drained method implemented in Groundhog.")
    zw_v = v["groundwater_depth_m"].value
    g_below = v["unit_weight_below_base_kn_m3"].value
    g_above = v["unit_weight_above_base_kn_m3"].value if depth > 0 else g_below
    g_sat = v["saturated_unit_weight_kn_m3"].value if "saturated_unit_weight_kn_m3" in v else None

    # Geostatic stress at base level (sum of gamma x thickness; u = gamma_w x depth below the water table).
    above = _GeostaticStress(_uniform_segments(g_above, depth), zw_v, g_sat if g_sat is not None else g_above, gw)
    sigma_v0 = above.total(depth)
    p0_eff = above.effective(depth)
    if p0_eff < -_TOL:
        raise GeoAIValidationError("Negative vertical effective stress at base level; check unit weights and groundwater.")
    p0_eff = max(0.0, p0_eff)

    # Unit weight in the N_gamma term: submerged if the water table is at/above the base, moist if it is at
    # least B below the base, linear in between (Das, Principles of Foundation Engineering, Sec. 3.6 cases).
    g_sub = (g_sat if g_sat is not None else g_below) - gw
    d_w = zw_v - depth
    if d_w <= 0:
        gamma_n, gamma_n_rule = g_sub, "submerged (water table at or above the base)"
    elif d_w >= ft.width:
        gamma_n, gamma_n_rule = g_below, "moist total unit weight (water table >= B below the base)"
    else:
        gamma_n = g_sub + (d_w / ft.width) * (g_below - g_sub)
        gamma_n_rule = f"interpolated (water table {d_w:g} m below the base, B = {ft.width:g} m)"
    if gamma_n <= 0:
        raise GeoAIValidationError(f"Effective unit weight below the base is {gamma_n:.3g} kN/m3 (<= 0); check the "
                                   f"saturated unit weight and gamma_w.")

    theta = math.degrees(math.atan2(H, V)) if H > 0 and V else 0.0
    kwargs: Dict[str, Any] = {"fail_silently": False, "load_inclination": theta}
    if not 3.0 <= gamma_n <= 12.0:
        # Groundhog's API range is for submerged offshore soils; the equation itself is unchanged.
        kwargs["effective_unit_weight__min"] = min(3.0, gamma_n)
        kwargs["effective_unit_weight__max"] = max(12.0, gamma_n)
        notes.append(f"Unit weight in the N_gamma term ({gamma_n:.3g} kN/m3) is outside Groundhog's API RP 2GEO "
                     f"suggested range 3-12 kN/m3 (submerged offshore soils); the same equation is applied.")

    from groundhog.shallowfoundations.capacity import ShallowFoundationCapacityDrained
    calc = ShallowFoundationCapacityDrained(title="GeoAI drained bearing capacity")
    _set_up_groundhog_capacity(calc, ft, depth, skirted, e_b, e_l, warn)
    calc.set_soilparameters_drained(effective_unit_weight=gamma_n, friction_angle=phi_v, effective_stress_base=p0_eff)
    with _groundhog("verticalcapacity_drained_api", warn):
        calc.calculate_bearing_capacity(**kwargs)
    cap = calc.capacity

    if c_res is not None and c_res.value > 0:
        warn.append(f"c' = {c_res.value:.3g} kPa ({c_res.source}) is NOT included: the API RP 2GEO drained method "
                    f"in Groundhog has no cohesion term, so the result neglects c' (lower than a c'-phi' solution).")
    basis = ("net of the overburden at base level ((Nq - 1) term; skirted foundation)" if skirted and depth > 0
             else "gross effective bearing pressure (Nq term includes the overburden p0' at base level)")
    factors = {k.split(" ")[0]: round_sig(cap[k], 4) for k in
               ("N_q [-]", "N_gamma [-]", "K_q [-]", "K_gamma [-]", "s_q [-]", "s_gamma [-]",
                "d_q [-]", "d_gamma [-]", "i_q [-]", "i_gamma [-]")}
    factors["load_inclination_deg"] = round_sig(theta, 4)
    out = _capacity_outputs(ft, calc)
    out.update({
        "analysis": "drained",
        "bearing_pressure_basis": basis,
        "method": ("API RP 2GEO (2011) drained vertical bearing capacity, q_u = p0'(N_q or N_q - 1)K_q + "
                   "0.5 gamma' B' N_gamma K_gamma (Groundhog ShallowFoundationCapacityDrained / "
                   "verticalcapacity_drained_api)"),
        "footing": _footing_result(ft, calc, depth, e_b, e_l),
        "factors": factors,
        "stresses": {"sigma_v0_base_kpa": round_sig(sigma_v0), "u_base_kpa": round_sig(above.pore(depth)),
                     "p0_eff_base_kpa": round_sig(p0_eff), "gamma_in_N_gamma_term_kn_m3": round_sig(gamma_n),
                     "gamma_in_N_gamma_term_rule": gamma_n_rule, "gamma_w_kn_m3": gw},
    })
    return out


def _capacity_undrained(ft: _Footing, depth: float, skirted: bool, e_b: float, e_l: float, H: float,
                        su: Optional[float], su_increase: float, gamma: Optional[float],
                        project: ProjectSoil, inputs: _Inputs, notes: List[str], warn: List[str]) -> Dict[str, Any]:
    z_top, z_bot = _influence_zone(depth, ft.width)
    inputs.resolve("undrained_shear_strength_kpa", su, "kPa", "undrained shear strength su at/below the base",
                   lambda: project.representative("undrained_shear_strength", z_top, z_bot, "kPa"))
    needs_overburden = depth > 0 and not skirted
    if needs_overburden or gamma is not None:
        inputs.resolve("unit_weight_above_base_kn_m3", gamma, "kN/m3",
                       "total unit weight above the base (overburden at base level)",
                       lambda: project.representative("unit_weight", 0.0, depth, "kN/m3"),
                       field="unit_weight_kn_m3", required=needs_overburden)
    inputs.raise_if_missing()

    v = inputs.values
    su_v = v["undrained_shear_strength_kpa"].value
    gamma_v = v["unit_weight_above_base_kn_m3"].value if "unit_weight_above_base_kn_m3" in v else 0.0
    if su_increase > 0:
        inputs.values["su_increase_kpa_per_m"] = ResolvedValue(su_increase, "kPa/m", "user input")
        if needs_overburden and abs(ft.length - ft.width) > _TOL and ft.shape != "circular":
            warn.append("Groundhog adds the overburden term as sigma_v0 x B' x B' (not B' x L') when su increases "
                        "with depth for a non-skirted, embedded footing; Q_ult for this non-square footing "
                        "carries that simplification.")

    from groundhog.shallowfoundations.capacity import ShallowFoundationCapacityUndrained
    calc = ShallowFoundationCapacityUndrained(title="GeoAI undrained bearing capacity")
    _set_up_groundhog_capacity(calc, ft, depth, skirted, e_b, e_l, warn)
    calc.set_soilparameters_undrained(unit_weight=gamma_v, su_base=su_v, su_increase=su_increase)
    h_model = H * ft.length if ft.per_metre else H
    with _groundhog("verticalcapacity_undrained_api", warn):
        calc.calculate_bearing_capacity(horizontal_load=h_model, fail_silently=False)
    cap = calc.capacity

    sigma_v0 = gamma_v * depth
    basis = ("net bearing pressure su N_c K_c; Q_ult adds the overburden sigma_v0 x A' (non-skirted, embedded)"
             if needs_overburden else "net bearing pressure su N_c K_c (no overburden term)")
    factors = {"N_c": 5.14}
    factors.update({k.split(" ")[0]: round_sig(cap[k], 4) for k in
                    ("K_c [-]", "s_c [-]", "d_c [-]", "i_c [-]") if cap.get(k) is not None})
    if su_increase > 0:
        factors["F"] = round_sig(cap["F [-]"], 4)
        factors["Su2_kpa"] = round_sig(cap["Su2 [kPa]"], 4)
    out = _capacity_outputs(ft, calc)
    out.update({
        "analysis": "undrained",
        "bearing_pressure_basis": basis,
        "method": ("API RP 2GEO (2011) undrained vertical bearing capacity, q_u = su N_c K_c (constant su) or "
                   "F (su0 N_c + kappa B'/4) K_c (linearly increasing su) (Groundhog "
                   "ShallowFoundationCapacityUndrained / verticalcapacity_undrained_api)"),
        "footing": _footing_result(ft, calc, depth, e_b, e_l),
        "factors": factors,
        "stresses": {"sigma_v0_base_kpa": round_sig(sigma_v0),
                     "su_above_base_kpa": round_sig(calc.su_above_base)},
    })
    if depth > 0:
        notes.append("Average su above the base taken equal to su at the base (Groundhog default).")
    return out


@geoai_tool(
    name="calculate_shallow_foundation_capacity",
    description=("Calculates the ultimate bearing capacity of a shallow foundation (footing, pad, strip or raft): "
                 "q_ult [kPa] and Q_ult [kN] for drained sand/gravel (phi') or undrained clay (su), with "
                 "embedment depth, groundwater, eccentric or inclined load (effective area). Missing soil "
                 "parameters are taken from the current project soil profile with their source."),
    category="shallow_foundations",
    input_model=ShallowFoundationCapacityInput,
    output_model=ShallowFoundationCapacityOutput,
)
def calculate_shallow_foundation_capacity(
    foundation_shape: str,
    width_m: float,
    foundation_depth_m: float,
    length_m: Optional[float] = None,
    analysis: Optional[str] = None,
    friction_angle_deg: Optional[float] = None,
    effective_cohesion_kpa: Optional[float] = None,
    undrained_shear_strength_kpa: Optional[float] = None,
    su_increase_kpa_per_m: float = 0.0,
    unit_weight_kn_m3: Optional[float] = None,
    saturated_unit_weight_kn_m3: Optional[float] = None,
    groundwater_depth_m: Optional[float] = None,
    vertical_load_kn: Optional[float] = None,
    horizontal_load_kn: float = 0.0,
    moment_b_knm: float = 0.0,
    moment_l_knm: float = 0.0,
    eccentricity_b_m: float = 0.0,
    eccentricity_l_m: float = 0.0,
    skirted: bool = False,
    unit_weight_water_kn_m3: float = 10.0,
    soil_profile: Optional[str] = None,
) -> Dict[str, Any]:
    notes: List[str] = []
    warn: List[str] = []
    inputs = _Inputs("calculate_shallow_foundation_capacity")
    ft = _footing(foundation_shape, width_m, length_m, notes)
    e_b, e_l = _eccentricities(ft, vertical_load_kn, horizontal_load_kn, moment_b_knm, moment_l_knm,
                               eccentricity_b_m, eccentricity_l_m, inputs, notes)
    kind = _choose_analysis(analysis, friction_angle_deg, undrained_shear_strength_kpa, inputs)
    project = ProjectSoil(soil_profile)

    if kind == "drained":
        out = _capacity_drained(ft, foundation_depth_m, skirted, e_b, e_l, vertical_load_kn, horizontal_load_kn,
                                unit_weight_water_kn_m3, friction_angle_deg, effective_cohesion_kpa,
                                unit_weight_kn_m3, saturated_unit_weight_kn_m3, groundwater_depth_m,
                                project, inputs, notes, warn)
    else:
        if horizontal_load_kn > 0 and vertical_load_kn is None:
            inputs.raise_if_missing()
        out = _capacity_undrained(ft, foundation_depth_m, skirted, e_b, e_l, horizontal_load_kn,
                                  undrained_shear_strength_kpa, su_increase_kpa_per_m, unit_weight_kn_m3,
                                  project, inputs, notes, warn)

    uses_project = any(not r.source.startswith("user") for r in inputs.values.values())
    if uses_project and project.profile_note():
        warn.append(project.profile_note())
    if max(e_b, e_l) > 0 and (e_b > ft.width / 6 or (not ft.per_metre and ft.shape != "circular"
                                                         and e_l > ft.length / 6)):
        warn.append("Load resultant lies outside the middle third of the base (e > B/6): part of the base "
                    "is not in contact under this load.")
    z_top, z_bot = _influence_zone(foundation_depth_m, ft.width)
    assumptions = [
        "Homogeneous soil below the base: one representative strength over the influence zone "
        f"{z_top:g}-{z_bot:g} m (Df to Df + 1.5B); layered-soil (e.g. punch-through) failure is not checked.",
        "Eccentric load: effective area A' = B' x L' (API RP 2GEO); horizontal load enters through the "
        "load-inclination factor.",
        "Foundation base and ground surface horizontal (no base or slope inclination factors).",
    ] + notes
    out.update({
        "soil_parameters": inputs.provenance(),
        "assumptions": assumptions,
        "warnings": warn,
        "note": CAPACITY_NOTE,
    })
    return out


# =============================================================================
# Settlement
# =============================================================================

@dataclass
class _ClayLayer:
    label: str
    top: float
    bottom: float
    params: Dict[str, ResolvedValue]
    method: str = ""       # "mv" or "cc"


def _net_pressure(ft: _Footing, q_gross: float, depth: float, use_net: bool,
                  stress: Optional[_GeostaticStress]) -> float:
    if not use_net or depth <= 0 or stress is None:
        return q_gross
    return q_gross - stress.total(depth)


def _stress_increase(ft: _Footing, z_below_base: float, q_net: float) -> float:
    """Vertical stress increase [kPa] below the footing centre (Groundhog Boussinesq solutions)."""
    from groundhog.shallowfoundations.stressdistribution import (
        stresses_circle, stresses_rectangle, stresses_stripload)
    if ft.shape == "circular":
        r = stresses_circle(z=z_below_base, footing_radius=0.5 * ft.width, imposedstress=q_net,
                            poissonsratio=0.3, fail_silently=False)
        return abs(r["delta sigma z [kPa]"])
    if ft.shape == "strip":
        r = stresses_stripload(z=z_below_base, x=0.5 * ft.width, width=ft.width, imposedstress=q_net,
                               fail_silently=False)
        return abs(r["delta sigma z [kPa]"])
    r = stresses_rectangle(imposedstress=q_net, length=0.5 * ft.length, width=0.5 * ft.width, z=z_below_base,
                           fail_silently=False)
    return 4.0 * abs(r["delta sigma z [kPa]"])


def _layer_parameters(layer: _ClayLayer, user: Dict[str, Optional[float]], project: ProjectSoil,
                      project_layer: Optional[Dict[str, Any]], inputs: _Inputs) -> None:
    """Resolve Cc/Cr/e0/OCR/sigma'p or mv for one compressible layer (user value > project value)."""
    specs = {  # key: (project parameter, unit, description)
        "mv_per_kpa": ("mv", "1/kPa", "coefficient of volume compressibility mv"),
        "compression_index": ("compression_index", "-", "compression index Cc"),
        "recompression_index": ("recompression_index", "-", "recompression index Cr"),
        "initial_void_ratio": ("initial_void_ratio", "-", "initial void ratio e0"),
        "ocr": ("ocr", "-", "overconsolidation ratio OCR"),
        "preconsolidation_pressure_kpa": ("preconsolidation_pressure", "kPa", "preconsolidation pressure sigma'p"),
    }
    found: Dict[str, ResolvedValue] = {}
    reasons: Dict[str, str] = {}
    for key, (param, unit, _desc) in specs.items():
        if user.get(key) is not None:
            found[key] = ResolvedValue(float(user[key]), unit, "user input")
            continue
        if project_layer is not None:
            value, note = project.layer_value(project_layer, param, unit)
            if value is not None:
                src = f"project profile '{project.name}': {project.layer_label(project_layer)}"
                found[key] = ResolvedValue(value, unit, src + (f" [{note}]" if note else ""))
            else:
                reasons[key] = f"{project.layer_label(project_layer)}: {note}"
        else:
            r, why = project.representative(param, layer.top, layer.bottom, unit)
            if r is not None:
                found[key] = r
            else:
                reasons[key] = why

    def user_given(k: str) -> bool:
        return found.get(k) is not None and found[k].source == "user input"

    if user_given("mv_per_kpa") or (not user_given("compression_index") and "mv_per_kpa" in found):
        layer.method = "mv"
        layer.params = {"mv_per_kpa": found["mv_per_kpa"]}
        return
    layer.method = "cc"
    tag = f" for {layer.label}"
    if "compression_index" not in found:
        inputs.add_missing("compression_index", "-", "compression index Cc (or give mv_per_kpa [1/kPa])" + tag,
                           reasons.get("compression_index", ""))
    if "initial_void_ratio" not in found:
        inputs.add_missing("initial_void_ratio", "-", "initial void ratio e0" + tag,
                           reasons.get("initial_void_ratio", ""))
    if "ocr" not in found and "preconsolidation_pressure_kpa" not in found:
        inputs.add_missing("ocr", "-", "OCR (1 = normally consolidated) or preconsolidation_pressure_kpa [kPa]" + tag,
                           reasons.get("ocr", ""))
    normally_consolidated = ("preconsolidation_pressure_kpa" not in found and "ocr" in found
                             and abs(found["ocr"].value - 1.0) < 1e-9)
    if "recompression_index" not in found and not normally_consolidated:
        inputs.add_missing("recompression_index", "-", "recompression index Cr (not needed when OCR = 1)" + tag,
                           reasons.get("recompression_index", ""))
    layer.params = {k: v for k, v in found.items() if k != "mv_per_kpa"}


def _compressible_layers(depth: float, top: Optional[float], bottom: Optional[float],
                         user: Dict[str, Optional[float]], project: ProjectSoil,
                         inputs: _Inputs, notes: List[str]) -> List[_ClayLayer]:
    if top is not None or bottom is not None:
        if top is None or bottom is None:
            inputs.add_missing("clay_top_depth_m" if top is None else "clay_bottom_depth_m", "m",
                               "top and bottom depth of the compressible layer below ground surface", "")
            inputs.raise_if_missing()
        if bottom <= top:
            raise GeoAIValidationError("clay_bottom_depth_m must be deeper than clay_top_depth_m.")
        if bottom <= depth + _TOL:
            raise GeoAIValidationError(f"The compressible layer ({top:g}-{bottom:g} m) lies above the footing base "
                                       f"({depth:g} m); it is not loaded by the footing in this model.")
        if top < depth:
            notes.append(f"Only the part of the compressible layer below the base ({depth:g}-{bottom:g} m) is "
                         f"included.")
        layer = _ClayLayer(f"clay layer {max(top, depth):g}-{bottom:g} m", max(top, depth), bottom, {})
        _layer_parameters(layer, user, project, None, inputs)
        return [layer]

    found = project.compressible_layers(depth)
    if not found:
        reason = (project.unavailable_reason if not project.available else
                  f"no layer below {depth:g} m in profile '{project.name}' defines Cc or mv")
        inputs.add_missing("clay_top_depth_m", "m", "top of the compressible clay layer below ground surface", reason)
        inputs.add_missing("clay_bottom_depth_m", "m", "bottom of the compressible clay layer", reason)
        layer = _ClayLayer("clay layer", depth, depth + 1.0, {})
        _layer_parameters(layer, user, ProjectSoil(context_loader=lambda: None), None, inputs)
        inputs.raise_if_missing()
    layers = []
    for pl in found:
        layer = _ClayLayer(project.layer_label(pl), max(pl["z_from"], depth), pl["z_to"], {})
        _layer_parameters(layer, user, project, pl, inputs)
        layers.append(layer)
    notes.append(f"Compressible layers taken from project profile '{project.name}': every layer below the base "
                 f"with Cc or mv defined ({', '.join(l.label for l in layers)}).")
    return layers


def _sublayers(layers: List[_ClayLayer], dz: float) -> Tuple[List[Tuple[_ClayLayer, float, float]], float]:
    """Equal sublayers per layer (n = ceil(H / dz), as Groundhog's CalculationGrid); capped at MAX_SUBLAYERS."""
    def build(step: float) -> List[Tuple[_ClayLayer, float, float]]:
        out = []
        for layer in layers:
            h = layer.bottom - layer.top
            n = max(1, int(math.ceil(h / step - 1e-9)))
            edges = [layer.top + h * i / n for i in range(n + 1)]
            out.extend((layer, edges[i], edges[i + 1]) for i in range(n))
        return out
    subs = build(dz)
    while len(subs) > MAX_SUBLAYERS:
        dz *= 2.0
        subs = build(dz)
    return subs, dz


def _breakdown(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compact per-depth table: each sublayer, or groups of consecutive sublayers (<= MAX_BREAKDOWN_ROWS)."""
    k = max(1, int(math.ceil(len(rows) / MAX_BREAKDOWN_ROWS)))
    table = []
    for i in range(0, len(rows), k):
        grp = rows[i:i + k]
        h = sum(r["h"] for r in grp)
        row = {"z_top_m": round_sig(grp[0]["top"], 4), "z_bottom_m": round_sig(grp[-1]["bottom"], 4),
               "layer": ", ".join(dict.fromkeys(r["layer"] for r in grp)),
               "delta_sigma_kpa": round_sig(sum(r["dsig"] * r["h"] for r in grp) / h, 4)}
        if all(r["sig0"] is not None for r in grp):
            row["sigma_v0_eff_kpa"] = round_sig(sum(r["sig0"] * r["h"] for r in grp) / h, 4)
        row["settlement_mm"] = round_sig(sum(r["dz"] for r in grp) * 1000.0, 4)
        table.append(row)
    return table


@geoai_tool(
    name="calculate_foundation_settlement",
    description=("Calculates how much a footing / shallow foundation will settle on clay: primary consolidation "
                 "settlement [mm] from Cc, Cr, e0 and OCR or preconsolidation pressure (or mv), with the "
                 "Boussinesq stress increase below the footing centre and a per-depth breakdown. Missing soil "
                 "parameters are taken from the current project soil profile with their source."),
    category="shallow_foundations",
    input_model=FoundationSettlementInput,
    output_model=FoundationSettlementOutput,
)
def calculate_foundation_settlement(
    foundation_shape: str,
    width_m: float,
    foundation_depth_m: float,
    length_m: Optional[float] = None,
    applied_pressure_kpa: Optional[float] = None,
    vertical_load_kn: Optional[float] = None,
    clay_top_depth_m: Optional[float] = None,
    clay_bottom_depth_m: Optional[float] = None,
    compression_index: Optional[float] = None,
    recompression_index: Optional[float] = None,
    initial_void_ratio: Optional[float] = None,
    preconsolidation_pressure_kpa: Optional[float] = None,
    ocr: Optional[float] = None,
    mv_per_kpa: Optional[float] = None,
    unit_weight_kn_m3: Optional[float] = None,
    saturated_unit_weight_kn_m3: Optional[float] = None,
    groundwater_depth_m: Optional[float] = None,
    use_net_pressure: bool = True,
    sublayer_thickness_m: float = 0.5,
    unit_weight_water_kn_m3: float = 10.0,
    soil_profile: Optional[str] = None,
) -> Dict[str, Any]:
    notes: List[str] = []
    warn: List[str] = []
    inputs = _Inputs("calculate_foundation_settlement")
    ft = _footing(foundation_shape, width_m, length_m, notes)
    depth = foundation_depth_m
    project = ProjectSoil(soil_profile)

    # 1. Applied pressure
    per = "kN/m" if ft.per_metre else "kN"
    if applied_pressure_kpa is not None:
        q = applied_pressure_kpa
        q_src = "user input"
        if vertical_load_kn is not None:
            q_from_v = vertical_load_kn / (ft.width if ft.per_metre else ft.area)
            if abs(q_from_v - q) > 0.01 * q:
                warn.append(f"vertical_load_kn gives q = {q_from_v:.4g} kPa, which differs from applied_pressure_kpa "
                            f"= {q:.4g} kPa; the applied pressure was used.")
    elif vertical_load_kn is not None:
        q = vertical_load_kn / (ft.width if ft.per_metre else ft.area)
        q_src = f"vertical load {vertical_load_kn:g} {per} / footing area"
    else:
        inputs.add_missing("applied_pressure_kpa", "kPa",
                           f"gross bearing pressure at the base, or vertical_load_kn [{per}]", "not a soil parameter")
        q, q_src = 0.0, ""

    # 2. Compressible layers and their parameters
    user = {"compression_index": compression_index, "recompression_index": recompression_index,
            "initial_void_ratio": initial_void_ratio, "ocr": ocr,
            "preconsolidation_pressure_kpa": preconsolidation_pressure_kpa, "mv_per_kpa": mv_per_kpa}
    layers = _compressible_layers(depth, clay_top_depth_m, clay_bottom_depth_m, user, project, inputs, notes)
    needs_effective = any(l.method == "cc" for l in layers)
    z_max = max(l.bottom for l in layers) if layers else depth

    # 3. Geostatic stresses (needed for sigma'v0 in the Cc method and for the net pressure)
    needs_total = use_net_pressure and depth > 0
    stress: Optional[_GeostaticStress] = None
    if needs_effective or needs_total:
        z_needed = z_max if needs_effective else depth
        if unit_weight_kn_m3 is not None:
            segments = _uniform_segments(unit_weight_kn_m3, z_needed)
            inputs.values["unit_weight_kn_m3"] = ResolvedValue(unit_weight_kn_m3, "kN/m3", "user input")
        else:
            segments, why = project.unit_weight_segments(z_needed)
            if segments is None:
                inputs.add_missing("unit_weight_kn_m3", "kN/m3", "total unit weight of the soil", why)
            else:
                inputs.values["unit_weight_kn_m3"] = ResolvedValue(
                    sum(g * (b - t) for t, b, g in segments) / z_needed if z_needed > 0 else segments[0][2],
                    "kN/m3", f"project profile '{project.name}': per-layer unit weights 0-{z_needed:g} m "
                             f"(value shown is the thickness-weighted mean)")
        gw_res = None
        if needs_effective or saturated_unit_weight_kn_m3 is not None:
            gw_res = inputs.resolve("groundwater_depth_m", groundwater_depth_m, "m",
                                    "groundwater depth below ground surface", project.groundwater_depth)
        if saturated_unit_weight_kn_m3 is not None:
            inputs.values["saturated_unit_weight_kn_m3"] = ResolvedValue(saturated_unit_weight_kn_m3, "kN/m3",
                                                                         "user input")
        inputs.raise_if_missing()
        stress = _GeostaticStress(segments, gw_res.value if gw_res else None, saturated_unit_weight_kn_m3,
                                  unit_weight_water_kn_m3)
    inputs.raise_if_missing()

    for layer in layers:
        for key, val in layer.params.items():
            inputs.values[f"{key} ({layer.label})" if len(layers) > 1 else key] = val
    if len(layers) == 1 and layers[0].method == "mv":
        inputs.values["mv_per_kpa"] = layers[0].params["mv_per_kpa"]

    q_net = _net_pressure(ft, q, depth, use_net_pressure, stress)
    base = {
        "applied_pressure_kpa": round_sig(q),
        "net_pressure_kpa": round_sig(q_net),
        "method": ("1D primary consolidation settlement summed over sublayers: Cc/Cr/e0 with sigma'p "
                   "(Groundhog primaryconsolidationsettlement_nc/_oc) or mv (consolidationsettlement_mv); "
                   "vertical stress increase below the footing centre from Boussinesq elastic solutions "
                   "(Groundhog stresses_rectangle x4 corners / stresses_circle / stresses_stripload), as in "
                   "Groundhog SettlementCalculation"),
        "footing": dict(ft.describe(), Df_m=round_sig(depth)),
    }
    if q_net <= 0:
        warn.append(f"Net pressure q - sigma_v0 = {q_net:.4g} kPa <= 0: the footing does not increase the vertical "
                    f"stress, so no primary consolidation settlement is calculated (heave/recompression not modelled).")
        rows, subs, dz_used = [], [], sublayer_thickness_m
    else:
        subs, dz_used = _sublayers(layers, sublayer_thickness_m)
        rows = _settlement_rows(ft, subs, depth, q_net, stress, warn)

    per_layer = []
    for layer in layers:
        s = sum(r["dz"] for r in rows if r["layer"] == layer.label) * 1000.0
        entry = {"layer": layer.label, "z_top_m": round_sig(layer.top), "z_bottom_m": round_sig(layer.bottom),
                 "method": "mv" if layer.method == "mv" else "Cc/Cr/e0",
                 "parameters": {k: round_sig(v.value) for k, v in layer.params.items()},
                 "settlement_mm": round_sig(s, 4)}
        per_layer.append(entry)
    total_mm = sum(r["dz"] for r in rows) * 1000.0

    uses_project = any(not r.source.startswith("user") for r in inputs.values.values())
    if uses_project and project.profile_note():
        warn.append(project.profile_note())
    if applied_pressure_kpa is None and vertical_load_kn is not None:
        notes.append(f"Bearing pressure q = {q_src}.")
    assumptions = [
        "Vertical stress increase below the centre of a flexible, uniformly loaded footing (elastic half-space, "
        "Boussinesq); settlement below the centre.",
        (f"Net pressure = q - sigma_v0 at the base ({depth:g} m) (overburden removed by excavation)."
         if use_net_pressure and depth > 0 else "Gross pressure applied at the base level."),
        "One-dimensional (oedometric) compression of each sublayer evaluated at its mid-depth; e_min = 0.3 cap "
        "(Groundhog default).",
        "sigma'p = OCR x sigma'v0 at each sublayer when OCR is given (Groundhog SettlementCalculation convention).",
        f"gamma_w = {unit_weight_water_kn_m3:g} kN/m3; the total unit weight is used above and below the water "
        "table unless a saturated unit weight is given.",
        "Immediate (elastic) settlement and secondary compression are not included (Groundhog provides no "
        "routine for them); time to reach this settlement (cv) is not calculated.",
    ] + notes
    base.update({
        "settlement_mm": round_sig(total_mm, 4),
        "compressible_layers": per_layer,
        "breakdown": _breakdown(rows),
        "discretisation": {"target_sublayer_thickness_m": round_sig(dz_used), "n_sublayers": len(subs),
                           "rule": "n = ceil(H / dz) equal sublayers per layer, evaluated at mid-depth"},
        "soil_parameters": inputs.provenance(),
        "assumptions": assumptions,
        "warnings": warn,
        "note": SETTLEMENT_NOTE,
    })
    return base


def _settlement_rows(ft: _Footing, subs: List[Tuple[_ClayLayer, float, float]], depth: float, q_net: float,
                     stress: Optional[_GeostaticStress], warn: List[str]) -> List[Dict[str, Any]]:
    from groundhog.shallowfoundations.settlement import (
        consolidationsettlement_mv, primaryconsolidationsettlement_nc, primaryconsolidationsettlement_oc)
    rows = []
    clamped = set()
    for layer, top, bottom in subs:
        h = bottom - top
        zc = 0.5 * (top + bottom)
        with _groundhog("stress distribution", warn):
            dsig = _stress_increase(ft, zc - depth, q_net)
        p = layer.params
        sig0 = None
        with _groundhog("consolidation settlement", warn):
            if layer.method == "mv":
                dz = consolidationsettlement_mv(initial_height=h, effective_stress_increase=dsig,
                                                compressibility=p["mv_per_kpa"].value,
                                                fail_silently=False)["delta z [m]"]
            else:
                sig0 = stress.effective(zc)
                if sig0 <= 0:
                    raise GeoAIValidationError(f"Vertical effective stress at {zc:.3g} m is {sig0:.3g} kPa (<= 0); "
                                               f"check unit weights and groundwater depth.")
                if "preconsolidation_pressure_kpa" in p:
                    pc = p["preconsolidation_pressure_kpa"].value
                else:
                    pc = p["ocr"].value * sig0
                if pc < sig0:
                    clamped.add(layer.label)
                    pc = sig0
                if "recompression_index" in p:
                    dz = primaryconsolidationsettlement_oc(
                        initial_height=h, initial_voidratio=p["initial_void_ratio"].value,
                        initial_effective_stress=sig0, preconsolidation_pressure=pc,
                        effective_stress_increase=dsig, compression_index=p["compression_index"].value,
                        recompression_index=p["recompression_index"].value, fail_silently=False)["delta z [m]"]
                else:
                    dz = primaryconsolidationsettlement_nc(
                        initial_height=h, initial_voidratio=p["initial_void_ratio"].value,
                        initial_effective_stress=sig0, effective_stress_increase=dsig,
                        compression_index=p["compression_index"].value, fail_silently=False)["delta z [m]"]
        rows.append({"layer": layer.label, "top": top, "bottom": bottom, "h": h, "dsig": dsig, "sig0": sig0,
                     "dz": _finite(dz, "sublayer settlement")})
    for label in sorted(clamped):
        warn.append(f"{label}: sigma'p below the in-situ sigma'v0 in some sublayers; sigma'p = sigma'v0 used there "
                    f"(normally consolidated).")
    return rows
