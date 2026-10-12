# Author: Utkarsh Gupta
# License: GPL v3
"""
.github/scripts/changelog.py: release notes and the docs changelog come from website/_content/geocore/changelog.md.
The file operations run on a temporary copy; the real changelog is only read.
"""
import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / ".github" / "scripts" / "changelog.py"

SAMPLE = """---
title: Changelog
---

Intro.

## Unreleased

### Added

- New thing, see [the docs](/docs/geocore/overview).

## v1.0.0 — 2026-10-04

First public release.

### Added

- Everything.
"""


@pytest.fixture()
def cl(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("changelog_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    path = tmp_path / "changelog.md"
    path.write_text(SAMPLE, encoding="utf-8")
    monkeypatch.setattr(module, "CHANGELOG", path)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    return module


def test_release_moves_unreleased_into_a_dated_version_section(cl):
    cl.release("v1.1.0", "2026-10-20")
    text = cl.CHANGELOG.read_text(encoding="utf-8")
    assert "## Unreleased\n\n## v1.1.0 — 2026-10-20\n" in text
    assert cl.check("v1.1.0") == 0 and "New thing" in cl.section_body(text, "v1.1.0")
    assert cl.section_body(text, "Unreleased") == ""
    with pytest.raises(SystemExit):  # nothing left to release
        cl.release("v1.2.0", "2026-10-21")
    with pytest.raises(SystemExit):  # never twice
        cl.release("v1.1.0", "2026-10-21")


def test_notes_flatten_site_links_and_link_the_code_comparison(cl):
    cl.release("v1.1.0", "2026-10-20")
    notes = cl.release_notes("v1.1.0")
    assert notes.startswith("### Added") and "see the docs." in notes and "/docs/" not in notes.split("---")[0]
    assert "compare/v1.0.0...v1.1.0" in notes
    assert "## v1.0.0" not in notes  # only this version's section


def test_auto_draft_is_replaced_on_rerun_and_blocks_release(cl):
    cl.write_draft(f"{cl.AUTO_START}\n- first\n{cl.AUTO_END}")
    cl.write_draft(f"{cl.AUTO_START}\n- second\n{cl.AUTO_END}")
    text = cl.CHANGELOG.read_text(encoding="utf-8")
    assert text.count(cl.AUTO_START) == 1 and "- second" in text and "- first" not in text
    with pytest.raises(SystemExit, match="auto-draft"):
        cl.release("v1.1.0", "2026-10-20")


def test_check_fails_for_a_missing_or_empty_version(cl):
    assert cl.check("v9.9.9") == 1
    cl.CHANGELOG.write_text(SAMPLE.replace("- New thing, see [the docs](/docs/geocore/overview).\n", ""),
                            encoding="utf-8")
    with pytest.raises(SystemExit, match="empty"):
        cl.release("v1.1.0", "2026-10-20")


def test_real_changelog_has_notes_for_every_released_version():
    spec = importlib.util.spec_from_file_location("changelog_real", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    text = module.CHANGELOG.read_text(encoding="utf-8")
    versions = [name for name, _, _, _ in module._sections(text) if name != "Unreleased"]
    assert versions, "no released versions in the changelog"
    for version in versions:
        assert module.check(version) == 0
    assert module.AUTO_START not in text, "an unreviewed auto-draft was left in the changelog"


def test_generated_docs_page_matches_the_changelog_source(tmp_path, monkeypatch):
    """website/_content/pages/changelog.md must be refreshed after the changelog is edited (changelog.py sync)."""
    spec = importlib.util.spec_from_file_location("changelog_sync", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    committed = (REPO / "website" / "_content" / "pages" / "changelog.md").read_text(encoding="utf-8")
    (tmp_path / "geocore").mkdir()
    (tmp_path / "pages").mkdir()
    source = tmp_path / "geocore" / "changelog.md"
    source.write_text(module.CHANGELOG.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "pages" / "changelog.md").write_text(committed, encoding="utf-8")
    monkeypatch.setattr(module, "CHANGELOG", source)
    module.sync_docs_page()
    assert (tmp_path / "pages" / "changelog.md").read_text(encoding="utf-8") == committed, \
        "run: python .github/scripts/changelog.py sync && python website/_build/build.py"
