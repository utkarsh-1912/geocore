# GeoCore docs content (`website/_content/`)

Source content for the GeoCore documentation site. A docs layout renders these Markdown pages under `/docs/`.
Everything in `pages/`, `nav.json`, `search-index.json`, `build-info.json`, `groundhog/api.json` and
`groundhog/assets/` is **generated** by `extract_docs.py`. Edit `geocore/*.md` (GeoCore pages) or the extractor,
never the generated files.

## Re-running the extractor

```bash
# one-off: clone groundhog at the commit pinned in python-backend/requirements.txt (outside the repo)
git clone https://github.com/snakesonabrain/groundhog.git <tmp>/groundhog
git -C <tmp>/groundhog checkout dc7d554c6b8986bae30f518304546a911b1ca5ab

# from the repository root
python-backend/venv/Scripts/python.exe website/_content/extract_docs.py --groundhog-repo <tmp>/groundhog
```

- Without `--groundhog-repo` only the API reference (from the installed package), GeoCore pages (including
  the Changelog, which is hand-written, not upstream), section indexes and the licence page are built;
  guides, tutorials and figures are skipped.
- The run deletes and rebuilds `pages/` and `groundhog/assets/`, then verifies the output (every nav slug
  has a page, no orphan pages, front-matter parses with the required fields, internal links and image
  paths resolve). It exits with status 1 if verification fails.
- Output is deterministic: identical inputs give byte-identical files (no timestamps).
- Dependencies: standard library, PyYAML and groundhog, all present in `python-backend/venv`. No pandoc or
  docutils; the RST, docstring and notebook converters are built into the script.
- Tests: `python-backend/venv/Scripts/python.exe -m pytest website/_content/tests -q`

## Layout

```
website/_content/
  extract_docs.py            extractor (run this)
  geocore/*.md               hand-written GeoCore pages (source)
  pages/<slug>.md            generated pages, one per nav node
  nav.json                   navigation tree
  search-index.json          search index
  build-info.json            counts from the last run
  groundhog/api.json         structured API data (parsed docstrings, signatures, validator ranges)
  groundhog/assets/          figures copied from the groundhog repo + manifest.json (provenance)
  tests/                     pytest for the docstring parser
```

## `nav.json`

```json
{
  "home": {"title": "GeoCore Documentation", "slug": "index"},
  "sections": [
    {"title": "Getting Started", "slug": "getting-started", "children": [{"title": "...", "slug": "geocore/overview"}]},
    ...
  ]
}
```

Every node is `{title, slug, children?}`. Section nodes have landing pages too. Sections, in order:
Getting Started, Using GeoCore, GeoAI, Groundhog Guides (introduction, getting started, Topics > 10 area
pages, Tutorials > notebooks), Groundhog API Reference (package > sub-package > module, mirroring
`groundhog.*`), Changelog, License & Credits.

## Pages

`pages/<slug>.md` = YAML front-matter + Markdown body. Page URL = `/docs/<slug>`; `index` is `/docs/`.

Front-matter fields (always present unless noted):

| Field | Meaning |
|---|---|
| `title`, `slug`, `section`, `description` | Page identity. `section` is the nav section title. |
| `origin` | `groundhog` (derived from upstream) or `geocore`. |
| `source_url` | Upstream source: GitHub file at the groundhog tag, or the GeoCore source file. |
| `license` | `GPL-3.0-or-later` (groundhog) or `GPL-3.0` (GeoCore). |
| `author`, `attribution` | Author and a ready-to-print attribution sentence. |
| `groundhog_version` | groundhog version the content matches (`0.16.0`, the commit pinned in `python-backend/requirements.txt`). |
| `edited_by_geocore` | `true` when GeoCore converted/restructured upstream content. |
| `geocore_edit_note` | What was changed (upstream pages only). |
| `upstream_docs_url` / `upstream_docs_urls` | Matching readthedocs page(s), when known. |
| `module` | API pages: dotted module name. |
| `geocore_available`, `geocore_functions` | API pages: whether the module has calculators in the GeoCore UI, and their UI ids. |
| `notebook` | Tutorial pages: notebook path in the groundhog repo. |
| `sources` | GeoCore pages: repository files the page was written from. |

