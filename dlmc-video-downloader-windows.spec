# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Windows (x64)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('bin/yt-dlp.exe', 'bin'),
        ('bin/ffmpeg.exe', 'bin'),
        ('logo.png', '.'),
    ],
    hiddenimports=[],
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
    console=False,        # no console window
    icon='icon.ico',      # Windows requires .ico format
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
