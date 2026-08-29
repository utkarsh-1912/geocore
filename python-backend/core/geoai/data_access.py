# Author: Utkarsh Gupta
# License: GPL v3
"""
Lazy Geotechnical Data Access Layer & Project Memory Container.
Provides on-demand, immutable, sliceable access to Soil Profiles,
Stratigraphy tables, Groundwater context, and Calculation History.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from core.state import state_manager
from core.geoai.provenance import CalculationProvenance


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
        if hasattr(profile_obj, 'layer_table') and isinstance(profile_obj.layer_table, pd.DataFrame):
            self._df = profile_obj.layer_table
        elif isinstance(profile_obj, pd.DataFrame):
            self._df = profile_obj
        elif isinstance(profile_obj, list):
            self._df = pd.DataFrame(profile_obj)
        elif hasattr(profile_obj, 'df') and isinstance(profile_obj.df, pd.DataFrame):
            self._df = profile_obj.df
        else:
            try:
                self._df = pd.DataFrame(profile_obj)
            except Exception as e:
                raise ValueError(f"Unsupported soil profile data format: {e}")

        # Identify depth columns
        self._z_from_col = next((c for c in self._df.columns if 'from' in c.lower()), 'Depth from [m]')
        self._z_to_col = next((c for c in self._df.columns if 'to' in c.lower()), 'Depth to [m]')

    @property
    def layer_table(self) -> pd.DataFrame:
        return self._df

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
        # If at boundary or slightly past bottom, return deepest layer within total depth
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

    def get_stratigraphy_summary(self) -> List[Dict[str, Any]]:
        """Returns clean list of layers with core geotechnical parameters."""
        summary = []
        for idx, row in self._df.iterrows():
            layer_dict = {
                "layer": idx + 1,
                "z_from": float(row.get(self._z_from_col, 0.0)),
                "z_to": float(row.get(self._z_to_col, 0.0)),
                "soil_type": str(row.get("Soil type", row.get("Soil description", row.get("soil_type", "Soil")))),
            }
            # Add numeric properties if present
            for col in self._df.columns:
                if col not in (self._z_from_col, self._z_to_col, "Soil type", "Soil description"):
                    val = row[col]
                    if pd.notna(val) and isinstance(val, (int, float, np.number)):
                        layer_dict[col] = float(val)
            summary.append(layer_dict)
        return summary

    def get_representative_parameters(self, z_top: float, z_bottom: float) -> Dict[str, float]:
        """
        Calculates depth-weighted average of soil properties across a depth interval [z_top, z_bottom].
        Ideal for foundation bearing capacity and settlement influence zones.
        """
        if z_bottom <= z_top:
            layer = self.get_layer_at_depth(z_top)
            if not layer:
                return {}
            return {k: v for k, v in layer.to_dict().items() if isinstance(v, (int, float, np.number))}

        total_span = z_bottom - z_top
        weighted_sums: Dict[str, float] = {}
        total_weights: Dict[str, float] = {}

        for _, row in self._df.iterrows():
            l_from = float(row.get(self._z_from_col, 0.0))
            l_to = float(row.get(self._z_to_col, 0.0))

            # Overlap with [z_top, z_bottom]
            overlap_top = max(z_top, l_from)
            overlap_bottom = min(z_bottom, l_to)
            dz = overlap_bottom - overlap_top

            if dz > 0:
                for col in self._df.columns:
                    val = row[col]
                    if pd.notna(val) and isinstance(val, (int, float, np.number)):
                        weighted_sums[col] = weighted_sums.get(col, 0.0) + float(val) * dz
                        total_weights[col] = total_weights.get(col, 0.0) + dz

        representative = {}
        for prop, w_sum in weighted_sums.items():
            if total_weights.get(prop, 0.0) > 0:
                representative[prop] = w_sum / total_weights[prop]

        return representative


class ProjectContext:
    """
    Project-level geotechnical memory container.
    Provides lazy resolution for multi-modal site investigation data,
    active stratigraphy, groundwater context, and calculation history.
    """
    def __init__(self, project_id: str, name: str = "Default Project"):
        self.project_id = project_id
        self.name = name
        self.water_table_depth: float = 0.0
        self._profiles: Dict[str, SoilProfileAccessor] = {}
        self._calculation_history: List[CalculationProvenance] = []
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

    def list_profile_names(self) -> List[str]:
        return list(self._profiles.keys())

    def add_calculation(self, provenance: Union[CalculationProvenance, Dict[str, Any]]) -> None:
        """Appends a calculation provenance record to project calculation history."""
        if isinstance(provenance, dict):
            prov_obj = CalculationProvenance(**provenance)
        else:
            prov_obj = provenance
        self._calculation_history.append(prov_obj)

    def get_calculation_history(self, limit: Optional[int] = None) -> List[CalculationProvenance]:
        """Returns the most recent calculation history records."""
        if limit:
            return self._calculation_history[-limit:]
        return list(self._calculation_history)

    def get_compact_context_string(self, max_tokens: int = 500) -> str:
        """
        Builds a concise, token-efficient Markdown representation of the project
        stratigraphy, groundwater level, and recent calculations.
        Fits within strict SLM context budgets (typically ~150-300 tokens).
        """
        lines = [f"### PROJECT STRATIGRAPHY: {self.name}"]
        lines.append(f"- Groundwater Level (GWT): {self.water_table_depth} m below ground surface")

        profile = self.get_profile()
        if profile and profile.layer_count > 0:
            lines.append("\n**Active Soil Stratigraphy**:")
            lines.append("| Layer | Depth [m] | Soil Type | Properties |")
            lines.append("|---|---|---|---|")
            for layer in profile.get_stratigraphy_summary():
                z_range = f"{layer['z_from']:.1f} - {layer['z_to']:.1f} m"
                soil_type = layer.get("soil_type", "Soil")
                
                # Format properties compactly
                prop_snippets = []
                for k, v in layer.items():
                    if k not in ("layer", "z_from", "z_to", "soil_type"):
                        clean_k = k.split("[")[0].strip()
                        prop_snippets.append(f"{clean_k}={v:.1f}")
                
                props_str = ", ".join(prop_snippets) if prop_snippets else "-"
                lines.append(f"| {layer['layer']} | {z_range} | {soil_type} | {props_str} |")
        else:
            lines.append("- Soil Profile: No stratigraphy profile loaded in active workspace.")

        if self._calculation_history:
            lines.append("\n**Recent Calculation History**:")
            for calc in self._calculation_history[-3:]:
                lines.append(f"- `{calc.tool_name}`: {calc.method} (UTC: {calc.timestamp_utc[:16]})")

        return "\n".join(lines)

    @classmethod
    def from_state_manager(cls, profile_id: Optional[str] = None) -> "ProjectContext":
        """
        Instantiate project context directly from registered workspace state objects.
        If profile_id is None, automatically loads all registered SoilProfiles.
        """
        ctx = cls(project_id="workspace_active", name="Active Workspace Project")
        
        if profile_id:
            obj = state_manager.get(profile_id)
            if obj is not None:
                ctx.add_profile(profile_id, obj)
        else:
            # Discover all SoilProfiles in StateManager
            for obj_id, meta in state_manager._metadata.items():
                if meta.get("type") == "SoilProfile":
                    obj = state_manager.get(obj_id)
                    if obj is not None:
                        ctx.add_profile(meta.get("name", obj_id), obj)

        return ctx


# Active Global Project Memory Singleton
active_project_context = ProjectContext("default_session", "Active Session")
