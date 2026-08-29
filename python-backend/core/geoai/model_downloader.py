# Author: Utkarsh Gupta
# License: GPL v3
"""
Local GGUF Model Downloader & Manager.
Downloads candidate SLM models (Qwen 2.5/3, Gemma) from Hugging Face directly
to the local GeoCore models directory and configures GeoAI for local inference.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from huggingface_hub import hf_hub_download

from core.geoai.model_config import (
    get_default_model_dir,
    load_config,
    save_config,
    find_gguf_models,
    GeoAIModelConfig
)

logger = logging.getLogger(__name__)

# Curated Candidate SLM Registry for Desktop Offline Geotechnical AI
RECOMMENDED_MODELS: Dict[str, Dict[str, Any]] = {
    "qwen2.5-1.5b-instruct": {
        "repo_id": "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
        "filename": "qwen2.5-1.5b-instruct-q4_k_m.gguf",
        "size_mb": 986,
        "description": "Ultra-lightweight (1.5B), fast CPU inference, native function calling support",
        "recommended_for": "Laptops, low-resource workstations, high-speed tool calling"
    },
    "qwen2.5-3b-instruct": {
        "repo_id": "Qwen/Qwen2.5-3B-Instruct-GGUF",
        "filename": "qwen2.5-3b-instruct-q4_k_m.gguf",
        "size_mb": 2040,
        "description": "Balanced (3B) with superior multi-turn geotechnical reasoning and tool precision",
        "recommended_for": "Standard desktop engineering workstations"
    },
    "gemma-2-2b-it": {
        "repo_id": "bartowski/gemma-2-2b-it-GGUF",
        "filename": "gemma-2-2b-it-Q4_K_M.gguf",
        "size_mb": 1630,
        "description": "Google Gemma 2 (2.6B) optimized for high factual grounding and synthesis",
        "recommended_for": "Literature research, standards interpretation, report writing"
    }
}


def list_available_models() -> List[Dict[str, Any]]:
    """Returns list of curated candidate models and their local download status."""
    installed = {p.name.lower(): p for p in find_gguf_models()}
    results = []

    for key, info in RECOMMENDED_MODELS.items():
        is_installed = info["filename"].lower() in installed
        local_path = str(installed[info["filename"].lower()]) if is_installed else None
        results.append({
            "id": key,
            "repo_id": info["repo_id"],
            "filename": info["filename"],
            "size_mb": info["size_mb"],
            "description": info["description"],
            "recommended_for": info["recommended_for"],
            "is_installed": is_installed,
            "local_path": local_path
        })
    return results


_download_state: Dict[str, Any] = {
    "status": "idle",  # "idle", "downloading", "completed", "error"
    "model_id": None,
    "error": None
}


def get_download_status() -> Dict[str, Any]:
    """Returns current active model download state."""
    return dict(_download_state)


def download_model(
    model_id: str = "qwen2.5-1.5b-instruct",
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
    _download_state["error"] = None

    try:
        logger.info(f"Starting download of {model_id} ({model_info['size_mb']} MB) into {target_dir}...")
        print(f"Downloading {model_id} ({model_info['filename']}) from {model_info['repo_id']}...")

        local_path = hf_hub_download(
            repo_id=model_info["repo_id"],
            filename=model_info["filename"],
            local_dir=str(target_dir),
            local_dir_use_symlinks=False
        )

        path_obj = Path(local_path)
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
