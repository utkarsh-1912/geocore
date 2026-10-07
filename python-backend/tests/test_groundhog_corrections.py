"""
GeoCore's corrections of Groundhog results (core/groundhog_corrections.py).

Groundhog 0.16.0 mohrcoulomb_triaxial_compression has sin(phi * tan(phi)) where the derivation has
sin(phi) * tan(phi): sigma_3 = 100 kPa, c = 0, phi = 30 degrees returns 301.57 kPa for a closed form of 300.
"""
import math

import pytest
from groundhog.constitutivemodels import general

from core.geoai.tool_registry import tool_registry
from core.groundhog_corrections import mohrcoulomb_triaxial_compression as corrected
from core.registry import Registry

CASES = [(20, 10, 35), (100, 0, 30), (50, 25, 20), (200, 0, 10), (0, 15, 28), (20, 10, 0), (100, 20, 45), (10, 5, 60)]


def closed_form(sigma_3, c, phi_deg):
    p = math.radians(phi_deg)
    sigma_1 = (sigma_3 * (1 + math.sin(p)) + 2 * c * math.cos(p)) / (1 - math.sin(p))
    radius, center = (sigma_1 - sigma_3) / 2, (sigma_1 + sigma_3) / 2
    return sigma_1, center, radius, radius * math.cos(p), center - radius * math.sin(p)


@pytest.mark.parametrize("sigma_3,c,phi", CASES)
def test_matches_the_closed_form_and_touches_the_envelope(sigma_3, c, phi):
    res = corrected(sigma_3=sigma_3, cohesion=c, phi=phi, latex_titles=False)
    sigma_1, center, radius, tau_f, sigma_f = closed_form(sigma_3, c, phi)
    assert res["sigma_1_f [kPa]"] == pytest.approx(sigma_1, rel=1e-12)
    assert res["center [kPa]"] == pytest.approx(center, rel=1e-12)
    assert res["radius [kPa]"] == pytest.approx(radius, rel=1e-12)
    assert res["tau_f [kPa]"] == pytest.approx(tau_f, rel=1e-12)
    assert res["sigma_f [kPa]"] == pytest.approx(sigma_f, rel=1e-12)
    # The failure point lies on the envelope tau = c + sigma tan(phi): the check Groundhog's circle fails.
    assert res["tau_f [kPa]"] == pytest.approx(c + res["sigma_f [kPa]"] * math.tan(math.radians(phi)), abs=1e-9)
    assert res["Failure angle [deg]"] == pytest.approx(45 - phi / 2)
    assert res["sigma_3_f [kPa]"] == sigma_3


def test_groundhog_original_is_wrong_so_the_correction_is_needed():
    # If this starts failing Groundhog has been fixed: drop the correction.
    original = general.mohrcoulomb_triaxial_compression(sigma_3=100, cohesion=0, phi=30, latex_titles=False)
    assert original["sigma_1_f [kPa]"] == pytest.approx(301.566, abs=0.001)
    assert corrected(sigma_3=100, cohesion=0, phi=30)["sigma_1_f [kPa]"] == pytest.approx(300.0, rel=1e-12)


def test_circle_and_figure_are_built_from_the_corrected_stress():
    res = corrected(sigma_3=20, cohesion=10, phi=35, latex_titles=False)
    circle = res["Mohr circle"]
    assert len(circle) == 250
    assert circle["sigma [kPa]"].max() == pytest.approx(res["sigma_1_f [kPa]"])
    assert circle["sigma [kPa]"].min() == pytest.approx(res["sigma_3_f [kPa]"], abs=0.01)  # 250 samples
    assert [t.name for t in res["Plot"].data] == [
        "Mohr circle", "Mohr-Coulomb criterion", "Location of stress state", "Location of stress state",
        "Sample", "Orientation of selected plane"]
    assert res["Plot"].layout.xaxis.title.text == "sigma [kPa]"
    assert set(res) == set(general.mohrcoulomb_triaxial_compression(sigma_3=1, cohesion=0, phi=30))  # same keys


def test_unsolvable_and_invalid_inputs_return_nan_like_groundhog():
    assert math.isnan(corrected(sigma_3=100, cohesion=0, phi=90)["sigma_1_f [kPa]"])  # unbounded
    with pytest.warns(UserWarning):
        assert math.isnan(corrected(sigma_3=100, cohesion=0, phi=-5)["sigma_1_f [kPa]"])


def test_name_module_signature_and_docstring_are_groundhogs():
    original = general.mohrcoulomb_triaxial_compression
    assert corrected.__name__ == original.__name__ and corrected.__module__ == original.__module__
    assert corrected.__doc__ == original.__doc__


def test_desktop_calculator_and_geoai_tool_use_the_correction():
    registry = Registry()
    assert registry.function_map["mohrcoulomb_triaxial_compression"] is corrected
    desktop = registry.execute_function(
        "constitutive", "mohrcoulomb_triaxial_compression", {"sigma_3": 100, "cohesion": 0, "phi": 30})
    values = {row["Output"]: row["Value"] for row in desktop["results"]["data"]}
    assert values["sigma_1_f"] == pytest.approx(300.0, rel=1e-9)
    geoai = tool_registry.invoke_tool("mohrcoulomb_triaxial_compression", {"sigma_3": 100, "cohesion": 0, "phi": 30})
    assert geoai["sigma_1_f [kPa]"] == pytest.approx(300.0, rel=1e-9)
