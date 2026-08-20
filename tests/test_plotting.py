
import sys
import os
import json
import pandas as pd
import numpy as np

# Add backend to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'python-backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

print(f"Added path: {backend_path}")
print(f"Files in backend: {os.listdir(backend_path)}")

try:
    from core.state import state_manager
    from core.registry import Registry
    from core.plotting_wrappers import plot_with_log_wrapper
    from groundhog.general.soilprofile import SoilProfile
    print("Imports successful!")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def test_plot_with_log():
    print("Testing plot_with_log wrapper...")
    
    # 1. Create a dummy Soil Profile
    df = pd.DataFrame({
        'Soil type': ['Sand', 'Clay'],
        'Depth from [m]': [0, 5],
        'Depth to [m]': [5, 10],
        'Unit weight [kN/m3]': [18, 19]
    })
    
    profile = SoilProfile(df)
    profile_id = state_manager.store(profile, type_name='soil_profile')
    print(f"Created SoilProfile with ID: {profile_id}")
    
    # 2. Call plot_with_log via Registry
    registry = Registry()
    
    # Case A: Simple Plot (just profile)
    print("\n[Case A] Simple Profile Plot")
    args_a = {
        'soilprofile': profile_id
    }
    # Using 'general' as module_id, though registry likely ignores it for special cases
    result_a = registry.execute_function('general', 'plot_with_log', args_a)
    
    if "error" in result_a:
        print("Error in Case A:", result_a['error'])
    else:
        print("Success Case A! keys:", result_a.keys())
        if 'data' in result_a and 'layout' in result_a:
             print("Verified Plotly structure.")

    # Case B: Plotting Traces
    print("\n[Case B] Plotting with Traces")
    x = [1, 2, 3, 4, 5]
    z = [1, 2, 3, 4, 5]
    
    args_b = {
        'soilprofile': profile_id,
        'x': x,
        'z': z,
        'names': 'Test Trace'
    }
    
    result_b = registry.execute_function('general', 'plot_with_log', args_b)
    
    if "error" in result_b:
        print("Error in Case B:", result_b['error'])
    else:
        print("Success Case B! Returned data length:", len(result_b.get('data', [])))
        # Expect at least grid lines + traces. 
        # Groundhog adds traces for the log and the data.
        
if __name__ == "__main__":
    test_plot_with_log()
