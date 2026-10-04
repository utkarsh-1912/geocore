# Author: Utkarsh Gupta
# License: GPL v3
"""
Indian Standard (BIS) calculations in core.standards.bis: values against the code tables, worked
examples and hand calculations (AGENTS.md §25), plus registry / GeoAI tool wiring.
"""
import math

import pytest

from core.standards.bis import (BIS_FUNCTIONS, BISInputError, bearing_capacity_is6403, borehole_layout_is1892,
                                classify_soil_is1498, consistency_indices_is2720, flow_index_is2720,
                                investigation_depth_is1892, liquid_limit_one_point_is2720,
                                permeability_constant_head_is2720, permeability_falling_head_is2720,
                                permissible_settlement_is1904, raft_rigidity_is2950, specific_gravity_is2720,
                                spt_correction_is2131, stability_check_is1904)
from core.standards.bis.is2131 import overburden_correction_factor_is2131
from core.standards.bis.is6403 import bearing_capacity_factors

QNU = "Net ultimate bearing capacity qnu [kPa]"


# ---------------------------------------------------------------------------- IS 6403

# IS 6403:1981 Table 1 (phi [deg]: Nc, Nq, Ngamma)
IS6403_TABLE_1 = {
    0: (5.14, 1.00, 0.00), 5: (6.49, 1.57, 0.45), 10: (8.35, 2.47, 1.22), 15: (10.98, 3.94, 2.65),
    20: (14.83, 6.40, 5.39), 25: (20.72, 10.66, 10.88), 30: (30.14, 18.40, 22.40), 35: (46.12, 33.30, 48.03),
    40: (75.31, 64.20, 109.41), 45: (133.88, 134.88, 271.76), 50: (266.89, 319.07, 762.89),
}


@pytest.mark.parametrize("phi,expected", sorted(IS6403_TABLE_1.items()))
def test_bearing_capacity_factors_reproduce_is6403_table_1(phi, expected):
    f = bearing_capacity_factors(phi)
    for got, want in zip((f["Nc"], f["Nq"], f["Ngamma"]), expected):
        assert got == pytest.approx(want, rel=1e-4, abs=0.006)


def test_bearing_factors_use_groundhog_inside_its_range_and_closed_form_below():
    assert "Groundhog" in bearing_capacity_factors(30)["source"]
    assert "Closed form" in bearing_capacity_factors(15)["source"]
    # Continuity across the 20 deg switch
    below, at = bearing_capacity_factors(19.999), bearing_capacity_factors(20.0)
    assert below["Nq"] == pytest.approx(at["Nq"], rel=1e-4)


def test_strip_on_sand_hand_calculation():
    # q (Nq - 1) = 27 x 17.40 = 469.8; 0.5 B gamma Ngamma = 0.5 x 2 x 18 x 22.40 = 403.2
    r = bearing_capacity_is6403(width=2, depth=1.5, water_table_depth=10, unit_weight=18, friction_angle=30)
    assert r["Surcharge term [kPa]"] == pytest.approx(469.8, rel=1e-3)
    assert r["Unit weight term [kPa]"] == pytest.approx(403.2, rel=1e-3)
    assert r[QNU] == pytest.approx(873.0, rel=1e-3)
    assert r["Net ultimate load on effective area [kN/m]"] == pytest.approx(2 * 873.0, rel=1e-3)


def test_undrained_square_reduces_to_cl_5_3_1_1():
    # qd = c Nc sc = 50 x 5.14 x 1.3 (phi = 0, no depth or inclination)
    r = bearing_capacity_is6403(width=2, depth=1.5, water_table_depth=0, unit_weight=18, cohesion=50,
                                shape="square", saturated_unit_weight=19)
    assert r["Surcharge term [kPa]"] == 0.0 and r["Unit weight term [kPa]"] == 0.0
    assert r[QNU] == pytest.approx(50 * (2 + math.pi) * 1.3, rel=1e-3)


