# Author: Utkarsh Gupta
# License: GPL v3
"""
Stage 3: export the trained PEFT adapter for the desktop runtime.

Sub-commands::

    # PEFT adapter -> GGUF LoRA (llama.cpp convert_lora_to_gguf.py) + sidecar
    python -m core.geoai.finetune.export gguf-lora --adapter-dir outputs/geoai-ft/grpo_adapter \
        --llama-cpp /content/llama.cpp --outfile outputs/geoai-ft/export/geoai-lora.gguf

    # optional alternative: merged q4_k_m GGUF (Unsloth save_pretrained_gguf; GPU box)
    python -m core.geoai.finetune.export merged --adapter-dir outputs/geoai-ft/grpo_adapter --out-dir outputs/geoai-ft/export/merged

    # on the desktop: pin the adapter to the exact base GGUF (fingerprint + sha256)
    python -m core.geoai.finetune.export sidecar --lora geoai-lora.gguf --base-gguf %APPDATA%/GeoCore/models/qwen2.5-1.5b-instruct-q4_k_m.gguf

    # on the desktop: record eval results and the go/no-go decision (AGENTS.md §32)
    python -m core.geoai.finetune.export annotate --lora geoai-lora.gguf --base-results base.json --candidate-results lora.json

The sidecar (``<adapter>.gguf.json``, schema ``geoai-lora-sidecar/1``) is what
``core.geoai.lora_adapter.check_adapter_compatibility`` reads before loading.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.geoai.finetune._hf import read_run_info, sha256_of
from core.geoai.finetune.config import FinetuneConfig
from core.geoai.lora_adapter import SIDECAR_SCHEMA, load_sidecar, sidecar_path

# ---- go/no-go rule (AGENTS.md §32: keep the base model unless the adapter is better) ----
GO_MIN_MEAN_SCORE_GAIN = 0.02
GO_MAX_CATEGORY_DROP = 0.05
GO_MAX_LATENCY_RATIO = 1.3


def go_no_go(base: Dict[str, Any], cand: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decide whether the adapter may replace the base model, from two runner
    result files produced on the SAME examples (``core.geoai.eval.runner``).

    GO only if: same example set; mean score +0.02 or more; strict pass rate,
    hallucinated-parameter rate, caution-violation rate and error rate no
    worse; no category pass rate drops by more than 0.05; p50 latency at most
    1.3x the base.
    """
    from core.geoai.eval.runner import compare_results

    cmp = compare_results(base, cand)
    m = cmp["metrics"]
    failed: List[str] = []

    def delta(k: str) -> Optional[float]:
        return (m.get(k) or {}).get("delta")

    if not cmp["same_examples"]:
        failed.append("base and candidate were not evaluated on the same examples")
    d = delta("mean_score")
    if d is None or d < GO_MIN_MEAN_SCORE_GAIN:
        failed.append(f"mean_score gain {d} < {GO_MIN_MEAN_SCORE_GAIN}")
    for k in ("strict_pass_rate",):
        if delta(k) is not None and delta(k) < 0:
            failed.append(f"{k} decreased ({delta(k)})")
    for k in ("hallucinated_parameter_rate", "caution_violation_rate", "error_rate"):
        if delta(k) is not None and delta(k) > 0:
            failed.append(f"{k} increased ({delta(k)})")
    for cat, v in cmp["per_category_pass_rate"].items():
        if v.get("delta") is not None and v["delta"] < -GO_MAX_CATEGORY_DROP:
            failed.append(f"category {cat} pass rate dropped {v['delta']}")
    lb, lc = (m.get("latency_p50_s") or {}).get("base"), (m.get("latency_p50_s") or {}).get("candidate")
    if lb and lc and lc > GO_MAX_LATENCY_RATIO * lb:
        failed.append(f"p50 latency {lc}s > {GO_MAX_LATENCY_RATIO}x base {lb}s")
    return {"decision": "go" if not failed else "no-go", "failed": failed,
            "mean_score": m.get("mean_score"), "strict_pass_rate": m.get("strict_pass_rate"),
            "fixed": cmp["fixed"], "regressed": cmp["regressed"], "n_shared": cmp["n_shared"]}


# =====================================================================
# Sidecar
# =====================================================================

