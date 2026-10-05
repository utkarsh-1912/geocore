# Author: Utkarsh Gupta
# License: GPL v3
"""
Desktop calculators for groundhog.constitutivemodels.general.mohrcoulomb_triaxial_compression /
_extension: the registry returns the Mohr circle figure plus the failure stresses as a table.
"""
import math

import pytest

from core.registry import Registry


@pytest.fixture(scope="module")
def registry():
    return Registry()


def _values(res):
    assert res["type"] == "multi_plot", res
    assert res["plots"][0]["data"], "Mohr circle figure is missing"
    assert res["results"]["columns"] == ["Output", "Value", "Unit"]
    return {row["Output"]: (row["Value"], row["Unit"]) for row in res["results"]["data"]}


def test_extension_matches_closed_form(registry):
    # Cohesionless soil, phi = 30 deg: sigma_3f = sigma_1 * tan^2(45 - phi/2) = 300 / 3 = 100 kPa
    vals = _values(registry.execute_function(
        "constitutive", "mohrcoulomb_triaxial_extension", {"sigma_1": 300, "cohesion": 0, "phi": 30}))
    assert vals["sigma_1_f"] == (300, "kPa")
    assert vals["sigma_3_f"][0] == pytest.approx(100.0, rel=1e-9)
    assert vals["radius"][0] == pytest.approx(100.0, rel=1e-9)
    assert vals["tau_f"][0] == pytest.approx(100.0 * math.cos(math.radians(30)), rel=1e-9)


def test_compression_returns_failure_state(registry):
    vals = _values(registry.execute_function(
        "constitutive", "mohrcoulomb_triaxial_compression", {"sigma_3": 100, "cohesion": 0, "phi": 30}))
    assert vals["sigma_3_f"] == (100, "kPa")
    # Closed form is 300 kPa; groundhog 0.15.0 returns 301.57 kPa for this case (its own construction).
    assert vals["sigma_1_f"][0] == pytest.approx(300.0, rel=0.01)
    assert vals["Failure angle"][1] == "deg"


def test_out_of_range_input_is_rejected_before_groundhog(registry):
    res = registry.execute_function(
        "constitutive", "mohrcoulomb_triaxial_compression", {"sigma_3": 100, "cohesion": 0, "phi": -5})
    assert res["status"] == "ValidationError" and "phi" in res["error"]
