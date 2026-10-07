"""
Image ids and the model's view of images (core/geoai/visuals.py, agent.py).

In place of a figure the model reads {"image_id", "details"} (never the plotted data) and may write
{{image:ID}} in its answer where the image belongs. The figure itself travels to the UI beside the result.
Every other part of the result and every non-chart block is passed on as before.
"""
import json

from core.geoai.agent import GeoAIAgent, _result_summary
from core.geoai.model_provider import ModelProvider, StreamChunk, ToolCall
from core.geoai.response_guard import AnswerStreamCleaner, clean_answer
from core.geoai.tool_registry import GeoAIToolRegistry, tool_registry
from core.geoai.visuals import ImageIds, image_manifest

MOHR = {"sigma_3": 20, "cohesion": 10, "phi": 35}
CALL = ToolCall(id="t1", function_name="mohrcoulomb_triaxial_compression", arguments=MOHR)


class _Agent(GeoAIAgent):
    def __init__(self):  # tool execution only, no model
        self._registry = tool_registry
        self._registry_displays = True


def _run(ids):
    agent = _Agent()
    wrapper = agent._execute_tool_call(CALL, ids=ids)
    return wrapper, agent._visuals_for(CALL, wrapper, ids)


def test_display_data_is_beside_the_result_not_in_it():
    plain = tool_registry.invoke_tool("mohrcoulomb_triaxial_compression", MOHR)
    assert "_display" not in plain
    with_display = tool_registry.invoke_tool("mohrcoulomb_triaxial_compression", MOHR, include_display=True)
    assert set(with_display["_display"]) == {"figures"}  # figures only: tables and the rest pass as they were


def test_placeholder_and_chart_share_a_turn_unique_id():
    ids = ImageIds()
    first, blocks = _run(ids)
    second, more = _run(ids)
    assert first["result"]["Plot"]["image_id"] == "img1" and second["result"]["Plot"]["image_id"] == "img2"
    chart = next(b for b in blocks if b["type"] == "figure")
    assert chart["id"] == "img1" and next(b for b in more if b["type"] == "figure")["id"] == "img2"
    assert "display" not in first  # the figure data is gone before anything is recorded or sent to the model


def test_only_charts_get_ids_and_nothing_else_changes():
    _, blocks = _run(ImageIds())
    assert [b.get("id") for b in blocks if b["type"] != "figure"] == [None] * (len(blocks) - 1)
    assert not any("description" in b for b in blocks if b["type"] != "figure")
    chart = next(b for b in blocks if b["type"] == "figure")
    layout = chart["figure"]["layout"]
    assert layout["xaxis"]["title"]["text"] == "σ [kPa]" and layout["yaxis"]["title"]["text"] == "τ [kPa]"
    assert "$" not in chart["description"] and "\\" not in chart["description"]
    names = [t["name"] for t in chart["figure"]["data"]]
    assert "Sample" in names and "Orientation of selected plane" in names  # Groundhog's inset is kept
    assert "xaxis2" in layout and "yaxis2" in layout


def test_manifest_lists_images_only_and_no_data():
    wrapper, blocks = _run(ImageIds())
    manifest = image_manifest(blocks)
    assert manifest.count("{{image:img1}}") == 1 and "metrics" not in manifest.lower()
    assert "112.7" not in manifest and "bdata" not in manifest
    assert image_manifest([b for b in blocks if b["type"] != "figure"]) == ""
    assert "112.7" in json.dumps(wrapper["result"])  # the numbers still reach the model, in the result itself


def test_result_summary_does_not_print_the_image_placeholder():
    wrapper, _ = _run(ImageIds())
    text = _result_summary([{"name": "mohr", "result": wrapper}])
    assert "image_id" not in text and "Plot" not in text
    assert "Mohr circle = table of 250 rows" in text and "sigma_1_f [kPa] = 112.7" in text


def test_markers_survive_the_answer_guards_whole_and_split_across_chunks():
    text = "The circle touches the envelope.\n{{image:img1}}\nThat is failure."
    assert "{{image:img1}}" in clean_answer(text, [])
    cleaner, out = AnswerStreamCleaner([]), ""
    for piece in ("The circle.\n{{ima", "ge:img1}}\nDone."):
        out += cleaner.feed(piece)
    assert "{{image:img1}}" in out + cleaner.flush()


class _Provider(ModelProvider):
    def __init__(self):
        self.seen = []
        self.rounds = [
            [StreamChunk(delta_tool_calls=[CALL])],
            [StreamChunk(delta_content="The circle touches the line.\n{{image:img1}}\n"), StreamChunk(finish_reason="stop")],
        ]

    def generate(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        raise AssertionError("streaming only")

    def generate_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        self.seen.append([m.content or "" for m in messages])
        yield from self.rounds.pop(0)

    def is_loaded(self):
        return True

    def model_info(self):
        return {"name": "mock"}


class _Registry(GeoAIToolRegistry):
    def invoke_tool(self, tool_name, args, include_display=False):
        return tool_registry.invoke_tool("mohrcoulomb_triaxial_compression", args, include_display=include_display)


def test_agent_gives_the_model_image_id_and_details_and_the_ui_the_chart():
    provider = _Provider()
    agent = GeoAIAgent(provider, _Registry())
    agent._explanations = "always"
    events = list(agent.run_stream("Calculate and explain the Mohr circle"))

    tool_result = next(e for e in events if e.type == "tool_result")
    chart = next(v for v in tool_result.visuals if v["type"] == "figure")
    assert chart["id"] == "img1" and chart["figure"]["data"]  # the UI gets the figure
    assert "display" not in tool_result.tool_result and "_display" not in tool_result.tool_result["result"]

    prompt = "\n".join(provider.seen[-1])
    assert '"image_id": "img1"' in prompt and "{{image:img1}}" in prompt  # the model got the id and details
    assert "bdata" not in prompt
    assert "Orientation of selected plane" in prompt  # in the details, as a series name only
    answer = "".join(e.content for e in events if e.type == "token")
    assert "{{image:img1}}" in answer  # the model's confirmation is kept for the UI to place
