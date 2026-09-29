"""
Compact model-facing tool schemas (AGENTS.md §7, §14, §16, §23, §25).

The model is offered a compact rendering of each tool schema (tool_selector.format_tools_compact)
to cut prompt-processing time on CPU; the registry still validates every call against the full
schema, and tool retrieval still ranks on cards built from the full schema.
"""
import json

import pytest

from core.registry import registry  # noqa: F401  (populates auto-registered Groundhog tools)
import core.geoai.tool_definitions  # noqa: F401  (registers curated tools)
import core.geoai.model_config as mc
import core.geoai.tool_selector as ts
from core.geoai.agent import GeoAIAgent
from core.geoai.exceptions import GeoAIValidationError
from core.geoai.heuristic_provider import HeuristicProvider
from core.geoai.slm_schema_generator import generate_openai_tool_definitions
from core.geoai.tool_registry import tool_registry

#: Largest model-facing schemas before compaction (Qwen3 tokens: 1,537 / 1,508 / 1,432 / 1,194).
BIG_TOOLS = ("calculate_foundation_settlement", "calculate_shallow_foundation_capacity",
             "pcpt_normalisations", "calculate_pile_capacity_from_cpt", "unitskinfriction_clay_almhamre")
#: Keys only the registry needs; none may reach the model in compact form.
DROPPED_KEYS = {"title", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "anyOf", "$defs",
                "$ref", "unit", "additionalProperties", "examples"}


@pytest.fixture(scope="module")
def defs():
    return {d["function"]["name"]: d for d in generate_openai_tool_definitions()}


