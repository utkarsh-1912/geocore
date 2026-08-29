# Author: Utkarsh Gupta
# License: GPL v3
"""
Automated Test Suite for First-Class CPT, SPT, and AGS Ingestion & Query Tools.
"""

import pytest
import pandas as pd
import numpy as np

from core.geoai.cpt import CPTSounding
from core.geoai.spt import SPTRecord
from core.geoai.ags import AGSProjectDataset
from core.geoai.tool_registry import tool_registry
import core.geoai.tool_definitions


# =====================================================================
# 1. CPT Sounding Normalization & SBT Classification Tests
# =====================================================================

def test_cpt_sounding_normalization_sand():
    # Synthetic sand layer at 5m depth: qc = 12.0 MPa, fs = 60 kPa, u2 = 50 kPa
    df = pd.DataFrame([{
        "depth": 5.0,
        "qc": 12.0,
        "fs": 60.0,
        "u2": 50.0
    }])
    cpt = CPTSounding("CPT-01", raw_data=df)
    summary = cpt.get_summary_at_depth(5.0)

    assert summary["sounding_id"] == "CPT-01"
    assert summary["qc_mpa"] == 12.0
    assert summary["Qt"] > 50.0  # High normalized resistance in dense sand
    assert summary["Ic"] < 2.05  # Sand classification
    assert "Sand" in summary["sbt_description"]

    # Parameter derivations
    derived = cpt.derive_soil_parameters(5.0)
    assert derived["phi_eff_deg"] > 35.0
    assert derived["Dr_pct"] > 40.0
    assert derived["su_kpa"] is None
    assert derived["Gmax_kpa"] > 10000.0


def test_cpt_sounding_normalization_clay():
    # Synthetic soft clay layer at 3m depth: qc = 0.8 MPa, fs = 35 kPa, u2 = 80 kPa
    df = pd.DataFrame([{
        "depth": 3.0,
        "qc": 0.8,
        "fs": 35.0,
        "u2": 80.0
    }])
    cpt = CPTSounding("CPT-02", raw_data=df)
    summary = cpt.get_summary_at_depth(3.0)

    assert summary["sounding_id"] == "CPT-02"
    assert summary["Ic"] > 2.60  # Fine-grained soil threshold (Robertson 1990)
    assert "Clay" in summary["sbt_description"] or "Silt" in summary["sbt_description"]

    # Parameter derivations with Nkt = 15
    derived = cpt.derive_soil_parameters(3.0, Nkt=15.0)
    assert derived["su_kpa"] is not None
    assert 30.0 <= derived["su_kpa"] <= 70.0
    assert derived["phi_eff_deg"] == 0.0


def test_cpt_sounding_compact_summary():
    df = pd.DataFrame([
        {"depth": 1.0, "qc": 1.2, "fs": 40.0, "u2": 10.0},
        {"depth": 2.0, "qc": 1.5, "fs": 45.0, "u2": 20.0},
        {"depth": 4.0, "qc": 10.5, "fs": 55.0, "u2": 30.0},
        {"depth": 6.0, "qc": 14.0, "fs": 70.0, "u2": 40.0}
    ])
    cpt = CPTSounding("CPT-03", raw_data=df)
    summary_md = cpt.to_compact_summary()

    assert "CPT SOUNDING SUMMARY: CPT-03" in summary_md
    assert "Total Depth: 6.00 m" in summary_md
    assert "SBT Classification" in summary_md


# =====================================================================
# 2. SPT Normalization & Empirical Correlation Tests
# =====================================================================

def test_spt_normalization_skempton_liao():
    # Test at 6.0m depth, raw N = 18, 60% hammer energy
    spt = SPTRecord(
        borehole_id="BH-01",
        depth=6.0,
        raw_n=18,
        energy_ratio=0.60,
        rod_length=8.0,
        borehole_diameter_mm=150.0,
        has_liner=False
    )
    n60, corrections = spt.calculate_n60()
    assert n60 > 15.0
    assert corrections["Ce"] == 1.0
    assert corrections["Cr"] == 0.95

    n60, n1_60, corr_full = spt.calculate_n1_60()
    assert n1_60 > 0
    assert "Cn" in corr_full

    correlations = spt.correlate_granular_properties()
    assert correlations["density_class"] in ("Medium Dense", "Dense")
    assert 30.0 <= correlations["phi_eff_deg"] <= 42.0
    assert 40.0 <= correlations["Dr_pct"] <= 85.0


