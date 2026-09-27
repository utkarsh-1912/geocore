"""Desktop-runtime LoRA adapter support: GGUF header reader, compatibility check, provider wiring."""
import json
import os
import sys
import types
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from gguf_fixtures import write_fake_base, write_fake_lora  # noqa: E402

from core.geoai.gguf_meta import (  # noqa: E402
    GGUFFormatError,
    base_model_fingerprint,
    compare_fingerprints,
    is_lora_adapter,
    read_gguf_metadata,
)
from core.geoai.llama_cpp_provider import LlamaCppProvider, parse_native_tool_calls  # noqa: E402
from core.geoai.lora_adapter import SIDECAR_SCHEMA, check_adapter_compatibility, sidecar_path  # noqa: E402
from core.geoai.model_config import GeoAIModelConfig, find_gguf_models, load_config  # noqa: E402
from core.geoai.model_provider import make_user_message  # noqa: E402


@pytest.fixture
def base(tmp_path):
    return write_fake_base(tmp_path / "base-q4_k_m.gguf")


@pytest.fixture
def lora(tmp_path):
    return write_fake_lora(tmp_path / "adapters_geoai-lora.gguf")


def _sidecar(lora_path, **fp_overrides):
    fp = {"architecture": "qwen2", "block_count": 28, "embedding_length": 1536, "vocab_size": 3,
          "finetune": "qwen2.5-1.5b-instruct"}
    fp.update(fp_overrides)
    sc = {"schema": SIDECAR_SCHEMA, "base_model_id": "Qwen/Qwen2.5-1.5B-Instruct", "chat_template": "native",
          "base_gguf": {"filename": "base-q4_k_m.gguf", "fingerprint": fp}}
    sidecar_path(str(lora_path)).write_text(json.dumps(sc), encoding="utf-8")
    return sc


# ---------------- GGUF header reader ----------------

def test_read_metadata_and_fingerprint(base):
    meta = read_gguf_metadata(base)
    assert meta["general.architecture"] == "qwen2"
    assert meta["tokenizer.ggml.tokens"]["len"] == 3  # arrays skipped, length kept
    fp = base_model_fingerprint(base)
    assert fp["architecture"] == "qwen2" and fp["block_count"] == 28 and fp["vocab_size"] == 3


def test_not_gguf_raises(tmp_path):
    p = tmp_path / "x.gguf"
    p.write_bytes(b"nope")
    with pytest.raises(GGUFFormatError):
        read_gguf_metadata(p)
    assert is_lora_adapter(p) is False


def test_is_lora_adapter(base, lora):
    assert is_lora_adapter(lora) is True
    assert is_lora_adapter(base) is False


def test_compare_fingerprints_rules():
    exp = {"architecture": "qwen2", "block_count": 28, "finetune": "qwen2.5-1.5b-instruct", "size_label": "1.5B"}
    assert compare_fingerprints(exp, {"architecture": "qwen2", "block_count": 28, "finetune": "Instruct",
                                      "size_label": "1.8B"}) is None
    assert "block_count" in compare_fingerprints(exp, {"architecture": "qwen2", "block_count": 36})
    assert "finetune" in compare_fingerprints(exp, {"architecture": "qwen2", "finetune": "qwen2.5-coder-1.5b"})


def test_find_gguf_models_skips_adapters(tmp_path, base, lora):
    names = [p.name for p in find_gguf_models(search_dir=tmp_path)]
    assert names == ["base-q4_k_m.gguf"]


# ---------------- compatibility check ----------------

def test_compatible_adapter_with_sidecar(base, lora):
    _sidecar(lora)
    chk = check_adapter_compatibility(str(lora), str(base))
    assert chk.ok and chk.reason is None
    assert chk.summary()["base_model_id"] == "Qwen/Qwen2.5-1.5B-Instruct"


def test_adapter_without_sidecar_is_allowed_with_warning(base, lora):
    chk = check_adapter_compatibility(str(lora), str(base))
    assert chk.ok and any("no sidecar" in w for w in chk.warnings)


def test_architecture_mismatch_rejected(tmp_path, base):
    other = write_fake_lora(tmp_path / "llama-lora.gguf", arch="llama")
    chk = check_adapter_compatibility(str(other), str(base))
    assert not chk.ok and "architecture" in chk.reason


def test_sidecar_base_mismatch_rejected(base, lora):
    _sidecar(lora, block_count=36)  # trained for a bigger model of the same architecture
    chk = check_adapter_compatibility(str(lora), str(base))
    assert not chk.ok and "block_count" in chk.reason


def test_full_model_is_not_an_adapter(tmp_path, base):
    other = write_fake_base(tmp_path / "other.gguf")
    chk = check_adapter_compatibility(str(other), str(base))
    assert not chk.ok and "not a GGUF LoRA adapter" in chk.reason


def test_missing_adapter_rejected(base, tmp_path):
    assert not check_adapter_compatibility(str(tmp_path / "nope.gguf"), str(base)).ok


# ---------------- config ----------------

def test_config_lora_defaults(monkeypatch):
    monkeypatch.delenv("GEOAI_LORA_PATH", raising=False)
    monkeypatch.delenv("GEOAI_CHAT_FORMAT", raising=False)
    cfg = GeoAIModelConfig()
    assert cfg.lora_path is None and cfg.lora_scale == 1.0 and cfg.chat_format is None


