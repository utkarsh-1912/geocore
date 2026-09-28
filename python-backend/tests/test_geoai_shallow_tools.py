"""GeoAI shallow-foundation tools: Groundhog oracles, project provenance, errors, units, selector ranking.

Worked examples: Groundhog tutorial "Shallow foundation capacity with groundhog"
(website/_content/pages/groundhog/tutorials/tutorial-shallow-foundation-capacity-with-groundhog.md):
8 m x 5 m mudmat, undrained su = 10 kPa -> q_u = 5.14 x 10 x (1 + 0.18 x 5/8) = 57.18 kPa;
drained gamma' = 9 kN/m3, phi' = 38 deg, surface -> q_u ~ 0.5 x 9 x 5 x 56.17 x (1 - 0.4 x 5/8) = 947.9 kPa;
eccentric e_L = 1 m, e_B = 0.5 m -> A' = (8 - 2)(5 - 1) = 24 m2.
"""
import warnings

import pandas as pd
import pytest

import core.geoai.tool_definitions  # noqa: F401  (registers canonical tools incl. tools_shallow)
import core.geoai.project_soil as project_soil
from core.geoai.data_access import ProjectContext
from core.geoai.exceptions import GeoAIValidationError
from core.geoai.tool_registry import tool_registry
from core.geoai.tools_shallow import GeoAIMissingParameterError

CAP = "calculate_shallow_foundation_capacity"
SET = "calculate_foundation_settlement"


def run(tool, **args):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return tool_registry.invoke_tool(tool, args)


@pytest.fixture(autouse=True)
def no_project(monkeypatch):
    """Default: an empty project (tests never read the developer's saved workspace)."""
    monkeypatch.setattr(project_soil, "load_project_context", lambda: ProjectContext("empty"))


@pytest.fixture
def project(monkeypatch):
    ctx = ProjectContext("p1", "Test project")
    ctx.add_profile("BH-01", pd.DataFrame({
        "Depth from [m]": [0.0, 0.8, 2.5, 5.0],
        "Depth to [m]": [0.8, 2.5, 5.0, 10.0],
        "SoilType": ["Fill", "Medium dense sand", "Soft clay", "Stiff clay"],
        "UnitWeight [kN_m3]": [17.5, 18.5, 17.0, 18.8],
        "FrictionAngle [deg]": [28.0, 32.0, 0.0, 0.0],
        "Su [kPa]": [0.0, 0.0, 35.0, 75.0],
        "Cc [-]": [0.0, 0.0, 0.3, 0.15],
        "Cr [-]": [0.0, 0.0, 0.05, 0.03],
        "e0 [-]": [0.0, 0.0, 1.2, 0.8],
        "OCR [-]": [0.0, 0.0, 1.0, 2.0],
        "WaterTable [m]": [3.2, 3.2, 3.2, 3.2],
    }))
    monkeypatch.setattr(project_soil, "load_project_context", lambda: ctx)
    return ctx


def groundhog_drained(length, width, depth, gamma_eff, phi, p0, skirted=False, e_w=0.0, e_l=0.0, **kw):
    from groundhog.shallowfoundations.capacity import ShallowFoundationCapacityDrained
    c = ShallowFoundationCapacityDrained("oracle")
    c.set_geometry(length=length, width=width, depth=depth, skirted=skirted)
    c.set_soilparameters_drained(effective_unit_weight=gamma_eff, friction_angle=phi, effective_stress_base=p0)
    c.set_eccentricity(eccentricity_width=e_w, eccentricity_length=e_l)
    c.calculate_bearing_capacity(**kw)
    return c


def groundhog_undrained(length, width, depth, gamma, su, skirted=False, e_w=0.0, e_l=0.0, **kw):
    from groundhog.shallowfoundations.capacity import ShallowFoundationCapacityUndrained
    c = ShallowFoundationCapacityUndrained("oracle")
    c.set_geometry(length=length, width=width, depth=depth, skirted=skirted)
    c.set_soilparameters_undrained(unit_weight=gamma, su_base=su)
    c.set_eccentricity(eccentricity_width=e_w, eccentricity_length=e_l)
    c.calculate_bearing_capacity(**kw)
    return c


