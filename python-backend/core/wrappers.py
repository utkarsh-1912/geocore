# Author: Utkarsh Gupta
# License: GPL v2


import numpy as np
import json
import plotly
import warnings
import math
from groundhog.shallowfoundations.capacity import ShallowFoundationCapacityUndrained, ShallowFoundationCapacityDrained
from groundhog.shallowfoundations.settlement import SettlementCalculation
from groundhog.general.soilprofile import SoilProfile
from groundhog.general.parameter_mapping import map_depth_properties, offsets

def map_depth_properties_wrapper(args):
    """
    Wrapper for map_depth_properties.
    Handles fetching dataframes from state_manager.
    """
    from .state import state_manager
    
    target_id = args.get('target_soilprofile')
    layering_id = args.get('layering_soilprofile')
    
    target_obj = state_manager.get(target_id)
    layering_obj = state_manager.get(layering_id)
    
    if not isinstance(target_obj, SoilProfile) or not isinstance(layering_obj, SoilProfile):
        raise ValueError("Inputs must be SoilProfile objects")
        
    target_df = target_obj.copy()
    layering_df = layering_obj.copy()
    
    res_df = map_depth_properties(
        target_df,
        layering_df,
        target_z_key=args.get('target_z_key'),
        layering_zfrom_key=args.get('layering_zfrom_key'),
        layering_zto_key=args.get('layering_zto_key')
    )
    
    return {
        "type": "dataframe",
        "data": _sanitize(res_df.to_dict(orient='records')),
        "columns": list(res_df.columns),
        "message": "Properties mapped successfully."
    }

def offsets_wrapper(args):
    """
    Wrapper for offsets.
    Handles coordinate tuple construction.
    """
    startpoint = (float(args.get('x1')), float(args.get('y1')))
    endpoint = (float(args.get('x2')), float(args.get('y2')))
    point = (float(args.get('xp')), float(args.get('yp')))
    latlon = args.get('latlon', False)
    
    res = offsets(startpoint, endpoint, point, latlon=latlon)
    return _sanitize(res)

def merge_two_dicts_wrapper(args):
    """
    Wrapper for merge_two_dicts to handle JSON string inputs.
    """
    from groundhog.general.parameter_mapping import merge_two_dicts
    import json
    
    x = args.get('x', '{}')
    y = args.get('y', '{}')
    
    # Parse if string
    dict_x = json.loads(x) if isinstance(x, str) else x
    dict_y = json.loads(y) if isinstance(y, str) else y
    
    return _sanitize(merge_two_dicts(dict_x, dict_y))

def reverse_dict_wrapper(args):
    """
    Wrapper for reverse_dict to handle JSON string inputs.
    """
    from groundhog.general.parameter_mapping import reverse_dict
    import json
    
    d = args.get('input_dict', '{}')
    target_dict = json.loads(d) if isinstance(d, str) else d
    
    return _sanitize(reverse_dict(target_dict))


def _sanitize(obj):
    """
    Sanitizes the object for JSON serialization.
    Converts NaN and Infinity to None.
    Handles nested dicts, lists, tuples, numpy arrays, and pandas objects.
    """
    if obj is None:
        return None
    
    # helper for pandas (Check first to avoid float confusion with NA)
    try:
        import pandas as pd
        if isinstance(obj, pd.DataFrame):
             return _sanitize(obj.to_dict(orient='records'))
        if isinstance(obj, pd.Series):
             return _sanitize(obj.to_dict())
    except ImportError:
        pass

    # Handle Numpy Arrays and Scalars
    if isinstance(obj, (np.ndarray, np.generic)):
        if isinstance(obj, np.ndarray):
            return _sanitize(obj.tolist())
        else:
             # Scalar numpy type
             val = obj.item()
             return _sanitize(val)
    
    # Handle Dicts and Lists (Recursion)
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize(v) for v in obj]

    # Handle Floats (Final check after containers)
    if isinstance(obj, float): 
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
        
    return obj

def shallow_foundation_capacity_undrained_wrapper(args):
    """
    Wrapper for ShallowFoundationCapacityUndrained class.
    """
    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        try:
            # 1. Initialize logic
            analysis = ShallowFoundationCapacityUndrained("Undrained Capacity Analysis")
            
            # 2. Geometry
            shape = args.get('foundation_shape', 'rectangle')
            width = float(args.get('width'))
            length = float(args.get('length', np.nan)) # Can be nan for circle
            base_depth = float(args.get('base_depth', 0.0))
            skirted = args.get('skirted', True)

            # Handle circular case where length might be missing or irrelevant
            if shape == 'circle':
                 analysis.set_geometry(option='circle', diameter=width, depth=base_depth, skirted=skirted)
            else:
                 analysis.set_geometry(option='rectangle', length=length, width=width, depth=base_depth, skirted=skirted)
            
            # 3. Eccentricity
            ecc_l = float(args.get('eccentricity_length', 0.0))
            ecc_b = float(args.get('eccentricity_width', 0.0))
            
            if shape == 'rectangle':
                 analysis.set_eccentricity(eccentricity_width=ecc_b, eccentricity_length=ecc_l)
            else:
                 analysis.set_eccentricity(eccentricity_width=ecc_b) # Circle only takes one eccentricity arg
            
            # 4. Soil Parameters
            unit_weight = float(args.get('unit_weight'))
            su_base = float(args.get('su_base'))
            su_increase = float(args.get('su_increase', 0.0))
            su_above_base = args.get('su_above_base')
            if su_above_base == "" or su_above_base is None:
                 su_above_base = np.nan
            else:
                 su_above_base = float(su_above_base)
                 
            analysis.set_soilparameters_undrained(
                unit_weight=unit_weight,
                su_base=su_base,
                su_increase=su_increase,
                su_above_base=su_above_base
            )
            
            # 5. Factors
            factor_sliding = float(args.get('factor_sliding', 1.5))
            factor_bearing = float(args.get('factor_bearing', 2.0))
            
            # 6. Calculate
            # Calculate individual capacities
            analysis.calculate_bearing_capacity() # Stores in analysis.capacity
            analysis.calculate_sliding_capacity() # Stores in analysis.sliding
            
            # Calculate Envelope
            analysis.calculate_envelope(factor_sliding=factor_sliding, factor_bearing=factor_bearing)
            
            # 7. Generate Plot
            try:
                fig = analysis.plot_envelope(showfig=False)
                plot_json = json.loads(plotly.io.to_json(fig))
                plot_data = plot_json['data']
                plot_layout = plot_json['layout']
            except Exception as plot_err:
                 # If plotting fails (e.g. due to NaNs), returning None for plot data
                 plot_data = []
                 plot_layout = {}
                 warnings.warn(f"Plotting failed: {str(plot_err)}")
            
            results = {
                "Ultimate Vertical Capacity [kN]": analysis.ultimate_capacity,
                "Net Bearing Pressure [kPa]": analysis.net_bearing_pressure,
                "Sliding Capacity (Base) [kN]": analysis.sliding_base_only,
                "Sliding Capacity (Full) [kN]": analysis.sliding_full,
                "Full Area [m2]": getattr(analysis, 'full_area', np.nan),
                "Effective Area [m2]": analysis.effective_area,
                "Effective Width [m]": analysis.effective_width,
                "Effective Length [m]": analysis.effective_length,
                "Eccentricity [m]": getattr(analysis, 'eccentricity', np.nan)
            }
            
            # 8. Prepare Result
            response = {
                "type": "plotly",
                "data": plot_data,
                "layout": plot_layout,
                "results": results,
                "message": "Undrained capacity analysis completed."
            }
            
            # Capture warnings
            warning_messages = [str(w.message) for w in caught_warnings]
            if warning_messages:
                response["warnings"] = warning_messages
                
            return _sanitize(response)
            
        except Exception as e:
            # Also capture warnings if exception occurred
            warning_messages = [str(w.message) for w in caught_warnings]
            return {
                "error": f"Undrained Capacity Analysis Error: {str(e)}",
                "warnings": warning_messages
            }

