#!/bin/bash
# JAMF Script: Remove legacy dlmc-dlp application
# Deploy via a JAMF Policy (Scripts) targeting machines with the old install.
# Safe to run even if the app is not present.

set -euo pipefail

APP_PATH="/Applications/dlmc-dlp.app"
RECEIPT_ID="com.dlmc.dlmc-dlp"

echo "=== Remove Legacy dlmc-dlp ==="

# ------------------------------------------------------------------
# 1. Quit the app if it is currently running
# ------------------------------------------------------------------
if pgrep -x "dlmc-dlp" &>/dev/null; then
    echo "App is running — quitting..."
    pkill -x "dlmc-dlp" || true
    sleep 2
fi

# ------------------------------------------------------------------
# 2. Remove the .app bundle
# ------------------------------------------------------------------
if [ -d "$APP_PATH" ]; then
    echo "Removing $APP_PATH ..."
    rm -rf "$APP_PATH"
    echo "Removed."
else
    echo "$APP_PATH not found — skipping."
fi

# ------------------------------------------------------------------
# 3. Forget the package receipt so JAMF/pkgutil no longer tracks it
# ------------------------------------------------------------------
if pkgutil --pkg-info "$RECEIPT_ID" &>/dev/null; then
    echo "Forgetting package receipt: $RECEIPT_ID"
    pkgutil --forget "$RECEIPT_ID" || true
else
    echo "No receipt found for $RECEIPT_ID — skipping."
fi

# ------------------------------------------------------------------
# 4. Remove any login item / LaunchAgent if one was ever registered
#    (dlmc-dlp did not register one by default, but clean up anyway)
# ------------------------------------------------------------------
LAUNCH_AGENT="/Library/LaunchAgents/com.dlmc.dlmc-dlp.plist"
if [ -f "$LAUNCH_AGENT" ]; then
    echo "Removing LaunchAgent: $LAUNCH_AGENT"
    launchctl unload "$LAUNCH_AGENT" 2>/dev/null || true
    rm -f "$LAUNCH_AGENT"
fi

echo ""
echo "=== Legacy dlmc-dlp removal complete ==="
exit 0
