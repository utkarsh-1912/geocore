# Author: Utkarsh Gupta
# License: GPL v3
"""
Phase relations "solve for": the quantity the user wants from the quantities they know, by chaining the
existing Groundhog phase-relation functions (the 14 methods of the catalogue's "phase_relations" calculation).

Nothing is calculated here. Each step runs one Groundhog function through ``registry.execute_function`` (the
path the forms use), and the solver only decides which function can run next and passes values along:

* forward chaining from the known quantities, in a fixed order, until the target is known;
* then only the steps the target depends on are kept, so the report shows the shortest chain that was used;
* constants are made consistent within a solve: the Groundhog functions default to gamma_w = 10 kN/m3 in the
  unit-weight relations but convert unit weight and density with g = 9.81 m/s2 and rho_w = 1000 kg/m3, which a
  chain through both would mix (about 5 % error). Here gamma_w = rho_w * g (9.81 kN/m3 by default); a request may
  give unit_weight_water instead, and g is then set to match. The constants used are listed in the result;
* soil properties are never assumed: Groundhog's defaults for specific gravity (Gs = 2.65) and saturation
  (Sr = 1) are used only when the request allows them in ``assume``, and are then reported as assumptions.

Water content, saturation and porosity are fractions [-] (as the Groundhog functions use them).
"""
from typing import Any, Dict, List, Optional, Tuple

QUANTITIES: Dict[str, Dict[str, str]] = {
    "specific_gravity": {"label": "Specific gravity Gs", "unit": "-"},
    "void_ratio": {"label": "Void ratio e", "unit": "-"},
    "porosity": {"label": "Porosity n", "unit": "-"},
    "water_content": {"label": "Water content w", "unit": "-"},
    "saturation": {"label": "Degree of saturation Sr", "unit": "-"},
    "bulk_unit_weight": {"label": "Bulk unit weight γ", "unit": "kN/m³"},
    "effective_unit_weight": {"label": "Effective unit weight γ'", "unit": "kN/m³"},
    "dry_unit_weight": {"label": "Dry unit weight γd", "unit": "kN/m³"},
    "saturated_unit_weight": {"label": "Saturated unit weight γsat", "unit": "kN/m³"},
    "bulk_density": {"label": "Bulk density ρ", "unit": "kg/m³"},
    "dry_density": {"label": "Dry density ρd", "unit": "kg/m³"},
    "e_min": {"label": "Minimum void ratio emin", "unit": "-"},
    "e_max": {"label": "Maximum void ratio emax", "unit": "-"},
    "relative_density": {"label": "Relative density Dr", "unit": "-"},
}
#: Physical constants (label, default, unit). gamma_w is derived from rho_w * g so that every step of a chain
#: uses the same water properties; see the module docstring.
WATER_DENSITY = 1000.0
GRAVITY = 9.81
CONSTANTS = {"unit_weight_water": ("Unit weight of water γw", WATER_DENSITY * GRAVITY / 1000.0, "kN/m³"),
             "gravity": ("Gravitational acceleration g", GRAVITY, "m/s²"),
             "water_density": ("Density of water ρw", WATER_DENSITY, "kg/m³")}


def _constants(unit_weight_water: Optional[float]) -> Dict[str, float]:
    """Consistent water/gravity constants: gamma_w = rho_w * g, from g = 9.81 or from a given gamma_w."""
    if unit_weight_water is None:
        return {"unit_weight_water": WATER_DENSITY * GRAVITY / 1000.0, "gravity": GRAVITY, "water_density": WATER_DENSITY}
    gw = float(unit_weight_water)
    if not 5.0 <= gw <= 15.0:
        raise PhaseRelationError(f"Unit weight of water {gw} kN/m³ is outside 5-15 kN/m³.")
    return {"unit_weight_water": gw, "gravity": gw * 1000.0 / WATER_DENSITY, "water_density": WATER_DENSITY}
#: Soil-property defaults of the Groundhog functions, used only when the request allows them.
ASSUMABLE = {"specific_gravity": 2.65, "saturation": 1.0}

