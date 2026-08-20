
import sys
import os
import json
import numpy as np
import warnings

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python-backend'))

from core.wrappers import effectivearea_circle_wrapper

def test_effective_area_conflict():
    print("Testing Effective Area Circle Wrapper...")
    
    # User inputs: 
    # Radius=10, V=120, M=3, e=2
    # Expectation: Wrapper should prioritize 'e' if set, or handle conflicts gracefully.
    
    args = {
        'foundation_radius': 10.0,
        'vertical_load': 120.0,
        'overturning_moment': 3.0,
        'eccentricity': 2.0
    }
    
    print("Running with conflicting arguments (M, V, e provided)...")
    result = effectivearea_circle_wrapper(args)
    print("Result:", result)
    
    if "error" in result:
        print("Wrapper returned error:", result['error'])
    else:
        print("Wrapper successfully handled conflict!")

    # Test with e only
    print("\nRunning with only eccentricity...")
    args_e = args.copy()
    args_e['vertical_load'] = ''
    args_e['overturning_moment'] = ''
    result_e = effectivearea_circle_wrapper(args_e)
    print("Result e only:", result_e)
    
    # Test with M, V only (e empty)
    print("\nRunning with M, V only...")
    args_mv = args.copy()
    args_mv['eccentricity'] = ''
    result_mv = effectivearea_circle_wrapper(args_mv)
    print("Result M, V only:", result_mv)

if __name__ == "__main__":
    test_effective_area_conflict()
