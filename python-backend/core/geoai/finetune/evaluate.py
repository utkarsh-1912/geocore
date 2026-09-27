# Author: Utkarsh Gupta
# License: GPL v3
"""
Quick GPU sanity evaluation of a PEFT adapter (or the base model) during training.

Generates one turn per example with the same prompts GRPO uses, scores it with
``core.geoai.eval.scoring.score_turn`` and reports mean score / strict pass
rate. Uses ``eval_val`` by default - never ``eval_test`` (the held-out split is
reserved for the real go/no-go evaluation with ``core.geoai.eval.runner`` on
the exported GGUF, on the desktop CPU runtime).

    python -m core.geoai.finetune.evaluate --adapter-dir /content/geoai-ft/sft_adapter --n 40
    python -m core.geoai.finetune.evaluate --base --n 40
"""

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.geoai.finetune.config import FinetuneConfig, add_config_args, config_from_args


def quick_eval(cfg: FinetuneConfig, adapter_dir: Optional[Path], n: int = 40, split: str = "val",
               max_new_tokens: int = 256) -> Dict[str, Any]:
    from unsloth import FastLanguageModel

    from core.geoai.eval.scoring import score_turn
    from core.geoai.finetune.grpo import build_grpo_records

    if split in ("test", "gold"):
        raise ValueError("quick_eval is a training-time check; use core.geoai.eval.runner for held-out splits")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(adapter_dir) if adapter_dir else cfg.base_model, max_seq_length=cfg.max_seq_length,
        load_in_4bit=cfg.resolved_load_in_4bit, dtype=None)
    FastLanguageModel.for_inference(model)
    recs = build_grpo_records(replace(cfg, grpo_splits=(split,)), limit=n)["records"]
    by_cat: Dict[str, List[float]] = defaultdict(list)
    totals, passes, samples = [], 0, []
    for r in recs:
        prompt = tokenizer.apply_chat_template(r["prompt"], tools=r["tools"] or None, tokenize=False,
                                               add_generation_prompt=True, **cfg.chat_template_kwargs())
        ids = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(model.device)
        out = model.generate(**ids, max_new_tokens=max_new_tokens, do_sample=False)
        text = tokenizer.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True)
        sb = score_turn(json.loads(r["example"]), text)
        totals.append(sb.total)
        passes += int(sb.passed)
        by_cat[r["category"]].append(sb.total)
        if len(samples) < 5:
            samples.append({"id": r["id"], "score": sb.total, "text": text[:300], "reasons": sb.reasons[:3]})
    n_done = len(totals) or 1
    return {"adapter": str(adapter_dir) if adapter_dir else None, "split": split, "n": len(totals),
            "mean_score": round(sum(totals) / n_done, 4), "strict_pass_rate": round(passes / n_done, 4),
            "per_category": {k: round(sum(v) / len(v), 4) for k, v in sorted(by_cat.items())}, "samples": samples}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Quick GPU eval of a GeoAI adapter on eval_val.")
    add_config_args(ap)
    ap.add_argument("--adapter-dir", type=Path)
    ap.add_argument("--base", action="store_true", help="Evaluate the base model (no adapter)")
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--split", default="val", choices=("val", "train"))
    args = ap.parse_args(argv)
    if not args.base and not args.adapter_dir:
        ap.error("pass --adapter-dir or --base")
    rep = quick_eval(config_from_args(args), None if args.base else args.adapter_dir, n=args.n, split=args.split)
    print(json.dumps(rep, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
