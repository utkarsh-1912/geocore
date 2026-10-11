# Author: Utkarsh Gupta
# License: GPL v3
"""
Running catalogue calculations by id and comparing their methods on the same inputs (core/catalogue/run.py and
POST /api/calculations/{id}/run|compare). Runs go through registry.execute_function, so the numbers are the
forms' numbers; expected values are closed forms or the Groundhog function called directly.
"""
import pytest
from fastapi.testclient import TestClient

from core.catalogue.run import CatalogueRunError, compare_methods, run_method


def test_run_default_method_returns_values_and_raw():
    r = run_method("earthpressurecoefficients_rankine", None, {"phi_eff": 30, "wall_angle": 0, "top_angle": 0})
    assert r["error"] is None and r["status"] == "verified" and "KaR [-]" in r["raw"]
    ka = next(v for v in r["values"] if v["key"] == "KaR [-]")
    assert ka["value"] == pytest.approx(1 / 3)


def test_run_reports_a_validation_failure_as_the_method_error():
    r = run_method("earthpressurecoefficients_rankine", None, {"wall_angle": 0})
    assert r["error"] and "phi_eff" in r["error"] and r["values"] == []


def test_unknown_calculation_or_method():
    with pytest.raises(CatalogueRunError):
        run_method("no_such_calculation", None, {})
    with pytest.raises(CatalogueRunError):
        run_method("pile_unit_shaft_friction", "no_such_method", {})


def test_compare_runs_every_method_on_the_same_inputs():
    from groundhog.deepfoundations.axialcapacity.skinfriction import API_unit_shaft_friction_clay
    inputs = {"undrained_shear_strength": 50, "sigma_vo_eff": 80, "depth": 10, "embedded_length": 20,
              "qt": 1.5, "fs": 0.03}
    c = compare_methods("pile_unit_shaft_friction", inputs)
    by_id = {m["method"]: m for m in c["methods"]}
    assert len(by_id) == 4
    assert by_id["API_unit_shaft_friction_clay"]["error"] is None
    assert by_id["unitskinfriction_clay_almhamre"]["error"] is None
    # The sand methods need inputs the clay ones do not: each says what it is missing, the others still run.
    assert "api_relativedensity" in by_id["API_unit_shaft_friction_sand_rp2geo"]["error"]
    assert "interface_friction_angle" in by_id["unitskinfriction_sand_almhamre"]["error"]
    expected = API_unit_shaft_friction_clay(undrained_shear_strength=50, sigma_vo_eff=80)["f_s_comp_out [kPa]"]
    row = next(r for r in c["rows"] if "API_unit_shaft_friction_clay" in r["values"]
               and r["values"]["API_unit_shaft_friction_clay"] == pytest.approx(expected))
    assert "unitskinfriction_clay_almhamre" in row["values"]  # both methods on one row


def test_compare_takes_each_methods_own_inputs():
    from groundhog.deepfoundations.axialcapacity.skinfriction import API_unit_shaft_friction_clay
    c = compare_methods("pile_unit_shaft_friction", {"sigma_vo_eff": 80},
                        ["API_unit_shaft_friction_clay", "unitskinfriction_clay_almhamre"],
                        {"API_unit_shaft_friction_clay": {"undrained_shear_strength": 50},
                         "unitskinfriction_clay_almhamre": {"sigma_vo_eff": 120, "depth": 10, "embedded_length": 20,
                                                            "qt": 1.5, "fs": 0.03}})
    by_id = {m["method"]: m for m in c["methods"]}
    assert by_id["API_unit_shaft_friction_clay"]["error"] is None
    assert by_id["unitskinfriction_clay_almhamre"]["error"] is None
    expected = API_unit_shaft_friction_clay(undrained_shear_strength=50, sigma_vo_eff=80)["f_s_comp_out [kPa]"]
    assert any(r["values"].get("API_unit_shaft_friction_clay") == pytest.approx(expected) for r in c["rows"])
    # A method's own value wins over the shared one, and does not leak into the other method.
    other = compare_methods("pile_unit_shaft_friction", {"sigma_vo_eff": 80}, ["API_unit_shaft_friction_clay"],
                            {"API_unit_shaft_friction_clay": {"undrained_shear_strength": 50, "sigma_vo_eff": 120}})
    assert not any(r["values"].get("API_unit_shaft_friction_clay") == pytest.approx(expected) for r in other["rows"]
                   if r["label"].lower().startswith("f"))


def test_endpoints():
    from main import app
    client = TestClient(app)
    r = client.post("/api/calculations/earthpressurecoefficients_rankine/run",
                    json={"inputs": {"phi_eff": 30, "wall_angle": 0, "top_angle": 0}})
    assert r.status_code == 200 and r.json()["error"] is None
    c = client.post("/api/calculations/pile_unit_shaft_friction/compare",
                    json={"inputs": {"undrained_shear_strength": 50, "sigma_vo_eff": 80},
                          "methods": ["API_unit_shaft_friction_clay"]})
    assert c.status_code == 200 and [m["method"] for m in c.json()["methods"]] == ["API_unit_shaft_friction_clay"]
    assert client.post("/api/calculations/nope/run", json={}).status_code == 404
    # The phase-relations routes are unaffected by the generic ones.
    assert client.get("/api/calculations/phase_relations").status_code == 200


def test_auto_method_follows_the_saved_data():
    from core.catalogue.suggest import suggest_method
    cpt = suggest_method("pile_axial_capacity", available={"cpt"})
    assert cpt["method"] in ("LCPC_Calculation", "KoppejanCalculation", "DeBeerCalculation")
    assert "CPT" in cpt["reason"] and set(cpt["fits"]) == {"LCPC_Calculation", "KoppejanCalculation", "DeBeerCalculation"}
    profile = suggest_method("pile_axial_capacity", available={"soil_profile"})
    assert profile["method"] == "AxCapCalculation" and "soil profile" in profile["reason"]
    nothing = suggest_method("pile_axial_capacity", available=set())
    assert nothing["method"] == "AxCapCalculation" and nothing["reason"].startswith("default method; no ")
    with pytest.raises(KeyError):
        suggest_method("no_such_calculation", available=set())


def test_available_data_reads_the_recorded_kinds(monkeypatch):
    import core.state as state
    from core.catalogue.suggest import available_data
    metas = [{"type": "SoilProfile", "kind": "cpt"}, {"type": "SoilProfile", "kind": None}, {"type": "Grid"}]
    monkeypatch.setattr(state.state_manager, "list_by_type", lambda t: metas)
    assert available_data() == {"cpt"}  # a table without a recorded kind is not guessed


def test_uncurated_tool_metadata_comes_from_the_catalogue():
    from core.geoai.tool_metadata import get_tool_metadata
    meta = get_tool_metadata("API_unit_shaft_friction_clay")
    assert meta["method"].startswith("Unit shaft friction: API (Clay)") and meta["standard"] == "API RP2GEO"
    assert get_tool_metadata("validate_float")["method"].startswith("Groundhog Deterministic")  # not catalogued
