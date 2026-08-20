# Author: Utkarsh Gupta
# License: GPL v2


import json
import os

# Load module info
with open('module_info_structured.json', 'r', encoding='utf-8') as f:
    module_data = json.load(f)

schemas = {}

for module_name, functions in module_data.items():
    for func in functions:
        func_name = func['name']
        args = func['args']
        doc = func.get('description', '') # Get full docs

        # Construct JSON Schema
        schema = {
            "type": "object",
            "properties": {},
            "required": [],
            "documentation": doc # Add documentation field
        }

        for arg in args:
            param_name = arg['name']
            param_type = arg['type']
            
            # Map Python types to JSON Schema types
            json_type = "string"
            if param_type == 'float':
                json_type = "number"
            elif param_type == 'boolean':
                json_type = "boolean"
            elif param_type == 'list':
                json_type = "array"
            
            prop = {
                "type": json_type,
                "title": arg['label'],
                "description": arg['description'],
                "unit": arg['unit'],
                "default": arg['default']
            }
            
            # Special handling for standard objects
            if param_name == 'soilprofile':
                 prop['objectType'] = 'SoilProfile'
                 prop['type'] = 'object_select' # Custom UI type
            
            schema["properties"][param_name] = prop
            
            if arg['required']:
                schema["required"].append(param_name)

        schemas[func_name] = schema

# Output to JS file
output_path = r"C:\Users\utkar\Downloads\Geocore\electron-app\src\features\calculations\schema_definitions.js"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("export const schemas = " + json.dumps(schemas, indent=4) + ";")

print(f"Schemas generated at {output_path}")
