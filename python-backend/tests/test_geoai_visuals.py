"""
Chat display blocks built from tool results (core.geoai.visuals, AGENTS.md §22, §25).

The oracle is the tool result itself: every number in a block must be a value the tool
returned (or the project CPT data), never a recomputed one. Visuals reach the UI only.
"""
import json
import warnings

import pytest

import core.geoai.tool_definitions  # noqa: F401  (registers curated tools)
import core.geoai.tools_cpt_piles as T
from core.geoai.agent import GeoAIAgent
from core.geoai.model_provider import ModelResponse, StreamChunk, ToolCall
from core.geoai.tool_registry import tool_registry
from core.geoai.visuals import MAX_PROFILE_POINTS, MAX_TABLE_ROWS, build_visuals, split_unit
from test_cpt_piles import KOPPEJAN_LAYERS, FakeStore, load_fixture, synthetic_cpt

warnings.filterwarnings("ignore")


def ok(result):
    return {"status": "success", "result": result}


def by_type(blocks, kind):
    return [b for b in blocks if b["type"] == kind]


@pytest.fixture
def cpt_store(monkeypatch):
    s = FakeStore({"a": ("SoilProfile", "CPT-03.xlsx", synthetic_cpt(dz=0.01))})
    monkeypatch.setattr(T, "_store", lambda: s)
    return s


@pytest.mark.parametrize("key, label, unit", [
    ("q_ult_kpa", "q ult", "kPa"), ("Q_ult_kn_per_m", "Q ult", "kN/m"), ("pile_tip_depth_m", "pile tip depth", "m"),
    ("Gmax [kPa]", "Gmax", "kPa"), ("KaR [-]", "KaR", "-"), ("phi_eff_deg", "phi eff", "°"), ("Ic", "Ic", None),
])
def test_split_unit(key, label, unit):
    assert split_unit(key) == (label, unit)


def test_output_units_take_precedence():
    assert split_unit("sigma_z", {"sigma_z": "kPa"}) == ("sigma z", "kPa")


def test_failed_call_has_no_visuals():
    assert build_visuals("get_cpt_summary", {}, {"status": "error", "error": "CPT not found"}) == []


def test_scalar_result_becomes_metrics_with_provenance_units():
    res = {"N60": 18.0, "Dr_pct": 62.5, "density_class": "medium dense", "flag": None,
           "_provenance": {"output_units": {"N60": "-"}}}
    (block,) = build_visuals("normalize_spt_test", {}, ok(res))
    assert block["type"] == "metrics" and block["tool"] == "normalize_spt_test" and not block["detail"]
    items = {i["label"]: (i["value"], i["unit"]) for i in block["items"]}
    assert items == {"N60": (18.0, None), "Dr": (62.5, "%"), "density class": ("medium dense", None)}


def test_lists_become_tables_and_notes():
    rows = [{"name": f"r{i}", "value_kpa": i, "stats": {"min": 1, "mean": 2.5, "max": 4}} for i in range(80)]
    res = {"rows": rows, "warnings": ["check units"], "assumptions": ["drained"]}
    blocks = build_visuals("x", {}, ok(res))
    (table,) = by_type(blocks, "table")
    assert [c["unit"] for c in table["columns"]] == [None, "kPa", None]
    assert table["columns"][2]["label"] == "stats mean (range)" and table["rows"][0][2] == "2.5 (1–4)"
    assert len(table["rows"]) == MAX_TABLE_ROWS and table["truncated"] == 80 - MAX_TABLE_ROWS
    warn, info = by_type(blocks, "notes")
    assert (warn["tone"], warn["detail"]) == ("warning", False)
    assert (info["tone"], info["detail"]) == ("info", True)


def test_equal_length_arrays_become_xy_chart():
    res = {"strain [%]": [0.001, 0.01, 0.1, 1.0], "G/Gmax [-]": [1.0, 0.95, 0.7, 0.3]}
    (chart,) = by_type(build_visuals("curve", {}, ok(res)), "xy")
    assert chart["x"] == {"label": "strain", "unit": "%"}
    assert chart["series"] == [{"name": "G/Gmax", "x": res["strain [%]"], "y": res["G/Gmax [-]"]}]