# Each step: Groundhog function, {its parameter: quantity or constant}, {its output key: quantity}.
# The order is the order in which steps are tried.
STEPS: List[Tuple[str, Dict[str, str], Dict[str, str]]] = [
    ("voidratio_porosity", {"porosity": "porosity"}, {"voidratio [-]": "void_ratio"}),
    ("porosity_voidratio", {"voidratio": "void_ratio"}, {"porosity [-]": "porosity"}),
    ("voidratio_drydensity", {"dry_density": "dry_density", "specific_gravity": "specific_gravity",
                              "water_density": "water_density"}, {"Void ratio [-]": "void_ratio"}),
    ("unitweight_density", {"density": "bulk_density", "g": "gravity"}, {"Unit weight [kN/m3]": "bulk_unit_weight"}),
    ("unitweight_density", {"density": "dry_density", "g": "gravity"}, {"Unit weight [kN/m3]": "dry_unit_weight"}),
    ("dryunitweight_watercontent", {"watercontent": "water_content", "bulkunitweight": "bulk_unit_weight"},
     {"dry unit weight [kN/m3]": "dry_unit_weight"}),
    ("bulkunitweight_dryunitweight", {"dryunitweight": "dry_unit_weight", "watercontent": "water_content",
                                      "unitweight_water": "unit_weight_water"},
     {"bulk unit weight [kN/m3]": "bulk_unit_weight", "effective unit weight [kN/m3]": "effective_unit_weight"}),
    ("voidratio_watercontent", {"water_content": "water_content", "saturation": "saturation",
                                "specific_gravity": "specific_gravity"}, {"Void ratio [-]": "void_ratio"}),
    ("watercontent_voidratio", {"voidratio": "void_ratio", "saturation": "saturation",
                                "specific_gravity": "specific_gravity"}, {"Water content [-]": "water_content"}),
    ("saturation_watercontent", {"water_content": "water_content", "voidratio": "void_ratio",
                                 "specific_gravity": "specific_gravity"}, {"saturation [-]": "saturation"}),
    ("bulkunitweight", {"saturation": "saturation", "voidratio": "void_ratio", "specific_gravity": "specific_gravity",
                        "unitweight_water": "unit_weight_water"},
     {"bulk unit weight [kN/m3]": "bulk_unit_weight", "effective unit weight [kN/m3]": "effective_unit_weight"}),
    ("voidratio_bulkunitweight", {"bulkunitweight": "bulk_unit_weight", "saturation": "saturation",
                                  "specific_gravity": "specific_gravity", "unitweight_water": "unit_weight_water"},
     {"e [-]": "void_ratio", "w [-]": "water_content"}),
    ("unitweight_watercontent_saturated", {"water_content": "water_content", "specific_gravity": "specific_gravity",
                                           "gamma_w": "unit_weight_water"}, {"gamma [kN/m3]": "saturated_unit_weight"}),
    ("density_unitweight", {"gamma": "bulk_unit_weight", "g": "gravity"}, {"Density [kg/m3]": "bulk_density"}),
    ("density_unitweight", {"gamma": "dry_unit_weight", "g": "gravity"}, {"Density [kg/m3]": "dry_density"}),
    # Groundhog names these void ratios by density: its e_min is the void ratio at MINIMUM density (loosest,
    # conventionally e_max) and vice versa - the same swap as the GeoAI tool (core/geoai/tool_definitions.py).
    ("relative_density", {"void_ratio": "void_ratio", "e_min": "e_max", "e_max": "e_min"},
     {"Dr [-]": "relative_density"}),
]


class PhaseRelationError(ValueError):
    """A request the solver cannot answer (unknown quantity, target not reachable, a step failed)."""

    def __init__(self, message: str, needs: Optional[List[List[str]]] = None,
                 skipped: Optional[List[Dict[str, str]]] = None):
        super().__init__(message)
        self.needs = needs or []
        self.skipped = skipped or []  # routes tried and refused (e.g. an input outside a function's range)


