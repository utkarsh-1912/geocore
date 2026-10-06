# Author: Utkarsh Gupta
# License: GPL v3
"""
Scan every calculation's documented inputs and outputs (symbol, unit, label).

Sources, all read without importing Groundhog:
  * ``function_manifest.json``  - the Groundhog docstrings (``:param x: text (:math:`sym`) [:math:`unit`]``,
    outputs as ``:rtype: ... keys ['f_s [kPa]', ...]``);
  * ``core.standards.bis``      - GeoCore's IS-code functions (flat ``{"name [unit]": value}`` outputs);
  * ``core.manual_functions``   - hand-written calculations.

The result feeds ``quantity_directory`` (the audit against the standard) and is also useful on its own:
``python -m core.quantity_scan`` prints how many inputs/outputs exist and how their units are spelled.
"""
import inspect
import json
import os
import re
from typing import Any, Dict, List

_HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST_PATH = os.path.join(_HERE, "function_manifest.json")

# ":param name: description (:math:`symbol`) [:math:`unit`] - Suggested range ..."
_PARAM_RE = re.compile(r"^:param\s+(\w+):\s*(.*?)(?=^\s*:(?:param|returns?|rtype|raises)\b|\Z)", re.S | re.M)
_SYMBOL_RE = re.compile(r"\(:math:`([^`]*)`\)")
_UNIT_RE = re.compile(r"\[(?::math:`([^`]*)`|([^\]\[`]*))\]")
# Output keys such as 'f_s [kPa]' inside the :rtype: / :returns: text.
_OUT_KEY_RE = re.compile(r"""['"]([^'"\[\]]+?)\s*\[([^\]]*)\]['"]""")
_OUT_MATH_RE = re.compile(r"(?P<label>[^,\n:`]+?)\s*\(:math:`(?P<sym>[^`]*)`\)\s*\[:math:`(?P<unit>[^`]*)`\]")


def _doc_sections(doc: str) -> Dict[str, str]:
    returns = re.search(r"^:returns?:(.*?)(?=^:\w+:|\Z)", doc, re.S | re.M)
    rtype = re.search(r"^:rtype:(.*?)(?=^\S|\Z)", doc, re.S | re.M)
    return {"returns": returns.group(1) if returns else "", "rtype": rtype.group(1) if rtype else ""}


def parse_docstring(function_id: str, module: str, doc: str, source: str) -> List[Dict[str, Any]]:
    """Input and output occurrences documented in one docstring."""
    if not doc:
        return []
    found: List[Dict[str, Any]] = []
    for m in _PARAM_RE.finditer(doc):
        name, body = m.group(1), " ".join(m.group(2).split())
        sym = _SYMBOL_RE.search(body)
        unit = _UNIT_RE.search(body)
        label = body.split("(:math:")[0].split(" [")[0].strip(" .-")
        found.append({
            "function": function_id, "module": module, "role": "input", "key": name,
            "label": label, "symbol": sym.group(1).strip() if sym else "",
            "unit_raw": (unit.group(1) if unit and unit.group(1) is not None else (unit.group(2) if unit else "")).strip() if unit else None,
            "source": source,
        })
    sections = _doc_sections(doc)
    seen = set()
    for m in _OUT_MATH_RE.finditer(sections["returns"]):
        found.append({"function": function_id, "module": module, "role": "output", "key": "",
                      "label": m.group("label").strip(), "symbol": m.group("sym").strip(),
                      "unit_raw": m.group("unit").strip(), "source": source})
        seen.add(m.group("label").strip().lower())
    for text in (sections["rtype"], sections["returns"], doc if source != "groundhog" else ""):
        for m in _OUT_KEY_RE.finditer(text):
            key, unit = m.group(1).strip(), m.group(2).strip()
            if (key, unit) in seen:
                continue
            seen.add((key, unit))
            found.append({"function": function_id, "module": module, "role": "output", "key": key,
                          "label": "", "symbol": "", "unit_raw": unit, "source": source})
    return found


def scan_all() -> List[Dict[str, Any]]:
    """Every documented input/output occurrence across Groundhog, BIS and manual functions."""
    occurrences: List[Dict[str, Any]] = []
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        for entry in json.load(f)["functions"]:
            # The manifest keeps the raw __doc__, whose indentation depends on the Python version
            # that wrote it (3.13 dedents docstrings, 3.10 does not); "^:returns:" needs it removed.
            doc = inspect.cleandoc(entry.get("doc") or "")
            occurrences += parse_docstring(entry["name"], entry["module"], doc, "groundhog")

    from core.standards.bis import BIS_FUNCTIONS
    for name, fn in BIS_FUNCTIONS.items():
        occurrences += parse_docstring(name, fn.__module__, inspect.getdoc(fn) or "", "bis")

    from core import manual_functions
    for name, fn in inspect.getmembers(manual_functions, inspect.isfunction):
        if not name.startswith("_") and fn.__module__ == manual_functions.__name__:
            occurrences += parse_docstring(name, fn.__module__, inspect.getdoc(fn) or "", "manual")
    return occurrences


if __name__ == "__main__":
    import collections
    occ = scan_all()
    inputs = [o for o in occ if o["role"] == "input"]
    outputs = [o for o in occ if o["role"] == "output"]
    print(f"{len({o['function'] for o in occ})} functions, {len(inputs)} inputs, {len(outputs)} outputs")
    print("input units :", collections.Counter(o["unit_raw"] for o in inputs).most_common(40))
    print("output units:", collections.Counter(o["unit_raw"] for o in outputs).most_common(40))
