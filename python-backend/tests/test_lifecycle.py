# Author: Utkarsh Gupta
# License: GPL v3
"""
Automated Test Suite for Model Lifecycle Management, Desktop Memory Optimization,
and FastAPI Lifecycle Endpoints.
"""

import pytest
import time
from fastapi.testclient import TestClient

from core.geoai.lifecycle import ModelLifecycleManager
from core.geoai.model_provider import ModelProvider, ModelResponse
from core.geoai.api import router
from fastapi import FastAPI

# Build test client
app = FastAPI()
app.include_router(router, prefix="/api")
client = TestClient(app)


class MockLifecycleProvider(ModelProvider):
    def __init__(self):
        self.loaded = True

    def is_loaded(self) -> bool:
        return self.loaded

    def model_info(self):
        return {"provider": "mock_lifecycle", "loaded": self.loaded}

    def generate(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        return ModelResponse(content="Mock response", finish_reason="stop")

    def generate_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        yield from []

    def unload(self):
        self.loaded = False


# =====================================================================
# 1. ModelLifecycleManager Unit Tests
# =====================================================================

def test_lifecycle_manager_basic_flow():
    mgr = ModelLifecycleManager(idle_timeout_seconds=2.0)
    provider = MockLifecycleProvider()
    mgr.set_provider(provider)

    status = mgr.get_memory_status()
    assert "process_ram_mb" in status
    assert status["is_model_loaded"] is True
    assert status["model_info"]["provider"] == "mock_lifecycle"

    # Touch and check idle
    mgr.touch()
    assert mgr.check_idle_and_unload() is False

    # Explicit unload
    unloaded = mgr.unload()
    assert unloaded["status"] == "unloaded"
    assert mgr.get_memory_status()["is_model_loaded"] is False


def test_lifecycle_manager_idle_timeout():
    mgr = ModelLifecycleManager(idle_timeout_seconds=0.1)
    provider = MockLifecycleProvider()
    mgr.set_provider(provider)

    time.sleep(0.15)
    # Model should auto-unload due to timeout
    did_unload = mgr.check_idle_and_unload()
    assert did_unload is True
    assert mgr.get_memory_status()["is_model_loaded"] is False


# =====================================================================
# 2. FastAPI Lifecycle Endpoints Tests
# =====================================================================

def test_api_status_endpoint():
    response = client.get("/api/geoai/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "tools_registered" in data
    assert data["tools_registered"] >= 10


def test_api_models_endpoint():
    response = client.get("/api/geoai/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) >= 3


def test_api_memory_endpoint():
    response = client.get("/api/geoai/memory")
    assert response.status_code == 200
    data = response.json()
    assert "process_ram_mb" in data
    assert "is_model_loaded" in data


def test_api_unload_endpoint():
    response = client.post("/api/geoai/unload")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unloaded"


def test_api_select_model_endpoint():
    response = client.post("/api/geoai/models/select", json={
        "model_path": "test/path/model.gguf",
        "provider": "llama_cpp"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "model_selected"
    assert data["config"]["model_path"] == "test/path/model.gguf"
