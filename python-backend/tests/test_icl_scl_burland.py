# Author: Utkarsh Gupta
# License: GPL v3
"""
Desktop calculator for groundhog.siteinvestigation.correlations.cohesive.icl_scl_burland
(Burland, 1990): the registry returns the ICL/SCL figure plus C*c and e*100 as a table.
"""
import pytest

from core.registry import Registry


@pytest.fixture(scope="module")
def registry():
    return Registry()


def _run(registry, args):
    res = registry.execute_function("correlations_cohesive", "icl_scl_burland", args)
    assert res["type"] == "multi_plot", res
    names = [trace["name"] for trace in res["plots"][0]["data"]]
    assert names == ["Intrinsic Compression Line (ICL)", "Sedimentation Compression Line (SCL)"]
    assert res["plots"][0]["layout"]["xaxis"]["type"] == "log"
    return {row["Output"]: row["Value"] for row in res["results"]["data"]}


def test_matches_burland_1990_equations(registry):
    # Burland (1990): Cc* = 0.256 eL - 0.04; e100* = 0.109 + 0.679 eL - 0.089 eL^2 + 0.016 eL^3
    eL = 1.5
    vals = _run(registry, {"eL": eL})
    assert vals["Intrinsic compression index C*c"] == pytest.approx(0.256 * eL - 0.04, rel=1e-9)
    assert vals["Void ratio on the ICL at 100 kPa e*100"] == pytest.approx(
        0.109 + 0.679 * eL - 0.089 * eL ** 2 + 0.016 * eL ** 3, rel=1e-9)


def test_measured_values_override_the_correlation(registry):
    vals = _run(registry, {"eL": 1.5, "e100star_override": 1.1, "Ccstaroverride": 0.3})
    assert vals["Intrinsic compression index C*c"] == pytest.approx(0.3)
    assert vals["Void ratio on the ICL at 100 kPa e*100"] == pytest.approx(1.1)


def test_out_of_range_void_ratio_is_rejected(registry):
    res = registry.execute_function("correlations_cohesive", "icl_scl_burland", {"eL": 9.0})
    assert res.get("status") == "ValidationError" or "error" in res