def _run(function_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
    from core.registry import registry
    result = registry.execute_function("phase_relations", function_id, args)
    if not isinstance(result, dict) or "error" in result or result.get("status") == "ValidationError":
        message = result.get("error") if isinstance(result, dict) else result
        raise PhaseRelationError(f"{function_id} failed: {message}")
    return result


def _missing_for(target: str, known: set) -> List[List[str]]:
    """For each step that yields the target, the quantities still missing to run it (what to ask the user)."""
    needs = []
    for _, params, outputs in STEPS:
        if target in outputs.values():
            miss = sorted({q for q in params.values() if q not in known and q not in CONSTANTS})
            if miss and miss not in needs:
                needs.append(miss)
    return needs


def solve(known: Dict[str, float], target: str, assume: Optional[List[str]] = None,
          unit_weight_water: Optional[float] = None) -> Dict[str, Any]:
    """
    {"target", "value", "unit", "steps": [{function, inputs, outputs}], "constants": [...], "assumptions": [...]}.
    Raises PhaseRelationError when the target cannot be reached from what is known.
    """
    unknown = [q for q in list(known) + [target] if q not in QUANTITIES]
    if unknown:
        raise PhaseRelationError(f"Unknown quantities: {unknown}. Known quantities: {sorted(QUANTITIES)}")
    if target in known:
        raise PhaseRelationError(f"{target} is already given.")
    assume = [a for a in (assume or []) if a in ASSUMABLE and a not in known]

    values: Dict[str, float] = {q: float(v) for q, v in known.items()}
    source: Dict[str, Any] = {q: "given" for q in values}
    for q in assume:
        values[q], source[q] = ASSUMABLE[q], "assumed"
    constants = _constants(unit_weight_water)
    for c, v in constants.items():
        values[c], source[c] = v, "constant"

    executed: List[Dict[str, Any]] = []
    skipped: List[Dict[str, str]] = []
    tried = set()
    progress = True
    while target not in values and progress:
        progress = False
        for index, (function_id, params, outputs) in enumerate(STEPS):
            if index in tried or not all(q in values for q in params.values()):
                continue
            new = [q for q in outputs.values() if q not in values]
            if not new:
                continue
            tried.add(index)
            args = {p: values[q] for p, q in params.items()}
            try:
                result = _run(function_id, args)
            except PhaseRelationError as e:
                # e.g. an input outside the function's validated range: this route is closed, others may work
                skipped.append({"function": function_id, "reason": str(e)})
                continue
            produced = {}
            for key, q in outputs.items():
                v = result.get(key)
                if q not in values and isinstance(v, (int, float)) and v == v:
                    values[q], source[q] = float(v), len(executed)
                    produced[q] = float(v)
            if produced:
                executed.append({"function": function_id, "inputs": {q: values[q] for q in params.values()},
                                 "outputs": produced, "parameters": params})
                progress = True
                if target in values:
                    break
    if target not in values:
        raise PhaseRelationError(f"{QUANTITIES[target]['label']} cannot be obtained from the given quantities.",
                                 needs=_missing_for(target, set(values)), skipped=skipped)

    # Keep only the steps the target depends on.
    needed, wanted = set(), [target]
    while wanted:
        q = wanted.pop()
        s = source.get(q)
        if isinstance(s, int) and s not in needed:
            needed.add(s)
            wanted.extend(executed[s]["inputs"].keys())
    steps = [executed[i] for i in sorted(needed)]
    used = {q for st in steps for q in st["inputs"]}
    return {
        "target": target, "label": QUANTITIES[target]["label"], "value": values[target], "unit": QUANTITIES[target]["unit"],
        "steps": [{"function": st["function"], "inputs": {q: v for q, v in st["inputs"].items()},
                   "outputs": st["outputs"]} for st in steps],
        "constants": [{"quantity": c, "label": CONSTANTS[c][0], "value": constants[c], "unit": CONSTANTS[c][2]}
                      for c in CONSTANTS if c in used],
        "assumptions": [{"quantity": q, "label": QUANTITIES[q]["label"], "value": ASSUMABLE[q],
                         "note": "Groundhog default, used because you allowed it"} for q in assume if q in used],
        # Routes that were tried and refused (e.g. an input outside a function's validated range), for transparency.
        "skipped": [s for s in skipped if s["function"] not in {st["function"] for st in steps}],
    }


def describe() -> Dict[str, Any]:
    """What the solver knows, for the form: quantities, constants and the defaults it may assume."""
    return {"quantities": [{"id": q, **meta} for q, meta in QUANTITIES.items()],
            "constants": [{"id": c, "label": l, "value": v, "unit": u} for c, (l, v, u) in CONSTANTS.items()],
            "assumable": [{"id": q, "label": QUANTITIES[q]["label"], "value": v} for q, v in ASSUMABLE.items()]}
