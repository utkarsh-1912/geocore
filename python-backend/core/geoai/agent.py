"""
Core Agent module for GeoCore's GeoAI subsystem.

This module provides the main orchestration loop that connects the SLM
(via ModelProvider) to the registered tools (via GeoAIToolRegistry).
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional, Tuple

from .model_provider import (
    ModelProvider,
    ChatMessage,
    ToolCall,
    ModelResponse,
    StreamChunk,
    MessageRole,
    make_tool_result_message,
    make_user_message,
    make_system_message
)
from .tool_registry import GeoAIToolRegistry
from .system_prompt import build_system_prompt
from .tool_selector import select_relevant_tools
from .exceptions import GeoAIValidationError

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 3

@dataclass
class AgentResponse:
    response_text: str
    tools_used: List[Dict[str, Any]]
    finish_reason: str
    usage: Optional[Dict[str, int]] = None

    def to_dict(self) -> dict:
        executed_tool = self.tools_used[0]["name"] if self.tools_used else None
        first_tool_result = self.tools_used[0]["result"] if self.tools_used else None
        
        # Extract provenances
        provenances = []
        for t in self.tools_used:
            res = t.get("result")
            if isinstance(res, dict):
                p = res.get("_provenance") or (res.get("result", {}).get("_provenance") if isinstance(res.get("result"), dict) else None)
                if p:
                    provenances.append(p)

        result = {
            "response": self.response_text,
            "executed_tool": executed_tool,
            "candidate_tools": [t["name"] for t in self.tools_used],
            "parameters_extracted": self.tools_used[0]["arguments"] if self.tools_used else None,
            "results": first_tool_result,
            "tools_used": self.tools_used,
            "provenance": provenances
        }
        return result

@dataclass
class AgentStreamEvent:
    type: str
    content: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_result: Optional[Dict[str, Any]] = None

    def to_sse(self) -> str:
        data = {
            "type": self.type,
            "content": self.content,
            "tool_name": self.tool_name,
            "tool_args": self.tool_args,
            "tool_result": self.tool_result
        }
        return f"data: {json.dumps(data)}\n\n"

class GeoAIAgent:
    def __init__(self, provider: ModelProvider, registry: GeoAIToolRegistry):
        self._provider = provider
        self._registry = registry

    def _build_messages(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> Tuple[List[ChatMessage], List[dict]]:
        """Build initial message list and select relevant tools for the model."""
        system_prompt = build_system_prompt(context)
        messages = [
            make_system_message(system_prompt),
            make_user_message(user_message)
        ]
        tools_for_model = select_relevant_tools(user_message, context)
        return messages, tools_for_model

    def _execute_tool_call(self, tool_call: ToolCall, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            args = dict(tool_call.arguments) if tool_call.arguments else {}
            # If project context is present, auto-resolve any missing (None) arguments
            if context:
                proj_ctx = context.get('project_context')
                if proj_ctx and hasattr(proj_ctx, 'get_profile'):
                    from core.geoai.context_resolver import ContextResolver
                    resolver = ContextResolver(proj_ctx)
                    args = resolver.fill_missing_parameters(args)

            result = self._registry.invoke_tool(tool_call.function_name, args)
            
            # Record calculation in project context memory if available
            if context and isinstance(result, dict) and "_provenance" in result:
                proj_ctx = context.get('project_context')
                if proj_ctx and hasattr(proj_ctx, 'add_calculation'):
                    proj_ctx.add_calculation(result["_provenance"])

            return {"status": "success", "tool_name": tool_call.function_name, "result": result}
        except GeoAIValidationError as e:
            return {"status": "error", "tool_name": tool_call.function_name, "error": str(e)}
        except Exception as e:
            return {"status": "error", "tool_name": tool_call.function_name, "error": f"Execution failed: {str(e)}"}

    def run(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        messages, tools_for_model = self._build_messages(user_message, context)
        tools_used = []
        
        for round_num in range(MAX_TOOL_ROUNDS):
            response = self._provider.generate(
                messages=messages,
                tools=tools_for_model,
                temperature=0.1,
                max_tokens=1024
            )
            
            if response.finish_reason != 'tool_calls' or not response.tool_calls:
                return AgentResponse(
                    response_text=response.content or "",
                    tools_used=tools_used,
                    finish_reason='complete',
                    usage=response.usage
                )
            
            assistant_msg = ChatMessage(role=MessageRole.ASSISTANT, content=response.content, tool_calls=response.tool_calls)
            messages.append(assistant_msg)
            
            for tc in response.tool_calls:
                result = self._execute_tool_call(tc, context=context)
                tools_used.append({"name": tc.function_name, "arguments": tc.arguments, "result": result})
                
                tool_result_msg = make_tool_result_message(tc.id, tc.function_name, result)
                messages.append(tool_result_msg)
            
            if round_num == MAX_TOOL_ROUNDS - 2:
                tools_for_model = None
        
        messages.append(make_user_message("Please summarize the results from the tools used."))
        final = self._provider.generate(messages=messages, tools=None)
        return AgentResponse(
            response_text=final.content or "Maximum tool rounds reached.",
            tools_used=tools_used,
            finish_reason='max_rounds',
            usage=final.usage
        )

    def run_stream(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> Iterator[AgentStreamEvent]:
        messages, tools_for_model = self._build_messages(user_message, context)
        tools_used = []
        
        for round_num in range(MAX_TOOL_ROUNDS):
            stream = self._provider.generate_stream(
                messages=messages,
                tools=tools_for_model,
                temperature=0.1,
                max_tokens=1024
            )
            
            full_content = ""
            tool_calls = []
            
            for chunk in stream:
                if chunk.delta_content:
                    full_content += chunk.delta_content
                    yield AgentStreamEvent(type='token', content=chunk.delta_content)
                if chunk.delta_tool_calls:
                    tool_calls.extend(chunk.delta_tool_calls)
            
            if not tool_calls:
                yield AgentStreamEvent(type='done')
                return
                
            assistant_msg = ChatMessage(role=MessageRole.ASSISTANT, content=full_content, tool_calls=tool_calls)
            messages.append(assistant_msg)
            
            for tc in tool_calls:
                yield AgentStreamEvent(type='tool_start', tool_name=tc.function_name, tool_args=tc.arguments)
                result = self._execute_tool_call(tc, context=context)
                tools_used.append({"name": tc.function_name, "arguments": tc.arguments, "result": result})
                yield AgentStreamEvent(type='tool_result', tool_name=tc.function_name, tool_result=result)
                
                tool_result_msg = make_tool_result_message(tc.id, tc.function_name, result)
                messages.append(tool_result_msg)
                
            # For explanation round after tools, use non-streaming generate() and yield full text as a single token event
            final = self._provider.generate(messages=messages, tools=None)
            yield AgentStreamEvent(type='token', content=final.content or "")
            yield AgentStreamEvent(type='done')
            return
            
        messages.append(make_user_message("Please summarize the results from the tools used."))
        final = self._provider.generate(messages=messages, tools=None)
        yield AgentStreamEvent(type='token', content=final.content or "Maximum tool rounds reached.")
        yield AgentStreamEvent(type='done')
