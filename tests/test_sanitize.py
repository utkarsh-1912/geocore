
import sys
import os

# Add python-backend to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, '..', 'python-backend')
sys.path.append(backend_dir)


try:
    from core.registry import Registry
except ImportError:
    print("Could not import core.registry.")
    sys.exit(1)

import numpy as np
import pandas as pd
import math
import json

def test():
    print("Testing Registry._sanitize...")
    reg = Registry()
    
    # 1. Numpy Array
    arr = np.array([1.0, 2.0, 3.0])
    res = reg._sanitize(arr)
    print(f"Numpy Array: {res} (Type: {type(res)})")
    
    # 2. Numpy Array with NaN
    nan_arr = np.array([1.0, np.nan, float('inf')])
    res_nan = reg._sanitize(nan_arr)
    print(f"NaN Array: {res_nan}")
    
    # Check JSON serialization
    try:
        json_out = json.dumps(res_nan)
        print(f"JSON Output: {json_out}")
    except ValueError as e:
        print(f"JSON Serialization Failed: {e}")

    # 3. Pandas Series
    ser = pd.Series([1.0, 2.0, np.nan])
    res_ser = reg._sanitize(ser)
    print(f"Pandas Series: {res_ser}")
    
    # 4. Nested Dict with Array and NaN
    nested = {"a": np.array([1, np.nan]), "b": float('nan'), "c": 3.0}
    res_nested = reg._sanitize(nested)
    print(f"Nested Dict: {res_nested}")
    
    print("Test Complete.")

if __name__ == "__main__":
    test()
