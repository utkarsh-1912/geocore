# Author: Utkarsh Gupta
# License: GPL v3
"""
Tests for the GeoCore docs adaptor (core/geoai/research/docs_adapter.py): structured function docs,
incremental indexing into the local research index, coverage reporting and the
get_function_documentation GeoAI tool.
"""
import json

import pytest

from core.geoai.exceptions import GeoAIValidationError
from core.geoai.research import docs_adapter as da
from core.geoai.research.indexer import LocalDocumentIndexer
from core.geoai.tool_registry import tool_registry
import core.geoai.tool_definitions  # noqa: F401  (registers the tools)


def _member(name, kind="function", **extra):
    member = {
        "kind": kind, "name": name, "qualname": name, "anchor": name, "line": 10,
        "signature": f"{name}(qc, sigma_vo_eff, k0=0.5)",
        "signature_params": [
            {"name": "qc", "default": None, "required": True},
            {"name": "sigma_vo_eff", "default": None, "required": True},
            {"name": "k0", "default": "0.5", "required": False},
        ],
        "validated": True,
        "validation": {"k0": {"type": "float", "min_value": 0.3, "max_value": 1.0}},
        "doc": {
            "summary": f"Summary of {name}.",
            "description_md": "Theory text. %%FIGURE:0%% <b>bold</b>",
            "params": [
                {"name": "qc", "description": "Cone resistance", "symbol": "q_c", "unit": "MPa",
                 "range": "0.0 <= qc <= 120.0"},
                {"name": "sigma_vo_eff", "description": "Vertical effective stress", "unit": "kPa"},
                {"name": "k0", "description": "Coefficient of lateral earth pressure", "unit": "-"},
                {"name": "**kwargs", "description": "ignored"},
            ],
            "returns": {"description": "Dictionary with the following keys:",
                        "items": [{"key": "Dr [-]", "description": "Relative density", "unit": "-"}]},
            "references": ["Jamiolkowski et al (2003). Evaluation of relative density."],
            "formulas": ["D_r = f(q_c)"],
        },
    }
    member.update(extra)
    return member


@pytest.fixture
def content_dir(tmp_path):
    root = tmp_path / "_content"
    (root / "groundhog").mkdir(parents=True)
    method = _member("calculate_capacity")
    method["qualname"] = "PileCalc.calculate_capacity"
    cls = _member("PileCalc", kind="class", methods=[method], init=None)
    cls["doc"]["params"] = []
    api = {
        "groundhog_version": "9.9.9", "license": "GPL-3.0-or-later", "author": "Test Author",
        "modules": [
            {"module": "groundhog.siteinvestigation.insitutests.pcpt_correlations",
             "source_path": "groundhog/siteinvestigation/insitutests/pcpt_correlations.py",
             "members": [_member("relativedensity_sand_test"), _member("unused_correlation")]},
            {"module": "groundhog.deepfoundations.axialcapacity.piles",
             "source_path": "groundhog/deepfoundations/axialcapacity/piles.py",
             "members": [cls]},
        ],
    }
    (root / "groundhog" / "api.json").write_text(json.dumps(api), encoding="utf-8")
    pages = root / "pages" / "geocore"
    pages.mkdir(parents=True)
    (pages / "overview.md").write_text(
        "---\ntitle: Overview\nslug: geocore/overview\nsection: Getting Started\norigin: geocore\n---\n"
        "# Overview\n\nGeoCore runs liquefaction screening offline with ![fig](x.png) figures.\n",
        encoding="utf-8")
    (pages / "api-module.md").write_text(
        "---\ntitle: Module\nslug: groundhog/api/x\nmodule: groundhog.x\n---\nAPI module page body text here.\n",
        encoding="utf-8")
    return root


@pytest.fixture
def adapter(content_dir):
    return da.DocsAdapter(content_dir)


def test_function_doc_is_structured_with_units_ranges_and_provenance(adapter):
    fd = adapter.function_doc("relativedensity_sand_test")
    assert fd.summary == "Summary of relativedensity_sand_test."
    assert fd.folder == "siteinvestigation/insitutests"
    params = {p.name: p for p in fd.params}
    assert set(params) == {"qc", "sigma_vo_eff", "k0"}          # **kwargs dropped
    assert params["qc"].unit == "MPa" and params["qc"].range == "0.0 <= qc <= 120.0"
    assert params["k0"].range == "0.3 <= k0 <= 1.0"            # from the validator when the docstring has none
    assert params["k0"].required is False and params["k0"].default == "0.5"
    assert fd.returns[0].key == "Dr [-]"
    assert fd.references == ["Jamiolkowski et al (2003). Evaluation of relative density."]
    assert "%%FIGURE" not in fd.description and "<b>" not in fd.description
    assert fd.docs_url == "/docs/groundhog/api/siteinvestigation/insitutests/pcpt_correlations/#relativedensity_sand_test"
    assert fd.source_url.endswith("/blob/v9.9.9/groundhog/siteinvestigation/insitutests/pcpt_correlations.py#L10")