def test_rectangle_with_inclination_and_water_table_hand_calculation():
    # B/L = 0.5: sc = sq = 1.1, sgamma = 0.8; alpha = 10: ic = iq = (80/90)^2, igamma = (20/30)^2;
    # Dw = 2 between Df = 1 and Df + B = 3: W' = 0.75; q = 18 kPa.
    r = bearing_capacity_is6403(width=2, length=4, shape="rectangle", depth=1, water_table_depth=2, unit_weight=18,
                                cohesion=10, friction_angle=30, load_inclination=10)
    assert (r["sc [-]"], r["sq [-]"], r["sgamma [-]"]) == (1.1, 1.1, 0.8)
    assert r["ic [-]"] == pytest.approx((8 / 9) ** 2, rel=1e-3)
    assert r["igamma [-]"] == pytest.approx((2 / 3) ** 2, rel=1e-3)
    assert r["W' [-]"] == 0.75
    expected = (10 * 30.14 * 1.1 * (8 / 9) ** 2 + 18 * 17.40 * 1.1 * (8 / 9) ** 2
                + 0.5 * 2 * 18 * 22.40 * 0.8 * (2 / 3) ** 2 * 0.75)
    assert r[QNU] == pytest.approx(expected, rel=2e-3)


def test_depth_factors_only_when_requested():
    base = dict(width=2, depth=1.5, water_table_depth=10, unit_weight=18, friction_angle=30)
    off = bearing_capacity_is6403(**base)
    on = bearing_capacity_is6403(**base, apply_depth_factors=True)
    root = math.tan(math.radians(60))
    assert off["dq [-]"] == 1.0
    assert on["dc [-]"] == pytest.approx(1 + 0.2 * 0.75 * root, rel=1e-3)
    assert on["dq [-]"] == pytest.approx(1 + 0.1 * 0.75 * root, rel=1e-3)
    assert any("compaction" in w for w in on["warnings"])


@pytest.mark.parametrize("dw,expected", [(1.0, 0.5), (0.0, 0.5), (2.0, 0.75), (3.0, 1.0), (8.0, 1.0)])
def test_water_table_factor_cl_5_1_2_4(dw, expected):
    r = bearing_capacity_is6403(width=2, depth=1, water_table_depth=dw, unit_weight=18, saturated_unit_weight=20,
                                friction_angle=30)
    assert r["W' [-]"] == expected


def test_effective_surcharge_uses_submerged_weight_below_water_table():
    r = bearing_capacity_is6403(width=3, depth=2, water_table_depth=0.5, unit_weight=18, saturated_unit_weight=20,
                                friction_angle=30)
    assert r["Effective surcharge q [kPa]"] == pytest.approx(18 * 0.5 + (20 - 9.81) * 1.5, rel=1e-3)


def test_local_shear_reduces_c_and_phi():
    r = bearing_capacity_is6403(width=2, depth=1, water_table_depth=10, unit_weight=18, cohesion=30,
                                friction_angle=30, failure_mode="local")
    assert r["phi used [deg]"] == pytest.approx(math.degrees(math.atan(0.67 * math.tan(math.radians(30)))), rel=1e-3)
    assert r["c used [kPa]"] == pytest.approx(20.0)


@pytest.mark.parametrize("dr,weight", [(80, 1.0), (10, 0.0), (45, 0.5)])
def test_table_3_failure_mode_from_relative_density(dr, weight):
    r = bearing_capacity_is6403(width=2, depth=1, water_table_depth=10, unit_weight=18, friction_angle=32,
                                failure_mode="from_relative_density", relative_density=dr)
    g, loc = r["qnu general shear [kPa]"], r["qnu local shear [kPa]"]
    assert r[QNU] == pytest.approx(loc + weight * (g - loc), rel=1e-3)


def test_eccentricity_gives_effective_dimensions():
    r = bearing_capacity_is6403(width=2, length=3, shape="rectangle", depth=1, water_table_depth=10, unit_weight=18,
                                friction_angle=30, eccentricity_width=0.2, eccentricity_length=0.3)
    assert r["Effective width B' [m]"] == pytest.approx(1.6)
    assert r["Effective length L' [m]"] == pytest.approx(2.4)
    assert r["Net ultimate load on effective area [kN]"] == pytest.approx(r[QNU] * 1.6 * 2.4, rel=2e-3)


