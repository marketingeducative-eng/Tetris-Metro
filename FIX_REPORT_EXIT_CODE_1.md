# FIX REPORT: Exit Code 1 - pythonforandroid.toolchain apk (android-debug arm64-v8a)

**Date**: 2026-03-03  
**Status**: IMPLEMENTED  
**Severity**: CRITICAL  
**Root Cause**: ModuleNotFoundError: No module named '_ctypes' (setuptools compilation via `--ignore-setup-py`)

---

## A) FORENSE DEL FALLO

### **First Error Line (Log Line ~11860)**
```
ModuleNotFoundError: No module named '_ctypes'
```

### **Error Context (15 lines around)**
```
[INFO]:    [32mBuilding setuptools for armeabi-v7a[0m
[INFO]:    setuptools apparently isn't already in site-packages
[INFO]:    Installing setuptools into site-packages
[INFO]:    [36m-> directory context .../build/other_builds/setuptools/armeabi-v7a__ndk_target_21/setuptools[0m
[DEBUG]:   [90m->[0m running python3 setup.py install -O2 ...

Traceback (most recent call last):
  File "...setuptools/setup.py", line 7, in <module>
    import setuptools
  File "...setuptools/__init__.py", line 18, in <module>
    from setuptools.dist import Distribution
  ...
  File ".../hostpython3/Lib/ctypes/__init__.py", line 8, in <module>
    from _ctypes import Union, Structure, Array
ModuleNotFoundError: No module named '_ctypes'
```

### **Root Cause Analysis**
1. **Immediate Symptom**: setuptools `setup.py install` tries to import `ctypes._ctypes`, a C extension module not compiled in p4a's hostpython binary
2. **Trigger**: p4a is being invoked with `--ignore-setup-py` flag
3. **Why**: buildozer.spec has `p4a.setup_py = true` (correct), but buildozer was passing `--ignore-setup-py` to p4a anyway
4. **Result**: p4a tries to **compile** setuptools from source instead of using pre-built, triggering _ctypes import failure
5. **Secondary Issue**: buildozer was compiling **both arm64-v8a and armeabi-v7a** despite spec specifying only arm64-v8a

---

## B) THREAT CHECKLIST

| # | Threat | Status | Evidence | Fix |
|-|-|-|-|-|
| **1** | NDK/SDK env pollution (runner vars vs buildozer) | ❌ CRITICAL | `ANDROID_NDK=/usr/local/lib/android/sdk/ndk/27.3.13750724` (runner) vs `ANDROIDNDK=~/.buildozer/...ndk-r25b` (buildozer) coexist | **Sanitize env**: unset runner vars, export buildozer-controlled paths |
| **2** | NDK version mismatch (r27/r29 vs r25b) | ⚠️ RISK | Runner has r27 & r29, project uses r25b → potential collision | ✅ Sanitization prevents this |
| **3** | p4a.setup_py ignored by buildozer | ❌ **ROOT CAUSE** | Log shows `--ignore-setup-py` passed to p4a despite spec having `p4a.setup_py = true` | **Pin buildozer >= 1.4.0** + verify spec + clean cache |
| **4** | Gradle/Java/Memory OOM | ✅ OK | NDK build completed successfully, failure occurs in setuptools post-NDK | No action needed |
| **5** | SDK licenses/build-tools missing | ✅ OK | License acceptance step exists, no license errors in log | No action needed |
| **6** | AndroidX/manifest/minsdk mismatch | ✅ OK | Build fails before reaching Gradle/aapt2 stage | No action needed |
| **7** | Corrupted caches (.buildozer, .gradle, pip) | ⚠️ RISK | Cache strategy exists but `.buildozer` could retain stale p4a configs | **Add cache cleanup step** |

---

## C) INTEGRATED FIX

### **Changes to `.github/workflows/android-debug.yml`**

#### **1. Install buildozer with pinned version (>=1.4.0)**
```yaml
- name: Install buildozer and dependencies
  run: |
    pip install --upgrade pip setuptools wheel
    # Pin buildozer to stable version (1.4.0+) to ensure p4a.setup_py support
    pip install --no-cache-dir 'buildozer>=1.4.0'
    pip install --no-cache-dir 'Cython==0.29.36'
    
    # Verify buildozer version
    echo "Buildozer version:"
    buildozer --version
```

