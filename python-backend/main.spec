# -*- mode: python ; coding: utf-8 -*-
# GeoCore — PyInstaller spec (one-folder mode)
# One-folder avoids AV false-positives caused by single-file temp extraction.
# Output: python-backend/dist/main/  (folder containing main.exe / main binary)

import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs, copy_metadata

block_cipher = None

# ---------------------------------------------------------------------------
# Hidden imports — uvicorn uses dynamic imports that PyInstaller can't detect
# ---------------------------------------------------------------------------
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.loops.asyncio',
    'uvicorn.loops.uvloop',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.websockets_impl',
    'uvicorn.protocols.websockets.wsproto_impl',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
    'fastapi',
    'fastapi.middleware',
    'fastapi.middleware.cors',
    'fastapi.staticfiles',
    'fastapi.responses',
    'fastapi.encoders',
    'pandas',
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.tslibs.timedeltas',
    'numpy',
    'openpyxl',
    'xlrd',
    'python_multipart',
    'multipart',
    'scipy',
]

hiddenimports += collect_submodules('groundhog')
# collect_submodules imports 'core' in a subprocess, which only finds it when this folder is on
# sys.path. The `pyinstaller` entry point (used in CI) does not add it, so without this line
# collect_submodules('core') silently returns nothing.
sys.path.insert(0, os.path.abspath(SPECPATH))
hiddenimports += collect_submodules('core')
# Loaded by name via importlib (registry._load_wrapper_module), so PyInstaller cannot see them.
hiddenimports += ['core.wrappers', 'core.plotting_wrappers', 'core.labtesting_wrappers']
hiddenimports += collect_submodules('plotly')
hiddenimports += collect_submodules('scipy')
hiddenimports += collect_submodules('matplotlib')
hiddenimports += collect_submodules('PIL')
hiddenimports += collect_submodules('pyproj')
hiddenimports += collect_submodules('requests')
hiddenimports += collect_submodules('urllib3')
hiddenimports += collect_submodules('httpx')
hiddenimports += collect_submodules('certifi')
hiddenimports += collect_submodules('jinja2')
hiddenimports += collect_submodules('markupsafe')

# ---------------------------------------------------------------------------
# Local LLM runtime (llama-cpp-python) for GeoAI.
# core/geoai/llama_cpp_provider.py imports it lazily, so PyInstaller cannot
# see it statically. The native ggml/llama DLLs live in llama_cpp/lib and are
# loaded via ctypes relative to the package's __file__, so they must be
# collected into the same relative folder. The optional OpenAI-compatible
# server subpackage is not used by GeoCore and is excluded.
# ---------------------------------------------------------------------------
llama_binaries = []
try:
    import llama_cpp  # noqa: F401
    hiddenimports += collect_submodules(
        'llama_cpp', filter=lambda name: not name.startswith('llama_cpp.server')
    )
    llama_binaries = collect_dynamic_libs('llama_cpp')
except ImportError:
    print('WARNING: llama_cpp not installed - GeoAI will fall back to the heuristic provider.')

# ---------------------------------------------------------------------------
# Data files
# ---------------------------------------------------------------------------
datas = []

if not os.path.exists('assets'):
    os.makedirs('assets', exist_ok=True)
datas.append(('assets', 'assets'))

for json_file in ['module_info_structured.json', 'schema_overrides.json']:
    if os.path.exists(json_file):
        datas.append((json_file, '.'))

# Include GeoAI parameter inventory
if os.path.exists('core/geoai/parameter_inventory.json'):
    datas.append(('core/geoai/parameter_inventory.json', 'core/geoai'))

# Lazy-registry manifest; without it the frozen app falls back to the slow eager scan.
# Regenerate before building: python -m core.function_manifest
datas.append(('core/function_manifest.json', 'core'))
datas += copy_metadata('groundhog')

# Docs content for the GeoAI docs adaptor (core/geoai/research/docs_adapter.py): Groundhog API
# docstrings + docs pages (~4 MB, text only; figures are not needed).
_docs_content = os.path.join('..', 'website', '_content')
if os.path.exists(os.path.join(_docs_content, 'groundhog', 'api.json')):
    datas.append((os.path.join(_docs_content, 'groundhog', 'api.json'), 'docs_content/groundhog'))
    datas.append((os.path.join(_docs_content, 'pages'), 'docs_content/pages'))

datas += collect_data_files('plotly')
datas += collect_data_files('jinja2')

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=llama_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'IPython', 'notebook', 'PyQt5', 'PySide2', 'wx',
        'torch', 'sympy', 'botocore', 'lxml',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ---------------------------------------------------------------------------
# EXE — scripts only (no binaries/datas — those go in COLLECT)
# ---------------------------------------------------------------------------
exe = EXE(
    pyz,
    a.scripts,
    [],                                  # <-- NO a.binaries / a.zipfiles / a.datas here
    exclude_binaries=True,               # <-- must be True for one-folder mode
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                           # <-- disabled: UPX triggers AV false-positives
    console=False,                       # <-- no terminal flash on startup
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# ---------------------------------------------------------------------------
# COLLECT — produces dist/main/ folder with all dependencies alongside binary
# ---------------------------------------------------------------------------
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='main',
)
