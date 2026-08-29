# GeoCore - GeoAI Agent Instructions

## Mission

You are developing **GeoAI**, the local geotechnical AI assistant inside GeoCore.

GeoAI is a lightweight desktop application feature combining:

* local SLM inference;
* Groundhog engineering calculations;
* GeoCore tools;
* CPT/SPT/AGS data;
* project context;
* local documents;
* optional external research.

The objective is to create a useful engineering AI, not a generic chatbot and not an AI API product.

---

# 1. Repository-first behaviour

Before changing code:

1. Inspect the repository.
2. Identify the relevant existing implementation.
3. Read existing tests.
4. Reuse existing abstractions.
5. Avoid duplicate functionality.
6. Make the smallest change that solves the problem.

Never assume an abstraction does not exist.

Search first.

---

# 2. Architecture

The intended architecture is:

```text
GeoCore Desktop
      │
      ▼
    GeoAI
      │
      ├── Local SLM
      │
      ├── Agent / Planner
      │
      ├── Project Context
      │
      ├── Tool Registry
      │
      └── Research
             │
             ├── Local documents
             └── Optional web
      │
      ▼
Groundhog / deterministic GeoCore calculations
```

The SLM reasons and orchestrates.

Groundhog calculates.

The application supplies evidence.

---

# 3. No unnecessary APIs

GeoAI is primarily a local desktop feature.

Do not introduce:

* cloud APIs;
* remote LLM dependencies;
* microservices;
* Docker;
* Redis;
* PostgreSQL;
* mandatory HTTP model servers.

Prefer direct local inference through the selected runtime.

If an API is genuinely required for an existing subsystem, preserve the existing architecture, but do not create an API merely to connect the local model.

---

# 4. Local model

The model must be replaceable.

Do not hard-code:

```text
Qwen
```

or:

```text
Gemma
```

throughout the application.

Use a model-provider interface.

Example:

```python
class ModelProvider:
    ...
```

Production target:

```text
llama.cpp + GGUF
```

Candidate models:

```text
Qwen3
Gemma 3
```

Model choice must be benchmark-driven.

---

# 5. Model responsibility

The SLM should:

* understand user intent;
* select tools;
* extract arguments;
* ask clarification questions;
* interpret results;
* synthesize evidence;
* explain engineering concepts.

The SLM should NOT:

* replace Groundhog;
* invent numerical calculations;
* silently invent missing soil parameters;
* fabricate references;
* claim unsupported engineering certainty.

---

# 6. Groundhog responsibility

Groundhog is authoritative for deterministic engineering calculations.

If a Groundhog/GeoCore function exists for a calculation, use it.

Do not reproduce the equation in an LLM prompt and ask the model to calculate it.

Correct:

```text
SLM
 ↓
tool call
 ↓
Groundhog
 ↓
result
 ↓
SLM explanation
```

Incorrect:

```text
SLM
 ↓
calculate engineering equation itself
```

---

# 7. Tool Registry

All model-accessible application functionality must go through the validated GeoCore Tool Registry.

Never allow the model to execute arbitrary:

* Python;
* shell;
* filesystem operations;
* SQL;
* subprocesses.

Tools must have explicit schemas.

Tool inputs must be validated before execution.

Tool outputs should be structured whenever practical.

---

# 8. Tool design

Tools should express engineering capabilities rather than implementation details.

Prefer:

```text
get_cpt_sounding
calculate_cpt_soil_behavior_type
calculate_pile_capacity_from_cpt
```

over:

```text
internal_cpt_helper_03
```

Each tool should document:

* purpose;
* inputs;
* units;
* assumptions;
* output;
* applicable methods;
* errors.

---

# 9. CPT

CPT is a core GeoAI capability.

Never pass large raw CPT datasets directly to the SLM unless necessary.

Use structured tools.

Typical flow:

```text
User
 ↓
get_cpt
 ↓
structured CPT
 ↓
interpretation tool
 ↓
derived parameters
 ↓
GeoAI explanation
```

