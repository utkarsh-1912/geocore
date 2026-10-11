# Author: Utkarsh Gupta
# License: GPL v3
"""Schemas of the project ground model tool (core.geoai.tools_project_model). Depths in m below the surface."""
from typing import Any, Dict, List, Optional

from pydantic import AliasChoices, model_validator

from core.geoai.exceptions import GeoAIValidationError
from core.geoai.schemas.base import GeoAIBaseModel, GeoAIOutputModel, GeotechnicalField


class ProjectInputsInput(GeoAIBaseModel):
    calculation: str = GeotechnicalField(
        ..., description="The calculation whose inputs are wanted: the name of the tool that will run it, "
                         "or a GeoCore function id",
        validation_alias=AliasChoices("calculation", "tool", "tool_name", "function", "function_id"))
    location: str = GeotechnicalField(
        ..., description="Borehole / CPT / profile name in the project, e.g. 'BH-01'",
        validation_alias=AliasChoices("location", "borehole", "location_name", "profile"))
    z_top_m: float = GeotechnicalField(..., unit="m", ge=0.0, description="Top of the depth range, depth below surface [m]",
                                       validation_alias=AliasChoices("z_top_m", "z_top", "depth_from_m", "top_m"))
    z_bottom_m: float = GeotechnicalField(..., unit="m", ge=0.0, description="Bottom of the depth range, depth below surface [m]",
                                          validation_alias=AliasChoices("z_bottom_m", "z_bottom", "depth_to_m", "bottom_m"))

    @model_validator(mode="after")
    def _positive_interval(self):
        if self.z_bottom_m <= self.z_top_m:
            raise GeoAIValidationError(
                f"z_bottom_m ({self.z_bottom_m:g} m) must be below z_top_m ({self.z_top_m:g} m).")
        return self


class ProjectInputsOutput(GeoAIOutputModel):
    location: str = GeotechnicalField(..., description="Project location the values come from")
    depth_range_m: List[float] = GeotechnicalField(..., unit="m", description="Depth range used [m]")
    values: Dict[str, Dict[str, Any]] = GeotechnicalField(
        ..., description="Input name -> {value, unit, source}: thickness-weighted project values with their source")
    unavailable: Dict[str, str] = GeotechnicalField(..., description="Input name -> why the project cannot supply it")
    note: Optional[str] = GeotechnicalField(None, description="How the values were obtained")
