import pytest
import pandas as pd
import numpy as np

from core.geoai.data_access import SoilLayerSlice, SoilProfileAccessor, ProjectContext
from core.geoai.context_resolver import ContextResolver


# =====================================================================
# 1. SoilLayerSlice tests
# =====================================================================

def test_soil_layer_slice_creation():
    data = {"Soil type": "Clay", "qc [MPa]": 5.0}
    layer = SoilLayerSlice(data)
    
    # Test get method
    assert layer.get("qc [MPa]") == 5.0
    assert layer.get("Soil type") == "Clay"
    
def test_soil_layer_slice_attribute_access():
    data = {"Soil type": "Clay", "depth_from": 0.0}
    layer = SoilLayerSlice(data)
    
    assert layer.depth_from == 0.0
    
    with pytest.raises(AttributeError, match="Layer property 'nonexistent' not found."):
        _ = layer.nonexistent

def test_soil_layer_slice_get():
    data = {"Su [kPa]": 50.0}
    layer = SoilLayerSlice(data)
    
    assert layer.get("Su [kPa]") == 50.0
    assert layer.get("Missing", default=100.0) == 100.0

def test_soil_layer_slice_to_dict():
    data = {"Soil type": "Sand", "gamma": 18.5}
    layer = SoilLayerSlice(data)
    
    assert layer.to_dict() == data
    assert layer.to_dict() is not data  # Ensure it's a copy


# =====================================================================
# 2. SoilProfileAccessor tests
# =====================================================================

@pytest.fixture
def sample_profile_df():
    return pd.DataFrame([
        {'Depth from [m]': 0, 'Depth to [m]': 3, 'qc [MPa]': 5, 'Soil type': 'Clay', 'gamma [kN/m3]': 16.0},
        {'Depth from [m]': 3, 'Depth to [m]': 7, 'qc [MPa]': 15, 'Soil type': 'Sand', 'gamma [kN/m3]': 19.0},
        {'Depth from [m]': 7, 'Depth to [m]': 12, 'qc [MPa]': 8, 'Soil type': 'Silt', 'gamma [kN/m3]': 17.5},
    ])

@pytest.fixture
def profile_accessor(sample_profile_df):
    return SoilProfileAccessor(sample_profile_df)

def test_soil_profile_accessor_properties(profile_accessor):
    assert profile_accessor.total_depth == 12.0
    assert profile_accessor.layer_count == 3

def test_soil_profile_accessor_get_layer_at_depth(profile_accessor):
    # Within first layer
    layer_1 = profile_accessor.get_layer_at_depth(1.5)
    assert layer_1 is not None
    assert layer_1.get("Soil type") == "Clay"

    # Within second layer
    layer_2 = profile_accessor.get_layer_at_depth(5.0)
    assert layer_2 is not None
    assert layer_2.get("Soil type") == "Sand"

    # Within third layer
    layer_3 = profile_accessor.get_layer_at_depth(10.0)
    assert layer_3 is not None
    assert layer_3.get("Soil type") == "Silt"

    # Negative depth
    assert profile_accessor.get_layer_at_depth(-1) is None

    # Beyond total depth
    assert profile_accessor.get_layer_at_depth(15.0) is None

def test_soil_profile_accessor_get_interval(profile_accessor):
    # From 2.0 to 8.0, should span Clay (0-3), Sand (3-7), and Silt (7-12)
    interval_layers = profile_accessor.get_interval(2.0, 8.0)
    assert len(interval_layers) == 3
    assert interval_layers[0].get("Soil type") == "Clay"
    assert interval_layers[1].get("Soil type") == "Sand"
    assert interval_layers[2].get("Soil type") == "Silt"

def test_soil_profile_accessor_get_property_profile(profile_accessor):
    z_grid, values = profile_accessor.get_property_profile('qc [MPa]', dz=1.0)
    assert len(z_grid) == 13  # 0.0 to 12.0 inclusive with dz=1.0
    
    # Check values at specific depths
    assert values[np.where(z_grid == 1.0)[0][0]] == 5.0
    assert values[np.where(z_grid == 5.0)[0][0]] == 15.0
    assert values[np.where(z_grid == 10.0)[0][0]] == 8.0


# =====================================================================
# 3. ProjectContext tests
# =====================================================================

def test_project_context_creation():
    ctx = ProjectContext(project_id="test_proj", name="Test Project")
    assert ctx.project_id == "test_proj"
    assert ctx.name == "Test Project"
    assert ctx.water_table_depth == 0.0

def test_project_context_profiles(sample_profile_df):
    ctx = ProjectContext(project_id="test_proj")
    
    # Test add_profile
    accessor = ctx.add_profile("cpt_1", sample_profile_df)
    assert isinstance(accessor, SoilProfileAccessor)
    
    # Test get_profile with name
    retrieved = ctx.get_profile("cpt_1")
    assert retrieved is accessor
    
    # Test get_profile with no name (returns first)
    first = ctx.get_profile()
    assert first is accessor
    
    # Test get_profile with non-existent name
    assert ctx.get_profile("nonexistent") is None


# =====================================================================
# 4. ContextResolver tests
# =====================================================================

@pytest.fixture
def context_resolver(sample_profile_df):
    ctx = ProjectContext("test_proj")
    ctx.add_profile("primary", sample_profile_df)
    return ContextResolver(ctx)

def test_context_resolver_resolve_parameter(context_resolver):
    # Test exact match
    val = context_resolver.resolve_parameter_at_depth('Soil type', 5.0)
    assert val == "Sand"
    
    # Test synonym resolution: 'unit_weight' -> 'gamma [kN/m3]'
    # At depth 1.5, gamma [kN/m3] is 16.0
    gamma = context_resolver.resolve_parameter_at_depth('unit_weight', 1.5)
    assert gamma == 16.0
    
    # Test unknown parameter
    assert context_resolver.resolve_parameter_at_depth('unknown_param', 1.5) is None
    
    # Test beyond depth
    assert context_resolver.resolve_parameter_at_depth('unit_weight', 20.0) is None

def test_context_resolver_fill_missing_parameters(context_resolver):
    func_args = {
        'depth': 5.0,
        'unit_weight': None,  # Should be filled (19.0)
        'su_base': None,      # Cannot be filled (missing from df)
        'custom_val': 42.0    # Should remain unchanged
    }
    
    resolved = context_resolver.fill_missing_parameters(func_args, depth_param='depth')
    
    assert resolved['depth'] == 5.0
    assert resolved['unit_weight'] == 19.0
    assert resolved['su_base'] is None
    assert resolved['custom_val'] == 42.0
