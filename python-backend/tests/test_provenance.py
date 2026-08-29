# Author: Utkarsh Gupta
# License: GPL v3
"""
Automated Test Suite for Geotechnical Calculation Provenance Tracking
and Multi-Tool Agent Chaining.
"""

import pytest
from typing import List, Optional, Dict, Any

from core.geoai.provenance import (
    CalculationProvenance,
    create_calculation_provenance,
    attach_provenance_to_result
)
from core.geoai.tool_metadata import get_tool_metadata
from core.geoai.tool_registry import tool_registry
from core.geoai.model_provider import (
    ModelProvider,
    ChatMessage,
    ToolCall,
    ModelResponse,
    StreamChunk,
    MessageRole
)
from core.geoai.agent import GeoAIAgent, AgentResponse
import core.geoai.tool_definitions


# =====================================================================
# 1. CalculationProvenance Data Structure Tests
# =====================================================================

def test_calculation_provenance_creation():
    inputs = {"phi_eff": 32.0, "wall_angle": 0.0}
    prov = create_calculation_provenance(
        tool_name="calculate_earth_pressure_rankine",
        sanitized_inputs=inputs
    )

    assert prov.tool_name == "calculate_earth_pressure_rankine"
    assert "Rankine" in prov.method
    assert "Eurocode 7" in prov.standard
    assert prov.inputs == inputs
    assert "Ka" in prov.output_units
    assert len(prov.assumptions) > 0
    assert prov.engine.startswith("Groundhog")
    assert prov.timestamp_utc is not None

    data = prov.to_dict()
    assert isinstance(data, dict)
    assert data["tool_name"] == "calculate_earth_pressure_rankine"
    assert data["inputs"] == inputs


def test_calculation_provenance_markdown_format():
    inputs = {"Vs": 250.0, "gamma": 18.0}
    prov = create_calculation_provenance(
        tool_name="calculate_gmax_from_shear_wave_velocity",
        sanitized_inputs=inputs
    )

    md = prov.format_markdown()
    assert "**Method**:" in md
    assert "**Standard / Reference**:" in md
    assert "`Vs`: 250.0" in md
    assert "**Engine**:" in md


def test_tool_metadata_retrieval():
    # Canonical tool metadata
    meta = get_tool_metadata("calculate_earth_pressure_rankine")
    assert "Rankine" in meta["method"]
    assert "EN 1997-1:2004" in meta["standard"]

    meta_pointload = get_tool_metadata("calculate_stresses_point_load")
    assert "Boussinesq" in meta_pointload["method"]

    # Unknown tool fallback
    meta_unknown = get_tool_metadata("unknown_geotech_calc")
    assert "Groundhog" in meta_unknown["method"]
    assert len(meta_unknown["assumptions"]) > 0


# =====================================================================
# 2. Tool Execution Output Provenance Integration
# =====================================================================

def test_tool_invoke_attaches_provenance():
    tool = tool_registry.get_tool("calculate_earth_pressure_rankine")
    assert tool is not None

    result = tool.invoke({"phi_eff": 30.0, "wall_angle": 0.0})
    assert "Ka" in result
    assert "Kp" in result
    assert "_provenance" in result

    prov = result["_provenance"]
    assert prov["tool_name"] == "calculate_earth_pressure_rankine"
    assert "Rankine" in prov["method"]
    assert prov["inputs"]["phi_eff"] == 30.0


def test_attach_provenance_to_result_helper():
    raw = {"sigma_z": 45.2, "sigma_r": 12.1}
    wrapped = attach_provenance_to_result(
        tool_name="calculate_stresses_circular_footing",
        sanitized_inputs={"footing_radius": 2.0, "q": 100.0, "z": 3.0},
        raw_result=raw
    )
    assert wrapped["status"] == "success"
    assert wrapped["result"]["sigma_z"] == 45.2
    assert "Boussinesq" in wrapped["provenance"]["method"]


# =====================================================================
# 3. Multi-Tool Chaining in GeoAIAgent
# =====================================================================

class ChainedMockProvider(ModelProvider):
    """
    Mock provider simulating a 2-step chained calculation:
    Step 1: Calls Gmax tool
    Step 2: Calls Point Load stress tool
    Step 3: Synthesizes final response
    """
    def __init__(self):
        self.call_count = 0

    def is_loaded(self) -> bool:
        return True

    def model_info(self) -> Dict[str, Any]:
        return {"provider": "mock_chained", "name": "Chained Mock"}

    def generate(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.1,
        max_tokens: int = 1024
    ) -> ModelResponse:
        self.call_count += 1
        
        if self.call_count == 1:
            # Round 1: Call Gmax tool
            return ModelResponse(
                content=None,
                tool_calls=[ToolCall(
                    id="call-gmax",
                    function_name="calculate_gmax_from_shear_wave_velocity",
                    arguments={"Vs": 250.0, "gamma": 18.0}
                )],
                finish_reason="tool_calls"
            )
        elif self.call_count == 2:
            # Round 2: Call Pointload stress tool
            return ModelResponse(
                content=None,
                tool_calls=[ToolCall(
                    id="call-pointload",
                    function_name="calculate_stresses_point_load",
                    arguments={"pointload": 500.0, "z": 4.0, "r": 2.0}
                )],
                finish_reason="tool_calls"
            )
        else:
            # Round 3: Synthesize final answer referencing both tools
            return ModelResponse(
                content="Based on Vs = 250 m/s, the small-strain shear modulus Gmax is 114.7 MPa. Under the 500 kN point load at 4m depth, vertical stress increase is 11.2 kPa.",
                tool_calls=None,
                finish_reason="stop"
            )

    def generate_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        resp = self.generate(messages, tools, temperature, max_tokens)
        if resp.tool_calls:
            yield StreamChunk(delta_tool_calls=resp.tool_calls, finish_reason="tool_calls")
        else:
            yield StreamChunk(delta_content=resp.content, finish_reason="stop")


def test_agent_multi_tool_chaining_and_provenance():
    mock_provider = ChainedMockProvider()
    agent = GeoAIAgent(provider=mock_provider, registry=tool_registry)

    response = agent.run("Evaluate soil dynamic modulus and surface point load stress distribution.")
    
    assert response.finish_reason == "complete"
    assert "Gmax" in response.response_text
    assert len(response.tools_used) == 2

    # Verify tool 1
    assert response.tools_used[0]["name"] == "calculate_gmax_from_shear_wave_velocity"
    assert response.tools_used[0]["result"]["status"] == "success"

    # Verify tool 2
    assert response.tools_used[1]["name"] == "calculate_stresses_point_load"
    assert response.tools_used[1]["result"]["status"] == "success"

    # Verify to_dict output contains full chain and provenance
    data = response.to_dict()
    assert len(data["tools_used"]) == 2
    assert len(data["provenance"]) == 2
    assert "Rankine" in data["provenance"][0].get("method", "") or "Elastic Wave" in data["provenance"][0].get("method", "")
