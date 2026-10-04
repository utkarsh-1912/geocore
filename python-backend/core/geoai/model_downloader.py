# Author: Utkarsh Gupta
# License: GPL v3
"""
Local GGUF Model Downloader & Manager.
Downloads candidate SLM models (Qwen 2.5/3, Granite, Mistral, and more) from Hugging Face directly
to the local GeoCore models directory and configures GeoAI for local inference.
"""

import os
import sys
import time
import logging
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional

import requests

from core.geoai.model_config import (
    get_default_model_dir,
    load_config,
    save_config,
    find_gguf_models,
    GeoAIModelConfig
)
from core.geoai.gguf_meta import sha256_file

logger = logging.getLogger(__name__)

# Curated Candidate SLM Registry for Desktop Offline Geotechnical AI.
# Optional per-entry keys: "size_bytes" and "sha256" (the Hub LFS oid) are
# verified after download when present.
# Benchmark winner (cpu-test40, 2026-09-28): best tool choice / argument accuracy at ~2.4 GB RAM.
DEFAULT_MODEL_ID = "qwen3-1.7b"

RECOMMENDED_MODELS: Dict[str, Dict[str, Any]] = {
    "qwen2.5-1.5b-instruct": {
        "family": "qwen",
        "license": "Apache-2.0",
        "display_name": "Qwen 2.5 (1.5B Instruct)",
        "repo_id": "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
        "filename": "qwen2.5-1.5b-instruct-q4_k_m.gguf",
        "size_mb": 1066,
        "size_bytes": 1117320736,
        "sha256": "6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e",
        "description": "Ultra-lightweight (1.5B), rapid CPU inference, high-precision function calling",
        "recommended_for": "Laptops & standard workstations for high-speed Groundhog calculation execution"
    },
    "qwen3.5-2b": {
        "family": "qwen",
        "license": "Apache-2.0",
        "display_name": "Qwen 3.5 (2B)",
        "repo_id": "unsloth/Qwen3.5-2B-GGUF",
        "filename": "Qwen3.5-2B-Q4_K_M.gguf",
        "size_mb": 1222,
        "size_bytes": 1280835840,
        "sha256": "aaf42c8b7c3cab2bf3d69c355048d4a0ee9973d48f16c731c0520ee914699223",
        "description": "Qwen 3.5 small (2B, 262k context) with native tool-calling chat template; benchmark candidate",
        "recommended_for": "Laptops & workstations; candidate replacement for Qwen 2.5 1.5B"
    },
    "qwen3-1.7b": {
        "family": "qwen",
        "license": "Apache-2.0",
        "display_name": "Qwen 3 (1.7B)",
        "repo_id": "unsloth/Qwen3-1.7B-GGUF",
        "filename": "Qwen3-1.7B-Q4_K_M.gguf",
        "size_mb": 1056,
        "size_bytes": 1107409472,
        "sha256": "b139949c5bd74937ad8ed8c8cf3d9ffb1e99c866c823204dc42c0d91fa181897",
        "description": "Qwen 3 (1.7B, 40k context) hybrid thinking model with native tool calling; benchmark candidate",
        "recommended_for": "Laptops & standard workstations; candidate replacement for Qwen 2.5 1.5B"
    },
    "qwen2.5-3b-instruct": {
        "family": "qwen",
        "license": "Qwen Research (non-commercial)",
        "display_name": "Qwen 2.5 (3B Instruct)",
        "repo_id": "Qwen/Qwen2.5-3B-Instruct-GGUF",
        "filename": "qwen2.5-3b-instruct-q4_k_m.gguf",
        "size_mb": 2040,
        "description": "Balanced (3B) with superior multi-turn geotechnical reasoning and complex parameter extraction",
        "recommended_for": "Engineering workstations requiring balanced speed and deep tool precision"
    },
    "qwen2.5-7b-instruct": {
        "family": "qwen",
        "license": "Apache-2.0",
        "display_name": "Qwen 2.5 (7B Instruct)",
        # The official Qwen repo splits Q4_K_M into 2 shards; this is a verified single file.
        "repo_id": "bartowski/Qwen2.5-7B-Instruct-GGUF",
        "filename": "Qwen2.5-7B-Instruct-Q4_K_M.gguf",
        "size_mb": 4466,
        "size_bytes": 4683074240,
        "sha256": "65b8fcd92af6b4fefa935c625d1ac27ea29dcb6ee14589c55a8f115ceaaa1423",
        "description": "Maximum capability (7B) for complex geotechnical synthesis, CPT profiling & tool orchestration",
        "recommended_for": "High-end workstations with dedicated GPU/VRAM acceleration"
    },
    "qwen3-4b-instruct-2507": {
        "family": "qwen",
        "license": "Apache-2.0",
        "display_name": "Qwen 3 (4B Instruct 2507)",
        "repo_id": "unsloth/Qwen3-4B-Instruct-2507-GGUF",
        "filename": "Qwen3-4B-Instruct-2507-Q4_K_M.gguf",
        "size_mb": 2382,
        "size_bytes": 2497281120,
        "sha256": "3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597",
        "description": "Qwen 3 (4B) non-thinking instruct release with native tool calling; benchmark candidate",
        "recommended_for": "Workstations with 8 GB+ RAM wanting stronger argument extraction than the 1.5-2B models"
    },
    "qwen3-8b": {
        "family": "qwen",
        "license": "Apache-2.0",
        "display_name": "Qwen 3 (8B)",
        "repo_id": "Qwen/Qwen3-8B-GGUF",
        "filename": "Qwen3-8B-Q4_K_M.gguf",
        "size_mb": 4795,
        "size_bytes": 5027783488,
        "sha256": "d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785",
        "description": "Qwen 3 (8B) hybrid thinking model with native tool calling; quality reference, slow on CPU",
        "recommended_for": "High-end workstations with 16 GB+ RAM or a GPU"
    },
    "phi-4-mini-instruct": {
        "family": "phi",
        "license": "MIT",
        "display_name": "Phi-4-mini (3.8B Instruct)",
        "repo_id": "unsloth/Phi-4-mini-instruct-GGUF",
        "filename": "Phi-4-mini-instruct-Q4_K_M.gguf",
        "size_mb": 2376,
        "size_bytes": 2491874272,
        "sha256": "88c00229914083cd112853aab84ed51b87bdf6b9ce42f532d8c85c7c63b1730a",
        "description": "Microsoft Phi-4-mini (3.8B), trained for function calling; MIT licence; benchmark candidate",
        "recommended_for": "Workstations with 8 GB+ RAM; permissive licence for redistribution"
    },
    "granite-4.1-3b": {
        "family": "granite",
        "license": "Apache-2.0",
        "display_name": "Granite 4.1 (3B)",
        "repo_id": "ibm-granite/granite-4.1-3b-GGUF",
        "filename": "granite-4.1-3b-Q4_K_M.gguf",
        "size_mb": 2002,
        "size_bytes": 2099501664,
        "sha256": "662b0626cd58f443baea23559b469df6576a81d349649c59413b36a9fb32eb29",
        "description": "IBM Granite 4.1 (3B) with native tool calling and an improved post-training pipeline "
                       "(enhanced tool calling over 4.0 Micro); benchmark candidate",
        "recommended_for": "Laptops & workstations with 8 GB RAM"
    },
    "smollm3-3b": {
        "family": "smollm",
        "license": "Apache-2.0",
        "display_name": "SmolLM3 (3B)",
        "repo_id": "ggml-org/SmolLM3-3B-GGUF",
        "filename": "SmolLM3-Q4_K_M.gguf",
        "size_mb": 1827,
        "size_bytes": 1915305312,
        "sha256": "8334b850b7bd46238c16b0c550df2138f0889bf433809008cc17a8b05761863e",
        "description": "Hugging Face SmolLM3 (3B) hybrid thinking model with tool calling; fully open training data",
        "recommended_for": "Laptops & workstations with 8 GB RAM"
    },
    "llama-3.2-3b-instruct": {
        "family": "llama",
        "license": "Llama 3.2 Community",
        "display_name": "Llama 3.2 (3B Instruct)",
        "repo_id": "bartowski/Llama-3.2-3B-Instruct-GGUF",
        "filename": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "size_mb": 1926,
        "size_bytes": 2019377696,
        "sha256": "6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff",
        "description": "Meta Llama 3.2 (3B) with JSON tool calls; custom licence with use restrictions",
        "recommended_for": "Laptops & workstations with 8 GB RAM"
    },
    "mistral-7b-instruct-v0.3": {
        "family": "mistral",
        "license": "Apache-2.0",
        "display_name": "Mistral 7B Instruct (v0.3)",
        "repo_id": "bartowski/Mistral-7B-Instruct-v0.3-GGUF",
        "filename": "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
        "size_mb": 4170,
        "size_bytes": 4372812000,
        "description": "Mistral 7B Instruct v0.3 with native [TOOL_CALLS] function calling; strong literature & standards synthesis",
        "recommended_for": "Research workstations with 8 GB+ RAM; tool-calling replacement for the old Gemma 2 research tier"
    }
}


