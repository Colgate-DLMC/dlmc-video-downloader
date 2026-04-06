# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('bin/yt-dlp', 'bin'),
        ('bin/ffmpeg', 'bin'),
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
    console=False,
    target_arch='arm64',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='dlmc-video-downloader',
)

app = BUNDLE(
    coll,
    name='dlmc-video-downloader.app',
    icon='icon.icns',
    bundle_identifier='com.dlmc.video-downloader',
    info_plist={
        'CFBundleShortVersionString': '1.2',
        'NSHighResolutionCapable': True,
    },
)
