# Author: Utkarsh Gupta
# License: GPL v3
"""
Deterministic set-up of Groundhog's CPT-based axial pile capacity classes (AGENTS.md §6, §9).

Groundhog calculates; this module only prepares its inputs (CPT arrays, layering, pile
factors for the pile type) and summarises its outputs compactly with provenance:

- ``LCPCAxcapCalculation``  (groundhog.deepfoundations.axialcapacity.lcpc)
- ``KoppejanCalculation``   (groundhog.deepfoundations.axialcapacity.koppejan)
- ``DeBeerCalculation``     (groundhog.deepfoundations.axialcapacity.debeer)

``AxCapCalculation`` (API RP2GEO / Alm & Hamre unit friction on a SoilProfile of su,
relative density, interface friction angle...) is not CPT-driven in Groundhog and is not
wrapped here.

Post-processing done here (never a re-implementation of a method): shaft resistance
between the shaft start depth and the tip is read from Groundhog's cumulative shaft
resistance (LCPC ``Qs [kN]``, Koppejan ``Frs [kN]``); for De Beer, Groundhog's per-layer
formula is evaluated with the layer thickness clipped at the tip (see run_debeer: pandas 3 regression).
"""
import copy
import hashlib
import json
import math
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from core.geoai.exceptions import GeoAIValidationError
from core.geoai.project_cpt import (ProjectCPT, SBT_UNIT_WEIGHT_KN_M3, sbt_available, sbt_intervals,
                                    data_quality_flags)
from core.geoai.schemas.cpt_piles import GeoAIMissingParameterError

MAX_BREAKDOWN_ROWS = 15

METHOD_INFO = {
    "lcpc": {
        "class": "groundhog.deepfoundations.axialcapacity.lcpc.LCPCAxcapCalculation",
        "reference": "LCPC method, Bustamante & Gianeselli (1982), Pile bearing capacity prediction by means "
                     "of static penetrometer CPT, ESOPT-II (as implemented in Groundhog 0.15)",
        "cpt_below_tip_d": 1.5,     # qca averaging window 1.5D below the tip
        "min_diameter_m": 0.2,
    },
    "koppejan": {
        "class": "groundhog.deepfoundations.axialcapacity.koppejan.KoppejanCalculation",
        "reference": "Koppejan method (Dutch practice); alpha_p / alpha_s from the Koppejan pile-type table in "
                     "the Groundhog documentation (Koppejan tutorial, Figure 2)",
        "cpt_below_tip_d": 4.0,     # qcII window up to 4D below the tip (Groundhog check)
        "min_diameter_m": 0.0,
    },
    "debeer": {
        "class": "groundhog.deepfoundations.axialcapacity.debeer.DeBeerCalculation",
        "reference": "De Beer's method, Belgian practice (Huybrechts et al., 2016, as cited by Groundhog)",
        "cpt_below_tip_d": 1.0,     # unit base resistance averaged over 1D below the level
        "min_diameter_m": 0.2,
    },
}

#: Pile types (circular section). LCPC categories per Bustamante & Gianeselli (1982): base group
#: I = non-displacement (bored), II = displacement (driven); shaft IA plain/mud bored, hollow auger;
#: IIA driven precast concrete; IIB driven steel. Koppejan factors from the Groundhog table.
PILE_TYPES: Dict[str, Dict[str, Any]] = {
    "driven_closed_steel_pipe": {
        "label": "Driven closed-ended steel pipe",
        "lcpc": ("II", "IIB", "driven metal pile"),
        "koppejan": (1.0, 0.010, "Steel pile, fixed cross section; closed end; driven"),
        "debeer": True,
    },
    "driven_open_steel_pipe": {
        "label": "Driven open-ended steel pipe",
        "lcpc": None,
        "lcpc_reason": "Groundhog's LCPC class always uses the full base area and has no open-ended/plugging option",
        "koppejan": (1.0, 0.006, "Steel pile, fixed cross section; open tube; driven"),
        "debeer": False,
        "debeer_reason": "plugging of open-ended pipes is not modelled in this De Beer set-up",
    },
    "driven_precast_concrete": {
        "label": "Driven precast concrete pile (circular section)",
        "lcpc": ("II", "IIA", "driven precast pile"),
        "koppejan": (1.0, 0.010, "Concrete pile, prefabricated with fixed cross section; driven"),
        "debeer": True,
    },
    "bored_support_fluid": {
        "label": "Bored cast-in-situ pile with support fluid",
        "lcpc": ("I", "IA", "mud bored pile"),
        "koppejan": (0.5, 0.006, "Concrete pile, cast-in-situ with the use of a supporting liquid; excavated or drilled"),
        "debeer": True,
    },
    "cfa": {
        "label": "Continuous flight auger (CFA) pile",
        "lcpc": ("I", "IA", "hollow auger bored pile"),
        "koppejan": (0.8, 0.006, "Concrete pile, cast-in-situ with the use of a continuous flight auger; screwed"),
        "debeer": True,
    },
}

