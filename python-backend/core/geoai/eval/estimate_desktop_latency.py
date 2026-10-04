# Author: Utkarsh Gupta
# License: GPL v3
"""
ESTIMATED desktop latency for a benchmark run (AGENTS.md §21, §23).

Cloud GPU runs measure quality, not desktop latency. Token counts, however, do not depend on the
hardware (same GGUF, template and prompt), so each example's desktop time is estimated as

    prompt_tokens / prompt_tok_s  +  completion_tokens / gen_tok_s        (warm model)
    + model_load_s                                                         (cold: first request only)

with throughput from ``data/desktop_calibration.json`` (measured on the reference laptop). Models
without a calibration entry are scaled from the reference model by GGUF size - rougher still.
Everything this script writes is marked ``"estimate": true``; it never runs a model.

Not modelled: llama.cpp prompt-prefix reuse between consecutive requests (makes real latency lower),
thermal throttling beyond the calibration range, LoRA adapter overhead on CPU, tool execution time.
Against the reference laptop's own Qwen3-1.7B runs (cpu-test40, cpu-test40-full-20260929; failure
records only) measured/estimated decision latency was 0.5-1.7x per example, median 0.81-0.89, i.e. the
estimate is slightly pessimistic; ``--validate`` recomputes that ratio for runs made on that machine.

Examples (from python-backend/):
    python -m core.geoai.eval.estimate_desktop_latency --run-id gpu-compact-ab
    python -m core.geoai.eval.estimate_desktop_latency --run-dir path/to/results/benchmark/gpu-models --no-write
    python -m core.geoai.eval.estimate_desktop_latency --run-id cpu-test40 --validate
"""

import argparse
import json
import statistics
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.geoai.eval.runner import RESULTS_DIR, _percentile

DEFAULT_CALIBRATION = Path(__file__).resolve().parent / "data" / "desktop_calibration.json"
OUTPUT_FILE = "desktop_latency_estimate.json"
SCHEMA_VERSION = 1


def load_calibration(path: Path = DEFAULT_CALIBRATION) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        cal = json.load(f)
    ref = cal.get("reference_model")
    if not ref or ref not in cal.get("models", {}):
        raise ValueError(f"{path}: 'reference_model' must name an entry of 'models'")
    for key, m in cal["models"].items():
        for field in ("prompt_tok_s", "gen_tok_s"):
            if not isinstance(m.get(field), (int, float)) or m[field] <= 0:
                raise ValueError(f"{path}: models.{key}.{field} must be a positive number")
    return cal


def _candidate_size_mb(model_key: Optional[str]) -> Optional[int]:
    from core.geoai.eval.benchmark import CANDIDATES
    c = CANDIDATES.get(model_key or "")
    return c.size_mb if c else None


def rates_for(cal: Dict[str, Any], model_key: Optional[str], size_mb: Optional[float] = None) -> Optional[Dict[str, Any]]:
    """Throughput for one model: its own calibration entry, else the reference scaled by GGUF size."""
    models = cal["models"]
    if model_key in models:
        m = models[model_key]
        factor, method = 1.0, "calibrated"
    else:
        size_mb = size_mb if size_mb is not None else _candidate_size_mb(model_key)
        ref = models[cal["reference_model"]]
        if not size_mb or not ref.get("size_mb"):
            return None
        m = ref
        factor, method = ref["size_mb"] / float(size_mb), f"scaled from {cal['reference_model']} by GGUF size"
    pp, tg = m["prompt_tok_s"] * factor, m["gen_tok_s"] * factor
    pp_lo, pp_hi = (x * factor for x in m.get("prompt_tok_s_range") or (m["prompt_tok_s"],) * 2)
    tg_lo, tg_hi = (x * factor for x in m.get("gen_tok_s_range") or (m["gen_tok_s"],) * 2)
    load = m.get("model_load_s")
    return {"prompt_tok_s": pp, "prompt_tok_s_range": [pp_lo, pp_hi], "gen_tok_s": tg, "gen_tok_s_range": [tg_lo, tg_hi],
            "model_load_s": (load / factor) if isinstance(load, (int, float)) else None, "method": method}


