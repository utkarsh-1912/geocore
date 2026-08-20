
import sys
import os
import json
import base64
import pandas as pd
import numpy as np

# Add python-backend to sys.path
# This assumes we are running from the project root (Geocore)
sys.path.append(os.path.join(os.getcwd(), 'python-backend'))

from core.registry import Registry
from core.state import state_manager

def test_registry_plotting():
    print("Initializing Registry...")
    try:
        registry = Registry()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 1. Create SoilProfile with raw headers (no brackets)
    print("\n--- Testing SoilProfile Creation with Header Normalization ---")
    raw_data = [
        {"Depth from [m]": 0.0, "Depth to [m]": 1.0, "UndrainedCohesion_kPa": 10.0, "Type": "Sand", "UnitWeight_kN_m3": 18},
        {"Depth from [m]": 1.0, "Depth to [m]": 2.0, "UndrainedCohesion_kPa": 20.0, "Type": "Clay", "UnitWeight_kN_m3": 19},
        {"Depth from [m]": 2.0, "Depth to [m]": 3.0, "UndrainedCohesion_kPa": 30.0, "Type": "Sand", "UnitWeight_kN_m3": 20},
    ]
    
    # Simulate API call args
    args_create = {
        'data': None,
        'raw_data': raw_data,
        'nan_strategy': 'fill',
        'name': 'TestProfile',
        'depth_from_col': 'Depth from [m]',
        'depth_to_col': 'Depth to [m]'
    }
    
    # Pass 'groundhog.general.soilprofile' as module_id (ignored by special case handler but good practice)
    result_create = registry.execute_function('groundhog.general.soilprofile', 'SoilProfile', args_create)
    
    if isinstance(result_create, dict) and result_create.get('error'):
        print("Error creating SoilProfile:", result_create['error'])
        sys.exit(1)
        
    profile_id = result_create['id']
    print(f"SoilProfile created with ID: {profile_id}")
    print("Columns:", result_create['columns'])
    
    # Verify normalization
    expected_col = "UndrainedCohesion [kPa]"
    if expected_col in result_create['columns']:
        print(f"SUCCESS: 'UndrainedCohesion_kPa' was normalized to '{expected_col}'")
    else:
        print(f"FAILURE: 'UndrainedCohesion_kPa' was NOT normalized. Columns: {result_create['columns']}")
    
    # 2. Test LogPlotMatplotlib
    print("\n--- Testing LogPlotMatplotlib ---")
    # Helper accepts comma separated string
    # We use the RENAMED column here, or we can test if the fallback works (by passing the old name)
    # Let's test the fallback!
    params_mpl_old = "UndrainedCohesion_kPa" # Should fallback to "UndrainedCohesion [kPa]"
    args_mpl = {
        'soilprofile': profile_id,
        'parameters': params_mpl_old
    }
    
    print(f"Requesting LogPlotMatplotlib with param: '{params_mpl_old}'")
    result_mpl = registry.execute_function('groundhog.general.plotting', 'LogPlotMatplotlib', args_mpl)
    
    if result_mpl.get('error'):
        print("Error in LogPlotMatplotlib:", result_mpl['error'])
    else:
        print("LogPlotMatplotlib returned success.")
        print("Type:", result_mpl.get('type'))
        if result_mpl.get('data'):
            print("Image data length:", len(result_mpl['data']))
            # Decode to check if valid
            try:
                base64.b64decode(result_mpl['data'])
                print("Image data is valid base64.")
            except:
                print("Image data IS NOT valid base64.")

if __name__ == "__main__":
    test_registry_plotting()
