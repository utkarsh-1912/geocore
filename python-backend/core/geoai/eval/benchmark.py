# Author: Utkarsh Gupta
# License: GPL v3
"""
GeoAI model benchmark (AGENTS.md §21, §31-32).

Runs several local GGUF models - and optionally GeoAI LoRA fine-tunes of them - through the
same GeoAI evaluation suite (``eval.runner``) with identical examples, prompts, tools,
``n_ctx`` and ``max_tools``, then writes one result file per model plus a leaderboard that the
website's "Model benchmarks" page is generated from.

Candidates are listed in ``CANDIDATES``; nothing here hard-codes a model elsewhere in the app.

Examples (from python-backend/):
    python -m core.geoai.eval.benchmark list
    python -m core.geoai.eval.benchmark download qwen3-1.7b phi-4-mini
    python -m core.geoai.eval.benchmark run --models all-local --split test --limit 40 --mode decision --run-id cpu-test40
    python -m core.geoai.eval.benchmark run --models qwen3-1.7b --lora qwen3-1.7b=C:/ft/geoai-lora.gguf --run-id cpu-test40
    python -m core.geoai.eval.benchmark leaderboard --run-id cpu-test40
"""

import argparse
import gc
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.geoai.eval.runner import RESULTS_DIR, build_report, make_provider, run_eval

BENCHMARK_DIR = RESULTS_DIR / "benchmark"
LEADERBOARD_FILE = "leaderboard.json"
LEADERBOARD_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class Candidate:
    key: str
    display_name: str
    params: str
    repo_id: str  # Hugging Face GGUF repository (Q4_K_M file sizes checked 2026-09-27)
    filename: str
    size_mb: int
    license: str
    tool_format: str  # how the model emits tool calls under llama.cpp (see llama_cpp_provider.parse_tool_calls)
    finetune_base: Optional[str] = None  # HF id to fine-tune (must match the GGUF), None = not planned
    finetune_family: Optional[str] = None  # finetune.config.FAMILY_PRESETS key
    notes: str = ""


CANDIDATES: Dict[str, Candidate] = {c.key: c for c in [
    Candidate("qwen2.5-1.5b", "Qwen2.5 1.5B Instruct", "1.5B", "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
              "qwen2.5-1.5b-instruct-q4_k_m.gguf", 986, "Apache-2.0", "native <tool_call>",
              "Qwen/Qwen2.5-1.5B-Instruct", "qwen2.5", "Current GeoAI default and fine-tuning baseline."),
    Candidate("qwen3-1.7b", "Qwen3 1.7B", "1.7B", "unsloth/Qwen3-1.7B-GGUF",
              "Qwen3-1.7B-Q4_K_M.gguf", 1056, "Apache-2.0", "native <tool_call>",
              "Qwen/Qwen3-1.7B", "qwen3", "Hybrid thinking model; GeoAI sends /no_think."),
    Candidate("qwen3.5-2b", "Qwen3.5 2B", "2B", "unsloth/Qwen3.5-2B-GGUF",
              "Qwen3.5-2B-Q4_K_M.gguf", 1222, "Apache-2.0", "native <tool_call>",
              "Qwen/Qwen3.5-2B", "qwen3.5", "Newest small Qwen; fine-tune preset uses 16-bit LoRA."),
    Candidate("qwen3-4b-2507", "Qwen3 4B Instruct 2507", "4B", "unsloth/Qwen3-4B-Instruct-2507-GGUF",
              "Qwen3-4B-Instruct-2507-Q4_K_M.gguf", 2382, "Apache-2.0", "native <tool_call>",
              "Qwen/Qwen3-4B-Instruct-2507", "qwen3", "Non-thinking instruct release."),
    Candidate("qwen3-8b", "Qwen3 8B", "8B", "Qwen/Qwen3-8B-GGUF",
              "Qwen3-8B-Q4_K_M.gguf", 4795, "Apache-2.0", "native <tool_call>",
              None, None, "Quality ceiling reference; too heavy to be the default."),
    Candidate("phi-4-mini", "Phi-4-mini Instruct", "3.8B", "unsloth/Phi-4-mini-instruct-GGUF",
              "Phi-4-mini-instruct-Q4_K_M.gguf", 2376, "MIT", "<|tool_call|> JSON list",
              None, None, "Trained for function calling; no fine-tuning preset yet."),
    Candidate("gemma-3-4b", "Gemma 3 4B IT", "4B", "unsloth/gemma-3-4b-it-GGUF",
              "gemma-3-4b-it-Q4_K_M.gguf", 2375, "Gemma terms", "prompted (template has no tools)",
              None, "gemma3", "Tools described in the system prompt (chat_format=prompted)."),
    Candidate("smollm3-3b", "SmolLM3 3B", "3B", "ggml-org/SmolLM3-3B-GGUF",
              "SmolLM3-Q4_K_M.gguf", 1827, "Apache-2.0", "native <tool_call>",
              None, None, "Hybrid thinking model; GeoAI sends /no_think."),
    Candidate("granite-4.0-micro", "Granite 4.0 Micro", "3B", "ibm-granite/granite-4.0-micro-GGUF",
              "granite-4.0-micro-Q4_K_M.gguf", 2002, "Apache-2.0", "native <tool_call>",
              None, None, "IBM enterprise model with function calling."),
    Candidate("llama-3.2-3b", "Llama 3.2 3B Instruct", "3B", "bartowski/Llama-3.2-3B-Instruct-GGUF",
              "Llama-3.2-3B-Instruct-Q4_K_M.gguf", 1926, "Llama 3.2 Community", "bare JSON (name, parameters)",
              None, None, "Custom licence with use restrictions."),
]}


