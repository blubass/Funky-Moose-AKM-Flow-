# -*- mode: python ; coding: utf-8 -*-

import platform

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


current_tkdnd_platform = "osx-arm64" if platform.machine() == "arm64" else "osx-x64"


def _collect_tkinterdnd2_datas():
    datas = []
    for source, target in collect_data_files("tkinterdnd2"):
        normalized = source.replace("\\", "/")
        if "/tkdnd/" not in normalized:
            datas.append((source, target))
            continue
        if f"/tkdnd/{current_tkdnd_platform}/" in normalized:
            datas.append((source, target))
    return datas


a = Analysis(
    ['akm_app.py'],
    pathex=[],
    binaries=[
        ('/opt/homebrew/bin/ffmpeg', '.'),
        ('/opt/homebrew/bin/ffprobe', '.')
    ],
    datas=_collect_tkinterdnd2_datas() + [
        ('app_logic',       'app_logic'),
        ('app_ui',          'app_ui'),
        ('app_controllers', 'app_controllers'),
        ('app_workflows',   'app_workflows'),
        ('projects',        'projects'),
        ('assets',          'assets'),
    ],
    hiddenimports=collect_submodules('tkinterdnd2'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy', 'pandas', 'matplotlib'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Funky Moose Release Forge',
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
    icon=['akm_icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Funky Moose Release Forge',
)
app = BUNDLE(
    coll,
    name='Funky Moose Release Forge.app',
    icon='akm_icon.icns',
    bundle_identifier='com.funkymoose.releaseforge',
)
