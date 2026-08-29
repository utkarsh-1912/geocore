"""
GeoAI Model Configuration Module.
Handles configuration persistence and model discovery.

Author: Utkarsh Gupta
License: GPL v3
"""

import os
import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_FILENAME = "geoai_config.json"

@dataclass
class GeoAIModelConfig:
    model_path: Optional[str] = None  # Absolute path to GGUF file
    n_ctx: int = 4096  # Context window size
    n_gpu_layers: int = 0  # 0 = CPU only, -1 = all layers on GPU
    temperature: float = 0.1  # Low temperature for deterministic tool calling
    max_tokens: int = 1024  # Max generation length
    provider: str = "auto"  # "llama_cpp", "heuristic", or "auto"
    verbose: bool = False  # llama.cpp verbose logging

def get_config_dir() -> Path:
    """Returns the config directory path and creates it if it doesn't exist."""
    if os.name == 'nt':
        appdata = os.environ.get('APPDATA')
        if appdata:
            path = Path(appdata) / "GeoCore"
        else:
            path = Path.home() / ".geocore"
    else:
        path = Path.home() / ".geocore"
        
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_default_model_dir() -> Path:
    """Returns the default models directory path and creates it if it doesn't exist."""
    path = get_config_dir() / "models"
    path.mkdir(parents=True, exist_ok=True)
    return path

def load_config() -> GeoAIModelConfig:
    """Loads configuration from JSON file and applies environment variable overrides."""
    config = GeoAIModelConfig()
    config_file = get_config_dir() / DEFAULT_CONFIG_FILENAME
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Update dataclass with loaded JSON fields
                for k, v in data.items():
                    if hasattr(config, k):
                        setattr(config, k, v)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in {config_file}. Using default configuration.")
        except Exception as e:
            logger.warning(f"Error loading {config_file}: {e}. Using default configuration.")

    # Apply environment variable overrides
    if "GEOAI_MODEL_PATH" in os.environ:
        config.model_path = os.environ["GEOAI_MODEL_PATH"]
    if "GEOAI_PROVIDER" in os.environ:
        config.provider = os.environ["GEOAI_PROVIDER"]
    if "GEOAI_N_CTX" in os.environ:
        try:
            config.n_ctx = int(os.environ["GEOAI_N_CTX"])
        except ValueError:
            logger.warning("Invalid value for GEOAI_N_CTX, keeping default.")
    if "GEOAI_GPU_LAYERS" in os.environ:
        try:
            config.n_gpu_layers = int(os.environ["GEOAI_GPU_LAYERS"])
        except ValueError:
            logger.warning("Invalid value for GEOAI_GPU_LAYERS, keeping default.")

    return config

def save_config(config: GeoAIModelConfig) -> None:
    """Saves the configuration to a JSON file."""
    config_file = get_config_dir() / DEFAULT_CONFIG_FILENAME
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(config), f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save configuration to {config_file}: {e}")

def get_all_search_directories() -> List[Path]:
    """Returns all directories where desktop or user GGUF models might reside."""
    dirs = [get_default_model_dir()]
    
    # Check application executable directory & PyInstaller bundle
    try:
        if getattr(sys, 'frozen', False):
            exe_dir = Path(sys.executable).parent
            dirs.append(exe_dir / "models")
            dirs.append(exe_dir / "resources" / "models")
            dirs.append(exe_dir.parent / "resources" / "models")
            
        meipass = getattr(sys, '_MEIPASS', None)
        if meipass:
            dirs.append(Path(meipass) / "models")
    except Exception:
        pass

    # Check local workspace / development paths
    try:
        repo_root = Path(__file__).resolve().parent.parent.parent
        dirs.append(repo_root / "models")
    except Exception:
        pass

    # Check Windows ProgramFiles and LocalAppData
    if os.name == 'nt':
        prog_files = os.environ.get('ProgramFiles')
        if prog_files:
            dirs.append(Path(prog_files) / "GeoCore" / "models")
        local_app = os.environ.get('LOCALAPPDATA')
        if local_app:
            dirs.append(Path(local_app) / "GeoCore" / "models")

    # Filter to existing directories without duplicates
    seen = set()
    valid_dirs = []
    for d in dirs:
        resolved = d.resolve() if d.exists() else d
        if str(resolved) not in seen:
            seen.add(str(resolved))
            valid_dirs.append(d)

    return valid_dirs

def find_gguf_models(search_dir: Optional[Path] = None) -> List[Path]:
    """Scans for .gguf files across all search directories or a specific directory."""
    if search_dir is not None:
        target_dirs = [search_dir]
    else:
        target_dirs = get_all_search_directories()
        
    models = []
    seen_files = set()
    
    for directory in target_dirs:
        if directory.exists() and directory.is_dir():
            try:
                for file in directory.iterdir():
                    if file.is_file() and file.suffix.lower() == '.gguf':
                        abs_str = str(file.resolve())
                        if abs_str not in seen_files:
                            seen_files.add(abs_str)
                            models.append(file)
            except Exception as e:
                logger.debug(f"Could not scan directory {directory}: {e}")
                
    return models

def auto_link_installed_model() -> Optional[str]:
    """Automatically detects and links any bundled/installed GGUF model to active config."""
    models = find_gguf_models()
    if not models:
        return None
        
    config = load_config()
    # If currently configured model path exists, keep it
    if config.model_path and Path(config.model_path).exists():
        return config.model_path
        
    # Auto-link first discovered model
    best_model = str(models[0].resolve())
    config.model_path = best_model
    config.provider = "llama_cpp"
    save_config(config)
    logger.info(f"Auto-linked detected model: {best_model}")
    return best_model