def test_factor_of_safety_and_shallow_depth_warning():
    r = bearing_capacity_is6403(width=2, depth=0.3, water_table_depth=10, unit_weight=18, friction_angle=30,
                                factor_of_safety=2.5)
    assert r["Net safe bearing capacity qns [kPa]"] == pytest.approx(r[QNU] / 2.5, rel=2e-3)
    assert any("IS 1904:2021 cl. 7.2" in w for w in r["warnings"])


@pytest.mark.parametrize("kwargs,match", [
    (dict(water_table_depth=0.5), "saturated_unit_weight"),
    (dict(friction_angle=55), "0-50"),
    (dict(shape="rectangle"), "length"),
    (dict(shape="circle", eccentricity_width=0.1), "circular"),
    (dict(friction_angle=0, cohesion=0), "shear strength"),
    (dict(water_table_depth=None), "water_table_depth"),
])
def test_bearing_capacity_rejects_out_of_scope_inputs(kwargs, match):
    args = dict(width=2, depth=1, water_table_depth=10, unit_weight=18, friction_angle=30)
    args.update(kwargs)
    with pytest.raises(BISInputError, match=match):
        bearing_capacity_is6403(**args)


# ---------------------------------------------------------------------------- IS 1498

@pytest.mark.parametrize("kwargs,symbol", [
    (dict(percent_fines=60, liquid_limit=55, plastic_limit=25), "CH"),
    (dict(percent_fines=3, percent_gravel=10, d10=0.1, d30=0.35, d60=0.8), "SW"),
    (dict(percent_fines=3, percent_gravel=10, d10=0.1, d30=0.15, d60=0.5), "SP"),
    (dict(percent_fines=8, percent_gravel=60, liquid_limit=30, plastic_limit=24, d10=0.1, d30=1.5, d60=6), "GP-GM"),
    (dict(percent_fines=20, percent_gravel=10, liquid_limit=40, plastic_limit=20), "SC"),
    (dict(percent_fines=20, percent_gravel=50, liquid_limit=24, plastic_limit=18), "GM-GC"),
    (dict(percent_fines=20, percent_gravel=10, non_plastic=True), "SM"),
    (dict(percent_fines=70, liquid_limit=22, plastic_limit=16), "ML-CL"),
    (dict(percent_fines=70, liquid_limit=45, plastic_limit=30), "MI"),
    (dict(percent_fines=90, liquid_limit=60, plastic_limit=35, liquid_limit_oven_dried=40), "OH"),
    (dict(percent_fines=80, liquid_limit=35, plastic_limit=15), "CL-CI"),
    (dict(percent_fines=0, highly_organic=True), "Pt"),
])
def test_is1498_group_symbols(kwargs, symbol):
    assert classify_soil_is1498(**kwargs)["Group symbol"] == symbol


def test_is1498_cl_3_5_2_worked_example_favours_non_plastic_symbol():
    # "a gravel with 10 percent fines, a Cu of 20, a Cc of 2.0 and Ip of 6 would be classified GW-GM"
    d10, d60 = 0.2, 4.0  # Cu = 20
    d30 = math.sqrt(2.0 * d10 * d60)  # Cc = 2.0
    r = classify_soil_is1498(percent_fines=10, percent_gravel=60, liquid_limit=25, plastic_limit=19,
                             d10=d10, d30=d30, d60=d60)
    assert r["Uniformity coefficient Cu [-]"] == pytest.approx(20)
    assert r["Coefficient of curvature Cc [-]"] == pytest.approx(2.0)
    assert r["Group symbol"] == "GW-GM"


def test_is1498_requires_gradation_and_limits():
    with pytest.raises(BISInputError, match="D10"):
        classify_soil_is1498(percent_fines=3, percent_gravel=40)
    with pytest.raises(BISInputError, match="Liquid and plastic limits"):
        classify_soil_is1498(percent_fines=70)
    with pytest.raises(BISInputError, match="exceed 100"):
        classify_soil_is1498(percent_fines=70, percent_gravel=40)


# ---------------------------------------------------------------------------- IS 2131

