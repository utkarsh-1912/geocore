"""
GeoCore website static generator.

Renders the Jinja2 templates in ``website/_templates`` into plain HTML files in
``website/`` (which Netlify publishes as-is). No runtime framework is involved;
the output is committed so the host never has to run a build.

Usage (from the repository root)::

    python-backend/venv/Scripts/python.exe website/_build/build.py

Facts shown on the site that come from the code base are read here, at build
time, so the copy cannot drift from the application:

* calculation counts per Groundhog domain  <- python-backend/core/function_manifest.json
* GeoAI model catalogue                    <- python-backend/core/geoai/model_downloader.py
* application version                      <- electron-app/package.json

Each source has a fallback snapshot so the site still builds if a file moves.

Author: Utkarsh Gupta
License: GPL v3
"""
from __future__ import annotations

import ast
import datetime as _dt
import hashlib
import json
import posixpath
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
except ImportError:  # pragma: no cover - guidance for first-time users
    sys.exit("Jinja2 is required: pip install jinja2 (it is already in python-backend/requirements.txt)")

WEBSITE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import docs_content  # noqa: E402
REPO = WEBSITE.parent
TEMPLATES = WEBSITE / "_templates"
DATA = WEBSITE / "_data"

REPO_URL = "https://github.com/utkarsh-1912/geocore"
RELEASES_URL = REPO_URL + "/releases"
LAST_UPDATED_PRIVACY = "2026-09-27"

# ---------------------------------------------------------------------------
# Groundhog domains (human-written copy; counts are computed from the manifest)
# ---------------------------------------------------------------------------

DOMAINS: List[Dict[str, Any]] = [
    {
        "key": "siteinvestigation", "title": "Site investigation & in-situ testing", "icon": "cpt",
        "summary": "CPT and SPT processing, soil classification, phase relations, lab testing and parameter correlations.",
        "examples": ["PCPT normalisation & Robertson (Ic) classification", "SPT N60 and overburden corrections",
                     "Shear-wave velocity from CPT (7 correlations)", "PSD and plasticity charts"],
    },
    {
        "key": "soildynamics", "title": "Soil dynamics & liquefaction", "icon": "waves",
        "summary": "CPT-based liquefaction triggering, cyclic behaviour of clays and sands, and small-strain stiffness.",
        "examples": ["Robertson & Wride (1998), Idriss & Boulanger (2008), Boulanger & Idriss (2014), Robertson & Cabal (2022)",
                     "Andersen cyclic contour diagrams (DSS, triaxial)", "Darendeli modulus reduction"],
    },
    {
        "key": "shallowfoundations", "title": "Shallow foundations", "icon": "layers",
        "summary": "Drained and undrained capacity, sliding, bearing capacity factors, stress distribution and settlement.",
        "examples": ["Vertical and sliding capacity (API)", "N-gamma: Meyerhof, Vesic, Davis & Booker",
                     "Stresses under point, strip, rectangular and circular loads"],
    },
    {
        "key": "deepfoundations", "title": "Deep foundations", "icon": "pile",
        "summary": "Axial pile capacity from CPT and unit resistance methods, load testing and pile groups.",
        "examples": ["LCPC, Koppejan and De Beer methods", "API RP 2GEO and Alm & Hamre unit friction / end bearing",
                     "Negative skin friction (Zeevaert–De Beer)", "Chin–Kondler load-test extrapolation"],
    },
    {
        "key": "general", "title": "Soil profiles, AGS & utilities", "icon": "database",
        "summary": "SoilProfile objects, calculation grids, log plots, AGS conversion and input validation.",
        "examples": ["SoilProfile and CalculationGrid", "AGS 3.1 / 4 conversion", "LogPlot depth plots"],
    },
    {
        "key": "pipelinescables", "title": "Pipelines & cables", "icon": "anchor",
        "summary": "On-bottom stability inputs for subsea pipelines and cables.",
        "examples": ["Drained and undrained embedment", "Contact width and penetrated area", "Lay touchdown factor"],
    },
    {
        "key": "excavations", "title": "Excavations & retaining", "icon": "trench",
        "summary": "Earth pressure coefficients and soil-mix wall stiffness.",
        "examples": ["Rankine and Poncelet coefficients", "Soil-mix bending stiffness (two methods)"],
    },
    {
        "key": "consolidation", "title": "Consolidation & groundwater", "icon": "droplets",
        "summary": "One-dimensional consolidation and groundwater flow.",
        "examples": ["Finite-difference 1D consolidation", "Degree of consolidation", "Unconfined aquifer conductivity"],
    },
    {
        "key": "constitutivemodels", "title": "Constitutive models", "icon": "curve",
        "summary": "Element-level constitutive behaviour.",
        "examples": ["Mohr–Coulomb triaxial compression / extension", "Hardening Soil"],
    },
    {
        "key": "standards", "title": "Standards (Eurocode 7)", "icon": "ruler",
        "summary": "Characteristic values and partial factoring according to Eurocode 7.",
        "examples": ["STR/GEO partial factors", "Characteristic values: constant value and linear trend"],
    },
]

