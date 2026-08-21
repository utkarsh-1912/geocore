"""
Lazy Geotechnical Data Access Layer
Provides on-demand, immutable, sliceable access to Soil Profiles, CPT soundings, and Borehole data.
"""
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from core.state import state_manager


class SoilLayerSlice:
    """Represents an immutable slice of a soil layer."""
    def __init__(self, data: Dict[str, Any]):
        self._data = dict(data)

    def __getattr__(self, name: str) -> Any:
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"Layer property '{name}' not found.")

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)


class SoilProfileAccessor:
    """Lazy accessor wrapping SoilProfile objects."""
    def __init__(self, profile_obj: Any):
        self._profile = profile_obj
        if hasattr(profile_obj, 'layer_table'):
            self._df = profile_obj.layer_table
        elif isinstance(profile_obj, pd.DataFrame):
            self._df = profile_obj
        elif isinstance(profile_obj, list):
            self._df = pd.DataFrame(profile_obj)
        else:
            raise ValueError("Unsupported soil profile data format.")

        # Identify depth columns
        self._z_from_col = next((c for c in self._df.columns if 'from' in c.lower()), 'Depth from [m]')
        self._z_to_col = next((c for c in self._df.columns if 'to' in c.lower()), 'Depth to [m]')

    @property
    def total_depth(self) -> float:
        if self._z_to_col in self._df.columns:
            return float(self._df[self._z_to_col].max())
        return 0.0

    @property
    def layer_count(self) -> int:
        return len(self._df)

    def get_layer_at_depth(self, z: float) -> Optional[SoilLayerSlice]:
        """Fetch soil layer properties at a specific depth z [m]."""
        if z < 0:
            return None
        match = self._df[(self._df[self._z_from_col] <= z) & (self._df[self._z_to_col] >= z)]
        if not match.empty:
            return SoilLayerSlice(match.iloc[0].to_dict())
        # If at exact boundary or slightly past bottom, check closest
        if z <= self.total_depth:
            match = self._df[self._df[self._z_to_col] >= z]
            if not match.empty:
                return SoilLayerSlice(match.iloc[0].to_dict())
        return None

    def get_interval(self, z_top: float, z_bottom: float) -> List[SoilLayerSlice]:
        """Fetch all layer slices spanning between z_top and z_bottom."""
        match = self._df[(self._df[self._z_to_col] >= z_top) & (self._df[self._z_from_col] <= z_bottom)]
        return [SoilLayerSlice(row.to_dict()) for _, row in match.iterrows()]

    def get_property_profile(self, prop_name: str, dz: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """Evaluate continuous/step profile for a given property across depth grid."""
        z_grid = np.arange(0.0, self.total_depth + dz, dz)
        values = []
        for z in z_grid:
            layer = self.get_layer_at_depth(z)
            val = layer.get(prop_name, np.nan) if layer else np.nan
            values.append(val)
        return z_grid, np.array(values)


class ProjectContext:
    """
    Project-level geotechnical container.
    Provides lazy resolution for multi-modal site investigation data.
    """
    def __init__(self, project_id: str, name: str = "Default Project"):
        self.project_id = project_id
        self.name = name
        self.water_table_depth: float = 0.0
        self._profiles: Dict[str, SoilProfileAccessor] = {}
        self._custom_data: Dict[str, Any] = {}

    def add_profile(self, name: str, profile_obj: Any) -> SoilProfileAccessor:
        accessor = SoilProfileAccessor(profile_obj)
        self._profiles[name] = accessor
        return accessor

    def get_profile(self, name: Optional[str] = None) -> Optional[SoilProfileAccessor]:
        if name and name in self._profiles:
            return self._profiles[name]
        if not name and self._profiles:
            return next(iter(self._profiles.values()))
        return None

    @classmethod
    def from_state_manager(cls, profile_id: str) -> "ProjectContext":
        """Instantiate project context directly from a registered state object."""
        obj = state_manager.get(profile_id)
        if obj is None:
            raise ValueError(f"State object '{profile_id}' not found.")
        ctx = cls(project_id=profile_id, name=f"Context for {profile_id}")
        ctx.add_profile("primary", obj)
        return ctx