# =====================================================================
# 3. AGS Ingestion & Query Tests
# =====================================================================

SAMPLE_AGS_TEXT = """
"GROUP","PROJ"
"HEADING","PROJ_ID","PROJ_NAME","PROJ_LOC","PROJ_CLNT"
"DATA","P1001","Offshore Substation Alpha","North Sea","Global Energy Corp"

"GROUP","HOLE"
"HEADING","HOLE_ID","HOLE_TYPE","HOLE_GL","HOLE_FDEP"
"DATA","BH-01","Borehole Rotary","0.0","25.0"
"DATA","BH-02","Sonic Borehole","0.0","30.0"

"GROUP","GEOL"
"HEADING","HOLE_ID","GEOL_TOP","GEOL_BASE","GEOL_DESC","GEOL_GEOL"
"DATA","BH-01","0.0","4.0","Very soft dark grey organic CLAY","CLAY"
"DATA","BH-01","4.0","12.5","Medium dense yellowish brown fine to medium SAND","SAND"
"DATA","BH-01","12.5","25.0","Very stiff dark brown silty CLAY with gravel","CLAY"

"GROUP","ISPT"
"HEADING","HOLE_ID","ISPT_TOP","ISPT_NVAL","ISPT_MAIN"
"DATA","BH-01","5.0","16","16"
"DATA","BH-01","8.0","24","24"
"DATA","BH-01","10.0","32","32"
"""

def test_ags_parser_groups_and_queries():
    dataset = AGSProjectDataset.parse_ags_text(SAMPLE_AGS_TEXT, filename="sample.ags")
    
    assert dataset.project_info["PROJ_NAME"] == "Offshore Substation Alpha"
    assert "HOLE" in dataset.groups
    assert "GEOL" in dataset.groups
    assert "ISPT" in dataset.groups

    # Borehole listing
    holes = dataset.list_boreholes()
    assert len(holes) == 2
    assert holes[0]["hole_id"] == "BH-01"
    assert holes[0]["final_depth_m"] == 25.0

    # Strata extraction
    strata = dataset.get_stratigraphy_for_hole("BH-01")
    assert len(strata) == 3
    assert strata[0]["description"].startswith("Very soft")
    assert strata[1]["thickness_m"] == 8.5

    # SPT extraction
    spts = dataset.get_spt_for_hole("BH-01")
    assert len(spts) == 3
    assert spts[0]["raw_N"] == 16
    assert spts[0]["phi_eff_deg"] > 30.0

    # Compact summary
    summary_md = dataset.to_compact_summary()
    assert "Offshore Substation Alpha" in summary_md
    assert "BH-01" in summary_md


# =====================================================================
# 4. Tool Registry Execution of In-Situ Tools
# =====================================================================

def test_invoke_normalize_spt_test():
    tool = tool_registry.get_tool("normalize_spt_test")
    assert tool is not None

    res = tool.invoke({"raw_n": 22, "depth": 5.0, "energy_ratio": 0.60})
    assert "N60" in res
    assert "N1_60" in res
    assert "phi_eff_deg" in res
    assert res["phi_eff_deg"] > 30.0
    assert "_provenance" in res
    assert "Skempton" in res["_provenance"]["method"]


def test_invoke_classify_cpt_soil_behavior():
    tool = tool_registry.get_tool("classify_cpt_soil_behavior")
    assert tool is not None

    res = tool.invoke({"qc_mpa": 15.0, "fs_kpa": 80.0, "depth": 6.0})
    assert "Qt" in res
    assert "Ic" in res
    assert "sbt_description" in res
    assert "_provenance" in res
    assert "Robertson" in res["_provenance"]["method"]


def test_invoke_derive_cpt_parameters():
    tool = tool_registry.get_tool("derive_cpt_parameters")
    assert tool is not None

    # Fine-grained soil: qc = 1.0 MPa, fs = 40 kPa
    res_clay = tool.invoke({"qc_mpa": 1.0, "fs_kpa": 40.0, "depth": 4.0, "Nkt": 15.0})
    assert "su_kpa" in res_clay
    assert res_clay["su_kpa"] is not None
    assert "_provenance" in res_clay
