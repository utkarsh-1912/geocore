"""Fine-tuning run profiles, clarification oversampling and multi-turn / project-context formatting (no torch)."""
import argparse
import json
import os
import sys
from collections import Counter

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from gguf_fixtures import write_gguf, write_fake_lora  # noqa: E402

from core.geoai.finetune import formatting as F  # noqa: E402
from core.geoai.finetune import rewards as R  # noqa: E402
from core.geoai.finetune.config import (  # noqa: E402
    DEFAULT_CATEGORY_WEIGHTS,
    DEFAULT_PROFILE,
    PROFILES,
    FinetuneConfig,
    add_config_args,
    config_from_args,
    validate_category_weights,
    weight_for,
)

QWEN3_SHA = "b139949c5bd74937ad8ed8c8cf3d9ffb1e99c866c823204dc42c0d91fa181897"


# ---------------- profiles ----------------

def test_qwen3_1p7b_profile_is_default_and_complete():
    assert DEFAULT_PROFILE == "qwen3-1.7b"
    cfg = FinetuneConfig.from_profile("qwen3-1.7b").validate()
    assert cfg.base_model == "unsloth/Qwen3-1.7B" and cfg.base_model_id == "Qwen/Qwen3-1.7B"
    assert cfg.family == "qwen3" and cfg.enable_thinking is False
    assert cfg.chat_template_kwargs() == {"enable_thinking": False}
    assert cfg.target_gguf_repo == "unsloth/Qwen3-1.7B-GGUF"
    assert cfg.target_gguf_filename == "Qwen3-1.7B-Q4_K_M.gguf" and cfg.target_gguf_sha256 == QWEN3_SHA
    assert cfg.target_gguf_fingerprint["architecture"] == cfg.preset.llama_cpp_arch == "qwen3"
    assert FinetuneConfig() == cfg


def test_other_profiles_still_work():
    q = FinetuneConfig.from_profile("qwen2.5-1.5b").validate()
    assert q.family == "qwen2.5" and q.chat_template_kwargs() == {}
    assert q.target_gguf_fingerprint["architecture"] == "qwen2"
    for name in PROFILES:
        c = FinetuneConfig.from_profile(name).validate()
        assert c.target_gguf_fingerprint["architecture"] == c.preset.llama_cpp_arch
    with pytest.raises(ValueError):
        FinetuneConfig.from_profile("nope")
    # profile dicts are never shared/mutated through a config
    c = FinetuneConfig.from_profile("qwen3-1.7b")
    c.target_gguf_fingerprint["block_count"] = 1
    assert PROFILES["qwen3-1.7b"]["target_gguf_fingerprint"]["block_count"] == 28


def test_non_qwen_families_have_a_working_profile():
    # The point of this test: fine-tuning is not Qwen-only. One profile per non-Qwen family
    # already offered in model_downloader.RECOMMENDED_MODELS / eval.benchmark.CANDIDATES.
    expected = {
        "phi-4-mini-instruct": "phi3",
        "granite-4.1-3b": "granite",
        "smollm3-3b": "smollm3",
        "llama-3.2-3b-instruct": "llama3",
        "mistral-7b-instruct-v0.3": "mistral",
    }
    for profile_name, family in expected.items():
        cfg = FinetuneConfig.from_profile(profile_name).validate()
        assert cfg.family == family
        assert cfg.preset.template_supports_tools is True
        assert cfg.target_gguf_fingerprint["architecture"] == cfg.preset.llama_cpp_arch
        # every profile's loss-masking markers must be non-empty and distinct
        assert cfg.preset.instruction_part and cfg.preset.response_part
        assert cfg.preset.instruction_part != cfg.preset.response_part


def _args(*argv):
    ap = argparse.ArgumentParser()
    add_config_args(ap)
    return ap.parse_args(list(argv))


