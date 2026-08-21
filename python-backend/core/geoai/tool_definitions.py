"""
Standard Tool Definitions for GeoAI
Binds Groundhog functions to the Tool Registry with canonical schemas.
"""
import groundhog.siteinvestigation.classification.phaserelations as pr
import groundhog.shallowfoundations.stressdistribution as sd
import groundhog.soildynamics.soilproperties as dp
import groundhog.excavations.basic as ep
import groundhog.pipelinescables.stability.penetration as pipe
import groundhog.consolidation.groundwaterflow.pumpingtests as gw

from core.geoai.tool_registry import tool_registry, geoai_tool
from core.geoai.schemas.classification import (
    BulkUnitWeightInput, BulkUnitWeightOutput,
    VoidRatioPorosityInput, VoidRatioPorosityOutput,
    RelativeDensityInput, RelativeDensityOutput
)
from core.geoai.schemas.shallowfoundations import (
    StressesCircleInput, StressesCircleOutput,
    StressesPointloadInput, StressesPointloadOutput
)
from core.geoai.schemas.expanded import (
    GmaxShearWaveVelocityInput, GmaxShearWaveVelocityOutput,
    EarthPressureRankineInput, EarthPressureRankineOutput,
    ContactWidthInput, ContactWidthOutput,
    HydraulicConductivityUnconfinedInput, HydraulicConductivityUnconfinedOutput
)

# 1. Bulk Unit Weight
@geoai_tool(
    name="calculate_bulk_unit_weight",
    description="Calculates bulk unit weight (gamma) and effective unit weight from specific gravity (Gs), void ratio (e), and degree of saturation (Sr).",
    category="classification",
    input_model=BulkUnitWeightInput,
    output_model=BulkUnitWeightOutput
)
def calculate_bulk_unit_weight(**kwargs):
    return pr.bulkunitweight(**kwargs)


# 2. Void Ratio from Porosity
@geoai_tool(
    name="calculate_void_ratio_from_porosity",
    description="Calculates void ratio (e) from porosity (n) using phase relations: e = n / (1 - n).",
    category="classification",
    input_model=VoidRatioPorosityInput,
    output_model=VoidRatioPorosityOutput
)
def calculate_void_ratio_from_porosity(**kwargs):
    return pr.voidratio_porosity(**kwargs)


# 3. Relative Density
@geoai_tool(
    name="calculate_relative_density",
    description="Calculates soil relative density (Dr) from current void ratio (e), minimum void ratio (e_min), and maximum void ratio (e_max).",
    category="classification",
    input_model=RelativeDensityInput,
    output_model=RelativeDensityOutput
)
def calculate_relative_density(**kwargs):
    return pr.relative_density(**kwargs)


# 4. Vertical Stresses below Circular Footing
@geoai_tool(
    name="calculate_stresses_circular_footing",
    description="Calculates vertical and horizontal elastic stress increments in a soil half-space under the center of a circular loaded area.",
    category="shallow_foundations",
    input_model=StressesCircleInput,
    output_model=StressesCircleOutput
)
def calculate_stresses_circular_footing(**kwargs):
    return sd.stresses_circle(**kwargs)


# 5. Point Load Stresses (Boussinesq)
@geoai_tool(
    name="calculate_stresses_point_load",
    description="Calculates 3D elastic stress distribution (sigma_z, sigma_r, sigma_theta, tau_rz) from a concentrated surface point load using Boussinesq theory.",
    category="shallow_foundations",
    input_model=StressesPointloadInput,
    output_model=StressesPointloadOutput
)
def calculate_stresses_point_load(**kwargs):
    return sd.stresses_pointload(**kwargs)


# 6. Gmax from Shear Wave Velocity
@geoai_tool(
    name="calculate_gmax_from_shear_wave_velocity",
    description="Calculates small-strain shear modulus Gmax [MPa] from shear wave velocity Vs [m/s] and unit weight gamma [kN/m3].",
    category="soil_dynamics",
    input_model=GmaxShearWaveVelocityInput,
    output_model=GmaxShearWaveVelocityOutput
)
def calculate_gmax_from_shear_wave_velocity(**kwargs):
    return dp.gmax_shearwavevelocity(**kwargs)


# 7. Earth Pressure Coefficients (Rankine)
@geoai_tool(
    name="calculate_earth_pressure_rankine",
    description="Calculates active (Ka) and passive (Kp) lateral earth pressure coefficients for inclined or vertical walls using Rankine theory.",
    category="excavations",
    input_model=EarthPressureRankineInput,
    output_model=EarthPressureRankineOutput
)
def calculate_earth_pressure_rankine(**kwargs):
    return ep.earthpressurecoefficients_rankine(**kwargs)


# 8. Pipeline Contact Width
@geoai_tool(
    name="calculate_pipeline_contact_width",
    description="Calculates contact width between a subsea pipeline and seabed from outer diameter and embedment depth.",
    category="pipelines",
    input_model=ContactWidthInput,
    output_model=ContactWidthOutput
)
def calculate_pipeline_contact_width(**kwargs):
    return pipe.contactwidth(**kwargs)


# 9. Hydraulic Conductivity (Pumping Test)
@geoai_tool(
    name="calculate_hydraulic_conductivity_unconfined",
    description="Calculates aquifer hydraulic conductivity k [m/s] from unconfined steady-state pumping test data using the Dupuit-Thiem solution.",
    category="consolidation",
    input_model=HydraulicConductivityUnconfinedInput,
    output_model=HydraulicConductivityUnconfinedOutput
)
def calculate_hydraulic_conductivity_unconfined(**kwargs):
    return gw.hydraulicconductivity_unconfinedaquifer(**kwargs)
