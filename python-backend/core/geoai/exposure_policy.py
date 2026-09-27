"""
GeoAI tool exposure policy: which Groundhog/GeoCore functions the SLM may see and call.

Rule (AGENTS.md §7, §8): a function is exposed to the model only if it is an engineering
capability that takes JSON-expressible engineering inputs (numbers, text choices, lists)
and returns engineering values. Everything else is excluded from the model-facing GeoAI
Tool Registry, and so from list_tools(), the OpenAI/Gemini tool definitions, the tool
selector's candidate set and invoke_tool().

The desktop UI is not affected: core.registry.Registry.function_map keeps every function,
and the input schemas of excluded functions stay in SCHEMA_REGISTRY for form validation.

Exclusions are explicit (module-wide or per function), each with a reason. New Groundhog
functions in an excluded module are excluded automatically; anything else is exposed by
default, so review this file when Groundhog is upgraded.

Deliberately KEPT (borderline): Eurocode 7 ``constant_value`` / ``linear_trend``
(characteristic-value selection is an engineering capability), ``logtimemethod`` /
``roottimemethod`` (cv from oedometer readings), ``mohrcoulomb_triaxial_*``,
``pilegroupeffect_reesevanimpe`` and ``negativeskinfriction_pilegroup_zeevaertdebeer``
(return engineering values even though some also return a figure).
"""
from typing import Dict, Optional

# Whole Groundhog modules that contain no model-facing engineering capability.
EXCLUDED_MODULES: Dict[str, str] = {
    "groundhog.general.validation":
        "Groundhog's own input-validation internals (Validator, map_args, validate_*), not calculations.",
    "groundhog.general.plotting":
        "Plotting / interactive figure helpers; they return figures, not engineering values.",
    "groundhog.general.parameter_mapping":
        "Generic dict, dataframe and coordinate utilities (merge/reverse dicts, depth mapping, "
        "point/line offsets); project locations and layering reach GeoAI via ProjectContext.",
    "groundhog.general.agsconversion":
        "Reads AGS files from a filesystem path (§7 forbids model filesystem access); AGS data "
        "reaches GeoAI through core.geoai.ags / project context.",
    "groundhog.general.soilprofile":
        "SoilProfile / CalculationGrid object construction, Excel/dataframe import, fence plots "
        "and web retrieval (BRO/DOV); project stratigraphy reaches GeoAI through "
        "core.geoai.data_access.ProjectContext and the context resolver instead.",
}

_STATEFUL = ("Stateful calculation class needing SoilProfile/DataFrame objects and multi-step "
             "method calls; driven by the desktop UI workflow in core.registry, not a one-shot tool.")
_FIGURE = "Returns a figure / plotting geometry only, no engineering values for the model to use."

# Individual functions excluded outside the modules above.
EXCLUDED_FUNCTIONS: Dict[str, str] = {
    # Test fixture
    "example_manual_function": "Test fixture in core.manual_functions, not an engineering capability.",
    # Stateful classes (UI workflows)
    "AxCapCalculation": _STATEFUL,
    "DeBeerCalculation": _STATEFUL,
    "KoppejanCalculation": _STATEFUL,
    "LCPCAxcapCalculation": _STATEFUL,
    "SettlementCalculation": _STATEFUL,
    "ShallowFoundationCapacity": _STATEFUL,
    "ShallowFoundationCapacityDrained": _STATEFUL,
    "ShallowFoundationCapacityUndrained": _STATEFUL,
    "ConsolidationCalculation": _STATEFUL,
    "HardeningSoil": _STATEFUL,
    "InsituTestProcessing": _STATEFUL,
    "PCPTProcessing": _STATEFUL,
    "SPTProcessing": _STATEFUL,
    "Eurocode7_factoring_STR_GEO": _STATEFUL,
    # Figure-only outputs
    "plotcycliccontours_dssclay_andersen": _FIGURE,
    "plotcycliccontours_triaxialclay_andersen": _FIGURE,
    "plotporepressureaccumulation_dssclay_andersen": _FIGURE,
    "plotporepressureaccumulation_dsssand_andersen": _FIGURE,
    "plotporepressureaccumulation_triaxialclay_andersen": _FIGURE,
    "plotstrainaccumulation_dssclay_andersen": _FIGURE,
    "plotstrainaccumulation_dsssand_andersen": _FIGURE,
    "plotstrainaccumulation_triaxialclay_andersen": _FIGURE,
    "plot_combined_longitudinal_profile": _FIGURE,
    "plot_longitudinal_profile": _FIGURE,
    "PSDChart": _FIGURE,
    "PlasticityChart": _FIGURE,
    "failuremechanism_prandtl": _FIGURE,
    # Interactive GUI / file I/O
    "selectpoints": "Interactive Matplotlib point picking (blocks waiting for mouse input).",
    "read_ags": "Reads an AGS file from a filesystem path (§7); use core.geoai.ags / project context.",
}


def exclusion_reason(func_name: str, module_name: Optional[str] = None) -> Optional[str]:
    """Why ``func_name`` is hidden from the model, or None when it may be exposed."""
    if func_name in EXCLUDED_FUNCTIONS:
        return EXCLUDED_FUNCTIONS[func_name]
    if module_name in EXCLUDED_MODULES:
        return EXCLUDED_MODULES[module_name]
    return None


def is_model_exposed(func_name: str, module_name: Optional[str] = None) -> bool:
    """True when the function may be offered to / invoked by the SLM (GeoAI registry)."""
    return exclusion_reason(func_name, module_name) is None
