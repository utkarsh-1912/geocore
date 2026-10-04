# Author: Utkarsh Gupta
# License: GPL v3
"""
Deterministic synthetic GeoCore project for GeoAI dataset generation, evaluation and
tests (AGENTS.md §9, §14, §21, §25, §28).

Project-context examples ("calculate X using the current project") need a project state
whose tool results are reproducible byte for byte. This module builds one:

* three CPT soundings stored the way the desktop app stores a "Soil Profile (w/ CPT Data)"
  upload -- ``SoilProfile`` tables with units in the column headers:
  ``CPT-01`` (to 22 m, groundwater column), ``CPT-02`` (to 15 m, qc stored in **kPa**,
  no u2, no groundwater) and ``CPT-03`` (to 26 m, groundwater column);
* one layered borehole soil profile ``BH-01`` (made ground / sand / soft clay / stiff
  clay / dense sand, water table 2.0 m) with unit weight, phi', su, Cc, Cr, e0, OCR.

``loaded(FIXTURE)`` installs it behind the same seams the tools read from, without touching
the user's saved workspace or the global ``state_manager``:

* project CPTs  -> ``core.geoai.tools_cpt_piles._store`` returns a private, in-memory
  ``core.state.StateManager`` holding the objects above (fixed object ids, never saved);
* project soil  -> ``core.geoai.project_soil.load_project_context`` returns a
  ``ProjectContext`` whose only profile is ``BH-01`` (as the active GeoAI project would).

``loaded(EMPTY)`` installs an empty project, so examples that must NOT find project data
(missing-parameter cases) never depend on the developer's workspace.

The context string the agent sees is ``compact_context()`` -- exactly
``ProjectContext.get_compact_context_string()`` as ``build_system_prompt`` injects it.
"""
from contextlib import contextmanager
from typing import Dict, Iterator, Optional

import numpy as np
import pandas as pd

FIXTURE = "synthetic_v1"
EMPTY = "empty"
FIXTURES = (FIXTURE, EMPTY)

PROJECT_ID = "synthetic_v1"
PROJECT_NAME = "Riverside Logistics Hub (synthetic)"
PROFILE_NAME = "BH-01"
WATER_TABLE_M = 2.0

#: CPT id -> (object name in the store, final depth [m], qc scale, clay/sand boundary shift [m])
CPT_SPECS = {
    "CPT-01": ("CPT-01.xlsx", 22.0, 1.00, 0.0),
    "CPT-02": ("CPT-02.xlsx", 15.0, 0.90, 0.5),
    "CPT-03": ("CPT-03.xlsx", 26.0, 1.10, -0.4),
}
CPT_LOCATIONS = {"CPT-01": (512300.0, 181200.0), "CPT-02": (512340.0, 181215.0), "CPT-03": (512385.0, 181240.0)}
CPT_DZ_M = 0.2   # coarse spacing keeps Groundhog runs fast and outputs compact


def _cpt_channels(z: np.ndarray, scale: float, shift: float):
    """Layered qc [MPa], fs [kPa], u2 [kPa] consistent with the BH-01 stratigraphy."""
    b1, b2, b3 = 1.0, 4.0 + shift, 9.0 + shift
    b4 = 16.0 + shift
    qc = np.select(
        [z < b1, z < b2, z < b3, z < b4],
        [np.full_like(z, 2.5), 8.0 + 1.5 * (z - b1), 0.6 + 0.05 * (z - b2), 1.8 + 0.1 * (z - b3)],
        15.0 + 0.8 * (z - b4)) * scale
    fs = np.select([z < b1, z < b2, z < b3, z < b4], [25.0, 60.0, 15.0, 70.0], 120.0)
    hydro = np.clip(10.0 * (z - WATER_TABLE_M), 0.0, None)
    u2 = np.select([z < b2, z < b3, z < b4], [hydro, hydro + 80.0, hydro + 200.0], hydro)
    return np.round(qc, 3), fs, np.round(u2, 1)


def cpt_tables() -> Dict[str, pd.DataFrame]:
    """CPT id -> stored table (units in the headers, as uploaded)."""
    out = {}
    for cpt_id, (_name, z_end, scale, shift) in CPT_SPECS.items():
        z = np.round(np.arange(CPT_DZ_M, z_end + 1e-9, CPT_DZ_M), 2)
        qc, fs, u2 = _cpt_channels(z, scale, shift)
        east, north = CPT_LOCATIONS[cpt_id]
        if cpt_id == "CPT-02":        # qc exported in kPa, no pore pressure, no groundwater record
            df = pd.DataFrame({"Depth [m]": z, "qc [kPa]": np.round(qc * 1000.0, 0), "fs [kPa]": fs})
        else:
            df = pd.DataFrame({"z [m]": z, "qc [MPa]": qc, "fs [kPa]": fs, "u2 [kPa]": u2,
                               "Water table depth [m]": WATER_TABLE_M})
        df["Easting [m]"] = east
        df["Northing [m]"] = north
        out[cpt_id] = df
    return out


