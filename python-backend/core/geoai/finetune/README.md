# GeoAI fine-tuning (LoRA SFT -> GRPO -> GGUF LoRA)

Training runs **off-machine** on a CUDA GPU (free Colab/Kaggle T4 is enough for 1.5B-4B models).
The desktop app never imports torch/unsloth/trl/peft: it only loads a GGUF LoRA adapter on top of its
base GGUF through llama.cpp, and falls back to the base model if the adapter is missing,
incompatible or not better (AGENTS.md §19, §32).

```
sft_train/sft_val.jsonl ──SFT (LoRA, assistant-only loss)──► sft_adapter/
eval_train.jsonl prompts ──GRPO (reward = eval.scoring.reward)──► grpo_adapter/
adapter ──llama.cpp convert_lora_to_gguf.py──► geoai-lora.gguf + geoai-lora.gguf.json (sidecar)
desktop: GEOAI_LORA_PATH / lora_path ──► LlamaCppProvider (checks sidecar, else base only)
```

## Files

| file | purpose |
|---|---|
| `config.py` | `FinetuneConfig` + named run `PROFILES` (base model, family preset, target GGUF, LoRA r/alpha/dropout/targets, 4-bit vs 16-bit, lengths, LR/epochs/batch, GRPO settings, thinking toggle, plan style, category weights) |
| `formatting.py` | SFT row preparation (plan line, tool cap), validation, tokenizer-free reference template, GRPO prompts (multi-step prefixes), gold/bad completions, seeded oversampling |
| `rewards.py` | TRL reward functions: the existing deterministic scorer (`core.geoai.eval.scoring.reward`, not copied) + a small format reward |
| `sft.py` / `grpo.py` | Unsloth + TRL training; `--dry-run` runs on CPU without torch |
| `evaluate.py` | quick GPU sanity eval on `eval_val` during training |
| `export.py` | GGUF LoRA conversion, merged q4_k_m export, sidecar, eval annotation + go/no-go |
| `colab/GeoAI_finetune.ipynb` | end-to-end notebook for a free T4 |

## Run profiles

A profile is the model identity of one run: what Unsloth loads, the HF reference id, the family preset,
the thinking switch and the exact base GGUF the desktop runs (repo, file, sha256, header fingerprint),
which `export.py` writes into the adapter sidecar. Default: **`qwen3-1.7b`** (best interim CPU benchmark).

One profile per model in `model_downloader.RECOMMENDED_MODELS` / `eval.benchmark.CANDIDATES` — not just
the Qwen family:

| profile | Unsloth loads | HF id | target GGUF |
|---|---|---|---|
| `qwen3-1.7b` (default) | `unsloth/Qwen3-1.7B` (QLoRA -> `unsloth/Qwen3-1.7B-unsloth-bnb-4bit`) | `Qwen/Qwen3-1.7B` | `unsloth/Qwen3-1.7B-GGUF` / `Qwen3-1.7B-Q4_K_M.gguf` (sha256 `b139949c...1897`) |
| `qwen2.5-1.5b` | `unsloth/Qwen2.5-1.5B-Instruct` | `Qwen/Qwen2.5-1.5B-Instruct` | `Qwen/Qwen2.5-1.5B-Instruct-GGUF` / `qwen2.5-1.5b-instruct-q4_k_m.gguf` |
| `qwen2.5-3b-instruct` | `unsloth/Qwen2.5-3B-Instruct` | `Qwen/Qwen2.5-3B-Instruct` | `Qwen/Qwen2.5-3B-Instruct-GGUF` / `qwen2.5-3b-instruct-q4_k_m.gguf` |
| `qwen2.5-7b-instruct` | `unsloth/Qwen2.5-7B-Instruct` | `Qwen/Qwen2.5-7B-Instruct` | `bartowski/Qwen2.5-7B-Instruct-GGUF` / `Qwen2.5-7B-Instruct-Q4_K_M.gguf` |
| `qwen3.5-2b` | `unsloth/Qwen3.5-2B` (16-bit LoRA) | `Qwen/Qwen3.5-2B` | `unsloth/Qwen3.5-2B-GGUF` / `Qwen3.5-2B-Q4_K_M.gguf` |
| `qwen3-4b-instruct-2507` | `unsloth/Qwen3-4B-Instruct-2507` | `Qwen/Qwen3-4B-Instruct-2507` | `unsloth/Qwen3-4B-Instruct-2507-GGUF` / `Qwen3-4B-Instruct-2507-Q4_K_M.gguf` |
| `qwen3-8b` | `unsloth/Qwen3-8B` | `Qwen/Qwen3-8B` | `Qwen/Qwen3-8B-GGUF` / `Qwen3-8B-Q4_K_M.gguf` |
| `phi-4-mini-instruct` | `unsloth/Phi-4-mini-instruct` | `microsoft/Phi-4-mini-instruct` | `unsloth/Phi-4-mini-instruct-GGUF` / `Phi-4-mini-instruct-Q4_K_M.gguf` |
| `granite-4.1-3b` | `unsloth/granite-4.1-3b` | `ibm-granite/granite-4.1-3b` | `ibm-granite/granite-4.1-3b-GGUF` / `granite-4.1-3b-Q4_K_M.gguf` |
| `smollm3-3b` | `unsloth/SmolLM3-3B` | `HuggingFaceTB/SmolLM3-3B` | `ggml-org/SmolLM3-3B-GGUF` / `SmolLM3-Q4_K_M.gguf` |
| `llama-3.2-3b-instruct` | `unsloth/Llama-3.2-3B-Instruct` | `meta-llama/Llama-3.2-3B-Instruct` | `bartowski/Llama-3.2-3B-Instruct-GGUF` / `Llama-3.2-3B-Instruct-Q4_K_M.gguf` |
| `mistral-7b-instruct-v0.3` | `unsloth/mistral-7b-instruct-v0.3` | `mistralai/Mistral-7B-Instruct-v0.3` | `bartowski/Mistral-7B-Instruct-v0.3-GGUF` / `Mistral-7B-Instruct-v0.3-Q4_K_M.gguf` |

