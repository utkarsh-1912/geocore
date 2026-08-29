"""
GeoAI Model Provider Interface
Abstract base class for all LLM providers in GeoAI. Ensures model-agnosticism.

Author: Utkarsh Gupta
License: GPL v3
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Iterator, List, Optional
import json


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class ToolCall:
    id: str
    function_name: str
    arguments: Dict[str, Any]


@dataclass
class ChatMessage:
    role: MessageRole
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Outputs standard OpenAI chat format."""
        result: Dict[str, Any] = {"role": self.role.value}
        
        if self.content is not None:
            result["content"] = self.content
            
        if self.tool_calls is not None:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function_name,
                        "arguments": json.dumps(tc.arguments)
                    }
                }
                for tc in self.tool_calls
            ]
            
        if self.tool_call_id is not None:
            result["tool_call_id"] = self.tool_call_id
            
        if self.name is not None:
            result["name"] = self.name
            
        return result


@dataclass
class ModelResponse:
    content: Optional[str]
    tool_calls: Optional[List[ToolCall]]
    finish_reason: str
    usage: Optional[Dict[str, int]] = None


@dataclass
class StreamChunk:
    delta_content: Optional[str] = None
    delta_tool_calls: Optional[List[ToolCall]] = None
    finish_reason: Optional[str] = None


class ModelProvider(ABC):
    @abstractmethod
    def generate(
        self, 
        messages: List[ChatMessage], 
        tools: Optional[List[dict]] = None, 
        temperature: float = 0.1, 
        max_tokens: int = 1024
    ) -> ModelResponse:
        """Generate a response from the model."""
        pass
    
    @abstractmethod
    def generate_stream(
        self, 
        messages: List[ChatMessage], 
        tools: Optional[List[dict]] = None, 
        temperature: float = 0.1, 
        max_tokens: int = 1024
    ) -> Iterator[StreamChunk]:
        """Generate a streaming response from the model."""
        pass
    
    @abstractmethod
    def is_loaded(self) -> bool:
        """Whether the model is currently loaded in memory."""
        pass
    
    @abstractmethod
    def model_info(self) -> Dict[str, Any]:
        """Return metadata about the loaded model."""
        pass


def make_user_message(text: str) -> ChatMessage:
    return ChatMessage(role=MessageRole.USER, content=text)


def make_system_message(text: str) -> ChatMessage:
    return ChatMessage(role=MessageRole.SYSTEM, content=text)


def make_tool_result_message(tool_call_id: str, tool_name: str, result: Any) -> ChatMessage:
    if isinstance(result, str):
        content_str = result
    else:
        try:
            content_str = json.dumps(result)
        except Exception:
            content_str = str(result)
            
    return ChatMessage(
        role=MessageRole.TOOL,
        content=content_str,
        tool_call_id=tool_call_id,
        name=tool_name
    )