def test_cpt_summary_plots_project_trace_with_sbt_bands(cpt_store):
    res = tool_registry.invoke_tool("get_cpt_summary", {"cpt_id": "CPT-03"})
    blocks = build_visuals("get_cpt_summary", {"cpt_id": "CPT-03"}, ok(res))
    (profile,) = by_type(blocks, "depth_profile")
    assert [t["title"] for t in profile["tracks"]] == ["qc", "fs", "u2"]
    qc = profile["tracks"][0]["series"][0]
    assert len(qc["depth"]) <= MAX_PROFILE_POINTS and "every" in profile["note"]   # 1400 points decimated
    data = synthetic_cpt(dz=0.01)
    z0 = qc["depth"][0]
    assert qc["value"][0] == pytest.approx(float(data.loc[data["z [m]"] == z0, "qc [MPa]"].iloc[0]))
    assert [(b["top"], b["bottom"]) for b in profile["bands"]] == \
        [(l["depth_from_m"], l["depth_to_m"]) for l in res["layering"]]
    (layering,) = [b for b in by_type(blocks, "table") if b["title"] == "Layering"]
    assert len(layering["rows"]) == len(res["layering"])
    # the trace is UI-only: the tool result the model sees stays compact
    assert "depth" not in json.dumps(res["layering"][0]).replace("depth_from_m", "").replace("depth_to_m", "")


def test_pile_capacity_shows_values_and_one_profile(monkeypatch):
    s = FakeStore({"a": ("SoilProfile", "KOP-1", load_fixture("groundhog_cpt_koppejan.csv"))})
    monkeypatch.setattr(T, "_store", lambda: s)
    args = {"cpt_id": "KOP-1", "method": "koppejan", "pile_type": "driven_closed_steel_pipe",
            "pile_diameter_m": 0.4, "pile_tip_depth_m": 16.5, "soil_layers": KOPPEJAN_LAYERS}
    res = tool_registry.invoke_tool("calculate_pile_capacity_from_cpt", args)
    blocks = build_visuals("calculate_pile_capacity_from_cpt", args, ok(res))
    metrics = {i["label"]: (i["value"], i["unit"]) for i in by_type(blocks, "metrics")[0]["items"]}
    assert metrics["ultimate total resistance"] == (res["ultimate_total_resistance_kn"], "kN")
    (profile,) = by_type(blocks, "depth_profile")
    assert profile["tracks"][0]["title"] == "qc" and "shaft resistance" in [t["title"] for t in profile["tracks"]]
    assert {"depth": 16.5, "label": "Pile tip"} in profile["markers"]
    assert max(profile["tracks"][0]["series"][0]["depth"]) <= 16.5 + 2.0
    shaft = next(t for t in profile["tracks"] if t["title"] == "shaft resistance")["series"][0]
    assert shaft["value"] == [r["shaft_resistance_kn"] for r in res["shaft_breakdown"]]


class _ScriptedProvider:
    """One tool call, then (if asked) a short explanation."""

    def __init__(self, call):
        self._call = call

    def is_loaded(self):
        return True

    def clear_cancel(self):
        pass

    def model_info(self):
        return {}

    def generate(self, messages, tools=None, **kw):
        if tools and not any(m.role.value == "tool" for m in messages):
            return ModelResponse(content="", tool_calls=[self._call], finish_reason="tool_calls")
        self.answer_prompt = messages
        return ModelResponse(content="The results are shown.", tool_calls=None, finish_reason="stop")

    def generate_stream(self, messages, tools=None, **kw):
        yield StreamChunk(delta_tool_calls=[self._call], finish_reason="tool_calls")

    def generate_answer_stream(self, messages, tools=None, **kw):
        self.answer_prompt = messages
        yield StreamChunk(delta_content="The results are shown.", finish_reason="stop")


def test_agent_streams_visuals_but_never_prompts_with_them(cpt_store):
    call = ToolCall(id="c1", function_name="get_cpt_summary", arguments={"cpt_id": "CPT-03"})
    provider = _ScriptedProvider(call)
    agent = GeoAIAgent(provider, tool_registry, max_tools=4)
    agent._explanations = "always"
    events = list(agent.run_stream("Explain CPT-03"))
    (result,) = [e for e in events if e.type == "tool_result"]
    assert by_type(result.visuals, "depth_profile")
    assert '"visuals"' in result.to_sse()
    prompt = "".join(m.content or "" for m in provider.answer_prompt)
    assert "depth_profile" not in prompt and "tracks" not in prompt

    response = agent.run("Explain CPT-03").to_dict()
    assert by_type(response["visuals"], "depth_profile")
