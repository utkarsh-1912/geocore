# Author: Utkarsh Gupta
# License: GPL v3
"""
Groundhog function manifest (startup cache for core.registry.Registry).

Scanning groundhog eagerly imports every groundhog module (and with them
scipy.optimize, matplotlib.pyplot, plotly, ...), which dominated backend
start-up time. The Registry only needs, per exposed function/class:

    name, defining module, signature (names, kinds, defaults) and docstring

so this module records exactly that in ``function_manifest.json`` and hands
the Registry lightweight ``LazyGroundhogCallable`` stand-ins. The real
groundhog object is imported on first call (thread-safe) and cached.

Cache validity is deterministic. The manifest is only used when its
fingerprint matches the running environment:

* manifest format version and Python major.minor;
* the list of groundhog modules (``pkgutil.walk_packages``);
* the installed groundhog version, when it can be determined;
* a SHA-256 of groundhog's ``.py`` sources, when they are on disk
  (not the case inside a frozen PyInstaller bundle, which is immutable).

If the manifest is missing, unreadable or stale, the original eager scan is
used and (outside frozen builds) the manifest is rewritten for the next start.

Regenerate explicitly (e.g. before a PyInstaller build) with::

    python -m core.function_manifest
"""
import hashlib
import importlib
import inspect
import json
import logging
import math
import os
import pkgutil
import sys
import threading
from typing import Any, Dict, List, Optional, Tuple

from .warmup import wait_for_warmup

logger = logging.getLogger("groundhog-backend")

MANIFEST_FORMAT = 1
MANIFEST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "function_manifest.json")


class ManifestError(Exception):
    """Raised when a manifest cannot be built or used."""


# ---------------------------------------------------------------------------
# Eager scan (the original Registry behaviour; also the fallback path)
# ---------------------------------------------------------------------------

def scan_groundhog() -> Dict[str, Any]:
    """Import every groundhog module and collect its public functions/classes."""
    import groundhog

    function_map: Dict[str, Any] = {}
    for _, name, ispkg in pkgutil.walk_packages(groundhog.__path__, groundhog.__name__ + "."):
        if ispkg:
            continue
        try:
            module = importlib.import_module(name)
            for func_name, obj in inspect.getmembers(module):
                if (inspect.isfunction(obj) or inspect.isclass(obj)) and \
                   getattr(obj, '__module__', '') == module.__name__:
                    if not func_name.startswith("_"):
                        function_map[func_name] = obj
        except Exception:
            # Some modules might fail to import due to missing optional dependencies
            pass
    return function_map


# ---------------------------------------------------------------------------
# Fingerprint
# ---------------------------------------------------------------------------

def _groundhog_version() -> Optional[str]:
    try:
        from importlib.metadata import version
        return version("groundhog")
    except Exception:
        return None


def _groundhog_source_hash() -> Optional[str]:
    """SHA-256 over groundhog's .py sources, or None if they are not on disk."""
    import groundhog

    root = os.path.dirname(os.path.abspath(getattr(groundhog, "__file__", "") or ""))
    if not os.path.isdir(root):
        return None
    digest = hashlib.sha256()
    found = False
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        for filename in sorted(filenames):
            if not filename.endswith(".py"):
                continue
            path = os.path.join(dirpath, filename)
            digest.update(os.path.relpath(path, root).replace(os.sep, "/").encode("utf-8"))
            with open(path, "rb") as f:
                digest.update(f.read())
            found = True
    return digest.hexdigest() if found else None


def _groundhog_modules() -> List[str]:
    import groundhog
    return sorted(
        name for _, name, ispkg in pkgutil.walk_packages(groundhog.__path__, groundhog.__name__ + ".")
        if not ispkg
    )


def compute_fingerprint() -> Dict[str, Any]:
    return {
        "format": MANIFEST_FORMAT,
        "python": "%d.%d" % sys.version_info[:2],
        "groundhog_modules": _groundhog_modules(),
        "groundhog_version": _groundhog_version(),
        "groundhog_source_hash": _groundhog_source_hash(),
    }


