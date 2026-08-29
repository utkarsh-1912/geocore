import os
import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from core.geoai.model_provider import (
    MessageRole,
    ChatMessage,
    ToolCall,
    make_user_message,
    make_system_message,
    make_tool_result_message,
)
from core.geoai.model_config import GeoAIModelConfig, load_config, find_gguf_models
from core.geoai.heuristic_provider import HeuristicProvider
from core.geoai.llama_cpp_provider import LlamaCppProvider

# --- MessageRole enum tests ---

def test_message_role_enum():
    assert MessageRole.SYSTEM.value == "system"
    assert MessageRole.USER.value == "user"
    assert MessageRole.ASSISTANT.value == "assistant"
    assert MessageRole.TOOL.value == "tool"

# --- ChatMessage tests ---

def test_chat_message_to_dict_user():
    msg = ChatMessage(role=MessageRole.USER, content="Hello")
    assert msg.to_dict() == {"role": "user", "content": "Hello"}

def test_chat_message_to_dict_assistant_with_tools():
    tc = ToolCall(id="call_1", function_name="get_weather", arguments={"loc": "NY"})
    msg = ChatMessage(role=MessageRole.ASSISTANT, tool_calls=[tc])
    d = msg.to_dict()
    assert d["role"] == "assistant"
    assert len(d["tool_calls"]) == 1
    assert d["tool_calls"][0]["id"] == "call_1"
    assert d["tool_calls"][0]["type"] == "function"
    assert d["tool_calls"][0]["function"]["name"] == "get_weather"
    assert json.loads(d["tool_calls"][0]["function"]["arguments"]) == {"loc": "NY"}

def test_chat_message_to_dict_tool_result():
    msg = ChatMessage(role=MessageRole.TOOL, content="42", tool_call_id="call_1", name="get_weather")
    d = msg.to_dict()
    assert d["role"] == "tool"
    assert d["content"] == "42"
    assert d["tool_call_id"] == "call_1"
    assert d["name"] == "get_weather"

# --- Helper function tests ---

def test_make_user_message():
    msg = make_user_message("Hi")
    assert msg.role == MessageRole.USER
    assert msg.content == "Hi"

def test_make_system_message():
    msg = make_system_message("Sys")
    assert msg.role == MessageRole.SYSTEM
    assert msg.content == "Sys"

def test_make_tool_result_message_dict():
    msg = make_tool_result_message("call_2", "calc", {"res": 10})
    assert msg.role == MessageRole.TOOL
    assert msg.tool_call_id == "call_2"
    assert msg.name == "calc"
    assert json.loads(msg.content) == {"res": 10}

def test_make_tool_result_message_str():
    msg = make_tool_result_message("call_3", "calc", "10")
    assert msg.role == MessageRole.TOOL
    assert msg.content == "10"

# --- HeuristicProvider tests ---

@patch("core.geoai.heuristic_provider.LocalGemmaEngine")
def test_heuristic_provider_is_loaded(mock_engine):
    provider = HeuristicProvider()
    assert provider.is_loaded() is True

@patch("core.geoai.heuristic_provider.LocalGemmaEngine")
def test_heuristic_provider_model_info(mock_engine):
    provider = HeuristicProvider()
    info = provider.model_info()
    assert info["provider"] == "heuristic"
    assert "name" in info

@patch("core.geoai.heuristic_provider.LocalGemmaEngine")
def test_heuristic_provider_generate_with_tools(mock_engine):
    mock_instance = mock_engine.return_value
    mock_instance.find_best_tools.return_value = [{"name": "rankine_calc"}]
    mock_instance.extract_parameters_from_text.return_value = {"phi": 32}

    provider = HeuristicProvider()
    msg = make_user_message("calculate Rankine earth pressure for phi = 32")
    res = provider.generate([msg])
    
    assert res.finish_reason == "tool_calls"
    assert res.tool_calls is not None
    assert len(res.tool_calls) == 1
    assert res.tool_calls[0].function_name == "rankine_calc"
    assert res.tool_calls[0].arguments == {"phi": 32}