def _keys(obj, out=None):
    out = set() if out is None else out
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.add(k)
            if k == "properties" and isinstance(v, dict):   # property *names* are not schema keywords
                for prop in v.values():
                    _keys(prop, out)
            else:
                _keys(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _keys(v, out)
    return out


def _compact(defs, name):
    return ts.format_tools_compact([defs[name]])[0]


# ---------------------------------------------------------------- renderer

def test_compact_rendering_is_deterministic(defs):
    first = json.dumps(ts.format_tools_compact(list(defs.values())))
    assert json.dumps(ts.format_tools_compact(list(defs.values()))) == first


def test_keeps_name_required_types_enums_and_units(defs):
    full = defs["calculate_pile_capacity_from_cpt"]["function"]
    tool = _compact(defs, "calculate_pile_capacity_from_cpt")
    fn = tool["function"]
    assert tool["type"] == "function" and fn["name"] == "calculate_pile_capacity_from_cpt"
    params = fn["parameters"]
    assert params["type"] == "object"
    assert params["required"] == full["parameters"]["required"]
    props = params["properties"]
    assert set(props) == set(full["parameters"]["properties"])      # nothing hidden from this tool
    assert props["method"]["enum"] == ["lcpc", "koppejan", "debeer"]
    assert "cfa" in props["pile_type"]["enum"]
    assert props["open_end_condition"] == {"type": "string", "enum": ["coring", "plugged"],
                                           "description": props["open_end_condition"]["description"]}
    assert props["pile_diameter_m"]["type"] == "number"
    assert props["pile_diameter_m"]["description"].endswith("[m]")
    assert props["wall_thickness_mm"]["description"].endswith("[mm]")
    # $ref'd array items are inlined in compact form, with their own required list.
    layer = props["soil_layers"]["items"]
    assert layer["required"] == ["depth_from_m", "depth_to_m"]
    assert layer["properties"]["total_unit_weight_kn_m3"]["description"].endswith("[kN/m3]")


def test_drops_bounds_titles_and_registry_only_keys(defs):
    for name, d in defs.items():
        keys = _keys(ts.format_tools_compact([d])[0])
        assert not keys & DROPPED_KEYS, (name, keys & DROPPED_KEYS)


def test_groundhog_descriptions_lose_latex_ranges_and_bracket_units(defs):
    props = _compact(defs, "unitskinfriction_clay_almhamre")["function"]["parameters"]["properties"]
    assert props["sigma_vo_eff"]["description"] == "Vertical effective stress [kPa]"
    assert props["qt"]["description"] == "Total cone resistance (q_t) [MPa]"    # plain symbols are kept
    text = json.dumps(props)
    assert "Suggested range" not in text and "\\\\" not in text and "optional, default" not in text


@pytest.mark.parametrize("text, unit, max_words, expected", [
    ("Depth at which it is calculated (z) [m] - Suggested range: depth >= 0.0", "m", 12,
     "Depth at which it is calculated (z) [m]"),
    ("Vertical effective stress (\\sigma_{vo}^{\\prime}) [kPa]", "kPa", 12, "Vertical effective stress [kPa]"),
    ("Multiplier on the equation () [-] (optional, default= 1.0)", "", 12, "Multiplier on the equation"),
    ("Effective friction angle phi' of the soil below the base (drained; method range 20-50 deg)", "deg", 12,
     "Effective friction angle phi' of the soil below the base [deg]"),
    ("First sentence here. Second sentence is dropped.", "", 12, "First sentence here"),
    ("", "kN", 12, "[kN]"),
])
def test_short_description(text, unit, max_words, expected):
    assert ts._short_description(text, unit, max_words) == expected


def test_description_word_caps(defs):
    for d in defs.values():
        params = ts.format_tools_compact([d])[0]["function"]["parameters"]
        required = set(params.get("required", []))
        for k, p in params["properties"].items():
            words = p.get("description", "").split(" [")[0].split()
            cap = ts.COMPACT_REQUIRED_WORDS if k in required else ts.COMPACT_OPTIONAL_WORDS
            assert len(words) <= cap, (d["function"]["name"], k, words)


def test_overflow_optionals_are_named_not_hidden(defs):
    full = defs["vs_cpt_andrus"]["function"]["parameters"]
    fn = _compact(defs, "vs_cpt_andrus")["function"]
    props = fn["parameters"]["properties"]
    extra = ts.overflow_optionals(full)
    assert extra and len(props) + len(extra) == len(full["properties"])
    assert {"qt", "depth", "ic"} <= set(props)                     # required always rendered in full
    assert not set(extra) & set(props)
    assert "Other optional inputs (defaults):" in fn["description"]
    assert all(k in fn["description"] for k in extra)
    assert "tertiary_z_exponent=0.099" in fn["description"]


def test_every_input_reaches_the_model_for_every_tool(defs):
    for name, d in defs.items():
        fn = ts.format_tools_compact([d])[0]["function"]
        full_props = set((d["function"]["parameters"].get("properties") or {}))
        shown = set(fn["parameters"]["properties"])
        assert shown <= full_props
        assert all(k in fn["description"] for k in full_props - shown), name


def test_compact_schemas_fit_budgets(defs):
    total_full = total_compact = 0
    for name, d in defs.items():
        full = len(json.dumps(ts.format_tools_for_prompt([d])[0]))
        compact = len(json.dumps(ts.format_tools_compact([d])[0]))
        total_full += full
        total_compact += compact
        assert compact <= full, name
    assert total_compact <= 0.62 * total_full        # ~0.52 in Qwen3 tokens (JSON punctuation is cheap)
    for name in BIG_TOOLS:
        compact = len(json.dumps(_compact(defs, name)))
        full = len(json.dumps(ts.format_tools_for_prompt([defs[name]])[0]))
        assert compact <= 0.7 * full, (name, compact, full)
        assert ts.schema_tokens(_compact(defs, name)) <= 900, name


# ---------------------------------------------------------------- selection / retrieval

@pytest.mark.parametrize("query", [
    "Calculate the pile capacity at CPT-03 with LCPC for a 0.6 m driven precast pile to 15 m",
    "Bearing capacity of a 2 m square footing on sand with phi' = 32 deg",
    "Shear wave velocity from the CPT with qt = 5 MPa",
])
def test_ranking_is_identical_with_compact_schemas(query):
    names = [t["function"]["name"] for t in ts.select_relevant_tools(query, max_tools=5)]
    compact = ts.select_relevant_tools(query, max_tools=5, compact=True)
    assert [t["function"]["name"] for t in compact] == names
    assert all("minimum" not in json.dumps(t) for t in compact)


def test_retrieval_cards_use_full_schema():
    index = ts._index()
    ts.select_relevant_tools("warm up", max_tools=5, compact=True)
    # Cards are built from the full definitions; the compact form is only a cached rendering.
    assert "maximum" in json.dumps(index.definitions["calculate_pile_capacity_from_cpt"])
    assert index.prompt_tool("calculate_pile_capacity_from_cpt") == ts.format_tools_for_prompt(
        [index.definitions["calculate_pile_capacity_from_cpt"]])[0]
    assert index.prompt_tool("calculate_pile_capacity_from_cpt", ts.format_tools_compact) == ts.format_tools_compact(
        [index.definitions["calculate_pile_capacity_from_cpt"]])[0]


# ---------------------------------------------------------------- validation unchanged

def test_registry_still_rejects_unknown_keys_and_out_of_range_values(defs):
    # Bounds are not shown to the model any more, so the registry must keep enforcing them.
    assert "maximum" not in json.dumps(_compact(defs, "nq_frictionangle_sand"))
    with pytest.raises(GeoAIValidationError, match="less than or equal to 50"):
        tool_registry.invoke_tool("nq_frictionangle_sand", {"friction_angle": 80})
    with pytest.raises(GeoAIValidationError, match="unknown parameter"):
        tool_registry.invoke_tool("nq_frictionangle_sand", {"friction_angle": 32, "bogus": 1})
    with pytest.raises(GeoAIValidationError, match="less than or equal to 60"):
        tool_registry.invoke_tool("calculate_earth_pressure_rankine", {"phi_eff": 95})
    assert "Nq" in json.dumps(tool_registry.invoke_tool("nq_frictionangle_sand", {"friction_angle": 32}))


# ---------------------------------------------------------------- config switch

@pytest.fixture
def clean_config(monkeypatch, tmp_path):
    monkeypatch.delenv("GEOAI_COMPACT_SCHEMAS", raising=False)
    monkeypatch.setattr(mc, "get_config_dir", lambda: tmp_path)
    return monkeypatch


def test_config_default(clean_config):
    assert mc.load_config().compact_tool_schemas is mc.COMPACT_TOOL_SCHEMAS_DEFAULT
    assert mc.GeoAIModelConfig().compact_tool_schemas is mc.COMPACT_TOOL_SCHEMAS_DEFAULT


@pytest.mark.parametrize("value, expected", [("1", True), ("true", True), ("on", True),
                                             ("0", False), ("false", False), ("off", False)])
def test_config_env_override(clean_config, value, expected):
    clean_config.setenv("GEOAI_COMPACT_SCHEMAS", value)
    assert mc.load_config().compact_tool_schemas is expected
    assert mc.GeoAIModelConfig().compact_tool_schemas is expected


def test_env_overrides_saved_config(clean_config, tmp_path):
    cfg = mc.GeoAIModelConfig()
    cfg.compact_tool_schemas = not mc.COMPACT_TOOL_SCHEMAS_DEFAULT
    mc.save_config(cfg)
    assert mc.load_config().compact_tool_schemas is (not mc.COMPACT_TOOL_SCHEMAS_DEFAULT)
    clean_config.setenv("GEOAI_COMPACT_SCHEMAS", "1" if mc.COMPACT_TOOL_SCHEMAS_DEFAULT else "0")
    assert mc.load_config().compact_tool_schemas is mc.COMPACT_TOOL_SCHEMAS_DEFAULT


@pytest.mark.parametrize("value", ["1", "0"])
def test_agent_offers_schemas_per_switch(clean_config, value):
    clean_config.setenv("GEOAI_COMPACT_SCHEMAS", value)
    agent = GeoAIAgent(HeuristicProvider(), tool_registry, max_tools=3)
    _, tools = agent._build_messages("Calculate the bearing capacity of a strip footing on clay with su = 50 kPa")
    assert tools
    has_bounds = any("minimum" in json.dumps(t) or "maximum" in json.dumps(t) for t in tools)
    assert has_bounds is (value == "0")
