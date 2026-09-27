---
title: GeoAI overview
slug: geoai/overview
section: GeoAI
nav_order: 10
description: What GeoAI does, how it uses groundhog for every number it reports, and how to use it.
sources:
- AGENTS.md
- stage/plan.md
- python-backend/core/geoai/agent.py
- python-backend/core/geoai/system_prompt.py
- python-backend/core/geoai/tool_selector.py
- python-backend/core/geoai/tool_registry.py
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

- selects up to 20 candidate tools that match the words in your request (and the calculator you have open), to keep the prompt small enough for local models;
- lets the model call tools for up to three rounds, so one answer can chain several calculations;
- validates every tool call before running it and returns validation errors to the model instead of guessing values;
- attaches a provenance record (tool, inputs, method, timestamp) to every tool result.

## Using GeoAI

- Open **GeoAI** from the sidebar for the full chat window. A compact assistant panel can be opened from the GeoAI window.
- Type a request such as *"Calculate the bulk unit weight for Gs = 2.65, e = 0.6 and full saturation"*. Suggested prompt cards are shown when the chat is empty.
- Answers stream in as they are generated. Tool calls, the inputs used and their results are shown with the answer.
- **Open in Form** opens the corresponding GeoCore calculator so you can check the inputs and rerun the calculation yourself.

If a required input is missing, GeoAI is instructed to ask for it rather than invent a value. See [Limitations and engineering caution](/docs/geoai/limitations) before relying on an answer.

## Without a model

If no language model is installed (or it cannot be loaded), GeoAI uses a **heuristic provider**: keyword matching chooses a tool and regular expressions pull numbers out of your message. It can run simple single-tool requests but cannot hold a conversation or explain results. [Install a model](/docs/geoai/model-setup) for the full experience.
