
import pandas as pd
import numpy as np
import sys
import os

# Mock State Manager
sys.path.append(os.getcwd())
try:
    from groundhog.general.soilprofile import SoilProfile
    import groundhog.general.plotting as plotting
except ImportError:
    print("Groundhog not found")
    sys.exit(1)

def reproduce():
    print("--- Reproducing SoilProfile Numeric detection ---")
    
    # Simulate data with mixed types (e.g. from CSV with empty strings or mostly numbers)
    raw_data = [
        {"Depth from [m]": 0.0, "Depth to [m]": 1.0, "UndrainedCohesion_kPa": 10.5, "Type": "Sand", "UnitWeight_kN_m3": 18},
        {"Depth from [m]": 1.0, "Depth to [m]": 2.0, "UndrainedCohesion_kPa": 20.0, "Type": "Clay", "UnitWeight_kN_m3": 19},
        {"Depth from [m]": 2.0, "Depth to [m]": 3.0, "UndrainedCohesion_kPa": "30.5", "Type": "Sand", "UnitWeight_kN_m3": "20"}, # String number
        {"Depth from [m]": 3.0, "Depth to [m]": 4.0, "UndrainedCohesion_kPa": 40, "Type": "Rock", "UnitWeight_kN_m3": 22},
        {"Depth from [m]": 4.0, "Depth to [m]": 5.0, "UndrainedCohesion_kPa": None, "Type": "Rock", "UnitWeight_kN_m3": None},   # None
    ]
    
    df = pd.DataFrame(raw_data)
    print("Original Dtypes:")
    print(df.dtypes)
    
    # Logic from registry.py
    for col in df.columns:
        numeric_col = pd.to_numeric(df[col], errors='coerce')
        if numeric_col.notna().any():
            df[col] = numeric_col
            print(f"Converted {col} to numeric")
        else:
            print(f"Skipped {col} (not numeric)")

    print("\nFinal Dtypes:")
    print(df.dtypes)
    
    profile = SoilProfile(df)
    try:
        print("\nNumerical Parameters detected by SoilProfile:")
        print(profile.numerical_soil_parameters())
    except Exception as e:
        print(f"Error getting parameters: {e}")

    try:
        print("\nChecking for LogPlotMatplotlib:")
        import groundhog.general.plotting as plotting
        if hasattr(plotting, 'LogPlotMatplotlib'):
            print("Found LogPlotMatplotlib in plotting")
        else:
            print("LogPlotMatplotlib NOT found in plotting")
            
        import groundhog
        if hasattr(groundhog, 'LogPlotMatplotlib'):
            print("Found LogPlotMatplotlib in groundhog root")
    except:
        pass

if __name__ == "__main__":
    reproduce()
