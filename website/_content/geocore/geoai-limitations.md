---
title: Limitations and engineering caution
slug: geoai/limitations
section: GeoAI
nav_order: 50
description: What GeoAI cannot do, known limitations of small local models, and how to check its answers.
sources:
- AGENTS.md
- stage/plan.md
- python-backend/core/geoai/system_prompt.py
- python-backend/core/geoai/tool_selector.py
- python-backend/core/geoai/model_config.py
---

GeoAI is an engineering assistant, not an engineer. Treat every answer as a starting point that you verify.

## What GeoAI is instructed to do

The system prompt given to the model requires it to:

- use calculation tools for all numbers and never work through engineering equations itself;
- ask for missing parameters instead of inventing them;
- report units with every numerical result;
- state results as "the calculated value is X based on method Y", never "this design is safe";
- flag unexpected results and suggest verification;
- distinguish project data, calculation results, literature, standards, its own interpretation and assumptions;
- never fabricate references.

These are instructions to a language model. Small local models do not always follow them, so check the answer against the tool results shown with it.

## Known limitations

- **Small models make mistakes.** Local models with a few billion parameters can choose the wrong tool, miss or misread an input, or misstate a unit. Always compare the inputs GeoAI passed to the tool with your request.
- **Tool preselection is keyword-based.** Only up to 20 tools that match words in your request (or the calculator you have open) are offered to the model. If the right calculation is not among them, GeoAI cannot use it; rephrasing with the method name or opening the relevant calculator first helps.
- **Limited context.** The default context window is 4096 tokens. Long conversations, many tool schemas or large results may not fit.
- **Heuristic fallback.** Without a model, GeoAI only matches keywords and extracts numbers with regular expressions. It cannot ask follow-up questions or explain results.
- **Unit handling depends on the tool.** Curated tools convert and check units; tools generated for other calculators take values in the units stated in the calculator and do not convert unit strings.
- **Not every calculator suits chat.** Calculations that need stored objects (soil profiles, CPT processing objects, AGS files) are best run from the calculation forms.
- **No web access.** GeoAI only knows what the model learned in training, the tool results and the documents in its [local index](/docs/geoai/research).

## Checking an answer

1. Look at the tool that was called and the inputs it received.
2. Check the units of every input and output.
3. Open the calculator with **Open in Form** and rerun it yourself.
4. Read the method's documentation and validity range in the [groundhog API reference](/docs/groundhog/api).
5. Apply engineering judgement. A calculated capacity or settlement depends on the method, the parameters and their uncertainty; GeoAI does not certify that a design is adequate.
