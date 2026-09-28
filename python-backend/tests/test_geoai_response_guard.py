"""
Tests for deterministic answer guards (core/geoai/response_guard.py) and the
conversation-history support in GeoAIAgent. Regression case: the CPT SBT answer
that looped on one sentence and reported dimensionless Qt / Bq in kPa.
"""
from core.geoai.agent import GeoAIAgent, history_to_messages, MAX_HISTORY_TURNS
from core.geoai.model_provider import MessageRole, ModelProvider, ModelResponse, StreamChunk, ToolCall
from core.geoai.response_guard import AnswerStreamCleaner, clean_answer, collapse_repetition, fix_result_units
from core.geoai.tool_registry import GeoAIToolRegistry

CPT_RESULT = {
    "Qt": 360.99603631249204, "Fr_pct": 0.46044592416809815, "Bq": -0.0031271362034462607,
    "Ic": 1.2699040541465563, "sbt_zone": 7, "sbt_description": "Gravelly Sand to Dense Sand",
    "_provenance": {
        "tool_name": "classify_cpt_soil_behavior",
        "method": "Robertson (1990 / 2009) SBTn Soil Classification Chart",
        "inputs": {"qc_mpa": 14.2, "fs_kpa": 65.0, "depth": 4.5},
        "output_units": {"Qt": "-", "Fr_pct": "%", "Bq": "-", "Ic": "-", "sbt_zone": "-"},
    },
}
CPT_TOOLS_USED = [{
    "name": "classify_cpt_soil_behavior",
    "arguments": {"qc_mpa": 14.2, "fs_kpa": 65.0, "depth": 4.5},
    "result": {"status": "success", "tool_name": "classify_cpt_soil_behavior", "result": CPT_RESULT},
}]
LOOP = "The soil behavior type index (Ic) is a measure of the soil's resistance to penetration. "


# --- collapse_repetition ---
def test_collapse_repetition_removes_repeated_sentences_and_cut_off_tail():
    text = "Zone 7 is dense sand. " + LOOP * 25 + "The soil behavior type index (Ic) is a measure of the soil"
    out = collapse_repetition(text)
    assert out == "Zone 7 is dense sand. " + LOOP.strip()


def test_collapse_repetition_keeps_normal_text_and_short_repeats():
    text = "Qt = 361.\nFr = 0.46 %.\nQt = 361.\nThe result depends on the supplied parameters."
    assert collapse_repetition(text) == text


def test_collapse_repetition_never_drops_decimals_or_list_items():
    # Regression: live Qwen2.5-1.5B output was truncated to "Qt: 360." / "Bq: -0.".
    text = ("Zone 7.\n- **Normalized Cone Resistance (Qt)**: 360.996\n- **Bq Index**: -0.003127\n"
            "- **Ic**: 1.27\nThe method is Robertson (1990/2009). Qt = 360.99 and Ic = 1.27.")
    assert collapse_repetition(text) == text


def test_collapse_repetition_preserves_all_text_without_repeats():
    text = "Result: su = 85.4 kPa (Nkt = 14). phi' = 32.5 deg!\n\nSee e.g. Robertson 2009"
    assert collapse_repetition(text) == text


def test_collapse_repetition_handles_empty():
    assert collapse_repetition(None) == ""
    assert collapse_repetition("") == ""


# --- fix_result_units ---
def test_dimensionless_results_lose_invented_units():
    text = "Qt is 360.99 kPa, Fr is 0.4604% and Bq is -0.0031 kPa. Ic is 1.27."
    assert fix_result_units(text, CPT_TOOLS_USED) == "Qt is 360.99, Fr is 0.4604% and Bq is -0.0031. Ic is 1.27."


def test_wrong_unit_replaced_with_declared_unit():
    tools = [{"name": "t", "arguments": {}, "result": {"status": "success", "result": {
        "su_kpa": 85.4, "_provenance": {"output_units": {"su_kpa": "kPa"}}}}}]
    assert fix_result_units("su = 85.4 MPa", tools) == "su = 85.4 kPa"
    assert fix_result_units("su = 85.4 kPa", tools) == "su = 85.4 kPa"


def test_inputs_and_unrelated_numbers_untouched():
    text = "At depth 4.5m for qc of 14.2 MPa and fs of 65 kPa the zone is 7."
    assert fix_result_units(text, CPT_TOOLS_USED) == text


def test_failed_tools_are_ignored():
    tools = [{"name": "t", "arguments": {}, "result": {"status": "error", "error": "missing Vs"}}]
    assert fix_result_units("Qt is 360.99 kPa", tools) == "Qt is 360.99 kPa"


