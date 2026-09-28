"""
CPU-latency settings for local inference: thread/batch config, per-phase generation caps,
thinking suppression, background warm-up and streamed final answers. llama_cpp is mocked.
"""
import functools
import os
import sys
import time
import types
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from gguf_fixtures import write_fake_base  # noqa: E402

from core.geoai.agent import GeoAIAgent  # noqa: E402
from core.geoai.lifecycle import ModelLifecycleManager  # noqa: E402
from core.geoai.llama_cpp_provider import LlamaCppProvider, ThinkStreamFilter  # noqa: E402
from core.geoai.model_config import GeoAIModelConfig, load_config, resolve_thread_counts  # noqa: E402
from core.geoai.model_provider import (ChatMessage, MessageRole, ModelProvider, ModelResponse,  # noqa: E402
                                       StreamChunk, ToolCall, make_user_message)
from core.geoai.response_guard import AnswerStreamCleaner, clean_answer  # noqa: E402
from core.geoai.tool_registry import GeoAIToolRegistry  # noqa: E402

PERF_ENV = ("GEOAI_N_THREADS", "GEOAI_N_THREADS_BATCH", "GEOAI_N_BATCH", "GEOAI_DECISION_MAX_TOKENS",
            "GEOAI_ANSWER_MAX_TOKENS", "GEOAI_THINKING")


@pytest.fixture
def clean_env(monkeypatch, tmp_path):
    for k in PERF_ENV:
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr("core.geoai.model_config.get_config_dir", lambda: tmp_path)
    return monkeypatch


# ---------------- config ----------------

def test_perf_config_defaults(clean_env):
    cfg = GeoAIModelConfig()
    assert cfg.n_threads is None and cfg.n_threads_batch is None  # auto
    assert cfg.n_batch == 512
    assert cfg.decision_max_tokens == 512  # also holds direct answers written without a tool
    assert cfg.answer_max_tokens == 1024
    assert cfg.disable_thinking is True


def test_perf_config_env_overrides(clean_env):
    for k, v in (("GEOAI_N_THREADS", "4"), ("GEOAI_N_THREADS_BATCH", "8"), ("GEOAI_N_BATCH", "256"),
                 ("GEOAI_DECISION_MAX_TOKENS", "200"), ("GEOAI_ANSWER_MAX_TOKENS", "300"), ("GEOAI_THINKING", "1")):
        clean_env.setenv(k, v)
    cfg = load_config()
    assert (cfg.n_threads, cfg.n_threads_batch, cfg.n_batch) == (4, 8, 256)
    assert (cfg.decision_max_tokens, cfg.answer_max_tokens) == (200, 300)
    assert cfg.disable_thinking is False
    assert GeoAIModelConfig().disable_thinking is False  # directly built configs (eval runner) too


def test_perf_config_invalid_env_keeps_default(clean_env):
    clean_env.setenv("GEOAI_N_THREADS", "many")
    clean_env.setenv("GEOAI_THINKING", "0")
    cfg = load_config()
    assert cfg.n_threads is None and cfg.disable_thinking is True


def test_resolve_thread_counts_auto_and_explicit(monkeypatch):
    monkeypatch.setattr(os, "cpu_count", lambda: 12)
    assert resolve_thread_counts(GeoAIModelConfig()) == (6, 12)  # llama-cpp-python defaults
    assert resolve_thread_counts(GeoAIModelConfig(n_threads=4, n_threads_batch=6)) == (4, 6)
    assert resolve_thread_counts(GeoAIModelConfig(n_threads=0)) == (6, 12)  # 0 = auto


# ---------------- provider (mocked llama_cpp) ----------------

def _fake_llama(content="ok", stream_deltas=None):
    fake = types.ModuleType("llama_cpp")
    fake.Llama = MagicMock()
    inst = fake.Llama.return_value
    inst._chat_handlers = {}
    inst.chat_format = "chat_template.default"

    def create_chat_completion(**kw):
        if kw.get("stream"):
            chunks = [{"choices": [{"delta": {"content": d}, "finish_reason": None}]} for d in stream_deltas or []]
            return iter(chunks + [{"choices": [{"delta": {}, "finish_reason": "stop"}]}])
        return {"choices": [{"message": {"role": "assistant", "content": content}, "finish_reason": "stop"}]}
    inst.create_chat_completion = MagicMock(side_effect=create_chat_completion)
    return fake


def test_provider_passes_threads_and_batch(tmp_path):
    base = write_fake_base(tmp_path / "m.gguf")
    fake = _fake_llama()
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), n_threads=3, n_threads_batch=7, n_batch=128))
        p.load()
    kw = fake.Llama.call_args.kwargs
    assert (kw["n_threads"], kw["n_threads_batch"], kw["n_batch"]) == (3, 7, 128)
    assert p.model_info()["n_threads"] == 3 and p.model_info()["n_threads_batch"] == 7


