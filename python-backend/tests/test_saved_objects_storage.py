# Author: Utkarsh Gupta
# License: GPL v3
"""
Per-user storage of saved objects: config-dir resolution, first-run migration
from the legacy working-directory file, and atomic writes.
"""
import json
import os
from pathlib import Path

import pandas as pd
import pytest

from core import paths, state
from core.paths import CONFIG_DIR_ENV_VAR, get_config_dir
from core.state import SAVED_OBJECTS_FILENAME, StateManager, resolve_saved_objects_path

SAVED = [{
    "id": "abc", "type": "SoilProfile", "name": "Profile A", "timestamp": "now",
    "data": [{"Depth from [m]": 0.0, "Depth to [m]": 2.0, "Soil type": "SAND"}],
}]


@pytest.fixture
def dirs(tmp_path, monkeypatch):
    """Isolated config dir, working dir and backend dir (the repo's own
    python-backend/saved_objects.json must not leak into these tests)."""
    config = tmp_path / "config"
    cwd = tmp_path / "cwd"
    backend = tmp_path / "backend"
    cwd.mkdir()
    backend.mkdir()
    monkeypatch.setenv(CONFIG_DIR_ENV_VAR, str(config))
    monkeypatch.chdir(cwd)
    monkeypatch.setattr(state, "_BACKEND_DIR", backend)
    return config, cwd, backend


def _write(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


# ---------------------------------------------------------------------------
# Config directory
# ---------------------------------------------------------------------------

def test_config_dir_env_override_is_created(tmp_path, monkeypatch):
    target = tmp_path / "custom" / "geocore"
    monkeypatch.setenv(CONFIG_DIR_ENV_VAR, str(target))
    assert get_config_dir() == target
    assert target.is_dir()


def test_config_dir_falls_back_to_home_dot_geocore(tmp_path, monkeypatch):
    monkeypatch.delenv(CONFIG_DIR_ENV_VAR, raising=False)
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setattr(paths.Path, "home", classmethod(lambda cls: tmp_path))
    assert get_config_dir() == tmp_path / ".geocore"
    assert (tmp_path / ".geocore").is_dir()


@pytest.mark.skipif(os.name != "nt", reason="APPDATA is only used on Windows")
def test_config_dir_uses_appdata_on_windows(tmp_path, monkeypatch):
    monkeypatch.delenv(CONFIG_DIR_ENV_VAR, raising=False)
    monkeypatch.setenv("APPDATA", str(tmp_path))
    assert get_config_dir() == tmp_path / "GeoCore"


def test_geoai_model_config_shares_the_helper():
    from core.geoai import model_config
    assert model_config.get_config_dir is get_config_dir


# ---------------------------------------------------------------------------
# Path resolution and migration
# ---------------------------------------------------------------------------

def test_resolve_without_any_file_points_into_config_dir(dirs):
    config, _, _ = dirs
    path = resolve_saved_objects_path()
    assert path == config / SAVED_OBJECTS_FILENAME
    assert not path.exists()


def test_legacy_file_in_working_directory_is_migrated(dirs):
    config, cwd, _ = dirs
    legacy = cwd / SAVED_OBJECTS_FILENAME
    _write(legacy, SAVED)

    path = resolve_saved_objects_path()

    assert path == config / SAVED_OBJECTS_FILENAME
    assert json.loads(path.read_text(encoding="utf-8")) == SAVED
    assert legacy.exists()  # left in place: the install folder may be read-only
    assert not list(config.glob("*.tmp"))


def test_legacy_file_in_backend_directory_is_migrated(dirs):
    config, _, backend = dirs
    _write(backend / SAVED_OBJECTS_FILENAME, SAVED)
    path = resolve_saved_objects_path()
    assert json.loads(path.read_text(encoding="utf-8")) == SAVED


def test_working_directory_takes_precedence_over_backend_directory(dirs):
    _, cwd, backend = dirs
    from_cwd = [dict(SAVED[0], name="from cwd")]
    _write(cwd / SAVED_OBJECTS_FILENAME, from_cwd)
    _write(backend / SAVED_OBJECTS_FILENAME, SAVED)
    path = resolve_saved_objects_path()
    assert json.loads(path.read_text(encoding="utf-8")) == from_cwd


def test_existing_config_file_is_not_overwritten_by_legacy(dirs):
    config, cwd, _ = dirs
    current = [dict(SAVED[0], name="current")]
    _write(config / SAVED_OBJECTS_FILENAME, current)
    _write(cwd / SAVED_OBJECTS_FILENAME, SAVED)
    path = resolve_saved_objects_path()
    assert json.loads(path.read_text(encoding="utf-8")) == current


# ---------------------------------------------------------------------------
# StateManager integration
# ---------------------------------------------------------------------------

def test_state_manager_resolves_and_migrates_lazily(dirs):
    config, cwd, _ = dirs
    _write(cwd / SAVED_OBJECTS_FILENAME, SAVED)

    manager = StateManager()
    assert manager._loaded is False
    assert not config.exists()  # nothing resolved or migrated at construction

    assert [m["id"] for m in manager.list_by_type("SoilProfile")] == ["abc"]
    assert manager.path == config / SAVED_OBJECTS_FILENAME
    assert manager.path.exists()


def test_state_manager_saves_to_config_dir_not_working_directory(dirs):
    config, cwd, _ = dirs
    manager = StateManager()
    df = pd.DataFrame([{"Depth from [m]": 0.0, "Depth to [m]": 1.0, "Soil type": "CLAY"}])
    obj_id = manager.store(df, "SoilProfile", name="Stored")

    saved = json.loads((config / SAVED_OBJECTS_FILENAME).read_text(encoding="utf-8"))
    assert [(o["id"], o["name"]) for o in saved] == [(obj_id, "Stored")]
    assert not (cwd / SAVED_OBJECTS_FILENAME).exists()
    assert not list(config.glob("*.tmp"))

    manager.delete(obj_id)
    assert json.loads((config / SAVED_OBJECTS_FILENAME).read_text(encoding="utf-8")) == []


def test_failed_save_keeps_previous_file_and_cleans_temp(dirs, monkeypatch):
    config, _, _ = dirs
    _write(config / SAVED_OBJECTS_FILENAME, SAVED)
    manager = StateManager()
    manager.ensure_loaded()
    before = (config / SAVED_OBJECTS_FILENAME).read_bytes()

    def failing_replace(src, dst):
        raise OSError("disk full")
    monkeypatch.setattr(state.os, "replace", failing_replace)

    df = pd.DataFrame([{"Depth from [m]": 0.0, "Depth to [m]": 1.0, "Soil type": "CLAY"}])
    manager.store(df, "SoilProfile")  # save error is reported, not raised

    assert (config / SAVED_OBJECTS_FILENAME).read_bytes() == before
    assert not list(config.glob("*.tmp"))