# Snapshot used only if function_manifest.json cannot be read (220 functions, Groundhog 0.15.0).
_FALLBACK_COUNTS = {
    "siteinvestigation": 86, "soildynamics": 40, "general": 27, "shallowfoundations": 26,
    "deepfoundations": 20, "pipelinescables": 6, "excavations": 5, "consolidation": 4,
    "constitutivemodels": 3, "standards": 3,
}

_FALLBACK_MODELS = [
    {"id": "qwen2.5-1.5b-instruct", "family": "qwen", "display_name": "Qwen 2.5 (1.5B Instruct)",
     "repo_id": "Qwen/Qwen2.5-1.5B-Instruct-GGUF", "size_mb": 986},
    {"id": "qwen2.5-3b-instruct", "family": "qwen", "display_name": "Qwen 2.5 (3B Instruct)",
     "repo_id": "Qwen/Qwen2.5-3B-Instruct-GGUF", "size_mb": 2040},
    {"id": "qwen2.5-7b-instruct", "family": "qwen", "display_name": "Qwen 2.5 (7B Instruct)",
     "repo_id": "Qwen/Qwen2.5-7B-Instruct-GGUF", "size_mb": 4400},
    {"id": "gemma-2-2b-it", "family": "gemma", "display_name": "Gemma 2 (2.6B IT)",
     "repo_id": "bartowski/gemma-2-2b-it-GGUF", "size_mb": 1630},
    {"id": "gemma-2-9b-it", "family": "gemma", "display_name": "Gemma 2 (9B IT)",
     "repo_id": "bartowski/gemma-2-9b-it-GGUF", "size_mb": 5400},
]


def _warn(msg: str) -> None:
    print(f"  warning: {msg}", file=sys.stderr)


def load_function_counts() -> Dict[str, Any]:
    """Count exposed Groundhog functions per top-level Groundhog package."""
    path = REPO / "python-backend" / "core" / "function_manifest.json"
    try:
        functions = json.loads(path.read_text(encoding="utf-8"))["functions"]
        counts: Dict[str, int] = {}
        for fn in functions:
            parts = str(fn.get("module", "")).split(".")
            if len(parts) > 1 and parts[0] == "groundhog":
                counts[parts[1]] = counts.get(parts[1], 0) + 1
        return {"counts": counts, "total": len(functions), "source": "function_manifest.json"}
    except (OSError, KeyError, ValueError) as exc:
        _warn(f"could not read {path} ({exc}); using snapshot counts")
        return {"counts": dict(_FALLBACK_COUNTS), "total": sum(_FALLBACK_COUNTS.values()), "source": "snapshot"}


def load_models() -> List[Dict[str, Any]]:
    """Read RECOMMENDED_MODELS from model_downloader.py without importing it."""
    path = REPO / "python-backend" / "core" / "geoai" / "model_downloader.py"
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            target = None
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                target, value = node.target.id, node.value
            elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                target, value = node.targets[0].id, node.value
            if target == "RECOMMENDED_MODELS" and value is not None:
                registry = ast.literal_eval(value)
                return [
                    {"id": key, "family": info.get("family", ""), "display_name": info.get("display_name", key),
                     "repo_id": info["repo_id"], "size_mb": info.get("size_mb", 0)}
                    for key, info in registry.items()
                ]
        raise ValueError("RECOMMENDED_MODELS not found")
    except (OSError, ValueError, SyntaxError, KeyError) as exc:
        _warn(f"could not read model catalogue from {path} ({exc}); using snapshot")
        return list(_FALLBACK_MODELS)


