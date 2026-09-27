# Author: Utkarsh Gupta
# License: GPL v3
"""Tests for the groundhog docstring parser in website/_content/extract_docs.py.

Run with the backend venv (groundhog installed):
    python-backend/venv/Scripts/python.exe -m pytest website/_content/tests -q
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import extract_docs as ed  # noqa: E402

pcpt = pytest.importorskip("groundhog.siteinvestigation.insitutests.pcpt_correlations")
cptliq = pytest.importorskip("groundhog.soildynamics.cptliquefaction")
categories = pytest.importorskip("groundhog.siteinvestigation.classification.categories")


def _param(parsed, name):
    return next(p for p in parsed["params"] if p["name"] == name)


def test_relativedensity_sand_jamiolkowski():
    d = ed.parse_docstring(ed._doc_of(pcpt.relativedensity_sand_jamiolkowski))
    assert [p["name"] for p in d["params"]][:3] == ["qc", "sigma_vo_eff", "k0"]
    qc = _param(d, "qc")
    assert qc["unit"] == "MPa"
    assert qc["symbol"] == "q_c"
    assert qc["range"] == "0.0 <= qc <= 120.0"
    assert qc["description"] == "Cone tip resistance"
    assert qc["default_doc"] is None
    pa = _param(d, "atmospheric_pressure")
    assert pa["unit"] == "kPa" and pa["default_doc"] == "100.0" and pa["optional"]
    keys = [it["key"] for it in d["returns"]["items"]]
    assert keys == ["Dr dry [-]", "Dr sat [-]"]
    assert d["returns"]["items"][0]["symbol"] == "D_{r,dry}"
    assert len(d["formulas"]) == 2
    assert d["formulas"][0].startswith("D_{r,dry} = \\frac{1}{2.96}")
    assert "$$" in d["description_md"]
    assert len(d["references"]) == 1 and d["references"][0].startswith("Jamiolkowski, M.")
    assert d["summary"].startswith("Jamiolkowksi et al formulated")


def test_liquefaction_strains_zhang_multiline_params_and_escape_repair():
    d = ed.parse_docstring(ed._doc_of(cptliq.liquefaction_strains_zhang))
    names = [p["name"] for p in d["params"]]
    assert names == ["FoS_liq", "relative_density", "Qtn_cs"]
    fos = _param(d, "FoS_liq")
    # continuation line with the suggested range is joined and converted to inline math
    assert fos["range"] == "$0.0 \\leq FoS_{liq} \\leq 5.0$"
    assert fos["unit"] == "-"
    # '\text' in a non-raw docstring arrives as TAB + 'ext'; the parser restores it
    assert any("\\text{otherwise}" in f for f in d["formulas"])
    assert [it["unit"] for it in d["returns"]["items"]] == ["%", "%"]
    assert len(d["references"]) == 2
    assert d["examples"] and d["examples"][0].startswith(">>> result = liquefaction_strains_zhang")


def test_samplequality_voidratio_lunne_grid_table_and_plain_units():
    d = ed.parse_docstring(ed._doc_of(categories.samplequality_voidratio_lunne))
    e0 = _param(d, "voidratio")
    assert e0["unit"] == "-"            # plain [-] (not :math:)
    assert e0["symbol"] == "e_0"
    assert e0["range"] == "0.3 <= voidratio <= 3.0"
    assert "```text\n+-------+" in d["description_md"]   # RST grid table kept as preformatted text
    assert [it["key"] for it in d["returns"]["items"]] == ["delta e/e0 [-]", "Quality category"]
    assert d["references"][0].startswith("Lunne, T.")


def test_rst_inline_conversions():
    assert ed.rst_inline("x (:math:`\\sigma`) ``code`` `link <https://a.b>`_") == \
        "x ($\\sigma$) `code` [link](https://a.b)"
    assert ed.rst_inline(":math:``") == ""


def test_md_cell_escapes_pipes_outside_math_only():
    assert ed.md_cell("a | b") == "a \\| b"
    assert ed.md_cell("$|x|$") == "$\\vert x\\vert $"