Body conventions:

- Links between pages are absolute: `/docs/<slug>` or `/docs/<slug>#<anchor>`.
- API anchors are explicit `<a id="..."></a>` before each heading; id = lower-cased qualname with `.` → `-`
  (`relativedensity_sand_jamiolkowski`, `pcptprocessing-load_pandas`).
- Math: inline `$...$`, display `$$...$$` (LaTeX from the docstrings; render with KaTeX or MathJax).
- "Available in GeoCore" badge: `<span class="gc-badge gc-available" data-geocore-function="<ui ids>">`
  followed by links into the calculation catalogue (`/docs/geocore/using/modules#<ui id lower-cased>`).
- Images use `/docs/assets/groundhog/<repo path>`; serve `groundhog/assets/` at `/docs/assets/groundhog/`.
- API pages: module intro, class/function list, then per item: signature, description (with formulas and
  figures in upstream order), **Parameters** table (Parameter, Unit, Suggested range, Default,
  Description), **Returns** table (Key, Unit, Description), Example, References, validation note.
  Missing upstream docs are shown as "No upstream documentation."

GeoCore pages may contain `<!-- geocore:generated <key> -->` markers that the extractor replaces
(`geoai-tools`, `eurocode7-factors`). The calculation catalogue (`geocore/using/modules`) is generated from
`electron-app/src/config/geotechnicalModules.js`, `python-backend/core/function_manifest.json` and the alias
table `UI_ALIASES` in the extractor (mirrors special cases in `python-backend/core/registry.py`).

## `search-index.json`

`[{slug, title, section, headings: [h2/h3 text], text: first ~300 characters of plain text}]`

## Counts (last run)

See `build-info.json`. At groundhog 0.16.0 (pinned commit): 45 API modules, 199 functions, 22 classes, 183 methods;
204 GeoCore calculators, all linked to their groundhog item; 32 upstream narrative pages (introduction,
getting started, 10 topic pages, 20 notebook tutorials); 16 GeoCore pages (15 hand-written, including the
Changelog, + generated catalogue). groundhog's own release history (`CHANGES.txt`) is not imported; the
Changelog page links to it upstream instead.

## Licensing

- groundhog (code and docs) is © Bruno Stuyts, GPL-3.0-or-later; the repository `LICENSE` is GPLv3 and
  `docs/` has no separate licence. GeoCore is GPL-3.0, so redistribution with attribution is permitted.
  The extractor checks the clone's `LICENSE` and skips all narrative content if it is not GPLv3.
- Each imported page carries source URL, author, licence, groundhog version and an edit note.
- Excluded (`EXCLUDED_UPSTREAM` in the extractor):
  - `docs/Golden_rules.rst` states a Creative Commons 4.0 BY-SA licence, conflicting with the repository's
    GPLv3; it is also not in the published toctree.
  - `notebooks/Images/cgs.png`: third-party organisation logo.
- `docs/tutorials/*.rst` are not imported because they only say the tutorials moved to the notebooks.
- Figures come only from the groundhog repository (`groundhog/assets/manifest.json` records source and
  pages using each). Several reproduce charts from the publications cited in the function docs.
- Only groundhog's own repo is used. External links in upstream text are kept as links.

## Conversion notes and gaps

- Docstrings are read from the source with `ast` (Python 3.13 dedents docstrings and expands tabs at
  compile time). LaTeX commands broken by non-raw docstrings (`\t`ext, `\f`rac, ...) are repaired.
- RST grid tables in docstrings are kept as preformatted text blocks.
- Notebook Markdown cells are kept, code cells become Python blocks, text and PNG outputs are reproduced;
  Plotly/HTML outputs are replaced by a note. Most upstream notebooks are stored without outputs.
- Upstream `automodule`/`autoclass` directives become links to the API pages. Topic pages keep the upstream
  toctree hierarchy.
- Readthedocs links point at `/en/main/`, which may be newer than the shipped groundhog; `source_url` pins the
  ref recorded in `groundhog/api.json` (`source_ref`: the installed commit, or `v<version>` for a release install).
