import pytest

import core.geoai.tool_definitions  # noqa: F401  registers curated tools
from core.geoai.tool_registry import tool_registry


def test_relative_density_uses_conventional_void_ratio_limits():
    # Dr = (e_max - e) / (e_max - e_min) with e_min = densest, e_max = loosest
    out = tool_registry.invoke_tool("calculate_relative_density", {"void_ratio": 0.6, "e_min": 0.4, "e_max": 0.9})
    assert out["Dr [-]"] == pytest.approx(0.6)


def test_relative_density_dense_sample_is_high():
    out = tool_registry.invoke_tool("calculate_relative_density", {"void_ratio": 0.45, "e_min": 0.4, "e_max": 0.9})
    assert out["Dr [-]"] == pytest.approx(0.9)


def test_relative_density_form_arg_map_is_published():
    info = next(t for t in tool_registry.list_tools() if t["name"] == "calculate_relative_density")
    assert info["form_function"] == "relative_density"
    assert info["form_arg_map"] == {"e_min": "e_max", "e_max": "e_min"}