Select with `--profile NAME`; add a new candidate by adding an entry to `PROFILES` in `config.py` (no model
names anywhere else). Passing `--base-model/--base-model-id/--family` that differ from the profile drops its
target GGUF, so a sidecar never claims the wrong base.

## Order of work

```
cd python-backend
# 1. regenerate the data (git-ignored; deterministic)
python -m core.geoai.training.scaleup --out core/geoai/training/data
# 2. CPU checks (no GPU stack; ~1 min each, mostly registry import)
python -m core.geoai.finetune.sft  --dry-run
python -m core.geoai.finetune.grpo --dry-run
# 3-6. on the GPU (Colab: colab/GeoAI_finetune.ipynb runs exactly these)
COMMON="--profile qwen3-1.7b --output-dir /content/geoai-ft"
python -m core.geoai.finetune.sft  $COMMON                                                          # 3. SFT
python -m core.geoai.finetune.evaluate --adapter-dir /content/geoai-ft/sft_adapter $COMMON --n 40   # 4. quick eval (eval_val)
python -m core.geoai.finetune.grpo $COMMON --set grpo_max_steps=300                                 # 5. GRPO
python -m core.geoai.finetune.export gguf-lora --adapter-dir /content/geoai-ft/grpo_adapter \
    --llama-cpp /content/llama.cpp --outfile /content/geoai-ft/export/geoai-lora.gguf                # 6. export
# 7. on the desktop: base vs adapter with GEOAI_CHAT_FORMAT=native and thinking off (see below)
```

Any config field can be overridden with `--set key=value` (e.g. `--set lora_r=32 --set load_in_4bit=false`)
or loaded from JSON with `--config` (a config saved before profiles existed gets no target GGUF).

## Clarification emphasis (oversampling)

Asking for missing / ambiguous / conflicting inputs instead of calling a tool is the weakest behaviour of
every benchmarked base model, so SFT repeats those rows of the **train split only** and GRPO repeats those
prompts (`sft_category_weights`, `grpo_category_weights`; defaults `missing_data` 2.0, `ambiguous_request` 2.0,
`conflicting_data` 1.5, `tool_failure` 1.5, `wrong_units:text` 1.5 - keys are `<category>` or
`<category>:tool_call|text`). A weight w gives floor(w) copies plus one more for a seeded-hash-chosen
fraction of rows, then a seeded shuffle, so the mix is identical on every run; weights < 1 downsample.
Train and val must share no id (checked); val and `eval_test` are never touched. The before/after mix is
printed by the dry-runs and training and stored in `geoai_run.json`. Disable with
`--set sft_category_weights={} --set grpo_category_weights={}`.

## Design choices

* **Base model is configurable** (profiles, or `base_model`, `base_model_id`, `family`). Family presets:
  `qwen2.5` (QLoRA), `qwen3` (QLoRA, `enable_thinking=False`), `qwen3.5` (16-bit LoRA as Unsloth recommends),
  `phi3` (Phi-4-mini), `granite` (Granite 4.1), `smollm3` (ChatML, `enable_thinking=False`), `llama3`
  (Llama 3.2), `mistral` (no per-turn role tag, just `[INST]`/`[/INST]`), `gemma3` (Gemma 3's template has
  no tool section: `sft.py` refuses it until a tool format is added). The adapter must be trained on the
  same model as the desktop base GGUF.
