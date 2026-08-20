# Author: Utkarsh Gupta
# License: GPL v2


import sys
import os
import json

# Add the project directory to sys.path
sys.path.append(os.getcwd())

from core.registry import Registry

registry = Registry()

def test_func(name, args):
    print(f"\n--- Testing {name} ---")
    try:
        result = registry.execute_function('labtesting', name, args)
        if 'error' in result:
            print(f"Error returned: {result['error']}")
        else:
            print("Success!")
            # Print a snippet of data
            if 'data' in result:
                print(f"Data keys: {list(result.keys())}")
            else:
                print(f"Result keys: {list(result.keys())}")
    except Exception as e:
        import traceback
        print(f"Exception during execution: {e}")
        traceback.print_exc()

# 1. Test undercompaction
test_func('undercompaction_cohesionless_ladd', {
    'sample_height': 0.1,
    'no_layers': 5,
    'undercompaction_deepest': 5,
    'undercompaction_shallowest': 0
})

# 2. Test PlasticityChart
test_func('PlasticityChart', {
    'll': [10, 20, 30],
    'pi': [5, 10, 15],
    'name': 'Test Sample'
})

# 3. Test roottimemethod (interactive required case)
test_func('roottimemethod', {
    'times': [0, 1, 4, 9, 16],
    'settlements': [0, 1, 2, 3, 4],
    'drainagelength': 0.01
})
