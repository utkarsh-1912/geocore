"""
Canonical Pydantic Schemas for Soil Dynamics, Earth Pressures, Pipelines & Consolidation
"""
from typing import Optional, Literal
from pydantic import Field, AliasChoices
from core.geoai.schemas.base import GeoAIBaseModel, GeotechnicalField


# --- Dynamics: Gmax from Shear Wave Velocity ---
class GmaxShearWaveVelocityInput(GeoAIBaseModel):
    """
    Calculates small-strain shear modulus Gmax [kPa] from shear wave velocity Vs [m/s]
    and total unit weight gamma [kN/m3]: Gmax = rho * Vs^2.
    """
    Vs: float = GeotechnicalField(
        ...,
        gt=0.0,
        le=3000.0,
        unit="m/s",
        description="Shear wave velocity Vs",
        validation_alias=AliasChoices('Vs', 'vs', 'shear_wave_velocity')
    )
    gamma: float = GeotechnicalField(
        ...,
        ge=5.0,
        le=30.0,
        unit="kN/m3",
        description="Total unit weight of soil gamma",
        validation_alias=AliasChoices('gamma', 'unit_weight', 'total_unit_weight')
    )
    g: float = GeotechnicalField(
        9.81,
        gt=9.0,
        le=10.0,
        unit="m/s2",
        description="Acceleration due to gravity g",
        validation_alias=AliasChoices('g', 'gravity')
    )


class GmaxShearWaveVelocityOutput(GeoAIBaseModel):
    Gmax: float = GeotechnicalField(
        ...,
        unit="kPa",
        description="Small-strain shear modulus Gmax [kPa]",
        validation_alias=AliasChoices('Gmax [kPa]', 'Gmax', 'gmax')
    )
    rho: Optional[float] = GeotechnicalField(
        None,
        unit="kg/m3",
        description="Soil density rho",
        validation_alias=AliasChoices('rho [kg/m3]', 'rho')
    )


# --- Excavations: Rankine Earth Pressure Coefficients ---
class EarthPressureRankineInput(GeoAIBaseModel):
    """
    Calculates active and passive earth pressure coefficients using Rankine theory.
    """
    phi_eff: float = GeotechnicalField(
        ...,
        ge=0.0,
        le=60.0,
        unit="deg",
        description="Effective friction angle phi'",
        validation_alias=AliasChoices('phi_eff', 'friction_angle', 'phi')
    )
    wall_angle: float = GeotechnicalField(
        0.0,
        ge=-45.0,
        le=45.0,
        unit="deg",
        description="Wall inclination angle beta (0 for vertical wall)",
        validation_alias=AliasChoices('wall_angle', 'beta')
    )
    top_angle: float = GeotechnicalField(
        0.0,
        ge=-45.0,
        le=45.0,
        unit="deg",
        description="Backfill slope angle alpha (0 for horizontal backfill)",
        validation_alias=AliasChoices('top_angle', 'alpha')
    )


class EarthPressureRankineOutput(GeoAIBaseModel):
    Ka: float = GeotechnicalField(..., unit="-", description="Active earth pressure coefficient Ka", validation_alias=AliasChoices('KaR [-]', 'Ka [-]', 'Ka', 'ka'))
    Kp: float = GeotechnicalField(..., unit="-", description="Passive earth pressure coefficient Kp", validation_alias=AliasChoices('KpR [-]', 'Kp [-]', 'Kp', 'kp'))


# --- Pipelines: Contact Width ---
class ContactWidthInput(GeoAIBaseModel):
    """
    Calculates pipeline-seabed contact width 2*b from pipe diameter D and penetration z.
    """
    diameter: float = GeotechnicalField(
        ...,
        gt=0.0,
        le=10.0,
        unit="m",
        description="Outer pipeline diameter D",
        validation_alias=AliasChoices('diameter', 'D', 'pipe_diameter')
    )
    penetration: float = GeotechnicalField(
        ...,
        ge=0.0,
        unit="m",
        description="Seabed embedment/penetration depth z",
        validation_alias=AliasChoices('penetration', 'z', 'embedment')
    )


class ContactWidthOutput(GeoAIBaseModel):
    contact_width: float = GeotechnicalField(
        ...,
        unit="m",
        description="Contact width 2*b",
        validation_alias=AliasChoices('B [m]', 'contact width [m]', 'contact_width')
    )


# --- Consolidation: Hydraulic Conductivity from Unconfined Aquifer Pumping Test ---
class HydraulicConductivityUnconfinedInput(GeoAIBaseModel):
    """
    Dupuit-Thiem equation for unconfined steady-state pumping test.
    k = (Q * ln(r2 / r1)) / (pi * (h2^2 - h1^2))
    """
    radius_1: float = GeotechnicalField(..., gt=0.0, unit="m", description="Radial distance to observation well 1 r1", validation_alias=AliasChoices('radius_1', 'r1'))
    radius_2: float = GeotechnicalField(..., gt=0.0, unit="m", description="Radial distance to observation well 2 r2", validation_alias=AliasChoices('radius_2', 'r2'))
    piezometric_height_1: float = GeotechnicalField(..., gt=0.0, unit="m", description="Piezometric height at observation well 1 h1", validation_alias=AliasChoices('piezometric_height_1', 'h1'))
    piezometric_height_2: float = GeotechnicalField(..., gt=0.0, unit="m", description="Piezometric height at observation well 2 h2", validation_alias=AliasChoices('piezometric_height_2', 'h2'))
    flowrate: float = GeotechnicalField(..., gt=0.0, unit="m3/s", description="Steady discharge rate Q", validation_alias=AliasChoices('flowrate', 'Q'))


class HydraulicConductivityUnconfinedOutput(GeoAIBaseModel):
    hydraulic_conductivity: float = GeotechnicalField(
        ...,
        unit="m/s",
        description="Hydraulic conductivity k",
        validation_alias=AliasChoices('hydraulic_conductivity [m/s]', 'hydraulic conductivity [m/s]', 'k', 'hydraulic_conductivity')
    )
