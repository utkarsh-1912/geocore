import pytest
from core.geoai.gemma_engine import LocalGemmaEngine
from core.geoai.tool_registry import tool_registry
import core.geoai.tool_definitions  # Ensure tools are registered

@pytest.fixture
def engine():
    return LocalGemmaEngine()

def test_find_best_tools(engine):
    # 'calculate Rankine earth pressure' -> best match should be 'calculate_earth_pressure_rankine'
    matches = engine.find_best_tools('calculate Rankine earth pressure')
    assert matches[0]['name'] == 'calculate_earth_pressure_rankine'
    
    # 'void ratio from porosity' -> best match should be 'calculate_void_ratio_from_porosity'
    matches = engine.find_best_tools('void ratio from porosity')
    assert matches[0]['name'] == 'calculate_void_ratio_from_porosity'
    
    # 'Gmax shear wave' -> best match should be 'calculate_gmax_from_shear_wave_velocity'
    matches = engine.find_best_tools('Gmax shear wave')
    assert matches[0]['name'] == 'calculate_gmax_from_shear_wave_velocity'
    
    # 'bulk unit weight' -> best match should be 'calculate_bulk_unit_weight'
    matches = engine.find_best_tools('bulk unit weight')
    assert matches[0]['name'] == 'calculate_bulk_unit_weight'
    
    # 'circular footing stress' -> best match should be 'calculate_stresses_circular_footing'
    matches = engine.find_best_tools('circular footing stress')
    assert matches[0]['name'] == 'calculate_stresses_circular_footing'
    
    # 'hydraulic conductivity' -> best match should be 'calculate_hydraulic_conductivity_unconfined'
    matches = engine.find_best_tools('hydraulic conductivity')
    assert matches[0]['name'] == 'calculate_hydraulic_conductivity_unconfined'
    
    # Random gibberish -> should return empty or low-confidence results
    matches = engine.find_best_tools('asdfg hjkl qwerty')
    # If it returns tools, they should have score 0 (which means they are not strongly matched)
    # Actually, in find_best_tools, score > 0 is required to append.
    assert len(matches) == 0

def test_extract_parameters_from_text(engine):
    # 'phi = 32 degrees wall_angle = 5 degrees' with tool 'calculate_earth_pressure_rankine'
    text = 'phi = 32 degrees wall_angle = 5 degrees'
    params = engine.extract_parameters_from_text(text, 'calculate_earth_pressure_rankine')
    assert 'phi_eff' in params and params['phi_eff'] == 32
    assert 'wall_angle' in params and params['wall_angle'] == 5
    
    # Point load tool parameter extraction
    text = 'point load = 500 kN at depth = 4 m with radius = 2 m'
    params = engine.extract_parameters_from_text(text, 'calculate_stresses_point_load')
    assert 'z' in params and params['z'] == 4
    
    # Text with no numbers -> should return empty dict
    text = 'friction angle is high and cohesion is low'
    params = engine.extract_parameters_from_text(text, 'calculate_earth_pressure_rankine')
    assert len(params) == 0
    
    # 'Vs = 250 m/s' with Gmax tool -> should extract Vs = 250
    text = 'Vs = 250 m/s'
    params = engine.extract_parameters_from_text(text, 'calculate_gmax_from_shear_wave_velocity')
    assert 'Vs' in params and params['Vs'] == 250

def test_chat_and_execute(engine):
    # 'Calculate Rankine earth pressure for phi = 32 degrees'
    text = 'Calculate Rankine earth pressure for phi = 32 degrees'
    res = engine.chat_and_execute(text)
    assert res['executed_tool'] == 'calculate_earth_pressure_rankine'
    assert 'results' in res
    
    # Query with no matching tool -> should return helpful message
    res = engine.chat_and_execute("xyzabc nonmatching query")
    assert res['executed_tool'] is None
    assert "I couldn't identify a specific geotechnical calculation" in res['response']
    
    # Query matching tool but no parameters -> should list required parameters
    res = engine.chat_and_execute("Calculate Rankine earth pressure")
    assert res['executed_tool'] == 'calculate_earth_pressure_rankine'
    assert 'missing_parameters' in res or 'results' in res

def test_autofill_form(engine):
    # Test with sample field notes text
    text = "Borehole BH-01 shows sand with friction angle 35 degrees."
    res = engine.autofill_form('calculate_earth_pressure_rankine', text)
    
    # Test returns function_id in response
    assert res['function_id'] == 'calculate_earth_pressure_rankine'
    
    # Test returns confidence scores
    assert 'fields' in res
    assert 'phi_eff' in res['fields']
    assert res['fields']['phi_eff']['confidence'] > 0.0
    assert res['fields']['phi_eff']['value'] == 35
