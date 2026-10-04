---
title: Setting up a GeoAI model
slug: geoai/model-setup
section: GeoAI
description: Download or link a local GGUF language model for GeoAI, where files are stored and how to configure it.
origin: geocore
source_url: https://github.com/utkarsh-1912/geocore/blob/main/website/_content/geocore/geoai-model-setup.md
license: GPL-3.0
author: Utkarsh Gupta
attribution: GeoCore documentation by Utkarsh Gupta, licensed under the GNU GPL v3.
groundhog_version: 0.15.0
edited_by_geocore: false
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
3. When the download completes the model becomes the active model. It is loaded the first time you send a message.

The model manager offers these curated models (4-bit `Q4_K_M` quantisations), grouped by model family. The list is generated from the application's model registry:

| Model | Download size | Licence | Notes |
|---|---|---|---|
| [Qwen 2.5 (1.5B Instruct)](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) | ~1.0 GB | Apache-2.0 | Ultra-lightweight (1.5B), rapid CPU inference, high-precision function calling |
| [Qwen 3.5 (2B)](https://huggingface.co/unsloth/Qwen3.5-2B-GGUF) | ~1.2 GB | Apache-2.0 | Qwen 3.5 small (2B, 262k context) with native tool-calling chat template; benchmark candidate |
| [Qwen 3 (1.7B)](https://huggingface.co/unsloth/Qwen3-1.7B-GGUF) | ~1.0 GB | Apache-2.0 | Qwen 3 (1.7B, 40k context) hybrid thinking model with native tool calling; benchmark candidate |
| [Qwen 2.5 (3B Instruct)](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF) | ~2.0 GB | Qwen Research (non-commercial) | Balanced (3B) with superior multi-turn geotechnical reasoning and complex parameter extraction |
| [Qwen 2.5 (7B Instruct)](https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF) | ~4.4 GB | Apache-2.0 | Maximum capability (7B) for complex geotechnical synthesis, CPT profiling & tool orchestration |
| [Qwen 3 (4B Instruct 2507)](https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF) | ~2.3 GB | Apache-2.0 | Qwen 3 (4B) non-thinking instruct release with native tool calling; benchmark candidate |
| [Qwen 3 (8B)](https://huggingface.co/Qwen/Qwen3-8B-GGUF) | ~4.7 GB | Apache-2.0 | Qwen 3 (8B) hybrid thinking model with native tool calling; quality reference, slow on CPU |
| [Phi-4-mini (3.8B Instruct)](https://huggingface.co/unsloth/Phi-4-mini-instruct-GGUF) | ~2.3 GB | MIT | Microsoft Phi-4-mini (3.8B), trained for function calling; MIT licence; benchmark candidate |
| [Granite 4.0 Micro (3B)](https://huggingface.co/ibm-granite/granite-4.0-micro-GGUF) | ~2.0 GB | Apache-2.0 | IBM Granite 4.0 Micro (3B) with native tool calling; benchmark candidate |
| [SmolLM3 (3B)](https://huggingface.co/ggml-org/SmolLM3-3B-GGUF) | ~1.8 GB | Apache-2.0 | Hugging Face SmolLM3 (3B) hybrid thinking model with tool calling; fully open training data |
| [Llama 3.2 (3B Instruct)](https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF) | ~1.9 GB | Llama 3.2 Community | Meta Llama 3.2 (3B) with JSON tool calls; custom licence with use restrictions |
| [Mistral 7B Instruct (v0.3)](https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF) | ~4.1 GB | Apache-2.0 | Mistral 7B Instruct v0.3 with native [TOOL_CALLS] function calling; strong literature & standards synthesis |
| [Gemma 3 (4B IT)](https://huggingface.co/unsloth/gemma-3-4b-it-GGUF) | ~2.3 GB | Gemma Terms of Use | Google Gemma 3 (4B); its template has no tool section, so GeoAI describes tools in the prompt |

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
| `max_tokens` | `1024` | Maximum length of a generated answer. |

The environment variables `GEOAI_MODEL_PATH`, `GEOAI_PROVIDER`, `GEOAI_N_CTX` and `GEOAI_GPU_LAYERS` override these settings. GPU offloading only has an effect with a GPU-enabled build of `llama-cpp-python`; the official GeoCore builds include the CPU build.

## Memory use

The model is loaded only when GeoAI is first used, not when GeoCore starts. The GeoAI window shows the engine's memory use and whether a model is loaded. Switching or downloading a model unloads the previous one; the new model is loaded on the next request. The engine also exposes an unload endpoint (`POST /api/geoai/unload`) that releases the model from memory.

If the model cannot be loaded (for example the file is missing or `llama-cpp-python` is not available), GeoAI falls back to the keyword-based heuristic provider.
