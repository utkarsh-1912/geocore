# Author: Utkarsh Gupta
# License: GPL v3
"""
AGENTS.md §28 milestone, end to end and deterministic (no LLM):

    user ("... using the current project") -> GeoAIAgent -> real tool selector offers tools
    -> (scripted) model emits a tool call -> real GeoAI Tool Registry validates it -> Groundhog
    calculates -> structured result with provenance goes back to the model -> grounded answer.

The model is a scripted ``ModelProvider`` that only (1) picks the tool and extracts arguments
from the user's words and (2) writes its answer from the tool message it is given - so every
number in the answer must have come from Groundhog through the registry. The project is the
deterministic synthetic project (``core.geoai.eval.synthetic_project``: CPT-01..03 + BH-01).

Oracle: Groundhog's ``KoppejanCalculation`` called directly on the same CPT (as in
tests/test_cpt_piles.py), not the LLM (§25).
"""
import json
import re
import warnings

import numpy as np
import pytest

import core.geoai.tool_definitions  # noqa: F401  (registers the curated tools)
from core.geoai.agent import GeoAIAgent
from core.geoai.eval import score_turn
from core.geoai.eval import synthetic_project as SP
from core.geoai.eval.example import EvalExample
from core.geoai.model_provider import MessageRole, ModelProvider, ModelResponse, ToolCall
from core.geoai.tool_registry import tool_registry

PILE = "calculate_pile_capacity_from_cpt"
QUESTION = ("Calculate the pile capacity at CPT-03 for a 0.6 m closed-ended driven steel pipe pile "
            "to 18 m using Koppejan")
QUESTION_NO_DIAMETER = ("Calculate the pile capacity at CPT-03 for a closed-ended driven steel pipe pile "
                        "to 18 m using Koppejan")


