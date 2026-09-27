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
from .response_guard import AnswerStreamCleaner, clean_answer, collapse_repetition
from .tool_registry import GeoAIToolRegistry
from .system_prompt import build_system_prompt
from .tool_selector import select_relevant_tools
from .exceptions import GeoAIValidationError

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 3
# The post-tool explanation only needs a few paragraphs; a tight cap bounds degenerate loops.
EXPLANATION_MAX_TOKENS = 512
# Prior conversation turns replayed to the model (small models need a short context).
MAX_HISTORY_TURNS = 6
MAX_HISTORY_CHARS = 600
# Share of the model context window the offered tool schemas may occupy (approximate tokens).
TOOL_SCHEMA_BUDGET_FRACTION = 0.45


def _compact_value(v: Any) -> Any:
    if isinstance(v, float):
        return float(f"{v:.4g}")
    return v


def _calculation_record(tool: Dict[str, Any]) -> Optional[str]:
    """One-line deterministic record of a previous tool call, for follow-up questions."""
    name = tool.get("name")
    if not name:
        return None
    wrapper = tool.get("result") if isinstance(tool.get("result"), dict) else {}
    record: Dict[str, Any] = {"tool": name, "inputs": tool.get("arguments") or {}}
    if wrapper.get("status") == "error":
        record["error"] = wrapper.get("error")
    else:
        res = wrapper.get("result", wrapper)
        if isinstance(res, dict):
            record["results"] = {k: _compact_value(v) for k, v in res.items() if not k.startswith("_")}
            prov = res.get("_provenance") if isinstance(res.get("_provenance"), dict) else {}
            if prov.get("output_units"):
                record["output_units"] = prov["output_units"]
            if prov.get("method"):
                record["method"] = prov["method"]
    return "[Calculation record] " + json.dumps(record, default=str)


