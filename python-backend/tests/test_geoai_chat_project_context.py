from fastapi.testclient import TestClient

import core.geoai.api as geoai_api
from core.geoai.system_prompt import build_system_prompt
from main import app

client = TestClient(app)


class _CapturingAgent:
    def __init__(self):
        self.context = None

    def run(self, user_message, context=None, history=None):
        self.context = context

        class _Resp:
            def to_dict(self):
                return {"response": "ok"}

        return _Resp()


def _chat(monkeypatch):
    agent = _CapturingAgent()
    monkeypatch.setattr(geoai_api, "_get_agent", lambda: agent)
    r = client.post("/api/geoai/chat", json={"prompt": "Bearing capacity of my footing?", "context": {"activeFunction": None}})
    assert r.status_code == 200
    return agent.context


def test_chat_attaches_project_with_recorded_groundwater(monkeypatch):
    assert client.put("/api/geoai/project/groundwater", json={"groundwater_depth_m": 2.5, "unit": "m"}).status_code == 200
    ctx = _chat(monkeypatch)
    assert "project_context" in ctx and ctx["activeFunction"] is None
    assert "2.5 m below ground surface" in build_system_prompt(ctx)
    client.put("/api/geoai/project/groundwater", json={"groundwater_depth_m": None, "unit": "m"})


def test_chat_skips_empty_project(monkeypatch):
    client.put("/api/geoai/project/groundwater", json={"groundwater_depth_m": None, "unit": "m"})
    monkeypatch.setattr("core.geoai.project_soil.load_project_context",
                        lambda: __import__("core.geoai.data_access", fromlist=["ProjectContext"]).ProjectContext("empty"))
    ctx = _chat(monkeypatch)
    assert "project_context" not in ctx
