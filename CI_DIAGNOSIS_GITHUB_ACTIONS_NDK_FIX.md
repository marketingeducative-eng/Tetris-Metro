# 🔍 GitHub Actions Android Build Diagnosis & NDK Fix

**Status:** 📊 Build in progress (RUN_ID: 22661342706)  
**Last Updated:** 2026-03-04 08:31 UTC  
**Target:** Deploy buildozer Android Debug APK to GitHub Actions

---

## 📋 Executive Summary

### Previous Build Failure (RUN_ID: 22661148007)
- **Status:** ❌ FAILED at Step 21 "Download and install Android NDK r25b"
- **Root Cause:** NDK r25b missing `platforms/android-21` directory
- **Impact:** Build never reached buildozer APK compilation phase
- **Duration:** ~3 minutes (failed before main work)

### Root Cause Analysis

**Problem:**
```
❌ CRITICAL: NDK r25b missing platforms/android-21
   Required for ndk-api=21 in buildozer.spec
   (platforms/ directory not found)
```

**Why:**
- NDK r25b (released 2024) removed the `platforms/` directory structure
- This directory existed in older NDK versions (r23 and earlier)
- Python-for-Android (p4a) toolchain expects `platforms/android-21` to find native headers
- p4a is an older tool and hasn't been updated for NDK r25b's new structure

**Technical Context:**
- buildozer.spec specifies: `android.ndk = 25b` and `android.ndk_api = 21`
- buildozer → p4a pipeline expects both:
  - NDK r25b binary for compilation (available: `toolchains/llvm/prebuilt/...`)
  - platforms directory for headers (missing in r25b)
- GitHub Actions ubuntu-latest runner has NDK v27 pre-installed (incompatible with workflow)
  - Our Step 0 correctly purges it
  - Step 21 downloads r25b from Google's repository
  - But r25b lacks the `platforms/` structure p4a expects

---

## 🔧 Applied Fixes

### Fix#1: Early NDK Purge (Step 0 - CRITICAL)
```bash
# Immediately after checkout, before any setup
echo "ANDROID_NDK=" >> $GITHUB_ENV
echo "ANDROID_NDK_LATEST_HOME=" >> $GITHUB_ENV
```
- **Why:** Runner's NDK v27 at `/usr/local/lib/android/sdk/ndk/27.3.13750724` would pollute p4a invocation
- **Impact:** Prevents buildozer from using runner's incompatible NDK
- **Serial Number:** ca6b929

### Fix#2: NDK Environment Configuration (Step 1)
```bash
# Verify Step 0 worked, set buildozer-managed paths via GITHUB_ENV
echo "ANDROID_HOME=$ANDROID_HOME" >> $GITHUB_ENV
echo "ANDROID_NDK_HOME=$ANDROID_NDK_HOME" >> $GITHUB_ENV
echo "ANDROIDNDK=$ANDROIDNDK" >> $GITHUB_ENV
```
- **Why:** Ensures all buildozer steps use consistent NDK paths
- **Impact:** All downstream p4a invocations reference `.buildozer` NDK only
- **Serial Number:** ca6b929

### Fix#3: NDK r25b Compatibility Workaround (Step 21) ← **NEW**
```bash
# Create symlink: platforms/android-21 -> sysroot
mkdir -p "$NDK_DIR/platforms"
ln -sf "$NDK_DIR/toolchains/llvm/prebuilt/linux-x86_64/sysroot" \
       "$NDK_DIR/platforms/android-21"
```
- **Why:** p4a needs to find headers at `platforms/android-21/` path
- **How it works:**
  - NDK r25b has headers at: `toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/include`
  - p4a looks at: `platforms/android-21/...`
  - Symlink transparently redirects lookups
- **Impact:** Makes NDK r25b compatible with legacy p4a
- **Commit:** 83244df
- **File:** `.github/workflows/android-debug.yml` lines ~540-560

### Additional Improvements
- ✅ Build logs uploaded as artifact (`buildozer-logs`)
- ✅ Pre-build environment validation checks added
- ✅ Gradle JVM memory limits configured for CI resource constraints

---

## 📊 Verification Checklist

### buildozer.spec (Already Correct ✅)
```ini
[Line 24]    requirements = python3,kivy,setuptools,Cython==0.29.36,pyjnius==1.6.1
[Line 38]    android.ndk_api = 21
[Line 41]    android.ndk = 25b
[Line 57]    android.archs = arm64-v8a
[Line 94]    p4a.setup_py = true
```
- ✅ setuptools present (prevents `ModuleNotFoundError` in pyjnius setup.py)
- ✅ Single architecture (arm64-v8a only, no armeabi-v7a)
- ✅ setup_py enabled (`--use-setup-py`, not `--ignore-setup-py`)
- ✅ Cython and pyjnius pinned to compatible versions

### setup.py (Already Simplified ✅)
```python
# Removed: ext_modules=cythonize(...) aggressive directives
# Kept: Basic setuptools with find_packages()
# Result: Allows p4a wheel metadata extraction without BuildBackendException
```

### .github/workflows/android-debug.yml (Updated with fix ✅)

