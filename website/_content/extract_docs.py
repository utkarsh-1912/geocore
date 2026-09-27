#!/usr/bin/env python
# Author: Utkarsh Gupta
# License: GPL v3
"""
GeoCore documentation content extractor.

Builds the Markdown content tree consumed by the website docs layout:

    website/_content/nav.json            navigation tree
    website/_content/pages/<slug>.md     one page per nav node (YAML front-matter + Markdown)
    website/_content/search-index.json   compact search index
    website/_content/groundhog/api.json  structured groundhog API data (parsed docstrings)
    website/_content/groundhog/assets/   figures copied from the groundhog repository

Sources (in priority order):
  1. The installed ``groundhog`` package (API reference, authoritative for the shipped version).
  2. The groundhog git repository (``--groundhog-repo``): docs/*.rst, notebooks/*.ipynb, CHANGES.txt.
     Optional; without it only the API reference, GeoCore pages and licence page are built.
  3. GeoCore's own Markdown pages in website/_content/geocore/.

Usage:
    python website/_content/extract_docs.py --groundhog-repo <path-to-groundhog-clone>

The script is deterministic: running it twice on the same inputs produces identical output.
It only uses the standard library, PyYAML and groundhog (all present in python-backend/venv).
"""

from __future__ import annotations

import argparse
import ast
import base64
import importlib
import inspect
import json
import pkgutil
import re
import shutil
import sys
import textwrap
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONTENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CONTENT_DIR.parent.parent
PAGES_DIR = CONTENT_DIR / "pages"
GH_ASSETS_DIR = CONTENT_DIR / "groundhog" / "assets"
GEOCORE_SRC_DIR = CONTENT_DIR / "geocore"

LINK_PREFIX = "/docs/"                       # page links are LINK_PREFIX + slug
ASSET_URL_PREFIX = "/docs/assets/groundhog/"  # served copy of groundhog/assets/

GH_REPO_URL = "https://github.com/snakesonabrain/groundhog"
GH_RTD_BASE = "https://groundhog.readthedocs.io/en/main/"
GH_AUTHOR = "Bruno Stuyts"
GH_LICENSE = "GPL-3.0-or-later"
GH_COPYRIGHT = "Copyright (C) 2020-2025 Bruno Stuyts"
GEOCORE_REPO_URL = "https://github.com/utkarsh-1912/geocore"
GEOCORE_LICENSE = "GPL-3.0"
GEOCORE_AUTHOR = "Utkarsh Gupta"

# Upstream content deliberately not imported (path relative to the groundhog repo root).
EXCLUDED_UPSTREAM = {
    "docs/Golden_rules.rst": (
        "States that groundhog is provided under a Creative Commons 4.0 Attribution-ShareAlike licence, "
        "which conflicts with the repository LICENSE (GPLv3). The page is also not part of the published "
        "documentation toctree. Excluded until the licence statement is clarified upstream."
    ),
    "notebooks/Images/cgs.png": (
        "Logo of a third-party organisation (webinar host); not groundhog content and not needed for the tutorial."
    ),
}
# Upstream pages replaced by the converted notebooks (they only say "moved to the notebooks").
SUPERSEDED_UPSTREAM = {
    "docs/tutorials/pcpt_processing.rst",
    "docs/tutorials/pile_calculation.rst",
    "docs/tutorials/soilprofiles.rst",
}

PACKAGE_TITLES = {
    "consolidation": "Consolidation",
    "constitutivemodels": "Constitutive models",
    "deepfoundations": "Deep foundations",
    "excavations": "Excavations",
    "general": "General",
    "pipelinescables": "Pipelines and cables",
    "shallowfoundations": "Shallow foundations",
    "siteinvestigation": "Site investigation",
    "soildynamics": "Soil dynamics",
    "standards": "Standards",
    "dissipation": "Dissipation",
    "groundwaterflow": "Groundwater flow",
    "axialcapacity": "Axial capacity",
    "axialresponse": "Axial response",
    "boreholestability": "Borehole stability",
    "lateralresponse": "Lateral response",
    "stability": "Stability",
    "classification": "Classification",
    "correlations": "Correlations",
    "insitutests": "In-situ tests",
    "labtesting": "Lab testing",
    "eurocode7": "Eurocode 7",
}

# GeoCore UI function ids that do not share the groundhog name (see python-backend/core/registry.py).
UI_ALIASES = {
    "AGSConverter_convert_ags_group": ("groundhog.general.agsconversion", "AGSConverter.convert_ags_group"),
    "offsets_api": ("groundhog.general.parameter_mapping", "offsets"),
    "LCPC_Calculation": ("groundhog.deepfoundations.axialcapacity.lcpc", "LCPCAxcapCalculation"),
    "PileSettlementCurves": ("groundhog.deepfoundations.axialresponse.settlement", "pile_settlement_curves"),
    "shallow_foundation_capacity_undrained": ("groundhog.shallowfoundations.capacity", "ShallowFoundationCapacityUndrained"),
    "shallow_foundation_capacity_drained": ("groundhog.shallowfoundations.capacity", "ShallowFoundationCapacityDrained"),
    "settlement_calculation": ("groundhog.shallowfoundations.settlement", "SettlementCalculation"),
    "consolidation_calculation": ("groundhog.consolidation.dissipation.onedimensionalconsolidation", "ConsolidationCalculation"),
    "parameter_selection_constant_value": ("groundhog.standards.eurocode7.parameter_selection", "constant_value"),
    "parameter_selection_linear_trend": ("groundhog.standards.eurocode7.parameter_selection", "linear_trend"),
    "eurocode7_factors": ("groundhog.standards.eurocode7.factors", "Eurocode7_factoring_STR_GEO"),
    "hardening_soil_drained_triaxial": ("groundhog.constitutivemodels.cohesionless", "HardeningSoil"),
}

SECTION_GETTING_STARTED = "Getting Started"
SECTION_USING = "Using GeoCore"
SECTION_GEOAI = "GeoAI"
SECTION_GUIDES = "Groundhog Guides"
SECTION_API = "Groundhog API Reference"
SECTION_CHANGELOG = "Changelog"
SECTION_LICENSE = "License & Credits"


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def anchor_id(qualname: str) -> str:
    return qualname.lower().replace(".", "-")


def page_link(slug: str, anchor: Optional[str] = None) -> str:
    return LINK_PREFIX + slug + (("#" + anchor) if anchor else "")


def gh_blob(path: str, tag: str) -> str:
    return f"{GH_REPO_URL}/blob/{tag}/" + quote(path)


def geocore_blob(path: str) -> str:
    return f"{GEOCORE_REPO_URL}/blob/main/" + quote(path)


def rtd_url(docs_rel_rst: str) -> str:
    """docs/site_investigation/pcpt_functions.rst -> readthedocs html URL."""
    rel = docs_rel_rst[len("docs/"):] if docs_rel_rst.startswith("docs/") else docs_rel_rst
    return GH_RTD_BASE + rel[:-4] + ".html"


def first_sentence(text: str, limit: int = 220) -> str:
    text = strip_markdown(text)
    m = re.search(r"(.+?[.!?])(\s|$)", text)
    s = m.group(1) if m else text
    if len(s) > limit:
        s = s[: limit - 1].rstrip() + "…"
    return s.strip()


def strip_markdown(md: str) -> str:
    t = re.sub(r"```.*?```", " ", md, flags=re.S)
    t = re.sub(r"\$\$.*?\$\$", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"!\[([^\]]*)\]\([^)]*\)", " ", t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"\$([^$]*)\$", r"\1", t)
    t = re.sub(r"^#+\s*", "", t, flags=re.M)
    t = re.sub(r"^\s*\|.*\|\s*$", " ", t, flags=re.M)
    t = t.replace("`", "").replace("**", "").replace("*", "")
    t = re.sub(r"^\s*>\s?", "", t, flags=re.M)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def md_cell(text: Any) -> str:
    """Escape a value for a GFM table cell (pipes inside $math$ become \\vert)."""
    if text is None:
        return ""
    s = str(text).replace("\n", " ").strip()
    parts = re.split(r"(\$[^$]*\$)", s)
    out = []
    for p in parts:
        if p.startswith("$") and p.endswith("$") and len(p) > 1:
            out.append(p.replace("|", r"\vert "))
        else:
            out.append(p.replace("|", r"\|"))
    return "".join(out)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def dump_json(path: Path, data: Any) -> None:
    write_text(path, json.dumps(data, indent=2, ensure_ascii=False, default=str) + "\n")


def render_front_matter(meta: Dict[str, Any]) -> str:
    clean = {k: v for k, v in meta.items() if v is not None}
    return "---\n" + yaml.safe_dump(clean, sort_keys=False, allow_unicode=True, width=10000,
                                    default_flow_style=False) + "---\n\n"


def split_front_matter(text: str) -> Tuple[Dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, flags=re.S)
    if not m:
        return {}, text
    return (yaml.safe_load(m.group(1)) or {}), m.group(2)


# ---------------------------------------------------------------------------
# RST inline conversion (shared by docstrings and narrative docs)
# ---------------------------------------------------------------------------

_CTRL_FIX = {"\a": "a", "\b": "b", "\f": "f", "\v": "v", "\r": "r"}


def repair_escapes(raw: str) -> str:
    """Repair LaTeX commands mangled by non-raw docstrings (e.g. '\\text' written as '\\t'+'ext').

    Only control characters immediately followed by a letter are touched; tabs are only repaired when
    they are not part of leading indentation.
    """
    for ch, letter in _CTRL_FIX.items():
        raw = re.sub(re.escape(ch) + r"(?=[A-Za-z])", "\\\\" + letter, raw)
    fixed = []
    for line in raw.split("\n"):
        lead = re.match(r"^[ \t]*", line).group(0)
        fixed.append(lead + re.sub(r"\t(?=[a-z])", r"\\t", line[len(lead):]))
    return "\n".join(fixed)


def rst_inline(text: str) -> str:
    """Convert RST inline markup to Markdown."""
    # :math:`x` -> $x$
    text = re.sub(r":math:`([^`]*)`", lambda m: f"${m.group(1).strip()}$" if m.group(1).strip() else "", text)
    # ``code`` (and the occasional ```code```) -> `code`
    text = re.sub(r"`{2,3}([^`]+)`{2,3}", r"`\1`", text)
    # `label <url>`_  /  `label <url>`__
    text = re.sub(r"`([^`<]+?)\s*<([^>]+)>`__?", lambda m: f"[{m.group(1).strip()}]({m.group(2).strip()})", text)
    # :ref:`label` / :py:func:`x` / :class:`x`
    text = re.sub(r":ref:`([^`<]+?)(?:\s*<[^>]+>)?`", r"\1", text)
    text = re.sub(r":(?:py:)?(?:func|class|meth|mod|attr|obj|data):`~?([^`]+)`", r"`\1`", text)
    return text


# ---------------------------------------------------------------------------
# Docstring parser
# ---------------------------------------------------------------------------

PARAM_RE = re.compile(r"^:param\s+(?:[\w\[\], ]+\s+)?(\*{0,2}\w+)\s*:\s*(.*)$")
RETURNS_RE = re.compile(r"^:returns?:\s*(.*)$")
RTYPE_RE = re.compile(r"^:rtype:\s*(.*)$")
RAISES_RE = re.compile(r"^:raises?\s*([\w.]*)\s*:\s*(.*)$")
DIRECTIVE_RE = re.compile(r"^\.\.\s+([\w:-]+)::\s*(.*)$")
REFERENCE_RE = re.compile(r"^References?\s*(?:-|:|–)\s*(.*)$")
EXAMPLE_RE = re.compile(r"^Examples?\s*:?\s*$")
LIST_ITEM_RE = re.compile(r"^([-*+]|\d+[.)])\s+(.*)$")


