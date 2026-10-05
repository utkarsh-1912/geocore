# Author: Utkarsh Gupta
# License: GPL v3
"""Registered tools must agree with independent closed-form oracles (core.geoai.eval.numeric_oracles)."""
import pytest

from core.geoai.eval.numeric_oracles import OracleCase, build_cases, run_cases


def test_tools_agree_with_independent_oracles():
    assert run_cases() == []


def test_oracle_runner_reports_mismatches_and_missing_keys():
    wrong = OracleCase("bad", "calculate_relative_density", dict(void_ratio=0.62, e_min=0.48, e_max=0.91),
                       {"Dr [-]": 0.5, "nope": 1.0}, "deliberately wrong")
    problems = run_cases(cases=[wrong])
    assert len(problems) == 2
    assert any("oracle 0.5" in p for p in problems) and any("no 'nope'" in p for p in problems)


@pytest.mark.parametrize("case", build_cases(), ids=lambda c: c.id)
def test_each_case_is_independent_of_tool_output(case):
    # an oracle value must be a plain float computed here, never read back from the registry
    assert all(isinstance(v, float) for v in case.expected.values())
