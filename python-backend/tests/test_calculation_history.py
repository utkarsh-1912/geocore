# Author: Utkarsh Gupta
# License: GPL v3
"""
Tests for the calculation audit trail (core/calculation_history.py) and its
/api/calculation-history endpoints — the durable record of every calculation run through the
main calculation UI (/api/execute), independent of GeoAI's own in-memory per-session history.
"""
import pytest
from fastapi.testclient import TestClient

from core import state
from core.state import StateManager
from main import app

client = TestClient(app)


@pytest.fixture
def sm(tmp_path, monkeypatch):
    """A fresh StateManager on an isolated config dir, same pattern as test_project_groundwater_and_data_kind.py."""
    from core.paths import CONFIG_DIR_ENV_VAR
    monkeypatch.setenv(CONFIG_DIR_ENV_VAR, str(tmp_path / "config"))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(state, "_BACKEND_DIR", tmp_path / "backend")
    manager = StateManager()
    manager._loaded = True
    monkeypatch.setattr(state, "state_manager", manager)
    return manager


def test_record_and_list_calculation(sm):
    from core.calculation_history import record_calculation, list_calculation_history
    record_calculation("earthpressurecoefficients_rankine", {"phi": 32}, {"Ka": 0.307, "Kp": 3.25})
    history = list_calculation_history()
    assert len(history) == 1
    entry = history[0]
    assert entry["function_id"] == "earthpressurecoefficients_rankine"
    assert entry["inputs"] == {"phi": 32}
    assert entry["outputs"] == {"Ka": 0.307, "Kp": 3.25}
    assert "id" in entry and "timestamp_utc" in entry
    assert entry["reviewed"] is False and entry["reviewed_at"] is None


def test_mark_reviewed_sets_fields(sm):
    from core.calculation_history import record_calculation, list_calculation_history, mark_reviewed
    record_calculation("fn", {}, {"x": 1})
    entry_id = list_calculation_history()[0]["id"]

    assert mark_reviewed(entry_id, reviewed=True, note="Checked against hand calc") is True
    entry = list_calculation_history()[0]
    assert entry["reviewed"] is True
    assert entry["reviewed_at"] is not None
    assert entry["reviewed_note"] == "Checked against hand calc"

    assert mark_reviewed(entry_id, reviewed=False) is True
    entry = list_calculation_history()[0]
    assert entry["reviewed"] is False
    assert entry["reviewed_at"] is None
    assert entry["reviewed_note"] is None


def test_mark_reviewed_unknown_id_returns_false(sm):
    from core.calculation_history import mark_reviewed
    assert mark_reviewed("does-not-exist") is False


def test_list_returns_newest_first(sm):
    from core.calculation_history import record_calculation, list_calculation_history
    record_calculation("fn_a", {}, {"x": 1})
    record_calculation("fn_b", {}, {"x": 2})
    history = list_calculation_history()
    assert [h["function_id"] for h in history] == ["fn_b", "fn_a"]


def test_drops_internal_and_status_keys(sm):
    from core.calculation_history import record_calculation, list_calculation_history
    record_calculation("fn", {}, {"_provenance": {"a": 1}, "status": "success", "warnings": [], "value": 1.0})
    assert list_calculation_history()[0]["outputs"] == {"value": 1.0}


def test_large_structures_are_sized_not_dumped(sm):
    from core.calculation_history import record_calculation, list_calculation_history
    record_calculation("fn", {}, {"big_list": list(range(50)), "small_list": [1, 2]})
    outputs = list_calculation_history()[0]["outputs"]
    assert outputs["big_list"] == "[50 items]"
    assert outputs["small_list"] == [1, 2]


def test_history_caps_at_max_entries(sm, monkeypatch):
    import core.calculation_history as ch
    monkeypatch.setattr(ch, "MAX_ENTRIES", 3)
    for i in range(5):
        ch.record_calculation(f"fn_{i}", {}, {"i": i})
    history = ch.list_calculation_history(limit=None)
    assert len(history) == 3
    assert [h["function_id"] for h in history] == ["fn_4", "fn_3", "fn_2"]


def test_clear_calculation_history(sm):
    from core.calculation_history import record_calculation, list_calculation_history, clear_calculation_history
    record_calculation("fn", {}, {"x": 1})
    clear_calculation_history()
    assert list_calculation_history() == []


def test_recording_never_raises_on_bad_input(sm):
    from core.calculation_history import record_calculation
    class Unserializable:
        pass
    # Must not raise even when a value can't be JSON-written cleanly.
    record_calculation("fn", {"obj": Unserializable()}, {"x": 1})


def test_execute_endpoint_records_history(sm, monkeypatch):
    import core.router as core_router

    def fake_execute(module_id, function_id, args):
        return {"result_value": 42.0}

    monkeypatch.setattr(core_router.registry, "execute_function", fake_execute)
    response = client.post("/api/execute", json={"moduleId": "m", "functionId": "fn_exec", "args": {"a": 1}})
    assert response.status_code == 200

    from core.calculation_history import list_calculation_history
    history = list_calculation_history()
    assert len(history) == 1
    assert history[0]["function_id"] == "fn_exec"


def test_calculation_history_endpoints(sm):
    from core.calculation_history import record_calculation
    record_calculation("fn", {"a": 1}, {"b": 2})

    response = client.get("/api/calculation-history")
    assert response.status_code == 200
    assert len(response.json()["history"]) == 1

    response = client.delete("/api/calculation-history")
    assert response.status_code == 200

    response = client.get("/api/calculation-history")
    assert response.json()["history"] == []


def test_review_endpoint_marks_entry_reviewed(sm):
    from core.calculation_history import record_calculation, list_calculation_history
    record_calculation("fn", {"a": 1}, {"b": 2})
    entry_id = list_calculation_history()[0]["id"]

    response = client.patch(f"/api/calculation-history/{entry_id}", json={"reviewed": True, "note": "OK"})
    assert response.status_code == 200
    entry = list_calculation_history()[0]
    assert entry["reviewed"] is True
    assert entry["reviewed_note"] == "OK"


def test_review_endpoint_unknown_id_returns_404(sm):
    response = client.patch("/api/calculation-history/does-not-exist", json={"reviewed": True})
    assert response.status_code == 404
