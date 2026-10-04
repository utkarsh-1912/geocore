"""
Chat reliability: turn outcomes are classified and traced, and a turn never ends blank.
"""
import json

import pytest

import core.geoai.tool_definitions  # noqa: F401  (registers canonical tools)
from core.geoai import turn_trace
from core.geoai.agent import AgentStreamEvent, GeoAIAgent
from core.geoai.model_provider import ModelProvider, ModelResponse, StreamChunk
from core.geoai.tool_registry import tool_registry


class _Provider(ModelProvider):
    def __init__(self, content):
        self.content = content

    def generate(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        return ModelResponse(content=self.content, tool_calls=None, finish_reason="stop")

    def generate_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        yield StreamChunk(delta_content=self.content, finish_reason="stop")

    def clear_cancel(self):
        pass

    def is_loaded(self):
        return True

    def model_info(self):
        return {"provider": "test", "model_path": "test.gguf", "chat_format": "native"}


@pytest.fixture(autouse=True)
def trace_file(tmp_path, monkeypatch):
    path = tmp_path / turn_trace.TRACE_FILENAME
    monkeypatch.setattr(turn_trace, "_trace_path", lambda: path)
    return path


def _ev(type_, **kw):
    return AgentStreamEvent(type=type_, **kw)


def test_classify_empty_turn():
    assert turn_trace.classify_turn("hello", [_ev("stage", content="thinking")]) == turn_trace.EMPTY_ANSWER
    assert turn_trace.classify_turn("hello", [_ev("token", content="  ")]) == turn_trace.EMPTY_ANSWER


def test_classify_raw_tool_markup_is_malformed_call():
    ev = [_ev("token", content='<tool_call>{"name": "x", "arguments": {')]
    assert turn_trace.classify_turn("calculate 5", ev) == turn_trace.MALFORMED_TOOL_CALL


def test_classify_calc_prompt_answered_in_prose():
    ev = [_ev("token", content="The capacity is about 300 kPa.")]
    assert turn_trace.classify_turn("Calculate bearing capacity for phi 30", ev) == turn_trace.NO_TOOL_CALL
    assert turn_trace.classify_turn("What is consolidation?", ev) == turn_trace.OK


def test_classify_tool_error_and_ok():
    start = _ev("tool_start", tool_name="t")
    bad = _ev("tool_result", tool_name="t", tool_result={"status": "error"})
    good = _ev("tool_result", tool_name="t", tool_result={"status": "success"})
    text = _ev("token", content="done")
    assert turn_trace.classify_turn("q", [start, bad, text]) == turn_trace.TOOL_ERROR
    assert turn_trace.classify_turn("q", [start, good, text]) == turn_trace.OK


def test_classify_exceptions():
    from core.geoai.model_provider import GenerationCancelled
    assert turn_trace.classify_turn("q", [], GenerationCancelled("GeoAI request stopped.")) == turn_trace.CANCELLED
    assert turn_trace.classify_turn("q", [], GenerationCancelled("exceeded the 600 s time limit.")) == turn_trace.TIMEOUT
    assert turn_trace.classify_turn("q", [], RuntimeError("boom")) == turn_trace.ERROR


def test_blank_model_output_gets_explicit_message_and_is_traced(trace_file):
    agent = GeoAIAgent(provider=_Provider(""), registry=tool_registry)
    events = list(agent.run_stream("calculate the thing"))
    text = "".join(e.content or "" for e in events if e.type == "token")
    assert text == turn_trace.EMPTY_ANSWER_MESSAGE
    assert events[-1].type == "done"
    entry = json.loads(trace_file.read_text().splitlines()[-1])
    assert entry["outcome"] == turn_trace.EMPTY_ANSWER


def test_normal_answer_is_untouched_and_traced_ok(trace_file):
    agent = GeoAIAgent(provider=_Provider("Consolidation is the gradual dissipation of excess pore pressure."),
                       registry=tool_registry)
    events = list(agent.run_stream("What is consolidation?"))
    text = "".join(e.content or "" for e in events if e.type == "token")
    assert "dissipation" in text and turn_trace.EMPTY_ANSWER_MESSAGE not in text
    assert json.loads(trace_file.read_text().splitlines()[-1])["outcome"] == turn_trace.OK
