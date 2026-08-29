"""
GeoAI Heuristic Engine Provider
Wraps the LocalGemmaEngine keyword-matching logic as a ModelProvider-compatible fallback.

Author: Utkarsh Gupta
License: GPL v3
"""
from typing import Any, Dict, Iterator, List, Optional
from core.geoai.model_provider import (
    ModelProvider,
    ModelResponse,
    StreamChunk,
    ChatMessage,
    ToolCall,
    MessageRole
)
from core.geoai.gemma_engine import LocalGemmaEngine


class HeuristicProvider(ModelProvider):
    """
    ModelProvider adapter for the LocalGemmaEngine.
    Delegates to the engine's rule-based keyword matching and regex extraction.
    """
    
    def __init__(self):
        self._engine = LocalGemmaEngine()

    def is_loaded(self) -> bool:
        """Always loaded as it uses in-memory regex and rules."""
        return True

    def model_info(self) -> Dict[str, Any]:
        """Return metadata about the heuristic engine."""
        return {
            "provider": "heuristic",
            "name": "GeoAI Heuristic Engine",
            "description": "Rule-based keyword matching and regex parameter extraction"
        }

    def generate(
        self, 
        messages: List[ChatMessage], 
        tools: Optional[List[dict]] = None, 
        temperature: float = 0.1, 
        max_tokens: int = 1024
    ) -> ModelResponse:
        """
        Extract intent from the last user message and route to a tool via heuristics.
        """
        # Extract the last user message
        user_text = ""
        for msg in reversed(messages):
            if msg.role == MessageRole.USER and msg.content:
                user_text = msg.content
                break

        if not user_text:
            return ModelResponse(
                content="I couldn't identify a matching geotechnical calculation...",
                tool_calls=None,
                finish_reason="stop",
                usage=None
            )

        candidate_tools = self._engine.find_best_tools(user_text)
        
        if candidate_tools:
            best_tool = candidate_tools[0]['name']
            extracted_args = self._engine.extract_parameters_from_text(user_text, best_tool)
            return ModelResponse(
                content=None,
                tool_calls=[ToolCall(id="heuristic-1", function_name=best_tool, arguments=extracted_args)],
                finish_reason="tool_calls",
                usage=None
            )
        else:
            return ModelResponse(
                content="I couldn't identify a matching geotechnical calculation...",
                tool_calls=None,
                finish_reason="stop",
                usage=None
            )

    def generate_stream(
        self, 
        messages: List[ChatMessage], 
        tools: Optional[List[dict]] = None, 
        temperature: float = 0.1, 
        max_tokens: int = 1024
    ) -> Iterator[StreamChunk]:
        """
        Generate a streaming response by delegating to generate() and yielding once.
        """
        result = self.generate(messages, tools, temperature, max_tokens)
        
        if result.tool_calls:
            yield StreamChunk(
                delta_content=None,
                delta_tool_calls=result.tool_calls,
                finish_reason="tool_calls"
            )
        else:
            yield StreamChunk(
                delta_content=result.content,
                delta_tool_calls=None,
                finish_reason="stop"
            )