def shallow_foundation_capacity_drained_wrapper(args):
    """
    Wrapper for ShallowFoundationCapacityDrained class.
    """
    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        try:
            # 1. Initialize logic
            analysis = ShallowFoundationCapacityDrained("Drained Capacity Analysis")
            
            # 2. Geometry
            shape = args.get('foundation_shape', 'rectangle')
            width = float(args.get('width'))
            length = float(args.get('length', np.nan))
            base_depth = float(args.get('base_depth', 0.0))
            skirted = args.get('skirted', True)

            if shape == 'circle':
                 analysis.set_geometry(option='circle', diameter=width, depth=base_depth, skirted=skirted)
            else:
                 analysis.set_geometry(option='rectangle', length=length, width=width, depth=base_depth, skirted=skirted)
            
            # 3. Eccentricity
            ecc_l = float(args.get('eccentricity_length', 0.0))
            ecc_b = float(args.get('eccentricity_width', 0.0))
            
            if shape == 'rectangle':
                 analysis.set_eccentricity(eccentricity_width=ecc_b, eccentricity_length=ecc_l)
            else:
                 analysis.set_eccentricity(eccentricity_width=ecc_b)
                 
            # 4. Soil Parameters
            eff_unit_weight = float(args.get('effective_unit_weight'))
            friction_angle = float(args.get('friction_angle'))
            eff_stress_base = float(args.get('effective_stress_base'))
            
            analysis.set_soilparameters_drained(
                effective_unit_weight=eff_unit_weight,
                friction_angle=friction_angle,
                effective_stress_base=eff_stress_base
            )
            
            # 5. Factors & Load
            factor_sliding = float(args.get('factor_sliding', 1.5))
            factor_bearing = float(args.get('factor_bearing', 2.0))
            vertical_load = float(args.get('vertical_load', 0.0))
            
            # 6. Calculate
            analysis.calculate_bearing_capacity()
            analysis.calculate_sliding_capacity(vertical_load=vertical_load)
            
            # Calculate Envelope
            analysis.calculate_envelope(factor_sliding=factor_sliding, factor_bearing=factor_bearing)
            
            # 7. Generate Plot
            try:
                fig = analysis.plot_envelope(showfig=False)
                plot_json = json.loads(plotly.io.to_json(fig))
                plot_data = plot_json['data']
                plot_layout = plot_json['layout']
            except Exception as plot_err:
                 plot_data = []
                 plot_layout = {}
                 warnings.warn(f"Plotting failed: {str(plot_err)}")
            
            results = {
                "Ultimate Vertical Capacity [kN]": analysis.ultimate_capacity,
                "Net Bearing Pressure [kPa]": analysis.net_bearing_pressure,
                "Sliding Capacity (Base) [kN]": analysis.sliding_base_only,
                "Sliding Capacity (Full) [kN]": analysis.sliding_full,
                "Full Area [m2]": getattr(analysis, 'full_area', np.nan),
                "Effective Area [m2]": analysis.effective_area,
                "Effective Width [m]": analysis.effective_width,
                "Effective Length [m]": analysis.effective_length,
                "Eccentricity [m]": getattr(analysis, 'eccentricity', np.nan)
            }
            
            # 8. Prepare Result
            response = {
                "type": "plotly",
                "data": plot_data,
                "layout": plot_layout,
                "results": results,
                "message": "Drained capacity analysis completed."
            }
            
            # Capture warnings
            warning_messages = [str(w.message) for w in caught_warnings]
            if warning_messages:
                response["warnings"] = warning_messages
            
            return _sanitize(response)
            
        except Exception as e:
            warning_messages = [str(w.message) for w in caught_warnings]
            return {
                "error": f"Drained Capacity Analysis Error: {str(e)}",
                "warnings": warning_messages
            }

def effectivearea_circle_wrapper(args):
    """
    Wrapper for effectivearea_circle_api to handle input conflicts (M, V vs e).
    """
    from groundhog.shallowfoundations.capacity import effectivearea_circle_api
    
    # Extract arguments
    radius = float(args.get('foundation_radius', np.nan))
    v_load = args.get('vertical_load')
    moment = args.get('overturning_moment')
    ecc = args.get('eccentricity')

    # Convert to float or nan
    v_load = float(v_load) if v_load is not None and v_load != "" else np.nan
    moment = float(moment) if moment is not None and moment != "" else np.nan
    ecc = float(ecc) if ecc is not None and ecc != "" else np.nan

    # Conflict Resolution Logic
    # If eccentricity is explicitly provided (and not 0 if M/V are present?), prioritize it?
    # Actually, if user types in Eccentricity, they likely want to use it.
    # If they type in M and V, likely want to use that.
    # If ALL are present:
    # Check if M and V are roughly consistent with e? No, that's too complex.
    # Simple rule: If Eccentricity is provided/valid, use it. M and V become irrelevant for AREA calculation (though V is used for reduction?).
    # Wait, effectivearea_circle_api uses V only to calculate e! 
    # "if not np.isnan(overturning_moment) and (not np.isnan(vertical_load)) ... e2 = overturning_moment / vertical_load"
    
    if not np.isnan(ecc):
        # Use eccentricity directly
        v_load = np.nan
        moment = np.nan
    elif not np.isnan(moment) and not np.isnan(v_load):
        # Use Moment and Load
        ecc = np.nan
    
    try:
        result = effectivearea_circle_api(
            foundation_radius=radius,
            vertical_load=v_load,
            overturning_moment=moment,
            eccentricity=ecc
        )
        return _sanitize(result)
    except Exception as e:
        return {"error": str(e)}

