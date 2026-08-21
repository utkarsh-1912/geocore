"""
Unit & Integration Tests for GeoAI Parameter Validation and Pilot Calculations
"""
import pytest
import math
from core.registry import registry
from core.geoai.validator import validate_and_coerce_inputs, sanitize_raw_input
from core.geoai.exceptions import GeoAIValidationError
from core.geoai.schemas.classification import BulkUnitWeightInput, VoidRatioPorosityInput
from core.geoai.schemas.shallowfoundations import StressesCircleInput


class TestGeoAISanitization:
    def test_strip_whitespace(self):
        cleaned = sanitize_raw_input({"name": "  test  ", "val": 10.5})
        assert cleaned["name"] == "test"
        assert cleaned["val"] == 10.5

    def test_remove_sentinel_strings(self):
        raw = {
            "param1": "-",
            "param2": "--",
            "param3": "N/A",
            "param4": "null",
            "param5": "undefined",
            "param6": "valid_val"
        }
        cleaned = sanitize_raw_input(raw)
        assert cleaned["param1"] is None
        assert cleaned["param2"] is None
        assert cleaned["param3"] is None
        assert cleaned["param4"] is None
        assert cleaned["param5"] is None
        assert cleaned["param6"] == "valid_val"

    def test_reject_nan_and_inf(self):
        with pytest.raises(GeoAIValidationError):
            sanitize_raw_input({"z": float("nan")})

        with pytest.raises(GeoAIValidationError):
            sanitize_raw_input({"z": float("inf")})


class TestCanonicalPilotSchemas:
    # 1. bulkunitweight
    def test_bulkunitweight_valid(self):
        payload = {
            "specific_gravity": 2.65,
            "voidratio": 0.65,
            "saturation": 0.8,
            "unitweight_water": 9.81
        }
        res = registry.execute_function("classification_phase", "bulkunitweight", payload)
        assert "error" not in res
        # Expected: (2.65 + 0.8 * 0.65) / (1 + 0.65) * 9.81 = 18.847
        val = res.get("bulk unit weight [kN/m3]") or res.get("bulk_unit_weight") or list(res.values())[0]
        assert pytest.approx(val, rel=1e-2) == 18.85

    def test_bulkunitweight_sentinel_rejection(self):
        payload = {
            "specific_gravity": "-",
            "voidratio": 0.65,
            "saturation": 0.8
        }
        res = registry.execute_function("classification_phase", "bulkunitweight", payload)
        assert res.get("status") == "ValidationError"
        assert "specific_gravity" in str(res.get("details"))

    def test_bulkunitweight_out_of_bounds(self):
        # Saturation > 1.0
        payload = {
            "specific_gravity": 2.65,
            "voidratio": 0.65,
            "saturation": 1.5
        }
        res = registry.execute_function("classification_phase", "bulkunitweight", payload)
        assert res.get("status") == "ValidationError"

    # 2. stresses_circle
    def test_stresses_circle_valid(self):
        payload = {
            "z": 2.0,
            "footing_radius": 1.5,
            "imposedstress": 150.0,
            "poissonsratio": 0.3
        }
        res = registry.execute_function("stress_dist", "stresses_circle", payload)
        assert "error" not in res
        # Vertical stress under circular footing
        assert any("sigma z" in k for k in res.keys())

    def test_stresses_circle_negative_depth_rejected(self):
        payload = {
            "z": -5.0,
            "footing_radius": 1.5,
            "imposedstress": 150.0
        }
        res = registry.execute_function("stress_dist", "stresses_circle", payload)
        assert res.get("status") == "ValidationError"

    # 3. voidratio_porosity
    def test_voidratio_porosity_valid(self):
        payload = {"porosity": 0.4}
        res = registry.execute_function("classification_phase", "voidratio_porosity", payload)
        assert "error" not in res
        # e = n / (1 - n) = 0.4 / 0.6 = 0.6667
        val = res.get("void ratio [-]") or res.get("void_ratio") or list(res.values())[0]
        assert pytest.approx(val, rel=1e-2) == 0.667

    def test_voidratio_porosity_invalid_porosity(self):
        # Porosity >= 1.0 is physically impossible
        payload = {"porosity": 1.2}
        res = registry.execute_function("classification_phase", "voidratio_porosity", payload)
        assert res.get("status") == "ValidationError"
