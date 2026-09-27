# Author: Utkarsh Gupta
# License: GPL v3
"""
Fine-tuning configuration (pure Python, no heavy imports).

The base model is configurable and never hard-coded elsewhere (AGENTS.md §4):
``FinetuneConfig.base_model`` is what Unsloth loads, ``base_model_id`` is the
Hugging Face reference id matching the base GGUF the desktop app runs (used by
``convert_lora_to_gguf.py`` and recorded in the adapter sidecar), and
``family`` selects a preset (quantisation default, chat-turn markers, thinking
switch, llama.cpp architecture).

Defaults target a free 16 GB T4 (fp16, no bf16) with a 1.5B-4B model.
"""

import argparse
import json
from dataclasses import asdict, dataclass, field, fields, replace
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "training" / "data"
HELD_OUT_SPLITS = frozenset({"test", "gold"})  # never trained on (AGENTS.md §21)


@dataclass(frozen=True)
class FamilyPreset:
    """Per-family defaults. ``instruction_part``/``response_part`` drive assistant-only loss masking."""
    load_in_4bit: bool
    instruction_part: str
    response_part: str
    llama_cpp_arch: str
    template_supports_tools: bool
    thinking_kwarg: Optional[str] = None  # chat-template kwarg that toggles thinking (Qwen3: enable_thinking)
    notes: str = ""


_CHATML = ("<|im_start|>user\n", "<|im_start|>assistant\n")

FAMILY_PRESETS: Dict[str, FamilyPreset] = {
    "qwen2.5": FamilyPreset(True, *_CHATML, llama_cpp_arch="qwen2", template_supports_tools=True,
                            notes="Current desktop baseline (Qwen2.5-1.5B-Instruct q4_k_m). QLoRA is fine."),
    "qwen3": FamilyPreset(True, *_CHATML, llama_cpp_arch="qwen3", template_supports_tools=True,
                          thinking_kwarg="enable_thinking",
                          notes="Hybrid thinking model: keep enable_thinking=False for CPU latency."),
    "qwen3.5": FamilyPreset(False, *_CHATML, llama_cpp_arch="qwen35", template_supports_tools=True,
                            thinking_kwarg="enable_thinking",
                            notes="Unsloth recommends 16-bit LoRA (not QLoRA) for Qwen3.5. Chat markers assumed "
                                  "ChatML - sft.py verifies them against the real tokenizer before training."),
    "gemma3": FamilyPreset(True, "<start_of_turn>user\n", "<start_of_turn>model\n", llama_cpp_arch="gemma3",
                           template_supports_tools=False,
                           notes="Gemma 3's chat template has no tool-calling section; sft.py refuses "
                                 "chat_template='native' unless the tokenizer template renders tools."),
}

SFT_DEFAULTS = dict(learning_rate=2e-4, num_train_epochs=2.0, per_device_train_batch_size=2,
                    gradient_accumulation_steps=8)