class ScriptedPileModel(ModelProvider):
    """
    Deterministic stand-in for the local SLM. Round 1: extracts the pile inputs from the user's
    words (only what is stated) and calls the pile tool if it was offered. Round 2: writes the
    answer from the tool message - quoting its numbers and provenance, or asking for the inputs
    the tool reported missing. It never computes or supplies a number itself.
    """

    def __init__(self, invent_diameter: bool = False):
        self.calls = []            # (messages, offered tool names)
        self.invent_diameter = invent_diameter

    def generate(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        offered = [t["function"]["name"] for t in (tools or [])]
        self.calls.append((list(messages), offered))
        tool_msgs = [m for m in messages if m.role == MessageRole.TOOL]
        if not tool_msgs:
            return self._decide(messages, offered)
        return ModelResponse(content=self._answer(json.loads(tool_msgs[-1].content)), tool_calls=None,
                             finish_reason="stop")

    def _decide(self, messages, offered):
        user = next(m.content for m in reversed(messages) if m.role == MessageRole.USER)
        if PILE not in offered:
            return ModelResponse(content="I do not have a suitable tool for this.", tool_calls=None,
                                 finish_reason="stop")
        args = {"cpt_id": re.search(r"CPT-\d+", user).group(0),
                "method": "Koppejan" if "koppejan" in user.lower() else None,
                "pile_type": "closed-ended steel pipe" if "closed-ended" in user else None}
        m = re.search(r"(\d+(?:\.\d+)?) m (?:closed|open|pile|diameter)", user)
        if m:
            args["pile_diameter_m"] = float(m.group(1))
        elif self.invent_diameter:
            args["pile_diameter_m"] = 0.5            # a "typical" value the user never gave
        tip = re.search(r"to (\d+(?:\.\d+)?) m", user)
        if tip:
            args["pile_tip_depth_m"] = float(tip.group(1))
        args = {k: v for k, v in args.items() if v is not None}
        return ModelResponse(content="", tool_calls=[ToolCall(id="call_1", function_name=PILE, arguments=args)],
                             finish_reason="tool_calls")

    @staticmethod
    def _answer(wrapper):
        if wrapper["status"] == "error":
            fields = re.findall(r"(\w+) \[(\w+)\] - ([^;.]+)", wrapper["error"])
            wanted = "; ".join(f"the {desc.strip()} ({unit})" for _, unit, desc in fields) or wrapper["error"]
            return (f"I could not run {wrapper['tool_name']}: it needs {wanted}, which you have not given. "
                    f"Could you provide it? I won't assume a value.")
        r = wrapper["result"]
        units = r["_provenance"]["output_units"]
        src = r["provenance"]["cpt_source"]
        return (f"Using {r['cpt_id']} ({r['method']} method, {r['groundhog_class'].rsplit('.', 1)[-1]}): "
                f"ultimate shaft resistance {r['ultimate_shaft_resistance_kn']} {units['ultimate_shaft_resistance_kn']}, "
                f"ultimate base resistance {r['ultimate_base_resistance_kn']} {units['ultimate_base_resistance_kn']}, "
                f"ultimate total resistance {r['ultimate_total_resistance_kn']} {units['ultimate_total_resistance_kn']}. "
                f"CPT data: {src['object_type']} '{src['object_name']}'. {r['scope_note']}")

    def generate_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        raise NotImplementedError

    def is_loaded(self):
        return True

    def model_info(self):
        return {"name": "scripted-pile-model"}


@pytest.fixture
def project():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with SP.loaded(SP.FIXTURE):
            yield {"project_context": SP.build_project_context()}


def _groundhog_koppejan_oracle():
    """Groundhog KoppejanCalculation run directly on CPT-03 (closed steel pipe: alpha_p 1, alpha_s 0.01)."""
    from groundhog.deepfoundations.axialcapacity.koppejan import KoppejanCalculation
    from core.geoai import cpt_pile_capacity as engine
    from core.geoai import project_cpt
    import core.geoai.tools_cpt_piles as T
    cpt = project_cpt.resolve_cpt("CPT-03", T._store())
    layering, _, _ = engine.build_layering("koppejan", cpt, None, SP.WATER_TABLE_M)
    layers = layering[["Depth from [m]", "Depth to [m]"]].assign(**{"Total unit weight [kN/m3]": 18.5})
    calc = KoppejanCalculation(depth=np.asarray(cpt.data["depth_m"]), qc=np.asarray(cpt.data["qc_mpa"]),
                               diameter=0.6, penetration=18.0)
    calc.set_layer_properties(layer_data=layers.reset_index(drop=True), waterlevel=SP.WATER_TABLE_M)
    calc.calculate_side_friction(alpha_s=0.01)
    calc.calculate_base_resistance(alpha_p=1.0)
    return round(float(calc.Frs), 1), round(float(calc.Frb), 1)


def test_milestone_pile_capacity_from_project_cpt(project):
    model = ScriptedPileModel()
    agent = GeoAIAgent(model, tool_registry)
    response = agent.run(QUESTION, project)

    # 1. the real selector offered the pile tool to the model
    _, offered = model.calls[0]
    assert PILE in offered and len(offered) <= agent._max_tools
    # the model saw the project context the system prompt builds
    assert SP.PROJECT_NAME in model.calls[0][0][0].content

    # 2. the registry validated (synonyms -> canonical) and Groundhog ran
    assert [t["name"] for t in response.tools_used] == [PILE]
    wrapper = response.tools_used[0]["result"]
    assert wrapper["status"] == "success", wrapper
    res = wrapper["result"]
    assert res["cpt_id"] == "CPT-03" and res["method"] == "koppejan"
    assert res["pile"]["type"] == "driven_closed_steel_pipe" and res["pile"]["diameter_m"] == 0.6
    assert res["groundhog_class"].endswith("KoppejanCalculation")
    rs, rb = _groundhog_koppejan_oracle()
    assert res["ultimate_shaft_resistance_kn"] == rs and res["ultimate_base_resistance_kn"] == rb
    assert res["ultimate_total_resistance_kn"] == pytest.approx(rs + rb, abs=0.11)

    # 3. the structured result with provenance was passed back to the model
    tool_msgs = [m for m in model.calls[1][0] if m.role == MessageRole.TOOL]
    assert len(tool_msgs) == 1 and tool_msgs[0].name == PILE
    passed = json.loads(tool_msgs[0].content)["result"]
    assert passed["provenance"]["cpt_source"]["object_name"] == "CPT-03.xlsx"
    assert passed["_provenance"]["tool_name"] == PILE and passed["_provenance"]["output_units"][
        "ultimate_total_resistance_kn"] == "kN"

    # 4. grounded final answer: Groundhog numbers, CPT id, method and units
    text = response.response_text
    assert response.finish_reason == "complete"
    for value in (rs, rb, res["ultimate_total_resistance_kn"]):
        assert f"{value} kN" in text
    assert "CPT-03" in text and "koppejan" in text.lower() and "CPT-03.xlsx" in text
    assert " is safe" not in text.lower()
    # 5. the calculation was recorded in project memory with its provenance
    history = project["project_context"].get_calculation_history()
    assert history and history[-1].tool_name == PILE
    # 6. the deterministic scorer agrees the answer is grounded
    final = EvalExample(id="e2e", category="correct_request", expected_action="synthesize",
                        turn_type="final_answer", messages=[{"role": "user", "content": QUESTION}],
                        expected_result_values={"Rs": rs, "Rb": rb}, metadata={"result_units": {"Rs": "kN", "Rb": "kN"}},
                        required_mentions=[["cpt-03"], ["koppejan"]])
    assert score_turn(final, {"content": text}).passed


def test_missing_diameter_ends_in_clarification_not_a_value(project):
    model = ScriptedPileModel()
    agent = GeoAIAgent(model, tool_registry)
    response = agent.run(QUESTION_NO_DIAMETER, project)

    assert PILE in model.calls[0][1]
    call = response.tools_used[0]
    assert "pile_diameter_m" not in call["arguments"]
    wrapper = call["result"]
    assert wrapper["status"] == "error"
    assert "pile_diameter_m [m]" in wrapper["error"] and "do not assume" in wrapper["error"]
    # the structured missing-parameter error was fed back to the model ...
    tool_msgs = [m for m in model.calls[1][0] if m.role == MessageRole.TOOL]
    assert "pile_diameter_m" in json.loads(tool_msgs[0].content)["error"]
    # ... and the flow ends with a question for the diameter, never a capacity
    text = response.response_text
    assert response.finish_reason == "complete" and "?" in text and "diameter" in text.lower()
    assert "kN" not in text and not re.search(r"\b0\.\d+ m\b", text)
    assert project["project_context"].get_calculation_history() == []
    clarify = EvalExample(id="e2e-missing", category="missing_data", expected_action="clarify",
                          messages=[{"role": "user", "content": QUESTION_NO_DIAMETER}], expected_tool=PILE,
                          missing_params=["pile_diameter_m"], clarify_keywords=[["diameter"]])
    assert score_turn(clarify, {"content": text}).passed


def test_invented_diameter_is_not_executed(project):
    """A model that fills in a 'typical' diameter is stopped before the registry (§5, §17)."""
    model = ScriptedPileModel(invent_diameter=True)
    agent = GeoAIAgent(model, tool_registry)
    response = agent.run(QUESTION_NO_DIAMETER, project)
    assert response.finish_reason == "clarification" and response.tools_used == []
    assert "diameter" in response.response_text.lower()
    assert len(model.calls) == 1
