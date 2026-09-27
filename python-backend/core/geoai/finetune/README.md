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
| `config.py` | `FinetuneConfig` (base model, family preset, LoRA r/alpha/dropout/targets, 4-bit vs 16-bit, lengths, LR/epochs/batch, GRPO settings, thinking toggle, plan style) |
| `formatting.py` | SFT row preparation (plan line, tool cap), validation, tokenizer-free reference template, GRPO prompts, gold/bad completions |
| `rewards.py` | TRL reward functions: the existing deterministic scorer (`core.geoai.eval.scoring.reward`, not copied) + a small format reward |
| `sft.py` / `grpo.py` | Unsloth + TRL training; `--dry-run` runs on CPU without torch |
| `evaluate.py` | quick GPU sanity eval on `eval_val` during training |
| `export.py` | GGUF LoRA conversion, merged q4_k_m export, sidecar, eval annotation + go/no-go |
| `colab/GeoAI_finetune.ipynb` | end-to-end notebook for a free T4 |

## Commands

Local / CI (CPU, no GPU stack; ~1 min each, mostly registry import):

```
cd python-backend
python -m core.geoai.training.scaleup --out core/geoai/training/data   # data is git-ignored
python -m core.geoai.finetune.sft  --dry-run
python -m core.geoai.finetune.grpo --dry-run
```

GPU (Colab: open `colab/GeoAI_finetune.ipynb`, or run the same commands):

```
COMMON="--base-model unsloth/Qwen2.5-1.5B-Instruct --base-model-id Qwen/Qwen2.5-1.5B-Instruct --family qwen2.5 --output-dir /content/geoai-ft"
python -m core.geoai.finetune.sft  $COMMON
python -m core.geoai.finetune.evaluate --adapter-dir /content/geoai-ft/sft_adapter $COMMON --n 40
python -m core.geoai.finetune.grpo $COMMON --set grpo_max_steps=300
python -m core.geoai.finetune.export gguf-lora --adapter-dir /content/geoai-ft/grpo_adapter \
    --llama-cpp /content/llama.cpp --outfile /content/geoai-ft/export/geoai-lora.gguf
```

Any config field can be overridden with `--set key=value` (e.g. `--set lora_r=32 --set load_in_4bit=false`)
or loaded from JSON with `--config`.

## Design choices

* **Base model is configurable** (`base_model`, `base_model_id`, `family`). Presets: `qwen2.5` (current
  baseline, QLoRA), `qwen3` (QLoRA, `enable_thinking=False`), `qwen3.5` (16-bit LoRA as Unsloth recommends),
  `gemma3` (Gemma 3's template has no tool section: `sft.py` refuses it until a tool format is added).
  The adapter must be trained on the same model as the desktop base GGUF.
* **Chat format**: rows are rendered with the model's own template including `tools`
  (`tokenizer.apply_chat_template(messages, tools=...)`); Qwen emits `<tool_call>{json}</tool_call>`.
  The desktop provider must therefore use the GGUF's own template: `chat_format="native"`
  (auto-selected when the adapter sidecar says `"chat_template": "native"`, or `GEOAI_CHAT_FORMAT=native`).
  The legacy `chatml-function-calling` handler uses a different prompt format and does not render tool results.
* **Short plan, no long thinking**: each decision turn starts with one `Plan: ...` line (no numbers, <= 25 words)
  then the tool call or clarification. Thinking is off (`enable_thinking=False`) for CPU latency.
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

| stage | Qwen2.5-1.5B on a T4 | notes |
|---|---|---|
| SFT, 2 epochs, ~1.6k rows | 30-60 min, ~6-9 GB VRAM (QLoRA) | 16-bit LoRA on 3-4B models may not fit 16 GB |
| GRPO, 300 steps, 4 generations | 1-3 h without vLLM | reduce steps or completions for a quick run |
| export GGUF LoRA | a few min | adapter ~20-40 MB at r=16, f16 |

## Evaluate base vs adapter (desktop, CPU) and the go/no-go rule

```
python -m core.geoai.finetune.export sidecar --lora geoai-lora.gguf --base-gguf %APPDATA%/GeoCore/models/qwen2.5-1.5b-instruct-q4_k_m.gguf
set GEOAI_CHAT_FORMAT=native
python -m core.geoai.eval.runner --provider llama_cpp --split test --label base --out base.json
set GEOAI_LORA_PATH=C:/path/to/geoai-lora.gguf
python -m core.geoai.eval.runner --provider llama_cpp --split test --label lora --out lora.json
python -m core.geoai.eval.runner --compare base.json lora.json
python -m core.geoai.finetune.export annotate --lora geoai-lora.gguf --base-results base.json --candidate-results lora.json
```

Evaluate both with the same chat format, examples and `n_ctx`. **Ship the adapter only if** (`export.go_no_go`):
same example set; `mean_score` +0.02 or more; strict pass rate, hallucinated-parameter rate, caution-violation
rate and error rate no worse; no category pass rate drops by more than 0.05; p50 latency at most 1.3x the
base. Otherwise keep the base model (AGENTS.md §32). Note: llama-cpp-python disables mmap when a LoRA is
loaded (more RAM); a merged GGUF (`export merged`) avoids the adapter overhead if it wins.