def test_cli_profile_selection_and_identity_override():
    assert config_from_args(_args()).profile == "qwen3-1.7b"
    assert config_from_args(_args("--profile", "qwen2.5-1.5b")).family == "qwen2.5"
    bare = config_from_args(_args("--profile", "none"))
    assert bare.profile == "qwen3-1.7b"  # dataclass defaults are the default profile
    other = config_from_args(_args("--base-model", "unsloth/Qwen3-4B", "--base-model-id", "Qwen/Qwen3-4B"))
    assert other.profile is None and other.target_gguf_sha256 is None and other.target_gguf_fingerprint is None


def test_legacy_config_json_gets_no_invented_target(tmp_path):
    p = tmp_path / "old.json"
    p.write_text(json.dumps({"base_model": "unsloth/Qwen2.5-1.5B-Instruct", "family": "qwen2.5"}))
    cfg = FinetuneConfig.load_json(p)
    assert cfg.profile is None and cfg.target_gguf_filename is None and cfg.family == "qwen2.5"
    cfg2 = FinetuneConfig.from_profile("qwen3-1.7b")
    cfg2.save_json(tmp_path / "new.json")
    assert FinetuneConfig.load_json(tmp_path / "new.json") == cfg2


def test_sidecar_uses_profile_target_gguf(tmp_path):
    from core.geoai.finetune.export import build_sidecar
    from core.geoai.lora_adapter import check_adapter_compatibility

    lora = write_fake_lora(tmp_path / "geoai-lora.gguf", arch="qwen3", n_embd=2048)
    adapter_dir = tmp_path / "adapter"
    adapter_dir.mkdir()
    FinetuneConfig.from_profile("qwen3-1.7b").save_json(adapter_dir / "geoai_finetune_config.json")
    sc = build_sidecar(lora, adapter_dir)
    assert sc["profile"] == "qwen3-1.7b"
    assert sc["base_gguf"]["fingerprint_source"] == "profile" and sc["base_gguf"]["sha256"] == QWEN3_SHA
    assert sc["base_gguf"]["repo"] == "unsloth/Qwen3-1.7B-GGUF"
    with open(str(lora) + ".json", "w", encoding="utf-8") as f:
        json.dump(sc, f)
    fp = PROFILES["qwen3-1.7b"]["target_gguf_fingerprint"]
    base_meta = {"general.architecture": "qwen3", "general.type": "model", "general.basename": fp["basename"]}
    base_meta.update({f"qwen3.{k}": v for k, v in fp.items() if k not in ("architecture", "vocab_size", "basename", "size_label")})
    good = write_gguf(tmp_path / "Qwen3-1.7B-Q4_K_M.gguf", base_meta)
    chk = check_adapter_compatibility(str(lora), str(good))
    assert chk.ok, chk.reason
    wrong = write_gguf(tmp_path / "Qwen3-4B.gguf", dict(base_meta, **{"qwen3.embedding_length": 2560}))
    assert not check_adapter_compatibility(str(lora), str(wrong)).ok


# ---------------- category weights / oversampling ----------------

def test_default_weights_emphasise_clarification():
    w = DEFAULT_CATEGORY_WEIGHTS
    for cat in ("missing_data", "ambiguous_request", "conflicting_data", "tool_failure"):
        assert 1.5 <= w[cat] <= 2.0
    assert weight_for(w, "correct_request", "tool_call") == 1.0
    assert weight_for(w, "wrong_units", "text") == 1.5 and weight_for(w, "wrong_units", "tool_call") == 1.0
    assert weight_for({"missing_data": 2.0, "missing_data:text": 3.0}, "missing_data", "text") == 3.0
    assert weight_for({}, "missing_data", "text") == 1.0
    cfg = FinetuneConfig()
    assert cfg.sft_category_weights == w and cfg.grpo_category_weights == w
    validate_category_weights(w)
    for bad in ({"not_a_category": 2}, {"missing_data:maybe": 2}, {"missing_data": -1}, {"missing_data": "x"}):
        with pytest.raises(ValueError):
            validate_category_weights(bad)
    with pytest.raises(ValueError):
        FinetuneConfig(sft_category_weights={"bogus": 2.0}).validate()
    assert FinetuneConfig().with_overrides({"sft_category_weights": "{}"}).sft_category_weights == {}


