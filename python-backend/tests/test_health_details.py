"""
Tests for the System Health diagnostics endpoint.
"""
from fastapi.testclient import TestClient

from main import app
from core.diagnostics import collect_diagnostics

client = TestClient(app)


def test_health_stays_lightweight():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.0.0"}


def test_health_details_shape():
    response = client.get("/health/details")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["uptime_seconds"] >= 0
    for section in ("engine", "runtime", "memory", "geoai"):
        assert isinstance(data[section], dict)

    assert isinstance(data["engine"]["ready"], bool)
    assert isinstance(data["engine"]["functions_registered"], int)
    assert data["runtime"]["python"].count(".") == 2
    assert isinstance(data["geoai"]["loaded"], bool)


def test_health_details_does_not_load_model():
    from core.geoai.lifecycle import lifecycle_manager

    lifecycle_manager.unload()
    client.get("/health/details")
    assert lifecycle_manager._provider is None


def test_collect_diagnostics_passes_function_count_through():
    assert collect_diagnostics(functions_registered=42)["engine"]["functions_registered"] == 42
    assert collect_diagnostics()["engine"]["functions_registered"] is None