# ---------------------------------------------------------------- worked examples (Groundhog tutorial)
def test_tutorial_undrained_mudmat():
    r = run(CAP, foundation_shape="rectangular", width_m=5, length_m=8, foundation_depth_m=0,
            undrained_shear_strength_kpa=10)
    assert r["analysis"] == "undrained"
    assert r["q_ult_kpa"] == pytest.approx(5.14 * 10 * (1 + 0.18 * 5 / 8), rel=1e-4)
    assert r["Q_ult_kn"] == pytest.approx(r["q_ult_kpa"] * 40, rel=1e-4)


def test_tutorial_drained_mudmat():
    # gamma' = 19 - 10 = 9 kN/m3 with the water table at the surface.
    r = run(CAP, foundation_shape="rectangular", width_m=5, length_m=8, foundation_depth_m=0,
            friction_angle_deg=38, unit_weight_kn_m3=19, groundwater_depth_m=0)
    assert r["q_ult_kpa"] == pytest.approx(0.5 * 9 * 5 * 56.17 * (1 - 0.4 * 5 / 8), rel=2e-3)
    assert r["q_ult_kpa"] == pytest.approx(groundhog_drained(8, 5, 0, 9, 38, 0).net_bearing_pressure, rel=1e-4)


def test_tutorial_eccentric_effective_area():
    r = run(CAP, foundation_shape="rectangular", width_m=5, length_m=8, foundation_depth_m=0,
            undrained_shear_strength_kpa=10, eccentricity_b_m=0.5, eccentricity_l_m=1.0)
    assert r["effective_area_m2"] == pytest.approx(24.0)
    oracle = groundhog_undrained(8, 5, 0, 16, 10, e_w=0.5, e_l=1.0)
    assert r["Q_ult_kn"] == pytest.approx(oracle.ultimate_capacity, rel=1e-4)


# ---------------------------------------------------------------- direct Groundhog oracles
def test_drained_embedded_matches_groundhog_class():
    # 2 m square pad at 1.5 m, gamma 18, water table deep (>= B below base) -> p0' = 27 kPa, gamma = 18 in N_gamma.
    r = run(CAP, foundation_shape="square", width_m=2, foundation_depth_m=1.5, friction_angle_deg=32,
            unit_weight_kn_m3=18, groundwater_depth_m=10)
    oracle = groundhog_drained(2, 2, 1.5, 18, 32, 27.0, effective_unit_weight__max=20)
    assert r["stresses"]["p0_eff_base_kpa"] == pytest.approx(27.0)
    assert r["q_ult_kpa"] == pytest.approx(oracle.net_bearing_pressure, rel=1e-4)
    assert r["Q_ult_kn"] == pytest.approx(oracle.ultimate_capacity, rel=1e-4)
    assert r["factors"]["N_q"] == pytest.approx(oracle.capacity["N_q [-]"], rel=1e-3)
    assert r["bearing_pressure_basis"].startswith("gross")


def test_undrained_embedded_matches_groundhog_class():
    r = run(CAP, foundation_shape="rectangular", width_m=2, length_m=3, foundation_depth_m=1.0,
            undrained_shear_strength_kpa=40, unit_weight_kn_m3=18)
    oracle = groundhog_undrained(3, 2, 1.0, 18, 40)
    assert r["q_ult_kpa"] == pytest.approx(oracle.net_bearing_pressure, rel=1e-4)
    assert r["Q_ult_kn"] == pytest.approx(oracle.ultimate_capacity, rel=1e-4)
    assert r["factors"]["d_c"] > 0


def test_inclined_load_drained_uses_groundhog_load_inclination():
    r = run(CAP, foundation_shape="square", width_m=2, foundation_depth_m=0, friction_angle_deg=35,
            unit_weight_kn_m3=19, groundwater_depth_m=0, vertical_load_kn=500, horizontal_load_kn=50)
    import math
    theta = math.degrees(math.atan(50 / 500))
    oracle = groundhog_drained(2, 2, 0, 9, 35, 0, load_inclination=theta)
    assert r["factors"]["load_inclination_deg"] == pytest.approx(theta, rel=1e-3)
    assert r["q_ult_kpa"] == pytest.approx(oracle.net_bearing_pressure, rel=1e-4)


def test_moment_gives_effective_area():
    r = run(CAP, foundation_shape="square", width_m=2, foundation_depth_m=1, undrained_shear_strength_kpa=50,
            unit_weight_kn_m3=18, vertical_load_kn=500, moment_b_knm=100)
    assert r["footing"]["e_B_m"] == pytest.approx(0.2)
    assert r["footing"]["effective_width_m"] == pytest.approx(1.6)
    assert r["effective_area_m2"] == pytest.approx(3.2)


