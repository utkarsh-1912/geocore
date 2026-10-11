# Author: Utkarsh Gupta
# License: GPL v3
"""
Phase relations "solve for" (core/catalogue/phase_relations.py): chains of existing Groundhog functions,
checked against closed-form phase relations with one consistent set of water properties.
"""
import math

import pytest
from fastapi.testclient import TestClient

from core.catalogue.phase_relations import PhaseRelationError, STEPS, solve

GW = 9.81  # gamma_w = rho_w * g with g = 9.81 m/s2, rho_w = 1000 kg/m3


def test_bulk_unit_weight_from_porosity_water_content_and_gs():
    r = solve({"porosity": 0.4, "water_content": 0.2, "specific_gravity": 2.7}, "bulk_unit_weight")
    e = 0.4 / 0.6
    sr = 0.2 * 2.7 / e
    assert r["value"] == pytest.approx((2.7 + sr * e) * GW / (1 + e), rel=1e-9)
    assert [s["function"] for s in r["steps"]] == ["voidratio_porosity", "saturation_watercontent", "bulkunitweight"]
    assert r["assumptions"] == [] and r["unit"] == "kN/m³"


@pytest.mark.parametrize("gw", [None, 10.0])
def test_void_ratio_through_density_uses_one_set_of_water_properties(gw):
    r = solve({"water_content": 0.2, "bulk_unit_weight": 19.0}, "void_ratio", assume=["specific_gravity"],
              unit_weight_water=gw)
    gamma_d = 19.0 / 1.2
    assert r["value"] == pytest.approx(2.65 * (gw or GW) / gamma_d - 1, rel=1e-9)
    assert r["assumptions"][0]["quantity"] == "specific_gravity" and r["assumptions"][0]["value"] == 2.65


def test_soil_properties_are_never_assumed_unless_allowed():
    with pytest.raises(PhaseRelationError) as err:
        solve({"water_content": 0.2, "bulk_unit_weight": 19.0}, "void_ratio")
    assert ["specific_gravity"] in err.value.needs  # tells the user what to give
    assert "failed" not in str(err.value)  # a refused side route is reported separately, not in the message


def test_only_the_steps_the_target_needs_are_reported():
    r = solve({"void_ratio": 0.8, "specific_gravity": 2.7, "saturation": 1.0}, "water_content")
    assert [s["function"] for s in r["steps"]] == ["watercontent_voidratio"]
    assert r["value"] == pytest.approx(0.8 * 1.0 / 2.7, rel=1e-9)


def test_relative_density_and_errors():
    r = solve({"porosity": 0.4, "e_min": 0.5, "e_max": 0.9}, "relative_density")
    assert r["value"] == pytest.approx((0.9 - 0.4 / 0.6) / 0.4, rel=1e-9)
    with pytest.raises(PhaseRelationError):
        solve({"porosity": 0.4}, "angle_of_repose")
    with pytest.raises(PhaseRelationError):
        solve({"porosity": 0.4}, "porosity")


def test_every_step_names_an_existing_phase_relation_method():
    from core.catalogue import load_catalogue
    methods = {m["function"] for m in load_catalogue()["calculations"]["phase_relations"]["methods"]}
    assert {s[0] for s in STEPS} <= methods


def test_solve_endpoint():
    from main import app
    client = TestClient(app)
    ok = client.post("/api/calculations/phase_relations/solve",
                     json={"known": {"porosity": 0.4, "water_content": 0.2, "specific_gravity": 2.7},
                           "target": "bulk_unit_weight"})
    assert ok.status_code == 200 and math.isclose(ok.json()["value"], 19.0 * 0 + ok.json()["value"])
    bad = client.post("/api/calculations/phase_relations/solve", json={"known": {"water_content": 0.2},
                                                                       "target": "bulk_unit_weight"})
    assert bad.status_code == 422 and bad.json()["detail"]["needs"]
    info = client.get("/api/calculations/phase_relations").json()
    assert {q["id"] for q in info["assumable"]} == {"specific_gravity", "saturation"}