def get_active_model_path() -> Optional[str]:
    """The GGUF GeoAI will load (config.model_path), or None when no model is configured or it is missing."""
    config = load_config()
    if config.provider == "heuristic" or not config.model_path:
        return None
    return config.model_path if Path(config.model_path).is_file() else None


def list_available_models() -> List[Dict[str, Any]]:
    """Returns list of curated candidate models, their local download status and which one is active."""
    installed = {p.name.lower(): p for p in find_gguf_models()}
    active_path = get_active_model_path()
    # Matched by file name so a registry model linked from another folder is still recognised.
    active_name = Path(active_path).name.lower() if active_path else None
    results = []

    for key, info in RECOMMENDED_MODELS.items():
        is_installed = info["filename"].lower() in installed
        local_path = str(installed[info["filename"].lower()]) if is_installed else None
        is_active = active_name == info["filename"].lower()
        if is_active:
            is_installed, local_path = True, active_path
        results.append({
            "id": key,
            "family": info.get("family", "qwen"),
            "license": info.get("license"),
            "display_name": info.get("display_name", key),
            "repo_id": info["repo_id"],
            "filename": info["filename"],
            "size_mb": info["size_mb"],
            "sha256": info.get("sha256"),
            "description": info["description"],
            "recommended_for": info["recommended_for"],
            "is_installed": is_installed,
            "is_active": is_active,
            "local_path": local_path
        })
    return results


