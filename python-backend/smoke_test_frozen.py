"""
Smoke test for the PyInstaller-frozen backend (used by the release workflow, runnable locally).

Starts the frozen executable, waits for /health/details to report the engine ready, and checks
that the calculation registry and the GeoAI tool registry are populated. A frozen build that is
missing a hidden import or a native library usually fails here rather than on a user's machine.

    python smoke_test_frozen.py dist/main/main[.exe] [--timeout 180]

Exit code 0 on success, 1 on failure (the executable's output is printed).

Author: Utkarsh Gupta
License: GPL v3
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"


def _get(path: str, timeout: float = 5.0):
    with urllib.request.urlopen(BASE + path, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _post_text(path: str, payload: dict, timeout: float = 60.0) -> str:
    """POST JSON and return the response body, also for error statuses."""
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.read().decode("utf-8", "replace")


# One calculation per wrapper module the registry imports by name (core.registry._load_wrapper_module).
# PyInstaller cannot see those imports. Each probe must pass schema validation so the wrapper is
# actually imported; plot_with_log then fails on the missing SoilProfile, which is fine.
LAZY_WRAPPER_PROBES = {
    "core.wrappers": ("effectivearea_circle_api", {"foundation_radius": 2, "eccentricity": 0.5}),
    "core.plotting_wrappers": ("plot_with_log", {}),
}


def _lazy_wrapper_problems() -> list:
    problems = []
    for module, (function_id, args) in LAZY_WRAPPER_PROBES.items():
        body = _post_text("/api/execute", {"moduleId": "", "functionId": function_id, "args": args})
        if "No module named" in body:
            problems.append(f"{module} missing from the frozen build ({function_id}: {body[:200]})")
    return problems


def _problems(details: dict) -> list:
    problems = []
    if details.get("status") != "ok":
        problems.append(f"status is {details.get('status')!r}")
    if not (details.get("engine") or {}).get("functions_registered"):
        problems.append("no calculation functions registered")
    if not (details.get("geoai") or {}).get("tools_registered"):
        problems.append("no GeoAI tools registered")
    if not (details.get("runtime") or {}).get("frozen"):
        problems.append("not running as a frozen build")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("executable")
    parser.add_argument("--timeout", type=float, default=180.0, help="seconds to wait for the engine to be ready")
    args = parser.parse_args()

    config_dir = tempfile.mkdtemp(prefix="geocore-smoke-")
    log_path = os.path.join(config_dir, "backend.log")
    env = dict(os.environ, GEOCORE_CONFIG_DIR=config_dir)  # never touch the real user config
    with open(log_path, "wb") as log:
        proc = subprocess.Popen([args.executable], stdout=log, stderr=subprocess.STDOUT, env=env)

    def output() -> str:
        with open(log_path, "rb") as f:
            return f.read().decode("utf-8", "replace")

    deadline = time.monotonic() + args.timeout
    last = "no response yet"
    try:
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                print(f"FAIL: backend exited early with code {proc.returncode}\n--- output ---\n{output()}")
                return 1
            try:
                details = _get("/health/details")
                last = json.dumps(details)[:400]
                if (details.get("engine") or {}).get("ready"):
                    problems = _problems(details) or _lazy_wrapper_problems()
                    if problems:
                        print("FAIL: " + "; ".join(problems) + f"\n{last}\n--- output ---\n{output()}")
                        return 1
                    status = _get("/api/geoai/status")
                    if status.get("status") != "ready":
                        print(f"FAIL: /api/geoai/status returned {status}")
                        return 1
                    print(f"OK: engine ready, {details['engine']['functions_registered']} functions, "
                          f"{details['geoai']['tools_registered']} GeoAI tools")
                    return 0
            except (urllib.error.URLError, ConnectionError, TimeoutError, ValueError) as e:
                last = str(e)
            time.sleep(2)
        print(f"FAIL: engine not ready after {args.timeout:.0f}s (last: {last})\n--- output ---\n{output()}")
        return 1
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    sys.exit(main())
