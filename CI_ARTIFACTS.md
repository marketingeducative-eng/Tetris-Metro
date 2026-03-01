# CI Artifacts - Download & Install Guide

## Overview

This guide explains how to download and install APKs built by GitHub Actions workflows for the Tetris-Metro (Pròxima Parada) project.

**Two build pipelines available**:
1. **Android Debug Build** (automatic on push/PR) - for testing
2. **Android Release Build** (manual trigger) - for production releases

---

## 🚀 Part 1: Executing Workflows

### Option A: Automatic Debug Builds (Default)

Every push to `main` branch automatically triggers a debug build.

**To manually trigger**:
1. Go to: `https://github.com/YOUR_REPO/actions`
2. Select: **"Android Debug Build"**
3. Click: **"Run workflow"** button
4. Wait for completion (5-30 minutes depending on cache)

**Output**: APK with debug symbols, ready for testing on device or emulator

---

### Option B: Manual Release Builds

For production or versioned releases.

**To trigger**:
1. Go to: `https://github.com/YOUR_REPO/actions`
2. Select: **"Android Release Build (Manual)"**
3. Click: **"Run workflow"** button
4. **Fill inputs**:
   - `version_name`: Enter exact version (e.g., `1.0.0`, `1.1.0-beta`)
   - `build_type`: Choose `release` or `debug`
5. Click: **"Run workflow"**
6. Wait for completion

**Output**: Release APK/AAB, suitable for Google Play or sideloading

---

## 📥 Part 2: Downloading Artifacts

### From GitHub Web UI (Easiest)

1. Go to: `https://github.com/YOUR_REPO/actions`
2. Click on the completed workflow run
3. Under **"Artifacts"** section, find:
   - For debug: `android-debug-apk` folder
   - For release: `proxima-parada-X.X.X-release` folder
4. Click download arrow next to the artifact
5. Unzip locally: `unzip android-debug-apk.zip` or `unzip proxima-parada-1.0.0-release.zip`

**Result**: `bin/proxima-parada-debug.apk` or `bin/proxima-parada-release.apk`

---

### From Command Line (GitHub CLI)

**Install GitHub CLI** (if not already installed):
```bash
# macOS
brew install gh

# Linux (Ubuntu/Debian)
sudo apt install gh

# Windows (via WSL or PowerShell)
# Download from https://github.com/cli/cli/releases
```

**Download artifact**:
```bash
# List recent workflow runs
gh run list --repo YOUR_REPO --workflow android-debug.yml --limit 5

# Download most recent
gh run download <RUN_ID> --repo YOUR_REPO --name android-debug-apk --dir .

# Or for release
gh run download <RUN_ID> --repo YOUR_REPO --name proxima-parada-1.0.0-release --dir .
```

---

## 📱 Part 3: Installing APK on Android Device

### Prerequisites

**Windows / WSL2**:
```powershell
# Install Android SDK Platform Tools
# Option 1: Using Chocolatey (Windows)
choco install android-sdk

# Option 2: Download directly
# https://developer.android.com/studio/releases/platform-tools
# Unzip and add to PATH
```

**Linux**:
```bash
# Ubuntu/Debian
sudo apt install android-tools-adb

# Fedora
sudo dnf install android-tools
```

**macOS**:
```bash
brew install android-platform-tools
```

**Verify installation**:
```bash
adb version
```

---

### Step 1: Connect Device

**Physical Device via USB**:
```bash
# 1. Enable Developer Mode on Android phone
#    Go to: Settings → About phone → Tap "Build number" 7 times

# 2. Enable USB Debugging
#    Settings → Developer options → USB Debugging → Enable

# 3. Plug USB cable into PC/laptop

# 4. Grant permission on phone when prompted
```

**Emulator (Android Studio)**:
```bash
# Start Android Studio emulator
# Or from command line:
emulator -avd <AVD_NAME> &
```

**Verify connection**:
```bash
adb devices
```

Expected output:
```
List of attached devices
emulator-5554          device
12345678               device
```

---

### Step 2: Install APK

**Option A: Using Helper Script (RECOMMENDED)**

