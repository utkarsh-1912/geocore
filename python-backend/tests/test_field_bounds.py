"""The form-facing bounds endpoint serves exactly the limits the calculation validates."""
import pytest

from core.geoai.exceptions import GeoAIValidationError
from core.geoai.validator import field_bounds, validate_and_coerce_inputs


def test_field_bounds_shape_and_known_values():
    bounds = field_bounds()
    p = bounds["stresses_circle"]["poissonsratio"]
    assert (p["min"], p["max"]) == (0.0, 0.5)  # schema allows -1, Groundhog's own range is 0-0.5
    # The hand-written schema allows z >= 0 m; Groundhog divides by z, so the form gets z > 0.
    z = bounds["stresses_circle"]["z"]
    assert (z["min"], z["min_exclusive"], z["max"]) == (0.0, True, 500.0)
    assert "coefficient1" not in bounds["constrainedmodulus_pcpt_robertson"]  # unbounded -> omitted


def test_field_bounds_only_numeric_and_bounded():
    for func, params in field_bounds().items():
        for name, b in params.items():
            assert b["min"] is not None or b["max"] is not None, f"{func}.{name}"
            if b["min"] is not None and b["max"] is not None:
                assert b["min"] <= b["max"], f"{func}.{name}"


def test_singular_groundhog_endpoint_is_exclusive():
    # Q_t = (q_t - sigma_vo) / sigma_vo_eff: Groundhog allows 0 but divides by it.
    b = field_bounds()["constrainedmodulus_pcpt_robertson"]["sigma_vo_eff"]
    assert (b["min"], b["min_exclusive"]) == (0.0, True)
    assert b["max_exclusive"] is False
    args = {"qt": 3.0, "ic": 2.5, "sigma_vo": 30.0}
    with pytest.raises(GeoAIValidationError):
        validate_and_coerce_inputs("constrainedmodulus_pcpt_robertson", {**args, "sigma_vo_eff": 0.0})
    validate_and_coerce_inputs("constrainedmodulus_pcpt_robertson", {**args, "sigma_vo_eff": 0.1})


def test_geocore_schema_limits_reach_the_form():
    # Hand-written schemas (IS codes) carry strict limits and units the form must show.
    b = field_bounds()["bearing_capacity_is6403"]
    assert b["width"] == {"min": 0.0, "max": 100.0, "min_exclusive": True, "max_exclusive": False,
                          "unit": "m", "integer": False}
    assert b["load_inclination"]["max_exclusive"] is True
