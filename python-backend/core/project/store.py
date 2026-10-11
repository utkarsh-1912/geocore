# Author: Utkarsh Gupta
# License: GPL v3
"""
The project ground model: one SQLite file per GeoCore config folder (``project.sqlite``).

It does not replace the existing workspace storage. Soil profiles, CPT tables and grids stay in
saved_objects.json, where the forms read them; ``sync_from_workspace`` (core/project/ground.py) indexes them here as
locations, layers and parameters, each parameter with its source. On top of that the project keeps what the
workspace has no place for: calculation runs, the parameters derived from them, and the links between them
(core/project/runs.py), so results can be traced and flagged when an input changes.

Tables
    meta(key, value)
    locations(id, name, kind, source_object, groundwater_m, synced_at)
    layers(id, location_id, idx, top_m, bottom_m, soil_type)
    parameters(id, location_id, layer_id, column_name, quantity, value, unit, source_kind, source_ref, param_key,
               created_at)                                 -- param_key: "<profile id>|<column>|<layer>" or "run:<id>|<key>"
    runs(id, function_id, calculation, method, status, inputs_json, results_json, created_at, location_id)
    run_inputs(run_id, name, value, param_key)             -- what each run consumed, by a key that survives re-sync
"""
import json
import os
import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

SCHEMA_VERSION = 1
_lock = threading.RLock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, kind TEXT NOT NULL, source_object TEXT UNIQUE,
    groundwater_m REAL, synced_at REAL);
CREATE TABLE IF NOT EXISTS layers (
    id INTEGER PRIMARY KEY, location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    idx INTEGER NOT NULL, top_m REAL NOT NULL, bottom_m REAL NOT NULL, soil_type TEXT);
CREATE TABLE IF NOT EXISTS parameters (
    id INTEGER PRIMARY KEY, location_id INTEGER REFERENCES locations(id) ON DELETE CASCADE,
    layer_id INTEGER REFERENCES layers(id) ON DELETE CASCADE, column_name TEXT, quantity TEXT,
    value REAL NOT NULL, unit TEXT, source_kind TEXT NOT NULL, source_ref TEXT, param_key TEXT, created_at REAL);
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY, function_id TEXT NOT NULL, calculation TEXT, method TEXT, status TEXT,
    inputs_json TEXT NOT NULL, results_json TEXT NOT NULL, created_at REAL NOT NULL,
    location_id INTEGER REFERENCES locations(id) ON DELETE SET NULL, note TEXT);
CREATE TABLE IF NOT EXISTS run_inputs (
    run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE, name TEXT NOT NULL, value REAL,
    param_key TEXT, source TEXT);
CREATE TABLE IF NOT EXISTS run_reviews (
    run_id INTEGER PRIMARY KEY REFERENCES runs(id) ON DELETE CASCADE, reviewer TEXT NOT NULL, note TEXT,
    reviewed_at REAL NOT NULL);
CREATE INDEX IF NOT EXISTS ix_parameters_layer ON parameters(layer_id);
CREATE INDEX IF NOT EXISTS ix_parameters_quantity ON parameters(quantity);
CREATE INDEX IF NOT EXISTS ix_parameters_key ON parameters(param_key);
CREATE INDEX IF NOT EXISTS ix_run_inputs_key ON run_inputs(param_key);
"""


def project_path() -> Path:
    from core.paths import get_config_dir
    override = os.environ.get("GEOCORE_PROJECT_DB")
    return Path(override) if override else get_config_dir() / "project.sqlite"


@contextmanager
def connect(path: Optional[Path] = None) -> Iterator[sqlite3.Connection]:
    """A connection with foreign keys on and the schema in place; commits on success."""
    with _lock:
        db = sqlite3.connect(str(path or project_path()), timeout=10)
        try:
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA foreign_keys = ON")
            db.executescript(SCHEMA)
            if db.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchone() is None:
                db.execute("INSERT INTO meta (key, value) VALUES ('schema_version', ?), ('created_at', ?)",
                           (str(SCHEMA_VERSION), str(time.time())))
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


def row_dict(row: sqlite3.Row) -> Dict[str, Any]:
    d = dict(row)
    for key in ("inputs_json", "results_json"):
        if key in d and isinstance(d[key], str):
            d[key[:-5]] = json.loads(d.pop(key))
    return d
