---
title: Model benchmarks
slug: geoai/model-benchmarks
section: GeoAI
nav_order: 25
description: How GeoAI compares small local language models, before and after GeoAI fine-tuning, on the same engineering test suite.
sources:
- python-backend/core/geoai/eval/benchmark.py
- python-backend/core/geoai/eval/runner.py
- python-backend/core/geoai/eval/scoring.py
- python-backend/core/geoai/llama_cpp_provider.py
- python-backend/core/geoai/finetune/README.md
- python-backend/core/geoai/finetune/export.py
- AGENTS.md
---

GeoAI does not depend on one particular language model. Any GGUF model that llama.cpp can run can be used, as long as it can choose GeoCore tools and fill in their arguments. This page explains how candidate models are compared and publishes the measured results.

The model is chosen on how well it does GeoAI's job, not on general leaderboard reputation. In GeoAI the model does not do engineering arithmetic: groundhog and GeoCore's own routines calculate. The model has to understand the request, pick the right tool, extract the inputs with their units, ask when something is missing, and explain the tool result without adding numbers of its own.

## The test suite

Every model is scored on GeoAI's held-out evaluation set. The examples are generated deterministically from the tool registry and are never used for training. They cover:

| Category | What a good answer does |
|---|---|
| Correct request | Calls the right tool with the right arguments and units |
| Ambiguous request | Asks which calculation or method is meant |
| Missing data | Asks for the missing input instead of inventing a value |
| Wrong units | Notices the unit error (for example a unit weight given in kPa) |
| Conflicting data | Points out the conflict, for example between a CPT and a borehole log |
| Research | Searches the local document index rather than quoting from memory |
| Tool failure | Explains the error and does not invent a result |
| Final answer | Explains a real tool result without changing its numbers |

Each response is scored by a deterministic scorer, not by another language model. Numerical checks run the requested tool through groundhog and compare the result with the expected one.

| Metric | Meaning |
|---|---|
| Mean score | Weighted score per example, 0 to 1 |
| Strict pass | Share of examples where every check passed |
| Tool choice | Correct tool when a tool call was expected |
| Arguments | Share of expected arguments extracted with the right value and unit |
| Clarification | Asked for clarification or refused when it should have |
| Invented inputs | Tool calls containing a parameter the user never supplied |
| p50 latency | Median time to the model's first decision, in seconds |
| Peak RAM | Peak memory of the benchmark process, in MB |

## Candidate models

All candidates are 4-bit `Q4_K_M` GGUF files downloaded from Hugging Face. GeoAI reads each model's own chat template: models whose template understands tools use it directly (`native`). Gemma 3's template has no tool section, so the tools are described in the system prompt instead (`prompted`). Qwen3 and SmolLM3 can "think" at length before answering, and GeoAI switches that off with `/no_think` to keep CPU response times usable.

<!-- geocore:generated geoai-model-candidates -->

Model licences differ. Apache 2.0 and MIT models can be redistributed most freely. The Gemma and Llama licences add their own use terms. GeoCore does not bundle any model; you download the model you choose.

## Fine-tuning

A model is only fine-tuned after its base version has been measured, and the fine-tuned version is compared with the base model on the same examples (AGENTS.md §32):

1. **Base model:** the GGUF as published, with GeoAI's system prompt and tools.
2. **GeoAI LoRA:** a small LoRA adapter trained on GeoAI tool-use examples (supervised fine-tuning, then reinforcement learning with the same deterministic scorer as reward). It is trained on a GPU outside GeoCore and loaded on top of the unchanged base GGUF.

The adapter is kept only if it beats the base model: a mean score at least 0.02 higher, no worse strict pass rate, invented-input rate, caution violations or error rate, no category dropping by more than 5 percentage points, and median latency no more than 1.3 times the base. Otherwise GeoAI keeps the base model.

## Results

<!-- geocore:generated geoai-model-benchmarks -->

## About public benchmarks

Model publishers report scores on public benchmarks such as MMLU (general knowledge), GSM8K (arithmetic) and BFCL (function calling). These are useful background, but they are measured with different prompts, tools, hardware and often unquantised weights. They say little about GeoAI's work, where arithmetic is done by groundhog and the tools are GeoCore's own. For that reason, only results from the GeoAI suite above are used to choose GeoAI's model, and this page does not repeat publishers' scores.

## Reproducing the benchmark

From `python-backend/` with the GeoCore virtual environment:

```bash
python -m core.geoai.eval.benchmark list
python -m core.geoai.eval.benchmark download qwen3-1.7b phi-4-mini
python -m core.geoai.eval.benchmark run --models all-local --heuristic --split test --limit 40 --run-id my-run
python -m core.geoai.eval.benchmark run --models qwen3-1.7b --lora qwen3-1.7b=path/to/geoai-lora.gguf --run-id my-run
```

Results are written to `core/geoai/eval/results/benchmark/<run-id>/`, one JSON file per model plus `leaderboard.json`. The website rebuild publishes the most recent leaderboard.