LCPC_SOIL_TYPES = ("Clay", "Silt", "Sand", "Chalk", "Gravel")
DEBEER_SOIL_TYPES = ("Clay", "Loam (silt)", "Sandy clay / loam (silt)", "Clayey sand / loam (silt)", "Sand")
#: Robertson SBT zone -> LCPC soil type (deterministic; Gravel/Chalk only from explicit layers).
LCPC_FROM_SBT = {2: "Clay", 3: "Clay", 4: "Silt", 5: "Sand", 6: "Sand", 7: "Sand"}

SCOPE_NOTE = ("Ultimate (unfactored) calculated axial compression resistance from the stated method. "
              "Partial/resistance and model factors, group effects, negative skin friction, settlement "
              "and structural checks are separate and not included; this result alone does not establish "
              "design adequacy.")


def _r1(v: float) -> float:
    return round(float(v), 1)


def _debeer_mapping() -> Dict[int, str]:
    from groundhog.deepfoundations.axialcapacity.debeer import DEBEER_SOILTYPES_MAPPING
    return dict(DEBEER_SOILTYPES_MAPPING)


# --------------------------------------------------------------------------- checks

def check_pile_and_method(method: str, pile_type: str, diameter: float, wall_thickness_mm: Optional[float],
                          tip: float, shaft_start: float) -> None:
    info, pile = METHOD_INFO[method], PILE_TYPES[pile_type]
    if method == "lcpc" and pile["lcpc"] is None:
        raise GeoAIValidationError(
            f"Method 'lcpc' is not applicable to pile type '{pile_type}': {pile['lcpc_reason']}. "
            f"Use method 'koppejan' (supports coring/plugged open-ended pipes), or confirm the pile is closed-ended.",
            errors=[{"field": "method", "type": "method_pile_incompatible"}])
    if method == "debeer" and not pile["debeer"]:
        raise GeoAIValidationError(
            f"Method 'debeer' is not applicable to pile type '{pile_type}': {pile['debeer_reason']}. "
            f"Use method 'koppejan'.", errors=[{"field": "method", "type": "method_pile_incompatible"}])
    if diameter < info["min_diameter_m"]:
        raise GeoAIValidationError(
            f"Method '{method}' requires a pile diameter of at least {info['min_diameter_m']} m "
            f"(Groundhog limit); got {diameter} m.", errors=[{"field": "pile_diameter_m", "type": "out_of_range"}])
    if wall_thickness_mm is not None and 2 * wall_thickness_mm / 1000.0 >= diameter:
        raise GeoAIValidationError(
            f"wall_thickness_mm = {wall_thickness_mm} mm is not smaller than the pile radius "
            f"({diameter / 2 * 1000:.0f} mm); check units (mm).", errors=[{"field": "wall_thickness_mm", "type": "out_of_range"}])
    if shaft_start >= tip:
        raise GeoAIValidationError(
            f"shaft_start_depth_m ({shaft_start} m) must be above the pile tip ({tip} m).",
            errors=[{"field": "shaft_start_depth_m", "type": "out_of_range"}])


