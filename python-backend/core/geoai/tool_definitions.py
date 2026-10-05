"""
Standard Tool Definitions for GeoAI
Binds Groundhog functions to the Tool Registry with canonical schemas.
"""
import math
from typing import Optional, Dict, Any, List

from core.geoai.tool_registry import tool_registry, geoai_tool, groundhog_forwarder
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
calculate_bulk_unit_weight = geoai_tool(
    name="calculate_bulk_unit_weight",
    description="Calculates bulk unit weight (gamma) and effective unit weight from specific gravity (Gs), void ratio (e), and degree of saturation (Sr).",
    category="classification",
    input_model=BulkUnitWeightInput,
    output_model=BulkUnitWeightOutput,
    form_function="bulkunitweight"
)(groundhog_forwarder("calculate_bulk_unit_weight", "groundhog.siteinvestigation.classification.phaserelations", "bulkunitweight"))


# 2. Void Ratio from Porosity
calculate_void_ratio_from_porosity = geoai_tool(
    name="calculate_void_ratio_from_porosity",
    description="Calculates void ratio (e) from porosity (n) using phase relations: e = n / (1 - n).",
    category="classification",
    input_model=VoidRatioPorosityInput,
    output_model=VoidRatioPorosityOutput,
    form_function="voidratio_porosity"
)(groundhog_forwarder("calculate_void_ratio_from_porosity", "groundhog.siteinvestigation.classification.phaserelations", "voidratio_porosity"))


# 3. Relative Density
calculate_relative_density = geoai_tool(
    name="calculate_relative_density",
    description="Calculates soil relative density (Dr) from current void ratio (e), minimum void ratio (e_min), and maximum void ratio (e_max).",
    category="classification",
    input_model=RelativeDensityInput,
    output_model=RelativeDensityOutput,
    form_function="relative_density"
)(groundhog_forwarder(
    "calculate_relative_density", "groundhog.siteinvestigation.classification.phaserelations", "relative_density",
    # Groundhog names void ratios by density: its e_min is the void ratio at MINIMUM density
    # (loosest, conventionally e_max) and vice versa. The tool uses the conventional meaning.
    arg_map={"e_min": "e_max", "e_max": "e_min"},
))


# 4. Vertical Stresses below Circular Footing
_stresses_circle_forward = groundhog_forwarder(
    "calculate_stresses_circular_footing", "groundhog.shallowfoundations.stressdistribution", "stresses_circle")


def _stresses_circle_corrected(**kwargs):
    result = _stresses_circle_forward(**kwargs)
    # Groundhog's 'delta sigma r [kPa]' uses 4(1 + nu) where Poulos & Davis (1974) /
    # Budhu (2011) have 2(1 + nu), so it tends to -q(1 + nu) instead of 0 at depth.
    # Recompute it here until fixed upstream; sigma_z from Groundhog is correct.
    # Left as NaN when Groundhog rejected the inputs.
    if not math.isnan(result['delta sigma r [kPa]']):
        q, nu = kwargs['imposedstress'], kwargs['poissonsratio']
        a = kwargs['z'] / math.hypot(kwargs['footing_radius'], kwargs['z'])
        result['delta sigma r [kPa]'] = 0.5 * q * ((1 + 2 * nu) - 2 * (1 + nu) * a + a ** 3)
    return result


_stresses_circle_corrected.__name__ = _stresses_circle_corrected.__qualname__ = "calculate_stresses_circular_footing"
_stresses_circle_corrected.__geoai_target__ = _stresses_circle_forward.__geoai_target__
_stresses_circle_corrected.__geoai_arg_map__ = _stresses_circle_forward.__geoai_arg_map__

calculate_stresses_circular_footing = geoai_tool(
    name="calculate_stresses_circular_footing",
    description="Calculates vertical and horizontal elastic stress increments in a soil half-space under the center of a circular loaded area.",
    category="shallow_foundations",
    input_model=StressesCircleInput,
    output_model=StressesCircleOutput,
    form_function="stresses_circle"
)(_stresses_circle_corrected)


# 5. Point Load Stresses (Boussinesq)
_stresses_pointload_forward = groundhog_forwarder(
    "calculate_stresses_point_load", "groundhog.shallowfoundations.stressdistribution", "stresses_pointload")


def _stresses_pointload_corrected(**kwargs):
    result = _stresses_pointload_forward(**kwargs)
    # Groundhog's 'delta sigma theta [kPa]' has the bracket reversed (sign flipped), so
    # on the load axis it does not equal sigma_r as axisymmetry requires. Recompute the
    # Boussinesq expression (compression positive) until fixed upstream; the other
    # components from Groundhog are correct. Left as NaN when Groundhog rejected the inputs.
    if not math.isnan(result['delta sigma theta [kPa]']):
        Q, z, nu = kwargs['pointload'], kwargs['z'], kwargs['poissonsratio']
        R = math.hypot(kwargs['r'], z)
        result['delta sigma theta [kPa]'] = (
            Q / (2 * math.pi) * (1 - 2 * nu) * (1 / (R * (R + z)) - z / R ** 3)
        )
    return result


_stresses_pointload_corrected.__name__ = _stresses_pointload_corrected.__qualname__ = "calculate_stresses_point_load"
_stresses_pointload_corrected.__geoai_target__ = _stresses_pointload_forward.__geoai_target__
_stresses_pointload_corrected.__geoai_arg_map__ = _stresses_pointload_forward.__geoai_arg_map__

