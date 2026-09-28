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
import logging
from typing import Dict, Any, Optional
from threading import RLock, Thread

try:
    import psutil
except ImportError:
    psutil = None

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
        self._warming = False
        self._idle_watch: Optional[Thread] = None

    def set_provider(self, provider: ModelProvider) -> None:
        with self._lock:
            self._provider = provider
            self._last_access_time = time.time()

    def get_provider(self) -> ModelProvider:
        with self._lock:
            self._last_access_time = time.time()
            if self._provider is None:
                self._provider = self._create_provider()
            self._ensure_idle_watch()
            return self._provider

    def _ensure_idle_watch(self) -> None:
        """Start (once) a daemon thread that applies the idle timeout while the app runs."""
        if self._idle_watch is not None and self._idle_watch.is_alive():
            return
        interval = max(1.0, min(60.0, self.idle_timeout_seconds / 4))

        def _watch():
            while True:
                time.sleep(interval)
                try:
                    self.check_idle_and_unload()
                except Exception as e:  # never let the watcher die silently mid-session
                    logger.warning(f"GeoAI idle check failed: {e}")

        self._idle_watch = Thread(target=_watch, name="geoai-idle-unload", daemon=True)
        self._idle_watch.start()

    def warm_up(self, background: bool = True) -> Dict[str, Any]:
        """
        Load the model ahead of the first request (e.g. when the GeoAI panel opens) and
        evaluate the static system prompt into the KV cache, so the first answer does not pay
        the model load (~8 s on a laptop CPU). The idle timeout still unloads it when unused.
        """
        with self._lock:
            provider = self.get_provider()
            if not hasattr(provider, "warm_up"):
                return {"status": "not_required", "loaded": provider.is_loaded()}
            if self._warming:
                return {"status": "warming", "loaded": False}
            if provider.is_loaded():
                return {"status": "loaded", "loaded": True}
            self._warming = True

        def _run():
            try:
                from core.geoai.system_prompt import build_system_prompt
                provider.warm_up(build_system_prompt(None))
            except Exception as e:
                logger.warning(f"GeoAI warm-up failed: {e}")
            finally:
                with self._lock:
                    self._warming = False
                    self._last_access_time = time.time()

        if background:
            Thread(target=_run, name="geoai-warm-up", daemon=True).start()
            return {"status": "warming", "loaded": False}
        _run()
        return {"status": "loaded" if provider.is_loaded() else "failed", "loaded": provider.is_loaded()}

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
            if elapsed < self.idle_timeout_seconds:
                return False
            logger.info(f"GeoAI: Model idle for {elapsed:.1f}s. Auto-unloading to free desktop memory.")
        self.unload()
        return True

    def cancel(self) -> Dict[str, Any]:
        """Aborts the GeoAI request in progress, if any (the model stays loaded)."""
        with self._lock:
            provider = self._provider
        if provider is not None:
            provider.cancel()
        return {"status": "cancelled" if provider is not None else "idle"}

    def unload(self) -> Dict[str, Any]:
        """Explicitly unloads the model from RAM / VRAM."""
        with self._lock:
            provider, self._provider = self._provider, None
        # Outside the manager lock: provider.unload() waits for a running generation, and
        # status/memory requests must not queue behind it (each holds a server thread).
        if provider is not None and hasattr(provider, "unload"):
            # Stop that generation first: otherwise a model switch waits minutes for it, while
            # the next request already loads the new model next to the old one in RAM.
            provider.cancel()
            provider.unload()

        return {
            "status": "unloaded",
            "message": "Model weights released from memory."
        }

    def get_memory_status(self) -> Dict[str, Any]:
        """Returns current process RAM usage and model load status."""
        ram_mb = 0.0
        if psutil is not None:
            try:
                process = psutil.Process(os.getpid())
                mem_info = process.memory_info()
                ram_mb = mem_info.rss / (1024 * 1024)
            except Exception:
                pass

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
