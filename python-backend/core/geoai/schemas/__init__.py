"""
GeoAI Schema Registry
Maps function_id to (InputSchema, OutputSchema)
"""
from typing import Dict, Tuple, Type, Optional
from core.geoai.schemas.base import GeoAIBaseModel
from core.geoai.schemas.classification import (
    BulkUnitWeightInput, BulkUnitWeightOutput,
    VoidRatioPorosityInput, VoidRatioPorosityOutput,
    RelativeDensityInput, RelativeDensityOutput
)
from core.geoai.schemas.shallowfoundations import (
    StressesCircleInput, StressesCircleOutput,
    StressesPointloadInput, StressesPointloadOutput,
    ShallowFoundationCapacityUndrainedInput
)
from core.geoai.schemas.expanded import (
    GmaxShearWaveVelocityInput, GmaxShearWaveVelocityOutput,
    EarthPressureRankineInput, EarthPressureRankineOutput,
    ContactWidthInput, ContactWidthOutput,
    HydraulicConductivityUnconfinedInput, HydraulicConductivityUnconfinedOutput
)

SCHEMA_REGISTRY: Dict[str, Tuple[Type[GeoAIBaseModel], Optional[Type[GeoAIBaseModel]]]] = {
    'bulkunitweight': (BulkUnitWeightInput, BulkUnitWeightOutput),
    'voidratio_porosity': (VoidRatioPorosityInput, VoidRatioPorosityOutput),
    'relative_density': (RelativeDensityInput, RelativeDensityOutput),
    'stresses_circle': (StressesCircleInput, StressesCircleOutput),
    'stresses_pointload': (StressesPointloadInput, StressesPointloadOutput),
    'shallow_foundation_capacity_undrained': (ShallowFoundationCapacityUndrainedInput, None),
    'gmax_shearwavevelocity': (GmaxShearWaveVelocityInput, GmaxShearWaveVelocityOutput),
    'earthpressurecoefficients_rankine': (EarthPressureRankineInput, EarthPressureRankineOutput),
    'contactwidth': (ContactWidthInput, ContactWidthOutput),
    'hydraulicconductivity_unconfinedaquifer': (HydraulicConductivityUnconfinedInput, HydraulicConductivityUnconfinedOutput),
}

def get_schema(function_id: str) -> Optional[Tuple[Type[GeoAIBaseModel], Optional[Type[GeoAIBaseModel]]]]:
    if function_id in SCHEMA_REGISTRY:
        return SCHEMA_REGISTRY[function_id]
        
    clean_id = function_id.replace('calculate_', '').lower()
    if clean_id in SCHEMA_REGISTRY:
        return SCHEMA_REGISTRY[clean_id]
        
    # Check tool registry (ensuring definitions are loaded)
    try:
        import core.geoai.tool_definitions
        from core.geoai.tool_registry import tool_registry
        tool = tool_registry.get_tool(function_id) or tool_registry.get_tool(clean_id)
        if tool and tool.input_model:
            return (tool.input_model, tool.output_model)
    except Exception:
        pass
        
    return None

def register_schema(function_id: str, input_cls: Type[GeoAIBaseModel], output_cls: Optional[Type[GeoAIBaseModel]] = None):
    SCHEMA_REGISTRY[function_id] = (input_cls, output_cls)
