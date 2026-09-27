# Author: Utkarsh Gupta
# License: GPL v3
"""
Unit tests for the deterministic GeoAI turn scorer (core/geoai/eval/scoring.py).
The scorer is the future GRPO reward, so every criterion is pinned here.
"""
import json

import pytest

import core.geoai.tool_definitions  # noqa: F401  (register canonical tools)
from core.geoai.eval import EvalExample, parse_completion, reward, score_turn
from core.geoai.eval.scoring import INVENTED_VALUE_CAP, extract_numbers, normalise_response
from core.geoai.model_provider import ModelResponse, ToolCall

GMAX = "calculate_gmax_from_shear_wave_velocity"


def _call(name, **args):
    return {"content": "", "tool_calls": [{"type": "function", "function": {"name": name, "arguments": args}}]}


@pytest.fixture
def gmax_example():
    return EvalExample(
        id="t-gmax", category="correct_request", expected_action="tool_call",
        messages=[{"role": "user", "content": "Calculate Gmax with Vs = 250 m/s and gamma = 19 kN/m3."}],
        expected_tool=GMAX, acceptable_tools=["gmax_shearwavevelocity"],
        expected_arguments={"Vs": 250.0, "gamma": 19.0}, provided_params=["Vs", "gamma"],
        expected_result={"Gmax": 121137.61467889908},
    )


@pytest.fixture
def missing_example():
    return EvalExample(
        id="t-missing", category="missing_data", expected_action="clarify",
        messages=[{"role": "user", "content": "Calculate Gmax with gamma = 19 kN/m3."}],
        expected_tool=GMAX, provided_params=["gamma"], missing_params=["Vs"],
        clarify_keywords=[["shear wave velocity", "Vs"]],
    )


# ---------------------------------------------------------------- tool calls
def test_perfect_tool_call_scores_one(gmax_example):
    sb = score_turn(gmax_example, _call(GMAX, Vs=250, gamma=19), execute=True)
    assert sb.passed and sb.total == pytest.approx(1.0)
    assert sb.action == sb.tool == sb.schema == sb.arguments == sb.no_invented == sb.execution == 1.0
    assert sb.predicted_action == "tool_call" and sb.predicted_tool == GMAX


def test_aliases_and_unit_strings_are_normalised_deterministically(gmax_example):
    # 820.2 ft/s = 250.0 m/s ; 120.95 pcf = 19.0 kN/m3 (converted by core.geoai.units via the schema)
    sb = score_turn(gmax_example, _call(GMAX, shear_wave_velocity="820.2 ft/s", unit_weight="120.95 pcf"))
    assert sb.schema == 1.0
    assert sb.arguments == 1.0
    assert sb.no_invented == 1.0


def test_wrong_value_partial_argument_credit(gmax_example):
    sb = score_turn(gmax_example, _call(GMAX, Vs=300, gamma=19))
    assert sb.arguments == pytest.approx(0.5)
    assert not sb.passed


def test_wrong_stated_value_is_strongly_penalised(gmax_example):
    """RL signal: a wrong value for a user-stated parameter must cost far more than format credit."""
    gold = score_turn(gmax_example, _call(GMAX, Vs=250, gamma=19)).total
    one_wrong = score_turn(gmax_example, _call(GMAX, Vs=300, gamma=19)).total
    all_wrong = score_turn(gmax_example, _call(GMAX, Vs=300, gamma=17)).total
    wrong_tool = score_turn(gmax_example, _call("calculate_earth_pressure_rankine", phi_eff=30)).total
    no_call = score_turn(gmax_example, "Please use the Gmax tool.").total
    assert gold == pytest.approx(1.0)
    assert gold - one_wrong >= 0.5
    assert gold > one_wrong > all_wrong > wrong_tool > no_call


def test_wrong_tool_and_equivalent_tool(gmax_example):
    wrong = score_turn(gmax_example, _call("calculate_earth_pressure_rankine", phi_eff=30))
    assert wrong.tool == 0.0 and wrong.arguments == 0.0
    equiv = score_turn(gmax_example, _call("gmax_shearwavevelocity", Vs=250, gamma=19))
    assert equiv.tool == 0.75 and equiv.arguments == 1.0


def test_hallucinated_tool(gmax_example):
    sb = score_turn(gmax_example, _call("calculate_gmax_magic", Vs=250, gamma=19))
    assert sb.hallucinated_tool and sb.schema == 0.0 and sb.tool == 0.0


def test_schema_violation_detected(gmax_example):
    sb = score_turn(gmax_example, _call(GMAX, Vs=250, gamma=45))  # gamma bound le=30
    assert sb.schema == 0.0
    assert any("schema" in r for r in sb.reasons)


