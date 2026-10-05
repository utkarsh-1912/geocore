import json

import core.geoai.tool_definitions  # noqa: F401  (registers the tools)
from core.geoai.model_provider import ModelProvider, ModelResponse, StreamChunk
from core.geoai.multi_agent import MultiAgentOrchestrator, ROLES, plan_request, verify_results
from core.geoai.tool_registry import tool_registry
from core.geoai.tool_selector import select_relevant_tools, tool_in_domains


class RecordingProvider(ModelProvider):
    """Answers every call with plain text and records the tool names and system prompt offered."""

    def __init__(self):
        self.offered, self.systems = [], []

    def _record(self, messages, tools):
        self.offered.append({t["function"]["name"] for t in tools or []})
        self.systems.append(messages[0].content)

    def generate(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        self._record(messages, tools)
        return ModelResponse(content="answer", tool_calls=None, finish_reason="stop", usage=None)

    def generate_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        self._record(messages, tools)
        yield StreamChunk(delta_content="answer", finish_reason="stop")

    def is_loaded(self):
        return True

    def model_info(self):
        return {"name": "recording"}


COMPOUND = "Classify the CPT with qc 5 MPa, then calculate bearing capacity of a 2 m footing"


def test_compound_request_is_planned_per_domain():
    steps = plan_request(COMPOUND)
    assert [s.role for s in steps] == ["site_investigation", "foundations"]
    assert "CPT" in steps[0].task and "bearing" in steps[1].task


def test_research_clause_gets_the_research_specialist():
    steps = plan_request("calculate bearing capacity of footing B=2 m and find literature on settlement limits")
    assert [s.role for s in steps] == ["foundations", "research"]


def test_single_topic_requests_are_not_multi_agent():
    for msg in ("What is bearing capacity?", "Calculate the bearing capacity of a 2 m footing", "hello", ""):
        assert len(plan_request(msg)) < 2


def test_domain_filter_restricts_offered_tools():
    tools = select_relevant_tools("classify cpt and bearing capacity of footing", max_tools=20,
                                  domains=ROLES["site_investigation"].domains)
    names = [t["function"]["name"] for t in tools]
    assert names and all(tool_in_domains(n, ROLES["site_investigation"].domains) for n in names)
    assert not any(tool_in_domains(n, ROLES["foundations"].domains) for n in names)


def test_specialists_see_only_their_tools_and_role():
    provider = RecordingProvider()
    orch = MultiAgentOrchestrator(provider, tool_registry)
    resp = orch.run(COMPOUND)
    assert len(provider.offered) == 2
    assert all(tool_in_domains(n, ROLES["site_investigation"].domains) for n in provider.offered[0])
    assert all(tool_in_domains(n, ROLES["foundations"].domains) for n in provider.offered[1])
    assert "site-investigation specialist" in provider.systems[0]
    assert "foundations specialist" in provider.systems[1]
    assert "**Site investigation**" in resp.response_text and "**Foundations**" in resp.response_text
    # no tool ran, so the verifier must say so rather than staying silent
    assert "**Checks**" in resp.response_text


def test_single_step_falls_through_to_plain_agent():
    provider = RecordingProvider()
    resp = MultiAgentOrchestrator(provider, tool_registry).run("What is bearing capacity?")
    assert resp.response_text == "answer"
    assert len(provider.offered) == 1


def test_stream_emits_plan_stages_and_one_combined_answer():
    provider = RecordingProvider()
    events = list(MultiAgentOrchestrator(provider, tool_registry).run_stream(COMPOUND))
    assert events[0].type == "plan"
    assert [s["role"] for s in json.loads(events[0].content)] == ["site_investigation", "foundations"]
    stages = [e.content for e in events if e.type == "stage" and e.content.startswith("agent:")]
    assert stages == ["agent:Site investigation", "agent:Foundations"]
    tokens = [e for e in events if e.type == "token"]
    assert len(tokens) == 1 and "**Foundations**" in tokens[0].content
    assert events[-1].type == "done" and sum(e.type == "done" for e in events) == 1


def test_verifier_reports_failed_tools():
    steps = plan_request(COMPOUND)
    failed = [{"name": "classify_cpt_soil_behavior", "result": {"status": "error", "error": "invalid CPT"}}]
    issues = verify_results(steps, [failed, []])
    assert any("invalid CPT" in i for i in issues)
    assert any("no calculation or retrieval" in i for i in issues)
