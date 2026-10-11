# Author: Utkarsh Gupta
# License: GPL v3
"""
"Auto" method choice: which method of a calculation fits the data the workspace holds, with the reason.

A method lists the data it works from (catalogue ``data`` tags, e.g. LCPC: cpt, AxCap: soil_profile). The data
available is what the saved tables are recorded as (state_manager metadata ``kind``, chosen at upload; tables
saved before kinds were recorded have none and are not counted). Rules, in order:

1. Methods whose data are all available; among them a verified one first, then the calculation's default, then
   catalogue order.
2. Nothing fits: the default method, saying what data the other methods would need.

It only suggests: the form shown is still the method the user picked, and nothing runs.
"""
from typing import Any, Dict, Iterable, List, Optional, Set

from core.catalogue import effective_status, load_catalogue

DATA_LABELS = {"cpt": "CPT", "spt": "SPT", "soil_profile": "soil profile", "lab": "lab test", "index": "index test",
               "ags": "AGS"}


def available_data() -> Set[str]:
    """Data tags of the tables saved in the workspace (by their recorded kind)."""
    from core.state import state_manager
    return {meta.get("kind") for meta in state_manager.list_by_type("all") if meta.get("kind")}


def _names(tags: Iterable[str], joiner: str = " and ") -> str:
    return joiner.join(DATA_LABELS.get(t, t) for t in tags)


def suggest_method(calculation_id: str, available: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    """{"method", "label", "reason", "available": [...], "fits": [method ids]} for a calculation with methods."""
    calc = load_catalogue()["calculations"].get(calculation_id)
    if calc is None:
        raise KeyError(calculation_id)
    have = set(available_data() if available is None else available)
    methods: List[Dict[str, Any]] = calc["methods"]
    default = next((m for m in methods if m["id"] == calc["default_method"]), methods[0])

    def needs(m):
        return list(m.get("data") or calc.get("data") or [])

    fits = [m for m in methods if needs(m) and all(t in have for t in needs(m))]
    if fits:
        best = sorted(fits, key=lambda m: (effective_status(m) != "verified", m["id"] != default["id"],
                                           methods.index(m)))[0]
        reason = f"{_names(needs(best))} data saved in the project"
        if effective_status(best) == "verified":
            reason += "; verified method"
        if len(fits) > 1:
            reason += f"; {len(fits)} methods fit"
    else:
        best = default
        wanted = sorted({t for m in methods for t in needs(m)})
        reason = ("default method; no " + _names(wanted, " or ") + " data saved yet") if wanted else "default method"
    return {"method": best["id"], "label": best["label"], "reason": reason, "available": sorted(have),
            "fits": [m["id"] for m in fits]}
