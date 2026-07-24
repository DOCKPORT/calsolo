# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


# ---------------------------------------------------------------------------
# RESOURCE FILES — SVGs, fonts, etc. that the application loads at runtime.
# Paths use '../' prefix because the spec runs from Binary/ but the project
# root is one level up.
# ---------------------------------------------------------------------------
added_files = [
    # --- App icon ---
    ('../calsolo.svg', 'Binary'),
]


# ---------------------------------------------------------------------------
# HIDDEN IMPORTS — Libraries imported dynamically that PyInstaller cannot
# detect through static analysis.
# ---------------------------------------------------------------------------
hiddenimports = [
    # --- Qt / PySide6 ---
    'PySide6.QtSvg',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    # --- Rust native module ---
    '_calc_rs',
    # --- Stdlib ---
    're',
    'json',
    'os',
    'sys',
    'importlib.util',
]


a = Analysis(
    ['../calsolo.py'],
    pathex=['..', '.'],
    binaries=[],
    datas=added_files,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Calsolo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['../calsolo.svg'],
)