@pytest.mark.parametrize("sigma_kgf,cn_fig1", [(0.5, 1.20), (1.0, 1.00), (2.0, 0.79), (3.0, 0.63), (4.0, 0.55), (5.0, 0.46)])
def test_overburden_correction_matches_digitised_is2131_fig_1(sigma_kgf, cn_fig1):
    assert overburden_correction_factor_is2131(sigma_kgf * 98.0665) == pytest.approx(cn_fig1, abs=0.04)


def test_overburden_correction_capped_at_2():
    assert overburden_correction_factor_is2131(1.0) == 2.0


def test_spt_dilatancy_and_energy_corrections():
    r = spt_correction_is2131(n_observed=25, effective_overburden_pressure=98.0665 * 20 / 10 ** (1 / 0.77),
                              fine_sand_or_silt_below_water_table=True)  # CN = 1.0
    assert r["Overburden correction CN [-]"] == pytest.approx(1.0, abs=1e-3)
    assert r["Corrected N [-]"] == pytest.approx(15 + 0.5 * (25 - 15), rel=1e-3)
    r = spt_correction_is2131(n_observed=20, effective_overburden_pressure=98.0665 * 20 / 10 ** (1 / 0.77),
                              energy_ratio=72)
    assert r["N60 [-]"] == pytest.approx(24.0)
    assert any("IS 2131:2025" in w for w in r["warnings"])
    r = spt_correction_is2131(n_observed=10, effective_overburden_pressure=100, fine_sand_or_silt_below_water_table=True)
    assert "N'' after dilatancy correction [-]" not in r


# ---------------------------------------------------------------------------- IS 1892

def test_investigation_depth_guidelines():
    r = investigation_depth_is1892("shallow", width=3, founding_depth=1.5)
    assert r["Minimum depth below reference level [m]"] == 6 and r["Maximum guideline depth below reference level [m]"] == 9
    assert r["Maximum guideline depth below ground level [m]"] == 10.5
    r = investigation_depth_is1892("raft", width=4)
    assert r["Minimum depth below reference level [m]"] == 6 and r["Maximum guideline depth below reference level [m]"] == 12
    assert investigation_depth_is1892("pile", pile_diameter=0.6)["Minimum depth below reference level [m]"] == 5
    assert investigation_depth_is1892("pile", pile_diameter=1.2)["Minimum depth below reference level [m]"] == 6
    assert investigation_depth_is1892("well", width=8)["Maximum guideline depth below reference level [m]"] == 16
    with pytest.raises(BISInputError):
        investigation_depth_is1892("pile")


def test_borehole_layout_table_2():
    assert borehole_layout_is1892("site_0_4_ha")["Minimum number of boreholes [-]"] == 5
    assert borehole_layout_is1892("large_plan_or_multiple_buildings", plan_length=120, plan_width=80)[
        "Minimum number of boreholes [-]"] == 12
    r = borehole_layout_is1892("linear", route_length=2000)
    assert (r["Boreholes at 500 m spacing [-]"], r["Boreholes at 50 m spacing [-]"]) == (5, 41)
    r = borehole_layout_is1892("solar_plant", site_area=30)
    assert (r["Boreholes at 1 per 5 ha [-]"], r["Boreholes at 1 per 2 ha [-]"]) == (6, 15)
    assert borehole_layout_is1892("solar_plant", site_area=4)["Boreholes at 1 per 2 ha [-]"] == 5


# ---------------------------------------------------------------------------- IS 1904

@pytest.mark.parametrize("fnd,struct,soil,expected", [
    ("isolated", "steel", "sand_hard_clay", (50, 0.0033, "1/300")),
    ("isolated", "reinforced_concrete", "plastic_clay", (75, 0.0015, "1/666")),
    ("isolated", "multistorey_framed", "sand_hard_clay", (60, 0.002, "1/500")),
    ("raft", "reinforced_concrete", "sand_hard_clay", (75, 0.0021, "1/500")),
    ("raft", "reinforced_concrete", "plastic_clay", (125, 0.002, "1/500")),  # 100 mm in IS 1904:1986
    ("raft", "multistorey_framed", "plastic_clay", (125, 0.0033, "1/300")),
    ("raft", "water_tower_silo", "sand_hard_clay", (100, 0.0025, "1/400")),
])
def test_is1904_table_1(fnd, struct, soil, expected):
    r = permissible_settlement_is1904(fnd, struct, soil)
    assert (r["Permissible maximum settlement [mm]"], r["Permissible differential settlement coefficient (x L) [-]"],
            r["Permissible angular distortion [-]"]) == expected