def history_to_messages(history: Optional[List[Dict[str, Any]]]) -> List[ChatMessage]:
    """
    Convert client-supplied prior turns into chat messages.

    Each item: {"role": "user"|"assistant", "content": str, "tool": {"name", "arguments", "result"}?}.
    Only the last MAX_HISTORY_TURNS items are kept and long texts are truncated; previous tool
    results are replayed as a compact calculation record rather than raw tool messages.
    """
    messages: List[ChatMessage] = []
    for item in (history or [])[-MAX_HISTORY_TURNS:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        text = collapse_repetition(str(item.get("content") or ""))
        if len(text) > MAX_HISTORY_CHARS:
            text = text[:MAX_HISTORY_CHARS].rstrip() + " ..."
        if role == "user":
            if text:
                messages.append(make_user_message(text))
        elif role == "assistant":
            tool = item.get("tool")
            record = _calculation_record(tool) if isinstance(tool, dict) else None
            content = "\n".join(p for p in (text, record) if p)
            if content:
                messages.append(ChatMessage(role=MessageRole.ASSISTANT, content=content))
    return messages


def _tool_selection_query(user_message: str, history: Optional[List[Dict[str, Any]]]) -> str:
    """Follow-ups ("explain the calculation") carry no keywords; borrow the last user turn's."""
    for item in reversed(history or []):
        if isinstance(item, dict) and item.get("role") == "user" and item.get("content"):
            return f"{user_message} {item['content']}"
    return user_message

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
    def __init__(self, provider: ModelProvider, registry: GeoAIToolRegistry, max_tools: Optional[int] = None,
                 tool_schema_token_budget: Optional[float] = None):
        self._provider = provider
        self._registry = registry
        from core.geoai.model_config import load_config
        config = load_config()
        if max_tools is None:
            max_tools = config.max_tools
        if tool_schema_token_budget is None:
            tool_schema_token_budget = TOOL_SCHEMA_BUDGET_FRACTION * config.n_ctx
        # Generation caps: the tool-selection turn (a call or a clarification) vs the answer
        # written after tool results. They bound runaway generations (p95 latency).
        self._decision_max_tokens = config.decision_max_tokens
        self._answer_max_tokens = config.answer_max_tokens
        self._max_tools = max_tools
        # A few Groundhog schemas are ~1k tokens; cap their total so the prompt fits n_ctx.
        self._tool_schema_token_budget = tool_schema_token_budget

    def _build_messages(self, user_message: str, context: Optional[Dict[str, Any]] = None,
                        history: Optional[List[Dict[str, Any]]] = None) -> Tuple[List[ChatMessage], List[dict]]:
        """Build initial message list and select relevant tools for the model."""
        system_prompt = build_system_prompt(context)
        messages = [make_system_message(system_prompt)]
        messages.extend(history_to_messages(history))
        messages.append(make_user_message(user_message))
        tools_for_model = select_relevant_tools(_tool_selection_query(user_message, history), context,
                                                max_tools=self._max_tools,
                                                max_schema_tokens=self._tool_schema_token_budget)
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
            # Models emit `"u2_kpa": null` for optional inputs they don't have; omit them so the
            # tool's own defaults apply instead of failing validation.
            args = {k: v for k, v in args.items() if v is not None}

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

    def run(self, user_message: str, context: Optional[Dict[str, Any]] = None,
            history: Optional[List[Dict[str, Any]]] = None) -> AgentResponse:
        messages, tools_for_model = self._build_messages(user_message, context, history)
        tools_used = []
        
        for round_num in range(MAX_TOOL_ROUNDS):
            response = self._provider.generate(
                messages=messages,
                tools=tools_for_model,
                temperature=0.1,
                max_tokens=self._decision_max_tokens if round_num == 0 else self._answer_max_tokens
            )
            
            if response.finish_reason != 'tool_calls' or not response.tool_calls:
                return AgentResponse(
                    response_text=clean_answer(response.content, tools_used),
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
        final = self._provider.generate(messages=messages, tools=None, max_tokens=self._answer_max_tokens)
        return AgentResponse(
            response_text=clean_answer(final.content, tools_used) or "Maximum tool rounds reached.",
            tools_used=tools_used,
            finish_reason='max_rounds',
            usage=final.usage
        )

    def run_stream(self, user_message: str, context: Optional[Dict[str, Any]] = None,
                   history: Optional[List[Dict[str, Any]]] = None) -> Iterator[AgentStreamEvent]:
        messages, tools_for_model = self._build_messages(user_message, context, history)
        tools_used = []
        
        for round_num in range(MAX_TOOL_ROUNDS):
            stream = self._provider.generate_stream(
                messages=messages,
                tools=tools_for_model,
                temperature=0.1,
                max_tokens=self._decision_max_tokens
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
                
            # Explanation round: stream the prose, released sentence by sentence through the
            # same guards clean_answer applies (repeats, echoed records, result units).
            yield from self._stream_answer(messages, tools_used)
            yield AgentStreamEvent(type='done')
            return

        messages.append(make_user_message("Please summarize the results from the tools used."))
        final = self._provider.generate(messages=messages, tools=None, max_tokens=self._answer_max_tokens)
        yield AgentStreamEvent(type='token', content=clean_answer(final.content, tools_used) or "Maximum tool rounds reached.")
        yield AgentStreamEvent(type='done')

    def _stream_answer(self, messages: List[ChatMessage], tools_used: List[Dict[str, Any]]) -> Iterator[AgentStreamEvent]:
        cleaner = AnswerStreamCleaner(tools_used)
        for chunk in self._provider.generate_stream(messages=messages, tools=None, temperature=0.1,
                                                    max_tokens=self._answer_max_tokens):
            text = cleaner.feed(chunk.delta_content)
            if text:
                yield AgentStreamEvent(type='token', content=text)
        text = cleaner.flush()
        if text:
            yield AgentStreamEvent(type='token', content=text)
