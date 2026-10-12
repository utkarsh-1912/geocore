# Author: Utkarsh Gupta
# License: GPL v3
"""
Worked solutions written by the local model and grounded in the calculation's guide details (core/geoai/solution.py,
POST /api/geoai/explain/solution). The model is replaced by a scripted provider: these tests check the grounding
it receives and the checks applied to what it writes, never the model itself (AGENTS.md §25).
"""
import json

import pytest
from fastapi.testclient import TestClient

from core.geoai.model_provider import StreamChunk
from core.geoai.solution import (SOLUTION_SYSTEM_PROMPT, build_grounding, equation_mismatch, stream_solution,
                                 substituted_formula, unverified_numbers, _default_symbols)

GMAX = ("gmax_shearwavevelocity", {"Vs": 260, "gamma": 19}, {"Gmax [kPa]": 130927.6249, "rho [kg/m3]": 1936.7992})


class ScriptedProvider:
    """Streams a fixed answer; records the messages it was given."""

    def __init__(self, answer):
        self.answer = answer
        self.messages = None

    def model_info(self):
        return {"provider": "scripted"}

    def generate_answer_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        self.messages = messages
        for word in self.answer.split(" "):
            yield StreamChunk(delta_content=word + " ")
        yield StreamChunk(finish_reason="stop")


def test_grounding_has_theory_equation_symbols_defaults_and_exact_results():
    text, explanation = build_grounding(*GMAX, applicability="Small strains only.")
    assert "THEORY:" in text and "shear wave velocity" in text.lower()
    assert "GOVERNING EQUATION (LaTeX): G_{max} = \\rho \\cdot V_s^2" in text
    assert "$V_s$ = 260 m/s" in text and "$\\gamma$ = 19 kN/m3" in text
    assert "DEFAULTS USED" in text and "= 9.81 m/s2" in text            # g, not entered by the user
    assert "130927.6249 kPa" in text and "1936.7992 kg/m3" in text      # results at full precision
    assert "- Small strains only." in text
    assert explanation["formula"]


def test_numbers_not_in_the_grounding_are_flagged():
    grounding, _ = build_grounding(*GMAX)
    answer = ("Gmax = 130,927.6249 kPa from rho = 1936.8 kg/m3, Vs = 260 m/s and g = 9.81 m/s2, "
              "about 131 MPa; that is 1.94 t/m3. Step 3.")
    assert unverified_numbers(answer, grounding) == ["131", "1.94"]


def test_equation_check_accepts_rewritten_forms_and_flags_a_different_equation():
    _, explanation = build_grounding(*GMAX)
    formula = explanation["formula"]
    assert not equation_mismatch("$$ G_{max} = \\rho \\cdot V_s^{2} $$ and $$\\rho = \\frac{\\gamma}{g}$$", formula)
    assert not equation_mismatch("$$G_{max} = \\rho \\times V_s^2 \\\\ \\rho = \\gamma / g$$", formula)
    assert equation_mismatch("$$G_{max} = \\frac{\\rho V_s^2}{g}$$ $$\\rho = \\gamma / g$$", formula)
    assert equation_mismatch("No equation written.", formula)


def test_equation_check_accepts_mathematically_equal_forms():
    """GeoAI substituting rho = gamma/g into G = rho Vs^2 is the same equation, not a different one."""
    _, explanation = build_grounding(*GMAX)
    formula = explanation["formula"]
    # The answer that raised the false alarm: rho folded in, then the numbers substituted on the same quantity.
    answer = (r"### Governing equation" "\n" r"$$G_{max} = \frac{\gamma}{g} V_s^2$$" "\n"
              r"### Substitution" "\n" r"$$G_{max} = \frac{19}{9.81} \times 260^2$$")
    assert not equation_mismatch(answer, formula)
    assert not equation_mismatch(r"$$G_{max} = V_s^{2} \cdot \gamma / g$$", formula)  # reordered
    assert not equation_mismatch(r"$$G_{max} = \left(\frac{\gamma}{g}\right) \cdot V_s^2$$", formula)
    # Still flagged: the right quantities in a wrong equation, with or without rho folded in.
    assert equation_mismatch(r"$$G_{max} = \frac{\gamma}{g} V_s$$", formula)
    assert equation_mismatch(r"$$G_{max} = \gamma \cdot g \cdot V_s^2$$", formula)
    assert equation_mismatch(r"$$G_{max} = \rho V_s^2$$ $$\rho = \gamma \cdot g$$", formula)


