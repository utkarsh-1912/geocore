# Author: Utkarsh Gupta
# License: GPL v3
"""
Canonical Pydantic Schemas for In-Situ Investigation Tools (CPT, SPT, AGS).
"""

from typing import Optional, Literal
from pydantic import Field, AliasChoices
from core.geoai.schemas.base import GeoAIBaseModel, GeoAIOutputModel, GeotechnicalField


# --- SPT Normalization & Correlations ---
class NormalizeSPTInput(GeoAIBaseModel):
    """
    Normalizes field SPT blow count N to standard N60 and overburden-corrected (N1)60
    and correlates relative density Dr and friction angle phi'.
    """
    raw_n: int = GeotechnicalField(
        ...,
        ge=0,
        le=150,
        unit="-",
        description="Field measured SPT blow count N",
        validation_alias=AliasChoices('raw_n', 'N', 'n_raw', 'blow_count')
    )
    depth: float = GeotechnicalField(
        ...,
        ge=0.0,
        le=200.0,
        unit="m",
        description="Depth below ground surface where SPT was conducted",
        validation_alias=AliasChoices('depth', 'z', 'test_depth')
    )
    energy_ratio: float = GeotechnicalField(
        0.60,
        ge=0.20,
        le=1.0,
        unit="-",
        description="Hammer energy ratio Er (0.60 for 60% standard safety hammer)",
        validation_alias=AliasChoices('energy_ratio', 'Er', 'er')
    )
    rod_length: float = GeotechnicalField(
        10.0,
        ge=1.0,
        le=200.0,
        unit="m",
        description="Total length of drill rods in meters",
        validation_alias=AliasChoices('rod_length', 'L', 'rod_len')
    )
    borehole_diameter_mm: float = GeotechnicalField(
        150.0,
        ge=50.0,
        le=300.0,
        unit="mm",
        description="Borehole diameter in mm",
        validation_alias=AliasChoices('borehole_diameter_mm', 'dia_mm', 'borehole_dia')
    )
    has_liner: bool = GeotechnicalField(
        False,
        description="True if split-spoon sampler was equipped with standard liner",
        validation_alias=AliasChoices('has_liner', 'liner')
    )
    overburden_kpa: Optional[float] = GeotechnicalField(
        None,
        ge=1.0,
        le=5000.0,
        unit="kPa",
        description="Effective vertical overburden stress sigma_v0' [kPa]",
        validation_alias=AliasChoices('overburden_kpa', 'sigma_v0_eff', 'effective_stress')
    )


class NormalizeSPTOutput(GeoAIOutputModel):
    N60: float = GeotechnicalField(..., unit="-", description="Energy-corrected SPT blow count N60")
    N1_60: float = GeotechnicalField(..., unit="-", description="Overburden stress-normalized (N1)60")
    Dr_pct: float = GeotechnicalField(..., unit="%", description="Empirical relative density Dr [%] (Skempton 1986)")
    phi_eff_deg: float = GeotechnicalField(..., unit="deg", description="Correlated effective friction angle phi' [deg] (Wolff 1989)")
    density_class: str = GeotechnicalField(..., description="Soil compactness description class")


# --- CPT Soil Behavior Type Classification ---
class ClassifyCPTSoilBehaviorInput(GeoAIBaseModel):
    """
    Classifies soil behavior type (SBT) and calculates normalized CPT indices
    (Qt, Fr, Bq, Ic) according to Robertson (1990/2009).
    """
    qc_mpa: float = GeotechnicalField(
        ...,
        gt=0.0,
        le=200.0,
        unit="MPa",
        description="Measured cone tip resistance qc [MPa]",
        validation_alias=AliasChoices('qc_mpa', 'qc', 'cone_resistance')
    )
    fs_kpa: float = GeotechnicalField(
        ...,
        ge=0.0,
        le=5000.0,
        unit="kPa",
        description="Measured sleeve friction fs [kPa]",
        validation_alias=AliasChoices('fs_kpa', 'fs', 'sleeve_friction')
    )
    depth: float = GeotechnicalField(
        ...,
        gt=0.0,
        le=200.0,
        unit="m",
        description="Measurement depth z [m]",
        validation_alias=AliasChoices('depth', 'z')
    )
    u2_kpa: float = GeotechnicalField(
        0.0,
        ge=-100.0,
        le=10000.0,
        unit="kPa",
        description="Measured shoulder pore pressure u2 [kPa]",
        validation_alias=AliasChoices('u2_kpa', 'u2', 'pore_pressure')
    )
    water_table_depth: float = GeotechnicalField(
        0.0,
        ge=0.0,
        unit="m",
        description="Depth to groundwater table below surface [m]",
        validation_alias=AliasChoices('water_table_depth', 'gwt', 'water_table')
    )


class ClassifyCPTSoilBehaviorOutput(GeoAIOutputModel):
    Qt: float = GeotechnicalField(..., unit="-", description="Normalized cone resistance Qt")
    Fr_pct: float = GeotechnicalField(..., unit="%", description="Normalized friction ratio Fr [%]")
    Bq: float = GeotechnicalField(..., unit="-", description="Pore pressure ratio Bq")
    Ic: float = GeotechnicalField(..., unit="-", description="Soil Behavior Type Index Ic")
    sbt_zone: int = GeotechnicalField(..., description="Robertson 1990 SBT Zone (1 to 9)")
    sbt_description: str = GeotechnicalField(..., description="Soil classification description")


# --- CPT Parameter Derivations ---
class DeriveCPTParametersInput(GeoAIBaseModel):
    """
    Derives engineering design parameters (su, phi', Dr, Gmax) from CPT measurements.
    """
    qc_mpa: float = GeotechnicalField(
        ...,
        gt=0.0,
        le=200.0,
        unit="MPa",
        description="Measured cone tip resistance qc [MPa]",
        validation_alias=AliasChoices('qc_mpa', 'qc')
    )
    fs_kpa: float = GeotechnicalField(
        ...,
        ge=0.0,
        le=5000.0,
        unit="kPa",
        description="Measured sleeve friction fs [kPa]",
        validation_alias=AliasChoices('fs_kpa', 'fs')
    )
    depth: float = GeotechnicalField(
        ...,
        gt=0.0,
        le=200.0,
        unit="m",
        description="Measurement depth z [m]",
        validation_alias=AliasChoices('depth', 'z')
    )
    Nkt: float = GeotechnicalField(
        15.0,
        ge=5.0,
        le=30.0,
        unit="-",
        description="Empirical cone factor Nkt for undrained shear strength (typically 12 - 18)",
        validation_alias=AliasChoices('Nkt', 'nkt', 'cone_factor')
    )


class DeriveCPTParametersOutput(GeoAIOutputModel):
    Ic: float = GeotechnicalField(..., unit="-", description="Soil Behavior Type Index Ic")
    sbt_description: str = GeotechnicalField(..., description="Soil Behavior Classification")
    su_kpa: Optional[float] = GeotechnicalField(None, unit="kPa", description="Undrained shear strength su [kPa] (for fine-grained soils)")
    phi_eff_deg: Optional[float] = GeotechnicalField(None, unit="deg", description="Effective friction angle phi' [deg] (for coarse-grained soils)")
    Dr_pct: Optional[float] = GeotechnicalField(None, unit="%", description="Relative density Dr [%] (for coarse-grained soils)")
    Gmax_kpa: float = GeotechnicalField(..., unit="kPa", description="Small-strain shear modulus Gmax [kPa] (Robertson 2009)")
