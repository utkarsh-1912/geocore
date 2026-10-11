# Author: Utkarsh Gupta
# License: GPL v3
"""
Every calculation the desktop app can open answers /api/execute exactly as recorded in tests/golden/outputs.json,
custom outputs included (Plotly figures, multi-plot payloads, tables, saved objects) - see tests/golden/golden_tools.py.

Runs in a separate process with its own GEOCORE_CONFIG_DIR, so it never writes saved objects or calculation
history into the user's GeoCore data. When an output change is intended, review it and re-record:

    python tests/golden/golden_tools.py record
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
GOLDEN = HERE / "golden"


def test_every_calculation_answers_as_recorded():
    sys.path.insert(0, str(GOLDEN))
    from golden_tools import OUTPUTS_PATH, environment_mismatch
    recorded = json.loads(OUTPUTS_PATH.read_text(encoding="utf-8")).get("environment", {})
    mismatch = environment_mismatch(recorded)
    if mismatch:
        pytest.skip("golden baseline recorded with other library versions: " + "; ".join(mismatch))
    env = dict(os.environ, GEOCORE_CONFIG_DIR=tempfile.mkdtemp(prefix="geocore-golden-"), PYTHONWARNINGS="ignore")
    proc = subprocess.run([sys.executable, str(GOLDEN / "golden_tools.py"), "check"], cwd=str(HERE.parent), env=env,
                          capture_output=True, text=True, timeout=900)
    start = proc.stdout.find("{\n")
    assert start != -1, f"golden check did not report:\nSTDOUT:\n{proc.stdout[-2000:]}\nSTDERR:\n{proc.stderr[-3000:]}"
    report = json.loads(proc.stdout[start:])
    assert report["cases"] >= 200
    assert not report["changed"] and not report["recorded_but_no_case"], (
        "Calculation outputs changed (re-record only if intended):\n" + json.dumps(report, indent=1)[:6000])
    # The catalogue's result envelope reads every response, custom outputs included, without changing it.
    assert not report["envelope_problems"], "\n".join(report["envelope_problems"][:40])


def test_every_sidebar_calculation_has_a_case():
    sys.path.insert(0, str(HERE.parent))
    from core.catalogue.sidebar import iter_sidebar_functions
    cases = json.loads((GOLDEN / "cases.json").read_text(encoding="utf-8"))
    covered = {c["function"] for c in cases["cases"]} | set(cases["skipped_no_schema"])
    assert {f["id"] for f in iter_sidebar_functions()} <= covered
