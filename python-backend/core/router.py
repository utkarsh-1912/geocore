# Author: Utkarsh Gupta
# License: GPL v2

from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from .registry import registry
import shutil
import os
import tempfile
import json

def create_dynamic_router():
    router = APIRouter()

    @router.post("/execute")
    async def execute_module_function(request: dict):
        module_id = request.get("moduleId")
        function_id = request.get("functionId")
        args = request.get("args", {})
        
        if not function_id:
             raise HTTPException(status_code=400, detail="Function ID is required")
             
        # Execute via registry
        result = registry.execute_function(module_id, function_id, args)
        
        if "error" in result:
             if result.get("status") == "ValidationError":
                 raise HTTPException(status_code=422, detail=result)
             raise HTTPException(status_code=500, detail=result["error"])
        
        return result

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
    async def upload_object(type_name: str, file: UploadFile = File(...)):
        if type_name not in ["SoilProfile", "AGSConverter"]:
            raise HTTPException(status_code=400, detail="Only SoilProfile and AGSConverter upload is currently supported")
        
        try:
            # Create temp file
            suffix = os.path.splitext(file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(file.file, tmp)
                tmp_path = tmp.name
            
            # Execute SoilProfile creation through registry
            # We treat it as a function execution
            result = registry.execute_function("general", "SoilProfile", {"data": tmp_path, "name": file.filename})
            
            # Clean up temp file (registry loads it into memory/df)
            os.unlink(tmp_path)
            
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/objects/create")
    async def create_object(type_name: str, data: dict = Body(...)):
        if type_name != "SoilProfile":
             raise HTTPException(status_code=400, detail="Only SoilProfile creation is currently supported")
        
        try:
            # Execute SoilProfile creation through registry
            # data should contain 'raw_data' (list of dicts) or conform to what registry expects
            # For consistency, we expect the frontend to send { "raw_data": [...] } or similar args
            result = registry.execute_function("general", "SoilProfile", data)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/schema/overrides")
    def get_overrides():
        from .schema_manager import schema_manager
        return schema_manager.get_overrides()

    @router.post("/schema/override")
    async def save_override(data: dict = Body(...)):
        from .schema_manager import schema_manager
        # data: { functionId, fieldName, metadata }
        func_id = data.get("functionId")
        field_name = data.get("fieldName")
        metadata = data.get("metadata")
        
        if not func_id or not field_name:
             raise HTTPException(status_code=400, detail="Missing funcId or fieldName")

        return schema_manager.save_override(func_id, field_name, metadata)

    @router.post("/assets/upload")
    async def upload_asset_file(file: UploadFile = File(...)):
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
