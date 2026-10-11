# Author: Utkarsh Gupta
# License: GPL v3
"""
GeoCore calculation catalogue: the engineering view of the calculations, independent of how the engines
(Groundhog, GeoCore wrappers, IS-code functions) organise their code.

``data/<domain>.json`` lists the calculations of one domain. A calculation answers one engineering question
("Pile axial capacity") and has one or more methods; each method points at a function the app already runs
through ``/api/execute`` (``function``), so nothing about running a calculation changes. ``data/_internal.json``
lists the reachable functions that are not user-facing calculations, each with a reason.

Phase 0 (this module): the catalogue is data plus checks. Navigation, forms, GeoAI and the calculation
endpoint do not read it yet; tests/test_catalogue.py keeps it complete (every calculation the app can open is
in it exactly once, every method points at a function that exists) and tests/test_execute_golden.py keeps the
existing outputs unchanged while later phases build on it.
"""
import json
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Set

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
INTERNAL_FILE = "_internal.json"

STATUSES = ("verified", "corrected", "unverified", "known_issue")
DATA_TAGS = ("soil_profile", "cpt", "spt", "lab", "index", "ags")


class CatalogueError(ValueError):
    """The catalogue data is malformed (raised by ``load_catalogue``)."""


def _read(name: str) -> Dict[str, Any]:
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def _check_calculation(calc: Dict[str, Any], where: str, problems: List[str]) -> None:
    for key in ("id", "title", "group", "methods", "default_method"):
        if not calc.get(key):
            problems.append(f"{where}: calculation without '{key}'")
    methods = calc.get("methods") or []
    ids = [m.get("id") for m in methods]
    if len(ids) != len(set(ids)):
        problems.append(f"{where}: duplicate method ids {ids}")
    if calc.get("default_method") not in ids:
        problems.append(f"{where}: default_method {calc.get('default_method')!r} is not one of its methods")
    for tag in calc.get("data", []):
        if tag not in DATA_TAGS:
            problems.append(f"{where}: unknown data tag {tag!r} (known: {DATA_TAGS})")
    for m in methods:
        for key in ("id", "label", "function", "status"):
            if not m.get(key):
                problems.append(f"{where}.{m.get('id')}: method without '{key}'")
        if m.get("status") not in STATUSES:
            problems.append(f"{where}.{m.get('id')}: status {m.get('status')!r} not in {STATUSES}")
        if m.get("status") in ("corrected", "known_issue") and not m.get("status_note"):
            problems.append(f"{where}.{m.get('id')}: status {m['status']} needs a status_note")
        for tag in m.get("data", []):
            if tag not in DATA_TAGS:
                problems.append(f"{where}.{m.get('id')}: unknown data tag {tag!r} (known: {DATA_TAGS})")


@lru_cache(maxsize=1)
def load_catalogue() -> Dict[str, Any]:
    """
    {"domains": [...in order, each with its calculations], "calculations": {id: calc},
     "methods": {function id: (calculation id, method id)}, "internal": {function id: reason}}.
    Raises CatalogueError listing every structural problem found.
    """
    problems: List[str] = []
    domains, calculations, methods = [], {}, {}
    for name in sorted(os.listdir(DATA_DIR)):
        if not name.endswith(".json") or name == INTERNAL_FILE:
            continue
        doc = _read(name)
        domain = dict(doc.get("domain") or {})
        if not domain.get("id") or not domain.get("title"):
            problems.append(f"{name}: domain without id/title")
            continue
        domain["calculations"] = []
        for calc in doc.get("calculations", []):
            where = f"{name}:{calc.get('id')}"
            _check_calculation(calc, where, problems)
            if calc.get("id") in calculations:
                problems.append(f"{where}: calculation id used twice")
                continue
            calc = dict(calc, domain=domain["id"])
            calculations[calc["id"]] = calc
            domain["calculations"].append(calc)
            for m in calc.get("methods", []):
                fn = m.get("function")
                if fn in methods:
                    problems.append(f"{where}.{m.get('id')}: function {fn!r} already used by {methods[fn]}")
                methods[fn] = (calc["id"], m.get("id"))
        domains.append(domain)
    domains.sort(key=lambda d: (d.get("order", 999), d["id"]))

    internal_doc = _read(INTERNAL_FILE)
    internal: Dict[str, str] = {}
    for section in ("sidebar", "backend_only"):
        for entry in internal_doc.get(section, []):
            if not entry.get("reason"):
                problems.append(f"{INTERNAL_FILE}: {entry.get('function')} has no reason")
            if entry.get("function") in methods:
                problems.append(f"{INTERNAL_FILE}: {entry.get('function')} is also a catalogue method")
            internal[entry["function"]] = entry.get("reason", "")
    if problems:
        raise CatalogueError("Calculation catalogue problems:\n  " + "\n  ".join(problems))
    return {"domains": domains, "calculations": calculations, "methods": methods, "internal": internal}


def find_method(function_id: str) -> Optional[Dict[str, Any]]:
    """The calculation and method a function id belongs to, or None (internal or unknown)."""
    cat = load_catalogue()
    hit = cat["methods"].get(function_id)
    if not hit:
        return None
    calc = cat["calculations"][hit[0]]
    method = next(m for m in calc["methods"] if m["id"] == hit[1])
    return {"calculation": calc, "method": method}


