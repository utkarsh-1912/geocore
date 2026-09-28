# Author: Utkarsh Gupta
# License: GPL v3
"""
Hand-computed checks for the stress components that the GeoAI tool wrappers
recompute because the installed Groundhog formulas are wrong
(see core/geoai/tool_definitions.py).
"""

import pytest

from core.geoai.tool_registry import tool_registry
import core.geoai.tool_definitions


def _component(result, field, groundhog_key):
    # Accept either the canonical schema field or Groundhog's raw key, so these
    # checks hold whether or not the output model normalizes the result.
    return result[field] if field in result else result[groundhog_key]


def test_circular_footing_sigma_r_poulos_davis():
    # sigma_r = q/2 * [(1 + 2nu) - 2(1 + nu) a + a^3], a = z / sqrt(R^2 + z^2) = 2 / sqrt(5)
    #         = 50 * (1.6 - 2.6 * 0.894427 + 0.715542)  (default nu = 0.3)
    result = tool_registry.invoke_tool(
        "calculate_stresses_circular_footing",
        {"z": 2.0, "footing_radius": 1.0, "imposedstress": 100.0},
    )
    assert _component(result, "sigma_r", "delta sigma r [kPa]") == pytest.approx(-0.4984472, rel=1e-5)
    # sigma_z = q * [1 - (z^2 / (R^2 + z^2))^1.5] is Groundhog's and unchanged
    assert _component(result, "sigma_z", "delta sigma z [kPa]") == pytest.approx(100.0 * (1.0 - 0.8 ** 1.5), rel=1e-5)


def test_circular_footing_sigma_r_at_surface_and_depth():
    # z -> 0: sigma_r -> q (1 + 2nu) / 2 = 80 kPa (Groundhog itself returns NaN at z = 0,
    # so use a very small depth); z -> infinity: sigma_r -> 0 (Groundhog gave -q(1 + nu)).
    shallow = tool_registry.invoke_tool(
        "calculate_stresses_circular_footing",
        {"z": 1e-6, "footing_radius": 1.0, "imposedstress": 100.0, "poissonsratio": 0.3},
    )
    deep = tool_registry.invoke_tool(
        "calculate_stresses_circular_footing",
        {"z": 400.0, "footing_radius": 1.0, "imposedstress": 100.0, "poissonsratio": 0.3},
    )
    assert _component(shallow, "sigma_r", "delta sigma r [kPa]") == pytest.approx(80.0, abs=1e-3)
    assert _component(deep, "sigma_r", "delta sigma r [kPa]") == pytest.approx(0.0, abs=1e-3)


def test_point_load_sigma_theta_off_axis():
    # Q = 100 kN, z = 2 m, r = 1 m, nu = 0.3, R = sqrt(5):
    # sigma_theta = Q / (2 pi) * (1 - 2nu) * [1 / (R (R + z)) - z / R^3]
    #             = 15.915494 * 0.4 * (0.105573 - 0.178885)
    result = tool_registry.invoke_tool(
        "calculate_stresses_point_load",
        {"pointload": 100.0, "z": 2.0, "r": 1.0, "poissonsratio": 0.3},
    )
    assert _component(result, "sigma_theta", "delta sigma theta [kPa]") == pytest.approx(-0.4667227, rel=1e-5)
    assert _component(result, "sigma_r", "delta sigma r [kPa]") == pytest.approx(1.036133, rel=1e-5)


def test_point_load_sigma_theta_equals_sigma_r_on_axis():
    # r = 0: axisymmetry requires sigma_theta == sigma_r = -Q (1 - 2nu) / (4 pi z^2)
    #      = -100 * 0.4 / (16 pi)
    result = tool_registry.invoke_tool(
        "calculate_stresses_point_load",
        {"pointload": 100.0, "z": 2.0, "r": 0.0, "poissonsratio": 0.3},
    )
    assert _component(result, "sigma_theta", "delta sigma theta [kPa]") == pytest.approx(-0.7957747, rel=1e-5)
    assert _component(result, "sigma_r", "delta sigma r [kPa]") == pytest.approx(-0.7957747, rel=1e-5)


def test_groundhog_rejection_stays_nan():
    # Groundhog only accepts 0 <= nu <= 0.5 and returns NaN otherwise; the wrapper must
    # not fill in a corrected number next to a rejected calculation.
    result = tool_registry.invoke_tool(
        "calculate_stresses_point_load",
        {"pointload": 100.0, "z": 2.0, "r": 1.0, "poissonsratio": -0.2},
    )
    theta = _component(result, "sigma_theta", "delta sigma theta [kPa]")
    assert theta != theta  # NaN
