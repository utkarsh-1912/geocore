"""Tool-call markup of the benchmarked model families, the prompted chat format and the thinking switch."""
import json
import os
import sys
import types
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from gguf_fixtures import write_fake_base  # noqa: E402

from core.geoai.llama_cpp_provider import (  # noqa: E402
    LlamaCppProvider,
    build_prompted_messages,
    parse_tool_calls,
    strip_thinking,
)
from core.geoai.model_config import GeoAIModelConfig  # noqa: E402
from core.geoai.model_provider import ChatMessage, MessageRole, ToolCall, make_user_message  # noqa: E402

ARGS = {"qc": 5.2, "fs": 40.0}
CALL = {"name": "calculate_cpt_soil_behavior_type", "arguments": ARGS}


@pytest.mark.parametrize("family,text", [
    ("hermes/qwen", "Plan: classify.\n<tool_call>\n" + json.dumps(CALL) + "\n</tool_call>"),
    ("granite3/phi", "<|tool_call|>[" + json.dumps(CALL) + "]"),
    ("phi closed", "<|tool_call|>" + json.dumps(CALL) + "<|/tool_call|>"),
    ("phi functools", "functools[" + json.dumps(CALL) + "]"),
    ("mistral", "[TOOL_CALLS][" + json.dumps(CALL) + "]"),
    ("llama python_tag", "<|python_tag|>" + json.dumps({"name": CALL["name"], "parameters": ARGS}) + "<|eom_id|>"),
    ("llama bare", json.dumps({"name": CALL["name"], "parameters": ARGS})),
    ("stripped marker list", "[" + json.dumps(CALL) + "]"),
    ("fenced json", "```json\n" + json.dumps(CALL) + "\n```"),
    ("openai nesting", "<tool_call>" + json.dumps({"function": {"name": CALL["name"], "arguments": json.dumps(ARGS)}})
     + "</tool_call>"),
])
def test_parse_tool_calls_formats(family, text):
    content, calls = parse_tool_calls(text)
    assert len(calls) == 1, family
    assert calls[0].function_name == CALL["name"] and calls[0].arguments == ARGS


@pytest.mark.parametrize("text", [
    '<tool_call>\n{\n"name": "relativedensity",\n"arguments": {\n"relative_density": 0.95,\n}\n}\n</tool_call>',
    '<tool_call>\n{\n"name": "earthpressurecoefficients_rankine",\n"arguments": {\n"phi_eff": 34.0,\n}\n}',
])
def test_parse_tool_calls_tolerates_trailing_comma(text):
    content, calls = parse_tool_calls(text)
    assert len(calls) == 1
    assert content == ""


def test_parse_qwen35_xml_tool_calls():
    # Verbatim shape of Qwen3.5-2B output seen in the benchmark log.
    text = ("<tool_call>\n<function=derive_cpt_parameters>\n<parameter=qc_mpa>\n10.1\n</parameter>\n"
            "<parameter=fs_kpa>\n44\n</parameter>\n<parameter=soil_type>\nclay\n</parameter>\n"
            "<parameter=drained>\nfalse\n</parameter>\n</function>\n</tool_call>")
    content, calls = parse_tool_calls(text)
    assert len(calls) == 1 and calls[0].function_name == "derive_cpt_parameters"
    assert calls[0].arguments == {"qc_mpa": 10.1, "fs_kpa": 44, "soil_type": "clay", "drained": False}
    assert content == ""


def test_parse_qwen35_xml_unterminated_and_multiple():
    text = ("<tool_call><function=a><parameter=x>1</parameter></function></tool_call>\n"
            "<tool_call><function=b><parameter=y>two")  # cut off at max_tokens
    _, calls = parse_tool_calls(text)
    assert [(c.function_name, c.arguments) for c in calls] == [("a", {"x": 1}), ("b", {"y": "two"})]


def test_parse_multiple_calls_and_keeps_preamble():
    two = [CALL, {"name": "get_cpt_sounding", "arguments": {"cpt_id": "CPT-03"}}]
    content, calls = parse_tool_calls("I will run both.\n<|tool_call|>" + json.dumps(two) + "<|/tool_call|>")
    assert [c.function_name for c in calls] == [CALL["name"], "get_cpt_sounding"]
    assert content == "I will run both."


