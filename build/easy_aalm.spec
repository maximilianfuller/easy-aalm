# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Easy AALM
Bundles Streamlit app with pywebview for native desktop experience
"""

import sys
import os
from pathlib import Path

block_cipher = None

# Project root directory (SPECPATH is build/, so go up one level)
PROJECT_ROOT = Path(SPECPATH).parent
SRC_DIR = PROJECT_ROOT / 'src'
AALM_DIR = PROJECT_ROOT / 'aalm_original'

# Collect all data files
datas = [
    # Application source files
    (str(SRC_DIR / 'app.py'), '.'),
    (str(SRC_DIR / 'fortran_input_generator.py'), '.'),
    (str(SRC_DIR / 'templates'), 'templates'),

    # AALM executable and required files
    (str(AALM_DIR / 'AALM_64.exe'), 'aalm_original'),
    (str(AALM_DIR / 'AALM_32.exe'), 'aalm_original'),
    (str(AALM_DIR / 'Examples'), 'aalm_original/Examples'),
    (str(AALM_DIR / 'RespMod'), 'aalm_original/RespMod'),

    # Streamlit config
    (str(PROJECT_ROOT / '.streamlit'), '.streamlit'),
]

# Hidden imports needed for Streamlit and dependencies
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
    'altair',
    'pyarrow',
    'PIL',
    'PIL.Image',
    'toml',
    'validators',
    'gitpython',
    'pydeck',
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
        'matplotlib',  # Not needed, saves space
        'scipy',  # Not needed
        'numpy.testing',  # Not needed
        'IPython',  # Not needed
        'jupyter',  # Not needed
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
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Easy AALM',
)

# macOS App Bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='Easy AALM.app',
        icon=str(PROJECT_ROOT / 'assets' / 'icon.icns'),
        bundle_identifier='com.easyaalm.app',
        info_plist={
            'CFBundleName': 'Easy AALM',
            'CFBundleDisplayName': 'Easy AALM',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,  # Support dark mode
            'LSMinimumSystemVersion': '10.13.0',
        },
    )
