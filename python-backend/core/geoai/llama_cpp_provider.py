"""
GeoAI LLaMA C++ Provider
Concrete implementation of ModelProvider for local GGUF models via llama-cpp-python.

Author: Utkarsh Gupta
License: GPL v3
"""
import functools
import json
import logging
import re
import threading
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from .model_provider import (
    ChatMessage,
    MessageRole,
    ModelProvider,
    ModelResponse,
    StreamChunk,
    ToolCall
)
from .model_config import CHAT_FORMATS, GeoAIModelConfig, resolve_thread_counts
from .lora_adapter import AdapterCheck, check_adapter_compatibility

logger = logging.getLogger(__name__)

LEGACY_CHAT_FORMAT = "chatml-function-calling"
# Formats rendered with the GGUF's own chat template (llama-cpp-python chat_format=None).
_TEMPLATE_FORMATS = ("native", "prompted")


def _read_chat_template(model_path: Optional[str]) -> Optional[str]:
    if not model_path:
        return None
    try:
        from .gguf_meta import read_gguf_metadata
        template = read_gguf_metadata(model_path, keys=["tokenizer.chat_template"]).get("tokenizer.chat_template")
    except Exception as e:
        logger.warning(f"Could not read chat template from {model_path}: {e}")
        return None
    return template if isinstance(template, str) else None


# Tool-call markup emitted by the model families GeoAI benchmarks (see eval/benchmark.py):
#   Hermes / Qwen2.5 / Qwen3 / SmolLM3 / Granite 4 / GeoAI fine-tunes: <tool_call>{...}</tool_call>
#   Granite 3.x / Phi-4-mini:  <|tool_call|>[{...}] (the marker may be stripped by detokenisation)
#   Phi-4-mini (vLLM parser):  functools[{...}]
#   Mistral:                   [TOOL_CALLS][{...}]
#   Llama 3.x:                 <|python_tag|>{"name": ..., "parameters": {...}} or a bare JSON object
# Every format decodes to {"name": str, "arguments"|"parameters": dict}; the agent and the tool
# registry still validate the name and arguments before anything is executed.
_TOOL_CALL_BLOCK = re.compile(r"<tool_call>\s*(.*?)\s*(?:</tool_call>|$)", re.DOTALL)
_PREFIXED_CALLS = re.compile(r"(?:<\|tool_call\|>|\[TOOL_CALLS\]|functools(?=\s*\[)|<\|python_tag\|>)\s*(.*?)\s*"
                             r"(?:<\|/tool_call\|>|<\|eom_id\|>|<\|eot_id\|>|$)", re.DOTALL)
_JSON_FENCE = re.compile(r"^```(?:json|tool_code|tool_call)?\s*(.*?)\s*```$", re.DOTALL)


def _decode_tool_json(blob: str) -> Optional[Any]:
    """
    json.loads, tolerating the doubled braces Qwen2.5's own chat template shows in
    its tool instructions (the base model often copies ``{{"name": ...}}}}``).
    """
    try:
        return json.loads(blob)
    except json.JSONDecodeError:
        pass
    s = blob.strip()
    while s.startswith("{{"):
        s = s[1:]
    try:
        obj, _end = json.JSONDecoder().raw_decode(s)
        return obj
    except json.JSONDecodeError:
        return None


def _as_call_objects(obj: Any) -> List[Dict[str, Any]]:
    """Normalise a decoded payload (object or list of objects) to [{"name", "arguments"}]."""
    items = obj if isinstance(obj, list) else [obj]
    out = []
    for it in items:
        if isinstance(it, dict) and isinstance(it.get("function"), dict):  # OpenAI-style nesting
            it = it["function"]
        if not isinstance(it, dict) or not isinstance(it.get("name"), str):
            continue
        args = it.get("arguments", it.get("parameters", {}))
        if isinstance(args, str):
            try:
                args = json.loads(args) if args.strip() else {}
            except json.JSONDecodeError:
                args = {}
        out.append({"name": it["name"], "arguments": args if isinstance(args, dict) else {}})
    return out


