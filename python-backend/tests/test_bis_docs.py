# Author: Utkarsh Gupta
# License: GPL v3
"""
Guide & Theory docs for the Indian Standard (BIS) calculators (website/_build/bis_docs.py -> functionDocs.json).

Every BIS calculator must have a guide entry, and the documented parameters must be the function's own: the
docs are generated from the implementation's docstrings, so a renamed or added argument fails here until the
docs are regenerated (python website/_build/app_docs.py).
"""
import importlib.util
import inspect
import json
from pathlib import Path

import pytest

from core.standards.bis import BIS_FUNCTIONS

REPO = Path(__file__).resolve().parents[2]
DOCS_JSON = REPO / "electron-app" / "src" / "features" / "calculations" / "guide" / "functionDocs.json"


def _bis_docs():
    spec = importlib.util.spec_from_file_location("bis_docs", REPO / "website" / "_build" / "bis_docs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def entries():
    return json.loads(DOCS_JSON.read_text(encoding="utf-8"))["functions"]


@pytest.mark.parametrize("name", sorted(BIS_FUNCTIONS))
def test_every_bis_calculator_has_a_generated_guide(entries, name):
    entry = entries.get(name)
    assert entry, f"{name}: no guide entry; run python website/_build/app_docs.py"
    assert entry["origin"] == "geocore" and entry["module"].startswith("core.standards.bis.")
    assert entry["summary"] and entry["theory_html"] and entry["returns_html"] and entry["references"]
    assert "\\[" in entry["theory_html"] or "\\(" in entry["theory_html"]
    signature = set(inspect.signature(BIS_FUNCTIONS[name]).parameters)
    assert set(entry["params"]) == signature, f"{name}: regenerate the docs (parameters changed)"


def test_curated_symbols_and_ranges_name_real_parameters():
    docs = _bis_docs()
    assert set(docs.BIS_DOCS) == set(BIS_FUNCTIONS)
    for name, spec in docs.BIS_DOCS.items():
        params = set(inspect.signature(BIS_FUNCTIONS[name]).parameters)
        assert set(spec["symbols"]) <= params, name
        assert set(spec["ranges"]) <= params, name
        assert set(spec["references"]) <= set(docs.REF), name


def test_documented_table_values_match_the_implementation():
    """The IS 1904 Table 1 printed in the guide is the table the calculator applies."""
    from core.standards.bis.is1904 import TABLE_1
    theory = _bis_docs().BIS_DOCS["permissible_settlement_is1904"]["theory"]
    label = {"steel": "Steel", "reinforced_concrete": "Reinforced concrete", "multistorey_framed": "Multistorey framed",
             "water_tower_silo": "Water tower / silo"}
    rows = {tuple(c.strip() for c in ln.strip("|").split("|")[:2]): [c.strip() for c in ln.strip("|").split("|")[2:]]
            for ln in theory.splitlines() if ln.startswith("| Isolated") or ln.startswith("| Raft")}
    for (fnd, struct, soil), (s_max, coeff, ad_den) in TABLE_1.items():
        cells = rows[(fnd.capitalize(), label[struct])]
        mx, diff = (cells[0], cells[1]) if soil == "sand_hard_clay" else (cells[2], cells[3])
        assert float(mx) == s_max and diff == f"{coeff:g} L", (fnd, struct, soil)
        assert f"1/{ad_den}" in cells[4], (fnd, struct, soil)
