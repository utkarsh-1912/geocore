"""GeoAI model benchmark: candidate registry and leaderboard aggregation (no model is loaded)."""
import json

from core.geoai.eval.benchmark import CANDIDATES, build_leaderboard, format_leaderboard
from core.geoai.finetune.config import FAMILY_PRESETS


def _report(path, label, key, score, ids, lora=None):
    rep = {"meta": {"label": label, "model_key": key, "lora_path": lora, "split": "test", "limit": 2,
                    "mode": "decision", "n_ctx": 4096, "max_tools": 5, "model_info": {"chat_format": "native"}},
           "metrics": {"n": len(ids), "mean_score": score, "strict_pass_rate": score / 2,
                       "per_category": {"missing_data": {"pass_rate": score}}},
           "per_example": {i: [score, score > 0.5] for i in ids}}
    path.write_text(json.dumps(rep), encoding="utf-8")


def test_candidates_are_consistent():
    for key, c in CANDIDATES.items():
        assert c.key == key
        assert c.filename.lower().endswith(".gguf") and "q4_k_m" in c.filename.lower()
        assert c.size_mb > 0 and "/" in c.repo_id
        assert c.finetune_family is None or c.finetune_family in FAMILY_PRESETS


def test_leaderboard_sorts_and_flags_fine_tunes(tmp_path):
    _report(tmp_path / "qwen3-1.7b.json", "qwen3-1.7b", "qwen3-1.7b", 0.6, ["a", "b"])
    _report(tmp_path / "qwen3-1.7b+geoai-lora.json", "qwen3-1.7b+geoai-lora", "qwen3-1.7b", 0.8, ["a", "b"],
            lora="x.gguf")
    _report(tmp_path / "heuristic.json", "heuristic", None, 0.3, ["a", "b"])
    lb = build_leaderboard(tmp_path)
    assert [r["label"] for r in lb["rows"]] == ["qwen3-1.7b+geoai-lora", "qwen3-1.7b", "heuristic"]
    assert lb["rows"][0]["fine_tuned"] and lb["rows"][0]["display_name"].endswith("+ GeoAI LoRA")
    assert lb["same_examples"] and lb["settings"]["max_tools"] == 5
    assert "qwen3-1.7b+geoai-lora" in format_leaderboard(lb)


def test_leaderboard_detects_different_example_sets(tmp_path):
    _report(tmp_path / "a.json", "a", None, 0.5, ["x"])
    _report(tmp_path / "b.json", "b", None, 0.5, ["y"])
    assert build_leaderboard(tmp_path)["same_examples"] is False
