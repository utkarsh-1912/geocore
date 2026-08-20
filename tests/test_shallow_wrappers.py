
import sys
import os
import json
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python-backend'))

from core.wrappers import shallow_foundation_capacity_undrained_wrapper, shallow_foundation_capacity_drained_wrapper

def test_undrained_wrapper():
    print("Testing Undrained Wrapper...")
    args = {
        'foundation_shape': 'rectangle',
        'width': 2.0,
        'length': 3.0,
        'unit_weight': 18.0,
        'su_base': 50.0,
        'base_depth': 1.0,
        'factor_sliding': 1.5,
        'factor_bearing': 2.0
    }
    
    result = shallow_foundation_capacity_undrained_wrapper(args)
    
    if "error" in result:
        print(f"FAILED: {result['error']}")
        return False
        
    print("Success!")
    print("Keys returned:", result.keys())
    if "results" in result:
        print("Results:", json.dumps(result["results"], indent=2))
    return True

def test_drained_wrapper():
    print("\nTesting Drained Wrapper...")
    args = {
        'foundation_shape': 'circle',
        'width': 2.5, # Diameter
        'effective_unit_weight': 10.0,
        'friction_angle': 30.0,
        'effective_stress_base': 50.0,
        'vertical_load': 1000.0,
        'base_depth': 0.5,
        'factor_sliding': 1.5,
        'factor_bearing': 2.0
    }
    
    result = shallow_foundation_capacity_drained_wrapper(args)
    
    if "error" in result:
        print(f"FAILED: {result['error']}")
        return False
        
    print("Success!")
    print("Keys returned:", result.keys())
    if "results" in result:
        print("Results:", json.dumps(result["results"], indent=2))
    return True

if __name__ == "__main__":
    u_ok = test_undrained_wrapper()
    d_ok = test_drained_wrapper()
    
    if u_ok and d_ok:
        print("\nAll wrapper tests passed.")
        sys.exit(0)
    else:
        print("\nSome tests failed.")
        sys.exit(1)
