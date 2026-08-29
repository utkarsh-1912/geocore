# Author: Utkarsh Gupta
# License: GPL v3
"""
Automated Test Suite for Local Document Research (RAG), SQLite FTS5 Indexing,
and 6-Tier Evidence Grounding Synthesis.
"""

import pytest
from pathlib import Path

from core.geoai.research.indexer import LocalDocumentIndexer, SearchResult
from core.geoai.research.evidence import (
    ResearchGroundingReport,
    EvidenceTier,
    EvidenceItem
)
from core.geoai.tool_registry import tool_registry
import core.geoai.tool_definitions


# =====================================================================
# 1. SQLite FTS5 Local Document Indexer Tests
# =====================================================================

def test_local_indexer_chunking_and_search(tmp_path):
    db_file = tmp_path / "test_rag.db"
    indexer = LocalDocumentIndexer(db_path=db_file)

    sample_doc = """
# Eurocode 7 Geotechnical Design Principles

## Ultimate Limit State (ULS) Requirements
For spread foundations, the design bearing capacity Rd must satisfy Vd <= Rd.
Partial resistance factors are applied to soil properties under Design Approach 1 (DA1).

## Consolidation and Settlement
Primary settlement shall be evaluated using one-dimensional oedometer constrained modulus M.
Secondary creep settlement becomes dominant in highly organic soils and soft clays.
    """

    chunks = indexer.index_text_content(
        doc_id="EC7_SUMMARY",
        title="Eurocode 7 Summary Note",
        content=sample_doc
    )
    assert chunks >= 2
    assert indexer.get_document_count() == 1

    # Search for "spread foundations"
    results = indexer.search("spread foundations")
    assert len(results) >= 1
    assert "ULS" in results[0].section_heading or "Eurocode" in results[0].doc_title
    assert "Vd <= Rd" in results[0].content

    # Search for "consolidation settlement"
    results_settle = indexer.search("consolidation settlement")
    assert len(results_settle) >= 1
    assert "oedometer" in results_settle[0].content.lower()


def test_indexer_file_indexing(tmp_path):
    db_file = tmp_path / "test_file_rag.db"
    indexer = LocalDocumentIndexer(db_path=db_file)

    # Create temporary markdown file
    doc_file = tmp_path / "cpt_technical_guideline.md"
    doc_file.write_text("""
# CPT Interpretation Guide 2024
The Robertson (2009) unified SBT index Ic ranges between 1.31 and 3.6.
For Ic > 2.6, soils behave predominantly as fine-grained clays and silts.
    """, encoding="utf-8")

    count = indexer.index_file(doc_file)
    assert count >= 1

    results = indexer.search("Robertson unified SBT")
    assert len(results) >= 1
    assert "fine-grained" in results[0].content


# =====================================================================
# 2. Evidence Grounding 6-Tier Report Tests
# =====================================================================

def test_evidence_grounding_report():
    report = ResearchGroundingReport(topic="Spread Footing Bearing Capacity at Site B")

    report.add_project_evidence("BH-01 at 4.0m", "Medium dense sand with measured SPT N = 22 and Vs = 260 m/s.")
    report.add_calculation_evidence(
        tool_name="calculate_earth_pressure_rankine",
        method="Rankine (1857)",
        result_summary="Ka = 0.333, Kp = 3.00 for phi' = 30.0 deg."
    )
    report.add_literature_evidence("Robertson (2009)", "SBT Index Ic < 2.05 indicates clean to silty sand behavior.")
    report.add_standard_guidance("Eurocode 7 EN 1997-1:2004", "Clause 6.5.2: Verification against bearing resistance failure.")
    report.add_assumption("Water table located at 1.5m depth under hydrostatic equilibrium.")

    md = report.to_markdown()
    assert "Evidence Grounding Report" in md
    assert "[Project Evidence]" in md or "#### Project Evidence" in md
    assert "[Calculation Evidence]" in md or "#### Calculation Evidence" in md
    assert "[Literature Evidence]" in md or "#### Literature Evidence" in md
    assert "[Standards / Guidance]" in md or "#### Standards / Guidance" in md
    assert "[Assumption]" in md or "#### Assumption" in md
    assert "BH-01" in md
    assert "Eurocode 7" in md


# =====================================================================
# 3. Tool Registry Invocation of Research Tools
# =====================================================================

def test_tool_registry_index_and_search():
    index_tool = tool_registry.get_tool("index_document_text")
    search_tool = tool_registry.get_tool("search_local_documents")
    assert index_tool is not None
    assert search_tool is not None

    # 1. Index document via tool
    res_idx = index_tool.invoke({
        "doc_id": "LCPC_NOTE",
        "title": "Bustamante LCPC Pile Capacity Method",
        "content": "The LCPC method computes pile unit base resistance qb = qc * kc and shaft friction qs from CPT cone resistance."
    })
    assert res_idx["status"] == "indexed"
    assert res_idx["indexed_chunks"] >= 1
    assert "_provenance" in res_idx

    # 2. Search document via tool
    res_search = search_tool.invoke({
        "query": "LCPC pile unit base resistance",
        "top_k": 3
    })
    assert res_search["total_found"] >= 1
    assert len(res_search["results"]) >= 1
    assert "qb = qc * kc" in res_search["results"][0]["content"]
    assert "_provenance" in res_search
