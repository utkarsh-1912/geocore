# Author: Utkarsh Gupta
# License: GPL v3
"""
Lexical retrieval index over the GeoAI Tool Registry (AGENTS.md §7-§8, §14).

Each registered tool gets a retrieval *card* assembled from data that already
exists -- nothing is re-declared here:

* the tool name (snake_case / camelCase / concatenated Groundhog names split
  into words, e.g. ``earthpressurecoefficients_rankine``);
* the registry description;
* parameter names, descriptions and units from the tool's input schema;
* returned quantities, extended text and references from the wrapped
  Groundhog docstring;
* method / standard / assumptions from ``tool_metadata.TOOL_METADATA``;
* the Groundhog module path and registry category.

Text is normalised deterministically (lower case, identifier splitting,
British/American spelling, a tiny suffix stemmer) and enriched with *concept*
tokens from a small explicit geotechnical synonym table plus the parameter
synonyms of ``context_resolver.PROPERTY_SYNONYMS`` (``Ic`` <-> "soil behaviour
type index", ``k`` <-> "permeability", ...).  Cards are ranked with Okapi BM25
(field weights are applied as term-frequency multipliers, i.e. BM25F-lite).

The index is pure Python: ~230 short documents are ranked in well under a
millisecond, the tokeniser has to be custom anyway (synonym phrases, identifier
splitting), and no SQLite connection has to be managed.  It is built lazily
once and rebuilt only when the registry's tool set changes.
"""

import functools
import json
import inspect
import math
import re
import threading
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------------

#: Words that carry no tool-selection signal (function words, request verbs,
#: project boiler-plate).  Applied after stemming, to both queries and cards.
_STOPWORDS_RAW = """
a an the of for with and or to from in on at by as is are be been was were it its this that these those
if then than so such via per into onto over under about also only very more most much many some any
what which who how why when where whose can could would should will shall may might must do does did
i we you our your my me us they them their please need want like let
calculate compute estimate determine find get obtain evaluate work out run perform give tell show return
value values data input inputs given using use used based following current project parameter
parameters result results number
"""

#: Single letters (k, e, n, w, ...) are never index terms on their own; they
#: only count inside synonym phrases (e.g. "k" -> ~permeability).
_MIN_TOKEN_LEN = 2

_SPELLING = {
    "behaviour": "behavior", "colour": "color", "analyse": "analyze", "analysed": "analyzed",
    "modelling": "modeling", "modelled": "modeled", "centre": "center", "metre": "meter",
    "metres": "meters", "fibre": "fiber", "litre": "liter", "grey": "gray", "labour": "labor",
    "sulphate": "sulfate", "programme": "program", "travelling": "traveling",
}

# Greek-letter / symbol spellings used in docstrings and prompts.
_SYMBOL_ALIASES = {"varphi": "phi", "vartheta": "theta", "varepsilon": "epsilon"}


def _british_to_american(word: str) -> str:
    if word in _SPELLING:
        return _SPELLING[word]
    # normalise / normalised / normalising / normalisation -> -ize forms
    m = re.fullmatch(r"([a-z]{4,})is(e|es|ed|ing|ation|ations)", word)
    if m:
        return f"{m.group(1)}iz{m.group(2)}"
    if len(word) > 5 and word.endswith("our"):
        return word[:-3] + "or"
    return word


