# Author: Utkarsh Gupta
# License: GPL v3
"""
Project ground model (core/project): indexing the workspace, form pre-fill with sources, runs, derived values,
staleness and reports. Uses a temporary project database and a fake workspace: never the user's data.
"""
import pandas as pd
import pytest
from fastapi.testclient import TestClient


class FakeWorkspace:
    """The two state_manager calls sync uses, over in-memory profiles."""

    def __init__(self, profiles):
        self.profiles = profiles  # id -> (name, DataFrame)

    def list_by_type(self, type_name):
        return [{"id": pid, "name": name, "type": "SoilProfile"} for pid, (name, _) in self.profiles.items()]

    def get(self, pid):
        return self.profiles.get(pid, (None, None))[1]


def _profile(phi_sand=32.0):
    return pd.DataFrame([
        {"Depth from [m]": 0.0, "Depth to [m]": 2.0, "Soil type": "Sand", "Total unit weight [kN/m3]": 18.0,
         "Friction angle [deg]": phi_sand, "Undrained shear strength [kPa]": 0.0},
        {"Depth from [m]": 2.0, "Depth to [m]": 6.0, "Soil type": "Clay", "Total unit weight [kN/m3]": 17.0,
         "Friction angle [deg]": 24.0, "Undrained shear strength [kPa]": 50.0},
    ])


@pytest.fixture
def project(tmp_path, monkeypatch):
    import core.state as state
    workspace = FakeWorkspace({"p1": ("BH-01", _profile())})
    monkeypatch.setenv("GEOCORE_PROJECT_DB", str(tmp_path / "project.sqlite"))
    monkeypatch.setattr(state.state_manager, "list_by_type", workspace.list_by_type)
    monkeypatch.setattr(state.state_manager, "get", workspace.get)
    monkeypatch.setattr("core.geoai.data_access.recorded_groundwater_depth", lambda store=None: 1.5)
    return workspace


def _location_id():
    from core.project.ground import summary
    return summary()["locations"][0]["id"]


def test_sync_indexes_profiles_with_sources(project):
    from core.project.ground import summary, sync_from_workspace
    counts = sync_from_workspace()
    assert counts["locations"] == 1 and counts["layers"] == 2 and counts["parameters"] == 6
    loc = summary()["locations"][0]
    assert loc["name"] == "BH-01" and loc["kind"] == "borehole" and loc["layers"] == 2 and loc["groundwater_m"] == 1.5
    assert sync_from_workspace()["locations"] == 1 and len(summary()["locations"]) == 1  # re-sync replaces, no duplicates


def test_prefill_thickness_weighted_with_source_and_refuses_undefined(project):
    from core.project.ground import prefill, sync_from_workspace
    sync_from_workspace()
    loc = _location_id()
    out = prefill("earthpressurecoefficients_rankine", loc, 1.0, 3.0)
    phi = out["proposals"]["phi_eff"]
    assert phi["value"] == pytest.approx((32 * 1 + 24 * 1) / 2) and phi["unit"] == "deg"
    assert "thickness-weighted over 1-3 m" in phi["source"] and "Friction angle [deg]" in phi["source"]
    su = prefill("su_categories", loc, 0.0, 4.0)
    assert "undrained_shear_strength" not in su["proposals"]  # su = 0 in the sand: not defined, never guessed
    assert "layer 1" in su["unavailable"]["undrained_shear_strength"]
    assert prefill("su_categories", loc, 2.5, 4.0)["proposals"]["undrained_shear_strength"]["value"] == 50.0


def test_runs_derive_parameters_and_go_stale_when_inputs_change(project):
    from core.project.ground import prefill, sync_from_workspace
    from core.project.runs import list_runs, record_run
    sync_from_workspace()
    loc = _location_id()
    proposal = prefill("earthpressurecoefficients_rankine", loc, 0.5, 1.5)["proposals"]["phi_eff"]
    run_a = record_run("earthpressurecoefficients_rankine", {"phi_eff": proposal["value"], "wall_angle": 0, "top_angle": 0},
                       {"KaR [-]": 0.307, "KpR [-]": 3.25}, input_sources={"phi_eff": proposal}, location_id=loc)
    runs = {r["id"]: r for r in list_runs()}
    assert runs[run_a]["stale"] == [] and runs[run_a]["status"] == "verified"

    # Chaining: a later calculation can take run A's result as its input; it depends on run A.
    from core.project.store import connect
    with connect() as db:
        derived = db.execute("SELECT param_key, value FROM parameters WHERE source_kind = 'calculation'").fetchall()
    assert {d["param_key"] for d in derived} == {f"run:{run_a}|KaR [-]", f"run:{run_a}|KpR [-]"}
    run_b = record_run("earthpressurecoefficients_rankine", {"phi_eff": 30}, {"KaR [-]": 0.333},
                       input_sources={"Ka": {"source": f"run #{run_a}", "inputs": [{"param_key": f"run:{run_a}|KaR [-]",
                                                                                   "value": 0.307}]}}, location_id=loc)

    # The engineer edits the profile (phi of the sand) and re-syncs: run A, and run B through it, are out of date.
    project.profiles["p1"] = ("BH-01", _profile(phi_sand=34.0))
    sync_from_workspace()
    runs = {r["id"]: r for r in list_runs()}
    assert any("changed from 32 to 34" in s for s in runs[run_a]["stale"])
    assert any(f"run #{run_a}" in s for s in runs[run_b]["stale"])


