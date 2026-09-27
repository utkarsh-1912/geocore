# Author: Utkarsh Gupta
# License: GPL v3

from typing import Dict, Any, List, Optional
import uuid
import os
import json
import threading

class StateManager:
    def __init__(self):
        self._objects_store: Dict[str, Any] = {}
        self._metadata_store: Dict[str, Dict[str, Any]] = {}
        self.filename = "saved_objects.json"
        # Saved objects are restored on first access rather than at import:
        # rebuilding a SoilProfile imports groundhog/scipy, which would slow
        # backend start-up. main.py pre-loads them in the background.
        self._loaded = False
        self._load_lock = threading.Lock()

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

    def _load_from_disk(self):
        if not os.path.exists(self.filename):
            return
        
        try:
            with open(self.filename, 'r') as f:
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
                    to_save.append({
                        "id": obj_id,
                        "type": meta["type"],
                        "name": meta["name"],
                        "timestamp": meta["timestamp"],
                        "data": data
                    })
        
        try:
            with open(self.filename, 'w') as f:
                json.dump(to_save, f, indent=2)
        except Exception as e:
            print(f"Failed to save objects to disk: {e}")

    def store(self, obj: Any, type_name: str, name: Optional[str] = None) -> str:
        """Stores an object and returns its ID."""
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

# Global state instance
state_manager = StateManager()