# =====================================================================
# Local files
# =====================================================================

def local_path(c: Candidate) -> Optional[Path]:
    from core.geoai.model_config import find_gguf_models
    for p in find_gguf_models():
        if p.name.lower() == c.filename.lower():
            return p
    return None


def download(keys: List[str]) -> None:
    """Download candidate GGUFs into the GeoCore models folder (huggingface_hub if installed, else plain HTTPS)."""
    from core.geoai.model_config import get_default_model_dir
    target = get_default_model_dir()
    for k in keys:
        c = CANDIDATES[k]
        if local_path(c):
            print(f"{k}: already present at {local_path(c)}")
            continue
        print(f"{k}: downloading {c.repo_id}/{c.filename} (~{c.size_mb} MB) -> {target}", flush=True)
        try:
            from huggingface_hub import hf_hub_download
        except ImportError:
            _https_download(f"https://huggingface.co/{c.repo_id}/resolve/main/{c.filename}", target / c.filename)
        else:
            hf_hub_download(repo_id=c.repo_id, filename=c.filename, local_dir=str(target))


def _https_download(url: str, dest: Path, chunk: int = 1 << 20) -> None:
    """Stream to ``dest.part`` and rename when complete, so an interrupted download is never picked up as a model."""
    import urllib.request
    part = dest.with_name(dest.name + ".part")
    with urllib.request.urlopen(url) as resp, open(part, "wb") as f:
        total = int(resp.headers.get("Content-Length") or 0)
        done = 0
        while True:
            buf = resp.read(chunk)
            if not buf:
                break
            f.write(buf)
            done += len(buf)
            if total and done % (256 * chunk) < chunk:
                print(f"  {done / total:5.1%} of {total / 2 ** 20:.0f} MB", flush=True)
    if total and done != total:
        part.unlink(missing_ok=True)
        raise IOError(f"incomplete download of {url}: {done} of {total} bytes")
    part.replace(dest)


def _resolve_models(spec: str) -> List[str]:
    if spec == "all-local":
        return [k for k, c in CANDIDATES.items() if local_path(c)]
    keys = [k.strip() for k in spec.split(",") if k.strip()]
    unknown = [k for k in keys if k not in CANDIDATES]
    if unknown:
        raise SystemExit(f"Unknown model key(s): {unknown}. Known: {sorted(CANDIDATES)}")
    return keys


