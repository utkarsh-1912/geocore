# Author: Utkarsh Gupta
# License: GPL v3


import numpy as np
import pandas as pd
import json
import groundhog.general.plotting as plotting
from .state import state_manager

def find_soil_type_column(profile):
    """
    Search for a suitable soil type column in the profile.
    """
    if profile is None: return None
    candidates = ['Soil type', 'SoilType', 'Soil Type', 'USCS', 'Stratigraphy', 'Lithology', 'Description']
    for c in candidates:
        if c in profile.columns:
            return c
    # Fallback to first string column if any
    for col in profile.columns:
        if profile[col].dtype == object or profile[col].dtype == 'string':
             return col
    return None

def plot_with_log_wrapper(args):
    """
    Wrapper for groundhog.general.plotting.plot_with_log
    Handles SoilProfile retrieval and argument formatting.
    """
    # 0. Delegate to LogPlot Wrapper if simple parameters are provided
    if 'parameters' in args and args['parameters']:
        return log_plot_wrapper(args)

    # 1. Retrieve Soil Data
    profile_id = args.get('soilprofile') or args.get('soildata')
    profile = None
    
    if profile_id:
        profile = state_manager.get(profile_id)
    
    if profile is None:
        return {"error": "Plotting Error: A 'SoilProfile' object is required. Please create or select a profile first."}

    # 2. Prepare Arguments
    # plot_with_log expects 'soildata' as a DataFrame
    # And 'x', 'z', 'names' as lists of lists (panels -> traces)
    
    func_args = {
        'soildata': profile,
        'depth_from_key': 'Depth from [m]', 
        'depth_to_key': 'Depth to [m]',
        'showfig': False, # Important: Don't try to show, return object
        'layout': {'height': 800, 'width': 1000} # Default size
    }

    # Map direct arguments
    # If user provides x/z as simple lists, wrap them for a single panel
    x = args.get('x')
    z = args.get('z')
    names = args.get('names')
    
    # helper to check if list contains primitives
    def is_primitive_list(l):
        # Check for numbers or strings
        if not isinstance(l, (list, tuple, np.ndarray)) or len(l) == 0:
            return False
        return isinstance(l[0], (int, float, np.number, str))

    def ensure_list_of_lists(data):
        if data is None: return [[]]
        
        # If it's a scalar (not list/tuple/array), wrap it
        if not isinstance(data, (list, tuple, np.ndarray)):
             return [[data]]

        # If it's a primitive list (1D array of numbers/strings), it's a single trace (or single set of names)
        # Note: If it's [1,2,3], we wrap to [[ [1,2,3] ]] for x/z? 
        # Wait, for x/z, [1,2,3] is an ARRAY for a trace. So it should be [[ [1,2,3] ]].
        # For names, ['A', 'B'] is a list of names for traces. So it should be [[ 'A', 'B' ]].
        
        # This implies x/z and names need different handling? 
        # No, groundhog expects:
        # x: list of lists of ARRAYS. [[ array1, array2 ]]
        # names: list of lists of STRINGS. [[ name1, name2 ]]
        
        # So:
        # If x is [1,2,3] (primitive numbers), it is ONE array. Wrap to [[ [1,2,3] ]].
        # If names is ['A', 'B'] (primitive strings), it is ONE LIST of names. Wrap to [[ 'A', 'B' ]].
        
        if is_primitive_list(data):
             # Check type of first element
             first = data[0]
             if isinstance(first, (int, float, np.number)):
                  # Coordinate array -> Wrap twice to get [[ array ]]
                  return [[data]]
             elif isinstance(first, str):
                  # Names list -> Wrap once to get [[ name1, name2 ]]
                  return [data]
        
        # If list of lists/arrays
        if len(data) > 0:
             # If element is list/array
             if isinstance(data[0], (list, tuple, np.ndarray)):
                  # check depth?
                  # If input is [ [1,2], [3,4] ] (two traces), output should be [[ [1,2], [3,4] ]] ??
                  # Or did user mean 2 panels?
                  # Let's assume 1 panel.
                  return [data]
        
        return data

    if x: func_args['x'] = ensure_list_of_lists(x)
    if z: func_args['z'] = ensure_list_of_lists(z)
    
    # Names handling might be slightly different if single string passed
    if names:
        if isinstance(names, str):
             func_args['names'] = [[names]]
        else:
             func_args['names'] = ensure_list_of_lists(names)

    # Map other optional args
    func_args['fillcolordict'] = args.get('fillcolordict', {'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green', 'ROCK': 'grey'})
    
    # Auto-generate colors for missing soil types
    if profile is not None:
        import random
        # Try to find soil type column
        soil_type_col = args.get('soiltypecolumn') or find_soil_type_column(profile)
        
        # plot_with_log hardcodes 'Soil type' as the key for fillcolordict
        # We MUST ensure the dataframe has this column
        if soil_type_col and soil_type_col != 'Soil type':
            # Create a copy and rename. Re-wrap as SoilProfile to preserve methods
            from groundhog.general.soilprofile import SoilProfile
            profile = SoilProfile(profile.copy())
            profile.rename(columns={soil_type_col: 'Soil type'}, inplace=True)
            soil_type_col = 'Soil type'
            func_args['soildata'] = profile

        if soil_type_col and soil_type_col in profile.columns:
            unique_types = profile[soil_type_col].unique()
            for st in unique_types:
                if st not in func_args['fillcolordict']:
                    # Use hash of string to pick color
                    fallback_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
                    color_idx = abs(hash(str(st))) % len(fallback_colors)
                    func_args['fillcolordict'][st] = fallback_colors[color_idx]
            # Pass the soil type column to plot_with_log
            func_args['soiltypecolumn'] = soil_type_col

    for k in ['logwidth', 'xtitles', 'ztitle', 'xranges', 'zrange', 'modes', 'colors']:
        if k in args and args[k] is not None:
             func_args[k] = args[k]

    # Enforce list lengths for per-panel arguments
    if 'x' in func_args and isinstance(func_args['x'], list):
        num_panels = len(func_args['x'])
        
        # XTITLES is required by groundhog to have length equal to num_panels
        if 'xtitles' not in func_args:
            func_args['xtitles'] = [''] * num_panels
        elif len(func_args['xtitles']) < num_panels:
            func_args['xtitles'].extend([''] * (num_panels - len(func_args['xtitles'])))
            
        # Optional lists that might crash if short
        for list_key in ['xranges', 'dticks']:
            if list_key in func_args and func_args[list_key] is not None:
                current_list = func_args[list_key]
                if isinstance(current_list, list) and len(current_list) < num_panels:
                     # For ranges/dticks, hard to guess default. Maybe None?
                     # groundhog iterates and accesses [i].
                     func_args[list_key].extend([None] * (num_panels - len(current_list)))

    # 3. Call Groundhog Function
    try:
        # We need to remove soiltypecolumn from func_args if we call plot_with_log directly
        # as it doesn't accept it.
        if 'soiltypecolumn' in func_args:
            del func_args['soiltypecolumn']

        fig = plotting.plot_with_log(**func_args)
        
        # 4. Return Plotly JSON
        
        # 4. Return Plotly JSON
        import plotly.io
        json_str = plotly.io.to_json(fig)
        fig_dict = json.loads(json_str)
        
        return {
            "type": "plotly",
            "data": fig_dict['data'],
            "layout": fig_dict['layout']
        }
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return {"error": f"Plotting Error: {str(e)}\n\nTraceback:\n{tb}"}

