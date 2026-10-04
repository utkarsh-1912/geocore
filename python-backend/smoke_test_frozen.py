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
                    problems = _problems(details)
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