def test_report_has_inputs_with_sources_method_status_and_staleness(project):
    from core.project.ground import prefill, sync_from_workspace
    from core.project.report import build_report, render_html
    from core.project.runs import record_run
    sync_from_workspace()
    loc = _location_id()
    proposal = prefill("earthpressurecoefficients_rankine", loc, 0.5, 1.5)["proposals"]["phi_eff"]
    run = record_run("earthpressurecoefficients_rankine", {"phi_eff": proposal["value"], "wall_angle": 0, "top_angle": 0},
                     {"KaR [-]": 0.307, "KpR [-]": 3.25, "Plot": {"type": "plotly", "data": []}},
                     input_sources={"phi_eff": proposal}, location_id=loc)
    r = build_report(run)
    phi = next(i for i in r["inputs"] if i["key"] == "phi_eff")
    assert "BH-01" in phi["source"] and next(i for i in r["inputs"] if i["key"] == "wall_angle")["source"] == "entered by the user"
    assert r["status"] == "verified" and any("Rankine" in b for b in r["benchmarks"])
    assert [v["value"] for v in r["results"]] == [0.307, 3.25]  # the figure is not a result value
    page = render_html([r])
    assert "Inputs" in page and "BH-01" in page and "Verified against closed-form cases" in page and "<script" not in page


def test_project_endpoints(project):
    from main import app
    client = TestClient(app)
    assert client.post("/api/project/sync").json()["locations"][0]["name"] == "BH-01"
    loc = client.get("/api/project").json()["locations"][0]["id"]
    assert len(client.get(f"/api/project/locations/{loc}/layers").json()) == 2
    pre = client.post("/api/project/prefill", json={"function_id": "earthpressurecoefficients_rankine",
                                                   "location_id": loc, "z_top": 0, "z_bottom": 1}).json()
    assert pre["proposals"]["phi_eff"]["value"] == 32.0
    run = client.post("/api/project/runs", json={"function_id": "earthpressurecoefficients_rankine",
                                                "inputs": {"phi_eff": 32}, "results": {"KaR [-]": 0.307}}).json()["id"]
    assert client.get(f"/api/project/runs/{run}/report").text.startswith("<!doctype html>")
    assert client.get(f"/api/project/runs/{run}/report?format=json").json()["run"] == run
    assert f"Run #{run}" in client.get("/api/project/report").text
    assert client.delete(f"/api/project/runs/{run}").status_code == 200
    assert client.post("/api/project/prefill", json={"function_id": "x", "location_id": loc, "z_top": 1,
                                                    "z_bottom": 1}).status_code == 400


AGS4 = """"GROUP","PROJ"
"HEADING","PROJ_ID","PROJ_NAME"
"DATA","P1","Test project"

"GROUP","LOCA"
"HEADING","LOCA_ID","LOCA_TYPE","LOCA_FDEP"
"UNIT","","","m"
"DATA","BH1","CP","10.0"
"DATA","BH2","CP","5.0"

"GROUP","GEOL"
"HEADING","LOCA_ID","GEOL_TOP","GEOL_BASE","GEOL_DESC"
"UNIT","","m","m",""
"DATA","BH1","0.0","3.0","Firm brown CLAY, sandy"
"DATA","BH1","3.0","10.0","Dense grey SAND"

"GROUP","ISPT"
"HEADING","LOCA_ID","ISPT_TOP","ISPT_NVAL"
"UNIT","","m",""
"DATA","BH1","4.0","20"
"DATA","BH1","6.0","30"
"DATA","BH1","9.0",">50"
"""


