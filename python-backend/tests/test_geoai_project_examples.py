# Author: Utkarsh Gupta
# License: GPL v3
"""
Training / eval examples for the project-data GeoAI tools (core/geoai/training/project_examples.py)
and the deterministic synthetic project they run against (core/geoai/eval/synthetic_project.py):
fixture isolation, validity by construction (every expected call executes through the registry
against the fixture, every stated value is in the prompt), scorer agreement, multi-step
trajectories, and runner support for later trajectory steps.
"""
import json
import warnings

import pytest

from core.geoai.eval import score_turn
from core.geoai.eval import synthetic_project as SP
from core.geoai.eval.scoring import (_grounding_text, default_registry, extract_numbers, field_unit,
                                     parse_completion, value_grounded, values_match)
from core.geoai.training.project_examples import PROJECT_TOOLS
from core.geoai.training.scaleup import build_dataset

warnings.filterwarnings("ignore")
PILE = "calculate_pile_capacity_from_cpt"


@pytest.fixture(scope="module")
def generated():
    return build_dataset(seed=11, per_tool=6, include_base=False)


# ------------------------------------------------------------------ synthetic project
def test_fixture_is_isolated_and_restored():
    import core.geoai.project_soil as project_soil
    import core.geoai.tools_cpt_piles as T
    before = (T._store, project_soil.load_project_context)
    reg = default_registry()
    with SP.loaded(SP.FIXTURE):
        listing = reg.invoke_tool("list_project_cpts", {})
        assert [c["cpt_id"] for c in listing["cpts"]] == ["CPT-01", "CPT-02", "CPT-03"]
        assert [c["depth_range_m"][1] for c in listing["cpts"]] == [22.0, 15.0, 26.0]
        # CPT-02 is stored with qc in kPa: converted deterministically to MPa
        s = reg.invoke_tool("get_cpt_summary", {"cpt_id": "CPT-02"})
        assert s["provenance"]["source"]["columns"]["qc"] == "qc [kPa]" and s["layering"][0]["qc_mpa"]["mean"] < 20
        with SP.loaded(SP.EMPTY):
            assert reg.invoke_tool("list_project_cpts", {})["count"] == 0
        assert reg.invoke_tool("list_project_cpts", {})["count"] == 3
    assert (T._store, project_soil.load_project_context) == before
    assert SP.build_state_manager()._path is None      # never resolved -> never saved to the workspace


def test_project_context_is_what_the_system_prompt_shows():
    from core.geoai.system_prompt import build_system_prompt
    text = SP.compact_context()
    assert text == SP.build_project_context().get_compact_context_string()
    assert "Soft clay" in text and "2.0 m below ground surface" in text
    assert text in build_system_prompt({"project_context": text})
    assert text in build_system_prompt({"project_context": SP.build_project_context()})


# ------------------------------------------------------------------ generated examples
def test_generation_deterministic_and_covers_tools_and_categories(generated):
    examples, drafts, report = generated
    again, _, _ = build_dataset(seed=11, per_tool=6, include_base=False)
    assert [e.to_dict() for e in examples] == [e.to_dict() for e in again]
    assert not report.dropped
    assert {e.category for e in examples} == {"correct_request", "missing_data", "wrong_units", "ambiguous_request",
                                              "conflicting_data", "tool_failure"}
    assert {e.expected_tool for e in examples if e.turn_type == "decision"} >= set(PROJECT_TOOLS)
    assert all(e.metadata.get("project_fixture") in SP.FIXTURES for e in examples)
    project = [e for e in examples if e.metadata["project_fixture"] == SP.FIXTURE]
    assert project and all(e.context == {"project_context": SP.compact_context()} for e in project)
    # multi-turn trajectory: list -> summary -> pile capacity -> grounded answer
    multi = [e for e in examples if e.group.startswith("correct_request|pile_multiturn|")]
    parent = next(e for e in multi if e.turn_type == "decision" and len(e.messages) == 1)
    steps = sorted((e for e in multi if e.metadata.get("parent_id") == parent.id), key=lambda e: len(e.messages))
    assert [e.expected_tool for e in [parent] + steps[:2]] == ["list_project_cpts", "get_cpt_summary", PILE]
    final = steps[-1]
    assert final.turn_type == "final_answer" and len(final.messages) == 7
    assert set(final.expected_result_values) == {"ultimate_shaft_resistance_kn", "ultimate_base_resistance_kn",
                                                 "ultimate_total_resistance_kn"}
    assert {e.split for e in [parent] + steps} == {parent.split}