def check_tip_against_cpt(method: str, cpt: ProjectCPT, tip: float, diameter: float) -> float:
    need = tip + METHOD_INFO[method]["cpt_below_tip_d"] * diameter
    if tip > cpt.depth_max:
        raise GeoAIValidationError(
            f"Pile tip at {tip} m is below the end of {cpt.cpt_id} ({cpt.depth_max:.2f} m). "
            f"The CPT does not reach the pile tip; a deeper CPT or a shallower tip is needed.",
            errors=[{"field": "pile_tip_depth_m", "type": "tip_below_cpt", "cpt_end_m": cpt.depth_max}])
    if need > cpt.depth_max + 1e-9:
        n = METHOD_INFO[method]["cpt_below_tip_d"]
        raise GeoAIValidationError(
            f"Method '{method}' needs CPT data to {n:g}D below the tip, i.e. to {need:.2f} m for a {diameter} m pile "
            f"with tip at {tip} m, but {cpt.cpt_id} ends at {cpt.depth_max:.2f} m. Use a shallower tip or a deeper CPT.",
            errors=[{"field": "pile_tip_depth_m", "type": "insufficient_cpt_below_tip", "required_to_m": need,
                     "cpt_end_m": cpt.depth_max}])
    if tip <= cpt.depth_min:
        raise GeoAIValidationError(
            f"Pile tip at {tip} m is above the first CPT reading of {cpt.cpt_id} ({cpt.depth_min:.2f} m).",
            errors=[{"field": "pile_tip_depth_m", "type": "tip_above_cpt"}])
    return need


# --------------------------------------------------------------------------- layering

def _canonical(value: Optional[str], allowed: Tuple[str, ...]) -> Optional[str]:
    if value is None:
        return None
    key = "".join(ch for ch in str(value).lower() if ch.isalnum())
    for a in allowed:
        if "".join(ch for ch in a.lower() if ch.isalnum()) == key:
            return a
    return None


def build_layering(method: str, cpt: ProjectCPT, layers: Optional[List[Dict[str, Any]]],
                   gw_for_sbt: Optional[float]) -> Tuple[pd.DataFrame, str, List[str]]:
    """Layering DataFrame (Groundhog column names), its source description, and notes."""
    notes: List[str] = []
    if layers:
        rows = sorted((dict(l) for l in layers), key=lambda l: l["depth_from_m"])
        if abs(rows[0]["depth_from_m"]) > 1e-6:
            raise GeoAIValidationError("soil_layers must start at 0 m.", errors=[{"field": "soil_layers", "type": "layering"}])
        for a, b in zip(rows, rows[1:]):
            if abs(a["depth_to_m"] - b["depth_from_m"]) > 1e-6:
                raise GeoAIValidationError(
                    f"soil_layers must be contiguous: a layer ends at {a['depth_to_m']} m but the next starts at "
                    f"{b['depth_from_m']} m.", errors=[{"field": "soil_layers", "type": "layering"}])
        for r in rows:
            if r["depth_to_m"] <= r["depth_from_m"]:
                raise GeoAIValidationError("Each soil layer needs depth_to_m > depth_from_m.",
                                           errors=[{"field": "soil_layers", "type": "layering"}])
        if rows[-1]["depth_to_m"] < cpt.depth_max - 1e-6:
            raise GeoAIValidationError(
                f"soil_layers end at {rows[-1]['depth_to_m']} m but {cpt.cpt_id} extends to {cpt.depth_max:.2f} m; "
                f"Groundhog needs the layering to cover the whole CPT.", errors=[{"field": "soil_layers", "type": "layering"}])
        df = pd.DataFrame({"Depth from [m]": [float(r["depth_from_m"]) for r in rows],
                           "Depth to [m]": [float(r["depth_to_m"]) for r in rows]})
        allowed = LCPC_SOIL_TYPES if method == "lcpc" else DEBEER_SOIL_TYPES if method == "debeer" else None
        if allowed:
            types = [_canonical(r.get("soil_type"), allowed) for r in rows]
            bad = [str(r.get("soil_type")) for r, t in zip(rows, types) if t is None]
            if bad:
                raise GeoAIValidationError(
                    f"soil_type {bad} not valid for method '{method}'. Allowed: {', '.join(allowed)}.",
                    errors=[{"field": "soil_layers", "type": "invalid_soil_type", "allowed": list(allowed)}])
            df["Soil type"] = types
        weights = [r.get("total_unit_weight_kn_m3") for r in rows]
        if any(w is not None for w in weights):
            if any(w is None for w in weights):
                raise GeoAIValidationError("Give total_unit_weight_kn_m3 for all soil_layers or for none.",
                                           errors=[{"field": "soil_layers", "type": "layering"}])
            df["Total unit weight [kN/m3]"] = [float(w) for w in weights]
        return df, "explicit soil_layers supplied with the request", notes

    if not sbt_available(cpt):
        raise GeoAIMissingParameterError(
            f"{cpt.cpt_id} has no usable sleeve friction (fs), so soil layering cannot be derived from the CPT. "
            f"Missing required input: soil_layers [depth_from_m, depth_to_m in m; soil_type] - "
            f"ask the user for the layering (e.g. from borehole logs).",
            errors=[{"field": "soil_layers", "type": "missing_parameter", "unit": "m",
                     "description": "explicit layering from 0 m to the CPT end"}])
    intervals = sbt_intervals(cpt, water_table_depth=gw_for_sbt)
    df = pd.DataFrame({"Depth from [m]": [iv["_top"] for iv in intervals],
                       "Depth to [m]": [iv["_bottom"] for iv in intervals]})
    zones = [iv["sbt_zone"] for iv in intervals]
    if method == "lcpc":
        df["Soil type"] = [LCPC_FROM_SBT[z] for z in zones]
        if 2 in zones:
            notes.append("Organic soil (Robertson zone 2) intervals treated as LCPC 'Clay' (soft clay and mud).")
        notes.append("LCPC soil type from Robertson SBT zone: 2-3 Clay, 4 Silt, 5-7 Sand (Gravel/Chalk only via soil_layers).")
    elif method == "debeer":
        mapping = _debeer_mapping()
        unmapped = [iv for iv in intervals if iv["sbt_zone"] not in mapping]
        if unmapped:
            spans = ", ".join(f"{iv['depth_from_m']}-{iv['depth_to_m']} m (zone {iv['sbt_zone']})" for iv in unmapped)
            raise GeoAIMissingParameterError(
                f"Groundhog's De Beer SBT mapping has no soil type for {spans}. Missing required input: soil_layers "
                f"with De Beer soil types - ask the user.",
                errors=[{"field": "soil_layers", "type": "missing_parameter", "unit": "m"}])
        df["Soil type"] = [mapping[z] for z in zones]
        notes.append("De Beer soil type from Robertson SBT zone via Groundhog DEBEER_SOILTYPES_MAPPING.")
    source = (f"derived from {cpt.cpt_id} Robertson SBT (Ic) intervals ({len(intervals)} layers; "
              f"intervals < 0.5 m merged)")
    return df, source, notes


