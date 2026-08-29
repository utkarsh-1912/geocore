# Author: Utkarsh Gupta
# License: GPL v3
"""
Comprehensive Automated Test Suite for Deterministic Geotechnical Unit Conversions
and Parameter Normalization.
"""

import pytest
import math
from core.geoai.units import (
    UnitDimension,
    parse_value_with_unit,
    convert_unit,
    get_unit_dimension,
    normalize_unit_str,
    normalize_parameter_value,
    GeoAIUnitError,
    GRAVITY_G
)
from core.geoai.schemas.expanded import EarthPressureRankineInput
from core.geoai.schemas.shallowfoundations import StressesPointloadInput
from core.geoai.validator import validate_and_coerce_inputs
from core.geoai.exceptions import GeoAIValidationError


# =====================================================================
# 1. Unit String Normalization & Dimension Identification
# =====================================================================

def test_normalize_unit_str():
    assert normalize_unit_str("[kPa]") == "kpa"
    assert normalize_unit_str(" kN/m3 ") == "kn/m3"
    assert normalize_unit_str("(deg)") == "deg"
    assert normalize_unit_str(None) == "-"
    assert normalize_unit_str("") == "-"


def test_get_unit_dimension():
    assert get_unit_dimension("kPa") == UnitDimension.PRESSURE
    assert get_unit_dimension("MPa") == UnitDimension.PRESSURE
    assert get_unit_dimension("bar") == UnitDimension.PRESSURE
    assert get_unit_dimension("psi") == UnitDimension.PRESSURE
    assert get_unit_dimension("ksf") == UnitDimension.PRESSURE

    assert get_unit_dimension("kN/m3") == UnitDimension.UNIT_WEIGHT
    assert get_unit_dimension("pcf") == UnitDimension.UNIT_WEIGHT
    assert get_unit_dimension("g/cm3") == UnitDimension.UNIT_WEIGHT
    assert get_unit_dimension("t/m3") == UnitDimension.UNIT_WEIGHT

    assert get_unit_dimension("kN") == UnitDimension.FORCE
    assert get_unit_dimension("MN") == UnitDimension.FORCE
    assert get_unit_dimension("kips") == UnitDimension.FORCE

    assert get_unit_dimension("kN/m") == UnitDimension.FORCE_PER_LENGTH
    assert get_unit_dimension("N/mm") == UnitDimension.FORCE_PER_LENGTH

    assert get_unit_dimension("m") == UnitDimension.LENGTH
    assert get_unit_dimension("mm") == UnitDimension.LENGTH
    assert get_unit_dimension("ft") == UnitDimension.LENGTH
    assert get_unit_dimension("in") == UnitDimension.LENGTH

    assert get_unit_dimension("deg") == UnitDimension.ANGLE
    assert get_unit_dimension("rad") == UnitDimension.ANGLE

    assert get_unit_dimension("m/s") == UnitDimension.VELOCITY
    assert get_unit_dimension("m/day") == UnitDimension.PERMEABILITY


# =====================================================================
# 2. Parsing Values with Units
# =====================================================================

def test_parse_value_with_unit_clean():
    val, u = parse_value_with_unit("18.5 kN/m3")
    assert val == 18.5
    assert u == "kN/m3"

    val, u = parse_value_with_unit("32 deg")
    assert val == 32.0
    assert u == "deg"

    val, u = parse_value_with_unit("1.5 MPa")
    assert val == 1.5
    assert u == "MPa"

    val, u = parse_value_with_unit("1e-4 m/s")
    assert val == 0.0001
    assert u == "m/s"

    val, u = parse_value_with_unit("-12.5 kN")
    assert val == -12.5
    assert u == "kN"

    val, u = parse_value_with_unit(42)
    assert val == 42.0
    assert u is None

    val, u = parse_value_with_unit(19.81)
    assert val == 19.81
    assert u is None


def test_parse_value_with_unit_invalid():
    with pytest.raises(GeoAIUnitError):
        parse_value_with_unit("")

    with pytest.raises(GeoAIUnitError):
        parse_value_with_unit("not a number")

    with pytest.raises(GeoAIUnitError):
        parse_value_with_unit(float('nan'))


# =====================================================================
# 3. Deterministic Conversions across Geotechnical Dimensions
# =====================================================================

def test_pressure_conversions():
    # 1.5 MPa -> 1500 kPa
    assert convert_unit(1.5, "MPa", "kPa") == pytest.approx(1500.0)
    # 100 kPa -> 1 bar
    assert convert_unit(100.0, "kPa", "bar") == pytest.approx(1.0)
    # 1 bar -> 100 kPa
    assert convert_unit(1.0, "bar", "kPa") == pytest.approx(100.0)
    # 1000 Pa -> 1 kPa
    assert convert_unit(1000.0, "Pa", "kPa") == pytest.approx(1.0)
    # 1 ksf -> 47.88026 kPa
    assert convert_unit(1.0, "ksf", "kPa") == pytest.approx(47.88026, rel=1e-4)
    # 14.5 psi -> ~100 kPa (1 bar)
    assert convert_unit(14.5038, "psi", "kPa") == pytest.approx(100.0, rel=1e-3)


