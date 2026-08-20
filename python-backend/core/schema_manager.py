# Author: Utkarsh Gupta
# License: GPL v2


import json
import os
import shutil
import logging

logger = logging.getLogger("groundhog-backend")

class SchemaManager:
    def __init__(self, overrides_path="schema_overrides.json", assets_dir="assets/schema_images"):
        self.overrides_path = overrides_path
        self.assets_dir = assets_dir
        self._ensure_paths()
        self.overrides = self._load_overrides()

    def _ensure_paths(self):
        if not os.path.exists(self.assets_dir):
            os.makedirs(self.assets_dir)
        if not os.path.exists(self.overrides_path):
            with open(self.overrides_path, 'w') as f:
                json.dump({}, f)

    def _load_overrides(self):
        try:
            with open(self.overrides_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load schema overrides: {e}")
            return {}

    def _save_overrides(self):
        try:
            with open(self.overrides_path, 'w') as f:
                json.dump(self.overrides, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save schema overrides: {e}")

    def get_overrides(self):
        return self.overrides

    def save_override(self, function_id, field_name, metadata):
        """
        metadata: { label, description, unit, placeholder, imageUrl, validationRegex }
        """
        if function_id not in self.overrides:
            self.overrides[function_id] = {}
        
        # Merge or overwrite field metadata
        # structure: func_id -> { field_name: { ...metadata } }
        # field_name can be '_page_docs' for function-level documentation
        self.overrides[function_id][field_name] = metadata
        self._save_overrides()
        return self.overrides

    def upload_asset(self, file_obj, filename):
        try:
            target_path = os.path.join(self.assets_dir, filename)
            with open(target_path, "wb") as buffer:
                shutil.copyfileobj(file_obj.file, buffer)
            
            # Return relative path for frontend to access via static mount
            return f"/assets/schema_images/{filename}"
        except Exception as e:
            logger.error(f"Failed to upload asset: {e}")
            raise e

# Global instance
schema_manager = SchemaManager()
