# Author: Utkarsh Gupta
# License: GPL v3
"""
Desktop-UI requests for the CPT pile forms (profile id + column names, as the form posts them).

These went through schemas auto-generated from the Groundhog constructors and failed with
"Field required"; and an uploaded boolean 'Ignore shaft friction' column was renamed with a unit
suffix that LCPC did not find.
"""
import pandas as pd
import pytest

from core.registry import Registry

DATA = pd.read_csv(__import__("pathlib").Path(__file__).parent / "data" / "groundhog_cpt_koppejan.csv", comment="#")


def _rows(extra=None):
    rows = []
    for z, qc in zip(DATA["z [m]"], DATA["qc [MPa]"]):
        row = {"Depth from [m]": round(z - 0.1, 2), "Depth to [m]": round(z + 0.1, 2), "qc [MPa]": qc,
               "Total unit weight [kN/m3]": 19.0, "Soil type": "Sand"}
        row.update(extra or {})
        rows.append(row)
    return rows


@pytest.fixture(scope="module")
def registry():
    return Registry()


def _upload(registry, rows):
    out = registry.execute_function("general", "SoilProfile", {"raw_data": rows, "data_kind": "soil_profile"})
    return out["id"]


def test_koppejan_form_request_runs(registry):
    pid = _upload(registry, _rows())
    out = registry.execute_function("koppejan", "KoppejanCalculation", {
        "soilprofile": pid, "pile_diameter": "0.5", "pile_penetration": "8", "qc_col": "qc [MPa]",
        "depth_from_col": "Depth from [m]", "depth_to_col": "Depth to [m]",
        "gamma_col": "Total unit weight [kN/m3]", "water_level": 0, "water_unit_weight": 10,
        "alpha_s": 0.006, "alpha_p": 0.3, "base_coefficient": 1, "crosssection_coefficient": 1, "coring": False})
    assert "error" not in out, out


@pytest.mark.parametrize("extra", [{}, {"Ignore shaft friction": False}], ids=["column-absent", "boolean-column"])
def test_lcpc_form_request_runs_with_or_without_ignore_column(registry, extra):
    pid = _upload(registry, _rows(extra))
    out = registry.execute_function("lcpc", "LCPC_Calculation", {
        "soilprofile": pid, "pile_diameter": "0.5", "group_base": "I", "group_shaft": "IA",
        "careful_execution": False, "water_level": 0, "qc_col": "qc [MPa]", "depth_col": "Depth to [m]",
        "soil_type_col": "Soil type"})
    assert "error" not in out, out


def test_uploaded_boolean_column_keeps_its_name(registry):
    pid = _upload(registry, _rows({"Ignore shaft friction": False}))
    from core.state import state_manager
    assert "Ignore shaft friction" in state_manager.get(pid).columns


def test_debeer_form_request_runs(registry):
    pid = _upload(registry, _rows({"Tertiary clay": False}))
    out = registry.execute_function("debeer", "DeBeerCalculation", {
        "soilprofile": pid, "pile_diameter": "0.5", "cone_diameter": 0.0357, "qc_col": "qc [MPa]",
        "depth_col": "Depth to [m]", "soil_type_col": "Soil type", "tertiary_clay_col": "Tertiary clay",
        "gamma_col": "Total unit weight [kN/m3]", "water_level": 0})
    assert "error" not in out, out
