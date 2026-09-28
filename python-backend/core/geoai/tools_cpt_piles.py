# Author: Utkarsh Gupta
# License: GPL v3
"""
GeoAI tools: project CPT retrieval and CPT-based axial pile capacity (AGENTS.md §8, §9, §28-29).

- ``list_project_cpts``                 compact list of CPTs in the current project
- ``get_cpt_summary``                   layering (SBT/Ic intervals), channel ranges, QA flags, provenance
- ``calculate_pile_capacity_from_cpt``  Groundhog LCPC / Koppejan / De Beer on a project CPT

Raw CPT arrays never go to the model: outputs are compact summaries with provenance.
The Groundhog classes stay hidden from the model (exposure_policy); these tools do the
multi-step set-up deterministically (core.geoai.cpt_pile_capacity).
"""
from typing import Any, Dict, List, Optional

from core.geoai.tool_registry import geoai_tool
from core.geoai import project_cpt
from core.geoai.schemas.cpt_piles import (
    ListProjectCPTsInput, ListProjectCPTsOutput, CPTSummaryInput, CPTSummaryOutput,
    PileCapacityFromCPTInput, PileCapacityFromCPTOutput,
)

MAX_LISTED_CPTS = 50


def _store():
    """Project object store (monkeypatched in tests)."""
    return project_cpt.default_store()


@geoai_tool(
    name="list_project_cpts",
    description="Lists the CPTs available in the current project: CPT id, depth range, channels, location.",
    category="in_situ",
    input_model=ListProjectCPTsInput,
    output_model=ListProjectCPTsOutput,
)
def list_project_cpts():
    """
    Which CPTs are in the project (CPT-01, CPT-03 ...): all available CPT soundings.

    Sources: SoilProfile CPT tables, PCPTProcessing objects and AGS SCPT groups in the GeoCore
    workspace object store; no raw data is returned.
    """
    cpts, unusable = project_cpt.discover_project_cpts(_store())
    note = "CPTs read from the GeoCore workspace (SoilProfile CPT tables, PCPTProcessing, AGS SCPT)."
    if not cpts:
        note += (" No usable CPT found: load a CPT table with depth and qc columns with units in the headers "
                 "(e.g. 'z [m]', 'qc [MPa]', 'fs [kPa]', 'u2 [kPa]') or an AGS file with an SCPT group.")
    listed = sorted(cpts, key=lambda c: project_cpt.normalize_cpt_id(c.cpt_id))
    if len(listed) > MAX_LISTED_CPTS:
        note += f" Showing the first {MAX_LISTED_CPTS} of {len(listed)}."
    return {"count": len(cpts), "cpts": [c.listing() for c in listed[:MAX_LISTED_CPTS]],
            "unusable_sources": unusable[:10], "note": note}


@geoai_tool(
    name="get_cpt_summary",
    description="Summarises one project CPT: depth range, soil layering from Robertson SBT/Ic intervals with "
                "qc [MPa], fs and u2 [kPa] ranges per layer, data-quality flags and provenance.",
    category="in_situ",
    input_model=CPTSummaryInput,
    output_model=CPTSummaryOutput,
)
def get_cpt_summary(cpt_id: str, min_layer_thickness_m: float = 0.5, max_intervals: int = 12):
    """
    CPT sounding summary, interpretation and soil behaviour type layering (cone resistance, sleeve friction,
    pore pressure, Ic) of one CPT.
    """
    cpt = project_cpt.resolve_cpt(cpt_id, _store())
    flags = project_cpt.data_quality_flags(cpt)
    layering: List[Dict[str, Any]] = []
    if project_cpt.sbt_available(cpt):
        for iv in project_cpt.sbt_intervals(cpt, min_thickness=min_layer_thickness_m, max_intervals=max_intervals,
                                            water_table_depth=cpt.groundwater_depth_m):
            layering.append({k: v for k, v in iv.items() if not k.startswith("_")})
    gw = cpt.groundwater_depth_m
    method = ("Robertson (2009) Ic / SBT zones via core.geoai.cpt.CPTSounding; "
              f"unit weight {project_cpt.SBT_UNIT_WEIGHT_KN_M3} kN/m3; "
              + (f"groundwater at {gw} m" if gw is not None else "groundwater assumed at ground level (not stored)")
              + f"; intervals thinner than {min_layer_thickness_m} m merged into a neighbour")
    if not layering:
        method = "No SBT layering: sleeve friction (fs) not available."
    return {
        "cpt_id": cpt.cpt_id,
        "depth_range_m": [round(cpt.depth_min, 2), round(cpt.depth_max, 2)],
        "n_points": int(len(cpt.data)),
        "median_spacing_m": None if project_cpt.median_spacing(cpt) is None else round(project_cpt.median_spacing(cpt), 3),
        "channels": cpt.channels(),
        "groundwater_depth_m": gw,
        "location": {k: v for k, v in cpt.location.items() if v is not None} or None,
        "layering": layering,
        "data_quality_flags": flags,
        "provenance": {"source": {k: v for k, v in cpt.source.items()}, "groundwater_source": cpt.groundwater_source,
                       "interpretation": method},
    }


@geoai_tool(
    name="calculate_pile_capacity_from_cpt",
    description="Calculates the ultimate axial pile capacity (shaft, base and total resistance in kN) of a "
                "single pile from a project CPT using Groundhog's LCPC, Koppejan or De Beer method.",
    category="deep_foundations",
    input_model=PileCapacityFromCPTInput,
    output_model=PileCapacityFromCPTOutput,
)
def calculate_pile_capacity_from_cpt(cpt_id: str, method: str, pile_type: str, pile_diameter_m: float,
                                     pile_tip_depth_m: float, wall_thickness_mm: Optional[float] = None,
                                     open_end_condition: Optional[str] = None,
                                     shaft_start_depth_m: Optional[float] = None,
                                     groundwater_depth_m: Optional[float] = None,
                                     debeer_alpha_s: Optional[float] = None, debeer_alpha_b: Optional[float] = None,
                                     soil_layers: Optional[List[Any]] = None):
    """
    Pile bearing capacity / axial resistance from cone penetration test (CPT) data: skin friction (shaft
    resistance) and end bearing (base / tip resistance) of a driven or bored pile at a CPT location,
    for a given pile diameter and pile tip depth (penetration / embedded length).

    Reference: Bustamante & Gianeselli (1982) LCPC; Koppejan; De Beer (Belgian practice).
    """
    from core.geoai import cpt_pile_capacity as engine
    cpt = project_cpt.resolve_cpt(cpt_id, _store())
    layers = None
    if soil_layers:
        layers = [l.model_dump() if hasattr(l, "model_dump") else dict(l) for l in soil_layers]
    try:
        return engine.calculate(cpt, method, pile_type, float(pile_diameter_m), float(pile_tip_depth_m),
                                wall_thickness_mm, open_end_condition, shaft_start_depth_m, groundwater_depth_m,
                                debeer_alpha_s, debeer_alpha_b, layers)
    except (ValueError, KeyError, IndexError) as e:
        from core.geoai.exceptions import GeoAIValidationError
        raise GeoAIValidationError(
            f"Groundhog {engine.METHOD_INFO[method]['class'].rsplit('.', 1)[-1]} could not complete the "
            f"calculation for {cpt.cpt_id}: {e}", errors=[{"type": "groundhog_error", "message": str(e)}])