def fingerprint_matches(stored: Dict[str, Any], current: Dict[str, Any]) -> bool:
    """Strict on format/python/module list; version and source hash are compared
    whenever the running environment can determine them."""
    for key in ("format", "python", "groundhog_modules"):
        if stored.get(key) != current.get(key):
            return False
    for key in ("groundhog_version", "groundhog_source_hash"):
        if current.get(key) is not None and stored.get(key) != current.get(key):
            return False
    return True


# ---------------------------------------------------------------------------
# Default value encoding (exact round-trip, JSON only)
# ---------------------------------------------------------------------------

def _encode_value(value: Any) -> Any:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is float:
        if math.isnan(value):
            return {"$float": "nan"}
        if math.isinf(value):
            return {"$float": "inf" if value > 0 else "-inf"}
        return value
    if type(value) is list:
        return [_encode_value(v) for v in value]
    if type(value) is tuple:
        return {"$tuple": [_encode_value(v) for v in value]}
    if type(value) is dict and all(type(k) is str for k in value):
        return {"$dict": {k: _encode_value(v) for k, v in value.items()}}
    raise ManifestError(f"Unsupported default value type: {type(value).__name__}")


def _decode_value(value: Any) -> Any:
    if isinstance(value, list):
        return [_decode_value(v) for v in value]
    if isinstance(value, dict):
        if "$float" in value:
            return float(value["$float"])
        if "$tuple" in value:
            return tuple(_decode_value(v) for v in value["$tuple"])
        if "$dict" in value:
            return {k: _decode_value(v) for k, v in value["$dict"].items()}
        raise ManifestError(f"Unknown encoded value: {value!r}")
    return value


def _encode_signature(sig: inspect.Signature) -> List[Dict[str, Any]]:
    params = []
    for p in sig.parameters.values():
        entry: Dict[str, Any] = {"name": p.name, "kind": int(p.kind)}
        if p.default is not inspect.Parameter.empty:
            entry["default"] = _encode_value(p.default)
        params.append(entry)
    return params


def _decode_signature(params: List[Dict[str, Any]]) -> inspect.Signature:
    return inspect.Signature([
        inspect.Parameter(
            p["name"],
            inspect._ParameterKind(p["kind"]),
            default=_decode_value(p["default"]) if "default" in p else inspect.Parameter.empty,
        )
        for p in params
    ])


# ---------------------------------------------------------------------------
# Lazy stand-in
# ---------------------------------------------------------------------------

_resolve_lock = threading.Lock()
_resolved: Dict[Tuple[str, str], Any] = {}


def resolve_object(module_name: str, attr: str) -> Any:
    """Import ``module_name`` and return ``attr`` from it (cached, thread-safe)."""
    key = (module_name, attr)
    obj = _resolved.get(key)
    if obj is None:
        wait_for_warmup()
        with _resolve_lock:
            obj = _resolved.get(key)
            if obj is None:
                obj = getattr(importlib.import_module(module_name), attr)
                _resolved[key] = obj
    return obj


