# Author: Utkarsh Gupta
# License: GPL v3
"""
GeoCore standard quantity directory: one canonical symbol, name and unit per physical quantity.

``quantity_standard.json`` is the hand-curated standard. This module

  * resolves any parameter / output name to its standard quantity (``lookup``),
  * canonicalises unit spellings (``canonical_unit``: ``pct`` -> ``%``, ``kN/m3`` -> ``kN/m³``),
  * audits every calculation's documented inputs/outputs against the standard (``audit``) and lists
    where they disagree, so the disagreements can be decided by an engineer instead of hidden,
  * writes the audit report and the copy of the standard that the desktop app bundles.

It never changes a calculation: units that disagree are reported, not converted. The unit a function
documents for a parameter always wins over the standard unit (``resolve``); wherever the two differ the
deviation is recorded in ``quantity_function_units.json`` (generated from the docstrings), and names that
mean something else in one function (``Ic`` = moment of inertia) are re-mapped in
``quantity_function_overrides.json`` (curated). Nothing in the calculation, form or GeoAI-schema code
imports this module (tests/test_quantity_directory.py enforces that), so the directory can only affect
what the app *displays*. Run

    python -m core.quantity_directory            # audit + regenerate the report and the app copy
    python -m core.quantity_directory --check    # exit 1 if the generated files are out of date
"""
import collections
import json
import os
import re
import sys
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
STANDARD_PATH = os.path.join(_HERE, "quantity_standard.json")
REPORT_PATH = os.path.join(_HERE, "quantity_audit.md")
OVERRIDES_PATH = os.path.join(_HERE, "quantity_function_overrides.json")
FUNCTION_UNITS_PATH = os.path.join(_HERE, "quantity_function_units.json")
_APP_CONFIG = os.path.normpath(os.path.join(_HERE, "..", "..", "electron-app", "src", "config"))
APP_COPY_PATH = os.path.join(_APP_CONFIG, "quantityStandard.json")
APP_FUNCTION_UNITS_PATH = os.path.join(_APP_CONFIG, "quantityFunctionUnits.json")
APP_OVERRIDES_PATH = os.path.join(_APP_CONFIG, "quantityFunctionOverrides.json")

# Physical dimension of every canonical display unit (independent of core.geoai.units so that
# acceleration, diffusivity, mass density etc. are covered; tests cross-check the shared ones).
UNIT_DIMENSION = {
    "-": "dimensionless", "%": "percent",
    "kPa": "pressure", "MPa": "pressure", "Pa": "pressure",
    "kN/m³": "unit_weight", "kg/m³": "mass_density", "g/cm³": "mass_density",
    "m": "length", "mm": "length", "cm": "length", "cm²": "area", "m²": "area", "m⁴": "second_moment",
    "m³/s": "flow", "m²/yr": "diffusivity", "m/s": "velocity", "m/s²": "acceleration", "g": "acceleration",
    "deg": "angle", "rad": "angle", "°C": "temperature",
    "kN": "force", "kN/m": "force_per_length", "kN·m": "moment", "kN·m²": "flexural_rigidity",
    "kPa/m": "pressure_gradient", "s": "time", "yr": "time", "Hz": "frequency",
    "cm³": "volume", "ha": "area", "1/kPa": "compressibility", "1/kN": "flexibility", "mm/kN": "flexibility",
    "kN·m²/m": "flexural_rigidity_per_length", "deg/blow": "angle_per_blow", "deg/blow²": "angle_per_blow_squared",
}


def _norm_key(text: str) -> str:
    return re.sub(r"[\s_\-]+", "", str(text or "")).lower()


def _norm_unit(text: Optional[str]) -> str:
    u = str(text or "").strip().lower()
    u = re.sub(r"^:math:`(.*)`$", r"\1", u)
    u = re.sub(r"\s*/\s*", "/", u)
    u = u.replace("³", "3").replace("²", "2").replace("⁴", "4")
    return u


