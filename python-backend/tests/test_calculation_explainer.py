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


def test_extract_formula_keeps_piecewise_cases_after_blank_line():
    doc = ("Summary.\n\n.. math::\n    B = 2 \\cdot \\sqrt{D \\cdot z - z^2} \\quad \\text{for } z < D/2\n"
           "    \n    B=D \\quad \\text{for } z \\geq D/2\n\n:returns: x")
    formula = extract_formula(doc)
    assert "z < D/2" in formula
    assert "B=D" in formula and "z \\geq D/2" in formula
    assert ":returns" not in formula


def test_extract_formula_returns_none_without_math_block():
    assert extract_formula("No formula here, just prose.") is None
    assert extract_formula(None) is None


def test_explain_calculation_known_tool_uses_tool_metadata():
    exp = explain_calculation("earthpressurecoefficients_rankine", {"phi": 32}, {"Ka": 0.307, "Kp": 3.25})
    assert exp["method"] == "Rankine (1857) Lateral Earth Pressure Theory"
    assert "Eurocode 7" in exp["standard"]
    assert exp["formula"]  # taken from the docstring, not fabricated
    assert exp["inputs"] == [{"key": "phi", "label": None, "symbol": None, "value": 32, "unit": None}]
    assert {"key": "Ka", "label": None, "symbol": None, "value": 0.307, "unit": "-"} in exp["outputs"]


def test_explain_calculation_unknown_tool_falls_back_without_crashing():
    exp = explain_calculation("totally_unknown_function_xyz", {"a": 1}, {"b": 2.0})
    assert exp["formula"] is None
    assert "totally_unknown_function_xyz" in exp["method"]
    assert exp["outputs"] == [{"key": "b", "label": None, "symbol": None, "value": 2.0, "unit": None}]


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


# --- worked derivation (steps) -----------------------------------------------------------------

API_SAND_ARGS = {"api_relativedensity": "Dense", "api_soildescription": "Sand", "sigma_vo_eff": 53, "qb_limit": True}
API_SAND_RESULTS = {"q_b_coring [kPa]": 2120.0, "q_b_plugged [kPa]": 2120.0, "internal_friction": False,
                    "q_b_lim [kPa]": 10000.0, "Nq [-]": 40.0}


def test_uncurated_function_uses_docstring_method_and_reference_not_generic_text():
    exp = explain_calculation("API_unit_end_bearing_sand_rp2geo", API_SAND_ARGS, API_SAND_RESULTS)
    assert exp["method"] == "Calculates unit end bearing in sand according to API RP2 GEO."
    assert exp["standard"].startswith("API RP 2GEO")
    assert "Groundhog Deterministic" not in exp["method"]
    assert exp["assumptions"] == []  # the generic "deterministic calculation" line says nothing


def test_steps_walk_from_objective_to_result_with_formula_symbol_values():
    exp = explain_calculation("API_unit_end_bearing_sand_rp2geo", API_SAND_ARGS, API_SAND_RESULTS)
    # The objective is the card heading here (no curated method), so it is not repeated as a step.
    assert [st["title"] for st in exp["steps"]] == ["Given", "Governing equation", "Result"]
    equation = exp["steps"][1]
    assert equation["formula"] == exp["formula"]  # straight from the docstring
    where = {w["symbol"]: (w["value"], w["unit"]) for w in equation["where"]}
    assert where["p'_{o,tip}"] == (53, "kPa")  # input, matched by its documented symbol
    assert where["N_q"] == (40.0, "-")         # output without a symbol, matched to N_q by key
    given = {i["key"]: i for i in exp["steps"][0]["items"]}
    assert given["sigma_vo_eff"]["unit"] == "kPa" and given["sigma_vo_eff"]["symbol"] == "p'_{o,tip}"


def test_outputs_are_labelled_by_exact_key_only():
    # This docstring documents keys ('q_b [kPa]', ...) other than those the function returns;
    # none may borrow a label by position.
    exp = explain_calculation("API_unit_end_bearing_sand_rp2geo", API_SAND_ARGS, API_SAND_RESULTS)
    labels = {o["key"]: o["label"] for o in exp["outputs"]}
    assert labels["q_b_coring [kPa]"] is None
    assert labels["q_b_lim [kPa]"] == "Unit end bearing limit"
    units = {o["key"]: o["unit"] for o in exp["outputs"]}
    assert units["q_b_coring [kPa]"] == "kPa"


def test_positional_returns_are_paired_with_rtype_keys():
    exp = explain_calculation("API_unit_shaft_friction_sand_rp2geo", {}, {"f_s [kPa]": 30.0, "beta [-]": 0.37})
    out = {o["key"]: (o["label"], o["symbol"]) for o in exp["outputs"]}
    assert out["f_s [kPa]"] == ("Unit skin friction", "f_s")
    assert out["beta [-]"] == ("Coefficient beta", r"\beta")


def test_narration_prompt_walks_the_equation_and_skips_flags():
    exp = explain_calculation("API_unit_end_bearing_sand_rp2geo", API_SAND_ARGS, API_SAND_RESULTS)
    prompt = build_narration_prompt(exp)
    assert "Where: " in prompt and "= 53 kPa" in prompt
    assert "internal_friction" not in prompt.split("Outputs:")[1]


def test_eurocode7_factors_has_real_method_and_readable_nested_outputs():
    # A registry wrapper with no docstring: curated metadata, and its factor tables as one row each.
    exp = explain_calculation("eurocode7_factors", {"design_approach": "DA1-1", "foundation_type": "Spread foundation"},
                              {"actions": {"Permanent unfavourable": 1.35, "Variable unfavourable": 1.5},
                               "resistance": {"Bearing": 1.0}, "message": "Selected factors for DA1-1 - Spread foundation"})
    assert "Groundhog Deterministic" not in exp["method"]
    assert "EN 1997-1" in exp["standard"]
    rows = {o["key"]: o["value"] for o in exp["outputs"]}
    assert rows["actions › Permanent unfavourable"] == 1.35
    assert rows["resistance › Bearing"] == 1.0
    assert not any(isinstance(o["value"], dict) for o in exp["outputs"])
