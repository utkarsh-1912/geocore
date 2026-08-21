"""
Canonical Pydantic Schemas for Shallow Foundations (Stress Distribution & Capacity)
"""
from typing import Optional, Literal, Dict, Any, List
from pydantic import Field
from core.geoai.schemas.base import GeoAIBaseModel, GeotechnicalField


# --- stresses_circle ---
class StressesCircleInput(GeoAIBaseModel):
    """
    Vertical stress below the center of a circular loaded area on an elastic half-space.
    """
    z: float = GeotechnicalField(
        ...,
        ge=0.0,
        le=500.0,
        unit="m",
        description="Depth below foundation base z"
    )
    footing_radius: float = GeotechnicalField(
        ...,
        gt=0.0,
        le=100.0,
        unit="m",
        description="Radius of circular footing R"
    )
    imposedstress: float = GeotechnicalField(
        ...,
        gt=0.0,
        unit="kPa",
        description="Uniform vertical pressure q applied by footing"
    )
    poissonsratio: float = GeotechnicalField(
        0.3,
        gt=-1.0,
        le=0.5,
        unit="-",
        description="Poisson's ratio nu of the soil"
    )


class StressesCircleOutput(GeoAIBaseModel):
    sigma_z: float = GeotechnicalField(
        ...,
        unit="kPa",
        description="Vertical stress increase Delta sigma_z"
    )
    sigma_r: Optional[float] = GeotechnicalField(
        None,
        unit="kPa",
        description="Radial stress increase Delta sigma_r"
    )
    sigma_theta: Optional[float] = GeotechnicalField(
        None,
        unit="kPa",
        description="Circumferential stress increase Delta sigma_theta"
    )


# --- stresses_pointload (Boussinesq) ---
class StressesPointloadInput(GeoAIBaseModel):
    pointload: float = GeotechnicalField(
        ...,
        gt=0.0,
        unit="kN",
        description="Magnitude of point load Q"
    )
    z: float = GeotechnicalField(
        ...,
        gt=0.0,
        unit="m",
        description="Depth below surface z"
    )
    r: float = GeotechnicalField(
        0.0,
        ge=0.0,
        unit="m",
        description="Radial horizontal distance from point load r"
    )
    poissonsratio: float = GeotechnicalField(
        0.3,
        gt=-1.0,
        le=0.5,
        unit="-",
        description="Poisson's ratio nu"
    )


class StressesPointloadOutput(GeoAIBaseModel):
    sigma_z: float = GeotechnicalField(..., unit="kPa", description="Vertical stress Delta sigma_z")
    sigma_r: Optional[float] = GeotechnicalField(None, unit="kPa", description="Radial stress Delta sigma_r")
    sigma_theta: Optional[float] = GeotechnicalField(None, unit="kPa", description="Tangential stress Delta sigma_theta")
    tau_rz: Optional[float] = GeotechnicalField(None, unit="kPa", description="Shear stress Delta tau_rz")


# --- shallow_foundation_capacity_undrained ---
class ShallowFoundationCapacityUndrainedInput(GeoAIBaseModel):
    foundation_shape: Literal['rectangle', 'circle'] = GeotechnicalField(
        'rectangle',
        description="Foundation geometry shape ('rectangle' or 'circle')"
    )
    width: float = GeotechnicalField(
        ...,
        gt=0.0,
        unit="m",
        description="Foundation width B (or diameter for circle)"
    )
    length: Optional[float] = GeotechnicalField(
        None,
        gt=0.0,
        unit="m",
        description="Foundation length L (for rectangular foundation)"
    )
    base_depth: float = GeotechnicalField(
        0.0,
        ge=0.0,
        unit="m",
        description="Embedment depth D"
    )
    skirted: bool = GeotechnicalField(
        True,
        description="Whether foundation is skirted"
    )
    eccentricity_length: float = GeotechnicalField(
        0.0,
        ge=0.0,
        unit="m",
        description="Load eccentricity along length e_L"
    )
    eccentricity_width: float = GeotechnicalField(
        0.0,
        ge=0.0,
        unit="m",
        description="Load eccentricity along width e_B"
    )
    unit_weight: float = GeotechnicalField(
        ...,
        ge=5.0,
        le=30.0,
        unit="kN/m3",
        description="Soil unit weight gamma"
    )
    su_base: float = GeotechnicalField(
        ...,
        gt=0.0,
        unit="kPa",
        description="Undrained shear strength at foundation base su0"
    )
    su_increase: float = GeotechnicalField(
        0.0,
        ge=0.0,
        unit="kPa/m",
        description="Increase of undrained shear strength with depth k_su"
    )
    su_above_base: Optional[float] = GeotechnicalField(
        None,
        ge=0.0,
        unit="kPa",
        description="Average undrained shear strength above base level"
    )
    factor_sliding: float = GeotechnicalField(
        1.5,
        ge=1.0,
        unit="-",
        description="Safety factor for sliding"
    )
    factor_bearing: float = GeotechnicalField(
        2.0,
        ge=1.0,
        unit="-",
        description="Safety factor for bearing capacity"
    )