# --------------------------------------------------------------------------- runners

def _cum_at(z: np.ndarray, cum: np.ndarray, depth: float) -> float:
    return float(np.interp(depth, z, np.nan_to_num(cum, nan=0.0)))


def _layer_rows(layering: pd.DataFrame, z: np.ndarray, cum: np.ndarray, qc: np.ndarray,
                unit_fs: Optional[np.ndarray], start: float, tip: float, soil_col: bool) -> List[Dict[str, Any]]:
    rows = []
    for _, lay in layering.iterrows():
        top, bot = max(start, float(lay["Depth from [m]"])), min(tip, float(lay["Depth to [m]"]))
        if bot <= top + 1e-9:
            continue
        sel = (z >= top) & (z <= bot)
        row = {"depth_from_m": round(top, 2), "depth_to_m": round(bot, 2)}
        if soil_col and "Soil type" in lay:
            row["soil_type"] = lay["Soil type"]
        row["qc_mean_mpa"] = round(float(np.nanmean(qc[sel])), 2) if sel.any() else None
        if unit_fs is not None:
            row["unit_shaft_friction_mean_kpa"] = round(float(np.nanmean(unit_fs[sel])), 1) if sel.any() and np.isfinite(unit_fs[sel]).any() else None
        row["shaft_resistance_kn"] = _r1(_cum_at(z, cum, bot) - _cum_at(z, cum, top))
        rows.append(row)
    return rows


def compact_rows(rows: List[Dict[str, Any]], limit: int = MAX_BREAKDOWN_ROWS) -> List[Dict[str, Any]]:
    """Merge consecutive rows so at most ``limit`` remain (sums kN, keeps depth span)."""
    if len(rows) <= limit:
        return rows
    size = math.ceil(len(rows) / limit)
    out = []
    for i in range(0, len(rows), size):
        grp = rows[i:i + size]
        merged = {"depth_from_m": grp[0]["depth_from_m"], "depth_to_m": grp[-1]["depth_to_m"],
                  "shaft_resistance_kn": _r1(sum(r["shaft_resistance_kn"] for r in grp)), "merged_layers": len(grp)}
        out.append(merged)
    return out


