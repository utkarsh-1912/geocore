"""
Standard Tool Definitions for GeoAI
Binds Groundhog functions to the Tool Registry with canonical schemas.
"""
from typing import Optional, Dict, Any, List
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


# 10. SPT Normalization & Empirical Correlation
from core.geoai.schemas.in_situ import (
    NormalizeSPTInput, NormalizeSPTOutput,
    ClassifyCPTSoilBehaviorInput, ClassifyCPTSoilBehaviorOutput,
    DeriveCPTParametersInput, DeriveCPTParametersOutput
)
from core.geoai.spt import SPTRecord
from core.geoai.cpt import CPTSounding
import pandas as pd


@geoai_tool(
    name="normalize_spt_test",
    description="Normalizes raw SPT blow count N to standard N60 and overburden-corrected (N1)60, and estimates relative density Dr and friction angle phi'.",
    category="in_situ",
    input_model=NormalizeSPTInput,
    output_model=NormalizeSPTOutput
)
def normalize_spt_test(
    raw_n: int,
    depth: float,
    energy_ratio: float = 0.60,
    rod_length: float = 10.0,
    borehole_diameter_mm: float = 150.0,
    has_liner: bool = False,
    overburden_kpa: Optional[float] = None
):
    rec = SPTRecord(
        borehole_id="SPT_TEST",
        depth=depth,
        raw_n=raw_n,
        energy_ratio=energy_ratio,
        rod_length=rod_length,
        borehole_diameter_mm=borehole_diameter_mm,
        has_liner=has_liner,
        effective_overburden_kpa=overburden_kpa
    )
    return rec.correlate_granular_properties()


# 11. CPT Soil Behavior Type Classification
@geoai_tool(
    name="classify_cpt_soil_behavior",
    description="Classifies soil behavior type (SBT) and calculates normalized CPT indices (Qt, Fr, Bq, Ic) using Robertson (1990/2009).",
    category="in_situ",
    input_model=ClassifyCPTSoilBehaviorInput,
    output_model=ClassifyCPTSoilBehaviorOutput
)
def classify_cpt_soil_behavior(
    qc_mpa: float,
    fs_kpa: float,
    depth: float,
    u2_kpa: float = 0.0,
    water_table_depth: float = 0.0
):
    df_raw = pd.DataFrame([{
        "depth": depth,
        "qc": qc_mpa,
        "fs": fs_kpa,
        "u2": u2_kpa
    }])
    sounding = CPTSounding(sounding_id="CPT_POINT", raw_data=df_raw)
    sounding.calculate_normalized_parameters(water_table_depth=water_table_depth)
    return sounding.get_summary_at_depth(depth)


# 12. CPT Parameter Derivations
@geoai_tool(
    name="derive_cpt_parameters",
    description="Derives geotechnical design parameters (undrained shear strength su, friction angle phi', relative density Dr, small-strain shear modulus Gmax) from CPT measurements.",
    category="in_situ",
    input_model=DeriveCPTParametersInput,
    output_model=DeriveCPTParametersOutput
)
def derive_cpt_parameters(
    qc_mpa: float,
    fs_kpa: float,
    depth: float,
    Nkt: float = 15.0
):
    df_raw = pd.DataFrame([{
        "depth": depth,
        "qc": qc_mpa,
        "fs": fs_kpa,
        "u2": 0.0
    }])
    sounding = CPTSounding(sounding_id="CPT_POINT", raw_data=df_raw)
    return sounding.derive_soil_parameters(depth, Nkt=Nkt)


# 13. Local Document Search (RAG)
from core.geoai.schemas.research import (
    SearchLocalDocumentsInput, SearchLocalDocumentsOutput,
    IndexDocumentTextInput, IndexDocumentTextOutput
)
from core.geoai.research.indexer import local_indexer


@geoai_tool(
    name="search_local_documents",
    description="Searches local project documents, technical notes, papers, and standards using BM25 full-text retrieval.",
    category="research",
    input_model=SearchLocalDocumentsInput,
    output_model=SearchLocalDocumentsOutput
)
def search_local_documents(query: str, top_k: int = 5):
    results = local_indexer.search(query, top_k=top_k)
    return {
        "query": query,
        "total_found": len(results),
        "results": [
            {
                "chunk_id": r.chunk_id,
                "doc_title": r.doc_title,
                "file_path": r.file_path,
                "section": r.section_heading,
                "content": r.content,
                "score": round(r.score, 3)
            }
            for r in results
        ]
    }


# 14. Local Document Indexing
@geoai_tool(
    name="index_document_text",
    description="Indexes raw text or markdown technical content into the local SQLite full-text search index.",
    category="research",
    input_model=IndexDocumentTextInput,
    output_model=IndexDocumentTextOutput
)
def index_document_text(doc_id: str, title: str, content: str):
    chunks = local_indexer.index_text_content(doc_id=doc_id, title=title, content=content)
    return {
        "doc_id": doc_id,
        "indexed_chunks": chunks,
        "status": "indexed"
    }