def test_equation_parser_subset():
    from core.geoai.equation_check import ParseError, parse, same_expression
    assert same_expression(parse(r"\frac{a}{b} c"), parse(r"a c / b"))
    assert same_expression(parse(r"\sqrt{x^2}"), parse(r"x"))
    assert same_expression(parse(r"K_{a} \cdot \sigma'_{v}"), parse(r"\sigma'_v K_a"))
    assert not same_expression(parse(r"x^2"), parse(r"2 x"))
    with pytest.raises(ParseError):
        parse(r"\int_0^1 x dx")  # outside the subset: the caller falls back to the text comparison


def test_substitution_replaces_inputs_and_defaults_only():
    _, explanation = build_grounding(*GMAX)
    sub = substituted_formula(explanation, _default_symbols("gmax_shearwavevelocity", {"Vs": 260, "gamma": 19}))
    assert sub == "G_{max} = \\rho \\cdot \\left(260\\right)^2 \\\\ \\rho = \\left(19\\right) / \\left(9.81\\right)"
    _, rd = build_grounding("relative_density", {"void_ratio": 0.6, "e_min": 0.9, "e_max": 0.4}, {"Dr [-]": 0.6})
    # "e" is replaced, "e_{min}" / "e_{max}" keep their own values (no clobbering of the subscripted symbols).
    assert substituted_formula(rd, {}) == ("D_r = \\frac{\\left(0.6\\right) - \\left(0.9\\right)}"
                                           "{\\left(0.4\\right) - \\left(0.9\\right)}")


def test_stream_gives_the_model_the_grounding_and_checks_its_answer():
    provider = ScriptedProvider("### Governing equation $$G_{max} = \\frac{\\rho V_s^2}{g}$$ "
                                "### Result Gmax = 130927.6249 kPa, roughly 131 MPa.")
    events = list(stream_solution(provider, *GMAX))
    assert provider.messages[0].content == SOLUTION_SYSTEM_PROMPT
    assert provider.messages[1].content.startswith("CALCULATION DETAILS:") and "130927.6249 kPa" in provider.messages[1].content
    text = "".join(e["content"] for e in events if e["type"] == "token")
    assert "130927.6249" in text
    check = events[-1]
    assert check["type"] == "check" and check["unverified"] == ["131"]
    assert check["equation_mismatch"] is True and check["equation"].startswith("G_{max} = \\rho")
    assert "\\left(260\\right)" in check["substitution"]


def _events(response):
    return [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]


def test_endpoint_without_a_model_says_so(monkeypatch):
    import core.geoai.api as api
    from core.geoai.heuristic_provider import HeuristicProvider
    from main import app
    monkeypatch.setattr(api.lifecycle_manager, "get_provider", lambda: HeuristicProvider())
    events = _events(TestClient(app).post("/api/geoai/explain/solution", json={
        "function_id": "calculate_gmax_from_shear_wave_velocity", "args": {"Vs": 260, "gamma": 19},
        "results": {"Gmax": 130927.6249, "rho": 1936.7992}}))
    assert [e["type"] for e in events] == ["unavailable", "done"]


def test_endpoint_streams_a_tool_result_solution(monkeypatch):
    import core.geoai.api as api
    from main import app
    provider = ScriptedProvider("### Governing equation $$G_{max} = \\rho \\cdot V_s^2$$ $$\\rho = \\gamma / g$$ "
                                "### Result Gmax = 130927.6249 kPa.")
    monkeypatch.setattr(api.lifecycle_manager, "get_provider", lambda: provider)
    monkeypatch.setattr(api.lifecycle_manager, "touch", lambda: None)
    events = _events(TestClient(app).post("/api/geoai/explain/solution", json={
        "function_id": "calculate_gmax_from_shear_wave_velocity", "args": {"Vs": 260, "gamma": 19},
        "results": {"Gmax": 130927.6249, "rho": 1936.7992}}))
    types = [e["type"] for e in events]
    assert types[0] == "stage" and "token" in types and types[-2:] == ["check", "done"]
    check = events[-2]
    assert check["unverified"] == [] and check["equation_mismatch"] is False
    # The GeoAI tool's outputs reached the model with Groundhog's units.
    assert "130927.6249 kPa" in provider.messages[1].content
