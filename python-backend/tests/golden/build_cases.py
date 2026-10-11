# Author: Utkarsh Gupta
# License: GPL v3
"""
Build tests/golden/cases.json: one or more requests for every calculation the desktop app can open.

Inputs come from the function's own validation schema (the one /api/execute applies): its default when it
has one, else a typical engineering value for the parameter (by name, then by unit) clamped into the
schema's range, else the middle of the range. Calculations whose forms post saved objects or column names
(piles, settlement, consolidation, plotting, EC7, ...) use the hand-written CURATED requests below, which
mirror what their forms send.

    python tests/golden/build_cases.py      # rewrites cases.json (then re-record outputs on purpose)
"""
import json
import os
import re
import sys
import tempfile
import typing
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))

TYPICAL_BY_NAME = {
    "sigma_vo_eff": 100.0, "sigma_vo": 120.0, "vertical_effective_stress": 100.0, "initial_effective_stress": 50.0,
    "effective_stress_increase": 50.0, "depth": 5.0, "z": 5.0, "N": 15, "Qtn_cs": 100.0, "Qtn": 100.0,
    "acceleration": 0.2, "qc": 5.0, "qt": 5.0, "fs": 0.05, "u2": 0.1, "phi": 30.0, "phi_eff": 30.0,
    "friction_angle": 30.0, "cohesion": 10.0, "undrained_shear_strength": 50.0, "su": 50.0, "su_base": 50.0,
    "width": 2.0, "length": 3.0, "effective_width": 2.0, "effective_length": 3.0, "diameter": 0.5,
    "imposedstress": 100.0, "initial_height": 0.02, "time": 3600.0, "drainagelength": 2.0, "drainage_length": 2.0,
    "embedded_length": 10.0, "toe_depth": 10.0, "offset": 1.0, "relative_density": 0.6, "Dr": 60.0,
    "plasticity_index": 20.0, "liquid_limit": 40.0, "water_content": 25.0, "void_ratio": 0.7, "e": 0.7,
    "gamma": 18.0, "bulkunitweight": 18.0, "unitweight": 18.0, "specific_gravity": 2.65, "Gs": 2.65,
    "saturation": 1.0, "porosity": 0.4, "ocr": 2.0, "OCR": 2.0, "Vs": 200.0, "vs": 200.0, "magnitude": 7.5,
    "CRR": 0.2, "CSR": 0.15, "MSF": 1.0, "K_sigma": 1.0, "x": 1.0, "y": 1.0,
    "lat1": 51.0, "lon1": 4.0, "lat2": 51.1, "lon2": 4.1, "lat3": 51.05, "lon3": 4.2,
}
TYPICAL_BY_UNIT = {
    "kPa": 100.0, "MPa": 5.0, "m": 2.0, "mm": 50.0, "cm": 5.0, "deg": 30.0, "%": 20.0, "pct": 20.0,
    "kN/m3": 18.0, "kN/m³": 18.0, "kN": 1000.0, "kN/m": 10.0, "kNm": 100.0, "kNm2": 1000.0, "s": 3600.0,
    "m/s": 200.0, "g": 0.2, "m/s2": 9.81, "m2": 1.0, "m^2": 1.0, "m4": 0.01, "kg/m3": 1800.0, "Hz": 1.0,
    "years": 10.0, "m^2/yr": 2.0, "m2/yr": 2.0, "-": 0.5,
}

