# Author: Utkarsh Gupta
# License: GPL v3
"""
Per-user storage locations shared by the backend (saved objects, GeoAI config,
models, research index).

The packaged backend runs with its working directory inside the installed
bundle, which is read-only on macOS and shared between users on Windows, so
anything written at runtime belongs in the per-user config directory instead.
"""
import os
from pathlib import Path

CONFIG_DIR_ENV_VAR = "GEOCORE_CONFIG_DIR"


def get_config_dir() -> Path:
    """
    Returns the per-user GeoCore config directory, creating it if needed.

    %APPDATA%\\GeoCore on Windows, ~/.geocore elsewhere. The GEOCORE_CONFIG_DIR
    environment variable overrides both (the test suite uses it for isolation).
    """
    override = os.environ.get(CONFIG_DIR_ENV_VAR)
    if override:
        path = Path(override)
    elif os.name == 'nt' and os.environ.get('APPDATA'):
        path = Path(os.environ['APPDATA']) / "GeoCore"
    else:
        path = Path.home() / ".geocore"

    path.mkdir(parents=True, exist_ok=True)
    return path
