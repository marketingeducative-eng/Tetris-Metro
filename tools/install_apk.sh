#!/bin/bash

################################################################################
# Install APK Helper Script for Kivy/Buildozer
# 
# Purpose: Install APK on Android device, detect launcher activity dynamically,
#          and launch app with multiple fallback methods.
#
# Usage: ./tools/install_apk.sh /path/to/apk
#        ./tools/install_apk.sh bin/proxima-parada-debug.apk
#
# Requirements:
#  - adb (Android Debug Bridge)
#  - Connected Android device or emulator
#  - Optional: aapt (for APK package inspection, gracefully skipped if missing)
#
# Activity Detection Methods (in order):
#  1. adb shell cmd package resolve-activity --brief <package>
#  2. dumpsys package <package> | grep -A 1 MAIN
#  3. Try known Kivy default activity (org.kivy.android.PythonActivity)
#  4. monkey -p <package> 1 (interactive launch)
#
################################################################################

set -e

# Configuration
PACKAGE_NAME="org.larosa.metrotetris"

# Detect if output is TTY (for colors)
if [ -t 1 ]; then
    USE_COLORS=true
else
    USE_COLORS=false
fi

# Colors for output (only if TTY)
if [ "$USE_COLORS" = "true" ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Helper functions
print_header() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if APK path provided
if [ $# -eq 0 ]; then
    print_error "No APK path provided"
    echo ""
    echo "Usage: $0 /path/to/apk"
    echo "Example: $0 bin/proxima-parada-debug.apk"
    exit 1
fi

APK_PATH="$1"

# Validate APK exists
print_header "Step 1: Validating APK"
if [ ! -f "$APK_PATH" ]; then
    print_error "APK not found: $APK_PATH"
    exit 1
fi

APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
print_success "APK found: $APK_PATH ($APK_SIZE)"

# Check adb is available
print_header "Step 2: Checking ADB"
if ! command -v adb &> /dev/null; then
    print_error "adb not found in PATH"
    echo ""
    echo "Install Android SDK Platform Tools:"
    echo "  Ubuntu/Debian: sudo apt install android-tools-adb"
    echo "  macOS:         brew install android-platform-tools"
    echo "  Windows:       Download from https://developer.android.com/studio/releases/platform-tools"
    exit 1
fi

ADB_VERSION=$(adb version | head -n 1)
print_success "ADB available: $ADB_VERSION"

# Check for connected devices
print_header "Step 3: Checking Connected Devices"
DEVICES=$(adb devices -l | tail -n +2 | grep "device$" | awk '{print $1}')
DEVICE_COUNT=$(echo "$DEVICES" | grep -c "^" || echo 0)

if [ "$DEVICE_COUNT" -eq 0 ]; then
    print_error "No devices found"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Physical device: Enable USB debugging in Developer options"
    echo "  2. Emulator: Start from Android Studio or: emulator -avd <name>"
    echo "  3. Reconnect: adb kill-server && adb start-server"
    echo ""
    exit 1
fi

print_success "Found $DEVICE_COUNT device(s):"
adb devices -l | grep "device$" | awk '{printf "  - %s (%s)\n", $1, $NF}'

if [ "$DEVICE_COUNT" -gt 1 ]; then
    # Pick first device
    DEVICE=$(echo "$DEVICES" | head -n 1)
    print_warning "Multiple devices found, using: $DEVICE"
else
    DEVICE=$(echo "$DEVICES" | head -n 1)
fi

# Install APK
print_header "Step 4: Installing APK"
echo "Target: $DEVICE"
echo ""

if adb -s "$DEVICE" install -r "$APK_PATH"; then
    print_success "APK installed successfully"
else
    print_error "APK installation failed"
    exit 1
fi

# Extract package name and main activity from APK
print_header "Step 5: Detecting Package and Activity"

DETECTED_PACKAGE="$PACKAGE_NAME"
MAIN_ACTIVITY=""

# Try to extract package name with aapt if available
if command -v aapt &> /dev/null; then
    print_info "Using aapt to inspect APK..."
    DETECTED_PACKAGE=$(aapt dump badging "$APK_PATH" 2>/dev/null | grep "package:" | awk '{print $2}' | cut -d"'" -f2 2>/dev/null || echo "$PACKAGE_NAME")
    print_success "Detected package: $DETECTED_PACKAGE"
else
    print_info "aapt not available (optional), using default package: $DETECTED_PACKAGE"
    print_info "For precise APK inspection, install: sudo apt install aapt"
fi

# Try to launch the app
print_header "Step 6: Launching App"

LAUNCH_SUCCESS=false
RESOLVED_ACTIVITY=""

# Method 1: Use adb resolve-activity (Android 5.0+, preferred for Kivy)
if [ $LAUNCH_SUCCESS = false ]; then
    print_info "Detecting launcher activity via resolve-activity..."
    RESOLVED_ACTIVITY=$(adb -s "$DEVICE" shell cmd package resolve-activity --brief "$DETECTED_PACKAGE" 2>/dev/null | head -n 1 || echo "")
    
    if [ -n "$RESOLVED_ACTIVITY" ] && [ "$RESOLVED_ACTIVITY" != "null" ]; then
        print_info "Resolved activity: $RESOLVED_ACTIVITY"
        if adb -s "$DEVICE" shell am start -n "$DETECTED_PACKAGE/$RESOLVED_ACTIVITY" 2>/dev/null; then
            print_success "App launched: $RESOLVED_ACTIVITY"
            LAUNCH_SUCCESS=true
        fi
    else
        print_info "resolve-activity returned no result"
    fi
fi

# Method 2: Fallback to dumpsys package (detect MAIN activity)
if [ $LAUNCH_SUCCESS = false ]; then
    print_info "Detecting launcher activity via dumpsys..."
    RESOLVED_ACTIVITY=$(adb -s "$DEVICE" shell dumpsys package "$DETECTED_PACKAGE" 2>/dev/null | grep -A 1 "MAIN" | grep "\w\+/$" | head -n 1 | awk '{print $1}' | sed 's/^\/.*\///' | sed 's/}$//' || echo "")
    
    if [ -n "$RESOLVED_ACTIVITY" ] && [ "$RESOLVED_ACTIVITY" != "null" ]; then
        print_info "Dumpsys detected activity: $RESOLVED_ACTIVITY"
        if adb -s "$DEVICE" shell am start -n "$DETECTED_PACKAGE/$RESOLVED_ACTIVITY" 2>/dev/null; then
            print_success "App launched: $RESOLVED_ACTIVITY"
            LAUNCH_SUCCESS=true
        fi
    else
        print_info "dumpsys did not find MAIN activity"
    fi
fi

# Method 3: Try known Kivy default activity
if [ $LAUNCH_SUCCESS = false ]; then
    print_info "Attempting default Kivy activity (org.kivy.android.PythonActivity)..."
    if adb -s "$DEVICE" shell am start -n "$DETECTED_PACKAGE/org.kivy.android.PythonActivity" 2>/dev/null; then
        print_success "App launched (Kivy PythonActivity)"
        LAUNCH_SUCCESS=true
    else
        print_info "Default Kivy activity not found"
    fi
fi

# Method 4: Try monkey (interactive launch without assuming specific activity)
if [ $LAUNCH_SUCCESS = false ]; then
    print_info "Attempting interactive launch with monkey..."
    if adb -s "$DEVICE" shell monkey -p "$DETECTED_PACKAGE" 1 2>/dev/null; then
        print_success "App launched (interactive mode)"
        LAUNCH_SUCCESS=true
    else
        print_info "Interactive launch did not trigger (app may have no launchable activities)"
    fi
fi

if [ $LAUNCH_SUCCESS = false ]; then
    print_warning "Could not automatically launch app"
    echo ""
    echo "Possible causes:"
    echo "  - App has no launchable activities (check AndroidManifest.xml)"
    echo "  - Activity declaration missing MAIN/LAUNCHER intent-filter"
    echo "  - App requires specific permissions not granted"
    echo ""
    echo "Manual troubleshooting:"
    echo "  List installed packages: adb -s $DEVICE shell pm list packages | grep $DETECTED_PACKAGE"
    echo "  View app manifest: adb -s $DEVICE shell cmd package dump $DETECTED_PACKAGE"
    echo "  View logs: adb -s $DEVICE logcat -s 'python' -v time"
    echo "  Try manual launch: adb -s $DEVICE shell am start -n $DETECTED_PACKAGE/<ACTIVITY>"
    echo ""
fi

# Show verification
print_header "Step 7: Verification"

# Check if app is installed
if adb -s "$DEVICE" shell pm list packages | grep -q "$DETECTED_PACKAGE"; then
    print_success "App is installed"
else
    print_error "App installation verification failed"
    exit 1
fi

# Show app info
print_info "App info:"
adb -s "$DEVICE" shell pm dump "$DETECTED_PACKAGE" 2>/dev/null | head -n 10 || true

# Show recent logs (first 20 lines)
print_header "Recent Logs (last 20 lines)"
adb -s "$DEVICE" logcat -d --pid=$(adb -s "$DEVICE" shell pidof python) 2>/dev/null | tail -n 20 || \
adb -s "$DEVICE" logcat -d -s "python" 2>/dev/null | tail -n 20 || \
print_info "No Python logs found yet"

print_header "Installation Complete"
echo ""
echo "App installed and ready to test!"
echo ""
echo "Useful commands:"
echo "  View logs (real-time):  adb -s $DEVICE logcat -s 'python' -v time"
echo "  Launch app manually:    adb -s $DEVICE shell am start -n $DETECTED_PACKAGE/<ACTIVITY>"
echo "  Clear app data:         adb -s $DEVICE shell pm clear $DETECTED_PACKAGE"
echo "  Uninstall:              adb -s $DEVICE uninstall $DETECTED_PACKAGE"
echo ""
print_success "Done!"