QWEN3_LIKE = "{% if tools %}x{% endif %}{% if enable_thinking is defined and enable_thinking is false %}y{% endif %}"


def test_thinking_disabled_through_template_kwarg(tmp_path):
    base = write_fake_base(tmp_path / "qwen3-like.gguf", **{"tokenizer.chat_template": QWEN3_LIKE})
    fake = _fake_llama("<think>\n\n</think>\n\nPlease give the cone resistance.")
    handler = MagicMock(name="template_handler")
    fake.Llama.return_value._chat_handlers["chat_template.default"] = handler
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), chat_format=None, disable_thinking=True))
        resp = p.generate([ChatMessage(role=MessageRole.SYSTEM, content="You are GeoAI."), make_user_message("qc?")],
                          tools=[{"type": "function", "function": {"name": "x"}}])
    ch = fake.Llama.return_value.chat_handler
    assert isinstance(ch, functools.partial) and ch.func is handler and ch.keywords == {"enable_thinking": False}
    kw = fake.Llama.return_value.create_chat_completion.call_args.kwargs
    assert kw["messages"][0]["content"] == "You are GeoAI."  # no /no_think soft switch needed
    assert resp.content == "Please give the cone resistance." and not resp.tool_calls


def test_thinking_enabled_passes_true(tmp_path):
    base = write_fake_base(tmp_path / "qwen3-like.gguf", **{"tokenizer.chat_template": QWEN3_LIKE})
    fake = _fake_llama()
    fake.Llama.return_value._chat_handlers["chat_template.default"] = MagicMock()
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), chat_format=None, disable_thinking=False))
        p.load()
    assert fake.Llama.return_value.chat_handler.keywords == {"enable_thinking": True}


def test_template_without_thinking_switch_is_untouched(tmp_path):
    base = write_fake_base(tmp_path / "qwen25-like.gguf", **{"tokenizer.chat_template": "{% if tools %}x{% endif %}"})
    fake = _fake_llama()
    sentinel = object()
    fake.Llama.return_value.chat_handler = sentinel
    fake.Llama.return_value._chat_handlers["chat_template.default"] = MagicMock()
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), chat_format=None))
        p.generate([ChatMessage(role=MessageRole.SYSTEM, content="S"), make_user_message("q")])
    assert fake.Llama.return_value.chat_handler is sentinel
    kw = fake.Llama.return_value.create_chat_completion.call_args.kwargs
    assert kw["messages"][0]["content"] == "S"


def test_thinking_fallback_soft_switch_when_handler_missing(tmp_path):
    base = write_fake_base(tmp_path / "qwen3-like.gguf", **{"tokenizer.chat_template": QWEN3_LIKE})
    fake = _fake_llama()  # no template handler registered
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), chat_format=None, disable_thinking=True))
        p.generate([ChatMessage(role=MessageRole.SYSTEM, content="S"), make_user_message("q")])
    kw = fake.Llama.return_value.create_chat_completion.call_args.kwargs
    assert kw["messages"][0]["content"].endswith("\n/no_think")


@pytest.mark.parametrize("deltas,expected", [
    (["<think>\n\n</think>\n\n", "The answer", " is 5."], "The answer is 5."),
    (["<thi", "nk>reasoning about qc", " and fs</thi", "nk>\n", "Zone 7."], "Zone 7."),
    (["Zone 7.", " <think>oops"], "Zone 7. "),  # unterminated block dropped
    (["No thinking < here", "."], "No thinking < here."),
    (["<", "b>bold</b>"], "<b>bold</b>"),
])
def test_think_stream_filter(deltas, expected):
    f = ThinkStreamFilter()
    out = "".join(f.feed(d) for d in deltas) + f.flush()
    assert out == expected


def test_generate_stream_strips_thinking(tmp_path):
    base = write_fake_base(tmp_path / "qwen3-like.gguf", **{"tokenizer.chat_template": QWEN3_LIKE})
    fake = _fake_llama(stream_deltas=["<think>", "\nhmm\n", "</think>\n\n", "Qt is", " 361."])
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), chat_format=None))
        text = "".join(c.delta_content or "" for c in p.generate_stream([make_user_message("q")]))
    assert text == "Qt is 361."


def test_warm_up_prefills_system_prompt(tmp_path):
    base = write_fake_base(tmp_path / "m.gguf", **{"tokenizer.chat_template": "{% if tools %}x{% endif %}"})
    fake = _fake_llama()
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), chat_format=None))
        p.warm_up("You are GeoAI.")
    assert p.is_loaded()
    kw = fake.Llama.return_value.create_chat_completion.call_args.kwargs
    assert kw["messages"] == [{"role": "system", "content": "You are GeoAI."}] and kw["max_tokens"] == 1


