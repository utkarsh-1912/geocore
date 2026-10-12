# Author: Utkarsh Gupta
# License: GPL v3
"""
Golden-output harness for /api/execute: what every calculation in the app returns today.

The calculation catalogue (core/catalogue) will gradually take over navigation, forms and GeoAI. Each step
must leave the existing calculations answering exactly as before, including the custom outputs (Plotly
figures, multi-plot payloads, tables, soil-profile objects). This module

* runs a case (function id + args, with ``@fixture`` placeholders for saved objects) through the real
  FastAPI route, in an isolated config folder,
* reduces the response to a stable fingerprint: numbers kept, long arrays and Plotly binary arrays reduced
  to count/min/max/sum/first/last, generated ids and timestamps masked,
* compares two fingerprints with a numeric tolerance and lists the differences by JSON path.

    python tests/golden/golden_tools.py check    # compare every case with tests/golden/outputs.json
    python tests/golden/golden_tools.py record   # (re)record tests/golden/outputs.json - only on purpose
"""
import base64
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

HERE = Path(__file__).resolve().parent
BACKEND = HERE.parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))  # run as a script: import main / core from python-backend
CASES_PATH = HERE / "cases.json"
OUTPUTS_PATH = HERE / "outputs.json"

REL_TOL = 1e-6
ABS_TOL = 1e-9
_ARRAY_LIMIT = 20  # numeric lists longer than this are fingerprinted
_UUID = re.compile(r"[0-9a-f]{0,8}-?[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")  # also a cut-off uuid
_NAME_SUFFIX = re.compile(r"\b([A-Z][A-Za-z]+)_[0-9a-f]{4,8}\b")  # generated object names: SoilProfile_86ad, _6e5ac7cc
# Interpreter noise that can land in a captured-warnings list depending on garbage-collection timing.
_ENV_NOISE = re.compile(r"unclosed <(socket|file|_io)|ResourceWarning")
_TIME = re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\b")
_DTYPES = {"f8": "<f8", "f4": "<f4", "i1": "<i1", "i2": "<i2", "i4": "<i4", "i8": "<i8",
           "u1": "<u1", "u2": "<u2", "u4": "<u4", "u8": "<u8"}


def _num(x: float) -> Any:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return None if x is None else str(x)
    return float(f"{float(x):.10g}")


def _array_fp(values: List[Any]) -> Dict[str, Any]:
    nums = [float(v) for v in values if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)]
    return {"__array__": len(values), "finite": len(nums),
            "min": _num(min(nums)) if nums else None, "max": _num(max(nums)) if nums else None,
            "sum": _num(sum(nums)) if nums else None,
            "first": _num(values[0]) if values and isinstance(values[0], (int, float)) else values[0] if values else None,
            "last": _num(values[-1]) if values and isinstance(values[-1], (int, float)) else values[-1] if values else None}


def _decode_bdata(obj: Dict[str, Any]) -> Optional[List[float]]:
    dtype = _DTYPES.get(obj.get("dtype"))
    if not dtype:
        return None
    try:
        arr = np.frombuffer(base64.b64decode(obj["bdata"]), dtype=dtype)
    except Exception:
        return None
    if obj.get("shape"):
        try:
            arr = arr.reshape([int(s) for s in str(obj["shape"]).split(",")])
        except Exception:
            pass
    return arr.ravel().tolist()


