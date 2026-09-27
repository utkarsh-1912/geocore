# Author: Utkarsh Gupta
# License: GPL v3
"""
Data preparation for GeoAI fine-tuning (pure Python; no torch/transformers).

* ``prepare_sft_example``   - one ``sft_*.jsonl`` row -> {"messages", "tools"} ready
                              for ``tokenizer.apply_chat_template(messages, tools=tools)``,
                              with an optional one-line "Plan: ..." before the decision.
* ``validate_sft_example``  - structural checks (roles, tool-call/tool-result pairing,
                              tool names offered, argument objects).
* ``render_reference_chatml`` + ``trainable_spans`` - tokenizer-free rendering in the
                              Qwen2.5 Hermes/ChatML layout and an emulation of
                              assistant-only loss masking, used by ``--dry-run``.
* ``build_grpo_record``     - an ``eval_*.jsonl`` example -> GRPO prompt (same system
                              prompt and tool subset the runtime agent builds).
* ``gold_completion`` / ``bad_completions`` - reference and deliberately wrong
                              completions used to prove the reward separates them.

Data formats are defined by ``core.geoai.training.scaleup`` and
``core.geoai.eval.example``; nothing here re-defines them.
"""

import copy
import json
import math
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

from core.geoai.finetune.config import HELD_OUT_SPLITS, FinetuneConfig

PLAN_PREFIX = "Plan:"
PLAN_MAX_WORDS = 25
# Measured with the Qwen2.5 tokenizer (GGUF vocab) on sft_val.jsonl: ~3.3 chars/token.
CHARS_PER_TOKEN = 3.3

_CATEGORY_PLANS = {
    "missing_data": "a required input is missing; ask for it instead of assuming a value.",
    "ambiguous_request": "the request is ambiguous; ask which calculation and inputs are intended.",
    "wrong_units": "a value has the wrong unit or dimension; flag it and ask for the correct value.",
    "conflicting_data": "the sources disagree; point out the conflict and ask which value to use.",
    "research": "answer only from retrieved evidence; do not invent sources.",
    "tool_failure": "the input cannot be used as given; explain the problem.",
}


# =====================================================================
# IO
# =====================================================================

def assert_trainable_file(path: Path) -> None:
    """Refuse to train on held-out evaluation files (eval_test / eval_gold)."""
    name = Path(path).name.lower()
    for split in HELD_OUT_SPLITS:
        if name.startswith(f"eval_{split}") or name.startswith(f"sft_{split}"):
            raise ValueError(f"{name} is a held-out split and must never be used for training")


def iter_jsonl(path: Path, limit: Optional[int] = None) -> Iterator[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        n = 0
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)
            n += 1
            if limit is not None and n >= limit:
                return