def _is_bare_call_payload(obj: Any) -> bool:
    """A whole completion that is only a call object/list (Llama 3.x, stripped Phi/Granite markers)."""
    items = obj if isinstance(obj, list) else [obj]
    return bool(items) and all(isinstance(it, dict) and isinstance(it.get("name"), str)
                               and ("arguments" in it or "parameters" in it) for it in items)


def parse_tool_calls(text: Optional[str]) -> Tuple[str, List[ToolCall]]:
    """
    Split a completion into (content, tool_calls), whatever the model family's tool-call markup
    (see the format list above). Malformed payloads are dropped with a warning, never executed.
    Text that merely mentions JSON is left alone: a bare JSON payload is only treated as a call
    when it is the entire completion and every item has a name plus arguments/parameters.
    """
    text = text or ""
    objs: List[Dict[str, Any]] = []
    content = text

    blocks = _TOOL_CALL_BLOCK.findall(text)
    if blocks:
        for blob in blocks:
            obj = _decode_tool_json(blob)
            if obj is None:
                logger.warning(f"Ignoring malformed <tool_call> block: {blob[:200]!r}")
                continue
            objs.extend(_as_call_objects(obj))
        if objs:
            content = _TOOL_CALL_BLOCK.sub("", text).strip()
    else:
        m = _PREFIXED_CALLS.search(text)
        if m:
            obj = _decode_tool_json(m.group(1))
            if obj is None:
                logger.warning(f"Ignoring malformed tool-call payload: {m.group(1)[:200]!r}")
            else:
                objs = _as_call_objects(obj)
                if objs:
                    content = (text[:m.start()] + text[m.end():]).strip()
        else:
            stripped = text.strip()
            fence = _JSON_FENCE.match(stripped)
            candidate = fence.group(1) if fence else stripped
            if candidate[:1] in "{[":
                try:
                    obj = json.loads(candidate)
                except json.JSONDecodeError:
                    obj = None
                if obj is not None and _is_bare_call_payload(obj):
                    objs = _as_call_objects(obj)
                    content = ""

    calls = [ToolCall(id=f"call_{i}", function_name=o["name"], arguments=o["arguments"]) for i, o in enumerate(objs)]
    return (content if calls else text), calls


def strip_thinking(text: str) -> str:
    """
    Drop <think>...</think> reasoning blocks (Qwen3/Qwen3.5/SmolLM3) from a completion,
    including empty and unterminated blocks and a leading block whose "<think>" was part of
    the prompt (Qwen3.5 prefills it when thinking is on). Same filter as streaming uses.
    """
    if "<think>" not in text and "</think>" not in text:
        return text
    close, open_ = text.find(ThinkStreamFilter.CLOSE), text.find(ThinkStreamFilter.OPEN)
    f = ThinkStreamFilter(start_inside=close >= 0 and (open_ < 0 or close < open_))
    return (f.feed(text) + f.flush()).strip()