@lru_cache(maxsize=1)
def load_standard() -> Dict[str, Any]:
    with open(STANDARD_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _unit_index() -> Dict[str, str]:
    index: Dict[str, str] = {}
    for canonical, spellings in load_standard()["unit_aliases"].items():
        index[_norm_unit(canonical)] = canonical
        for spelling in spellings:
            index[_norm_unit(spelling)] = canonical
    return index


@lru_cache(maxsize=1)
def _key_indexes() -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Optional[Dict[str, Any]]]]:
    exact: Dict[str, Dict[str, Any]] = {}
    loose: Dict[str, Optional[Dict[str, Any]]] = {}
    for q in load_standard()["quantities"]:
        for key in q["keys"]:
            exact.setdefault(key, q)
            nk = _norm_key(key)
            # A loose key shared by two quantities (qt / Qt) is ambiguous: only exact matches resolve it.
            loose[nk] = q if loose.get(nk, q) is q else None
    return exact, loose


@lru_cache(maxsize=1)
def load_overrides() -> Dict[str, Any]:
    with open(OVERRIDES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _quantity_by_id() -> Dict[str, Dict[str, Any]]:
    return {q["id"]: q for q in load_standard()["quantities"]}


def canonical_unit(raw: Optional[str]) -> Optional[str]:
    """Standard spelling of a unit string, or None when the unit is not in the directory."""
    return _unit_index().get(_norm_unit(raw))


def lookup(key: str) -> Optional[Dict[str, Any]]:
    """The standard quantity a parameter / output name refers to, or None."""
    exact, loose = _key_indexes()
    return exact.get(key) or loose.get(_norm_key(key))


def lookup_in(function_id: Optional[str], key: str) -> Optional[Dict[str, Any]]:
    """Like ``lookup`` but honours the curated per-function re-mappings (``Ic`` in the inertia function)."""
    if function_id:
        for o in load_overrides()["quantity"]:
            if o["function"] == function_id and o["key"] == key:
                return _quantity_by_id()[o["quantity"]]
    return lookup(key)


def resolve(function_id: Optional[str], key: str, documented_unit: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    What to show for a function's parameter / output: the standard quantity with the unit that function
    actually uses. Order: unit documented in the function's own docstring > recorded deviation > standard unit.
    Returns None for names the directory does not know.
    """
    q = lookup_in(function_id, key)
    if q is None:
        return None
    unit, source = q["unit"], "standard"
    recorded = load_function_units().get(function_id or "", {}).get(key)
    if recorded:
        unit, source = recorded, "function"
    if documented_unit is not None and canonical_unit(documented_unit):
        unit, source = canonical_unit(documented_unit), "function"
    return {**q, "unit": unit, "unit_source": source}


@lru_cache(maxsize=1)
def load_function_units() -> Dict[str, Dict[str, str]]:
    try:
        with open(FUNCTION_UNITS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)["units"]
    except OSError:
        return {}


def audit(occurrences: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Compare every documented input/output with the standard and record where a function deviates."""
    if occurrences is None:
        from core.quantity_scan import scan_all
        occurrences = scan_all()

    findings = collections.defaultdict(list)
    deviations: Dict[str, Dict[str, str]] = collections.defaultdict(dict)
    unmatched: Dict[Tuple[str, str], Dict[str, Any]] = {}
    matched = collections.Counter()
    total = collections.Counter()
    for o in occurrences:
        role = o["role"]
        key = o["key"] or ""
        total[role] += 1
        q = lookup_in(o["function"], key) if key else None
        raw = o["unit_raw"]
        canon = canonical_unit(raw) if raw is not None else None
        where = f"{o['function']}.{key or o['label']}"

        if raw is None and role == "input":
            findings["undocumented_unit"].append(where)
        elif raw is not None and canon is None:
            findings["unknown_unit_string"].append(f"{where} = {raw[:40]!r}")
        if q is None:
            if key:
                bucket = unmatched.setdefault((key, canon or "?"), {"key": key, "unit": canon or "?", "n": 0, "label": o["label"], "functions": set()})
                bucket["n"] += 1
                bucket["functions"].add(o["function"])
            continue
        matched[role] += 1
        if canon is None:
            continue
        if raw != q["unit"] and canon == q["unit"]:
            findings["spelling"].append(f"{where}: {raw!r} -> {q['unit']!r}")
        elif canon != q["unit"]:
            have, want = UNIT_DIMENSION.get(canon), UNIT_DIMENSION.get(q["unit"])
            line = f"{where} [{q['id']}]: documented {canon}, standard {q['unit']}"
            if have == want or {have, want} == {"percent", "dimensionless"}:
                kind = "percent_vs_fraction" if have != want else "different_unit_same_dimension"
                findings[kind].append(line)
                deviations[o["function"]].setdefault(key, canon)  # the function's own unit wins; first (input) documentation kept
            else:
                findings["dimension_mismatch"].append(f"{line} ({have} vs {want})")

    return {
        "totals": dict(total), "matched": dict(matched),
        "functions": len({o["function"] for o in occurrences}),
        "findings": {k: sorted(set(v)) for k, v in findings.items()},
        "deviations": {fn: dict(sorted(keys.items())) for fn, keys in sorted(deviations.items())},
        "unmatched": sorted(unmatched.values(), key=lambda b: -b["n"]),
    }


# (finding, title, status) - status tells the reader whether anything is left to do.
FINDING_TITLES = [
    ("dimension_mismatch", "Name collisions: one name used for different physical quantities", "ACTION: add a per-function re-mapping to quantity_function_overrides.json"),
    ("percent_vs_fraction", "Percent vs fraction", "RESOLVED: the function's own documented unit is recorded in quantity_function_units.json and wins over the standard"),
    ("different_unit_same_dimension", "Same dimension, different unit", "RESOLVED: recorded per function, as above"),
    ("spelling", "Unit spelling variants", "RESOLVED: shown with the standard spelling; the function itself is untouched"),
    ("unknown_unit_string", "Unit strings the directory does not know", "INFO: mostly formula text that leaked out of a docstring; no unit is shown for these"),
    ("undocumented_unit", "Inputs with no documented unit", "INFO: the directory never invents a unit for these"),
]


def render_report(result: Dict[str, Any]) -> str:
    std = load_standard()
    lines = [
        "# GeoCore quantity directory - audit",
        "",
        "Generated by `python -m core.quantity_directory`; do not edit by hand. The standard itself is `quantity_standard.json`.",
        "",
        f"- Functions scanned: **{result['functions']}**",
        f"- Documented inputs: **{result['totals'].get('input', 0)}** ({result['matched'].get('input', 0)} matched to a standard quantity)",
        f"- Documented outputs: **{result['totals'].get('output', 0)}** ({result['matched'].get('output', 0)} matched)",
        f"- Standard quantities: **{len(std['quantities'])}**",
        f"- Functions with a recorded unit deviation: **{len(result['deviations'])}**",
        "",
        "Nothing here changes a calculation. Where a function documents a different unit than the standard, the function wins.",
        "",
    ]
    for key, title, status in FINDING_TITLES:
        items = result["findings"].get(key, [])
        lines += [f"## {title} - {len(items)}", "", f"_{status}_", ""]
        lines += [f"- `{i}`" for i in items[:60]]
        if len(items) > 60:
            lines.append(f"- ... and {len(items) - 60} more")
        lines.append("")
    lines += ["## Names not yet in the standard (most used first)", "", "| Name | Unit | Uses | Example |", "| --- | --- | ---: | --- |"]
    for b in result["unmatched"][:80]:
        lines.append(f"| `{b['key']}` | {b['unit']} | {b['n']} | {b['label'][:60].replace('|', '/')} |")
    lines.append("")
    return "\n".join(lines)


def function_units_json(result: Dict[str, Any]) -> str:
    doc = {
        "_comment": "Generated by `python -m core.quantity_directory` from the function docstrings. Where a function documents a unit that differs from the standard one, that unit wins.",
        "units": result["deviations"],
    }
    return json.dumps(doc, ensure_ascii=False, indent=1) + "\n"


def app_copy() -> str:
    """The standard as bundled with the desktop app."""
    return json.dumps(load_standard(), ensure_ascii=False, indent=1) + "\n"


def generated_files(result: Dict[str, Any]) -> List[Tuple[str, str]]:
    units = function_units_json(result)
    return [
        (REPORT_PATH, render_report(result)),
        (FUNCTION_UNITS_PATH, units),
        (APP_COPY_PATH, app_copy()),
        (APP_FUNCTION_UNITS_PATH, units),
        (APP_OVERRIDES_PATH, _read(OVERRIDES_PATH) or ""),
    ]


def _read(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def main(argv: List[str]) -> int:
    result = audit()
    files = generated_files(result)
    if "--check" in argv:
        stale = [p for p, text in files if _read(p) != text]
        for p in stale:
            print(f"out of date: {p}")
        return 1 if stale else 0
    for path, text in files:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print(f"wrote {path}")
    print({k: len(v) for k, v in result["findings"].items()}, "unmatched names:", len(result["unmatched"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