def load_training_jsonl(path: Path, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    assert_trainable_file(path)
    return list(iter_jsonl(path, limit))


# =====================================================================
# SFT preparation
# =====================================================================

def _args_as_object(args: Any) -> Dict[str, Any]:
    if isinstance(args, dict):
        return args
    if isinstance(args, str):
        try:
            v = json.loads(args) if args.strip() else {}
            return v if isinstance(v, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def _decision_index(messages: List[Dict[str, Any]]) -> Optional[int]:
    """Index of the first assistant message after the last user message."""
    last_user = max((i for i, m in enumerate(messages) if m.get("role") == "user"), default=None)
    if last_user is None:
        return None
    for i in range(last_user + 1, len(messages)):
        if messages[i].get("role") == "assistant":
            return i
    return None


def make_plan(messages: List[Dict[str, Any]], category: Optional[str]) -> Optional[str]:
    """
    One-line plan for the decision turn (no numbers, so it can never invent a value).
    Returns None when there is no decision turn.
    """
    i = _decision_index(messages)
    if i is None:
        return None
    msg = messages[i]
    calls = msg.get("tool_calls") or []
    if calls:
        fn = calls[0].get("function", calls[0])
        names = list(_args_as_object(fn.get("arguments")).keys())
        has_ctx = any(m.get("role") == "system" and "### CURRENT CONTEXT" in (m.get("content") or "") for m in messages)
        source = "the request and project context" if has_ctx else "the request"
        shown = ", ".join(names[:6]) + (", ..." if len(names) > 6 else "")
        plan = f"{PLAN_PREFIX} call {fn.get('name')} with {shown or 'no arguments'} from {source}."
    else:
        plan = f"{PLAN_PREFIX} {_CATEGORY_PLANS.get(category or '', 'answer directly from the given information.')}"
    words = plan.split()
    if len(words) > PLAN_MAX_WORDS:
        plan = " ".join(words[:PLAN_MAX_WORDS]).rstrip(",.") + "."
    return plan


def _trim_tools(tools: List[Dict[str, Any]], called: List[str], max_tools: Optional[int]) -> List[Dict[str, Any]]:
    if not max_tools or len(tools) <= max_tools:
        return tools
    keep = [t for t in tools if t.get("function", {}).get("name") in called]
    rest = [t for t in tools if t.get("function", {}).get("name") not in called]
    return keep + rest[: max(0, max_tools - len(keep))]


def prepare_sft_example(row: Dict[str, Any], cfg: FinetuneConfig) -> Dict[str, Any]:
    """sft_*.jsonl row -> {"id", "category", "messages", "tools"} (input row is not mutated)."""
    msgs = copy.deepcopy(row["messages"])
    called: List[str] = []
    for m in msgs:
        for tc in m.get("tool_calls") or []:
            fn = tc.setdefault("function", {})
            fn["arguments"] = _args_as_object(fn.get("arguments"))
            called.append(fn.get("name", ""))
        if m.get("role") == "assistant" and m.get("content") is None:
            m["content"] = ""
    if cfg.plan_style == "brief":
        plan = make_plan(msgs, row.get("category"))
        i = _decision_index(msgs)
        if plan and i is not None:
            body = (msgs[i].get("content") or "").strip()
            msgs[i]["content"] = plan if not body else f"{plan}\n{body}"
    tools = _trim_tools(list(row.get("tools") or []), called, cfg.max_tools)
    return {"id": row.get("id"), "category": row.get("category"), "messages": msgs, "tools": tools}


def validate_sft_example(ex: Dict[str, Any]) -> List[str]:
    """Return a list of structural problems (empty list = OK)."""
    problems: List[str] = []
    msgs = ex.get("messages") or []
    tool_names = {t.get("function", {}).get("name") for t in ex.get("tools") or []}
    if not msgs:
        return ["no messages"]
    if msgs[0].get("role") != "system":
        problems.append("first message is not the system prompt")
    if not any(m.get("role") == "user" for m in msgs):
        problems.append("no user message")
    pending: Dict[str, str] = {}
    for i, m in enumerate(msgs):
        role = m.get("role")
        if role not in ("system", "user", "assistant", "tool"):
            problems.append(f"message {i}: unknown role {role!r}")
        if role == "assistant":
            for tc in m.get("tool_calls") or []:
                fn = tc.get("function", {})
                if fn.get("name") not in tool_names:
                    problems.append(f"message {i}: tool '{fn.get('name')}' is not in the offered tools")
                if not isinstance(fn.get("arguments"), dict):
                    problems.append(f"message {i}: tool arguments are not a JSON object")
                pending[tc.get("id", "")] = fn.get("name", "")
        if role == "tool":
            tcid = m.get("tool_call_id", "")
            if tcid not in pending:
                problems.append(f"message {i}: tool result without a matching tool call")
            elif m.get("name") and m["name"] != pending[tcid]:
                problems.append(f"message {i}: tool result name does not match the call")
            try:
                json.loads(m.get("content") or "")
            except json.JSONDecodeError:
                problems.append(f"message {i}: tool result is not JSON")
    last = msgs[-1]
    if last.get("role") != "assistant" or (not (last.get("content") or "").strip() and not last.get("tool_calls")):
        problems.append("conversation does not end with a non-empty assistant turn")
    return problems


def render_reference_chatml(messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Tokenizer-free rendering in the Qwen2.5 Hermes/ChatML layout (mirrors the
    GGUF/HF chat template). Only used for dry-run checks and length estimates;
    real training always renders with the model's own tokenizer template.
    """
    out: List[str] = []
    sys_msg = messages[0]["content"] if messages and messages[0].get("role") == "system" else "You are a helpful assistant."
    if tools:
        out.append("<|im_start|>system\n" + sys_msg + "\n\n# Tools\n\nYou may call one or more functions to assist "
                   "with the user query.\n\nYou are provided with function signatures within <tools></tools> XML tags:\n<tools>")
        for t in tools:
            out.append("\n" + json.dumps(t, ensure_ascii=False))
        out.append("\n</tools>\n\nFor each function call, return a json object with function name and arguments within "
                   "<tool_call></tool_call> XML tags:\n<tool_call>\n{\"name\": <function-name>, \"arguments\": "
                   "<args-json-object>}\n</tool_call><|im_end|>\n")
    else:
        out.append("<|im_start|>system\n" + sys_msg + "<|im_end|>\n")
    start = 1 if messages and messages[0].get("role") == "system" else 0
    for i in range(start, len(messages)):
        m = messages[i]
        role = m.get("role")
        if role == "user" or (role == "assistant" and not m.get("tool_calls")) or role == "system":
            out.append(f"<|im_start|>{role}\n{m.get('content') or ''}<|im_end|>\n")
        elif role == "assistant":
            out.append("<|im_start|>assistant")
            if m.get("content"):
                out.append("\n" + m["content"])
            for tc in m["tool_calls"]:
                fn = tc.get("function", tc)
                out.append('\n<tool_call>\n{"name": "' + str(fn.get("name")) + '", "arguments": '
                           + json.dumps(_args_as_object(fn.get("arguments")), ensure_ascii=False) + "}\n</tool_call>")
            out.append("<|im_end|>\n")
        elif role == "tool":
            if i == 0 or messages[i - 1].get("role") != "tool":
                out.append("<|im_start|>user")
            out.append("\n<tool_response>\n" + (m.get("content") or "") + "\n</tool_response>")
            if i == len(messages) - 1 or messages[i + 1].get("role") != "tool":
                out.append("<|im_end|>\n")
    return "".join(out)


def trainable_spans(text: str, instruction_part: str, response_part: str) -> List[str]:
    """
    Emulate Unsloth ``train_on_responses_only``: loss is computed on the text that
    follows each ``response_part`` up to the next ``instruction_part``.
    """
    spans: List[str] = []
    pos = 0
    while True:
        r = text.find(response_part, pos)
        if r < 0:
            break
        s = r + len(response_part)
        nxt = text.find(instruction_part, s)
        spans.append(text[s: nxt if nxt >= 0 else len(text)])
        pos = s
    return spans


def estimate_tokens(text: str) -> int:
    return int(math.ceil(len(text) / CHARS_PER_TOKEN))


# =====================================================================
# GRPO prompts (eval examples)
# =====================================================================

ToolsFor = Callable[[str, Optional[Dict[str, Any]], Optional[str]], List[Dict[str, Any]]]


def registry_tools_for() -> Tuple[ToolsFor, Any]:
    """
    Return (tools_for, context_manager) reusing the dataset generator's own tool
    subset logic (runtime selector + expected tool guaranteed to be offered),
    so GRPO prompts match the SFT data. Imports the GeoAI registry (Groundhog).
    """
    from core.geoai.eval.scoring import default_registry
    from core.geoai.slm_schema_generator import generate_openai_tool_definitions
    from core.geoai.training.scaleup import _cached_tool_definitions, _tools_for

    default_registry()  # registers the canonical GeoAI tools (core.geoai.tool_definitions) first
    ctx = _cached_tool_definitions()
    state: Dict[str, Any] = {}

    def tools_for(prompt: str, context: Optional[Dict[str, Any]], expected_tool: Optional[str]) -> List[Dict[str, Any]]:
        if "all_defs" not in state:
            state["all_defs"] = {t["function"]["name"]: t for t in generate_openai_tool_definitions()}
        tools, _miss = _tools_for(prompt, context, expected_tool, state["all_defs"])
        return tools

    return tools_for, ctx


def build_grpo_record(example: Dict[str, Any], tools_for: Optional[ToolsFor],
                      max_tools: Optional[int] = None) -> Dict[str, Any]:
    """
    eval_*.jsonl example -> {"prompt": [messages], "tools": [...]|None, "example": json str, ...}.

    Decision turns get the agent's system prompt + user message + tool subset;
    final-answer turns get the full prefix (tool call + real tool result) and no
    tools, exactly as the eval runner does.
    """
    from core.geoai.system_prompt import build_system_prompt

    if example.get("split") in HELD_OUT_SPLITS:
        raise ValueError(f"example {example.get('id')} is from held-out split {example.get('split')!r}")
    msgs = [{"role": "system", "content": build_system_prompt(example.get("context"))}]
    for m in example.get("messages") or []:
        m = copy.deepcopy(m)
        for tc in m.get("tool_calls") or []:
            fn = tc.setdefault("function", {})
            fn["arguments"] = _args_as_object(fn.get("arguments"))
        msgs.append(m)
    tools = None
    if example.get("turn_type", "decision") == "decision" and tools_for is not None:
        user = next((m.get("content") or "" for m in reversed(example.get("messages") or []) if m.get("role") == "user"), "")
        tools = tools_for(user, example.get("context"), example.get("expected_tool"))
        tools = _trim_tools(tools, [example.get("expected_tool") or ""], max_tools)
    return {
        "id": example.get("id"),
        "category": example.get("category"),
        "turn_type": example.get("turn_type", "decision"),
        "prompt": msgs,
        "tools": tools,
        "example": json.dumps(example, ensure_ascii=False),
    }


# =====================================================================
# Reference / adversarial completions (reward sanity checks)
# =====================================================================

def format_tool_call(name: str, arguments: Dict[str, Any]) -> str:
    return "<tool_call>\n" + json.dumps({"name": name, "arguments": arguments}, ensure_ascii=False) + "\n</tool_call>"


def gold_completion(example: Dict[str, Any], plan_style: str = "brief") -> Optional[str]:
    """Best-case completion built from the example's own expectations (None if not derivable)."""
    turn = example.get("turn_type", "decision")
    if turn == "final_answer":
        return example.get("reference_response")
    if example.get("expected_action") == "tool_call" and example.get("expected_tool"):
        args = dict(example.get("expected_arguments") or {})
        call = format_tool_call(example["expected_tool"], args)
        if plan_style == "brief":
            msgs = [{"role": "user", "content": ""},
                    {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": example["expected_tool"], "arguments": args}}]}]
            return make_plan(msgs, example.get("category")) + "\n" + call
        return call
    ref = example.get("reference_response")
    if not ref:
        return None
    if plan_style == "brief":
        plan = f"{PLAN_PREFIX} {_CATEGORY_PLANS.get(example.get('category') or '', 'answer directly from the given information.')}"
        return f"{plan}\n{ref}"
    return ref


def bad_completions(example: Dict[str, Any], other_tool: str = "calculate_earth_pressure_rankine") -> Dict[str, str]:
    """Deliberately wrong completions, each violating one GeoAI rule."""
    out: Dict[str, str] = {
        "empty": "",
        "unsafe_claim": "The foundation has plenty of capacity. This design is safe.",
        "malformed_call": "<tool_call>\n{name: broken, arguments: }\n</tool_call>",
        "hallucinated_tool": format_tool_call("compute_everything_exactly", {"x": 1.0}),
    }
    turn = example.get("turn_type", "decision")
    expected_tool = example.get("expected_tool")
    exp_args = dict(example.get("expected_arguments") or {})
    if turn == "final_answer":
        out["invented_result"] = "The calculated value is 987.65 kPa based on the supplied parameters. This design is safe."
        return out
    if example.get("expected_action") == "tool_call" and expected_tool:
        wrong = other_tool if other_tool != expected_tool else "calculate_bulk_unit_weight"
        out["wrong_tool"] = format_tool_call(wrong, exp_args)
        mutated = dict(exp_args)
        for k, v in mutated.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                mutated[k] = round(float(v) * 1.73 + 7.1, 3)
                break
        out["wrong_value"] = format_tool_call(expected_tool, mutated)
        out["text_instead_of_tool"] = "Typical values are around 30 degrees, so the answer is roughly 120 kPa."
    else:
        tool = expected_tool or other_tool
        invented = {p: 30.0 for p in (example.get("missing_params") or [])} or {"phi_eff": 30.0}
        invented.update({k: v for k, v in exp_args.items()})
        out["tool_instead_of_clarify"] = format_tool_call(tool, invented)
    return out
