# Author: Utkarsh Gupta
# License: GPL v3
"""
Calculation Provenance Tracking Module.
Provides structured metadata capturing method citations, reference standards,
sanitized inputs, output units, UTC execution timestamps, and execution engines.
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import json

from core.geoai.tool_metadata import get_tool_metadata


@dataclass
class CalculationProvenance:
    """
    Structured provenance record for an authoritative engineering calculation.
    """
    tool_name: str
    method: str
    standard: str
    inputs: Dict[str, Any]
    output_units: Dict[str, str] = field(default_factory=dict)
    assumptions: List[str] = field(default_factory=list)
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    engine: str = "Groundhog Geotechnical Engine (Deterministic)"

    def to_dict(self) -> Dict[str, Any]:
        """Convert provenance object to standard JSON-serializable dictionary."""
        return asdict(self)

    def format_markdown(self) -> str:
        """Render provenance record into clean markdown for engineering documentation."""
        lines = [
            f"**Method**: {self.method}",
            f"**Standard / Reference**: {self.standard}",
            f"**Engine**: {self.engine}",
            f"**Executed (UTC)**: `{self.timestamp_utc}`"
        ]
        if self.assumptions:
            lines.append("\n**Key Assumptions & Applicability**:")
            for a in self.assumptions:
                lines.append(f"- {a}")
        if self.inputs:
            lines.append("\n**Adopted Parameters**:")
            for k, v in self.inputs.items():
                lines.append(f"- `{k}`: {v}")
        return "\n".join(lines)


def create_calculation_provenance(
    tool_name: str,
    sanitized_inputs: Dict[str, Any],
    custom_method: Optional[str] = None,
    custom_standard: Optional[str] = None,
    custom_assumptions: Optional[List[str]] = None,
    custom_output_units: Optional[Dict[str, str]] = None
) -> CalculationProvenance:
    """
    Constructs a CalculationProvenance instance by combining tool metadata catalog
    defaults with any execution-specific overrides.
    """
    meta = get_tool_metadata(tool_name)

    method = custom_method or meta.get("method", f"Groundhog Calculation ({tool_name})")
    standard = custom_standard or meta.get("standard", "Standard Geotechnical Practice")
    assumptions = custom_assumptions if custom_assumptions is not None else meta.get("assumptions", [])
    output_units = custom_output_units if custom_output_units is not None else meta.get("output_units", {})

    return CalculationProvenance(
        tool_name=tool_name,
        method=method,
        standard=standard,
        inputs=sanitized_inputs,
        output_units=output_units,
        assumptions=assumptions
    )


def attach_provenance_to_result(
    tool_name: str,
    sanitized_inputs: Dict[str, Any],
    raw_result: Any
) -> Dict[str, Any]:
    """
    Wraps raw tool execution result with full provenance metadata.
    """
    provenance = create_calculation_provenance(tool_name, sanitized_inputs)
    
    if isinstance(raw_result, dict):
        result_data = dict(raw_result)
    else:
        result_data = {"result": raw_result}

    return {
        "status": "success",
        "tool_name": tool_name,
        "result": result_data,
        "provenance": provenance.to_dict()
    }
