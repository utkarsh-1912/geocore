"""
GeoAI exposure policy (AGENTS.md §7, §8): internal helpers never reach the model-facing tool
list, while the desktop UI registry still exposes every calculation.
"""
import pytest

from core.registry import registry
import core.geoai.tool_definitions  # noqa: F401
from core.geoai.exceptions import GeoAIValidationError
from core.geoai.exposure_policy import EXCLUDED_FUNCTIONS, EXCLUDED_MODULES, exclusion_reason, is_model_exposed
from core.geoai.schema_factory import MODEL_EXCLUDED_FUNCTIONS
from core.geoai.schemas import SCHEMA_REGISTRY
from core.geoai.slm_schema_generator import generate_gemini_tool_definitions, generate_openai_tool_definitions
from core.geoai.tool_registry import tool_registry
from core.geoai.validator import validate_and_coerce_inputs

# Helpers that must never be offered to the SLM.
HELPERS = [
    "merge_two_dicts", "reverse_dict", "map_args", "validate_boolean", "validate_float", "validate_integer",
    "validate_list", "validate_string", "Validator", "example_manual_function", "offsets", "selectpoints",
    "peak_picker", "get_projected_point", "latlon_distance", "check_layer_overlap", "map_depth_properties",
    "profile_from_dataframe", "create_blank_soilprofile", "read_excel", "CalculationGrid", "SoilProfile",
    "AGSConverter", "read_ags", "LogPlot", "LogPlotMatplotlib", "plot_with_log", "plot_fence_diagram",
    "plot_longitudinal_profile", "plotcycliccontours_dssclay_andersen", "PSDChart", "PlasticityChart",
    "retrieve_geological_profile_bro", "SettlementCalculation", "ShallowFoundationCapacity",
]
# Borderline functions deliberately kept as engineering capabilities.
KEPT = ["constant_value", "linear_trend", "logtimemethod", "mohrcoulomb_triaxial_compression",
        "pilegroupeffect_reesevanimpe", "cycliccontours_dssclay_andersen", "nq_frictionangle_sand"]

UI_FUNCTION_COUNT = 222  # core.registry.Registry.function_map (desktop calculation forms)


def _model_facing_names():
    return {
        "list_tools": {t["name"] for t in tool_registry.list_tools()},
        "openai": {t["function"]["name"] for t in generate_openai_tool_definitions()},
        "gemini": {t["name"] for t in generate_gemini_tool_definitions()["function_declarations"]},
    }


@pytest.mark.parametrize("name", HELPERS)
def test_helpers_never_reach_the_model(name):
    assert name in registry.function_map  # still a UI function
    assert not is_model_exposed(name, getattr(registry.function_map[name], "__module__", None))
    for listing, names in _model_facing_names().items():
        assert name not in names, f"{name} leaked into {listing}"
    with pytest.raises(GeoAIValidationError, match="not in the authorized"):
        tool_registry.invoke_tool(name, {})


@pytest.mark.parametrize("name", KEPT)
def test_engineering_capabilities_stay_exposed(name):
    assert tool_registry.get_tool(name) is not None


def test_ui_registry_is_unchanged_and_keeps_schemas():
    assert len(registry.function_map) == UI_FUNCTION_COUNT
    assert all(name in SCHEMA_REGISTRY for name in registry.function_map)
    # The desktop form path still validates an excluded function's inputs.
    validated, _ = validate_and_coerce_inputs("latlon_distance", {"lon1": 3.0, "lat1": 51.0, "lon2": 3.1, "lat2": 51.1})
    assert validated["lat2"] == 51.1


def test_every_exclusion_has_a_reason_and_matches_a_ui_function():
    assert set(MODEL_EXCLUDED_FUNCTIONS) == {
        n for n, o in registry.function_map.items() if exclusion_reason(n, getattr(o, "__module__", None))}
    assert all(MODEL_EXCLUDED_FUNCTIONS.values())
    assert set(EXCLUDED_FUNCTIONS) <= set(registry.function_map)
    modules = {getattr(o, "__module__", None) for o in registry.function_map.values()}
    assert set(EXCLUDED_MODULES) <= modules
    # Model-facing tools = UI functions minus exclusions, plus curated GeoAI tools.
    exposed_groundhog = {n for n in tool_registry._tools if n in registry.function_map}
    assert exposed_groundhog == set(registry.function_map) - set(MODEL_EXCLUDED_FUNCTIONS)
