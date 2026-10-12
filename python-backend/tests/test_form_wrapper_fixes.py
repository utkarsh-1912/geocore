# Author: Utkarsh Gupta
# License: GPL v3
"""
Form calculations that failed before every result (found by the golden /api/execute run):

* settlement_calculation: `if not profile` on a SoilProfile (a DataFrame), then the grid built before the initial
  state and a plot that called show() and returned nothing.
* map_depth_properties, check_layer_overlap, negativeskinfriction_pilegroup_zeevaertdebeer, piletest_chinkondler:
  rejected by the schema generated from the Groundhog signature before their wrappers ran (the forms send a saved
  SoilProfile id and column names); the last two also only read JSON rows, not a saved profile.
* logtimemethod / roottimemethod: the drainage length was lost when mapping the form fields.

The saved objects are an in-memory stand-in for the workspace (never the user's data). Expected numbers come from
the Groundhog functions called directly.
"""
import math

import pandas as pd
import pytest
from groundhog.general.soilprofile import SoilProfile

from core.registry import registry

LAYERS = [
    {"Depth from [m]": 0.0, "Depth to [m]": 3.0, "Soil type": "Sand", "Total unit weight [kN/m3]": 18.0,
     "Submerged unit weight [kN/m3]": 9.0, "Cc [-]": 0.1, "Cr [-]": 0.02, "OCR [-]": 1.0, "K [-]": 0.4,
     "Interface friction angle [deg]": 24.0},
    {"Depth from [m]": 3.0, "Depth to [m]": 8.0, "Soil type": "Clay", "Total unit weight [kN/m3]": 17.0,
     "Submerged unit weight [kN/m3]": 7.0, "Cc [-]": 0.3, "Cr [-]": 0.05, "OCR [-]": 1.0, "K [-]": 0.5,
     "Interface friction angle [deg]": 15.0},
]
PILE_TEST = [{"Depth from [m]": float(i), "Depth to [m]": float(i + 1), "Load [kN]": f, "Settlement [mm]": w}
             for i, (f, w) in enumerate(zip([0, 200, 400, 600, 800, 1000, 1200, 1400, 1600],
                                            [0.0, 1.1, 2.5, 4.3, 6.8, 10.2, 15.0, 22.0, 32.0]))]
TIMES = [0.1, 0.25, 0.5, 1, 2, 4, 8, 15, 30, 60, 120, 240, 480, 1440]
SETTLEMENTS = [0.05, 0.08, 0.11, 0.15, 0.21, 0.29, 0.4, 0.52, 0.64, 0.72, 0.76, 0.78, 0.8, 0.82]


@pytest.fixture
def saved(monkeypatch):
    import core.state as state
    objects = {"layers": SoilProfile(pd.DataFrame(LAYERS)), "piletest": SoilProfile(pd.DataFrame(PILE_TEST)),
               "target": SoilProfile(pd.DataFrame([{"Depth from [m]": z, "Depth to [m]": z + 0.5}
                                                   for z in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5)]))}
    monkeypatch.setattr(state.state_manager, "get", lambda oid: objects.get(oid))
    return objects


def _run(function_id, args):
    return registry.execute_function("test", function_id, args)


def test_settlement_calculation_runs_and_matches_groundhog(saved):
    from groundhog.shallowfoundations.settlement import SettlementCalculation
    out = _run("settlement_calculation", {"soilprofile": "layers", "foundation_width": 2, "foundation_shape": "strip",
                                          "foundation_length": 0, "skirt_depth": 0, "applied_stress": 100,
                                          "water_level": 1})
    assert "error" not in out and out["type"] == "plotly" and out["data"]
    calc = SettlementCalculation(SoilProfile(pd.DataFrame(LAYERS)))
    calc.set_foundation(width=2, shape="strip", length=0)
    calc.calculate_initial_state(waterlevel=1)
    calc.create_grid()
    calc.calculate_foundation_stress(applied_stress=100)
    calc.calculate()
    assert out["settlement [m]"] == pytest.approx(float(calc.settlement)) and 0 < out["settlement [m]"] < 1


def test_settlement_undefined_is_an_error_not_nan(saved):
    saved["layers"] = SoilProfile(pd.DataFrame([{**r, "Cc [-]": 0.0} for r in LAYERS]))
    out = _run("settlement_calculation", {"soilprofile": "layers", "foundation_width": 2, "applied_stress": 100,
                                          "water_level": 1})
    assert "Settlement undefined" in out["error"] and "Cc >= 0.1" in out["error"]
    assert "not found" in _run("settlement_calculation", {"soilprofile": "missing"})["error"]


