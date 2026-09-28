# Author: Utkarsh Gupta
# License: GPL v3
"""
GeoAI evaluation runner (AGENTS.md §21, §31-32).

Runs evaluation examples through the real GeoAI path — ``GeoAIAgent`` with a
``ModelProvider`` (heuristic or llama.cpp/GGUF) and the GeoAI Tool Registry —
scores every turn with the deterministic scorer and writes a small JSON report.

Decision turns use ``GeoAIAgent.run`` (``--mode agent``, default; full loop incl.
tool execution and the explanation round) or only the first model call built by
the agent's own prompt/tool-selection code (``--mode decision``; faster).
Final-answer turns (prefix already contains the real tool result) call
``provider.generate`` with the same system prompt the agent uses.

Examples:
    python -m core.geoai.eval.runner --provider heuristic --split test --out results.json
    python -m core.geoai.eval.runner --provider llama_cpp --model PATH.gguf --split test --limit 50 --out qwen.json
    python -m core.geoai.eval.runner --compare base.json finetuned.json
"""

import argparse
import ctypes
import json
import math
import os
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence

from core.geoai.eval.example import EvalExample
from core.geoai.eval.scoring import SIDE_EFFECT_TOOLS, ParsedResponse, default_registry, project_fixture, score_turn
from core.geoai.exceptions import GeoAIValidationError
from core.geoai.model_provider import (
    ChatMessage,
    MessageRole,
    ModelProvider,
    ModelResponse,
    StreamChunk,
    ToolCall,
    make_system_message,
)
from core.geoai.system_prompt import build_system_prompt
from core.geoai.tool_registry import GeoAIToolRegistry

RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULT_SCHEMA_VERSION = 1


# =====================================================================
# Instrumentation
# =====================================================================

@dataclass
class _Call:
    response: Optional[ModelResponse]
    latency_s: float
    tools_offered: List[str]
    error: Optional[str] = None


class RecordingProvider(ModelProvider):
    """Transparent ModelProvider wrapper that records every generate() call and its latency."""

    def __init__(self, inner: ModelProvider):
        self.inner = inner
        self.calls: List[_Call] = []

    def reset(self) -> None:
        self.calls = []

    def generate(self, messages, tools=None, temperature=0.1, max_tokens=1024) -> ModelResponse:
        offered = [t.get("function", {}).get("name", "") for t in (tools or [])]
        t0 = time.perf_counter()
        try:
            resp = self.inner.generate(messages, tools=tools, temperature=temperature, max_tokens=max_tokens)
        except Exception as e:
            self.calls.append(_Call(None, time.perf_counter() - t0, offered, error=str(e)))
            raise
        self.calls.append(_Call(resp, time.perf_counter() - t0, offered))
        return resp

    def generate_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024) -> Iterator[StreamChunk]:
        return self.inner.generate_stream(messages, tools=tools, temperature=temperature, max_tokens=max_tokens)

    def is_loaded(self) -> bool:
        return self.inner.is_loaded()

    def model_info(self) -> Dict[str, Any]:
        return self.inner.model_info()


class EvalRegistry(GeoAIToolRegistry):
    """Registry view used during evaluation: identical tools, but state-mutating tools are blocked."""

    def __init__(self, base: GeoAIToolRegistry):
        super().__init__()
        self._base = base
        self._tools = base._tools

    def invoke_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name in SIDE_EFFECT_TOOLS:
            raise GeoAIValidationError(f"Tool '{tool_name}' is disabled during evaluation (side effects).")
        return self._base.invoke_tool(tool_name, args)


