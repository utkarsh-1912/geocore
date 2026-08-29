# Author: Utkarsh Gupta
# License: GPL v3
"""
Automated Test Suite for Geotechnical Project Context, Stratigraphy Slicing,
and Multi-Parameter Context Resolution.
"""

import pytest
import pandas as pd
import numpy as np

from core.geoai.data_access import SoilLayerSlice, SoilProfileAccessor, ProjectContext
from core.geoai.context_resolver import ContextResolver, PROPERTY_SYNONYMS
from core.geoai.provenance import create_calculation_provenance
from core.geoai.system_prompt import build_system_prompt


@pytest.fixture
def sample_stratigraphy_df():
    """3-layer representative soil stratigraphy."""
    return pd.DataFrame([
        {
            "Depth from [m]": 0.0,
            "Depth to [m]": 3.0,
            "Soil type": "Soft Clay",
            "Friction angle [deg]": 0.0,
            "Cohesion [kPa]": 25.0,
            "Unit weight [kN/m3]": 17.5,
            "Su [kPa]": 35.0,
            "Vs [m/s]": 140.0
        },
        {
            "Depth from [m]": 3.0,
            "Depth to [m]": 8.0,
            "Soil type": "Medium Dense Sand",
            "Friction angle [deg]": 33.0,
            "Cohesion [kPa]": 0.0,
            "Unit weight [kN/m3]": 19.0,
            "Su [kPa]": np.nan,
            "Vs [m/s]": 260.0
        },
        {
            "Depth from [m]": 8.0,
            "Depth to [m]": 15.0,
            "Soil type": "Stiff Silt / Clay",
            "Friction angle [deg]": 22.0,
            "Cohesion [kPa]": 15.0,
            "Unit weight [kN/m3]": 18.5,
            "Su [kPa]": 90.0,
            "Vs [m/s]": 310.0
        }
    ])


# =====================================================================
# 1. SoilProfileAccessor Stratigraphy & Representative Evaluation
# =====================================================================

def test_soil_profile_accessor_stratigraphy(sample_stratigraphy_df):
    accessor = SoilProfileAccessor(sample_stratigraphy_df)
    assert accessor.total_depth == 15.0
    assert accessor.layer_count == 3

    summary = accessor.get_stratigraphy_summary()
    assert len(summary) == 3
    assert summary[0]["soil_type"] == "Soft Clay"
    assert summary[1]["soil_type"] == "Medium Dense Sand"
    assert summary[2]["soil_type"] == "Stiff Silt / Clay"


def test_soil_profile_representative_parameters(sample_stratigraphy_df):
    accessor = SoilProfileAccessor(sample_stratigraphy_df)
    
    # Layer 1 only: [0, 2] m -> gamma = 17.5
    params_top = accessor.get_representative_parameters(0.0, 2.0)
    assert params_top["Unit weight [kN/m3]"] == pytest.approx(17.5)

    # Straddling Layer 1 (3m @ 17.5) and Layer 2 (3m @ 19.0) -> interval [0, 6] m
    # Weighted avg = (3*17.5 + 3*19.0) / 6 = 18.25
    params_straddle = accessor.get_representative_parameters(0.0, 6.0)
    assert params_straddle["Unit weight [kN/m3]"] == pytest.approx(18.25)


# =====================================================================
# 2. ProjectContext Memory & Compact Markdown Formatting
# =====================================================================

def test_project_context_memory(sample_stratigraphy_df):
    ctx = ProjectContext(project_id="PROJ-001", name="Offshore Wind Farm Site A")
    ctx.water_table_depth = 1.5
    ctx.add_profile("BH-01", sample_stratigraphy_df)

    assert "BH-01" in ctx.list_profile_names()
    assert ctx.water_table_depth == 1.5

    # Add calculation history
    prov = create_calculation_provenance(
        tool_name="calculate_earth_pressure_rankine",
        sanitized_inputs={"phi_eff": 33.0, "wall_angle": 0.0}
    )
    ctx.add_calculation(prov)
    history = ctx.get_calculation_history()
    assert len(history) == 1
    assert history[0].tool_name == "calculate_earth_pressure_rankine"

    # Verify compact context markdown
    summary_md = ctx.get_compact_context_string()
    assert "PROJECT STRATIGRAPHY: Offshore Wind Farm Site A" in summary_md
    assert "Groundwater Level (GWT): 1.5 m" in summary_md
    assert "Soft Clay" in summary_md
    assert "Medium Dense Sand" in summary_md
    assert "Recent Calculation History" in summary_md
    assert "calculate_earth_pressure_rankine" in summary_md


