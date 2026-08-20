import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add python-backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from core.registry import Registry

client = TestClient(app)

def test_registry_loading():
    """Test that the registry loads correctly."""
    registry = Registry()
    assert len(registry.function_map) > 0

def test_manual_function_loading():
    """Test that manual functions are loaded."""
    # Ensure manual_functions.py has content or create a dummy one for test
    from core import manual_functions
    assert hasattr(manual_functions, 'example_manual_function')
    
    registry = Registry()
    assert 'example_manual_function' in registry.function_map

def test_health_check():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Geotechnical Analysis Engine Running"}

def test_list_modules():
    """Test listing modules."""
    response = client.get("/modules")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data.keys()) > 0
