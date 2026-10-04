"""
Tests for the deterministic calculation explainer (core/geoai/calculation_explainer.py) and its
/api/geoai/explain(/narrate) endpoints. The formula must come from groundhog's own docstring — these
tests fail if it is ever replaced by a guessed or hand-written one.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

from core.geoai import api
from core.geoai.calculation_explainer import (explain_calculation, extract_formula, extract_param_labels,
                                               build_narration_prompt)
from core.geoai.heuristic_provider import HeuristicProvider
from core.geoai.model_provider import ModelResponse

client = TestClient(app)


def test_extract_formula_from_real_docstring():
    from core.registry import registry
    import inspect
    func = registry.find_function("earthpressurecoefficients_rankine")
    doc = inspect.getdoc(func)
    formula = extract_formula(doc)
    assert formula is not None
    assert "\\cos" in formula or "\\sin" in formula


def test_extract_formula_returns_none_without_math_block():
    assert extract_formula("No formula here, just prose.") is None
    assert extract_formula(None) is None


def test_explain_calculation_known_tool_uses_tool_metadata():
    exp = explain_calculation("earthpressurecoefficients_rankine", {"phi": 32}, {"Ka": 0.307, "Kp": 3.25})
    assert exp["method"] == "Rankine (1857) Lateral Earth Pressure Theory"
    assert "Eurocode 7" in exp["standard"]
    assert exp["formula"]  # taken from the docstring, not fabricated
    assert exp["inputs"] == [{"key": "phi", "label": None, "value": 32}]
    assert {"key": "Ka", "label": None, "value": 0.307, "unit": "-"} in exp["outputs"]


def test_explain_calculation_unknown_tool_falls_back_without_crashing():
    exp = explain_calculation("totally_unknown_function_xyz", {"a": 1}, {"b": 2.0})
    assert exp["formula"] is None
    assert "totally_unknown_function_xyz" in exp["method"]
    assert exp["outputs"] == [{"key": "b", "label": None, "value": 2.0, "unit": None}]


def test_extract_param_labels_from_real_docstring():
    from core.registry import registry
    import inspect
    func = registry.find_function("dryunitweight_watercontent")
    labels = extract_param_labels(inspect.getdoc(func))
    assert labels["bulkunitweight"] == "Bulk unit weight of the sample"
    assert labels["watercontent"].startswith("Water content of the sample")


def test_explain_calculation_attaches_real_param_labels():
    exp = explain_calculation("dryunitweight_watercontent", {"bulkunitweight": 18, "watercontent": 0.2}, {})
    labels = {i["key"]: i["label"] for i in exp["inputs"]}
    assert labels["bulkunitweight"] == "Bulk unit weight of the sample"


def test_explain_calculation_drops_internal_and_status_keys():
    exp = explain_calculation("x", {}, {"_provenance": {"x": 1}, "status": "success", "warnings": [], "value": 1.0})
    keys = {o["key"] for o in exp["outputs"]}
    assert keys == {"value"}


def test_narration_prompt_only_contains_given_facts():
    exp = explain_calculation("earthpressurecoefficients_rankine", {"phi": 32}, {"Ka": 0.307})
    prompt = build_narration_prompt(exp)
    assert "Rankine" in prompt
    assert "phi=32" in prompt
    assert "Ka=0.307" in prompt


def test_explain_endpoint_requires_function_id():
    response = client.post("/api/geoai/explain", json={"args": {}, "results": {}})
    assert response.status_code == 400


def test_explain_endpoint_returns_grounded_explanation():
    payload = {"function_id": "earthpressurecoefficients_rankine", "args": {"phi": 32},
               "results": {"Ka": 0.307, "Kp": 3.25}}
    response = client.post("/api/geoai/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["method"] == "Rankine (1857) Lateral Earth Pressure Theory"
    assert data["formula"]


def test_narrate_endpoint_degrades_without_a_local_model(monkeypatch):
    # With the heuristic fallback active (no GGUF model), narration must be skipped rather than
    # calling generate() on it: HeuristicProvider.generate() routes text as a tool-call request,
    # not a narration, and would return nonsense for this prompt.
    monkeypatch.setattr(api.lifecycle_manager, "get_provider", lambda: HeuristicProvider())
    payload = {"function_id": "earthpressurecoefficients_rankine", "args": {"phi": 32},
               "results": {"Ka": 0.307}}
    response = client.post("/api/geoai/explain/narrate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["narration"] is None
    assert "reason" in data


class _FakeNarratingProvider:
    """A minimal ModelProvider stand-in with a real GGUF model's shape, for a fast, deterministic test."""

    def model_info(self):
        return {"provider": "llama_cpp"}

    def generate(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        return ModelResponse(content="Rankine's active coefficient was computed for phi=32.",
                             tool_calls=None, finish_reason="stop", usage=None)


def test_narrate_endpoint_returns_model_narration(monkeypatch):
    monkeypatch.setattr(api.lifecycle_manager, "get_provider", lambda: _FakeNarratingProvider())
    monkeypatch.setattr(api.lifecycle_manager, "touch", lambda: None)
    payload = {"function_id": "earthpressurecoefficients_rankine", "args": {"phi": 32},
               "results": {"Ka": 0.307}}
    response = client.post("/api/geoai/explain/narrate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["narration"] == "Rankine's active coefficient was computed for phi=32."
