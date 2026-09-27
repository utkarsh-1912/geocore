# Author: Utkarsh Gupta
# License: GPL v3
"""
System diagnostics for the desktop "System Health" panel.

Everything here is cheap and side-effect free: it never loads the GeoAI model,
never waits for the background warm-up and never imports groundhog. Optional
information (psutil, GeoAI config) degrades to ``None`` when unavailable.
"""
import os
import platform
import sys
import time
from typing import Any, Dict, Optional

try:
    import psutil
except ImportError:
    psutil = None

APP_VERSION = "1.0.0"
_STARTED_AT = time.time()


def _groundhog_version() -> Optional[str]:
    try:
        from importlib.metadata import version
        return version("groundhog")
    except Exception:
        return None


def _system_memory() -> Dict[str, Optional[float]]:
    info: Dict[str, Optional[float]] = {
        "process_ram_mb": None,
        "system_total_mb": None,
        "system_available_mb": None,
        "system_percent": None,
        "cpu_count": os.cpu_count(),
    }
    if psutil is None:
        return info
    try:
        info["process_ram_mb"] = round(psutil.Process(os.getpid()).memory_info().rss / 2**20, 1)
        vm = psutil.virtual_memory()
        info["system_total_mb"] = round(vm.total / 2**20, 1)
        info["system_available_mb"] = round(vm.available / 2**20, 1)
        info["system_percent"] = round(vm.percent, 1)
    except Exception:
        pass
    return info


def _geoai_summary() -> Dict[str, Any]:
    """Configured provider/model and whether weights are resident, without loading anything."""
    summary: Dict[str, Any] = {
        "provider": None,
        "model_path": None,
        "model_name": None,
        "model_file_found": None,
        "loaded": False,
        "idle_seconds": None,
        "tools_registered": None,
    }
    try:
        from core.geoai.model_config import load_config
        config = load_config()
        summary["provider"] = config.provider
        if config.model_path:
            summary["model_path"] = str(config.model_path)
            summary["model_name"] = os.path.basename(str(config.model_path))
            summary["model_file_found"] = os.path.isfile(str(config.model_path))
    except Exception:
        pass
    try:
        from core.geoai.lifecycle import lifecycle_manager
        memory = lifecycle_manager.get_memory_status()
        summary["loaded"] = bool(memory.get("is_model_loaded"))
        summary["idle_seconds"] = memory.get("idle_duration_seconds")
    except Exception:
        pass
    try:
        from core.geoai.tool_registry import tool_registry
        summary["tools_registered"] = len(tool_registry.list_tools())
    except Exception:
        pass
    return summary


def collect_diagnostics(functions_registered: Optional[int] = None) -> Dict[str, Any]:
    """Snapshot of engine, runtime, memory and GeoAI state for the health panel."""
    from core.warmup import is_warm

    return {
        "status": "ok",
        "version": APP_VERSION,
        "uptime_seconds": round(time.time() - _STARTED_AT, 1),
        "engine": {
            "ready": is_warm(),
            "groundhog_version": _groundhog_version(),
            "functions_registered": functions_registered,
        },
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.system(),
            "platform_release": platform.release(),
            "architecture": platform.machine(),
            "frozen": bool(getattr(sys, "frozen", False)),
        },
        "memory": _system_memory(),
        "geoai": _geoai_summary(),
    }
