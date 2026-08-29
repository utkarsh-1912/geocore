# Author: Utkarsh Gupta
# License: GPL v3
"""
GeoAI Memory Lifecycle & Resource Management.
Ensures desktop application responsiveness by providing:
- Lazy loading and explicit unloading of GGUF model weights
- Idle timeout auto-unloading when GeoAI is inactive
- Process memory (RAM) and model state tracking
"""

import time
import os
import psutil
import logging
from typing import Dict, Any, Optional
from threading import RLock

from core.geoai.model_provider import ModelProvider
from core.geoai.model_config import load_config, save_config, GeoAIModelConfig

logger = logging.getLogger(__name__)


class ModelLifecycleManager:
    """
    Manages local model loading, memory release, and idle timeouts.
    """
    def __init__(self, idle_timeout_seconds: float = 900.0):  # 15 minutes default
        self.idle_timeout_seconds = idle_timeout_seconds
        self._provider: Optional[ModelProvider] = None
        self._last_access_time: float = time.time()
        self._lock = RLock()

    def set_provider(self, provider: ModelProvider) -> None:
        with self._lock:
            self._provider = provider
            self._last_access_time = time.time()

    def get_provider(self) -> ModelProvider:
        with self._lock:
            self._last_access_time = time.time()
            if self._provider is None:
                self._provider = self._create_provider()
            return self._provider

    def touch(self) -> None:
        """Mark provider as recently used."""
        with self._lock:
            self._last_access_time = time.time()

    def _create_provider(self) -> ModelProvider:
        """Instantiate configured provider."""
        config = load_config()
        if config.provider == "llama_cpp" or (config.provider == "auto" and config.model_path):
            try:
                from core.geoai.llama_cpp_provider import LlamaCppProvider
                return LlamaCppProvider(config)
            except Exception as e:
                logger.warning(f"Could not load LlamaCppProvider: {e}. Reverting to heuristic.")
                from core.geoai.heuristic_provider import HeuristicProvider
                return HeuristicProvider()
        else:
            from core.geoai.heuristic_provider import HeuristicProvider
            return HeuristicProvider()

    def check_idle_and_unload(self) -> bool:
        """Unloads model if inactive for longer than idle_timeout_seconds."""
        with self._lock:
            if self._provider is None or not self._provider.is_loaded():
                return False

            elapsed = time.time() - self._last_access_time
            if elapsed >= self.idle_timeout_seconds:
                logger.info(f"GeoAI: Model idle for {elapsed:.1f}s. Auto-unloading to free desktop memory.")
                self.unload()
                return True
        return False

    def unload(self) -> Dict[str, Any]:
        """Explicitly unloads the model from RAM / VRAM."""
        with self._lock:
            if self._provider is not None:
                if hasattr(self._provider, "unload"):
                    self._provider.unload()
                self._provider = None

        return {
            "status": "unloaded",
            "message": "Model weights released from memory."
        }

    def get_memory_status(self) -> Dict[str, Any]:
        """Returns current process RAM usage and model load status."""
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        ram_mb = mem_info.rss / (1024 * 1024)

        with self._lock:
            is_loaded = self._provider is not None and self._provider.is_loaded()
            info = self._provider.model_info() if self._provider else {"provider": "none", "loaded": False}
            idle_seconds = time.time() - self._last_access_time

        return {
            "process_ram_mb": round(ram_mb, 1),
            "is_model_loaded": is_loaded,
            "idle_duration_seconds": round(idle_seconds, 1),
            "model_info": info
        }


# Global singleton lifecycle manager
lifecycle_manager = ModelLifecycleManager()