def run_lcpc(depth, qc, diameter, group_base, group_shaft, layering: pd.DataFrame, water_level: float,
             tip: float, start: float, truncate_to: Optional[float] = None) -> Dict[str, Any]:
    from groundhog.deepfoundations.axialcapacity.lcpc import LCPCAxcapCalculation
    from groundhog.general.soilprofile import SoilProfile
    depth, qc = np.asarray(depth, float), np.asarray(qc, float)
    if truncate_to is not None:
        keep = depth <= truncate_to
        depth, qc = depth[keep], qc[keep]
    lay = layering.copy()
    if "Total unit weight [kN/m3]" not in lay:
        lay["Total unit weight [kN/m3]"] = SBT_UNIT_WEIGHT_KN_M3
    lay["Ignore shaft friction"] = False
    calc = LCPCAxcapCalculation(depth=depth, qc=qc, diameter_pile=diameter, group_base=group_base, group_shaft=group_shaft)
    calc.set_soil_layers(soilprofile=SoilProfile(lay), water_level=water_level)
    calc.qca_calculation()
    calc.calculate_base_resistance()
    calc.calculate_shaft_resistance()
    res = calc.get_axialpileresistance(pile_penetration=tip)
    cd = calc.calculation_data
    z, cum = cd["z [m]"].to_numpy(float), cd["Qs [kN]"].to_numpy(float)
    rs = float(res["Rs [kN]"]) - _cum_at(z, cum, start)
    rb = float(res["Rb [kN]"])
    i_tip = int(np.argmin(np.abs(z - tip)))
    tip_row = cd.iloc[i_tip]
    lcpc_cat = LCPCAxcapCalculation.soiltype_lcpc(qc=tip_row["qc [MPa]"], soiltype=tip_row["Soil type"])
    from groundhog.deepfoundations.axialcapacity.lcpc import LCPC_FACTORS
    base = {"qca_at_tip_mpa": round(float(np.interp(tip, z, cd["qca [MPa]"].to_numpy(float))), 3),
            "qb_at_tip_mpa": round(float(np.interp(tip, z, cd["qb [MPa]"].to_numpy(float))), 3),
            "lcpc_soil_category_at_tip": lcpc_cat, "kc": LCPC_FACTORS["kc"][group_base][lcpc_cat],
            "base_area_m2": round(0.25 * math.pi * diameter ** 2, 4)}
    rows = _layer_rows(layering, z, cum, cd["qc [MPa]"].to_numpy(float), cd["fs [kPa]"].to_numpy(float), start, tip, True)
    warnings = []
    clay = cd[(cd["Soil type"] == "Clay") & (cd["qc [MPa]"] > 1) & (cd["qc [MPa]"] < 5) & (cd["z [m]"] <= tip + 1.5 * diameter)]
    if len(clay):
        warnings.append("Groundhog 0.15 LCPC classifies clay with 1 < qc < 5 MPa as 'Compact to stiff clay' (its "
                        "'Moderately compact clay' branch is unreachable); results follow Groundhog - review the "
                        f"{len(clay)} affected clay points.")
    return {"rs": rs, "rb": rb, "raw": res, "base": base, "rows": rows, "warnings": warnings, "calc": calc}


def run_koppejan(depth, qc, diameter, tip, layering: pd.DataFrame, water_level: float, alpha_s: float, alpha_p: float,
                 coring: bool, wall_thickness_mm: Optional[float], start: float) -> Dict[str, Any]:
    from groundhog.deepfoundations.axialcapacity.koppejan import KoppejanCalculation
    lay = layering[["Depth from [m]", "Depth to [m]"] +
                   (["Total unit weight [kN/m3]"] if "Total unit weight [kN/m3]" in layering else [])].copy()
    if "Total unit weight [kN/m3]" not in lay:
        lay["Total unit weight [kN/m3]"] = SBT_UNIT_WEIGHT_KN_M3
    lay = lay.reset_index(drop=True)
    calc = KoppejanCalculation(depth=np.asarray(depth, float), qc=np.asarray(qc, float), diameter=diameter, penetration=tip)
    calc.set_layer_properties(layer_data=lay, waterlevel=water_level)
    calc.calculate_side_friction(alpha_s=alpha_s)
    calc.calculate_base_resistance(alpha_p=alpha_p, coring=coring,
                                   wall_thickness=np.nan if wall_thickness_mm is None else wall_thickness_mm)
    d = calc.data
    z, cum = d["z [m]"].to_numpy(float), d["Frs [kN]"].to_numpy(float)
    rs = float(calc.Frs) - _cum_at(z, cum, start)
    base = {"qcI_mpa": round(float(calc.qcI), 3), "qcII_mpa": round(float(calc.qcII), 3),
            "qcIII_mpa": round(float(calc.qcIII), 3), "qc_avg_mpa": round(float(calc.qcavg), 3),
            "qb_max_mpa": round(float(calc.qbmax), 3), "qb_cap_mpa": 15.0, "base_area_m2": round(float(calc.base_area), 4)}
    rows = _layer_rows(layering, z, cum, d["qc [MPa]"].to_numpy(float), d["tau s max [kPa]"].to_numpy(float), start, tip, False)
    return {"rs": rs, "rb": float(calc.Frb), "base": base, "rows": rows, "warnings": [], "calc": calc}


