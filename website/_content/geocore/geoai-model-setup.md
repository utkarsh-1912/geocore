---
title: Setting up a GeoAI model
slug: geoai/model-setup
section: GeoAI
nav_order: 20
description: Download or link a local GGUF language model for GeoAI, where files are stored and how to configure it.
sources:
- python-backend/core/geoai/model_downloader.py
- python-backend/core/geoai/model_config.py
- python-backend/core/geoai/lifecycle.py
- python-backend/core/geoai/api.py
- RELEASE_GUIDE.md
---

GeoAI runs language models in the GGUF format through [llama.cpp](https://github.com/ggerganov/llama.cpp) (via `llama-cpp-python`), on the CPU by default. Models are not bundled with GeoCore; you download one once and it is then used offline.

## Installing a model from GeoCore

1. Open **GeoAI**. If no model is installed, the chat shows an installer card; otherwise open the **Local AI Model Manager**.
2. Pick a model and click **Download**. The download runs in the background and needs an internet connection. Models are downloaded from Hugging Face.
3. When the download completes the model becomes the active model. It is loaded the next time you use the chat.

The model manager offers these curated models (4-bit `Q4_K_M` quantisations), grouped by model family. The list is generated from the application's model registry:

<!-- geocore:generated geoai-model-catalogue -->

Larger models need more memory and respond more slowly on a CPU. Licences differ between families: check a model's licence before using it commercially. How the candidates compare on GeoAI's own test suite is published on the [Model benchmarks](/docs/geoai/model-benchmarks) page.

## Using a model you already have

- **Auto-link** scans the known model folders (see below) for `.gguf` files and activates the first one found if no valid model is configured.
- You can also enter the full path to any `.gguf` file in the model manager.

## Where files are stored

| Item | Windows | macOS / Linux |
|---|---|---|
| Downloaded models | `%APPDATA%\GeoCore\models` | `~/.geocore/models` |
| GeoAI settings (`geoai_config.json`) | `%APPDATA%\GeoCore` | `~/.geocore` |

Auto-link also looks in a `models` folder next to the application, in `%ProgramFiles%\GeoCore\models` and in `%LOCALAPPDATA%\GeoCore\models` on Windows.

## Settings

`geoai_config.json` holds the active model and runtime settings. Defaults:

| Setting | Default | Meaning |
|---|---|---|
| `model_path` | none | Path of the active `.gguf` file. |
| `provider` | `auto` | `llama_cpp`, `heuristic`, or `auto` (use the model when one is configured). |
| `n_ctx` | `4096` | Context window in tokens. |
| `n_gpu_layers` | `0` | Layers offloaded to a GPU (`0` = CPU only, `-1` = all). |
| `temperature` | `0.1` | Low temperature for consistent tool calls. |
| `max_tools` | `5` | Tools offered to the model per request. Each tool description costs about 390 tokens, so 20 tools would not fit in a 4096-token context. |
| `decision_max_tokens` | `512` | Length limit for the first step, where the model calls a tool or answers directly. |
| `answer_max_tokens` | `1024` | Length limit for the answer written after a tool call. |
| `explanations` | `on_request` | When the model writes up a tool result: `on_request` (only when you ask it to explain, interpret or compare), `always` or `never`. |
| `generation_timeout_s` | `600` | A single model call is stopped after this many seconds (`0` = no limit). |
| `multi_agent` | `true` | Split compound requests between specialist agents. |

Environment variables override these settings:

| Variable | Setting |
|---|---|
| `GEOAI_MODEL_PATH` | Path of the `.gguf` file |
| `GEOAI_PROVIDER` | `llama_cpp`, `heuristic` or `auto` |
| `GEOAI_N_CTX` | Context window |
| `GEOAI_GPU_LAYERS` | Layers offloaded to a GPU |
| `GEOAI_N_THREADS`, `GEOAI_N_THREADS_BATCH` | CPU threads for generation and prompt processing (default: chosen for the machine) |
| `GEOAI_MAX_TOOLS` | Tools offered per request |
| `GEOAI_DECISION_MAX_TOKENS`, `GEOAI_ANSWER_MAX_TOKENS` | Generation length limits |
| `GEOAI_EXPLANATIONS` | `on_request`, `always` or `never` |
| `GEOAI_GENERATION_TIMEOUT_S` | Time limit per model call |
| `GEOAI_MULTI_AGENT` | `0` turns off splitting compound requests |
| `GEOAI_CHAT_FORMAT` | `chatml-function-calling`, `native` or `prompted` (default: chosen from the model) |
| `GEOAI_THINKING` | `1` turns on the reasoning mode of models that have one (off by default; it is slow on a CPU) |
| `GEOAI_LORA_PATH`, `GEOAI_LORA_SCALE` | Optional LoRA adapter |

GPU offloading only has an effect with a GPU-enabled build of `llama-cpp-python`; the official GeoCore builds include the CPU build.

## Memory use

The model is not loaded when GeoCore starts. It is loaded in the background when you open the GeoAI chat (or start typing in it), so the first answer does not wait for the load, and it is released again after 15 minutes without use. The GeoAI window shows the engine's memory use and whether a model is loaded. Switching or downloading a model unloads the previous one. The engine also exposes an unload endpoint (`POST /api/geoai/unload`) that releases the model from memory.

If the model cannot be loaded (for example the file is missing or `llama-cpp-python` is not available), GeoAI falls back to the keyword-based heuristic provider.