def test_moment_without_vertical_load_is_missing_parameter():
    with pytest.raises(GeoAIMissingParameterError) as exc:
        run(CAP, foundation_shape="square", width_m=2, foundation_depth_m=1, undrained_shear_strength_kpa=50,
            unit_weight_kn_m3=18, moment_b_knm=100)
    assert "vertical_load_kn" in str(exc.value)


def test_eccentricity_beyond_edge_rejected():
    with pytest.raises(GeoAIValidationError):
        run(CAP, foundation_shape="square", width_m=2, foundation_depth_m=0, undrained_shear_strength_kpa=50,
            eccentricity_b_m=1.0)


@pytest.mark.parametrize("shape,extra", [("strip", {}), ("circular", {}), ("rectangular", {"length_m": 4})])
def test_shapes_return_finite_capacity(shape, extra):
    r = run(CAP, foundation_shape=shape, width_m=2, foundation_depth_m=1, undrained_shear_strength_kpa=50,
            unit_weight_kn_m3=18, **extra)
    assert r["q_ult_kpa"] > 0
    if shape == "strip":
        assert r["Q_ult_kn_per_m"] > 0 and r["Q_ult_kn"] is None
        assert r["factors"]["s_c"] < 1e-3          # B/L -> 0
    else:
        assert r["Q_ult_kn"] > 0


def test_groundwater_reduces_drained_capacity():
    dry = run(CAP, foundation_shape="square", width_m=2, foundation_depth_m=1.5, friction_angle_deg=32,
              unit_weight_kn_m3=19, groundwater_depth_m=20)
    wet = run(CAP, foundation_shape="square", width_m=2, foundation_depth_m=1.5, friction_angle_deg=32,
              unit_weight_kn_m3=19, groundwater_depth_m=0)
    assert wet["stresses"]["p0_eff_base_kpa"] == pytest.approx(1.5 * 9)
    assert wet["q_ult_kpa"] < 0.6 * dry["q_ult_kpa"]


def test_cohesion_reported_not_silently_used():
    r = run(CAP, foundation_shape="square", width_m=2, foundation_depth_m=0, friction_angle_deg=30,
            effective_cohesion_kpa=10, unit_weight_kn_m3=19, groundwater_depth_m=5)
    assert any("NOT included" in w for w in r["warnings"])


# ---------------------------------------------------------------- missing parameters (never invented)
def test_missing_parameters_named_with_units():
    with pytest.raises(GeoAIMissingParameterError) as exc:
        run(CAP, foundation_shape="square", width_m=2, foundation_depth_m=1.5, analysis="drained")
    fields = {e["field"]: e["unit"] for e in exc.value.errors}
    assert fields == {"friction_angle_deg": "deg", "unit_weight_kn_m3": "kN/m3", "groundwater_depth_m": "m"}
    assert all(e["type"] == "missing_parameter" for e in exc.value.errors)
    assert "no soil profile" in exc.value.errors[0]["project_lookup"]


def test_analysis_ambiguous_asks():
    with pytest.raises(GeoAIMissingParameterError) as exc:
        run(CAP, foundation_shape="square", width_m=2, foundation_depth_m=1)
    assert exc.value.errors[0]["field"] == "analysis"


def test_rectangular_needs_length():
    with pytest.raises(GeoAIMissingParameterError):
        run(CAP, foundation_shape="rectangular", width_m=2, foundation_depth_m=1, undrained_shear_strength_kpa=50)


def test_settlement_missing_parameters():
    with pytest.raises(GeoAIMissingParameterError) as exc:
        run(SET, foundation_shape="square", width_m=2, foundation_depth_m=1.5, applied_pressure_kpa=150,
            clay_top_depth_m=3, clay_bottom_depth_m=8)
    fields = {e["field"] for e in exc.value.errors}
    assert {"compression_index", "initial_void_ratio", "ocr", "recompression_index"} <= fields


# ---------------------------------------------------------------- project context with provenance
def test_project_parameters_carry_provenance(project):
    r = run(CAP, foundation_shape="square", width_m=2, foundation_depth_m=3.0, analysis="undrained")
    su = r["soil_parameters"]["undrained_shear_strength_kpa"]
    # influence zone 3-6 m: soft clay 2 m (35 kPa) + stiff clay 1 m (75 kPa)
    assert su["value"] == pytest.approx((35 * 2 + 75 * 1) / 3, rel=1e-4)
    assert "BH-01" in su["source"] and "Soft clay" in su["source"] and "Stiff clay" in su["source"]
    assert r["soil_parameters"]["unit_weight_above_base_kn_m3"]["source"].startswith("project profile")


