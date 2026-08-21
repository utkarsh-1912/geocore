"""
Geotechnical Context Parameter Resolver
Resolves missing calculation inputs on-demand from a ProjectContext.
"""
from typing import Dict, Any, Optional
from core.geoai.data_access import ProjectContext, SoilProfileAccessor

PROPERTY_SYNONYMS = {
    'friction_angle': ['Friction angle [deg]', 'friction_angle', 'phi', 'phi [deg]'],
    'cohesion': ['Cohesion [kPa]', 'cohesion', 'c', 'c [kPa]'],
    'unit_weight': ['Unit weight [kN/m3]', 'unit_weight', 'gamma', 'gamma [kN/m3]', 'Total unit weight [kN/m3]'],
    'su_base': ['Su [kPa]', 'su', 'undrained_shear_strength', 'su [kPa]'],
    'void_ratio': ['Void ratio [-]', 'e', 'voidratio'],
}

class ContextResolver:
    """Resolves required function parameters from geotechnical project context."""
    def __init__(self, context: ProjectContext):
        self.context = context

    def resolve_parameter_at_depth(self, param_name: str, depth: float, profile_name: Optional[str] = None) -> Optional[Any]:
        profile = self.context.get_profile(profile_name)
        if not profile:
            return None

        layer = profile.get_layer_at_depth(depth)
        if not layer:
            return None

        # Check exact name
        if layer.get(param_name) is not None:
            return layer.get(param_name)

        # Check synonyms
        synonyms = PROPERTY_SYNONYMS.get(param_name, [])
        for syn in synonyms:
            val = layer.get(syn)
            if val is not None:
                return val

        return None

    def fill_missing_parameters(self, func_args: Dict[str, Any], depth_param: str = 'z', profile_name: Optional[str] = None) -> Dict[str, Any]:
        """Automatically fills any None / omitted arguments using property values at specified depth."""
        depth = float(func_args.get(depth_param, func_args.get('depth', 0.0)))
        resolved_args = dict(func_args)

        for k, v in list(resolved_args.items()):
            if v is None:
                auto_val = self.resolve_parameter_at_depth(k, depth, profile_name)
                if auto_val is not None:
                    resolved_args[k] = auto_val

        return resolved_args
