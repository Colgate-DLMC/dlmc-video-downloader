# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Windows (x64)
from PyInstaller.utils.hooks import collect_all

datas_ytdlp, binaries_ytdlp, hiddenimports_ytdlp = collect_all('yt_dlp')

with open('version.txt') as _vf:
    _APP_VERSION = _vf.read().strip()

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries_ytdlp,
    datas=[
        ('bin/ffmpeg.exe', 'bin'),
        ('bin/deno.exe', 'bin'),
        ('logo.png', '.'),
        ('version.txt', '.'),
    ] + datas_ytdlp,
    hiddenimports=hiddenimports_ytdlp,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='dlmc-video-downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon='icon.ico',
    target_arch='x86_64',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='dlmc-video-downloader',
)