def test_project_friction_angle_not_available_over_clay(project):
    with pytest.raises(GeoAIMissingParameterError) as exc:
        run(CAP, foundation_shape="square", width_m=2, foundation_depth_m=1.5, analysis="drained")
    err = {e["field"]: e for e in exc.value.errors}
    assert "friction_angle_deg" in err and "Soft clay" in err["friction_angle_deg"]["project_lookup"]


def test_user_value_overrides_project_and_groundwater_from_project(project):
    r = run(CAP, foundation_shape="square", width_m=1, foundation_depth_m=0.8, friction_angle_deg=33,
            analysis="drained")
    sp = r["soil_parameters"]
    assert sp["friction_angle_deg"]["source"] == "user input"
    assert sp["groundwater_depth_m"]["value"] == pytest.approx(3.2)
    assert "WaterTable" in sp["groundwater_depth_m"]["source"]
    assert sp["unit_weight_below_base_kn_m3"]["source"].startswith("project profile")


def test_settlement_layers_from_project(project):
    r = run(SET, foundation_shape="square", width_m=2, foundation_depth_m=1.5, applied_pressure_kpa=150)
    labels = [l["layer"] for l in r["compressible_layers"]]
    assert len(labels) == 2 and "Soft clay" in labels[0] and "Stiff clay" in labels[1]
    assert r["settlement_mm"] > 0
    assert sum(l["settlement_mm"] for l in r["compressible_layers"]) == pytest.approx(r["settlement_mm"], rel=1e-3)
    assert "BH-01" in r["soil_parameters"]["compression_index (" + labels[0] + ")"]["source"]


# ---------------------------------------------------------------- units
def test_unit_conversion_mm_and_mpa():
    a = run(CAP, foundation_shape="square", width_m="2000 mm", foundation_depth_m=1.0,
            undrained_shear_strength_kpa="0.05 MPa", unit_weight_kn_m3=18)
    b = run(CAP, foundation_shape="square", width_m=2, foundation_depth_m=1.0,
            undrained_shear_strength_kpa=50, unit_weight_kn_m3=18)
    assert a["q_ult_kpa"] == pytest.approx(b["q_ult_kpa"])


def test_wrong_unit_dimension_rejected():
    with pytest.raises(GeoAIValidationError):
        run(CAP, foundation_shape="square", width_m=2, foundation_depth_m=1.0,
            undrained_shear_strength_kpa=50, unit_weight_kn_m3="18 kPa")


# ---------------------------------------------------------------- settlement oracle vs Groundhog SettlementCalculation
@pytest.mark.parametrize("shape,gh_shape", [("square", "rectangular"), ("circular", "circular"), ("strip", "strip")])
def test_settlement_matches_groundhog_settlementcalculation(shape, gh_shape):
    from groundhog.general.soilprofile import SoilProfile
    from groundhog.shallowfoundations.settlement import SettlementCalculation
    from groundhog.siteinvestigation.classification.phaserelations import voidratio_bulkunitweight
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sp = SoilProfile({"Depth from [m]": [0.0], "Depth to [m]": [6.0], "Soil type": ["CLAY"],
                          "Total unit weight [kN/m3]": [17.0], "Cc [-]": [0.3], "Cr [-]": [0.05], "OCR [-]": [1.0]})
        calc = SettlementCalculation(sp)
        calc.calculate_initial_state(waterlevel=0)
        calc.set_foundation(width=2.0, shape=gh_shape, length=2.0 if gh_shape == "rectangular" else float("nan"))
        calc.create_grid(dz=0.5)
        calc.calculate_foundation_stress(applied_stress=100.0)
        calc.calculate()
    e0 = voidratio_bulkunitweight(bulkunitweight=17.0, saturation=1)["e [-]"]
    r = run(SET, foundation_shape=shape, width_m=2, foundation_depth_m=0, applied_pressure_kpa=100,
            clay_top_depth_m=0, clay_bottom_depth_m=6, compression_index=0.3, initial_void_ratio=e0, ocr=1,
            unit_weight_kn_m3=17, groundwater_depth_m=0)
    assert r["discretisation"]["n_sublayers"] == len(calc.grid.elements) == 12
    assert r["settlement_mm"] == pytest.approx(calc.settlement * 1000.0, rel=1e-3)


