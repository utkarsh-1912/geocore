#!/usr/bin/env python
# Author: Utkarsh Gupta
# License: GPL v3
"""
Offline "Guide & Theory" content for the GeoCore desktop app.

Writes electron-app/src/features/calculations/guide/functionDocs.json: one entry per calculator in
electron-app/src/config/geotechnicalModules.js, keyed by the calculator id, with the theory, formulas,
parameter metadata, outputs and references taken from the groundhog docstrings that GeoCore ships
(website/_content/groundhog/api.json).

Reuses the docs pipeline rather than duplicating it:
  - calculator id -> groundhog target: extract_docs.load_geocore_ui() (same mapping as the website),
  - Markdown for parameter ranges / returns: extract_docs._range_text() / render_returns(),
  - Markdown -> HTML with math kept as \\( .. \\) / \\[ .. \\]: docs_content.render_markdown().

The app renders the math with KaTeX. Links are flattened to text because the desktop window must not
navigate away; figures are omitted (they live in the online docs) and replaced by a short note.
Output is deterministic (sorted keys, no timestamps).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CONTENT_DIR = REPO / "website" / "_content"
API_JSON = CONTENT_DIR / "groundhog" / "api.json"
OUT_PATH = REPO / "electron-app" / "src" / "features" / "calculations" / "guide" / "functionDocs.json"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(CONTENT_DIR))
import docs_content  # noqa: E402
import extract_docs  # noqa: E402  (pure helpers only; importing does not run the extractor)

_LINK = re.compile(r"<a\b[^>]*>(.*?)</a>", re.S)
_FIGURE = re.compile(r"%%FIGURE:(\d+)%%")


def _find_item(api: Dict[str, Any], module: str, qualname: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Return (module entry, function/class/method entry) from api.json."""
    mod = next((m for m in api["modules"] if m["module"] == module), None)
    if mod is None:
        return None, None
    head, _, rest = qualname.partition(".")
    for member in mod["members"]:
        if member["qualname"] != head:
            continue
        if not rest:
            return mod, member
        return mod, next((mm for mm in member.get("methods", []) if mm["qualname"] == qualname), None)
    return mod, None


def _figures_note(desc: str, figures: List[Dict[str, Any]]) -> str:
    def repl(m: "re.Match[str]") -> str:
        fig = figures[int(m.group(1))] if int(m.group(1)) < len(figures) else {}
        cap = fig.get("caption") or Path(fig.get("path", "figure")).stem
        return f"*Figure omitted in the app: {cap}. See the groundhog documentation.*"
    return _FIGURE.sub(repl, desc or "")


def _html(md: Any, text: str) -> Tuple[str, bool]:
    if not text.strip():
        return "", False
    out, _, has_math = docs_content.render_markdown(md, text)
    return _LINK.sub(r"\1", out).strip(), has_math


def _params(item: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """Per-parameter metadata the app merges into its own input table (symbol, unit, range, description).

    Class calculators take their inputs from the constructor and several methods, so those docstrings are
    merged too; the first documented occurrence of a name wins.
    """
    out: Dict[str, Dict[str, str]] = {}
    sources = [item] + ([item["init"]] if item.get("init") else []) + list(item.get("methods", []))
    for src in sources:
        spec = src.get("validation")
        for p in src["doc"]["params"]:
            name = p["name"]
            if name.startswith("*") or name in out:
                continue
            entry = {
                "description": p.get("description") or "",
                "symbol": p.get("symbol") or "",
                "unit": p.get("unit") or "",
                "range": extract_docs._range_text(name, p.get("range"), spec),
            }
            out[name] = {k: v for k, v in entry.items() if v}
        for name in (spec or {}):
            if name not in out:
                rng = extract_docs._range_text(name, None, spec)
                if rng:
                    out[name] = {"range": rng}
    return out


def _theory_md(item: Dict[str, Any]) -> str:
    doc = item["doc"]
    parts = [_figures_note(doc["description_md"], doc["figures"])]
    # Classes: the calculation workflow is spread over methods; keep each documented method's theory.
    for meth in item.get("methods", []):
        mdoc = meth["doc"]
        body = _figures_note(mdoc["description_md"], mdoc["figures"]).strip()
        if not body:
            continue
        parts += [f"#### `{meth['name']}`", "", body, ""]
    return "\n\n".join(p for p in parts if p.strip())


def _references(md: Any, item: Dict[str, Any]) -> List[str]:
    refs = list(item["doc"]["references"])
    for meth in item.get("methods", []):
        refs += [r for r in meth["doc"]["references"] if r not in refs]
    out = []
    for r in refs:
        html, _ = _html(md, r)
        out.append(re.sub(r"^<p>(.*)</p>$", r"\1", html, flags=re.S))
    return out


def build_app_docs() -> Path:
    api = json.loads(API_JSON.read_text(encoding="utf-8"))
    version = api["groundhog_version"]
    ui = extract_docs.load_geocore_ui()
    md = docs_content.make_markdown()
    functions: Dict[str, Any] = {}
    missing: List[str] = []
    for entry in ui["entries"]:
        target = entry.get("target")
        mod, item = _find_item(api, *target) if target else (None, None)
        if item is None:
            missing.append(entry["id"])
            continue
        doc = item["doc"]
        theory_html, theory_math = _html(md, _theory_md(item))
        returns_html, returns_math = _html(md, extract_docs.render_returns(doc["returns"], doc["rtype"])
                                           .replace("**Returns**\n\n", "", 1))
        functions[entry["id"]] = {
            "title": entry["title"],
            "category": entry.get("category"),
            "submodule": entry.get("submodule"),
            "module": item["module"],
            "qualname": item["qualname"],
            "kind": item["kind"],
            "summary": doc["summary"],
            "theory_html": theory_html,
            "returns_html": returns_html,
            "params": _params(item),
            "references": _references(md, item),
            "validated": bool(item.get("validated")),
            "has_math": theory_math or returns_math,
            "docs_slug": extract_docs.module_slug(item["module"]),
            "source_url": f"{extract_docs.GH_REPO_URL}/blob/v{version}/{mod['source_path']}#L{item.get('line') or 1}",
        }
    data = {
        "groundhog_version": version,
        "license": api["license"],
        "author": api["author"],
        "attribution": (f"Theory, formulas and references adapted from the groundhog {version} docstrings by "
                        f"{api['author']} (https://github.com/snakesonabrain/groundhog), {api['license']}."),
        "functions": functions,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
                        encoding="utf-8")
    if missing:
        print(f"  WARNING: no groundhog docs for app calculators: {missing}")
    return OUT_PATH


if __name__ == "__main__":
    path = build_app_docs()
    print(f"wrote {path.relative_to(REPO)} ({path.stat().st_size / 1024:.0f} KB)")