_download_state: Dict[str, Any] = {
    "status": "idle",  # "idle", "downloading", "completed", "error"
    "model_id": None,
    "display_name": None,
    "size_mb": None,
    "error": None,
    # Live progress (bytes / seconds). None when unknown.
    "downloaded_bytes": 0,
    "total_bytes": None,
    "percent": None,
    "speed_bps": None,
    "eta_seconds": None,
    "elapsed_seconds": 0.0,
}

_PROGRESS_POLL_SECONDS = 0.5
# Weight of the newest speed sample in the exponential moving average.
_SPEED_SMOOTHING = 0.3


def get_download_status() -> Dict[str, Any]:
    """Returns current active model download state."""
    return dict(_download_state)


def _reset_progress(total_bytes: Optional[int]) -> None:
    _download_state.update({
        "downloaded_bytes": 0,
        "total_bytes": total_bytes,
        "percent": 0.0 if total_bytes else None,
        "speed_bps": None,
        "eta_seconds": None,
        "elapsed_seconds": 0.0,
    })


def compute_progress(
    downloaded_bytes: int,
    total_bytes: Optional[int],
    prev_bytes: int,
    dt_seconds: float,
    prev_speed_bps: Optional[float],
) -> Dict[str, Optional[float]]:
    """Derives percent, smoothed speed and ETA from two byte-count samples."""
    speed = prev_speed_bps
    if dt_seconds > 0:
        instant = max(downloaded_bytes - prev_bytes, 0) / dt_seconds
        speed = instant if prev_speed_bps is None else (
            _SPEED_SMOOTHING * instant + (1 - _SPEED_SMOOTHING) * prev_speed_bps
        )

    percent = None
    eta = None
    if total_bytes:
        percent = min(100.0, 100.0 * downloaded_bytes / total_bytes)
        if speed and speed > 0:
            eta = max(total_bytes - downloaded_bytes, 0) / speed
    return {"percent": percent, "speed_bps": speed, "eta_seconds": eta}


HF_BASE_URL = "https://huggingface.co"
_HTTP_TIMEOUT = (15, 60)  # (connect, read) seconds
_CHUNK_BYTES = 1024 * 1024
_MAX_ATTEMPTS = 5
_RETRY_BACKOFF_SECONDS = 2.0
_PART_SUFFIX = ".part"


