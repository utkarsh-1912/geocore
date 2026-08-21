"""
Tests for GeoAI Tool Registry, SLM Tool Calling Schemas, and Invocation Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from core.geoai.tool_registry import tool_registry

client = TestClient(app)

def test_list_geoai_tools():
    response = client.get("/api/geoai/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    tool_names = [t["name"] for t in data["tools"]]
    assert "calculate_bulk_unit_weight" in tool_names
    assert "calculate_stresses_circular_footing" in tool_names

def test_export_openai_tool_schemas():
    response = client.get("/api/geoai/tools/format/openai")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) > 0
    sample = data["tools"][0]
    assert sample["type"] == "function"
    assert "parameters" in sample["function"]
    assert "properties" in sample["function"]["parameters"]

def test_export_gemini_tool_schemas():
    response = client.get("/api/geoai/tools/format/gemini")
    assert response.status_code == 200
    data = response.json()
    assert "function_declarations" in data
    assert len(data["function_declarations"]) > 0

def test_invoke_geoai_tool_valid():
    payload = {
        "tool_name": "calculate_bulk_unit_weight",
        "args": {
            "specific_gravity": 2.7,
            "voidratio": 0.6,
            "saturation": 0.9,
            "unitweight_water": 9.81
        }
    }
    response = client.post("/api/geoai/invoke", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "bulk_unit_weight" in data["result"] or "bulk unit weight [kN/m3]" in data["result"]

def test_invoke_geoai_tool_invalid():
    payload = {
        "tool_name": "calculate_bulk_unit_weight",
        "args": {
            "specific_gravity": 2.7,
            "voidratio": 0.6,
            "saturation": 2.5  # Impossible saturation > 1.0
        }
    }
    response = client.post("/api/geoai/invoke", json=payload)
    assert response.status_code == 422

def test_invoke_unregistered_tool():
    payload = {
        "tool_name": "unregistered_dangerous_command",
        "args": {}
    }
    response = client.post("/api/geoai/invoke", json=payload)
    assert response.status_code == 422