def _items(n_per_cat=100):
    out = []
    for cat in ("correct_request", "missing_data", "conflicting_data", "research"):
        for i in range(n_per_cat):
            out.append({"id": f"{cat}-{i}", "category": cat})
    return out


def test_oversample_is_deterministic_and_weighted():
    items = _items()
    w = {"missing_data": 2.0, "conflicting_data": 1.5}
    a, rep = F.oversample(items, w, seed=7, kind_fn=lambda it: None)
    b, _ = F.oversample(items, w, seed=7, kind_fn=lambda it: None)
    assert [x["id"] for x in a] == [x["id"] for x in b]
    c, _ = F.oversample(items, w, seed=8, kind_fn=lambda it: None)
    assert [x["id"] for x in a] != [x["id"] for x in c]
    by = rep["by_category"]
    assert by["missing_data"] == {"before": 100, "after": 200}
    assert by["correct_request"]["after"] == 100 and by["research"]["after"] == 100
    assert 35 <= by["conflicting_data"]["after"] - 100 <= 65  # ~half get a second copy
    counts = Counter(x["id"] for x in a)
    assert set(counts.values()) <= {1, 2} and len(counts) == len(items)
    # the fractional extra copy depends on the id, not on input order
    rev, _ = F.oversample(list(reversed(items)), w, seed=7, kind_fn=lambda it: None)
    assert Counter(x["id"] for x in rev) == counts


def test_oversample_decision_kind_keys():
    rows = [{"id": "u1", "category": "wrong_units", "messages": [
                {"role": "system", "content": ""}, {"role": "user", "content": "gamma = 18 kPa"},
                {"role": "assistant", "content": "That is a pressure, not a unit weight. Please confirm."}]},
            {"id": "u2", "category": "wrong_units", "messages": [
                {"role": "system", "content": ""}, {"role": "user", "content": "B = 1500 mm"},
                {"role": "assistant", "content": "", "tool_calls": [{"id": "c", "function": {"name": "t", "arguments": {}}}]}]}]
    out, rep = F.oversample(rows, {"wrong_units:text": 2.0}, seed=1, kind_fn=F.sft_decision_kind)
    assert Counter(r["id"] for r in out) == {"u1": 2, "u2": 1}
    assert F.eval_decision_kind({"expected_action": "clarify"}) == "text"
    assert F.eval_decision_kind({"expected_action": "tool_call"}) == "tool_call"


def test_train_val_disjoint_guard():
    F.assert_disjoint(["a", "b"], ["c"])
    with pytest.raises(ValueError):
        F.assert_disjoint(["a", "b"], ["b"])


# ---------------- multi-turn trajectories with project context ----------------

PROJECT_CTX = {"project_context": "## Project\n| CPT | depth |\n| CPT-01 | 0-22 m |"}


def _trajectory_row():
    from core.geoai.system_prompt import build_system_prompt

    def call(cid, name, args):
        return {"role": "assistant", "content": "",
                "tool_calls": [{"id": cid, "type": "function", "function": {"name": name, "arguments": args}}]}

    def result(cid, name, payload):
        return {"role": "tool", "name": name, "tool_call_id": cid, "content": json.dumps({"status": "success", "result": payload})}

    msgs = [{"role": "system", "content": build_system_prompt(PROJECT_CTX)},
            {"role": "user", "content": "Pile capacity from the deepest CPT in the project, 0.6 m diameter, 18 m long."},
            call("call_x_1", "list_project_cpts", {}), result("call_x_1", "list_project_cpts", {"count": 1}),
            call("call_x_2", "summarize_project_cpt", {"cpt_id": "CPT-01"}), result("call_x_2", "summarize_project_cpt", {"layers": 3}),
            call("call_x_3", "calculate_pile_capacity_from_project_cpt", {"cpt_id": "CPT-01", "diameter": 0.6, "length": 18}),
            result("call_x_3", "calculate_pile_capacity_from_project_cpt", {"Rc [kN]": 2100.0}),
            {"role": "assistant", "content": "Using CPT-01 (from the project): Rc = 2100 kN (LCPC)."}]
    tools = [{"type": "function", "function": {"name": n, "description": "d", "parameters": {"type": "object", "properties": {}}}}
             for n in ["d1", "d2", "d3", "d4", "list_project_cpts", "summarize_project_cpt",
                       "calculate_pile_capacity_from_project_cpt"]]
    return {"id": "correct_request-traj", "category": "correct_request", "split": "train", "messages": msgs, "tools": tools}


