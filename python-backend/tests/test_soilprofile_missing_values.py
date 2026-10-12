"""Soil profile upload: the 'Missing values' choice (nan_strategy) offered by the form."""
import math

import pytest

from core.registry import Registry
from core.state import state_manager


@pytest.fixture(scope="module")
def registry():
    return Registry()


ROWS = [
    {"Depth from [m]": 0, "Depth to [m]": 2, "qc [MPa]": 1.5, "Soil type": "SAND"},
    {"Depth from [m]": 2, "Depth to [m]": 5, "qc [MPa]": None, "Soil type": "CLAY"},
]


def _upload(registry, **extra):
    return registry.execute_function("general", "SoilProfile", {"raw_data": ROWS, "data_kind": "soil_profile", **extra})


@pytest.mark.parametrize("extra", [{}, {"nan_strategy": "fill"}, {"nan_strategy": ""}])
def test_fill_is_the_default_and_fills_numbers_with_zero(registry, extra):
    out = _upload(registry, **extra)
    assert "error" not in out, out
    assert state_manager.get(out["id"])["qc [MPa]"].tolist() == [1.5, 0.0]


def test_keep_leaves_missing_numbers_blank(registry):
    out = _upload(registry, nan_strategy="keep")
    assert "error" not in out, out
    qc = state_manager.get(out["id"])["qc [MPa]"].tolist()
    assert qc[0] == 1.5 and math.isnan(qc[1])


def test_unknown_strategy_is_rejected_instead_of_silently_keeping(registry):
    out = _upload(registry, nan_strategy="interpolate")
    assert "Unknown missing-value strategy" in out["error"]