calculate_stresses_point_load = geoai_tool(
    name="calculate_stresses_point_load",
    description="Calculates 3D elastic stress distribution (sigma_z, sigma_r, sigma_theta, tau_rz) from a concentrated surface point load using Boussinesq theory.",
    category="shallow_foundations",
    input_model=StressesPointloadInput,
    output_model=StressesPointloadOutput,
    form_function="stresses_pointload"
)(_stresses_pointload_corrected)


# 6. Gmax from Shear Wave Velocity
calculate_gmax_from_shear_wave_velocity = geoai_tool(
    name="calculate_gmax_from_shear_wave_velocity",
    description="Calculates small-strain shear modulus Gmax [kPa] from shear wave velocity Vs [m/s] and unit weight gamma [kN/m3].",
    category="soil_dynamics",
    input_model=GmaxShearWaveVelocityInput,
    output_model=GmaxShearWaveVelocityOutput,
    form_function="gmax_shearwavevelocity"
)(groundhog_forwarder("calculate_gmax_from_shear_wave_velocity", "groundhog.soildynamics.soilproperties", "gmax_shearwavevelocity"))


# 7. Earth Pressure Coefficients (Rankine)
calculate_earth_pressure_rankine = geoai_tool(
    name="calculate_earth_pressure_rankine",
    description="Calculates active (Ka) and passive (Kp) lateral earth pressure coefficients for inclined or vertical walls using Rankine theory.",
    category="excavations",
    input_model=EarthPressureRankineInput,
    output_model=EarthPressureRankineOutput,
    form_function="earthpressurecoefficients_rankine"
)(groundhog_forwarder("calculate_earth_pressure_rankine", "groundhog.excavations.basic", "earthpressurecoefficients_rankine"))


# 8. Pipeline Contact Width
calculate_pipeline_contact_width = geoai_tool(
    name="calculate_pipeline_contact_width",
    description="Calculates contact width between a subsea pipeline and seabed from outer diameter and embedment depth.",
    category="pipelines",
    input_model=ContactWidthInput,
    output_model=ContactWidthOutput,
    form_function="contactwidth"
)(groundhog_forwarder("calculate_pipeline_contact_width", "groundhog.pipelinescables.stability.penetration", "contactwidth"))


# 9. Hydraulic Conductivity (Pumping Test)
calculate_hydraulic_conductivity_unconfined = geoai_tool(
    name="calculate_hydraulic_conductivity_unconfined",
    description="Calculates aquifer hydraulic conductivity k [m/s] from unconfined steady-state pumping test data using the Dupuit-Thiem solution.",
    category="consolidation",
    input_model=HydraulicConductivityUnconfinedInput,
    output_model=HydraulicConductivityUnconfinedOutput,
    form_function="hydraulicconductivity_unconfinedaquifer"
)(groundhog_forwarder("calculate_hydraulic_conductivity_unconfined", "groundhog.consolidation.groundwaterflow.pumpingtests", "hydraulicconductivity_unconfinedaquifer"))


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
    IndexDocumentTextInput, IndexDocumentTextOutput,
    GetFunctionDocumentationInput, GetFunctionDocumentationOutput
)
from core.geoai.research.indexer import local_indexer
from core.geoai.research.docs_adapter import get_docs_adapter
from core.geoai.exceptions import GeoAIValidationError


@geoai_tool(
    name="search_local_documents",
    description="Searches local project documents, technical notes, papers, and standards using BM25 full-text retrieval.",
    category="research",
    input_model=SearchLocalDocumentsInput,
    output_model=SearchLocalDocumentsOutput
)
def search_local_documents(query: str, top_k: int = 5):
    # The shipped GeoCore/Groundhog docs are part of the index (once per process, skipped when unchanged).
    get_docs_adapter().ensure_indexed(local_indexer)
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


# 14b. Function documentation (shipped Groundhog docstrings via the docs adaptor)
@geoai_tool(
    name="get_function_documentation",
    description="Returns the documented inputs (with units and suggested ranges), outputs, formulas and cited references of one Groundhog calculation function. Use it to explain a method or check required inputs; it does not calculate.",
    category="documentation",
    input_model=GetFunctionDocumentationInput,
    output_model=GetFunctionDocumentationOutput
)
def get_function_documentation(function_name: str):
    import difflib
    adapter = get_docs_adapter()
    if not adapter.available():
        raise GeoAIValidationError("GeoCore documentation is not available in this installation.")
    doc = adapter.function_doc(function_name)
    if doc is None:
        close = difflib.get_close_matches(function_name, adapter.function_names(), n=5, cutoff=0.6)
        hint = f" Did you mean: {', '.join(close)}?" if close else ""
        raise GeoAIValidationError(f"No documentation for '{function_name}'.{hint}")
    out = doc.to_dict()
    out["attribution"] = adapter.attribution
    return out


# 15-16. Shallow foundation bearing capacity and settlement (Groundhog stateful workflows as one-shot tools)
import core.geoai.tools_shallow  # noqa: E402,F401  (registers calculate_shallow_foundation_capacity / _settlement)


# 17-19. Project CPT retrieval and CPT-based axial pile capacity (Groundhog LCPC / Koppejan / De Beer)
import core.geoai.tools_cpt_piles  # noqa: E402,F401  (registers list_project_cpts, get_cpt_summary, calculate_pile_capacity_from_cpt)