# ---------------- lifecycle warm-up ----------------

class WarmableProvider(ModelProvider):
    def __init__(self):
        self.loaded = False
        self.warm_prompts = []

    def warm_up(self, system_prompt=None):
        time.sleep(0.05)
        self.warm_prompts.append(system_prompt)
        self.loaded = True

    def is_loaded(self):
        return self.loaded

    def model_info(self):
        return {"provider": "warmable", "loaded": self.loaded}

    def generate(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        return ModelResponse(content="ok", tool_calls=None, finish_reason="stop")

    def generate_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        yield from []

    def unload(self):
        self.loaded = False


def test_lifecycle_warm_up_in_background_then_idle_unload():
    mgr = ModelLifecycleManager(idle_timeout_seconds=0.2)
    provider = WarmableProvider()
    mgr.set_provider(provider)
    assert mgr.warm_up(background=True)["status"] == "warming"
    assert mgr.warm_up(background=True)["status"] == "warming"  # no second load
    deadline = time.time() + 5
    while not provider.loaded and time.time() < deadline:
        time.sleep(0.01)
    assert provider.loaded and len(provider.warm_prompts) == 1
    assert provider.warm_prompts[0].startswith("You are GeoAI")  # static system prompt prefix
    assert mgr.warm_up()["status"] == "loaded"
    time.sleep(0.25)
    assert mgr.check_idle_and_unload() is True  # warm-up does not pin the model in memory


def test_lifecycle_warm_up_not_required_for_heuristic():
    from core.geoai.heuristic_provider import HeuristicProvider
    mgr = ModelLifecycleManager()
    mgr.set_provider(HeuristicProvider())
    assert mgr.warm_up()["status"] == "not_required"


def test_warmup_endpoint(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from core.geoai import api
    calls = []
    monkeypatch.setattr(api.lifecycle_manager, "warm_up",
                        lambda background=True: calls.append(background) or {"status": "warming", "loaded": False})
    app = FastAPI()
    app.include_router(api.router, prefix="/api")
    r = TestClient(app).post("/api/geoai/warmup")
    assert r.status_code == 200 and r.json()["status"] == "warming" and calls == [True]


# ---------------- agent generation caps ----------------

class CapRecorder(ModelProvider):
    def __init__(self, responses):
        self.responses = list(responses)
        self.max_tokens = []

    def generate(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        self.max_tokens.append(max_tokens)
        return self.responses.pop(0)

    def generate_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        self.max_tokens.append(max_tokens)
        yield StreamChunk(delta_content="Done.", finish_reason="stop")

    def is_loaded(self):
        return True

    def model_info(self):
        return {}


class EchoRegistry(GeoAIToolRegistry):
    def invoke_tool(self, tool_name, args):
        return {"value": 1.0}


def test_agent_uses_phase_token_caps(clean_env):
    clean_env.setenv("GEOAI_DECISION_MAX_TOKENS", "111")
    clean_env.setenv("GEOAI_ANSWER_MAX_TOKENS", "222")
    call = ModelResponse(content=None, tool_calls=[ToolCall(id="c", function_name="t", arguments={})],
                         finish_reason="tool_calls")
    p = CapRecorder([call, ModelResponse(content="Value is 1.0.", tool_calls=None, finish_reason="stop")])
    GeoAIAgent(p, EchoRegistry(), max_tools=5).run("calc")
    assert p.max_tokens == [111, 222]

    p = CapRecorder([])
    p.generate_stream = lambda messages, tools=None, temperature=0.1, max_tokens=1024: (
        p.max_tokens.append(max_tokens) or iter([StreamChunk(delta_tool_calls=[call.tool_calls[0]])] if tools
                                                else [StreamChunk(delta_content="Done.")]))
    events = list(GeoAIAgent(p, EchoRegistry(), max_tools=5).run_stream("calc t"))
    assert p.max_tokens[-1] == 222
    assert [e.content for e in events if e.type == "token"] == ["Done."]


# ---------------- streamed answer guard ----------------

def test_answer_stream_cleaner_matches_clean_answer_for_any_chunking():
    import random
    tools = [{"name": "cpt", "result": {"status": "success", "result": {
        "Qt": 360.99, "Ic": 1.31, "_provenance": {"output_units": {"Qt": "-", "Ic": "-"}}}}}]
    loop = "The soil behaviour type index Ic is 1.31. "
    texts = [
        "Qt is 360.99 kPa. " + loop + "\n\nThis indicates sand. " + loop * 5 + "The soil beha",
        "The result is 5.2 kN/m3. [Calculation record] inline stays\n"
        "[Calculation record] {\"tool\": \"x\"}\nMore text, fine.\n- bullet one\n- bullet two",
        "Line one\nLine two.\n\n\nValue 1.31 kPa!",
        "Ka is 0.283. Active state full ... [Calculation record] {\"tool\": \"x\", \"Kp\": -1.5}\n"
        "Per EN 1997-1 \\u00a79.5 [see note]. Done.",
        "",
    ]
    rng = random.Random(0)
    for text in texts:
        expected = clean_answer(text, tools)
        for _ in range(100):
            c, out, i = AnswerStreamCleaner(tools), "", 0
            while i < len(text):
                n = rng.randint(1, 9)
                out += c.feed(text[i:i + n])
                i += n
            out += c.flush()
            assert out.rstrip() == expected


def test_answer_stream_cleaner_releases_sentences_early():
    c = AnswerStreamCleaner([])
    assert c.feed("First sentence is here.") == ""  # may still be followed by more of the separator
    assert c.feed(" Second") == "First sentence is here."
    assert c.flush() == " Second"


# ---------------- one think-stripping mechanism, stop strings, prompt prefix ----------------

@pytest.mark.parametrize("text,expected", [
    ("<think>\nhmm\n</think>\n\nAnswer", "Answer"),
    ("<think>\n\n</think>\n\nAnswer", "Answer"),  # empty block (enable_thinking=False output)
    ("<think>unterminated", ""),
    ("reasoning prefilled by the template\n</think>\n\nAnswer", "Answer"),  # Qwen3.5 thinking on
    ("No thinking", "No thinking"),
    ("  keep  as is  ", "  keep  as is  "),
])
def test_strip_thinking_uses_stream_filter_semantics(text, expected):
    from core.geoai.llama_cpp_provider import strip_thinking
    assert strip_thinking(text) == expected


def test_tool_turn_has_stop_strings_answer_turn_does_not(tmp_path):
    from core.geoai.llama_cpp_provider import TOOL_TURN_STOP
    base = write_fake_base(tmp_path / "m.gguf", **{"tokenizer.chat_template": "{% if tools %}x{% endif %}"})
    fake = _fake_llama('<tool_call>\n{"name": "x", "arguments": {}}\n</tool_call>')
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), chat_format=None))
        resp = p.generate([make_user_message("q")], tools=[{"type": "function", "function": {"name": "x"}}])
        assert fake.Llama.return_value.create_chat_completion.call_args.kwargs["stop"] == list(TOOL_TURN_STOP)
        p.generate([make_user_message("q")])
        assert "stop" not in fake.Llama.return_value.create_chat_completion.call_args.kwargs
    assert resp.tool_calls[0].function_name == "x"


