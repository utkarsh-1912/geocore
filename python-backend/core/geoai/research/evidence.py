# Author: Utkarsh Gupta
# License: GPL v3
"""
Structured Evidence Synthesis & Provenance Citation Engine.
Implements the 6-tier evidence grounding taxonomy required by AGENTS.md §12:
1. [Project Evidence]: In-situ measurements, sounding data, lab tests from the active project.
2. [Calculation Evidence]: Deterministic numerical outputs from Groundhog tools.
3. [Literature Evidence]: Published papers, research findings, and technical notes.
4. [Standards / Guidance]: Official design codes (Eurocode 7, API RP 2GEO, ASTM, ISO).
5. [Model Interpretation]: Qualitative reasoning and engineering synthesis.
6. [Assumption]: Stated engineering boundary conditions or adopted parameters.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict


class EvidenceTier(str, Enum):
    PROJECT_EVIDENCE = "Project Evidence"
    CALCULATION_EVIDENCE = "Calculation Evidence"
    LITERATURE_EVIDENCE = "Literature Evidence"
    STANDARDS_GUIDANCE = "Standards / Guidance"
    MODEL_INTERPRETATION = "Model Interpretation"
    ASSUMPTION = "Assumption"


@dataclass
class EvidenceItem:
    tier: EvidenceTier
    source: str
    content: str
    details: Optional[Dict[str, Any]] = None

    def format_badge(self) -> str:
        """Renders the evidence block with standard markdown labeling."""
        lines = [f"**[{self.tier.value}]** — *Source: {self.source}*"]
        lines.append(f"> {self.content}")
        return "\n".join(lines)


@dataclass
class ResearchGroundingReport:
    """
    Complete evidence grounding container combining multi-source engineering evidence.
    """
    topic: str
    items: List[EvidenceItem] = field(default_factory=list)

    def add_project_evidence(self, source: str, content: str, details: Optional[Dict[str, Any]] = None) -> None:
        self.items.append(EvidenceItem(EvidenceTier.PROJECT_EVIDENCE, source, content, details))

    def add_calculation_evidence(self, tool_name: str, method: str, result_summary: str, details: Optional[Dict[str, Any]] = None) -> None:
        self.items.append(EvidenceItem(
            EvidenceTier.CALCULATION_EVIDENCE,
            f"Groundhog `{tool_name}` ({method})",
            result_summary,
            details
        ))

    def add_literature_evidence(self, citation: str, excerpt: str) -> None:
        self.items.append(EvidenceItem(EvidenceTier.LITERATURE_EVIDENCE, citation, excerpt))

    def add_standard_guidance(self, code_reference: str, clause: str) -> None:
        self.items.append(EvidenceItem(EvidenceTier.STANDARDS_GUIDANCE, code_reference, clause))

    def add_assumption(self, description: str) -> None:
        self.items.append(EvidenceItem(EvidenceTier.ASSUMPTION, "Engineering Boundary Condition", description))

    def to_markdown(self) -> str:
        """Formats complete structured evidence report in clean Markdown."""
        lines = [f"### Evidence Grounding Report: {self.topic}"]
        
        # Group items by tier
        grouped: Dict[EvidenceTier, List[EvidenceItem]] = {}
        for item in self.items:
            grouped.setdefault(item.tier, []).append(item)

        for tier in EvidenceTier:
            if tier in grouped:
                lines.append(f"\n#### {tier.value}")
                for it in grouped[tier]:
                    lines.append(f"- **{it.source}**: {it.content}")

        return "\n".join(lines)
