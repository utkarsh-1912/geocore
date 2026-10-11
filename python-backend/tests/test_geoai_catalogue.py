# Author: Utkarsh Gupta
# License: GPL v3
"""
GeoAI on the calculation catalogue (Phase 6): catalogue metadata on tool listings and the tools used in an answer
(UI only, never in the model's tool messages), applicability warnings (only when a check fails, so prompts of
valid calls are unchanged), and the optional catalogue-grouped tool offer (off by default).
"""
import json

import pytest

import core.geoai.tool_definitions  # noqa: F401  (registers the curated tools)
from core.catalogue.applicability import check
from core.geoai.agent import AgentStreamEvent, GeoAIAgent, _result_summary
from core.geoai.catalogue_link import sibling_tools, tool_catalogue, tool_warnings
from core.geoai.model_provider import make_tool_result_message
from core.geoai.tool_registry import tool_registry
from core.geoai.tool_selector import with_sibling_methods


def test_rankine_backfill_steeper_than_phi_is_flagged():
    assert check("earthpressurecoefficients_rankine", {"phi_eff": 30, "wall_angle": 0, "top_angle": 20}) == []
    msg = check("earthpressurecoefficients_rankine", {"phi_eff": 30, "wall_angle": 0, "top_angle": 35})
    assert len(msg) == 1 and "steeper than the friction angle" in msg[0]


def test_relative_density_uses_groundhog_naming_and_the_tool_maps_it():
    # Groundhog: e_min = loosest state (larger void ratio), e_max = densest.
    assert check("relative_density", {"void_ratio": 0.6, "e_min": 0.9, "e_max": 0.4}) == []
    assert "swapped" in check("relative_density", {"void_ratio": 0.6, "e_min": 0.4, "e_max": 0.9})[0]
    assert "outside 0-100 %" in check("relative_density", {"void_ratio": 1.0, "e_min": 0.9, "e_max": 0.4})[0]
    # The curated tool uses the conventional meaning (e_min = densest); its arg_map turns it into Groundhog's.
    tool = tool_registry.get_tool("calculate_relative_density")
    assert tool_warnings(tool, {"void_ratio": 0.6, "e_min": 0.4, "e_max": 0.9}) == []
    assert tool_warnings(tool, {"void_ratio": 1.0, "e_min": 0.4, "e_max": 0.9})


def test_checks_never_break_and_unknown_functions_have_none():
    assert check("relative_density", {"void_ratio": "x"}) == []
    assert check("not_a_function", {"a": 1}) == []


def test_warnings_only_when_a_check_fails_so_valid_prompts_are_unchanged():
    ok = tool_registry.invoke_tool("calculate_earth_pressure_rankine", {"phi_eff": 30, "top_angle": 0})
    assert "_warnings" not in ok
    bad = tool_registry.invoke_tool("calculate_earth_pressure_rankine", {"phi_eff": 30, "top_angle": 35})
    assert bad["_warnings"] and "steeper" in bad["_warnings"][0]
    # The model reads the warning in the tool message; catalogue metadata is never part of it.
    wrapper = {"status": "success", "tool_name": "calculate_earth_pressure_rankine", "result": bad}
    content = json.loads(make_tool_result_message("1", "calculate_earth_pressure_rankine", wrapper).content)
    assert content["result"]["_warnings"] == bad["_warnings"] and "catalogue" not in json.dumps(content)


def test_result_summary_reports_the_warning():
    bad = tool_registry.invoke_tool("calculate_earth_pressure_rankine", {"phi_eff": 30, "top_angle": 35})
    text = _result_summary([{"name": "calculate_earth_pressure_rankine",
                             "result": {"status": "success", "result": bad}}])
    assert "Warning: Rankine earth pressure is undefined" in text


def test_tool_catalogue_for_curated_and_auto_registered_tools():
    info = tool_catalogue(tool_registry.get_tool("calculate_earth_pressure_rankine"))
    assert info["calculation_id"] == "earthpressurecoefficients_rankine" and info["status"] == "verified"
    assert info["benchmarks"] >= 1 and "frictionless wall" in info["applicability"]
    auto = next(t for t in tool_registry._tools.values() if not t.form_function and tool_catalogue(t))
    assert tool_catalogue(auto)["method_id"]
    listing = {t["name"]: t for t in tool_registry.list_tools()}
    assert listing["calculate_earth_pressure_rankine"]["catalogue"]["calculation"] == "Earth Pressure (Rankine)"


def test_agent_tools_used_and_stream_events_carry_the_catalogue():
    agent = GeoAIAgent(provider=None, registry=tool_registry)
    assert agent._catalogue_of("calculate_earth_pressure_rankine")["catalogue"]["status"] == "verified"
    assert agent._catalogue_of("no_such_tool") == {}
    event = AgentStreamEvent(type="tool_result", tool_name="t", catalogue={"status": "verified"})
    assert json.loads(event.to_sse()[len("data: "):])["catalogue"] == {"status": "verified"}
    assert "catalogue" not in json.loads(AgentStreamEvent(type="token", content="x").to_sse()[len("data: "):])


def test_sibling_methods_grouping_is_ordered_and_off_by_default(monkeypatch):
    siblings = sibling_tools("calculate_relative_density")
    assert "calculate_bulk_unit_weight" in siblings and "calculate_relative_density" not in siblings
    assert "relative_density" not in siblings  # the auto-registered twin of the same function is not another method
    out = [n for n, _ in with_sibling_methods([("calculate_relative_density", 2.0), ("calculate_bulk_unit_weight", 1.0)])]
    assert out[:1 + len(siblings)] == ["calculate_relative_density", *siblings]  # the methods follow the ranked tool
    assert len(out) == len(set(out))
    monkeypatch.delenv("GEOAI_CATALOGUE_METHODS", raising=False)
    from core.geoai.model_config import GeoAIModelConfig
    assert GeoAIModelConfig().catalogue_methods is False
    monkeypatch.setenv("GEOAI_CATALOGUE_METHODS", "1")
    assert GeoAIModelConfig().catalogue_methods is True


@pytest.mark.parametrize("flag", [False, True])
def test_select_relevant_tools_accepts_the_grouping_flag(flag):
    from core.geoai.tool_selector import select_relevant_tools
    tools = select_relevant_tools("relative density from void ratio", None, max_tools=5, group_methods=flag)
    assert tools and len({t["function"]["name"] for t in tools}) == len(tools)


def test_explain_accepts_a_geoai_tool_name_and_maps_its_arguments():
    # The chat "Explain" button sends the GeoAI tool and its arguments; the explainer works on the Groundhog
    # function, so the tool's renames apply (conventional e_min = densest = Groundhog's e_max).
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    out = client.post("/api/geoai/explain", json={
        "function_id": "calculate_relative_density",
        "args": {"void_ratio": 0.6, "e_min": 0.4, "e_max": 0.9}, "results": {"relative_density": 0.6}}).json()
    assert out["tool_name"] == "relative_density"
    given = {i["key"]: i["value"] for i in out["inputs"]}
    assert given == {"void_ratio": 0.6, "e_max": 0.4, "e_min": 0.9}
    assert any(s["title"] == "Governing equation" for s in out["steps"])
    # A GeoCore function id is used as it is (the results Formula card).
    same = client.post("/api/geoai/explain", json={"function_id": "relative_density",
                                                   "args": {"void_ratio": 0.6}, "results": {"Dr [-]": 0.6}}).json()
    assert same["tool_name"] == "relative_density"
    assert client.post("/api/geoai/explain", json={"args": {}}).status_code == 400