def test_text_answer_when_tool_expected(gmax_example):
    sb = score_turn(gmax_example, "Gmax = rho * Vs^2 = 121 MPa.")
    assert sb.action == 0.0 and sb.tool == 0.0 and sb.arguments == 0.0


# ---------------------------------------------------------- invented values
def test_invented_parameter_in_missing_data_is_penalised(missing_example):
    sb = score_turn(missing_example, _call(GMAX, Vs=200, gamma=19))
    assert sb.action == 0.0
    assert sb.invented_params == ["Vs"]
    assert sb.no_invented == 0.0
    assert sb.clarification == 0.0
    assert sb.total <= INVENTED_VALUE_CAP


def test_extra_invented_optional_parameter(gmax_example):
    # g is optional (default 9.81); supplying an unstated non-default value is an invention
    sb = score_turn(gmax_example, _call(GMAX, Vs=250, gamma=19, g=9.5))
    assert sb.invented_params == ["g"] and sb.total <= INVENTED_VALUE_CAP
    # restating the schema default is harmless
    ok = score_turn(gmax_example, _call(GMAX, Vs=250, gamma=19, g=9.81))
    assert ok.invented_params == [] and ok.passed


def test_numeric_grounding_fallback_without_provided_params():
    ex = EvalExample(id="t-fallback", category="correct_request", expected_action="tool_call",
                     messages=[{"role": "user", "content": "Rankine Ka for a friction angle of 0.5236 rad"}],
                     expected_tool="calculate_earth_pressure_rankine", expected_arguments={"phi_eff": 30.0})
    assert score_turn(ex, _call("calculate_earth_pressure_rankine", phi_eff=30.0)).invented_params == []
    sb = score_turn(ex, _call("calculate_earth_pressure_rankine", phi_eff=30.0, top_angle=12))
    assert sb.invented_params == ["top_angle"]


def test_unknown_parameter_on_permissive_auto_schema():
    # Auto-registered Groundhog schemas use extra='allow'; the scorer still flags unknown keys.
    ex = EvalExample(id="t-nq", category="correct_request", expected_action="tool_call",
                     messages=[{"role": "user", "content": "Nq for friction angle 32 deg"}],
                     expected_tool="nq_frictionangle_sand", expected_arguments={"friction_angle": 32.0},
                     provided_params=["friction_angle"])
    sb = score_turn(ex, _call("nq_frictionangle_sand", friction_angle=32, bogus=3))
    assert sb.unknown_params == ["bogus"] and sb.schema == 0.0 and sb.no_invented == 0.0


# ---------------------------------------------------------- clarification
def test_clarification_keywords(missing_example):
    good = score_turn(missing_example, "Could you provide the shear wave velocity Vs in m/s? I won't assume it.")
    assert good.passed and good.clarification == 1.0
    vague = score_turn(missing_example, "Could you give me more details?")
    assert vague.action == 1.0 and vague.clarification == 0.0 and not vague.passed


def test_reject_expected_text_scored():
    ex = EvalExample(id="t-rej", category="tool_failure", expected_action="reject", acceptable_actions=["clarify"],
                     messages=[{"role": "user", "content": "Classify qc = -5 MPa, fs = 20 kPa at 3 m"}],
                     clarify_keywords=[["qc", "cone"], ["negative", "positive", "invalid", "must"]])
    sb = score_turn(ex, "The cone resistance qc cannot be negative; it must be positive. Please check the sensor zero.")
    assert sb.passed
    bad = score_turn(ex, _call("classify_cpt_soil_behavior", qc_mpa=-5, fs_kpa=20, depth=3))
    assert bad.action == 0.0 and not bad.passed


# ---------------------------------------------------------- unit traps
def test_convertible_unit_trap():
    ex = EvalExample(id="t-conv", category="wrong_units", expected_action="tool_call",
                     messages=[{"role": "user", "content": "Classify CPT: qc = 8500 kPa, fs = 42 kPa, depth 4.2 m"}],
                     expected_tool="classify_cpt_soil_behavior",
                     expected_arguments={"qc_mpa": 8.5, "fs_kpa": 42.0, "depth": 4.2},
                     provided_params=["qc_mpa", "fs_kpa", "depth"],
                     unit_trap={"param": "qc_mpa", "kind": "convertible", "given": "8500 kPa"})
    as_string = score_turn(ex, _call("classify_cpt_soil_behavior", qc_mpa="8500 kPa", fs_kpa=42, depth=4.2))
    converted = score_turn(ex, _call("classify_cpt_soil_behavior", qc_mpa=8.5, fs_kpa=42, depth=4.2))
    assert as_string.unit_trap == 1.0 and converted.unit_trap == 1.0 and converted.passed
    # Passing the raw kPa number into an MPa field fails the schema bound or the trap
    raw = score_turn(ex, _call("classify_cpt_soil_behavior", qc_mpa=85.0, fs_kpa=42, depth=4.2))
    assert raw.unit_trap == 0.0 and raw.arguments < 1.0


