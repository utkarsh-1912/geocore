"""
Core Agent module for GeoCore's GeoAI subsystem.

This module provides the main orchestration loop that connects the SLM
(via ModelProvider) to the registered tools (via GeoAIToolRegistry).
"""

import inspect
import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

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
from .response_guard import (TRUNCATION_NOTE, AnswerStreamCleaner, clean_answer, collapse_repetition,
                             sentence_keys, strip_calculation_records)
from .tool_registry import GeoAIToolRegistry
from .system_prompt import build_system_prompt
from .tool_selector import select_relevant_tools
from .exceptions import GeoAIValidationError
from .argument_grounding import missing_inputs_message, ungrounded_arguments
from .visuals import ImageIds, assign_image_ids, build_visuals, image_manifest
from .turn_trace import CANCELLED, EMPTY_ANSWER, EMPTY_ANSWER_MESSAGE, FAILURES, classify_turn, record_turn

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 3
# Closing instruction for the write-up after successful tool calls. The exact values are already
# shown (deterministic result summary), and small models misquote numbers and units when they
# restate them, so the model only says what the results indicate.
EXPLANATION_INSTRUCTION = ("The results above are already shown to the user with their units. "
                           "In a few sentences, explain what they indicate and any limits of the method. "
                           "Do not restate the numerical values.")
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
    return "[Calculation record] " + json.dumps(record, default=str, ensure_ascii=False)


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


def _history_seed(history: Optional[List[Dict[str, Any]]]) -> List[str]:
    """
    Sentences already shown in prior assistant turns, to seed cross-turn repetition dedup.
    Without this, a model asked to "continue" after a truncated answer tends to restate the
    cut-off sentence verbatim before adding anything new; collapse_repetition/AnswerStreamCleaner
    only dedupe within one generation, so the restatement would otherwise reach the user twice.
    """
    seed: List[str] = []
    for item in (history or [])[-MAX_HISTORY_TURNS:]:
        if isinstance(item, dict) and item.get("role") == "assistant":
            seed.extend(sentence_keys(strip_calculation_records(str(item.get("content") or ""))))
    return seed


def _grounding_text(messages: List[ChatMessage]) -> str:
    """
    Text a tool argument may legitimately come from: the system prompt (project context), the
    user's turns, tool results and earlier [Calculation record]s. Assistant prose is excluded, so
    a number the model itself wrote (e.g. a typical range) cannot ground its own tool call.
    """
    parts = []
    for m in messages:
        text = m.content or ""
        if m.role == MessageRole.ASSISTANT:
            text = "\n".join(line for line in text.splitlines() if line.startswith("[Calculation record]"))
        parts.append(text)
    return "\n".join(parts)


def _result_summary(tools_used: List[Dict[str, Any]]) -> str:
    """Deterministic answer from tool results, used when the model writes no explanation."""
    lines = []
    for t in tools_used:
        wrapper = t.get("result") if isinstance(t.get("result"), dict) else {}
        if wrapper.get("status") == "error":
            lines.append(f"**{t.get('name')}** failed: {wrapper.get('error')}")
            continue
        res = wrapper.get("result", wrapper)
        if not isinstance(res, dict):
            continue
        prov = res.get("_provenance") if isinstance(res.get("_provenance"), dict) else {}
        units = prov.get("output_units") if isinstance(prov.get("output_units"), dict) else {}
        values = []
        for k, v in res.items():
            if k.startswith("_"):
                continue
            unit = units.get(k)
            if isinstance(v, dict) and set(v) == {"image_id", "details"}:
                continue  # an image: drawn by the UI, not a value to read out
            if isinstance(v, dict) and set(v) == {"columns", "n_rows"}:  # a long table summarised for the model
                values.append(f"{k} = table of {v['n_rows']} rows")
                continue
            values.append(f"{k} = {_compact_value(v)}" + (f" {unit}" if unit and unit != "-" else ""))
        lines.append(f"**{t.get('name')}** result: " + ", ".join(values))
    return "\n".join(lines)


_EXPLAIN_REQUEST_RE = re.compile(
    r"\b(explain|why|interpret\w*|what (?:does|do|is|are)|meaning|means?|mean|discuss|compare|comment|"
    r"describe|recommend\w*|suggest\w*|summari[sz]e|implications?|reason|how (?:does|do|should|can))\b",
    re.IGNORECASE)


