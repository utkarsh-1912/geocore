"""
Tiny pure-Python GGUF writer for tests (header + metadata + optional F32 tensors).

Used to fabricate base-model headers and LoRA adapter files without
downloading anything. Not a general GGUF writer.
"""
import struct
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_ALIGN = 32


def _s(x: str) -> bytes:
    b = x.encode("utf-8")
    return struct.pack("<Q", len(b)) + b


def _kv(key: str, value: Any) -> bytes:
    out = _s(key)
    if isinstance(value, bool):
        return out + struct.pack("<I", 7) + struct.pack("<?", value)
    if isinstance(value, int):
        return out + struct.pack("<I", 4) + struct.pack("<I", value)
    if isinstance(value, float):
        return out + struct.pack("<I", 6) + struct.pack("<f", value)
    if isinstance(value, str):
        return out + struct.pack("<I", 8) + _s(value)
    if isinstance(value, list):  # list of str
        body = b"".join(_s(v) for v in value)
        return out + struct.pack("<I", 9) + struct.pack("<I", 8) + struct.pack("<Q", len(value)) + body
    raise TypeError(type(value))


def write_gguf(path: Path, metadata: Dict[str, Any],
               tensors: Optional[Sequence[Tuple[str, Sequence[int]]]] = None) -> Path:
    """Write a GGUF v3 file; tensors are zero-filled F32 with ggml dims ``ne``."""
    tensors = list(tensors or [])
    header = b"GGUF" + struct.pack("<I", 3) + struct.pack("<Q", len(tensors)) + struct.pack("<Q", len(metadata))
    kvs = b"".join(_kv(k, v) for k, v in metadata.items())
    infos: List[bytes] = []
    offset = 0
    sizes = []
    for name, ne in tensors:
        n = 1
        for d in ne:
            n *= d
        size = n * 4
        infos.append(_s(name) + struct.pack("<I", len(ne)) + b"".join(struct.pack("<Q", d) for d in ne)
                     + struct.pack("<I", 0) + struct.pack("<Q", offset))
        sizes.append(size)
        offset += (size + _ALIGN - 1) // _ALIGN * _ALIGN
    blob = header + kvs + b"".join(infos)
    blob += b"\x00" * ((-len(blob)) % _ALIGN)
    for size in sizes:
        blob += b"\x00" * size + b"\x00" * ((-size) % _ALIGN)
    Path(path).write_bytes(blob)
    return Path(path)


QWEN2_1P5B_META = {
    "general.architecture": "qwen2",
    "general.type": "model",
    "general.name": "qwen2.5-1.5b-instruct",
    "general.finetune": "qwen2.5-1.5b-instruct",
    "general.size_label": "1.8B",
    "qwen2.block_count": 28,
    "qwen2.embedding_length": 1536,
    "qwen2.feed_forward_length": 8960,
    "qwen2.attention.head_count": 12,
    "qwen2.attention.head_count_kv": 2,
    "tokenizer.ggml.tokens": ["a", "b", "c"],
}


def write_fake_base(path: Path, **overrides: Any) -> Path:
    meta = dict(QWEN2_1P5B_META)
    meta.update(overrides)
    return write_gguf(path, meta)


def write_fake_lora(path: Path, arch: str = "qwen2", n_embd: int = 1536, rank: int = 1,
                    layers: Sequence[int] = (0,)) -> Path:
    """A zero LoRA on attn_q of the given layers (no-op when applied)."""
    meta = {"general.architecture": arch, "general.type": "adapter", "adapter.type": "lora",
            "adapter.lora.alpha": float(rank)}
    tensors = []
    for i in layers:
        tensors.append((f"blk.{i}.attn_q.weight.lora_a", (n_embd, rank)))
        tensors.append((f"blk.{i}.attn_q.weight.lora_b", (rank, n_embd)))
    return write_gguf(path, meta, tensors)
