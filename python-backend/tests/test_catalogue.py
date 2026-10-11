# Author: Utkarsh Gupta
# License: GPL v3
"""
The calculation catalogue (core/catalogue) is complete and consistent (Phase 0 of the catalogue upgrade).

Completeness: every calculation the desktop app can open (electron-app/src/config/geotechnicalModules.js) and
every function the backend registry knows is either a catalogue method or listed as internal with a reason,
and nothing in the catalogue points at a function that does not exist.
"""
import json
import warnings

import pytest
from fastapi.testclient import TestClient

from core.catalogue import CatalogueError, DATA_TAGS, STATUSES, api_payload, coverage, find_method, load_catalogue
from core.catalogue.envelope import envelope, extract_values
from core.catalogue.sidebar import iter_sidebar_functions, load_sidebar
from core.registry import Registry


@pytest.fixture(scope="module")
def ids():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        backend = set(Registry().function_map)
    return {f["id"] for f in iter_sidebar_functions()}, backend


def test_sidebar_reader_sees_the_whole_navigation():
    entries = list(iter_sidebar_functions())
    assert len(load_sidebar()) == 11 and len(entries) == 221
    assert len({e["id"] for e in entries}) == len(entries)


def test_catalogue_is_complete(ids):
    sidebar, backend = ids
    assert coverage(sidebar, backend) == {
        "sidebar_not_catalogued": [], "backend_not_catalogued": [],
        "methods_without_function": [], "internal_without_function": []}


def test_every_calculation_the_app_opens_maps_to_one_method_or_is_internal(ids):
    sidebar, _ = ids
    cat = load_catalogue()
    for fid in sidebar:
        assert (fid in cat["methods"]) != (fid in cat["internal"]), fid


def test_structure_is_valid_and_complete():
    cat = load_catalogue()  # raises CatalogueError on any structural problem
    assert len(cat["domains"]) == 10
    for calc in cat["calculations"].values():
        assert calc["default_method"] in {m["id"] for m in calc["methods"]}
        assert set(calc.get("data", [])) <= set(DATA_TAGS)
        assert {m["status"] for m in calc["methods"]} <= set(STATUSES)
    assert all(reason for reason in cat["internal"].values())


def test_merged_calculations_group_the_methods_of_one_question():
    cat = load_catalogue()
    methods = lambda cid: [m["function"] for m in cat["calculations"][cid]["methods"]]  # noqa: E731
    assert methods("pile_axial_capacity") == ["AxCapCalculation", "LCPC_Calculation", "KoppejanCalculation",
                                              "DeBeerCalculation"]
    assert len(methods("phase_relations")) == 14
    assert len(methods("pile_unit_shaft_friction")) == 4 and len(methods("pile_unit_end_bearing")) == 4
    assert find_method("LCPC_Calculation")["calculation"]["id"] == "pile_axial_capacity"
    assert find_method("validate_float") is None  # a library helper, not a calculation


def test_developer_helpers_are_internal_not_calculations():
    internal = load_catalogue()["internal"]
    for helper in ("validate_float", "validate_string", "merge_two_dicts", "reverse_dict"):
        assert helper in internal


def test_status_notes_are_required_for_corrected_methods():
    m = find_method("mohrcoulomb_triaxial_compression")["method"]
    assert m["status"] == "corrected" and "groundhog_corrections" in m["status_note"]


def test_malformed_catalogue_is_rejected(tmp_path, monkeypatch):
    import core.catalogue as catalogue
    (tmp_path / "x.json").write_text(json.dumps({"domain": {"id": "x", "title": "X"}, "calculations": [
        {"id": "c", "title": "C", "group": "G", "default_method": "nope",
         "methods": [{"id": "m", "label": "M", "function": "f", "status": "maybe"}]}]}), encoding="utf-8")
    (tmp_path / "_internal.json").write_text(json.dumps({"sidebar": [], "backend_only": []}), encoding="utf-8")
    monkeypatch.setattr(catalogue, "DATA_DIR", str(tmp_path))
    catalogue.load_catalogue.cache_clear()
    try:
        with pytest.raises(CatalogueError) as err:
            catalogue.load_catalogue()
        assert "default_method" in str(err.value) and "status 'maybe'" in str(err.value)
    finally:
        monkeypatch.undo()
        catalogue.load_catalogue.cache_clear()


def test_catalogue_endpoint():
    from main import app
    body = TestClient(app).get("/api/catalogue").json()
    assert body == api_payload()
    assert [d["id"] for d in body["domains"]][:2] == ["ground_data", "ground_characterisation"]
    assert sum(len(d["calculations"]) for d in body["domains"]) == len(load_catalogue()["calculations"])


def test_envelope_names_values_and_keeps_the_raw_response():
    raw = {"sigma_1_f [kPa]": 112.2, "Failure angle [deg]": 27.5, "Mohr circle": {"columns": [], "n_rows": 0},
           "Plot": {"data": [], "layout": {}}}
    env = envelope("mohrcoulomb_triaxial_compression", raw)
    assert env["raw"] is raw and env["calculation"] == "mohrcoulomb_triaxial_compression"
    by_key = {v["key"]: v for v in env["values"]}
    assert by_key["sigma_1_f [kPa]"]["label"] == "Axial stress at failure" and by_key["sigma_1_f [kPa]"]["unit"] == "kPa"
    assert by_key["Failure angle [deg]"]["symbol"] == "θf"
    assert set(by_key) == {"sigma_1_f [kPa]", "Failure angle [deg]"}  # tables and figures are not values


def test_envelope_reads_wrapper_output_tables():
    raw = {"type": "multi_plot", "plots": [], "results": {"type": "dataframe", "columns": ["Output", "Value", "Unit"],
           "data": [{"Output": "sigma_1_f", "Value": 300.0, "Unit": "kPa"}, {"Output": "note", "Value": [1], "Unit": "-"}]}}
    values = extract_values("mohrcoulomb_triaxial_compression", raw)
    assert values == [{"key": "sigma_1_f", "label": "Axial stress at failure", "symbol": "σ₁f", "unit": "kPa",
                       "value": 300.0}]
    assert extract_values("x", {"error": "boom"}) == [] and extract_values("x", [1, 2]) == []


def test_app_navigation_copy_is_up_to_date():
    import os
    from core.catalogue import APP_NAVIGATION_PATH, navigation_json
    assert os.path.exists(APP_NAVIGATION_PATH), "run: python -m core.catalogue"
    with open(APP_NAVIGATION_PATH, encoding="utf-8") as f:
        assert f.read() == navigation_json(), "catalogueNavigation.json is stale: run python -m core.catalogue"


def test_catalogue_navigation_opens_every_calculation_the_classic_one_does(ids):
    """Switching the sidebar to the catalogue view loses nothing: same function ids, each once, minus internals."""
    from core.catalogue import navigation
    sidebar, _ = ids
    nav_ids = [fn["id"] for m in navigation()["modules"] for g in m["items"] for fn in g["functions"]]
    assert len(nav_ids) == len(set(nav_ids))
    assert set(nav_ids) == sidebar - set(load_catalogue()["internal"])
    for m in navigation()["modules"]:
        assert m["items"] and all(g["functions"] for g in m["items"]), m["id"]
        assert len({g["id"] for g in m["items"]}) == len(m["items"]), m["id"]