def test_dimension_mismatch_unit_trap():
    ex = EvalExample(id="t-dim", category="wrong_units", expected_action="clarify",
                     messages=[{"role": "user", "content": "Calculate Gmax with Vs = 300 m/s and gamma = 19 kPa."}],
                     expected_tool=GMAX, provided_params=["Vs"],
                     unit_trap={"param": "gamma", "kind": "dimension_mismatch", "given": "19 kPa"},
                     clarify_keywords=[["unit weight", "gamma"], ["unit", "kpa"]])
    flagged = score_turn(ex, "Unit mismatch: gamma = 19 kPa is a pressure; unit weight must be in kN/m3. Did you mean 19 kN/m3?")
    assert flagged.unit_trap == 1.0 and flagged.passed
    passed_on = score_turn(ex, _call(GMAX, Vs=300, gamma=19))
    assert passed_on.unit_trap == 0.0 and passed_on.action == 0.0


# ---------------------------------------------------------- final answers & caution
def test_final_answer_grounding_and_unit_conversion():
    ex = EvalExample(id="t-final", category="correct_request", expected_action="synthesize", turn_type="final_answer",
                     messages=[{"role": "user", "content": "Gmax for Vs 250 m/s, gamma 19 kN/m3"}],
                     expected_result_values={"Gmax": 121137.6}, metadata={"result_units": {"Gmax": "kPa"}})
    assert score_turn(ex, "Gmax = 121,138 kPa (calculated by Groundhog).").grounding == 1.0
    assert score_turn(ex, "Gmax is about 121.1 MPa based on the supplied inputs.").grounding == 1.0
    miss = score_turn(ex, "The shear modulus was calculated successfully.")
    assert miss.grounding == 0.0 and not miss.passed


def test_caution_violations():
    ex = EvalExample(id="t-safe", category="conflicting_data", expected_action="synthesize",
                     messages=[{"role": "user", "content": "Is my footing OK?"}])
    assert score_turn(ex, "Yes, this design is safe and you can proceed with construction now.").caution == 0.0
    doi = score_turn(ex, "See Smith (2014), doi:10.1016/j.geocomp.2014.05.001 for the full method description.")
    assert doi.caution == 0.0
    ok = score_turn(ex, "The calculated capacity depends on the supplied parameters; engineering judgement is required.")
    assert ok.caution == 1.0


# ---------------------------------------------------------- parsing / API
def test_parse_completion_formats():
    hermes = parse_completion('<tool_call>\n{"name": "x_tool", "arguments": {"a": 1}}\n</tool_call>')
    assert hermes.tool_calls[0].name == "x_tool" and hermes.tool_calls[0].arguments == {"a": 1}
    bare = parse_completion('{"name": "y_tool", "arguments": "{\\"b\\": 2}"}')
    assert bare.tool_calls[0].arguments == {"b": 2}
    broken = parse_completion("<tool_call>{not json}</tool_call>")
    assert broken.tool_calls[0].parse_error
    text = parse_completion("Please provide the friction angle.")
    assert text.tool_calls == [] and text.content.startswith("Please")


def test_model_response_and_raw_text_inputs_agree(gmax_example):
    mr = ModelResponse(content=None, tool_calls=[ToolCall(id="1", function_name=GMAX, arguments={"Vs": 250, "gamma": 19})],
                       finish_reason="tool_calls")
    raw = '<tool_call>{"name": "%s", "arguments": {"Vs": 250, "gamma": 19}}</tool_call>' % GMAX
    a, b = score_turn(gmax_example, mr), score_turn(gmax_example, raw)
    assert a.to_dict() == b.to_dict()
    assert normalise_response(mr).tool_calls[0].name == GMAX


def test_scorer_is_deterministic_and_dict_examples_work(gmax_example):
    d = json.loads(json.dumps(gmax_example.to_dict()))
    r1 = score_turn(d, _call(GMAX, Vs=250, gamma=18)).to_dict()
    r2 = score_turn(d, _call(GMAX, Vs=250, gamma=18)).to_dict()
    assert r1 == r2
    assert reward(d, _call(GMAX, Vs=250, gamma=19)) == pytest.approx(1.0)


def test_extract_numbers_handles_separators_and_scientific():
    nums = extract_numbers("k = 2.6 × 10^-4 m/s, Gmax = 155,841 kPa, e = 1e-3")
    vals = [v for v, _ in nums]
    assert any(abs(v - 2.6e-4) < 1e-12 for v in vals)
    assert 155841.0 in vals and 1e-3 in vals