def test_unit_weight_conversions():
    # 1800 kg/m3 -> 1800 * 9.80665 / 1000 = 17.65197 kN/m3
    assert convert_unit(1800.0, "kg/m3", "kN/m3") == pytest.approx(1800.0 * GRAVITY_G / 1000.0)
    # 1.8 t/m3 -> 17.65197 kN/m3
    assert convert_unit(1.8, "t/m3", "kN/m3") == pytest.approx(1.8 * GRAVITY_G)
    # 120 pcf -> 18.8505 kN/m3
    assert convert_unit(120.0, "pcf", "kN/m3") == pytest.approx(120.0 * 0.15708746, rel=1e-4)
    # 2.0 g/cm3 -> 19.6133 kN/m3
    assert convert_unit(2.0, "g/cm3", "kN/m3") == pytest.approx(2.0 * GRAVITY_G)


def test_force_and_length_conversions():
    # 0.5 MN -> 500 kN
    assert convert_unit(0.5, "MN", "kN") == pytest.approx(500.0)
    # 100 kips -> 444.822 kN
    assert convert_unit(100.0, "kips", "kN") == pytest.approx(444.822, rel=1e-4)

    # 10 ft -> 3.048 m
    assert convert_unit(10.0, "ft", "m") == pytest.approx(3.048)
    # 250 mm -> 0.25 m
    assert convert_unit(250.0, "mm", "m") == pytest.approx(0.25)
    # 12 in -> 0.3048 m
    assert convert_unit(12.0, "in", "m") == pytest.approx(0.3048)


def test_angle_conversions():
    # pi/6 rad (0.5235988 rad) -> 30 deg
    assert convert_unit(math.pi / 6.0, "rad", "deg") == pytest.approx(30.0)
    # 45 deg -> pi/4 rad
    assert convert_unit(45.0, "deg", "rad") == pytest.approx(math.pi / 4.0)


def test_permeability_conversions():
    # 1e-4 cm/s -> 1e-6 m/s
    assert convert_unit(1e-4, "cm/s", "m/s") == pytest.approx(1e-6)
    # 1 m/day -> 1/86400 m/s
    assert convert_unit(1.0, "m/day", "m/s") == pytest.approx(1.0 / 86400.0)


# =====================================================================
# 4. Incompatible Dimension Diagnostics
# =====================================================================

def test_dimension_mismatch_raises():
    # Converting Pressure (kPa) to Unit Weight (kN/m3) must fail loudly
    with pytest.raises(GeoAIUnitError) as excinfo:
        convert_unit(25.0, "kPa", "kN/m3", field_name="gamma")
    assert "Unit dimension mismatch" in str(excinfo.value)
    assert excinfo.value.field == "gamma"
    assert excinfo.value.provided_unit == "kPa"
    assert excinfo.value.expected_unit == "kN/m3"

    # Converting Length (m) to Angle (deg) must fail
    with pytest.raises(GeoAIUnitError):
        convert_unit(10.0, "m", "deg", field_name="phi_eff")


def test_unrecognized_unit_raises():
    with pytest.raises(GeoAIUnitError, match="Unrecognized source unit"):
        convert_unit(10.0, "furlongs", "m")


# =====================================================================
# 5. Parameter Value Normalization Engine
# =====================================================================

def test_normalize_parameter_value():
    # String with MPa to expected kPa
    assert normalize_parameter_value("2.5 MPa", expected_unit="kPa") == pytest.approx(2500.0)
    # String with rad to expected deg
    assert normalize_parameter_value("0.5236 rad", expected_unit="deg") == pytest.approx(30.0, rel=1e-3)
    # Raw float with expected unit returns float
    assert normalize_parameter_value(32.0, expected_unit="deg") == 32.0
    # None returns None
    assert normalize_parameter_value(None, expected_unit="kPa") is None

    # Mismatched dimension raises GeoAIUnitError
    with pytest.raises(GeoAIUnitError):
        normalize_parameter_value("18 kPa", expected_unit="kN/m3", field_name="gamma")


# =====================================================================
# 6. Schema Integration with Pydantic Models & Validator
# =====================================================================

def test_schema_automatic_unit_conversion():
    # EarthPressureRankineInput expects phi_eff in deg. Pass 0.5585 rad (~32 deg)
    model = EarthPressureRankineInput(phi_eff="0.558505 rad", wall_angle="0 deg")
    assert model.phi_eff == pytest.approx(32.0, rel=1e-3)
    assert model.wall_angle == 0.0

    # StressesPointloadInput expects pointload in kN, z in m, r in m.
    # Pass pointload='0.5 MN', z='5000 mm', r='200 cm'
    pt_model = StressesPointloadInput(pointload="0.5 MN", z="5000 mm", r="200 cm")
    assert pt_model.pointload == pytest.approx(500.0)
    assert pt_model.z == pytest.approx(5.0)
    assert pt_model.r == pytest.approx(2.0)


def test_validator_with_unit_conversion():
    # validate_and_coerce_inputs should automatically convert units for registered canonical tools
    raw_args = {
        "phi_eff": "0.523599 rad",  # 30 deg
        "wall_angle": "0 deg"
    }
    validated, instance = validate_and_coerce_inputs("calculate_earth_pressure_rankine", raw_args)
    assert validated["phi_eff"] == pytest.approx(30.0, rel=1e-3)

    # Incompatible unit should raise structured GeoAIValidationError
    bad_args = {
        "phi_eff": "100 kPa"  # Pressure instead of angle!
    }
    with pytest.raises(GeoAIValidationError) as excinfo:
        validate_and_coerce_inputs("calculate_earth_pressure_rankine", bad_args)
    assert "Unit dimension mismatch" in str(excinfo.value)
