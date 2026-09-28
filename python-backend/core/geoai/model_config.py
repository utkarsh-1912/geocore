"""
GeoAI Model Configuration Module.
Handles configuration persistence and model discovery.

Author: Utkarsh Gupta
License: GPL v3
"""

import os
import sys
import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, List

# Re-exported: callers and tests reference core.geoai.model_config.get_config_dir.
from core.paths import get_config_dir

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_FILENAME = "geoai_config.json"

# Chat formats understood by LlamaCppProvider (None = auto, see GeoAIModelConfig.chat_format).
CHAT_FORMATS = ("chatml-function-calling", "native", "prompted")


def _env_lora_path() -> Optional[str]:
    return os.environ.get("GEOAI_LORA_PATH") or None


def _env_lora_scale() -> float:
    try:
        return float(os.environ.get("GEOAI_LORA_SCALE", "1.0"))
    except ValueError:
        logger.warning("Invalid value for GEOAI_LORA_SCALE, using 1.0.")
        return 1.0


def _env_chat_format() -> Optional[str]:
    return os.environ.get("GEOAI_CHAT_FORMAT") or None


def _env_disable_thinking() -> bool:
    """GEOAI_THINKING=1/true/yes/on enables reasoning traces; default (unset) is off."""
    return os.environ.get("GEOAI_THINKING", "").strip().lower() not in ("1", "true", "yes", "on")


@dataclass
class GeoAIModelConfig:
    model_path: Optional[str] = None  # Absolute path to GGUF file
    n_ctx: int = 4096  # Context window size
    n_gpu_layers: int = 0  # 0 = CPU only, -1 = all layers on GPU
    temperature: float = 0.1  # Low temperature for deterministic tool calling
    max_tokens: int = 1024  # Max generation length
    # llama.cpp repetition penalty. Small models otherwise loop on the post-tool explanation
    # ("The soil behavior type index (Ic) is ... " repeated until max_tokens).
    repeat_penalty: float = 1.15
    provider: str = "auto"  # "llama_cpp", "heuristic", or "auto"
    verbose: bool = False  # llama.cpp verbose logging
    # Optional GGUF LoRA adapter applied on top of model_path (see core/geoai/lora_adapter.py).
    # Defaults come from GEOAI_LORA_PATH / GEOAI_LORA_SCALE so callers that build the
    # config directly (e.g. the eval runner) pick up an adapter without code changes.
    lora_path: Optional[str] = field(default_factory=_env_lora_path)
    lora_scale: float = field(default_factory=_env_lora_scale)
    # Prompt format: "chatml-function-calling" (llama-cpp-python handler, legacy default),
    # "native" (the GGUF's own chat template; tool calls parsed from <tool_call> blocks),
    # "prompted" (the GGUF's own template, tool schemas described in the system text; for
    # templates without a tool section such as Gemma 3),
    # or None = auto: "native" when an active adapter's sidecar says it was trained with
    # the native template, else "native"/"prompted" depending on whether the GGUF's template
    # renders tools, else "chatml-function-calling". Env: GEOAI_CHAT_FORMAT.
    chat_format: Optional[str] = field(default_factory=_env_chat_format)
    # Tools offered per request. Each schema is ~390 tokens, so 20 tools overflow n_ctx=4096;
    # on eval_test recall@5 is 0.569 vs 0.590 at 20. Must match finetune.config.max_tools.
    max_tools: int = 5
    # Suppress reasoning traces for GGUFs whose chat template has an enable_thinking switch
    # (Qwen3, Qwen3.5, SmolLM3): the template is rendered with enable_thinking=False (as in
    # fine-tuning), falling back to the "/no_think" soft switch; <think> blocks are stripped
    # from answers either way. Traces cost tens of seconds per turn on a CPU and GeoAI plans in
    # one line. Env: GEOAI_THINKING=1 turns thinking on.
    disable_thinking: bool = field(default_factory=_env_disable_thinking)
    # --- CPU inference performance (see resolve_thread_counts) ---
    # Threads for token generation (n_threads) and prompt processing (n_threads_batch).
    # None = auto. Env: GEOAI_N_THREADS / GEOAI_N_THREADS_BATCH.
    n_threads: Optional[int] = None
    n_threads_batch: Optional[int] = None
    # Prompt-processing batch size (tokens per llama_decode call). Env: GEOAI_N_BATCH.
    n_batch: int = 512
    # Generation caps per agent phase. The first turn is usually a tool call (~40-120 tokens;
    # XML-style calls such as Qwen3.5's are ~2x) but it is also where a direct answer without a
    # tool is written (concept explanations, research), so it cannot be tiny. The post-tool answer
    # may cover several results, assumptions and sources. Looping completions do not run to these
    # caps: the agent stops generation once the answer starts repeating itself (response_guard).
    # Env: GEOAI_DECISION_MAX_TOKENS / GEOAI_ANSWER_MAX_TOKENS.
    decision_max_tokens: int = 512
    answer_max_tokens: int = 1024
    # Wall-clock limit for one model call (prompt processing + generation), in seconds. A call
    # past it is aborted so a stuck request can never hold the model forever. Env:
    # GEOAI_GENERATION_TIMEOUT_S. 0 = no limit.
    generation_timeout_s: int = 600