def test_stream_with_thinking_on_holds_until_complete(tmp_path):
    base = write_fake_base(tmp_path / "qwen35-like.gguf", **{"tokenizer.chat_template": QWEN3_LIKE})
    fake = _fake_llama(stream_deltas=["reasoning that the template", " opened\n</think>\n\n", "Zone 7."])
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), chat_format=None, disable_thinking=False))
        chunks = [c.delta_content for c in p.generate_stream([make_user_message("q")]) if c.delta_content]
    assert chunks == ["Zone 7."]


def test_static_system_prompt_is_the_prefix_of_every_request_prompt():
    # Warm-up prefills build_system_prompt(None); llama.cpp reuses it only if every request's
    # system text starts with exactly that static part (dynamic context goes after it).
    from core.geoai.system_prompt import build_system_prompt
    static = build_system_prompt(None)
    ctx = {"activeFunction": "classify_cpt_soil_behavior", "activeCategory": "CPT",
           "project_context": "### ACTIVE PROJECT CONTEXT\n- Project: X"}
    assert build_system_prompt(ctx).startswith(static)


def test_saved_old_default_caps_are_upgraded_but_custom_values_kept(clean_env, tmp_path, monkeypatch):
    import json
    import core.geoai.model_config as mc
    monkeypatch.setattr(mc, "get_config_dir", lambda: tmp_path)
    (tmp_path / mc.DEFAULT_CONFIG_FILENAME).write_text(
        json.dumps({"decision_max_tokens": 200, "answer_max_tokens": 320}), encoding="utf-8")
    cfg = load_config()
    assert (cfg.decision_max_tokens, cfg.answer_max_tokens) == (512, 1024)  # old defaults, never chosen
    (tmp_path / mc.DEFAULT_CONFIG_FILENAME).write_text(
        json.dumps({"decision_max_tokens": 300, "answer_max_tokens": 2048}), encoding="utf-8")
    cfg = load_config()
    assert (cfg.decision_max_tokens, cfg.answer_max_tokens) == (300, 2048)  # deliberate values kept