@dataclass
class FigureRef:
    path: str
    options: Dict[str, str] = field(default_factory=dict)
    caption: str = ""


def _collect_block(lines: List[str], start: int, base_indent: int) -> Tuple[List[str], int]:
    """Collect lines after `start` that are blank or indented deeper than base_indent."""
    block = []
    j = start
    while j < len(lines):
        ln = lines[j]
        if ln.strip() and indent_of(ln) <= base_indent:
            break
        block.append(ln)
        j += 1
    while block and not block[-1].strip():
        block.pop()
        j -= 1
    # keep j pointing at the first unconsumed line (trailing blanks are harmless to re-read)
    return block, j


def _dedent(block: List[str]) -> List[str]:
    return textwrap.dedent("\n".join(block)).split("\n") if block else []


def parse_param_text(name: str, text: str) -> Dict[str, Any]:
    """Split a groundhog ':param x:' text into description, symbol, unit, range and default."""
    raw = re.sub(r"\s+", " ", text).strip()
    rest = raw
    default = None
    m = re.search(r"\(\s*optional\s*,?\s*default\s*=\s*(.*?)\)\s*\.?\s*$", rest, flags=re.I)
    if m:
        default = m.group(1).strip()
        rest = rest[: m.start()].strip()
    optional = bool(re.search(r"\(\s*optional", raw, flags=re.I))
    rng = None
    m = re.search(r"-?\s*Suggested range\s*:?\s*(.*)$", rest, flags=re.I)
    if m:
        rng = rst_inline(m.group(1).strip()).rstrip(" .") or None
        rest = rest[: m.start()].strip()
    symbol = None
    m = re.search(r"\(\s*:math:`([^`]*)`\s*\)", rest)
    sym_end = None
    if m:
        symbol = m.group(1).strip() or None
        sym_end = m.end()
        desc_part = rest[: m.start()]
        after = rest[m.end():]
    else:
        desc_part, after = rest, ""
    unit = None
    um = re.search(r"\[\s*(?::math:`([^`]*)`|([^\]]*))\s*\]", after if sym_end is not None else rest)
    if um:
        unit = (um.group(1) if um.group(1) is not None else um.group(2) or "").strip() or None
        if sym_end is None:
            desc_part = rest[: um.start()]
            after = rest[um.end():]
        else:
            after = after[: um.start()] + after[um.end():]
    extra = after.strip(" -")
    description = desc_part.strip().rstrip(" -")
    if extra:
        description = (description + " " + extra).strip()
    return {
        "name": name,
        "description": rst_inline(description),
        "symbol": symbol,
        "unit": unit,
        "range": rng,
        "default_doc": default,
        "optional": optional or default is not None,
        "raw": raw,
    }


def parse_returns_block(first: str, block: List[str]) -> Dict[str, Any]:
    lines = [first] + _dedent(block)
    desc_lines: List[str] = []
    items: List[Dict[str, Any]] = []
    cur: Optional[List[str]] = None
    for ln in lines:
        s = ln.strip()
        if not s:
            cur = None
            continue
        m = LIST_ITEM_RE.match(s)
        if m and m.group(1) in "-*+":
            cur = [m.group(2)]
            items.append({"_lines": cur})
        elif cur is not None and indent_of(ln) > 0:
            cur.append(s)
        else:
            desc_lines.append(s)
            cur = None
    parsed_items = []
    for it in items:
        text = " ".join(it["_lines"])
        km = re.match(r"^['\"](.+?)['\"]\s*:\s*(.*)$", text)
        if km:
            key, rest = km.group(1), km.group(2)
        else:
            km2 = re.match(r"^([^:]{1,60}):\s+(.*)$", text)
            key, rest = (km2.group(1), km2.group(2)) if km2 else (None, text)
        symbol = None
        sm = re.search(r"\(\s*:math:`([^`]*)`\s*\)", rest)
        if sm:
            symbol = sm.group(1).strip() or None
            rest = rest[: sm.start()] + rest[sm.end():]
        unit = None
        um = re.search(r"\[\s*:math:`([^`]*)`\s*\]", rest)
        if um:
            unit = um.group(1).strip() or None
            rest = rest[: um.start()] + rest[um.end():]
        elif key:
            km3 = re.search(r"\[([^\]]*)\]\s*$", key)
            if km3:
                unit = km3.group(1).strip() or None
        parsed_items.append({
            "key": key,
            "description": rst_inline(re.sub(r"\s+", " ", rest).strip(" -")) or None,
            "symbol": symbol,
            "unit": unit,
        })
    return {
        "description": rst_inline(" ".join(desc_lines)).strip(),
        "items": parsed_items,
        "raw": "\n".join(lines).strip(),
    }


def _render_list(block_lines: List[str]) -> str:
    items: List[Tuple[int, str]] = []
    for ln in block_lines:
        if not ln.strip():
            continue
        s = ln.strip()
        m = LIST_ITEM_RE.match(s)
        if m:
            items.append((indent_of(ln), (m.group(1) if m.group(1)[0].isdigit() else "-") + " " + m.group(2)))
        elif items:
            ind, t = items[-1]
            items[-1] = (ind, t + " " + s)
    if not items:
        return ""
    levels = sorted({i for i, _ in items})
    out = []
    for ind, t in items:
        depth = levels.index(ind)
        out.append("  " * depth + rst_inline(t))
    return "\n".join(out)


def parse_docstring(raw: Optional[str]) -> Dict[str, Any]:
    """Parse a groundhog-style RST docstring into structured fields.

    Returns a dict with: summary, description_md, params, returns, rtype, raises, formulas,
    figures, references, examples, raw.
    """
    result: Dict[str, Any] = {
        "summary": "", "description_md": "", "params": [], "returns": None, "rtype": None,
        "raises": [], "formulas": [], "figures": [], "references": [], "examples": [], "raw": raw or "",
    }
    if not raw or not raw.strip():
        return result
    doc = inspect.cleandoc(repair_escapes(raw))
    lines = doc.split("\n")
    chunks: List[str] = []      # markdown chunks (in source order)
    para: List[str] = []

    def flush():
        if para:
            chunks.append(rst_inline(" ".join(p.strip() for p in para)))
            para.clear()

    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        s = line.strip()
        ind = indent_of(line)
        if not s:
            flush()
            i += 1
            continue

        m = PARAM_RE.match(s)
        if m:
            flush()
            block, j = _collect_block(lines, i + 1, ind)
            text = " ".join([m.group(2)] + [b.strip() for b in block if b.strip()])
            result["params"].append(parse_param_text(m.group(1), text))
            i = j
            continue
        m = RETURNS_RE.match(s)
        if m:
            flush()
            block, j = _collect_block(lines, i + 1, ind)
            result["returns"] = parse_returns_block(m.group(1), block)
            i = j
            continue
        m = RTYPE_RE.match(s)
        if m:
            flush()
            result["rtype"] = m.group(1).strip()
            i += 1
            continue
        m = RAISES_RE.match(s)
        if m:
            flush()
            block, j = _collect_block(lines, i + 1, ind)
            result["raises"].append({"exception": m.group(1) or None,
                                     "description": rst_inline(" ".join([m.group(2)] + [b.strip() for b in block]).strip())})
            i = j
            continue
        m = DIRECTIVE_RE.match(s)
        if m:
            flush()
            name, arg = m.group(1), m.group(2).strip()
            block, j = _collect_block(lines, i + 1, ind)
            body = _dedent(block)
            opts: Dict[str, str] = {}
            content: List[str] = []
            in_opts = True
            for bl in body:
                om = re.match(r"^:([\w-]+):\s*(.*)$", bl.strip())
                if in_opts and om and bl.strip():
                    opts[om.group(1)] = om.group(2)
                    continue
                if in_opts and not bl.strip():
                    in_opts = False
                    continue
                in_opts = False
                content.append(bl)
            if name == "math":
                eqs = []
                src = ([arg] if arg else []) + content
                cur: List[str] = []
                for cl in src:
                    if cl.strip():
                        cur.append(cl.rstrip())
                    elif cur:
                        eqs.append(textwrap.dedent("\n".join(cur)).strip())
                        cur = []
                if cur:
                    eqs.append(textwrap.dedent("\n".join(cur)).strip())
                for eq in eqs:
                    result["formulas"].append(eq)
                    chunks.append("$$\n" + eq + "\n$$")
            elif name in ("figure", "image"):
                caption = " ".join(c.strip() for c in content if c.strip())
                fig = FigureRef(path=arg, options=opts, caption=rst_inline(caption))
                result["figures"].append({"path": arg, "options": opts, "caption": fig.caption})
                chunks.append(f"%%FIGURE:{len(result['figures']) - 1}%%")
            elif name in ("code-block", "code", "sourcecode"):
                chunks.append(f"```{arg or 'python'}\n" + "\n".join(content).strip("\n") + "\n```")
            elif name in ("note", "warning", "important", "tip", "caution"):
                txt = rst_inline(" ".join(c.strip() for c in ([arg] + content) if c.strip()))
                chunks.append(f"> **{name.capitalize()}:** {txt}")
            else:
                chunks.append("```text\n" + "\n".join([s] + block) + "\n```")
            i = j
            continue
        m = REFERENCE_RE.match(s)
        if m:
            flush()
            first = m.group(1).strip()
            if not first:
                block, j = _collect_block(lines, i + 1, ind)
                if block:
                    listed = any(LIST_ITEM_RE.match(b.strip()) for b in block if b.strip())
                    if listed:
                        for r in _render_list(block).split("\n"):
                            r = re.sub(r"^\s*-\s*", "", r).strip()
                            if r:
                                result["references"].append(r)
                    else:
                        paras = re.split(r"\n\s*\n", "\n".join(block))
                        for ptxt in paras:
                            if ptxt.strip():
                                result["references"].append(rst_inline(" ".join(x.strip() for x in ptxt.split("\n"))))
                    i = j
                    continue
                first = ""
            # single reference: continues until blank line
            j = i + 1
            parts = [first]
            while j < n and lines[j].strip() and not REFERENCE_RE.match(lines[j].strip()) \
                    and not lines[j].strip().startswith((":", "..")):
                parts.append(lines[j].strip())
                j += 1
            ref_text = rst_inline(" ".join(p for p in parts if p)).strip()
            if ref_text:
                result["references"].append(ref_text)
            i = j
            continue
        if EXAMPLE_RE.match(s):
            flush()
            block, j = _collect_block(lines, i + 1, ind)
            body = _dedent(block)
            code_lines = []
            for bl in body:
                if DIRECTIVE_RE.match(bl.strip()) or re.match(r"^:[\w-]+:", bl.strip()):
                    continue
                code_lines.append(bl)
            code = textwrap.dedent("\n".join(code_lines)).strip("\n")
            if code:
                result["examples"].append(code)
            i = j
            continue
        if s.startswith("+-") or s.startswith("+="):
            flush()
            j = i
            tbl = []
            while j < n and lines[j].strip():
                tbl.append(lines[j].strip())
                j += 1
            chunks.append("```text\n" + re.sub(r":math:`([^`]*)`", r"\1", "\n".join(tbl)) + "\n```")
            i = j
            continue
        if LIST_ITEM_RE.match(s):
            flush()
            j = i
            block_lines = []
            base = ind
            while j < n:
                ln = lines[j]
                st = ln.strip()
                if not st:
                    # a blank line ends the list unless followed by another item / deeper line
                    k = j + 1
                    if k < n and lines[k].strip() and (LIST_ITEM_RE.match(lines[k].strip()) and indent_of(lines[k]) >= base
                                                       or indent_of(lines[k]) > base):
                        j += 1
                        continue
                    break
                if indent_of(ln) < base:
                    break
                if indent_of(ln) == base and not LIST_ITEM_RE.match(st):
                    break
                if PARAM_RE.match(st) or RETURNS_RE.match(st) or DIRECTIVE_RE.match(st):
                    break
                block_lines.append(ln)
                j += 1
            chunks.append(_render_list(block_lines))
            i = j
            continue
        para.append(s)
        i += 1
    flush()
    desc = "\n\n".join(c for c in chunks if c.strip())
    result["description_md"] = desc
    textual = [c for c in chunks if c.strip() and not c.startswith(("$$", "%%FIGURE", "```", ">"))]
    result["summary"] = first_sentence(textual[0]) if textual else ""
    return result


