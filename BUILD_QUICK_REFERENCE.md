# Quick Reference: Build Requirements Checklist

**All items MUST be verified before attempting build. Use this checklist during troubleshooting.**

## ✅ Pre-Build Checklist

### Step 1: Buildozer Version
```bash
python3 -m pip show buildozer | grep Version
# Must show: Version: 1.5.0 or higher (>= 1.4.0)
```
- [ ] Version is >= 1.4.0

### Step 2: buildozer.spec - Requirements Section
```bash
grep "^requirements" buildozer.spec
# Must include: Cython==0.29.36 and pyjnius==1.6.1
```
Expected output contains:
```
python3,kivy,setuptools,Cython==0.29.36,pyjnius==1.6.1
```
- [ ] Cython==0.29.36 present (NOT 3.x)
- [ ] pyjnius==1.6.1 present
- [ ] setuptools present
- [ ] NO armeabi-v7a in requirements

### Step 3: buildozer.spec - Architecture
```bash
grep "^android.archs" buildozer.spec
# Must be EXACTLY: android.archs = arm64-v8a
```
- [ ] Shows exactly: `android.archs = arm64-v8a`
- [ ] NO armeabi-v7a
- [ ] NO x86 or x86_64

### Step 4: buildozer.spec - NDK Settings
```bash
grep "^android.ndk " buildozer.spec
grep "^android.ndk_api" buildozer.spec
```
- [ ] `android.ndk = 25b` (NOT 26, 27, or others)
- [ ] `android.ndk_api = 21` (minimum API level)

### Step 5: buildozer.spec - p4a.setup_py
```bash
grep "^p4a.setup_py" buildozer.spec
# Must show: p4a.setup_py = true
```
- [ ] `p4a.setup_py = true` (NOT false)
- [ ] CRITICAL: This enables setuptools execution

### Step 6: NDK Directory Structure
```bash
ls -lh ~/.buildozer/android/platform/android-ndk-r25b/platforms/android-21
# Must be a symlink, not empty directory

ls -lh ~/.buildozer/android/platform/android-ndk-r25b/toolchains/llvm/prebuilt/linux-x86_64/bin/clang
# Must exist and be executable or symlink
```
- [ ] `platforms/android-21` is a symlink
- [ ] Symlink points to: `.../sysroot`
- [ ] `clang` binary/symlink exists

### Step 7: Environment Variables
```bash
# Option 1: Manual setup
export ANDROID_NDK_HOME="$HOME/.buildozer/android/platform/android-ndk-r25b"
export ANDROID_NDK="$HOME/.buildozer/android/platform/android-ndk-r25b"
export ANDROID_NDK_LATEST_HOME="$HOME/.buildozer/android/platform/android-ndk-r25b"

# Option 2: Use setup script
source scripts/setup_build_env.sh

# Verify:
echo $ANDROID_NDK_HOME  # Should end with: android-ndk-r25b
echo $ANDROID_NDK       # Should end with: android-ndk-r25b
```
- [ ] ANDROID_NDK_HOME set to r25b path
- [ ] ANDROID_NDK set to r25b path
- [ ] ANDROID_NDK_LATEST_HOME set to r25b path

### Step 8: setup.py Validation
```bash
grep "ext_modules=" setup.py
# Should NOT contain aggressive cythonize() directives
```
- [ ] setup.py does NOT have `ext_modules=cythonize(...)`
- [ ] Has basic `find_packages()`
- [ ] Has `install_requires` with pinned versions

---

## 🔧 Quick Commands

### Run Full Validation
```bash
/tmp/validate_env.sh
```
Expected: All 4 sections show ✅

### Setup Environment
```bash
source scripts/setup_build_env.sh
```
Expected: "✅ BUILD ENVIRONMENT READY!"

### Clean Build
```bash
buildozer -v android clean
```

### Start Build
```bash
buildozer -v android debug
```

---

## ⚠️ Common Failures & Fixes

| Error Message | Cause | Fix |
|---------------|-------|-----|
| "Unsupported class file major version 65" | NDK v27 being used instead of r25b | `source scripts/setup_build_env.sh` |
| "Cannot find android-21 headers" | Missing `platforms/android-21` symlink | Run symlink creation manually |
| "pyjnius: No module named '_ctypes'" | `p4a.setup_py = false` | Set to `true` in buildozer.spec |
| "Cython 3.x compilation error" | Wrong Cython version | Must use Cython==0.29.36 |
| "armeabi-v7a not found" | Multiple architectures configured | Set `android.archs = arm64-v8a` only |
| "buildozer: command not found" | Not in venv or not installed | `source .venv/bin/activate` first |

---

## 📋 What Each Fix Prevents

1. **Buildozer >= 1.4.0**
   - Enables `p4a.setup_py = true` option
   - Ensures proper setuptools integration

2. **NDK r25b + Environment Variables**
   - Prevents runner's NDK v27 from interfering
   - Ensures p4a uses correct NDK version
   - Avoids "Unsupported class file major version 65" error

3. **platforms/android-21 Symlink**
   - Redirects p4a header searches to actual location
   - Prevents "Cannot find android-21" failures
   - Makes legacy p4a compatible with NDK r25b

4. **Cython==0.29.36**
   - Maintains Python 3.10+ compatibility
   - Avoids Cython 3.x breaking changes (removed `long` type)

5. **pyjnius==1.6.1**
   - Compatible with Cython 0.29.36
   - Provides JNI bindings for Android

6. **p4a.setup_py = true**
   - Enables setuptools execution
   - Generates config.pxi for Cython
   - Prevents _ctypes module errors

7. **Single Architecture (arm64-v8a)**
   - Faster build time
   - Sufficient for modern Android devices
   - Prevents cross-architecture confusion

---

## ✅ Ready to Build?

When all checklist items are marked [ ], you can proceed:

```bash
source scripts/setup_build_env.sh
buildozer -v android debug
```

Expected build time: 20-35 minutes depending on machine

---

**Last Updated:** March 4, 2026