def soil_profile_table() -> pd.DataFrame:
    """BH-01 layered soil profile (0 in a column = parameter not defined for that layer)."""
    return pd.DataFrame({
        "Depth from [m]": [0.0, 1.0, 4.0, 9.0, 16.0],
        "Depth to [m]": [1.0, 4.0, 9.0, 16.0, 30.0],
        "Soil type": ["Made ground", "Medium dense sand", "Soft clay", "Stiff clay", "Dense sand"],
        "UnitWeight [kN_m3]": [18.0, 18.5, 17.0, 19.0, 20.0],
        "FrictionAngle [deg]": [28.0, 32.0, 0.0, 0.0, 36.0],
        "Su [kPa]": [0.0, 0.0, 30.0, 85.0, 0.0],
        "Cc [-]": [0.0, 0.0, 0.35, 0.18, 0.0],
        "Cr [-]": [0.0, 0.0, 0.06, 0.03, 0.0],
        "e0 [-]": [0.0, 0.0, 1.3, 0.85, 0.0],
        "OCR [-]": [0.0, 0.0, 1.0, 2.5, 0.0],
        "WaterTable [m]": [WATER_TABLE_M] * 5,
    })


def _soil_profile(df: pd.DataFrame):
    """Wrap in Groundhog ``SoilProfile`` only if the table has the required columns.

    CPT sounding tables use ``'z [m]'`` or ``'Depth [m]'`` — not the
    ``'Depth from [m]'`` that ``SoilProfile`` requires — so they stay as plain
    DataFrames.
    """
    if "Depth from [m]" not in df.columns:
        return df
    try:
        from groundhog.general.soilprofile import SoilProfile
        return SoilProfile(df)
    except ImportError:  # pragma: no cover
        return df


def build_state_manager(empty: bool = False):
    """A private in-memory ``StateManager`` with the project objects (fixed ids; never saved)."""
    from core.state import StateManager
    sm = StateManager()
    sm._loaded = True                       # no disk read, and nothing here calls store()/_save_to_disk
    if empty:
        return sm
    # Data kinds as recorded by the desktop upload (core.state.DATA_KINDS).
    objects = [(f"synthetic-{cpt_id.lower()}", "SoilProfile", CPT_SPECS[cpt_id][0], _soil_profile(df), "cpt")
               for cpt_id, df in cpt_tables().items()]
    objects.append(("synthetic-bh-01", "SoilProfile", PROFILE_NAME, _soil_profile(soil_profile_table()),
                    "soil_profile"))
    for obj_id, type_name, name, obj, kind in objects:
        sm._objects_store[obj_id] = obj
        sm._metadata_store[obj_id] = {"id": obj_id, "type": type_name, "name": name, "timestamp": "synthetic",
                                      "kind": kind}
    return sm


def build_project_context(empty: bool = False):
    """The GeoAI ``ProjectContext`` (soil profile BH-01 only; CPTs are reached through the tools)."""
    from core.geoai.data_access import ProjectContext
    if empty:
        return ProjectContext("empty", "Empty project")
    ctx = ProjectContext(PROJECT_ID, PROJECT_NAME)
    ctx.water_table_depth = WATER_TABLE_M
    ctx.add_profile(PROFILE_NAME, soil_profile_table())
    return ctx


def compact_context() -> str:
    """Project context exactly as the system prompt shows it (``get_compact_context_string``)."""
    return build_project_context().get_compact_context_string()


def eval_context(fixture: Optional[str]) -> Optional[Dict[str, str]]:
    """``EvalExample.context`` for a fixture (None for the empty project)."""
    return {"project_context": compact_context()} if fixture == FIXTURE else None


@contextmanager
def loaded(fixture: Optional[str] = FIXTURE) -> Iterator[None]:
    """
    Make ``fixture`` the current project for the CPT and soil-profile tools; restores the
    previous hooks on exit. ``None`` is a no-op (the real workspace is used).
    """
    if fixture is None:
        yield
        return
    if fixture not in FIXTURES:
        raise ValueError(f"unknown project fixture {fixture!r} (expected one of {FIXTURES})")
    import core.geoai.project_soil as project_soil
    import core.geoai.tools_cpt_piles as tools_cpt_piles
    empty = fixture == EMPTY
    store = build_state_manager(empty=empty)
    ctx = build_project_context(empty=empty)
    old_store, old_loader = tools_cpt_piles._store, project_soil.load_project_context
    tools_cpt_piles._store = lambda: store
    project_soil.load_project_context = lambda: ctx
    try:
        yield
    finally:
        tools_cpt_piles._store = old_store
        project_soil.load_project_context = old_loader
