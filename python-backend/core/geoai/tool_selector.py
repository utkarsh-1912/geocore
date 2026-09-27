# Author: Utkarsh Gupta
# License: GPL v3
"""
Tool subset selection for context-constrained local SLMs (AGENTS.md §7, §14).

Only a handful of tool schemas fit in a small model's context window, so the
tools offered for a request are *retrieved*: every registered tool is ranked
with BM25 over a retrieval card built from existing registry / docstring /
metadata text (see ``core.geoai.tool_retrieval``).  Domain inference and the
active form (``context['activeFunction']``) are soft score boosts -- never hard
filters -- and the active function is always offered.
"""

import json
import re
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from core.geoai.tool_registry import tool_registry
from core.geoai.slm_schema_generator import _clean_json_schema, generate_openai_tool_definitions
import core.geoai.tool_retrieval as _retrieval


#: Engineering domains inferred from the request.  Keywords are matched as
#: stemmed phrases ("skin_friction" == "skin friction(s)").
CATEGORY_KEYWORDS = {
    "site_investigation": {"cpt", "spt", "pcpt", "cone", "borehole", "n60", "qc", "ic", "friction_ratio"},
    "shallow_foundations": {"bearing", "settlement", "footing", "shallow", "foundation", "boussinesq", "vesic", "schmertmann"},
    "deep_foundations": {"pile", "shaft", "lcpc", "koppejan", "debeer", "axcap", "skin_friction", "end_bearing"},
    "earth_pressure": {"rankine", "coulomb", "earth", "pressure", "active", "passive", "retaining", "ka", "kp"},
    "excavations": {"rankine", "coulomb", "earth", "pressure", "active", "passive", "retaining", "ka", "kp", "excavation"},
    "soil_dynamics": {"liquefaction", "gmax", "shear_wave", "vs", "cyclic", "dynamic", "darendeli"},
    "phase_relations": {"void", "porosity", "density", "unit_weight", "saturation", "water_content", "gamma"},
    "consolidation": {"consolidation", "settlement", "oedometer", "cv", "isochrone"},
    "pipelines": {"pipeline", "subsea", "contact_width", "penetration", "embedment"},
    "groundwater": {"hydraulic", "conductivity", "permeability", "pumping", "aquifer", "dupuit"},
    "eurocode": {"eurocode", "ec7", "en1997", "partial_factor", "design_approach", "fractile"},
    "research": {"literature", "references", "papers", "publications", "documents", "research",
                 "compare", "comparison", "guidance", "sources", "citation", "library", "evidence"},
}

#: Domain -> markers found in the real registry categories / Groundhog module
#: paths (``groundhog.shallowfoundations.capacity`` -> "shallowfoundations",
#: "capacity").  A tool belongs to a domain if any marker matches.
DOMAIN_MARKERS: Dict[str, Set[str]] = {
    "site_investigation": {"siteinvestigation", "insitutests", "in_situ", "pcpt_correlations", "spt_correlations",
                           "pcpt_processing", "spt_processing"},
    "shallow_foundations": {"shallowfoundations", "shallow_foundations"},
    "deep_foundations": {"deepfoundations", "axialcapacity"},
    "earth_pressure": {"excavations"},
    "excavations": {"excavations"},
    "soil_dynamics": {"soildynamics", "soil_dynamics"},
    "phase_relations": {"classification", "phaserelations"},
    "consolidation": {"consolidation", "onedimensionalconsolidation", "settlement", "compressibility"},
    "pipelines": {"pipelinescables", "pipelines"},
    "groundwater": {"groundwaterflow", "pumpingtests"},
    "eurocode": {"eurocode7"},
    "research": {"research"},
}

#: Ranking constants (tuned on eval_val only; see core/geoai/eval/selector_recall.py).
DOMAIN_BOOST = 0.05          # x best BM25 score, for lexically matching tools in an inferred domain
RESEARCH_BOOST = 1.5         # x best BM25 score, research wording without numeric inputs
CANONICAL_BONUS = 0.10       # relative bonus for curated GeoAI tools over auto-registered duplicates
NAME_WEIGHT = 1.0            # x idf, per query term found in the tool name ("Poncelet", "Hazen")
TARGET_WEIGHT = 1.0          # x idf, per requested-quantity term matching the tool's output (name target)

