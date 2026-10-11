# Author: Utkarsh Gupta
# License: GPL v3
"""
GeoAI tool get_project_inputs (core/geoai/tools_project_model.py): a calculation's inputs from the project ground
model, with sources, through the validated tool registry. Temporary project database and a fake workspace.
"""
import pytest

import core.geoai.tool_definitions  # noqa: F401  (registers the tools)
from core.geoai.exceptions import GeoAIValidationError
from core.geoai.tool_registry import tool_registry
from test_project_model import AGS4, FakeWorkspace, _profile


@pytest.fixture
def project(tmp_path, monkeypatch):
    import core.state as state
    workspace = FakeWorkspace({"p1": ("BH-01", _profile())})
    monkeypatch.setenv("GEOCORE_PROJECT_DB", str(tmp_path / "project.sqlite"))
    monkeypatch.setattr(state.state_manager, "list_by_type", workspace.list_by_type)
    monkeypatch.setattr(state.state_manager, "get", workspace.get)
    monkeypatch.setattr("core.geoai.data_access.recorded_groundwater_depth", lambda store=None: 1.5)
    return workspace


def test_inputs_for_a_curated_tool_with_sources(project):
    out = tool_registry.invoke_tool("get_project_inputs", {"calculation": "calculate_earth_pressure_rankine",
                                                           "location": "bh-01", "z_top_m": 1.0, "z_bottom_m": 3.0})
    phi = out["values"]["phi_eff"]
    assert phi["value"] == pytest.approx(28.0) and phi["unit"] == "deg"
    assert "BH-01" in phi["source"] and "thickness-weighted over 1-3 m" in phi["source"]
    assert out["location"] == "BH-01" and out["depth_range_m"] == [1.0, 3.0]


def test_tool_field_names_follow_the_tool_not_groundhog(project):
    # calculate_relative_density renames Groundhog's e_min/e_max; nothing in the profile supplies them, and the
    # reasons are keyed by the names the tool takes.
    out = tool_registry.invoke_tool("get_project_inputs", {"calculation": "calculate_relative_density",
                                                           "location": "BH-01", "z_top_m": 0.0, "z_bottom_m": 1.0})
    assert out["values"] == {}


def test_ags_spt_values_reach_geoai(project):
    from core.project.ags_import import import_ags
    import_ags(AGS4, "site.ags")
    out = tool_registry.invoke_tool("get_project_inputs", {"calculation": "overburdencorrection_spt_liaowhitman",
                                                           "location": "BH1", "z_top_m": 4.0, "z_bottom_m": 8.0})
    assert out["values"]["N"]["value"] == pytest.approx(100 / 3)
    assert "mean of 3 SPT" in out["values"]["N"]["source"] and "sigma_vo_eff" in out["unavailable"]


def test_unknown_location_lists_the_project_locations(project):
    with pytest.raises(GeoAIValidationError, match="BH-01"):
        tool_registry.invoke_tool("get_project_inputs", {"calculation": "calculate_earth_pressure_rankine",
                                                         "location": "BH-99", "z_top_m": 0, "z_bottom_m": 1})


def test_depth_range_must_have_thickness(project):
    with pytest.raises(GeoAIValidationError, match="must be below"):
        tool_registry.invoke_tool("get_project_inputs", {"calculation": "calculate_earth_pressure_rankine",
                                                         "location": "BH-01", "z_top_m": 2, "z_bottom_m": 2})