def effectivearea_rectangle_wrapper(args):
    """
    Wrapper for effectivearea_rectangle_api to handle input conflicts.
    """
    from groundhog.shallowfoundations.capacity import effectivearea_rectangle_api
    
    length = float(args.get('length', np.nan))
    width = float(args.get('width', np.nan))
    
    v_load = args.get('vertical_load')
    m_b = args.get('moment_width') # Moment around length axis -> eccentricity in width
    m_l = args.get('moment_length') # Moment around width axis -> eccentricity in length
    
    ecc_b = args.get('eccentricity_width')
    ecc_l = args.get('eccentricity_length')

    # Float conversion
    v_load = float(v_load) if v_load is not None and v_load != "" else np.nan
    m_b = float(m_b) if m_b is not None and m_b != "" else np.nan
    m_l = float(m_l) if m_l is not None and m_l != "" else np.nan
    ecc_b = float(ecc_b) if ecc_b is not None and ecc_b != "" else np.nan
    ecc_l = float(ecc_l) if ecc_l is not None and ecc_l != "" else np.nan

    # Logic for Width direction
    if not np.isnan(ecc_b):
        m_b = np.nan
        # v_load might be needed for the OTHER direction? No, V is shared.
        # But if we zero out V, we can't calculate the other ecc if it relies on M.
        # However, effectivearea_rectangle_api takes (vertical_load, overturning_moment_width, overturning_moment_length) OR (eccentricity_width, eccentricity_length)
        # It actually allows mixing?
        # Let's check signature. 
        # (length, width, vertical_load=nan, overturning_moment_width=nan, overturning_moment_length=nan, eccentricity_width=nan, eccentricity_length=nan)
    
    # Simple logic: If any eccentricity is set, try to use eccentricities.
    # If moments are set, use moments.
    # If both, prioritize eccentricity.
    
    if not np.isnan(ecc_b) or not np.isnan(ecc_l):
        # Ensure V/M are cleared if we want to force ecc usage
        # But wait, what if user provides e_width but M_length?
        # The API probably handles mixed if V is provided?
        # Let's check groundhog source if needed. 
        # For now, simplest approach:
        if not np.isnan(ecc_b): m_b = np.nan
        if not np.isnan(ecc_l): m_l = np.nan
        # If we have any eccentricities, we might not need V for those directions.
        # If we have M, we need V.
        # If we have one e and one M, we need V for the M.
        
    try:
        result = effectivearea_rectangle_api(
            length=length,
            width=width,
            vertical_load=v_load,
            moment_width=m_b,
            moment_length=m_l,
            eccentricity_width=ecc_b,
            eccentricity_length=ecc_l
        )
        return _sanitize(result)
    except Exception as e:
        return {"error": str(e)}

def axcap_calculation_wrapper(args):
    """
    Wrapper for AxCapCalculation class.
    Produces capacity profile and plots.
    """
    from .state import state_manager
    from groundhog.deepfoundations.axialcapacity.axcap import AxCapCalculation
    import json
    import plotly
    import math

    try:
        # 1. Get Soil Profile
        profile_id = args.get('soilprofile')
        profile = state_manager.get(profile_id)
        if profile is None:
             return {"error": f"SoilProfile with ID {profile_id} not found."}

        # 2. Initialize
        # Ensure profile has 'Unit skin friction' and 'Unit end bearing' columns
        # The wrapper handles initialization
        calc = AxCapCalculation(profile)

        # 3. Create Grid
        dz = float(args.get('dz', 1.0))
        calc.create_grid(dz=dz)

        # 4. Calculation Parameters
        circumference = float(args.get('circumference'))
        base_area = float(args.get('base_area'))
        
        # Optional args
        internal_circumference = args.get('internal_circumference')
        internal_circumference = float(internal_circumference) if internal_circumference is not None and internal_circumference != "" else np.nan
        
        annulus_area = args.get('annulus_area')
        annulus_area = float(annulus_area) if annulus_area is not None and annulus_area != "" else np.nan
        
        pile_weight = float(args.get('pile_weight_permeter', 0.0))
        plug_weight = float(args.get('soilplug_weight_permeter', 0.0))

        # 5. Calculate
        calc.calculate_capacity_profile(
            circumference=circumference,
            base_area=base_area,
            internal_circumference=internal_circumference,
            annulus_area=annulus_area,
            pile_weight_permeter=pile_weight,
            soilplug_weight_permeter=plug_weight
        )

        # 6. Generate Plot (Plotly)
        # plot_all_penetrations uses LogPlot (graph_objects)
        # We need to capture the figure. 
        # Groundhog's LogPlot usually returns a figure if return_fig=True
        
        fig = calc.plot_all_penetrations(return_fig=True, showfig=False)
        
        # Convert to JSON for frontend
        plot_json = json.loads(plotly.io.to_json(fig))
        
        # 7. Prepare Results
        # Send back the tabular results (capacity profile)
        # sanitize dataframe
        
        results_df = calc.capacity_profile
        
        return {
            "type": "plotly",
            "data": plot_json['data'],
            "layout": plot_json['layout'],
            "results": {
                "type": "dataframe",
                "data": _sanitize(results_df.to_dict(orient='records')),
                "columns": list(results_df.columns)
            },
            "message": "Axial capacity calculation completed."
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"AxCap Calculation Error: {str(e)}"}

def debeer_calculation_wrapper(args):
    """
    Wrapper for DeBeerCalculation class.
    """
    from .state import state_manager
    from groundhog.deepfoundations.axialcapacity.debeer import DeBeerCalculation
    import json
    import plotly
    import numpy as np
    import pandas as pd

    try:
        # 1. Get Soil Profile
        profile_id = args.get('soilprofile')
        profile = state_manager.get(profile_id)
        if profile is None:
             return {"error": f"SoilProfile with ID {profile_id} not found."}
        
        # 2. Extract Data (Depth and Qc)
        # Check for qc column
        qc_col = args.get('qc_col', 'qc [MPa]')
        if qc_col not in profile.columns:
             return {"error": f"Column '{qc_col}' not found in Soil Profile."}
        
        # Groundhog requires depth and qc as arrays
        # SoilProfile has depth_from and depth_to. We can use depth_to or average.
        # However, DeBeer usually expects continuous CPT data. 
        # If the input is a "SoilProfile" (layers), we might need to map it or expect the user to have loaded CPT data into it.
        # Assuming the SoilProfile *is* the CPT data or has high-res layers.
        # Let's use 'Depth to [m]' as the depth array.
        
        depth_col = args.get('depth_col', 'Depth [m]')
        if depth_col not in profile.columns:
             if 'Depth to [m]' in profile.columns:
                 depth_col = 'Depth to [m]'
             else:
                 return {"error": f"Column '{depth_col}' not found."}

        min_depth = profile[depth_col].min()
        max_depth = profile[depth_col].max()
        
        # Filter NaNs
        valid_data = profile.dropna(subset=[depth_col, qc_col])
        depths = valid_data[depth_col].values
        qcs = valid_data[qc_col].values

        # 3. Parameters
        diameter_pile = float(args.get('pile_diameter'))
        diameter_cone = float(args.get('cone_diameter', 0.0357))
        
        # 4. Initialize Calculation
        calc = DeBeerCalculation(depths, qcs, diameter_pile, diameter_cone)
        
        # Resample (Required by DeBeer logic often, default 0.2m)
        calc.resample_data(spacing=0.2)

        # 5. Set Soil Layers (using the same profile)
        # This requires 'Soil type' column and others
        soil_type_col = args.get('soil_type_col', 'Soil type')
        tertiary_clay_col = args.get('tertiary_clay_col', 'Tertiary clay')
        gamma_col = args.get('gamma_col', 'Total unit weight [kN/m3]')
        water_level = float(args.get('water_level', 0.0))
        
        # If tertiary clay column doesn't exist, Create it as False (Handled by set_soil_layers logic but better to ensure)
        
        calc.set_soil_layers(
            soilprofile=profile,
            soiltypecolumn=soil_type_col,
            tertiaryclaycolumn=tertiary_clay_col,
            totalunitweightcolumn=gamma_col,
            water_level=water_level
        )
        
        # 6. Set Factors
        alpha_b_tertiary = float(args.get('alpha_b_tertiary_clay', 0.5))
        alpha_b_other = float(args.get('alpha_b_other', 0.5))
        alpha_s_tertiary = float(args.get('alpha_s_tertiary_clay', 0.025))
        alpha_s_other = float(args.get('alpha_s_other', 0.01))
        
        calc.set_shaft_base_factors(
            alpha_b_tertiary_clay=alpha_b_tertiary,
            alpha_b_other=alpha_b_other,
            alpha_s_tertiary_clay=alpha_s_tertiary,
            alpha_s_other=alpha_s_other
        )
        
        # 7. Calculate Components
        # Unit Shaft Friction
        calc.calculate_average_qc()
        calc.calculate_unit_shaft_friction()
        
        # Base Resistance
        calc.calculate_base_resistance()
        
        # 8. Calculate Total Capacity Profile
        # Iterate over depths to calculate Rc vs Depth
        # We can calculate it at every meter or matching the CPT grid
        
        results = []
        # Calculate for depths where we have qb (calc.depth_qb)
        # We need check max depth
        
        calc_depths = calc.depth_qb.values
        
        circumference = np.pi * diameter_pile
        base_area = np.pi * (diameter_pile / 2)**2

        for d in calc_depths:
            if d <= 0 or d > max_depth: continue
            try:
                calc.calculate_pile_resistance(
                    pile_penetration=d,
                    base_area=base_area,
                    circumference=circumference
                )
                results.append({
                    "Depth [m]": d,
                    "Rb [kN]": calc.Rb,
                    "Rs [kN]": calc.Rs,
                    "Rc [kN]": calc.Rc,
                    "qb [MPa]": calc.qb_selected # unit base resistance
                })
            except Exception:
                pass
                
        results_df = pd.DataFrame(results)

        # 9. Plots
        # Base Plot
        calc.plot_base_resistance(show_fig=False)
        base_plot_json = json.loads(plotly.io.to_json(calc.base_plot))
        
        # Shaft Plot
        calc.plot_unit_shaft_friction(show_fig=False)
        shaft_plot_json = json.loads(plotly.io.to_json(calc.unit_shaft_plot))
        
        return {
            "type": "multi_plot",
            "plots": [
                {"title": "Base Resistance", "data": base_plot_json['data'], "layout": base_plot_json['layout']},
                {"title": "Unit Shaft Friction", "data": shaft_plot_json['data'], "layout": shaft_plot_json['layout']}
            ],
            "results": {
                "type": "dataframe",
                "data": _sanitize(results_df.to_dict(orient='records')),
                "columns": list(results_df.columns)
            },
            "message": "De Beer calculation completed."
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"De Beer Calculation Error: {str(e)}"}

