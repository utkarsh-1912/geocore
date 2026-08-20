
import sys
import os
import json
import numpy as np
import warnings

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python-backend'))

from core.wrappers import shallow_foundation_capacity_undrained_wrapper

def test_circle_area():
    print("Testing Circular Foundation Area...")
    
    width = 2.0 # Diameter
    radius = width / 2.0
    expected_area = np.pi * radius**2
    print(f"Diameter: {width}, Radius: {radius}")
    print(f"Expected Full Area: {expected_area}")

    args = {
        'foundation_shape': 'circle',
        'width': width,
        'length': np.nan,
        'unit_weight': 18.0,
        'su_base': 50.0,
        'base_depth': 0.0,
        'eccentricity_width': 0.0,
        'eccentricity_length': 0.0
    }
    
    result = shallow_foundation_capacity_undrained_wrapper(args)
    
    if "results" in result:
        res = result['results']
        print(f"Returned Effective Area: {res.get('Effective Area [m2]')}")
        print(f"Returned Full Area: {res.get('Full Area [m2]')}")
        print(f"Returned Eccentricity: {res.get('Eccentricity [m]')}")
        
        eff_area = res.get('Effective Area [m2]')
        full_area = res.get('Full Area [m2]')
        
        if eff_area is not None:
            if abs(eff_area - expected_area) < 1e-4:
                print("Effective Area matches expected full area (eccentricity=0).")
            else:
                print("Effective Area DOES NOT match expected full area!")
                
        if full_area is not None:
             if abs(full_area - expected_area) < 1e-4:
                 print("Full Area matches expected full area.")
             else:
                 print("Full Area DOES NOT match expected full area!")
    else:
        print("No results returned.")
        print(result)

    # Test with eccentricity
    ecc = 0.1
    args['eccentricity_width'] = ecc
    result_ecc = shallow_foundation_capacity_undrained_wrapper(args)
    
    output = {
        "e=0": result['results'] if "results" in result else result,
        "e=0.1": result_ecc['results'] if "results" in result_ecc else result_ecc
    }
    
    with open('circle_results.json', 'w') as f:
        json.dump(_sanitize(output), f, indent=2)

def _sanitize(obj):
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    return obj
    
if __name__ == "__main__":
    test_circle_area()
