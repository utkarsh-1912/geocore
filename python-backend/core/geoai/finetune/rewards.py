# Author: Utkarsh Gupta
# License: GPL v3
"""
GRPO reward functions (TRL ``reward_funcs`` signature), pure Python.

* ``geoai_reward``  - the deterministic GeoAI scorer, used as-is:
                      ``core.geoai.eval.scoring.reward(example, completion)``.
                      No scoring logic is duplicated here.
* ``format_reward`` - small shaping term for things the scorer does not grade:
                      every ``<tool_call>`` block must be valid JSON with a name
                      and an argument object, nothing may follow the last call,
                      the decision plan must be one short "Plan:" line, and no
                      thinking block when thinking is disabled. (The scorer does
                      penalise a malformed call - it becomes an unknown tool with
                      schema=0 - but still gives partial action credit.)

TRL passes dataset columns as keyword lists; the GRPO dataset stores each
eval example as a JSON string in the ``example`` column and the turn type in
``turn_type``.
"""

import json
import re
from typing import Any, Dict, List, Optional

from core.geoai.finetune.formatting import PLAN_MAX_WORDS, PLAN_PREFIX

_TOOL_BLOCK = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)
_THINK = re.compile(r"<think>(.*?)</think>", re.DOTALL)


def completion_text(completion: Any) -> str:
    """TRL gives str (standard) or [{'role': 'assistant', 'content': ...}] (conversational)."""
    if completion is None:
        return ""
    if isinstance(completion, str):
        return completion
    if isinstance(completion, dict):
        return str(completion.get("content") or "")
    if isinstance(completion, (list, tuple)):
        return "".join(completion_text(c) for c in completion if not isinstance(c, dict) or c.get("role", "assistant") == "assistant")
    return str(completion)


def format_score(text: str, turn_type: str = "decision", plan_style: str = "brief", thinking: bool = False) -> float:
    """Format quality in [0, 1] (independent of engineering correctness)."""
    text = text or ""
    if not text.strip():
        return 0.0
    score = 1.0
    if not thinking:
        m = _THINK.search(text)
        if m and m.group(1).strip():
            score -= 0.5
        text = _THINK.sub("", text).strip()
    opens = text.count("<tool_call>")
    blocks = _TOOL_BLOCK.findall(text)
    if opens != len(blocks):
        return 0.0  # unterminated tool call
    for b in blocks:
        try:
            obj = json.loads(b)
        except json.JSONDecodeError:
            return 0.0
        if not isinstance(obj, dict) or not isinstance(obj.get("name"), str) or not isinstance(obj.get("arguments", {}), dict):
            return 0.0
    if blocks and text[text.rfind("</tool_call>") + len("</tool_call>"):].strip():
        score -= 0.25  # chatter after the call
    if turn_type == "decision" and plan_style == "brief":
        first = text.strip().splitlines()[0]
        if not first.startswith(PLAN_PREFIX):
            score -= 0.25
        elif len(first.split()) > PLAN_MAX_WORDS + 5:
            score -= 0.25
    return max(0.0, min(1.0, score))


def _col(kwargs: Dict[str, Any], name: str, i: int, default: Any = None) -> Any:
    v = kwargs.get(name)
    if isinstance(v, (list, tuple)) and i < len(v):
        return v[i]
    return default


def geoai_reward(prompts: List[Any], completions: List[Any], **kwargs) -> List[float]:
    """Deterministic scorer reward in [0, 1] per completion (TRL reward_func)."""
    from core.geoai.eval.scoring import reward

    out: List[float] = []
    for i, c in enumerate(completions):
        ex = _col(kwargs, "example", i)
        if isinstance(ex, str):
            ex = json.loads(ex)
        try:
            out.append(float(reward(ex, completion_text(c))))
        except Exception:
            out.append(0.0)  # a scorer failure must never crash training
    return out


def make_format_reward(plan_style: str = "brief", thinking: bool = False):
    def format_reward(prompts: List[Any], completions: List[Any], **kwargs) -> List[float]:
        return [format_score(completion_text(c), _col(kwargs, "turn_type", i, "decision") or "decision",
                             plan_style, thinking) for i, c in enumerate(completions)]
    format_reward.__name__ = "format_reward"
    return format_reward


def combined_reward(example: Dict[str, Any], completion: Any, *, format_weight: float = 0.1,
                    plan_style: str = "brief", thinking: bool = False) -> float:
    """Scalar used by the dry-run: scorer reward + weighted format reward (as TRL sums them)."""
    from core.geoai.eval.scoring import reward

    text = completion_text(completion)
    return float(reward(example, text)) + format_weight * format_score(
        text, example.get("turn_type", "decision"), plan_style, thinking)


def reward_sanity_check(examples: List[Dict[str, Any]], *, plan_style: str = "brief", format_weight: float = 0.1,
                        thinking: bool = False) -> Dict[str, Any]:
    """
    Score a gold completion and several deliberately bad completions for each
    example with the real reward (scorer + weighted format term). Used by the
    dry-runs to prove the reward separates good from bad before any GPU time.
    """
    from core.geoai.finetune.formatting import bad_completions, gold_completion

    pairs: List[Dict[str, Any]] = []
    per_kind: Dict[str, List[float]] = {}
    failures: List[Dict[str, Any]] = []
    for ex in examples:
        gold = gold_completion(ex, plan_style)
        if gold is None:
            continue
        g = combined_reward(ex, gold, format_weight=format_weight, plan_style=plan_style, thinking=thinking)
        bad = {k: combined_reward(ex, v, format_weight=format_weight, plan_style=plan_style, thinking=thinking)
               for k, v in bad_completions(ex).items()}
        for k, v in bad.items():
            per_kind.setdefault(k, []).append(v)
        pairs.append({"good": g, "bad": bad})
        if any(g <= b for b in bad.values()):
            failures.append({"id": ex.get("id"), "good": round(g, 4),
                             "beaten_by": {k: round(v, 4) for k, v in bad.items() if v >= g}})
    report: Dict[str, Any] = reward_separation(pairs)
    report["mean_bad_by_kind"] = {k: round(sum(v) / len(v), 4) for k, v in sorted(per_kind.items())}
    report["failures"] = failures[:10]
    report["max_reward"] = 1.0 + format_weight
    return report


def reward_separation(pairs: List[Dict[str, Any]], margin: float = 0.0) -> Dict[str, Optional[float]]:
    """Summarise [{'good': float, 'bad': {name: float}}] into separation statistics."""
    goods = [p["good"] for p in pairs]
    bads = [b for p in pairs for b in p["bad"].values()]
    wins = [all(p["good"] > b + margin for b in p["bad"].values()) for p in pairs]
    mean = lambda xs: round(sum(xs) / len(xs), 4) if xs else None  # noqa: E731
    return {
        "n_examples": len(pairs),
        "mean_good": mean(goods),
        "mean_bad": mean(bads),
        "min_good": round(min(goods), 4) if goods else None,
        "max_bad": round(max(bads), 4) if bads else None,
        "win_rate": mean([1.0 if w else 0.0 for w in wins]),
    }