Preserve provenance for derived parameters.

Example:

```text
value
method
source
inputs
units
```

---

# 10. SPT / boreholes / AGS

Use the same principle as CPT.

Parse source data deterministically.

Normalize it into GeoCore structures.

Then expose compact query tools to GeoAI.

Do not expect the SLM to understand arbitrary raw AGS files.

---

# 11. Research

Research is a first-class feature.

For current/external information:

```text
question
 ↓
search
 ↓
retrieve
 ↓
evidence
 ↓
synthesis
```

Never fabricate:

* papers;
* authors;
* standards;
* publication dates;
* DOI;
* quotations;
* numerical claims.

If evidence cannot be verified, say so.

---

# 12. Research grounding

Research answers should distinguish:

```text
Project evidence
Calculation evidence
Literature evidence
Standards/guidance
Model interpretation
Assumption
```

When possible, expose source information to the user.

The model should not imply that a literature claim is a project measurement.

---

# 13. Local RAG

Prefer a lightweight local architecture.

Default direction:

```text
documents
 ↓
text extraction
 ↓
chunking
 ↓
embedding
 ↓
SQLite/local index
 ↓
retrieval
 ↓
SLM
```

Do not introduce a heavyweight vector database unless measurements show that it is necessary.

---

# 14. Context

Never put the entire project into the prompt.

Retrieve only what is relevant.

Example:

```text
Question
 ↓
identify CPT-03
 ↓
retrieve CPT-03
 ↓
retrieve relevant soil parameters
 ↓
retrieve relevant calculation history
 ↓
build context
 ↓
SLM
```

Small local models require disciplined context management.

---

# 15. Memory

Separate:

* conversation memory;
* project memory;
* calculation history;
* research evidence.

Do not blindly append all history to every request.

Use retrieval and summarization.

---

# 16. Units

Units must be explicit.

Never assume the SLM has correctly converted a value.

Use deterministic unit conversion wherever possible.

Common units include:

```text
kPa
MPa
kN
kN/m
kN/m²
kN/m³
m
mm
degrees
%
```

Tool schemas should clearly identify expected units.

---

# 17. Error handling

Tool failures are information.

If a tool reports:

```text
missing parameter
```

do not invent a value.

Ask the user.

If a tool reports:

```text
invalid CPT
```

explain the problem.

If a calculation produces an unexpected result:

1. verify inputs;
2. verify units;
3. verify method;
4. inspect tool output;
5. flag uncertainty.

---

# 18. Engineering caution

GeoAI is an engineering assistant.

Avoid statements such as:

> This design is safe.

unless the application has a well-defined basis for making that statement.

Prefer:

> The calculated ultimate capacity is...

> Based on the supplied parameters...

> This result depends on...

> Further engineering judgement is required...

---

# 19. Fine-tuning

Do not fine-tune before a working tool-using baseline exists.

Required sequence:

```text
working tools
 ↓
working agent
 ↓
evaluation dataset
 ↓
failure collection
 ↓
SFT/LoRA/QLoRA
 ↓
benchmark
```

The model should be trained primarily for:

* tool selection;
* argument extraction;
* clarification;
* CPT interpretation;
* engineering terminology;
* research planning;
* evidence synthesis.

Do not train the model to replace deterministic Groundhog calculations.

---

# 20. Dataset quality

Prefer high-quality examples over massive synthetic datasets.

Every training example should have a clear expected behaviour.

Include:

### Correct requests

```text
Calculate settlement for...
```

### Ambiguous requests

```text
Calculate the pile capacity.
```

### Missing data

```text
Calculate bearing capacity.
```

### Wrong units

```text
gamma = 18 kPa
```

### Conflicting data

```text
CPT says...
Borehole says...
```

### Research

```text
Compare CPT methods for...
```

### Tool failure

```text
CPT unavailable
```

The model must learn to respond appropriately.

---

# 21. Evaluation

