# Author: Utkarsh Gupta
# License: GPL v3
"""
Smoke tests for the GeoAI evaluation runner with the heuristic provider
(real GeoAIAgent + Tool Registry path, no llama.cpp required).
"""
import json

import pytest

from core.geoai.eval.example import save_examples_jsonl
from core.geoai.eval.runner import (
    EvalRegistry,
    RecordingProvider,
    build_report,
    compare_results,
    main,
    make_provider,
    peak_memory_mb,
    run_eval,
)
from core.geoai.eval.scoring import default_registry
from core.geoai.exceptions import GeoAIValidationError
from core.geoai.training.scaleup import build_dataset, gold_examples


@pytest.fixture(scope="module")
def small_set():
    examples, _, _ = build_dataset(seed=5, per_tool=4)
    picked, seen = [], set()
    for e in examples:  # one decision + one final-answer example per category
        key = (e.category, e.turn_type)
        if key not in seen:
            seen.add(key)
            picked.append(e)
    return picked + gold_examples()[:3]


def test_run_eval_heuristic_smoke(small_set):
    run = run_eval(small_set, make_provider("heuristic"))
    m = run["metrics"]
    assert m["n"] == len(small_set) == len(run["records"])
    for key in ("tool_selection_accuracy", "argument_accuracy", "clarification_accuracy",
                "hallucinated_parameter_rate", "latency_p50_s", "latency_p95_s", "per_category"):
        assert key in m
    assert 0.0 <= m["mean_score"] <= 1.0
    assert m["error_rate"] == 0.0
    # the gold Gmax example is solved by the heuristic router
    rec = next(r for r in run["records"] if r["id"] == "gold-correct_01_gmax")
    assert rec["score"]["tool"] == 1.0
    report = build_report(run, {"provider": "heuristic"})
    json.dumps(report)  # serialisable
    cmp = compare_results(report, report)
    assert cmp["fixed"] == cmp["regressed"] == 0
    assert all(v["delta"] in (0, 0.0, None) for v in cmp["metrics"].values())


def test_cli_writes_results_and_compares(tmp_path, small_set):
    data = tmp_path / "mini.jsonl"
    save_examples_jsonl(small_set[:6], data)
    out = tmp_path / "res.json"
    assert main(["--provider", "heuristic", "--dataset", str(data), "--mode", "decision", "--out", str(out), "--quiet"]) == 0
    res = json.loads(out.read_text(encoding="utf-8"))
    assert res["metrics"]["n"] == 6 and len(res["per_example"]) == 6
    cmp_out = tmp_path / "cmp.json"
    assert main(["--compare", str(out), str(out), "--out", str(cmp_out)]) == 0
    assert json.loads(cmp_out.read_text(encoding="utf-8"))["n_shared"] == 6


def test_eval_registry_blocks_side_effect_tools():
    reg = EvalRegistry(default_registry())
    assert reg.get_tool("index_document_text") is not None
    with pytest.raises(GeoAIValidationError):
        reg.invoke_tool("index_document_text", {"doc_id": "x", "title": "t", "content": "c"})


def test_recording_provider_and_memory_probe():
    rec = RecordingProvider(make_provider("heuristic"))
    from core.geoai.model_provider import make_user_message
    rec.generate([make_user_message("Calculate Gmax with Vs = 250 m/s and gamma = 19 kN/m3")])
    assert len(rec.calls) == 1 and rec.calls[0].latency_s >= 0
    mem = peak_memory_mb()
    assert mem is None or mem > 0
