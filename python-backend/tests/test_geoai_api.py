"""
Integration Tests for FastAPI /api/execute endpoint with GeoAI validation
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_api_execute_valid_calculation():
    payload = {
        "moduleId": "classification_phase",
        "functionId": "bulkunitweight",
        "args": {
            "specific_gravity": 2.7,
            "voidratio": 0.5,
            "saturation": 1.0,
            "unitweight_water": 9.81
        }
    }
    response = client.post("/api/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert any("bulk unit weight" in k for k in data.keys())

def test_api_execute_validation_error_returns_422():
    payload = {
        "moduleId": "classification_phase",
        "functionId": "bulkunitweight",
        "args": {
            "specific_gravity": "-",
            "voidratio": 0.5,
            "saturation": 1.0
        }
    }
    response = client.post("/api/execute", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert data["detail"]["status"] == "ValidationError"

def test_api_execute_missing_function_id():
    response = client.post("/api/execute", json={"moduleId": "general", "args": {}})
    assert response.status_code == 400
