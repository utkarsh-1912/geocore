# Author: Utkarsh Gupta
# License: GPL v3
"""
Stage 2: GRPO with verifiable rewards, starting from the SFT LoRA adapter.

* Prompts: ``eval_train.jsonl`` (``grpo_splits``; held-out test/gold are refused)
  rendered exactly like the runtime agent builds them - system prompt from
  ``build_system_prompt``, the same tool subset logic as the SFT data (capped at
  ``max_tools``), the model's own chat template with the thinking switch from
  the config. Final-answer turns carry the real tool result and no tools.
* Reward: ``core.geoai.eval.scoring.reward`` (deterministic scorer, weight 1.0)
  + ``format_reward`` (weight ``grpo_format_reward_weight``), see rewards.py.
* Rollouts: plain HF generation by default (works on a T4). Optional
  ``--set grpo_use_vllm=true`` loads the model with Unsloth ``fast_inference``
  (vLLM) for much faster rollouts at the cost of extra VRAM/installs - not
  required.

GPU:  python -m core.geoai.finetune.grpo --output-dir /content/geoai-ft
CPU:  python -m core.geoai.finetune.grpo --dry-run
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.geoai.finetune.config import HELD_OUT_SPLITS, FinetuneConfig, add_config_args, config_from_args
from core.geoai.finetune.formatting import (
    build_grpo_record,
    estimate_tokens,
    eval_decision_kind,
    iter_jsonl,
    oversample,
    registry_tools_for,
    render_reference_chatml,
)


def load_grpo_examples(cfg: FinetuneConfig, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Eval examples used as GRPO prompts (deterministic, evenly spread subset when ``limit`` is set)."""
    out: List[Dict[str, Any]] = []
    for split in cfg.grpo_splits:
        if split in HELD_OUT_SPLITS:
            raise ValueError(f"refusing to build GRPO prompts from held-out split '{split}'")
        path = Path(cfg.data_dir) / f"eval_{split}.jsonl"
        for ex in iter_jsonl(path):
            if ex.get("turn_type", "decision") in cfg.grpo_turn_types:
                out.append(ex)
    if limit is not None and limit < len(out):
        out = sorted(out, key=lambda e: e.get("id") or "")
        step = len(out) / float(limit)
        out = [out[int(i * step)] for i in range(limit)]
    return out


def grpo_prompt_mix(cfg: FinetuneConfig) -> Dict[str, Any]:
    """Category mix of all GRPO prompts before/after ``grpo_category_weights`` (no tool schemas built)."""
    _, report = oversample(load_grpo_examples(cfg), cfg.grpo_category_weights, seed=cfg.seed,
                           kind_fn=eval_decision_kind)
    return report


def build_grpo_records(cfg: FinetuneConfig, limit: Optional[int] = None) -> Dict[str, Any]:
    """Build prompt records; drops prompts whose estimated length exceeds grpo_max_prompt_length."""
    examples = load_grpo_examples(cfg, limit)
    tools_for, ctx = registry_tools_for()
    records, dropped = [], Counter()
    with ctx:
        for ex in examples:
            rec = build_grpo_record(ex, tools_for, max_tools=cfg.max_tools)
            n = estimate_tokens(render_reference_chatml(rec["prompt"], rec["tools"]))
            if n > cfg.grpo_max_prompt_length:
                dropped["prompt_too_long"] += 1
                continue
            rec["est_prompt_tokens"] = n
            records.append(rec)
    return {"records": records, "dropped": dict(dropped)}