def hf_resolve_url(repo_id: str, filename: str, revision: str = "main") -> str:
    """Direct download URL of a file in a Hugging Face model repo."""
    return f"{HF_BASE_URL}/{repo_id}/resolve/{revision}/{filename}"


def _fetch_remote_size(repo_id: str, filename: str) -> Optional[int]:
    """Exact file size from the Hub, or None if it cannot be determined."""
    try:
        r = requests.head(hf_resolve_url(repo_id, filename), allow_redirects=True, timeout=_HTTP_TIMEOUT)
        r.raise_for_status()
        size = r.headers.get("Content-Length")
        return int(size) if size else None
    except Exception as e:
        logger.debug(f"Could not fetch remote size for {repo_id}/{filename}: {e}")
        return None


def _part_path(target_dir: Path, filename: str) -> Path:
    return Path(target_dir) / (filename + _PART_SUFFIX)


def _partial_download_size(target_dir: Path, filename: str) -> int:
    """Bytes written so far to <target_dir>/<filename>.part (0 if absent)."""
    try:
        return _part_path(target_dir, filename).stat().st_size
    except OSError:
        return 0


def _verify_file(path: Path, expected_size: Optional[int], expected_sha256: Optional[str]) -> None:
    """Raises ValueError if the file does not match the expected size/sha256."""
    actual_size = path.stat().st_size
    if expected_size is not None and actual_size != expected_size:
        raise ValueError(f"Size mismatch for {path.name}: expected {expected_size} bytes, got {actual_size}")
    if expected_sha256:
        actual = sha256_file(path)
        if actual.lower() != expected_sha256.lower():
            raise ValueError(f"SHA-256 mismatch for {path.name}: expected {expected_sha256}, got {actual}")


def _download_once(url: str, part: Path, session: Any) -> None:
    """One HTTP attempt, resuming <part> with a Range request when it already has bytes."""
    offset = part.stat().st_size if part.exists() else 0
    headers = {"Range": f"bytes={offset}-"} if offset else {}
    with session.get(url, headers=headers, stream=True, allow_redirects=True, timeout=_HTTP_TIMEOUT) as r:
        if r.status_code == 416:
            return  # requested range starts at EOF: the .part file is already complete
        r.raise_for_status()
        mode = "ab" if (offset and r.status_code == 206) else "wb"  # 200 = server ignored Range: restart
        with open(part, mode) as f:
            for chunk in r.iter_content(chunk_size=_CHUNK_BYTES):
                if chunk:
                    f.write(chunk)


def download_file(
    url: str,
    dest: Path,
    expected_size: Optional[int] = None,
    expected_sha256: Optional[str] = None,
    session: Any = None,
    max_attempts: int = _MAX_ATTEMPTS,
) -> Path:
    """
    Resumable, verified download: streams into <dest>.part (resuming via HTTP Range
    after interruptions, up to ``max_attempts``), verifies size/sha256, then renames
    atomically to <dest>. A corrupt .part is deleted so the next attempt starts clean.
    """
    dest = Path(dest)
    part = dest.with_name(dest.name + _PART_SUFFIX)
    session = session or requests.Session()

    last_error: Optional[Exception] = None
    for attempt in range(1, max_attempts + 1):
        try:
            _download_once(url, part, session)
            break
        except requests.RequestException as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            if status is not None and 400 <= status < 500 and status != 429:
                raise  # 401/404 etc. will not fix themselves
            last_error = e
            logger.warning(f"Download attempt {attempt}/{max_attempts} failed for {dest.name}: {e}")
            if attempt < max_attempts:
                time.sleep(_RETRY_BACKOFF_SECONDS * attempt)
    else:
        raise RuntimeError(f"Download of {dest.name} failed after {max_attempts} attempts: {last_error}")

    try:
        _verify_file(part, expected_size, expected_sha256)
    except ValueError:
        part.unlink(missing_ok=True)
        raise
    os.replace(part, dest)
    return dest


