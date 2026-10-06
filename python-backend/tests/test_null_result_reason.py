"""
A Groundhog calculation that returns only nulls explains why, using the function's own error.

Groundhog's @Validator swallows an error raised inside a function and returns NaN, so the app used to
say only "inputs do not satisfy the boundary equations". cycliccontours_triaxialclay_andersen normalises
by Su: tau_a/Su and tau_cy/Su must lie inside the chart (<= 1), which the form's per-field ranges
(1-100, -50-100, 0-100) cannot express.
"""
from core.registry import registry


def _run(**args):
    return registry.execute_function("groundhog.soildynamics.cyclicbehaviour", "cycliccontours_triaxialclay_andersen", args)


def test_out_of_chart_ratios_report_the_real_reason():
    result = _run(undrained_shear_strength=4, average_shear_stress=8, cyclic_shear_stress=9)
    assert result["status"] == "Error"
    assert "Normalised average shear stress should be between -0.5 and 1" in result["error"]
    assert "cycliccontours_triaxialclay_andersen" in result["error"]


def test_inputs_inside_the_chart_still_calculate():
    result = _run(undrained_shear_strength=40, average_shear_stress=8, cyclic_shear_stress=9)
    assert "error" not in result and result["Nf [-]"] > 10


def test_generic_message_remains_when_no_reason_can_be_recovered():
    message = registry._null_result_message("some_function", lambda **kw: {"x": None}, {})
    assert "returned no output" in message and "some_function" in message
