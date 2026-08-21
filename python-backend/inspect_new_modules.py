# Author: Utkarsh Gupta
# License: GPL v3


import inspect
import json
import pkgutil
import re
import groundhog.siteinvestigation as si
import numpy as np

def get_js_type(val):
    if isinstance(val, bool):
        return 'boolean'
    if isinstance(val, (int, float)):
        return 'float'
    if isinstance(val, str):
        return 'string'
    if isinstance(val, list):
        return 'list'
    if isinstance(val, dict):
        return 'json'
    return 'string'

def serialize_default(val):
    if val is inspect.Parameter.empty:
        return None
    if val is None:
        return 'null'
    if isinstance(val, bool):
        return 'true' if val else 'false'
    if isinstance(val, (int, float)):
        if np.isnan(val):
            return 'null'
        return str(val)
    if isinstance(val, str):
        clean = val.replace("'", "\\'")
        return f"'{clean}'"
    if isinstance(val, (list, dict)):
        return json.dumps(val)
    return f"'{str(val)}'"

def parse_docstring_params(doc):
    if not doc:
        return {}
    params = {}
    lines = doc.split('\n')
    for line in lines:
        line = line.strip()
        match = re.search(r':param\s+(\w+):\s+(.*)', line)
        if match:
            name = match.group(1)
            desc = match.group(2)
            params[name] = desc
    return params

def convert_rst_to_html(doc):
    if not doc:
        return ""
    
    # Basic RST to HTML conversion
    html = doc
    
    # Escape HTML special chars first? No, we trust the source.
    
    # 1. Math: :math:`...` -> <span class="math">...</span>
    html = re.sub(r':math:`([^`]+)`', r'<span class="math-inline">\1</span>', html)
    
    # 2. Block math: .. math:: -> <div class="math-block">
    html = re.sub(r'\.\.\s+math::', r'<div class="math-block">', html)
    
    # 3. Parameters list -> <ul>
    # This is hard to parse perfectly without a real parser, but we can try to wrap lines starting with :param
    # For now, let's just make sure newlines are preserved
    html = html.replace('\n', '<br/>')
    
    # 4. Images: .. figure:: images/name.png -> <img src="...">
    # We need to map `images/` to our assets folder if possible, or just ignore.
    # Groundhog images are local. We might not be able to show them easily unless we copy them.
    # Let's just strip the directive for now or try to point to a placeholder.
    html = re.sub(r'\.\.\s+figure::\s+images/(\S+)', r'<img src="/assets/groundhog_images/\1" alt="Figure" />', html)
    
    return html

info = {}

prefix = si.__name__ + "."
print(f"Scanning path: {si.__path__}")

for importer, modname, ispkg in pkgutil.walk_packages(si.__path__, prefix):
    try:
        mod = __import__(modname, fromlist="dummy")
        simple_name = modname.replace('groundhog.siteinvestigation.', '')
        info[simple_name] = []
        
        for name, obj in inspect.getmembers(mod):
            if inspect.isfunction(obj) or inspect.isclass(obj):
                if obj.__module__ == mod.__name__:
                    if name.startswith('_'):
                        continue

                    func_args = []
                    descriptions = {}
                    full_doc = ""
                    
                    try:
                        if obj.__doc__:
                            descriptions = parse_docstring_params(obj.__doc__)
                            full_doc = convert_rst_to_html(obj.__doc__)
                            
                        sig = inspect.signature(obj)
                        for param_name, param in sig.parameters.items():
                            if param_name in ['self', 'kwargs', 'args']:
                                continue
                            
                            default_val = param.default
                            arg_type = 'float'
                            if default_val is not inspect.Parameter.empty:
                                arg_type = get_js_type(default_val)
                            else:
                                if 'symbol' in param_name or 'type' in param_name or 'name' in param_name:
                                    arg_type = 'string'
                            
                            desc = descriptions.get(param_name, '')
                            
                            unit = ""
                            unit_match = re.search(r'\[([^\]]+)\]', desc)
                            if unit_match:
                                unit = unit_match.group(1)
                                if ':math:' in unit:
                                     unit = unit.replace(':math:`', '').replace('`', '')
                            
                            # Convert description to HTML for rich rendering
                            clean_desc = convert_rst_to_html(desc)

                            func_args.append({
                                'name': param_name,
                                'type': arg_type,
                                'default': serialize_default(default_val),
                                'required': default_val is inspect.Parameter.empty,
                                'label': param_name.replace('_', ' ').title(),
                                'description': clean_desc, # Rich HTML description
                                'unit': unit
                            })

                    except Exception as e:
                        print(f"Error for {name}: {e}")
                        continue

                    info[simple_name].append({
                        'name': name,
                        'description': full_doc, # Captured full doc here
                        'args': func_args
                    })
    except Exception as e:
        print(f"Error importing {modname}: {e}")

with open('module_info_structured.json', 'w', encoding='utf-8') as f:
    json.dump(info, f, indent=2)
print("Done")
