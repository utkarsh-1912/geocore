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
3. When the download completes the model becomes the active model. It is loaded the first time you send a message.

The model manager offers these curated models (4-bit `Q4_K_M` quantisations):

| Model | Download size | Notes |
|---|---|---|
| Qwen 2.5 1.5B Instruct | ~1.0 GB | Smallest and fastest; suited to laptops. Default choice. |
| Qwen 2.5 3B Instruct | ~2.0 GB | Balance of speed and quality. |
| Qwen 2.5 7B Instruct | ~4.4 GB | Best quality of the Qwen options; needs a powerful machine. |
| Gemma 2 2B IT | ~1.6 GB | Alternative small model. |
| Gemma 2 9B IT | ~5.4 GB | Large model; 16 GB RAM or more recommended. |

Which model works best for GeoAI's tool calling is still being evaluated. Larger models need more memory and respond more slowly on a CPU.

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