def fingerprint(obj: Any) -> Any:
    """Stable, compact form of a response for comparison (see module docstring)."""
    if isinstance(obj, dict):
        if set(obj) >= {"dtype", "bdata"}:
            decoded = _decode_bdata(obj)
            if decoded is not None:
                return _array_fp(decoded)
        # A Plotly layout's "template" is the library's styling defaults (differs between Plotly versions),
        # not calculation output.
        return {k: fingerprint(v) for k, v in obj.items() if k != "template"}
    if isinstance(obj, list):
        obj = [v for v in obj if not (isinstance(v, str) and _ENV_NOISE.search(v))]
        if len(obj) > _ARRAY_LIMIT and all(isinstance(v, (int, float)) or v is None for v in obj):
            return _array_fp(obj)
        if len(obj) > 200:
            return {"__list__": len(obj), "head": [fingerprint(v) for v in obj[:5]],
                    "tail": [fingerprint(v) for v in obj[-2:]]}
        return [fingerprint(v) for v in obj]
    if isinstance(obj, bool) or obj is None:
        return obj
    if isinstance(obj, (int, float)):
        return _num(obj)
    if isinstance(obj, str):
        return _NAME_SUFFIX.sub(r"\1_<id>", _TIME.sub("<time>", _UUID.sub("<uuid>", obj)))
    return str(obj)


def differences(expected: Any, actual: Any, path: str = "$", out: Optional[List[str]] = None, limit: int = 12) -> List[str]:
    """Paths where two fingerprints differ (numbers compared with REL_TOL/ABS_TOL)."""
    out = [] if out is None else out
    if len(out) >= limit:
        return out
    if isinstance(expected, dict) and isinstance(actual, dict):
        for k in expected.keys() | actual.keys():
            if k not in actual:
                out.append(f"{path}.{k}: missing (expected {str(expected[k])[:80]})")
            elif k not in expected:
                out.append(f"{path}.{k}: unexpected new key ({str(actual[k])[:80]})")
            else:
                differences(expected[k], actual[k], f"{path}.{k}", out, limit)
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            out.append(f"{path}: length {len(expected)} -> {len(actual)}")
        for i, (e, a) in enumerate(zip(expected, actual)):
            differences(e, a, f"{path}[{i}]", out, limit)
    elif isinstance(expected, (int, float)) and isinstance(actual, (int, float)) \
            and not isinstance(expected, bool) and not isinstance(actual, bool):
        if not math.isclose(expected, actual, rel_tol=REL_TOL, abs_tol=ABS_TOL):
            out.append(f"{path}: {expected} -> {actual}")
    elif expected != actual:
        out.append(f"{path}: {str(expected)[:80]!r} -> {str(actual)[:80]!r}")
    return out


# ---------------------------------------------------------------------------- running cases

def make_client():
    """FastAPI test client on the real app, with an isolated config folder (never the user's data)."""
    import tempfile
    os.environ.setdefault("GEOCORE_CONFIG_DIR", tempfile.mkdtemp(prefix="geocore-golden-"))
    import warnings
    warnings.filterwarnings("ignore")
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app, raise_server_exceptions=False)  # an unhandled error is a 500, as in the app