def test_is1904_load_bearing_walls_interpolate_and_check():
    r = permissible_settlement_is1904("isolated", "load_bearing_walls", "plastic_clay", length_height_ratio=4.5)
    assert r["Permissible differential settlement coefficient (x L) [-]"] == pytest.approx(0.0003)
    assert r["Permissible angular distortion [-]"] == "1/3333"
    with pytest.raises(BISInputError, match="not likely"):
        permissible_settlement_is1904("raft", "load_bearing_walls", "sand_hard_clay", length_height_ratio=3)
    r = permissible_settlement_is1904("isolated", "reinforced_concrete", "sand_hard_clay", span_length=6,
                                      calculated_max_settlement=40, calculated_differential_settlement=8)
    assert r["Permissible differential settlement [mm]"] == pytest.approx(9.0)
    assert r["Calculated angular distortion [-]"] == "1/750"
    assert r["Differential settlement within limit"] and r["Maximum settlement within limit"]


def test_is1904_stability_minimums():
    assert stability_check_is1904("sliding", 175, 100)["Meets IS 1904 minimum"]
    r = stability_check_is1904("overturning", 190, 100)
    assert r["Required minimum factor of safety [-]"] == 2.0 and not r["Meets IS 1904 minimum"]
    assert stability_check_is1904("overturning", 160, 100, wind_or_seismic=True)["Meets IS 1904 minimum"]


# ---------------------------------------------------------------------------- IS 2950

def test_raft_relative_stiffness_and_critical_spacing():
    flexible = raft_rigidity_is2950("rectangular", raft_thickness=1, concrete_modulus=2.5e7, soil_modulus=2.5e4,
                                    raft_length=10)
    assert flexible["Relative stiffness factor K [-]"] == pytest.approx(1000 / 12 * 1e-3, rel=1e-3)
    assert flexible["K criterion"].startswith("flexible")
    rigid = raft_rigidity_is2950("rectangular", raft_thickness=2.5, concrete_modulus=2.5e7, soil_modulus=2.5e4,
                                 raft_length=10)
    assert rigid["K criterion"].startswith("rigid")
    r = raft_rigidity_is2950("rectangular", raft_thickness=1, concrete_modulus=2.5e7, soil_modulus=2.5e4,
                             raft_length=10, subgrade_modulus=2e4, column_spacing=6)
    lam = (3 * 2e4 / 2.5e7) ** 0.25
    assert r["lambda [1/m]"] == pytest.approx(lam, rel=1e-3)
    assert r["Critical column spacing 1.75/lambda [m]"] == pytest.approx(1.75 / lam, rel=1e-3)
    assert r["Spacing criterion"].startswith("rigid") and r["Analysis method"].startswith("Rigid")


# ---------------------------------------------------------------------------- IS 2720

def test_specific_gravity_and_temperature_correction():
    r = specific_gravity_is2720(30, 55, 145.6, 130)
    assert r["Specific gravity at test temperature [-]"] == pytest.approx(25 / 9.4, rel=1e-3)
    assert r["Specific gravity at 27 degC [-]"] == pytest.approx(25 / 9.4, rel=1e-3)
    r20 = specific_gravity_is2720(30, 55, 145.6, 130, temperature=20)
    assert r20["Temperature correction factor K [-]"] == pytest.approx(998.21 / 996.52, abs=2e-5)


