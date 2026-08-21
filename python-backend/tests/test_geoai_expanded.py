"""
Tests for Expanded GeoAI Schemas and Tools across Dynamics, Excavations, Pipelines, and Consolidation
"""
import pytest
from core.registry import registry
from core.geoai.tool_registry import tool_registry

class TestExpandedCalculations:
    # 1. Gmax from Vs
    def test_gmax_calculation(self):
        payload = {"Vs": 250.0, "gamma": 19.0, "g": 9.81}
        res = registry.execute_function("dynamic_props", "gmax_shearwavevelocity", payload)
        assert "error" not in res
        # Gmax = rho * Vs^2 = (19 / 9.81 * 1000) * 250^2 = 121049.95 kPa
        val = res.get("Gmax [kPa]") or res.get("Gmax")
        assert pytest.approx(val, rel=1e-2) == 121050.0

    # 2. Rankine Earth Pressure
    def test_earth_pressure_rankine(self):
        payload = {"phi_eff": 30.0, "wall_angle": 0.0, "top_angle": 0.0}
        res = registry.execute_function("earth_pressure", "earthpressurecoefficients_rankine", payload)
        assert "error" not in res
        # For phi = 30: Ka = (1 - sin 30) / (1 + sin 30) = 1/3 = 0.3333; Kp = 3.0
        ka = res.get("KaR [-]") or res.get("Ka [-]") or res.get("Ka")
        kp = res.get("KpR [-]") or res.get("Kp [-]") or res.get("Kp")
        assert pytest.approx(ka, rel=1e-2) == 0.333
        assert pytest.approx(kp, rel=1e-2) == 3.0

    # 3. Pipeline Contact Width
    def test_pipeline_contact_width(self):
        payload = {"diameter": 1.0, "penetration": 0.2}
        res = registry.execute_function("pipeline_stability", "contactwidth", payload)
        assert "error" not in res
        # B = 0.8
        val = res.get("B [m]") or res.get("contact width [m]") or res.get("contact_width")
        assert pytest.approx(val, rel=1e-2) == 0.8

    # 4. Pumping Test Hydraulic Conductivity
    def test_hydraulic_conductivity(self):
        payload = {
            "radius_1": 10.0,
            "radius_2": 50.0,
            "piezometric_height_1": 18.0,
            "piezometric_height_2": 20.0,
            "flowrate": 0.05
        }
        res = registry.execute_function("groundwater", "hydraulicconductivity_unconfinedaquifer", payload)
        assert "error" not in res
        val = res.get("hydraulic_conductivity [m/s]") or res.get("hydraulic conductivity [m/s]")
        assert val is not None and val > 0.0

    # 5. Tool Registry List Count
    def test_tool_registry_has_expanded_tools(self):
        tools = tool_registry.list_tools()
        tool_names = [t["name"] for t in tools]
        assert len(tools) >= 9
        assert "calculate_gmax_from_shear_wave_velocity" in tool_names
        assert "calculate_earth_pressure_rankine" in tool_names
        assert "calculate_pipeline_contact_width" in tool_names
        assert "calculate_hydraulic_conductivity_unconfined" in tool_names