def build_sidecar(lora_gguf: Path, adapter_dir: Optional[Path] = None, base_gguf: Optional[Path] = None,
                  existing: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Sidecar contents. The base fingerprint comes from ``base_gguf`` when given
    (authoritative: the exact GGUF the desktop runs), otherwise from the HF
    config dims recorded at training time.
    """
    from core.geoai.gguf_meta import base_model_fingerprint

    sc: Dict[str, Any] = dict(existing or {})
    run: Dict[str, Any] = read_run_info(adapter_dir) if adapter_dir else {}
    cfg_dict: Dict[str, Any] = {}
    if adapter_dir and (Path(adapter_dir) / "geoai_finetune_config.json").is_file():
        cfg_dict = FinetuneConfig.load_json(Path(adapter_dir) / "geoai_finetune_config.json").to_dict()
    sc["schema"] = SIDECAR_SCHEMA
    sc["adapter_file"] = Path(lora_gguf).name
    sc["adapter_sha256"] = sha256_of(lora_gguf)
    if run or "base_model_id" not in sc:
        sc["base_model_id"] = run.get("base_model_id") or cfg_dict.get("base_model_id") or sc.get("base_model_id")
        sc["base_model"] = run.get("base_model") or cfg_dict.get("base_model") or sc.get("base_model")
        sc["family"] = run.get("family") or cfg_dict.get("family") or sc.get("family")
    if run:
        sc["chat_template"] = run.get("chat_template", "native")
        sc["plan_style"] = run.get("plan_style")
        sc["enable_thinking"] = run.get("enable_thinking", False)
        sc["training"] = {"stage": run.get("stage"), "data": run.get("data"), "grpo_data": run.get("grpo_data"),
                          "config": cfg_dict or None}
    sc.setdefault("chat_template", "native")
    base = dict(sc.get("base_gguf") or {})
    if base_gguf is not None:
        base.update({"filename": Path(base_gguf).name, "sha256": sha256_of(base_gguf),
                     "fingerprint": base_model_fingerprint(base_gguf), "fingerprint_source": "base_gguf"})
    elif run.get("base_fingerprint_from_hf_config") and "fingerprint" not in base:
        base.update({"fingerprint": run["base_fingerprint_from_hf_config"], "fingerprint_source": "hf_config"})
    sc["base_gguf"] = base
    sc["created_utc"] = sc.get("created_utc") or datetime.now(timezone.utc).isoformat(timespec="seconds")
    sc["updated_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return sc


def write_sidecar(lora_gguf: Path, sidecar: Dict[str, Any]) -> Path:
    p = sidecar_path(str(lora_gguf))
    with open(p, "w", encoding="utf-8") as f:
        json.dump(sidecar, f, indent=2, default=str)
    return p


def annotate(lora_gguf: Path, base_results: Path, candidate_results: Path) -> Dict[str, Any]:
    """Add runner metrics for base and adapter plus the go/no-go decision to the sidecar."""
    with open(base_results, encoding="utf-8") as f:
        base = json.load(f)
    with open(candidate_results, encoding="utf-8") as f:
        cand = json.load(f)
    sc = load_sidecar(str(lora_gguf)) or build_sidecar(lora_gguf)
    keys = ("n", "mean_score", "strict_pass_rate", "tool_selection_accuracy", "argument_accuracy",
            "clarification_accuracy", "hallucinated_parameter_rate", "caution_violation_rate",
            "latency_p50_s", "peak_memory_mb")
    sc["eval"] = {
        "split": (cand.get("meta") or {}).get("split"),
        "base": {k: base["metrics"].get(k) for k in keys},
        "adapter": {k: cand["metrics"].get(k) for k in keys},
        "go_no_go": go_no_go(base, cand),
        "annotated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    write_sidecar(lora_gguf, sc)
    return sc


# =====================================================================
# Conversions (GPU box / llama.cpp checkout)
# =====================================================================

def convert_lora_to_gguf(adapter_dir: Path, llama_cpp_dir: Path, outfile: Path, outtype: str = "f16",
                         base_dir: Optional[Path] = None, base_model_id: Optional[str] = None) -> Path:
    """
    Run llama.cpp's ``convert_lora_to_gguf.py`` (developer tool, not model-accessible).
    ``--base`` (local HF dir with config.json) wins over ``--base-model-id`` (config fetched from the Hub).
    """
    script = Path(llama_cpp_dir) / "convert_lora_to_gguf.py"
    if not script.is_file():
        raise FileNotFoundError(f"{script} not found (clone https://github.com/ggml-org/llama.cpp and "
                                f"pip install -r requirements/requirements-convert_lora_to_gguf.txt)")
    outfile = Path(outfile)
    outfile.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(script), str(adapter_dir), "--outfile", str(outfile), "--outtype", outtype]
    if base_dir:
        cmd += ["--base", str(base_dir)]
    elif base_model_id:
        cmd += ["--base-model-id", base_model_id]
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)
    return outfile


def export_merged_gguf(adapter_dir: Path, out_dir: Path, quantization: str = "q4_k_m") -> Path:
    """Merge LoRA into the base and write a quantised GGUF via Unsloth (needs the GPU stack)."""
    from unsloth import FastLanguageModel

    cfg = FinetuneConfig.load_json(Path(adapter_dir) / "geoai_finetune_config.json")
    model, tokenizer = FastLanguageModel.from_pretrained(model_name=str(adapter_dir),
                                                         max_seq_length=cfg.max_seq_length,
                                                         load_in_4bit=cfg.resolved_load_in_4bit)
    model.save_pretrained_gguf(str(out_dir), tokenizer, quantization_method=quantization)
    return Path(out_dir)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Export GeoAI LoRA adapters for the desktop runtime.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gguf-lora", help="PEFT adapter -> GGUF LoRA + sidecar")
    g.add_argument("--adapter-dir", type=Path, required=True)
    g.add_argument("--llama-cpp", type=Path, required=True, help="Path to a llama.cpp checkout")
    g.add_argument("--outfile", type=Path, required=True)
    g.add_argument("--outtype", default="f16", choices=("f32", "f16", "bf16", "q8_0", "auto"))
    g.add_argument("--base-dir", type=Path, help="Local HF base model dir (config.json)")
    g.add_argument("--base-model-id", help="HF id of the base (default: from the training config)")
    g.add_argument("--base-gguf", type=Path, help="Base GGUF to fingerprint (optional; can be added later)")

    m = sub.add_parser("merged", help="Merged, quantised GGUF (alternative to the adapter)")
    m.add_argument("--adapter-dir", type=Path, required=True)
    m.add_argument("--out-dir", type=Path, required=True)
    m.add_argument("--quantization", default="q4_k_m")

    s = sub.add_parser("sidecar", help="(Re)write the sidecar, e.g. to pin the exact base GGUF")
    s.add_argument("--lora", type=Path, required=True)
    s.add_argument("--adapter-dir", type=Path)
    s.add_argument("--base-gguf", type=Path)

    a = sub.add_parser("annotate", help="Record base vs adapter eval results and the go/no-go decision")
    a.add_argument("--lora", type=Path, required=True)
    a.add_argument("--base-results", type=Path, required=True)
    a.add_argument("--candidate-results", type=Path, required=True)

    args = ap.parse_args(argv)
    if args.cmd == "gguf-lora":
        cfg_path = args.adapter_dir / "geoai_finetune_config.json"
        base_id = args.base_model_id or (FinetuneConfig.load_json(cfg_path).base_model_id if cfg_path.is_file() else None)
        out = convert_lora_to_gguf(args.adapter_dir, args.llama_cpp, args.outfile, args.outtype, args.base_dir, base_id)
        p = write_sidecar(out, build_sidecar(out, args.adapter_dir, args.base_gguf))
        print(f"wrote {out} and {p}")
    elif args.cmd == "merged":
        print(f"wrote {export_merged_gguf(args.adapter_dir, args.out_dir, args.quantization)}")
    elif args.cmd == "sidecar":
        p = write_sidecar(args.lora, build_sidecar(args.lora, args.adapter_dir, args.base_gguf, load_sidecar(str(args.lora))))
        print(f"wrote {p}")
    elif args.cmd == "annotate":
        sc = annotate(args.lora, args.base_results, args.candidate_results)
        print(json.dumps(sc["eval"]["go_no_go"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