def coverage(sidebar_ids: Set[str], backend_ids: Set[str]) -> Dict[str, List[str]]:
    """
    What the catalogue misses or invents. ``sidebar_ids``: calculations the app can open today;
    ``backend_ids``: functions the backend registry knows. All lists empty = complete.
    """
    cat = load_catalogue()
    known = set(cat["methods"]) | set(cat["internal"])
    return {
        "sidebar_not_catalogued": sorted(sidebar_ids - known),
        "backend_not_catalogued": sorted(backend_ids - known - sidebar_ids),
        "methods_without_function": sorted(f for f in cat["methods"] if f not in sidebar_ids | backend_ids),
        "internal_without_function": sorted(f for f in cat["internal"] if f not in sidebar_ids | backend_ids),
    }


def api_payload() -> Dict[str, Any]:
    """The catalogue as GET /api/catalogue returns it (domains -> calculations -> methods)."""
    cat = load_catalogue()
    return {
        "version": 1,
        "domains": [
            {"id": d["id"], "title": d["title"], "description": d.get("description", ""),
             "calculations": [{k: v for k, v in c.items() if k != "domain"} for c in d["calculations"]]}
            for d in cat["domains"]
        ],
        "statuses": list(STATUSES),
        "data_tags": list(DATA_TAGS),
    }


# ---------------------------------------------------------------------------- desktop navigation

APP_NAVIGATION_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "electron-app", "src", "config",
    "catalogueNavigation.json"))


def _slug(text: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _group_description(functions: List[Dict[str, Any]]) -> str:
    """'4 calculations: Pile axial capacity, ...' - what a group page card shows instead of a generic placeholder."""
    titles = list(dict.fromkeys(fn.get("calculation_title") or fn["title"] for fn in functions))
    shown = ", ".join(titles[:3]) + (f" and {len(titles) - 3} more" if len(titles) > 3 else "")
    count = f"{len(titles)} calculation{'s' if len(titles) != 1 else ''}"
    methods = len(functions) - len(titles)
    return f"{count}{f' ({len(functions)} methods)' if methods else ''}: {shown}"


def navigation() -> Dict[str, Any]:
    """
    The catalogue in the shape the desktop app's navigation already uses (config/geotechnicalModules.js):
    modules (domains) -> items (groups) -> functions ({id, title}), so the sidebar, home page and search can
    switch between the classic and the catalogue navigation without other changes. Every function id is one
    the app already opens; each also carries its calculation, method, status and standards.
    """
    cat = load_catalogue()
    modules = []
    for d in cat["domains"]:
        items: List[Dict[str, Any]] = []
        by_group: Dict[str, Dict[str, Any]] = {}
        for calc in d["calculations"]:
            group = by_group.get(calc["group"])
            if group is None:
                group = {"id": _slug(calc["group"]), "title": calc["group"], "functions": []}
                by_group[calc["group"]] = group
                items.append(group)
            for m in calc["methods"]:
                fn = {"id": m["function"], "title": m["label"], "calculation": calc["id"], "method": m["id"],
                      "status": effective_status(m)}
                cases = load_benchmarks().get(m["function"], [])
                if cases:
                    fn["benchmarks"] = [c["source"] for c in cases]
                if len(calc["methods"]) > 1:
                    fn["calculation_title"] = calc["title"]
                if m.get("standards"):
                    fn["standards"] = m["standards"]
                if m.get("status_note"):
                    fn["status_note"] = m["status_note"]
                data = m.get("data") or calc.get("data")  # what the method works from (search filter, Auto)
                if data:
                    fn["data"] = list(data)
                group["functions"].append(fn)
        for group in items:
            group["description"] = _group_description(group["functions"])
        modules.append({"id": d["id"], "title": d["title"], "description": d.get("description", ""), "items": items})
    return {"_comment": "Generated by `python -m core.catalogue` from python-backend/core/catalogue/data; "
                        "do not edit by hand.", "version": 1, "modules": modules}


def navigation_json() -> str:
    return json.dumps(navigation(), indent=1, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------------------- verification (Phase 3)

BENCHMARKS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "benchmarks.json")


@lru_cache(maxsize=1)
def load_benchmarks() -> Dict[str, List[Dict[str, Any]]]:
    """{function id: [cases]} from benchmarks.json (closed-form verification cases)."""
    with open(BENCHMARKS_PATH, encoding="utf-8") as f:
        cases = json.load(f)["cases"]
    out: Dict[str, List[Dict[str, Any]]] = {}
    for case in cases:
        out.setdefault(case["method"], []).append(case)
    return out


def effective_status(method: Dict[str, Any]) -> str:
    """'corrected' / 'known_issue' as curated; otherwise 'verified' only when the method has benchmark cases."""
    if method.get("status") in ("corrected", "known_issue"):
        return method["status"]
    return "verified" if load_benchmarks().get(method.get("function")) else "unverified"


def run_benchmark(case: Dict[str, Any]) -> Dict[str, Any]:
    """Run one case through registry.execute_function (the forms' path) and compare with its expected values."""
    import math
    from core.catalogue.envelope import extract_values
    from core.registry import registry
    raw = registry.execute_function("benchmark", case["method"], dict(case["inputs"]))
    if not isinstance(raw, dict) or "error" in raw:
        return {"ok": False, "problems": [f"error: {raw.get('error') if isinstance(raw, dict) else raw}"], "actual": {}}
    actual = {v["key"]: v["value"] for v in extract_values(case["method"], raw)}
    problems = []
    for key, expected in case["expected"].items():
        got = actual.get(key)
        if not isinstance(got, (int, float)) or not math.isclose(got, expected, rel_tol=case.get("rel_tol", 1e-6), abs_tol=1e-12):
            problems.append(f"{key}: expected {expected}, got {got}")
    return {"ok": not problems, "problems": problems, "actual": actual}
