# Author: Utkarsh Gupta
# License: GPL v3
"""
IS 1892:2021 (second revision) - Subsurface investigation for foundations: location and depth of
investigation (clause 5.6).

* Table 2      disposition of boreholes / trial pits by type of structure.
* 5.6.3.1      investigate at least to the depth where the foundation stress increase is below 10 % of
               the in-situ stress.
* 5.6.3.2      guideline depths below founding level: shallow (non-raft) 2-3 x largest width; raft
               1.0-2.0 x width (width taken as at least 6 m); piles at least max(5 m, 5 diameters) below
               the pile tip; embankments 1.0-2.0 x height; wells 1.5-2.0 x width; and, where rock is met
               earlier, at least 5 m into rock.
The clause says these "may be followed"; they are guidelines, not limits.
"""
import math
from typing import Any, Dict, List, Optional

from core.standards.bis._common import BISInputError, choice, require_positive, round_sig

STANDARD = "IS 1892:2021"
FOUNDATION_TYPES = ("shallow", "raft", "pile", "embankment", "well")
STRUCTURE_TYPES = ("light_residential", "site_0_4_ha", "large_plan_or_multiple_buildings", "tall_building",
                   "linear", "solar_plant")
RAFT_MIN_WIDTH = 6.0
GRID_SPACING = 50.0
ROCK_PENETRATION = 5.0


def investigation_depth_is1892(foundation_type: str, width: Optional[float] = None,
                               pile_diameter: Optional[float] = None, embankment_height: Optional[float] = None,
                               founding_depth: float = 0.0) -> Dict[str, Any]:
    """
    Guideline depth of investigation to IS 1892:2021 cl. 5.6.3.2.

    :param foundation_type: Foundation type. Options: shallow, raft, pile, embankment, well
    :param width: Largest foundation width (shallow), raft width, or well width/diameter [m]
    :param pile_diameter: Pile diameter, for pile foundations [m]
    :param embankment_height: Embankment height, for embankments [m]
    :param founding_depth: Founding level (pile tip / well termination for those types) below ground level [m]
    :returns: Minimum and maximum guideline depth below founding level and below ground level.
    """
    kind = choice(foundation_type, "foundation_type", FOUNDATION_TYPES)
    zf = require_positive(founding_depth, "founding_depth", allow_zero=True)
    warnings: List[str] = []
    if kind == "shallow":
        b = require_positive(width, "width")
        d_min, d_max, rule = 2.0 * b, 3.0 * b, "2 to 3 times the estimated width of the largest foundation"
    elif kind == "raft":
        b = require_positive(width, "width")
        if b < RAFT_MIN_WIDTH:
            warnings.append(f"Raft width taken as {RAFT_MIN_WIDTH:g} m, the minimum IS 1892 uses for planning the investigation.")
            b = RAFT_MIN_WIDTH
        d_min, d_max, rule = 1.0 * b, 2.0 * b, "1.0 to 2.0 times the raft width (width at least 6 m)"
    elif kind == "pile":
        dia = require_positive(pile_diameter, "pile_diameter")
        d_min = max(5.0, 5.0 * dia)
        d_max = None
        rule = "sufficiently below the pile termination level, not less than 5 m or 5 pile diameters, whichever is more"
    elif kind == "embankment":
        h = require_positive(embankment_height, "embankment_height")
        d_min, d_max, rule = 1.0 * h, 2.0 * h, "1.0 to 2.0 times the embankment height"
        warnings.append("Embankment depth is measured from the base of the embankment.")
    else:
        b = require_positive(width, "width")
        d_min, d_max, rule = 1.5 * b, 2.0 * b, "1.5 to 2.0 times the well width/diameter below the well termination level"

    reference = {"pile": "pile termination level", "well": "well termination level",
                 "embankment": "base of the embankment"}.get(kind, "founding level")
    result: Dict[str, Any] = {
        "Foundation type": kind,
        "Rule": rule,
        "Reference level": reference,
        "Minimum depth below reference level [m]": round_sig(d_min),
    }
    if d_max is not None:
        result["Maximum guideline depth below reference level [m]"] = round_sig(d_max)
    if kind != "embankment":
        result["Minimum depth below ground level [m]"] = round_sig(zf + d_min)
        if d_max is not None:
            result["Maximum guideline depth below ground level [m]"] = round_sig(zf + d_max)
    warnings.append(f"If rock is met before this depth, extend the boreholes at least {ROCK_PENETRATION:g} m into rock "
                    "depending on rock characteristics (cl. 5.6.3.2 f).")
    warnings.append("The investigation must also reach the depth where the foundation stress increase is below 10 % "
                    "of the in-situ stress (cl. 5.6.3.1), and deeper where weaker layers lie below that zone.")
    result["Standard"] = f"{STANDARD}, cl. 5.6.3"
    result["warnings"] = warnings
    return result


