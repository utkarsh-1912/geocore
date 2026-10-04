# Author: Utkarsh Gupta
# License: GPL v3

from typing import Dict, Any, List, Optional
from pathlib import Path
import uuid
import os
import json
import tempfile
import threading

from .paths import get_config_dir

SAVED_OBJECTS_FILENAME = "saved_objects.json"
#: Project-level settings (e.g. the recorded groundwater level), kept next to the saved objects.
PROJECT_SETTINGS_FILENAME = "project_settings.json"

#: What an uploaded table holds. Recorded at upload (chosen by the user) and kept in the object's
#: metadata as "kind"; objects saved before kinds were recorded have none.
DATA_KIND_SOIL_PROFILE = "soil_profile"
DATA_KIND_CPT = "cpt"
DATA_KINDS = (DATA_KIND_SOIL_PROFILE, DATA_KIND_CPT)
_BACKEND_DIR = Path(__file__).resolve().parent.parent


def _legacy_saved_objects_paths() -> List[Path]:
    """Where earlier versions kept saved_objects.json: the working directory
    (the install folder in packaged builds) and the backend folder (dev)."""
    candidates = [
        Path.cwd() / SAVED_OBJECTS_FILENAME,
        _BACKEND_DIR / SAVED_OBJECTS_FILENAME,
    ]
    return list(dict.fromkeys(candidates))


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    """Writes via a temp file in the same directory and os.replace, so a crash
    mid-write never leaves a truncated file behind."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def resolve_saved_objects_path() -> Path:
    """
    Returns the per-user saved-objects file. On first run, copies an existing
    file from a legacy location (the old file is left in place, since the
    install folder may be read-only).
    """
    path = get_config_dir() / SAVED_OBJECTS_FILENAME
    if path.exists():
        return path
    for legacy in _legacy_saved_objects_paths():
        if not legacy.is_file():
            continue
        try:
            _atomic_write_bytes(path, legacy.read_bytes())
            print(f"Migrated saved objects from {legacy} to {path}.")
            break
        except OSError as e:
            print(f"Failed to migrate saved objects from {legacy}: {e}")
    return path


class StateManager:
    def __init__(self):
        self._objects_store: Dict[str, Any] = {}
        self._metadata_store: Dict[str, Dict[str, Any]] = {}
        # Resolved (and migrated) on first load, not at import.
        self._path: Optional[Path] = None
        # Saved objects are restored on first access rather than at import:
        # rebuilding a SoilProfile imports groundhog/scipy, which would slow
        # backend start-up. main.py pre-loads them in the background.
        self._loaded = False
        self._load_lock = threading.Lock()
        # Project settings load on first use, independently of the (slower) saved objects.
        self._settings: Optional[Dict[str, Any]] = None
        self._settings_lock = threading.Lock()

    def ensure_loaded(self):
        if self._loaded:
            return
        from .warmup import wait_for_warmup
        wait_for_warmup()  # the start-up warm-up restores saved objects itself
        with self._load_lock:
            if not self._loaded:
                self._load_from_disk()
                self._loaded = True

    @property
    def _objects(self) -> Dict[str, Any]:
        self.ensure_loaded()
        return self._objects_store

    @property
    def _metadata(self) -> Dict[str, Dict[str, Any]]:
        self.ensure_loaded()
        return self._metadata_store

    @property
    def path(self) -> Path:
        if self._path is None:
            self._path = resolve_saved_objects_path()
        return self._path

    def _load_from_disk(self):
        try:
            if not self.path.exists():
                return
            with open(self.path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for obj_data in data:
                obj_id = obj_data["id"]
                type_name = obj_data["type"]
                name = obj_data["name"]
                raw_data = obj_data.get("data")
                
                # Reconstruct object based on type
                if type_name == "SoilProfile" and raw_data:
                    # SoilProfile is typically a DataFrame or list of dicts. 
                    # If we saved it as record list:
                    import pandas as pd
                    # Fix: Reconstruct as SoilProfile object, not raw DataFrame
                    try:
                        from groundhog.general.soilprofile import SoilProfile
                        df = pd.DataFrame(raw_data)
                        self._objects_store[obj_id] = SoilProfile(df)
                    except ImportError:
                        print("Warning: Could not import SoilProfile from groundhog. Reverting to DataFrame.")
                        df = pd.DataFrame(raw_data)
                        self._objects_store[obj_id] = df
                
                self._metadata_store[obj_id] = {
                    "id": obj_id,
                    "type": type_name,
                    "name": name,
                    "timestamp": obj_data.get("timestamp", "restored")
                }
                if obj_data.get("kind") in DATA_KINDS:
                    self._metadata_store[obj_id]["kind"] = obj_data["kind"]
                
            print(f"Loaded {len(self._objects_store)} objects from disk.")
        except Exception as e:
            print(f"Failed to load saved objects: {e}")

    def _save_to_disk(self):
        # We only save SoilProfiles for now as they are simple DataFrames
        to_save = []
        for obj_id, meta in self._metadata.items():
            if meta["type"] == "SoilProfile":
                obj = self._objects.get(obj_id)
                if hasattr(obj, 'to_dict'):
                    # Save as records
                    data = obj.to_dict(orient='records')
                    record = {
                        "id": obj_id,
                        "type": meta["type"],
                        "name": meta["name"],
                        "timestamp": meta["timestamp"],
                        "data": data
                    }
                    if meta.get("kind"):
                        record["kind"] = meta["kind"]
                    to_save.append(record)
        
        try:
            _atomic_write_bytes(self.path, json.dumps(to_save, indent=2).encode('utf-8'))
        except Exception as e:
            print(f"Failed to save objects to disk: {e}")

    def store(self, obj: Any, type_name: str, name: Optional[str] = None, kind: Optional[str] = None) -> str:
        """Stores an object and returns its ID. ``kind`` is one of DATA_KINDS (or None: not recorded)."""
        if kind is not None and kind not in DATA_KINDS:
            raise ValueError(f"Unknown data kind '{kind}' (expected one of: {', '.join(DATA_KINDS)}).")
        obj_id = str(uuid.uuid4())
        
        # improved naming strategy
        if not name:
            name = f"{type_name}_{obj_id[:8]}"
            
        self._objects[obj_id] = obj
        self._metadata[obj_id] = {
            "id": obj_id,
            "type": type_name,
            "name": name,
            "timestamp": "now" # In real app, use datetime
        }
        if kind:
            self._metadata[obj_id]["kind"] = kind
        
        self._save_to_disk()
        return obj_id

    def get(self, obj_id: str) -> Optional[Any]:
        return self._objects.get(obj_id)

    def list_by_type(self, type_name: str) -> List[Dict[str, Any]]:
        return [
            meta for meta in self._metadata.values() 
            if meta["type"] == type_name or type_name == "all"
        ]
    
    def delete(self, obj_id: str):
        if obj_id in self._objects:
            del self._objects[obj_id]
            del self._metadata[obj_id]
            self._save_to_disk()

    # ------------------------------------------------------------------ project settings
    @property
    def settings_path(self) -> Path:
        return self.path.parent / PROJECT_SETTINGS_FILENAME

    def _project_settings(self) -> Dict[str, Any]:
        if self._settings is None:
            with self._settings_lock:
                if self._settings is None:
                    self._settings = self._read_settings()
        return self._settings

    def _read_settings(self) -> Dict[str, Any]:
        try:
            if self.settings_path.is_file():
                data = json.loads(self.settings_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
                print(f"Ignoring malformed project settings in {self.settings_path}.")
        except (OSError, ValueError) as e:
            print(f"Failed to load project settings: {e}")
        return {}

    def get_project_setting(self, key: str, default: Any = None) -> Any:
        return self._project_settings().get(key, default)

    def set_project_setting(self, key: str, value: Any) -> None:
        """Saves one project setting; None removes it. Raises OSError when it cannot be written."""
        settings = dict(self._project_settings())
        if value is None:
            settings.pop(key, None)
        else:
            settings[key] = value
        _atomic_write_bytes(self.settings_path, json.dumps(settings, indent=2).encode('utf-8'))
        self._settings = settings

# Global state instance
state_manager = StateManager()