# =====================================================================
# 3. ContextResolver Geotechnical Parameter Resolution
# =====================================================================

def test_context_resolver_synonyms(sample_stratigraphy_df):
    ctx = ProjectContext(project_id="PROJ-001")
    ctx.add_profile("BH-01", sample_stratigraphy_df)
    resolver = ContextResolver(ctx)

    # In layer 1 (depth = 1.5m): Su = 35, gamma = 17.5
    assert resolver.resolve_parameter_at_depth("su", depth=1.5) == 35.0
    assert resolver.resolve_parameter_at_depth("gamma", depth=1.5) == 17.5
    assert resolver.resolve_parameter_at_depth("Vs", depth=1.5) == 140.0

    # In layer 2 (depth = 5.0m): phi_eff = 33, gamma = 19.0
    assert resolver.resolve_parameter_at_depth("phi_eff", depth=5.0) == 33.0
    assert resolver.resolve_parameter_at_depth("unit_weight", depth=5.0) == 19.0
    assert resolver.resolve_parameter_at_depth("Vs", depth=5.0) == 260.0


def test_context_resolver_foundation_influence_zone(sample_stratigraphy_df):
    ctx = ProjectContext(project_id="PROJ-001")
    ctx.add_profile("BH-01", sample_stratigraphy_df)
    resolver = ContextResolver(ctx)

    # Foundation at Df = 2.0m, B = 2.0m -> zone [2.0, 5.0]m
    # Overlap Layer 1 [2.0, 3.0] (1m @ 17.5) + Layer 2 [3.0, 5.0] (2m @ 19.0)
    # Weighted avg gamma = (1*17.5 + 2*19.0) / 3 = 55.5 / 3 = 18.5
    zone_params = resolver.resolve_layer_for_foundation(footing_depth=2.0, footing_width=2.0)
    assert zone_params["Unit weight [kN/m3]"] == pytest.approx(18.5)


def test_context_resolver_fill_missing_parameters(sample_stratigraphy_df):
    ctx = ProjectContext(project_id="PROJ-001")
    ctx.add_profile("BH-01", sample_stratigraphy_df)
    resolver = ContextResolver(ctx)

    # User supplied depth z = 4.0m, but omitted phi_eff and gamma
    partial_args = {
        "z": 4.0,
        "phi_eff": None,
        "gamma": None,
        "wall_angle": 0.0
    }
    filled = resolver.fill_missing_parameters(partial_args)
    assert filled["z"] == 4.0
    assert filled["phi_eff"] == 33.0    # From Layer 2 Sand
    assert filled["gamma"] == 19.0      # From Layer 2 Sand
    assert filled["wall_angle"] == 0.0  # Preserved


# =====================================================================
# 4. System Prompt Context Injection
# =====================================================================

def test_system_prompt_with_project_context(sample_stratigraphy_df):
    ctx = ProjectContext(project_id="PROJ-001", name="Harbor Terminal Expansion")
    ctx.water_table_depth = 2.0
    ctx.add_profile("BH-01", sample_stratigraphy_df)

    context_dict = {
        "activeFunction": "calculate_earth_pressure_rankine",
        "activeCategory": "excavations",
        "project_context": ctx
    }

    prompt = build_system_prompt(context_dict)
    assert "Harbor Terminal Expansion" in prompt
    assert "Groundwater Level (GWT): 2.0 m" in prompt
    assert "Soft Clay" in prompt
    assert "Active Calculation Tool: calculate_earth_pressure_rankine" in prompt
