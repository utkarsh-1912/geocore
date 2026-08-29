import pytest
from core.geoai.agent import AgentResponse, AgentStreamEvent, GeoAIAgent, MAX_TOOL_ROUNDS
from core.geoai.model_provider import ModelProvider, ModelResponse, StreamChunk, ToolCall, ChatMessage, MessageRole
from core.geoai.tool_registry import GeoAIToolRegistry
from core.geoai.exceptions import GeoAIValidationError

class MockProvider(ModelProvider):
    def __init__(self, responses=None, stream_chunks=None):
        self.responses = responses or []
        self.stream_chunks = stream_chunks or []
        self.call_count = 0

    def generate(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        if self.call_count < len(self.responses):
            resp = self.responses[self.call_count]
            self.call_count += 1
            return resp
        # Fallback if out of responses
        return ModelResponse(content="Default response", tool_calls=None, finish_reason="stop", usage=None)

    def generate_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        for chunk in self.stream_chunks:
            yield chunk

    def is_loaded(self):
        return True

    def model_info(self):
        return {"name": "mock_model"}

class MockRegistry(GeoAIToolRegistry):
    def __init__(self, results=None, exceptions=None):
        super().__init__()
        self.results = results or {}
        self.exceptions = exceptions or {}

    def invoke_tool(self, tool_name, args):
        if tool_name in self.exceptions:
            raise self.exceptions[tool_name]
        return self.results.get(tool_name, {"default": "result"})


# 1. AgentResponse tests
def test_agent_response_to_dict_no_tools():
    resp = AgentResponse(
        response_text="Hello",
        tools_used=[],
        finish_reason="complete",
        usage={"total_tokens": 10}
    )
    d = resp.to_dict()
    assert d["response"] == "Hello"
    assert d["executed_tool"] is None
    assert d["candidate_tools"] == []
    assert d["parameters_extracted"] is None
    assert d["results"] is None

def test_agent_response_to_dict_with_tools():
    tools_used = [
        {"name": "test_tool", "arguments": {"arg1": 1}, "result": {"res": 2}},
        {"name": "second_tool", "arguments": {}, "result": {}}
    ]
    resp = AgentResponse(
        response_text="Done",
        tools_used=tools_used,
        finish_reason="complete",
        usage=None
    )
    d = resp.to_dict()
    assert d["response"] == "Done"
    assert d["executed_tool"] == "test_tool"
    assert d["candidate_tools"] == ["test_tool", "second_tool"]
    assert d["parameters_extracted"] == {"arg1": 1}
    assert d["results"] == {"res": 2}


# 2. AgentStreamEvent tests
def test_agent_stream_event_to_sse_token():
    event = AgentStreamEvent(type="token", content="word")
    sse = event.to_sse()
    assert sse == 'data: {"type": "token", "content": "word", "tool_name": null, "tool_args": null, "tool_result": null}\n\n'

def test_agent_stream_event_to_sse_tool_start():
    event = AgentStreamEvent(type="tool_start", tool_name="my_tool", tool_args={"a": 1})
    sse = event.to_sse()
    assert sse == 'data: {"type": "tool_start", "content": null, "tool_name": "my_tool", "tool_args": {"a": 1}, "tool_result": null}\n\n'

def test_agent_stream_event_to_sse_done():
    event = AgentStreamEvent(type="done")
    sse = event.to_sse()
    assert sse == 'data: {"type": "done", "content": null, "tool_name": null, "tool_args": null, "tool_result": null}\n\n'


# 3. GeoAIAgent tests
def test_geoai_agent_direct_answer():
    provider = MockProvider(responses=[
        ModelResponse(content="Direct answer", tool_calls=None, finish_reason="stop")
    ])
    registry = MockRegistry()
    agent = GeoAIAgent(provider, registry)

    response = agent.run("Hello")
    assert response.response_text == "Direct answer"
    assert response.tools_used == []
    assert response.finish_reason == "complete"

def test_geoai_agent_single_tool_call_flow():
    tool_call = ToolCall(id="call_1", function_name="calc_tool", arguments={"val": 5})
    provider = MockProvider(responses=[
        ModelResponse(content=None, tool_calls=[tool_call], finish_reason="tool_calls"),
        ModelResponse(content="Calculation complete", tool_calls=None, finish_reason="stop")
    ])
    registry = MockRegistry(results={"calc_tool": {"output": 10}})
    agent = GeoAIAgent(provider, registry)

    response = agent.run("Calculate this")
    assert response.response_text == "Calculation complete"
    assert len(response.tools_used) == 1
    assert response.tools_used[0]["name"] == "calc_tool"
    assert response.tools_used[0]["result"] == {"status": "success", "tool_name": "calc_tool", "result": {"output": 10}}
    assert response.finish_reason == "complete"

def test_geoai_agent_tool_execution_error():
    tool_call = ToolCall(id="call_err", function_name="bad_tool", arguments={})
    provider = MockProvider(responses=[
        ModelResponse(content=None, tool_calls=[tool_call], finish_reason="tool_calls"),
        ModelResponse(content="Tool failed", tool_calls=None, finish_reason="stop")
    ])
    registry = MockRegistry(exceptions={"bad_tool": GeoAIValidationError("Invalid input")})
    agent = GeoAIAgent(provider, registry)

    response = agent.run("Run bad tool")
    assert response.response_text == "Tool failed"
    assert len(response.tools_used) == 1
    assert response.tools_used[0]["result"]["status"] == "error"
    assert "Invalid input" in response.tools_used[0]["result"]["error"]

def test_geoai_agent_max_rounds_limit():
    tool_call = ToolCall(id="call_inf", function_name="infinite_tool", arguments={})
    responses = [ModelResponse(content=None, tool_calls=[tool_call], finish_reason="tool_calls") for _ in range(MAX_TOOL_ROUNDS)]
    # Plus one final response for the summary round
    responses.append(ModelResponse(content="Final summary after max rounds", tool_calls=None, finish_reason="stop"))
    
    provider = MockProvider(responses=responses)
    registry = MockRegistry()
    agent = GeoAIAgent(provider, registry)

    response = agent.run("Trigger loop")
    assert response.finish_reason == "max_rounds"
    assert response.response_text == "Final summary after max rounds"
    assert len(response.tools_used) == MAX_TOOL_ROUNDS

def test_geoai_agent_missing_parameter_handling():
    # Simulate a scenario where the model asks for clarification instead of calling a tool
    provider = MockProvider(responses=[
        ModelResponse(content="Please provide the missing value", tool_calls=None, finish_reason="stop")
    ])
    registry = MockRegistry()
    agent = GeoAIAgent(provider, registry)

    response = agent.run("Calculate without params")
    assert response.response_text == "Please provide the missing value"
    assert response.tools_used == []
    assert response.finish_reason == "complete"


# 4. _execute_tool_call tests
def test_execute_tool_call_success():
    registry = MockRegistry(results={"my_tool": {"val": 42}})
    agent = GeoAIAgent(MockProvider(), registry)
    tool_call = ToolCall(id="t1", function_name="my_tool", arguments={})
    
    res = agent._execute_tool_call(tool_call)
    assert res["status"] == "success"
    assert res["result"] == {"val": 42}

def test_execute_tool_call_validation_error():
    registry = MockRegistry(exceptions={"my_tool": GeoAIValidationError("Validation failed")})
    agent = GeoAIAgent(MockProvider(), registry)
    tool_call = ToolCall(id="t1", function_name="my_tool", arguments={})
    
    res = agent._execute_tool_call(tool_call)
    assert res["status"] == "error"
    assert res["error"] == "Validation failed"

def test_execute_tool_call_generic_error():
    registry = MockRegistry(exceptions={"my_tool": Exception("Unexpected failure")})
    agent = GeoAIAgent(MockProvider(), registry)
    tool_call = ToolCall(id="t1", function_name="my_tool", arguments={})
    
    res = agent._execute_tool_call(tool_call)
    assert res["status"] == "error"
    assert "Execution failed" in res["error"]
    assert "Unexpected failure" in res["error"]


# 5. run_stream tests
def test_run_stream_direct_answer():
    provider = MockProvider(stream_chunks=[
        StreamChunk(delta_content="Hello "),
        StreamChunk(delta_content="World")
    ])
    registry = MockRegistry()
    agent = GeoAIAgent(provider, registry)

    events = list(agent.run_stream("Hi"))
    
    assert len(events) == 3
    assert events[0].type == "token"
    assert events[0].content == "Hello "
    assert events[1].type == "token"
    assert events[1].content == "World"
    assert events[2].type == "done"

def test_run_stream_tool_call_flow():
    tool_call = ToolCall(id="stream_t1", function_name="calc_tool", arguments={"v": 1})
    provider = MockProvider(
        stream_chunks=[
            StreamChunk(delta_tool_calls=[tool_call])
        ],
        responses=[
            ModelResponse(content="Final response after tool", tool_calls=None, finish_reason="stop")
        ]
    )
    registry = MockRegistry(results={"calc_tool": {"out": 2}})
    agent = GeoAIAgent(provider, registry)

    events = list(agent.run_stream("Calculate stream"))
    
    # Expected sequence:
    # 1. tool_start
    # 2. tool_result
    # 3. token (final explanation)
    # 4. done
    assert len(events) == 4
    
    assert events[0].type == "tool_start"
    assert events[0].tool_name == "calc_tool"
    assert events[0].tool_args == {"v": 1}
    
    assert events[1].type == "tool_result"
    assert events[1].tool_name == "calc_tool"
    assert events[1].tool_result["status"] == "success"
    
    assert events[2].type == "token"
    assert events[2].content == "Final response after tool"
    
    assert events[3].type == "done"