@pytest.mark.parametrize("text", [
    "The friction angle is 32 degrees.",
    'A settlement record looks like {"name": "S1", "value": 12}.',  # JSON in prose, no arguments key
    '{"name": "S1", "value": 12}',  # whole reply is JSON but not a call
    "[TOOL_CALLS][{broken",
])
def test_parse_tool_calls_leaves_non_calls_alone(text):
    content, calls = parse_tool_calls(text)
    assert calls == [] and content == text


def test_strip_thinking():
    assert strip_thinking("<think>\nhmm\n</think>\n\nAnswer") == "Answer"
    assert strip_thinking("<think>unterminated") == ""
    assert strip_thinking("No thinking") == "No thinking"


def test_build_prompted_messages_rewrites_tool_turns():
    tools = [{"type": "function", "function": {"name": "get_cpt_sounding", "parameters": {}}}]
    msgs = [
        {"role": "system", "content": "You are GeoAI."},
        {"role": "user", "content": "CPT-03?"},
        {"role": "assistant", "content": None,
         "tool_calls": [{"id": "c0", "type": "function",
                         "function": {"name": "get_cpt_sounding", "arguments": '{"cpt_id": "CPT-03"}'}}]},
        {"role": "tool", "tool_call_id": "c0", "content": '{"n": 10}'},
        {"role": "tool", "tool_call_id": "c1", "content": '{"n": 11}'},
    ]
    out = build_prompted_messages(msgs, tools)
    assert [m["role"] for m in out] == ["system", "user", "assistant", "user"]
    assert "<tools>" in out[0]["content"] and "get_cpt_sounding" in out[0]["content"]
    assert out[0]["content"].startswith("You are GeoAI.")
    assert '"cpt_id": "CPT-03"' in out[2]["content"] and out[2]["content"].startswith("<tool_call>")
    assert out[3]["content"].count("<tool_response>") == 2  # consecutive tool results merged


def _fake_llama(content):
    fake = types.ModuleType("llama_cpp")
    fake.Llama = MagicMock()
    fake.Llama.return_value.create_chat_completion.return_value = {
        "choices": [{"message": {"role": "assistant", "content": content}, "finish_reason": "stop"}]}
    return fake


def test_provider_auto_prompted_for_template_without_tools(tmp_path):
    base = write_fake_base(tmp_path / "gemma-like.gguf",
                           **{"tokenizer.chat_template": "{% for m in messages %}<start_of_turn>{{ m.content }}{% endfor %}"})
    fake = _fake_llama("<tool_call>" + json.dumps(CALL) + "</tool_call>")
    tools = [{"type": "function", "function": {"name": CALL["name"], "parameters": {}}}]
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), chat_format=None))
        resp = p.generate([make_user_message("classify")], tools=tools)
    assert fake.Llama.call_args.kwargs["chat_format"] is None
    assert p.model_info()["chat_format"] == "prompted"
    kw = fake.Llama.return_value.create_chat_completion.call_args.kwargs
    assert "tools" not in kw  # described in the system text instead
    assert kw["messages"][0]["role"] == "system" and "<tools>" in kw["messages"][0]["content"]
    assert resp.tool_calls[0].function_name == CALL["name"] and resp.tool_calls[0].arguments == ARGS


def test_provider_no_think_switch_and_think_stripping(tmp_path):
    base = write_fake_base(tmp_path / "qwen3-like.gguf",
                           **{"tokenizer.chat_template": "{% if tools %}x{% endif %}{% if enable_thinking %}y{% endif %}"})
    fake = _fake_llama("<think>\n\n</think>\n\nPlease give the cone resistance.")
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), chat_format=None))
        resp = p.generate([ChatMessage(role=MessageRole.SYSTEM, content="You are GeoAI."), make_user_message("qc?")],
                          tools=[{"type": "function", "function": {"name": "x"}}])
    kw = fake.Llama.return_value.create_chat_completion.call_args.kwargs
    assert kw["messages"][0]["content"].endswith("\n/no_think")
    assert resp.content == "Please give the cone resistance." and not resp.tool_calls

    fake = _fake_llama("ok")
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), chat_format=None, disable_thinking=False))
        p.generate([make_user_message("qc?")])
    kw = fake.Llama.return_value.create_chat_completion.call_args.kwargs
    assert all("/no_think" not in (m.get("content") or "") for m in kw["messages"])
