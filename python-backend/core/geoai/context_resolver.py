# Author: Utkarsh Gupta
# License: GPL v3
"""
Geotechnical Context Parameter Resolver.
Resolves missing calculation inputs and representative layer properties on-demand
from active project stratigraphy and SoilProfiles.
"""

from typing import Dict, Any, Optional, List, Union
import numpy as np
from core.geoai.data_access import ProjectContext, SoilProfileAccessor, SoilLayerSlice


PROPERTY_SYNONYMS: Dict[str, List[str]] = {
    'phi_eff': ['Friction angle [deg]', 'friction_angle', 'phi', 'phi [deg]', 'phi_eff', 'effective_friction_angle', 'phi_p'],
    'friction_angle': ['Friction angle [deg]', 'friction_angle', 'phi', 'phi [deg]', 'phi_eff'],
    'c_eff': ['Cohesion [kPa]', 'cohesion', 'c', 'c [kPa]', 'c_eff', 'effective_cohesion', "c'"],
    'cohesion': ['Cohesion [kPa]', 'cohesion', 'c', 'c [kPa]', 'c_eff'],
    'gamma': ['Unit weight [kN/m3]', 'unit_weight', 'gamma', 'gamma [kN/m3]', 'Total unit weight [kN/m3]', 'bulk_unit_weight', 'gamma_bulk', 'gamma_tot'],
    'unit_weight': ['Unit weight [kN/m3]', 'unit_weight', 'gamma', 'gamma [kN/m3]', 'Total unit weight [kN/m3]'],
    'su': ['Su [kPa]', 'su', 'undrained_shear_strength', 'su [kPa]', 'cu', 'undrained shear strength', 's_u'],
    'su_base': ['Su [kPa]', 'su', 'undrained_shear_strength', 'su [kPa]'],
    'Vs': ['Vs [m/s]', 'Vs', 'vs', 'shear_wave_velocity', 'shear velocity', 'Vs [m/sec]'],
    'Gmax': ['Gmax [kPa]', 'Gmax', 'gmax', 'small_strain_shear_modulus'],
    'poissonsratio': ['Poissons ratio [-]', 'nu', 'poissonsratio', 'poisson', "poisson's ratio", 'v'],
    'void_ratio': ['Void ratio [-]', 'e', 'voidratio', 'void_ratio'],
    'porosity': ['Porosity [-]', 'n', 'porosity'],
    'Dr': ['Relative density [%]', 'Dr', 'relative_density', 'dr'],
    'k': ['Hydraulic conductivity [m/s]', 'permeability', 'k', 'k [m/s]'],
}


class ContextResolver:
    """
    Resolves required function parameters from geotechnical project stratigraphy and SoilProfiles.
    """
    def __init__(self, context: ProjectContext):
        self.context = context

    def resolve_parameter_at_depth(
        self,
        param_name: str,
        depth: float,
        profile_name: Optional[str] = None
    ) -> Optional[Any]:
        """
        Retrieves a parameter value from the soil stratigraphy at depth z [m].
        Searches exact column names, canonical names, and geotechnical synonyms.
        """
        profile = self.context.get_profile(profile_name)
        if not profile:
            return None

        layer = profile.get_layer_at_depth(depth)
        if not layer:
            return None

        # 1. Exact match
        if layer.get(param_name) is not None:
            return layer.get(param_name)

        # 2. Check synonyms
        synonyms = PROPERTY_SYNONYMS.get(param_name, [])
        for syn in synonyms:
            val = layer.get(syn)
            if val is not None:
                return val

        # 3. Check reverse synonym matches
        for canon, syn_list in PROPERTY_SYNONYMS.items():
            if param_name in syn_list:
                for syn in [canon] + syn_list:
                    val = layer.get(syn)
                    if val is not None:
                        return val

        return None

    def resolve_layer_for_foundation(
        self,
        footing_depth: float,
        footing_width: float,
        profile_name: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Calculates representative depth-weighted soil parameters over the foundation
        influence zone [Df, Df + 1.5*B].
        """
        profile = self.context.get_profile(profile_name)
        if not profile:
            return {}

        z_top = max(0.0, footing_depth)
        z_bottom = z_top + max(0.5, 1.5 * footing_width)
        return profile.get_representative_parameters(z_top, z_bottom)

    def fill_missing_parameters(
        self,
        func_args: Dict[str, Any],
        depth_param: str = 'z',
        profile_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Automatically fills any omitted (None) arguments using properties from the active
        soil profile evaluated at the target depth.
        """
        # Determine depth from args or default to 1.0 m
        depth = 1.0
        for d_key in (depth_param, 'z', 'depth', 'penetration', 'z_p', 'h1', 'footing_depth'):
            if func_args.get(d_key) is not None:
                try:
                    depth = float(func_args[d_key])
                    break
                except (ValueError, TypeError):
                    pass

        resolved_args = dict(func_args)

        for k, v in list(resolved_args.items()):
            if v is None:
                auto_val = self.resolve_parameter_at_depth(k, depth, profile_name)
                if auto_val is not None:
                    resolved_args[k] = auto_val

        return resolved_args