def _cpt_rows(extra: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    import pandas as pd
    data = pd.read_csv(HERE.parent / "data" / "groundhog_cpt_koppejan.csv", comment="#")
    rows = []
    for z, qc in zip(data["z [m]"], data["qc [MPa]"]):
        row = {"Depth from [m]": round(z - 0.1, 2), "Depth to [m]": round(z + 0.1, 2), "qc [MPa]": qc,
               "Total unit weight [kN/m3]": 19.0, "Soil type": "Sand"}
        row.update(extra or {})
        rows.append(row)
    return rows


def _layer_rows() -> List[Dict[str, Any]]:
    return [
        {"Depth from [m]": 0.0, "Depth to [m]": 3.0, "Soil type": "Sand", "Total unit weight [kN/m3]": 18.0,
         "Submerged unit weight [kN/m3]": 9.0, "Friction angle [deg]": 32.0, "Undrained shear strength [kPa]": 0.0, "Cc [-]": 0.0, "Cr [-]": 0.0, "e0 [-]": 0.6, "K [-]": 0.4, "Interface friction angle [deg]": 24.0},
        {"Depth from [m]": 3.0, "Depth to [m]": 8.0, "Soil type": "Clay", "Total unit weight [kN/m3]": 17.0,
         "Submerged unit weight [kN/m3]": 7.0, "Friction angle [deg]": 0.0, "Undrained shear strength [kPa]": 50.0, "Cc [-]": 0.3, "Cr [-]": 0.05, "e0 [-]": 1.0, "K [-]": 0.5, "Interface friction angle [deg]": 15.0},
        {"Depth from [m]": 8.0, "Depth to [m]": 15.0, "Soil type": "Sand", "Total unit weight [kN/m3]": 19.0,
         "Submerged unit weight [kN/m3]": 10.0, "Friction angle [deg]": 35.0, "Undrained shear strength [kPa]": 0.0, "Cc [-]": 0.0, "Cr [-]": 0.0, "e0 [-]": 0.6, "K [-]": 0.4, "Interface friction angle [deg]": 24.0},
    ]


def _piletest_rows() -> List[Dict[str, Any]]:
    loads = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600]
    settlements = [0.0, 1.1, 2.5, 4.3, 6.8, 10.2, 15.0, 22.0, 32.0]
    # Uploaded through the soil-profile path like any table, which needs depth intervals.
    return [{"Depth from [m]": float(i), "Depth to [m]": float(i + 1), "Load [kN]": f, "Settlement [mm]": w}
            for i, (f, w) in enumerate(zip(loads, settlements))]


FIXTURES = {
    "@piletest_table": lambda: {"raw_data": _piletest_rows(), "data_kind": "soil_profile"},
    "@cpt_profile": lambda: {"raw_data": _cpt_rows({"Tertiary clay": False, "Ignore shaft friction": False}),
                             "data_kind": "soil_profile"},
    "@layer_profile": lambda: {"raw_data": _layer_rows(), "data_kind": "soil_profile"},
}


#: "@name" strings replaced by the data itself (e.g. the rows a soil-profile upload posts).
DATA_FIXTURES = {"@layer_rows": _layer_rows, "@cpt_rows": _cpt_rows}


def _resolve(args: Any, client, made: Dict[str, str]) -> Any:
    """Replace "@fixture" strings by the id of a saved object created for this run, or by fixture data."""
    if isinstance(args, dict):
        return {k: _resolve(v, client, made) for k, v in args.items()}
    if isinstance(args, list):
        return [_resolve(v, client, made) for v in args]
    if isinstance(args, str) and args in DATA_FIXTURES:
        return DATA_FIXTURES[args]()
    if isinstance(args, str) and args in FIXTURES:
        if args not in made:
            resp = client.post("/api/execute", json={"moduleId": "general", "functionId": "SoilProfile",
                                                     "args": FIXTURES[args]()}).json()
            made[args] = resp.get("id") or f"<fixture {args} failed: {str(resp)[:80]}>"
        return made[args]
    return args


def run_case(client, case: Dict[str, Any], made: Dict[str, str], envelope_problems: Optional[List[str]] = None) -> Any:
    body = {"moduleId": case.get("module", "golden"), "functionId": case["function"],
            "args": _resolve(case.get("args", {}), client, made)}
    resp = client.post("/api/execute", json=body)
    try:
        payload = resp.json()
    except ValueError:
        payload = {"__non_json__": resp.text[:500]}
    if envelope_problems is not None:
        envelope_problems.extend(_check_envelope(case["function"], payload))
    return {"http": resp.status_code, "body": fingerprint(payload)}


def _check_envelope(function_id: str, payload: Any) -> List[str]:
    """core.catalogue.envelope must read a response without changing it and stay JSON-encodable."""
    import copy
    from core.catalogue.envelope import envelope
    before = copy.deepcopy(payload)
    try:
        env = envelope(function_id, payload)
        json.dumps(env, allow_nan=True)
    except Exception as e:  # noqa: BLE001 - reported per calculation
        return [f"{function_id}: envelope raised {type(e).__name__}: {e}"]
    problems = []
    if env["raw"] is not payload or payload != before:
        problems.append(f"{function_id}: envelope changed or replaced the raw response")
    if env["calculation"] is None and function_id not in _internal_ids():
        problems.append(f"{function_id}: not found in the catalogue")
    return problems


