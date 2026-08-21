"""
Generate complete Parameter Inventory for all Groundhog & GeoCore functions.
Exports to docs/PARAMETER_INVENTORY.csv and python-backend/core/geoai/parameter_inventory.json
"""
import os
import sys
import json
import csv
import inspect
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'python-backend')))

from core.registry import Registry

# Load module_info_structured.json if available
meta_path = os.path.join(os.path.dirname(__file__), 'python-backend', 'module_info_structured.json')
structured_meta = {}
if os.path.exists(meta_path):
    with open(meta_path, 'r', encoding='utf-8') as f:
        structured_meta = json.load(f)

# Flatten structured meta by function name
func_meta_lookup = {}
for mod_name, mod_funcs in structured_meta.items():
    for f_info in mod_funcs:
        fn_name = f_info.get('name')
        if fn_name:
            func_meta_lookup[fn_name] = {
                'module': mod_name,
                'description': f_info.get('description', ''),
                'args': {arg['name']: arg for arg in f_info.get('args', [])}
            }

def infer_range(param_name, unit, param_type):
    """Infer physical plausible range based on parameter name and unit."""
    name_lower = param_name.lower()
    unit_lower = (unit or '').lower()
    
    if 'phi' in name_lower or 'friction' in name_lower or 'angle' in name_lower or 'delta' in name_lower:
        if 'rad' in unit_lower:
            return (0.0, 1.2)
        return (0.0, 60.0)
    if 'poisson' in name_lower or name_lower in ['nu', 'poissonsratio']:
        return (-1.0, 0.5)
    if name_lower in ['e', 'voidratio', 'void_ratio', 'initial_voidratio']:
        return (0.05, 5.0)
    if 'depth' in name_lower or 'penetration' in name_lower or 'height' in name_lower or 'z' in name_lower or 'radius' in name_lower or 'diameter' in name_lower or 'width' in name_lower or 'length' in name_lower or 'thickness' in name_lower:
        return (0.0, 10000.0)
    if 'unitweight' in name_lower or 'gamma' in name_lower or 'density' in name_lower:
        if 'kn/m3' in unit_lower:
            return (5.0, 30.0)
        if 'kg/m3' in unit_lower or 'g/cm3' in unit_lower:
            return (500.0, 3000.0)
        return (0.0, 50.0)
    if 'pressure' in name_lower or 'stress' in name_lower or 'su' in name_lower or 'cohesion' in name_lower or 'modulus' in name_lower or 'qc' in name_lower:
        return (0.0, 1e8)
    if 'saturation' in name_lower or 'relative_density' in name_lower or 'dr' in name_lower:
        if '%' in unit_lower or 'pct' in unit_lower:
            return (0.0, 100.0)
        return (0.0, 1.0)
    if 'watercontent' in name_lower or 'w' == name_lower:
        return (0.0, 500.0)
    return (None, None)

def extract_unit_from_docstring(docstring, param_name):
    if not docstring:
        return None
    # Look for :param <param_name>: ... [unit]
    pattern = rf':param\s+{re.escape(param_name)}:.*?\[([^\]]+)\]'
    match = re.search(pattern, docstring, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

reg = Registry()
inventory = []

for func_name, func_obj in sorted(reg.function_map.items()):
    module_name = getattr(func_obj, '__module__', 'unknown')
    docstring = inspect.getdoc(func_obj) or ''
    
    # Try signature
    try:
        sig = inspect.signature(func_obj)
        params = sig.parameters
    except Exception:
        params = {}
    
    meta_info = func_meta_lookup.get(func_name, {})
    meta_args = meta_info.get('args', {})
    
    for param_name, param in params.items():
        if param_name in ('self', 'cls', 'args', 'kwargs'):
            continue
            
        m_arg = meta_args.get(param_name, {})
        
        # Determine type
        p_type = 'float'
        if param.annotation != inspect.Parameter.empty:
            p_type = getattr(param.annotation, '__name__', str(param.annotation))
        elif m_arg.get('type'):
            p_type = m_arg.get('type')
        elif param.default is not inspect.Parameter.empty and param.default is not None:
            p_type = type(param.default).__name__
            
        # Determine default
        default_val = None
        is_nullable = False
        if param.default != inspect.Parameter.empty:
            default_val = param.default
            is_nullable = (default_val is None)
        elif 'default' in m_arg:
            default_val = m_arg['default']
            is_nullable = (default_val is None or default_val == 'null')
            
        # Determine unit
        unit = m_arg.get('unit')
        if not unit:
            unit = extract_unit_from_docstring(docstring, param_name)
        if not unit:
            unit = '-'
            
        # Inferred range
        min_val, max_val = infer_range(param_name, unit, p_type)
        
        # Physical description
        desc = m_arg.get('description', '')
        if not desc:
            # Try to extract param line from docstring
            p_match = re.search(rf':param\s+{re.escape(param_name)}:\s*(.+?)(?=\n\s*:(?:param|return|raises)|\Z)', docstring, re.DOTALL)
            if p_match:
                desc = p_match.group(1).strip().replace('\n', ' ')
        if not desc:
            desc = f"{param_name.replace('_', ' ').title()}"
            
        inventory.append({
            'module_id': meta_info.get('module', module_name),
            'function_id': func_name,
            'parameter_name': param_name,
            'python_type': p_type,
            'canonical_unit': unit,
            'display_unit': unit,
            'min_value': min_val if min_val is not None else '',
            'max_value': max_val if max_val is not None else '',
            'is_nullable': is_nullable,
            'default_value': str(default_val) if default_val is not None else '',
            'physical_meaning': desc
        })

# Output JSON
json_path = os.path.join(os.path.dirname(__file__), 'python-backend', 'core', 'geoai', 'parameter_inventory.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(inventory, f, indent=2)

# Output CSV
csv_path = os.path.join(os.path.dirname(__file__), 'docs', 'PARAMETER_INVENTORY.csv')
with open(csv_path, 'w', encoding='utf-8', newline='') as f:
    if inventory:
        fieldnames = list(inventory[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(inventory)

print(f"Successfully generated inventory of {len(inventory)} parameters across {len(reg.function_map)} functions.")
