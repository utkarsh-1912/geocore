
import sys
import os
import json
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python-backend'))

from core.wrappers import shallow_foundation_capacity_undrained_wrapper, shallow_foundation_capacity_drained_wrapper

def test_undrained_warnings():
    print("Testing Undrained Wrapper Warnings...")
    # Inputs that should trigger validation warnings (length < 0)
    args = {
        'foundation_shape': 'rectangle',
        'width': 2.0,
        'length': -1.0, # Invalid length
        'unit_weight': 25.0, # High unit weight
        'su_base': 50.0,
        'base_depth': 1.0,
        'factor_sliding': 1.5,
        'factor_bearing': 2.0
    }
    
    result = shallow_foundation_capacity_undrained_wrapper(args)
    
    print("Result Keys:", result.keys())
    if "warnings" in result:
        print("Warnings Captured:")
        for w in result['warnings']:
            print(f" - {w}")
    else:
        print("No warnings captured.")
        
    if "error" in result:
        print(f"Error: {result['error']}")
    
    # Check if results are sanitized (no NaNs)
    print("Sanitized Results Sample:", json.dumps(result.get("results"), indent=2))
    return True

def test_drained_warnings():
    print("\nTesting Drained Wrapper Warnings...")
    # Inputs that trigger warnings
    args = {
        'foundation_shape': 'rectangle',
        'width': 2.5,
        'length': 2.5,
        'effective_unit_weight': 20.0, # Too high (>12)
        'friction_angle': 15.0, # Too low (<20)
        'effective_stress_base': 50.0,
        'vertical_load': 1000.0
    }
    
    result = shallow_foundation_capacity_drained_wrapper(args)
    
    print("Result Keys:", result.keys())
    if "warnings" in result:
        print("Warnings Captured:")
        for w in result['warnings']:
            print(f" - {w}")
    else:
        print("No warnings captured.")

    if "error" in result:
        print(f"Error: {result['error']}")

    print("Sanitized Results Sample:", json.dumps(result.get("results"), indent=2))
    return True

if __name__ == "__main__":
    test_undrained_warnings()
    test_drained_warnings()
