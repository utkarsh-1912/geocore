
import sys
import os
import pandas as pd
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'python-backend'))
# Add venv site-packages if needed (usually handled by python executable)

try:
    from groundhog.general.plotting import plot_with_log
    from groundhog.general.soilprofile import SoilProfile
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def test_direct():
    print("Testing plot_with_log directly...")
    
    # Setup Profile
    df = pd.DataFrame({
        'Soil type': ['Sand', 'Clay'],
        'Depth from [m]': [0, 5],
        'Depth to [m]': [5, 10],
        'Unit weight [kN/m3]': [18, 19]
    })
    profile = SoilProfile(df)
    
    # Test Params
    x = [[[1, 2, 3, 4, 5]]] # 1 Panel, 1 Trace, Array data
    z = [[[1, 2, 3, 4, 5]]]
    names = [['Test Trace']] # 1 Panel, 1 Trace Name
    
    # Default colors (needs patching usually, but groundhog has defaults)
    fillcolordict = {'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green', 'ROCK': 'grey'}
    # Helper to patch colors (similar to wrapper)
    fillcolordict['Sand'] = 'yellow'
    fillcolordict['Clay'] = 'brown'

    try:
        fig = plot_with_log(
            x=x,
            z=z,
            names=names,
            soildata=profile,
            depth_from_key='Depth from [m]',
            depth_to_key='Depth to [m]',
            fillcolordict=fillcolordict,
            showfig=False
        )
        print("Success! Figure generated.")
        
        # Verify traces
        # Plotly figure structure
        # fig.data should contain traces
        import plotly.io
        json_str = plotly.io.to_json(fig)
        print("JSON generated.")
        
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct()
