#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

BIN_DIR="$SCRIPT_DIR/bin"
DIST_DIR="$SCRIPT_DIR/dist"
PKG_STAGE="$SCRIPT_DIR/pkg-stage"

echo "=== dlmc-dlp build script ==="

# -------------------------------------------------------
# 1. Ensure PyInstaller is installed
# -------------------------------------------------------
if ! python3 -m PyInstaller --version &>/dev/null; then
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
fi
echo "PyInstaller $(python3 -m PyInstaller --version)"

# -------------------------------------------------------
# 2. Download binaries if needed
# -------------------------------------------------------
mkdir -p "$BIN_DIR"

# --- yt-dlp ---
# Remove old directory-based yt-dlp if it exists
if [ -d "$BIN_DIR/yt-dlp" ]; then
    echo "Removing old yt-dlp directory..."
    rm -rf "$BIN_DIR/yt-dlp"
fi

if [ ! -f "$BIN_DIR/yt-dlp" ]; then
    echo "Downloading yt-dlp (macOS universal binary)..."
    curl -L -o "$BIN_DIR/yt-dlp" \
        "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos"
    chmod +x "$BIN_DIR/yt-dlp"
    echo "yt-dlp downloaded."
else
    echo "yt-dlp binary already present."
fi

# --- ffmpeg ---
# Check if existing ffmpeg is arm64-compatible
NEED_FFMPEG=false
if [ ! -f "$BIN_DIR/ffmpeg" ]; then
    NEED_FFMPEG=true
elif ! file "$BIN_DIR/ffmpeg" | grep -q "arm64"; then
    echo "Existing ffmpeg is not arm64-compatible, replacing..."
    NEED_FFMPEG=true
fi

if [ "$NEED_FFMPEG" = true ]; then
    echo "Downloading ffmpeg (macOS arm64 binary)..."
    # martin-riedl.de provides signed arm64 static builds for macOS
    curl -L -o /tmp/ffmpeg.zip \
        "https://ffmpeg.martin-riedl.de/redirect/latest/macos/arm64/snapshot/ffmpeg.zip"
    unzip -o /tmp/ffmpeg.zip -d /tmp/ffmpeg-extract
    mv /tmp/ffmpeg-extract/ffmpeg "$BIN_DIR/ffmpeg"
    rm -rf /tmp/ffmpeg.zip /tmp/ffmpeg-extract
    chmod +x "$BIN_DIR/ffmpeg"
    echo "ffmpeg downloaded."
else
    echo "ffmpeg binary already present and arm64-compatible."
fi

# Verify binaries
echo ""
echo "Binary check:"
file "$BIN_DIR/yt-dlp"
file "$BIN_DIR/ffmpeg"
echo ""

# -------------------------------------------------------
# 3. Run PyInstaller
# -------------------------------------------------------
echo "Building .app with PyInstaller..."
python3 -m PyInstaller --clean --noconfirm dlmc-dlp.spec

echo ""
echo "Build complete: $DIST_DIR/dlmc-dlp.app"

# -------------------------------------------------------
# 4. Package into .pkg for JAMF
# -------------------------------------------------------
echo "Creating .pkg installer..."

# Stage the .app for pkgbuild
rm -rf "$PKG_STAGE"
mkdir -p "$PKG_STAGE/Applications"
cp -R "$DIST_DIR/dlmc-dlp.app" "$PKG_STAGE/Applications/"

# Create a component plist and disable bundle relocation so the .app
# always installs to /Applications regardless of existing copies elsewhere.
pkgbuild --analyze --root "$PKG_STAGE" /tmp/dlmc-dlp-component.plist
# Set BundleIsRelocatable to false
/usr/libexec/PlistBuddy -c "Set :0:BundleIsRelocatable false" /tmp/dlmc-dlp-component.plist

pkgbuild \
    --root "$PKG_STAGE" \
    --component-plist /tmp/dlmc-dlp-component.plist \
    --identifier com.dlmc.dlmc-dlp \
    --version 1.2 \
    --install-location / \
    "$SCRIPT_DIR/dlmc-dlp.pkg"

rm -f /tmp/dlmc-dlp-component.plist

# Clean up staging
rm -rf "$PKG_STAGE"

echo ""
echo "=== Done ==="
echo "App:     $DIST_DIR/dlmc-dlp.app"
echo "Package: $SCRIPT_DIR/dlmc-dlp.pkg"
echo ""
echo "To test the .pkg locally:"
echo "  sudo installer -pkg dlmc-dlp.pkg -target /"
echo "  open /Applications/dlmc-dlp.app"
