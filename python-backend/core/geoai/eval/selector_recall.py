# Author: Utkarsh Gupta
# License: GPL v3
"""
Tool-selector retrieval benchmark (AGENTS.md §21).

Measures recall@k of ``tool_selector.select_relevant_tools``: an example is a
hit at k when its ``expected_tool`` or any of its ``acceptable_tools`` is among
the first k offered tools.  Only examples with an expected tool are counted.
The query is the first user message; the example's context is passed through.

CLI::

    python -m core.geoai.eval.selector_recall --split test --k 1 3 5 10
    python -m core.geoai.eval.selector_recall --split val --show-misses 20
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from core.geoai.eval.example import EvalExample, load_examples_jsonl

DATA_DIR = Path(__file__).resolve().parent.parent / "training" / "data"
SPLITS = ("train", "val", "test", "gold")


def first_user_prompt(ex: EvalExample) -> str:
    for m in ex.messages:
        if m.get("role") == "user":
            return m.get("content") or ""
    return ""


def load_split(split: str, data_dir: Path = DATA_DIR) -> List[EvalExample]:
    return [ex for ex in load_examples_jsonl(Path(data_dir) / f"eval_{split}.jsonl") if ex.expected_tool]


def _percentile(values: Sequence[float], q: float) -> float:
    s = sorted(values)
    if not s:
        return 0.0
    k = (len(s) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def selector_recall(examples: Sequence[EvalExample], ks: Sequence[int] = (1, 3, 5, 10)) -> Dict[str, Any]:
    """Recall@k, selection latency and the misses at the largest k in ``ks``."""
    import core.geoai.tool_definitions  # noqa: F401  (registers the canonical tools)
    from core.geoai.tool_selector import select_relevant_tools

    ks = sorted(set(int(k) for k in ks))
    kmax = max(ks)
    select_relevant_tools("warm up", None, max_tools=kmax)   # builds the cached index

    hits = {k: 0 for k in ks}
    latencies: List[float] = []
    misses: List[Dict[str, Any]] = []
    for ex in examples:
        prompt = first_user_prompt(ex)
        t0 = time.perf_counter()
        names = [t["function"]["name"] for t in select_relevant_tools(prompt, ex.context or None, max_tools=kmax)]
        latencies.append((time.perf_counter() - t0) * 1000.0)
        ok = {ex.expected_tool, *(ex.acceptable_tools or [])}
        for k in ks:
            hits[k] += bool(ok & set(names[:k]))
        if not ok & set(names[:ks[len(ks) // 2] if len(ks) > 1 else kmax]):
            misses.append({"id": ex.id, "prompt": prompt, "expected": ex.expected_tool, "offered": names[:5]})
    n = len(examples)
    return {
        "n": n,
        "recall": {k: (hits[k] / n if n else 0.0) for k in ks},
        "latency_ms": {"p50": _percentile(latencies, 0.5), "p95": _percentile(latencies, 0.95),
                       "max": max(latencies) if latencies else 0.0},
        "misses": misses,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Recall@k of the GeoAI tool selector on the eval splits.")
    ap.add_argument("--split", nargs="+", default=["val"], choices=SPLITS)
    ap.add_argument("--k", nargs="+", type=int, default=[1, 3, 5, 10])
    ap.add_argument("--data-dir", type=Path, default=DATA_DIR)
    ap.add_argument("--show-misses", type=int, default=0, help="print up to N misses (at the middle k)")
    ap.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = ap.parse_args(argv)

    report = {}
    for split in args.split:
        res = selector_recall(load_split(split, args.data_dir), args.k)
        report[split] = res
        if not args.json:
            rec = "  ".join(f"R@{k}={v:.3f}" for k, v in res["recall"].items())
            lat = res["latency_ms"]
            print(f"{split:5s} n={res['n']:4d}  {rec}  latency p50={lat['p50']:.2f}ms p95={lat['p95']:.2f}ms")
            for m in res["misses"][: args.show_misses]:
                print(f"   MISS {m['expected']:<45s} <- {m['prompt'][:110]!r}")
                print(f"        offered: {m['offered']}")
    if args.json:
        for res in report.values():
            res["recall"] = {str(k): v for k, v in res["recall"].items()}
        json.dump(report, sys.stdout, indent=2)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