def test_config_env_override_applies_to_direct_construction(monkeypatch):
    # the eval runner builds GeoAIModelConfig(...) directly, so env must reach the dataclass defaults
    monkeypatch.setenv("GEOAI_LORA_PATH", "/x/geoai-lora.gguf")
    monkeypatch.setenv("GEOAI_LORA_SCALE", "0.5")
    cfg = GeoAIModelConfig(model_path="m.gguf", n_ctx=4096, n_gpu_layers=0, provider="llama_cpp")
    assert cfg.lora_path == "/x/geoai-lora.gguf" and cfg.lora_scale == 0.5


def test_load_config_env_overrides_file(monkeypatch, tmp_path):
    (tmp_path / "geoai_config.json").write_text(json.dumps({"lora_path": "/file/a.gguf"}), encoding="utf-8")
    monkeypatch.setenv("GEOAI_LORA_PATH", "/env/b.gguf")
    with patch("core.geoai.model_config.get_config_dir", return_value=tmp_path):
        assert load_config().lora_path == "/env/b.gguf"
    monkeypatch.delenv("GEOAI_LORA_PATH")
    with patch("core.geoai.model_config.get_config_dir", return_value=tmp_path):
        assert load_config().lora_path == "/file/a.gguf"


# ---------------- provider ----------------

def _fake_llama_module(side_effect=None):
    mod = types.ModuleType("llama_cpp")
    mod.Llama = MagicMock(side_effect=side_effect)
    return mod


def test_provider_passes_lora_params(base, lora):
    _sidecar(lora)
    fake = _fake_llama_module()
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), lora_path=str(lora), lora_scale=0.7))
        p.load()
    kw = fake.Llama.call_args.kwargs
    assert kw["lora_path"] == str(lora) and kw["lora_scale"] == 0.7
    assert kw["chat_format"] is None  # sidecar says native -> GGUF's own template
    info = p.model_info()
    assert info["lora_adapter"]["status"] == "active" and info["chat_format"] == "native"


def test_provider_refuses_mismatched_adapter(base, lora):
    _sidecar(lora, embedding_length=2048)
    fake = _fake_llama_module()
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), lora_path=str(lora)))
        p.load()
    kw = fake.Llama.call_args.kwargs
    assert "lora_path" not in kw and kw["chat_format"] == "chatml-function-calling"
    info = p.model_info()["lora_adapter"]
    assert info["status"] == "rejected" and info["active"] is False and "embedding_length" in info["reason"]


def test_provider_falls_back_when_llama_rejects_adapter(base, lora):
    ok_model = MagicMock()

    def llama(**kw):
        if kw.get("lora_path"):
            raise ValueError("Failed to initialize LoRA adapter")
        return ok_model

    fake = _fake_llama_module(side_effect=llama)
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), lora_path=str(lora)))
        p.load()
    assert p._model is ok_model and fake.Llama.call_count == 2
    assert p.model_info()["lora_adapter"]["status"] == "rejected"


def test_provider_without_adapter_unchanged(base):
    fake = _fake_llama_module()
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), lora_path=None, chat_format=None))
        p.load()
    kw = fake.Llama.call_args.kwargs
    assert "lora_path" not in kw and kw["chat_format"] == "chatml-function-calling"
    assert p.model_info()["lora_adapter"] is None


def test_provider_auto_uses_native_when_template_renders_tools(tmp_path):
    base = write_fake_base(tmp_path / "tools-base.gguf",
                           **{"tokenizer.chat_template": "{% if tools %}<tools>{{ tools }}</tools>{% endif %}"})
    fake = _fake_llama_module()
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), lora_path=None, chat_format=None))
        p.load()
    assert fake.Llama.call_args.kwargs["chat_format"] is None
    assert p.model_info()["chat_format"] == "native"


def test_native_generate_parses_tool_calls(base):
    fake = _fake_llama_module()
    completion = ('Plan: call calculate_gmax_from_shear_wave_velocity with Vs, gamma from the request.\n'
                  '<tool_call>\n{"name": "calculate_gmax_from_shear_wave_velocity", "arguments": {"Vs": 280, "gamma": 19.5}}\n</tool_call>')
    fake.Llama.return_value.create_chat_completion.return_value = {
        "choices": [{"message": {"role": "assistant", "content": completion}, "finish_reason": "stop"}]}
    with patch.dict(sys.modules, {"llama_cpp": fake}):
        p = LlamaCppProvider(GeoAIModelConfig(model_path=str(base), chat_format="native"))
        resp = p.generate([make_user_message("Gmax?")], tools=[{"type": "function", "function": {"name": "x"}}])
    assert resp.finish_reason == "tool_calls"
    assert resp.tool_calls[0].function_name == "calculate_gmax_from_shear_wave_velocity"
    assert resp.tool_calls[0].arguments == {"Vs": 280, "gamma": 19.5}
    assert resp.content.startswith("Plan:")


def test_parse_native_tool_calls_variants():
    content, calls = parse_native_tool_calls('<tool_call>\n{{"name": "t", "arguments": {"a": 1}}}}\n</tool_call>')
    assert calls and calls[0].function_name == "t" and calls[0].arguments == {"a": 1}
    content, calls = parse_native_tool_calls("<tool_call>{broken</tool_call>")
    assert calls == []
    content, calls = parse_native_tool_calls("Please provide the friction angle.")
    assert calls == [] and content == "Please provide the friction angle."
