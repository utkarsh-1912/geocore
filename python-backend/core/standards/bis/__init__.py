# Author: Utkarsh Gupta
# License: GPL v3
"""
Indian Standard (Bureau of Indian Standards) geotechnical calculations.

Deterministic implementations of clauses of IS 6403, IS 1498, IS 2131, IS 1892, IS 1904, IS 2950 (Part 1)
and IS 2720 that Groundhog does not cover. Every function takes SI inputs, cites the clause it applies,
raises ``BISInputError`` for inputs outside the clause (never patches them) and returns a flat
``{"name [unit]": value}`` dict like Groundhog, with clause notes in ``warnings``.

``BIS_FUNCTIONS`` is added to ``core.registry.Registry.function_map`` (desktop forms) and from there to
the GeoAI Tool Registry, with the curated input schemas in ``core.geoai.schemas.bis``.
"""
from core.standards.bis._common import BISInputError
from core.standards.bis.is1498 import classify_soil_is1498
from core.standards.bis.is1892 import borehole_layout_is1892, investigation_depth_is1892
from core.standards.bis.is1904 import permissible_settlement_is1904, stability_check_is1904
from core.standards.bis.is2131 import spt_correction_is2131
from core.standards.bis.is2720 import (consistency_indices_is2720, flow_index_is2720, liquid_limit_one_point_is2720,
                                       permeability_constant_head_is2720, permeability_falling_head_is2720,
                                       specific_gravity_is2720)
from core.standards.bis.is2950 import raft_rigidity_is2950
from core.standards.bis.is6403 import bearing_capacity_is6403

BIS_FUNCTIONS = {f.__name__: f for f in (
    bearing_capacity_is6403,
    classify_soil_is1498,
    spt_correction_is2131,
    investigation_depth_is1892,
    borehole_layout_is1892,
    permissible_settlement_is1904,
    stability_check_is1904,
    raft_rigidity_is2950,
    specific_gravity_is2720,
    flow_index_is2720,
    liquid_limit_one_point_is2720,
    consistency_indices_is2720,
    permeability_constant_head_is2720,
    permeability_falling_head_is2720,
)}

__all__ = ["BISInputError", "BIS_FUNCTIONS", *BIS_FUNCTIONS]