def resolve_thread_counts(config: "GeoAIModelConfig") -> "tuple[int, int]":
    """
    (n_threads, n_threads_batch) for llama.cpp on this machine.

    Explicit config values win. Auto: generation is memory-bandwidth bound and stalls on the
    slowest thread, so it uses the physical core count (hyper-threads add contention);
    prompt processing is compute bound and uses every logical CPU. Both leave nothing to
    the rest of the desktop only while a request is running.
    """
    logical = os.cpu_count() or 4
    physical = None
    try:
        import psutil  # optional dependency (already used by lifecycle/diagnostics)
        physical = psutil.cpu_count(logical=False)
    except Exception:
        pass
    physical = physical or max(1, logical // 2)
    n = config.n_threads if config.n_threads and config.n_threads > 0 else physical
    nb = config.n_threads_batch if config.n_threads_batch and config.n_threads_batch > 0 else logical
    return n, nb


def get_default_model_dir() -> Path:
    """Returns the default models directory path and creates it if it doesn't exist."""
    path = get_config_dir() / "models"
    path.mkdir(parents=True, exist_ok=True)
    return path

# save_config writes every field, so a saved file pins the defaults of the version that wrote it.
# Values equal to a superseded default are treated as "never chosen" and move to the current
# default; any other saved value (a deliberate choice) and env overrides are kept.
_LEGACY_DEFAULTS = {
    "decision_max_tokens": (200,),
    "answer_max_tokens": (320, 512),
}


def _upgrade_legacy_defaults(config: GeoAIModelConfig) -> None:
    defaults = GeoAIModelConfig()
    for attr, old in _LEGACY_DEFAULTS.items():
        value, new = getattr(config, attr), getattr(defaults, attr)
        if value in old and value != new:
            logger.info(f"GeoAI config: {attr}={value} was an old default; using {new}.")
            setattr(config, attr, new)


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
                _upgrade_legacy_defaults(config)
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
    if "GEOAI_LORA_PATH" in os.environ:
        config.lora_path = _env_lora_path()
    if "GEOAI_LORA_SCALE" in os.environ:
        config.lora_scale = _env_lora_scale()
    if "GEOAI_CHAT_FORMAT" in os.environ:
        config.chat_format = _env_chat_format()
    if "GEOAI_MAX_TOOLS" in os.environ:
        try:
            config.max_tools = int(os.environ["GEOAI_MAX_TOOLS"])
        except ValueError:
            logger.warning("Invalid value for GEOAI_MAX_TOOLS, keeping default.")
    if "GEOAI_THINKING" in os.environ:
        config.disable_thinking = _env_disable_thinking()
    for env, attr in (("GEOAI_N_THREADS", "n_threads"), ("GEOAI_N_THREADS_BATCH", "n_threads_batch"),
                      ("GEOAI_N_BATCH", "n_batch"), ("GEOAI_DECISION_MAX_TOKENS", "decision_max_tokens"),
                      ("GEOAI_ANSWER_MAX_TOKENS", "answer_max_tokens"),
                      ("GEOAI_GENERATION_TIMEOUT_S", "generation_timeout_s")):
        if env in os.environ:
            try:
                setattr(config, attr, int(os.environ[env]))
            except ValueError:
                logger.warning(f"Invalid value for {env}, keeping default.")

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
    """
    Scans for .gguf model files across all search directories or a specific directory.

    GGUF LoRA adapters (``general.type == 'adapter'``) are not models and are skipped;
    keep adapters in e.g. ``models/adapters/`` and point ``lora_path`` at them.
    """
    from core.geoai.gguf_meta import is_lora_adapter
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
                        if is_lora_adapter(file):
                            continue
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

