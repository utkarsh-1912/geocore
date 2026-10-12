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


# --- acousticimpedance_bulkunitweight_chen -------------------------------------------------------------------

from groundhog.siteinvestigation.correlations import general as correlations_general  # noqa: E402

from core.groundhog_corrections import acousticimpedance_bulkunitweight_chen as acoustic  # noqa: E402

CHEN = (0.0001315, -0.03776, 4.201, -245.0, 8603.0)  # calibration factors 4..0 (Chen et al., 2021)


def chen_closed_form(gamma, gs=2.65, s=1.0, gamma_w=10.0):
    e = (gamma_w * gs - gamma) / (gamma - s * gamma_w)  # Budhu (2011) phase relation
    n = e / (1 + e)
    p = 100 * n
    return e, n, sum(c * p ** k for c, k in zip(CHEN, (4, 3, 2, 1, 0)))


@pytest.mark.parametrize("kwargs", [
    {"bulkunitweight": 18.0},
    {"bulkunitweight": 18.0, "specific_gravity": 2.0},   # Groundhog: KeyError 'w [-]' (helper allows 2.4-2.9)
    {"bulkunitweight": 22.0, "specific_gravity": 3.0},   # same, upper end of the documented G_s range
    {"bulkunitweight": 12.0},                             # Groundhog: NaN (e = 7.25 > helper's 5)
    {"bulkunitweight": 16.0, "saturation": 0.8, "gamma_w": 10.25},
])
def test_acoustic_impedance_matches_the_phase_relations(kwargs):
    res = acoustic(**kwargs, fail_silently=False)
    e, n, impedance = chen_closed_form(kwargs["bulkunitweight"], kwargs.get("specific_gravity", 2.65),
                                       kwargs.get("saturation", 1.0), kwargs.get("gamma_w", 10.0))
    assert res["e [-]"] == pytest.approx(e, rel=1e-12)
    assert res["n [-]"] == pytest.approx(n, rel=1e-12)
    assert res["I [(m/s).(g/cm3)]"] == pytest.approx(impedance, rel=1e-12)


def test_acoustic_impedance_groundhog_original_fails_so_the_correction_is_needed():
    # If these start passing Groundhog has been fixed: drop the correction.
    original = correlations_general.acousticimpedance_bulkunitweight_chen
    with pytest.raises(KeyError):
        original(bulkunitweight=18.0, specific_gravity=2.0, fail_silently=False)
    assert math.isnan(original(bulkunitweight=12.0)["I [(m/s).(g/cm3)]"])
    # Inside the helpers' ranges the correction is Groundhog's own result.
    assert acoustic(bulkunitweight=18.0) == original(bulkunitweight=18.0)


def test_acoustic_impedance_rejects_inputs_like_groundhog():
    with pytest.warns(UserWarning):
        assert math.isnan(acoustic(bulkunitweight=11.0)["I [(m/s).(g/cm3)]"])  # below the documented 12 kN/m3
    # gamma > G_s gamma_w would need a negative void ratio.
    assert math.isnan(acoustic(bulkunitweight=22.0, specific_gravity=2.0)["e [-]"])
    with pytest.raises(ValueError, match="negative"):
        acoustic(bulkunitweight=22.0, specific_gravity=2.0, fail_silently=False)


def test_acoustic_impedance_keeps_groundhogs_name_signature_and_validation():
    import inspect
    from core.geoai.inventory_sync import groundhog_validation_spec
    original = correlations_general.acousticimpedance_bulkunitweight_chen
    assert acoustic.__name__ == original.__name__ and acoustic.__module__ == original.__module__
    assert acoustic.__doc__ == original.__doc__
    assert inspect.signature(acoustic) == inspect.signature(original)
    assert groundhog_validation_spec(acoustic) is correlations_general.ACOUSTICIMPEDANCE_BULKUNITWEIGHT_CHEN


def test_desktop_calculator_and_geoai_tool_use_the_acoustic_correction():
    registry = Registry()
    assert registry.function_map["acousticimpedance_bulkunitweight_chen"] is acoustic
    args = {"bulkunitweight": 18.0, "specific_gravity": 2.0}
    expected = chen_closed_form(18.0, 2.0)[2]
    desktop = registry.execute_function("siteinvestigation", "acousticimpedance_bulkunitweight_chen", args)
    assert desktop["I [(m/s).(g/cm3)]"] == pytest.approx(expected, rel=1e-9)
    geoai = tool_registry.invoke_tool("acousticimpedance_bulkunitweight_chen", args)
    assert geoai["I [(m/s).(g/cm3)]"] == pytest.approx(expected, rel=1e-9)