def test_liquid_limit_one_point_and_indices():
    assert liquid_limit_one_point_is2720(40, blows=25)["Liquid limit wL [%]"] == pytest.approx(40.0, abs=0.01)
    assert liquid_limit_one_point_is2720(40, blows=15)["Liquid limit wL [%]"] == pytest.approx(40 / (1.3215 - 0.23 * math.log10(15)), rel=1e-3)
    cone = liquid_limit_one_point_is2720(50, method="cone", cone_penetration=20)
    assert cone["Liquid limit wL, linear relation [%]"] == pytest.approx(50.0)
    assert cone["Liquid limit wL, log relation [%]"] == pytest.approx(50 / (0.77 * math.log10(20)), rel=1e-3)
    with pytest.raises(BISInputError, match="15-35"):
        liquid_limit_one_point_is2720(40, blows=40)
    assert flow_index_is2720(45, 10, 35, 100)["Flow index If [%]"] == pytest.approx(10.0)
    r = consistency_indices_is2720(50, 20, natural_water_content=35, flow_index=15)
    assert (r["Plasticity index Ip [%]"], r["Liquidity index IL [-]"], r["Consistency index Ic [-]"],
            r["Toughness index It [-]"]) == (30, 0.5, 0.5, 2.0)
    assert consistency_indices_is2720(30, 32)["Plasticity index Ip [%]"] == 0


def test_permeability_tests_referred_to_27_degc():
    r = permeability_constant_head_is2720(50, 15, 78.54, 30, 600, temperature=20)
    k_t = 50 * 15 / (78.54 * 30 * 600)
    assert r["Permeability at test temperature kT [cm/s]"] == pytest.approx(k_t, rel=1e-3)
    # IAPWS viscosities: 1.0016 mPa s at 20 degC, 0.8509 mPa s at 27 degC
    assert r["Permeability at 27 degC k27 [cm/s]"] == pytest.approx(k_t * 1.0016 / 0.8509, rel=5e-3)
    r = permeability_falling_head_is2720(0.5, 12, 80, 100, 50, 3600)
    assert r["Permeability at test temperature kT [cm/s]"] == pytest.approx(2.303 * 0.5 * 12 / (80 * 3600) * math.log10(2), rel=1e-3)
    assert r["Permeability at 27 degC k27 [cm/s]"] == r["Permeability at test temperature kT [cm/s]"]
    with pytest.raises(BISInputError):
        permeability_falling_head_is2720(0.5, 12, 80, 50, 100, 3600)


# ---------------------------------------------------------------------------- Wiring

def test_every_bis_function_is_a_ui_function_and_a_validated_geoai_tool():
    from core.registry import registry
    from core.geoai.schemas.bis import BIS_SCHEMAS
    from core.geoai.tool_registry import tool_registry
    from core.geoai.tool_metadata import get_tool_metadata
    assert set(BIS_SCHEMAS) == set(BIS_FUNCTIONS)
    for name, func in BIS_FUNCTIONS.items():
        assert registry.function_map[name] is func
        tool = tool_registry.get_tool(name)
        assert tool is not None and tool.input_model is BIS_SCHEMAS[name]
        assert get_tool_metadata(name)["standard"].startswith("IS ")


def test_geoai_tool_normalises_units_and_options_and_attaches_provenance():
    from core.geoai.tool_registry import tool_registry
    r = tool_registry.invoke_tool("bearing_capacity_is6403", {"width": "2000 mm", "depth": "1.5 m", "water_table_depth": 10,
                                                              "unit_weight": "18 kN/m3", "friction_angle": 30, "shape": "Strip"})
    assert r[QNU] == pytest.approx(873.0, rel=1e-3)
    assert "IS 6403" in r["_provenance"]["standard"]


def test_desktop_path_runs_bis_function_and_reports_input_errors():
    from core.registry import registry
    r = registry.execute_function("bis", "permissible_settlement_is1904",
                                  {"foundation_type": "raft", "structure_type": "reinforced_concrete", "soil_type": "plastic_clay"})
    assert r["Permissible maximum settlement [mm]"] == 125
    r = registry.execute_function("bis", "bearing_capacity_is6403",
                                  {"width": 2, "depth": 1, "water_table_depth": 0.5, "unit_weight": 18, "friction_angle": 30})
    assert "saturated_unit_weight" in (r.get("error") or "")
