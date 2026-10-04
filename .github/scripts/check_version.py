"""
Fail unless every place that carries the app version agrees with the release tag.

    python .github/scripts/check_version.py v1.2.3

The version lives in electron-app/package.json, python-backend/main.py (twice) and
python-backend/core/diagnostics.py; RELEASE_GUIDE.md says to update all of them.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    tag = sys.argv[1]
    if not re.fullmatch(r"v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", tag):
        print(f"FAIL: tag {tag!r} is not of the form vMAJOR.MINOR.PATCH")
        return 1
    expected = tag[1:]

    found = {"electron-app/package.json": [json.loads((ROOT / "electron-app/package.json").read_text("utf-8"))["version"]]}
    main_py = (ROOT / "python-backend/main.py").read_text("utf-8")
    found["python-backend/main.py"] = (re.findall(r'version\s*=\s*"([^"]+)"', main_py)
                                       + re.findall(r'"version":\s*"([^"]+)"', main_py))
    diag = (ROOT / "python-backend/core/diagnostics.py").read_text("utf-8")
    found["python-backend/core/diagnostics.py"] = re.findall(r'APP_VERSION\s*=\s*"([^"]+)"', diag)

    bad = False
    for path, versions in found.items():
        if not versions:
            print(f"FAIL: no version found in {path}")
            bad = True
        elif any(v != expected for v in versions):
            print(f"FAIL: {path} has {versions}, tag says {expected}")
            bad = True
        else:
            print(f"ok: {path} = {expected}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
