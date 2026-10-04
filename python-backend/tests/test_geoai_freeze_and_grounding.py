"""
Regression tests for the "0.95 -> Dr = 1.39" conversation and the GeoAI freeze:

* tool calls carrying numbers the user never gave are not executed (AGENTS.md §5, §17);
* the post-tool answer keeps the offered tools (prompt-cache reuse) and never ends empty;
* a request can be cancelled, and unloading never blocks the lifecycle lock.
"""
import threading
import time

import pytest

import core.geoai.tool_definitions  # noqa: F401  (registers canonical tools)
from core.geoai.agent import GeoAIAgent
from core.geoai.argument_grounding import missing_inputs_message, ungrounded_arguments
from core.geoai.lifecycle import ModelLifecycleManager
from core.geoai.llama_cpp_provider import LlamaCppProvider
from core.geoai.model_config import GeoAIModelConfig
from core.geoai.model_provider import (
    GenerationCancelled,
    ModelProvider,
    ModelResponse,
    StreamChunk,
    ToolCall,
)
from core.geoai.tool_registry import tool_registry

BALDI = "relativedensity_ncsand_baldi"
# What Qwen2.5-1.5B produced after the user answered "0.95": qc/sigma_vo_eff were invented.
INVENTED_BALDI_ARGS = {"qc": 120.0, "sigma_vo_eff": 400.0, "coefficient_0": 157.0,
                       "coefficient_1": 0.55, "coefficient_2": 2.41}


