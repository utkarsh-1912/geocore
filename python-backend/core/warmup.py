# Author: Utkarsh Gupta
# License: GPL v3
"""
Background warm-up of heavy imports (groundhog, scipy, matplotlib, plotly).

The backend defers these imports so that it starts listening quickly. Once
the server is up, main.py runs the deferred imports on a single background
thread. Code paths that need groundhog call ``wait_for_warmup()`` first, so
heavy modules are never imported concurrently from two threads (avoiding
partially-initialised-module races) and behaviour matches the old eager start.

When no warm-up has been started (tests, scripts, ``import main``) the wait
returns immediately and imports happen lazily on first use.
"""
import logging
import threading
import time
from typing import Callable, Optional

logger = logging.getLogger("groundhog-backend")

_done = threading.Event()
_done.set()
_thread: Optional[threading.Thread] = None
_start_lock = threading.Lock()


def wait_for_warmup() -> None:
    """Block until an in-progress warm-up has finished (no-op otherwise)."""
    if threading.current_thread() is _thread:
        return
    _done.wait()


def is_warm() -> bool:
    """True once no warm-up is in progress (heavy modules are importable without waiting)."""
    return _done.is_set()


async def wait_for_warmup_async() -> None:
    """Async variant for event-loop handlers: waits without blocking the loop,
    so /health keeps answering while the warm-up finishes."""
    if _done.is_set():
        return
    import asyncio
    await asyncio.to_thread(_done.wait)


def start_background_warmup(task: Callable[[], None],
                            ready: Optional[Callable[[], bool]] = None,
                            ready_timeout: float = 60.0) -> bool:
    """
    Run ``task`` once on a daemon thread, after ``ready()`` becomes true
    (e.g. the server is listening) or ``ready_timeout`` seconds elapse.
    Returns False if a warm-up was already started.
    """
    global _thread
    with _start_lock:
        if _thread is not None:
            return False

        def _run():
            try:
                if ready is not None:
                    deadline = time.monotonic() + ready_timeout
                    while not ready() and time.monotonic() < deadline:
                        time.sleep(0.05)
                t0 = time.perf_counter()
                task()
                logger.info(f"Background warm-up finished in {time.perf_counter() - t0:.1f} s")
            except Exception as e:
                logger.warning(f"Background warm-up failed: {e}")
            finally:
                _done.set()

        _done.clear()
        _thread = threading.Thread(target=_run, name="geocore-warmup", daemon=True)
        _thread.start()
        return True