def peak_memory_mb() -> Optional[float]:
    """Peak resident memory of this process in MB (psutil if available, else OS APIs)."""
    try:
        import psutil  # type: ignore
        mi = psutil.Process(os.getpid()).memory_info()
        return round((getattr(mi, "peak_wset", None) or mi.rss) / 2 ** 20, 1)
    except ImportError:
        pass
    try:
        if os.name == "nt":
            class PMC(ctypes.Structure):
                _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
                            ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                            ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
            pmc = PMC()
            pmc.cb = ctypes.sizeof(PMC)
            k32 = ctypes.WinDLL("kernel32")
            psapi = ctypes.WinDLL("psapi")
            k32.GetCurrentProcess.restype = ctypes.c_void_p
            psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(PMC), ctypes.c_ulong]
            if psapi.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb):
                return round(pmc.PeakWorkingSetSize / 2 ** 20, 1)
            return None
        import resource
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return round(peak / (2 ** 20 if sys.platform == "darwin" else 1024), 1)
    except Exception:
        return None


def _percentile(values: Sequence[float], q: float) -> Optional[float]:
    if not values:
        return None
    s = sorted(values)
    k = (len(s) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return round(s[lo] + (s[hi] - s[lo]) * (k - lo), 4)


# =====================================================================
# Providers
# =====================================================================

def make_provider(name: str, model_path: Optional[str] = None, n_ctx: int = 4096, n_gpu_layers: int = 0) -> ModelProvider:
    if name == "heuristic":
        from core.geoai.heuristic_provider import HeuristicProvider
        return HeuristicProvider()
    if name == "llama_cpp":
        from core.geoai.llama_cpp_provider import LlamaCppProvider
        from core.geoai.model_config import GeoAIModelConfig, find_gguf_models
        if not model_path:
            found = find_gguf_models()
            if not found:
                raise RuntimeError("No GGUF model found; pass --model PATH.")
            model_path = str(found[0])
        cfg = GeoAIModelConfig(model_path=model_path, n_ctx=n_ctx, n_gpu_layers=n_gpu_layers, provider="llama_cpp")
        return LlamaCppProvider(cfg)
    raise ValueError(f"Unknown provider '{name}' (expected heuristic | llama_cpp)")


def force_llama_tool_choice(provider: ModelProvider, choice: str = "auto") -> None:
    """
    EVAL-ONLY adapter. ``LlamaCppProvider.generate`` passes ``tools`` without
    ``tool_choice``; llama-cpp-python's ``chatml-function-calling`` handler then
    renders the prompt WITHOUT the tools, so the model can never call one.
    This wraps the loaded ``Llama.create_chat_completion`` to add
    ``tool_choice`` so the runner can measure the effect of the provider fix
    without modifying the provider. Production behaviour is unchanged.
    """
    provider.load()  # type: ignore[attr-defined]
    llama = provider._model  # type: ignore[attr-defined]
    inner = llama.create_chat_completion

    def create_chat_completion(**kwargs):
        if kwargs.get("tools") and "tool_choice" not in kwargs:
            kwargs["tool_choice"] = choice
        return inner(**kwargs)

    llama.create_chat_completion = create_chat_completion


def _to_chat_messages(msgs: List[Dict[str, Any]]) -> List[ChatMessage]:
    out = []
    for m in msgs:
        calls = None
        if m.get("tool_calls"):
            calls = []
            for tc in m["tool_calls"]:
                fn = tc.get("function", tc)
                args = fn.get("arguments") or {}
                if isinstance(args, str):
                    args = json.loads(args)
                calls.append(ToolCall(id=tc.get("id", ""), function_name=fn.get("name", ""), arguments=args))
        out.append(ChatMessage(role=MessageRole(m["role"]), content=m.get("content"), tool_calls=calls,
                               tool_call_id=m.get("tool_call_id"), name=m.get("name")))
    return out


# =====================================================================
# Running
# =====================================================================

def run_example(ex: EvalExample, rec: RecordingProvider, registry: GeoAIToolRegistry, *,
                mode: str = "agent", execute: bool = True) -> Dict[str, Any]:
    from core.geoai.agent import GeoAIAgent
    rec.reset()
    error = None
    final_text = None
    t0 = time.perf_counter()
    try:
        with project_fixture(ex):  # project-data examples run against their synthetic project
            if ex.turn_type == "final_answer":
                messages = [make_system_message(build_system_prompt(ex.context))] + _to_chat_messages(ex.messages)
                rec.generate(messages, tools=None, temperature=0.1, max_tokens=512)
            elif len(ex.messages) > 1:
                # Later step of a multi-step trajectory: the prefix holds earlier tool calls and their
                # real results, which GeoAIAgent.run cannot take, so judge the next decision directly
                # with the agent's own system prompt and tool selection.
                agent = GeoAIAgent(rec, registry)
                messages, tools = agent._build_messages(ex.user_prompt, ex.context)
                messages = messages[:1] + _to_chat_messages(ex.messages)
                rec.generate(messages, tools=tools, temperature=0.1, max_tokens=1024)
            else:
                agent = GeoAIAgent(rec, registry)
                if mode == "agent":
                    final_text = agent.run(ex.user_prompt, ex.context).response_text
                else:
                    messages, tools = agent._build_messages(ex.user_prompt, ex.context)
                    rec.generate(messages, tools=tools, temperature=0.1, max_tokens=1024)
    except Exception as e:  # generation failure is a scored failure, not a crash
        error = f"{type(e).__name__}: {str(e)[:300]}"
    latency = time.perf_counter() - t0

    first = rec.calls[0] if rec.calls else None
    response = first.response if first and first.response is not None else ParsedResponse()
    sb = score_turn(ex, response, registry=registry, execute=execute)
    offered = first.tools_offered if first else []
    return {
        "id": ex.id,
        "category": ex.category,
        "turn_type": ex.turn_type,
        "expected_action": ex.expected_action,
        "expected_tool": ex.expected_tool,
        "score": sb.to_dict(),
        "latency_s": round(latency, 4),
        "decision_latency_s": round(first.latency_s, 4) if first else None,
        "n_model_calls": len(rec.calls),
        "expected_tool_offered": (ex.expected_tool in offered) if (ex.expected_tool and ex.turn_type == "decision") else None,
        "response_text": (getattr(response, "content", None) or "")[:400],
        "final_text": (final_text or "")[:400] if final_text else None,
        "usage": getattr(response, "usage", None),
        "error": error,
    }


def _stratified_limit(examples: List[EvalExample], limit: Optional[int]) -> List[EvalExample]:
    if not limit or limit >= len(examples):
        return examples
    by_cat: Dict[str, List[EvalExample]] = defaultdict(list)
    for ex in sorted(examples, key=lambda e: e.id):
        by_cat[(ex.category, ex.turn_type)].append(ex)
    keys = sorted(by_cat)
    out: List[EvalExample] = []
    i = 0
    while len(out) < limit:
        progressed = False
        for k in keys:
            if i < len(by_cat[k]) and len(out) < limit:
                out.append(by_cat[k][i])
                progressed = True
        if not progressed:
            break
        i += 1
    return out


def summarise(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    def mean(xs):
        xs = [x for x in xs if x is not None]
        return round(sum(xs) / len(xs), 4) if xs else None

    sc = [r["score"] for r in records]
    dec = [r for r in records if r["turn_type"] == "decision"]
    tool_exp = [r for r in dec if r["expected_action"] == "tool_call" and r["expected_tool"]]
    clar_exp = [r for r in dec if r["expected_action"] in ("clarify", "reject")]
    predicted_calls = [r for r in records if r["score"]["predicted_action"] == "tool_call"]
    valid_calls = [r for r in predicted_calls if not r["score"]["hallucinated_tool"]]

    metrics: Dict[str, Any] = {
        "n": len(records),
        "mean_score": mean(s["total"] for s in sc),
        "strict_pass_rate": mean(1.0 if s["passed"] else 0.0 for s in sc),
        "action_accuracy": mean(1.0 if s["action"] == 1.0 else 0.0 for s in sc),
        "tool_selection_accuracy": mean(1.0 if r["score"]["tool"] == 1.0 else 0.0 for r in tool_exp),
        "tool_selection_accuracy_incl_equivalent": mean(1.0 if (r["score"]["tool"] or 0) > 0 else 0.0 for r in tool_exp),
        "argument_accuracy": mean(r["score"]["arguments"] for r in tool_exp),
        "schema_valid_rate": mean(r["score"]["schema"] for r in predicted_calls),
        "clarification_accuracy": mean(1.0 if r["score"]["action"] == 1.0 else 0.0 for r in clar_exp),
        "clarification_keyword_score": mean(r["score"]["clarification"] for r in clar_exp),
        "hallucinated_parameter_rate": mean(
            1.0 if (r["score"]["invented_params"] or r["score"]["unknown_params"]) else 0.0 for r in valid_calls),
        "hallucinated_tool_rate": mean(1.0 if r["score"]["hallucinated_tool"] else 0.0 for r in predicted_calls),
        "unit_trap_accuracy": mean(s["unit_trap"] for s in sc),
        "execution_match_rate": mean(s["execution"] for s in sc),
        "final_answer_grounding": mean(r["score"]["grounding"] for r in records if r["turn_type"] == "final_answer"),
        "caution_violation_rate": mean(None if s["caution"] is None else 1.0 - s["caution"] for s in sc),
        "selector_recall": mean(None if r["expected_tool_offered"] is None else (1.0 if r["expected_tool_offered"] else 0.0) for r in tool_exp),
        "error_rate": mean(1.0 if r["error"] else 0.0 for r in records),
        "latency_p50_s": _percentile([r["latency_s"] for r in records], 0.5),
        "latency_p95_s": _percentile([r["latency_s"] for r in records], 0.95),
        "decision_latency_p50_s": _percentile([r["decision_latency_s"] for r in records if r["decision_latency_s"] is not None], 0.5),
        "decision_latency_p95_s": _percentile([r["decision_latency_s"] for r in records if r["decision_latency_s"] is not None], 0.95),
    }
    per_cat: Dict[str, Dict[str, Any]] = {}
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in records:
        groups[r["category"]].append(r)
        groups[f"turn:{r['turn_type']}"].append(r)
    for k, rs in sorted(groups.items()):
        per_cat[k] = {
            "n": len(rs),
            "pass_rate": mean(1.0 if r["score"]["passed"] else 0.0 for r in rs),
            "mean_score": mean(r["score"]["total"] for r in rs),
            "action_accuracy": mean(1.0 if r["score"]["action"] == 1.0 else 0.0 for r in rs),
        }
    metrics["per_category"] = per_cat
    return metrics


def run_eval(examples: List[EvalExample], provider: ModelProvider, *, mode: str = "agent", execute: bool = True,
             registry: Optional[GeoAIToolRegistry] = None, progress: bool = False) -> Dict[str, Any]:
    reg = EvalRegistry(registry if registry is not None else default_registry())
    rec = RecordingProvider(provider)
    mem_start = peak_memory_mb()
    load_s = None
    if hasattr(provider, "load"):
        t0 = time.perf_counter()
        provider.load()
        load_s = round(time.perf_counter() - t0, 2)
    records = []
    t_start = time.perf_counter()
    for i, ex in enumerate(examples, 1):
        records.append(run_example(ex, rec, reg, mode=mode, execute=execute))
        if progress and (i % 10 == 0 or i == len(examples)):
            done = records[-10:]
            print(f"  [{i}/{len(examples)}] last-10 pass={sum(r['score']['passed'] for r in done)}/{len(done)} "
                  f"elapsed={time.perf_counter() - t_start:.0f}s", flush=True)
    metrics = summarise(records)
    metrics["model_load_s"] = load_s
    metrics["peak_memory_mb"] = peak_memory_mb()
    metrics["memory_at_start_mb"] = mem_start
    metrics["wall_time_s"] = round(time.perf_counter() - t_start, 2)
    return {"metrics": metrics, "records": records}


# =====================================================================
# Reporting / comparison
# =====================================================================

_TABLE_KEYS = ("n", "mean_score", "strict_pass_rate", "action_accuracy", "tool_selection_accuracy",
               "argument_accuracy", "schema_valid_rate", "clarification_accuracy", "hallucinated_parameter_rate",
               "unit_trap_accuracy", "execution_match_rate", "final_answer_grounding", "caution_violation_rate",
               "selector_recall", "error_rate", "latency_p50_s", "latency_p95_s", "peak_memory_mb")


def _fmt(v: Any) -> str:
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def format_table(metrics: Dict[str, Any]) -> str:
    lines = [f"{'metric':<34}{'value':>10}"]
    for k in _TABLE_KEYS:
        lines.append(f"{k:<34}{_fmt(metrics.get(k)):>10}")
    lines.append("")
    lines.append(f"{'category':<24}{'n':>5}{'pass':>8}{'score':>8}{'action':>8}")
    for k, v in metrics.get("per_category", {}).items():
        lines.append(f"{k:<24}{v['n']:>5}{_fmt(v['pass_rate']):>8}{_fmt(v['mean_score']):>8}{_fmt(v['action_accuracy']):>8}")
    return "\n".join(lines)


def compare_results(base: Dict[str, Any], cand: Dict[str, Any]) -> Dict[str, Any]:
    """Paired comparison of two result files (e.g. base vs fine-tuned, Qwen vs Gemma)."""
    bm, cm = base["metrics"], cand["metrics"]
    deltas = {}
    for k in _TABLE_KEYS:
        b, c = bm.get(k), cm.get(k)
        deltas[k] = {"base": b, "candidate": c,
                     "delta": round(c - b, 4) if isinstance(b, (int, float)) and isinstance(c, (int, float)) else None}
    cats = {}
    for k in sorted(set(bm.get("per_category", {})) | set(cm.get("per_category", {}))):
        b = bm.get("per_category", {}).get(k, {}).get("pass_rate")
        c = cm.get("per_category", {}).get(k, {}).get("pass_rate")
        cats[k] = {"base": b, "candidate": c,
                   "delta": round(c - b, 4) if b is not None and c is not None else None}
    bp, cp = base.get("per_example", {}), cand.get("per_example", {})
    shared = sorted(set(bp) & set(cp))
    fixed = [i for i in shared if not bp[i][1] and cp[i][1]]
    regressed = [i for i in shared if bp[i][1] and not cp[i][1]]
    same_set = set(bp) == set(cp)
    return {"base": base.get("meta", {}), "candidate": cand.get("meta", {}), "same_examples": same_set,
            "n_shared": len(shared), "metrics": deltas, "per_category_pass_rate": cats,
            "fixed": len(fixed), "regressed": len(regressed), "regressed_ids": regressed[:50]}


def format_comparison(cmp: Dict[str, Any]) -> str:
    b = cmp["base"].get("label") or cmp["base"].get("provider")
    c = cmp["candidate"].get("label") or cmp["candidate"].get("provider")
    lines = [f"base={b}  candidate={c}  shared={cmp['n_shared']}  same_examples={cmp['same_examples']}",
             f"{'metric':<34}{'base':>9}{'cand':>9}{'delta':>9}"]
    for k, v in cmp["metrics"].items():
        lines.append(f"{k:<34}{_fmt(v['base']):>9}{_fmt(v['candidate']):>9}{_fmt(v['delta']):>9}")
    lines.append("")
    lines.append(f"{'category pass-rate':<34}{'base':>9}{'cand':>9}{'delta':>9}")
    for k, v in cmp["per_category_pass_rate"].items():
        lines.append(f"{k:<34}{_fmt(v['base']):>9}{_fmt(v['candidate']):>9}{_fmt(v['delta']):>9}")
    lines.append(f"\npaired: fixed={cmp['fixed']} regressed={cmp['regressed']}")
    return "\n".join(lines)


def build_report(run: Dict[str, Any], meta: Dict[str, Any], keep_records: str = "failures",
                 max_records: Optional[int] = 100) -> Dict[str, Any]:
    records = run["records"]
    if keep_records == "none":
        kept = []
    elif keep_records == "all":
        kept = records
    else:
        kept = [r for r in records if not r["score"]["passed"]]
    if max_records is not None and len(kept) > max_records:
        # keep a deterministic, category-balanced sample so result files stay small
        by_cat: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for r in sorted(kept, key=lambda r: r["id"]):
            by_cat[r["category"]].append(r)
        sampled: List[Dict[str, Any]] = []
        i = 0
        while len(sampled) < max_records:
            added = False
            for cat in sorted(by_cat):
                if i < len(by_cat[cat]) and len(sampled) < max_records:
                    sampled.append(by_cat[cat][i])
                    added = True
            if not added:
                break
            i += 1
        kept = sampled
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "meta": meta,
        "metrics": run["metrics"],
        "per_example": {r["id"]: [r["score"]["total"], r["score"]["passed"]] for r in records},
        "records": kept,
    }


# =====================================================================
# CLI
# =====================================================================

def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Run the GeoAI evaluation suite.")
    ap.add_argument("--provider", choices=("heuristic", "llama_cpp"), default="heuristic")
    ap.add_argument("--model", help="Path to GGUF model (llama_cpp)")
    ap.add_argument("--label", help="Human label for this run (e.g. qwen2.5-1.5b-q4km-base)")
    ap.add_argument("--split", default="test", choices=("train", "val", "test", "gold"))
    ap.add_argument("--dataset", type=Path, help="Eval JSONL file (overrides --split)")
    ap.add_argument("--limit", type=int, help="Stratified subset size")
    ap.add_argument("--turn-type", choices=("decision", "final_answer"))
    ap.add_argument("--mode", choices=("agent", "decision"), default="agent")
    ap.add_argument("--no-execute", action="store_true", help="Skip the end-to-end Groundhog check")
    ap.add_argument("--n-ctx", type=int, default=4096)
    ap.add_argument("--n-gpu-layers", type=int, default=0)
    ap.add_argument("--llama-tool-choice", choices=("provider", "auto"), default="provider",
                    help="'provider' = production LlamaCppProvider behaviour; 'auto' = eval-only adapter "
                         "that passes tool_choice='auto' (see force_llama_tool_choice)")
    ap.add_argument("--records", choices=("failures", "all", "none"), default="failures")
    ap.add_argument("--max-records", type=int, default=60, help="Cap on stored records (0 = no cap)")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--compare", nargs=2, type=Path, metavar=("BASE", "CANDIDATE"))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    if args.compare:
        with open(args.compare[0], encoding="utf-8") as f:
            base = json.load(f)
        with open(args.compare[1], encoding="utf-8") as f:
            cand = json.load(f)
        cmp = compare_results(base, cand)
        print(format_comparison(cmp))
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(cmp, f, indent=2)
        return 0

    from core.geoai.training.scaleup import DEFAULT_SEED, GENERATOR_VERSION, load_split
    from core.geoai.eval.example import load_examples_jsonl
    examples = load_examples_jsonl(args.dataset) if args.dataset else load_split(args.split)
    if args.turn_type:
        examples = [e for e in examples if e.turn_type == args.turn_type]
    examples = _stratified_limit(examples, args.limit)

    provider = make_provider(args.provider, args.model, n_ctx=args.n_ctx, n_gpu_layers=args.n_gpu_layers)
    if args.provider == "llama_cpp" and args.llama_tool_choice == "auto":
        force_llama_tool_choice(provider, "auto")
    print(f"GeoAI eval: provider={args.provider} split={args.split} n={len(examples)} mode={args.mode}", flush=True)
    run = run_eval(examples, provider, mode=args.mode, execute=not args.no_execute, progress=not args.quiet)
    meta = {
        "label": args.label or args.provider,
        "provider": args.provider,
        "model_info": provider.model_info(),
        "split": str(args.dataset) if args.dataset else args.split,
        "limit": args.limit, "turn_type": args.turn_type, "mode": args.mode,
        "n_ctx": args.n_ctx if args.provider == "llama_cpp" else None,
        "llama_tool_choice": args.llama_tool_choice if args.provider == "llama_cpp" else None,
        "dataset_generator_version": GENERATOR_VERSION, "dataset_seed": DEFAULT_SEED,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": sys.version.split()[0], "platform": sys.platform,
    }
    report = build_report(run, meta, keep_records=args.records, max_records=args.max_records or None)
    print(format_table(run["metrics"]))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=1, default=str)
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