class ScriptedProvider(ModelProvider):
    """Decision turn from ``decision``; the answer turn streams ``answer`` chunks."""

    def __init__(self, decision, answer=("",)):
        self.decision = decision
        self.answer = list(answer)
        self.answer_tools = "unset"
        self.cleared = 0

    def generate(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        return self.decision

    def generate_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        d = self.decision
        yield StreamChunk(delta_content=d.content, delta_tool_calls=d.tool_calls, finish_reason=d.finish_reason)

    def generate_answer_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        self.answer_tools = tools
        for text in self.answer:
            yield StreamChunk(delta_content=text)

    def clear_cancel(self):
        self.cleared += 1

    def is_loaded(self):
        return True

    def model_info(self):
        return {"provider": "scripted"}


def _baldi_call(args):
    return ModelResponse(content=None, tool_calls=[ToolCall(id="c1", function_name=BALDI, arguments=args)],
                         finish_reason="tool_calls")


# --- argument grounding ------------------------------------------------------------------

def test_invented_inputs_are_detected_and_defaults_are_not():
    model = tool_registry.get_tool(BALDI).input_model
    assert ungrounded_arguments(model, INVENTED_BALDI_ARGS, "0.95 explain relative density") == ["qc", "sigma_vo_eff"]


def test_stated_inputs_are_grounded_including_unit_conversion():
    model = tool_registry.get_tool(BALDI).input_model
    text = "qc = 120 MPa, vertical effective stress 0.4 MPa"
    assert ungrounded_arguments(model, INVENTED_BALDI_ARGS, text) == []


def test_percent_is_grounded_as_fraction():
    model = tool_registry.get_tool("relativedensity_categories").input_model
    assert ungrounded_arguments(model, {"relative_density": 0.95}, "Dr is 95 %") == []


def test_missing_inputs_message_is_plain_text_with_units():
    model = tool_registry.get_tool(BALDI).input_model
    msg = missing_inputs_message(BALDI, model, ["qc", "sigma_vo_eff"])
    assert "`qc` [MPa]" in msg and "`sigma_vo_eff` [kPa]" in msg
    assert "<span" not in msg
    assert "suggested range" in msg


# --- agent -------------------------------------------------------------------------------

def test_stream_asks_instead_of_running_tool_with_invented_inputs():
    provider = ScriptedProvider(_baldi_call(INVENTED_BALDI_ARGS))
    agent = GeoAIAgent(provider, tool_registry, max_tools=5)
    history = [{"role": "user", "content": "relativedensity"},
               {"role": "assistant", "content": "The relative density is typically 0.0 <= Dr <= 1.0."}]

    events = list(agent.run_stream("0.95", history=history))

    assert [e.type for e in events] == ["stage", "stage", "token", "done"]
    assert "qc" in events[2].content and "sigma_vo_eff" in events[2].content
    assert provider.cleared == 1


def test_run_asks_instead_of_running_tool_with_invented_inputs():
    agent = GeoAIAgent(ScriptedProvider(_baldi_call(INVENTED_BALDI_ARGS)), tool_registry, max_tools=5)
    resp = agent.run("0.95")
    assert resp.finish_reason == "clarification"
    assert resp.tools_used == []


def test_grounded_call_runs_and_answer_keeps_offered_tools():
    args = {"qc": 12.0, "sigma_vo_eff": 100.0}
    provider = ScriptedProvider(_baldi_call(args), answer=["The relative density is high."])
    agent = GeoAIAgent(provider, tool_registry, max_tools=5)

    events = list(agent.run_stream("Relative density from Baldi for qc = 12 MPa and sigma'vo = 100 kPa"))

    types = [e.type for e in events]
    assert types[:4] == ["stage", "stage", "tool_start", "tool_result"] and types[-1] == "done"
    assert events[3].tool_result["status"] == "success"
    # Same tool block as the decision turn, so llama.cpp can reuse the evaluated prompt.
    assert provider.answer_tools and any(t["function"]["name"] == BALDI for t in provider.answer_tools)


def test_empty_explanation_falls_back_to_deterministic_result():
    provider = ScriptedProvider(_baldi_call({"qc": 12.0, "sigma_vo_eff": 100.0}), answer=[""])
    agent = GeoAIAgent(provider, tool_registry, max_tools=5)

    events = list(agent.run_stream("Baldi relative density, qc = 12 MPa, sigma'vo = 100 kPa"))

    text = "".join(e.content or "" for e in events if e.type == "token")
    assert f"**{BALDI}** result: Dr" in text


# --- provider cancellation ---------------------------------------------------------------

def test_cancelled_provider_fails_fast_without_loading_the_model():
    provider = LlamaCppProvider(GeoAIModelConfig(model_path="missing.gguf"))
    provider.cancel()
    with pytest.raises(GenerationCancelled):
        provider.generate([], tools=None)
    with pytest.raises(GenerationCancelled):
        list(provider.generate_stream([], tools=None))
    provider.clear_cancel()
    with pytest.raises(RuntimeError, match="not found"):  # re-armed: it now tries to load
        provider.generate([], tools=None)


def test_abort_flag_follows_cancel_and_deadline():
    provider = LlamaCppProvider(GeoAIModelConfig(model_path="missing.gguf", generation_timeout_s=1))
    assert not provider._should_abort()
    provider._start_call()
    assert not provider._should_abort()
    provider._deadline = time.monotonic() - 1
    assert provider._should_abort()
    assert "time limit" in str(provider._aborted_error())
    provider._deadline = None
    provider.cancel()
    assert provider._should_abort()
    assert "stopped" in str(provider._aborted_error())


def test_default_answer_stream_drops_tools():
    seen = {}

    class Plain(ScriptedProvider):
        def generate_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
            seen["tools"] = tools
            yield StreamChunk(delta_content="ok")

    chunks = list(ModelProvider.generate_answer_stream(Plain(None), [], tools=[{"x": 1}]))
    assert seen["tools"] is None and chunks[0].delta_content == "ok"


# --- lifecycle ---------------------------------------------------------------------------

class BlockingUnloadProvider(ScriptedProvider):
    """unload() waits like LlamaCppProvider.unload() does behind a running generation."""

    def __init__(self):
        super().__init__(None)
        self.release = threading.Event()
        self.cancelled = False

    def unload(self):
        self.release.wait(5)

    def cancel(self):
        self.cancelled = True


def test_unload_does_not_hold_the_lifecycle_lock():
    manager = ModelLifecycleManager()
    provider = BlockingUnloadProvider()
    manager.set_provider(provider)
    t = threading.Thread(target=manager.unload)
    t.start()
    time.sleep(0.1)
    start = time.monotonic()
    manager.get_memory_status()  # previously blocked until the generation finished
    assert time.monotonic() - start < 1.0
    provider.release.set()
    t.join(5)


def test_lifecycle_cancel_reaches_provider():
    manager = ModelLifecycleManager()
    assert manager.cancel()["status"] == "idle"
    provider = BlockingUnloadProvider()
    manager.set_provider(provider)
    assert manager.cancel()["status"] == "cancelled"
    assert provider.cancelled