def load_app_version() -> str:
    try:
        return json.loads((REPO / "electron-app" / "package.json").read_text(encoding="utf-8"))["version"]
    except (OSError, KeyError, ValueError):
        return ""


def load_json(name: str, default: Any) -> Any:
    path = DATA / name
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

_hash_cache: Dict[str, str] = {}


def asset_version(rel_path: str) -> str:
    """Short content hash for cache-busting (?v=...)."""
    if rel_path not in _hash_cache:
        file = WEBSITE / rel_path
        _hash_cache[rel_path] = hashlib.sha256(file.read_bytes()).hexdigest()[:10] if file.exists() else "0"
    return _hash_cache[rel_path]


def make_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.filters["mb"] = lambda v: f"{float(v) / 1024:.1f} GB" if float(v) >= 1000 else f"{int(v)} MB"
    return env


def rel_root(out_path: str) -> str:
    """Relative prefix from an output page back to the site root ('' or '../')."""
    depth = out_path.count("/")
    return "../" * depth


def render(env: Environment, template: str, out_path: str, context: Dict[str, Any],
           absolute: bool = False) -> Path:
    # 404.html is served for missing URLs at any depth, so it must use root-absolute links.
    root = "/" if absolute else rel_root(out_path)

    def url(path: str) -> str:
        """Site-root-relative path -> link relative to the current page."""
        if re.match(r"^[a-z]+:|^#|^//", path):
            return path
        return root + path.lstrip("/") if root or path else "./"

    def asset(path: str) -> str:
        return f"{url(path)}?v={asset_version(path)}"

    def icon(name: str, cls: str = "icon", label: Optional[str] = None) -> str:
        from markupsafe import Markup
        aria = f' role="img" aria-label="{label}"' if label else ' aria-hidden="true" focusable="false"'
        return Markup(f'<svg class="{cls}"{aria}><use href="{asset("assets/icons.svg")}#i-{name}"></use></svg>')

    ctx = dict(context)
    ctx.update(root=root, url=url, asset=asset, icon=icon, page_path=out_path)
    html = env.get_template(template).render(**ctx)
    target = WEBSITE / out_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8", newline="\n")
    return target


# ---------------------------------------------------------------------------
# Docs helpers (contract documented in website/README.md)
# ---------------------------------------------------------------------------

def is_docs_url(url: Optional[str]) -> bool:
    return bool(url) and url.startswith("docs/") and not url.endswith(".json")


