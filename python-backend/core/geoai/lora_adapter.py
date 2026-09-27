# Author: Utkarsh Gupta
# License: GPL v3
"""
GGUF LoRA adapter compatibility checks for the desktop runtime.

A GeoAI fine-tune ships as a GGUF LoRA adapter (llama.cpp
``convert_lora_to_gguf.py``) plus a JSON *sidecar* written by
``core.geoai.finetune.export``::

    geoai-lora.gguf
    geoai-lora.gguf.json   <- sidecar (SIDECAR_SUFFIX appended to the adapter path)

Before llama.cpp loads an adapter, ``check_adapter_compatibility`` verifies
that it was trained for the base GGUF about to be loaded (architecture,
dimensions, vocabulary, model names). An incompatible adapter is refused and
the base model is used alone (AGENTS.md §32: the base model is the fallback).

This module has no heavy dependencies; it only reads GGUF headers and JSON.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.geoai.gguf_meta import (
    GGUFFormatError,
    base_model_fingerprint,
    compare_fingerprints,
    read_gguf_metadata,
)

logger = logging.getLogger(__name__)

SIDECAR_SUFFIX = ".json"
SIDECAR_SCHEMA = "geoai-lora-sidecar/1"


def sidecar_path(lora_path: str) -> Path:
    return Path(str(lora_path) + SIDECAR_SUFFIX)


def load_sidecar(lora_path: str) -> Optional[Dict[str, Any]]:
    """Return the adapter's sidecar dict, or None if absent/unreadable."""
    p = sidecar_path(lora_path)
    if not p.exists():
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError) as e:
        logger.warning(f"Could not read LoRA sidecar {p}: {e}")
        return None


@dataclass
class AdapterCheck:
    ok: bool
    lora_path: str
    reason: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    sidecar: Optional[Dict[str, Any]] = None
    adapter_architecture: Optional[str] = None
    base_fingerprint: Optional[Dict[str, Any]] = None

    def summary(self) -> Dict[str, Any]:
        """Compact, JSON-safe description for model_info()/UI."""
        sc = self.sidecar or {}
        return {
            "path": self.lora_path,
            "compatible": self.ok,
            "reason": self.reason,
            "warnings": list(self.warnings),
            "adapter_architecture": self.adapter_architecture,
            "base_model_id": sc.get("base_model_id"),
            "trained_chat_template": sc.get("chat_template"),
            "created_utc": sc.get("created_utc"),
            "eval": sc.get("eval"),
        }

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def check_adapter_compatibility(lora_path: str, base_model_path: str) -> AdapterCheck:
    """
    Decide whether ``lora_path`` may be applied to ``base_model_path``.

    Refuses (ok=False) when: the adapter file is missing or not a GGUF LoRA
    adapter; its architecture differs from the base; or its sidecar's recorded
    base fingerprint contradicts the base GGUF. A missing sidecar is allowed
    with a warning (only architecture can then be checked). Never raises.
    """
    chk = AdapterCheck(ok=False, lora_path=str(lora_path))
    lp = Path(lora_path)
    if not lp.is_file():
        chk.reason = f"adapter file not found: {lora_path}"
        return chk
    try:
        ameta = read_gguf_metadata(lp, keys=("general.architecture", "general.type", "adapter.type"))
    except (OSError, GGUFFormatError) as e:
        chk.reason = f"adapter is not a readable GGUF file: {e}"
        return chk
    gtype = str(ameta.get("general.type", "")).lower()
    atype = str(ameta.get("adapter.type", "")).lower()
    if gtype != "adapter" and not atype:
        chk.reason = f"'{lp.name}' is not a GGUF LoRA adapter (general.type={gtype or 'missing'})"
        return chk
    if atype and atype != "lora":
        chk.reason = f"unsupported adapter type '{atype}' (expected 'lora')"
        return chk
    chk.adapter_architecture = ameta.get("general.architecture")

    try:
        base_fp = base_model_fingerprint(base_model_path)
    except (OSError, GGUFFormatError) as e:
        chk.reason = f"cannot read base model metadata: {e}"
        return chk
    chk.base_fingerprint = base_fp

    if chk.adapter_architecture and base_fp.get("architecture") and chk.adapter_architecture != base_fp["architecture"]:
        chk.reason = (f"adapter architecture '{chk.adapter_architecture}' does not match base model "
                      f"architecture '{base_fp['architecture']}'")
        return chk

    sc = load_sidecar(str(lp))
    chk.sidecar = sc
    if sc is None:
        chk.warnings.append("no sidecar found; only the architecture could be checked")
    else:
        if sc.get("schema") != SIDECAR_SCHEMA:
            chk.warnings.append(f"unknown sidecar schema {sc.get('schema')!r}")
        expected = ((sc.get("base_gguf") or {}).get("fingerprint")) or {}
        if expected:
            mismatch = compare_fingerprints(expected, base_fp)
            if mismatch:
                chk.reason = (f"adapter was trained for base model '{sc.get('base_model_id')}' "
                              f"and does not match the loaded base GGUF ({mismatch})")
                return chk
        else:
            chk.warnings.append("sidecar has no base fingerprint; only the architecture could be checked")
        exp_name = (sc.get("base_gguf") or {}).get("filename")
        if exp_name and exp_name != Path(base_model_path).name:
            chk.warnings.append(f"base GGUF filename differs from the one used at export ({exp_name}); "
                                f"dimensions match, so a different quantisation of the same model is assumed")
    chk.ok = True
    return chk