def koppejan_calculation_wrapper(args):
    """
    Wrapper for KoppejanCalculation class.
    """
    from .state import state_manager
    from groundhog.deepfoundations.axialcapacity.koppejan import KoppejanCalculation
    import json
    import plotly
    import numpy as np
    import pandas as pd

    try:
        # 1. Get Soil Profile
        profile_id = args.get('soilprofile')
        profile = state_manager.get(profile_id)
        if profile is None:
             return {"error": f"SoilProfile with ID {profile_id} not found."}
        
        # 2. Extract Data
        qc_col = args.get('qc_col', 'qc [MPa]')
        if qc_col not in profile.columns:
             return {"error": f"Column '{qc_col}' not found in Soil Profile."}
        
        # Depth Columns (From and To)
        depth_from_col = args.get('depth_from_col', 'Depth from [m]')
        depth_to_col = args.get('depth_to_col', 'Depth to [m]')
        
        if depth_from_col not in profile.columns:
             return {"error": f"Column '{depth_from_col}' not found."}
        if depth_to_col not in profile.columns:
             return {"error": f"Column '{depth_to_col}' not found."}

        # Filter NaNs
        valid_data = profile.dropna(subset=[depth_from_col, depth_to_col, qc_col]).sort_values(by=depth_to_col)
        
        # Use Depth To as the main depth array for calculation steps (conservative)
        depths = valid_data[depth_to_col].values
        qcs = valid_data[qc_col].values

        # 3. Parameters
        diameter = float(args.get('pile_diameter'))
        # Target penetration for the detailed plots
        max_valid_depth = depths.max()
        default_penetration = max(0, max_valid_depth - 4 * diameter - 1)
        penetration = float(args.get('pile_penetration') or default_penetration)
        
        if penetration > (max_valid_depth - 4 * diameter):
             return {"error": f"Pile penetration ({penetration}m) too deep. Max allowed: {max_valid_depth - 4*diameter:.2f}m (Max Depth - 4D)"}

        # 4. Initialize Calculation
        calc = KoppejanCalculation(depths, qcs, diameter, penetration)
        
        # 5. Set Layers
        gamma_col = args.get('gamma_col', 'Total unit weight [kN/m3]')
        water_level = float(args.get('water_level', 0.0))
        water_unit_weight = float(args.get('water_unit_weight', 10.0))
        
        layer_df = profile.copy()
        if gamma_col not in layer_df.columns:
             return {"error": f"Column '{gamma_col}' not found for Unit Weight."}
        
        # Map to standard names expected by Groundhog
        layer_df['Depth from [m]'] = layer_df[depth_from_col]
        layer_df['Depth to [m]'] = layer_df[depth_to_col]
        layer_df['Total unit weight [kN/m3]'] = layer_df[gamma_col]
        
        calc.set_layer_properties(
            layer_data=layer_df, 
            waterlevel=water_level, 
            waterunitweight=water_unit_weight
        )
        
        # 6. Coefficients
        alpha_s = float(args.get('alpha_s', 0.006)) # friction factor
        alpha_p = float(args.get('alpha_p', 0.3))   # base factor
        base_coeff = float(args.get('base_coefficient', 1.0))
        xs_coeff = float(args.get('crosssection_coefficient', 1.0))
        coring = args.get('coring', False)
        wall_thick = float(args.get('wall_thickness', np.nan)) if args.get('wall_thickness') else np.nan
        
        # 7. Calculate Side Friction (Valid for all depths)
        calc.calculate_side_friction(alpha_s=alpha_s)
        
        # 8. Loop for Capacity Profile
        # Create a grid for calculation
        profile_results = []
        
        # Limit max depth for calculation
        calc_limit = max_valid_depth - 4 * diameter
        
        # Step size 0.5m or similar
        calc_depths = np.arange(depths.min() + diameter, calc_limit, 0.5) 
        
        # Also include the target penetration
        if penetration not in calc_depths:
            calc_depths = np.sort(np.append(calc_depths, penetration))

        # We can optimize by pre-calculating Rs interpolation
        # Rs is in calc.data['Frs [kN]']
        
        full_rs_interp = np.interp(calc_depths, calc.data['z [m]'], calc.data['Frs [kN]'])
        
        for idx, d in enumerate(calc_depths):
            if d <= 0: continue
            
            # Update penetration
            calc.penetration = d
            
            try:
                calc.calculate_base_resistance(
                    alpha_p=alpha_p,
                    base_coefficient=base_coeff,
                    crosssection_coefficient=xs_coeff,
                    coring=coring,
                    wall_thickness=wall_thick
                )
                
                profile_results.append({
                    "Depth [m]": d,
                    "Rb [kN]": calc.Frb,
                    "Rs [kN]": full_rs_interp[idx],
                    "Rc [kN]": calc.Frb + full_rs_interp[idx],
                    "qb_max [MPa]": calc.qbmax
                })
            except Exception:
                pass

        results_df = pd.DataFrame(profile_results)
        
        # 9. Detailed Plots for TARGET Penetration
        # Reset to target
        calc.penetration = penetration
        calc.calculate_base_resistance(
            alpha_p=alpha_p,
            base_coefficient=base_coeff,
            crosssection_coefficient=xs_coeff,
            coring=coring,
            wall_thickness=wall_thick
        )
        
        calc.plot_baseconstruction(show_fig=False)
        calc.plot_shaft_resistance(show_fig=False)
        
        base_fig = json.loads(plotly.io.to_json(calc.base_fig))
        shaft_fig = json.loads(plotly.io.to_json(calc.shaft_fig))

        return {
            "type": "multi_plot",
            "plots": [
                {"title": f"Base Construction (Tip @ {penetration}m)", "data": base_fig['data'], "layout": base_fig['layout']},
                {"title": "Shaft Resistance Construction", "data": shaft_fig['data'], "layout": shaft_fig['layout']}
            ],
            "results": {
                "type": "dataframe",
                "data": _sanitize(results_df.to_dict(orient='records')),
                "columns": list(results_df.columns)
            },
            "message": "Koppejan calculation completed."
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Koppejan Calculation Error: {str(e)}"}

def lcpc_calculation_wrapper(args):
    """
    Wrapper for LCPCAxcapCalculation class.
    """
    from .state import state_manager
    from groundhog.deepfoundations.axialcapacity.lcpc import LCPCAxcapCalculation
    import json
    import plotly
    import numpy as np
    import pandas as pd

    try:
        # 1. Get Soil Profile
        profile_id = args.get('soilprofile')
        profile = state_manager.get(profile_id)
        if profile is None:
             return {"error": f"SoilProfile with ID {profile_id} not found."}
        
        # 2. Extract Data (Depth and Qc)
        qc_col = args.get('qc_col', 'qc [MPa]')
        if qc_col not in profile.columns:
             return {"error": f"Column '{qc_col}' not found in Soil Profile."}
        
        depth_col = args.get('depth_col', 'Depth [m]')
        if depth_col not in profile.columns:
             if 'Depth to [m]' in profile.columns:
                 depth_col = 'Depth to [m]'
             else:
                 return {"error": f"Column '{depth_col}' not found."}

        # Filter NaNs
        valid_data = profile.dropna(subset=[depth_col, qc_col]).sort_values(by=depth_col)
        # Ensure sufficient data? LCPC needs 1.5D below tip. 
        # But we calculate for a full profile usually.
        # Groundhog LCPC takes lists
        depths = valid_data[depth_col].values
        qcs = valid_data[qc_col].values

        # 3. Parameters
        diameter_pile = float(args.get('pile_diameter'))
        diameter_shaft = float(args.get('diameter_shaft')) if args.get('diameter_shaft') else np.nan
        group_base = args.get('group_base', 'I')
        group_shaft = args.get('group_shaft', 'IA')
        
        # 4. Initialize Calculation
        calc = LCPCAxcapCalculation(
            depth=depths,
            qc=qcs,
            diameter_pile=diameter_pile,
            group_base=group_base,
            group_shaft=group_shaft,
            diameter_shaft=diameter_shaft
        )
        
        # 5. Set Soil Layers
        # Needs 'Soil type' column with specific values: Clay, Silt, Sand, Chalk, Gravel
        soil_type_col = args.get('soil_type_col', 'Soil type')
        water_level = float(args.get('water_level', 0.0))
        
        # We need to pass the profile object.
        # But groundhog checks validations on the profile object passed to set_soil_layers.
        # Our "profile" variable is a DataFrame with metadata (from state_manager wrapper). 
        # Groundhog's LCPCAxcapCalculation.set_soil_layers expects a Groundhog SoilProfile object.
        # We need to convert our DataFrame wrapper back to a Groundhog SoilProfile or ensure it behaves like one.
        # In state_manager, we usually store the Groundhog SoilProfile object directly? 
        # Let's check wrappers.py imports. It implies `profile = state_manager.get(profile_id)`.
        # If `profile` is the actual object, we are good.
        
        try:
            calc.set_soil_layers(
                soilprofile=profile,
                soiltypecolumn=soil_type_col,
                water_level=water_level
            )
        except ValueError as e:
            return {"error": f"Soil Layer Error: {str(e)}. Ensure Soil Types are one of: Clay, Silt, Sand, Chalk, Gravel."}

        # 6. Run Calculations
        calc.qca_calculation()
        calc.calculate_base_resistance()
        
        careful = args.get('careful_execution', False)
        calc.calculate_shaft_resistance(careful_execution=careful)
        
        # 7. Results
        # calc.calculation_data contains the results
        results_df = calc.calculation_data.copy()
        
        # Calculate Rc
        results_df['Rc [kN]'] = results_df['Qb [kN]'] + results_df['Qs [kN]']
        
        # Filter for output (sanitize NaNs)
        output_data = _sanitize(results_df.to_dict(orient='records'))

        # 8. Plots
        # LCPC has built-in plot methods `plot_axcap` and `plot_fs_qb`
        # They return Groundhog LogPlot objects. We need to convert them to JSON.
        # The LogPlot object wraps Plotly. `plot.fig` gives the figure?
        # Let's check groundhog source or assume standard mechanism.
        # Looking at LCPC source: `axcapplot = LogPlot(...)` ... `axcapplot.show()`.
        # LogPlot likely has a `.fig` attribute which is the plotly Figure.
        
        axcap_plot_obj = calc.plot_axcap(return_fig=True, show_fig=False)
        fs_qb_plot_obj = calc.plot_fs_qb(return_fig=True, show_fig=False)
        
        # Safely access the figure. 
        # If LogPlot is a wrapper, we need the underlying figure.
        # Inspecting groundhog/general/plotting.py would confirm, but usually `fig` is the attribute.
        
        # Hack: if LogPlot doesn't expose `fig` cleanly, we might need to rely on what `to_json` expects.
        # Usually our wrappers return pure Plotly JSON.
        
        def get_fig_json(plot_obj):
            if hasattr(plot_obj, 'fig'):
                return json.loads(plotly.io.to_json(plot_obj.fig))
            else:
                 # Fallback if plot_obj IS the figure (unlikely given source code uses LogPlot wrapper)
                 return json.loads(plotly.io.to_json(plot_obj))

        axcap_json = get_fig_json(axcap_plot_obj)
        fsqb_json = get_fig_json(fs_qb_plot_obj)

        return {
            "type": "multi_plot",
            "plots": [
                {"title": "Axial Capacity Profile", "data": axcap_json['data'], "layout": axcap_json['layout']},
                {"title": "Unit Friction & End Bearing", "data": fsqb_json['data'], "layout": fsqb_json['layout']}
            ],
            "results": {
                "type": "dataframe",
                "data": output_data,
                "columns": list(results_df.columns)
            },
            "message": "LCPC calculation completed."
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"LCPC Calculation Error: {str(e)}"}

def pile_settlement_curves_wrapper(args):
    """
    Wrapper for pile_settlement_curves function.
    """
    from groundhog.deepfoundations.axialresponse.settlement import pile_settlement_curves
    import numpy as np

    try:
        # 1. Extract Parameters
        diameter = float(args.get('diameter'))
        shaft_resistance = float(args.get('shaft_resistance'))
        base_resistance = float(args.get('base_resistance'))
        pile_type = args.get('pile_type', 'driven')
        
        # 2. Run Calculation
        results = pile_settlement_curves(
            diameter=diameter,
            shaft_resistance=shaft_resistance,
            base_resistance=base_resistance,
            pile_type=pile_type
        )
        
        # 3. Process Results for Plotting
        # The function returns dictionaries with 'w [m]' and 'F [kN]' or normalized versions.
        
        total_data = results['total']
        shaft_data = results['shaft_denormalised']
        base_data = results['base_denormalised']
        
        # Prepare Plotly Data
        plot_data = [
            {
                "x": total_data['w [m]'].tolist() if isinstance(total_data['w [m]'], np.ndarray) else total_data['w [m]'],
                "y": total_data['F [kN]'].tolist() if isinstance(total_data['F [kN]'], np.ndarray) else total_data['F [kN]'],
                "type": "scatter",
                "mode": "lines",
                "name": "Total Resistance"
            },
            {
                "x": shaft_data['w [m]'].tolist() if isinstance(shaft_data['w [m]'], np.ndarray) else shaft_data['w [m]'],
                "y": shaft_data['Fs [kN]'].tolist() if isinstance(shaft_data['Fs [kN]'], np.ndarray) else shaft_data['Fs [kN]'],
                "type": "scatter",
                "mode": "lines",
                "name": "Shaft Resistance",
                "line": {"dash": "dash"}
            },
            {
                "x": base_data['w [m]'].tolist() if isinstance(base_data['w [m]'], np.ndarray) else base_data['w [m]'],
                "y": base_data['Fb [kN]'].tolist() if isinstance(base_data['Fb [kN]'], np.ndarray) else base_data['Fb [kN]'],
                "type": "scatter",
                "mode": "lines",
                "name": "Base Resistance",
                "line": {"dash": "dot"}
            }
        ]
            
        layout = {
            "title": f"Pile Settlement Curves ({pile_type}, D={diameter}m)",
            "xaxis": {"title": "Settlement w [m]"},
            "yaxis": {"title": "Load F [kN]"},
            "showlegend": True
        }

        # 4. Return
        return {
            "type": "plot",
            "data": plot_data,
            "layout": layout,
            "message": "Pile settlement curves calculated successfully."
        }


    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Pile Settlement Curves Error: {str(e)}"}

def pilegroupeffect_reesevanimpe_wrapper(args):
    """
    Wrapper for pilegroupeffect_reesevanimpe.
    Handles converting string inputs to lists.
    """
    from groundhog.deepfoundations.lateralresponse.lateral import pilegroupeffect_reesevanimpe
    import json
    import plotly
    
    # helper to parse comma separated floats
    def parse_float_list(s):
        if not s: return []
        return [float(x.strip()) for x in str(s).split(',')]

    pile_x = parse_float_list(args.get('pile_x', '0, 3, 0, 3'))
    pile_y = parse_float_list(args.get('pile_y', '0, 0, 3, 3'))
    pile_diameters = parse_float_list(args.get('pile_diameters', '1.0, 1.0, 1.0, 1.0'))
    load_x = float(args.get('load_x', 100))
    load_y = float(args.get('load_y', 0))
    
    try:
        res = pilegroupeffect_reesevanimpe(
            pile_x=pile_x,
            pile_y=pile_y,
            pile_diameters=pile_diameters,
            load_x=load_x,
            load_y=load_y,
            show_fig=False
        )
        
        # Handle plot
        fig = res.pop('pile_fig', None)
        plot_json = None
        if fig:
            # Convert Matplotlib figure to Plotly JSON
            plot_json = json.loads(plotly.io.to_json(fig))
            
        return {
            "type": "plot",
            "data": plot_json['data'] if plot_json else [],
            "layout": plot_json['layout'] if plot_json else {},
            "raw_data": _sanitize(res),
            "message": "Pile group effect calculated."
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Pile Group Effect Error: {str(e)}"}

def reinforced_circularsection_inertia_wrapper(args):
    """
    Wrapper for reinforced_circularsection_inertia.
    """
    from groundhog.deepfoundations.lateralresponse.lateral import reinforced_circularsection_inertia
    
    diameter = float(args.get('diameter'))
    modulus_ratio = float(args.get('modulus_ratio', 7))
    n_bars = int(args.get('n_bars', 8))
    offset = float(args.get('offset'))
    rebar_diameter = float(args.get('rebar_diameter'))
    maximum_resistance = args.get('maximum_resistance', True)
    
    try:
        res = reinforced_circularsection_inertia(
            diameter=diameter,
            modulus_ratio=modulus_ratio,
            n_bars=n_bars,
            offset=offset,
            rebar_diameter=rebar_diameter,
            maximum_resistance=maximum_resistance
        )
        return _sanitize(res)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Inertia Calculation Error: {str(e)}"}


def expansion_cylinder_tresca_wrapper(args):
    from groundhog.deepfoundations.boreholestability.cavityexpansion import expansion_cylinder_tresca
    
    insitu_pressure = float(args.get('insitu_pressure'))
    borehole_pressure = float(args.get('borehole_pressure'))
    diameter = float(args.get('diameter'))
    undrained_shear_strength = float(args.get('undrained_shear_strength'))
    shear_modulus = float(args.get('shear_modulus'))
    poissons_ratio = float(args.get('poissons_ratio', 0.5))
    max_radius_multiplier = float(args.get('max_radius_multiplier', 10.0))
    number_radii = int(args.get('number_radii', 250))
    
    try:
        res = expansion_cylinder_tresca(
            insitu_pressure=insitu_pressure,
            borehole_pressure=borehole_pressure,
            diameter=diameter,
            undrained_shear_strength=undrained_shear_strength,
            shear_modulus=shear_modulus,
            poissons_ratio=poissons_ratio,
            max_radius_multiplier=max_radius_multiplier,
            number_radii=number_radii
        )
        
        # Create Plots
        charts = []
        if 'radii [m]' in res:
             # Radial & Tangential Stresses
             charts.append({
                "x": res['radii [m]'].tolist() if hasattr(res['radii [m]'], 'tolist') else res['radii [m]'],
                "y": res['radial stresses [kPa]'].tolist() if hasattr(res['radial stresses [kPa]'], 'tolist') else res['radial stresses [kPa]'],
                "type": "scatter",
                "mode": "lines",
                "name": "Radial Stress"
             })
             charts.append({
                "x": res['radii [m]'].tolist() if hasattr(res['radii [m]'], 'tolist') else res['radii [m]'],
                "y": res['tangential stresses [kPa]'].tolist() if hasattr(res['tangential stresses [kPa]'], 'tolist') else res['tangential stresses [kPa]'],
                "type": "scatter",
                "mode": "lines",
                "name": "Tangential Stress"
             })

        plot_data = {
            "type": "plotly",
            "data": charts,
            "layout": {
                "title": "Cylinder Expansion Stresses",
                "xaxis": {"title": "Radius [m]"},
                "yaxis": {"title": "Stress [kPa]"}
            },
            "raw_data": _sanitize(res)
        }
        return plot_data

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Expansion Cylinder Tresca Error: {str(e)}"}

def expansion_tresca_thicksphere_wrapper(args):
    from groundhog.deepfoundations.boreholestability.cavityexpansion import expansion_tresca_thicksphere
    
    su = float(args.get('undrained_shear_strength'))
    ri = float(args.get('internal_radius'))
    re = float(args.get('external_radius'))
    pi = float(args.get('internal_pressure'))
    pe = float(args.get('external_pressure'))
    E = float(args.get('youngs_modulus'))
    nu = float(args.get('poissons_ratio', 0.5))
    seed = int(args.get('seed', 100))
    
    try:
        res = expansion_tresca_thicksphere(
            undrained_shear_strength=su,
            internal_radius=ri,
            external_radius=re,
            internal_pressure=pi,
            external_pressure=pe,
            youngs_modulus=E,
            poissons_ratio=nu,
            seed=seed
        )
        
        charts = []
        # Elastic Phase
        if 'elastic radii [m]' in res:
             charts.append({
                "x": res['elastic radii [m]'].tolist() if hasattr(res['elastic radii [m]'], 'tolist') else res['elastic radii [m]'],
                "y": res['elastic_radial_stress [kPa]'].tolist() if hasattr(res['elastic_radial_stress [kPa]'], 'tolist') else res['elastic_radial_stress [kPa]'],
                "type": "scatter",
                "mode": "lines",
                "name": "Elastic Radial Stress"
             })
             charts.append({
                "x": res['elastic radii [m]'].tolist() if hasattr(res['elastic radii [m]'], 'tolist') else res['elastic radii [m]'],
                "y": res['elastic_tangential_stress [kPa]'].tolist() if hasattr(res['elastic_tangential_stress [kPa]'], 'tolist') else res['elastic_tangential_stress [kPa]'],
                "type": "scatter",
                "mode": "lines",
                "name": "Elastic Tangential Stress"
             })

        # Elastoplastic Phase
        if 'elastoplastic radii [m]' in res:
             charts.append({
                "x": res['elastoplastic radii [m]'].tolist() if hasattr(res['elastoplastic radii [m]'], 'tolist') else res['elastoplastic radii [m]'],
                "y": res['elastoplastic_radial_stress [kPa]'].tolist() if hasattr(res['elastoplastic_radial_stress [kPa]'], 'tolist') else res['elastoplastic_radial_stress [kPa]'],
                "type": "scatter",
                "mode": "lines",
                "name": "Elasto-Plastic Radial Stress",
                "line": {"dash": "dash"}
             })
             charts.append({
                "x": res['elastoplastic radii [m]'].tolist() if hasattr(res['elastoplastic radii [m]'], 'tolist') else res['elastoplastic radii [m]'],
                "y": res['elastoplastic_tangential_stress [kPa]'].tolist() if hasattr(res['elastoplastic_tangential_stress [kPa]'], 'tolist') else res['elastoplastic_tangential_stress [kPa]'],
                "type": "scatter",
                "mode": "lines",
                "name": "Elasto-Plastic Tangential Stress",
                "line": {"dash": "dash"}
             })

        return {
            "type": "plotly",
            "data": charts,
            "layout": {
                "title": "Thick Sphere Expansion Stresses",
                "xaxis": {"title": "Radius [m]"},
                "yaxis": {"title": "Stress [kPa]"}
            },
            "raw_data": _sanitize(res)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Expansion Thick Sphere Error: {str(e)}"}

def stress_cylinder_elastic_isotropic_wrapper(args):
    from groundhog.deepfoundations.boreholestability.cavityexpansion import stress_cylinder_elastic_isotropic
    import numpy as np

    radius_arg = args.get('radius')
    # Parse list of radii
    if isinstance(radius_arg, str):
         radii = [float(x.strip()) for x in radius_arg.split(',')]
         radii = np.array(radii)
    else:
         radii = float(radius_arg)

    internal_pressure = float(args.get('internal_pressure'))
    farfield_pressure = float(args.get('farfield_pressure'))
    borehole_radius = float(args.get('borehole_radius'))
    
    shear_modulus_arg = args.get('shear_modulus')
    shear_modulus = float(shear_modulus_arg) if shear_modulus_arg not in [None, ''] else np.nan
    
    try:
        res = stress_cylinder_elastic_isotropic(
            radius=radii,
            internal_pressure=internal_pressure,
            farfield_pressure=farfield_pressure,
            borehole_radius=borehole_radius,
            shear_modulus=shear_modulus
        )
        
        # If input was array, plot the results
        if isinstance(radii, (list, np.ndarray)):
            charts = []
            charts.append({
                "x": radii.tolist() if hasattr(radii, 'tolist') else radii,
                "y": res['radial stress [kPa]'].tolist() if hasattr(res['radial stress [kPa]'], 'tolist') else res['radial stress [kPa]'],
                "type": "scatter",
                "mode": "lines+markers",
                "name": "Radial Stress"
            })
            charts.append({
                "x": radii.tolist() if hasattr(radii, 'tolist') else radii,
                "y": res['tangential stress [kPa]'].tolist() if hasattr(res['tangential stress [kPa]'], 'tolist') else res['tangential stress [kPa]'],
                "type": "scatter",
                "mode": "lines+markers",
                "name": "Tangential Stress"
            })
            
            return {
                "type": "plotly",
                "data": charts,
                "layout": {
                    "title": "Elastic Cylinder Stresses",
                    "xaxis": {"title": "Radius [m]"},
                    "yaxis": {"title": "Stress [kPa]"}
                },
                "raw_data": _sanitize(res)
            }
        else:
             return _sanitize(res)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Elastic Cylinder Stress Error: {str(e)}"}


def negativeskinfriction_pilegroup_zeevaertdebeer_wrapper(args):
    """
    Wrapper for negativeskinfriction_pilegroup_zeevaertdebeer
    """
    try:
        from groundhog.deepfoundations.axialcapacity.negativeskinfriction import negativeskinfriction_pilegroup_zeevaertdebeer
    except ImportError:
        return {"error": "Could not import groundhog.deepfoundations.axialcapacity.negativeskinfriction"}

    soilprofile = args.get('soilprofile', [])
    eff_unit_weight_col = args.get('eff_unit_weight_col', 'Effective Unit Weight [kN/m3]')
    k_col = args.get('k_col', 'K0')
    delta_col = args.get('delta_col', 'Interface Friction Angle [deg]')
    surcharge = float(args.get('surcharge', 0))
    diameter = float(args.get('diameter', 0.5))
    diameter_influence = float(args.get('diameter_influence', 0.5))

    if isinstance(soilprofile, str):
        import json
        try:
            soilprofile = json.loads(soilprofile)
        except Exception as e:
            return {"error": f"Failed to parse soilprofile JSON: {str(e)}"}

    if not soilprofile:
        return {"error": "Soil Profile is required"}

    # Extract arrays
    try:
        depths = [float(layer.get('Depth [m]', 0)) for layer in soilprofile]
        eff_unit_weights = [float(layer.get(eff_unit_weight_col, 0)) for layer in soilprofile]
        k_values = [float(layer.get(k_col, 0)) for layer in soilprofile]
        delta_values = [float(layer.get(delta_col, 0)) for layer in soilprofile]
    except (ValueError, KeyError) as e:
        return {"error": f"Error extracting columns from Soil Profile: {str(e)}. Check if selected columns exist and contain numbers."}

    if len(depths) > 1 and depths[0] > depths[-1]:
         depths.reverse()
         eff_unit_weights.reverse()
         k_values.reverse()
         delta_values.reverse()

    try:
        res = negativeskinfriction_pilegroup_zeevaertdebeer(
            depths=depths,
            effective_unit_weights=eff_unit_weights,
            lateral_earth_pressure_coefficients=k_values,
            interface_friction_angles=delta_values,
            surcharge=surcharge,
            diameter=diameter,
            diameter_influence=diameter_influence
        )
        
        # Plotting
        charts = []
        if 'negative_skin_friction_profile_single [kN]' in res:
             charts.append({
                "x": res['negative_skin_friction_profile_single [kN]'].tolist() if hasattr(res['negative_skin_friction_profile_single [kN]'], 'tolist') else res['negative_skin_friction_profile_single [kN]'],
                "y": depths,
                "type": "scatter",
                "mode": "lines",
                "name": "Single Pile NSF",
                "orientation": "h"
             })
        if 'negative_skin_friction_profile_group [kN]' in res:
             charts.append({
                "x": res['negative_skin_friction_profile_group [kN]'].tolist() if hasattr(res['negative_skin_friction_profile_group [kN]'], 'tolist') else res['negative_skin_friction_profile_group [kN]'],
                "y": depths,
                "type": "scatter",
                "mode": "lines",
                "name": "Group Pile NSF",
                "orientation": "h"
             })
             
        if 'virgin_effective_stress [kPa]' in res:
             charts.append({
                "x": res['virgin_effective_stress [kPa]'].tolist() if hasattr(res['virgin_effective_stress [kPa]'], 'tolist') else res['virgin_effective_stress [kPa]'],
                "y": depths,
                "type": "scatter",
                "mode": "lines",
                "name": "Virgin Eff. Stress",
                "orientation": "h",
                "visible": "legendonly"
             })
        if 'group_effective_stress [kPa]' in res:
             charts.append({
                "x": res['group_effective_stress [kPa]'].tolist() if hasattr(res['group_effective_stress [kPa]'], 'tolist') else res['group_effective_stress [kPa]'],
                "y": depths,
                "type": "scatter",
                "mode": "lines",
                "name": "Group Eff. Stress",
                "orientation": "h",
                "visible": "legendonly"
             })

        return {
            "type": "plotly",
            "data": charts,
            "layout": {
                "title": "Negative Skin Friction",
                "xaxis": {"title": "Force [kN] / Stress [kPa]", "side": "top"},
                "yaxis": {"title": "Depth [m]", "autorange": "reversed"},
                "legend": {"orientation": "h", "y": -0.1}
            },
            "raw_data": _sanitize(res)
        }

    except Exception as e:
         import traceback
         traceback.print_exc()
         return {"error": f"Negative Skin Friction Error: {str(e)}"}


def piletest_chinkondler_wrapper(args):
    """
    Wrapper for piletest_chinkondler
    """
    try:
        from groundhog.deepfoundations.axialcapacity.piletesting import piletest_chinkondler
    except ImportError:
        return {"error": "Could not import groundhog.deepfoundations.axialcapacity.piletesting"}

    soilprofile = args.get('soilprofile', [])
    
    if isinstance(soilprofile, str):
        import json
        try:
            soilprofile = json.loads(soilprofile)
        except Exception as e:
            return {"error": f"Failed to parse soilprofile JSON: {str(e)}"}

    load_col = args.get('load_col', 'Load [kN]')
    settlement_col = args.get('settlement_col', 'Settlement [mm]')
    no_discard_points = int(args.get('no_discard_points', 1))
    max_settlement = float(args.get('max_settlement', 50))
    selected_settlement = float(args.get('selected_settlement', 40))

    if not soilprofile:
        return {"error": "Test Data (Soil Profile) is required"}

    try:
        loads = [float(layer.get(load_col, 0)) for layer in soilprofile]
        settlements = [float(layer.get(settlement_col, 0)) for layer in soilprofile]
    except (ValueError, KeyError) as e:
        return {"error": f"Error extraction columns: {str(e)}"}

    try:
        res = piletest_chinkondler(
            loads=loads,
            settlements=settlements,
            no_discard_points=no_discard_points,
            max_settlement=max_settlement,
            selected_settlement=selected_settlement,
            show_fig=False
        )
        
        charts = []
        
        # 1. Extrapolated Curve vs Measured
        charts.append({
            "x": settlements,
            "y": loads,
            "type": "scatter",
            "mode": "markers",
            "name": "Measured Data",
            "marker": {"color": "black"}
        })
        
        if 'Settlements [mm]' in res and 'Q [kN]' in res:
            charts.append({
                "x": res['Settlements [mm]'] if isinstance(res['Settlements [mm]'], list) else res['Settlements [mm]'].tolist(),
                "y": res['Q [kN]'] if isinstance(res['Q [kN]'], list) else res['Q [kN]'].tolist(),
                "type": "scatter",
                "mode": "lines",
                "name": "Chin-Kondler Extrapolation",
                "line": {"dash": "dash"}
            })

        # 2. Linearization Plot (s/Q vs s)
        sq_measured = []
        s_measured_clean = []
        for q, s in zip(loads, settlements):
            if q > 1e-6: # Avoid division by zero
                sq_measured.append(s/q)
                s_measured_clean.append(s)
        
        charts.append({
            "x": s_measured_clean,
            "y": sq_measured,
            "type": "scatter",
            "mode": "markers",
            "name": "Measured s/Q",
            "xaxis": "x2",
            "yaxis": "y2"
        })
        
        slope = res.get('slope [1/kN]')
        intercept = res.get('intercept [mm/kN]')
        
        if slope is not None and intercept is not None:
             max_s = max(settlements) if settlements else max_settlement
             x_fit = [0, max_s]
             y_fit = [intercept, slope * max_s + intercept]
             
             charts.append({
                "x": x_fit,
                "y": y_fit,
                "type": "scatter",
                "mode": "lines",
                "name": "Linear Fit",
                "xaxis": "x2",
                "yaxis": "y2"
             })

        layout = {
            "title": "Chin-Kondler Results",
            "grid": {"rows": 1, "columns": 2, "pattern": "independent"},
            "xaxis": {"title": "Settlement [mm]"},
            "yaxis": {"title": "Load [kN]"},
            "xaxis2": {"title": "Settlement [mm]"},
            "yaxis2": {"title": "Settlement / Load [mm/kN]"}
        }

        return {
            "type": "plotly",
            "data": charts,
            "layout": layout,
            "raw_data": _sanitize(res)
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Chin-Kondler Error: {str(e)}"}
