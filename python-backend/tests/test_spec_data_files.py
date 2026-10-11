# Author: Utkarsh Gupta
# License: GPL v3
"""
The frozen desktop backend (PyInstaller, main.spec) must ship every data file the code reads at runtime. Development
and the other tests read them from the source tree, so a file missing from the spec only breaks the installed app
(e.g. core/catalogue/benchmarks.json: every method status, the catalogue endpoint and GeoAI's tool listing).
"""
import re
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
# Data used only by offline tooling (evaluation, training, fine-tuning), not by the running app.
OFFLINE = ("core/geoai/eval/", "core/geoai/training/", "core/geoai/finetune/")


def _spec_sources():
    spec = (BACKEND / "main.spec").read_text(encoding="utf-8")
    sources = set(re.findall(r"datas\.append\(\(\s*'([^']+)'", spec))
    sources |= set(re.findall(r'datas\.append\(\(\s*"([^"]+)"', spec))
    # for json_file in [...]: datas.append((os.path.join('core', json_file), 'core'))
    for names, folder in re.findall(r"for json_file in \[([^\]]*)\]:\s*\n\s*datas\.append\(\(os\.path\.join\('([^']+)', json_file\)", spec):
        sources |= {f"{folder}/{n}" for n in re.findall(r"'([^']+)'", names)}
    return {s.replace("\\", "/").rstrip("/") for s in sources}


def test_every_runtime_json_under_core_is_in_the_spec():
    sources = _spec_sources()
    missing = []
    for path in sorted((BACKEND / "core").rglob("*.json")):
        rel = path.relative_to(BACKEND).as_posix()
        if "__pycache__" in rel or rel.startswith(OFFLINE):
            continue
        if not any(rel == s or rel.startswith(s + "/") for s in sources):
            missing.append(rel)
    assert missing == [], f"add to main.spec datas: {missing}"


def test_spec_sources_exist():
    for source in _spec_sources():
        if source.startswith("core/"):
            assert (BACKEND / source).exists(), source
