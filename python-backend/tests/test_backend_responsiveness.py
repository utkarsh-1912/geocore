# Author: Utkarsh Gupta
# License: GPL v3
"""
Freeze regressions: a long calculation must not stall the server's event loop, a Stop must
really stop the generation it was aimed at, and unloading must not wait behind a generation.
"""
import asyncio
import threading
import time

import httpx
from fastapi import FastAPI

from core import router as core_router
from core.geoai.lifecycle import ModelLifecycleManager
from core.geoai.llama_cpp_provider import LlamaCppProvider
from core.geoai.model_config import GeoAIModelConfig
from core.geoai.model_provider import ModelProvider, ModelResponse


def test_execute_does_not_block_the_event_loop(monkeypatch):
    release = threading.Event()

    def slow_execute(module_id, function_id, args):
        release.wait(5)
        return {"status": "ok"}

    monkeypatch.setattr(core_router.registry, "execute_function", slow_execute)
    app = FastAPI()
    app.include_router(core_router.create_dynamic_router(), prefix="/api")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    async def scenario():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            calc = asyncio.create_task(client.post("/api/execute", json={"functionId": "slow"}))
            await asyncio.sleep(0.2)  # the calculation is now running
            start = time.monotonic()
            health = await asyncio.wait_for(client.get("/health"), timeout=2)
            elapsed = time.monotonic() - start
            assert not calc.done()
            release.set()
            assert (await calc).status_code == 200
            return health.status_code, elapsed

    status, elapsed = asyncio.run(scenario())
    assert status == 200 and elapsed < 1.0


def test_clear_cancel_waits_for_the_stopped_call():
    provider = LlamaCppProvider(GeoAIModelConfig(model_path="missing.gguf"))
    provider._lock.acquire()  # a generation is still running
    provider.cancel()          # Stop
    cleared = threading.Event()

    def next_question():
        provider.clear_cancel()
        cleared.set()

    t = threading.Thread(target=next_question)
    t.start()
    time.sleep(0.2)
    assert not cleared.is_set() and provider._should_abort()  # the running call still sees Stop
    provider._lock.release()   # it aborts and gives the model back
    t.join(5)
    assert cleared.is_set() and not provider._should_abort()


class _GeneratingProvider(ModelProvider):
    """unload() returns only once the running generation has been cancelled."""

    def __init__(self):
        self.cancelled = threading.Event()

    def generate(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        return ModelResponse(content="")

    def generate_stream(self, messages, tools=None, temperature=0.1, max_tokens=1024):
        yield from ()

    def cancel(self):
        self.cancelled.set()

    def unload(self):
        assert self.cancelled.wait(2), "unload waited behind a generation that was never stopped"

    def is_loaded(self):
        return True

    def model_info(self):
        return {}


def test_unload_stops_the_running_generation():
    manager = ModelLifecycleManager()
    provider = _GeneratingProvider()
    manager.set_provider(provider)
    start = time.monotonic()
    manager.unload()
    assert provider.cancelled.is_set() and time.monotonic() - start < 1.0