def example_tokens(report: Dict[str, Any]) -> Dict[str, Any]:
    """Per-example token counts: ``per_example_usage`` (all examples) or, for older result files, the kept records."""
    rows: List[Dict[str, Any]] = []
    source = "per_example_usage"
    usage = report.get("per_example_usage")
    if usage:
        for ex_id, u in usage.items():
            if u.get("prompt_tokens") is not None and u.get("completion_tokens") is not None:
                rows.append({"id": ex_id, "prompt_tokens": u["prompt_tokens"], "completion_tokens": u["completion_tokens"],
                             "measured_s": u.get("decision_latency_s") if u.get("model_calls") == 1 else u.get("latency_s")})
    else:
        source = "records (older result file: failure records only)"
        for r in report.get("records", []):
            p, c = r.get("prompt_tokens"), r.get("completion_tokens")
            if p is None and r.get("usage"):
                p, c = r["usage"].get("prompt_tokens"), r["usage"].get("completion_tokens")
            if p is not None and c is not None:
                rows.append({"id": r["id"], "prompt_tokens": p, "completion_tokens": c,
                             "measured_s": r.get("decision_latency_s") if r.get("n_model_calls") == 1 else r.get("latency_s")})
    n_total = (report.get("metrics") or {}).get("n") or len(report.get("per_example", {}))
    return {"rows": rows, "source": source, "n_total": n_total}


def _seconds(p: float, c: float, pp: float, tg: float) -> float:
    return p / pp + c / tg


def estimate_report(report: Dict[str, Any], cal: Dict[str, Any], validate: bool = False) -> Dict[str, Any]:
    meta = report.get("meta", {})
    label, key = meta.get("label"), meta.get("model_key")
    out: Dict[str, Any] = {"label": label, "model_key": key, "estimate": True,
                           "measured_on": meta.get("platform"), "n_gpu_layers": meta.get("n_gpu_layers"),
                           "measured_latency_p50_s": (report.get("metrics") or {}).get("decision_latency_p50_s")}
    if meta.get("provider") == "heuristic" or (meta.get("model_info") or {}).get("provider") == "heuristic":
        return dict(out, skipped="heuristic baseline (no model, no tokens)")
    tok = example_tokens(report)
    out.update(n_examples=tok["n_total"], n_with_tokens=len(tok["rows"]), token_source=tok["source"])
    if not tok["rows"]:
        return dict(out, skipped="no token counts in this result file")
    rates = rates_for(cal, key)
    if rates is None:
        return dict(out, skipped=f"no calibration for model '{key}' and no size to scale by")
    pp, tg = rates["prompt_tok_s"], rates["gen_tok_s"]
    nominal = [_seconds(r["prompt_tokens"], r["completion_tokens"], pp, tg) for r in tok["rows"]]
    fast = [_seconds(r["prompt_tokens"], r["completion_tokens"], rates["prompt_tok_s_range"][1], rates["gen_tok_s_range"][1])
            for r in tok["rows"]]
    slow = [_seconds(r["prompt_tokens"], r["completion_tokens"], rates["prompt_tok_s_range"][0], rates["gen_tok_s_range"][0])
            for r in tok["rows"]]
    p50 = _percentile(nominal, 0.5)
    load = rates["model_load_s"]
    out.update({
        "rate_method": rates["method"],
        "prompt_tok_s": round(pp, 2), "gen_tok_s": round(tg, 2),
        "prompt_tokens_p50": _percentile([r["prompt_tokens"] for r in tok["rows"]], 0.5),
        "completion_tokens_p50": _percentile([r["completion_tokens"] for r in tok["rows"]], 0.5),
        "est_desktop_p50_s": round(p50, 1),
        "est_desktop_p95_s": round(_percentile(nominal, 0.95), 1),
        "est_desktop_p50_range_s": [round(_percentile(fast, 0.5), 1), round(_percentile(slow, 0.5), 1)],
        "est_desktop_p95_range_s": [round(_percentile(fast, 0.95), 1), round(_percentile(slow, 0.95), 1)],
        "est_model_load_s": round(load, 1) if load is not None else None,
        "est_desktop_cold_p50_s": round(p50 + load, 1) if load is not None else None,
    })
    if meta.get("lora_path"):
        out["note"] = "LoRA adapter overhead on CPU (no mmap, extra matmuls) is not included"
    if validate:
        ratios = [r["measured_s"] / e for r, e in zip(tok["rows"], nominal) if r.get("measured_s") and e > 0]
        out["validation"] = {
            "n": len(ratios),
            "measured_over_estimate_p50": round(statistics.median(ratios), 2) if ratios else None,
            "measured_over_estimate_range": [round(min(ratios), 2), round(max(ratios), 2)] if ratios else None,
            "meaningful_only_if": "the run was measured on the calibration machine (CPU, same settings)",
        }
    return out


