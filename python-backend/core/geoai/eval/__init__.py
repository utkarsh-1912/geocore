"""
GeoAI evaluation package: deterministic scorer, example schema and runner.

Public API (stable, used as the RL reward):
    score_turn(example, model_response, *, registry=None, execute=False) -> ScoreBreakdown
    reward(example, completion) -> float
    parse_completion(text) -> ParsedResponse
    EvalExample
"""
from core.geoai.eval.example import EvalExample, load_examples_jsonl, save_examples_jsonl
from core.geoai.eval.scoring import (
    CRITERION_WEIGHTS,
    ParsedResponse,
    ScoreBreakdown,
    parse_completion,
    reward,
    score_turn,
)

__all__ = [
    "EvalExample",
    "load_examples_jsonl",
    "save_examples_jsonl",
    "CRITERION_WEIGHTS",
    "ParsedResponse",
    "ScoreBreakdown",
    "parse_completion",
    "reward",
    "score_turn",
]
