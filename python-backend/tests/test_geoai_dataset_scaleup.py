# Author: Utkarsh Gupta
# License: GPL v3
"""
Tests for the registry-validated GeoAI dataset generator (core/geoai/training/scaleup.py):
determinism, validity by construction, category coverage, split leakage and SFT export format.
"""
import json
import math
import re

import pytest

from core.geoai.eval import score_turn
from core.geoai.eval.example import CATEGORIES, load_examples_jsonl
from core.geoai.eval.scoring import default_registry, effective_arguments, values_match
from core.geoai.training.scaleup import build_dataset, export_dataset, gold_examples

PER_TOOL = 8  # small but covers every builder


@pytest.fixture(scope="module")
def dataset():
    examples, drafts, report = build_dataset(seed=123, per_tool=PER_TOOL)
    return examples, drafts, report


def _norm(p):
    return re.sub(r"\s+", " ", p.strip().lower())


def test_generation_is_deterministic(dataset):
    examples, _, _ = dataset
    again, _, _ = build_dataset(seed=123, per_tool=PER_TOOL)
    assert [e.to_dict() for e in examples] == [e.to_dict() for e in again]
    other, _, _ = build_dataset(seed=124, per_tool=PER_TOOL)
    assert [e.id for e in other] != [e.id for e in examples]


def test_all_categories_present_in_every_split(dataset):
    examples, _, report = dataset
    assert {e.category for e in examples} == set(CATEGORIES)
    for split in ("train", "test"):
        cats = {e.category for e in examples if e.split == split}
        assert cats == set(CATEGORIES), f"{split} missing {set(CATEGORIES) - cats}"
    assert {e.turn_type for e in examples} == {"decision", "final_answer"}
    assert report.total == len(examples)


def test_ids_unique_and_no_duplicate_prompts(dataset):
    examples, _, _ = dataset
    assert len({e.id for e in examples}) == len(examples)
    keys = [(e.turn_type, _norm(e.user_prompt), json.dumps(e.context, sort_keys=True)) for e in examples]
    assert len(set(keys)) == len(keys)


def test_no_split_leakage(dataset):
    examples, _, _ = dataset
    groups, prompts = {}, {}
    for e in examples:
        assert groups.setdefault(e.group, e.split) == e.split, f"group {e.group} spans splits"
        key = (_norm(e.user_prompt), json.dumps(e.context, sort_keys=True))
        assert prompts.setdefault(key, e.split) == e.split, f"prompt leaks across splits: {e.user_prompt[:80]}"


def test_every_expected_tool_call_executes_through_registry(dataset):
    examples, drafts, _ = dataset
    reg = default_registry()
    checked = 0
    for d in drafts:
        if d.target_call is None or d.example.category == "tool_failure":
            continue
        ex = d.example
        tool = reg.get_tool(ex.expected_tool)
        eff, err = effective_arguments(tool.input_model, d.target_call["arguments"])
        assert err is None, (ex.id, err)
        for p, v in ex.expected_arguments.items():
            assert values_match(v, eff[p], rel_tol=1e-6), (ex.id, p, v, eff[p])
        if ex.expected_tool == "search_local_documents":
            continue  # reads the user's local index; validity of the call is what matters
        res = reg.invoke_tool(ex.expected_tool, dict(d.target_call["arguments"]))
        for k, v in ex.expected_result.items():
            assert math.isfinite(v) and values_match(v, res[k], rel_tol=1e-9), (ex.id, k)
        checked += 1
    assert checked > 100


def test_clarify_examples_are_refused_by_registry(dataset):
    examples, _, _ = dataset
    reg = default_registry()
    missing = [e for e in examples if e.category == "missing_data"]
    assert missing
    for e in missing:
        assert e.expected_action == "clarify" and e.missing_params
        assert e.missing_params[0] not in e.provided_params
        assert reg.get_tool(e.expected_tool).input_model.model_fields[e.missing_params[0]].is_required()


def test_reference_behaviour_passes_scorer(dataset):
    """Generator and scorer must agree: every target behaviour scores a strict pass."""
    examples, drafts, _ = dataset
    by_id = {d.example.id: d for d in drafts}
    failures = []
    for e in examples:
        if e.turn_type == "decision" and by_id[e.id].target_call:
            resp = {"content": "", "tool_calls": [{"function": by_id[e.id].target_call}]}
        else:
            resp = {"content": e.reference_response}
        sb = score_turn(e, resp)
        if not sb.passed:
            failures.append((e.id, sb.reasons))
    assert not failures, failures[:5]


def test_gold_set_preserved_and_valid():
    from core.geoai.training.dataset_generator import build_core_training_examples
    gold = gold_examples()
    assert len(gold) == len(build_core_training_examples()) and all(g.split == "gold" for g in gold)
    reg = default_registry()
    for g in gold:
        if g.expected_action == "tool_call":
            eff, err = effective_arguments(reg.get_tool(g.expected_tool).input_model, g.expected_arguments)
            assert err is None, (g.id, err)


def test_export_holds_out_test_split(tmp_path):
    manifest = export_dataset(tmp_path, seed=7, per_tool=4)
    test_ids = {e.id for e in load_examples_jsonl(tmp_path / "eval_test.jsonl")}
    assert test_ids
    assert not (tmp_path / "sft_test.jsonl").exists()
    sft_ids = set()
    for split in ("train", "val"):
        with open(tmp_path / f"sft_{split}.jsonl", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                sft_ids.add(rec["id"])
                assert rec["split"] == split
                roles = [m["role"] for m in rec["messages"]]
                assert roles[0] == "system" and roles[1] == "user" and roles[-1] == "assistant"
                assert isinstance(rec["tools"], list) and rec["tools"]
                for m in rec["messages"]:
                    for tc in m.get("tool_calls") or []:
                        assert isinstance(tc["function"]["arguments"], dict)
                        names = [t["function"]["name"] for t in rec["tools"]]
                        assert tc["function"]["name"] in names
                if "tool" in roles:
                    assert roles[-3:] == ["assistant", "tool", "assistant"]
    assert not (sft_ids & test_ids)
    assert manifest["files"]["eval_gold.jsonl"] == len(gold_examples())
