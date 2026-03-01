# Android SDK Configuration for Buildozer

## Overview
Buildozer requires proper Android SDK/NDK configuration to compile APK files. This guide ensures `sdkmanager` and `adb` are accessible.

---

## 1. Determine Your SDK Root

Run the SDK doctor to check current configuration:
```bash
bash tools/android_sdk_doctor.sh
```

Common Android SDK locations:
- **Ubuntu/Debian system install**: `/usr/lib/android-sdk`
- **Manual install**: `$HOME/Android/Sdk`
- **Buildozer auto-download**: `~/.buildozer/android/platform/android-sdk`

---

## 2. Export Environment Variables

Add to `~/.bashrc` or `~/.profile`:

```bash
# Android SDK Configuration
export ANDROID_SDK_ROOT="/usr/lib/android-sdk"
export ANDROID_HOME="$ANDROID_SDK_ROOT"

# Add sdkmanager to PATH (cmdline-tools/latest/bin)
export PATH="$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$PATH"

# Add platform-tools to PATH (for adb, fastboot)
export PATH="$ANDROID_SDK_ROOT/platform-tools:$PATH"
```

**Important**: Replace `/usr/lib/android-sdk` with your actual SDK root.

After editing, reload:
```bash
source ~/.bashrc
```

Verify:
```bash
echo $ANDROID_SDK_ROOT
which sdkmanager
which adb
```

---

## 3. Buildozer.spec Optional Configuration

If Buildozer cannot auto-detect SDK/NDK, add these lines to `buildozer.spec`:

### Option A: Let Buildozer Auto-Download (Default)
No changes needed. Buildozer will download SDK/NDK to `~/.buildozer/android/platform/`.

### Option B: Use System-Installed SDK

Add to `[app:android]` section (after `android.ndk = 25b`):

```ini
# Android SDK path (optional - if not auto-detected)
# android.sdk_path = /usr/lib/android-sdk

# Android NDK path (optional - if not auto-detected)  
# android.ndk_path = /usr/lib/android-sdk/ndk/25.2.9519653

# Automatically accept SDK licenses
android.accept_sdk_license = True

# Skip Android SDK/NDK update check
# android.skip_update = False

# Copy Python distribution from system (faster builds)
# android.copy_libs = 1
```

**Uncomment** `android.sdk_path` and `android.ndk_path` only if Buildozer fails to detect them.

---

## 4. Verify sdkmanager Path

Buildozer expects `sdkmanager` in one of these locations:
1. `$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager`
2. `$ANDROID_SDK_ROOT/tools/bin/sdkmanager` (legacy)
3. System PATH (via `which sdkmanager`)

### Fix "sdkmanager not found" Error

If Buildozer cannot find sdkmanager:

**Step 1**: Check if cmdline-tools exists:
```bash
ls -la /usr/lib/android-sdk/cmdline-tools/
```

**Step 2**: If missing, install via package manager:
```bash
sudo apt install google-android-cmdline-tools-12.0-installer
```

**Step 3**: Create `latest` symlink (if needed):
```bash
cd /usr/lib/android-sdk/cmdline-tools/
sudo ln -s 12.0 latest
```

**Step 4**: Verify:
```bash
sdkmanager --version
```

---

## 5. Accept SDK Licenses

Before first build:
```bash
sdkmanager --licenses --sdk_root="$ANDROID_SDK_ROOT"
```

Type `y` and press Enter for each license prompt.

Or run automated bootstrap:
```bash
bash scripts/android_sdk_bootstrap.sh
```

---

## 6. Install Required Packages

Minimum packages for Android 31 (API level 31):
```bash
sdkmanager --sdk_root="$ANDROID_SDK_ROOT" \
  "platform-tools" \
  "platforms;android-31" \
  "build-tools;31.0.0"
```

For newer API levels (recommended):
```bash
sdkmanager --sdk_root="$ANDROID_SDK_ROOT" \
  "platform-tools" \
  "platforms;android-34" \
  "build-tools;34.0.0"
```

---

## 7. Troubleshooting

### Issue: "Could not find sdkmanager"
- Run `bash tools/android_sdk_doctor.sh` to check PATH
- Verify `sdkmanager` symlink exists: `ls -la $ANDROID_SDK_ROOT/cmdline-tools/latest/bin/`
- Add to PATH: `export PATH="$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$PATH"`

### Issue: "ANDROID_SDK_ROOT not set"
- Check `~/.bashrc` for export statements
- Run `source ~/.bashrc` to reload
- Verify with `echo $ANDROID_SDK_ROOT`

### Issue: "License not accepted"
- Run `sdkmanager --licenses --sdk_root="$ANDROID_SDK_ROOT"`
- Or add `android.accept_sdk_license = True` to buildozer.spec

### Issue: Buildozer downloads duplicate SDK
- Explicitly set `android.sdk_path` in buildozer.spec to use system SDK
- Saves disk space (~6GB) and build time

---

## 8. Quick Diagnostic Command

```bash
bash tools/android_sdk_doctor.sh
```

Checks:
- ✓ ANDROID_SDK_ROOT and ANDROID_HOME variables
- ✓ sdkmanager location and version
- ✓ adb location and version
- ✓ Installed platforms (android-*)
- ✓ Installed build-tools versions
- ✓ Disk space availability
- ✓ Java installation

Report saved to `logs/android_sdk_doctor_YYYYMMDD_HHMM.log`

---

## 9. Recommended Workflow

1. **First-time setup**:
   ```bash
   bash scripts/android_sdk_bootstrap.sh
   ```

2. **Verify configuration**:
   ```bash
   bash tools/android_sdk_doctor.sh
   ```

3. **Build APK**:
   ```bash
   bash scripts/build_android_debug.sh
   ```

4. **Monitor issues**: Check `logs/` directory for error logs

---

## References
- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [Android Command Line Tools](https://developer.android.com/studio/command-line)
- Project scripts: `scripts/android_sdk_bootstrap.sh`, `tools/android_sdk_doctor.sh`