# --- history ---
def test_history_to_messages_replays_calculation_record():
    history = [
        {"role": "user", "content": "Classify CPT soil behavior type at 4.5m for qc = 14.2 MPa and fs = 65 kPa"},
        {"role": "assistant", "content": "Zone 7. " + LOOP * 10,
         "tool": {"name": "classify_cpt_soil_behavior", "arguments": CPT_TOOLS_USED[0]["arguments"],
                  "result": CPT_TOOLS_USED[0]["result"]}},
    ]
    msgs = history_to_messages(history)
    assert [m.role for m in msgs] == [MessageRole.USER, MessageRole.ASSISTANT]
    content = msgs[1].content
    assert content.count("soil behavior type index") == 1  # degenerate loop not replayed
    assert "[Calculation record]" in content
    assert '"tool": "classify_cpt_soil_behavior"' in content
    assert '"Qt": 361.0' in content and '"Qt": "-"' in content
    assert "Robertson" in content
    assert "_provenance" not in content


def test_history_to_messages_limits_and_skips_invalid_items():
    history = [{"role": "user", "content": f"q{i}"} for i in range(20)] + ["junk", {"role": "system", "content": "x"}]
    msgs = history_to_messages(history)
    assert len(msgs) <= MAX_HISTORY_TURNS
    assert all(m.role == MessageRole.USER for m in msgs)
    assert history_to_messages(None) == []


def test_history_error_record():
    msgs = history_to_messages([{"role": "assistant", "content": "",
                                 "tool": {"name": "t", "arguments": {}, "result": {"status": "error", "error": "Vs: Field required"}}}])
    assert "Vs: Field required" in msgs[0].content