def _monitor_progress(target_dir: Path, filename: str, stop: threading.Event) -> None:
    start = time.monotonic()
    prev_t = start
    prev_bytes = _partial_download_size(target_dir, filename)  # resumed bytes don't count toward speed
    while not stop.wait(_PROGRESS_POLL_SECONDS):
        now = time.monotonic()
        downloaded = _partial_download_size(target_dir, filename)
        stats = compute_progress(
            downloaded, _download_state["total_bytes"],
            prev_bytes, now - prev_t, _download_state["speed_bps"],
        )
        _download_state.update(stats)
        _download_state["downloaded_bytes"] = downloaded
        _download_state["elapsed_seconds"] = now - start
        prev_t, prev_bytes = now, downloaded


def download_model(
    model_id: str = DEFAULT_MODEL_ID,
    set_as_active: bool = True
) -> Path:
    """
    Downloads candidate GGUF model from Hugging Face into the local GeoCore models directory.
    
    Args:
        model_id: Key from RECOMMENDED_MODELS or custom model name.
        set_as_active: If True, updates geoai_config.json to use this model immediately.
        
    Returns:
        Path to the downloaded GGUF file.
    """
    global _download_state
    if model_id not in RECOMMENDED_MODELS:
        raise ValueError(f"Unknown model_id '{model_id}'. Available: {list(RECOMMENDED_MODELS.keys())}")

    model_info = RECOMMENDED_MODELS[model_id]
    target_dir = get_default_model_dir()

    _download_state["status"] = "downloading"
    _download_state["model_id"] = model_id
    _download_state["display_name"] = model_info.get("display_name", model_id)
    _download_state["size_mb"] = model_info.get("size_mb", 0)
    _download_state["error"] = None
    expected_size = model_info.get("size_bytes")
    total_bytes = expected_size or _fetch_remote_size(model_info["repo_id"], model_info["filename"])
    if total_bytes is None and model_info.get("size_mb"):
        total_bytes = int(model_info["size_mb"] * 1024 * 1024)  # catalogue estimate
    _reset_progress(total_bytes)

    stop_monitor = threading.Event()
    monitor = threading.Thread(
        target=_monitor_progress,
        args=(Path(target_dir), model_info["filename"], stop_monitor),
        daemon=True,
    )
    try:
        logger.info(f"Starting download of {model_id} ({model_info['size_mb']} MB) into {target_dir}...")
        print(f"Downloading {model_id} ({model_info['filename']}) from {model_info['repo_id']}...")

        dest = Path(target_dir) / model_info["filename"]
        monitor.start()
        try:
            if dest.exists() and expected_size and dest.stat().st_size == expected_size:
                local_path = dest  # already installed; skip the network entirely
            else:
                local_path = download_file(
                    hf_resolve_url(model_info["repo_id"], model_info["filename"]),
                    dest,
                    expected_size=expected_size,
                    expected_sha256=model_info.get("sha256"),
                )
        finally:
            stop_monitor.set()
            monitor.join(timeout=2)

        path_obj = Path(local_path)
        final_size = path_obj.stat().st_size
        _download_state.update({
            "downloaded_bytes": final_size,
            "total_bytes": final_size,
            "percent": 100.0,
            "eta_seconds": 0.0,
        })
        logger.info(f"Model successfully saved at: {path_obj}")
        print(f"Model downloaded successfully to: {path_obj}")

        if set_as_active:
            config = load_config()
            config.model_path = str(path_obj)
            config.provider = "llama_cpp"
            save_config(config)
            print(f"Config updated: active model set to {path_obj}")

        _download_state["status"] = "completed"
        return path_obj
    except Exception as e:
        _download_state["status"] = "error"
        _download_state["error"] = str(e)
        logger.error(f"Download failed for {model_id}: {e}")
        raise


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="GeoAI Local GGUF Model Manager")
    parser.add_argument("--list", action="store_true", help="List available models")
    parser.add_argument("--download", type=str, default=None, help="Model ID to download (e.g. qwen2.5-1.5b-instruct)")
    args = parser.parse_args()

    if args.list:
        models = list_available_models()
        print("\n=== GeoAI Local Model Registry ===")
        for m in models:
            status = "[INSTALLED]" if m["is_installed"] else "[AVAILABLE]"
            print(f"- {m['id']} ({m['size_mb']} MB) {status}: {m['description']}")
    elif args.download:
        download_model(args.download)
    else:
        parser.print_help()
