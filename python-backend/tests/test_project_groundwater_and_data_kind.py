# Author: Utkarsh Gupta
# License: GPL v3
"""
Project groundwater level (recorded, persisted, synced into ProjectContext, exposed through
/api/geoai/project/*) and the data kind recorded at upload (CPT sounding vs layered soil
profile), which decides what GeoAI treats as a soil profile and what as a CPT.
"""
import json
import warnings

import numpy as np
import pandas as pd
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import core.geoai.tool_definitions  # noqa: F401  (registers the GeoAI tools)
from core import state
from core.geoai import data_access, project_cpt
from core.geoai.data_access import (GROUNDWATER_PROVENANCE, ProjectContext, active_project_context,
                                    validate_groundwater_depth)
from core.geoai.exceptions import GeoAIValidationError
from core.paths import CONFIG_DIR_ENV_VAR
from core.state import PROJECT_SETTINGS_FILENAME, SAVED_OBJECTS_FILENAME, StateManager

warnings.filterwarnings("ignore")

LAYERED = pd.DataFrame({"Depth from [m]": [0.0, 3.0], "Depth to [m]": [3.0, 10.0], "Soil type": ["Sand", "Clay"],
                        "qc [MPa]": [8.0, 1.2], "UnitWeight [kN_m3]": [19.0, 17.0]})


def cpt_table(n=40):
    """A CPT stored the way an upload must be (depth intervals, qc [MPa], fs [kPa])."""
    z = np.round(np.arange(0.0, n * 0.2, 0.2), 2)
    # Rounded: groundhog requires each layer's "from" to equal the previous "to" exactly, and
    # z + 0.2 alone yields values such as 0.6000000000000001 that break that.
    return pd.DataFrame({"Depth from [m]": z, "Depth to [m]": np.round(z + 0.2, 2),
                         "qc [MPa]": np.where(z < 3, 6.0, 1.0), "fs [kPa]": np.where(z < 3, 40.0, 20.0)})


@pytest.fixture
def sm(tmp_path, monkeypatch):
    """A fresh StateManager on an isolated config dir, installed wherever GeoAI reads the store."""
    monkeypatch.setenv(CONFIG_DIR_ENV_VAR, str(tmp_path / "config"))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(state, "_BACKEND_DIR", tmp_path / "backend")
    manager = StateManager()
    manager._loaded = True
    monkeypatch.setattr(state, "state_manager", manager)
    monkeypatch.setattr(data_access, "state_manager", manager)
    monkeypatch.setattr(active_project_context, "water_table_depth", None)
    return manager


@pytest.fixture
def client(sm):
    from core.geoai.api import router as geoai_router
    from core.router import create_dynamic_router
    app = FastAPI()
    app.include_router(create_dynamic_router(), prefix="/api")
    app.include_router(geoai_router, prefix="/api")
    return TestClient(app)


# ------------------------------------------------------------------ groundwater: validation

@pytest.mark.parametrize("raw,expected", [(None, None), ("", None), ("  ", None), (0, 0.0), (2.5, 2.5),
                                          ("3.25", 3.25)])
def test_groundwater_validation_accepts(raw, expected):
    assert validate_groundwater_depth(raw) == expected


@pytest.mark.parametrize("raw", [-0.1, "abc", "2 kPa", float("nan"), float("inf"), True, [1.0]])
def test_groundwater_validation_rejects(raw):
    with pytest.raises(GeoAIValidationError) as e:
        validate_groundwater_depth(raw)
    assert e.value.errors and e.value.errors[0]["field"] == "groundwater_depth_m"


def test_groundwater_units_converted_deterministically():
    assert validate_groundwater_depth(2500, "mm") == pytest.approx(2.5)
    with pytest.raises(GeoAIValidationError):
        validate_groundwater_depth(2.5, "kPa")


# ------------------------------------------------------------------ groundwater: persistence & sync

def test_groundwater_persists_and_clears(sm, tmp_path):
    assert data_access.recorded_groundwater_depth() is None
    assert data_access.record_groundwater_depth(1.75) == 1.75
    assert active_project_context.water_table_depth == 1.75
    path = tmp_path / "config" / PROJECT_SETTINGS_FILENAME
    assert json.loads(path.read_text(encoding="utf-8")) == {"groundwater_depth_m": 1.75}

    reopened = StateManager()            # a restart reads the same file
    assert data_access.recorded_groundwater_depth(reopened) == 1.75

    assert data_access.record_groundwater_depth(None) is None
    assert active_project_context.water_table_depth is None
    assert json.loads(path.read_text(encoding="utf-8")) == {}
    assert data_access.recorded_groundwater_depth(StateManager()) is None


def test_invalid_value_is_not_saved(sm):
    data_access.record_groundwater_depth(2.0)
    with pytest.raises(GeoAIValidationError):
        data_access.record_groundwater_depth(-1)
    assert data_access.recorded_groundwater_depth() == 2.0 and active_project_context.water_table_depth == 2.0