CPT_PILE = {"soilprofile": "@cpt_profile", "pile_diameter": "0.5", "qc_col": "qc [MPa]", "water_level": 0}
CURATED = {
    "KoppejanCalculation": [dict(CPT_PILE, pile_penetration="8", depth_from_col="Depth from [m]",
                                 depth_to_col="Depth to [m]", gamma_col="Total unit weight [kN/m3]",
                                 water_unit_weight=10, alpha_s=0.006, alpha_p=0.3, base_coefficient=1,
                                 crosssection_coefficient=1, coring=False)],
    "LCPC_Calculation": [dict(CPT_PILE, group_base="I", group_shaft="IA", careful_execution=False,
                              depth_col="Depth to [m]", soil_type_col="Soil type")],
    "DeBeerCalculation": [dict(CPT_PILE, cone_diameter=0.0357, depth_col="Depth to [m]", soil_type_col="Soil type",
                               tertiary_clay_col="Tertiary clay", gamma_col="Total unit weight [kN/m3]")],
    "mohrcoulomb_triaxial_compression": [{"sigma_3": 20, "cohesion": 10, "phi": 35}, {"sigma_3": 100, "cohesion": 0, "phi": 30}],
    "mohrcoulomb_triaxial_extension": [{"sigma_1": 300, "cohesion": 0, "phi": 30}],
    "contactwidth": [{"diameter": 2, "penetration": 1.4}, {"diameter": 1, "penetration": 0.2}],
    "SoilProfile": [{"raw_data": "@layer_rows", "data_kind": "soil_profile"}],
    # App-only calculations (no backend schema): the fields their forms post (features/calculations/schemas).
    "offsets_api": [{"x1": 0, "y1": 0, "x2": 10, "y2": 0, "xp": 4, "yp": 3, "latlon": False}],
    "PileSettlementCurves": [{"diameter": 0.6, "shaft_resistance": 1500, "base_resistance": 800, "pile_type": "driven"},
                             {"diameter": 0.6, "shaft_resistance": 1500, "base_resistance": 800, "pile_type": "bored"}],
    "shallow_foundation_capacity_drained": [{"foundation_shape": "rectangle", "length": 3, "width": 2,
                                             "eccentricity_length": 0, "eccentricity_width": 0,
                                             "effective_unit_weight": 9, "friction_angle": 32,
                                             "effective_stress_base": 20, "vertical_load": 1500, "base_depth": 1,
                                             "skirted": False, "factor_sliding": 1.5, "factor_bearing": 2}],
    "shallow_foundation_capacity_undrained": [{"foundation_shape": "rectangle", "length": 3, "width": 2,
                                               "eccentricity_length": 0, "eccentricity_width": 0, "unit_weight": 18,
                                               "su_base": 50, "su_increase": 0, "su_above_base": 40, "base_depth": 1,
                                               "skirted": False, "factor_sliding": 1.5, "factor_bearing": 2}],
    "settlement_calculation": [{"soilprofile": "@layer_profile", "foundation_width": 2, "foundation_shape": "strip",
                                "foundation_length": 0, "skirt_depth": 0, "applied_stress": 100, "water_level": 1}],
    "consolidation_calculation": [{"height": 4, "total_time": 3.15e7, "no_nodes": 50, "cv": 3e-7, "u0": 100,
                                   "freedrainage_top": True, "freedrainage_bottom": True}],
    "parameter_selection_constant_value": [{"data": [30, 32, 31, 29, 33, 30.5], "mode": "Low", "confidence": 0.95}],
    "parameter_selection_linear_trend": [{"data": [20, 28, 35, 44, 50, 61], "depths": [1, 2, 3, 4, 5, 6],
                                          "requested_depths": [1.5, 3.5, 5.5], "mode": "Low", "confidence": 0.95}],
    "eurocode7_factors": [{"design_approach": "DA1-1", "foundation_type": "Spread foundation"},
                          {"design_approach": "DA2", "foundation_type": "Spread foundation"}],
    "LogPlot": [{"soilprofile": "@layer_profile", "parameters": "Total unit weight [kN/m3]", "soiltypecolumn": "Soil type"}],
    "LogPlotMatplotlib": [{"soilprofile": "@layer_profile", "parameters": "Total unit weight [kN/m3]",
                           "soiltypecolumn": "Soil type"}],
    "plot_with_log": [{"soilprofile": "@layer_profile", "parameters": "Total unit weight [kN/m3]",
                       "soiltypecolumn": "Soil type"}],
    "map_depth_properties": [{"target_soilprofile": "@cpt_profile", "layering_soilprofile": "@layer_profile",
                              "target_z_key": "Depth to [m]", "layering_zfrom_key": "Depth from [m]",
                              "layering_zto_key": "Depth to [m]"}],
    "check_layer_overlap": [{"df": "@layer_profile", "raise_error": False, "z_from_key": "Depth from [m]",
                             "z_to_key": "Depth to [m]"}],
    "negativeskinfriction_pilegroup_zeevaertdebeer": [{"soilprofile": "@layer_profile",
                                                       "eff_unit_weight_col": "Submerged unit weight [kN/m3]",
                                                       "k_col": "K [-]", "delta_col": "Interface friction angle [deg]",
                                                       "surcharge": 10, "diameter": 0.5, "diameter_influence": 1.5}],
    "piletest_chinkondler": [{"soilprofile": "@piletest_table", "load_col": "Load [kN]", "settlement_col": "Settlement [mm]",
                              "no_discard_points": 1, "max_settlement": 50, "selected_settlement": 40}],
    "logtimemethod": [{"times": [0.1, 0.25, 0.5, 1, 2, 4, 8, 15, 30, 60, 120, 240, 480, 1440],
                       "settlements": [0.05, 0.08, 0.11, 0.15, 0.21, 0.29, 0.40, 0.52, 0.64, 0.72, 0.76, 0.78, 0.80, 0.82],
                       "drainagelength": 0.01}],
    "roottimemethod": [{"times": [0.1, 0.25, 0.5, 1, 2, 4, 8, 15, 30, 60, 120, 240, 480, 1440],
                        "settlements": [0.05, 0.08, 0.11, 0.15, 0.21, 0.29, 0.40, 0.52, 0.64, 0.72, 0.76, 0.78, 0.80, 0.82],
                        "drainagelength": 0.01}],
    "merge_two_dicts": [{"x": "{\"a\": 1}", "y": "{\"b\": 2}"}],
    "reverse_dict": [{"input_dict": "{\"a\": 1, \"b\": 2}"}],
    "hardening_soil_drained_triaxial": [{"friction_angle": 35, "cohesion": 0, "Rf": 0.9, "E50_ref": 30000,
                                         "Eur_ref": 90000, "Eoed_ref": 30000, "p_ref": 100, "sigma3": 100,
                                         "sigma1_0": 100, "m": 0.5, "N": 100}],
}


