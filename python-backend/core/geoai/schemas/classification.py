"""
Canonical Pydantic Schemas for Geotechnical Classification & Phase Relations
"""
from typing import Optional, Literal
from pydantic import Field, AliasChoices
from core.geoai.schemas.base import GeoAIBaseModel, GeotechnicalField


# --- bulkunitweight ---
class BulkUnitWeightInput(GeoAIBaseModel):
    """
    Calculate bulk unit weight from specific gravity, void ratio, and degree of saturation.
    gamma = (Gs + Sr * e) / (1 + e) * gamma_w
    """
    saturation: float = GeotechnicalField(
        ...,
        ge=0.0,
        le=1.0,
        unit="-",
        description="Degree of saturation Sr (fraction between 0.0 and 1.0)",
        validation_alias=AliasChoices('saturation', 'Sr')
    )
    voidratio: float = GeotechnicalField(
        ...,
        gt=0.01,
        le=10.0,
        unit="-",
        description="Void ratio e",
        validation_alias=AliasChoices('voidratio', 'void_ratio', 'e')
    )
    specific_gravity: float = GeotechnicalField(
        2.65,
        gt=1.0,
        le=5.0,
        unit="-",
        description="Specific gravity of soil solids Gs (typically 2.6 - 2.8 for soils)",
        validation_alias=AliasChoices('specific_gravity', 'Gs')
    )
    unitweight_water: float = GeotechnicalField(
        9.81,
        gt=8.0,
        le=12.0,
        unit="kN/m3",
        description="Unit weight of water gamma_w",
        validation_alias=AliasChoices('unitweight_water', 'water_unit_weight', 'waterunitweight', 'gamma_w')
    )


class BulkUnitWeightOutput(GeoAIBaseModel):
    bulk_unit_weight: float = GeotechnicalField(
        ...,
        unit="kN/m3",
        description="Bulk unit weight gamma",
        validation_alias=AliasChoices('bulk unit weight [kN/m3]', 'bulk_unit_weight')
    )


# --- voidratio_porosity ---
class VoidRatioPorosityInput(GeoAIBaseModel):
    porosity: float = GeotechnicalField(
        ...,
        gt=0.0,
        lt=1.0,
        unit="-",
        description="Porosity n (fraction between 0.0 and 1.0)",
        validation_alias=AliasChoices('porosity', 'n')
    )


class VoidRatioPorosityOutput(GeoAIBaseModel):
    void_ratio: float = GeotechnicalField(
        ...,
        unit="-",
        description="Void ratio e",
        validation_alias=AliasChoices('void ratio [-]', 'void_ratio', 'voidratio')
    )


# --- relative_density ---
class RelativeDensityInput(GeoAIBaseModel):
    voidratio: float = GeotechnicalField(
        ...,
        gt=0.01,
        unit="-",
        description="Current void ratio e",
        validation_alias=AliasChoices('voidratio', 'void_ratio', 'e')
    )
    e_min: float = GeotechnicalField(
        ...,
        gt=0.01,
        unit="-",
        description="Minimum void ratio e_min (densest state)",
        validation_alias=AliasChoices('e_min', 'emin')
    )
    e_max: float = GeotechnicalField(
        ...,
        gt=0.01,
        unit="-",
        description="Maximum void ratio e_max (loosest state)",
        validation_alias=AliasChoices('e_max', 'emax')
    )


class RelativeDensityOutput(GeoAIBaseModel):
    relative_density: float = GeotechnicalField(
        ...,
        unit="-",
        description="Relative density Dr (fraction between 0 and 1)",
        validation_alias=AliasChoices('relative density [-]', 'relative_density', 'Dr')
    )
