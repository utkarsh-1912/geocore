"""Training-side GeoAI fine-tuning package: config, formatting, rewards, dry-runs, export helpers (no torch)."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from gguf_fixtures import write_fake_base, write_fake_lora  # noqa: E402

from core.geoai.finetune.config import FAMILY_PRESETS, FinetuneConfig  # noqa: E402
from core.geoai.finetune import formatting as F  # noqa: E402
from core.geoai.finetune import rewards as R  # noqa: E402

DATA_DIR = Path(FinetuneConfig().data_dir)
HAVE_DATA = all((DATA_DIR / f).exists() for f in ("sft_train.jsonl", "sft_val.jsonl", "eval_train.jsonl"))
BACKEND = Path(__file__).resolve().parent.parent

SYSTEM = {"role": "system", "content": "You are GeoAI."}


def _tool(name):
    return {"type": "function", "function": {"name": name, "description": "d", "parameters": {"type": "object", "properties": {}}}}


def _tool_row():
    return {
        "id": "correct_request-abc", "category": "correct_request", "split": "train",
        "messages": [SYSTEM, {"role": "user", "content": "Gmax for Vs 280 m/s and gamma 19.5 kN/m3"},
                     {"role": "assistant", "content": "", "tool_calls": [{"id": "c1", "type": "function", "function": {
                         "name": "calculate_gmax_from_shear_wave_velocity", "arguments": '{"Vs": 280, "gamma": 19.5}'}}]},
                     {"role": "tool", "name": "calculate_gmax_from_shear_wave_velocity", "tool_call_id": "c1",
                      "content": json.dumps({"status": "success", "result": {"Gmax [kPa]": 155918}})},
                     {"role": "assistant", "content": "Gmax = 155,918 kPa (calculated by Groundhog)."}],
        "tools": [_tool(f"distractor_{i}") for i in range(8)] + [_tool("calculate_gmax_from_shear_wave_velocity")],
    }


# ---------------- config ----------------

def test_config_defaults_target_t4_and_current_baseline():
    cfg = FinetuneConfig()
    assert cfg.family == "qwen2.5" and "Qwen2.5-1.5B-Instruct" in cfg.base_model_id
    assert cfg.resolved_load_in_4bit is True and cfg.max_seq_length == 4096
    assert cfg.lora_r == 16 and cfg.lora_alpha == 32 and "down_proj" in cfg.target_modules
    assert cfg.enable_thinking is False and cfg.plan_style == "brief" and cfg.max_tools == 5
    assert cfg.grpo_splits == ("train",)
    assert cfg.grpo_max_prompt_length + cfg.grpo_max_completion_length <= cfg.max_seq_length
    cfg.validate()


def test_family_presets_quantisation_and_thinking():
    assert FinetuneConfig(family="qwen3.5").resolved_load_in_4bit is False  # 16-bit LoRA for Qwen3.5
    assert FinetuneConfig(family="qwen3").chat_template_kwargs() == {"enable_thinking": False}
    assert FinetuneConfig(family="qwen3", enable_thinking=True).chat_template_kwargs() == {"enable_thinking": True}
    assert FinetuneConfig().chat_template_kwargs() == {}
    assert FinetuneConfig(family="qwen2.5", load_in_4bit=False).resolved_load_in_4bit is False
    assert {"qwen2.5", "qwen3", "qwen3.5", "gemma3"} <= set(FAMILY_PRESETS)


def test_config_validation_and_overrides(tmp_path):
    with pytest.raises(ValueError):
        FinetuneConfig(grpo_splits=("train", "test")).validate()
    with pytest.raises(ValueError):
        FinetuneConfig(family="nope").validate()
    cfg = FinetuneConfig().with_overrides({"lora_r": "32", "load_in_4bit": "false", "target_modules": "q_proj,v_proj",
                                           "max_tools": "none"})
    assert cfg.lora_r == 32 and cfg.load_in_4bit is False and cfg.target_modules == ("q_proj", "v_proj")
    assert cfg.max_tools is None
    with pytest.raises(ValueError):
        FinetuneConfig().with_overrides({"not_a_field": 1})
    cfg.save_json(tmp_path / "c.json")
    assert FinetuneConfig.load_json(tmp_path / "c.json") == cfg


# ---------------- imports without the GPU stack ----------------

def test_finetune_modules_import_without_torch():
    code = (
        "import sys, importlib.abc\n"
        "class Block(importlib.abc.MetaPathFinder):\n"
        "    def find_spec(self, name, path, target=None):\n"
        "        if name.split('.')[0] in {'torch','unsloth','trl','peft','transformers','datasets','vllm','bitsandbytes'}:\n"
        "            raise ImportError('blocked ' + name)\n"
        "sys.meta_path.insert(0, Block())\n"
        "import core.geoai.finetune, core.geoai.finetune.config, core.geoai.finetune.formatting\n"
        "import core.geoai.finetune.rewards, core.geoai.finetune.sft, core.geoai.finetune.grpo, core.geoai.finetune.export\n"
        "import core.geoai.finetune._hf, core.geoai.finetune.evaluate\n"
        "print('ok')\n"
    )
    r = subprocess.run([sys.executable, "-c", code], cwd=str(BACKEND), capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr
    assert "ok" in r.stdout


# ---------------- formatting ----------------

def test_prepare_sft_example_adds_plan_and_normalises():
    row = _tool_row()
    ex = F.prepare_sft_example(row, FinetuneConfig())
    decision = ex["messages"][2]
    assert decision["content"].startswith("Plan: call calculate_gmax_from_shear_wave_velocity with Vs, gamma")
    assert decision["tool_calls"][0]["function"]["arguments"] == {"Vs": 280, "gamma": 19.5}
    names = [t["function"]["name"] for t in ex["tools"]]
    assert len(names) == 5 and "calculate_gmax_from_shear_wave_velocity" in names  # called tool always kept
    assert row["messages"][2]["content"] == ""  # input not mutated
    assert F.validate_sft_example(ex) == []
    ex_none = F.prepare_sft_example(row, FinetuneConfig(plan_style="none", max_tools=None))
    assert ex_none["messages"][2]["content"] == "" and len(ex_none["tools"]) == 9


def test_plan_never_contains_numbers_and_is_short():
    ex = F.prepare_sft_example(_tool_row(), FinetuneConfig())
    plan = ex["messages"][2]["content"]
    assert not any(ch.isdigit() for ch in plan.replace("calculate_gmax", ""))
    assert len(plan.split()) <= F.PLAN_MAX_WORDS
    clar = {"id": "m", "category": "missing_data", "messages": [SYSTEM, {"role": "user", "content": "bearing capacity?"},
                                                               {"role": "assistant", "content": "Please provide phi."}],
            "tools": [_tool("x")]}
    c = F.prepare_sft_example(clar, FinetuneConfig())["messages"][2]["content"]
    assert c.startswith("Plan: a required input is missing") and c.endswith("Please provide phi.")


def test_validate_sft_example_catches_problems():
    row = _tool_row()
    ex = F.prepare_sft_example(row, FinetuneConfig(max_tools=None))
    ex["tools"] = [_tool("other")]
    ex["messages"][3]["tool_call_id"] = "zzz"
    probs = F.validate_sft_example(ex)
    assert any("not in the offered tools" in p for p in probs)
    assert any("without a matching tool call" in p for p in probs)


def test_reference_render_and_loss_mask():
    cfg = FinetuneConfig()
    ex = F.prepare_sft_example(_tool_row(), cfg)
    text = F.render_reference_chatml(ex["messages"], ex["tools"])
    assert "<tools>" in text and '<tool_call>\n{"name": "calculate_gmax_from_shear_wave_velocity"' in text
    spans = F.trainable_spans(text, cfg.preset.instruction_part, cfg.preset.response_part)
    assert len(spans) == 2
    assert "<tool_call>" in spans[0] and spans[0].startswith("Plan:")
    assert all("<tool_response>" not in s and "<tools>" not in s for s in spans)
    assert "Gmax = 155,918 kPa" in spans[1]


def test_held_out_files_and_examples_are_refused(tmp_path):
    for name in ("eval_test.jsonl", "eval_gold.jsonl"):
        with pytest.raises(ValueError):
            F.assert_trainable_file(tmp_path / name)
    F.assert_trainable_file(tmp_path / "sft_train.jsonl")
    with pytest.raises(ValueError):
        F.build_grpo_record({"id": "x", "split": "test", "messages": []}, None)


def test_build_grpo_record_final_answer_has_no_tools():
    ex = {"id": "a__final", "split": "train", "turn_type": "final_answer", "expected_action": "synthesize",
          "category": "correct_request", "messages": _tool_row()["messages"][1:4]}
    rec = F.build_grpo_record(ex, tools_for=lambda *a: [_tool("never")])
    assert rec["tools"] is None and rec["prompt"][0]["role"] == "system" and rec["prompt"][-1]["role"] == "tool"
    assert isinstance(rec["prompt"][2]["tool_calls"][0]["function"]["arguments"], dict)
    assert json.loads(rec["example"])["id"] == "a__final"


# ---------------- rewards ----------------

def test_format_score():
    good = 'Plan: call t with a from the request.\n<tool_call>\n{"name": "t", "arguments": {"a": 1}}\n</tool_call>'
    assert R.format_score(good) == 1.0
    assert R.format_score("") == 0.0
    assert R.format_score("<tool_call>{bad json</tool_call>") == 0.0
    assert R.format_score("<tool_call>{\"name\": \"t\"") == 0.0  # unterminated
    assert R.format_score(good + " and more chatter") == 0.75
    assert R.format_score('<tool_call>\n{"name": "t", "arguments": {}}\n</tool_call>') == 0.75  # no plan
    assert R.format_score("<think>long reasoning</think>" + good) == 0.5
    assert R.format_score("The result is 12 kPa.", turn_type="final_answer") == 1.0


def test_trl_style_reward_functions():
    from core.geoai.training.scaleup import gold_examples

    ex = next(e for e in gold_examples() if e.expected_action == "tool_call" and e.expected_arguments).to_dict()
    gold = F.gold_completion(ex)
    comps = [[{"role": "assistant", "content": gold}], [{"role": "assistant", "content": "This design is safe."}]]
    kw = {"example": [json.dumps(ex)] * 2, "turn_type": ["decision"] * 2}
    scores = R.geoai_reward(prompts=[None, None], completions=comps, **kw)
    assert scores[0] > 0.9 and scores[1] < 0.5
    fmt = R.make_format_reward()(prompts=[None, None], completions=comps, **kw)
    assert fmt[0] == 1.0 and fmt[1] == 0.75


def test_reward_separates_gold_from_bad_on_gold_set():
    from core.geoai.training.scaleup import gold_examples

    exs = [e.to_dict() for e in gold_examples()]
    rep = R.reward_sanity_check(exs)
    assert rep["n_examples"] >= 8
    assert rep["win_rate"] >= 0.9
    assert rep["mean_good"] - rep["mean_bad"] >= 0.3


# ---------------- dry runs on the generated data ----------------

@pytest.mark.skipif(not HAVE_DATA, reason="generated dataset not present (python -m core.geoai.training.scaleup)")
def test_sft_dry_run_passes():
    from core.geoai.finetune.sft import dry_run

    rep = dry_run(FinetuneConfig(), n=12, reward_examples=16)
    assert rep["ok"], json.dumps({k: v for k, v in rep.items() if k != "config"}, default=str)[:2000]
    assert rep["held_out_leakage"] == []
    assert rep["reward_check"]["win_rate"] >= 0.9


@pytest.mark.skipif(not HAVE_DATA, reason="generated dataset not present")
def test_grpo_dry_run_passes():
    from core.geoai.finetune.grpo import dry_run

    rep = dry_run(FinetuneConfig(), n=16)
    assert rep["ok"], json.dumps({k: v for k, v in rep.items() if k != "config"}, default=str)[:2000]
    assert rep["prompts"]["problems"] == []


# ---------------- export ----------------

def _report(mean, strict=0.5, halluc=0.1, lat=5.0, cat_pass=0.5):
    ids = {f"e{i}": [mean, True] for i in range(3)}
    return {"meta": {"label": "x", "split": "test"}, "per_example": ids,
            "metrics": {"n": 3, "mean_score": mean, "strict_pass_rate": strict, "hallucinated_parameter_rate": halluc,
                        "caution_violation_rate": 0.0, "error_rate": 0.0, "latency_p50_s": lat,
                        "per_category": {"correct_request": {"pass_rate": cat_pass}}}}


def test_go_no_go_rule():
    from core.geoai.finetune.export import go_no_go

    assert go_no_go(_report(0.60), _report(0.66, strict=0.55))["decision"] == "go"
    d = go_no_go(_report(0.60), _report(0.61))
    assert d["decision"] == "no-go" and any("mean_score" in f for f in d["failed"])
    assert go_no_go(_report(0.60), _report(0.70, halluc=0.2))["decision"] == "no-go"
    assert go_no_go(_report(0.60), _report(0.70, lat=9.0))["decision"] == "no-go"
    assert go_no_go(_report(0.60), _report(0.70, cat_pass=0.3))["decision"] == "no-go"


def test_sidecar_roundtrip_is_accepted_by_runtime_check(tmp_path):
    from core.geoai.finetune.export import annotate, build_sidecar, write_sidecar
    from core.geoai.lora_adapter import check_adapter_compatibility

    base = write_fake_base(tmp_path / "base.gguf")
    lora = write_fake_lora(tmp_path / "geoai-lora.gguf")
    adapter_dir = tmp_path / "adapter"
    adapter_dir.mkdir()
    FinetuneConfig().save_json(adapter_dir / "geoai_finetune_config.json")
    (adapter_dir / "geoai_run.json").write_text(json.dumps({
        "stage": "grpo", "base_model_id": "Qwen/Qwen2.5-1.5B-Instruct", "family": "qwen2.5",
        "chat_template": "native", "base_fingerprint_from_hf_config": {"architecture": "qwen2", "block_count": 28}}))
    sc = build_sidecar(lora, adapter_dir, base_gguf=base)
    write_sidecar(lora, sc)
    assert sc["base_gguf"]["fingerprint"]["block_count"] == 28 and sc["base_gguf"]["fingerprint_source"] == "base_gguf"
    assert sc["base_model_id"] == "Qwen/Qwen2.5-1.5B-Instruct" and sc["adapter_sha256"]
    assert check_adapter_compatibility(str(lora), str(base)).ok
    wrong = write_fake_base(tmp_path / "wrong.gguf", **{"qwen2.block_count": 36})
    assert not check_adapter_compatibility(str(lora), str(wrong)).ok

    (tmp_path / "b.json").write_text(json.dumps(_report(0.6)))
    (tmp_path / "c.json").write_text(json.dumps(_report(0.7, strict=0.6)))
    out = annotate(lora, tmp_path / "b.json", tmp_path / "c.json")
    assert out["eval"]["go_no_go"]["decision"] == "go"
    assert json.loads((tmp_path / "geoai-lora.gguf.json").read_text())["eval"]["adapter"]["mean_score"] == 0.7