def log_plot_wrapper(args):
    """
    Wrapper for SoilProfile.plot_profile (high-level plotting).
    Expects:
    - soilprofile: ID of the profile
    - parameters: Comma-separated string of parameters (e.g. "qc [MPa], Dr [%]")
    """
    # 1. Retrieve Soil Data
    profile_id = args.get('soilprofile')
    if not profile_id:
        return {"error": "Plotting Error: 'soilprofile' argument is required."}
    
    profile = state_manager.get(profile_id)
    if profile is None:
        return {"error": f"Plotting Error: SoilProfile with ID '{profile_id}' not found."}

    # 2. Parse Parameters
    params_str = args.get('parameters', "")
    if not params_str:
        return {"error": "Plotting Error: 'parameters' argument is required (comma-separated string)."}
    
    # Split by comma and strip whitespace/quotes
    # Robust split: handle comma-separated strings that might have quotes
    param_list = [p.strip().strip("'").strip('"') for p in params_str.split(',') if p.strip()]
    
    if not param_list:
         return {"error": "Plotting Error: No valid parameters provided."}

    # Check if parameters exist in profile
    missing_params = [p for p in param_list if p not in profile.columns]
    if missing_params:
        available = ", ".join(sorted(profile.columns))
        missing_str = ", ".join(f'"{mp}"' for mp in missing_params)
        return {"error": f"Plotting Error: The following parameters are not in the profile: {missing_str}.\n\nAvailable columns:\n{available}"}

    # Construct the tuple of tuples (one param per panel)
    plotting_params = tuple((p,) for p in param_list)
    
    # Auto-generate colors for missing soil types
    fillcolordict = {'SAND': 'yellow', 'CLAY': 'brown', 'SILT': 'green', 'ROCK': 'grey'}
    # Also add Title Case versions for robustness
    fillcolordict.update({'Sand': 'yellow', 'Clay': 'brown', 'Silt': 'green', 'Rock': 'grey'})
    
    # 3. Handle Soil Type Column
    soil_type_col = args.get('soiltypecolumn')
    if soil_type_col and (soil_type_col == '-- Select column --' or soil_type_col == 'None' or not soil_type_col.strip()):
        soil_type_col = None

    raw_df = pd.DataFrame(profile).copy()

    # Determine which column to use for soil type
    if not soil_type_col or soil_type_col not in raw_df.columns:
        soil_type_col = find_soil_type_column(raw_df)

    if soil_type_col and soil_type_col in raw_df.columns:
        raw_df['Soil type'] = raw_df[soil_type_col]
    else:
        raw_df['Soil type'] = 'Soil'

    # Build SoilProfile from the prepared DataFrame
    from groundhog.general.soilprofile import SoilProfile
    profile_to_plot = SoilProfile(raw_df)

    # Auto-generate colors for unique soil types
    unique_types = profile_to_plot['Soil type'].unique()
    for st in unique_types:
        st_str = str(st)
        if st_str not in fillcolordict and st not in fillcolordict:
            fallback_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#e6ab02', '#a6761d']
            color_idx = abs(hash(st_str)) % len(fallback_colors)
            fillcolordict[st] = fallback_colors[color_idx]
            fillcolordict[st_str] = fallback_colors[color_idx]

    # 4. Call plot_profile
    try:
        fig = profile_to_plot.plot_profile(plotting_params, soiltypecolumn='Soil type', showfig=False, fillcolordict=fillcolordict)
        
        # 4. Return Plotly JSON
        import plotly.io
        import json
        json_str = plotly.io.to_json(fig)
        fig_dict = json.loads(json_str)
        
        return {
            "type": "plotly",
            "data": fig_dict['data'],
            "layout": fig_dict['layout']
        }

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return {"error": f"Plotting Error: {str(e)}\n\nTraceback:\n{tb}"}