def _call_for(e, by_id):
    d = by_id.get(e.id)
    if d is not None and d.target_call:
        return d.target_call
    parsed = parse_completion(e.reference_response or "")
    return {"name": parsed.tool_calls[0].name, "arguments": parsed.tool_calls[0].arguments} if parsed.tool_calls else None


def test_every_expected_call_executes_against_the_fixture(generated):
    examples, drafts, _ = generated
    reg = default_registry()
    by_id = {d.example.id: d for d in drafts}
    checked = 0
    for e in examples:
        if e.turn_type != "decision" or e.expected_action != "tool_call" or not e.expected_result:
            continue
        call = _call_for(e, by_id)
        with SP.loaded(e.metadata["project_fixture"]):
            res = reg.invoke_tool(call["name"], dict(call["arguments"]))
        for k, v in e.expected_result.items():
            assert values_match(v, res[k], rel_tol=1e-9), (e.id, k)
        checked += 1
    assert checked >= 20


def test_stated_values_are_in_the_prompt_and_clarifications_name_the_input(generated):
    examples, _, _ = generated
    reg = default_registry()
    for e in examples:
        if e.turn_type == "decision" and e.expected_arguments:
            nums = extract_numbers(_grounding_text(e))
            model = reg.get_tool(e.expected_tool).input_model
            for k, v in e.expected_arguments.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    assert value_grounded(v, nums, field_unit(model.model_fields[k])), (e.id, k, v, e.user_prompt)
        if e.category == "missing_data":
            assert e.expected_action == "clarify" and e.missing_params[0] not in e.provided_params
            assert any(w in e.reference_response.lower() for w in e.clarify_keywords[0])


def test_reference_behaviour_passes_scorer_with_execution(generated):
    examples, drafts, _ = generated
    by_id = {d.example.id: d for d in drafts}
    failures = []
    for e in examples:
        call = _call_for(e, by_id) if e.turn_type == "decision" and e.expected_action == "tool_call" else None
        resp = {"content": "", "tool_calls": [{"function": call}]} if call else {"content": e.reference_response}
        sb = score_turn(e, resp, execute=True)          # loads the example's project fixture
        if not sb.passed:
            failures.append((e.id, sb.reasons))
    assert not failures, failures[:5]


def test_sft_trajectories_offer_every_called_tool(generated):
    from core.geoai.training.scaleup import _cached_tool_definitions, sft_record
    from core.geoai.slm_schema_generator import generate_openai_tool_definitions
    _, drafts, _ = generated
    multi = [d for d in drafts if d.example.group.startswith("correct_request|pile_multiturn|")][:1]
    with _cached_tool_definitions():
        defs = {t["function"]["name"]: t for t in generate_openai_tool_definitions()}
        rec = sft_record(multi[0], defs)
    roles = [m["role"] for m in rec["messages"]]
    assert roles == ["system", "user", "assistant", "tool", "assistant", "tool", "assistant", "tool", "assistant"]
    offered = {t["function"]["name"] for t in rec["tools"]}
    assert {"list_project_cpts", "get_cpt_summary", PILE} <= offered
    assert SP.compact_context() in rec["messages"][0]["content"]


# ------------------------------------------------------------------ runner
def test_runner_judges_later_trajectory_steps_with_their_prefix(generated):
    from core.geoai.eval.runner import EvalRegistry, RecordingProvider, run_example
    from core.geoai.model_provider import MessageRole, ModelProvider, ModelResponse, ToolCall
    examples, _, _ = generated
    step = next(e for e in examples if e.metadata.get("step") == 3 and e.expected_tool == PILE)
    target = parse_completion(step.reference_response).tool_calls[0]

    class Scripted(ModelProvider):
        seen = None

        def generate(self, messages, tools=None, temperature=0.1, max_tokens=1024):
            Scripted.seen = (messages, [t["function"]["name"] for t in tools or []])
            return ModelResponse(content="", finish_reason="tool_calls",
                                 tool_calls=[ToolCall(id="c", function_name=target.name, arguments=target.arguments)])

        def generate_stream(self, *a, **k):
            raise NotImplementedError

        def is_loaded(self):
            return True

        def model_info(self):
            return {}

    rec = run_example(step, RecordingProvider(Scripted()), EvalRegistry(default_registry()), mode="agent")
    messages, offered = Scripted.seen
    assert [m.role for m in messages][:2] == [MessageRole.SYSTEM, MessageRole.USER]
    assert sum(m.role == MessageRole.TOOL for m in messages) == 2           # list + summary results in the prefix
    assert SP.PROJECT_NAME in messages[0].content and PILE in offered
    assert rec["error"] is None and rec["score"]["passed"] and rec["score"]["execution"] == 1.0, rec["score"]["reasons"]