def test_negative_skin_friction_from_a_saved_layered_profile(saved):
    from groundhog.deepfoundations.axialcapacity.negativeskinfriction import negativeskinfriction_pilegroup_zeevaertdebeer
    from core.wrappers import _nsf_points
    out = _run("negativeskinfriction_pilegroup_zeevaertdebeer", {
        "soilprofile": "layers", "eff_unit_weight_col": "Submerged unit weight [kN/m3]", "k_col": "K [-]",
        "delta_col": "Interface friction angle [deg]", "surcharge": 10, "diameter": 0.5, "diameter_influence": 1.5})
    assert "error" not in out and out["type"] == "plotly"
    depths, (gamma, k, delta) = _nsf_points(LAYERS, ["Submerged unit weight [kN/m3]", "K [-]",
                                                     "Interface friction angle [deg]"])
    assert depths[0] == 0.0 and depths[-1] == 8.0 and depths == sorted(set(depths))
    assert gamma[depths.index(3.0)] == 7.0 and gamma[depths.index(3.0) - 1] == 9.0  # a boundary takes the layer below
    direct = negativeskinfriction_pilegroup_zeevaertdebeer(depths=depths, effective_unit_weights=gamma,
                                                         lateral_earth_pressure_coefficients=k,
                                                         interface_friction_angles=delta, surcharge=10,
                                                         diameter=0.5, diameter_influence=1.5)
    assert out["raw_data"]["negative_skin_friction [kN]"] == pytest.approx(float(direct["negative_skin_friction [kN]"]))
    missing = _run("negativeskinfriction_pilegroup_zeevaertdebeer", {"soilprofile": "layers", "k_col": "nope"})
    assert "nope" in missing["error"]


def test_pile_test_chin_kondler_from_a_saved_table(saved):
    from groundhog.deepfoundations.axialcapacity.piletesting import piletest_chinkondler
    out = _run("piletest_chinkondler", {"soilprofile": "piletest", "load_col": "Load [kN]",
                                        "settlement_col": "Settlement [mm]", "no_discard_points": 1,
                                        "max_settlement": 50, "selected_settlement": 40})
    assert "error" not in out and out["type"] == "plotly"
    direct = piletest_chinkondler(loads=[r["Load [kN]"] for r in PILE_TEST],
                                  settlements=[r["Settlement [mm]"] for r in PILE_TEST], no_discard_points=1,
                                  max_settlement=50, selected_settlement=40, show_fig=False)
    assert out["raw_data"]["slope [1/kN]"] == pytest.approx(float(direct["slope [1/kN]"]))


def test_map_depth_properties_and_layer_overlap_reach_their_wrappers(saved):
    out = _run("map_depth_properties", {"target_soilprofile": "target", "layering_soilprofile": "layers",
                                        "target_z_key": "Depth to [m]", "layering_zfrom_key": "Depth from [m]",
                                        "layering_zto_key": "Depth to [m]"})
    assert out["type"] == "dataframe" and [r["Soil type"] for r in out["data"]] == ["Sand"] * 5 + ["Clay"] * 3
    too_deep = SoilProfile(pd.DataFrame([{"Depth from [m]": 0.0, "Depth to [m]": 20.0}]))
    saved["target"] = too_deep
    assert "Map depth properties" in _run("map_depth_properties", {"target_soilprofile": "target",
                                                                   "layering_soilprofile": "layers",
                                                                   "target_z_key": "Depth to [m]"})["error"]
    overlap = _run("check_layer_overlap", {"df": "layers", "raise_error": False, "z_from_key": "Depth from [m]",
                                           "z_to_key": "Depth to [m]"})
    assert overlap["gaps_or_overlaps"] == 0 and overlap["layers_checked"] == 2


@pytest.mark.parametrize("function_id", ["logtimemethod", "roottimemethod"])
def test_consolidation_curve_fitting_keeps_the_drainage_length(function_id):
    plot = _run(function_id, {"times": TIMES, "settlements": SETTLEMENTS, "drainagelength": 0.01})
    assert plot.get("interactive_required") is True  # the first step asks the user to pick points
    text = _run(function_id, {"times": ",".join(map(str, TIMES)), "settlements": ",".join(map(str, SETTLEMENTS)),
                              "drainagelength": 0.01})
    assert text.get("interactive_required") is True  # comma-separated series from the form are parsed