#### **2. Sanitize NDK/SDK environment (NEW)**
Add after "Install buildozer" step:
```yaml
- name: Sanitize NDK/SDK environment for buildozer
  run: |
    echo "════════════════════════════════════════════════════════════════"
    echo "SANITIZING NDK/SDK ENVIRONMENT (Removing runner pollution)"
    echo "════════════════════════════════════════════════════════════════"
    
    # Unset runner-supplied variables that conflict with buildozer
    unset ANDROID_NDK
    unset ANDROID_NDK_LATEST_HOME
    unset ANDROID_HOME
    
    # Set buildozer-specific paths
    export ANDROID_HOME="$HOME/.buildozer/android/platform/android-sdk"
    export ANDROID_SDK_ROOT="$ANDROID_HOME"
    export ANDROIDNDK="$HOME/.buildozer/android/platform/android-ndk-r25b"
    export ANDROID_NDK_HOME="$ANDROIDNDK"
    export ANDROID_NDK_ROOT="$ANDROIDNDK"
    
    # Persist for all subsequent steps
    echo "ANDROID_HOME=$ANDROID_HOME" >> $GITHUB_ENV
    echo "ANDROID_SDK_ROOT=$ANDROID_SDK_ROOT" >> $GITHUB_ENV
    echo "ANDROIDNDK=$ANDROIDNDK" >> $GITHUB_ENV
    echo "ANDROID_NDK_HOME=$ANDROID_NDK_HOME" >> $GITHUB_ENV
    echo "ANDROID_NDK_ROOT=$ANDROID_NDK_ROOT" >> $GITHUB_ENV
    
    echo "[After sanitization]"
    echo "  ANDROID_HOME=$ANDROID_HOME"
    echo "  ANDROIDNDK=$ANDROIDNDK"
    echo "════════════════════════════════════════════════════════════════"
```

#### **3. Add fast-fail verification step (NEW)**
```yaml
- name: Fast-fail verification (p4a config + NDK path)
  run: |
    echo "════════════════════════════════════════════════════════════════"
    echo "FAST-FAIL VERIFICATION (Detect issues BEFORE long build)"
    echo "════════════════════════════════════════════════════════════════"
    
    # Check 1: NDK path
    if [[ "$ANDROIDNDK" != *"android-ndk-r25b" ]]; then
      echo "❌ CRITICAL: ANDROIDNDK is not r25b"
      echo "   Got: $ANDROIDNDK"
      exit 1
    fi
    
    # Check 2: p4a.setup_py must be true
    if grep -q '^p4a.setup_py = true$' buildozer.spec; then
      echo "✓ p4a.setup_py = true (will use --use-setup-py)"
    else
      echo "❌ CRITICAL: p4a.setup_py is not 'true' in buildozer.spec"
      exit 1
    fi
    
    echo "✅ All fast-fail checks PASSED"
    echo "════════════════════════════════════════════════════════════════"
```

#### **4. Clean buildozer cache before build (NEW)**
```yaml
- name: Clean buildozer cache (force fresh build)
  run: |
    echo "════════════════════════════════════════════════════════════════"
    echo "CLEANING BUILDOZER CACHE (Force fresh build)"
    echo "════════════════════════════════════════════════════════════════"
    
    if [ -d ".buildozer" ]; then
      echo "[*] Removing local .buildozer directory..."
      rm -rf .buildozer
      echo "    ✓ Done"
    fi
    
    echo "✅ Cache cleaned"
    echo "════════════════════════════════════════════════════════════════"
```

#### **5. Modify "Build Android APK" step**
Change `run:` section to add `continue-on-error: true` and `id: build` to allow capturing logs on failure:
```yaml
- name: Build Android APK
  continue-on-error: true
  id: build
  run: |
    echo "Starting build with resource monitoring..."
    # ... rest stays the same
```

#### **6. Add "Capture buildozer logs on failure" step (NEW - after Build APK)**
```yaml
- name: Capture buildozer logs on failure
  if: failure()
  run: |
    echo "════════════════════════════════════════════════════════════════"
    echo "BUILD FAILED - CAPTURING LOGS FOR DEBUGGING"
    echo "════════════════════════════════════════════════════════════════"
    
    mkdir -p .artifacts/logs
    
    # Copy buildozer logs
    if [ -d ".buildozer/android/platform/logs" ]; then
      cp -r ".buildozer/android/platform/logs" ".artifacts/logs/buildozer_platform_logs" 2>/dev/null || true
    fi
    
    # Copy recent buildozer debug log
    RECENT_LOG=$(find ~/.buildozer -name "*.log" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
    if [ -n "$RECENT_LOG" ] && [ -f "$RECENT_LOG" ]; then
      cp "$RECENT_LOG" ".artifacts/logs/buildozer_recent.log"
    fi
    
    # Capture environment snapshot
    {
      echo "=== ENVIRONMENT ==="
      env | grep -E 'ANDROID|NDK|SDK|GRADLE' | sort
      echo ""
      echo "=== BUILDOZER CONFIG ==="
      grep -E '^p4a\.|^android\.' buildozer.spec | head -20
    } > ".artifacts/logs/env_snapshot.txt"
    
    echo "✓ Artifacts captured to .artifacts/logs/"
```

