# -*- mode: python ; coding: utf-8 -*-
# GeoCore — PyInstaller spec (one-folder mode)
# One-folder avoids AV false-positives caused by single-file temp extraction.
# Output: python-backend/dist/main/  (folder containing main.exe / main binary)

import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

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
hiddenimports += collect_submodules('core')
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

datas += collect_data_files('plotly')
datas += collect_data_files('jinja2')

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'IPython', 'notebook', 'PyQt5', 'PySide2', 'wx',
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