def borehole_layout_is1892(structure_type: str, plan_length: Optional[float] = None,
                           plan_width: Optional[float] = None, route_length: Optional[float] = None,
                           site_area: Optional[float] = None) -> Dict[str, Any]:
    """
    Disposition of boreholes / trial pits to IS 1892:2021 Table 2.

    :param structure_type: Structure category. Options: light_residential, site_0_4_ha, large_plan_or_multiple_buildings, tall_building, linear, solar_plant
    :param plan_length: Plan length of the built-up area, for large_plan_or_multiple_buildings [m]
    :param plan_width: Plan width of the built-up area, for large_plan_or_multiple_buildings [m]
    :param route_length: Length of a linear structure (road, railway, pipeline, wall, line) [m]
    :param site_area: Site area, for a solar power plant [ha]
    :returns: The Table 2 rule and the corresponding minimum number of boreholes.
    """
    kind = choice(structure_type, "structure_type", STRUCTURE_TYPES)
    warnings: List[str] = ["Boreholes are preferred over trial pits; add boreholes where stratification varies significantly (cl. 5.6.2)."]
    result: Dict[str, Any] = {"Structure type": kind}
    if kind == "light_residential":
        result.update({"Rule": "At least one borehole/trial pit at the centre of the building "
                               "(lightly loaded single/double storeyed residential building)",
                       "Minimum number of boreholes [-]": 1})
    elif kind == "site_0_4_ha":
        result.update({"Rule": "At least one borehole in each corner and one in the centre (site of about 0.4 ha)",
                       "Minimum number of boreholes [-]": 5})
    elif kind == "large_plan_or_multiple_buildings":
        length = require_positive(plan_length, "plan_length")
        width = require_positive(plan_width, "plan_width")
        nx = math.ceil(length / GRID_SPACING) + 1
        ny = math.ceil(width / GRID_SPACING) + 1
        result.update({"Rule": "Boreholes in a grid with points not more than 50 m apart, minimum two, covering the "
                               "built-up area (plan dimension > 50 m, multiple buildings on > 0.4 ha, or buildings up to 50 m high)",
                       "Grid points along length [-]": nx, "Grid points along width [-]": ny,
                       "Minimum number of boreholes [-]": max(2, nx * ny)})
        warnings.append("Grid count assumes a rectangular built-up area covered by a regular grid at 50 m spacing.")
    elif kind == "tall_building":
        result.update({"Rule": "Minimum three boreholes at each building/structure higher than 50 m",
                       "Minimum number of boreholes [-]": 3})
    elif kind == "linear":
        length = require_positive(route_length, "route_length")
        result.update({"Rule": "Boreholes at 50 m to 500 m spacing; closer in erratic strata, wider in uniform strata",
                       "Boreholes at 500 m spacing [-]": math.ceil(length / 500.0) + 1,
                       "Boreholes at 50 m spacing [-]": math.ceil(length / 50.0) + 1})
    else:
        area = require_positive(site_area, "site_area")
        result.update({"Rule": "One borehole for every 2 to 5 hectares, minimum 5 boreholes per site",
                       "Boreholes at 1 per 5 ha [-]": max(5, math.ceil(area / 5.0)),
                       "Boreholes at 1 per 2 ha [-]": max(5, math.ceil(area / 2.0))})
    result["Standard"] = f"{STANDARD}, cl. 5.6.2, Table 2"
    result["warnings"] = warnings
    return result
