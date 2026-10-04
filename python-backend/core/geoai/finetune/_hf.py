# Author: Utkarsh Gupta
# License: GPL v3
"""
Small helpers shared by sft.py / grpo.py for the (lazily imported) Hugging Face
stack. Nothing here imports torch/unsloth/trl at module import time.
"""

import hashlib
import inspect
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.geoai.finetune.config import FinetuneConfig

RUN_INFO_FILE = "geoai_run.json"
CONFIG_FILE = "geoai_finetune_config.json"


def filter_kwargs(cls: Any, kwargs: Dict[str, Any], renames: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Keep only kwargs accepted by ``cls.__init__`` (TRL/Unsloth argument names
    drift between releases). ``renames`` maps a preferred name to a fallback,
    e.g. {"max_seq_length": "max_length"}.
    """
    try:
        params = set(inspect.signature(cls.__init__).parameters)
    except (TypeError, ValueError):
        return dict(kwargs)
    if not params - {"self", "args", "kwargs"}:  # opaque (*args, **kwargs) signature: pass everything
        return dict(kwargs)
    out: Dict[str, Any] = {}
    for k, v in kwargs.items():
        if k in params:
            out[k] = v
        elif renames and k in renames and renames[k] in params:
            out[renames[k]] = v
    return out


def sha256_of(path: Path) -> Optional[str]:
    p = Path(path)
    if not p.is_file():
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def data_fingerprint(data_dir: Path, files: List[str]) -> Dict[str, Any]:
    """sha256 of manifest.json and of the data files actually used for training."""
    d = Path(data_dir)
    fp: Dict[str, Any] = {"manifest_sha256": sha256_of(d / "manifest.json"), "files": {}}
    try:
        with open(d / "manifest.json", "r", encoding="utf-8") as f:
            man = json.load(f)
        fp["generator_version"] = man.get("generator_version")
        fp["seed"] = man.get("seed")
    except (OSError, json.JSONDecodeError):
        pass
    for name in files:
        fp["files"][name] = sha256_of(d / name)
    return fp


def base_dims_from_hf_config(model: Any, cfg: FinetuneConfig) -> Dict[str, Any]:
    """
    GGUF-style fingerprint of the base model from its HF config, so the export
    sidecar can be written without a base GGUF at hand. vocab_size is omitted
    (HF config vocab may be padded differently from the GGUF token list).
    """
    c = getattr(model, "config", None)
    c = getattr(c, "text_config", None) or c
    get = lambda k: getattr(c, k, None) if c is not None else None  # noqa: E731
    fp = {"architecture": cfg.preset.llama_cpp_arch, "block_count": get("num_hidden_layers"),
          "embedding_length": get("hidden_size"), "feed_forward_length": get("intermediate_size"),
          "attention.head_count": get("num_attention_heads"), "attention.head_count_kv": get("num_key_value_heads")}
    return {k: v for k, v in fp.items() if isinstance(v, (int, str))}


def write_run_info(out_dir: Path, cfg: FinetuneConfig, info: Dict[str, Any]) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg.save_json(out_dir / CONFIG_FILE)
    with open(out_dir / RUN_INFO_FILE, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, default=str)


def read_run_info(adapter_dir: Path) -> Dict[str, Any]:
    p = Path(adapter_dir) / RUN_INFO_FILE
    if not p.is_file():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def check_template(tokenizer: Any, cfg: FinetuneConfig, example: Dict[str, Any]) -> str:
    """
    Render one prepared example with the real tokenizer template and verify
    (1) tools are rendered, (2) the loss-masking markers exist, (3) the target
    tool call is inside a trainable span. Returns the rendered text.
    """
    from core.geoai.finetune.formatting import trainable_spans

    text = tokenizer.apply_chat_template(example["messages"], tools=example["tools"] or None, tokenize=False,
                                         **cfg.chat_template_kwargs())
    tool_names = [t["function"]["name"] for t in example["tools"] or []]
    if tool_names and not any(n in text.split(cfg.preset.response_part)[0] for n in tool_names):
        raise RuntimeError(
            f"The chat template of '{cfg.base_model}' did not render the `tools` list. Family '{cfg.family}' "
            f"cannot be trained with chat_template='native'; pick a tool-capable base (any FAMILY_PRESETS entry "
            f"with template_supports_tools=True, e.g. Qwen2.5/Qwen3/Qwen3.5/Phi-3/Granite/SmolLM3/Llama3/Mistral) "
            f"or add an explicit tool format first.")
    for part in (cfg.preset.instruction_part, cfg.preset.response_part):
        if part not in text:
            raise RuntimeError(f"Loss-masking marker {part!r} not found in the rendered template; "
                               f"set the family preset correctly for '{cfg.base_model}'.")
    spans = trainable_spans(text, cfg.preset.instruction_part, cfg.preset.response_part)
    called = [tc["function"]["name"] for m in example["messages"] for tc in (m.get("tool_calls") or [])]
    if called and not any(called[0] in s for s in spans):
        raise RuntimeError("The target tool call is not inside a trainable (assistant) span.")
    return text
