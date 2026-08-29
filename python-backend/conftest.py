import sys
from pathlib import Path

# Automatically ensure python-backend root is on sys.path for test discovery and execution
BACKEND_ROOT = Path(__file__).resolve().parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
