# Author: Utkarsh Gupta
# License: GPL v2


import pandas as pd
import numpy as np
import warnings
import json
import plotly

try:
    from groundhog.shallowfoundations.stressdistribution import stresses_circle
    from groundhog.shallowfoundations.settlement import SettlementCalculation
    from groundhog.general.soilprofile import SoilProfile
    print("Imports successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    exit(1)

# 1. Test Stress Distribution
print("\nTesting stresses_circle...")
try:
    res = stresses_circle(z=2.0, footing_radius=1.5, imposedstress=100.0, poissonsratio=0.3)
    print("stresses_circle result keys:", res.keys())
    # Expecting: 'delta sigma z [kPa]', 'delta sigma r [kPa]'
    if 'delta sigma z [kPa]' in res:
        print(f"Success! Delta sigma z: {res['delta sigma z [kPa]']:.2f}")
    else:
        print("Failed: Unexpected result structure.")
except Exception as e:
    print(f"stresses_circle failed: {e}")

# 2. Test SettlementCalculation logic
print("\nTesting SettlementCalculation...")
try:
    # Create dummy profile
    data = {
        'Depth from [m]': [0, 2, 5],
        'Depth to [m]': [2, 5, 10],
        'Total unit weight [kN/m3]': [18, 19, 20],
        'Cc [-]': [0.1, 0.2, 0.3],
        'Cr [-]': [0.01, 0.02, 0.03],
        'OCR [-]': [1, 1, 1],
        'e0 [-]': [0.5, 0.6, 0.7] # Optional? Check init
    }
    df = pd.DataFrame(data)
    profile = SoilProfile(df)
    
    calc = SettlementCalculation(profile)
    calc.set_foundation(width=2.0, shape='strip')
    calc.create_grid(dz=0.5)
    calc.calculate_initial_state(waterlevel=0.0)
    calc.calculate_foundation_stress(applied_stress=100.0)
    calc.calculate()
    
    print("Calculation finished.")
    
    # Try plotting
    calc.plot_result(showfig=False)
    # The figure is stored in calc.result_plot.fig
    fig = calc.result_plot.fig
    
    plot_json = json.loads(plotly.io.to_json(fig))
    print("Plot generated successfully.")
    print("Plot Data contains:", len(plot_json['data']), "traces")

except Exception as e:
    print(f"SettlementCalculation failed: {e}")