# ---------------------------------------------------------------------------
# groundhog API walker
# ---------------------------------------------------------------------------

def _source_line(obj: Any) -> int:
    try:
        return inspect.getsourcelines(obj)[1]
    except Exception:
        return 10 ** 9


def _validation_spec(func: Any) -> Optional[Dict[str, Any]]:
    """Return groundhog's Validator spec for a decorated function (min/max/options per parameter)."""
    try:
        cv = inspect.getclosurevars(func)
    except Exception:
        return None
    validator = cv.nonlocals.get("self")
    spec = getattr(validator, "validationspec", None)
    if isinstance(spec, dict):
        return spec
    return None


def _format_default(value: Any) -> str:
    if value is inspect.Parameter.empty:
        return ""
    if isinstance(value, float) and value != value:
        return "nan"
    return repr(value)


def _signature(obj: Any, name: str, skip_self: bool = False) -> Tuple[str, List[Dict[str, Any]]]:
    try:
        sig = inspect.signature(obj)
    except (TypeError, ValueError):
        return f"{name}(...)", []
    params = []
    parts = []
    for i, (pname, p) in enumerate(sig.parameters.items()):
        if skip_self and i == 0 and pname in ("self", "cls"):
            continue
        entry = {"name": pname, "kind": p.kind.name,
                 "default": _format_default(p.default) if p.default is not inspect.Parameter.empty else None,
                 "required": p.default is inspect.Parameter.empty and p.kind in (
                     p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)}
        params.append(entry)
        if p.kind == p.VAR_POSITIONAL:
            parts.append("*" + pname)
        elif p.kind == p.VAR_KEYWORD:
            parts.append("**" + pname)
        elif entry["default"] is not None:
            parts.append(f"{pname}={entry['default']}")
        else:
            parts.append(pname)
    one_line = f"{name}({', '.join(parts)})"
    if len(one_line) > 88 and parts:
        one_line = f"{name}(\n" + "".join(f"    {p},\n" for p in parts) + ")"
    return one_line, params


def _doc_of(obj: Any) -> Optional[str]:
    """Return the docstring exactly as written in the source.

    Python 3.13+ dedents docstrings at compile time and expands tabs, which destroys LaTeX commands such as
    ``\\text`` in non-raw docstrings (written as TAB + 'ext'). Reading the literal from the source with ``ast``
    keeps the original characters so that :func:`repair_escapes` can restore them.
    """
    runtime = obj.__dict__.get("__doc__") if inspect.isclass(obj) else getattr(obj, "__doc__", None)
    if not runtime:
        return runtime
    try:
        src = textwrap.dedent(inspect.getsource(obj))
        node = ast.parse(src).body[0]
        raw = ast.get_docstring(node, clean=False)
        if raw and inspect.cleandoc(raw.expandtabs()).split() == inspect.cleandoc(runtime).split():
            return raw
    except Exception:
        pass
    return runtime


def describe_callable(obj: Any, qualname: str, module: str, is_method: bool = False) -> Dict[str, Any]:
    name = qualname.split(".")[-1]
    sig, sig_params = _signature(obj, name, skip_self=is_method)
    parsed = parse_docstring(_doc_of(obj))
    spec = _validation_spec(obj)
    return {
        "kind": "method" if is_method else "function",
        "name": name,
        "qualname": qualname,
        "module": module,
        "anchor": anchor_id(qualname),
        "signature": sig,
        "signature_params": sig_params,
        "validated": spec is not None,
        "validation": spec,
        "doc": parsed,
        "line": _source_line(obj),
    }


def describe_class(cls: Any, module: str) -> Dict[str, Any]:
    init = cls.__dict__.get("__init__")
    init_desc = describe_callable(init, f"{cls.__name__}.__init__", module, is_method=True) \
        if inspect.isfunction(init) else None
    sig = f"{cls.__name__}(...)"
    if init_desc:
        sig = init_desc["signature"].replace("__init__(", cls.__name__ + "(", 1)
    methods = []
    for mname, mobj in cls.__dict__.items():
        if mname.startswith("_"):
            continue
        func = mobj.__func__ if isinstance(mobj, (staticmethod, classmethod)) else mobj
        if inspect.isfunction(func):
            methods.append(describe_callable(func, f"{cls.__name__}.{mname}", module,
                                             is_method=not isinstance(mobj, staticmethod)))
    methods.sort(key=lambda d: (d["line"], d["name"]))
    return {
        "kind": "class",
        "name": cls.__name__,
        "qualname": cls.__name__,
        "module": module,
        "anchor": anchor_id(cls.__name__),
        "signature": sig,
        "doc": parse_docstring(_doc_of(cls)),
        "init": init_desc,
        "methods": methods,
        "line": _source_line(cls),
    }


def walk_groundhog() -> Tuple[str, List[Dict[str, Any]]]:
    import groundhog
    version = getattr(importlib.import_module("groundhog.__version__"), "__version__", "unknown")
    modules = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        infos = sorted(pkgutil.walk_packages(groundhog.__path__, "groundhog."), key=lambda mi: mi.name)
        for mi in infos:
            if mi.name.split(".")[-1].startswith("_"):
                continue
            try:
                mod = importlib.import_module(mi.name)
            except Exception as exc:  # pragma: no cover - depends on optional deps
                print(f"  ! could not import {mi.name}: {exc}", file=sys.stderr)
                continue
            members = []
            for name, obj in vars(mod).items():
                if name.startswith("_") or getattr(obj, "__module__", None) != mi.name:
                    continue
                if inspect.isfunction(obj):
                    members.append(describe_callable(obj, name, mi.name))
                elif inspect.isclass(obj):
                    members.append(describe_class(obj, mi.name))
            members.sort(key=lambda d: (d["line"], d["name"]))
            modules.append({
                "module": mi.name,
                "is_package": mi.ispkg,
                "doc": parse_docstring(mod.__doc__),
                "members": members,
                "source_path": "groundhog/" + "/".join(mi.name.split(".")[1:]) + ("/__init__.py" if mi.ispkg else ".py"),
            })
    return version, modules


def module_slug(module: str) -> str:
    return "groundhog/api/" + "/".join(module.split(".")[1:])


# ---------------------------------------------------------------------------
# GeoCore UI availability
# ---------------------------------------------------------------------------

def load_geocore_ui() -> Dict[str, Any]:
    """Parse electron-app/src/config/geotechnicalModules.js (category > sub-module > function)."""
    path = REPO_ROOT / "electron-app" / "src" / "config" / "geotechnicalModules.js"
    manifest_path = REPO_ROOT / "python-backend" / "core" / "function_manifest.json"
    entries = []
    if path.exists():
        cat_title = sub_title = None
        for ln in path.read_text(encoding="utf-8").splitlines():
            fm = re.search(r"\{\s*id:\s*'([^']+)',\s*title:\s*'([^']+)'\s*\}", ln)
            if fm:
                entries.append({"id": fm.group(1), "title": fm.group(2), "category": cat_title, "submodule": sub_title})
                continue
            tm = re.match(r"^(\s*)title:\s*'([^']+)'", ln)
            if tm:
                if len(tm.group(1)) <= 8:
                    cat_title, sub_title = tm.group(2), None
                else:
                    sub_title = tm.group(2)
    manifest = {}
    if manifest_path.exists():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        for f in data.get("functions", []):
            manifest[f["attr"]] = (f["module"], f["qualname"])
    by_target: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for e in entries:
        target = UI_ALIASES.get(e["id"]) or manifest.get(e["id"])
        e["target"] = list(target) if target else None
        if target:
            by_target.setdefault(tuple(target), []).append(e)
    return {"entries": entries, "by_target": by_target, "manifest_count": len(manifest)}


# ---------------------------------------------------------------------------
# groundhog repository (narrative docs)
# ---------------------------------------------------------------------------

@dataclass
class UpstreamRepo:
    root: Path
    tag: str
    version: str
    commit: Optional[str]
    license_ok: bool
    license_first_lines: str


def open_repo(path: Optional[str], installed_version: str) -> Optional[UpstreamRepo]:
    if not path:
        return None
    root = Path(path).resolve()
    if not (root / "docs").is_dir():
        print(f"  ! {root} does not look like a groundhog clone (no docs/); skipping narrative docs", file=sys.stderr)
        return None
    lic = (root / "LICENSE").read_text(encoding="utf-8", errors="replace") if (root / "LICENSE").exists() else ""
    head = " ".join(lic.split()[:8])
    license_ok = "GNU GENERAL PUBLIC LICENSE" in lic[:200] and "Version 3" in lic[:200]
    version = "unknown"
    vf = root / "groundhog" / "__version__.py"
    if vf.exists():
        m = re.search(r"__version__\s*=\s*['\"]([^'\"]+)", vf.read_text(encoding="utf-8"))
        if m:
            version = m.group(1)
    commit = None
    head_file = root / ".git" / "HEAD"
    try:
        ref = head_file.read_text().strip()
        if ref.startswith("ref:"):
            ref_path = root / ".git" / ref.split(" ", 1)[1]
            commit = ref_path.read_text().strip() if ref_path.exists() else None
        else:
            commit = ref
    except Exception:
        pass
    if version != installed_version:
        print(f"  ! groundhog repo version {version} != installed {installed_version}; "
              f"narrative docs will be labelled with the repo version", file=sys.stderr)
    return UpstreamRepo(root=root, tag=f"v{version}", version=version, commit=commit,
                        license_ok=license_ok, license_first_lines=head)


class AssetStore:
    """Copies upstream images into groundhog/assets and records provenance."""

    def __init__(self, repo: Optional[UpstreamRepo]):
        self.repo = repo
        self.records: Dict[str, Dict[str, Any]] = {}
        self.excluded_hits: List[str] = []
        self._index: Dict[str, List[str]] = {}
        if repo:
            for p in sorted(repo.root.rglob("*")):
                if p.is_file() and p.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".svg"):
                    rel = p.relative_to(repo.root).as_posix()
                    if rel.startswith((".git/", "docs/_build/")):
                        continue
                    self._index.setdefault(p.name.lower(), []).append(rel)

    def resolve(self, ref: str, base_dir: str) -> Optional[str]:
        """Return repo-relative path of an image referenced from base_dir, or None."""
        if not self.repo:
            return None
        cand = (Path(base_dir) / ref).as_posix()
        cand = re.sub(r"[^/]+/\.\./", "", cand)
        for c in (cand, cand + ".png"):
            if (self.repo.root / c).is_file():
                return c
        # case-insensitive match in the same directory
        d = self.repo.root / Path(cand).parent
        if d.is_dir():
            for f in sorted(d.iterdir()):
                if f.name.lower() in (Path(cand).name.lower(), Path(cand).name.lower() + ".png"):
                    return f.relative_to(self.repo.root).as_posix()
        hits = self._index.get(Path(cand).name.lower()) or self._index.get(Path(cand).name.lower() + ".png")
        if hits and base_dir.startswith("docs"):
            docs_hits = [h for h in hits if h.startswith("docs/")]
            if docs_hits:
                return docs_hits[0]
        return None

    def use(self, rel: str, slug: str) -> Optional[str]:
        """Copy an image and return its public URL (None if excluded/missing)."""
        if rel in EXCLUDED_UPSTREAM:
            if rel not in self.excluded_hits:
                self.excluded_hits.append(rel)
            return None
        src = self.repo.root / rel
        dst = GH_ASSETS_DIR / rel
        if rel not in self.records:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            self.records[rel] = {"path": rel, "url": ASSET_URL_PREFIX + quote(rel),
                                 "source_url": gh_blob(rel, self.repo.tag), "used_by": []}
        if slug not in self.records[rel]["used_by"]:
            self.records[rel]["used_by"].append(slug)
        return self.records[rel]["url"]

    def add_generated(self, rel: str, data: bytes, slug: str, source_path: str) -> str:
        dst = GH_ASSETS_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        self.records[rel] = {"path": rel, "url": ASSET_URL_PREFIX + quote(rel),
                             "source_url": gh_blob(source_path, self.repo.tag), "used_by": [slug],
                             "note": "Image output embedded in the upstream notebook"}
        return self.records[rel]["url"]


