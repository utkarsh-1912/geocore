"""
Tests for the groundhog function manifest (fast backend start-up):
manifest vs eager scan equivalence, lazy invocation, stale-cache fallback,
and the background warm-up gate.
"""
import asyncio
import inspect
import json
import math
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

from core import function_manifest as fm
from core import warmup
from core.registry import Registry
from core.geoai.schema_factory import build_schema_for_function

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _same(a, b):
    """Exact equality that also treats NaN == NaN and checks container types."""
    if type(a) is not type(b):
        return False
    if isinstance(a, float):
        return (math.isnan(a) and math.isnan(b)) or a == b
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    return a == b


def _schema_or_error(name, obj):
    try:
        return build_schema_for_function(name, obj).model_json_schema()
    except Exception as e:  # compare failure modes too
        return ("error", type(e).__name__)


@pytest.fixture(scope="module")
def eager_map():
    return fm.scan_groundhog()


@pytest.fixture(scope="module")
def lazy_map(eager_map):
    # Round-trip through JSON exactly as the on-disk manifest does
    manifest = json.loads(json.dumps(fm.build_manifest(eager_map)))
    return fm.function_map_from_manifest(manifest)


# ---------------------------------------------------------------------------
# Manifest == eager scan
# ---------------------------------------------------------------------------

def test_manifest_has_same_functions_in_same_order(eager_map, lazy_map):
    assert len(eager_map) > 100
    assert list(lazy_map) == list(eager_map)


def test_manifest_metadata_matches_eager_scan(eager_map, lazy_map):
    for name, real in eager_map.items():
        lazy = lazy_map[name]
        assert lazy.__name__ == real.__name__, name
        assert lazy.__module__ == real.__module__, name
        assert lazy.__doc__ == real.__doc__, name
        assert inspect.getdoc(lazy) == inspect.getdoc(real), name

        real_params = list(inspect.signature(real).parameters.values())
        lazy_params = list(inspect.signature(lazy).parameters.values())
        assert [(p.name, p.kind) for p in lazy_params] == [(p.name, p.kind) for p in real_params], name
        for rp, lp in zip(real_params, lazy_params):
            assert _same(lp.default, rp.default), f"{name}.{rp.name}"


def test_manifest_geoai_schemas_match_eager_scan(eager_map, lazy_map):
    for name in eager_map:
        assert _schema_or_error(name, lazy_map[name]) == _schema_or_error(name, eager_map[name]), name


def test_committed_manifest_is_current(eager_map):
    """The shipped core/function_manifest.json must match the installed groundhog.

    If this fails, regenerate it with:  python -m core.function_manifest
    """
    lazy, source = fm.load_function_map(fm.MANIFEST_PATH, write_cache=False)
    assert source == "manifest"
    assert list(lazy) == list(eager_map)


def test_registry_uses_lazy_objects_without_importing_groundhog_modules():
    code = (
        "import sys, core.registry as r\n"
        "heavy = [m for m in ('core.wrappers', 'scipy.optimize', 'matplotlib.pyplot',\n"
        "         'groundhog.general.soilprofile', 'groundhog.shallowfoundations.capacity') if m in sys.modules]\n"
        "assert not heavy, heavy\n"
        "obj = r.registry.function_map['bulkunitweight']\n"
        "assert type(obj).__name__ == 'LazyGroundhogCallable', type(obj)\n"
        "print('ok')\n"
    )
    out = subprocess.run([sys.executable, "-c", code], cwd=BACKEND_ROOT,
                         capture_output=True, text=True, timeout=300)
    assert out.returncode == 0, out.stderr
    assert "ok" in out.stdout


# ---------------------------------------------------------------------------
# Lazy invocation == eager invocation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name, kwargs", [
    ("bulkunitweight", {"voidratio": 0.65, "saturation": 0.8, "specific_gravity": 2.65}),
    ("gmax_shearwavevelocity", {"Vs": 250.0, "gamma": 19.0}),
    ("earthpressurecoefficients_rankine", {"phi_eff": 30.0, "wall_angle": 0.0, "top_angle": 0.0}),
    ("hydraulicconductivity_unconfinedaquifer", {
        "radius_1": 10.0, "radius_2": 50.0, "piezometric_height_1": 18.0,
        "piezometric_height_2": 20.0, "flowrate": 0.05}),
])
def test_lazy_call_matches_eager_call(eager_map, lazy_map, name, kwargs):
    assert _same(lazy_map[name](**kwargs), eager_map[name](**kwargs))


def test_lazy_class_constructs_real_class(eager_map, lazy_map):
    real_cls = eager_map["PCPTProcessing"]
    instance = lazy_map["PCPTProcessing"](title="lazy")
    assert isinstance(instance, real_cls)
    assert lazy_map["PCPTProcessing"].resolve() is real_cls


@pytest.mark.parametrize("function_id, args", [
    ("gmax_shearwavevelocity", {"Vs": 250.0, "gamma": 19.0, "g": 9.81}),
    ("earthpressurecoefficients_rankine", {"phi_eff": 30.0, "wall_angle": 0.0, "top_angle": 0.0}),
    ("hydraulicconductivity_unconfinedaquifer", {
        "radius_1": 10.0, "radius_2": 50.0, "piezometric_height_1": 18.0,
        "piezometric_height_2": 20.0, "flowrate": 0.05}),
    ("voidratio_bulkunitweight", {"bulkunitweight": 18.0, "saturation": 1.0}),
])
def test_registry_execute_lazy_matches_eager(eager_map, function_id, args):
    lazy_registry = Registry()
    assert isinstance(lazy_registry.function_map[function_id], fm.LazyGroundhogCallable)

    eager_registry = Registry.__new__(Registry)
    eager_registry.modules = {}
    eager_registry.function_map = dict(eager_map)

    lazy_result = lazy_registry.execute_function("m", function_id, dict(args))
    eager_result = eager_registry.execute_function("m", function_id, dict(args))
    assert lazy_result == eager_result
    assert "error" not in lazy_result