def test_log_time_method_result_uses_the_drainage_length():
    args = {"times": TIMES, "settlements": SETTLEMENTS, "xy_primary": [[0.5, 0.18], [1.5, 0.6]],
            "xy_secondary": [[2.5, 0.78], [3.1, 0.82]], "pointB": [[-0.6, 0.08]]}
    a = _run("logtimemethod", {**args, "drainagelength": 0.01})
    b = _run("logtimemethod", {**args, "drainagelength": 0.02})
    # cv = 0.197 H^2 / t50: doubling the drainage length quadruples cv at the same t50
    assert a["t50 [s]"] == pytest.approx(b["t50 [s]"]) and math.isfinite(a["cv [m2/s]"])
    assert b["cv [m2/s]"] == pytest.approx(4 * a["cv [m2/s]"])


def test_settlement_names_what_the_profile_lacks(saved):
    # A real-world profile: unit weight spelt 'UnitWeight [kN_m3]', soil type 'SoilType', no compressibility.
    saved["field"] = SoilProfile(pd.DataFrame([
        {"Depth from [m]": 0.0, "Depth to [m]": 3.0, "SoilType": "Clayey Sand", "UnitWeight [kN_m3]": 18.5, "SPT [N]": 12},
        {"Depth from [m]": 3.0, "Depth to [m]": 8.0, "SoilType": "Soft Clay", "UnitWeight [kN_m3]": 17.0, "SPT [N]": 6},
    ]))
    before = list(saved["field"].columns)
    out = _run("settlement_calculation", {"soilprofile": "field", "foundation_width": 2, "applied_stress": 100,
                                          "water_level": 1})
    msg = out["error"]
    assert "cannot be used for a settlement calculation" in msg and "'mv [1/kPa]'" in msg and "'OCR [-]'" in msg
    assert "unit weight" not in msg.split("It needs")[1].split("Columns")[0]      # UnitWeight [kN_m3] was recognised
    assert "Soil type" not in msg.split("It needs")[1].split("Columns")[0]        # SoilType was recognised
    assert "Columns in the profile: Depth from [m], Depth to [m], SoilType" in msg and "does not assume" in msg
    assert list(saved["field"].columns) == before


def test_settlement_reports_a_partial_compressibility_set(saved):
    saved["partial"] = SoilProfile(pd.DataFrame([{**r, "OCR [-]": None} for r in LAYERS[:1]] + [dict(r) for r in LAYERS[1:]]))
    msg = _run("settlement_calculation", {"soilprofile": "partial", "foundation_width": 2, "applied_stress": 100,
                                          "water_level": 1})["error"]
    assert "it has Cc [-], Cr [-], OCR [-] but not OCR [-] in every layer" in msg


def test_settlement_accepts_common_spellings_and_leaves_the_saved_profile_alone(saved):
    from groundhog.shallowfoundations.settlement import SettlementCalculation
    renamed = [{"Depth from [m]": r["Depth from [m]"], "Depth to [m]": r["Depth to [m]"], "SoilType": r["Soil type"],
                "Unit weight [kN/m3]": r["Total unit weight [kN/m3]"], "Compression index": r["Cc [-]"],
                "Cr": r["Cr [-]"], "OCR": r["OCR [-]"]} for r in LAYERS]
    saved["spelt"] = SoilProfile(pd.DataFrame(renamed))
    before = list(saved["spelt"].columns)
    out = _run("settlement_calculation", {"soilprofile": "spelt", "foundation_width": 2, "foundation_shape": "strip",
                                          "foundation_length": 0, "applied_stress": 100, "water_level": 1})
    calc = SettlementCalculation(SoilProfile(pd.DataFrame(LAYERS)))
    calc.set_foundation(width=2, shape="strip", length=0)
    calc.calculate_initial_state(waterlevel=1)
    calc.create_grid()
    calc.calculate_foundation_stress(applied_stress=100)
    calc.calculate()
    assert out["settlement [m]"] == pytest.approx(float(calc.settlement))
    assert list(saved["spelt"].columns) == before  # no columns added to the saved profile
    # A unit weight with the wrong unit is not taken as one.
    saved["wrong"] = SoilProfile(pd.DataFrame([{**r, "Unit weight [kN/m3]": None, "Unit weight [kPa]": 18.0}
                                               for r in renamed]).drop(columns=["Unit weight [kN/m3]"]))
    assert "'Total unit weight [kN/m3]'" in _run("settlement_calculation", {"soilprofile": "wrong", "foundation_width": 2,
                                                                            "applied_stress": 100})["error"]