#: A numeric *input* ("phi = 30", "depth of 10 m", "qc is 8 MPa", "12.5 kPa") -- as opposed to
#: years or labels in research questions ("Robertson 1990", "Eurocode 7", "N60").
_NUMERIC_INPUT = re.compile(
    r"(?:[=:]|\b(?:of|is|was|be|at|to)\b)\s*-?\d|"
    r"-?\d+(?:\.\d+)?\s*(?:%|°|kpa|mpa|kn|m\b|mm\b|cm\b|m/s|m2|m3|deg|kg|t/m|ft|psf|psi|blows)",
    re.IGNORECASE)


def _phrase(keyword: str) -> Tuple[str, ...]:
    return tuple(_retrieval.stem(t) for t in _retrieval.raw_tokens(keyword.replace("_", " ")))


_DOMAIN_PHRASES: Dict[str, List[Tuple[str, ...]]] = {
    domain: sorted({_phrase(k) for k in kws}) for domain, kws in CATEGORY_KEYWORDS.items()
}


_MAX_PHRASE = max(len(p) for phrases in _DOMAIN_PHRASES.values() for p in phrases)


def _ngrams(seq: Sequence[str], max_n: int) -> Set[Tuple[str, ...]]:
    return {tuple(seq[i:i + n]) for n in range(1, max_n + 1) for i in range(len(seq) - n + 1)}


def infer_categories(query: str) -> List[str]:
    """Infer engineering domains from the request (stemmed keyword phrases).

    Returns domain names sorted by number of matching keywords (ties keep the
    ``CATEGORY_KEYWORDS`` order).
    """
    grams = _ngrams([_retrieval.stem(t) for t in _retrieval.raw_tokens(query)], _MAX_PHRASE)
    scores = {}
    for domain, phrases in _DOMAIN_PHRASES.items():
        hits = sum(1 for p in phrases if p in grams)
        if hits:
            scores[domain] = hits
    return [d for d, _ in sorted(scores.items(), key=lambda kv: -kv[1])]


def _tool_markers(tool: Any) -> Set[str]:
    module = getattr(getattr(tool, "func", None), "__module__", "") or ""
    return {getattr(tool, "category", "") or ""} | set(module.split("."))


_MATH_BLOCK = re.compile(r"\s*\.\. math::.*", re.S)
_MATH_ROLE = re.compile(r":math:`([^`]*)`")
_HTML_TAG = re.compile(r"<[^>]+>")


def _compact_text(text: str) -> str:
    """Drop Sphinx ``.. math::`` blocks and unwrap ``:math:`x``` / HTML from docstring-derived text."""
    t = _MATH_BLOCK.sub("", text)
    t = _MATH_ROLE.sub(lambda m: m.group(1), t)
    t = _HTML_TAG.sub("", t)
    return re.sub(r"\s+", " ", t).strip()


