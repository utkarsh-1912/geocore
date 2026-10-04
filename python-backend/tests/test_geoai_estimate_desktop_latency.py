# Author: Utkarsh Gupta
# License: GPL v3
"""Desktop-latency estimate from benchmark token counts (synthetic result files, no model is loaded)."""
import json

import pytest

from core.geoai.eval.benchmark import build_leaderboard
from core.geoai.eval.estimate_desktop_latency import (
    DEFAULT_CALIBRATION,
    OUTPUT_FILE,
    estimate_report,
    estimate_run,
    format_estimate,
    load_calibration,
    main,
    rates_for,
)

CAL = {
    "reference_model": "qwen3-1.7b",
    "machine": {"cpu": "test cpu"},
    "date": "2026-10-04",
    "models": {"qwen3-1.7b": {"size_mb": 1000, "prompt_tok_s": 20.0, "prompt_tok_s_range": [10.0, 40.0],
                              "gen_tok_s": 5.0, "gen_tok_s_range": [4.0, 10.0], "model_load_s": 4.0}},
}


def _report(label, key, usage, provider="llama_cpp", lora=None, records=None):
    return {"meta": {"label": label, "model_key": key, "provider": provider, "lora_path": lora,
                     "platform": "linux", "n_gpu_layers": -1},
            "metrics": {"n": len(usage), "decision_latency_p50_s": 1.0},
            "per_example": {i: [1.0, True] for i in usage},
            "per_example_usage": usage, "records": records or []}


def _u(p, c, lat=None):
    return {"prompt_tokens": p, "completion_tokens": c, "model_calls": 1, "decision_latency_s": lat, "latency_s": lat}


def test_shipped_calibration_is_valid():
    cal = load_calibration(DEFAULT_CALIBRATION)
    ref = cal["models"][cal["reference_model"]]
    assert 17 <= ref["prompt_tok_s"] <= 31 and 4 <= ref["gen_tok_s"] <= 6
    assert cal["date"] and cal["machine"]["cpu"]


def test_estimate_uses_token_formula():
    # 200/20 + 50/5 = 20 s; 400/20 + 100/5 = 40 s; 600/20 + 150/5 = 60 s
    usage = {"a": _u(200, 50), "b": _u(400, 100), "c": _u(600, 150)}
    est = estimate_report(_report("qwen3-1.7b", "qwen3-1.7b", usage), CAL)
    assert est["estimate"] is True and est["rate_method"] == "calibrated"
    assert est["n_with_tokens"] == 3 and est["token_source"] == "per_example_usage"
    assert est["est_desktop_p50_s"] == pytest.approx(40.0)
    assert est["est_desktop_p95_s"] == pytest.approx(58.0)  # linear interpolation between 40 and 60
    assert est["est_desktop_cold_p50_s"] == pytest.approx(44.0)  # + model load
    fast, slow = est["est_desktop_p50_range_s"]  # 400/40+100/10 = 20; 400/10+100/4 = 65
    assert fast == pytest.approx(20.0) and slow == pytest.approx(65.0)


def test_uncalibrated_model_is_scaled_by_size():
    r = rates_for(CAL, "other", size_mb=2000)
    assert r["prompt_tok_s"] == pytest.approx(10.0) and r["gen_tok_s"] == pytest.approx(2.5)
    assert r["model_load_s"] == pytest.approx(8.0) and "scaled" in r["method"]
    assert rates_for(CAL, "unknown-model-without-size") is None


def test_skips_heuristic_and_missing_tokens_and_flags_lora():
    assert "skipped" in estimate_report(_report("heuristic", None, {"a": _u(None, None)}, provider="heuristic"), CAL)
    assert "skipped" in estimate_report(_report("qwen3-1.7b", "qwen3-1.7b", {"a": _u(None, None)}), CAL)
    est = estimate_report(_report("qwen3-1.7b+geoai-lora", "qwen3-1.7b", {"a": _u(100, 10)}, lora="x.gguf"), CAL)
    assert "LoRA" in est["note"]


def test_older_result_files_fall_back_to_records():
    rep = _report("qwen3-1.7b", "qwen3-1.7b", {})
    rep["per_example_usage"] = None
    rep["metrics"]["n"] = 40
    rep["records"] = [{"id": "x", "usage": {"prompt_tokens": 200, "completion_tokens": 50}, "n_model_calls": 1,
                       "decision_latency_s": 10.0}]
    est = estimate_report(rep, CAL, validate=True)
    assert est["n_with_tokens"] == 1 and est["n_examples"] == 40 and "records" in est["token_source"]
    assert est["validation"]["measured_over_estimate_p50"] == pytest.approx(0.5)  # 10 s measured / 20 s estimated


def test_run_folder_cli_writes_estimate_and_leaderboard_ignores_it(tmp_path):
    (tmp_path / "qwen3-1.7b.json").write_text(json.dumps(_report("qwen3-1.7b", "qwen3-1.7b", {"a": _u(200, 50)})))
    (tmp_path / "heuristic.json").write_text(json.dumps(_report("heuristic", None, {"a": _u(None, None)},
                                                                provider="heuristic")))
    cal_file = tmp_path / "cal.json"
    cal_file.write_text(json.dumps(CAL))
    assert main(["--run-dir", str(tmp_path), "--calibration", str(cal_file)]) == 0
    out = json.loads((tmp_path / OUTPUT_FILE).read_text(encoding="utf-8"))
    assert out["estimate"] is True and [r["label"] for r in out["rows"]] == ["qwen3-1.7b", "heuristic"]
    assert out["rows"][0]["est_desktop_p50_s"] == pytest.approx(20.0)
    assert "ESTIMATED" in format_estimate(estimate_run(tmp_path, CAL))
    # the estimate file in the run folder must not become a leaderboard row
    assert sorted(r["label"] for r in build_leaderboard(tmp_path)["rows"]) == ["heuristic", "qwen3-1.7b"]