def test_settings_do_not_touch_saved_objects(sm, tmp_path):
    data_access.record_groundwater_depth(3.0)
    assert not (tmp_path / "config" / SAVED_OBJECTS_FILENAME).exists()


def test_from_state_manager_and_project_soil_use_recorded_level(sm):
    from core.geoai.project_soil import ProjectSoil
    sm.store(LAYERED.drop(columns=["qc [MPa]"]), "SoilProfile", name="BH-01", kind="soil_profile")
    ctx = ProjectContext.from_state_manager()
    assert ctx.water_table_depth is None and "not recorded" in ctx.get_compact_context_string()

    data_access.record_groundwater_depth(2.5)
    ctx = ProjectContext.from_state_manager()
    assert ctx.water_table_depth == 2.5 and "2.5 m below ground surface" in ctx.get_compact_context_string()
    value, _ = ProjectSoil(context_loader=lambda: ctx).groundwater_depth()
    assert value.value == 2.5 and value.unit == "m" and value.source == GROUNDWATER_PROVENANCE


def test_recorded_level_used_without_a_soil_profile():
    from core.geoai.project_soil import ProjectSoil
    ctx = ProjectContext("p")
    ctx.water_table_depth = 4.0
    value, _ = ProjectSoil(context_loader=lambda: ctx).groundwater_depth()
    assert value.value == 4.0 and value.source == GROUNDWATER_PROVENANCE
    assert ProjectSoil(context_loader=lambda: ProjectContext("p")).groundwater_depth()[0] is None


def test_shallow_tool_reports_recorded_level_provenance(sm, monkeypatch):
    from core.geoai import project_soil
    from core.geoai.tool_registry import tool_registry
    ctx = ProjectContext("p")
    ctx.water_table_depth = 1.0
    monkeypatch.setattr(project_soil, "load_project_context", lambda: ctx)
    res = tool_registry.invoke_tool("calculate_shallow_foundation_capacity", dict(
        foundation_shape="square", width_m=2.0, foundation_depth_m=1.0, friction_angle_deg=30,
        unit_weight_kn_m3=18))
    text = json.dumps(res)
    assert GROUNDWATER_PROVENANCE in text


# ------------------------------------------------------------------ groundwater: API

def test_groundwater_api_round_trip(client, sm):
    r = client.get("/api/geoai/project/groundwater")
    assert r.status_code == 200
    assert r.json()["groundwater_depth_m"] is None and r.json()["status"] == "not recorded"

    r = client.put("/api/geoai/project/groundwater", json={"groundwater_depth_m": 2.5, "unit": "m"})
    assert r.status_code == 200 and r.json()["groundwater_depth_m"] == 2.5
    assert r.json()["provenance"] == GROUNDWATER_PROVENANCE and r.json()["unit"] == "m"
    assert client.get("/api/geoai/project/groundwater").json()["groundwater_depth_m"] == 2.5
    assert active_project_context.water_table_depth == 2.5

    ctx = client.get("/api/geoai/project/context").json()
    assert ctx["groundwater"]["groundwater_depth_m"] == 2.5
    assert "2.5 m below ground surface" in ctx["compact_context"]

    r = client.put("/api/geoai/project/groundwater", json={"groundwater_depth_m": None})
    assert r.status_code == 200 and r.json()["status"] == "not recorded"
    assert client.get("/api/geoai/project/groundwater").json()["groundwater_depth_m"] is None
    assert "not recorded" in client.get("/api/geoai/project/context").json()["compact_context"]


@pytest.mark.parametrize("body", [{"groundwater_depth_m": -1}, {"groundwater_depth_m": "deep"},
                                  {"groundwater_depth_m": 2, "unit": "kPa"}, {}])
def test_groundwater_api_rejects_invalid(client, body):
    client.put("/api/geoai/project/groundwater", json={"groundwater_depth_m": 1.0})
    r = client.put("/api/geoai/project/groundwater", json=body)
    assert r.status_code == 422 and r.json()["detail"]["status"] == "ValidationError"
    assert client.get("/api/geoai/project/groundwater").json()["groundwater_depth_m"] == 1.0


# ------------------------------------------------------------------ data kind: storage

def test_kind_persisted_with_saved_objects(sm, tmp_path):
    a = sm.store(cpt_table(), "SoilProfile", name="CPT-01.csv", kind="cpt")
    b = sm.store(LAYERED, "SoilProfile", name="BH-01.csv", kind="soil_profile")
    c = sm.store(LAYERED, "SoilProfile", name="old.csv")
    saved = {o["id"]: o for o in json.loads((tmp_path / "config" / SAVED_OBJECTS_FILENAME).read_text("utf-8"))}
    assert saved[a]["kind"] == "cpt" and saved[b]["kind"] == "soil_profile" and "kind" not in saved[c]

    reloaded = StateManager()
    kinds = {m["id"]: m.get("kind") for m in reloaded.list_by_type("SoilProfile")}
    assert kinds == {a: "cpt", b: "soil_profile", c: None}


