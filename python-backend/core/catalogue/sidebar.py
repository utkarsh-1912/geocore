# Author: Utkarsh Gupta
# License: GPL v3
"""
Read the desktop app's current navigation (electron-app/src/config/geotechnicalModules.js) from Python.

The file is a single exported array literal (no imports, no code), so it is converted to JSON with a small
tokenizer that understands JavaScript strings, comments, unquoted keys and trailing commas. Used by the
catalogue coverage check: every calculation the app can open today must stay reachable.
"""
import json
import os
from functools import lru_cache
from typing import Any, Dict, Iterator, List

_HERE = os.path.dirname(os.path.abspath(__file__))
SIDEBAR_PATH = os.path.normpath(
    os.path.join(_HERE, "..", "..", "..", "electron-app", "src", "config", "geotechnicalModules.js"))


def _js_literal_to_json(src: str) -> str:
    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c in "'\"`":  # string: re-emit as a JSON string
            quote, i, buf = c, i + 1, []
            while i < n and src[i] != quote:
                if src[i] == "\\" and i + 1 < n:
                    nxt = src[i + 1]
                    buf.append({"n": "\n", "t": "\t", "\\": "\\", "'": "'", '"': '"', "`": "`"}.get(nxt, nxt))
                    i += 2
                    continue
                buf.append(src[i])
                i += 1
            out.append(json.dumps("".join(buf), ensure_ascii=False))
            i += 1
        elif src.startswith("//", i):
            i = src.find("\n", i) if src.find("\n", i) != -1 else n
        elif src.startswith("/*", i):
            end = src.find("*/", i + 2)
            i = n if end == -1 else end + 2
        elif c.isalpha() or c in "_$":  # bare identifier: a key (quote it) or a literal (true/false/null)
            j = i
            while j < n and (src[j].isalnum() or src[j] in "_$"):
                j += 1
            word = src[i:j]
            k = j
            while k < n and src[k] in " \t\r\n":
                k += 1
            out.append(json.dumps(word) if k < n and src[k] == ":" else word)
            i = j
        elif c == ",":  # drop trailing commas
            k = i + 1
            while k < n and src[k] in " \t\r\n":
                k += 1
            if k < n and src[k] in "]}":
                i += 1
                continue
            out.append(c)
            i += 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


@lru_cache(maxsize=1)
def load_sidebar(path: str = SIDEBAR_PATH) -> List[Dict[str, Any]]:
    """The GEOTECHNICAL_MODULES array: modules -> items (groups) -> functions ({id, title})."""
    with open(path, encoding="utf-8") as f:
        src = f.read()
    start = src.index("[", src.index("GEOTECHNICAL_MODULES"))
    end = src.rindex("]") + 1
    return json.loads(_js_literal_to_json(src[start:end]))


def iter_sidebar_functions(path: str = SIDEBAR_PATH) -> Iterator[Dict[str, str]]:
    """Every calculation entry: {"id", "title", "module", "group"} in sidebar order."""
    for module in load_sidebar(path):
        for group in module.get("items", []):
            for fn in group.get("functions", []):
                yield {"id": fn["id"], "title": fn.get("title", fn["id"]), "module": module["id"], "group": group["id"]}
