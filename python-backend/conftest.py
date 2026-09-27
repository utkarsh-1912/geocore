import sys
from pathlib import Path

import pytest

# Automatically ensure python-backend root is on sys.path for test discovery and execution
BACKEND_ROOT = Path(__file__).resolve().parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture(autouse=True)
def _isolate_user_config(tmp_path_factory, monkeypatch):
    """Keep tests from writing the developer's real %APPDATA%/GeoCore config."""
    home = tmp_path_factory.mktemp("geocore_home")
    monkeypatch.setenv("APPDATA", str(home))
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
