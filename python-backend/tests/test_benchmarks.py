# Author: Utkarsh Gupta
# License: GPL v3
"""
Verification cases (core/catalogue/benchmarks.json): each runs through registry.execute_function - the path the
forms use - and must reproduce its closed-form result. A method is shown as verified only because of these cases.
"""
import json

import pytest

from core.catalogue import (BENCHMARKS_PATH, effective_status, find_method, load_benchmarks, load_catalogue,
                            navigation, run_benchmark)

CASES = json.load(open(BENCHMARKS_PATH, encoding="utf-8"))["cases"]


@pytest.mark.parametrize("case", CASES, ids=[f"{c['method']}#{i}" for i, c in enumerate(CASES)])
def test_benchmark_reproduces_its_closed_form(case):
    result = run_benchmark(case)
    assert result["ok"], result["problems"]


def test_every_case_names_a_catalogue_method_and_states_its_source():
    for case in CASES:
        assert find_method(case["method"]) is not None, case["method"]
        assert case["source"].strip() and case["expected"]


def test_verified_is_never_hand_set_in_the_catalogue_data():
    for calc in load_catalogue()["calculations"].values():
        for m in calc["methods"]:
            assert m["status"] != "verified", f"{m['function']}: 'verified' must come from benchmarks.json"


def test_status_shown_in_the_app_follows_the_benchmarks():
    nav = {fn["id"]: fn for mod in navigation()["modules"] for g in mod["items"] for fn in g["functions"]}
    for fid in load_benchmarks():
        expected = "corrected" if fid == "mohrcoulomb_triaxial_compression" else "verified"
        assert nav[fid]["status"] == expected and nav[fid]["benchmarks"], fid
    assert nav["LCPC_Calculation"]["status"] == "unverified" and "benchmarks" not in nav["LCPC_Calculation"]
    assert effective_status({"function": "x", "status": "known_issue"}) == "known_issue"
