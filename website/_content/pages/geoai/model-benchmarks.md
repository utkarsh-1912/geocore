---
title: Model benchmarks
slug: geoai/model-benchmarks
section: GeoAI
description: How GeoAI compares small local language models, before and after GeoAI fine-tuning, on the same engineering test suite.
origin: geocore
source_url: https://github.com/utkarsh-1912/geocore/blob/main/website/_content/geocore/geoai-model-benchmarks.md
license: GPL-3.0
author: Utkarsh Gupta
attribution: GeoCore documentation by Utkarsh Gupta, licensed under the GNU GPL v3.
groundhog_version: 0.15.0
edited_by_geocore: false
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

| Model | Parameters | Download | Licence | Tool calls | Notes |
|---|---|---|---|---|---|
| [Qwen2.5 1.5B Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) | 1.5B | ~1.0 GB | Apache-2.0 | native &lt;tool_call&gt; | Current GeoAI default and fine-tuning baseline. |
| [Qwen2.5 3B Instruct](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF) | 3B | ~2.0 GB | Qwen Research (non-commercial) | native &lt;tool_call&gt; | Balanced speed/precision; non-commercial licence. |
| [Qwen2.5 7B Instruct](https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF) | 7B | ~4.4 GB | Apache-2.0 | native &lt;tool_call&gt; | Quality ceiling reference for the Qwen2.5 line. |
| [Qwen3 1.7B](https://huggingface.co/unsloth/Qwen3-1.7B-GGUF) | 1.7B | ~1.0 GB | Apache-2.0 | native &lt;tool_call&gt; | Hybrid thinking model; GeoAI sends /no_think. |
| [Qwen3.5 2B](https://huggingface.co/unsloth/Qwen3.5-2B-GGUF) | 2B | ~1.2 GB | Apache-2.0 | native &lt;tool_call&gt; | Newest small Qwen; fine-tune preset uses 16-bit LoRA. |
| [Qwen3 4B Instruct 2507](https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF) | 4B | ~2.3 GB | Apache-2.0 | native &lt;tool_call&gt; | Non-thinking instruct release. |
| [Qwen3 8B](https://huggingface.co/Qwen/Qwen3-8B-GGUF) | 8B | ~4.7 GB | Apache-2.0 | native &lt;tool_call&gt; | Quality ceiling reference; too heavy to be the default. |
| [Phi-4-mini Instruct](https://huggingface.co/unsloth/Phi-4-mini-instruct-GGUF) | 3.8B | ~2.3 GB | MIT | &lt;\|tool_call\|&gt; JSON list | Trained for function calling. |
| [SmolLM3 3B](https://huggingface.co/ggml-org/SmolLM3-3B-GGUF) | 3B | ~1.8 GB | Apache-2.0 | native &lt;tool_call&gt; | Hybrid thinking model; GeoAI sends /no_think. |
| [Granite 4.1 (3B)](https://huggingface.co/ibm-granite/granite-4.1-3b-GGUF) | 3B | ~2.0 GB | Apache-2.0 | native &lt;tool_call&gt; | IBM enterprise model; 4.1 post-training upgrade over 4.0 Micro with enhanced tool calling. |
| [Llama 3.2 3B Instruct](https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF) | 3B | ~1.9 GB | Llama 3.2 Community | bare JSON (name, parameters) | Custom licence with use restrictions. |
| [Mistral 7B Instruct v0.3](https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF) | 7B | ~4.1 GB | Apache-2.0 | [TOOL_CALLS] JSON list | Strong literature/standards synthesis. |

Model licences differ. Apache 2.0 and MIT models can be redistributed most freely. The Gemma and Llama licences add their own use terms. GeoCore does not bundle any model; you download the model you choose.

## Fine-tuning

A model is only fine-tuned after its base version has been measured, and the fine-tuned version is compared with the base model on the same examples (AGENTS.md §32):

1. **Base model:** the GGUF as published, with GeoAI's system prompt and tools.
2. **GeoAI LoRA:** a small LoRA adapter trained on GeoAI tool-use examples (supervised fine-tuning, then reinforcement learning with the same deterministic scorer as reward). It is trained on a GPU outside GeoCore and loaded on top of the unchanged base GGUF.

The adapter is kept only if it beats the base model: a mean score at least 0.02 higher, no worse strict pass rate, invented-input rate, caution violations or error rate, no category dropping by more than 5 percentage points, and median latency no more than 1.3 times the base. Otherwise GeoAI keeps the base model.

## Results

Run `cpu-test40-full-20260929`: 40 examples from the `test` split (stratified subset of 40), decision mode, `n_ctx` 4096, 5 tools offered per request, CPU only, dataset generator 1.0.0. All models answered the same examples.

| Model | Mean score | Strict pass | Tool choice | Arguments | Clarification | Invented inputs | p50 latency (s) | Peak RAM (MB) |
|---|---|---|---|---|---|---|---|---|
| Qwen3 1.7B | 0.669 | 45% | 73% | 71% | 14% | 41% | 69.8 | 2185 |

<div class="bar-chart" aria-hidden="true">
  <p class="bar-chart__title">Mean score by model</p>
  <div class="bar-chart__row">
    <span class="bar-chart__label">Qwen3 1.7B</span>
    <svg class="bar-chart__track" viewBox="0 0 100 10" preserveAspectRatio="none" role="presentation">
      <rect class="bar-chart__track-bg" width="100" height="10" rx="5"></rect>
      <rect class="bar-chart__fill" width="100.0" height="10" rx="5"></rect>
    </svg>
    <span class="bar-chart__value">0.669</span>
  </div>
</div>

Strict pass rate by category:

| Model | ambiguous request | conflicting data | correct request | missing data | research | tool failure | wrong units |
|---|---|---|---|---|---|---|---|
| Qwen3 1.7B | 25% | 25% | 62% | 0% | 88% | 17% | 50% |

No GeoAI fine-tuned adapter is included in this run yet; all rows are base models.

Small subsets give noisy rates: with 40 examples one example is 2.5 percentage points. Latency and memory depend on the machine the run used.

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
