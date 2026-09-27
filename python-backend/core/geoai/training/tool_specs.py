# Author: Utkarsh Gupta
# License: GPL v3
"""
Curated phrasing & sampling catalogue for GeoAI dataset generation.

This module deliberately contains ONLY what the registry cannot tell us:
natural-language names engineers use for each parameter, realistic sampling
ranges, and which alternative / wrong units are plausible in practice.

Everything else — parameter names, required vs optional, physical bounds,
canonical units, defaults — is read at generation time from the real tool
``input_model`` held by the GeoAI Tool Registry, and every generated tool call
is executed through the registry before it is kept. Parameter names below are
checked against the live schema; a spec that drifts from its schema raises.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Tuple


@dataclass(frozen=True)
class ParamSpec:
    names: Tuple[str, ...]                 # natural-language names; first is primary
    low: float = 0.0
    high: float = 1.0
    decimals: int = 2
    integer: bool = False
    choices: Tuple[float, ...] = ()
    display_unit: Optional[str] = None     # override of schema unit for display only
    alt_units: Tuple[str, ...] = ()        # convertible units (must exist in core.geoai.units)
    trap_units: Tuple[str, ...] = ()       # dimensionally wrong units (must be rejected)
    fraction: bool = False                 # schema value is a 0-1 fraction; '%' phrasing converts
    include_prob: float = 1.0              # probability of stating an optional parameter
    invalid_value: Optional[float] = None  # physically invalid value for tool-failure cases


@dataclass(frozen=True)
class ToolSpec:
    tool: str
    tasks: Tuple[str, ...]                 # imperative task phrases (lower case)
    questions: Tuple[str, ...]             # question phrases (lower case, no '?')
    domain: str                            # short noun phrase for clarifications
    params: Dict[str, ParamSpec] = field(default_factory=dict)
    constrain: Optional[Callable[[Dict[str, float]], Dict[str, float]]] = None
    result_keys: Tuple[str, ...] = ()      # outputs to quote in final answers (default: numeric)


# ---------------------------------------------------------------------
# Reusable parameter phrasings
# ---------------------------------------------------------------------
_DEPTH = ParamSpec(("depth", "depth below ground level", "test depth"), 1.0, 25.0, 1,
                   alt_units=("ft",), trap_units=("kPa",), invalid_value=-3.0)
_PHI = ParamSpec(("effective friction angle", "friction angle phi'", "angle of shearing resistance"),
                 24.0, 40.0, 0, display_unit="deg", alt_units=("rad",), trap_units=("kPa",))
_GAMMA = ParamSpec(("total unit weight", "bulk unit weight gamma", "soil unit weight"), 16.0, 21.5, 1,
                   alt_units=("pcf",), trap_units=("kPa", "kN"))
_QC = ParamSpec(("cone tip resistance qc", "cone resistance", "qc"), 0.5, 30.0, 1,
                alt_units=("kPa",), trap_units=("kN",), invalid_value=-5.0)
_FS = ParamSpec(("sleeve friction fs", "sleeve friction", "fs"), 5.0, 250.0, 0,
                alt_units=("MPa",), trap_units=("kN",), invalid_value=-20.0)
_POISSON = ParamSpec(("Poisson's ratio", "Poisson ratio nu"), 0.2, 0.45, 2, include_prob=0.35)
_Q = ParamSpec(("applied pressure", "uniform bearing pressure", "surface pressure q"), 50.0, 400.0, 0,
               alt_units=("MPa", "psf", "ksf"), trap_units=("kN", "kN/m3"), invalid_value=-100.0)
_LAYER_H = ParamSpec(("layer thickness", "initial layer height", "thickness of the clay layer"), 1.0, 10.0, 1,
                     alt_units=("ft",))
_DSIGMA = ParamSpec(("effective stress increase", "increase in vertical effective stress", "stress increment"),
                    20.0, 200.0, 0, alt_units=("MPa", "psf"), trap_units=("kN/m3",))
_WATER = ParamSpec(("water content", "natural moisture content w"), 0.15, 0.6, 2, fraction=True)


def _cpt_constrain(v: Dict[str, float]) -> Dict[str, float]:
    # Keep the friction ratio Rf = fs/qc within 0.3 - 6 % (physically plausible CPT data).
    if "qc_mpa" in v and "fs_kpa" in v:
        qc_kpa = v["qc_mpa"] * 1000.0
        rf = v["fs_kpa"] / qc_kpa
        if rf < 0.003 or rf > 0.06:
            v["fs_kpa"] = float(max(1, round(qc_kpa * min(max(rf, 0.004), 0.05))))
    return v


def _pumping_constrain(v: Dict[str, float]) -> Dict[str, float]:
    if v.get("radius_2", 0) <= v.get("radius_1", 0):
        v["radius_2"] = round(v["radius_1"] * 3.0, 1)
    if v.get("piezometric_height_2", 0) <= v.get("piezometric_height_1", 0):
        v["piezometric_height_2"] = round(v["piezometric_height_1"] + 0.8, 2)
    return v


def _rankine_constrain(v: Dict[str, float]) -> Dict[str, float]:
    if "top_angle" in v and v["top_angle"] >= v.get("phi_eff", 30) - 5:
        v["top_angle"] = float(max(0, int(v.get("phi_eff", 30) - 10)))
    return v


def _pipe_constrain(v: Dict[str, float]) -> Dict[str, float]:
    if v.get("penetration", 0) > 0.45 * v.get("diameter", 1):
        v["penetration"] = round(0.3 * v["diameter"], 3)
    return v


def _poncelet_constrain(v: Dict[str, float]) -> Dict[str, float]:
    phi = v.get("phi_eff", 30)
    v["interface_friction_angle"] = float(round(phi * 2.0 / 3.0))
    for k in ("top_angle", "wall_angle"):
        if v.get(k, 0) > phi / 2:
            v[k] = float(int(phi / 3))
    return v


def _nc_constrain(v: Dict[str, float]) -> Dict[str, float]:
    return v


TOOL_SPECS: Tuple[ToolSpec, ...] = (
    # ---------------- canonical GeoAI tools ----------------
    ToolSpec(
        "calculate_bulk_unit_weight",
        ("calculate the bulk unit weight", "compute the bulk and effective unit weight",
         "determine the soil unit weight from phase relations"),
        ("what is the bulk unit weight", "what are the bulk and effective unit weights"),
        "bulk unit weight",
        {
            "saturation": ParamSpec(("degree of saturation", "saturation Sr"), 0.3, 1.0, 2, fraction=True,
                                    invalid_value=1.4),
            "voidratio": ParamSpec(("void ratio", "void ratio e"), 0.4, 1.2, 2, invalid_value=-0.5),
            "specific_gravity": ParamSpec(("specific gravity", "specific gravity of solids Gs"), 2.6, 2.75, 2,
                                          include_prob=0.5),
        },
    ),
    ToolSpec(
        "calculate_void_ratio_from_porosity",
        ("calculate the void ratio from porosity", "convert porosity to void ratio",
         "compute the void ratio"),
        ("what is the void ratio", "what void ratio corresponds to this porosity"),
        "void ratio",
        {"porosity": ParamSpec(("porosity", "porosity n"), 0.25, 0.55, 2, fraction=True, invalid_value=1.2)},
    ),
    ToolSpec(
        "calculate_relative_density",
        ("calculate the relative density", "compute the relative density Dr", "determine the density index"),
        ("what is the relative density",),
        "relative density",
        {
            "void_ratio": ParamSpec(("in-situ void ratio", "current void ratio"), 0.5, 0.8, 2),
            "e_min": ParamSpec(("minimum void ratio", "e_min"), 0.35, 0.48, 2),
            "e_max": ParamSpec(("maximum void ratio", "e_max"), 0.85, 1.05, 2),
        },
    ),
    ToolSpec(
        "calculate_stresses_circular_footing",
        ("calculate the vertical stress increase below the centre of a circular footing",
         "compute the stress increment under a circular foundation",
         "estimate the elastic stress increase beneath the centre of a circular loaded area"),
        ("what is the vertical stress increase under the centre of the circular footing",
         "how much does the vertical stress increase below the circular tank"),
        "stress increase below a circular footing",
        {
            "z": ParamSpec(("depth below the footing", "depth z", "depth below the foundation base"), 0.5, 20.0, 1,
                           alt_units=("ft",), trap_units=("kPa",), invalid_value=-2.0),
            "footing_radius": ParamSpec(("footing radius", "radius of the footing", "foundation radius"), 0.5, 6.0, 1,
                                        alt_units=("ft", "mm"), trap_units=("kPa",), invalid_value=-1.5),
            "imposedstress": _Q,
            "poissonsratio": _POISSON,
        },
    ),
    ToolSpec(
        "calculate_stresses_point_load",
        ("calculate the Boussinesq stresses below a point load",
         "compute the vertical stress increase due to a concentrated surface load",
         "estimate the stress distribution under a point load"),
        ("what is the vertical stress below the point load", "what stress does the column point load induce"),
        "stresses below a point load",
        {
            "pointload": ParamSpec(("point load", "concentrated load Q", "column load"), 50.0, 2000.0, 0,
                                   alt_units=("MN", "kips"), trap_units=("kPa",), invalid_value=-250.0),
            "z": ParamSpec(("depth", "depth z", "depth below the surface"), 0.5, 15.0, 1, alt_units=("ft",),
                           invalid_value=-1.0),
            "r": ParamSpec(("radial distance", "horizontal offset r", "radial offset from the load"), 0.0, 5.0, 1,
                           include_prob=0.7),
            "poissonsratio": _POISSON,
        },
    ),
    ToolSpec(
        "calculate_gmax_from_shear_wave_velocity",
        ("calculate the small-strain shear modulus Gmax", "compute Gmax from the shear wave velocity",
         "estimate the maximum shear modulus from Vs"),
        ("what is Gmax", "what is the small-strain shear modulus"),
        "small-strain shear modulus Gmax",
        {
            "Vs": ParamSpec(("shear wave velocity", "shear wave velocity Vs", "Vs"), 100.0, 600.0, 0,
                            alt_units=("ft/s",), trap_units=("kPa",), invalid_value=-250.0),
            "gamma": _GAMMA,
        },
    ),
    ToolSpec(
        "calculate_earth_pressure_rankine",
        ("calculate the Rankine active and passive earth pressure coefficients",
         "compute Ka and Kp using Rankine theory",
         "estimate the lateral earth pressure coefficients for the retaining wall (Rankine)"),
        ("what are the Rankine Ka and Kp values", "what are the active and passive coefficients"),
        "Rankine earth pressure coefficients",
        {
            "phi_eff": _PHI,
            "top_angle": ParamSpec(("backfill slope angle", "slope of the retained ground"), 0.0, 15.0, 0,
                                   display_unit="deg", include_prob=0.35),
            "wall_angle": ParamSpec(("wall inclination", "wall back angle"), 0.0, 10.0, 0,
                                    display_unit="deg", include_prob=0.25),
        },
        constrain=_rankine_constrain,
    ),
    ToolSpec(
        "calculate_pipeline_contact_width",
        ("calculate the pipeline-seabed contact width", "compute the contact width of the pipe on the seabed",
         "determine the seabed contact width for the pipeline"),
        ("what is the contact width between the pipeline and the seabed",),
        "pipeline contact width",
        {
            "diameter": ParamSpec(("outer pipe diameter", "pipeline diameter D", "outside diameter"), 0.2, 1.2, 2,
                                  alt_units=("mm", "in"), trap_units=("kPa",), invalid_value=-0.5),
            "penetration": ParamSpec(("embedment", "pipe penetration", "penetration depth"), 0.02, 0.3, 3,
                                     alt_units=("mm",), invalid_value=-0.1),
        },
        constrain=_pipe_constrain,
    ),
    ToolSpec(
        "calculate_hydraulic_conductivity_unconfined",
        ("calculate the hydraulic conductivity from the pumping test",
         "estimate the permeability of the unconfined aquifer (Dupuit-Thiem)",
         "back-calculate k from the steady-state pumping test"),
        ("what is the hydraulic conductivity of the aquifer",),
        "hydraulic conductivity from a pumping test",
        {
            "radius_1": ParamSpec(("distance to observation well 1", "r1"), 3.0, 15.0, 1, alt_units=("ft",)),
            "radius_2": ParamSpec(("distance to observation well 2", "r2"), 20.0, 60.0, 1, alt_units=("ft",)),
            "piezometric_height_1": ParamSpec(("piezometric height at well 1", "h1"), 5.0, 9.0, 2),
            "piezometric_height_2": ParamSpec(("piezometric height at well 2", "h2"), 9.1, 12.0, 2),
            "flowrate": ParamSpec(("pumping rate", "discharge Q", "steady pumping rate"), 0.002, 0.03, 4,
                                  display_unit="m3/s", invalid_value=-0.01),
        },
        constrain=_pumping_constrain,
    ),
    ToolSpec(
        "normalize_spt_test",
        ("normalise the SPT blow count", "correct the SPT N value to N60 and (N1)60",
         "normalize the SPT result and estimate Dr and phi'"),
        ("what are N60 and (N1)60 for this SPT", "what is the corrected SPT N value"),
        "SPT normalisation",
        {
            "raw_n": ParamSpec(("SPT N", "field blow count N", "measured SPT N value"), 4, 50, 0, integer=True,
                               invalid_value=-12),
            "depth": _DEPTH,
            "energy_ratio": ParamSpec(("hammer energy ratio", "energy ratio Er"), 0.55, 0.9, 2, fraction=True,
                                      include_prob=0.4),
            "borehole_diameter_mm": ParamSpec(("borehole diameter",), choices=(100.0, 150.0, 200.0), decimals=0,
                                              alt_units=("in",), include_prob=0.3),
            "overburden_kpa": ParamSpec(("effective overburden stress", "vertical effective stress"), 20.0, 300.0, 0,
                                        alt_units=("MPa",), include_prob=0.3),
        },
    ),
    ToolSpec(
        "classify_cpt_soil_behavior",
        ("classify the soil behaviour type from the CPT", "determine the Robertson SBT zone and Ic",
         "interpret the CPT reading to get the soil behaviour type"),
        ("what soil behaviour type does this CPT reading indicate", "what is the Ic and SBT zone"),
        "CPT soil behaviour type",
        {
            "qc_mpa": _QC,
            "fs_kpa": _FS,
            "depth": _DEPTH,
            "u2_kpa": ParamSpec(("pore pressure u2", "measured u2"), 0.0, 400.0, 0, include_prob=0.3),
            "water_table_depth": ParamSpec(("groundwater depth", "water table depth"), 0.0, 5.0, 1,
                                           include_prob=0.3, alt_units=("ft",)),
        },
        constrain=_cpt_constrain,
    ),
    ToolSpec(
        "derive_cpt_parameters",
        ("derive design parameters from the CPT", "estimate su, phi', Dr and Gmax from the CPT reading",
         "derive geotechnical parameters from the cone data"),
        ("what soil parameters can be derived from this CPT reading", "what are su and Gmax from the CPT"),
        "CPT parameter derivation",
        {
            "qc_mpa": _QC,
            "fs_kpa": _FS,
            "depth": _DEPTH,
            "Nkt": ParamSpec(("cone factor Nkt", "Nkt"), 12.0, 20.0, 0, include_prob=0.4),
        },
        constrain=_cpt_constrain,
    ),
    # ---------------- auto-registered Groundhog tools ----------------
    ToolSpec(
        "nq_frictionangle_sand",
        ("calculate the bearing capacity factor Nq", "compute Nq for the sand"),
        ("what is the bearing capacity factor Nq",),
        "bearing capacity factor Nq",
        {"friction_angle": ParamSpec(("friction angle", "effective friction angle"), 25.0, 42.0, 0,
                                     display_unit="deg")},
    ),
    ToolSpec(
        "ngamma_frictionangle_vesic",
        ("calculate the Vesic bearing capacity factor Ngamma", "compute Ngamma using Vesic"),
        ("what is Ngamma according to Vesic",),
        "bearing capacity factor Ngamma (Vesic)",
        {"friction_angle": ParamSpec(("friction angle", "effective friction angle"), 25.0, 42.0, 0,
                                     display_unit="deg")},
    ),
    ToolSpec(
        "k0_frictionangle_mesri",
        ("estimate the at-rest earth pressure coefficient K0 (Mesri)", "calculate K0 from the friction angle"),
        ("what is the at-rest coefficient K0",),
        "at-rest earth pressure coefficient K0",
        {
            "phi_cs": ParamSpec(("critical state friction angle", "constant-volume friction angle"), 25.0, 36.0, 0,
                                display_unit="deg"),
            "ocr": ParamSpec(("OCR", "overconsolidation ratio"), 1.0, 4.0, 1, include_prob=0.5),
        },
    ),
    ToolSpec(
        "stresses_stripload",
        ("calculate the stresses below a strip load", "compute the vertical stress increase under a strip footing"),
        ("what is the stress increase below the strip load",),
        "stresses below a strip load",
        {
            "z": ParamSpec(("depth", "depth below the strip"), 0.5, 15.0, 1),
            "x": ParamSpec(("horizontal offset from the strip centre", "offset x"), 0.0, 4.0, 1),
            "width": ParamSpec(("strip width", "footing width B"), 1.0, 6.0, 1),
            "imposedstress": ParamSpec(("applied pressure", "strip pressure q"), 50.0, 300.0, 0),
        },
    ),
    ToolSpec(
        "consolidationsettlement_mv",
        ("calculate the consolidation settlement using mv", "estimate the 1D settlement from the volume compressibility"),
        ("what is the consolidation settlement of the layer",),
        "consolidation settlement (mv method)",
        {
            "initial_height": _LAYER_H,
            "effective_stress_increase": _DSIGMA,
            "compressibility": ParamSpec(("coefficient of volume compressibility mv", "mv"), 0.0001, 0.001, 5,
                                         display_unit="m2/kN"),
        },
    ),
    ToolSpec(
        "primaryconsolidationsettlement_nc",
        ("calculate the primary consolidation settlement of the normally consolidated clay",
         "estimate the NC clay settlement using the compression index"),
        ("how much will the normally consolidated clay settle",),
        "primary consolidation settlement (NC clay)",
        {
            "initial_height": _LAYER_H,
            "initial_voidratio": ParamSpec(("initial void ratio", "e0"), 0.8, 2.0, 2),
            "initial_effective_stress": ParamSpec(("initial vertical effective stress", "sigma'v0"), 30.0, 150.0, 0),
            "effective_stress_increase": _DSIGMA,
            "compression_index": ParamSpec(("compression index Cc", "Cc"), 0.15, 0.8, 2),
        },
        constrain=_nc_constrain,
    ),
    ToolSpec(
        "permeability_d10_hazen",
        ("estimate the permeability with Hazen's formula", "calculate k from D10 using Hazen"),
        ("what is the Hazen permeability",),
        "Hazen permeability",
        {"grain_size": ParamSpec(("effective grain size D10", "D10"), 0.06, 1.0, 2)},
    ),
    ToolSpec(
        "earthpressurecoefficients_poncelet",
        ("calculate the Coulomb/Poncelet earth pressure coefficients",
         "compute Ka and Kp with wall friction (Poncelet)"),
        ("what are Ka and Kp including wall friction",),
        "Poncelet earth pressure coefficients",
        {
            "phi_eff": ParamSpec(("effective friction angle", "friction angle phi'"), 26.0, 40.0, 0, display_unit="deg"),
            "interface_friction_angle": ParamSpec(("wall friction angle delta", "interface friction angle"), 15.0, 26.0, 0,
                                                  display_unit="deg"),
            "wall_angle": ParamSpec(("wall inclination",), 0.0, 10.0, 0, display_unit="deg"),
            "top_angle": ParamSpec(("backfill slope angle",), 0.0, 10.0, 0, display_unit="deg"),
        },
        constrain=_poncelet_constrain,
    ),
    ToolSpec(
        "dryunitweight_watercontent",
        ("calculate the dry unit weight", "compute the dry unit weight from the water content"),
        ("what is the dry unit weight",),
        "dry unit weight",
        {"watercontent": ParamSpec(("water content", "moisture content w"), 0.08, 0.45, 2, fraction=True),
         "bulkunitweight": ParamSpec(("bulk unit weight", "total unit weight"), 16.0, 21.5, 1)},
    ),
    ToolSpec(
        "overburdencorrection_spt_liaowhitman",
        ("apply the Liao & Whitman overburden correction to the SPT N", "compute N1 with the Liao-Whitman correction"),
        ("what is the overburden-corrected SPT N1",),
        "SPT overburden correction (Liao & Whitman)",
        {"N": ParamSpec(("SPT N", "blow count"), 5, 50, 0, integer=True),
         "sigma_vo_eff": ParamSpec(("vertical effective stress", "effective overburden stress"), 20.0, 300.0, 0)},
    ),
    ToolSpec(
        "porosity_voidratio",
        ("calculate the porosity from the void ratio", "convert void ratio to porosity"),
        ("what is the porosity",),
        "porosity",
        {"voidratio": ParamSpec(("void ratio", "void ratio e"), 0.4, 1.4, 2)},
    ),
    ToolSpec(
        "compressionindex_watercontent_koppula",
        ("estimate the compression index from the water content (Koppula)", "calculate Cc from the natural water content"),
        ("what is the compression index Cc",),
        "compression index (Koppula)",
        {"water_content": _WATER},
    ),
    ToolSpec(
        "unitweight_watercontent_saturated",
        ("calculate the saturated unit weight from the water content", "estimate the unit weight of the saturated soil"),
        ("what is the saturated unit weight",),
        "saturated unit weight",
        {"water_content": _WATER,
         "specific_gravity": ParamSpec(("specific gravity", "Gs"), 2.6, 2.75, 2, include_prob=0.4)},
    ),
)


def spec_by_tool() -> Dict[str, ToolSpec]:
    return {s.tool: s for s in TOOL_SPECS}


# ---------------------------------------------------------------------
# Non-tool categories
# ---------------------------------------------------------------------

# (prompt, clarify keyword groups)
AMBIGUOUS_PROMPTS = (
    ("Calculate the pile capacity.", [["diameter", "geometry", "length", "pile type"], ["method", "cpt", "api", "lcpc", "soil"]]),
    ("What is the settlement of the foundation?", [["load", "pressure"], ["dimension", "width", "size", "geometry"], ["compressib", "modulus", "cc", "mv", "soil"]]),
    ("Work out the bearing capacity.", [["width", "dimension", "geometry", "size"], ["friction angle", "phi", "su", "shear strength", "cohesion"]]),
    ("Give me the earth pressure.", [["friction angle", "phi"], ["active", "passive", "at-rest", "wall"]]),
    ("Calculate Gmax.", [["shear wave velocity", "vs", "cpt"], ["unit weight", "density", "gamma", "method"]]),
    ("Classify this CPT.", [["qc", "cone resistance", "tip resistance"], ["fs", "sleeve friction"], ["depth"]]),
    ("Run the stress calculation for my footing.", [["load", "pressure"], ["shape", "circular", "strip", "rectangular", "geometry", "dimension"], ["depth"]]),
    ("What's the stiffness of the soil?", [["which", "stiffness", "modulus", "gmax", "young"], ["data", "cpt", "vs", "test"]]),
    ("Check the retaining wall.", [["height", "geometry", "wall"], ["friction angle", "phi", "soil"], ["check", "sliding", "overturning", "what"]]),
    ("Calculate the permeability.", [["pumping", "grain size", "d10", "test", "data"]]),
    ("Normalise the SPT.", [["n value", "blow count", "spt n", " n "], ["depth"]]),
    ("How much will the clay consolidate?", [["thickness", "height", "layer"], ["stress", "load"], ["cc", "compression index", "mv", "compressib"]]),
    ("Calculate the factor of safety.", [["which", "slope", "foundation", "wall", "what"], ["load", "geometry", "parameter"]]),
    ("Can you do the liquefaction check?", [["earthquake", "magnitude", "pga", "acceleration", "seismic"], ["cpt", "spt", "data"]]),
    ("Estimate the undrained shear strength.", [["cpt", "qc", "spt", "test", "data"], ["nkt", "method", "correlation", "depth"]]),
    ("Work out the friction angle.", [["cpt", "spt", "test", "data", "lab"], ["depth", "method", "correlation"]]),
    ("Calculate the unit weight.", [["void ratio", "water content", "saturation", "specific gravity", "data", "density"]]),
    ("Design the foundation for me.", [["load", "structure"], ["soil", "ground", "parameter"], ["type", "shallow", "pile", "foundation"]]),
    ("What is K0?", [["friction angle", "phi"], ["ocr", "overconsolidation", "method"]]),
    ("Compute the contact width.", [["diameter"], ["embedment", "penetration"]]),
    ("Get me the vertical stress.", [["load", "pressure"], ["depth"], ["geometry", "point", "strip", "circular", "footing", "shape"]]),
    ("Calculate the void ratio.", [["porosity", "water content", "density", "unit weight", "data"]]),
    ("Evaluate the pile group settlement.", [["pile", "number", "layout", "spacing", "geometry"], ["load"], ["soil", "stiffness", "modulus"]]),
    ("Calculate X using the current project.", [["which", "what", "calculation", "specify", "quantity"]]),
    ("Run the analysis for borehole BH-01.", [["which", "what", "analysis", "calculation"]]),
    ("Estimate the capacity.", [["which", "bearing", "pile", "capacity", "what"], ["geometry", "dimension", "load", "soil"]]),
)
AMBIGUOUS_WRAPPERS = ("{p}", "Quick question: {p}", "{p} Thanks.", "For the project we discussed: {p}")

# (topic phrase, search query keywords)
RESEARCH_TOPICS = (
    ("CPT-based axial pile capacity methods (LCPC versus Koppejan)", "CPT pile capacity LCPC Koppejan"),
    ("the Robertson 1990 and 2009 soil behaviour type charts", "Robertson soil behaviour type chart"),
    ("selecting the cone factor Nkt for undrained shear strength", "Nkt cone factor undrained shear strength"),
    ("CPT-based liquefaction triggering procedures", "CPT liquefaction triggering"),
    ("SPT energy corrections and N60", "SPT energy correction N60"),
    ("small-strain stiffness Gmax correlations with CPT", "Gmax CPT correlation small-strain stiffness"),
    ("Eurocode 7 partial factors for design approach 1", "Eurocode 7 partial factors design approach"),
    ("negative skin friction on piles", "negative skin friction piles"),
    ("consolidation settlement of soft clay under embankments", "consolidation settlement soft clay embankment"),
    ("Rankine versus Coulomb earth pressure theory", "Rankine Coulomb earth pressure"),
    ("pipeline embedment in soft clay", "pipeline embedment soft clay"),
    ("Hazen's formula for permeability of sands", "Hazen permeability D10 sand"),
    ("the Dupuit-Thiem pumping test interpretation", "Dupuit Thiem pumping test"),
    ("relative density correlations from CPT in sands", "relative density CPT sand correlation"),
    ("shallow foundation bearing capacity factors", "bearing capacity factors Nq Ngamma"),
    ("K0 in overconsolidated clays", "K0 overconsolidated clay"),
    ("cyclic degradation of clay under offshore loading", "cyclic degradation clay offshore"),
    ("stress distribution below footings (Boussinesq)", "Boussinesq stress distribution footing"),
    ("sample disturbance effects on void ratio", "sample disturbance void ratio"),
    ("groundwater lowering effects on settlement", "groundwater lowering settlement"),
    ("API RP 2GEO axial pile design in sand", "API RP 2GEO pile sand"),
    ("undrained bearing capacity of skirted foundations", "undrained bearing capacity skirted foundation"),
    ("secondary compression of organic clays", "secondary compression organic clay"),
    ("interpretation of CPT dissipation tests", "CPT dissipation test interpretation"),
    ("shear wave velocity measurement methods", "shear wave velocity measurement"),
    ("friction angle correlations from SPT", "friction angle SPT correlation"),
    ("unit weight estimation from CPT", "unit weight CPT estimation"),
    ("plasticity index correlations for friction angle", "plasticity index friction angle correlation"),
)
RESEARCH_FRAMES = (
    "Compare {topic}.",
    "What guidance do we have on {topic}?",
    "Find references on {topic} in our documents.",
    "Search the project library for {topic}.",
    "What does the literature say about {topic}?",
    "Summarise the available evidence on {topic}.",
)

# CPT vs borehole textual conflicts: (cpt_description, borehole_description)
SOIL_CONFLICTS = (
    ("clean sand (Ic = 1.6)", "soft silty clay"),
    ("dense sand (Ic = 1.5)", "firm clay"),
    ("soft clay (Ic = 3.2)", "medium dense sand"),
    ("silty sand (Ic = 2.2)", "stiff clay with gravel"),
    ("organic clay (Ic = 3.4)", "dense gravel"),
    ("sand to silty sand (Ic = 1.9)", "peat"),
)
CONFLICT_SOURCES = (
    ("the lab report", "the CPT correlation"),
    ("borehole BH-01", "borehole BH-03"),
    ("the 2019 site investigation", "the 2024 site investigation"),
    ("the geotechnical baseline report", "the design memo"),
)
MISSING_DATA_IDS = ("CPT-07", "CPT-12", "BH-09", "SCPT-04", "BH-15", "CPT-21")
