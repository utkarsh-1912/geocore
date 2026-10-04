# GeoAI

The local geotechnical assistant inside GeoCore. A small local model understands the question and picks a tool; the GeoCore tool registry runs the deterministic Groundhog calculation; the model explains the result. Design rules are in [../../../AGENTS.md](../../../AGENTS.md). This page is the map of the code.

## One chat turn

```text
POST /api/geoai/chat?stream=true            api.py
  └─ GeoAIAgent.run_stream                  agent.py
       1. stage checking_tools   select_relevant_tools (tool_selector.py, tool_retrieval.py)
       2. stage thinking         model decides: tool call, clarification or direct answer
       3. guard                  argument_grounding.py refuses calls that carry numbers the user never gave
       4. tool_start / tool_result   GeoAIToolRegistry.invoke_tool (validated, unit-normalised, provenance attached)
       5. stage writing_answer   model explains; response_guard.py removes repeats, echoed records, wrong units
       6. done
```

SSE event types: `stage`, `token`, `tool_start`, `tool_result`, `done`, `cancelled`, `error`. Lines starting with `:` are keepalives (every 5 s) and carry no data.

If a turn would end with no answer text, `run_stream` appends an explicit "nothing was calculated" message so the chat is never blank.

## Modules

| Module | Role |
| :--- | :--- |
| `model_provider.py` | `ModelProvider` interface and message types. The model is replaceable; nothing else names a specific model |
| `llama_cpp_provider.py` | Production provider (llama.cpp, GGUF). Parses tool calls for each model family, strips thinking blocks, enforces cancel and the per-call time limit |
| `heuristic_provider.py`, `gemma_engine.py` | Rule-based provider: no-model fallback and test double |
| `model_config.py`, `model_downloader.py`, `gguf_meta.py`, `lora_adapter.py` | Configuration, model download and discovery, GGUF metadata, LoRA compatibility |
| `lifecycle.py` | Lazy load, background warm-up, idle unload, cancel |
| `agent.py` | The loop above, plus history replay and turn tracing |
| `system_prompt.py` | System prompt (engineering-caution rules, compact project context) |
| `tool_registry.py`, `tool_definitions.py`, `tool_metadata.py`, `schema_factory.py`, `schemas/` | Tool registry: explicit Pydantic schemas, bounds, units, method metadata. Only registered tools are reachable by the model |
| `tool_selector.py`, `tool_retrieval.py` | Offer the model a small relevant subset of tools (default 5) to fit the context window |
| `units.py`, `validator.py`, `argument_grounding.py` | Deterministic unit conversion, input validation, and the no-invented-values rule |
| `provenance.py` | Method, inputs, units and source recorded with every derived value |
| `cpt.py`, `spt.py`, `ags.py`, `project_cpt.py`, `project_soil.py`, `data_access.py`, `context_resolver.py` | Project data: parse deterministically, expose compact query tools, resolve missing inputs from the project |
| `research/` | Local document index (SQLite FTS5) and evidence tiers (project, calculation, literature, standards, interpretation, assumption) |
| `calculation_explainer.py` | Deterministic "Formula & Derivation" explanation and optional narration |
| `turn_trace.py` | Per-turn outcome classification and log (below) |
| `eval/` | Offline evaluation: scorer, runner, benchmark, baselines in `eval/results/` |
| `training/`, `finetune/` | Dataset generation and LoRA/QLoRA tooling. See [finetune/README.md](finetune/README.md). Not used at runtime |

## Reliability and diagnostics

Every streamed turn is classified and appended to `geoai_turns.jsonl` in the user config directory (`%APPDATA%\GeoCore\` or `~/.geocore/`; rotated at 2 MB, local only, never uploaded). A line records the outcome, elapsed time, stages reached, tools called and tool errors, answer length, model file, chat format and any error. It contains no prompt text.

| Outcome | Meaning |
| :--- | :--- |
| `ok` | Answered, with or without a tool |
| `tool_error` | A tool rejected its inputs or failed (usually the right outcome for missing data) |
| `empty_answer` | The model produced nothing; the user got the explicit notice |
| `malformed_tool_call` | Raw tool-call markup came back as text instead of a valid call |
| `no_tool_call_suspected` | A calculation-style request was answered in prose without a tool |
| `timeout` | A model call exceeded `generation_timeout_s` |
| `cancelled` | Stop pressed, window closed or client disconnected |
| `error` | Unexpected exception |

Count them with:

```bash
python -c "import json,collections,pathlib,os; p=pathlib.Path(os.environ.get('APPDATA','~')).expanduser()/'GeoCore'/'geoai_turns.jsonl'; print(collections.Counter(json.loads(l)['outcome'] for l in p.open()))"
```

On macOS/Linux replace the path with `~/.geocore/geoai_turns.jsonl`.

## Configuration

Environment variables are listed in the [root README](../../../README.md#models). Generation caps (`decision_max_tokens`, `answer_max_tokens`) and `generation_timeout_s` are in `GeoAIModelConfig`.

## Adding a tool

1. Write or reuse the deterministic function (Groundhog or a GeoCore module). Do not put the equation in a prompt.
2. Add a Pydantic input schema in `schemas/` with units in field descriptions and physical bounds.
3. Register it in `tool_definitions.py` with method and applicable-standard metadata in `tool_metadata.py`.
4. Add tests: schema validation, a numerical check against a known result, and an agent-level test with a scripted provider (see `tests/test_geoai_freeze_and_grounding.py` for the pattern).
5. Re-run the evaluation (`python -m core.geoai.eval.runner`) and compare against the previous baseline.

## Testing

```bash
python -m pytest tests/ -k geoai
```

Tests use scripted providers, so they need no model. For real-model behaviour use the evaluation runner with `--provider llama_cpp --model <file.gguf>`.