# The response depends on a random saved-object id (the validator reads the id as a number + unit when it starts
# with digits), so only the HTTP status is compared.
STATUS_ONLY = {"check_layer_overlap"}


def _first_choice(annotation):
    args = typing.get_args(annotation)
    if getattr(annotation, "__origin__", None) is typing.Literal:
        return args[0]
    for a in args:
        if getattr(a, "__origin__", None) is typing.Literal:
            return typing.get_args(a)[0]
    return None


def _bounds(field):
    lo = hi = None
    for m in field.metadata:
        lo = getattr(m, "ge", getattr(m, "gt", lo)) if lo is None else lo
        hi = getattr(m, "le", getattr(m, "lt", hi)) if hi is None else hi
    return lo, hi


def _value(name, field):
    from pydantic_core import PydanticUndefined
    if field.default is not PydanticUndefined and field.default is not None:
        return field.default, "default"
    choice = _first_choice(field.annotation)
    if choice is not None:
        return choice, "choice"
    unit = (field.json_schema_extra or {}).get("unit") if isinstance(field.json_schema_extra, dict) else None
    typical = TYPICAL_BY_NAME.get(name, TYPICAL_BY_UNIT.get(unit))
    lo, hi = _bounds(field)
    if typical is None:
        typical = 1.0
    if lo is not None and typical < lo:
        typical = lo + (abs(lo) * 0.5 if lo else 1.0)
    if hi is not None and typical > hi:
        typical = lo + 0.4 * (hi - lo) if lo is not None else hi * 0.5
    base = typing.get_args(field.annotation) or (field.annotation,)
    if int in base and float not in base:
        typical = int(round(typical))
    return typical, "typical"


_OPTIONS = re.compile(r"Options:\s*[(\[]([^)\]]*)[)\]]")
_PROFILE_PARAMS = {"soilprofile", "profile", "secondaryprofile", "soil_profile"}


def _doc_options(function_id):
    """{param: first documented option} from ':param x: ... - Options: ("A", "B")' lines of the docstring."""
    import inspect
    from core.registry import Registry
    fn = _REGISTRY.function_map.get(function_id) if _REGISTRY else None
    doc = inspect.getdoc(fn) if fn else ""
    out = {}
    for name, rest in re.findall(r"^:param\s+(\w+):(.*)$", doc or "", re.M):
        m = _OPTIONS.search(rest)
        if m:
            first = re.findall(r"[\"']([^\"']+)[\"']", m.group(1))
            if first:
                out[name] = first[0]
    return out


_REGISTRY = None
PYDANTIC_UNDEFINED = object()


def generated_args(function_id):
    from core.geoai.schemas import get_schema
    pair = get_schema(function_id)
    if not pair:
        return None
    options = _doc_options(function_id)
    args = {}
    for name, field in pair[0].model_fields.items():
        if name in ("latex_titles", "show_fig", "showfig", "fig"):
            continue
        if name in _PROFILE_PARAMS:
            args[name] = "@layer_profile"
            continue
        if name in options and field.default in (None,) + tuple([PYDANTIC_UNDEFINED]):
            args[name] = options[name]
            continue
        value, _ = _value(name, field)
        if isinstance(value, (int, float, str, bool)):
            args[name] = value
    return args


def build():
    os.environ.setdefault("GEOCORE_CONFIG_DIR", tempfile.mkdtemp(prefix="geocore-golden-build-"))
    import warnings
    warnings.filterwarnings("ignore")
    import main  # noqa: F401  (startup registers the schemas exactly as the app does)
    global _REGISTRY, PYDANTIC_UNDEFINED
    from core.registry import Registry
    from pydantic_core import PydanticUndefined as PYDANTIC_UNDEFINED
    _REGISTRY = Registry()
    from core.catalogue.sidebar import iter_sidebar_functions

    cases, skipped = [], []
    for fn in iter_sidebar_functions():
        fid = fn["id"]
        variants = CURATED.get(fid)
        if variants is None:
            args = generated_args(fid)
            if args is None:
                skipped.append(fid)
                continue
            variants = [args]
        for i, args in enumerate(variants):
            case = {"name": fid if i == 0 else f"{fid}#{i + 1}", "function": fid, "module": fn["module"],
                    "args": args, "source": "curated" if fid in CURATED else "generated"}
            if fid in STATUS_ONLY:
                case["compare"] = "status"
            cases.append(case)
    (HERE / "cases.json").write_text(json.dumps({
        "_comment": "Generated by `python tests/golden/build_cases.py`; curated requests live in CURATED there.",
        "skipped_no_schema": skipped, "cases": cases}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(cases)} cases, {len(skipped)} calculations without a schema: {skipped}")


if __name__ == "__main__":
    build()