```bash
# Make script executable
chmod +x tools/install_apk.sh

# Install APK
./tools/install_apk.sh /path/to/proxima-parada-debug.apk

# Example:
./tools/install_apk.sh bin/proxima-parada-debug.apk
```

**Script Features** (Kivy/Buildozer robust):

1. ✓ Validates APK file exists and is readable
2. ✓ Checks adb availability (with install instructions if missing)
3. ✓ Detects all connected devices
4. ✓ Installs APK with `adb install -r` (replaces existing)
5. ✓ **Detects launcher activity** (does NOT assume `.MainActivity`):
   - Tries `adb shell cmd package resolve-activity --brief` (Android 5.0+, preferred)
   - Falls back to `dumpsys package` for MAIN intent-filter parsing
   - Tries known Kivy default (`org.kivy.android.PythonActivity`)
   - Uses interactive launch via `monkey` if needed
6. ✓ Gracefully handles missing `aapt` (no hard failure)
7. ✓ Disables colors when not in TTY (for CI/automation)
8. ✓ Shows comprehensive logs and manual fallback options

**Why detection matters**: Kivy projects don't always use `.MainActivity`. The script dynamically discovers the correct launcher activity, making it compatible with any Kivy/Buildozer configuration.

---

**Option B: Manual adb Commands**

```bash
# 1. Install APK
adb install -r bin/proxima-parada-debug.apk

# 2. Launch app (if you know package name)
# Package name from buildozer.spec: org.larosa.metrotetris
adb shell am start -n org.larosa.metrotetris/org.kivy.android.PythonActivity

# 3. View logs in real time
adb logcat -s "python"
```

---

### Step 3: Verify Installation

**Check app is installed**:
```bash
adb shell pm list packages | grep metrotetris
# Output: package:org.larosa.metrotetris
```

---

## 🔍 Troubleshooting

### "No devices found"

**Problem**: `adb devices` shows empty list

**Solutions**:
```bash
# 1. Reconnect device
adb kill-server
adb start-server
adb devices

# 2. Check USB cable (try different port)

# 3. On Windows/WSL: ensure WSL has USB access
#    (This requires WSL 2 with usbipd or Windows 11 USB forwarding)

# 4. Check Android permissions on phone
#    Settings → Apps & notifications → Special app access → USB debugging
```

---

### "Installation failed: INSTALL_FAILED_EXISTING_PACKAGE"

**Problem**: App is already installed, can't overwrite

**Solutions**:
```bash
# Option 1: Use -r flag (script does this automatically)
adb install -r bin/proxima-parada-debug.apk

# Option 2: Uninstall first
adb uninstall org.larosa.metrotetris
adb install bin/proxima-parada-debug.apk
```

---

### "Installation failed: INSTALL_FAILED_NO_MATCHING_ABIS"

**Problem**: APK architecture doesn't match device

**Likely cause**: Device is 32-bit (armeabi-v7a) but APK is 64-bit (arm64-v8a)

**Solutions**:
```bash
# Check device architecture
adb shell uname -m

# Check APK architecture (requires aapt)
aapt dump badging bin/proxima-parada-debug.apk | grep native-code

# If no match: rebuild with different architecture (advanced)
```

---

### "App crashes immediately after launch"

**Check logs**:
```bash
adb logcat -s "python" -v time
# Look for "FATAL EXCEPTION" or import errors
```

**Common causes**:
- Missing assets (data/ files not included)
- Python dependency not available
- Incorrect permissions in buildozer.spec

---

### "Could not automatically launch app" (Activity Detection Failed)

**Problem**: Script tried all methods but couldn't detect or launch the app

**Possible causes**:
- App has no launchable activities (missing MAIN/LAUNCHER intent-filter)
- Activity declaration missing from `AndroidManifest.xml`
- Kivy misconfiguration in `buildozer.spec`
- App requires permissions not yet granted

**Troubleshooting**:

1. **Verify app is installed**:
   ```bash
   adb shell pm list packages | grep org.larosa.metrotetris
   # Should output: package:org.larosa.metrotetris
   ```