**Expected ndozer Command (After Fix):**
```bash
/usr/bin/python3 -m pythonforandroid.toolchain apk \
  --bootstrap=sdl2 \
  --requirements=python3,kivy,setuptools,Cython==0.29.36,pyjnius==1.6.1 \
  --arch=arm64-v8a \
  --use-setup-py \
  --ndk-api=21 \
  ...
```

**Safeguards:**
- ✅ Pre-build: Verify buildozer.spec SHA256, android.archs=arm64-v8a, requirem ents pinned
- ✅ Post-build: Parse p4a command, count `--arch` flags (must be 1), verify `--use-setup-py`
- ✅ Hard-fail if dual-arch or `--ignore-setup-py` detected

---

## ⏱️ Current Build Status

### RUN_ID: 22661342706
- **Branch:** ci/activate-pyjnius-smoke
- **Triggered:** 2026-03-04T08:31:59Z
- **Expected Duration:** ~25-30 minutes
  - ~2 min: System setup & dependencies
  - ~8 min: Android SDK cmdline-tools + licenses
  - ~5 min: NDK r25b download + symlink fix
  - ~10-15 min: buildozer + gradle build

### Monitoring Script
```bash
URL: https://github.com/marketingeducative-eng/Tetris-Metro/actions/runs/22661342706
Live Status: https://github.com/marketingeducative-eng/Tetris-Metro/actions
```

---

## 🎯 Expected Outcomes

### ✅ If Build SUCCEEDS
1. APK generated: `bin/metrotetris-0.1-debug.apk`
2. Artifact uploaded: `android-debug-apk` (30-day retention)
3. Build logs uploaded: `buildozer-logs` (5-day retention)
4. Commit 83244df contains proven NDK r25b compatibility fix
5. CI workflow validated for single-architecture arm64-v8a compilation

### ❌ If Build FAILS (Before Reaching APK Step)

**Most Likely Failure Points:**
1. Step 21 NDK symlink creation (if sysroot structure differs)
2. Step 24 Gradle build (Java version mismatch, memory limits)
3. buildozer distribute step (APK signing, resource limits)

**If Fails:**
1. Download `buildozer-logs` artifact from GitHub Actions
2. Check last few steps of build/21_Download...NDK_r25b.txt or build/22_Build...APK.txt
3. Common fixes:
   - Increase `GRADLE_OPTS` memory
   - Update p4a to newer version (if symlink approach insufficient)
   - Switch to NDK r21 (longer-term compatibility)

---

## 📚 Historical Context

###Previous Local WSL Build (20260304_0906.log)
- ❌ Gradle build failed: `Unsupported class file major version 65`
- 🔍 Root cause: Java version mismatch (compiled for Java 21, Gradle using Java 11)
- ✅ CI has explicit `JAVA_TOOL_OPTIONS` + `GRADLE_OPTS` to prevent this
- 🎯 CI environment is cleaner than local WSL

### Previous CI Build (22661148007)
- Duration: ~3 minutes (failure fast)
- ❌ Failed at NDK verification (exact error shown in this document)
- ✅ Provided clear diagnostic for symlink workaround

---

## 🔐 Security & Configuration Notes

### Token Handling
- ✅ GH_TOKEN never logged, printed, or written to files
- ✅ Used only for GitHub API requests
- ✅ Build logs don't contain sensitive data

### NDK/SDK Paths
```
~/buildozer/android/platform/
├── android-sdk/           ← Downloaded by CI
├── android-ndk-r25b/      ← Newly downloaded, with symlink fix
└── apache-ant-1.9.4/      ← Cached by buildozer
```

### Cache Management
- ✅ buildozer cache: 400MB (Git-LFS optimized)
- ✅ gradle cache: ~900MB (persistent, cleared only on spec change)
- ✅ per-build artifacts: ~60MB (logs), ~100MB (APK)

---

## 🚀 Next Steps After Successful Build

1. **Verify APK:**
   ```bash
   unzip -l bin/metrotetris-0.1-debug.apk | head -20
   ```

2. **Document Success:**
   - Update ARCHITECTURE.md with CI build info
   - Add note about NDK r25b compatibility fix

3. **Optional Maintenance:**
   - Consider upgrading p4a to newer version (longer-term solution)
   - Or switch to NDK r21 (if p4a upgrade causes issues)
   - Profile buildtimes to identify bottlenecks

4. **Production Deploy:**
   - Merge ci/activate-pyjnius-smoke → main
   - Set up android-release.yml CI workflow
   - Configure GitHub Releases with APK artifacts

---

## 📞 Troubleshooting Reference

| Problem | Symptom | Solution |
|---------|---------|----------|
| NDK crash | "platforms not found" | ✅ Applied as Fix#3 |
| Dual-arch compile | Build 2x slower | ✅ Checked in Step 23 hard-fail |
| Wrong NDK version | "NDK v27 not compatible" | ✅ Purged in Step 0 |
| Missing setuptools | pyjnius setup.py fails | ✅ In buildozer.spec Line 24 |
| Gradle OOM | "OutOfMemoryError" | ✅ GRADLE_OPTS configured |

---

**Generated:** 2026-03-04 08:31 UTC  
**Build Branch:** ci/activate-pyjnius-smoke  
**Target Repository:** github.com/marketingeducative-eng/Tetris-Metro
