# Author: Utkarsh Gupta
# License: GPL v3
"""
Stage 1: supervised LoRA fine-tuning (Unsloth + TRL) on sft_train / sft_val.

* Each row (``messages`` + ``tools``) is rendered with the base model's own chat
  template (``tokenizer.apply_chat_template(messages, tools=tools)``), so the
  model learns the tool-call format its runtime template (llama.cpp "native"
  chat format) produces and parses.
* Loss is on assistant turns only (Unsloth ``train_on_responses_only``); tool
  results arrive as user-side ``<tool_response>`` turns and are masked.
* A one-line "Plan: ..." is prepended to each decision turn (``plan_style``);
  no long chain-of-thought (CPU inference budget). Thinking is off unless
  ``enable_thinking`` is set.
* Examples longer than ``max_seq_length`` are dropped, never truncated (a
  truncated example would lose its assistant target).

GPU (Colab/Kaggle T4):
    python -m core.geoai.finetune.sft --output-dir /content/geoai-ft
CPU check (local/CI, no torch needed):
    python -m core.geoai.finetune.sft --dry-run
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.geoai.finetune.config import FinetuneConfig, add_config_args, config_from_args
from core.geoai.finetune.formatting import (
    estimate_tokens,
    iter_jsonl,
    load_training_jsonl,
    prepare_sft_example,
    render_reference_chatml,
    trainable_spans,
    validate_sft_example,
)

SFT_FILES = ("sft_train.jsonl", "sft_val.jsonl")


def prepare_split(cfg: FinetuneConfig, filename: str, limit: Optional[int] = None) -> Tuple[List[Dict[str, Any]], Counter]:
    """Load, prepare and validate one SFT file. Returns (examples, drop_counter)."""
    rows = load_training_jsonl(Path(cfg.data_dir) / filename, limit)
    out: List[Dict[str, Any]] = []
    drops: Counter = Counter()
    for r in rows:
        ex = prepare_sft_example(r, cfg)
        problems = validate_sft_example(ex)
        if problems:
            drops["invalid:" + problems[0].split(":")[-1].strip()] += 1
            continue
        out.append(ex)
    return out, drops


def leakage_check(cfg: FinetuneConfig, train_ids: List[str]) -> List[str]:
    """IDs present in training data that also appear in the held-out eval_test split."""
    test_path = Path(cfg.data_dir) / "eval_test.jsonl"
    if not test_path.exists():
        return []
    held = set()
    for ex in iter_jsonl(test_path):
        held.add(ex.get("id"))
        parent = (ex.get("metadata") or {}).get("parent_id")
        if parent:
            held.add(parent)
    return sorted(set(train_ids) & held)


# =====================================================================
# Dry run (CPU, tokenizer-free)
# =====================================================================

def dry_run(cfg: FinetuneConfig, n: int = 64, reward_examples: int = 40) -> Dict[str, Any]:
    """
    Validate data formatting on N examples per SFT file with the reference
    (tokenizer-free) template, emulate assistant-only masking, estimate
    lengths, check for held-out leakage, and prove the reward separates gold
    from bad completions. Raises SystemExit(1) on failure.
    """
    from core.geoai.finetune.grpo import load_grpo_examples
    from core.geoai.finetune.rewards import reward_sanity_check

    report: Dict[str, Any] = {"stage": "sft", "config": cfg.to_dict(), "files": {}}
    ok = True
    all_ids: List[str] = []
    for fname in SFT_FILES:
        exs, drops = prepare_split(cfg, fname, n)
        lens, bad_mask, plans = [], 0, 0
        for ex in exs:
            text = render_reference_chatml(ex["messages"], ex["tools"])
            lens.append(estimate_tokens(text))
            spans = trainable_spans(text, cfg.preset.instruction_part, cfg.preset.response_part)
            targets_ok = bool(spans) and not any("<tool_response>" in s or "# Tools" in s for s in spans)
            called = [tc["function"]["name"] for m in ex["messages"] for tc in (m.get("tool_calls") or [])]
            if called and not any("<tool_call>" in s and called[0] in s for s in spans):
                targets_ok = False
            bad_mask += int(not targets_ok)
            plans += int(any((m.get("content") or "").startswith("Plan:") for m in ex["messages"] if m.get("role") == "assistant"))
            all_ids.append(ex["id"])
        over = sum(1 for x in lens if x > cfg.max_seq_length)
        rep = {"checked": len(exs) + sum(drops.values()), "valid": len(exs), "dropped_invalid": dict(drops),
               "bad_loss_mask": bad_mask, "with_plan": plans,
               "est_tokens_median": sorted(lens)[len(lens) // 2] if lens else None,
               "est_tokens_max": max(lens) if lens else None,
               "est_overlong": over}
        if exs:
            rep["sample_render_tail"] = render_reference_chatml(exs[0]["messages"], exs[0]["tools"])[-600:]
        report["files"][fname] = rep
        if bad_mask or drops or not exs:
            ok = False
    leaks = leakage_check(cfg, all_ids)
    report["held_out_leakage"] = leaks
    ok = ok and not leaks

    examples = load_grpo_examples(cfg, limit=reward_examples)
    sep = reward_sanity_check(examples, plan_style=cfg.plan_style, format_weight=cfg.grpo_format_reward_weight,
                              thinking=cfg.enable_thinking)
    report["reward_check"] = sep
    if not sep["n_examples"] or sep["win_rate"] < 0.9 or (sep["mean_good"] - sep["mean_bad"]) < 0.3:
        ok = False
    report["ok"] = ok
    return report


# =====================================================================
# Training (GPU; heavy imports are local)
# =====================================================================

def train(cfg: FinetuneConfig) -> Path:
    import torch  # noqa: F401  (fail fast with a clear error if the GPU stack is missing)
    from unsloth import FastLanguageModel  # must be imported before trl/transformers
    from unsloth.chat_templates import train_on_responses_only
    from datasets import Dataset
    from trl import SFTConfig, SFTTrainer

    from core.geoai.finetune._hf import base_dims_from_hf_config, check_template, data_fingerprint, filter_kwargs, write_run_info

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=cfg.base_model, max_seq_length=cfg.max_seq_length,
        load_in_4bit=cfg.resolved_load_in_4bit, dtype=None)

    train_ex, train_drops = prepare_split(cfg, "sft_train.jsonl", cfg.max_train_examples)
    val_ex, val_drops = prepare_split(cfg, "sft_val.jsonl")
    check_template(tokenizer, cfg, next(e for e in train_ex if any(m.get("tool_calls") for m in e["messages"])))

    def render(exs: List[Dict[str, Any]]) -> Tuple[List[Dict[str, str]], int]:
        rows, overlong = [], 0
        for e in exs:
            text = tokenizer.apply_chat_template(e["messages"], tools=e["tools"] or None, tokenize=False,
                                                 **cfg.chat_template_kwargs())
            n_tok = len(tokenizer(text, add_special_tokens=False)["input_ids"])
            if n_tok > cfg.max_seq_length:
                overlong += 1
                if cfg.drop_overlong:
                    continue
            rows.append({"text": text})
        return rows, overlong

    train_rows, train_over = render(train_ex)
    val_rows, val_over = render(val_ex)
    print(f"SFT rows: train={len(train_rows)} (overlong {train_over}) val={len(val_rows)} (overlong {val_over})", flush=True)

    model = FastLanguageModel.get_peft_model(
        model, r=cfg.lora_r, lora_alpha=cfg.lora_alpha, lora_dropout=cfg.lora_dropout,
        target_modules=list(cfg.target_modules), bias="none", use_gradient_checkpointing="unsloth",
        random_state=cfg.seed, use_rslora=cfg.use_rslora)

    args = SFTConfig(**filter_kwargs(SFTConfig, dict(
        output_dir=str(Path(cfg.output_dir) / "sft_checkpoints"),
        dataset_text_field="text", max_seq_length=cfg.max_seq_length, packing=False,
        per_device_train_batch_size=cfg.per_device_train_batch_size,
        gradient_accumulation_steps=cfg.gradient_accumulation_steps,
        num_train_epochs=cfg.num_train_epochs, learning_rate=cfg.learning_rate,
        warmup_ratio=cfg.warmup_ratio, weight_decay=cfg.weight_decay, lr_scheduler_type=cfg.lr_scheduler_type,
        optim=cfg.optim, logging_steps=cfg.logging_steps, eval_strategy="steps", eval_steps=cfg.eval_steps,
        save_strategy="no", seed=cfg.seed, report_to=cfg.report_to,
    ), renames={"max_seq_length": "max_length", "eval_strategy": "evaluation_strategy"}))
    trainer = SFTTrainer(**filter_kwargs(SFTTrainer, dict(
        model=model, processing_class=tokenizer, train_dataset=Dataset.from_list(train_rows),
        eval_dataset=Dataset.from_list(val_rows) if val_rows else None, args=args,
    ), renames={"processing_class": "tokenizer"}))
    trainer = train_on_responses_only(trainer, instruction_part=cfg.preset.instruction_part,
                                      response_part=cfg.preset.response_part)
    result = trainer.train()
    metrics = trainer.evaluate() if val_rows else {}

    out = cfg.sft_dir
    model.save_pretrained(str(out))
    tokenizer.save_pretrained(str(out))
    write_run_info(out, cfg, {
        "stage": "sft", "base_model": cfg.base_model, "base_model_id": cfg.base_model_id, "family": cfg.family,
        "base_fingerprint_from_hf_config": base_dims_from_hf_config(model, cfg),
        "data": data_fingerprint(Path(cfg.data_dir), list(SFT_FILES)),
        "rows": {"train": len(train_rows), "val": len(val_rows), "train_overlong": train_over, "val_overlong": val_over,
                 "dropped_invalid": dict(train_drops + val_drops)},
        "train_metrics": getattr(result, "metrics", {}), "eval_metrics": metrics,
        "chat_template": cfg.chat_template, "plan_style": cfg.plan_style, "enable_thinking": cfg.enable_thinking,
    })
    print(f"Saved SFT adapter to {out}", flush=True)
    return out


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="GeoAI SFT (LoRA) with Unsloth + TRL.")
    add_config_args(ap)
    ap.add_argument("--dry-run", action="store_true", help="CPU-only data/template/reward checks; no training")
    ap.add_argument("--n", type=int, default=64, help="Examples per file checked in --dry-run")
    ap.add_argument("--json", action="store_true", help="Print the dry-run report as JSON")
    args = ap.parse_args(argv)
    cfg = config_from_args(args)
    if args.dry_run:
        rep = dry_run(cfg, n=args.n)
        print(json.dumps(rep, indent=2, default=str) if args.json else summarise_dry_run(rep))
        return 0 if rep["ok"] else 1
    train(cfg)
    return 0


def summarise_dry_run(rep: Dict[str, Any]) -> str:
    lines = [f"[{rep['stage']} dry-run] {'OK' if rep['ok'] else 'FAILED'}"]
    for f, r in rep.get("files", {}).items():
        lines.append(f"  {f}: valid {r['valid']}/{r['checked']} bad_mask={r['bad_loss_mask']} with_plan={r['with_plan']} "
                     f"est_tokens median={r['est_tokens_median']} max={r['est_tokens_max']} overlong={r['est_overlong']} "
                     f"dropped={r['dropped_invalid']}")
    for k in ("prompts", "held_out_leakage"):
        if k in rep:
            lines.append(f"  {k}: {rep[k]}")
    s = rep.get("reward_check", {})
    if s:
        lines.append(f"  reward: n={s['n_examples']} mean_good={s['mean_good']} mean_bad={s['mean_bad']} "
                     f"min_good={s['min_good']} max_bad={s['max_bad']} win_rate={s['win_rate']} (max {s['max_reward']})")
        lines.append(f"  mean bad reward by kind: {s['mean_bad_by_kind']}")
        if s.get("failures"):
            lines.append(f"  not separated: {s['failures']}")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