def test_multiturn_sft_row_formats_and_masks_correctly():
    cfg = FinetuneConfig()
    ex = F.prepare_sft_example(_trajectory_row(), cfg)
    assert F.validate_sft_example(ex) == []
    names = {t["function"]["name"] for t in ex["tools"]}
    assert {"list_project_cpts", "summarize_project_cpt", "calculate_pile_capacity_from_project_cpt"} <= names
    assistants = [m for m in ex["messages"] if m["role"] == "assistant"]
    assert assistants[0]["content"].startswith("Plan: call list_project_cpts") and "project context" in assistants[0]["content"]
    assert all(not (m.get("content") or "").startswith("Plan:") for m in assistants[1:])  # plan only on the first decision
    text = F.render_reference_chatml(ex["messages"], ex["tools"])
    assert "### CURRENT CONTEXT" in text and "CPT-01 | 0-22 m" in text
    spans = F.trainable_spans(text, cfg.preset.instruction_part, cfg.preset.response_part)
    assert len(spans) == 4  # three tool-call turns + final answer
    assert all("<tool_response>" not in s and "CURRENT CONTEXT" not in s for s in spans)
    for name, s in zip(["list_project_cpts", "summarize_project_cpt", "calculate_pile_capacity_from_project_cpt"], spans):
        assert f'"name": "{name}"' in s
    assert F.sft_decision_kind(ex) == "tool_call"


def test_multiturn_step_prompt_offers_prefix_tools_and_has_no_plan():
    row = _trajectory_row()
    step = {"id": "correct_request-traj__step3", "split": "train", "category": "correct_request",
            "turn_type": "decision", "expected_action": "tool_call", "context": PROJECT_CTX,
            "expected_tool": "calculate_pile_capacity_from_project_cpt",
            "expected_arguments": {"cpt_id": "CPT-01", "diameter": 0.6, "length": 18},
            "messages": row["messages"][1:6]}
    seen = {}

    def tools_for(prompt, context, expected_tool, also=()):
        seen["also"] = list(also)
        return [{"type": "function", "function": {"name": n}} for n in ["a", "b", "c", "d", "e", expected_tool, *also]]

    rec = F.build_grpo_record(step, tools_for, max_tools=5)
    names = [t["function"]["name"] for t in rec["tools"]]
    assert seen["also"] == ["list_project_cpts", "summarize_project_cpt"]
    assert {"calculate_pile_capacity_from_project_cpt", "list_project_cpts", "summarize_project_cpt"} <= set(names)
    assert rec["format_turn"] == "step" and rec["prompt"][-1]["role"] == "tool"
    assert "### CURRENT CONTEXT" in rec["prompt"][0]["content"]
    gold = F.gold_completion(step)
    assert gold.startswith("<tool_call>")  # later steps carry no plan line
    assert R.format_score(gold, turn_type="step") == 1.0
    first = dict(step, messages=row["messages"][1:2], expected_tool="list_project_cpts", expected_arguments={},
                 id="correct_request-traj")
    assert F.format_turn_of(first) == "decision"
    assert F.gold_completion(first).startswith("Plan: call list_project_cpts") and "project context" in F.gold_completion(first)
    fmt = R.make_format_reward()(prompts=[None], completions=[gold], format_turn=["step"], turn_type=["decision"])
    assert fmt == [1.0]