@functools.lru_cache(maxsize=8192)
def stem(word: str) -> str:
    """Tiny deterministic English suffix stripper (Porter-lite).

    Only has to map inflections of the same word onto one key, e.g.
    ``settlement/settle/settlements``, ``calculated/calculation``,
    ``normalised/normalization``, ``stresses/stress``, ``behaviour/behavior``.
    """
    w = word
    if len(w) <= 3 or not w.isalpha():
        return _british_to_american(w)
    # 1. plurals, then British -> American spelling ("behaviours" -> "behaviour" -> "behavior")
    if w.endswith("ies") and len(w) > 4:
        w = w[:-3] + "y"
    elif w.endswith("sses"):
        w = w[:-2]
    elif w.endswith("s") and not w.endswith(("ss", "us", "is")):
        w = w[:-1]
    w = _british_to_american(w)
    # 2. -ing / -ed (+ undouble "embedded" -> "embed")
    for suf in ("ing", "ed"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[: -len(suf)]
            if len(w) > 3 and w[-1] == w[-2] and w[-1] not in "lsz":
                w = w[:-1]
            break
    # 3. derivational suffixes
    if w.endswith("ification"):
        w = w[:-9] + "ify"
    elif w.endswith("ifi") and len(w) > 5:          # classified -> classifi (after -ed)
        w = w[:-1] + "y"
    elif w.endswith("ssion"):
        w = w[:-3]
    elif w.endswith("ction"):
        w = w[:-3]
    elif w.endswith("ation") and len(w) > 6:
        w = w[:-5] + "ate"
    for suf in ("ment", "ness", "ity"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            w = w[: -len(suf)]
            break
    # 4. trailing e, and -izate -> -iz (normalization == normalize)
    if len(w) > 4 and w.endswith("e"):
        w = w[:-1]
    if w.endswith("izat"):
        w = w[:-2]
    return w


_MATH_ROLE = re.compile(r":math:`([^`]*)`")
_MATH_BLOCK = re.compile(r"\.\. math::.*?(?=:param|:return|Reference|\Z)", re.S)
_HTML_TAG = re.compile(r"<[^>]+>")
_LATEX_CMD = re.compile(r"\\(prime|left|right|circ|cdot|mathrm|text|frac|quad|,)")


def _collapse_symbol(expr: str) -> str:
    """``N_q`` -> ``Nq N q``; ``\\phi_p^{\\prime}`` -> ``phip phi p``; ``m_v`` -> ``mv m v``."""
    e = _LATEX_CMD.sub(" ", expr)
    e = e.replace("\\", " ").replace("{", "").replace("}", "").replace("^", "")
    e = e.replace("'", "").strip()
    collapsed = re.sub(r"[_\s]+", "", e)
    # Single-letter pieces ("K" of K_{ac}) would collide with real symbols (k = permeability).
    pieces = [p for p in re.split(r"[_\s]+", e) if len(p) >= 2 and p != collapsed]
    return " " + " ".join([collapsed, *pieces]) + " "


def clean_doc_text(text: str) -> str:
    """Strip Sphinx math blocks / roles and HTML from docstring-derived text."""
    if not text:
        return ""
    t = _MATH_BLOCK.sub(" ", text)
    t = _MATH_ROLE.sub(lambda m: _collapse_symbol(m.group(1)), t)
    t = _HTML_TAG.sub(" ", t)
    return t


_CAMEL_1 = re.compile(r"([a-z0-9])([A-Z])")
_CAMEL_2 = re.compile(r"([A-Z]+)([A-Z][a-z])")


def split_identifier(name: str) -> List[str]:
    """``earthpressurecoefficients_rankine`` -> [..]; ``AxCapCalculation`` -> [ax, cap, calculation]."""
    s = _CAMEL_2.sub(r"\1 \2", _CAMEL_1.sub(r"\1 \2", name))
    parts = []
    for p in re.split(r"[^A-Za-z0-9]+", s.lower()):
        if p:
            parts.append(p)
            m = re.fullmatch(r"([a-z]{4,})\d+", p)     # "eurocode7" -> also "eurocode" (keeps n60, d10, k0)
            if m:
                parts.append(m.group(1))
    return parts


def raw_tokens(text: str) -> List[str]:
    """Lower-case alphanumeric tokens (no stemming, no stop-word removal)."""
    out = re.findall(r"[a-z0-9]+", (text or "").lower())
    return [_SYMBOL_ALIASES.get(t, t) for t in out]


def _is_number(tok: str) -> bool:
    return tok.isdigit()


STOPWORDS = frozenset(stem(w) for w in _STOPWORDS_RAW.split()) | frozenset(_STOPWORDS_RAW.split())

# ---------------------------------------------------------------------------
# Concepts (synonyms / abbreviations)
# ---------------------------------------------------------------------------

#: Explicit geotechnical synonym / abbreviation groups.  Only gaps not covered
#: by ``context_resolver.PROPERTY_SYNONYMS``.  Each phrase is matched as a
#: stemmed token sequence; a match adds the concept token ``~<group>``.
GEOTECH_SYNONYMS: Dict[str, Tuple[str, ...]] = {
    "relative_density": ("relative density", "dr", "density index"),
    "cone_resistance": ("cone resistance", "cone tip resistance", "tip resistance", "qc", "qt",
                        "corrected cone resistance"),
    "sleeve_friction": ("sleeve friction", "fs", "local friction"),
    "friction_ratio": ("friction ratio", "rf", "fr"),
    "sbt_index": ("soil behaviour type index", "soil behavior type", "soil behaviour type", "ic", "sbt",
                  "sbtn", "behaviour index", "behaviour type"),
    "cpt": ("cpt", "cptu", "pcpt", "cone penetration test", "cone penetration", "piezocone", "cone test",
            "cone data"),
    "spt": ("spt", "standard penetration test", "blow count", "n60", "n1 60", "spt n", "n value"),
    "undrained_strength": ("su", "cu", "undrained shear strength", "undrained strength", "undrained cohesion"),
    "friction_angle": ("phi", "friction angle", "angle of shearing resistance", "angle of internal friction",
                       "shearing resistance angle", "internal friction angle"),
    "gmax": ("gmax", "g0", "small strain shear modulus", "maximum shear modulus", "small strain stiffness",
             "initial shear modulus"),
    "shear_wave_velocity": ("vs", "shear wave velocity", "shear velocity", "shear wave"),
    "active_pressure": ("ka", "active earth pressure", "active pressure coefficient"),
    "passive_pressure": ("kp", "passive earth pressure", "passive pressure coefficient"),
    "at_rest_pressure": ("k0", "at rest", "earth pressure at rest", "at rest earth pressure"),
    "earth_pressure_coefficient": ("ka", "kp", "k0", "earth pressure coefficient", "lateral earth pressure"),
    "permeability": ("k", "hydraulic conductivity", "permeability", "coefficient of permeability"),
    "liquefaction": ("csr", "crr", "cyclic stress ratio", "cyclic resistance ratio", "liquefaction",
                     "liquefaction triggering", "factor of safety against liquefaction"),
    "water_content": ("water content", "moisture content", "natural water content"),
    "unit_weight": ("unit weight", "gamma", "unit weight of soil"),
    "saturation": ("degree of saturation", "saturation", "sr"),
    "specific_gravity": ("specific gravity", "gs", "specific gravity of solids"),
    "compression_index": ("compression index", "cc"),
    "volume_compressibility": ("mv", "coefficient of volume compressibility", "volume compressibility",
                               "compressibility", "constrained modulus"),
    "ocr": ("ocr", "overconsolidation ratio", "over consolidation ratio", "overconsolidated"),
    "effective_overburden": ("vertical effective stress", "effective overburden", "effective overburden stress",
                             "overburden stress", "sigma v0", "sigmav0", "effective vertical stress"),
    "pore_pressure": ("u2", "pore pressure", "pore water pressure", "excess pore pressure"),
    "grain_size": ("d10", "effective grain size", "effective size", "grain size"),
    "footing": ("footing", "foundation", "shallow foundation", "spread footing", "raft"),
    "pile": ("pile", "deep foundation", "shaft", "caisson"),
    "pipeline": ("pipeline", "pipe", "subsea pipeline", "cable"),
    "embedment": ("embedment", "penetration", "embedment depth", "penetration depth"),
    "point_load": ("point load", "concentrated load", "column load", "concentrated force"),
    "strip_load": ("strip load", "strip footing", "line load", "strip foundation"),
    "stress_increase": ("stress increase", "stress increment", "stress distribution", "induced stress",
                        "stress redistribution", "vertical stress"),
    "pumping_test": ("pumping test", "pumping well", "observation well", "drawdown", "aquifer", "well test"),
    "bearing_capacity_factor": ("bearing capacity factor", "nq", "ngamma", "nc factor"),
    "bearing_capacity": ("bearing capacity", "ultimate bearing", "bearing resistance"),
    "void_ratio": ("void ratio", "voidratio"),
    "porosity": ("porosity",),
    "consolidation": ("consolidation", "oedometer", "primary consolidation"),
    "normally_consolidated": ("normally consolidated", "nc clay"),
    "research": ("literature", "reference", "references", "paper", "papers", "publication", "publications",
                 "document", "documents", "report", "reports", "guidance", "research", "source", "sources",
                 "compare", "comparison", "versus", "review", "citation", "cite", "technical note", "library",
                 "evidence", "summarise", "summary", "search", "state of the art", "best practice", "say about",
                 "says about"),
}

_CONCEPT_PREFIX = "~"


def _phrase_key(phrase: str) -> Tuple[str, ...]:
    return tuple(stem(t) for t in raw_tokens(phrase))


def _load_property_synonyms() -> Dict[str, Tuple[str, ...]]:
    """Reuse ``context_resolver.PROPERTY_SYNONYMS`` (column labels -> canonical parameter)."""
    try:
        from core.geoai.context_resolver import PROPERTY_SYNONYMS
    except Exception:  # pragma: no cover - optional dependency chain
        return {}
    groups: Dict[str, Tuple[str, ...]] = {}
    for canon, syns in PROPERTY_SYNONYMS.items():
        phrases = []
        for s in [canon, *syns]:
            s = re.sub(r"\[[^\]]*\]", " ", s)          # drop "[kPa]" unit labels
            words = raw_tokens(s.replace("_", " "))
            # single letters ("c", "e", "n", "v") are far too ambiguous as phrases
            if not words or (len(words) == 1 and len(words[0]) < 2):
                continue
            phrases.append(" ".join(words))
        if phrases:
            groups[canon.lower()] = tuple(dict.fromkeys(phrases))
    return groups


def concept_groups() -> Dict[str, Tuple[str, ...]]:
    """``GEOTECH_SYNONYMS`` extended with ``PROPERTY_SYNONYMS``.

    Property groups that share a phrase with each other are merged; a merged
    group sharing a phrase with a GeoTech group is folded into it, so one
    physical quantity yields one concept token (``phi_eff``, ``friction_angle``
    and "friction angle" all become ``~friction_angle``).
    """
    groups: Dict[str, List[str]] = {k: list(v) for k, v in GEOTECH_SYNONYMS.items()}
    owner: Dict[Tuple[str, ...], str] = {}
    for concept in sorted(groups):
        for p in groups[concept]:
            owner.setdefault(_phrase_key(p), concept)

    merged: List[Tuple[str, Dict[Tuple[str, ...], str]]] = []   # (name, {phrase key: raw phrase})
    for canon, phrases in sorted(_load_property_synonyms().items()):
        keyed = {_phrase_key(p): p for p in phrases}
        hits = [m for m in merged if m[1].keys() & keyed.keys()]
        if hits:
            hits[0][1].update(keyed)
            for other in hits[1:]:
                hits[0][1].update(other[1])
                merged.remove(other)
        else:
            merged.append((canon, keyed))

    for canon, keyed in merged:
        owners = sorted({owner[k] for k in keyed if k in owner})
        target = owners[0] if owners else f"prop_{canon}"
        groups.setdefault(target, []).extend(keyed[k] for k in sorted(keyed))
    return {k: tuple(dict.fromkeys(v)) for k, v in groups.items()}


class ConceptMatcher:
    """Adds one ``~concept`` token per (non-overlapping) synonym phrase occurrence."""

    def __init__(self, groups: Dict[str, Sequence[str]]):
        self._by_first: Dict[str, List[Tuple[Tuple[str, ...], str]]] = defaultdict(list)
        for concept, phrases in sorted(groups.items()):
            for seq in sorted({_phrase_key(p) for p in phrases}):
                if seq:
                    self._by_first[seq[0]].append((seq, _CONCEPT_PREFIX + concept))
        for lst in self._by_first.values():
            lst.sort(key=lambda item: (-len(item[0]), item[1]))

    def concepts(self, stems: Sequence[str]) -> List[str]:
        found: List[str] = []
        covered_until: Dict[str, int] = {}
        for i, tok in enumerate(stems):
            for seq, concept in self._by_first.get(tok, ()):
                if covered_until.get(concept, -1) > i:
                    continue                         # "effective friction angle" != 2 x friction angle
                if tuple(stems[i:i + len(seq)]) == seq:
                    found.append(concept)
                    covered_until[concept] = i + len(seq)
        return found


_MATCHER: Optional[ConceptMatcher] = None
_MATCHER_LOCK = threading.Lock()


def concept_matcher() -> ConceptMatcher:
    global _MATCHER
    if _MATCHER is None:
        with _MATCHER_LOCK:
            if _MATCHER is None:
                _MATCHER = ConceptMatcher(concept_groups())
    return _MATCHER


# ---------------------------------------------------------------------------
# Compound splitting ("bulkunitweight" -> bulk unit weight)
# ---------------------------------------------------------------------------

_SHORT_PIECES = frozenset({"su", "cu", "k0", "mv", "cc", "nq", "nc", "dr", "ic", "qc", "fs", "vs", "cv",
                           "api", "spt", "cpt", "ocr", "psd", "d10", "n60", "dss"})


def segment_compound(token: str, vocab: Iterable[str]) -> List[str]:
    """Split a concatenated identifier into known words.

    ``earthpressurecoefficients`` -> ``earth pressure coefficients``.  Pieces
    must be vocabulary words of >= 3 letters (or a known short symbol) and not
    stop words; the split with the most pieces wins (ties: longer first
    piece).  Returns ``[]`` when no split into >= 2 pieces exists.
    """
    n = len(token)
    if n < 6:
        return []
    vocab = vocab if isinstance(vocab, (set, frozenset)) else set(vocab)

    def ok(piece: str) -> bool:
        return (piece in vocab and piece != token and piece not in STOPWORDS
                and (len(piece) >= 3 or piece in _SHORT_PIECES))

    # best[i] = (-pieces, piece lengths negated, pieces) for token[:i]; lexicographic min wins.
    best: List[Optional[Tuple[int, Tuple[int, ...], List[str]]]] = [None] * (n + 1)
    best[0] = (0, (), [])
    for end in range(1, n + 1):
        for start in range(end):
            prev = best[start]
            piece = token[start:end]
            if prev is None or not ok(piece):
                continue
            cand = (prev[0] - 1, prev[1] + (-len(piece),), prev[2] + [piece])
            if best[end] is None or cand[:2] < best[end][:2]:
                best[end] = cand
    res = best[n]
    return res[2] if res and len(res[2]) >= 2 else []


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------

def analyze(text: str, vocab: Optional[frozenset] = None, identifier: bool = False) -> List[str]:
    """Text -> list of index terms (stems without stop words/numbers + ``~concept`` tokens)."""
    words: List[str] = []
    if identifier:
        for part in split_identifier(text):
            words.append(part)
            if vocab:
                words.extend(segment_compound(part, vocab))
    else:
        for tok in raw_tokens(text):
            words.append(tok)
            if vocab and len(tok) >= 8 and tok not in vocab:
                words.extend(segment_compound(tok, vocab))
    stems = [stem(w) for w in words]
    terms = [s for s in stems if len(s) >= _MIN_TOKEN_LEN and not _is_number(s) and s not in STOPWORDS]
    terms.extend(concept_matcher().concepts(stems))
    return terms


# ---------------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------------

#: Field weights (term-frequency multipliers).  Tuned on eval_val only.
FIELD_WEIGHTS: Dict[str, float] = {
    "name": 3.0,
    "description": 2.0,
    "outputs": 1.5,
    "parameters": 1.0,
    "metadata": 1.0,
    "module": 1.0,
    "extended": 0.5,
}


@dataclass
class ToolCard:
    name: str
    category: str
    canonical: bool
    fields: Dict[str, List[str]] = field(default_factory=dict)
    #: Terms of the quantity the tool *returns*, read from its name
    #: (``porosity_voidratio`` -> porosity; ``calculate_void_ratio_from_porosity`` -> void ratio).
    target: List[str] = field(default_factory=list)

    def weighted_terms(self) -> Counter:
        tf: Counter = Counter()
        for fname, terms in self.fields.items():
            w = FIELD_WEIGHTS.get(fname, 1.0)
            for t in terms:
                tf[t] += w
        return tf


def _split_docstring(doc: str) -> Dict[str, str]:
    """Split a Groundhog/Sphinx docstring into summary / extended / returns / reference text."""
    doc = inspect.cleandoc(doc or "")
    if not doc:
        return {}
    ref = ""
    m = re.search(r"\n\s*Reference[s]?\s*[-:]", doc)
    if m:  # keep the cited work (author, year, title) but not the word "Reference"
        doc, ref = doc[: m.start()], doc[m.end():]
    returns = ""
    m = re.search(r":returns?:", doc)
    if m:
        doc, returns = doc[: m.start()], doc[m.end():]
    body = re.split(r":param\s", doc, maxsplit=1)[0]
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    return {
        "summary": paragraphs[0] if paragraphs else "",
        "extended": " ".join(paragraphs[1:]),
        "returns": returns,
        "reference": ref,
    }


def _returned_quantities(returns: str) -> str:
    """Keep only the quantity names/descriptions of ``- 'Nq [-]': Bearing capacity factor``."""
    keys = re.findall(r"-\s*'([^']+)'\s*:\s*([^\n]*)", returns)
    if keys:
        return " ".join(f"{re.sub(r'\[[^\]]*\]', ' ', k)} {d}" for k, d in keys)
    return returns


def is_canonical_tool(tool: Any) -> bool:
    """Hand-written GeoAI tools (tool_definitions.py etc.) rather than auto-registered Groundhog ones."""
    module = getattr(getattr(tool, "func", None), "__module__", "") or ""
    return module.startswith("core.geoai")


def build_card_texts(tool: Any, parameters: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    """Collect the raw texts of a tool card.

    Returns ``(free_text_fields, identifier_fields)``; the latter are split as
    identifiers (snake/camel/concatenated).
    """
    from core.geoai.tool_metadata import TOOL_METADATA

    func = getattr(tool, "func", None)
    doc = _split_docstring(getattr(func, "__doc__", "") or "")
    params = (parameters or {}).get("properties", {}) if isinstance(parameters, dict) else {}

    param_text = []
    for pname, spec in params.items():
        if not isinstance(spec, dict):
            continue
        desc = re.split(r"-?\s*Suggested range:", str(spec.get("description", "")), maxsplit=1)[0]
        param_text.append(clean_doc_text(desc))
        unit = spec.get("unit")
        if unit:
            param_text.append(clean_doc_text(str(unit)))

    meta = TOOL_METADATA.get(tool.name) or {}
    meta_text = " ".join(
        [str(meta.get("method", "")), str(meta.get("standard", ""))]
        + [str(a) for a in meta.get("assumptions", [])]
        + [str(k) for k in (meta.get("output_units") or {})]
    )

    module = getattr(func, "__module__", "") or ""
    module_parts = [] if module.startswith("core.") else module.split(".")[1:]

    free = {
        "description": clean_doc_text(tool.description or ""),
        "outputs": clean_doc_text(_returned_quantities(doc.get("returns", ""))),
        "parameters": " ".join(param_text),
        "metadata": meta_text,
        "extended": clean_doc_text(" ".join([doc.get("extended", ""), doc.get("reference", "")])),
    }
    ident = {
        "name": [tool.name],
        "parameters": list(params.keys()),
        "module": module_parts + [tool.category or ""],
    }
    return free, ident


_NAME_VERBS = frozenset({"calculate", "compute", "derive", "classify", "normalize", "normalise", "estimate",
                         "get", "run", "search", "index"})


def name_target(name: str) -> str:
    """The returned quantity encoded in a tool name.

    Curated names read ``<verb>_<target>_from_<inputs>``; Groundhog names read
    ``<target>_<inputs>_<author>``; CamelCase class names are taken whole.
    """
    parts = [p for p in name.split("_") if p]
    if not parts:
        return name
    if parts[0].lower() in _NAME_VERBS:
        parts = parts[1:] or parts
        if "from" in parts:
            parts = parts[: parts.index("from")]
        return " ".join(parts)
    if "from" in parts:
        return " ".join(parts[: parts.index("from")])
    return parts[0]


def build_cards(tools: Sequence[Any], parameters_by_name: Dict[str, Dict[str, Any]]) -> Tuple[List[ToolCard], frozenset]:
    texts = [(t, *build_card_texts(t, parameters_by_name.get(t.name))) for t in tools]

    # Vocabulary for compound splitting: every plain word found in any card or synonym phrase.
    vocab: set = set()
    for _, free, _ident in texts:
        for txt in free.values():
            vocab.update(w for w in raw_tokens(txt) if w.isalpha())
    for phrases in GEOTECH_SYNONYMS.values():
        for p in phrases:
            vocab.update(raw_tokens(p))
    vocab.update(_SHORT_PIECES)
    vocab_f = frozenset(vocab)

    cards = []
    for tool, free, ident in texts:
        fields: Dict[str, List[str]] = {}
        for fname, txt in free.items():
            fields.setdefault(fname, []).extend(analyze(txt, vocab_f))
        for fname, names in ident.items():
            for nm in names:
                fields.setdefault(fname, []).extend(analyze(nm, vocab_f, identifier=True))
        cards.append(ToolCard(name=tool.name, category=tool.category or "", canonical=is_canonical_tool(tool),
                              fields=fields, target=analyze(name_target(tool.name), vocab_f, identifier=True)))
    return cards, vocab_f


# ---------------------------------------------------------------------------
# Query head ("What is the porosity if the void ratio is 0.6?" -> "porosity")
# ---------------------------------------------------------------------------

_REQUEST_CUES = frozenset({"what", "how", "calculate", "compute", "estimate", "determine", "derive", "find", "get",
                           "convert", "classify", "interpret", "correct", "normalise", "normalize", "evaluate",
                           "check", "obtain", "need", "work"})
#: Words that end the requested quantity and start the inputs / conditions.
_HEAD_DELIMITERS = frozenset({"from", "if", "given", "with", "using", "for", "based", "when", "where", "at",
                              "data", "inputs", "input", "below", "under", "beneath", "via", "by", "in", "on"})


def query_head(query: str) -> str:
    """The part of a request that names the wanted quantity.

    Takes the first sentence with a request cue and cuts it at the first
    delimiter ("from", "if", "given", "with", ...).  "convert A to B" -> "B".
    """
    sentences = [s for s in re.split(r"(?<=[.?!:])\s+", query or "") if s.strip()]
    if not sentences:
        return ""
    chosen = next((s for s in sentences if _REQUEST_CUES & set(raw_tokens(s))), sentences[0])
    toks = re.findall(r"[A-Za-z0-9'()\-]+", chosen)
    low = [t.lower() for t in toks]
    if "convert" in low:
        for sep in ("to", "into"):
            if sep in low[low.index("convert"):]:
                return " ".join(toks[low.index(sep, low.index("convert")) + 1:])
    head = []
    for tok, lw in zip(toks, low):
        if lw in _HEAD_DELIMITERS and head:
            break
        head.append(tok)
    return " ".join(head)


# ---------------------------------------------------------------------------
# BM25
# ---------------------------------------------------------------------------

class BM25Index:
    """Okapi BM25 over weighted term frequencies (deterministic, pure Python)."""

    def __init__(self, docs: Sequence[Counter], k1: float = 1.2, b: float = 0.75):
        self.k1, self.b = k1, b
        self.n = len(docs)
        self.doc_len = [sum(d.values()) for d in docs]
        self.avgdl = (sum(self.doc_len) / self.n) if self.n else 0.0
        df: Counter = Counter()
        self.postings: Dict[str, List[Tuple[int, float]]] = defaultdict(list)
        for i, d in enumerate(docs):
            for term, tf in d.items():
                df[term] += 1
                self.postings[term].append((i, tf))
        self.idf = {t: math.log(1.0 + (self.n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def scores(self, query_terms: Iterable[str]) -> List[float]:
        out = [0.0] * self.n
        if not self.n:
            return out
        for term in dict.fromkeys(query_terms):   # de-duplicated, order-preserving
            idf = self.idf.get(term)
            if idf is None:
                continue
            for i, tf in self.postings[term]:
                norm = self.k1 * (1.0 - self.b + self.b * self.doc_len[i] / self.avgdl)
                out[i] += idf * tf * (self.k1 + 1.0) / (tf + norm)
        return out


# ---------------------------------------------------------------------------
# Registry-backed cached index
# ---------------------------------------------------------------------------

class ToolRetrievalIndex:
    """BM25 index over the cards of every registered tool plus their prompt schemas."""

    def __init__(self, tools: Sequence[Any], definitions: Sequence[Dict[str, Any]],
                 formatter: Optional[Callable[[List[dict]], List[dict]]] = None):
        self.definitions = {d["function"]["name"]: d for d in definitions}
        self._formatter = formatter
        self._prompt_json: Dict[str, str] = {}
        self._query_cache: Dict[str, List[str]] = {}
        params = {name: d["function"].get("parameters") or {} for name, d in self.definitions.items()}
        self.cards, self.vocab = build_cards(tools, params)
        self.names = [c.name for c in self.cards]
        self.position = {n: i for i, n in enumerate(self.names)}
        self.bm25 = BM25Index([c.weighted_terms() for c in self.cards])
        self.name_postings = self._postings(set(c.fields.get("name", ())) for c in self.cards)
        self.target_postings = self._postings(set(c.target) for c in self.cards)

    @staticmethod
    def _postings(term_sets: Iterable[set]) -> Dict[str, List[int]]:
        out: Dict[str, List[int]] = defaultdict(list)
        for i, terms in enumerate(term_sets):
            for t in sorted(terms):
                out[t].append(i)
        return out

    def analyze_query(self, query: str) -> List[str]:
        cached = self._query_cache.get(query)
        if cached is None:
            if len(self._query_cache) >= 256:
                self._query_cache.clear()
            cached = self._query_cache[query] = analyze(query, self.vocab)
        return list(cached)

    def prompt_tool(self, name: str) -> Dict[str, Any]:
        """Fresh copy of the prompt-formatted schema of ``name`` (formatted once, cached as JSON)."""
        cached = self._prompt_json.get(name)
        if cached is None:
            d = self.definitions[name]
            cached = self._prompt_json[name] = json.dumps(self._formatter([d])[0] if self._formatter else d)
        return json.loads(cached)

    def _match(self, terms: Iterable[str], postings: Dict[str, List[int]], out: List[float], weight: float) -> None:
        for t in dict.fromkeys(terms):
            idf = self.bm25.idf.get(t, 0.0)
            for i in postings.get(t, ()):
                out[i] += weight * idf

    def score(self, query: str, name_weight: float = 0.0, target_weight: float = 0.0) -> List[float]:
        """BM25 over the cards plus idf-weighted bonuses for query terms found in the
        tool *name* and for terms of the query head found in the tool's *target*."""
        terms = self.analyze_query(query)
        scores = self.bm25.scores(terms)
        if name_weight:
            self._match(terms, self.name_postings, scores, name_weight)
        if target_weight:
            self._match(analyze(query_head(query), self.vocab), self.target_postings, scores, target_weight)
        return scores


_INDEX: Optional[ToolRetrievalIndex] = None
_INDEX_KEY: Optional[Tuple] = None
_INDEX_LOCK = threading.Lock()


def registry_signature(registry: Any) -> Tuple:
    """Changes whenever a tool is added, removed or re-registered."""
    return tuple((name, id(tool)) for name, tool in registry._tools.items())


def get_index(registry: Any, definitions_factory: Callable[[], List[Dict[str, Any]]],
              formatter: Optional[Callable[[List[dict]], List[dict]]] = None) -> ToolRetrievalIndex:
    """Lazily build (once) and cache the index; rebuild when the registry's tool set changes.

    ``formatter`` turns a raw tool definition into its prompt form (cached per tool).
    """
    global _INDEX, _INDEX_KEY
    key = registry_signature(registry)
    if _INDEX is not None and _INDEX_KEY == key:
        return _INDEX
    with _INDEX_LOCK:
        if _INDEX is None or _INDEX_KEY != key:
            _INDEX = ToolRetrievalIndex(list(registry._tools.values()), definitions_factory(), formatter)
            _INDEX_KEY = key
    return _INDEX


def clear_index_cache() -> None:
    global _INDEX, _INDEX_KEY
    with _INDEX_LOCK:
        _INDEX, _INDEX_KEY = None, None