def _wants_model_explanation(mode: str, user_message: str, tools_used: List[Dict[str, Any]],
                             interpretive_tools: Iterable[str] = ()) -> bool:
    """
    Whether the local model should write prose after the tool calls. A plain "calculate X"
    request whose tools all succeeded is answered from the deterministic result summary;
    failures always go to the model so it can explain them and ask for what is missing, and
    so do results of interpretive tools (e.g. a CPT soil behaviour type), which mean little
    without a sentence on what they indicate.
    """
    if mode == "always":
        return True
    if mode == "never":
        return False
    failed = any((t.get("result") or {}).get("status") != "success" for t in tools_used)
    interpretive = set(interpretive_tools)
    return (failed or any(t.get("name") in interpretive for t in tools_used)
            or bool(_EXPLAIN_REQUEST_RE.search(user_message or "")))


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
            "provenance": provenances,
            "visuals": [v for t in self.tools_used for v in t.get("visuals") or []],
        }
        return result

@dataclass
class AgentStreamEvent:
    type: str
    content: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_result: Optional[Dict[str, Any]] = None
    # Display blocks for the UI only (core.geoai.visuals); never part of the model prompt.
    visuals: Optional[List[Dict[str, Any]]] = None

    def to_sse(self) -> str:
        data = {
            "type": self.type,
            "content": self.content,
            "tool_name": self.tool_name,
            "tool_args": self.tool_args,
            "tool_result": self.tool_result
        }
        if self.visuals:
            data["visuals"] = self.visuals
        return f"data: {json.dumps(data)}\n\n"

def _close_stream(stream: Any) -> None:
    """Close a generator stream early (stops llama.cpp generation); plain iterators are left alone."""
    close = getattr(stream, "close", None)
    if close:
        close()


def _with_truncation_note(text: str, finish_reason: Optional[str], raw: Optional[str] = None) -> str:
    """
    Say so when an answer stopped at the generation cap instead of ending mid-sentence silently.
    A completion that hit the cap because it was looping is not unfinished, so it gets no note.
    """
    if not text or finish_reason != "length":
        return text
    probe = AnswerStreamCleaner()
    probe.feed(raw or "")
    probe.flush()
    return text if probe.looping else text + TRUNCATION_NOTE


