"""A plain calculation request is answered from the deterministic tool result, without a second model pass."""
import pytest

from core.geoai.agent import _wants_model_explanation

OK = [{"name": "t", "result": {"status": "success", "result": {"x": 1}}}]
FAILED = [{"name": "t", "result": {"status": "error", "error": "missing qc"}}]


@pytest.mark.parametrize("message", [
    "Classify CPT soil behavior type at depth 4.5m for qc = 14.2 MPa and fs = 65 kPa",
    "Calculate Ka for phi = 34 deg",
])
def test_plain_calculation_skips_model_writeup(message):
    assert not _wants_model_explanation("on_request", message, OK)


SBT = [{"name": "classify_cpt_soil_behavior", "result": {"status": "success", "result": {"Ic": 1.27}}}]


def test_interpretive_results_get_an_explanation_without_asking():
    message = "Classify CPT soil behavior type at depth 4.5m for qc = 14.2 MPa and fs = 65 kPa"
    assert _wants_model_explanation("on_request", message, SBT, ["classify_cpt_soil_behavior"])
    assert not _wants_model_explanation("never", message, SBT, ["classify_cpt_soil_behavior"])


def test_registry_marks_cpt_classification_interpretive():
    import core.geoai.tool_definitions  # noqa: F401  (registers the tools)
    from core.geoai.tool_registry import tool_registry
    assert tool_registry.get_tool("classify_cpt_soil_behavior").interpretive
    assert not tool_registry.get_tool("derive_cpt_parameters").interpretive


@pytest.mark.parametrize("message", ["Calculate Ka and explain the result", "Why is Ic so low?", "Interpret this CPT"])
def test_explanation_requests_use_the_model(message):
    assert _wants_model_explanation("on_request", message, OK)


def test_failures_go_to_the_model_unless_never():
    assert _wants_model_explanation("on_request", "Calculate Ka", FAILED)
    assert not _wants_model_explanation("never", "explain", FAILED)


def test_always_mode():
    assert _wants_model_explanation("always", "Calculate Ka", OK)