def test_unknown_kind_rejected(sm):
    with pytest.raises(ValueError):
        sm.store(LAYERED, "SoilProfile", name="x", kind="borehole")


def test_upload_records_kind(client, sm):
    cpt_csv = cpt_table().to_csv(index=False).encode()
    r = client.post("/api/objects/upload?type_name=SoilProfile&data_kind=cpt",
                    files={"file": ("CPT-07.csv", cpt_csv, "text/csv")})
    assert r.status_code == 200, r.text
    assert r.json()["kind"] == "cpt"
    layered_csv = LAYERED.to_csv(index=False).encode()
    r = client.post("/api/objects/upload?type_name=SoilProfile&data_kind=soil_profile",
                    files={"file": ("BH-02.csv", layered_csv, "text/csv")})
    assert r.status_code == 200, r.text
    listed = {o["name"]: o.get("kind") for o in client.get("/api/objects/SoilProfile").json()["objects"]}
    assert listed == {"CPT-07.csv": "cpt", "BH-02.csv": "soil_profile"}

    r = client.post("/api/objects/upload?type_name=SoilProfile&data_kind=borehole",
                    files={"file": ("x.csv", layered_csv, "text/csv")})
    assert r.status_code == 422


def test_create_records_kind_and_rejects_unknown(client, sm):
    rows = LAYERED.drop(columns=["qc [MPa]"]).to_dict(orient="records")
    r = client.post("/api/objects/create?type_name=SoilProfile",
                    json={"raw_data": rows, "name": "Manual", "data_kind": "soil_profile"})
    assert r.status_code == 200, r.text
    assert sm.list_by_type("SoilProfile")[0]["kind"] == "soil_profile"
    r = client.post("/api/objects/create?type_name=SoilProfile",
                    json={"raw_data": rows, "name": "Bad", "data_kind": "borehole"})
    assert r.status_code == 422


# ------------------------------------------------------------------ data kind: GeoAI context and CPT discovery

def test_context_and_cpt_discovery_respect_kind(sm):
    sm.store(cpt_table(), "SoilProfile", name="CPT-01.csv", kind="cpt")
    sm.store(LAYERED, "SoilProfile", name="BH-01.csv", kind="soil_profile")   # has a qc column
    ctx = ProjectContext.from_state_manager()
    assert ctx.list_profile_names() == ["BH-01.csv"]
    assert "qc=" in ctx.get_compact_context_string()   # its representative qc stays a layer property

    cpts, unusable = project_cpt.discover_project_cpts(sm)
    assert [c.cpt_id for c in cpts] == ["CPT-01"] and not unusable
    assert cpts[0].kind_note is None and "note" not in cpts[0].listing()
    assert not any("kind not recorded" in f for f in project_cpt.data_quality_flags(cpts[0]))


def test_cpt_kind_without_qc_is_reported(sm):
    sm.store(LAYERED.drop(columns=["qc [MPa]"]), "SoilProfile", name="CPT-09.csv", kind="cpt")
    cpts, unusable = project_cpt.discover_project_cpts(sm)
    assert not cpts and "recorded as a CPT" in unusable[0]["reason"]
    assert ProjectContext.from_state_manager().list_profile_names() == []


def test_legacy_objects_keep_behaviour_and_flag_ambiguity(sm, monkeypatch):
    import core.geoai.tools_cpt_piles as T
    sm.store(cpt_table(), "SoilProfile", name="CPT-03.xlsx")           # saved before kinds were recorded
    sm.store(LAYERED, "SoilProfile", name="BH-old.csv")                 # legacy layered profile with qc
    sm.store(LAYERED, "SoilProfile", name="BH-new.csv", kind="soil_profile")

    ctx = ProjectContext.from_state_manager()                          # recorded profiles first
    assert ctx.list_profile_names() == ["BH-new.csv", "CPT-03.xlsx", "BH-old.csv"]

    monkeypatch.setattr(T, "_store", lambda: sm)
    from core.geoai.tool_registry import tool_registry
    listing = tool_registry.invoke_tool("list_project_cpts", {})
    assert sorted(c["cpt_id"] for c in listing["cpts"]) == ["BH-old", "CPT-03"]   # qc column -> CPT, as before
    assert all("Data kind not recorded" in c["note"] for c in listing["cpts"])
    assert "data kind not recorded" in listing["note"]
    summary = tool_registry.invoke_tool("get_cpt_summary", {"cpt_id": "CPT-03"})
    assert any("Data kind not recorded" in f for f in summary["data_quality_flags"])