class ThinkStreamFilter:
    """
    Removes <think>...</think> blocks (also empty or unterminated ones) from a sequence of
    text deltas, holding back a possibly partial tag. ``strip_thinking`` is the one-shot use.
    ``start_inside``: the prompt already opened the block (template prefilled "<think>").
    """
    OPEN, CLOSE = "<think>", "</think>"

    def __init__(self, start_inside: bool = False):
        self._buf = ""
        self._inside = start_inside
        self._lstrip = True  # drop whitespace at the start and after a closed block

    @staticmethod
    def _partial_tag_len(text: str, tag: str) -> int:
        for k in range(min(len(tag) - 1, len(text)), 0, -1):
            if text.endswith(tag[:k]):
                return k
        return 0

    def _out(self, text: str) -> str:
        if self._lstrip:
            text = text.lstrip()
            if text:
                self._lstrip = False
        return text

    def feed(self, delta: Optional[str]) -> str:
        self._buf += delta or ""
        out = ""
        while self._buf:
            if self._inside:
                j = self._buf.find(self.CLOSE)
                if j < 0:
                    keep = self._partial_tag_len(self._buf, self.CLOSE)
                    self._buf = self._buf[len(self._buf) - keep:] if keep else ""
                    return out
                self._buf = self._buf[j + len(self.CLOSE):]
                self._inside, self._lstrip = False, True
                continue
            i = self._buf.find(self.OPEN)
            if i >= 0:
                out += self._out(self._buf[:i])
                self._buf = self._buf[i + len(self.OPEN):]
                self._inside = True
                continue
            keep = self._partial_tag_len(self._buf, self.OPEN)
            out += self._out(self._buf[:len(self._buf) - keep])
            self._buf = self._buf[len(self._buf) - keep:]
            return out
        return out

    def flush(self) -> str:
        rest = "" if self._inside else self._out(self._buf)
        self._buf = ""
        return rest


# Stop strings for a turn that offers tools (native/prompted formats): the model must never
# write the tool response itself. The EOS/<|im_end|> stop comes from the chat template.
TOOL_TURN_STOP = ("<tool_response>",)


# Backwards-compatible name (tests, fine-tune tooling).
parse_native_tool_calls = parse_tool_calls


PROMPTED_TOOL_INSTRUCTIONS = (
    "# Tools\n\n"
    "You may call one or more of the functions below. Their JSON schemas are listed inside <tools></tools>.\n"
    "<tools>\n{tools}\n</tools>\n\n"
    "To call a function, reply with one JSON object per call inside <tool_call></tool_call> tags, "
    "and nothing after the last tag:\n"
    '<tool_call>\n{{"name": "<function-name>", "arguments": {{<argument-name>: <value>}}}}\n</tool_call>\n'
    "Function results are returned to you inside <tool_response></tool_response> tags."
)


def build_prompted_messages(msg_dicts: List[Dict[str, Any]], tools: Optional[List[dict]]) -> List[Dict[str, Any]]:
    """
    Rewrite an OpenAI-style message list for a chat template without a tool section (Gemma 3):
    tool schemas go into the system text, earlier tool calls become ``<tool_call>`` text and
    tool results become user turns wrapped in ``<tool_response>``. Consecutive same-role turns
    are merged because such templates require strictly alternating user/assistant roles.
    """
    out: List[Dict[str, Any]] = []
    for d in msg_dicts:
        role, content = d.get("role"), d.get("content") or ""
        if role == "assistant" and d.get("tool_calls"):
            parts = [content] if content else []
            for tc in d["tool_calls"]:
                fn = tc.get("function", tc)
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        pass
                parts.append("<tool_call>\n" + json.dumps({"name": fn.get("name"), "arguments": args}) + "\n</tool_call>")
            content = "\n".join(parts)
        elif role == "tool":
            role, content = "user", f"<tool_response>\n{content}\n</tool_response>"
        if out and out[-1]["role"] == role and role != "system":
            out[-1]["content"] += "\n\n" + content
        else:
            out.append({"role": role, "content": content})
    if tools:
        block = PROMPTED_TOOL_INSTRUCTIONS.format(tools="\n".join(json.dumps(t) for t in tools))
        if out and out[0]["role"] == "system":
            out[0]["content"] = (out[0]["content"] + "\n\n" + block).strip()
        else:
            out.insert(0, {"role": "system", "content": block})
    return out


