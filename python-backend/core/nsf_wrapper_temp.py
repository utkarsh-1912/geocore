# Author: Utkarsh Gupta
# License: GPL v3


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

    # Sort by depth if needed (Groundhog usually expects sorted depths)
    # We assume soil profile is usually sorted, but let's be safe if it's not?
    # Actually, standard soil profiles in this app are user-entered layers, usually sorted.
    # If we sort, we must sort all arrays together.
    if len(depths) > 1 and depths[0] > depths[-1]:
         # Reverse if descending
         depths.reverse()
         eff_unit_weights.reverse()
         k_values.reverse()
         delta_values.reverse()
    
    # Check if depths are unique and ascending
    # Groundhog requirement: "order: ascending, unique: True"
    # If there are duplicates, we might need to filter or warn.
    # For now, let's proceed.

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
                "x": res['negative_skin_friction_profile_single [kN]'],
                "y": depths,
                "type": "scatter",
                "mode": "lines",
                "name": "Single Pile NSF",
                "orientation": "h"
             })
        if 'negative_skin_friction_profile_group [kN]' in res:
             charts.append({
                "x": res['negative_skin_friction_profile_group [kN]'],
                "y": depths,
                "type": "scatter",
                "mode": "lines",
                "name": "Group Pile NSF",
                "orientation": "h"
             })
             
        # Add effective stress profiles if available
        if 'virgin_effective_stress [kPa]' in res:
             charts.append({
                "x": res['virgin_effective_stress [kPa]'],
                "y": depths,
                "type": "scatter",
                "mode": "lines",
                "name": "Virgin Eff. Stress",
                "orientation": "h",
                "visible": "legendonly"
             })
        if 'group_effective_stress [kPa]' in res:
             charts.append({
                "x": res['group_effective_stress [kPa]'],
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