# =====================================================================
# Running
# =====================================================================

def _run_one(label: str, model_path: Optional[str], examples, args, lora: Optional[str] = None,
             provider_name: str = "llama_cpp") -> Dict[str, Any]:
    # LoRA is read from the environment by GeoAIModelConfig (model_config._env_lora_path).
    if lora:
        os.environ["GEOAI_LORA_PATH"] = lora
    else:
        os.environ.pop("GEOAI_LORA_PATH", None)
    provider = make_provider(provider_name, model_path, n_ctx=args.n_ctx, n_gpu_layers=args.n_gpu_layers)
    print(f"\n=== {label}: n={len(examples)} mode={args.mode}", flush=True)
    try:
        run = run_eval(examples, provider, mode=args.mode, execute=not args.no_execute, progress=True)
    finally:
        info = provider.model_info()
        if hasattr(provider, "unload"):
            provider.unload()
        gc.collect()
    return run, info


def cmd_run(args) -> int:
    from core.geoai.eval.example import load_examples_jsonl
    from core.geoai.eval.runner import _stratified_limit
    from core.geoai.training.scaleup import DEFAULT_SEED, GENERATOR_VERSION, load_split

    # Same tool budget for every model, independent of the user's saved config.
    os.environ["GEOAI_MAX_TOOLS"] = str(args.max_tools)
    if args.chat_format:
        os.environ["GEOAI_CHAT_FORMAT"] = args.chat_format

    examples = load_examples_jsonl(args.dataset) if args.dataset else load_split(args.split)
    if args.turn_type:
        examples = [e for e in examples if e.turn_type == args.turn_type]
    examples = _stratified_limit(examples, args.limit)

    loras: Dict[str, str] = {}
    for spec in args.lora or []:
        key, _, path = spec.partition("=")
        if key not in CANDIDATES or not path:
            raise SystemExit(f"--lora expects KEY=PATH with a known key, got {spec!r}")
        loras[key] = path

    out_dir = BENCHMARK_DIR / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    from core.geoai.model_config import load_config
    common_meta = {
        "run_id": args.run_id, "split": str(args.dataset) if args.dataset else args.split, "limit": args.limit,
        "turn_type": args.turn_type, "mode": args.mode, "n_ctx": args.n_ctx, "max_tools": args.max_tools,
        "n_gpu_layers": args.n_gpu_layers, "dataset_generator_version": GENERATOR_VERSION,
        "dataset_seed": DEFAULT_SEED, "python": sys.version.split()[0], "platform": sys.platform,
        # Prompt-shaping switches that change the result (GEOAI_COMPACT_SCHEMAS etc., see model_config).
        "compact_tool_schemas": bool(load_config().compact_tool_schemas), "label_suffix": args.label_suffix or None,
    }

    jobs: List[Dict[str, Any]] = []
    if args.heuristic:
        jobs.append({"label": "heuristic", "key": None, "provider": "heuristic", "path": None, "lora": None})
    for key in _resolve_models(args.models):
        c = CANDIDATES[key]
        path = local_path(c)
        if not path:
            print(f"skip {key}: {c.filename} not found (run `benchmark download {key}`)")
            continue
        jobs.append({"label": key, "key": key, "provider": "llama_cpp", "path": str(path), "lora": None})
        if key in loras:
            jobs.append({"label": f"{key}+geoai-lora", "key": key, "provider": "llama_cpp",
                         "path": str(path), "lora": loras[key]})

    for job in jobs:
        job["label"] += args.label_suffix or ""  # e.g. "-compact": two configs of one model in one run
        out_file = out_dir / f"{job['label']}.json"
        if out_file.exists() and not args.overwrite:
            print(f"skip {job['label']}: {out_file.name} exists (use --overwrite)")
            continue
        run, info = _run_one(job["label"], job["path"], examples, args, lora=job["lora"], provider_name=job["provider"])
        meta = dict(common_meta, label=job["label"], model_key=job["key"], provider=job["provider"],
                    lora_path=job["lora"], model_info=info,
                    timestamp_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        report = build_report(run, meta, keep_records="failures", max_records=args.max_records or None)
        out_file.write_text(json.dumps(report, indent=1, default=str), encoding="utf-8")
        print(f"wrote {out_file}", flush=True)

    write_leaderboard(out_dir)
    return 0


# =====================================================================
# Leaderboard
# =====================================================================

LEADERBOARD_METRICS = ("mean_score", "strict_pass_rate", "action_accuracy", "tool_selection_accuracy",
                       "argument_accuracy", "schema_valid_rate", "clarification_accuracy",
                       "hallucinated_parameter_rate", "hallucinated_tool_rate", "unit_trap_accuracy",
                       "caution_violation_rate", "error_rate", "decision_latency_p50_s", "latency_p50_s",
                       "peak_memory_mb", "model_load_s", "prompt_tokens_p50", "completion_tokens_p50")


def build_leaderboard(out_dir: Path) -> Dict[str, Any]:
    rows = []
    example_sets = set()
    reports = [(f, json.loads(f.read_text(encoding="utf-8"))) for f in sorted(out_dir.glob("*.json"))
               if f.name != LEADERBOARD_FILE]
    # Only result files: auxiliary JSON in the run folder (desktop_latency_estimate.json, ...) has no metrics.
    reports = [(f, rep) for f, rep in reports if isinstance(rep, dict) and "metrics" in rep and "meta" in rep]
    for f, rep in reports:
        meta, m = rep.get("meta", {}), rep.get("metrics", {})
        example_sets.add(tuple(sorted(rep.get("per_example", {}))))
        c = CANDIDATES.get(meta.get("model_key") or "")
        rows.append({
            "label": meta.get("label", f.stem),
            "model_key": meta.get("model_key"),
            "display_name": (c.display_name + (" + GeoAI LoRA" if meta.get("lora_path") else "")
                             + (f" ({meta['label_suffix'].strip('-_ ')})" if meta.get("label_suffix") else ""))
            if c else meta.get("label"),
            "params": c.params if c else None,
            "size_mb": c.size_mb if c else None,
            "license": c.license if c else None,
            "fine_tuned": bool(meta.get("lora_path")),
            "chat_format": (meta.get("model_info") or {}).get("chat_format"),
            "compact_tool_schemas": meta.get("compact_tool_schemas"),
            "n": m.get("n"),
            "metrics": {k: m.get(k) for k in LEADERBOARD_METRICS},
            "per_category": {k: v.get("pass_rate") for k, v in (m.get("per_category") or {}).items()},
            "timestamp_utc": meta.get("timestamp_utc"),
            "file": f.name,
        })
    rows.sort(key=lambda r: -(r["metrics"].get("mean_score") or 0))
    first = reports[0][1].get("meta", {}) if reports else {}
    settings = {k: first.get(k) for k in ("split", "limit", "turn_type", "mode", "n_ctx", "max_tools", "n_gpu_layers",
                                          "dataset_generator_version", "dataset_seed", "platform")}
    return {"schema_version": LEADERBOARD_SCHEMA_VERSION, "run_id": out_dir.name, "settings": settings,
            "same_examples": len(example_sets) <= 1, "rows": rows,
            "candidates": {k: asdict(c) for k, c in CANDIDATES.items()}}


def write_leaderboard(out_dir: Path) -> Path:
    lb = build_leaderboard(out_dir)
    path = out_dir / LEADERBOARD_FILE
    path.write_text(json.dumps(lb, indent=1), encoding="utf-8")
    print(format_leaderboard(lb))
    print(f"wrote {path}")
    return path


def _f(v: Any, pct: bool = False) -> str:
    if v is None:
        return "-"
    if pct:
        return f"{100 * v:.0f}%"
    return f"{v:.3f}" if isinstance(v, float) else str(v)


def format_leaderboard(lb: Dict[str, Any]) -> str:
    lines = [f"run={lb['run_id']} settings={lb['settings']} same_examples={lb['same_examples']}",
             f"{'model':<28}{'n':>4}{'score':>8}{'pass':>7}{'tool':>7}{'args':>7}{'clarify':>9}{'halluc':>8}"
             f"{'p50 s':>8}{'RAM MB':>9}"]
    for r in lb["rows"]:
        m = r["metrics"]
        lines.append(f"{r['label']:<28}{_f(r['n']):>4}{_f(m['mean_score']):>8}{_f(m['strict_pass_rate'], True):>7}"
                     f"{_f(m['tool_selection_accuracy'], True):>7}{_f(m['argument_accuracy']):>7}"
                     f"{_f(m['clarification_accuracy'], True):>9}{_f(m['hallucinated_parameter_rate'], True):>8}"
                     f"{_f(m['decision_latency_p50_s']):>8}{_f(m['peak_memory_mb']):>9}")
    return "\n".join(lines)


def latest_leaderboard(results_dir: Path = BENCHMARK_DIR) -> Optional[Dict[str, Any]]:
    """Most recently written leaderboard (used by the website generator)."""
    files = sorted(results_dir.glob(f"*/{LEADERBOARD_FILE}"), key=lambda p: p.stat().st_mtime)
    return json.loads(files[-1].read_text(encoding="utf-8")) if files else None


# =====================================================================
# CLI
# =====================================================================

def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Benchmark local GGUF models on the GeoAI evaluation suite.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List candidate models and whether they are downloaded")

    d = sub.add_parser("download", help="Download candidate GGUFs from Hugging Face")
    d.add_argument("models", nargs="+", choices=sorted(CANDIDATES))

    r = sub.add_parser("run", help="Run the eval suite for each model with identical settings")
    r.add_argument("--models", default="all-local", help="Comma-separated candidate keys, or 'all-local'")
    r.add_argument("--lora", action="append", metavar="KEY=PATH", help="Also run KEY with this GGUF LoRA adapter")
    r.add_argument("--heuristic", action="store_true", help="Include the heuristic (no model) baseline")
    r.add_argument("--run-id", required=True, help="Folder name under eval/results/benchmark/")
    r.add_argument("--split", default="test", choices=("val", "test", "gold"))
    r.add_argument("--dataset", type=Path)
    r.add_argument("--limit", type=int)
    r.add_argument("--turn-type", choices=("decision", "final_answer"))
    r.add_argument("--mode", choices=("agent", "decision"), default="decision")
    r.add_argument("--no-execute", action="store_true")
    r.add_argument("--n-ctx", type=int, default=4096)
    r.add_argument("--n-gpu-layers", type=int, default=0)
    r.add_argument("--max-tools", type=int, default=5)
    r.add_argument("--chat-format", choices=("native", "prompted", "chatml-function-calling"),
                   help="Force one chat format for every model (default: auto per GGUF)")
    r.add_argument("--max-records", type=int, default=60)
    r.add_argument("--overwrite", action="store_true")
    r.add_argument("--label-suffix", default="",
                   help="Appended to every result label/file to keep two configs of one model in one run, "
                        "e.g. --label-suffix=-compact (use '=' because the value starts with '-')")

    lb = sub.add_parser("leaderboard", help="Rebuild the leaderboard of a run")
    lb.add_argument("--run-id", required=True)

    args = ap.parse_args(argv)
    if args.cmd == "list":
        for k, c in CANDIDATES.items():
            p = local_path(c)
            print(f"{k:<20}{c.params:>6}{c.size_mb:>7} MB  {c.license:<20}{'downloaded' if p else '-':<12}{c.tool_format}")
        return 0
    if args.cmd == "download":
        download(args.models)
        return 0
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "leaderboard":
        write_leaderboard(BENCHMARK_DIR / args.run_id)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