def run_debeer(depth, qc, diameter, tip, layering: pd.DataFrame, water_level: float, alpha_s: float, alpha_b: float,
               start: float) -> Dict[str, Any]:
    from groundhog.deepfoundations.axialcapacity.debeer import DeBeerCalculation
    from groundhog.general.soilprofile import SoilProfile
    lay = layering.copy().reset_index(drop=True)
    calc = DeBeerCalculation(depth=np.asarray(depth, float), qc=np.asarray(qc, float), diameter_pile=diameter, diameter_cone=0.0357)
    calc.resample_data()
    calc.set_soil_layers(soilprofile=SoilProfile(lay), water_level=water_level)
    calc.calculate_base_resistance()
    calc.correct_shaft_qc(cone_type="E")
    calc.calculate_average_qc()
    calc.calculate_unit_shaft_friction()
    calc.set_shaft_base_factors(alpha_b_tertiary_clay=alpha_b, alpha_b_other=alpha_b,
                                alpha_s_tertiary_clay=alpha_s, alpha_s_other=alpha_s)
    calc.calculate_pile_resistance(pile_penetration=tip, base_area=0.25 * math.pi * diameter ** 2,
                                   circumference=math.pi * diameter)
    # Groundhog 0.15 truncates the tip layer with a chained assignment
    # (capacity_calc["Depth to [m]"].iloc[-1] = pile_penetration), which is a no-op under pandas >= 3
    # Copy-on-Write, so its Rs integrates to the bottom of the tip layer. Its own formula
    # Rs,i = circumference * alpha_s * thickness * qs is therefore evaluated here with the thickness
    # clipped to [shaft start, tip]; this reproduces Groundhog's published test value (1313.1 kN).
    cc = calc.capacity_calc
    circumference = math.pi * diameter
    rows, rs = [], 0.0
    for _, r in cc.iterrows():
        top, bot = max(start, float(r["Depth from [m]"])), min(tip, float(r["Depth to [m]"]))
        if bot <= top + 1e-9:
            continue
        rs_i = circumference * float(r["alpha_s"]) * (bot - top) * float(r["qs [kPa]"])
        rs += rs_i
        rows.append({"depth_from_m": round(top, 2), "depth_to_m": round(bot, 2), "soil_type": r["Soil type"],
                     "qc_avg_mpa": round(float(r["qc avg [MPa]"]), 2),
                     "unit_shaft_friction_kpa": round(float(r["qs [kPa]"]), 1), "shaft_resistance_kn": _r1(rs_i)})
    warnings = []
    if abs(float(calc.Rs) - rs) > 1e-6 and start == 0.0:
        warnings.append(f"Groundhog DeBeerCalculation.Rs ({float(calc.Rs):.1f} kN) integrates to the bottom of the "
                        "tip layer under pandas 3 (chained-assignment no-op); shaft thickness clipped at the tip "
                        "by GeoCore using Groundhog's per-layer qs and alpha_s.")
    base = {"qb_at_tip_mpa": round(float(calc.qb_selected), 3), "alpha_b": alpha_b, "epsilon_b": calc.epsilon_b,
            "base_area_m2": round(0.25 * math.pi * diameter ** 2, 4), "cone_diameter_m": 0.0357}
    return {"rs": rs, "rb": float(calc.Rb), "base": base, "rows": rows, "warnings": warnings, "calc": calc}


