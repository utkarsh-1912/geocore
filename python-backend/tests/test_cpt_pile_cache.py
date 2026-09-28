import pandas as pd

from core.geoai import cpt_pile_capacity as engine
from core.geoai.project_cpt import ProjectCPT


def _cpt(qc_scale=1.0):
    data = pd.DataFrame({"depth_m": [0.0, 1.0, 2.0], "qc_mpa": [1.0 * qc_scale, 2.0, 3.0], "fs_kpa": [10.0, 20.0, 30.0]})
    return ProjectCPT(cpt_id="CPT-03", data=data, source={"object_id": "x"})


def test_cache_reuses_identical_inputs_and_never_serves_stale(monkeypatch):
    calls = []

    def fake_calculate(cpt, *args):
        calls.append(args)
        return {"total_kN": float(cpt.data["qc_mpa"].sum()) * args[2], "rows": [1, 2]}

    engine._RESULT_CACHE.clear()
    monkeypatch.setattr(engine, "calculate", fake_calculate)
    args = ("koppejan", "driven_closed_steel", 0.6, 1.5, None, None, None, None, None, None, None)

    first = engine.calculate_cached(_cpt(), *args)
    first["rows"].append("mutated")
    second = engine.calculate_cached(_cpt(), *args)
    assert len(calls) == 1 and second["rows"] == [1, 2]

    engine.calculate_cached(_cpt(qc_scale=2.0), *args)            # different CPT data
    engine.calculate_cached(_cpt(), *args[:2], 0.8, *args[3:])    # different diameter
    assert len(calls) == 3


def test_errors_are_not_cached(monkeypatch):
    calls = []

    def failing(cpt, *args):
        calls.append(1)
        raise ValueError("tip below CPT end")

    engine._RESULT_CACHE.clear()
    monkeypatch.setattr(engine, "calculate", failing)
    for _ in range(2):
        try:
            engine.calculate_cached(_cpt(), "lcpc")
        except ValueError:
            pass
    assert len(calls) == 2