def dry_run(cfg: FinetuneConfig, n: int = 64) -> Dict[str, Any]:
    """Build N GRPO prompts (CPU), check them, and prove the reward separates gold from bad completions."""
    from core.geoai.finetune.rewards import reward_sanity_check

    built = build_grpo_records(cfg, limit=n)
    recs = built["records"]
    problems = []
    for r in recs:
        ex = json.loads(r["example"])
        if ex.get("split") in HELD_OUT_SPLITS:
            problems.append(f"{r['id']}: held-out split")
        if r["turn_type"] == "decision":
            names = [t["function"]["name"] for t in r["tools"] or []]
            if ex.get("expected_tool") and ex["expected_tool"] not in names:
                problems.append(f"{r['id']}: expected tool not offered")
            prefix = [tc.get("function", tc).get("name") for m in ex.get("messages") or [] for tc in (m.get("tool_calls") or [])]
            if any(p not in names for p in prefix):
                problems.append(f"{r['id']}: a tool called earlier in the prefix is not offered")
        if r["prompt"][0]["role"] != "system" or r["prompt"][-1]["role"] not in ("user", "tool"):
            problems.append(f"{r['id']}: prompt does not end with a user/tool turn")
    lens = sorted(r["est_prompt_tokens"] for r in recs)
    examples = [json.loads(r["example"]) for r in recs]
    sep = reward_sanity_check(examples, plan_style=cfg.plan_style, format_weight=cfg.grpo_format_reward_weight,
                              thinking=cfg.enable_thinking)
    ok = bool(recs) and not problems and sep["n_examples"] > 0 and sep["win_rate"] >= 0.9 \
        and (sep["mean_good"] - sep["mean_bad"]) >= 0.3
    return {
        "stage": "grpo", "ok": ok, "config": cfg.to_dict(),
        "prompts": {"built": len(recs), "dropped": built["dropped"], "problems": problems[:10],
                    "turn_types": dict(Counter(r["turn_type"] for r in recs)),
                    "format_turns": dict(Counter(r["format_turn"] for r in recs)),
                    "est_prompt_tokens_median": lens[len(lens) // 2] if lens else None,
                    "est_prompt_tokens_max": lens[-1] if lens else None},
        "reward_check": sep,
        "prompt_mix": grpo_prompt_mix(cfg),
    }


def train(cfg: FinetuneConfig, sft_adapter: Optional[Path] = None) -> Path:
    import torch  # noqa: F401
    from unsloth import FastLanguageModel  # before trl/transformers
    from datasets import Dataset
    from trl import GRPOConfig, GRPOTrainer

    from core.geoai.finetune._hf import data_fingerprint, filter_kwargs, read_run_info, write_run_info
    from core.geoai.finetune.rewards import geoai_reward, make_format_reward

    adapter = Path(sft_adapter or cfg.sft_dir)
    if not (adapter / "adapter_config.json").is_file():
        raise FileNotFoundError(f"SFT adapter not found at {adapter}; run core.geoai.finetune.sft first")
    load_kw = dict(model_name=str(adapter), max_seq_length=cfg.max_seq_length,
                   load_in_4bit=cfg.resolved_load_in_4bit, dtype=None)
    if cfg.grpo_use_vllm:
        load_kw.update(fast_inference=True, max_lora_rank=cfg.lora_r,
                       gpu_memory_utilization=cfg.grpo_gpu_memory_utilization)
    model, tokenizer = FastLanguageModel.from_pretrained(**load_kw)
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    if trainable == 0:
        raise RuntimeError("Loaded SFT adapter has no trainable parameters; cannot continue with GRPO.")

    built = build_grpo_records(cfg)
    # Same clarification emphasis as SFT: repeat weighted prompts (seeded, deterministic).
    records, mix = oversample(built["records"], cfg.grpo_category_weights, seed=cfg.seed,
                              kind_fn=lambda r: r["decision_kind"])
    from core.geoai.finetune.sft import format_mix
    print(f"GRPO prompt oversampling: {format_mix(mix)}", flush=True)
    rendered: Dict[str, str] = {}
    rows = []
    for r in records:
        if r["id"] not in rendered:
            rendered[r["id"]] = tokenizer.apply_chat_template(
                r["prompt"], tools=r["tools"] or None, tokenize=False, add_generation_prompt=True,
                **cfg.chat_template_kwargs())
        prompt = rendered[r["id"]]
        rows.append({"prompt": prompt, "example": r["example"], "turn_type": r["turn_type"],
                     "format_turn": r["format_turn"]})
    print(f"GRPO prompts: {len(rows)} (dropped {built['dropped']}) trainable params={trainable:,}", flush=True)

    args = GRPOConfig(**filter_kwargs(GRPOConfig, dict(
        output_dir=str(Path(cfg.output_dir) / "grpo_checkpoints"),
        learning_rate=cfg.grpo_learning_rate, max_steps=cfg.grpo_max_steps,
        per_device_train_batch_size=cfg.grpo_per_device_batch_size,
        gradient_accumulation_steps=cfg.grpo_gradient_accumulation_steps,
        num_generations=cfg.grpo_num_generations, max_prompt_length=cfg.grpo_max_prompt_length,
        max_completion_length=cfg.grpo_max_completion_length, temperature=cfg.grpo_temperature,
        beta=cfg.grpo_beta, reward_weights=[1.0, cfg.grpo_format_reward_weight], use_vllm=cfg.grpo_use_vllm,
        optim=cfg.optim, lr_scheduler_type=cfg.lr_scheduler_type, warmup_ratio=cfg.warmup_ratio,
        logging_steps=cfg.logging_steps, save_strategy="no", seed=cfg.seed, report_to=cfg.report_to,
    )))
    trainer = GRPOTrainer(**filter_kwargs(GRPOTrainer, dict(
        model=model, processing_class=tokenizer,
        reward_funcs=[geoai_reward, make_format_reward(cfg.plan_style, cfg.enable_thinking)],
        args=args, train_dataset=Dataset.from_list(rows),
    ), renames={"processing_class": "tokenizer"}))
    result = trainer.train()

    out = cfg.grpo_dir
    model.save_pretrained(str(out))
    tokenizer.save_pretrained(str(out))
    sft_info = read_run_info(adapter)
    write_run_info(out, cfg, {
        **{k: v for k, v in sft_info.items() if k not in ("stage", "train_metrics", "eval_metrics")},
        "stage": "grpo", "sft_adapter": str(adapter), "sft_run": sft_info,
        "grpo_data": data_fingerprint(Path(cfg.data_dir), [f"eval_{s}.jsonl" for s in cfg.grpo_splits]),
        "grpo_prompts": len(rows), "prompt_mix": mix, "train_metrics": getattr(result, "metrics", {}),
    })
    print(f"Saved GRPO adapter to {out}", flush=True)
    return out


def main(argv: Optional[List[str]] = None) -> int:
    from core.geoai.finetune.sft import summarise_dry_run

    ap = argparse.ArgumentParser(description="GeoAI GRPO (verifiable GeoAI scorer reward) from the SFT adapter.")
    add_config_args(ap)
    ap.add_argument("--sft-adapter", type=Path, help="SFT adapter dir (default: <output-dir>/sft_adapter)")
    ap.add_argument("--dry-run", action="store_true", help="CPU-only prompt/reward checks; no training")
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    cfg = config_from_args(args)
    if args.dry_run:
        rep = dry_run(cfg, n=args.n)
        print(json.dumps(rep, indent=2, default=str) if args.json else summarise_dry_run(rep))
        return 0 if rep["ok"] else 1
    train(cfg, args.sft_adapter)
    return 0


if __name__ == "__main__":
    sys.exit(main())
