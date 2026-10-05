# Author: Utkarsh Gupta
# License: GPL v3
"""
GeoCore documentation adaptor: the docs site content as structured, local GeoAI evidence.

The documentation under ``website/_content`` is generated deterministically from the Groundhog
docstrings that GeoCore ships (``groundhog/api.json``) plus the hand-written GeoCore pages
(``pages/**.md``). This module adapts that content for the backend without the website build:

* ``DocsAdapter.function_doc(name)``: one Groundhog function/class as structured data (summary,
  parameters with symbols, units and validated ranges, returns, formulas, references, source).
  Backs the ``get_function_documentation`` GeoAI tool, so the model reads the documented inputs,
  units and references instead of recalling them (AGENTS.md §5, §11).
* ``DocsAdapter.index_into(indexer)``: feeds every API entry and docs page into the local SQLite/FTS5
  research index (``research/indexer.py``) so ``search_local_documents`` can cite them. Incremental:
  nothing is re-indexed while the docs fingerprint is unchanged.
* ``coverage_report(...)``: which documented functions the desktop app, the backend registry and the
  GeoAI tool registry do (not) implement, grouped by Groundhog package folder.

Nothing here imports Groundhog or the website build scripts; it only reads JSON/Markdown.

Content location (first match wins): ``$GEOCORE_DOCS_DIR``; ``<bundle>/docs_content`` in a frozen
build (see main.spec); ``<repo>/website/_content`` in a source checkout. When none exists the adaptor
reports ``available() == False`` and every consumer degrades to "documentation not available".
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

import yaml

logger = logging.getLogger("groundhog-backend")

DOCS_DIR_ENV_VAR = "GEOCORE_DOCS_DIR"
DOC_ID_PREFIX = "geocore-docs:"
_FINGERPRINT_DOC_ID = DOC_ID_PREFIX + "__fingerprint__"
_GH_REPO_URL = "https://github.com/snakesonabrain/groundhog"

_FIGURE = re.compile(r"%%FIGURE:\d+%%")
_HTML_TAG = re.compile(r"<[^>]+>")
_MD_IMAGE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
_FRONT_MATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class ParamDoc:
    name: str
    description: str = ""
    symbol: str = ""
    unit: str = ""
    range: str = ""
    required: bool = True
    default: Optional[str] = None


@dataclass
class ReturnDoc:
    key: str
    description: str = ""
    unit: str = ""


@dataclass
class FunctionDoc:
    """One documented Groundhog function or class (from the shipped docstrings)."""
    name: str
    qualname: str
    module: str
    kind: str                      # "function" | "class"
    folder: str                    # Groundhog package folder, e.g. "siteinvestigation/insitutests"
    signature: str
    summary: str
    description: str
    params: List[ParamDoc] = field(default_factory=list)
    returns: List[ReturnDoc] = field(default_factory=list)
    returns_note: str = ""
    formulas: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    validated: bool = False
    docs_url: str = ""             # site-relative docs URL with anchor
    source_url: str = ""           # upstream source pinned to the shipped Groundhog version

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DocsPage:
    """One page of the docs site (front-matter + Markdown body)."""
    slug: str
    title: str
    section: str
    origin: str                    # "groundhog" | "geocore"
    body: str
    url: str
    source_url: str = ""
    license: str = ""
    attribution: str = ""


# ---------------------------------------------------------------------------
# Location
# ---------------------------------------------------------------------------

def default_content_dir() -> Optional[Path]:
    """The docs content directory, or None when this install has no documentation."""
    candidates: List[Path] = []
    override = os.environ.get(DOCS_DIR_ENV_VAR)
    if override:
        candidates.append(Path(override))
    bundle = getattr(sys, "_MEIPASS", None)
    if bundle:
        candidates.append(Path(bundle) / "docs_content")
    # core/geoai/research/docs_adapter.py -> repository root is parents[4]
    candidates.append(Path(__file__).resolve().parents[4] / "website" / "_content")
    for path in candidates:
        if (path / "groundhog" / "api.json").is_file():
            return path
    return None


def _module_folder(module: str) -> str:
    """groundhog.siteinvestigation.insitutests.pcpt_correlations -> siteinvestigation/insitutests."""
    parts = module.split(".")[1:-1]
    return "/".join(parts) or module.split(".")[-1]


def _module_slug(module: str) -> str:
    """Docs slug for an API module page (mirrors extract_docs.module_slug)."""
    return "groundhog/api/" + "/".join(module.split(".")[1:])


def _plain(md: str) -> str:
    """Markdown/HTML -> plain text good enough for FTS indexing and model context."""
    text = _FIGURE.sub("", md or "")
    text = _MD_IMAGE.sub(r"\1", text)
    text = _HTML_TAG.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


# ---------------------------------------------------------------------------
# Adaptor
# ---------------------------------------------------------------------------

class DocsAdapter:
    """Read-only view of the GeoCore/Groundhog documentation content."""

    def __init__(self, content_dir: Optional[Path] = None):
        self.content_dir = Path(content_dir) if content_dir else default_content_dir()
        self._api: Optional[Dict[str, Any]] = None
        self._by_name: Optional[Dict[str, Tuple[Dict[str, Any], Dict[str, Any]]]] = None
        self._indexed: set = set()

    # -- loading ------------------------------------------------------------

    def available(self) -> bool:
        return self.content_dir is not None and (self.content_dir / "groundhog" / "api.json").is_file()

    @property
    def api_path(self) -> Optional[Path]:
        return self.content_dir / "groundhog" / "api.json" if self.content_dir else None

    def _load_api(self) -> Dict[str, Any]:
        if self._api is None:
            if not self.available():
                self._api = {"modules": []}
            else:
                self._api = json.loads(self.api_path.read_text(encoding="utf-8"))
        return self._api

    def _index(self) -> Dict[str, Tuple[Dict[str, Any], Dict[str, Any]]]:
        if self._by_name is None:
            self._by_name = {}
            for mod in self._load_api().get("modules", []):
                for member in mod.get("members", []):
                    self._by_name.setdefault(member["qualname"], (mod, member))
        return self._by_name

    @property
    def groundhog_version(self) -> str:
        return str(self._load_api().get("groundhog_version", "unknown"))

    @property
    def license(self) -> str:
        return str(self._load_api().get("license", ""))

    @property
    def attribution(self) -> str:
        api = self._load_api()
        if not api.get("modules"):
            return ""
        return (f"Adapted from the groundhog {self.groundhog_version} docstrings by {api.get('author', '')} "
                f"({_GH_REPO_URL}), {api.get('license', '')}.")

    def fingerprint(self) -> str:
        """Changes whenever the docs content changes (api.json bytes + page sizes/mtimes)."""
        if not self.available():
            return ""
        h = hashlib.sha256(self.api_path.read_bytes())
        pages = self.content_dir / "pages"
        if pages.is_dir():
            for p in sorted(pages.rglob("*.md")):
                st = p.stat()
                h.update(f"{p.relative_to(pages).as_posix()}:{st.st_size}:{int(st.st_mtime)}".encode())
        return h.hexdigest()

    # -- API reference ------------------------------------------------------

    def function_names(self) -> List[str]:
        return sorted(self._index())

    def iter_functions(self) -> Iterator[FunctionDoc]:
        for name in self.function_names():
            doc = self.function_doc(name)
            if doc is not None:
                yield doc

    def function_doc(self, name: str) -> Optional[FunctionDoc]:
        """Structured docs for a Groundhog function/class by name, or None if undocumented.

        Accepts ``Class.method`` too; the class entry is returned with the method's docs merged in.
        """
        head, _, method = (name or "").strip().partition(".")
        hit = self._index().get(head)
        if hit is None:
            return None
        mod, member = hit
        doc_src = member
        if method:
            doc_src = next((m for m in member.get("methods", []) if m.get("name") == method), None)
            if doc_src is None:
                return None
        return self._build_function_doc(mod, member, doc_src)

    def _build_function_doc(self, mod: Dict[str, Any], member: Dict[str, Any],
                            src: Dict[str, Any]) -> FunctionDoc:
        doc = src.get("doc", {})
        # Classes take their inputs through __init__ and the workflow methods (set_*, calculate_*);
        # merge them, first documented occurrence of a name wins (as in website/_build/app_docs.py).
        param_sources = [src]
        if src is member:
            param_sources += ([member["init"]] if member.get("init") else []) + list(member.get("methods", []))
        defaults: Dict[str, Dict[str, Any]] = {}
        validation: Dict[str, Any] = {}
        for ps in param_sources:
            for p in ps.get("signature_params", []):
                defaults.setdefault(p["name"], p)
            for k, v in (ps.get("validation") or {}).items():
                validation.setdefault(k, v)
        params: List[ParamDoc] = []
        seen = set()
        for ps in param_sources:
            for p in ps.get("doc", {}).get("params", []):
                pname = p["name"]
                if pname.startswith("*") or pname in ("args", "kwargs") or pname in seen:
                    continue
                seen.add(pname)
                sig = defaults.get(pname, {})
                rng = p.get("range") or ""
                if not rng and pname in validation:
                    v = validation[pname]
                    lo, hi = v.get("min_value"), v.get("max_value")
                    if lo is not None and hi is not None:
                        rng = f"{lo} <= {pname} <= {hi}"
                    elif lo is not None:
                        rng = f"{pname} >= {lo}"
                    elif hi is not None:
                        rng = f"{pname} <= {hi}"
                params.append(ParamDoc(
                    name=pname,
                    description=p.get("description") or "",
                    symbol=p.get("symbol") or "",
                    unit=p.get("unit") or "",
                    range=rng,
                    required=bool(sig.get("required", not p.get("optional", False))),
                    default=sig.get("default"),
                ))
        ret = doc.get("returns") or {}
        returns = [ReturnDoc(key=i.get("key", ""), description=i.get("description") or "", unit=i.get("unit") or "")
                   for i in ret.get("items", [])]
        anchor = src.get("anchor") or member.get("anchor") or member["qualname"]
        line = src.get("line") or member.get("line") or 1
        return FunctionDoc(
            name=member["name"] if src is member else f"{member['name']}.{src['name']}",
            qualname=src.get("qualname", member["qualname"]),
            module=mod["module"],
            kind=member["kind"] if src is member else "method",
            folder=_module_folder(mod["module"]),
            signature=src.get("signature", ""),
            summary=doc.get("summary", ""),
            description=_plain(doc.get("description_md", "")),
            params=params,
            returns=returns,
            returns_note=(ret.get("description") or "") if not returns else "",
            formulas=list(doc.get("formulas", [])),
            references=list(doc.get("references", [])),
            methods=[m["name"] for m in member.get("methods", [])] if src is member else [],
            validated=bool(src.get("validated")),
            docs_url=f"/docs/{_module_slug(mod['module'])}/#{anchor}",
            source_url=(f"{_GH_REPO_URL}/blob/v{self.groundhog_version}/{mod.get('source_path', '')}#L{line}"
                        if mod.get("source_path") else ""),
        )

    # -- pages --------------------------------------------------------------

    def iter_pages(self) -> Iterator[DocsPage]:
        """Every docs page, API module pages excluded (those are covered per function)."""
        if not self.content_dir:
            return
        pages_dir = self.content_dir / "pages"
        if not pages_dir.is_dir():
            return
        for path in sorted(pages_dir.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            m = _FRONT_MATTER.match(text)
            meta: Dict[str, Any] = {}
            if m:
                try:
                    meta = yaml.safe_load(m.group(1)) or {}
                except yaml.YAMLError:
                    meta = {}
                text = text[m.end():]
            slug = str(meta.get("slug") or path.relative_to(pages_dir).with_suffix("").as_posix())
            if meta.get("module"):
                continue
            yield DocsPage(
                slug=slug,
                title=str(meta.get("title") or slug),
                section=str(meta.get("section") or ""),
                origin=str(meta.get("origin") or ""),
                body=_plain(text),
                url="/docs/" if slug == "index" else f"/docs/{slug}/",
                source_url=str(meta.get("source_url") or ""),
                license=str(meta.get("license") or ""),
                attribution=str(meta.get("attribution") or ""),
            )

    # -- research index -----------------------------------------------------

    @staticmethod
    def function_markdown(fd: FunctionDoc) -> str:
        """Compact Markdown for one function, as indexed for search."""
        lines = [f"# {fd.name}", f"Module: {fd.module}", "", fd.summary, "", fd.description]
        if fd.params:
            lines += ["", "## Parameters"]
            for p in fd.params:
                unit = f" [{p.unit}]" if p.unit else ""
                rng = f" (range {p.range})" if p.range else ""
                lines.append(f"- {p.name}{unit}: {p.description}{rng}")
        if fd.returns:
            lines += ["", "## Returns"] + [f"- {r.key}: {r.description}" for r in fd.returns]
        if fd.references:
            lines += ["", "## References"] + [f"- {r}" for r in fd.references]
        return "\n".join(lines)

    def index_into(self, indexer: Any, force: bool = False) -> Dict[str, Any]:
        """Index API entries and pages into a ``LocalDocumentIndexer``; skipped when unchanged.

        Each document's ``file_path`` is its docs URL, so search results point at the source.
        """
        if not self.available():
            return {"status": "unavailable", "functions": 0, "pages": 0}
        fingerprint = self.fingerprint()
        if not force and indexer.get_document_hash(_FINGERPRINT_DOC_ID) == fingerprint:
            return {"status": "up_to_date", "functions": 0, "pages": 0}

        docs = [(f"{DOC_ID_PREFIX}api:{fd.qualname}", f"Groundhog {fd.name} ({fd.module})",
                 self.function_markdown(fd), fd.docs_url) for fd in self.iter_functions()]
        n_func = len(docs)
        docs += [(f"{DOC_ID_PREFIX}page:{p.slug}", f"GeoCore Docs: {p.title}", p.body, p.url)
                 for p in self.iter_pages() if p.body.strip()]
        n_page = len(docs) - n_func
        indexer.delete_documents_with_prefix(DOC_ID_PREFIX)
        indexer.index_new_documents(docs)
        indexer.set_document_marker(_FINGERPRINT_DOC_ID, "GeoCore documentation fingerprint", fingerprint)
        logger.info("GeoAI: indexed GeoCore docs (%d functions, %d pages)", n_func, n_page)
        return {"status": "indexed", "functions": n_func, "pages": n_page}

    def ensure_indexed(self, indexer: Any) -> None:
        """``index_into`` at most once per index per process; failures are logged, never raised."""
        key = str(getattr(indexer, "db_path", id(indexer)))
        if key in self._indexed:
            return
        try:
            self.index_into(indexer)
        except Exception as e:  # the search must still work on the user's own documents
            logger.warning("GeoAI: could not index GeoCore docs: %s", e)
        self._indexed.add(key)


# ---------------------------------------------------------------------------
# Coverage: documented functions vs. what the app implements
# ---------------------------------------------------------------------------

@dataclass
class CoverageRow:
    name: str
    module: str
    folder: str
    kind: str
    summary: str
    in_backend: bool               # callable through core.registry (POST /api/execute)
    in_desktop_ui: bool            # has a calculator in electron-app geotechnicalModules.js
    geoai_tool: bool               # offered to the SLM through the GeoAI tool registry
    geoai_note: str = ""           # why it is not a GeoAI tool, when known


def coverage_report(adapter: DocsAdapter,
                    backend_targets: Iterable[Tuple[str, str]],
                    ui_targets: Iterable[Tuple[str, str]],
                    geoai_exclusions: Dict[str, str],
                    geoai_skipped: Optional[Dict[str, str]] = None) -> List[CoverageRow]:
    """Every documented Groundhog function/class with its implementation status in GeoCore.

    ``backend_targets``/``ui_targets`` are ``(module, qualname)`` pairs; a UI target on a class method
    (``Class.method``) counts for the class. ``geoai_exclusions`` maps function name -> reason it is
    hidden from the model (``exposure_policy``); ``geoai_skipped`` adds schema-generation failures.
    """
    backend = {(m, q.split(".")[0]) for m, q in backend_targets}
    ui = {(m, q.split(".")[0]) for m, q in ui_targets}
    skipped = geoai_skipped or {}
    rows: List[CoverageRow] = []
    for fd in adapter.iter_functions():
        key = (fd.module, fd.qualname)
        in_backend = key in backend
        note = geoai_exclusions.get(fd.name) or skipped.get(fd.name) or ""
        if not in_backend:
            note = note or "not in the backend registry"
        rows.append(CoverageRow(
            name=fd.name, module=fd.module, folder=fd.folder, kind=fd.kind, summary=fd.summary,
            in_backend=in_backend, in_desktop_ui=key in ui,
            geoai_tool=in_backend and not note, geoai_note=note,
        ))
    return sorted(rows, key=lambda r: (r.folder, r.module, r.name))


def coverage_markdown(rows: List[CoverageRow], groundhog_version: str) -> str:
    """Render the 'functions not implemented in the app' report, grouped by folder."""
    by_folder: Dict[str, List[CoverageRow]] = {}
    for r in rows:
        by_folder.setdefault(r.folder, []).append(r)

    def count(pred) -> int:
        return sum(1 for r in rows if pred(r))

    out = [
        "# Groundhog function coverage in GeoCore",
        "",
        f"Generated by `python -m core.geoai.research.docs_adapter --coverage` from the shipped documentation "
        f"(groundhog {groundhog_version}, `website/_content/groundhog/api.json`). Do not edit by hand.",
        "",
        "Columns: **Backend** = callable through the calculation engine (`core.registry`, `POST /api/execute`); "
        "**Desktop UI** = has a calculator in `electron-app/src/config/geotechnicalModules.js`; "
        "**GeoAI** = offered to the local model as a tool (`core/geoai/exposure_policy.py`).",
        "",
        "## Summary",
        "",
        "| Folder | Documented | Backend | Desktop UI | GeoAI tool |",
        "|---|---:|---:|---:|---:|",
    ]
    for folder, frs in sorted(by_folder.items()):
        out.append(f"| `{folder}` | {len(frs)} | {sum(r.in_backend for r in frs)} | "
                   f"{sum(r.in_desktop_ui for r in frs)} | {sum(r.geoai_tool for r in frs)} |")
    out.append(f"| **Total** | **{len(rows)}** | **{count(lambda r: r.in_backend)}** | "
               f"**{count(lambda r: r.in_desktop_ui)}** | **{count(lambda r: r.geoai_tool)}** |")

    def section(title: str, intro: str, pred, with_note: bool) -> None:
        out.extend(["", f"## {title}", "", intro, ""])
        hits = [r for r in rows if pred(r)]
        if not hits:
            out.append("None.")
            return
        current = None
        for r in hits:
            if r.folder != current:
                current = r.folder
                out.extend(["", f"### `{current}`", ""])
                out.append("| Function | Module | Kind | Summary |" + (" Reason |" if with_note else ""))
                out.append("|---|---|---|---|" + ("---|" if with_note else ""))
            summary = (r.summary or "").replace("|", "\\|")
            row = f"| `{r.name}` | `{r.module.split('.')[-1]}` | {r.kind} | {summary} |"
            if with_note:
                row += f" {r.geoai_note.replace('|', '/')} |"
            out.append(row)

    section("Not implemented in the backend",
            "Documented Groundhog functions the calculation engine cannot run.",
            lambda r: not r.in_backend, False)
    section("Not available in the desktop UI",
            "Documented functions with no calculator in the GeoCore desktop app.",
            lambda r: not r.in_desktop_ui, False)
    section("Not available to GeoAI",
            "Documented functions the local model cannot call, with the reason from the exposure policy.",
            lambda r: not r.geoai_tool, True)
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# Default instance and CLI
# ---------------------------------------------------------------------------

_default: Optional[DocsAdapter] = None


def get_docs_adapter() -> DocsAdapter:
    """Process-wide adaptor (api.json is parsed once, on first use)."""
    global _default
    if _default is None:
        _default = DocsAdapter()
    return _default


def _ui_targets_from_repo(repo_root: Path) -> List[Tuple[str, str]]:
    """Desktop calculators -> Groundhog targets, using the same mapping as the docs build."""
    sys.path.insert(0, str(repo_root / "website" / "_content"))
    import extract_docs  # dev-only: the website build's own parser for geotechnicalModules.js
    return [tuple(t) for t in extract_docs.load_geocore_ui()["by_target"]]


def _main(argv: Optional[List[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--coverage", action="store_true",
                        help="write the 'functions not implemented in the app' report")
    parser.add_argument("--out", default=None, help="report path (default: <repo>/FUNCTION_COVERAGE.md)")
    parser.add_argument("--index", action="store_true", help="(re)index the docs into the local research index")
    args = parser.parse_args(argv)

    adapter = get_docs_adapter()
    if not adapter.available():
        print("GeoCore documentation content not found (set GEOCORE_DOCS_DIR).", file=sys.stderr)
        return 1
    repo_root = Path(__file__).resolve().parents[4]

    if args.index:
        from core.geoai.research.indexer import local_indexer
        print(adapter.index_into(local_indexer, force=True))

    if args.coverage:
        from core.function_manifest import MANIFEST_PATH
        from core.geoai.exposure_policy import exclusion_reason
        manifest = json.loads(Path(MANIFEST_PATH).read_text(encoding="utf-8"))
        backend = [(f["module"], f["qualname"]) for f in manifest.get("functions", [])]
        exclusions = {}
        for fd in adapter.iter_functions():
            reason = exclusion_reason(fd.name, fd.module)
            if reason:
                exclusions[fd.name] = reason
        rows = coverage_report(adapter, backend, _ui_targets_from_repo(repo_root), exclusions)
        out = Path(args.out) if args.out else repo_root / "FUNCTION_COVERAGE.md"
        out.write_text(coverage_markdown(rows, adapter.groundhog_version), encoding="utf-8")
        print(f"wrote {out} ({sum(not r.in_desktop_ui for r in rows)} documented functions without a desktop "
              f"calculator, {sum(not r.geoai_tool for r in rows)} not available to GeoAI)")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
