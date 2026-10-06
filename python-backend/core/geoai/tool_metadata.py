# Author: Utkarsh Gupta
# License: GPL v3
"""
Geotechnical Tool Metadata Catalog.
Provides authoritative references, standards, assumptions, and output unit mappings
for GeoCore & Groundhog calculation routines to guarantee complete provenance.
"""

from typing import Dict, Any, List, Optional


TOOL_METADATA: Dict[str, Dict[str, Any]] = {
    # 1. Earth Pressure & Excavations
    "calculate_earth_pressure_rankine": {
        "method": "Rankine (1857) Lateral Earth Pressure Theory",
        "standard": "EN 1997-1:2004 (Eurocode 7 §9.5)",
        "assumptions": [
            "Cohesionless, isotropic, homogenous soil backfill",
            "Planar failure surface extending behind wall",
            "Frictionless interface between wall and soil (delta = 0)",
            "Active and passive states fully mobilized"
        ],
        "output_units": {
            "Ka": "-",
            "Kp": "-"
        }
    },
    "earthpressurecoefficients_rankine": {
        "method": "Rankine (1857) Lateral Earth Pressure Theory",
        "standard": "EN 1997-1:2004 (Eurocode 7 §9.5)",
        "assumptions": [
            "Cohesionless, isotropic backfill",
            "Planar slip surface, frictionless wall interface"
        ],
        "output_units": {"Ka": "-", "Kp": "-"}
    },
    "earthpressurecoefficients_coulomb": {
        "method": "Coulomb (1776) Wedge Equilibrium Method",
        "standard": "EN 1997-1:2004 (Eurocode 7 §9.5)",
        "assumptions": [
            "Planar failure wedge behind wall",
            "Wall-soil interface friction angle delta explicitly considered"
        ],
        "output_units": {"Ka": "-", "Kp": "-"}
    },
    "earthpressurecoefficients_caquotkerisel": {
        "method": "Caquot & Kérisel (1948) Logarithmic Spiral Method",
        "standard": "Eurocode 7 Annex C / French Standard NF P 94-282",
        "assumptions": [
            "Log-spiral failure mechanism for passive resistance",
            "Prevents unconservative passive resistance overestimation from planar wedges"
        ],
        "output_units": {"Ka": "-", "Kp": "-"}
    },

    # 2. Phase Relations & Classification
    "calculate_bulk_unit_weight": {
        "method": "Fundamental Soil Mechanics Phase Relations",
        "standard": "BS 1377-2 / ASTM D7263 / ISO 17892-2",
        "assumptions": [
            "Three-phase soil system (solid, water, air)",
            "Full or partial saturation governed by Sr"
        ],
        "output_units": {
            "gamma_bulk": "kN/m3",
            "gamma_dry": "kN/m3",
            "void_ratio": "-"
        }
    },
    "calculate_void_ratio_from_porosity": {
        "method": "Fundamental Phase Relations (e = n / (1 - n))",
        "standard": "ASTM D7263 / ISO 17892-2",
        "assumptions": ["Valid for 0 < n < 1.0"],
        "output_units": {"voidratio": "-"}
    },
    "calculate_relative_density": {
        "method": "Relative Density Definition (Dr = (e_max - e) / (e_max - e_min))",
        "standard": "ASTM D4253 & D4254 / ISO 17892-4",
        "assumptions": [
            "Cohesionless granular soil",
            "e_min <= e <= e_max"
        ],
        "output_units": {"Dr": "-"}
    },

    # 3. Shallow Foundations
    "calculate_stresses_circular_footing": {
        "method": "Boussinesq (1885) & Love (1929) Elastic Integration",
        "standard": "Poulos & Davis (1974) Elastic Solutions for Soil & Rock Mechanics",
        "assumptions": [
            "Homogeneous, isotropic, linear elastic semi-infinite half-space",
            "Uniform vertical stress q over flexible circular area of radius R"
        ],
        "output_units": {
            "sigma_z": "kPa",
            "sigma_r": "kPa",
            "sigma_theta": "kPa"
        }
    },
    "calculate_stresses_point_load": {
        "method": "Boussinesq (1885) 3D Point Load Closed-Form Solution",
        "standard": "Poulos & Davis (1974)",
        "assumptions": [
            "Semi-infinite, homogeneous, isotropic, linear elastic medium",
            "Concentrated normal vertical surface point load Q"
        ],
        "output_units": {
            "sigma_z": "kPa",
            "sigma_r": "kPa",
            "tau_rz": "kPa"
        }
    },
    "shallow_foundation_capacity_undrained": {
        "method": "V-H-M Bearing Capacity Interaction Envelopes (Undrained)",
        "standard": "EN 1997-1:2004 / ISO 19901-4 / API RP 2GEO",
        "assumptions": [
            "Rigid foundation on cohesive soil layer under total stress (short-term)",
            "Uniform or linearly increasing undrained shear strength profile"
        ],
        "output_units": {
            "V_ult": "kN",
            "H_ult": "kN",
            "bearing_capacity": "kPa",
            "factor_of_safety": "-"
        }
    },
    "shallow_foundation_capacity_drained": {
        "method": "Vesic (1975) & Eurocode 7 Drained Bearing Capacity",
        "standard": "EN 1997-1:2004 §6.5 / API RP 2GEO",
        "assumptions": [
            "Effective stress failure mechanism with inclination and shape factors",
            "Drained response governed by c' and phi'"
        ],
        "output_units": {
            "V_ult": "kN",
            "q_ult": "kPa",
            "factor_of_safety": "-"
        }
    },

    # 4. Deep Foundations
    "lcpc_calculation": {
        "method": "Bustamante & Gianeselli (1982) LCPC CPT Method",
        "standard": "French Standard NF P 94-262 / FHWA-GEC-010",
        "assumptions": [
            "Unit skin friction qs and unit base resistance qb derived from qc",
            "Equivalent cone resistance qc_eq calculated within influence zone [-1.5D, +1.5D]"
        ],
        "output_units": {
            "Q_total": "kN",
            "Q_base": "kN",
            "Q_shaft": "kN"
        }
    },
    "koppejan_calculation": {
        "method": "Koppejan CPT-based Base and Shaft Resistance",
        "standard": "Dutch Standard NEN 6743 / CUR 143",
        "assumptions": [
            "Base resistance calculated from averaged qc above and below pile toe",
            "Construction depth window filtered for non-monotonic records"
        ],
        "output_units": {
            "R_b": "kN",
            "R_s": "kN",
            "R_c": "kN"
        }
    },
    "debeer_calculation": {
        "method": "De Beer (1971) Scale Effect & Boundary Integration Method",
        "standard": "Belgian National Standards / Eurocode 7 Design Guidance",
        "assumptions": [
            "Accounts for penetration scale effect between CPT cone and large diameter pile"
        ],
        "output_units": {
            "R_base": "kN",
            "R_shaft": "kN",
            "R_total": "kN"
        }
    },
    "axcap_calculation": {
        "method": "Axial Capacity Depth Integration Profile",
        "standard": "API RP 2GEO / ISO 19901-4",
        "assumptions": [
            "Integrated unit skin friction along embedded shaft + end bearing at tip"
        ],
        "output_units": {
            "compression_capacity": "kN",
            "tension_capacity": "kN"
        }
    },

    # 5. Dynamics & In-Situ Correlations
    "calculate_gmax_from_shear_wave_velocity": {
        "method": "Small-strain shear modulus from Elastic Wave theory (Gmax = rho * Vs^2, rho = gamma / g)",
        "standard": "Robertson & Cabal (2015), Guide to Cone Penetration Testing, 6th ed. (Groundhog reference)",
        "assumptions": [
            "Homogeneous isotropic elastic continuum at small shear strain (< 1e-4 %)",
            "Shear wave propagation through solid soil matrix"
        ],
        "output_units": {
            "Gmax": "kPa",
            "rho": "kg/m3"
        }
    },
    "calculate_pipeline_contact_width": {
        "method": "Subsea Pipeline Circular Cylinder Embedment Theory",
        "standard": "DNV-RP-F114 (Pipe-Soil Interaction for Submarine Pipelines)",
        "assumptions": [
            "Rigid circular cylinder embedded into cohesive/frictional seabed",
            "Contact width B = 2 * sqrt(D * z_p - z_p^2)"
        ],
        "output_units": {
            "contact_width": "m"
        }
    },
    "calculate_hydraulic_conductivity_unconfined": {
        "method": "Dupuit-Thiem Well Equilibrium Formula",
        "standard": "ASTM D4050 / BS 5930",
        "assumptions": [
            "Steady radial laminar flow to fully penetrating well",
            "Horizontal unconfined water table under gravity drainage"
        ],
        "output_units": {
            "k": "m/s"
        }
    },
    "normalize_spt_test": {
        "method": "Skempton (1986) & Liao-Whitman (1986) Energy & Overburden Normalization",
        "standard": "ASTM D1586 / BS EN ISO 22476-3 / Eurocode 7 Part 2",
        "assumptions": [
            "Energy correction Ce = Er / 0.60 to standard 60% energy baseline",
            "Effective overburden normalization Cn = sqrt(Pa / sigma_v0') capped at 2.0",
            "Empirical friction angle correlation (Wolff 1989 / Peck et al. 1974)"
        ],
        "output_units": {
            "N60": "-",
            "N1_60": "-",
            "Dr_pct": "%",
            "phi_eff_deg": "deg"
        }
    },
    "classify_cpt_soil_behavior": {
        "method": "Robertson (1990 / 2009) SBTn Soil Classification Chart",
        "standard": "ASTM D5778 / ISO 22476-1 / ISSMGE TC-16",
        "assumptions": [
            "Normalized cone resistance Qt and normalized friction ratio Fr",
            "Soil Behavior Type Index Ic determines 9 distinct soil zones",
            "Pore pressure correction qt = qc + u2*(1-a) applied"
        ],
        "output_units": {
            "Qt": "-",
            "Fr_pct": "%",
            "Bq": "-",
            "Ic": "-",
            "sbt_zone": "-"
        }
    },
    "derive_cpt_parameters": {
        "method": "Robertson (2009) & Kulhawy-Mayne (1990) CPT Parameter Correlations",
        "standard": "ISSMGE TC-16 CPT Interpretation Guidelines",
        "assumptions": [
            "Undrained shear strength su = (qt - sigma_v0) / Nkt for fine-grained soils (Ic > 2.6)",
            "Effective friction angle phi' from Robertson & Campanella (1983) for sands (Ic <= 2.6)",
            "Small-strain shear modulus Gmax from Robertson (2009) SBT formulation"
        ],
        "output_units": {
            "su_kpa": "kPa",
            "phi_eff_deg": "deg",
            "Dr_pct": "%",
            "Gmax_kpa": "kPa"
        }
    },
    "search_local_documents": {
        "method": "SQLite FTS5 BM25 Full-Text Information Retrieval",
        "standard": "Local Desktop Offline RAG Engine",
        "assumptions": [
            "Queries indexed local markdown, text, report, and standard passages",
            "Exact keyword matching with Porter stemming tokenization"
        ],
        "output_units": {"total_found": "-"}
    },
    "get_function_documentation": {
        "method": "Lookup in the shipped Groundhog docstrings (GeoCore docs adaptor)",
        "standard": "Groundhog documentation, GPL-3.0-or-later (Bruno Stuyts)",
        "assumptions": [
            "Returns documentation only; no calculation is performed",
            "Units, ranges and references are quoted from the docstrings of the shipped Groundhog version"
        ],
        "output_units": {}
    },
    "index_document_text": {
        "method": "Semantic Text Chunking & FTS5 Indexing",
        "standard": "Local Desktop Offline RAG Engine",
        "assumptions": ["Splits content into coherent paragraphs and section headings"],
        "output_units": {"indexed_chunks": "-"}
    },

    # 6. Shallow foundation design workflows (core.geoai.tools_shallow)
    "calculate_shallow_foundation_capacity": {
        "method": "API RP 2GEO (2011) shallow foundation bearing capacity (Groundhog ShallowFoundationCapacityDrained / Undrained)",
        "standard": "API RP 2GEO (2011) Geotechnical and Foundation Design Considerations; Groundhog (Stuyts) implementation",
        "assumptions": [
            "Ultimate bearing pressure and vertical capacity of a footing or pad; no factor of safety applied",
            "Drained: cohesionless soil (no c' term), Nq = exp(pi tan phi') tan^2(45 + phi'/2), Ngamma = 1.5 (Nq - 1) tan phi'",
            "Undrained: Nc = 5.14 with shape, depth and load inclination factors; constant or linearly increasing su",
            "Eccentric load handled with the effective area A' = B' x L'",
            "Groundwater lowers the effective stress at base level and the unit weight below the base"
        ],
        "output_units": {
            "q_ult_kpa": "kPa",
            "Q_ult_kn": "kN",
            "Q_ult_kn_per_m": "kN/m",
            "effective_area_m2": "m2"
        }
    },
    "calculate_foundation_settlement": {
        "method": "One-dimensional primary consolidation settlement (Cc/Cr/e0 or mv) with Boussinesq stress increase below the footing centre (Groundhog functions)",
        "standard": "Budhu (2011) Soil Mechanics and Foundations; Groundhog SettlementCalculation procedure",
        "assumptions": [
            "Clay compresses one-dimensionally; consolidation settlement of soft or stiff clay below the footing",
            "Stress increase from elastic half-space solutions below the centre of a flexible footing",
            "Net pressure (q minus overburden at base level) by default",
            "Immediate (elastic) and secondary compression settlement not included"
        ],
        "output_units": {
            "settlement_mm": "mm",
            "applied_pressure_kpa": "kPa",
            "net_pressure_kpa": "kPa"
        }
    },

    # 7. Project CPT retrieval and CPT-based pile capacity (core.geoai.tools_cpt_piles)
    "list_project_cpts": {
        "method": "Deterministic read of CPT soundings from the GeoCore workspace (SoilProfile CPT tables, PCPTProcessing, AGS SCPT)",
        "standard": "GeoCore project data; units taken from column headers only",
        "assumptions": [
            "CPT channels normalised to depth [m], qc [MPa], fs [kPa], u2 [kPa] by deterministic unit conversion",
            "Columns without a recognised unit are not used and are reported"
        ],
        "output_units": {"count": "-", "depth_range_m": "m", "groundwater_depth_m": "m"}
    },
    "get_cpt_summary": {
        "method": "Robertson (2009) Ic / soil behaviour type intervals (core.geoai.cpt.CPTSounding) with deterministic merging of thin intervals",
        "standard": "Robertson (1990, 2009) CPT soil behaviour type; ISO 22476-1 CPT channels",
        "assumptions": [
            "Stress normalisation with unit weight 18.5 kN/m3; groundwater from the CPT source, else at ground level",
            "Intervals thinner than min_layer_thickness_m are merged into the thicker neighbour",
            "SBT layering is an interpretation of the CPT, not a borehole log"
        ],
        "output_units": {"depth_range_m": "m", "median_spacing_m": "m", "groundwater_depth_m": "m",
                         "qc_mpa": "MPa", "fs_kpa": "kPa", "u2_kpa": "kPa", "ic_mean": "-"}
    },
    "calculate_pile_capacity_from_cpt": {
        "method": "CPT-based axial pile capacity: LCPC (Bustamante & Gianeselli 1982), Koppejan, or De Beer (Belgian practice) via Groundhog LCPCAxcapCalculation / KoppejanCalculation / DeBeerCalculation",
        "standard": "Bustamante & Gianeselli (1982) ESOPT-II; Koppejan pile-type factors (Groundhog documentation); De Beer / Huybrechts et al. (2016) Belgian practice",
        "assumptions": [
            "Single circular pile in axial compression; ultimate (unfactored) shaft, base and total resistance",
            "Pile-type factors: LCPC categories I/II and IA/IIA/IIB; Koppejan alpha_p/alpha_s table; De Beer alpha_s/alpha_b user-specified",
            "Soil layering from explicit soil_layers or from CPT Robertson SBT intervals",
            "Resistance/partial factors, group effects, negative skin friction and settlement are not included"
        ],
        "output_units": {
            "ultimate_shaft_resistance_kn": "kN",
            "ultimate_base_resistance_kn": "kN",
            "ultimate_total_resistance_kn": "kN",
            "diameter_m": "m",
            "tip_depth_m": "m",
            "base_area_m2": "m2",
            "qb_at_tip_mpa": "MPa",
            "shaft_resistance_kn": "kN"
        }
    },

    # 8. Indian Standard (BIS) calculations implemented in GeoCore (core.standards.bis)
    "bearing_capacity_is6403": {
        "method": "IS 6403 net ultimate bearing capacity: qd = c Nc sc dc ic + q (Nq - 1) sq dq iq + 0.5 B gamma Ngamma sgamma dgamma igamma W'",
        "standard": "IS 6403:1981 (Reaffirmed) cl. 5.1-5.3, Tables 1-3 (GeoCore implementation; Nq, Ngamma from Groundhog for phi 20-50 deg)",
        "assumptions": [
            "Shear criterion only; no factor of safety unless supplied, settlement not checked",
            "Local shear with c' = 2c/3 and phi' = atan(0.67 tan phi); Table 3 interpolation on relative density when selected",
            "Depth factors only when requested (properly compacted backfill)",
            "W' interpolated between 0.5 (water table at base) and 1 (at Df + B); q from total/submerged unit weights"
        ],
        "output_units": {"Net ultimate bearing capacity qnu [kPa]": "kPa", "Net safe bearing capacity qns [kPa]": "kPa"}
    },
    "classify_soil_is1498": {
        "method": "Indian Standard Soil Classification System, laboratory method (gradation, Atterberg limits, A-line Ip = 0.73 (wL - 20))",
        "standard": "IS 1498:1970 (Reaffirmed) cl. 3.5, Table 3, Fig. 1 (GeoCore implementation)",
        "assumptions": [
            "Compressibility L / I / H at wL < 35, 35-50, > 50",
            "Borderline-of-borderline cases favour the non-plastic symbol (cl. 3.5.2)",
            "Organic fines identified only when the oven-dried liquid limit is given; Pt identified visually by the user"
        ],
        "output_units": {}
    },
    "spt_correction_is2131": {
        "method": "IS 2131 overburden correction CN = 0.77 log10(20 / sigma'v [kgf/cm2]) <= 2 (Fig. 1) and dilatancy correction N'' = 15 + (N' - 15)/2",
        "standard": "IS 2131:1981 (Reaffirmed) cl. 3.6 (GeoCore implementation); optional N60 = N ER/60 per ISO 22476-3",
        "assumptions": [
            "Cohesionless soil; Fig. 1 represented by the Peck, Hanson & Thornburn (1974) curve it plots",
            "Energy normalisation only when the measured energy ratio is supplied (not part of IS 2131:1981)"
        ],
        "output_units": {"Corrected N [-]": "-"}
    },
    "investigation_depth_is1892": {
        "method": "IS 1892 guideline depth of investigation by foundation type",
        "standard": "IS 1892:2021 cl. 5.6.3 (GeoCore implementation)",
        "assumptions": ["Guideline values ('may be followed'); the 10 % stress-increase criterion of cl. 5.6.3.1 also applies"],
        "output_units": {"Minimum depth below reference level [m]": "m"}
    },
    "borehole_layout_is1892": {
        "method": "IS 1892 disposition of boreholes / trial pits by structure type",
        "standard": "IS 1892:2021 cl. 5.6.2, Table 2 (GeoCore implementation)",
        "assumptions": ["Grid counts assume a rectangular built-up area at 50 m spacing"],
        "output_units": {"Minimum number of boreholes [-]": "-"}
    },
    "permissible_settlement_is1904": {
        "method": "IS 1904 permissible maximum settlement, differential settlement and angular distortion for shallow foundations",
        "standard": "IS 1904:2021 cl. 16.3, Table 1 (GeoCore implementation)",
        "assumptions": ["Table 1 values are a guide; the designer decides the permissible settlements",
                        "Load bearing walls interpolated linearly between L/H = 2 and 7"],
        "output_units": {"Permissible maximum settlement [mm]": "mm", "Permissible differential settlement [mm]": "mm"}
    },
    "stability_check_is1904": {
        "method": "Factor of safety = resisting / disturbing action against sliding or overturning",
        "standard": "IS 1904:2021 cl. 17.1 (GeoCore implementation)",
        "assumptions": ["Resisting and disturbing actions supplied by the engineer for the governing load case"],
        "output_units": {"Factor of safety [-]": "-"}
    },
    "raft_rigidity_is2950": {
        "method": "IS 2950 relative stiffness factor K = E/(12 Es) (d/b)^3 and critical column spacing 1.75/lambda, lambda = (kB/4EcI)^(1/4)",
        "standard": "IS 2950 (Part 1):1981 (Reaffirmed) cl. 5.1-5.2, Appendix C (GeoCore implementation)",
        "assumptions": ["K > 0.5 rigid; I = B d^3/12 unless given", "20 % column load/spacing variation check left to the engineer"],
        "output_units": {"Relative stiffness factor K [-]": "-", "Critical column spacing 1.75/lambda [m]": "m"}
    },
    "specific_gravity_is2720": {
        "method": "Density bottle G = (m2 - m1)/((m4 - m1) - (m3 - m2)), corrected to 27 degC by the water density ratio",
        "standard": "IS 2720 (Part 3/Sec 1):1980 cl. 5 (GeoCore implementation; water density after Tanaka et al. 2001)",
        "assumptions": ["Water used as the air-free liquid"],
        "output_units": {"Specific gravity at 27 degC [-]": "-"}
    },
    "flow_index_is2720": {
        "method": "Flow index If = (w1 - w2) / log10(N2 / N1)",
        "standard": "IS 2720 (Part 5):1985 cl. 3.5.2 (GeoCore implementation)",
        "assumptions": ["Straight flow curve on semi-log axes"],
        "output_units": {"Flow index If [%]": "%"}
    },
    "liquid_limit_one_point_is2720": {
        "method": "One-point liquid limit: wN / (1.3215 - 0.23 log N) (Casagrande) or wN / (0.77 log D), wN / (0.65 + 0.0175 D) (cone)",
        "standard": "IS 2720 (Part 5):1985 cl. 5.6, 6.5 (GeoCore implementation)",
        "assumptions": ["Not for highly organic soils; regional constants"],
        "output_units": {"Liquid limit wL [%]": "%"}
    },
    "consistency_indices_is2720": {
        "method": "Ip = wL - wP, IL = (w - wP)/Ip, Ic = (wL - w)/Ip, It = Ip/If",
        "standard": "IS 2720 (Part 5):1985 cl. 8-11 (GeoCore implementation)",
        "assumptions": ["Ip = 0 when wP >= wL"],
        "output_units": {"Plasticity index Ip [%]": "%"}
    },
    "permeability_constant_head_is2720": {
        "method": "Constant head k = Q L / (A h t), referred to 27 degC by the viscosity ratio",
        "standard": "IS 2720 (Part 17):1986 cl. 5.4 (GeoCore implementation; water viscosity by the Vogel equation)",
        "assumptions": ["Laminar flow through a saturated specimen"],
        "output_units": {"Permeability at 27 degC k27 [cm/s]": "cm/s"}
    },
    "permeability_falling_head_is2720": {
        "method": "Falling head k = 2.303 a L / (A t) log10(h1 / h2), referred to 27 degC by the viscosity ratio",
        "standard": "IS 2720 (Part 17):1986 cl. 6.3 (GeoCore implementation; water viscosity by the Vogel equation)",
        "assumptions": ["Laminar flow through a saturated specimen"],
        "output_units": {"Permeability at 27 degC k27 [cm/s]": "cm/s"}
    },
    # GeoCore registry wrapper around groundhog's Eurocode7_factoring_STR_GEO (no docstring of its own).
    "eurocode7_factors": {
        "method": "Eurocode 7 partial factors for STR/GEO limit states",
        "standard": "EN 1997-1:2004 Annex A (partial factor sets A, M and R)",
        "assumptions": [
            "Recommended Annex A values; the National Annex may prescribe different factors",
            "Factor sets per design approach (groundhog): DA1-1 A1+M1+R1, DA1-2 A2+M2+R1, DA2 A1+M1+R2, "
            "DA3-1 A1+M2+R3, DA3-2 A2+M2+R3",
            "Resistance factors depend on the selected foundation type",
        ],
        "output_units": {}
    }
}


def curated_tool_metadata(tool_name: str) -> Optional[Dict[str, Any]]:
    """The hand-written TOOL_METADATA entry for a tool, or None when it has none."""
    clean_name = tool_name.replace("calculate_", "").lower()
    if tool_name in TOOL_METADATA:
        return dict(TOOL_METADATA[tool_name])
    if clean_name in TOOL_METADATA:
        return dict(TOOL_METADATA[clean_name])
    return None


def get_tool_metadata(tool_name: str) -> Dict[str, Any]:
    """Retrieve standard reference and provenance metadata for a tool."""
    curated = curated_tool_metadata(tool_name)
    if curated is not None:
        return curated

    # Default generic metadata for dynamic Groundhog functions
    return {
        "method": f"Groundhog Deterministic Geotechnical Routine ({tool_name})",
        "standard": "Groundhog Open-Source Geotechnical Engineering Library",
        "assumptions": ["Deterministic calculation based on supplied parameters."],
        "output_units": {}
    }
