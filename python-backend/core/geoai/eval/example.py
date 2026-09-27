# Author: Utkarsh Gupta
# License: GPL v3
"""
GeoAI evaluation example schema.

A single ``EvalExample`` describes one model *turn* to be judged:

* ``turn_type == "decision"``: the model sees the system prompt + ``messages``
  (normally one user message) and must decide what to do (call a tool, ask for
  clarification, reject invalid input, or answer directly).
* ``turn_type == "final_answer"``: ``messages`` already contains the tool call
  and the tool result produced by the real registry; the model must write the
  grounded final answer.

The same record is used by the dataset generator (``core.geoai.training``),
the deterministic scorer (``core.geoai.eval.scoring``) and the runner.  It is
plain JSON-serialisable data so it can be stored in JSONL and passed to an RL
reward function unchanged.
"""

import json
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

ACTIONS = ("tool_call", "clarify", "reject", "synthesize")

CATEGORIES = (
    "correct_request",
    "ambiguous_request",
    "missing_data",
    "wrong_units",
    "conflicting_data",
    "research",
    "tool_failure",
)


@dataclass
class EvalExample:
    id: str
    category: str
    expected_action: str
    messages: List[Dict[str, Any]]
    turn_type: str = "decision"
    context: Optional[Dict[str, Any]] = None
    # Other actions that are also acceptable (full action credit).
    acceptable_actions: List[str] = field(default_factory=list)
    # Tool expectations (canonical parameter names, canonical units).
    expected_tool: Optional[str] = None
    acceptable_tools: List[str] = field(default_factory=list)
    expected_arguments: Optional[Dict[str, Any]] = None
    # Canonical parameter names whose values are stated in the prompt/context.
    # ``None`` means "unknown" and the scorer falls back to numeric grounding.
    provided_params: Optional[List[str]] = None
    # Required parameters deliberately absent (expected clarification).
    missing_params: List[str] = field(default_factory=list)
    # {"param": str, "kind": "convertible"|"dimension_mismatch", "given": str}
    unit_trap: Optional[Dict[str, Any]] = None
    # Each group is a list of synonyms; a group is satisfied if any synonym
    # appears (case-insensitive) in the model's text.
    clarify_keywords: List[List[str]] = field(default_factory=list)
    required_mentions: List[List[str]] = field(default_factory=list)
    forbidden_patterns: List[str] = field(default_factory=list)
    # Numeric Groundhog outputs of the expected tool call (end-to-end check),
    # and output values that a grounded final answer must quote.
    expected_result: Optional[Dict[str, Any]] = None
    expected_result_values: Optional[Dict[str, float]] = None
    reference_response: Optional[str] = None
    # Bookkeeping
    split: Optional[str] = None
    source: str = "generated"
    group: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    @property
    def user_prompt(self) -> str:
        for m in reversed(self.messages):
            if m.get("role") == "user":
                return m.get("content") or ""
        return ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvalExample":
        known = {f.name for f in fields(cls)}
        payload = {k: v for k, v in data.items() if k in known}
        if "messages" not in payload:
            prompt = data.get("user_prompt") or ""
            payload["messages"] = [{"role": "user", "content": prompt}]
        return cls(**payload)


ExampleLike = Union[EvalExample, Dict[str, Any]]


def as_example(example: ExampleLike) -> EvalExample:
    if isinstance(example, EvalExample):
        return example
    if isinstance(example, dict):
        return EvalExample.from_dict(example)
    raise TypeError(f"Unsupported example type: {type(example)!r}")


def save_examples_jsonl(examples: Iterable[EvalExample], path: Path) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(path, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
            n += 1
    return n


def load_examples_jsonl(path: Path) -> List[EvalExample]:
    out: List[EvalExample] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(EvalExample.from_dict(json.loads(line)))
    return out