* **Chat format**: rows are rendered with the model's own template including `tools`
  (`tokenizer.apply_chat_template(messages, tools=...)`); Qwen/SmolLM3/Granite emit
  `<tool_call>{json}</tool_call>`, Mistral emits `[TOOL_CALLS][{json}]`, Llama 3.x a bare JSON object.
  Multi-step project trajectories (user -> call -> result -> call -> result -> answer) keep every tool they
  call offered; project context stays in the system prompt (`### CURRENT CONTEXT`).
  The desktop provider must therefore use the GGUF's own template: `chat_format="native"`
  (auto-selected when the adapter sidecar says `"chat_template": "native"`, or `GEOAI_CHAT_FORMAT=native`).
  The legacy `chatml-function-calling` handler uses a different prompt format and does not render tool results.
* **Short plan, no long thinking**: the first decision after a user message starts with one `Plan: ...` line
  (no numbers, <= 25 words) then the tool call or clarification; later steps after a tool result have no plan
  (the GRPO format reward follows the same rule). Thinking is off (`enable_thinking=False`) for CPU latency.
* **Loss on assistant turns only** (Unsloth `train_on_responses_only`); tool results are user-side
  `<tool_response>` turns and are masked. Over-long rows are dropped, never truncated.
* **Tool cap**: `max_tools=5` (called tool always kept). With all generated tools ~47% of SFT rows exceed
  4096 tokens; with 5 about 6%. The runtime selector currently offers up to 20 tools, which overflows
  `n_ctx=4096` in native mode - cap it to match before evaluating.
* **GRPO reward**: `core.geoai.eval.scoring.reward` (weight 1.0) + `format_reward` (weight 0.1): parseable
  `<tool_call>` JSON, no trailing chatter, a short plan line, no thinking block. The scorer already penalises
  malformed calls (unknown tool, schema 0) but still gives partial action credit, hence the format term.
* **Held-out data**: `eval_test` / `eval_gold` are refused by every loader; the SFT dry-run checks that no
  training id occurs in `eval_test`.
* **vLLM** (`--set grpo_use_vllm=true`) loads the model with Unsloth `fast_inference` for much faster rollouts;
  optional, needs `pip install vllm` and more VRAM.

## Expectations (estimates, not measurements)

| stage | ~1.7B model on a T4 | notes |
|---|---|---|
| SFT, 2 epochs, ~2.2k rows after oversampling | 45-90 min, ~7-10 GB VRAM (QLoRA) | 16-bit LoRA on 3-4B models may not fit 16 GB |
| GRPO, 300 steps, 4 generations | 1-3 h without vLLM | reduce steps or completions for a quick run |
| export GGUF LoRA | a few min | adapter ~20-40 MB at r=16, f16 |

## Evaluate base vs adapter (desktop, CPU) and the go/no-go rule

Keep adapters out of the models folder itself (e.g. `models/adapters/`). Thinking is off by default at
runtime - leave `GEOAI_THINKING` unset.

```
set BASE=%APPDATA%/GeoCore/models/Qwen3-1.7B-Q4_K_M.gguf
python -m core.geoai.finetune.export sidecar --lora geoai-lora.gguf --base-gguf %BASE%
set GEOAI_CHAT_FORMAT=native
python -m core.geoai.eval.runner --provider llama_cpp --model %BASE% --split test --label base --out base.json
set GEOAI_LORA_PATH=C:/path/to/geoai-lora.gguf
python -m core.geoai.eval.runner --provider llama_cpp --model %BASE% --split test --label lora --out lora.json
python -m core.geoai.eval.runner --compare base.json lora.json
python -m core.geoai.finetune.export annotate --lora geoai-lora.gguf --base-results base.json --candidate-results lora.json
```

Evaluate both with the same chat format, examples and `n_ctx`. **Ship the adapter only if** (`export.go_no_go`):
same example set; `mean_score` +0.02 or more; strict pass rate, hallucinated-parameter rate, caution-violation
rate and error rate no worse; no category pass rate drops by more than 0.05; p50 latency at most 1.3x the
base. Otherwise keep the base model (AGENTS.md §32). Note: llama-cpp-python disables mmap when a LoRA is
loaded (more RAM); a merged GGUF (`export merged`) avoids the adapter overhead if it wins.
