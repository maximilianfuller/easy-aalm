# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Easy AALM - Windows Build
"""

import sys
import os
from pathlib import Path

block_cipher = None

# Project root directory (SPECPATH is build/, so go up one level)
PROJECT_ROOT = Path(SPECPATH).parent
SRC_DIR = PROJECT_ROOT / 'src'
AALM_DIR = PROJECT_ROOT / 'aalm_original'

datas = [
    (str(SRC_DIR / 'app.py'), '.'),
    (str(SRC_DIR / 'aalm_constants.py'), '.'),
    (str(SRC_DIR / 'fortran_input_generator.py'), '.'),
    (str(SRC_DIR / 'templates'), 'templates'),
    (str(AALM_DIR / 'AALM_64.exe'), 'aalm_original'),
    (str(AALM_DIR / 'AALM_32.exe'), 'aalm_original'),
    (str(AALM_DIR / 'Examples'), 'aalm_original/Examples'),
    (str(AALM_DIR / 'RespMod'), 'aalm_original/RespMod'),
    (str(PROJECT_ROOT / '.streamlit'), '.streamlit'),
]

hiddenimports = [
    'streamlit',
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner',
    'streamlit.runtime.scriptrunner.magic_funcs',
    'pandas',
    'plotly',
    'plotly.graph_objects',
    'plotly.express',
    'openpyxl',
    'webview',
    'webview.platforms.edgechromium',
    'webview.platforms.winforms',
    'clr_loader',
    'pythonnet',
    'altair',
    'pyarrow',
    'PIL',
    'PIL.Image',
    'toml',
    'tornado',
    'tornado.web',
    'tornado.routing',
    'tornado.websocket',
    'click',
    'rich',
    'packaging',
    'packaging.version',
    'packaging.specifiers',
    'packaging.requirements',
    'importlib_metadata',
    'typing_extensions',
]

a = Analysis(
    [str(SRC_DIR / 'main_pywebview.py')],
    pathex=[str(SRC_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'numpy.testing',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Easy AALM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here: 'assets/icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EasyAALM',
)