@dataclass
class FinetuneConfig:
    # ---- model -----------------------------------------------------------
    base_model: str = "unsloth/Qwen2.5-1.5B-Instruct"
    base_model_id: str = "Qwen/Qwen2.5-1.5B-Instruct"
    family: str = "qwen2.5"
    load_in_4bit: Optional[bool] = None  # None -> family preset (QLoRA vs 16-bit LoRA)
    max_seq_length: int = 4096  # = desktop n_ctx default; longer examples cannot be served anyway
    # ---- LoRA ------------------------------------------------------------
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.0  # 0 is Unsloth's fast path
    target_modules: Tuple[str, ...] = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")
    use_rslora: bool = False
    # ---- data / formatting ----------------------------------------------
    data_dir: str = str(DEFAULT_DATA_DIR)
    chat_template: str = "native"  # render with the tokenizer's own template incl. `tools`
    plan_style: str = "brief"  # "brief": one-line "Plan: ..." before decisions; "none": data as generated
    enable_thinking: bool = False  # only used by families with a thinking switch (Qwen3/3.5)
    drop_overlong: bool = True  # drop (not truncate) examples longer than max_seq_length
    # Cap tool schemas per example (the called tool is always kept). Measured on sft_val:
    # all tools -> 47% of examples exceed 4096 tokens; 5 -> 6%; 3 -> 0%. None = as generated.
    max_tools: Optional[int] = 5
    max_train_examples: Optional[int] = None  # debugging subset
    # ---- SFT -------------------------------------------------------------
    learning_rate: float = SFT_DEFAULTS["learning_rate"]
    num_train_epochs: float = SFT_DEFAULTS["num_train_epochs"]
    per_device_train_batch_size: int = SFT_DEFAULTS["per_device_train_batch_size"]
    gradient_accumulation_steps: int = SFT_DEFAULTS["gradient_accumulation_steps"]
    warmup_ratio: float = 0.05
    weight_decay: float = 0.01
    lr_scheduler_type: str = "cosine"
    optim: str = "adamw_8bit"
    logging_steps: int = 10
    eval_steps: int = 50
    # ---- GRPO ------------------------------------------------------------
    grpo_learning_rate: float = 5e-6
    grpo_max_steps: int = 300
    grpo_num_generations: int = 4
    grpo_per_device_batch_size: int = 4  # must be a multiple of grpo_num_generations
    grpo_gradient_accumulation_steps: int = 2
    grpo_max_prompt_length: int = 3584  # + completion 256 = 3840 <= max_seq_length (5 tool schemas can reach ~4k tokens)
    grpo_max_completion_length: int = 256  # plan + tool call / clarification: short on purpose
    grpo_temperature: float = 0.9
    grpo_beta: float = 0.04  # KL to the SFT policy
    grpo_format_reward_weight: float = 0.1  # relative to the scorer reward (weight 1.0)
    grpo_splits: Tuple[str, ...] = ("train",)
    grpo_turn_types: Tuple[str, ...] = ("decision", "final_answer")
    grpo_use_vllm: bool = False  # Unsloth fast_inference (vLLM); faster rollouts, more VRAM, optional
    grpo_gpu_memory_utilization: float = 0.6
    # ---- misc ------------------------------------------------------------
    seed: int = 20260926
    output_dir: str = "outputs/geoai-ft"
    report_to: str = "none"

    # ------------------------------------------------------------------
    @property
    def preset(self) -> FamilyPreset:
        if self.family not in FAMILY_PRESETS:
            raise ValueError(f"Unknown family '{self.family}'. Known: {sorted(FAMILY_PRESETS)}")
        return FAMILY_PRESETS[self.family]

    @property
    def resolved_load_in_4bit(self) -> bool:
        return self.preset.load_in_4bit if self.load_in_4bit is None else bool(self.load_in_4bit)

    @property
    def sft_dir(self) -> Path:
        return Path(self.output_dir) / "sft_adapter"

    @property
    def grpo_dir(self) -> Path:
        return Path(self.output_dir) / "grpo_adapter"

    @property
    def export_dir(self) -> Path:
        return Path(self.output_dir) / "export"

    def chat_template_kwargs(self) -> Dict[str, Any]:
        """Extra kwargs for tokenizer.apply_chat_template (explicit thinking toggle)."""
        kw = self.preset.thinking_kwarg
        return {kw: bool(self.enable_thinking)} if kw else {}

    def validate(self) -> "FinetuneConfig":
        _ = self.preset
        if self.chat_template != "native":
            raise ValueError("chat_template must be 'native' (the tokenizer's own template with tools)")
        if self.plan_style not in ("brief", "none"):
            raise ValueError("plan_style must be 'brief' or 'none'")
        bad = set(self.grpo_splits) & HELD_OUT_SPLITS
        if bad:
            raise ValueError(f"grpo_splits must not include held-out splits {sorted(bad)}")
        if self.grpo_per_device_batch_size % self.grpo_num_generations:
            raise ValueError("grpo_per_device_batch_size must be a multiple of grpo_num_generations")
        if self.grpo_max_prompt_length + self.grpo_max_completion_length > self.max_seq_length:
            raise ValueError("grpo_max_prompt_length + grpo_max_completion_length exceeds max_seq_length")
        if not (0 <= self.lora_dropout < 1) or self.lora_r <= 0:
            raise ValueError("invalid LoRA hyper-parameters")
        return self

    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["target_modules"] = list(self.target_modules)
        d["grpo_splits"] = list(self.grpo_splits)
        d["grpo_turn_types"] = list(self.grpo_turn_types)
        d["resolved_load_in_4bit"] = self.resolved_load_in_4bit
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FinetuneConfig":
        known = {f.name: f for f in fields(cls)}
        kw = {}
        for k, v in data.items():
            if k in known:
                kw[k] = tuple(v) if isinstance(v, list) else v
        return cls(**kw)

    def save_json(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_json(cls, path: Path) -> "FinetuneConfig":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def with_overrides(self, overrides: Dict[str, Any]) -> "FinetuneConfig":
        known = {f.name: f for f in fields(self)}
        kw = {}
        for k, raw in overrides.items():
            if k not in known:
                raise ValueError(f"Unknown config key '{k}'")
            kw[k] = _coerce(raw, getattr(self, k))
        return replace(self, **kw)


def _coerce(raw: Any, current: Any) -> Any:
    if not isinstance(raw, str):
        return raw
    s = raw.strip()
    if s.lower() in ("none", "null"):
        return None
    if isinstance(current, bool) or s.lower() in ("true", "false"):
        return s.lower() in ("1", "true", "yes", "on")
    if isinstance(current, tuple):
        return tuple(x.strip() for x in s.split(",") if x.strip())
    if isinstance(current, int) and not isinstance(current, bool):
        return int(s)
    if isinstance(current, float):
        return float(s)
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return s


# ----------------------------------------------------------------------
# Shared CLI helpers (sft.py / grpo.py / export.py)
# ----------------------------------------------------------------------

def add_config_args(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--config", type=Path, help="FinetuneConfig JSON (e.g. written by a previous run)")
    ap.add_argument("--base-model", help="Model Unsloth loads (HF id or local dir)")
    ap.add_argument("--base-model-id", help="HF reference id matching the desktop base GGUF")
    ap.add_argument("--family", choices=sorted(FAMILY_PRESETS))
    ap.add_argument("--output-dir")
    ap.add_argument("--data-dir")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="Override any FinetuneConfig field, e.g. --set lora_r=32 --set load_in_4bit=false")


def config_from_args(args: argparse.Namespace) -> FinetuneConfig:
    cfg = FinetuneConfig.load_json(args.config) if getattr(args, "config", None) else FinetuneConfig()
    ov: Dict[str, Any] = {}
    for attr, key in (("base_model", "base_model"), ("base_model_id", "base_model_id"), ("family", "family"),
                      ("output_dir", "output_dir"), ("data_dir", "data_dir")):
        v = getattr(args, attr, None)
        if v:
            ov[key] = v
    for item in getattr(args, "set", []) or []:
        if "=" not in item:
            raise ValueError(f"--set expects KEY=VALUE, got '{item}'")
        k, v = item.split("=", 1)
        ov[k.strip()] = v
    return cfg.with_overrides(ov).validate() if ov else cfg.validate()
