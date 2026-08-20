
import pandas as pd
from groundhog.general.soilprofile import SoilProfile
from core.plotting_wrappers import log_plot_wrapper
from core.state import state_manager

# 1. Create a profile without 'Soil type' (use 'Stratigraphy' instead)
data = {
    'Depth from [m]': [0.0, 5.0],
    'Depth to [m]': [5.0, 10.0],
    'Stratigraphy': ['SAND', 'CLAY'],
    'UnitWeight [kN_m3]': [18.0, 20.0],
    'WaterTable [-]': [0, 0]
}
df = pd.DataFrame(data)
profile = SoilProfile(df)
# store returns an ID
profile_id = state_manager.store(profile, 'SoilProfile', name='test_profile_logplot')

# 2. Call log_plot_wrapper
args = {
    'soilprofile': profile_id,
    'parameters': 'UnitWeight [kN_m3], WaterTable [-]',
    'soiltypecolumn': 'Stratigraphy'
}

print("Running log_plot_wrapper...")
result = log_plot_wrapper(args)

if 'error' in result:
    print(f"FAILED: {result['error']}")
else:
    print("SUCCESS: Plot generated successfully.")
    print(f"Result keys: {list(result.keys())}")
    # Verify that the original profile columns were NOT renamed in-place
    print(f"Original profile columns: {profile.columns.tolist()}")
    if 'Soil type' in profile.columns and 'Stratigraphy' not in profile.columns:
        print("WARNING: Original profile was modified in-place!")
