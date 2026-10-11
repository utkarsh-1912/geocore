# Author: Utkarsh Gupta
# License: GPL v3
"""
GeoAI tool on the project ground model (core/project, AGENTS.md §14, §28-29):

- ``get_project_inputs``  the inputs of a calculation that the project can supply for one location and depth
                          range, each with its source (profile column and layer, AGS SPT tests, or an earlier
                          saved calculation)

It uses the same rules as the form's "Project values" panel (core.project.ground.prefill): thickness-weighted over
the depth range, units converted deterministically, values <= 0 treated as "not defined", nothing defaulted. What the
project cannot supply is listed with the reason, so the agent asks the user for it.

The project index is refreshed from the workspace's saved soil profiles first (read-only on the workspace, the same
sync as the panel's button); AGS imports are kept.
"""
from typing import Optional

from core.geoai.exceptions import GeoAIValidationError
from core.geoai.schemas.project_model import ProjectInputsInput, ProjectInputsOutput
from core.geoai.tool_registry import geoai_tool, tool_registry


def _function_and_names(calculation: str):
    """(GeoCore function id, {groundhog parameter: name the GeoAI tool uses})."""
    from core.geoai.catalogue_link import tool_function_id
    tool = tool_registry.get_tool(calculation)
    if tool is None:
        return calculation, {}
    arg_map = getattr(tool.func, "__geoai_arg_map__", None) or {}
    return tool_function_id(tool), {groundhog: name for name, groundhog in arg_map.items()}


def _location_id(name: str) -> Optional[int]:
    from core.project.ground import summary
    wanted = name.strip().lower()
    for loc in summary()["locations"]:
        if loc["name"].strip().lower() == wanted:
            return loc["id"]
    return None


@geoai_tool(
    name="get_project_inputs",
    description="Gets the inputs of a calculation that the project can supply (from borehole, CPT or "
                "AGS data, or earlier saved calculations) for one location and depth range, each with its source.",
    category="project",
    input_model=ProjectInputsInput,
    output_model=ProjectInputsOutput,
)
def get_project_inputs(calculation: str, location: str, z_top_m: float, z_bottom_m: float):
    """Project values for a calculation's inputs, thickness-weighted over a depth range, with sources."""
    from core.project.ground import prefill, summary, sync_from_workspace
    sync_from_workspace()
    loc_id = _location_id(location)
    if loc_id is None:
        names = [l["name"] for l in summary()["locations"]]
        raise GeoAIValidationError(
            f"Location '{location}' is not in the project. Locations: {', '.join(names) if names else 'none'}"
            + ("" if names else " (save a soil profile or CPT table, or import an AGS file, first)") + ".")
    function_id, renamed = _function_and_names(calculation)
    try:
        result = prefill(function_id, loc_id, z_top_m, z_bottom_m)
    except ValueError as e:
        raise GeoAIValidationError(str(e))
    values = {renamed.get(k, k): {"value": p["value"], "unit": p["unit"], "source": p["source"]}
              for k, p in result["proposals"].items()}
    unavailable = {renamed.get(k, k): why for k, why in result["unavailable"].items()}
    return {
        "location": result["location"]["name"],
        "depth_range_m": [z_top_m, z_bottom_m],
        "values": values,
        "unavailable": unavailable,
        "note": ("Thickness-weighted project values over the depth range; units converted deterministically. "
                 "Inputs not listed have no project data: ask the user for them."),
    }
