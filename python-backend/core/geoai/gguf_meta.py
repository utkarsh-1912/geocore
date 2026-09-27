# Author: Utkarsh Gupta
# License: GPL v3
"""
Minimal, dependency-free GGUF header reader.

Reads only the key/value metadata section of a GGUF file (never tensor data),
so it is cheap enough to call before loading a model. Used to:

* tell LoRA adapter GGUFs apart from full model GGUFs (``general.type``);
* fingerprint a base model (architecture + dimensions + names) so a LoRA
  adapter trained for a different base can be refused before llama.cpp
  loads it.

Format reference: https://github.com/ggml-org/ggml/blob/master/docs/gguf.md
"""

import hashlib
import re
import struct
from pathlib import Path
from typing import Any, BinaryIO, Dict, Iterable, Optional, Union

GGUF_MAGIC = b"GGUF"

# value type ids -> struct format (scalars)
_SCALAR = {
    0: "<B", 1: "<b", 2: "<H", 3: "<h", 4: "<I", 5: "<i",
    6: "<f", 7: "<?", 10: "<Q", 11: "<q", 12: "<d",
}
_STRING, _ARRAY = 8, 9


class GGUFFormatError(ValueError):
    """The file is not a readable GGUF file."""


class _ArrayInfo(dict):
    """Placeholder for a skipped array value: {'type': 'array', 'elem_type': int, 'len': int}."""


def _read_exact(f: BinaryIO, n: int) -> bytes:
    b = f.read(n)
    if len(b) != n:
        raise GGUFFormatError("unexpected end of file while reading GGUF header")
    return b


def _read_u32(f: BinaryIO) -> int:
    return struct.unpack("<I", _read_exact(f, 4))[0]


def _read_u64(f: BinaryIO) -> int:
    return struct.unpack("<Q", _read_exact(f, 8))[0]


def _read_str(f: BinaryIO, max_len: int = 1 << 26) -> str:
    n = _read_u64(f)
    if n > max_len:
        raise GGUFFormatError(f"implausible GGUF string length {n}")
    return _read_exact(f, n).decode("utf-8", errors="replace")


def _skip_str(f: BinaryIO) -> None:
    n = _read_u64(f)
    f.seek(n, 1)


def _read_value(f: BinaryIO, vtype: int, keep_arrays: bool) -> Any:
    if vtype in _SCALAR:
        fmt = _SCALAR[vtype]
        return struct.unpack(fmt, _read_exact(f, struct.calcsize(fmt)))[0]
    if vtype == _STRING:
        return _read_str(f)
    if vtype == _ARRAY:
        etype = _read_u32(f)
        count = _read_u64(f)
        if keep_arrays:
            return [_read_value(f, etype, keep_arrays) for _ in range(count)]
        if etype in _SCALAR:
            f.seek(struct.calcsize(_SCALAR[etype]) * count, 1)
        elif etype == _STRING:
            for _ in range(count):
                _skip_str(f)
        else:
            for _ in range(count):
                _read_value(f, etype, False)
        return _ArrayInfo(type="array", elem_type=etype, len=count)
    raise GGUFFormatError(f"unknown GGUF value type {vtype}")


def read_gguf_metadata(
    path: Union[str, Path],
    keys: Optional[Iterable[str]] = None,
    keep_arrays: bool = False,
) -> Dict[str, Any]:
    """
    Read GGUF key/value metadata.

    Args:
        path: GGUF file.
        keys: if given, stop as soon as all of these keys have been read
            (cheap for ``general.*`` keys, which come first).
        keep_arrays: materialise array values (e.g. vocabularies). By default
            arrays are skipped and reported as ``{'type': 'array', 'len': n}``.

    Returns:
        dict of metadata plus ``'__gguf_version__'`` and ``'__tensor_count__'``.

    Raises:
        GGUFFormatError: not a GGUF file / truncated header.
    """
    wanted = set(keys) if keys is not None else None
    out: Dict[str, Any] = {}
    with open(path, "rb") as f:
        if f.read(4) != GGUF_MAGIC:
            raise GGUFFormatError(f"{path} is not a GGUF file")
        version = _read_u32(f)
        if version == 1:
            tensor_count, kv_count = _read_u32(f), _read_u32(f)
        elif version in (2, 3):
            tensor_count, kv_count = _read_u64(f), _read_u64(f)
        else:
            raise GGUFFormatError(f"unsupported GGUF version {version}")
        out["__gguf_version__"] = version
        out["__tensor_count__"] = tensor_count
        for _ in range(kv_count):
            key = _read_str(f, max_len=1 << 16)
            vtype = _read_u32(f)
            out[key] = _read_value(f, vtype, keep_arrays)
            if wanted is not None and wanted.issubset(out):
                break
    return out


def is_lora_adapter(path: Union[str, Path]) -> bool:
    """True if ``path`` is a GGUF LoRA adapter (``general.type == 'adapter'``). Never raises."""
    try:
        meta = read_gguf_metadata(path, keys=("general.type", "general.architecture"))
    except (OSError, GGUFFormatError):
        return False
    return str(meta.get("general.type", "")).lower() == "adapter" or "adapter.type" in meta


# Dimension keys that must match for a LoRA adapter to be meaningful.
_DIM_KEYS = ("block_count", "embedding_length", "feed_forward_length",
             "attention.head_count", "attention.head_count_kv")
_NAME_KEYS = ("general.basename", "general.size_label", "general.finetune")


def base_model_fingerprint(path: Union[str, Path]) -> Dict[str, Any]:
    """
    Quantisation-independent identity of a base model GGUF: architecture,
    transformer dimensions, vocabulary size and model names. Two GGUFs of the
    same model at different quantisations (q4_k_m, q8_0, f16) share it.
    """
    meta = read_gguf_metadata(path)
    arch = meta.get("general.architecture")
    fp: Dict[str, Any] = {"architecture": arch}
    for k in _DIM_KEYS:
        v = meta.get(f"{arch}.{k}")
        if isinstance(v, (int, float)):
            fp[k] = v
    toks = meta.get("tokenizer.ggml.tokens")
    if isinstance(toks, dict) and "len" in toks:
        fp["vocab_size"] = toks["len"]
    for k in _NAME_KEYS:
        v = meta.get(k)
        if isinstance(v, str) and v.strip():
            fp[k.split(".", 1)[1]] = v
    return fp


def _norm_name(s: Any) -> str:
    return re.sub(r"[^a-z0-9.]", "", str(s).lower())


def compare_fingerprints(expected: Dict[str, Any], actual: Dict[str, Any]) -> Optional[str]:
    """
    Return None if ``actual`` (the base GGUF about to be loaded) is compatible
    with ``expected`` (recorded when the adapter was exported), else a reason.
    Only keys present in both are compared. Names are compared loosely
    (case/punctuation-insensitive, containment allowed) because different
    GGUF converters spell them differently; ``size_label`` is informational
    only (converters disagree, e.g. '1.8B' vs '1.5B' for Qwen2.5-1.5B).
    """
    for k in ("architecture", "vocab_size") + _DIM_KEYS:
        if k in expected and k in actual and expected[k] != actual[k]:
            return f"{k}: adapter expects {expected[k]!r}, base model has {actual[k]!r}"
    for k in ("basename", "finetune"):
        if k in expected and k in actual:
            a, b = _norm_name(expected[k]), _norm_name(actual[k])
            if a and b and a != b and a not in b and b not in a:
                return f"{k}: adapter expects {expected[k]!r}, base model has {actual[k]!r}"
    return None


def sha256_file(path: Union[str, Path], chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()
