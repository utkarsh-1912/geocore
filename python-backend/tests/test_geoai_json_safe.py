"""
Tool results must be JSON-encodable: the agent encodes them for the model and the SSE stream.

Regression: mohrcoulomb_triaxial_compression returns a Plotly figure and a DataFrame, which failed with
"Object of type DataFrame is not JSON serializable". The fix changes only what JSON could not encode: a figure
becomes {"image_id", "details"}; everything JSON could already encode passes through unchanged.
"""
import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from core.geoai.tool_registry import _json_safe, tool_registry

MOHR = {"sigma_3": 20, "cohesion": 10, "phi": 35}


def test_mohr_coulomb_triaxial_result_is_json_serialisable():
    result = tool_registry.invoke_tool("mohrcoulomb_triaxial_compression", MOHR)
    json.dumps(result)  # must not raise
    assert abs(result["sigma_1_f [kPa]"] - 112.73) < 0.01  # the deterministic Groundhog value is unchanged
    image = result["Plot"]
    assert set(image) == {"image_id", "details"} and "Mohr circle" in image["details"]
    assert "data" not in image  # the model gets the description, never the plotted data
    assert result["Mohr circle"] == {"columns": ["tau [kPa]", "sigma [kPa]"], "n_rows": 250}  # long table: summary
    assert "_display" not in result


def test_values_json_could_already_encode_are_unchanged():
    original = {
        "text": "kPa", "int": 3, "float": 1.5, "nan": float("nan"), "none": None, "flag": True,
        "list": [1, 2.5, "x", None], "tuple": (1, 2), "nested": {"a": [{"b": 1}], "c": {"d": "e"}},
        "table": [{"depth_m": 1.0, "qc": 5.0}, {"depth_m": 2.0, "qc": 6.0}],
    }
    assert json.dumps(_json_safe(original)) == json.dumps(original)


def test_objects_json_could_not_encode_are_converted():
    out = _json_safe({
        "i": np.int64(3), "f": np.float64(1.5), "nan": np.float64("nan"), "flag": np.bool_(True),
        "arr": np.array([1.0, 2.0]), "series": pd.Series([1, 2]), "nested": {"x": [np.float32(0.5)]},
        "small": pd.DataFrame({"a": [1, 2]}), "long": pd.DataFrame({"a": range(60)}),
    })
    json.dumps(out)
    assert out["i"] == 3 and type(out["i"]) is int and type(out["f"]) is float and out["flag"] is True
    assert out["nan"] != out["nan"]  # NaN keeps its value (callers format it)
    assert out["arr"] == [1.0, 2.0] and out["series"] == [1, 2]
    assert out["small"] == [{"a": 1}, {"a": 2}]  # a short table goes to the model whole
    assert out["long"] == {"columns": ["a"], "n_rows": 60}  # a long one only as a summary


def test_figures_become_an_image_id_with_details():
    fig = go.Figure(go.Scatter(x=[0, 1], y=[0, 1], name="curve"))
    fig.update_layout(title="Mohr circle", xaxis_title="$ \\sigma \\ \\text{[kPa]}$", yaxis_title="tau [kPa]")
    out = _json_safe({"Plot": fig, "n": 2})
    assert out["n"] == 2
    assert out["Plot"]["image_id"] == "Plot"  # the agent swaps in a turn-unique id
    assert out["Plot"]["details"] == "Chart 'Mohr circle' (tau [kPa] against σ [kPa]) with series: curve"
    json.dumps(out)
