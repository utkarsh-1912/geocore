# Author: Utkarsh Gupta
# License: GPL v3
"""
GeoAI tools on the calculation catalogue (Phase 6). A tool's function id (its ``form_function``, else its name:
auto-registered Groundhog tools are named after the function) is a method of a catalogue calculation; this
module gives:

* ``tool_catalogue``: the calculation, method, verification status and standards of a tool, for the UI (tool
  listings and the tools used in an answer). It is never added to the model's tool messages.
* ``tool_warnings``: applicability messages for a call (core.catalogue.applicability), mapped from tool fields
  to Groundhog parameters. The tool result carries them only when a check fails.
* ``sibling_tools``: other tools that are methods of the same calculation (optional catalogue-grouped tool
  offer, GeoAIModelConfig.catalogue_methods).
"""
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple


def _find(function_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not function_id:
        return None
    try:
        from core.catalogue import find_method
        return find_method(function_id)
    except Exception:  # a malformed catalogue must not break GeoAI
        return None


def tool_function_id(tool: Any) -> Optional[str]:
    """The GeoCore function id of a tool: its form_function, else its own name (auto-registered Groundhog tools
    are named after the function, which is also the form id)."""
    if tool is None:
        return None
    return getattr(tool, "form_function", None) or getattr(tool, "name", None)


def tool_catalogue(tool: Any) -> Optional[Dict[str, Any]]:
    """{function, calculation_id, calculation, method_id, method, status, benchmarks, standards?, applicability?} or None."""
    function_id = tool_function_id(tool)
    hit = _find(function_id)
    if not hit:
        return None
    from core.catalogue import effective_status, load_benchmarks
    from core.catalogue.applicability import NOTES
    calc, method = hit["calculation"], hit["method"]
    info = {"function": function_id, "calculation_id": calc["id"], "calculation": calc["title"], "method_id": method["id"],
            "method": method["label"], "status": effective_status(method),
            "benchmarks": len(load_benchmarks().get(method["function"], []))}
    if method.get("standards"):
        info["standards"] = list(method["standards"])
    if NOTES.get(function_id):
        info["applicability"] = NOTES[function_id]
    return info


def tool_warnings(tool: Any, call_args: Dict[str, Any]) -> List[str]:
    """Applicability messages for ``call_args`` (tool field names) of ``tool`` ([] when none apply)."""
    function_id = tool_function_id(tool)
    if not function_id:
        return []
    from core.catalogue.applicability import check
    arg_map = getattr(getattr(tool, "func", None), "__geoai_arg_map__", None) or {}
    return check(function_id, {arg_map.get(k, k): v for k, v in (call_args or {}).items()})


@lru_cache(maxsize=4)
def _calculation_tools(registry_id: int, names: Tuple[str, ...]) -> Dict[str, Tuple[str, ...]]:
    from core.geoai.tool_registry import tool_registry
    by_calc: Dict[str, List[str]] = {}
    of_tool: Dict[str, Tuple[str, str]] = {}  # tool -> (calculation id, function id)
    for name in names:
        function_id = tool_function_id(tool_registry.get_tool(name))
        hit = _find(function_id)
        if hit:
            of_tool[name] = (hit["calculation"]["id"], function_id)
            by_calc.setdefault(hit["calculation"]["id"], []).append(name)
    # Other METHODS only: a tool for the same function (a curated tool and its auto-registered twin) is not one.
    return {name: tuple(n for n in by_calc[calc] if of_tool[n][1] != function_id)
            for name, (calc, function_id) in of_tool.items()}


def sibling_tools(name: str) -> Tuple[str, ...]:
    """Registered tools that are other methods of the calculation ``name`` belongs to (registry order)."""
    from core.geoai.tool_registry import tool_registry
    names = tuple(tool_registry._tools)
    return _calculation_tools(id(tool_registry), names).get(name, ())