# ---------------------------------------------------------------------------
# Cache validity / fallback
# ---------------------------------------------------------------------------

def test_stale_manifest_falls_back_to_eager_scan_and_is_rewritten(tmp_path, eager_map):
    path = tmp_path / "function_manifest.json"
    manifest = fm.build_manifest(eager_map)
    manifest["fingerprint"]["groundhog_modules"] = manifest["fingerprint"]["groundhog_modules"][:-1]
    manifest["functions"] = manifest["functions"][:5]  # stale content must not be served
    fm.save_manifest(manifest, str(path))

    function_map, source = fm.load_function_map(str(path), write_cache=True)
    assert source == "scan"
    assert list(function_map) == list(eager_map)
    assert all(not isinstance(v, fm.LazyGroundhogCallable) for v in function_map.values())

    # Rewritten with the current fingerprint -> next start uses it
    function_map, source = fm.load_function_map(str(path), write_cache=False)
    assert source == "manifest"
    assert list(function_map) == list(eager_map)


@pytest.mark.parametrize("key, value", [
    ("format", -1),
    ("python", "2.7"),
    ("groundhog_version", "0.0.0-other"),
    ("groundhog_source_hash", "0" * 64),
])
def test_any_fingerprint_change_invalidates(key, value):
    current = fm.compute_fingerprint()
    stored = dict(current, **{key: value})
    if current.get(key) is None:
        pytest.skip(f"{key} not determinable in this environment")
    assert not fm.fingerprint_matches(stored, current)
    assert fm.fingerprint_matches(dict(current), current)


def test_undeterminable_fields_are_not_compared():
    # e.g. frozen build: no .py sources on disk / no dist-info metadata
    current = dict(fm.compute_fingerprint(), groundhog_version=None, groundhog_source_hash=None)
    stored = dict(current, groundhog_version="0.15.0", groundhog_source_hash="abc")
    assert fm.fingerprint_matches(stored, current)


def test_missing_or_corrupt_manifest_falls_back(tmp_path):
    function_map, source = fm.load_function_map(str(tmp_path / "missing.json"), write_cache=False)
    assert source == "scan" and len(function_map) > 100

    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text("{not json", encoding="utf-8")
    function_map, source = fm.load_function_map(str(corrupt), write_cache=False)
    assert source == "scan" and len(function_map) > 100


# ---------------------------------------------------------------------------
# Default value encoding
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value", [
    None, True, 0, 1.5, "Sand", float("nan"), float("inf"), float("-inf"),
    [], [[]], (0, 100), {"Sand": "yellow"}, {"a": [1, (2.0, None)], "$float": "x"},
])
def test_default_encoding_round_trips(value):
    encoded = json.loads(json.dumps(fm._encode_value(value)))
    assert _same(fm._decode_value(encoded), value)


def _function_with_object_default(x=object()):
    return x


def test_unencodable_default_is_imported_eagerly():
    with pytest.raises(fm.ManifestError):
        fm._encode_value(object())
    manifest = fm.build_manifest({"_function_with_object_default": _function_with_object_default},
                                 fingerprint={})
    assert manifest["functions"][0].get("eager") is True
    function_map = fm.function_map_from_manifest(json.loads(json.dumps(manifest)))
    assert function_map["_function_with_object_default"] is _function_with_object_default


# ---------------------------------------------------------------------------
# Warm-up gate
# ---------------------------------------------------------------------------

def test_warmup_gate_blocks_until_task_done(monkeypatch):
    monkeypatch.setattr(warmup, "_thread", None)
    monkeypatch.setattr(warmup, "_done", threading.Event())
    warmup._done.set()
    warmup.wait_for_warmup()  # no warm-up started: returns immediately

    finished = []
    ready = threading.Event()

    def task():
        warmup.wait_for_warmup()  # the warm-up thread itself must never block on itself
        time.sleep(0.2)
        finished.append(True)

    assert warmup.start_background_warmup(task, ready=ready.is_set)
    assert not warmup.start_background_warmup(task)  # only once
    assert not finished
    ready.set()
    warmup.wait_for_warmup()
    assert finished == [True]
    asyncio.run(warmup.wait_for_warmup_async())


# ---------------------------------------------------------------------------
# Saved objects are restored lazily (not at import), with identical content
# ---------------------------------------------------------------------------

def test_state_manager_restores_saved_objects_on_first_access(tmp_path, monkeypatch):
    from core.state import StateManager

    saved = [{
        "id": "abc", "type": "SoilProfile", "name": "Profile A", "timestamp": "now",
        "data": [{"Depth from [m]": 0.0, "Depth to [m]": 2.0, "Soil type": "SAND"}],
    }]
    (tmp_path / "saved_objects.json").write_text(json.dumps(saved), encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    manager = StateManager()
    assert manager._loaded is False and manager._objects_store == {}

    assert manager.list_by_type("SoilProfile") == [
        {"id": "abc", "type": "SoilProfile", "name": "Profile A", "timestamp": "now"}]
    from groundhog.general.soilprofile import SoilProfile
    assert isinstance(manager.get("abc"), SoilProfile)
    assert "abc" in manager._metadata  # direct access (core.geoai.data_access) also loads