# --------------------------------------------------------------------------- orchestration

def calculate(cpt: ProjectCPT, method: str, pile_type: str, diameter: float, tip: float,
              wall_thickness_mm: Optional[float], open_end_condition: Optional[str], shaft_start: Optional[float],
              groundwater: Optional[float], debeer_alpha_s: Optional[float], debeer_alpha_b: Optional[float],
              soil_layers: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
    info, pile = METHOD_INFO[method], PILE_TYPES[pile_type]
    start = 0.0 if shaft_start is None else float(shaft_start)
    check_pile_and_method(method, pile_type, diameter, wall_thickness_mm, tip, start)
    need_to = check_tip_against_cpt(method, cpt, tip, diameter)

    assumptions: List[str] = [f"Circular cross-section, outer diameter {diameter} m; single pile, axial compression."]
    if shaft_start is None:
        assumptions.append("Shaft resistance counted from ground level (first CPT reading) to the tip "
                           "(no shaft_start_depth_m given).")
    gw_source = "request"
    if groundwater is None and cpt.groundwater_depth_m is not None:
        groundwater, gw_source = cpt.groundwater_depth_m, cpt.groundwater_source
    if groundwater is None:
        if method == "debeer":
            raise GeoAIMissingParameterError(
                "Missing required input(s): groundwater_depth_m [m] - groundwater depth below ground level "
                "(De Beer uses effective stresses; none is stored with this CPT). Ask the user; do not assume it.",
                errors=[{"field": "groundwater_depth_m", "type": "missing_parameter", "unit": "m",
                         "description": "groundwater depth below ground level"}])
        water_level, gw_source = 0.0, None
        assumptions.append(f"No groundwater level given or stored; {method} capacity does not depend on it "
                           "(Groundhog layering uses water at 0 m; SBT classification assumes water at ground level).")
    else:
        water_level = float(groundwater)

    layering, layering_source, notes = build_layering(method, cpt, soil_layers, groundwater)
    assumptions.extend(notes)
    if not soil_layers:
        assumptions.append(f"SBT classification uses unit weight {SBT_UNIT_WEIGHT_KN_M3} kN/m3 for stresses "
                           "(core.geoai.cpt.CPTSounding).")
    if method in ("lcpc", "koppejan") and "Total unit weight [kN/m3]" not in layering:
        assumptions.append(f"Nominal unit weight {SBT_UNIT_WEIGHT_KN_M3} kN/m3 passed to Groundhog's layering "
                           f"only to compute overburden; the {method} capacity does not use it.")
    if method == "debeer" and "Total unit weight [kN/m3]" not in layering:
        assumptions.append("Unit weights: Groundhog De Beer Belgian-practice defaults (15.696 kN/m3 above, "
                           "19.62 kN/m3 below the water table).")

    d = cpt.data
    depth, qc = d["depth_m"].to_numpy(float), d["qc_mpa"].to_numpy(float)
    warnings = [f for f in data_quality_flags(cpt) if "fs channel" not in f or method != "koppejan"]
    open_ended = pile_type == "driven_open_steel_pipe"
    factors: Dict[str, Any]
    if method == "lcpc":
        gb, gs, desc = pile["lcpc"]
        dz = float(np.max(np.diff(depth))) if len(depth) > 1 else 0.0
        truncate = tip + 1.5 * diameter + 2 * dz
        out = run_lcpc(depth, qc, diameter, gb, gs, layering, water_level, tip, start, truncate_to=truncate)
        factors = {"group_base": gb, "group_shaft": gs, "pile_category": desc,
                   "fs_limits": "standard execution (Groundhog default)",
                   "basis": "Bustamante & Gianeselli (1982) pile categories - confirm for the actual pile"}
        cpt_used = [round(cpt.depth_min, 2), round(min(truncate, cpt.depth_max), 2)]
        assumptions.append("LCPC base area = full circular area; kc and alpha/fs,lim from Groundhog LCPC_FACTORS.")
    elif method == "koppejan":
        alpha_p, alpha_s, row = pile["koppejan"]
        coring = open_ended and open_end_condition == "coring"
        out = run_koppejan(depth, qc, diameter, tip, layering, water_level, alpha_s, alpha_p, coring,
                           wall_thickness_mm if coring else None, start)
        factors = {"alpha_p": alpha_p, "alpha_s": alpha_s, "table_row": row,
                   "qc_lim_mpa": "15 (layers >= 1 m thick), 12 (thinner layers)", "base_coefficient_beta": 1,
                   "crosssection_coefficient_s": 1}
        cpt_used = [round(cpt.depth_min, 2), round(cpt.depth_max, 2)]
        if open_ended:
            assumptions.append("Open-ended pipe, " + ("coring: base on the steel annulus only" if coring
                               else "plugged: base on the full circular area") + " (as specified).")
        assumptions.append("Uniform, circular pile: Koppejan beta = s = 1; qb,max capped at 15 MPa (Groundhog).")
    else:
        out = run_debeer(depth, qc, diameter, tip, layering, water_level, debeer_alpha_s, debeer_alpha_b, start)
        factors = {"alpha_s": debeer_alpha_s, "alpha_b": debeer_alpha_b, "source": "user-specified (Belgian practice)",
                   "beta_base": 1, "lambda_base": 1}
        cpt_used = [round(cpt.depth_min, 2), round(cpt.depth_max, 2)]
        assumptions.append("Electric cone (no mechanical-cone qc correction); no layer flagged as Tertiary clay; "
                           "CPT resampled to 0.2 m; standard cone diameter 0.0357 m (Groundhog defaults).")
    warnings.extend(out["warnings"])

    rs, rb = out["rs"], out["rb"]
    base_area = out["base"].get("base_area_m2")
    pile_out = {"type": pile_type, "description": pile["label"], "diameter_m": diameter, "tip_depth_m": tip,
                "shaft_start_depth_m": start, "shaft_length_m": round(tip - start, 3),
                "perimeter_m": round(math.pi * diameter, 4), "base_area_m2": base_area}
    if open_ended:
        pile_out.update({"wall_thickness_mm": wall_thickness_mm, "open_end_condition": open_end_condition})
    return {
        "cpt_id": cpt.cpt_id,
        "method": method,
        "method_reference": info["reference"],
        "groundhog_class": info["class"],
        "ultimate_shaft_resistance_kn": _r1(rs),
        "ultimate_base_resistance_kn": _r1(rb),
        "ultimate_total_resistance_kn": _r1(rs + rb),
        "pile": pile_out,
        "base_details": out["base"],
        "shaft_breakdown": compact_rows(out["rows"]),
        "method_factors": factors,
        "soil_layering_source": layering_source,
        "cpt_depth_range_m": [round(cpt.depth_min, 2), round(cpt.depth_max, 2)],
        "cpt_depth_used_m": cpt_used,
        "groundwater_depth_m": None if gw_source is None else water_level,
        "assumptions": assumptions,
        "warnings": warnings,
        "provenance": {"cpt_source": {k: v for k, v in cpt.source.items() if k != "object_id"},
                       "cpt_object_id": cpt.source.get("object_id"), "groundwater_source": gw_source,
                       "cpt_data_required_to_m": round(need_to, 2)},
        "scope_note": SCOPE_NOTE,
    }


# Groundhog's LCPC loops row by row (10-25 s on a finely spaced CPT); repeat questions reuse the result.
_RESULT_CACHE: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
_RESULT_CACHE_SIZE = 32


def _cache_key(cpt: ProjectCPT, args: Tuple[Any, ...]) -> str:
    h = hashlib.sha256()
    h.update(cpt.cpt_id.encode())
    h.update(json.dumps(list(map(str, cpt.data.columns))).encode())
    h.update(np.ascontiguousarray(cpt.data.to_numpy(dtype=float, na_value=np.nan)).tobytes())
    h.update(json.dumps([cpt.groundwater_depth_m, cpt.groundwater_source, list(args)], default=str).encode())
    return h.hexdigest()


def calculate_cached(cpt: ProjectCPT, *args: Any) -> Dict[str, Any]:
    """``calculate`` with an LRU cache keyed on the CPT data and every input. Errors are not cached."""
    key = _cache_key(cpt, args)
    if key in _RESULT_CACHE:
        _RESULT_CACHE.move_to_end(key)
        return copy.deepcopy(_RESULT_CACHE[key])
    result = calculate(cpt, *args)
    _RESULT_CACHE[key] = copy.deepcopy(result)
    if len(_RESULT_CACHE) > _RESULT_CACHE_SIZE:
        _RESULT_CACHE.popitem(last=False)
    return result
