# Author: Utkarsh Gupta
# License: GPL v3

from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from .registry import registry
import shutil
import os
import tempfile
import json
import threading

# The endpoints below are plain `def` so FastAPI runs them on its thread pool: a Groundhog
# calculation, plot or file parse must never run on the event loop, where it stalls every
# other request (health checks, GeoAI streaming) and the app appears frozen. Calculations
# stay one at a time, as they were while they ran on the event loop, because matplotlib's
# pyplot and the saved-object store are not thread-safe.
_execute_lock = threading.Lock()

def create_dynamic_router():
    router = APIRouter()

    @router.post("/execute")
    def execute_module_function(request: dict):
        module_id = request.get("moduleId")
        function_id = request.get("functionId")
        args = request.get("args", {})
        
        if not function_id:
             raise HTTPException(status_code=400, detail="Function ID is required")
             
        # Execute via registry (it waits for the start-up warm-up itself)
        with _execute_lock:
            result = registry.execute_function(module_id, function_id, args)
        
        if "error" in result:
             if result.get("status") == "ValidationError":
                 raise HTTPException(status_code=422, detail=result)
             raise HTTPException(status_code=500, detail=result["error"])

        from core.calculation_history import record_calculation
        record_calculation(function_id, args, result)

        return result

    @router.get("/calculation-history")
    def get_calculation_history(limit: int = 50):
        from core.calculation_history import list_calculation_history
        return {"history": list_calculation_history(limit)}

    @router.delete("/calculation-history")
    def delete_calculation_history():
        from core.calculation_history import clear_calculation_history
        clear_calculation_history()
        return {"status": "cleared"}

    @router.get("/objects/{type_name}")
    def list_objects(type_name: str):
        from .state import state_manager
        return {"objects": state_manager.list_by_type(type_name)}

    @router.get("/objects/{type_name}/{obj_id}")
    def get_object_details(type_name: str, obj_id: str):
        from .state import state_manager
        obj = state_manager.get(obj_id)
        if obj is None:
            raise HTTPException(status_code=404, detail="Object not found")
        
        details = {}
        # If it's a pandas DataFrame or similar (SoilProfile)
        if hasattr(obj, 'columns'):
            try:
                details['columns'] = list(obj.columns)
                # Return data for viewing
                if hasattr(obj, 'to_dict'):
                    details['data'] = obj.to_dict(orient='records')
            except:
                pass
        
        return details

    @router.post("/objects/upload")
    def upload_object(type_name: str, file: UploadFile = File(...), data_kind: Optional[str] = None):
        """``data_kind`` (``cpt`` or ``soil_profile``) records what the uploaded table holds."""
        from .state import DATA_KINDS
        if type_name not in ["SoilProfile", "AGSConverter"]:
            raise HTTPException(status_code=400, detail="Only SoilProfile and AGSConverter upload is currently supported")
        if data_kind and data_kind not in DATA_KINDS:
            raise HTTPException(status_code=422,
                                detail=f"Unknown data_kind '{data_kind}' (expected one of: {', '.join(DATA_KINDS)}).")

        try:
            # Create temp file
            suffix = os.path.splitext(file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(file.file, tmp)
                tmp_path = tmp.name
            
            # Execute SoilProfile creation through registry
            # We treat it as a function execution
            with _execute_lock:
                result = registry.execute_function("general", "SoilProfile",
                                                   {"data": tmp_path, "name": file.filename, "data_kind": data_kind})
            
            # Clean up temp file (registry loads it into memory/df)
            os.unlink(tmp_path)
            
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/objects/create")
    def create_object(type_name: str, data: dict = Body(...)):
        if type_name != "SoilProfile":
             raise HTTPException(status_code=400, detail="Only SoilProfile creation is currently supported")
        
        try:
            # Execute SoilProfile creation through registry
            # data should contain 'raw_data' (list of dicts) or conform to what registry expects
            # For consistency, we expect the frontend to send { "raw_data": [...] } or similar args
            with _execute_lock:
                result = registry.execute_function("general", "SoilProfile", data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        if result.get("status") == "ValidationError":
            raise HTTPException(status_code=422, detail=result)
        return result

    @router.get("/schema/overrides")
    def get_overrides():
        from .schema_manager import schema_manager
        return schema_manager.get_overrides()

    @router.post("/schema/override")
    def save_override(data: dict = Body(...)):
        from .schema_manager import schema_manager
        # data: { functionId, fieldName, metadata }
        func_id = data.get("functionId")
        field_name = data.get("fieldName")
        metadata = data.get("metadata")
        
        if not func_id or not field_name:
             raise HTTPException(status_code=400, detail="Missing funcId or fieldName")

        return schema_manager.save_override(func_id, field_name, metadata)

    @router.post("/assets/upload")
    def upload_asset_file(file: UploadFile = File(...)):
        from .schema_manager import schema_manager
        try:
            # Save file
            file_path = schema_manager.upload_asset(file, file.filename)
            return {"url": file_path}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete("/objects/{type_name}/{obj_id}")
    def delete_object(type_name: str, obj_id: str):
        from .state import state_manager
        state_manager.delete(obj_id)
        return {"status": "success", "id": obj_id}

    return router