# --- RST documents ----------------------------------------------------------

@dataclass
class RstDoc:
    path: str                 # repo-relative, e.g. docs/piles/debeer.rst
    title: str
    lines: List[str]
    toctree: List[str]        # repo-relative rst paths
    auto: List[Tuple[str, str]]  # (directive, target)


def _is_underline(line: str) -> bool:
    s = line.rstrip()
    return len(s) >= 3 and len(set(s)) == 1 and s[0] in "=-~^\"'#*+`:._"


def read_rst(repo: UpstreamRepo, rel: str) -> RstDoc:
    text = (repo.root / rel).read_text(encoding="utf-8", errors="replace")
    lines = text.replace("\r\n", "\n").split("\n")
    title = Path(rel).stem
    for k in range(len(lines) - 1):
        if lines[k].strip() and _is_underline(lines[k + 1]) and not _is_underline(lines[k]):
            title = lines[k].strip()
            break
    toctree, auto = [], []
    k = 0
    while k < len(lines):
        m = DIRECTIVE_RE.match(lines[k].strip())
        if m and m.group(1) == "toctree":
            block, j = _collect_block(lines, k + 1, indent_of(lines[k]))
            for b in block:
                bs = b.strip()
                if bs and not bs.startswith(":"):
                    target = (Path(rel).parent / (bs + ".rst")).as_posix()
                    toctree.append(target)
            k = j
            continue
        if m and m.group(1) in ("automodule", "autoclass", "autofunction"):
            auto.append((m.group(1), m.group(2).strip()))
        k += 1
    return RstDoc(path=rel, title=title, lines=lines, toctree=toctree, auto=auto)


def rst_to_markdown(doc: RstDoc, repo: UpstreamRepo, assets: AssetStore, slug: str,
                    link_for_rst, drop_sections: Tuple[str, ...] = ()) -> str:
    """Convert a narrative RST document to Markdown (constructs used by groundhog docs)."""
    lines = doc.lines
    out: List[str] = []
    levels: List[str] = []
    base_dir = str(Path(doc.path).parent.as_posix())
    i, n = 0, len(lines)
    para: List[str] = []
    skipping = False
    skip_level = 0
    title_seen = False

    def flush():
        if para:
            out.append(rst_inline(" ".join(p.strip() for p in para)))
            out.append("")
            para.clear()

    while i < n:
        line = lines[i]
        s = line.strip()
        # section titles (with optional overline)
        if s and i + 1 < n and _is_underline(lines[i + 1]) and not _is_underline(line) and indent_of(line) == 0:
            flush()
            ch = lines[i + 1].strip()[0]
            overline = i > 0 and _is_underline(lines[i - 1])
            key = ch + ("o" if overline else "")
            if key not in levels:
                levels.append(key)
            level = levels.index(key) + 1
            i += 2
            if skipping and level <= skip_level:
                skipping = False
            if s in drop_sections:
                skipping, skip_level = True, level
                continue
            if skipping:
                continue
            if level == 1 and not title_seen:
                title_seen = True    # page title lives in the front-matter
                continue
            out.append("#" * max(2, level) + " " + rst_inline(s))
            out.append("")
            continue
        if _is_underline(line) and (i + 1 < n and lines[i + 1].strip() and i + 2 < n and _is_underline(lines[i + 2])):
            i += 1  # overline of an overlined title
            continue
        if skipping:
            i += 1
            continue
        if not s:
            flush()
            i += 1
            continue
        m = DIRECTIVE_RE.match(s)
        if m:
            flush()
            name, arg = m.group(1), m.group(2).strip()
            block, j = _collect_block(lines, i + 1, indent_of(line))
            body = _dedent(block)
            opts = {}
            content = []
            for bl in body:
                om = re.match(r"^:([\w-]+):\s*(.*)$", bl.strip())
                if om and not content:
                    opts[om.group(1)] = om.group(2)
                elif bl.strip() or content:
                    content.append(bl)
            if name == "code-block":
                out.append(f"```{arg or 'text'}")
                out.extend(textwrap.dedent("\n".join(content)).strip("\n").split("\n"))
                out.append("```")
                out.append("")
            elif name == "image" or name == "figure":
                alt = opts.get("alt", "")
                if re.match(r"^https?://", arg):
                    url = arg
                else:
                    rel = assets.resolve(arg, base_dir)
                    url = assets.use(rel, slug) if rel else None
                if url:
                    img = f"![{alt}]({url})"
                    if "target" in opts:
                        img = f"[{img}]({opts['target']})"
                    out.append(img)
                    out.append("")
            elif name == "toctree":
                targets = [(Path(doc.path).parent / (c.strip() + ".rst")).as_posix() for c in content if c.strip()]
                for target in targets:
                    link = link_for_rst(target)
                    if link:
                        out.append(f"- [{link[0]}]({link[1]})")
                out.append("")
            elif name == "raw":
                html = "\n".join(content)
                hm = re.search(r"href=\"([^\"]+)\"", html)
                if hm:
                    out.append(f"[Support groundhog]({hm.group(1)})")
                    out.append("")
            elif name in ("automodule", "autoclass", "autofunction"):
                link = link_for_auto(name, arg)
                if link:
                    out.append(f"See the API reference: [{link[0]}]({link[1]})")
                    out.append("")
            i = j
            continue
        if s.startswith(".. "):
            # RST comment
            block, j = _collect_block(lines, i + 1, indent_of(line))
            i = j
            continue
        if LIST_ITEM_RE.match(s) and indent_of(line) == 0:
            flush()
            j = i
            items = []
            def is_title(k: int) -> bool:
                return bool(lines[k].strip()) and k + 1 < n and _is_underline(lines[k + 1]) \
                    and not _is_underline(lines[k])

            while j < n and (lines[j].strip() == "" or LIST_ITEM_RE.match(lines[j].strip()) or indent_of(lines[j]) > 0):
                if is_title(j):
                    break
                if lines[j].strip() == "":
                    if j + 1 < n and LIST_ITEM_RE.match(lines[j + 1].strip() or "x x") and not is_title(j + 1):
                        j += 1
                        continue
                    break
                items.append(lines[j])
                j += 1
            out.append(_render_list(items))
            out.append("")
            i = j
            continue
        if indent_of(line) > 0:
            flush()
            block, j = _collect_block(lines, i, 0)
            quote_lines = [b.strip() for b in _dedent(block)]
            out.append("\n".join(("> " + rst_inline(q)) if q else ">" for q in quote_lines))
            out.append("")
            i = j
            continue
        para.append(s)
        i += 1
    flush()
    md = "\n".join(out)
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    return md


# populated in build(); maps "automodule groundhog.x" etc. to (title, url)
_AUTO_LINKS: Dict[Tuple[str, str], Tuple[str, str]] = {}


def link_for_auto(directive: str, target: str) -> Optional[Tuple[str, str]]:
    return _AUTO_LINKS.get((directive, target))


# --- notebooks -----------------------------------------------------------------

def notebook_to_markdown(nb_path: Path, rel: str, slug: str, assets: AssetStore) -> Tuple[str, str, List[str]]:
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    base_dir = str(Path(rel).parent.as_posix())
    out: List[str] = []
    title = nb_path.stem
    notes: List[str] = []
    img_counter = 0
    first_md = True

    def fix_images(src: str) -> str:
        def repl_md(m):
            alt, ref = m.group(1), m.group(2).strip()
            if re.match(r"^(https?:|data:)", ref):
                return m.group(0)
            r = assets.resolve(ref, base_dir)
            url = assets.use(r, slug) if r else None
            return f"![{alt}]({url})" if url else ""

        def repl_html(m):
            ref = m.group(2)
            if re.match(r"^(https?:|data:)", ref):
                return m.group(0)
            r = assets.resolve(ref, base_dir)
            url = assets.use(r, slug) if r else None
            return (m.group(1) + url + m.group(3)) if url else ""

        src = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", repl_md, src)
        src = re.sub(r"(<img[^>]*?src=[\"'])([^\"']+)([\"'][^>]*>)", repl_html, src)
        return src

    for cell in nb.get("cells", []):
        src = "".join(cell.get("source", []))
        if cell.get("cell_type") == "markdown":
            src = fix_images(src).rstrip()
            if first_md:
                hm = re.match(r"^\s*#\s+(.+?)\s*(?:\n|$)", src)
                if hm:
                    title = re.sub(r"<[^>]+>", "", hm.group(1)).strip() or title
                    src = src[hm.end():].strip()
                first_md = False
            if src:
                out.append(src)
                out.append("")
        elif cell.get("cell_type") == "code":
            if not src.strip():
                continue
            out.append("```python")
            out.append(src.rstrip("\n"))
            out.append("```")
            out.append("")
            omitted = False
            for o in cell.get("outputs", []):
                ot = o.get("output_type")
                data = o.get("data", {})
                if ot == "stream":
                    txt = "".join(o.get("text", []))
                    out.extend(_output_block(txt))
                elif ot in ("execute_result", "display_data"):
                    if "image/png" in data:
                        img_counter += 1
                        png = base64.b64decode("".join(data["image/png"]) if isinstance(data["image/png"], list)
                                               else data["image/png"])
                        url = assets.add_generated(f"notebooks/outputs/{slug.split('/')[-1]}-{img_counter}.png",
                                                   png, slug, rel)
                        out.append(f"![Notebook output {img_counter}]({url})")
                        out.append("")
                    elif "text/plain" in data and not any(k.startswith("application/vnd.plotly") for k in data):
                        txt = "".join(data["text/plain"]) if isinstance(data["text/plain"], list) else data["text/plain"]
                        out.extend(_output_block(txt))
                    else:
                        omitted = True
                elif ot == "error":
                    out.extend(_output_block(f"{o.get('ename', 'Error')}: {o.get('evalue', '')}"))
            if omitted:
                out.append("*Interactive output (Plotly/HTML) is not reproduced here; run the notebook to see it.*")
                out.append("")
    md = "\n".join(out)
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    return title, md, notes


def _output_block(txt: str, max_lines: int = 30) -> List[str]:
    lines = txt.rstrip("\n").split("\n")
    if len(lines) > max_lines:
        lines = lines[:max_lines] + ["... (output truncated)"]
    return ["```text"] + lines + ["```", ""]