def test_ags_import_holes_strata_and_spt_with_sources(project):
    from core.project.ags_import import import_ags
    from core.project.ground import prefill, summary, sync_from_workspace
    counts = import_ags(AGS4, "site.ags")
    assert counts["locations"] == 1 and counts["layers"] == 2 and counts["parameters"] == 1
    assert counts["skipped"] == ["BH2: no stratigraphy (GEOL)"]
    loc = next(l for l in summary()["locations"] if l["name"] == "BH1")
    from core.project.store import connect
    with connect() as db:
        layers = db.execute("SELECT idx, soil_type FROM layers WHERE location_id = ? ORDER BY idx", (loc["id"],)).fetchall()
        spt = db.execute("SELECT value, quantity, source_ref FROM parameters WHERE location_id = ?", (loc["id"],)).fetchone()
    assert layers[0]["soil_type"] == "Firm brown CLAY, sandy"  # a quoted comma stays in the description
    assert spt["value"] == pytest.approx((20 + 30 + 50) / 3) and spt["quantity"] == "spt_n"
    assert "mean of 3 SPT at 4, 6, 9 (refusal) m" in spt["source_ref"] and "site.ags" in spt["source_ref"]
    # A workspace sync keeps the imported locations; re-importing the file replaces them (no duplicates).
    sync_from_workspace()
    assert any(l["name"] == "BH1" for l in summary()["locations"])
    import_ags(AGS4, "site.ags")
    assert [l["name"] for l in summary()["locations"]].count("BH1") == 1


def test_ags_import_without_holes_says_so(project):
    from core.project.ags_import import import_ags
    assert import_ags('"GROUP","PROJ"\n"HEADING","PROJ_ID"\n"DATA","P1"\n', "x.ags")["skipped"]


def test_import_ags_endpoint(project):
    from main import app
    client = TestClient(app)
    r = client.post("/api/project/import_ags", json={"text": AGS4, "filename": "site.ags"})
    assert r.status_code == 200 and r.json()["imported"]["locations"] == 1
    assert any(l["name"] == "BH1" for l in r.json()["locations"])
    assert client.post("/api/project/import_ags", json={"text": ""}).status_code == 400


def test_spt_form_prefills_from_imported_ags(project):
    from core.project.ags_import import import_ags
    from core.project.ground import prefill, summary
    import_ags(AGS4, "site.ags")
    loc = next(l for l in summary()["locations"] if l["name"] == "BH1")["id"]
    n = prefill("overburdencorrection_spt_liaowhitman", loc, 4.0, 8.0)["proposals"]["N"]
    assert n["value"] == pytest.approx(100 / 3) and "mean of 3 SPT at 4, 6, 9 (refusal) m" in n["source"]


def test_review_sign_off_in_report_and_flagged_when_stale(project):
    from core.project.ground import prefill, sync_from_workspace
    from core.project.report import build_report, render_html
    from core.project.runs import clear_review, list_runs, record_run, review_run
    sync_from_workspace()
    loc = _location_id()
    proposal = prefill("earthpressurecoefficients_rankine", loc, 0.5, 1.5)["proposals"]["phi_eff"]
    run = record_run("earthpressurecoefficients_rankine", {"phi_eff": proposal["value"], "wall_angle": 0, "top_angle": 0},
                     {"KaR [-]": 0.307}, input_sources={"phi_eff": proposal}, location_id=loc)
    assert "Not reviewed." in render_html([build_report(run)])
    with pytest.raises(ValueError):
        review_run(run, "  ")
    with pytest.raises(KeyError):
        review_run(9999, "A. Engineer")
    review_run(run, "A. Engineer", "Inputs checked against the factual report.")
    page = render_html([build_report(run)])
    assert "Checked by <b>A. Engineer</b>" in page and "Inputs checked against the factual report." in page
    assert "applies to its earlier inputs" not in page
    assert next(r for r in list_runs() if r["id"] == run)["review"]["reviewer"] == "A. Engineer"
    # The profile changes: the sign-off stays, but the report says it was for the earlier inputs.
    project.profiles["p1"] = ("BH-01", _profile(phi_sand=34.0))
    sync_from_workspace()
    assert "applies to its earlier inputs" in render_html([build_report(run)])
    assert clear_review(run) and "Not reviewed." in render_html([build_report(run)])


def test_review_endpoints(project):
    from main import app
    client = TestClient(app)
    run = client.post("/api/project/runs", json={"function_id": "earthpressurecoefficients_rankine",
                                                "inputs": {"phi_eff": 32}, "results": {"KaR [-]": 0.307}}).json()["id"]
    assert client.post(f"/api/project/runs/{run}/review", json={"reviewer": "A. Engineer"}).json()["reviewer"] == "A. Engineer"
    assert client.post(f"/api/project/runs/{run}/review", json={"reviewer": ""}).status_code == 400
    assert client.post("/api/project/runs/9999/review", json={"reviewer": "x"}).status_code == 404
    assert "Checked by" in client.get(f"/api/project/runs/{run}/report").text
    assert client.delete(f"/api/project/runs/{run}/review").json()["cleared"] is True