class LazyGroundhogCallable:
    """
    Stand-in for a groundhog function or class.

    Exposes the metadata the Registry and GeoAI schema factory read
    (``__name__``, ``__module__``, ``__doc__`` and ``inspect.signature``)
    without importing groundhog; the real object is imported on first call.
    """

    def __init__(self, attr: str, module: str, name: str, qualname: str,
                 doc: Optional[str], signature: inspect.Signature):
        self._attr = attr
        self.__module__ = module
        self.__name__ = name
        self.__qualname__ = qualname
        self.__doc__ = doc
        self.__signature__ = signature

    def resolve(self) -> Any:
        return resolve_object(self.__module__, self._attr)

    def __call__(self, *args, **kwargs):
        return self.resolve()(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<lazy groundhog object {self.__module__}.{self.__qualname__}>"


# ---------------------------------------------------------------------------
# Build / save / load
# ---------------------------------------------------------------------------

def build_manifest(function_map: Optional[Dict[str, Any]] = None,
                   fingerprint: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build the manifest from an eager scan (performed here if not supplied)."""
    if function_map is None:
        function_map = scan_groundhog()
    entries = []
    for attr, obj in function_map.items():
        entry: Dict[str, Any] = {
            "attr": attr,
            "module": obj.__module__,
            "name": obj.__name__,
            "qualname": getattr(obj, "__qualname__", obj.__name__),
            "doc": obj.__doc__,
        }
        try:
            entry["params"] = _encode_signature(inspect.signature(obj))
        except (ManifestError, TypeError, ValueError):
            # Cannot be represented faithfully: import this one eagerly at startup.
            entry["eager"] = True
        entries.append(entry)
    return {
        "fingerprint": fingerprint if fingerprint is not None else compute_fingerprint(),
        "functions": entries,
    }


def save_manifest(manifest: Dict[str, Any], path: str = MANIFEST_PATH) -> None:
    tmp_path = f"{path}.{os.getpid()}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    os.replace(tmp_path, path)


def function_map_from_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    function_map: Dict[str, Any] = {}
    for entry in manifest["functions"]:
        if entry.get("eager"):
            function_map[entry["attr"]] = resolve_object(entry["module"], entry["attr"])
        else:
            function_map[entry["attr"]] = LazyGroundhogCallable(
                attr=entry["attr"],
                module=entry["module"],
                name=entry["name"],
                qualname=entry["qualname"],
                doc=entry["doc"],
                signature=_decode_signature(entry["params"]),
            )
    return function_map


def load_function_map(path: str = MANIFEST_PATH, write_cache: Optional[bool] = None) -> Tuple[Dict[str, Any], str]:
    """
    Return ``(function_map, source)`` where source is ``"manifest"`` or ``"scan"``.

    Uses the manifest when its fingerprint matches; otherwise performs the
    eager scan and, when ``write_cache`` (default: not frozen), rewrites it.
    """
    if write_cache is None:
        write_cache = not getattr(sys, "frozen", False)

    fingerprint = compute_fingerprint()
    try:
        with open(path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        if fingerprint_matches(manifest.get("fingerprint", {}), fingerprint):
            return function_map_from_manifest(manifest), "manifest"
        logger.info("Groundhog function manifest is stale; performing full scan.")
    except FileNotFoundError:
        logger.info("Groundhog function manifest not found; performing full scan.")
    except Exception as e:
        logger.warning(f"Groundhog function manifest unusable ({e}); performing full scan.")

    function_map = scan_groundhog()
    if write_cache:
        try:
            save_manifest(build_manifest(function_map, fingerprint), path)
        except Exception as e:
            logger.warning(f"Could not write groundhog function manifest: {e}")
    return function_map, "scan"


_cache_lock = threading.Lock()
_cached_map: Optional[Dict[str, Any]] = None


def get_function_map() -> Dict[str, Any]:
    """Process-wide cached groundhog function map (a fresh dict per call)."""
    global _cached_map
    with _cache_lock:
        if _cached_map is None:
            _cached_map, _ = load_function_map()
        return dict(_cached_map)


def warm_imports(modules: Optional[List[str]] = None) -> None:
    """Import groundhog modules (default: all in the manifest) to pre-pay first-call cost."""
    if modules is None:
        with _cache_lock:
            source = _cached_map or {}
        modules = sorted({getattr(obj, "__module__", "") for obj in source.values()})
    for name in modules:
        if not name:
            continue
        try:
            importlib.import_module(name)
        except Exception:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    manifest = build_manifest()
    save_manifest(manifest)
    print(f"Wrote {len(manifest['functions'])} entries to {MANIFEST_PATH}")
