---
title: Local document search
slug: geoai/research
section: GeoAI
description: GeoAI's offline full-text index for project notes, reports and standards, and how evidence is kept separate.
origin: geocore
source_url: https://github.com/utkarsh-1912/geocore/blob/main/website/_content/geocore/geoai-research.md
license: GPL-3.0
author: Utkarsh Gupta
attribution: GeoCore documentation by Utkarsh Gupta, licensed under the GNU GPL v3.
groundhog_version: 0.15.0
edited_by_geocore: false
sources:
- python-backend/core/geoai/research/indexer.py
- python-backend/core/geoai/research/evidence.py
- python-backend/core/geoai/tool_definitions.py
- AGENTS.md
---

GeoAI includes a small, fully local search index for engineering text: project notes, report extracts, papers or standards you are allowed to use. It is meant to let GeoAI quote *your* documents instead of relying on the model's memory.

## How it works

- Text is split into chunks by heading and paragraph and stored in a SQLite database with an FTS5 full-text index (`geoai_research.db` in the GeoAI settings folder: `%APPDATA%\GeoCore` on Windows, `~/.geocore` elsewhere).
- Searches use BM25 keyword ranking. There is no vector database and no embedding model; nothing leaves your computer.
- Two tools expose the index to GeoAI:
  - `index_document_text` adds a document (id, title and text or Markdown) to the index;
  - `search_local_documents` returns the best-matching chunks with document title, section heading, file path and score.

There is currently no dedicated screen for managing indexed documents; documents are added through the `index_document_text` tool (for example with `POST /api/geoai/invoke`, see [GeoAI tools](/docs/geoai/tools#api-endpoints)).

## Keeping evidence types apart

GeoAI is instructed to distinguish between the kinds of evidence behind an answer and not to present a literature value as a project measurement:

| Evidence type | Example |
|---|---|
| Project evidence | A CPT or borehole from your project |
| Calculation evidence | A groundhog result produced by a tool |
| Literature evidence | A passage found in an indexed paper |
| Standards / guidance | A clause from an indexed standard |
| Model interpretation | GeoAI's own explanation |
| Assumption | A value you or GeoAI assumed |

GeoAI does not search the internet. If the index has no relevant passage, the answer cannot be backed by a source, and GeoAI is instructed to say so rather than invent a reference.
