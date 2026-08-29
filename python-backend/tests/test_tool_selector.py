import pytest
from core.geoai.tool_selector import (
    infer_categories,
    format_tools_for_prompt,
    select_relevant_tools
)
import core.geoai.tool_definitions  # Ensure tools are registered

def test_infer_categories():
    assert 'deep_foundations' in infer_categories('calculate pile capacity')
    assert 'shallow_foundations' in infer_categories('bearing capacity of shallow footing')
    assert 'earth_pressure' in infer_categories('rankine earth pressure')
    assert 'soil_dynamics' in infer_categories('Gmax from shear wave velocity')
    assert 'phase_relations' in infer_categories('void ratio from porosity')
    assert infer_categories('') == []
    assert infer_categories('generic non geotechnical query') == []

def test_format_tools_for_prompt():
    tools = [{
        "name": "calculate_earth_pressure",
        "description": "Calculates earth pressure. This is a very long second sentence that should be removed. And a third.",
        "input_schema": {
            "type": "object",
            "properties": {"phi": {"type": "number"}}
        }
    }]
    
    formatted = format_tools_for_prompt(tools)
    assert len(formatted) == 1
    assert formatted[0]["type"] == "function"
    assert formatted[0]["function"]["name"] == "calculate_earth_pressure"
    assert formatted[0]["function"]["description"] == "Calculates earth pressure."
    assert "parameters" in formatted[0]["function"]
    
    # Test empty tool list
    assert format_tools_for_prompt([]) == []

def test_select_relevant_tools():
    # Test with rankine query returns tools
    tools = select_relevant_tools("rankine earth pressure")
    assert len(tools) > 0
    assert any("rankine" in t["function"]["name"].lower() or "earth_pressure" in t["function"]["name"].lower() for t in tools)
    
    # Test max_tools limit is respected
    tools = select_relevant_tools("calculate", max_tools=2)
    assert len(tools) <= 2
    
    # Test returns OpenAI format tools
    assert all("type" in t and t["type"] == "function" for t in tools)
    assert all("function" in t for t in tools)
    
    # Test with context having activeFunction includes that function
    context = {"activeFunction": "calculate_stresses_point_load"}
    tools = select_relevant_tools("unrelated query", context=context)
    assert any(t["function"]["name"] == "calculate_stresses_point_load" for t in tools)