class LlamaCppProvider(ModelProvider):
    def __init__(self, config: GeoAIModelConfig):
        """Initialize the LlamaCppProvider with lazy loading."""
        self.config = config
        self._model = None
        self._model_path = config.model_path
        self._adapter_check: Optional[AdapterCheck] = None
        self._adapter_active = False
        self._chat_format: Optional[str] = None  # resolved at load time
        self._thinking_switch = False  # GGUF template has an enable_thinking switch (resolved at load time)
        self._threads: Optional[Tuple[int, int]] = None  # (n_threads, n_threads_batch) used at load time
        self._thinking_kwarg = False  # enable_thinking is passed to the chat template (see _set_template_kwargs)
        # One llama.cpp context is not thread-safe: loading, background warm-up, generation and
        # unloading are serialised. A plain Lock (not RLock) because a streaming generator may be
        # resumed and closed on different server threads.
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # LoRA adapter / chat-format resolution
    # ------------------------------------------------------------------
    def _resolve_adapter(self, model_path: Path) -> Optional[str]:
        """Return the LoRA path to apply, or None (incompatible adapters are refused)."""
        lora = getattr(self.config, "lora_path", None)
        if not lora:
            self._adapter_check = None
            return None
        chk = check_adapter_compatibility(lora, str(model_path))
        self._adapter_check = chk
        for w in chk.warnings:
            logger.warning(f"LoRA adapter {lora}: {w}")
        if not chk.ok:
            logger.warning(f"Refusing LoRA adapter {lora}: {chk.reason}. Loading the base model only.")
            return None
        return lora

    def _resolve_chat_format(self, adapter_used: bool) -> str:
        cf = getattr(self.config, "chat_format", None)
        if cf:
            if cf not in CHAT_FORMATS:
                logger.warning(f"Unknown chat_format {cf!r}; using {LEGACY_CHAT_FORMAT!r}.")
                return LEGACY_CHAT_FORMAT
            return cf
        sc = (self._adapter_check.sidecar or {}) if (adapter_used and self._adapter_check) else {}
        if sc.get("chat_template") == "native":
            return "native"
        # The legacy handler drops `tools` unless tool_choice is forced, so the model can never
        # call a tool; prefer the GGUF's own template whenever it renders tools, and describe the
        # tools in the prompt when the template has no tool section (Gemma 3).
        template = _read_chat_template(self._model_path)
        if template is not None:
            return "native" if "tools" in template else "prompted"
        return LEGACY_CHAT_FORMAT

    def _ensure_loaded(self) -> None:
        """Load the model if it is not already loaded."""
        if self._model is not None:
            return

        if not self._model_path:
            raise RuntimeError("Model path is not specified in configuration.")

        model_path = Path(self._model_path)
        if not model_path.exists():
            raise RuntimeError(f"Model file not found at {self._model_path}")

        try:
            from llama_cpp import Llama
        except ImportError as e:
            raise ImportError(
                "llama-cpp-python is not installed. "
                "Please install it to use LlamaCppProvider."
            ) from e

        lora = self._resolve_adapter(model_path)
        self._thinking_switch = "enable_thinking" in (_read_chat_template(self._model_path) or "")

        def _build(lora_path: Optional[str]):
            chat_format = self._resolve_chat_format(adapter_used=lora_path is not None)
            kwargs: Dict[str, Any] = dict(
                model_path=str(model_path),
                n_ctx=self.config.n_ctx,
                n_gpu_layers=self.config.n_gpu_layers,
                verbose=self.config.verbose,
                # None -> llama-cpp-python uses the GGUF's own chat template (native: tools are passed
                # to it; prompted: tools are described in the system text, see build_prompted_messages).
                chat_format=None if chat_format in _TEMPLATE_FORMATS else chat_format,
            )
            n_threads, n_threads_batch = resolve_thread_counts(self.config)
            self._threads = (n_threads, n_threads_batch)
            kwargs.update(n_threads=n_threads, n_threads_batch=n_threads_batch,
                          n_batch=int(getattr(self.config, "n_batch", 512) or 512))
            if lora_path:
                # llama-cpp-python 0.3.x: Llama(lora_path=..., lora_scale=...); note it disables mmap.
                kwargs["lora_path"] = str(lora_path)
                kwargs["lora_scale"] = float(getattr(self.config, "lora_scale", 1.0))
            return Llama(**kwargs), chat_format

        try:
            self._model, self._chat_format = _build(lora)
            self._adapter_active = lora is not None
        except Exception as e:
            if lora is None:
                raise RuntimeError(f"Failed to load model from {self._model_path}: {e}") from e
            # The adapter passed the metadata checks but llama.cpp rejected it: fall back to base.
            logger.warning(f"Failed to apply LoRA adapter {lora} ({e}); loading the base model only.")
            if self._adapter_check is not None:
                self._adapter_check.ok = False
                self._adapter_check.reason = f"llama.cpp failed to apply the adapter: {e}"
            try:
                self._model, self._chat_format = _build(None)
                self._adapter_active = False
            except Exception as e2:
                raise RuntimeError(f"Failed to load model from {self._model_path}: {e2}") from e2
        self._thinking_kwarg = False
        if self._thinking_switch and self._chat_format in _TEMPLATE_FORMATS:
            self._thinking_kwarg = self._set_template_kwargs(
                enable_thinking=not getattr(self.config, "disable_thinking", True))
        logger.info(f"Model successfully loaded from {self._model_path}"
                    + (f" with LoRA adapter {lora} (scale {self.config.lora_scale})" if self._adapter_active else "")
                    + f" [chat_format={self._chat_format}]")

    def _set_template_kwargs(self, **template_kwargs: Any) -> bool:
        """
        Pass extra variables (e.g. ``enable_thinking``) to the GGUF's Jinja chat template.
        ``Llama.create_chat_completion`` has no parameter for them, but the template handler
        forwards unknown keyword arguments to the template, so the handler is wrapped with them
        (the same kwargs the fine-tuning chat template uses, finetune.config.chat_template_kwargs).
        Returns False when the handler cannot be found (the caller falls back to a soft switch).
        """
        llama = self._model
        handlers = getattr(llama, "_chat_handlers", None)
        base = handlers.get(getattr(llama, "chat_format", None)) if isinstance(handlers, dict) else None
        if base is None:
            return False
        llama.chat_handler = functools.partial(base, **template_kwargs)
        return True

    def load(self) -> None:
        """Explicitly load the model."""
        with self._lock:
            self._ensure_loaded()

    def warm_up(self, system_prompt: Optional[str] = None) -> None:
        """
        Load the model and, if given, evaluate the system prompt into the KV cache. The next
        request that starts with the same system text then skips that part of prompt
        processing (llama-cpp-python reuses the longest common token prefix of the last
        evaluated prompt).
        """
        with self._lock:
            self._ensure_loaded()
            if not system_prompt:
                return
            msgs = self._message_dicts([ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)])
            self._model.create_chat_completion(messages=msgs, max_tokens=1, temperature=0.0)

    def unload(self) -> None:
        """Unload the model and free memory (waits for a running generation to finish)."""
        with self._lock:
            if self._model is not None:
                self._model = None
                self._adapter_active = False
                logger.info("Model unloaded.")

    def is_loaded(self) -> bool:
        """Whether the model is currently loaded in memory."""
        return self._model is not None

    def model_info(self) -> Dict[str, Any]:
        """Return metadata about the loaded model (and LoRA adapter, if configured)."""
        lora_path = getattr(self.config, "lora_path", None)
        adapter: Optional[Dict[str, Any]] = None
        if lora_path:
            adapter = {"path": str(lora_path), "scale": getattr(self.config, "lora_scale", 1.0),
                       "active": self._adapter_active,
                       "status": ("active" if self._adapter_active else
                                  "rejected" if (self._adapter_check and not self._adapter_check.ok) else
                                  "not_loaded")}
            if self._adapter_check is not None:
                adapter.update({k: v for k, v in self._adapter_check.summary().items() if k != "path"})
        return {
            "provider": "llama_cpp",
            "model_path": str(self._model_path) if self._model_path else None,
            "loaded": self.is_loaded(),
            "n_ctx": self.config.n_ctx,
            "n_gpu_layers": self.config.n_gpu_layers,
            "n_threads": self._threads[0] if self._threads else None,
            "n_threads_batch": self._threads[1] if self._threads else None,
            "chat_format": self._chat_format or getattr(self.config, "chat_format", None),
            "lora_adapter": adapter,
        }

    def _message_dicts(self, messages: List[ChatMessage], tools: Optional[List[dict]] = None) -> List[Dict[str, Any]]:
        msg_dicts = [msg.to_dict() for msg in messages]
        if self._thinking_switch and not self._thinking_kwarg and getattr(self.config, "disable_thinking", True):
            # Fallback when enable_thinking=False could not be passed to the template: hybrid
            # thinking models (Qwen3, SmolLM3) honour a "/no_think" soft switch in the system
            # prompt; long reasoning traces cost minutes per turn on a CPU.
            if msg_dicts and msg_dicts[0].get("role") == "system":
                msg_dicts[0]["content"] = (msg_dicts[0].get("content") or "") + "\n/no_think"
            else:
                msg_dicts.insert(0, {"role": "system", "content": "/no_think"})
        if self._chat_format == "prompted":
            return build_prompted_messages(msg_dicts, tools)
        if self._chat_format == "native":
            # Native HF templates (Qwen2.5: `arguments | tojson`) expect argument objects, not JSON strings.
            for d in msg_dicts:
                for tc in d.get("tool_calls") or []:
                    fn = tc.get("function", {})
                    if isinstance(fn.get("arguments"), str):
                        try:
                            fn["arguments"] = json.loads(fn["arguments"])
                        except json.JSONDecodeError:
                            pass
        return msg_dicts

    def generate(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.1,
        max_tokens: int = 1024
    ) -> ModelResponse:
        """Generate a response from the model."""
        with self._lock:
            return self._generate(messages, tools, temperature, max_tokens)

    def _generate(self, messages: List[ChatMessage], tools: Optional[List[dict]],
                  temperature: float, max_tokens: int) -> ModelResponse:
        self._ensure_loaded()

        msg_dicts = self._message_dicts(messages, tools)
        kwargs = {
            "messages": msg_dicts,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "repeat_penalty": float(getattr(self.config, "repeat_penalty", 1.15)),
        }
        if tools and self._chat_format != "prompted":
            kwargs["tools"] = tools
        if tools and self._chat_format in _TEMPLATE_FORMATS:
            # A tool-call turn is over once the call is written; small models sometimes go on to
            # invent the tool's reply. Stopping there saves tokens and keeps fake results out.
            kwargs["stop"] = list(TOOL_TURN_STOP)

        try:
            response = self._model.create_chat_completion(**kwargs)
            choice = response["choices"][0]
            message = choice.get("message", {})
            finish_reason = choice.get("finish_reason")

            if message.get("content"):
                message["content"] = strip_thinking(message["content"])
            if (self._chat_format == "native" or (self._chat_format == "prompted" and tools))                     and not message.get("tool_calls"):
                content, native_calls = parse_tool_calls(message.get("content"))
                if native_calls:
                    return ModelResponse(content=content or None, tool_calls=native_calls,
                                         finish_reason="tool_calls", usage=response.get("usage"))

            parsed_tool_calls = None
            if finish_reason == "tool_calls" or "tool_calls" in message:
                parsed_tool_calls = []
                for tc in message.get("tool_calls", []):
                    func_name = tc.get("function", {}).get("name", "")
                    raw_args = tc.get("function", {}).get("arguments", "{}")
                    
                    try:
                        args = json.loads(raw_args)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse tool call arguments: {raw_args}")
                        args = {}
                        
                    parsed_tool_calls.append(
                        ToolCall(
                            id=tc.get("id", ""),
                            function_name=func_name,
                            arguments=args
                        )
                    )

            return ModelResponse(
                content=message.get("content"),
                tool_calls=parsed_tool_calls,
                finish_reason=finish_reason,
                usage=response.get("usage")
            )
        except Exception as e:
            logger.error(f"Error during generation: {e}")
            raise RuntimeError(f"Generation failed: {e}") from e

    def generate_stream(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.1,
        max_tokens: int = 1024
    ) -> Iterator[StreamChunk]:
        """Generate a streaming response from the model."""
        with self._lock:
            yield from self._generate_stream(messages, tools, temperature, max_tokens)

    def _generate_stream(self, messages: List[ChatMessage], tools: Optional[List[dict]],
                         temperature: float, max_tokens: int) -> Iterator[StreamChunk]:
        self._ensure_loaded()

        if self._chat_format in _TEMPLATE_FORMATS and tools:
            # Native tool calls arrive as <tool_call> text that is only parseable once complete;
            # emit the finished turn as one chunk rather than streaming raw markup to the UI.
            resp = self._generate(messages, tools, temperature, max_tokens)
            yield StreamChunk(delta_content=resp.content, delta_tool_calls=resp.tool_calls,
                              finish_reason=resp.finish_reason)
            return

        msg_dicts = self._message_dicts(messages, tools)
        kwargs = {
            "messages": msg_dicts,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "repeat_penalty": float(getattr(self.config, "repeat_penalty", 1.15)),
            "stream": True
        }
        if tools:
            kwargs["tools"] = tools

        try:
            response_stream = self._model.create_chat_completion(**kwargs)
            think_filter = ThinkStreamFilter()
            # With thinking on, a template may prefill "<think>" (Qwen3.5), so a block can close
            # without having opened in the output: hold the text and strip it once complete.
            hold_all = self._thinking_switch and not getattr(self.config, "disable_thinking", True)
            held = ""

            for chunk in response_stream:
                choice = chunk["choices"][0]
                delta = choice.get("delta", {})
                finish_reason = choice.get("finish_reason")

                delta_content = delta.get("content")
                if hold_all:
                    held += delta_content or ""
                    delta_content = (strip_thinking(held) or None) if finish_reason is not None else None
                elif delta_content is not None or finish_reason is not None:
                    delta_content = think_filter.feed(delta_content)
                    if finish_reason is not None:
                        delta_content += think_filter.flush()
                    delta_content = delta_content or None

                delta_tool_calls = None
                if "tool_calls" in delta:
                    delta_tool_calls = []
                    for tc in delta.get("tool_calls", []):
                        func_name = tc.get("function", {}).get("name") if "function" in tc else ""
                        raw_args = tc.get("function", {}).get("arguments", "") if "function" in tc else ""
                        
                        args = {}
                        if raw_args:
                            try:
                                args = json.loads(raw_args)
                            except json.JSONDecodeError:
                                # For streaming, args might be partial, but the instructions say "handle JSON parse errors gracefully".
                                # A partial JSON will fail to parse here, which means we might not emit args progressively, but since ToolCall expects Dict[str, Any], this is the best we can do.
                                # Let's store raw_args in a dummy key if it fails? No, the instructions didn't specify streaming partial JSON handling for tools. Just "handle graceful JSON".
                                pass
                                
                        delta_tool_calls.append(
                            ToolCall(
                                id=tc.get("id", ""),
                                function_name=func_name or "",
                                arguments=args
                            )
                        )
                        
                yield StreamChunk(
                    delta_content=delta_content,
                    delta_tool_calls=delta_tool_calls,
                    finish_reason=finish_reason
                )
        except Exception as e:
            logger.error(f"Error during streaming generation: {e}")
            raise RuntimeError(f"Streaming generation failed: {e}") from e