def _compact_schema_descriptions(obj: Any, _in_properties: bool = False) -> Any:
    """Recursively compact every ``description`` string of a JSON schema and drop the
    auto-generated Pydantic ``title`` of each property (token budget, §23)."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k == "title" and isinstance(v, str) and not _in_properties:
                continue
            if k == "description" and isinstance(v, str) and not _in_properties:
                out[k] = _compact_text(v)
            else:
                out[k] = _compact_schema_descriptions(v, _in_properties=(k == "properties"))
        return out
    if isinstance(obj, list):
        return [_compact_schema_descriptions(v) for v in obj]
    return obj


def format_tools_for_prompt(tools: List[dict]) -> List[dict]:
    """
    Takes tool dicts from the registry and formats them into the OpenAI tool-calling spec.
    Strips overly verbose descriptions (first sentence of the tool description; no
    LaTeX math blocks in parameter descriptions) to save tokens.
    Ensures all schemas are JSON-serializable (no NaN/Inf).
    """
    formatted = []
    for tool in tools:
        # Normalize input whether it came from generate_openai_tool_definitions or tool_registry
        if "type" in tool and "function" in tool:
            func = tool["function"]
            name = func.get("name", "")
            desc = func.get("description", "")
            params = func.get("parameters", {})
        else:
            name = tool.get("name", "")
            desc = tool.get("description", "")
            params = tool.get("input_schema", {})

        # Strip long descriptions (keep first sentence roughly)
        short_desc = desc
        if short_desc:
            sentences = [s.strip() for s in short_desc.split(". ") if s.strip()]
            if sentences:
                short_desc = sentences[0]
                if not short_desc.endswith("."):
                    short_desc += "."

        cleaned_params = _compact_schema_descriptions(_clean_json_schema(params))

        formatted.append({
            "type": "function",
            "function": {
                "name": name,
                "description": short_desc,
                "parameters": cleaned_params
            }
        })

    return formatted


def _index() -> "_retrieval.ToolRetrievalIndex":
    # Module globals are looked up at call time so callers may substitute a registry view
    # (see training.scaleup._cached_tool_definitions).
    return _retrieval.get_index(tool_registry, generate_openai_tool_definitions, format_tools_for_prompt)


def rank_tools(query: str, context: Optional[Dict[str, Any]] = None) -> List[Tuple[str, float]]:
    """Rank registered tools for ``query``; returns ``(name, score)`` with score > 0, best first.

    Deterministic: ties are broken by curated-before-auto-registered, then
    registry order.
    """
    index = _index()
    tools = tool_registry._tools
    query = query or ""

    scores = index.score(query, name_weight=NAME_WEIGHT, target_weight=TARGET_WEIGHT)
    top = max(scores) if scores else 0.0

    if top > 0:
        # Soft boosts (never filters).  A literature/document question about a topic
        # ("guidance on pile skin friction") favours research tools over the topic's
        # calculators; otherwise inferred engineering domains are favoured.
        research = "~research" in index.analyze_query(query) and not _NUMERIC_INPUT.search(query)
        domains = [] if research else [d for d in infer_categories(query) if d != "research"]
        markers: Set[str] = set().union(*(DOMAIN_MARKERS.get(d, set()) for d in domains)) if domains else set()
        for i, name in enumerate(index.names):
            if scores[i] <= 0:
                continue
            tool_markers = _tool_markers(tools[name]) if name in tools else set()
            if markers and tool_markers & markers:
                scores[i] += DOMAIN_BOOST * top
            if research and "research" in tool_markers:
                scores[i] += RESEARCH_BOOST * top
            if index.cards[i].canonical:
                scores[i] *= 1.0 + CANONICAL_BONUS

    active = (context or {}).get("activeFunction")
    ranked = [(name, scores[i]) for i, name in enumerate(index.names) if scores[i] > 0 and name != active]
    if not ranked:
        # Nothing matched lexically: offer curated tools first (registry order).
        ranked = [(c.name, 0.0) for c in index.cards if c.canonical and c.name != active]
    ranked.sort(key=lambda item: (-item[1], not index.cards[index.position[item[0]]].canonical,
                                  index.position[item[0]]))
    if active and active in index.position:
        ranked.insert(0, (active, float("inf")))   # the open form always gets a slot
    return ranked


#: Rough characters-per-token ratio used for schema budgeting (same as the agent tests).
CHARS_PER_TOKEN = 3.5


def schema_tokens(tool: dict) -> float:
    """Approximate prompt tokens of one formatted tool schema."""
    return len(json.dumps(tool)) / CHARS_PER_TOKEN


def select_relevant_tools(query: str, context: Optional[Dict[str, Any]] = None, max_tools: int = 20, *,
                          max_schema_tokens: Optional[float] = None) -> List[dict]:
    """
    Select the ``max_tools`` most relevant registered tools for ``query`` and
    return them in OpenAI tool-calling format (see ``format_tools_for_prompt``).

    ``max_schema_tokens`` optionally caps the approximate prompt size of the
    returned schemas: lower-ranked tools that would exceed it are skipped (the
    best-ranked tool, e.g. the active form, is always kept).
    """
    index = _index()
    limit = max(0, int(max_tools))
    ranked = rank_tools(query, context)
    if max_schema_tokens is None:
        return [index.prompt_tool(n) for n, _ in ranked[:limit] if n in index.definitions]

    selected: List[dict] = []
    used = 0.0
    for name, _ in ranked[: 4 * limit]:          # don't dig deep into irrelevant tools for small ones
        if len(selected) >= limit:
            break
        if name not in index.definitions:
            continue
        tool = index.prompt_tool(name)
        cost = schema_tokens(tool)
        if selected and used + cost > max_schema_tokens:
            continue
        used += cost
        selected.append(tool)
    return selected