@patch("core.geoai.heuristic_provider.LocalGemmaEngine")
def test_heuristic_provider_generate_empty(mock_engine):
    provider = HeuristicProvider()
    res = provider.generate([])
    assert res.finish_reason == "stop"
    assert res.tool_calls is None
    assert "couldn't identify" in res.content

@patch("core.geoai.heuristic_provider.LocalGemmaEngine")
def test_heuristic_provider_generate_stream(mock_engine):
    mock_instance = mock_engine.return_value
    mock_instance.find_best_tools.return_value = [{"name": "rankine_calc"}]
    mock_instance.extract_parameters_from_text.return_value = {"phi": 32}

    provider = HeuristicProvider()
    msg = make_user_message("calculate Rankine earth pressure for phi = 32")
    stream = list(provider.generate_stream([msg]))
    
    assert len(stream) == 1
    chunk = stream[0]
    assert chunk.finish_reason == "tool_calls"
    assert chunk.delta_tool_calls[0].function_name == "rankine_calc"

# --- LlamaCppProvider tests ---

def test_llamacpp_init_lazy():
    config = GeoAIModelConfig(model_path="dummy.gguf")
    provider = LlamaCppProvider(config)
    assert provider.is_loaded() is False

def test_llamacpp_ensure_loaded_no_path():
    config = GeoAIModelConfig(model_path=None)
    provider = LlamaCppProvider(config)
    with pytest.raises(RuntimeError, match="Model path is not specified"):
        provider._ensure_loaded()

def test_llamacpp_ensure_loaded_not_found():
    config = GeoAIModelConfig(model_path="nonexistent_model.gguf")
    provider = LlamaCppProvider(config)
    with pytest.raises(RuntimeError, match="Model file not found"):
        provider._ensure_loaded()

def test_llamacpp_model_info():
    config = GeoAIModelConfig(model_path="dummy.gguf", n_ctx=2048, n_gpu_layers=10)
    provider = LlamaCppProvider(config)
    info = provider.model_info()
    assert info["provider"] == "llama_cpp"
    assert info["model_path"] == "dummy.gguf"
    assert info["loaded"] is False
    assert info["n_ctx"] == 2048
    assert info["n_gpu_layers"] == 10

def test_llamacpp_unload():
    config = GeoAIModelConfig(model_path="dummy.gguf")
    provider = LlamaCppProvider(config)
    provider._model = MagicMock()
    assert provider.is_loaded() is True
    provider.unload()
    assert provider.is_loaded() is False

# --- GeoAIModelConfig tests ---

def test_config_defaults():
    config = GeoAIModelConfig()
    assert config.n_ctx == 4096
    assert config.n_gpu_layers == 0
    assert config.provider == "auto"

@patch("core.geoai.model_config.get_config_dir")
def test_load_config_no_file(mock_get_config_dir, tmp_path):
    mock_get_config_dir.return_value = tmp_path
    config = load_config()
    assert config.n_ctx == 4096
    assert config.provider == "auto"

@patch.dict(os.environ, {"GEOAI_MODEL_PATH": "/custom/path.gguf", "GEOAI_PROVIDER": "llama_cpp", "GEOAI_N_CTX": "8192", "GEOAI_GPU_LAYERS": "-1"})
@patch("core.geoai.model_config.get_config_dir")
def test_load_config_env_vars(mock_get_config_dir, tmp_path):
    mock_get_config_dir.return_value = tmp_path
    config = load_config()
    assert config.model_path == "/custom/path.gguf"
    assert config.provider == "llama_cpp"
    assert config.n_ctx == 8192
    assert config.n_gpu_layers == -1

def test_find_gguf_models_empty(tmp_path):
    models = find_gguf_models(search_dir=tmp_path)
    assert models == []

def test_find_gguf_models_with_files(tmp_path):
    (tmp_path / "model1.gguf").touch()
    (tmp_path / "model2.gguf").touch()
    (tmp_path / "not_model.txt").touch()
    
    models = find_gguf_models(search_dir=tmp_path)
    assert len(models) == 2
    names = [m.name for m in models]
    assert "model1.gguf" in names
    assert "model2.gguf" in names