def _internal_ids():
    from core.catalogue import load_catalogue
    return set(load_catalogue()["internal"])


def load_cases() -> List[Dict[str, Any]]:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]


#: Libraries whose version changes numbers or payload shapes; the baseline is only comparable on the same
#: major.minor versions (requirements.txt does not pin them, so CI may resolve older ones).
ENV_LIBRARIES = ("numpy", "pandas", "scipy", "plotly", "matplotlib")


def environment() -> Dict[str, str]:
    import importlib
    env = {"python": f"{sys.version_info.major}.{sys.version_info.minor}"}
    for name in ENV_LIBRARIES:
        try:
            env[name] = importlib.import_module(name).__version__
        except Exception:
            env[name] = "missing"
    return env


def environment_mismatch(recorded: Dict[str, str]) -> List[str]:
    """Libraries whose major.minor version differs from the one the baseline was recorded with."""
    now = environment()
    mm = lambda v: ".".join(str(v).split(".")[:2])  # noqa: E731
    return [f"{k} {recorded.get(k)} (recorded) vs {now[k]}" for k in ENV_LIBRARIES if mm(recorded.get(k)) != mm(now[k])]


def record() -> None:
    client = make_client()
    made: Dict[str, str] = {}
    outputs = {}
    for case in load_cases():
        outputs[case["name"]] = run_case(client, case, made)
    OUTPUTS_PATH.write_text(json.dumps({"_comment": "Generated by `python tests/golden/golden_tools.py record`. "
                                        "Re-record only when an output change is intended and reviewed.",
                                        "environment": environment(), "outputs": outputs},
                                       indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"recorded {len(outputs)} cases -> {OUTPUTS_PATH}")


def summary(outputs: Dict[str, Any]) -> Dict[str, List[str]]:
    """Cases by outcome: ok, error (an error/status key or HTTP != 200)."""
    out: Dict[str, List[str]] = {"ok": [], "error": []}
    for name, res in outputs.items():
        body = res.get("body")
        bad = res.get("http") != 200 or (isinstance(body, dict) and (
            "error" in body or body.get("status") in ("Error", "ValidationError")))
        out["error" if bad else "ok"].append(name)
    return out


def check() -> int:
    """Re-run every case and compare with outputs.json. Prints a JSON report; returns the number of changed cases."""
    expected = json.loads(OUTPUTS_PATH.read_text(encoding="utf-8"))["outputs"]
    client = make_client()
    made: Dict[str, str] = {}
    changed: Dict[str, List[str]] = {}
    envelope_problems: List[str] = []
    cases = load_cases()
    for case in cases:
        actual = run_case(client, case, made, envelope_problems)
        if case["name"] not in expected:
            changed[case["name"]] = ["no recorded output: record the baseline for this new case"]
            continue
        if case.get("compare") == "status":  # output depends on a random object id: compare the status only
            exp = expected[case["name"]]
            diff = [] if exp.get("http") == actual.get("http") else [f"http {exp.get('http')} -> {actual.get('http')}"]
        else:
            diff = differences(expected[case["name"]], actual)
        if diff:
            changed[case["name"]] = diff
    missing = sorted(set(expected) - {c["name"] for c in cases})
    print(json.dumps({"cases": len(cases), "changed": changed, "recorded_but_no_case": missing,
                      "envelope_problems": envelope_problems}, indent=1))
    return len(changed) + len(missing) + len(envelope_problems)


if __name__ == "__main__":
    if sys.argv[1:] == ["record"]:
        record()
    elif sys.argv[1:] == ["check"]:
        sys.exit(1 if check() else 0)
    else:
        print(__doc__)