def flatten_nav(nav: Iterable[Dict[str, Any]], trail: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Depth-first list of nav nodes that are docs pages (url under docs/), each with its breadcrumb trail.

    Links to other site pages or external sites are shown in the sidebar but are
    not part of the prev/next reading order or the breadcrumb chain.
    """
    out: List[Dict[str, Any]] = []
    trail = trail or []
    for node in nav:
        url = node.get("url")
        crumb = {"title": node["title"], "url": url if is_docs_url(url) else None}
        if is_docs_url(url) and not node.get("external"):
            out.append({"title": node["title"], "url": url, "trail": trail + [crumb]})
        out.extend(flatten_nav(node.get("children", []), trail + [crumb]))
    return out


NAV_NODE_DEFAULTS = {"url": None, "children": [], "status": None, "external": False,
                     "slug": None, "icon": None, "summary": None, "key": None}
PAGE_DEFAULTS = {"description": None, "body_html": "", "toc": [], "source": None, "updated": None,
                 "title_html": None, "has_math": False, "meta": None}


def normalize_nav(nav: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Give every nav node all optional keys (templates render with StrictUndefined)."""
    out = []
    for node in nav:
        if "title" not in node:
            raise ValueError(f"docs nav node without a title: {node}")
        n = dict(NAV_NODE_DEFAULTS, **node)
        if not n["slug"]:
            n["slug"] = re.sub(r"[^a-z0-9]+", "-", n["title"].lower()).strip("-")
        n["children"] = normalize_nav(n["children"] or [])
        out.append(n)
    return out


def docs_page_context(page: Dict[str, Any], nav: List[Dict[str, Any]],
                      ordered: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Fill in defaults, breadcrumbs, prev/next and the nav trail for a docs page from the nav tree."""
    ordered = ordered if ordered is not None else flatten_nav(nav)
    urls = [n["url"] for n in ordered]
    page = dict(PAGE_DEFAULTS, **page)
    if "url" not in page or "title" not in page:
        raise ValueError("docs page needs at least 'title' and 'url'")
    if page["url"] in urls:
        i = urls.index(page["url"])
        trail = ordered[i]["trail"]
        page.setdefault("breadcrumbs", [{"title": "Docs", "url": "docs/"}] + trail[:-1])
        page.setdefault("prev", {"title": ordered[i - 1]["title"], "url": ordered[i - 1]["url"]} if i > 0 else None)
        page.setdefault("next", {"title": ordered[i + 1]["title"], "url": ordered[i + 1]["url"]} if i + 1 < len(ordered) else None)
        page.setdefault("trail_urls", [c["url"] for c in trail if c["url"]])
    else:
        page.setdefault("breadcrumbs", [{"title": "Docs", "url": "docs/"}])
        page.setdefault("prev", None)
        page.setdefault("next", None)
        page.setdefault("trail_urls", [])
    return page


def docs_out_path(url: str) -> str:
    """'docs/x/' -> 'docs/x/index.html' (pretty URL); explicit .html paths are used as-is."""
    return url + "index.html" if url.endswith("/") else url


def render_docs_page(env: Environment, page: Dict[str, Any], nav: List[Dict[str, Any]],
                     base_context: Dict[str, Any], template: str = "docs_page.html",
                     ordered: Optional[List[Dict[str, Any]]] = None) -> Path:
    """Render one docs page. ``page['url']`` is its site-root-relative URL, e.g. 'docs/groundhog/api/'.

    Docs pages use root-absolute links ('/docs/...') so they work whether or not the host
    adds a trailing slash to the pretty URL.
    """
    ctx = dict(base_context)
    ctx.update(page=docs_page_context(page, nav, ordered), docs_nav=nav)
    return render(env, template, docs_out_path(page["url"]), ctx, absolute=True)


def write_search_index(entries: List[Dict[str, Any]]) -> Path:
    index = {
        "version": 1,
        "generated": _dt.date.today().isoformat(),
        "docs": entries,
    }
    target = WEBSITE / "docs" / "search-index.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    return target


def seed_search_entries(domains: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Search entries for the marketing pages and calculation domains."""
    entries = [
        {"id": "download", "title": "Download GeoCore", "url": "download.html", "section": "Site",
         "summary": "Installers for Windows and macOS, system requirements, installation and GeoAI models.",
         "headings": ["System requirements", "Install on Windows", "Install on macOS", "GeoAI models"],
         "body": "SmartScreen Gatekeeper installer dmg exe arm64 x64 RAM GGUF Hugging Face auto-update"},
        {"id": "privacy", "title": "Privacy", "url": "privacy.html", "section": "Site",
         "summary": "Every network request GeoCore makes, and what is stored on your computer.",
         "headings": ["Network activity", "Data stored on your computer", "This website"],
         "body": "telemetry update check GitHub Hugging Face fonts APPDATA local storage Netlify"},
        {"id": "about", "title": "About GeoCore", "url": "about.html", "section": "Site",
         "summary": "Mission, architecture, license and credits (Groundhog by Bruno Stuyts).",
         "headings": ["Principles", "How it is built", "Open source", "Credits"],
         "body": "GPLv3 Groundhog Bruno Stuyts Electron React FastAPI llama.cpp"},
    ]
    for d in domains:
        entries.append({
            "id": f"domain-{d['key']}", "title": d["title"], "url": f"index.html#domain-{d['key']}",
            "section": "Calculations",
            "summary": d["summary"], "headings": d["examples"], "body": f"{d['count']} Groundhog functions",
        })
    return entries


def clean_docs_output() -> None:
    """Remove generated docs HTML (everything under website/docs except the mirrored assets)."""
    docs = WEBSITE / "docs"
    if not docs.is_dir():
        return
    for child in docs.iterdir():
        if child.name == "assets":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        elif child.suffix in (".html", ".json"):
            child.unlink()


SECTION_ICONS = {
    "getting-started": "download", "using-geocore": "sliders", "geoai": "sparkles",
    "groundhog-guides": "book", "groundhog-api": "code", "changelog": "history", "license": "scale",
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build() -> None:
    env = make_env()
    fn = load_function_counts()
    domains = []
    for d in DOMAINS:
        d = dict(d, count=fn["counts"].get(d["key"], 0))
        domains.append(d)
    unknown = set(fn["counts"]) - {d["key"] for d in DOMAINS}
    if unknown:
        _warn(f"manifest has Groundhog packages without website copy: {sorted(unknown)}")

    problems: List[str] = []
    content_dir = WEBSITE / docs_content.CONTENT_DIRNAME
    docs_pages: List[Dict[str, Any]] = []
    home: Dict[str, Any] = {}
    if (content_dir / "nav.json").exists():
        raw_nav, docs_pages, home = docs_content.build_pages(content_dir, WEBSITE, problems)
        for n in raw_nav:
            n["icon"] = SECTION_ICONS.get(n["slug"], "book")
        docs_nav = normalize_nav(raw_nav)
    else:
        _warn(f"{content_dir} has no nav.json; docs pages are not generated")
        docs_nav = []
    models = load_models()
    base = {
        "site_name": "GeoCore",
        "repo_url": REPO_URL,
        "releases_url": RELEASES_URL,
        "app_version": load_app_version(),
        "fn_total": fn["total"],
        "domains": domains,
        "models": models,
        "model_min_mb": min((m["size_mb"] for m in models), default=0),
        "model_max_mb": max((m["size_mb"] for m in models), default=0),
        "groundhog_version": "0.15.0",
        "privacy_updated": LAST_UPDATED_PRIVACY,
        "year": _dt.date.today().year,
        "docs_nav": docs_nav,
    }

    pages = [
        ("index.html", "index.html", "home"),
        ("about.html", "about.html", "about"),
        ("privacy.html", "privacy.html", "privacy"),
        ("download.html", "download.html", "download"),
        ("404.html", "404.html", ""),
    ]
    for template, out, nav_key in pages:
        target = render(env, template, out, dict(base, nav_active=nav_key), absolute=(out == "404.html"))
        print(f"  wrote {target.relative_to(REPO)}")

    clean_docs_output()
    docs_ctx = dict(base, nav_active="docs")
    ordered = flatten_nav(docs_nav)
    landing = dict(home or {})
    landing.update({
        "title": "Documentation",
        "title_html": None,
        "description": "GeoCore documentation: installing and using GeoCore, GeoAI, the Groundhog guides and API reference.",
        "url": "docs/",
        "breadcrumbs": [],
        "toc": [{"id": s["slug"], "title": s["title"], "level": 2} for s in docs_nav],
        "meta": None,
    })
    render_docs_page(env, landing, docs_nav, docs_ctx, template="docs/index.html", ordered=ordered)
    for page in docs_pages:
        render_docs_page(env, page, docs_nav, docs_ctx, ordered=ordered)
    print(f"  wrote website/docs: {len(docs_pages) + 1} pages")

    entries = seed_search_entries(domains) + docs_content.search_entries(docs_pages)
    target = write_search_index(entries)
    print(f"  wrote {target.relative_to(REPO)} ({len(entries)} entries, {target.stat().st_size / 1024:.0f} KB)")
    if home:
        st = home.get("stats", {})
        print(f"  docs images: {st.get('images', 0)} files, {st.get('image_bytes', 0) / 1e6:.1f} MB")
    for p in problems:
        _warn(p)
    print(f"done: {fn['total']} Groundhog functions ({fn['source']}), {len(models)} GeoAI models, "
          f"{len(problems)} content problems")


if __name__ == "__main__":
    _t0 = time.perf_counter()
    build()
    print(f"build time: {time.perf_counter() - _t0:.1f} s")
