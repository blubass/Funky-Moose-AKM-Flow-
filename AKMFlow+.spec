# -*- mode: python ; coding: utf-8 -*-

import os
import platform
import shutil
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


SYSTEM = platform.system()
MACHINE = platform.machine().lower()
APP_NAME = "Funky Moose Release Forge"

TKDND_PLATFORMS = {
    ("Darwin", "arm64"): "osx-arm64",
    ("Darwin", "x86_64"): "osx-x64",
    ("Linux", "aarch64"): "linux-arm64",
    ("Linux", "arm64"): "linux-arm64",
    ("Linux", "x86_64"): "linux-x64",
    ("Windows", "amd64"): "win-x64",
    ("Windows", "x86_64"): "win-x64",
    ("Windows", "arm64"): "win-arm64",
    ("Windows", "x86"): "win-x86",
}
current_tkdnd_platform = TKDND_PLATFORMS.get((SYSTEM, MACHINE))


def _collect_existing_dirs(*names):
    datas = []
    for name in names:
        path = Path(name)
        if path.exists():
            datas.append((str(path), name))
    return datas


def _optional_binary(path_str):
    if not path_str:
        return []
    path = Path(path_str).expanduser()
    if path.exists():
        return [(str(path), ".")]
    return []


def _collect_ffmpeg_binaries():
    executable_names = ("ffmpeg.exe", "ffprobe.exe") if SYSTEM == "Windows" else ("ffmpeg", "ffprobe")
    candidates = []
    explicit_dir = os.environ.get("AKM_FFMPEG_DIR")
    if explicit_dir:
        base = Path(explicit_dir).expanduser()
        candidates.extend(base / name for name in executable_names)
    for executable_name in executable_names:
        resolved = shutil.which(executable_name)
        if resolved:
            candidates.append(Path(resolved))

    binaries = []
    seen = set()
    for candidate in candidates:
        resolved = str(candidate.resolve())
        if resolved in seen:
            continue
        seen.add(resolved)
        binaries.extend(_optional_binary(resolved))
    return binaries


def _resolve_icon():
    if SYSTEM == "Darwin":
        return "akm_icon.icns"
    if SYSTEM == "Windows" and Path("akm_icon.ico").exists():
        return "akm_icon.ico"
    return None


def _collect_tkinterdnd2_datas():
    datas = []
    for source, target in collect_data_files("tkinterdnd2"):
        normalized = source.replace("\\", "/")
        if "/tkdnd/" not in normalized:
            datas.append((source, target))
            continue
        if current_tkdnd_platform and f"/tkdnd/{current_tkdnd_platform}/" in normalized:
            datas.append((source, target))
    return datas


icon_path = _resolve_icon()


a = Analysis(
    ["akm_app.py"],
    pathex=[],
    binaries=_collect_ffmpeg_binaries(),
    datas=_collect_tkinterdnd2_datas() + [
        *_collect_existing_dirs(
            "app_logic",
            "app_ui",
            "app_controllers",
            "app_workflows",
            "projects",
            "assets",
        ),
    ],
    hiddenimports=collect_submodules("tkinterdnd2"),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["numpy", "pandas", "matplotlib"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
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
    icon=[icon_path] if icon_path else None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)

if SYSTEM == "Darwin":
    app = BUNDLE(
        coll,
        name=f"{APP_NAME}.app",
        icon="akm_icon.icns",
        bundle_identifier="com.funkymoose.releaseforge",
    )