def estimate_run(run_dir: Path, cal: Dict[str, Any], validate: bool = False) -> Dict[str, Any]:
    rows = []
    for f in sorted(Path(run_dir).glob("*.json")):
        rep = json.loads(f.read_text(encoding="utf-8"))
        if not (isinstance(rep, dict) and "metrics" in rep and "meta" in rep):
            continue  # leaderboard.json, this script's own output, ...
        rows.append(dict(estimate_report(rep, cal, validate=validate), file=f.name))
    rows.sort(key=lambda r: (r.get("est_desktop_p50_s") is None, r.get("est_desktop_p50_s") or 0))
    return {
        "schema_version": SCHEMA_VERSION,
        "estimate": True,
        "run_id": Path(run_dir).name,
        "formula": "prompt_tokens/prompt_tok_s + completion_tokens/gen_tok_s; cold adds model_load_s",
        "calibration": {k: cal.get(k) for k in ("machine", "date", "reference_model")},
        "not_modelled": ["prompt-prefix cache reuse (real latency lower)", "LoRA overhead on CPU",
                         "tool execution time", "throttling outside the calibration range"],
        "rows": rows,
    }


def _f(v: Any) -> str:
    return "-" if v is None else (f"{v:.1f}" if isinstance(v, float) else str(v))


def format_estimate(est: Dict[str, Any]) -> str:
    cal = est["calibration"]
    machine = (cal.get("machine") or {}).get("cpu") or (cal.get("machine") or {}).get("name")
    lines = [f"ESTIMATED desktop latency (not measured) for run={est['run_id']}  calibration: {machine}, {cal.get('date')}",
             f"{'model':<30}{'n':>5}{'p_tok50':>9}{'c_tok50':>9}{'est p50 s':>11}{'est p95 s':>11}"
             f"{'p50 range':>14}{'cold p50':>10}  method"]
    for r in est["rows"]:
        if r.get("skipped"):
            lines.append(f"{str(r['label']):<30}  skipped: {r['skipped']}")
            continue
        rng = r["est_desktop_p50_range_s"]
        lines.append(f"{str(r['label']):<30}{r['n_with_tokens']:>5}{_f(r['prompt_tokens_p50']):>9}"
                     f"{_f(r['completion_tokens_p50']):>9}{_f(r['est_desktop_p50_s']):>11}{_f(r['est_desktop_p95_s']):>11}"
                     f"{f'{rng[0]:.0f}-{rng[1]:.0f}':>14}{_f(r['est_desktop_cold_p50_s']):>10}  {r['rate_method']}")
        if r["n_with_tokens"] < (r.get("n_examples") or 0):
            lines.append(f"{'':<30}  tokens for {r['n_with_tokens']}/{r['n_examples']} examples ({r['token_source']})")
        if r.get("validation"):
            v = r["validation"]
            lines.append(f"{'':<30}  validate: measured/estimate p50={v['measured_over_estimate_p50']} "
                         f"range={v['measured_over_estimate_range']} (n={v['n']})")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Estimate desktop latency of a benchmark run from its token counts "
                                             "(no model is run).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--run-id", help="Folder under eval/results/benchmark/")
    g.add_argument("--run-dir", type=Path, help="Any folder of benchmark result files (e.g. an extracted remote run)")
    ap.add_argument("--calibration", type=Path, default=DEFAULT_CALIBRATION)
    ap.add_argument("--validate", action="store_true",
                    help="Also report measured/estimate ratios (only meaningful for runs on the calibration machine)")
    ap.add_argument("--no-write", action="store_true", help=f"Print only; do not write {OUTPUT_FILE}")
    args = ap.parse_args(argv)

    run_dir = args.run_dir or (RESULTS_DIR / "benchmark" / args.run_id)
    if not run_dir.is_dir():
        raise SystemExit(f"not a directory: {run_dir}")
    est = estimate_run(run_dir, load_calibration(args.calibration), validate=args.validate)
    print(format_estimate(est))
    if not args.no_write:
        out = run_dir / OUTPUT_FILE
        out.write_text(json.dumps(est, indent=1), encoding="utf-8")
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