Maintain a regression test suite.

Test:

* tool selection;
* argument extraction;
* unit conversion;
* clarification;
* CPT reasoning;
* calculation selection;
* research grounding;
* citation accuracy;
* hallucination;
* latency;
* memory usage.

Every major model/prompt/tool change should be evaluated.

---

# 22. UI principles

GeoAI should feel integrated into GeoCore.

Useful UI concepts:

```text
Chat
Research
Project
CPT
Calculations
Sources
```

Answers should make it easy to inspect:

* tools used;
* inputs;
* results;
* assumptions;
* sources.

Do not overload the interface with technical AI internals.

---

# 23. Performance

This is a lightweight desktop application.

Prefer:

* lazy loading;
* streaming;
* quantized models;
* cached embeddings;
* cached project context;
* incremental retrieval;
* background processing.

Do not keep a large model loaded when GeoAI is unused if doing so materially harms application responsiveness.

---

# 24. Dependencies

Before adding a dependency:

1. Check whether the existing project already solves the problem.
2. Check package size.
3. Check offline compatibility.
4. Check platform compatibility.
5. Check maintenance status.
6. Ask whether the feature can be implemented simply without it.

Avoid dependency creep.

---

# 25. Testing

Every new GeoAI capability should have:

1. unit tests;
2. tool schema tests;
3. agent/tool integration tests where practical;
4. representative engineering examples.

Do not use the LLM itself as the only test oracle.

For numerical calculations, compare against deterministic expected results.

---

# 26. Development style

Prefer explicit, boring, maintainable code.

Avoid:

* magic routing;
* giant functions;
* hidden global state;
* implicit model behaviour;
* duplicated schemas;
* duplicated engineering calculations.

Use clear interfaces.

---

# 27. Existing functionality

Before replacing any existing GeoAI functionality, understand why it exists.

Existing heuristic routing may be useful as:

```text
fallback
```

but should not become the primary architecture if model-based tool selection is available.

Preserve working behaviour while migrating incrementally.

---

# 28. First milestone

The first working vertical slice must be:

```text
User:
"Calculate X using the current project."

        ↓

GeoAI

        ↓

Local model

        ↓

tool selection

        ↓

GeoCore Tool Registry

        ↓

Groundhog

        ↓

structured result

        ↓

GeoAI

        ↓

grounded answer
```

Do not implement the entire research system before this works.

---

# 29. Second milestone

Add:

```text
CPT retrieval
CPT interpretation
SPT retrieval
borehole retrieval
AGS-backed project context
```

Then test real project questions.

---

# 30. Third milestone

Add:

```text
local document retrieval
research
citations
evidence display
```

---

# 31. Fourth milestone

Build the model evaluation dataset.

Benchmark:

```text
Qwen
vs
Gemma
```

using identical:

* tools;
* prompts;
* context;
* test cases.

Choose based on GeoAI performance, not generic benchmark reputation.

---

# 32. Fifth milestone

Fine-tune the best candidate using LoRA/QLoRA.

Compare:

```text
base
vs
prompted base
vs
fine-tuned
```

Do not assume fine-tuning improves performance.

Keep the base model if it performs better.

---

# 33. Critical rule

When uncertain, prefer:

```text
ask
retrieve
calculate
cite
```

over:

```text
guess
invent
assume
```

GeoAI must be useful because it is grounded in GeoCore and engineering evidence.

---

# 34. Definition of done

A feature is complete only when:

* it works offline where intended;
* it integrates with existing GeoCore architecture;
* tools are validated;
* numerical calculations remain deterministic;
* relevant tests exist;
* errors are handled;
* the model receives appropriate context;
* the UI remains responsive;
* the feature does not unnecessarily increase application complexity.

The ultimate goal is:

> **GeoAI: a lightweight local geotechnical engineering and research assistant grounded in the user's project, GeoCore tools, Groundhog calculations, CPT/SPT/AGS data and verifiable evidence.**
