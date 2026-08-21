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

SCHEMA_REGISTRY: Dict[str, Tuple[Type[GeoAIBaseModel], Optional[Type[GeoAIBaseModel]]]] = {
    'bulkunitweight': (BulkUnitWeightInput, BulkUnitWeightOutput),
    'voidratio_porosity': (VoidRatioPorosityInput, VoidRatioPorosityOutput),
    'relative_density': (RelativeDensityInput, RelativeDensityOutput),
    'stresses_circle': (StressesCircleInput, StressesCircleOutput),
    'stresses_pointload': (StressesPointloadInput, StressesPointloadOutput),
    'shallow_foundation_capacity_undrained': (ShallowFoundationCapacityUndrainedInput, None),
}

def get_schema(function_id: str) -> Optional[Tuple[Type[GeoAIBaseModel], Optional[Type[GeoAIBaseModel]]]]:
    return SCHEMA_REGISTRY.get(function_id)

def register_schema(function_id: str, input_cls: Type[GeoAIBaseModel], output_cls: Optional[Type[GeoAIBaseModel]] = None):
    SCHEMA_REGISTRY[function_id] = (input_cls, output_cls)
