# DLMC Video Downloader - Windows Build Script
# Requires: Python 3, pip, Inno Setup (for installer packaging)
# Run from the repo root in PowerShell:  .\build.ps1

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$BinDir  = Join-Path $ScriptDir "bin"
$DistDir = Join-Path $ScriptDir "dist"

Write-Host "=== DLMC Video Downloader - Windows Build ===" -ForegroundColor Cyan

# -------------------------------------------------------
# 1. Ensure PyInstaller is installed
# -------------------------------------------------------
try {
    python -m PyInstaller --version | Out-Null
} catch {
    Write-Host "Installing PyInstaller..."
    pip install pyinstaller
}
$pyiVersion = python -m PyInstaller --version
Write-Host "PyInstaller $pyiVersion"

# -------------------------------------------------------
# 2. Download binaries if needed
# -------------------------------------------------------
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

# --- yt-dlp ---
$ytdlpPath = Join-Path $BinDir "yt-dlp.exe"
if (-Not (Test-Path $ytdlpPath)) {
    Write-Host "Downloading yt-dlp (Windows x64)..."
    Invoke-WebRequest -Uri "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe" `
                      -OutFile $ytdlpPath
    Write-Host "yt-dlp downloaded."
} else {
    Write-Host "yt-dlp already present."
}

# --- ffmpeg ---
$ffmpegPath = Join-Path $BinDir "ffmpeg.exe"
if (-Not (Test-Path $ffmpegPath)) {
    Write-Host "Downloading ffmpeg (Windows x64)..."
    $ffmpegZip = Join-Path $env:TEMP "ffmpeg.zip"
    # Gyan.dev provides reliable static Windows builds
    Invoke-WebRequest -Uri "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" `
                      -OutFile $ffmpegZip
    $ffmpegExtract = Join-Path $env:TEMP "ffmpeg-extract"
    Expand-Archive -Path $ffmpegZip -DestinationPath $ffmpegExtract -Force
    $ffmpegBin = Get-ChildItem -Path $ffmpegExtract -Recurse -Filter "ffmpeg.exe" | Select-Object -First 1
    Copy-Item $ffmpegBin.FullName $ffmpegPath
    Remove-Item $ffmpegZip, $ffmpegExtract -Recurse -Force
    Write-Host "ffmpeg downloaded."
} else {
    Write-Host "ffmpeg already present."
}

# -------------------------------------------------------
# 3. Run PyInstaller
# -------------------------------------------------------
Write-Host ""
Write-Host "Building with PyInstaller..."
python -m PyInstaller --clean --noconfirm dlmc-video-downloader-windows.spec

$appDir = Join-Path $DistDir "dlmc-video-downloader"
Write-Host ""
Write-Host "Build complete: $appDir"

# -------------------------------------------------------
# 4. Package with Inno Setup (if installed)
# -------------------------------------------------------
$inno = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (Test-Path $inno) {
    Write-Host "Packaging installer with Inno Setup..."
    & $inno "dlmc-video-downloader.iss"
    Write-Host "Installer created: Output\dlmc-video-downloader-setup.exe"
} else {
    Write-Host ""
    Write-Host "Inno Setup not found - skipping installer packaging." -ForegroundColor Yellow
    Write-Host "Install from https://jrsoftware.org/isinfo.php and re-run to produce a .exe installer."
    Write-Host "The raw app folder is at: $appDir"
}

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Cyan
