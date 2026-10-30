#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

BIN_DIR="$SCRIPT_DIR/bin"
DIST_DIR="$SCRIPT_DIR/dist"
PKG_STAGE="$SCRIPT_DIR/pkg-stage"

VERSION="$(cat version.txt)"

echo "=== DLMC Video Downloader build script — v${VERSION} ==="

export MACOSX_DEPLOYMENT_TARGET=10.13

# -------------------------------------------------------
# 1. Ensure Python dependencies are installed
# -------------------------------------------------------
PYTHON=/opt/homebrew/bin/python3.13

if ! $PYTHON -m PyInstaller --version &>/dev/null; then
    echo "Installing PyInstaller..."
    $PYTHON -m pip install pyinstaller
fi
echo "PyInstaller $($PYTHON -m PyInstaller --version)"

echo "Installing/upgrading yt-dlp..."
$PYTHON -m pip install --upgrade yt-dlp
echo "yt-dlp $($PYTHON -c 'import yt_dlp; print(yt_dlp.version.__version__)')"

# -------------------------------------------------------
# 2. Download ffmpeg if needed
# -------------------------------------------------------
mkdir -p "$BIN_DIR"

NEED_FFMPEG=false
if [ ! -f "$BIN_DIR/ffmpeg" ]; then
    NEED_FFMPEG=true
elif ! file "$BIN_DIR/ffmpeg" | grep -q "arm64"; then
    echo "Existing ffmpeg is not arm64-compatible, replacing..."
    NEED_FFMPEG=true
fi

if [ "$NEED_FFMPEG" = true ]; then
    echo "Downloading ffmpeg (macOS arm64)..."
    curl -L -o /tmp/ffmpeg.zip \
        "https://ffmpeg.martin-riedl.de/redirect/latest/macos/arm64/snapshot/ffmpeg.zip"
    unzip -o /tmp/ffmpeg.zip -d /tmp/ffmpeg-extract
    mv /tmp/ffmpeg-extract/ffmpeg "$BIN_DIR/ffmpeg"
    rm -rf /tmp/ffmpeg.zip /tmp/ffmpeg-extract
    chmod +x "$BIN_DIR/ffmpeg"
    echo "ffmpeg downloaded."
else
    echo "ffmpeg already present and arm64-compatible."
fi

echo ""
echo "Binary check:"
file "$BIN_DIR/ffmpeg"
echo ""

# -------------------------------------------------------
# 3. Run PyInstaller
# -------------------------------------------------------
echo "Building .app with PyInstaller..."
$PYTHON -m PyInstaller --clean --noconfirm dlmc-video-downloader.spec

echo ""
echo "Build complete: $DIST_DIR/dlmc-video-downloader.app"

# -------------------------------------------------------
# 4. Package into .pkg for JAMF
# -------------------------------------------------------
echo "Creating .pkg installer..."

rm -rf "$PKG_STAGE"
mkdir -p "$PKG_STAGE/Applications"
cp -R "$DIST_DIR/dlmc-video-downloader.app" "$PKG_STAGE/Applications/"

pkgbuild --analyze --root "$PKG_STAGE" /tmp/dlmc-video-downloader-component.plist
/usr/libexec/PlistBuddy -c "Set :0:BundleIsRelocatable false" /tmp/dlmc-video-downloader-component.plist

pkgbuild \
    --root "$PKG_STAGE" \
    --scripts scripts \
    --component-plist /tmp/dlmc-video-downloader-component.plist \
    --identifier com.dlmc.video-downloader \
    --version "$VERSION" \
    --install-location / \
    "$SCRIPT_DIR/dlmc-video-downloader.pkg"

rm -f /tmp/dlmc-video-downloader-component.plist
rm -rf "$PKG_STAGE"

echo ""
echo "=== Done ==="
echo "App:     $DIST_DIR/dlmc-video-downloader.app"
echo "Package: $SCRIPT_DIR/dlmc-video-downloader.pkg"
echo ""
echo "To test the .pkg locally:"
echo "  sudo installer -pkg dlmc-video-downloader.pkg -target /"
echo "  open /Applications/dlmc-video-downloader.app"