class RecordingProvider(ModelProvider):
    """Returns canned responses in order and records every generate() call."""

    def __init__(self, responses, stream_chunks=None):
        self.responses = list(responses)
        self.stream_chunks = stream_chunks or []
        self.calls = []

    def generate(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        self.calls.append({"messages": list(messages), "tools": tools, "max_tokens": max_tokens})
        return self.responses.pop(0)

    def generate_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        yield from self.stream_chunks

    def is_loaded(self):
        return True

    def model_info(self):
        return {"name": "recording"}


class MockRegistry(GeoAIToolRegistry):
    def __init__(self, results):
        super().__init__()
        self.results = results

    def invoke_tool(self, tool_name, args):
        return self.results[tool_name]


def test_agent_passes_history_and_cleans_final_answer():
    provider = RecordingProvider([
        ModelResponse(content=None, tool_calls=[ToolCall(id="c1", function_name="classify_cpt_soil_behavior",
                                                         arguments={"qc_mpa": 14.2, "fs_kpa": 65, "depth": 4.5})],
                      finish_reason="tool_calls"),
        ModelResponse(content="Qt is 360.99 kPa. " + LOOP * 20, tool_calls=None, finish_reason="length"),
    ])
    registry = MockRegistry(results={"classify_cpt_soil_behavior": CPT_RESULT})
    agent = GeoAIAgent(provider, registry, max_tools=5)
    history = [{"role": "user", "content": "earlier question"}, {"role": "assistant", "content": "earlier answer"}]

    resp = agent.run("Classify CPT soil behavior type", history=history)

    first_msgs = provider.calls[0]["messages"]
    assert [m.role for m in first_msgs] == [MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT, MessageRole.USER]
    assert first_msgs[-1].content == "Classify CPT soil behavior type"
    assert provider.calls[1]["max_tokens"] <= 1024
    assert resp.response_text == "Qt is 360.99. " + LOOP.strip()


def test_agent_stream_streams_cleaned_explanation_and_caps_tokens():
    tc = ToolCall(id="c1", function_name="classify_cpt_soil_behavior", arguments={"qc_mpa": 14.2, "fs_kpa": 65, "depth": 4.5})
    answer = "Bq is -0.0031 kPa. Zone 7 is dense sand.\n" + LOOP * 20
    turns = [[StreamChunk(delta_tool_calls=[tc], finish_reason="tool_calls")],
             [StreamChunk(delta_content=answer[i:i + 7]) for i in range(0, len(answer), 7)]
             + [StreamChunk(finish_reason="length")]]
    stream_calls = []

    class StreamingProvider(RecordingProvider):
        def generate_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
            stream_calls.append({"tools": tools, "max_tokens": max_tokens})
            yield from turns.pop(0)

    provider = StreamingProvider([])
    registry = MockRegistry(results={"classify_cpt_soil_behavior": CPT_RESULT})
    agent = GeoAIAgent(provider, registry, max_tools=5)

    events = list(agent.run_stream("Classify CPT", history=[{"role": "user", "content": "hi"}]))
    tokens = [e.content for e in events if e.type == "token"]
    assert len(tokens) >= 3  # released sentence by sentence, not as one block
    assert "".join(tokens).rstrip() == clean_answer(answer, CPT_TOOLS_USED)
    assert "".join(tokens).rstrip() == "Bq is -0.0031. Zone 7 is dense sand.\n" + LOOP.strip()
    assert stream_calls[-1] == {"tools": None, "max_tokens": agent._answer_max_tokens}
    assert events[-1].type == "done" and not provider.calls  # explanation no longer non-streaming


def test_clean_answer_strips_echoed_calculation_record():
    text = 'Zone 7 is dense sand.\n[Calculation record] {"tool": "classify_cpt_soil_behavior"}\nIc is 1.27.'
    assert clean_answer(text) == "Zone 7 is dense sand.\nIc is 1.27."


def test_agent_drops_null_optional_arguments():
    seen = {}

    class ArgRegistry(GeoAIToolRegistry):
        def invoke_tool(self, tool_name, args):
            seen.update(args)
            return CPT_RESULT

    provider = RecordingProvider([
        ModelResponse(content=None, tool_calls=[ToolCall(id="c1", function_name="classify_cpt_soil_behavior",
                                                         arguments={"qc_mpa": 14.2, "fs_kpa": 65, "depth": 4.5, "u2_kpa": None})],
                      finish_reason="tool_calls"),
        ModelResponse(content="Zone 7.", tool_calls=None, finish_reason="stop"),
    ])
    GeoAIAgent(provider, ArgRegistry(), max_tools=5).run("Classify CPT")
    assert seen == {"qc_mpa": 14.2, "fs_kpa": 65, "depth": 4.5}


def test_clean_answer_without_tools_only_collapses():
    assert clean_answer("Pressure 12.5 kPa. " + LOOP * 3) == "Pressure 12.5 kPa. " + LOOP.strip()


def test_clean_answer_strips_inline_echoed_calculation_record():
    text = 'Ka is 0.283; active state full ... [Calculation record] {"tool": "x", "results": {"Kp": -1.569}}'
    assert clean_answer(text) == "Ka is 0.283; active state full ..."
    assert clean_answer("See the [Calculation record] above.") == "See the [Calculation record] above."


def test_clean_answer_unescapes_json_unicode_escapes():
    assert clean_answer("EN 1997-1:2004 Eurocode 7 \u00a79.5") == "EN 1997-1:2004 Eurocode 7 §9.5"


def test_agent_stream_cleans_direct_answer_without_tool_call():
    # A repeated question answered from history: the model echoes the history record.
    answer = ('Ka = 0.2827 per Eurocode 7 \u00a79.5.\n'
              '[Calculation record] {"tool": "calculate_earth_pressure_rankine", "results": {"Kp": -1.569}}')
    provider = RecordingProvider([], stream_chunks=[StreamChunk(delta_content=answer[i:i + 5])
                                                    for i in range(0, len(answer), 5)])
    agent = GeoAIAgent(provider, MockRegistry(results={}), max_tools=5)

    events = list(agent.run_stream("Calculate Ka for phi = 34 deg"))
    assert "".join(e.content for e in events if e.type == "token") == "Ka = 0.2827 per Eurocode 7 \u00a79.5."
    assert events[-1].type == "done"


# ---------------- output caps: loop stop and truncation note ----------------

def test_stream_cleaner_flags_loop_after_repeats():
    from core.geoai.response_guard import LOOP_STOP_REPEATS
    cleaner = AnswerStreamCleaner([])
    cleaner.feed("Zone 7 is dense sand to gravelly sand. ")
    assert not cleaner.looping
    for _ in range(LOOP_STOP_REPEATS):
        cleaner.feed("Zone 7 is dense sand to gravelly sand. ")
    cleaner.flush()  # the last sentence is held back until its end is certain
    assert cleaner.looping


def test_stream_answer_stops_generating_once_looping():
    tc = ToolCall(id="c1", function_name="classify_cpt_soil_behavior", arguments={"qc_mpa": 14.2, "fs_kpa": 65, "depth": 4.5})
    produced = []

    def endless_loop():
        yield StreamChunk(delta_content="Bq is -0.0031. ")
        while True:
            produced.append(1)
            if len(produced) > 500:
                raise AssertionError("generation was not stopped")
            yield StreamChunk(delta_content=LOOP)

    turns = [iter([StreamChunk(delta_tool_calls=[tc], finish_reason="tool_calls")]), endless_loop()]

    class StreamingProvider(RecordingProvider):
        def generate_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
            return turns.pop(0)

    agent = GeoAIAgent(StreamingProvider([]), MockRegistry(results={"classify_cpt_soil_behavior": CPT_RESULT}), max_tools=5)
    text = "".join(e.content for e in agent.run_stream("Classify CPT") if e.type == "token")
    assert len(produced) < 20  # stopped a few repeats in, not at the token cap
    assert "cut off" not in text  # a loop is not an unfinished answer


def test_answer_cut_at_cap_gets_truncation_note():
    from core.geoai.response_guard import TRUNCATION_NOTE
    provider = RecordingProvider([ModelResponse(content="CPT methods differ in how they treat the cone factor and",
                                                tool_calls=None, finish_reason="length")])
    resp = GeoAIAgent(provider, MockRegistry(results={}), max_tools=5).run("Compare CPT methods")
    assert resp.response_text.endswith(TRUNCATION_NOTE)
    provider = RecordingProvider([ModelResponse(content="Short complete answer.", tool_calls=None, finish_reason="stop")])
    resp = GeoAIAgent(provider, MockRegistry(results={}), max_tools=5).run("Compare CPT methods")
    assert resp.response_text == "Short complete answer."
