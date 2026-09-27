import json

from core.geoai.agent import GeoAIAgent
from core.geoai.heuristic_provider import HeuristicProvider
from core.geoai.model_config import GeoAIModelConfig, load_config
from core.geoai.tool_registry import tool_registry


def test_agent_offers_at_most_configured_tools():
    agent = GeoAIAgent(HeuristicProvider(), tool_registry, max_tools=3)
    _, tools = agent._build_messages("Calculate bearing capacity, settlement, earth pressure and Gmax", None)
    assert 0 < len(tools) <= 3


def test_default_tool_budget_fits_context_window():
    cfg = GeoAIModelConfig()
    agent = GeoAIAgent(HeuristicProvider(), tool_registry, max_tools=cfg.max_tools)
    _, tools = agent._build_messages("Calculate the settlement and bearing capacity of a footing on sand", None)
    approx_tokens = sum(len(json.dumps(t)) for t in tools) / 3.5
    assert approx_tokens < cfg.n_ctx / 2


def test_max_tools_env_override(monkeypatch):
    monkeypatch.setenv("GEOAI_MAX_TOOLS", "7")
    assert load_config().max_tools == 7
