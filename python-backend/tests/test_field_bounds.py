"""The form-facing bounds endpoint mirrors the inventory (Groundhog's validated ranges)."""
from core.geoai.inventory_sync import field_bounds


def test_field_bounds_shape_and_known_values():
    bounds = field_bounds()
    p = bounds["stresses_circle"]["poissonsratio"]
    assert (p["min"], p["max"]) == (0.0, 0.5)
    assert bounds["stresses_circle"]["z"]["min"] == 0.0
    assert bounds["stresses_circle"]["z"]["max"] is None
    assert "imposedstress" not in bounds["stresses_circle"]  # unbounded -> omitted


def test_field_bounds_only_numeric_and_bounded():
    for func, params in field_bounds().items():
        for name, b in params.items():
            assert b["min"] is not None or b["max"] is not None, f"{func}.{name}"
            if b["min"] is not None and b["max"] is not None:
                assert b["min"] <= b["max"], f"{func}.{name}"