def test_class_doc_merges_method_inputs_and_methods_are_addressable(adapter):
    fd = adapter.function_doc("PileCalc")
    assert fd.kind == "class" and fd.methods == ["calculate_capacity"]
    assert {p.name for p in fd.params} == {"qc", "sigma_vo_eff", "k0"}
    meth = adapter.function_doc("PileCalc.calculate_capacity")
    assert meth.kind == "method" and meth.name == "PileCalc.calculate_capacity"
    assert adapter.function_doc("PileCalc.missing") is None
    assert adapter.function_doc("does_not_exist") is None


def test_pages_skip_api_module_pages_and_strip_markup(adapter):
    pages = list(adapter.iter_pages())
    assert [p.slug for p in pages] == ["geocore/overview"]
    assert pages[0].url == "/docs/geocore/overview/"
    assert "x.png" not in pages[0].body and "liquefaction screening" in pages[0].body


def test_index_into_is_incremental_and_searchable(adapter, content_dir, tmp_path):
    indexer = LocalDocumentIndexer(db_path=tmp_path / "rag.db")
    indexer.index_text_content("USER_NOTE", "My note", "User owned note about pile set-up in clay.")

    first = adapter.index_into(indexer)
    assert first == {"status": "indexed", "functions": 3, "pages": 1}   # methods are folded into their class
    assert adapter.index_into(indexer)["status"] == "up_to_date"

    hits = indexer.search("Jamiolkowski relative density", top_k=3)
    assert hits and hits[0].file_path.startswith("/docs/groundhog/api/")
    assert indexer.search("liquefaction screening")[0].file_path == "/docs/geocore/overview/"

    # Changed docs are re-indexed; the user's own documents are never touched.
    api_path = content_dir / "groundhog" / "api.json"
    api = json.loads(api_path.read_text(encoding="utf-8"))
    api["modules"].pop(1)
    api_path.write_text(json.dumps(api), encoding="utf-8")
    second = da.DocsAdapter(content_dir).index_into(indexer)
    assert second["status"] == "indexed" and second["functions"] == 2
    assert indexer.get_document_hash("geocore-docs:api:PileCalc") is None
    assert indexer.search("pile set-up clay")[0].doc_title == "My note"


def test_missing_content_degrades_gracefully(tmp_path):
    adapter = da.DocsAdapter(tmp_path / "nowhere")
    assert not adapter.available()
    assert adapter.function_doc("anything") is None
    assert adapter.index_into(LocalDocumentIndexer(db_path=tmp_path / "x.db"))["status"] == "unavailable"


def test_coverage_report_groups_by_folder_and_explains_gaps(adapter):
    calc_mod = "groundhog.siteinvestigation.insitutests.pcpt_correlations"
    pile_mod = "groundhog.deepfoundations.axialcapacity.piles"
    rows = da.coverage_report(
        adapter,
        backend_targets=[(calc_mod, "relativedensity_sand_test"), (pile_mod, "PileCalc")],
        ui_targets=[(calc_mod, "relativedensity_sand_test"), (pile_mod, "PileCalc.calculate_capacity")],
        geoai_exclusions={"PileCalc": "stateful"},
    )
    by_name = {r.name: r for r in rows}
    assert set(by_name) == {"relativedensity_sand_test", "unused_correlation", "PileCalc"}
    assert by_name["relativedensity_sand_test"].geoai_tool
    assert by_name["PileCalc"].in_desktop_ui and not by_name["PileCalc"].geoai_tool
    gap = by_name["unused_correlation"]
    assert not gap.in_backend and not gap.in_desktop_ui and gap.geoai_note == "not in the backend registry"

    md = da.coverage_markdown(rows, "9.9.9")
    assert "### `siteinvestigation/insitutests`" in md
    assert "| `unused_correlation` |" in md
    assert "| **Total** | **3** | **2** | **2** | **1** |" in md


def test_get_function_documentation_tool(monkeypatch, adapter):
    monkeypatch.setattr(da, "_default", adapter)
    tool = tool_registry.get_tool("get_function_documentation")
    assert tool is not None and tool.category == "documentation"

    out = tool_registry.invoke_tool("get_function_documentation", {"function_name": "relativedensity_sand_test"})
    assert out["module"].endswith("pcpt_correlations")
    assert out["params"][0]["unit"] == "MPa"
    assert out["references"] == ["Jamiolkowski et al (2003). Evaluation of relative density."]
    assert "Test Author" in out["attribution"]
    assert "_provenance" in out

    with pytest.raises(GeoAIValidationError, match="Did you mean: relativedensity_sand_test"):
        tool_registry.invoke_tool("get_function_documentation", {"function_name": "relativedensity_sand"})


def test_shipped_docs_cover_every_backend_groundhog_function():
    """The real docs must document every Groundhog function in the backend manifest."""
    adapter = da.DocsAdapter()
    if not adapter.available():
        pytest.skip("website/_content not present")
    from core.function_manifest import MANIFEST_PATH
    manifest = json.loads(open(MANIFEST_PATH, encoding="utf-8").read())
    missing = [f["qualname"] for f in manifest["functions"] if adapter.function_doc(f["qualname"]) is None]
    assert missing == []