2. **Check what activity systems found**:
   ```bash
   # Try resolve-activity directly
   adb shell cmd package resolve-activity --brief org.larosa.metrotetris
   
   # Or check full manifest
   adb shell cmd package dump org.larosa.metrotetris
   ```

3. **View why app won't launch**:
   ```bash
   adb logcat -s "AndroidRuntime" -v time
   # Look for "Unable to find explicit activity", "ClassNotFound", etc.
   ```

4. **Manual launch options** (if detection fails):
   ```bash
   # Try known Kivy activity directly
   adb shell am start -n org.larosa.metrotetris/org.kivy.android.PythonActivity
   
   # Or try interactive launch
   adb shell monkey -p org.larosa.metrotetris 1
   
   # Watch logs in real-time
   adb logcat -s "python" -v time
   ```

5. **Advanced: Check buildozer.spec**:
   - Verify `android.entrypoint` points to correct Python module
   - Check `android.package` matches `org.larosa.metrotetris`
   - Ensure no typos in activity declarations

**Note**: The script uses multiple detection methods (resolve-activity → dumpsys → Kivy defaults → monkey) to be compatible with various Kivy configurations. If all fail, the Android app configuration may need review.

---

### "adb: command not found" (Windows/WSL)

**Problem**: adb not in PATH

**Fix**:
```bash
# Find Android SDK location
# Usually: Windows: C:\Users\<username>\AppData\Local\Android\sdk\platform-tools
# WSL: /mnt/c/Users/<username>/AppData/Local/Android/sdk/platform-tools

# Add to PATH
export PATH="/mnt/c/Users/usuario/AppData/Local/Android/sdk/platform-tools:$PATH"

# Or download platform-tools separately:
cd ~/android-tools
unzip platform-tools-latest-linux.zip
export PATH="~/android-tools/platform-tools:$PATH"
```

---

## 📊 Workflow Details

### Debug Build Workflow (`android-debug.yml`)

**Trigger**: Every push/PR to `main`

**Build time**: 
- First: 18-25 min (SDK/NDK download)
- Cached: 8-12 min

**Output**:
- `android-debug-apk/bin/proxima-parada-debug.apk`
- Retention: 30 days

**Best for**: Testing, CI validation

---

### Release Build Workflow (`android-release.yml`)

**Trigger**: Manual via GitHub UI

**Inputs**:
- `version_name` (required): semantic version (1.0.0, 1.1.0-beta, etc.)
- `build_type` (required): debug or release (default: release)

**Build time**:
- First: 18-25 min
- Cached: 8-12 min

**Output**:
- `proxima-parada-{version}-release/bin/proxima-parada-release.aab` (app bundle)
- `proxima-parada-{version}-release/bin/proxima-parada-release.apk` (sideload APK)
- `release-notes-{version}/release_notes.txt` (metadata)
- Retention: 90 days

**Best for**: Production releases, versioned deployments

---

## 🎯 Quick Start Summary

```bash
# 1. Download APK from GitHub Actions artifact
gh run download <RUN_ID> --repo YOUR_REPO --name android-debug-apk --dir .

# 2. Extract
unzip android-debug-apk.zip

# 3. Install & launch (automatic)
./tools/install_apk.sh bin/proxima-parada-debug.apk

# 4. View logs
adb logcat -s "python" -v time

# 5. Uninstall (if needed)
adb uninstall org.larosa.metrotetris
```

---

## 📝 Notes

- **Package name**: `org.larosa.metrotetris` (from buildozer.spec)
- **Min API**: 21 (Android 5.0)
- **Target API**: 31 (Android 12)
- **Architecture**: arm64-v8a (64-bit only)
- **Orientation**: Portrait

---

## 🆘 Need Help?

**Check workflow logs**:
1. Go to Actions tab
2. Click on the failed run
3. Expand each step to see output

**Common errors in logs**:
- Memory issues: Check post-build diagnostics
- Gradle errors: Check "Configure Gradle/JVM" step
- Asset errors: Check CI_READINESS.md for asset inclusion

---

**Last Updated**: 2026-03-01  
**Project**: Tetris-Metro (Pròxima Parada)