def changelog_to_markdown(text: str) -> str:
    out = []
    for ln in text.replace("\r\n", "\n").split("\n"):
        if not ln.strip():
            continue
        if indent_of(ln) == 0 and not ln.lstrip().startswith("-"):
            out.append("")
            out.append("## " + ln.strip())
            out.append("")
        else:
            s = ln.strip()
            depth = max(0, (indent_of(ln) - 4) // 4)
            item = s[1:].strip() if s.startswith("-") else s
            out.append("  " * depth + "- " + item)
    return "\n".join(out).strip() + "\n"


# ---------------------------------------------------------------------------
# Page model
# ---------------------------------------------------------------------------

@dataclass
class Page:
    slug: str
    title: str
    section: str
    body: str
    meta: Dict[str, Any] = field(default_factory=dict)

    def render(self) -> str:
        meta = {"title": self.title, "slug": self.slug, "section": self.section}
        meta.update(self.meta)
        return render_front_matter(meta) + self.body.rstrip() + "\n"


def upstream_meta(version: str, source_url: str, edited: bool, extra: Optional[Dict[str, Any]] = None,
                  note: Optional[str] = None) -> Dict[str, Any]:
    meta = {
        "description": None,
        "origin": "groundhog",
        "source_url": source_url,
        "license": GH_LICENSE,
        "author": GH_AUTHOR,
        "attribution": f"Adapted from the groundhog documentation by {GH_AUTHOR} ({GH_REPO_URL}), "
                       f"licensed under the GNU GPL v3 or later.",
        "groundhog_version": version,
        "edited_by_geocore": edited,
    }
    if note:
        meta["geocore_edit_note"] = note
    if extra:
        meta.update(extra)
    return meta


def geocore_meta(version: str, source_url: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    meta = {
        "description": None,
        "origin": "geocore",
        "source_url": source_url,
        "license": GEOCORE_LICENSE,
        "author": GEOCORE_AUTHOR,
        "attribution": f"GeoCore documentation by {GEOCORE_AUTHOR}, licensed under the GNU GPL v3.",
        "groundhog_version": version,
        "edited_by_geocore": False,
    }
    if extra:
        meta.update(extra)
    return meta


# ---------------------------------------------------------------------------
# API page rendering
# ---------------------------------------------------------------------------

def _range_text(pname: str, doc_range: Optional[str], spec: Optional[Dict[str, Any]]) -> str:
    if doc_range:
        return doc_range
    if spec and pname in spec:
        s = spec[pname]
        lo, hi = s.get("min_value"), s.get("max_value")
        if s.get("options"):
            return "one of " + ", ".join(f"`{o}`" for o in s["options"])
        if lo is not None and hi is not None:
            return f"{lo} <= {pname} <= {hi}"
        if lo is not None:
            return f"{pname} >= {lo}"
        if hi is not None:
            return f"{pname} <= {hi}"
    return ""


def _figures_to_md(desc: str, figures: List[Dict[str, Any]], module_rst_dirs: List[str],
                   assets: AssetStore, slug: str) -> str:
    def repl(m):
        fig = figures[int(m.group(1))]
        rel = None
        for d in module_rst_dirs or ["docs"]:
            rel = assets.resolve(fig["path"], d)
            if rel:
                break
        url = assets.use(rel, slug) if rel else None
        cap = fig.get("caption") or ""
        if url:
            return f"![{cap or Path(fig['path']).stem}]({url})" + (f"\n\n*{cap}*" if cap else "")
        if assets.repo:
            return (f"*Figure `{fig['path']}` is referenced by the docstring but is not present in the groundhog "
                    f"repository at `{assets.repo.tag}`.*")
        return f"*Figure `{fig['path']}` is not included (groundhog repository not available to the extractor).*"
    return re.sub(r"%%FIGURE:(\d+)%%", repl, desc)


def render_params_table(doc_params: List[Dict[str, Any]], sig_params: List[Dict[str, Any]],
                        spec: Optional[Dict[str, Any]]) -> str:
    by_name = {p["name"]: p for p in doc_params}
    rows = []
    seen = set()
    for sp in sig_params:
        if sp["kind"] in ("VAR_POSITIONAL", "VAR_KEYWORD"):
            continue
        dp = by_name.get(sp["name"])
        seen.add(sp["name"])
        default = sp["default"] if sp["default"] is not None else ("required" if sp["required"] else "")
        rows.append((sp["name"], dp, default))
    for dp in doc_params:
        if dp["name"] not in seen and not dp["name"].startswith("*"):
            rows.append((dp["name"], dp, dp.get("default_doc") or ""))
    if not rows:
        return ""
    out = ["| Parameter | Unit | Suggested range | Default | Description |",
           "|---|---|---|---|---|"]
    for name, dp, default in rows:
        desc = dp["description"] if dp else "No upstream documentation."
        if dp and dp.get("symbol"):
            desc = f"{desc} (${dp['symbol']}$)" if desc else f"${dp['symbol']}$"
        unit = f"${dp['unit']}$" if dp and dp.get("unit") and dp["unit"] != "-" and re.search(r"[\\^_{]", dp["unit"]) \
            else (dp.get("unit") or "") if dp else ""
        rng = _range_text(name, dp.get("range") if dp else None, spec)
        out.append("| " + " | ".join([f"`{name}`", md_cell(unit), md_cell(rng), md_cell(f"`{default}`" if default and default != "required" else default),
                                      md_cell(desc)]) + " |")
    return "\n".join(out)


def render_returns(ret: Optional[Dict[str, Any]], rtype: Optional[str]) -> str:
    if not ret and not rtype:
        return ""
    out = ["**Returns**", ""]
    if ret and ret.get("description"):
        out.append(ret["description"])
        out.append("")
    if ret and ret.get("items"):
        out.append("| Key | Unit | Description |")
        out.append("|---|---|---|")
        for it in ret["items"]:
            desc = it.get("description") or ""
            if it.get("symbol"):
                desc = f"{desc} (${it['symbol']}$)".strip()
            unit = it.get("unit") or ""
            if unit and re.search(r"[\\^_{]", unit):
                unit = f"${unit}$"
            out.append("| " + " | ".join([md_cell(f"`{it['key']}`" if it.get("key") else ""), md_cell(unit), md_cell(desc)]) + " |")
        out.append("")
    if rtype:
        out.append(f"Return type: `{rtype}`")
        out.append("")
    return "\n".join(out).rstrip()


def availability_badge(entries: List[Dict[str, Any]]) -> str:
    if not entries:
        return ""
    parts = []
    for e in entries:
        path = " › ".join(x for x in (e.get("category"), e.get("submodule"), e.get("title")) if x)
        parts.append(f"[{path}]({page_link('geocore/using/modules', anchor_id(e['id']))})")
    ids = " ".join(e["id"] for e in entries)
    return (f'<span class="gc-badge gc-available" data-geocore-function="{ids}">Available in GeoCore</span> '
            + "; ".join(parts))


def render_callable(d: Dict[str, Any], heading: str, ui: Dict[str, Any], assets: AssetStore, slug: str,
                    rst_dirs: List[str]) -> str:
    doc = d["doc"]
    out = [f'<a id="{d["anchor"]}"></a>', "", f"{heading} `{d['qualname']}`", ""]
    badge = availability_badge(ui["by_target"].get((d["module"], d["qualname"]), []))
    if badge:
        out += [badge, ""]
    out += ["```python", d["signature"], "```", ""]
    desc = _figures_to_md(doc["description_md"], doc["figures"], rst_dirs, assets, slug)
    out.append(desc if desc.strip() else "No upstream documentation.")
    out.append("")
    table = render_params_table(doc["params"], d.get("signature_params", []), d.get("validation"))
    if table:
        out += ["**Parameters**", "", table, ""]
    ret = render_returns(doc["returns"], doc["rtype"])
    if ret:
        out += [ret, ""]
    if doc["raises"]:
        out += ["**Raises**", ""] + [f"- `{r['exception'] or 'Exception'}`: {r['description']}" for r in doc["raises"]] + [""]
    if doc["examples"]:
        out += ["**Example**", ""]
        for ex in doc["examples"]:
            out += ["```python", ex, "```", ""]
    if doc["references"]:
        out += ["**References**", ""] + [f"- {r}" for r in doc["references"]] + [""]
    if d.get("validated"):
        out += ["*Input validation:* this function is wrapped by groundhog's `Validator`. Inputs outside the "
                "validation ranges raise a warning and, by default (`fail_silently=True`), the function returns its "
                "error output (typically `NaN` values) instead of raising.", ""]
    return "\n".join(out)


def render_api_module(mod: Dict[str, Any], ui: Dict[str, Any], assets: AssetStore, slug: str,
                      rst_dirs: List[str], upstream_links: List[Tuple[str, str]], version: str) -> str:
    out = []
    mdoc = mod["doc"]
    out.append(f"Module `{mod['module']}` (groundhog {version}). "
               f"[View source]({gh_blob(mod['source_path'], 'v' + version)}).")
    out.append("")
    if mdoc["description_md"].strip():
        out.append(mdoc["description_md"])
        out.append("")
    if upstream_links:
        out.append("Upstream documentation: " + ", ".join(f"[{t}]({u})" for t, u in upstream_links) + ".")
        out.append("")
    funcs = [m for m in mod["members"] if m["kind"] == "function"]
    classes = [m for m in mod["members"] if m["kind"] == "class"]
    summary = []
    if classes:
        summary.append("**Classes:** " + ", ".join(f"[`{c['name']}`](#{c['anchor']})" for c in classes))
    if funcs:
        summary.append("**Functions:** " + ", ".join(f"[`{f['name']}`](#{f['anchor']})" for f in funcs))
    out += ["\n\n".join(summary), ""]
    for c in classes:
        out.append(f'<a id="{c["anchor"]}"></a>')
        out.append("")
        out.append(f"## class `{c['name']}`")
        out.append("")
        badge = availability_badge(ui["by_target"].get((c["module"], c["qualname"]), []))
        if badge:
            out += [badge, ""]
        out += ["```python", c["signature"], "```", ""]
        cdesc = _figures_to_md(c["doc"]["description_md"], c["doc"]["figures"], rst_dirs, assets, slug)
        if cdesc.strip():
            out += [cdesc, ""]
        if c["init"]:
            out.append(render_callable(c["init"], "###", ui, assets, slug, rst_dirs))
            out.append("")
        if not cdesc.strip() and not (c["init"] and c["init"]["doc"]["description_md"].strip()):
            out += ["No upstream documentation.", ""]
        for meth in c["methods"]:
            out.append(render_callable(meth, "###", ui, assets, slug, rst_dirs))
            out.append("")
    for f in funcs:
        out.append(render_callable(f, "##", ui, assets, slug, rst_dirs))
        out.append("")
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


# ---------------------------------------------------------------------------
# GeoCore generated content
# ---------------------------------------------------------------------------

def geoai_tools_markdown() -> str:
    """List the curated GeoAI tools by statically parsing python-backend/core/geoai/tool_definitions.py."""
    path = REPO_ROOT / "python-backend" / "core" / "geoai" / "tool_definitions.py"
    if not path.exists():
        return "*Tool list unavailable: tool_definitions.py not found.*"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    rows = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and getattr(dec.func, "id", None) == "geoai_tool":
                kw = {k.arg: k.value for k in dec.keywords}
                get = lambda k: kw[k].value if k in kw and isinstance(kw[k], ast.Constant) else ""
                target = ""
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Return) and isinstance(sub.value, ast.Call):
                        f = sub.value.func
                        if isinstance(f, ast.Attribute):
                            target = f.attr
                rows.append((get("name"), get("category"), get("description"), target))
    out = ["| Tool | Category | What it does |", "|---|---|---|"]
    for name, cat, desc, _ in rows:
        out.append(f"| `{name}` | {md_cell(cat)} | {md_cell(desc)} |")
    return "\n".join(out)


GEOAI_EVAL_DIR = REPO_ROOT / "python-backend" / "core" / "geoai" / "eval"
_CANDIDATE_FIELDS = ("key", "display_name", "params", "repo_id", "filename", "size_mb", "license", "tool_format",
                     "finetune_base", "finetune_family", "notes")


def geoai_model_candidates() -> List[Dict[str, Any]]:
    """Statically parse CANDIDATES in core/geoai/eval/benchmark.py (not imported: no app dependencies)."""
    path = GEOAI_EVAL_DIR / "benchmark.py"
    if not path.exists():
        return []
    out = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "Candidate":
            vals = {f: (a.value if isinstance(a, ast.Constant) else None) for f, a in zip(_CANDIDATE_FIELDS, node.args)}
            vals.update({k.arg: k.value.value for k in node.keywords if isinstance(k.value, ast.Constant)})
            out.append(vals)
    return out


def geoai_model_candidates_markdown() -> str:
    rows = geoai_model_candidates()
    if not rows:
        return "*Candidate list unavailable: benchmark.py not found.*"
    out = ["| Model | Parameters | Download | Licence | Tool calls | Notes |", "|---|---|---|---|---|---|"]
    for c in rows:
        out.append(f"| [{md_cell(c['display_name'])}](https://huggingface.co/{c['repo_id']}) | {c['params']} | "
                   f"~{c['size_mb'] / 1024:.1f} GB | {md_cell(c['license'])} | {md_cell(c['tool_format']).replace('<', '&lt;').replace('>', '&gt;')} | "
                   f"{md_cell(c.get('notes') or '')} |")
    return "\n".join(out)


def _pct(v: Any) -> str:
    return "–" if v is None else f"{100 * v:.0f}%"


def _num(v: Any, fmt: str = "{:.2f}") -> str:
    return "–" if v is None else fmt.format(v)


def geoai_model_benchmarks_markdown() -> str:
    """Render the most recent published benchmark leaderboard (run folders starting with '_' are private)."""
    runs = [p for p in (GEOAI_EVAL_DIR / "results" / "benchmark").glob("*/leaderboard.json")
            if not p.parent.name.startswith("_")]
    if not runs:
        return ("No benchmark run has been published yet. Results appear here once the candidate models have been "
                "run through the GeoAI suite with the commands below.")
    lb = json.loads(max(runs, key=lambda p: p.stat().st_mtime).read_text(encoding="utf-8"))
    s = lb.get("settings") or {}
    split = s.get("split") or "test"
    n = max((r.get("n") or 0) for r in lb["rows"]) if lb["rows"] else 0
    out = [
        f"Run `{lb['run_id']}`: {n} examples from the `{split}` split"
        + (f" (stratified subset of {s['limit']})" if s.get("limit") else "")
        + f", {s.get('mode') or 'decision'} mode, `n_ctx` {s.get('n_ctx')}, {s.get('max_tools')} tools offered per "
          f"request, " + ("CPU only" if not s.get("n_gpu_layers") else f"{s['n_gpu_layers']} GPU layers")
        + f", dataset generator {s.get('dataset_generator_version')}. "
        + ("All models answered the same examples." if lb.get("same_examples") else
           "**Warning: the models did not all answer the same examples; rows are not directly comparable.**"),
        "",
        "| Model | Mean score | Strict pass | Tool choice | Arguments | Clarification | Invented inputs | p50 latency (s) | Peak RAM (MB) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in lb["rows"]:
        m = r["metrics"]
        name = r.get("display_name") or r["label"]
        if r["label"] == "heuristic":
            name = "Keyword heuristic (no model)"
        out.append(f"| {md_cell(name)} | {_num(m.get('mean_score'), '{:.3f}')} | {_pct(m.get('strict_pass_rate'))} | "
                   f"{_pct(m.get('tool_selection_accuracy'))} | {_pct(m.get('argument_accuracy'))} | "
                   f"{_pct(m.get('clarification_accuracy'))} | {_pct(m.get('hallucinated_parameter_rate'))} | "
                   f"{_num(m.get('decision_latency_p50_s'), '{:.1f}')} | {_num(m.get('peak_memory_mb'), '{:.0f}')} |")
    cats = sorted({k for r in lb["rows"] for k in (r.get("per_category") or {}) if not k.startswith("turn:")})
    if cats:
        out += ["", "Strict pass rate by category:", "",
                "| Model | " + " | ".join(c.replace("_", " ") for c in cats) + " |",
                "|---|" + "---|" * len(cats)]
        for r in lb["rows"]:
            name = "Keyword heuristic" if r["label"] == "heuristic" else (r.get("display_name") or r["label"])
            out.append(f"| {md_cell(name)} | " + " | ".join(_pct((r.get("per_category") or {}).get(c)) for c in cats) + " |")
    tuned = [r for r in lb["rows"] if r.get("fine_tuned")]
    if not tuned:
        out += ["", "No GeoAI fine-tuned adapter is included in this run yet; all rows are base models."]
    out += ["", "Small subsets give noisy rates: with 40 examples one example is 2.5 percentage points. "
                "Latency and memory depend on the machine the run used."]
    return "\n".join(out)


def modules_catalogue_markdown(ui: Dict[str, Any], api_index: Dict[Tuple[str, str], str]) -> Tuple[str, int, int]:
    out = []
    cat = sub = None
    total = linked = 0
    for e in ui["entries"]:
        if e["category"] != cat:
            cat, sub = e["category"], None
            out += ["", f"## {cat}", ""]
        if e["submodule"] != sub:
            sub = e["submodule"]
            if sub:
                out += ["", f"### {sub}", ""]
        total += 1
        target = tuple(e["target"]) if e.get("target") else None
        link = api_index.get(target) if target else None
        ref = f" — [groundhog `{target[1]}`]({link})" if link else " — No upstream documentation."
        if link:
            linked += 1
        out.append(f'- <a id="{anchor_id(e["id"])}"></a>**{e["title"]}** (`{e["id"]}`){ref}')
    return "\n".join(out).strip() + "\n", total, linked


def eurocode7_markdown() -> str:
    from groundhog.standards.eurocode7.factors import Eurocode7_factoring_STR_GEO
    ec7 = Eurocode7_factoring_STR_GEO()
    out = []
    out += ["## Partial factors on actions (A1, A2)", "", "| Action | A1 | A2 |", "|---|---|---|"]
    for k in ec7.factors_actions["A1"]:
        out.append(f"| {k} | {ec7.factors_actions['A1'][k]} | {ec7.factors_actions['A2'][k]} |")
    out += ["", "## Partial factors on soil parameters (M1, M2)", "", "| Soil parameter | M1 | M2 |", "|---|---|---|"]
    for k in ec7.factors_soil["M1"]:
        out.append(f"| {k} | {ec7.factors_soil['M1'][k]} | {ec7.factors_soil['M2'][k]} |")
    out += ["", "## Partial factors on resistances (R1 to R4)", ""]
    sets = list(ec7.factors_resistance.keys())
    ftypes = list(ec7.factors_resistance[sets[0]].keys())
    for ft in ftypes:
        comps = list(ec7.factors_resistance[sets[0]][ft].keys())
        out += [f"### {ft}", "", "| Component | " + " | ".join(sets) + " |", "|---|" + "---|" * len(sets)]
        for c in comps:
            vals = []
            for s in sets:
                v = ec7.factors_resistance[s].get(ft, {}).get(c, None)
                vals.append("–" if v is None or (isinstance(v, float) and v != v) else str(v))
            out.append(f"| {c} | " + " | ".join(vals) + " |")
        out.append("")
    out += ["## Design approaches", "",
            "`select_design_approach` combines the factor sets as follows:", "",
            "| Design approach | Actions | Soil | Resistances |", "|---|---|---|---|"]
    for da in ["DA1-1", "DA1-2", "DA2", "DA3-1", "DA3-2"]:
        ec = Eurocode7_factoring_STR_GEO()
        ec.select_design_approach(da, "Spread foundation")
        a = next(k for k, v in ec.factors_actions.items() if v is ec.selected_factors_actions)
        m = next(k for k, v in ec.factors_soil.items() if v is ec.selected_factors_soil)
        r = next(k for k, v in ec.factors_resistance.items() if v["Spread foundation"] is ec.selected_factors_resistance)
        out.append(f"| {da} | {a} | {m} | {r} |")
    return "\n".join(out).strip() + "\n"


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def humanize(seg: str) -> str:
    return PACKAGE_TITLES.get(seg, seg.replace("_", " "))


def build(repo_path: Optional[str]) -> Dict[str, Any]:
    print("Walking installed groundhog package ...")
    version, modules = walk_groundhog()
    tag = f"v{version}"
    repo = open_repo(repo_path, version)
    if repo and not repo.license_ok:
        print("  ! groundhog LICENSE is not GPLv3; narrative docs will NOT be imported", file=sys.stderr)
    use_repo = repo if (repo and repo.license_ok) else None
    assets = AssetStore(use_repo)
    ui = load_geocore_ui()

    # clean generated outputs
    if PAGES_DIR.exists():
        shutil.rmtree(PAGES_DIR)
    if GH_ASSETS_DIR.exists():
        shutil.rmtree(GH_ASSETS_DIR)

    pages: Dict[str, Page] = {}

    def add(page: Page):
        if page.slug in pages:
            raise ValueError(f"duplicate slug {page.slug}")
        pages[page.slug] = page

    # ---------------- upstream docs structure (rst) ----------------
    rst_docs: Dict[str, RstDoc] = {}
    module_rsts: Dict[str, List[str]] = {}   # module -> rst paths that document it
    module_titles: Dict[str, str] = {}
    if use_repo:
        for p in sorted((use_repo.root / "docs").rglob("*.rst")):
            rel = p.relative_to(use_repo.root).as_posix()
            rst_docs[rel] = read_rst(use_repo, rel)
        for rel, d in rst_docs.items():
            for directive, target in d.auto:
                mod = target if directive == "automodule" else target.rsplit(".", 1)[0]
                module_rsts.setdefault(mod, []).append(rel)
                if directive == "automodule":
                    module_titles.setdefault(mod, d.title)

    # ---------------- API reference ----------------
    api_modules = [m for m in modules if m["members"]]
    api_index: Dict[Tuple[str, str], str] = {}
    for m in api_modules:
        slug = module_slug(m["module"])
        for mem in m["members"]:
            api_index[(m["module"], mem["qualname"])] = page_link(slug, mem["anchor"])
            if mem["kind"] == "class":
                for meth in mem["methods"]:
                    api_index[(m["module"], meth["qualname"])] = page_link(slug, meth["anchor"])
                if mem["init"]:
                    api_index[(m["module"], mem["init"]["qualname"])] = page_link(slug, mem["init"]["anchor"])
    for m in api_modules:
        slug = module_slug(m["module"])
        title = module_titles.get(m["module"]) or m["module"].split(".")[-1]
        _AUTO_LINKS[("automodule", m["module"])] = (f"groundhog.{m['module'].split('.', 1)[1]}", page_link(slug))
        for mem in m["members"]:
            if mem["kind"] == "class":
                _AUTO_LINKS[("autoclass", f"{m['module']}.{mem['name']}")] = (mem["name"], page_link(slug, mem["anchor"]))
            else:
                _AUTO_LINKS[("autofunction", f"{m['module']}.{mem['name']}")] = (mem["name"], page_link(slug, mem["anchor"]))

    api_nav_children: Dict[str, Any] = {}
    stats = {"modules": 0, "functions": 0, "classes": 0, "methods": 0, "geocore_available": 0}
    for m in api_modules:
        slug = module_slug(m["module"])
        rels = sorted(set(module_rsts.get(m["module"], [])))
        rst_dirs = [str(Path(r).parent.as_posix()) for r in rels]
        upstream_links = [(rst_docs[r].title, rtd_url(r)) for r in rels] if use_repo else []
        body = render_api_module(m, ui, assets, slug, rst_dirs, upstream_links, version)
        funcs = [x for x in m["members"] if x["kind"] == "function"]
        classes = [x for x in m["members"] if x["kind"] == "class"]
        stats["modules"] += 1
        stats["functions"] += len(funcs)
        stats["classes"] += len(classes)
        stats["methods"] += sum(len(c["methods"]) for c in classes)
        avail = []
        for mem in m["members"]:
            quals = [mem["qualname"]] + ([x["qualname"] for x in mem.get("methods", [])] if mem["kind"] == "class" else [])
            for q in quals:
                for e in ui["by_target"].get((m["module"], q), []):
                    avail.append(e["id"])
        stats["geocore_available"] += len(set(avail))
        title = module_titles.get(m["module"]) or m["module"].split(".")[-1]
        desc = m["doc"]["summary"] or f"API reference for groundhog.{m['module'].split('.', 1)[1]}: " \
               f"{len(funcs)} functions, {len(classes)} classes."
        meta = upstream_meta(version, gh_blob(m["source_path"], tag), edited=True, note=(
            "Generated from the docstrings of the installed groundhog package; RST converted to Markdown and "
            "parameter/return tables derived from the docstrings."),
            extra={"module": m["module"],
                   "upstream_docs_urls": [u for _, u in upstream_links] or None,
                   "geocore_available": bool(avail),
                   "geocore_functions": sorted(set(avail)) or None})
        meta["description"] = desc
        add(Page(slug=slug, title=title, section=SECTION_API, body=body, meta=meta))
        # nav tree: package path -> module
        parts = m["module"].split(".")[1:]
        node = api_nav_children
        for seg in parts[:-1]:
            node = node.setdefault(seg, {})
        node.setdefault("__modules__", []).append((title, slug))

    def build_api_nav(tree: Dict[str, Any], prefix: List[str]) -> List[Dict[str, Any]]:
        nodes = []
        for seg in sorted(k for k in tree if k != "__modules__"):
            slug = "groundhog/api/" + "/".join(prefix + [seg])
            children = build_api_nav(tree[seg], prefix + [seg])
            nodes.append({"title": humanize(seg), "slug": slug, "children": children})
            # package index page
            mods = [m for m in api_modules if m["module"].split(".")[1:len(prefix) + 2] == prefix + [seg]]
            lines = [f"Package `groundhog.{'.'.join(prefix + [seg])}` in groundhog {version}.", ""]
            for c in children:
                page_desc = pages[c["slug"]].meta.get("description", "") if c["slug"] in pages else ""
                lines.append(f"- [{c['title']}]({page_link(c['slug'])})" + (f" — {page_desc}" if page_desc else ""))
            meta = upstream_meta(version, f"{GH_REPO_URL}/tree/{tag}/groundhog/" + "/".join(prefix + [seg]),
                                 edited=True, note="Index page generated by GeoCore from the package structure.")
            meta["description"] = f"groundhog {humanize(seg)} package: {len(mods)} documented modules."
            if slug in pages:
                raise ValueError(slug)
            pages[slug] = Page(slug=slug, title=humanize(seg), section=SECTION_API, body="\n".join(lines) + "\n", meta=meta)
        for title, slug in sorted(tree.get("__modules__", []), key=lambda x: x[1]):
            nodes.append({"title": title, "slug": slug})
        return nodes

    api_nav = build_api_nav(api_nav_children, [])
    # API root
    lines = [f"Reference documentation for every public function and class in groundhog {version}, "
             f"generated from the docstrings of the package that GeoCore ships.", "",
             f"{stats['modules']} modules, {stats['functions']} functions, {stats['classes']} classes and "
             f"{stats['methods']} public methods are documented. Items marked **Available in GeoCore** can be run "
             f"from the GeoCore calculation forms.", "",
             "Parameter tables list the unit, suggested (validated) range and default taken from the docstrings; "
             "where a docstring gives no range, the range enforced by groundhog's validator is shown.", ""]
    for n in api_nav:
        lines.append(f"- [{n['title']}]({page_link(n['slug'])})")
    meta = upstream_meta(version, f"{GH_REPO_URL}/tree/{tag}/groundhog", edited=True,
                         note="Index page generated by GeoCore.")
    meta["description"] = f"API reference for groundhog {version}."
    add(Page("groundhog/api", "Groundhog API Reference", SECTION_API, "\n".join(lines) + "\n", meta))

    # structured API data
    dump_json(CONTENT_DIR / "groundhog" / "api.json", {
        "groundhog_version": version, "source": "installed package", "license": GH_LICENSE, "author": GH_AUTHOR,
        "modules": [{k: v for k, v in m.items()} for m in api_modules],
    })

    # ---------------- narrative guides ----------------
    nav_guides: List[Dict[str, Any]] = []
    nav_changelog: List[Dict[str, Any]] = []
    narrative_count = 0
    topic_slugs: Dict[str, str] = {}
    if use_repo:
        def rst_link(target: str) -> Optional[Tuple[str, str]]:
            if target in topic_slugs:
                return (rst_docs[target].title, page_link(topic_slugs[target]))
            if target == "docs/gettingstarted.rst":
                return (rst_docs[target].title, page_link("groundhog/guides/getting-started"))
            return None

        index = rst_docs["docs/index.rst"]
        area_rsts = [t for t in index.toctree if t != "docs/gettingstarted.rst"]
        for rel in area_rsts:
            topic_slugs[rel] = "groundhog/guides/topics/" + slugify(Path(rel).parent.name)

        # introduction (index.rst)
        body = rst_to_markdown(index, use_repo, assets, "groundhog/guides/introduction", rst_link,
                               drop_sections=("Indices and tables",))
        meta = upstream_meta(use_repo.version, gh_blob("docs/index.rst", use_repo.tag), edited=True,
                             note="Converted from reStructuredText. Sphinx-only 'Indices and tables' section removed; "
                                  "raw HTML donation button replaced by a plain link.",
                             extra={"upstream_docs_url": GH_RTD_BASE})
        meta["description"] = "Introduction to groundhog, the geotechnical Python library behind GeoCore's calculations."
        add(Page("groundhog/guides/introduction", "Introduction to groundhog", SECTION_GUIDES, body, meta))

        gs = rst_docs["docs/gettingstarted.rst"]
        body = rst_to_markdown(gs, use_repo, assets, "groundhog/guides/getting-started", rst_link)
        meta = upstream_meta(use_repo.version, gh_blob(gs.path, use_repo.tag), edited=True,
                             note="Converted from reStructuredText.",
                             extra={"upstream_docs_url": rtd_url(gs.path)})
        meta["description"] = "Installing Python and groundhog, and taking the first steps with groundhog functions."
        add(Page("groundhog/guides/getting-started", gs.title, SECTION_GUIDES, body, meta))
        narrative_count += 2

        # topic pages (per documentation area)
        topic_nav = []
        empty_modules = []

        def render_topic(rel: str, level: int, out: List[str]):
            d = rst_docs.get(rel)
            if d is None:
                return
            if level > 1:
                out.append("#" * min(level, 4) + " " + d.title)
                out.append("")
                out.append(f"Upstream page: [{d.title}]({rtd_url(rel)})")
                out.append("")
            for directive, target in d.auto:
                link = link_for_auto(directive, target)
                if directive == "automodule":
                    mod = next((m for m in api_modules if m["module"] == target), None)
                    if link and mod:
                        names = ", ".join(f"[`{mem['name']}`]({api_index[(target, mem['qualname'])]})" for mem in mod["members"])
                        out.append(f"- Module [`{target}`]({link[1]}): {names}")
                    else:
                        empty_modules.append(target)
                        out.append(f"- Module `{target}`: no public functions or classes in groundhog {version}.")
                else:
                    if link:
                        out.append(f"- Class [`{target.rsplit('.', 1)[1]}`]({link[1]}) (`{target.rsplit('.', 1)[0]}`)")
                    else:
                        out.append(f"- `{target}`: No upstream documentation.")
            if d.auto:
                out.append("")
            for child in d.toctree:
                render_topic(child, level + 1, out)

        for rel in area_rsts:
            d = rst_docs[rel]
            out: List[str] = [f"This page mirrors the structure of the upstream groundhog documentation for "
                              f"*{d.title}* and links each topic to the API reference.", ""]
            render_topic(rel, 1, out)
            slug = topic_slugs[rel]
            meta = upstream_meta(use_repo.version, gh_blob(rel, use_repo.tag), edited=True,
                                 note="Upstream toctree/autodoc structure restructured into a single topic page "
                                      "that links to the API reference instead of duplicating it.",
                                 extra={"upstream_docs_url": rtd_url(rel)})
            meta["description"] = f"Overview of groundhog's {d.title.lower()} functionality with links to the API reference."
            add(Page(slug, d.title, SECTION_GUIDES, re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n", meta))
            topic_nav.append({"title": d.title, "slug": slug})
            narrative_count += 1
        meta = upstream_meta(use_repo.version, gh_blob("docs/index.rst", use_repo.tag), edited=True,
                             note="Index page generated by GeoCore from the upstream toctree.")
        meta["description"] = "Topic overview pages following the structure of the groundhog documentation."
        add(Page("groundhog/guides/topics", "Topics", SECTION_GUIDES,
                 "\n".join(f"- [{t['title']}]({page_link(t['slug'])})" for t in topic_nav) + "\n", meta))

        # notebooks
        tut_nav = []
        for nbp in sorted((use_repo.root / "notebooks").glob("*.ipynb")):
            rel = nbp.relative_to(use_repo.root).as_posix()
            slug = "groundhog/tutorials/" + slugify(nbp.stem)
            title, body, _ = notebook_to_markdown(nbp, rel, slug, assets)
            meta = upstream_meta(use_repo.version, gh_blob(rel, use_repo.tag), edited=True,
                                 note="Converted from a Jupyter notebook: Markdown cells kept, code cells shown as code, "
                                      "text and image outputs reproduced, interactive Plotly/HTML outputs omitted.",
                                 extra={"notebook": rel})
            meta["description"] = first_sentence(body.split("```")[0]) or f"groundhog tutorial notebook: {nbp.stem}."
            add(Page(slug, title, SECTION_GUIDES, body, meta))
            tut_nav.append({"title": title, "slug": slug})
            narrative_count += 1
        tl = ["Tutorial and demo notebooks from the groundhog repository, converted to documentation pages. "
              "The code needs groundhog (and for some notebooks, data files from the groundhog repository) to run.", ""]
        tl += [f"- [{t['title']}]({page_link(t['slug'])})" for t in tut_nav]
        meta = upstream_meta(use_repo.version, f"{GH_REPO_URL}/tree/{use_repo.tag}/notebooks", edited=True,
                             note="Index page generated by GeoCore.")
        meta["description"] = "groundhog tutorial and demo notebooks."
        add(Page("groundhog/tutorials", "Tutorials", SECTION_GUIDES, "\n".join(tl) + "\n", meta))

        nav_guides = [
            {"title": "Introduction to groundhog", "slug": "groundhog/guides/introduction"},
            {"title": gs.title, "slug": "groundhog/guides/getting-started"},
            {"title": "Topics", "slug": "groundhog/guides/topics", "children": topic_nav},
            {"title": "Tutorials", "slug": "groundhog/tutorials", "children": tut_nav},
        ]

        # changelog
        ch = use_repo.root / "CHANGES.txt"
        if ch.exists():
            body = (f"Release history of groundhog, copied from `CHANGES.txt` at tag `{use_repo.tag}`. "
                    f"GeoCore ships groundhog {version}; entries above that version were unreleased plans at the time "
                    f"of that tag.\n\n" + changelog_to_markdown(ch.read_text(encoding="utf-8")))
            meta = upstream_meta(use_repo.version, gh_blob("CHANGES.txt", use_repo.tag), edited=True,
                                 note="Plain-text changelog converted to Markdown headings and lists.")
            meta["description"] = "groundhog release history."
            add(Page("changelog/groundhog", "groundhog changelog", SECTION_CHANGELOG, body, meta))
            nav_changelog.append({"title": "groundhog changelog", "slug": "changelog/groundhog"})
            narrative_count += 1

    # ---------------- GeoCore pages ----------------
    geocore_pages: List[Tuple[int, Page]] = []
    generated = {
        "geoai-tools": geoai_tools_markdown,
        "geoai-model-candidates": geoai_model_candidates_markdown,
        "geoai-model-benchmarks": geoai_model_benchmarks_markdown,
        "eurocode7-factors": eurocode7_markdown,
    }
    if GEOCORE_SRC_DIR.exists():
        for src in sorted(GEOCORE_SRC_DIR.glob("*.md")):
            fm, body = split_front_matter(src.read_text(encoding="utf-8"))
            for key, fn in generated.items():
                marker = f"<!-- geocore:generated {key} -->"
                if marker in body:
                    body = body.replace(marker, fn())
            rel = src.relative_to(REPO_ROOT).as_posix()
            meta = geocore_meta(version, geocore_blob(rel),
                                extra={k: v for k, v in fm.items() if k not in ("title", "slug", "section", "nav_order")})
            meta["description"] = fm.get("description")
            page = Page(fm["slug"], fm["title"], fm["section"], body.strip() + "\n", meta)
            geocore_pages.append((int(fm.get("nav_order", 100)), page))
            add(page)
    # generated catalogue of UI calculations
    cat_md, cat_total, cat_linked = modules_catalogue_markdown(ui, api_index)
    intro = (f"GeoCore's calculation browser groups its calculators into the categories below. This list is generated "
             f"from the application's module configuration: {cat_total} calculators, of which {cat_linked} link to the "
             f"groundhog function or class they run.\n")
    meta = geocore_meta(version, geocore_blob("electron-app/src/config/geotechnicalModules.js"),
                        extra={"geocore_available": True})
    meta["description"] = "Every calculator available in GeoCore, with links to the underlying groundhog API reference."
    catalogue = Page("geocore/using/modules", "Calculation catalogue", SECTION_USING, intro + "\n" + cat_md, meta)
    add(catalogue)
    geocore_pages.append((25, catalogue))

    # ---------------- licence page ----------------
    lic_lines = [
        "## GeoCore", "",
        f"GeoCore is developed by {GEOCORE_AUTHOR} and licensed under the GNU General Public License v3.0. "
        f"See the [LICENSE file]({geocore_blob('LICENSE')}).", "",
        "## groundhog", "",
        f"GeoCore's engineering calculations are performed by [groundhog]({GH_REPO_URL}), a general-purpose Python "
        f"library for geotechnical engineering by {GH_AUTHOR}.", "",
        f"> groundhog. A general-purpose Python library for geotechnical engineering. {GH_COPYRIGHT}. "
        "This program is free software: you can redistribute it and/or modify it under the terms of the GNU General "
        "Public License as published by the Free Software Foundation, either version 3 of the License, or (at your "
        "option) any later version.", "",
        f"GeoCore ships groundhog {version}. The groundhog API reference, guides, tutorials and changelog in these docs "
        f"are derived from the groundhog package docstrings and the groundhog repository "
        f"({GH_REPO_URL}, tag `{repo.tag if repo else tag}`" + (f", commit `{repo.commit}`" if repo and repo.commit else "")
        + ") and are redistributed under the same licence. Each page lists its source, author and licence, and states "
          "whether GeoCore edited it.", "",
        "Upstream online documentation: [groundhog.readthedocs.io](https://groundhog.readthedocs.io).", "",
        "### Content not imported", "",
    ]
    for p_, reason in sorted(EXCLUDED_UPSTREAM.items()):
        lic_lines.append(f"- `{p_}`: {reason}")
    for p_ in sorted(SUPERSEDED_UPSTREAM):
        lic_lines.append(f"- `{p_}`: only states that the tutorial moved to the notebooks; the notebook is included instead.")
    lic_lines += ["", "### Figures", "",
                  "Figures are copied from the groundhog repository. Several figures reproduce charts from the "
                  "publications cited in the corresponding function documentation; see those references for the "
                  "original sources.", "",
                  "## Other GeoCore dependencies", "",
                  "GeoCore also uses open-source components such as FastAPI, Pydantic, NumPy, SciPy, pandas, Plotly, "
                  "React and Electron, each under its own licence. GeoAI can optionally run local models through "
                  "llama.cpp (llama-cpp-python); downloaded model weights are covered by their publishers' licences."]
    meta = geocore_meta(version, geocore_blob("website/_content/extract_docs.py"))
    meta["description"] = "Licences and attribution for GeoCore and the groundhog documentation it includes."
    add(Page("license", "License & Credits", SECTION_LICENSE, "\n".join(lic_lines) + "\n", meta))

    # ---------------- nav ----------------
    def gc_nav(section: str) -> List[Dict[str, Any]]:
        return [{"title": p.title, "slug": p.slug} for o, p in sorted(geocore_pages, key=lambda x: (x[0], x[1].slug))
                if p.section == section]

    sections = [
        (SECTION_GETTING_STARTED, "getting-started", gc_nav(SECTION_GETTING_STARTED),
         "Install GeoCore and learn how the application is put together."),
        (SECTION_USING, "using-geocore", gc_nav(SECTION_USING),
         "Run calculations, manage soil profiles and export results."),
        (SECTION_GEOAI, "geoai", gc_nav(SECTION_GEOAI),
         "GeoAI, the local geotechnical assistant inside GeoCore."),
    ]
    if nav_guides:
        sections.append((SECTION_GUIDES, "groundhog/guides", nav_guides,
                         "Narrative documentation and tutorials from the groundhog project."))
    sections.append((SECTION_API, "groundhog/api", api_nav, None))
    if nav_changelog:
        sections.append((SECTION_CHANGELOG, "changelog", nav_changelog, "Release history."))
    sections.append((SECTION_LICENSE, "license", [], None))

    nav_sections = []
    for title, slug, children, blurb in sections:
        if slug not in pages:
            body = (blurb + "\n\n" if blurb else "") + "\n".join(
                f"- [{c['title']}]({page_link(c['slug'])})" + (f" — {pages[c['slug']].meta.get('description')}"
                                                              if pages[c['slug']].meta.get('description') else "")
                for c in children) + "\n"
            is_gh = slug.startswith("groundhog")
            meta = (upstream_meta(version, f"{GH_REPO_URL}/tree/{repo.tag if repo else tag}/docs", edited=True,
                                  note="Section index generated by GeoCore.") if is_gh
                    else geocore_meta(version, geocore_blob("website/_content/extract_docs.py")))
            meta["description"] = blurb
            add(Page(slug, title, title, body, meta))
        node = {"title": title, "slug": slug}
        if children:
            node["children"] = children
        nav_sections.append(node)

    home_lines = ["GeoCore is an offline geotechnical engineering workstation built on the groundhog library. "
                  "These docs cover the application, its GeoAI assistant and the complete groundhog reference.", ""]
    for s in nav_sections:
        d = pages[s["slug"]].meta.get("description")
        home_lines.append(f"- [{s['title']}]({page_link(s['slug'])})" + (f" — {d}" if d else ""))
    meta = geocore_meta(version, geocore_blob("website/_content/extract_docs.py"))
    meta["description"] = "GeoCore documentation home."
    add(Page("index", "GeoCore Documentation", "Home", "\n".join(home_lines) + "\n", meta))

    nav = {"home": {"title": "GeoCore Documentation", "slug": "index"}, "sections": nav_sections}

    # Links to pages that were not built (e.g. guides when no repo clone is given) are reduced to plain text.
    def _unlink(m: "re.Match") -> str:
        target = m.group(2)[len(LINK_PREFIX):].split("#", 1)[0]
        if target.startswith("assets/") or target in pages:
            return m.group(0)
        print(f"  ! link to missing page /docs/{target} rendered as text", file=sys.stderr)
        return m.group(1)
    for page in pages.values():
        page.body = re.sub(r"(?<!!)\[([^\]]+)\]\((/docs/[^)\s]+)\)", _unlink, page.body)

    # ---------------- write ----------------
    for slug, page in sorted(pages.items()):
        write_text(PAGES_DIR / (slug + ".md"), page.render())
    dump_json(CONTENT_DIR / "nav.json", nav)
    search = []
    for slug, page in sorted(pages.items()):
        heads = [re.sub(r"`", "", h).strip() for h in re.findall(r"^#{2,3}\s+(.+)$", page.body, flags=re.M)]
        search.append({"slug": slug, "title": page.title, "section": page.section, "headings": heads,
                       "text": strip_markdown(page.body)[:300]})
    dump_json(CONTENT_DIR / "search-index.json", search)
    if assets.records:
        dump_json(GH_ASSETS_DIR / "manifest.json", sorted(assets.records.values(), key=lambda r: r["path"]))

    counts = {
        "groundhog_version": version,
        "groundhog_repo": ({"tag": repo.tag, "commit": repo.commit, "license_gplv3": repo.license_ok} if repo else None),
        "api_modules": stats["modules"], "api_functions": stats["functions"], "api_classes": stats["classes"],
        "api_methods": stats["methods"], "api_items_available_in_geocore": stats["geocore_available"],
        "narrative_pages": narrative_count,
        "geocore_pages": len(geocore_pages),
        "total_pages": len(pages),
        "images": len(assets.records),
        "ui_calculators": cat_total, "ui_calculators_linked": cat_linked,
        "excluded_upstream": sorted(EXCLUDED_UPSTREAM) if repo else [],
    }
    dump_json(CONTENT_DIR / "build-info.json", counts)
    return counts


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify() -> List[str]:
    errors = []
    nav = json.loads((CONTENT_DIR / "nav.json").read_text(encoding="utf-8"))
    slugs = [nav["home"]["slug"]]

    def walk(nodes):
        for nd in nodes:
            slugs.append(nd["slug"])
            walk(nd.get("children", []))
    walk(nav["sections"])
    if len(slugs) != len(set(slugs)):
        errors.append("duplicate slugs in nav")
    files = {p.relative_to(PAGES_DIR).as_posix()[:-3] for p in PAGES_DIR.rglob("*.md")}
    for s in slugs:
        if s not in files:
            errors.append(f"nav slug without page: {s}")
    for f in sorted(files - set(slugs)):
        errors.append(f"orphan page (not in nav): {f}")
    required = ["title", "slug", "section", "description", "source_url", "license", "attribution",
                "groundhog_version", "edited_by_geocore"]
    for p in sorted(PAGES_DIR.rglob("*.md")):
        fm, body = split_front_matter(p.read_text(encoding="utf-8"))
        rel = p.relative_to(PAGES_DIR).as_posix()[:-3]
        if not fm:
            errors.append(f"front-matter missing/unparseable: {rel}")
            continue
        for k in required:
            if k not in fm:
                errors.append(f"{rel}: missing front-matter field {k}")
        if fm.get("slug") != rel:
            errors.append(f"{rel}: slug mismatch {fm.get('slug')}")
        # internal links must resolve
        for link in re.findall(r"\]\((/docs/[^)#\s]+)(?:#[^)]*)?\)", body):
            target = link[len(LINK_PREFIX):]
            if target.startswith("assets/"):
                if not (GH_ASSETS_DIR / target[len("assets/groundhog/"):].replace("%20", " ")).exists():
                    errors.append(f"{rel}: missing asset {link}")
            elif target not in files:
                errors.append(f"{rel}: broken link {link}")
    return errors


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--groundhog-repo", help="path to a clone of snakesonabrain/groundhog (ideally at the tag "
                                             "matching the installed version)")
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(line_buffering=True)
        except Exception:
            pass
    counts = build(args.groundhog_repo)
    print(json.dumps(counts, indent=2))
    errors = verify()
    if errors:
        print(f"{len(errors)} verification problem(s):", file=sys.stderr)
        for e in errors:
            print("  - " + e, file=sys.stderr)
        return 1
    print("Verification passed: every nav slug has a page, no orphan pages, front-matter parses, links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
