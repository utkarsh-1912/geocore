# Author: Utkarsh Gupta
# License: GPL v3
"""
Direct Preference Optimization (DPO) and Reinforcement Learning from Geotechnical Feedback (RLGF).
Constructs (prompt, chosen, rejected) trios encoding strict engineering caution,
provenance citation, and deterministic tool execution rules from AGENTS.md §5 & §18.
"""

from pathlib import Path
import json
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class DPOPreferencePair:
    id: str
    prompt: str
    chosen: str      # Safe, evidence-grounded, tool-calling response
    rejected: str    # Hallucinated calculation, definitive safety claim, or guessing missing parameters
    rationale: str   # Engineering alignment rule


def build_dpo_preference_dataset() -> List[DPOPreferencePair]:
    pairs = [
        # --- Rule: Never say "this design is safe" without formal limit state basis ---
        DPOPreferencePair(
            id="dpo_01_safety_claim",
            prompt="I calculated bearing capacity q_ult = 420 kPa for a 150 kPa applied load. Is this foundation safe?",
            chosen="Under the applied load of 150 kPa and calculated ultimate bearing capacity of 420 kPa, the geotechnical factor of safety is FS = 2.80 (exceeding standard minimum FS of 2.5 - 3.0 for permanent shallow foundations under Eurocode 7 / USACE). Settlement, sliding, and eccentric tilt limit states must also be verified.",
            rejected="Yes, this design is completely safe and you can proceed with construction immediately.",
            rationale="AGENTS.md §18: Never make definitive 'this design is safe' claims. Report calculated margins, factor of safety, and remaining limit states."
        ),

        # --- Rule: Never calculate engineering equations directly in the LLM prompt ---
        DPOPreferencePair(
            id="dpo_02_deterministic_tool",
            prompt="What is Ka for friction angle 30 degrees?",
            chosen="[Tool Call: `calculate_earth_pressure_rankine(phi_eff=30.0)`]\nBased on Rankine (1857) theory, the active lateral earth pressure coefficient is Ka = 0.333 (Kp = 3.00) assuming a frictionless vertical retaining wall with horizontal backfill.",
            rejected="Let me calculate that: Ka = (1 - sin(30)) / (1 + sin(30)) = (1 - 0.5) / (1 + 0.5) = 0.5 / 1.5 = 0.3333333333333333.",
            rationale="AGENTS.md §6: SLM reasons and orchestrates; Groundhog calculates deterministically. Do not reproduce equations in prompt."
        ),

        # --- Rule: Never invent missing soil parameters silently ---
        DPOPreferencePair(
            id="dpo_03_no_silent_invention",
            prompt="Calculate the undrained bearing capacity of a 3m wide footing at 1m depth.",
            chosen="To calculate undrained bearing capacity, please specify the soil's undrained shear strength (su in kPa) and total unit weight (gamma in kN/m³).",
            rejected="Assuming typical clay with su = 50 kPa and unit weight 18 kN/m3, the bearing capacity is 257 kPa.",
            rationale="AGENTS.md §5 & §17: Never silently invent missing soil parameters. Prompt the user for required values."
        ),

        # --- Rule: Never fabricate citations, standards, or DOIs ---
        DPOPreferencePair(
            id="dpo_04_no_hallucinated_citations",
            prompt="What paper introduced the Soil Behavior Type Index Ic?",
            chosen="The Soil Behavior Type Index Ic was formulated by Robertson & Wride (1998) 'Evaluating cyclic liquefaction potential using the cone penetration test' (Canadian Geotechnical Journal, 35(3): 442-459) and subsequently refined in Robertson (2009) 'Interpretation of cone penetration tests — a unified approach'.",
            rejected="The Ic index was introduced by Robertson et al. (2014) in Journal of Geotechnical Computing doi:10.1016/j.geocomp.2014.05.001.",
            rationale="AGENTS.md §11: Never fabricate papers, authors, publication dates, DOIs, or numerical claims."
        )
    ]
    return pairs


def export_dpo_jsonl(filepath: Path) -> int:
    """Exports DPO preference dataset in JSONL format."""
    pairs = build_dpo_preference_dataset()
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, "w", encoding="utf-8") as f:
        for p in pairs:
            record = asdict(p)
            f.write(json.dumps(record) + "\n")
            
    return len(pairs)
