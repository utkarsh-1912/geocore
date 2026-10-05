---
title: GeoAI overview
slug: geoai/overview
section: GeoAI
description: What GeoAI does, how it uses groundhog for every number it reports, and how to use it.
origin: geocore
source_url: https://github.com/utkarsh-1912/geocore/blob/main/website/_content/geocore/geoai-overview.md
license: GPL-3.0
author: Utkarsh Gupta
attribution: GeoCore documentation by Utkarsh Gupta, licensed under the GNU GPL v3.
groundhog_version: 0.15.0
edited_by_geocore: false
sources:
- AGENTS.md
- stage/plan.md
- python-backend/core/geoai/agent.py
- python-backend/core/geoai/system_prompt.py
- python-backend/core/geoai/tool_selector.py
- python-backend/core/geoai/tool_registry.py
- python-backend/core/geoai/model_config.py
- python-backend/core/geoai/argument_grounding.py
- python-backend/core/geoai/multi_agent.py
- python-backend/core/geoai/lifecycle.py
- electron-app/src/features/copilot/ProjectGroundwaterField.jsx
- electron-app/src/features/copilot/GeoAIFullWindow.jsx
- electron-app/src/features/copilot/GeoAICopilot.jsx
---

GeoAI is the geotechnical assistant built into GeoCore. You describe a calculation in plain language; GeoAI chooses a calculation tool, extracts the input values from your message, runs the calculation through groundhog and explains the result.

GeoAI runs locally. It uses a small language model on your own computer (or a rule-based fallback when no model is installed). Your prompts and project data are not sent to a cloud service.

## How it works

```text
Your request
   │
   ▼
Local language model ── chooses a tool and extracts the inputs
   │
   ▼
GeoCore tool registry ── validates the inputs against the tool's schema
   │
   ▼
groundhog ── performs the calculation
   │
   ▼
Local language model ── explains the result, with units and method
```

The language model **does not calculate**. Every number in a GeoAI answer that comes from a calculation is produced by a groundhog function (or a GeoCore CPT/SPT routine), and the model is instructed to report it with its units and method. The model can only call tools registered in GeoCore's tool registry; it cannot run arbitrary code, shell commands or file operations.

Specifically, GeoAI:

- offers the model the 5 tools that best match your request (and the calculator you have open), to keep the prompt small enough for local models;
- lets the model call tools for up to three rounds, so one answer can chain several calculations;
- splits compound requests (for example *"classify CPT-03, then size a footing"*) between specialist agents;
- validates every tool call before running it and returns validation errors to the model instead of guessing values;
- refuses a tool call that contains numbers you never gave, instead of running it;
- attaches a provenance record (tool, inputs, method, timestamp) to every tool result.

For a plain calculation request, GeoAI answers straight away with a fixed summary of the tool result rather than asking the model to write it up: small models sometimes misquote numbers, and the write-up takes tens of seconds on a CPU. Ask GeoAI to *explain*, *interpret* or *compare* when you want a written explanation.

## Using GeoAI

- Open **GeoAI** from the sidebar for the full chat window. A compact assistant panel can be opened from the GeoAI window, from the command palette, or with `Ctrl+Shift+A` (`Cmd+Shift+A` on macOS) from anywhere in the app.
- Type a request such as *"Calculate the bulk unit weight for Gs = 2.65, e = 0.6 and full saturation"*. Suggested prompt cards are shown when the chat is empty.
- Answers stream in as they are generated, and the chat shows what GeoAI is doing (*Checking for tools*, *Interpreting input*, *Calling tool*, *Generating output*). Tool calls, the inputs used and their results are shown with the answer. The stop button (**Stop generating**) cancels a turn.
- **Open in Form** opens the corresponding GeoCore calculator so you can check the inputs and rerun the calculation yourself.
- Record the project's **groundwater level** in the GeoAI window. When it is not recorded, GeoAI asks for it instead of assuming one.
- The model is loaded in the background when you open the chat, and released after 15 minutes without use.

If a required input is missing, GeoAI is instructed to ask for it rather than invent a value. See [Limitations and engineering caution](/docs/geoai/limitations) before relying on an answer.

## Without a model

If no language model is installed (or it cannot be loaded), GeoAI uses a **heuristic provider**: keyword matching chooses a tool and regular expressions pull numbers out of your message. It can run simple single-tool requests but cannot hold a conversation or explain results. [Install a model](/docs/geoai/model-setup) for the full experience.
