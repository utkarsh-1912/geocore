# Author: Utkarsh Gupta
# License: GPL v3
"""
Geotechnical Evaluation & SFT/LoRA Training Dataset Generator.
Synthesizes gold-standard instruction tuning and evaluation datasets conforming
to AGENTS.md §19 & §20 requirements across 7 core engineering categories:
1. Correct Requests (Exact Groundhog tool calling with unit normalization)
2. Ambiguous Requests (Engineering clarification dialogues)
3. Missing Parameter Requests (Specific soil parameter prompting)
4. Unit Conversion & Trap Cases (Handling and correcting non-standard units)
5. Conflicting Data Scenarios (Reconciling CPT vs Borehole discrepancies)
6. Research & Literature Synthesis (Grounded technical comparisons without hallucinated DOIs)
7. Tool Failure Recovery (Transparent error explanation and remediation guidance)
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class GeotechnicalExample:
    id: str
    category: str
    user_prompt: str
    expected_action: str  # "tool_call", "clarify", "reject", "synthesize", "explain"
    expected_tool: Optional[str] = None
    expected_arguments: Optional[Dict[str, Any]] = None
    expected_response: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    def to_chatml(self) -> List[Dict[str, Any]]:
        """Converts example into standard ChatML conversation format for training."""
        messages = [
            {"role": "system", "content": "You are GeoAI, a local geotechnical engineering assistant inside GeoCore. You reason and select tools while Groundhog calculates deterministically. Never invent soil parameters or claim unsupported certainty."},
            {"role": "user", "content": self.user_prompt}
        ]
        
        if self.expected_action == "tool_call" and self.expected_tool:
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": f"call_{self.id}",
                    "type": "function",
                    "function": {
                        "name": self.expected_tool,
                        "arguments": json.dumps(self.expected_arguments or {})
                    }
                }]
            })
        else:
            messages.append({
                "role": "assistant",
                "content": self.expected_response or ""
            })
            
        return messages


def build_core_training_examples() -> List[GeotechnicalExample]:
    """Generates curated representative geotechnical instruction-tuning dataset."""
    examples = [
        # --- 1. Correct Tool Requests ---
        GeotechnicalExample(
            id="correct_01_gmax",
            category="correct_request",
            user_prompt="Calculate the small-strain shear modulus Gmax for a dense sand layer where shear wave velocity is 280 m/s and total unit weight is 19.5 kN/m3.",
            expected_action="tool_call",
            expected_tool="calculate_gmax_from_shear_wave_velocity",
            expected_arguments={"Vs": 280.0, "gamma": 19.5}
        ),
        GeotechnicalExample(
            id="correct_02_rankine",
            category="correct_request",
            user_prompt="Estimate active and passive lateral earth pressure coefficients for a vertical retaining wall with horizontal backfill where friction angle is 34 degrees.",
            expected_action="tool_call",
            expected_tool="calculate_earth_pressure_rankine",
            expected_arguments={"phi_eff": 34.0, "wall_angle": 0.0, "top_angle": 0.0}
        ),
        GeotechnicalExample(
            id="correct_03_spt_normalization",
            category="correct_request",
            user_prompt="Normalize an SPT test at 7.5m depth with a field blow count N = 22 using a 60% standard safety hammer and 150mm borehole.",
            expected_action="tool_call",
            expected_tool="normalize_spt_test",
            expected_arguments={"raw_n": 22, "depth": 7.5, "energy_ratio": 0.60, "borehole_diameter_mm": 150.0}
        ),
        GeotechnicalExample(
            id="correct_04_cpt_sbt",
            category="correct_request",
            user_prompt="Classify the soil behavior type for a CPT test at 4.2m depth with cone tip resistance qc = 8.5 MPa and sleeve friction fs = 42 kPa.",
            expected_action="tool_call",
            expected_tool="classify_cpt_soil_behavior",
            expected_arguments={"qc_mpa": 8.5, "fs_kpa": 42.0, "depth": 4.2}
        ),
        GeotechnicalExample(
            id="correct_05_circular_footing_stress",
            category="correct_request",
            user_prompt="Calculate the vertical stress increment under the center of a circular footing with radius 2.5m bearing 150 kPa surface pressure at a depth of 6m.",
            expected_action="tool_call",
            expected_tool="calculate_stresses_circular_footing",
            expected_arguments={"footing_radius": 2.5, "q": 150.0, "z": 6.0, "r": 0.0}
        ),

        # --- 2. Ambiguous Requests (Clarification) ---
        GeotechnicalExample(
            id="ambiguous_01_pile",
            category="ambiguous_request",
            user_prompt="Calculate the pile capacity for my project.",
            expected_action="clarify",
            expected_response="To calculate axial pile capacity, please specify:\n1. Pile geometry (diameter/width, embedded length, wall thickness if hollow steel pipe).\n2. Installation method (driven open/closed ended steel tube, bored cast-in-place concrete, CFA).\n3. Calculation method (e.g. CPT-based LCPC Bustamante & Gianeselli, API RP 2GEO, or ICP-05).\n4. Target soil profile or sounding ID."
        ),
        GeotechnicalExample(
            id="ambiguous_02_settlement",
            category="ambiguous_request",
            user_prompt="What is the settlement of the foundation?",
            expected_action="clarify",
            expected_response="To evaluate foundation settlement, I need:\n1. Foundation dimensions (width B, length L, embedment depth Df).\n2. Applied bearing pressure or column load.\n3. Soil compressibility parameters (compression index Cc / recompression index Cr, or constrained modulus M, or SPT/CPT profile)."
        ),

        # --- 3. Missing Data Requests ---
        GeotechnicalExample(
            id="missing_01_bearing_capacity",
            category="missing_data",
            user_prompt="Calculate the bearing capacity for a 2m wide square footing at 1m depth.",
            expected_action="clarify",
            expected_response="To compute bearing capacity using Hansen/Vesic formulations, please provide the soil shear strength parameters: effective friction angle (phi') and effective cohesion (c') for drained conditions, or undrained shear strength (su) for undrained analysis, along with the soil unit weight (gamma)."
        ),
        GeotechnicalExample(
            id="missing_02_retaining_wall",
            category="missing_data",
            user_prompt="What is the passive earth pressure coefficient for my retaining wall?",
            expected_action="clarify",
            expected_response="Please specify the effective soil friction angle (phi') and whether the backfill is horizontal or sloping. If the wall has interface friction (delta), please provide that as well."
        ),

        # --- 4. Unit Conversion & Trap Cases ---
        GeotechnicalExample(
            id="unit_trap_01_pressure",
            category="wrong_units",
            user_prompt="Calculate Gmax with Vs = 300 m/s and gamma = 19 kPa.",
            expected_action="clarify",
            expected_response="Unit mismatch detected: '19 kPa' is a pressure unit, whereas soil total unit weight (gamma) must be in unit weight units (kN/m³). Did you mean gamma = 19.0 kN/m³?"
        ),
        GeotechnicalExample(
            id="unit_norm_02_valid",
            category="correct_request",
            user_prompt="Estimate Rankine earth pressure coefficients for friction angle 0.5236 radians.",
            expected_action="tool_call",
            expected_tool="calculate_earth_pressure_rankine",
            expected_arguments={"phi_eff": 30.0, "wall_angle": 0.0, "top_angle": 0.0}
        ),

        # --- 5. Conflicting Data Scenarios ---
        GeotechnicalExample(
            id="conflict_01_cpt_vs_borehole",
            category="conflicting_data",
            user_prompt="CPT-01 at 5m depth indicates clean sand with Ic = 1.6, but borehole log BH-02 at 5m depth describes soft silty clay. How should I reconcile this?",
            expected_action="synthesize",
            expected_response="### Stratigraphic Reconciliation Analysis:\n1. **Horizontal Distance & Geological Dip**: Check the spatial separation between CPT-01 and BH-02 for dipping strata or paleochannel boundaries.\n2. **CPT Pore Pressure**: Inspect CPT sleeve friction (fs) and dynamic pore pressure (u2). If u2 did not elevate above hydrostatic, sandy behavior is confirmed at CPT-01.\n3. **Sampling Disturbance in BH-02**: Verify whether sample recovery in BH-02 experienced washing of fines or sample mix-up.\n4. **Recommended Action**: Review continuous CPT Qt and Fr profiles across the 4-6m depth interval and perform localized verification push."
        ),

        # --- 6. Research & Standards Synthesis ---
        GeotechnicalExample(
            id="research_01_cpt_methods",
            category="research",
            user_prompt="Compare Robertson 1990 vs Robertson 2009 formulations for CPT soil behavior type index Ic.",
            expected_action="synthesize",
            expected_response="### CPT SBTn Formulation Comparison:\n- **Robertson (1990)**: Uses normalized cone resistance Qt = (qt - sigma_v0) / sigma_v0' and normalized friction ratio Fr. The stress exponent n is fixed at 1.0 (typical for clays).\n- **Robertson & Wride (1998) / Robertson (2009)**: Introduces an iterative stress exponent n that varies continuously from 1.0 in clays to 0.5 in clean sands: n = 0.381*(Ic) + 0.05*(sigma_v0'/Pa) - 0.150 <= 1.0. This prevents artificial overestimation of normalized resistance in deep dense sands.\n- **Standard Reference**: ASTM D5778 / ISSMGE TC-16."
        ),

        # --- 7. Tool Failure Recovery ---
        GeotechnicalExample(
            id="failure_01_invalid_cpt",
            category="tool_failure",
            user_prompt="Classify soil behavior for qc = -5.0 MPa and fs = 20 kPa at depth 3m.",
            expected_action="reject",
            expected_response="Cone tip resistance qc must be strictly positive (qc > 0 MPa). Negative values indicate sensor drift, baseline zero offset error, or uncorrected hydrostatic bias during pre-push calibration."
        )
    ]
    return examples


def export_dataset_jsonl(filepath: Path) -> int:
    """Exports instruction dataset in JSONL format for fine-tuning / evaluation."""
    examples = build_core_training_examples()
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, "w", encoding="utf-8") as f:
        for ex in examples:
            record = {
                "id": ex.id,
                "category": ex.category,
                "user_prompt": ex.user_prompt,
                "expected_action": ex.expected_action,
                "expected_tool": ex.expected_tool,
                "expected_arguments": ex.expected_arguments,
                "messages": ex.to_chatml()
            }
            f.write(json.dumps(record) + "\n")
            
    return len(examples)