def test_settlement_mv_matches_groundhog_functions():
    from groundhog.shallowfoundations.settlement import consolidationsettlement_mv
    from groundhog.shallowfoundations.stressdistribution import stresses_rectangle
    r = run(SET, foundation_shape="square", width_m=2, foundation_depth_m=0, applied_pressure_kpa=100,
            clay_top_depth_m=0, clay_bottom_depth_m=2, mv_per_kpa=0.0005, sublayer_thickness_m=1.0)
    expected = 0.0
    for zc in (0.5, 1.5):
        dsig = 4 * stresses_rectangle(imposedstress=100, length=1.0, width=1.0, z=zc)["delta sigma z [kPa]"]
        expected += consolidationsettlement_mv(initial_height=1.0, effective_stress_increase=dsig,
                                               compressibility=0.0005)["delta z [m]"]
    assert r["settlement_mm"] == pytest.approx(expected * 1000.0, rel=1e-3)
    assert "unit_weight_kn_m3" not in r["soil_parameters"]   # mv surface footing needs no stresses


def test_net_pressure_and_oc_branch():
    common = dict(foundation_shape="square", width_m=2, foundation_depth_m=1.5, applied_pressure_kpa=150,
                  clay_top_depth_m=3, clay_bottom_depth_m=9, compression_index=0.3, recompression_index=0.05,
                  initial_void_ratio=1.1, unit_weight_kn_m3=18, groundwater_depth_m=2)
    nc = run(SET, ocr=1, **common)
    oc = run(SET, ocr=3, **common)
    assert nc["net_pressure_kpa"] == pytest.approx(150 - 18 * 1.5)
    assert oc["settlement_mm"] < nc["settlement_mm"]


def test_settlement_breakdown_is_compact():
    r = run(SET, foundation_shape="square", width_m=2, foundation_depth_m=0, applied_pressure_kpa=100,
            clay_top_depth_m=0, clay_bottom_depth_m=20, mv_per_kpa=0.0003, sublayer_thickness_m=0.25)
    assert r["discretisation"]["n_sublayers"] == 80
    assert len(r["breakdown"]) <= 15
    assert sum(row["settlement_mm"] for row in r["breakdown"]) == pytest.approx(r["settlement_mm"], rel=1e-3)


# ---------------------------------------------------------------- wording, registry, exposure, selector
def test_results_state_scope_without_safety_claim():
    r = run(CAP, foundation_shape="square", width_m=2, foundation_depth_m=0, undrained_shear_strength_kpa=50)
    assert "factors of safety" in r["note"] and "Ultimate" in r["note"]
    text = (r["note"] + " ".join(r["assumptions"])).lower()
    assert " is safe" not in text and "design is adequate" not in text


def test_tools_registered_and_raw_classes_hidden():
    from core.geoai.exposure_policy import is_model_exposed
    names = {t["name"] for t in tool_registry.list_tools()}
    assert {CAP, SET} <= names
    for cls in ("ShallowFoundationCapacity", "ShallowFoundationCapacityDrained",
                "ShallowFoundationCapacityUndrained", "SettlementCalculation", "ConsolidationCalculation"):
        assert not is_model_exposed(cls) and cls not in names


def test_tool_metadata_used_in_provenance():
    r = run(CAP, foundation_shape="square", width_m=2, foundation_depth_m=0, undrained_shear_strength_kpa=50)
    assert "API RP 2GEO" in r["_provenance"]["method"]
    assert r["_provenance"]["output_units"]["q_ult_kpa"] == "kPa"


@pytest.mark.parametrize("query,expected", [
    ("bearing capacity of a 2 m square pad on sand phi 32", CAP),
    ("what's the bearing capacity of a 2 m square footing at 1.5 m in the current project", CAP),
    ("ultimate capacity of a strip footing on clay with su 40 kPa", CAP),
    ("what load can a 1.5 x 3 m pad carry at 1 m depth in the current project?", CAP),
    ("how much will this footing settle on soft clay", SET),
    ("how much will it settle", SET),
    ("consolidation settlement of a 3 m wide footing, Cc 0.3, e0 1.1", SET),
    ("footing settlement under 150 kPa", SET),
])
def test_selector_ranks_new_tools_top3(query, expected):
    from core.geoai.tool_selector import select_relevant_tools
    names = [t["function"]["name"] for t in select_relevant_tools(query, max_tools=5)]
    assert expected in names[:3], names