class GeoAIAgent:
    def __init__(self, provider: ModelProvider, registry: GeoAIToolRegistry, max_tools: Optional[int] = None,
                 tool_schema_token_budget: Optional[float] = None,
                 domains: Optional[Iterable[str]] = None, role_instructions: Optional[str] = None):
        self._provider = provider
        self._registry = registry
        # Registries that can also hand back what only the UI shows (figures, full tables).
        self._registry_displays = "include_display" in inspect.signature(registry.invoke_tool).parameters
        # A specialist (core.geoai.multi_agent) only sees tools of its domains and a role note.
        self._domains = list(domains) if domains is not None else None
        self._role_instructions = role_instructions
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
        self._explanations = getattr(config, "explanations", "on_request")
        self._max_tools = max_tools
        # Compact model-facing schemas (validation still uses the full schema, see tool_selector).
        self._compact_tool_schemas = bool(getattr(config, "compact_tool_schemas", False))
        # A few Groundhog schemas are ~1k tokens; cap their total so the prompt fits n_ctx.
        self._tool_schema_token_budget = tool_schema_token_budget

    def _build_messages(self, user_message: str, context: Optional[Dict[str, Any]] = None,
                        history: Optional[List[Dict[str, Any]]] = None) -> Tuple[List[ChatMessage], List[dict]]:
        """Build initial message list and select relevant tools for the model."""
        if self._role_instructions:
            context = {**(context or {}), "agent_role": self._role_instructions}
        system_prompt = build_system_prompt(context)
        messages = [make_system_message(system_prompt)]
        messages.extend(history_to_messages(history))
        messages.append(make_user_message(user_message))
        tools_for_model = select_relevant_tools(_tool_selection_query(user_message, history), context,
                                                max_tools=self._max_tools,
                                                max_schema_tokens=self._tool_schema_token_budget,
                                                compact=self._compact_tool_schemas,
                                                domains=self._domains)
        return messages, tools_for_model

    def _execute_tool_call(self, tool_call: ToolCall, context: Optional[Dict[str, Any]] = None,
                           ids: Optional[ImageIds] = None) -> Dict[str, Any]:
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

            if self._registry_displays:
                result = self._registry.invoke_tool(tool_call.function_name, args, include_display=True)
            else:
                result = self._registry.invoke_tool(tool_call.function_name, args)
            # For the UI only: never part of the tool message the model reads or of the saved record.
            display = result.pop("_display", None) if isinstance(result, dict) else None
            if display and display.get("figures") and isinstance(result, dict):
                # The model reads {"image_id", "details"} where the figure was; give each a turn-unique id.
                display["figure_ids"] = {}
                for key in display["figures"]:
                    placeholder = result.get(key)
                    if isinstance(placeholder, dict) and set(placeholder) == {"image_id", "details"}:
                        image_id = ids.next() if ids else key
                        placeholder["image_id"] = image_id
                        display["figure_ids"][key] = image_id
            
            # Record calculation in project context memory if available
            if context and isinstance(result, dict) and "_provenance" in result:
                proj_ctx = context.get('project_context')
                if proj_ctx and hasattr(proj_ctx, 'add_calculation'):
                    proj_ctx.add_calculation(result["_provenance"])

            wrapper = {"status": "success", "tool_name": tool_call.function_name, "result": result}
            if display:
                wrapper["display"] = display
            return wrapper
        except GeoAIValidationError as e:
            return {"status": "error", "tool_name": tool_call.function_name, "error": str(e)}
        except Exception as e:
            return {"status": "error", "tool_name": tool_call.function_name, "error": f"Execution failed: {str(e)}"}

    def _visuals_for(self, tool_call: ToolCall, wrapper: Dict[str, Any], ids: ImageIds) -> List[Dict[str, Any]]:
        """
        Display blocks for one executed call. Charts get the image ids (and descriptions) the model was told
        about; other blocks are unchanged. Built as soon as the tool returns, so they reach the UI (tool_result
        event) before the model starts its interpretation. The display-only data is removed from the wrapper.
        """
        visuals = build_visuals(tool_call.function_name, tool_call.arguments, wrapper)
        wrapper.pop("display", None)
        assign_image_ids(visuals, ids)
        return visuals

    def _interpretive_tools(self, tools_used: List[Dict[str, Any]]) -> List[str]:
        """Names of the used tools whose registry entry is marked interpretive."""
        names = []
        for t in tools_used:
            tool = self._registry.get_tool(t.get("name"))
            if tool is not None and getattr(tool, "interpretive", False):
                names.append(t["name"])
        return names

    def _clarify_invented_arguments(self, tool_calls: List[ToolCall], messages: List[ChatMessage]) -> Optional[str]:
        """
        A clarification when a call carries numeric inputs the user never gave (AGENTS.md §5,
        §17); such a call is not executed. None when every call is grounded.
        """
        grounding = _grounding_text(messages)
        for tc in tool_calls:
            tool = self._registry.get_tool(tc.function_name)
            if tool is None:
                continue  # unknown tools fail in the registry with their own error
            args = {k: v for k, v in (tc.arguments or {}).items() if v is not None}
            invented = ungrounded_arguments(tool.input_model, args, grounding)
            if invented:
                logger.info(f"GeoAI: not running {tc.function_name}; ungrounded inputs {invented}")
                return missing_inputs_message(tc.function_name, tool.input_model, invented)
        return None

    def run(self, user_message: str, context: Optional[Dict[str, Any]] = None,
            history: Optional[List[Dict[str, Any]]] = None) -> AgentResponse:
        self._provider.clear_cancel()
        messages, tools_for_model = self._build_messages(user_message, context, history)
        tools_used = []
        ids = ImageIds()
        seed = _history_seed(history)

        for round_num in range(MAX_TOOL_ROUNDS):
            response = self._provider.generate(
                messages=messages,
                tools=tools_for_model,
                temperature=0.1,
                max_tokens=self._decision_max_tokens if round_num == 0 else self._answer_max_tokens
            )

            if response.finish_reason != 'tool_calls' or not response.tool_calls:
                return AgentResponse(
                    response_text=_with_truncation_note(clean_answer(response.content, tools_used, seed=seed),
                                                        response.finish_reason, response.content),
                    tools_used=tools_used,
                    finish_reason='complete',
                    usage=response.usage
                )
            
            clarification = self._clarify_invented_arguments(response.tool_calls, messages)
            if clarification:
                return AgentResponse(response_text=clarification, tools_used=tools_used,
                                     finish_reason='clarification', usage=response.usage)

            assistant_msg = ChatMessage(role=MessageRole.ASSISTANT, content=response.content, tool_calls=response.tool_calls)
            messages.append(assistant_msg)
            
            for tc in response.tool_calls:
                result = self._execute_tool_call(tc, context=context, ids=ids)
                visuals = self._visuals_for(tc, result, ids)
                tools_used.append({"name": tc.function_name, "arguments": tc.arguments, "result": result,
                                   "visuals": visuals})
                
                tool_result_msg = make_tool_result_message(tc.id, tc.function_name, result)
                messages.append(tool_result_msg)
            manifest = image_manifest([v for t in tools_used for v in t.get("visuals") or []])
            if manifest:
                messages.append(make_user_message(manifest))
            
            if round_num == MAX_TOOL_ROUNDS - 2:
                tools_for_model = None
        
        messages.append(make_user_message("Please summarize the results from the tools used."))
        final = self._provider.generate(messages=messages, tools=None, max_tokens=self._answer_max_tokens)
        return AgentResponse(
            response_text=_with_truncation_note(clean_answer(final.content, tools_used, seed=seed),
                                                final.finish_reason, final.content)
            or "Maximum tool rounds reached.",
            tools_used=tools_used,
            finish_reason='max_rounds',
            usage=final.usage
        )

    def run_stream(self, user_message: str, context: Optional[Dict[str, Any]] = None,
                   history: Optional[List[Dict[str, Any]]] = None) -> Iterator[AgentStreamEvent]:
        """
        One streamed turn with reliability guarantees: a turn that ends without any answer text
        gets an explicit message instead of a blank bubble, and every turn's outcome is traced
        (turn_trace) so chat failures can be counted by cause.
        """
        started = time.monotonic()
        events: List[AgentStreamEvent] = []
        outcome: Optional[str] = None
        try:
            for event in self._run_stream(user_message, context, history):
                if event.type == 'done':
                    outcome = classify_turn(user_message, events)  # before any notice is added
                    if outcome == EMPTY_ANSWER:
                        notice = AgentStreamEvent(type='token', content=EMPTY_ANSWER_MESSAGE)
                        events.append(notice)
                        yield notice
                events.append(event)
                yield event
        except GeneratorExit:  # the client went away mid-turn
            record_turn(CANCELLED, user_message, events, started, self._provider.model_info())
            raise
        except Exception as e:
            record_turn(classify_turn(user_message, events, e), user_message, events, started,
                        self._provider.model_info(), e)
            raise
        outcome = outcome or classify_turn(user_message, events)
        if outcome in FAILURES:
            logger.warning(f"GeoAI turn outcome: {outcome}")
        record_turn(outcome, user_message, events, started, self._provider.model_info())

    def _run_stream(self, user_message: str, context: Optional[Dict[str, Any]] = None,
                    history: Optional[List[Dict[str, Any]]] = None) -> Iterator[AgentStreamEvent]:
        yield AgentStreamEvent(type='stage', content='checking_tools')  # tool retrieval + context
        messages, tools_for_model = self._build_messages(user_message, context, history)
        tools_used = []
        ids = ImageIds()
        seed = _history_seed(history)

        for round_num in range(MAX_TOOL_ROUNDS):
            # The first call on a cold provider pays model load time (seconds on a laptop CPU);
            # tell the UI which it's waiting on instead of a generic spinner.
            stage = 'loading_model' if round_num == 0 and not self._provider.is_loaded() else 'thinking'
            yield AgentStreamEvent(type='stage', content=stage)
            if round_num == 0:
                # Waits for a previous call to release the model; the stage is already shown.
                self._provider.clear_cancel()
            stream = self._provider.generate_stream(
                messages=messages,
                tools=tools_for_model,
                temperature=0.1,
                max_tokens=self._decision_max_tokens
            )

            full_content = ""
            tool_calls = []
            finish_reason = None
            # A direct answer (no tool call) gets the same guards as the explanation round.
            cleaner = AnswerStreamCleaner(tools_used, seed=seed)

            for chunk in stream:
                if chunk.delta_content:
                    full_content += chunk.delta_content
                    text = cleaner.feed(chunk.delta_content)
                    if text:
                        yield AgentStreamEvent(type='token', content=text)
                if chunk.delta_tool_calls:
                    tool_calls.extend(chunk.delta_tool_calls)
                finish_reason = chunk.finish_reason or finish_reason
                if cleaner.looping and not tool_calls:
                    _close_stream(stream)  # stop generating: the rest of a loop would be dropped anyway
                    break

            if not tool_calls:
                text = cleaner.flush()
                if finish_reason == "length" and not cleaner.looping:
                    text += TRUNCATION_NOTE
                if text:
                    yield AgentStreamEvent(type='token', content=text)
                yield AgentStreamEvent(type='done')
                return
                
            clarification = self._clarify_invented_arguments(tool_calls, messages)
            if clarification:
                yield AgentStreamEvent(type='token', content=clarification)
                yield AgentStreamEvent(type='done')
                return

            assistant_msg = ChatMessage(role=MessageRole.ASSISTANT, content=full_content, tool_calls=tool_calls)
            messages.append(assistant_msg)
            
            for tc in tool_calls:
                yield AgentStreamEvent(type='tool_start', tool_name=tc.function_name, tool_args=tc.arguments)
                result = self._execute_tool_call(tc, context=context, ids=ids)
                visuals = self._visuals_for(tc, result, ids)
                tools_used.append({"name": tc.function_name, "arguments": tc.arguments, "result": result,
                                   "visuals": visuals})
                yield AgentStreamEvent(type='tool_result', tool_name=tc.function_name, tool_result=result,
                                       visuals=visuals)
                
                tool_result_msg = make_tool_result_message(tc.id, tc.function_name, result)
                messages.append(tool_result_msg)
                
            if not _wants_model_explanation(self._explanations, user_message, tools_used,
                                            self._interpretive_tools(tools_used)):
                yield AgentStreamEvent(type='token', content=_result_summary(tools_used))
                yield AgentStreamEvent(type='done')
                return

            # Explanation round: stream the prose, released sentence by sentence through the
            # same guards clean_answer applies (repeats, echoed records, result units). The
            # offered tools stay in the prompt so the provider can reuse its prompt cache.
            yield AgentStreamEvent(type='stage', content='writing_answer')
            yield from self._stream_answer(messages, tools_used, tools_for_model, seed=seed)
            yield AgentStreamEvent(type='done')
            return

        messages.append(make_user_message("Please summarize the results from the tools used."))
        final = self._provider.generate(messages=messages, tools=None, max_tokens=self._answer_max_tokens)
        yield AgentStreamEvent(type='token', content=_with_truncation_note(
                                                   clean_answer(final.content, tools_used, seed=seed),
                                                   final.finish_reason, final.content)
                               or "Maximum tool rounds reached.")
        yield AgentStreamEvent(type='done')

    def _stream_answer(self, messages: List[ChatMessage], tools_used: List[Dict[str, Any]],
                       tools_for_model: Optional[List[dict]] = None,
                       seed: Iterable[str] = ()) -> Iterator[AgentStreamEvent]:
        # The exact results first, from the tools; the model's prose follows.
        yield AgentStreamEvent(type='token', content=_result_summary(tools_used) + "\n\n")
        if all((t.get("result") or {}).get("status") == "success" for t in tools_used):
            manifest = image_manifest([v for t in tools_used for v in t.get("visuals") or []])
            messages = messages + [make_user_message(EXPLANATION_INSTRUCTION + ("\n\n" + manifest if manifest else ""))]
        cleaner = AnswerStreamCleaner(tools_used, seed=seed)
        finish_reason = None
        stream = self._provider.generate_answer_stream(messages=messages, tools=tools_for_model,
                                                       temperature=0.1, max_tokens=self._answer_max_tokens)
        for chunk in stream:
            text = cleaner.feed(chunk.delta_content)
            if text:
                yield AgentStreamEvent(type='token', content=text)
            finish_reason = chunk.finish_reason or finish_reason
            if cleaner.looping:
                _close_stream(stream)  # stop generating: the rest of a loop would be dropped anyway
                break
        text = cleaner.flush()
        if text and finish_reason == "length" and not cleaner.looping:
            text += TRUNCATION_NOTE
        if text:
            yield AgentStreamEvent(type='token', content=text)