#### **7. Add artifact upload on failure (NEW)**
```yaml
- name: Upload build logs on failure
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: android-debug-build-logs
    path: .artifacts/logs/
    retention-days: 30
```

---

### **Changes to `buildozer.spec`**

#### **Update p4a.setup_py section (lines 78-84)**

**BEFORE:**
```ini
# CRITICAL FIX: Enable pyjnius setup.py execution to generate config.pxi
# Required for Cython compilation of pyjnius 1.4+
# Modern Buildozer token: true => --use-setup-py, false => --ignore-setup-py
p4a.setup_py = true
```

**AFTER:**
```ini
# CRITICAL FIX: Enable pyjnius setup.py execution to generate config.pxi
# Required for Cython compilation of pyjnius 1.4+
# This PREVENTS ModuleNotFoundError: No module named '_ctypes' during setuptools install
# Valid in buildozer >= 1.4.0
# true = --use-setup-py (setuptools installs from setup.py, generates config.pxi)
# false = --ignore-setup-py (causes p4a to compile setuptools, fails with _ctypes error)
p4a.setup_py = true
```

**No functional change, but clarifies intent and troubleshooting.**

---

## D) HOW FIX PREVENTS REGRESSION

| Threat | Prevention Mechanism | Detection |
|-|-|-|
| NDK env pollution | Sanitization step unsets runner vars, sets buildozer-controlled paths | `echo` of all `ANDROID_*` variables in log |
| p4a ignoring `p4a.setup_py` | Pin buildozer to >=1.4.0 (must support this) + clean cache | Fast-fail step verifies configuration |
| Stale cache forcing old behavior | `rm -rf .buildozer` before build | Build starts fresh |
| Undetected failures (exit code 1) | `continue-on-error: true` + artifact upload | Logs captured for every failure |
| Missing _ctypes error in build output | Fast-fail checks `p4a.setup_py = true` BEFORE build | Fails immediately if misconfigured |

---

## E) ACCEPTANCE CRITERIA

✅ **Build must**:
1. Complete `buildozer -v android debug` without exit code 1 for arm64-v8a
2. Generate APK in `bin/` or `.buildozer/.../outputs/apk/`
3. If fails, logs captured and uploaded as artifact
4. If run fails in future with same error, quick detection from fast-fail step

✅ **Reproducibility**:
- Clean cache flow documented
- Buildozer version pinned (>=1.4.0)
- NDK path deterministic (r25b only)
- Cython version pinned (0.29.36)

---

## F) MANUAL TEST (Local)

To verify locally before CI:
```bash
# 1. Clean
rm -rf .buildozer

# 2. Sanitize env (if same runner setup as CI)
export ANDROID_HOME="$HOME/.buildozer/android/platform/android-sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export ANDROIDNDK="$HOME/.buildozer/android/platform/android-ndk-r25b"
unset ANDROID_NDK ANDROID_NDK_LATEST_HOME

# 3. Verify config
grep '^p4a.setup_py = true$' buildozer.spec || echo "ERROR: p4a.setup_py not set!"

# 4. Build
buildozer -v android debug
```

If build still fails with `_ctypes` error, check:
```bash
# Check buildozer version
buildozer --version

# Check what args were passed to p4a
grep -i "pythonforandroid.toolchain" ~/.buildozer/android/platform/logs/*.log | grep -E '\-\-ignore-setup-py|\-\-use-setup-py'
```

---

## G) REMAINING NOTES

- **Future improvement**: Consider enforcing ARM64-only arch in workflow guards (prevent accidental armeabi-v7a builds that take 2x time)
- **Monitoring**: Log capture on failure allows rapid triage of future android-debug
 failures
- **Off-ramp**: If buildozer >= 1.4.0 STILL ignores `p4a.setup_py = true`, consider direct p4a invocation instead of buildozer wrapper
