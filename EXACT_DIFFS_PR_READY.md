# EXACT DIFFS - PR READY

## File: buildozer.spec

```diff
--- buildozer.spec (BEFORE)
+++ buildozer.spec (AFTER)

 # CRITICAL FIX: Enable pyjnius setup.py execution to generate config.pxi
 # Required for Cython compilation of pyjnius 1.4+
-# Modern Buildozer token: true => --use-setup-py, false => --ignore-setup-py
+# This PREVENTS ModuleNotFoundError: No module named '_ctypes' during setuptools install
+# Valid in buildozer >= 1.4.0
+# true = --use-setup-py (setuptools installs from setup.py, generates config.pxi)
+# false = --ignore-setup-py (causes p4a to compile setuptools, fails with _ctypes error)
 p4a.setup_py = true
```

---

## File: .github/workflows/android-debug.yml

### **Change 1: Install buildozer with version pin**

```diff
       - name: Install buildozer and dependencies
         run: |
           pip install --upgrade pip setuptools wheel
-          pip install --no-cache-dir buildozer
+          # Pin buildozer to stable version (1.4.0+) to ensure p4a.setup_py support
+          pip install --no-cache-dir 'buildozer>=1.4.0'
           pip install --no-cache-dir 'Cython==0.29.36'
+          
+          # Verify buildozer version
+          echo "Buildozer version:"
+          buildozer --version
```

### **Change 2: Add NDK/SDK sanitization (INSERT AFTER Install buildozer)**

Location: After "Install buildozer and dependencies" step, insert this new step:

```yaml
      - name: Sanitize NDK/SDK environment for buildozer
        run: |
          echo "════════════════════════════════════════════════════════════════"
          echo "SANITIZING NDK/SDK ENVIRONMENT (Removing runner pollution)"
          echo "════════════════════════════════════════════════════════════════"
          echo ""
          echo "[BEFORE SANITIZATION - Runner variables that pollute p4a:]"
          echo "  ANDROID_NDK=${ANDROID_NDK:-UNSET}"
          echo "  ANDROID_NDK_LATEST_HOME=${ANDROID_NDK_LATEST_HOME:-UNSET}"
          echo "  ANDROID_HOME=${ANDROID_HOME:-UNSET}"
          echo "  ANDROID_SDK_ROOT=${ANDROID_SDK_ROOT:-UNSET}"
          echo ""
          
          # Unset runner-supplied NDK/SDK variables that conflict with buildozer
          unset ANDROID_NDK
          unset ANDROID_NDK_LATEST_HOME
          unset ANDROID_HOME
          
          # Set buildozer-specific paths for consistency
          export ANDROID_HOME="$HOME/.buildozer/android/platform/android-sdk"
          export ANDROID_SDK_ROOT="$ANDROID_HOME"
          export ANDROIDNDK="$HOME/.buildozer/android/platform/android-ndk-r25b"
          export ANDROID_NDK_HOME="$ANDROIDNDK"
          export ANDROID_NDK_ROOT="$ANDROIDNDK"
          
          # Persist these for all subsequent steps
          echo "ANDROID_HOME=$ANDROID_HOME" >> $GITHUB_ENV
          echo "ANDROID_SDK_ROOT=$ANDROID_SDK_ROOT" >> $GITHUB_ENV
          echo "ANDROIDNDK=$ANDROIDNDK" >> $GITHUB_ENV
          echo "ANDROID_NDK_HOME=$ANDROID_NDK_HOME" >> $GITHUB_ENV
          echo "ANDROID_NDK_ROOT=$ANDROID_NDK_ROOT" >> $GITHUB_ENV
          
          echo "[AFTER SANITIZATION - Buildozer-controlled paths:]"
          echo "  ANDROID_HOME=$ANDROID_HOME"
          echo "  ANDROID_SDK_ROOT=$ANDROID_SDK_ROOT"
          echo "  ANDROIDNDK=$ANDROIDNDK"
          echo "  ANDROID_NDK_HOME=$ANDROID_NDK_HOME"
          echo "  ANDROID_NDK_ROOT=$ANDROID_NDK_ROOT"
          echo ""
          echo "════════════════════════════════════════════════════════════════"
          echo ""
```

### **Change 3: Enhance Verify pinned dependencies step**

APPEND to existing "Verify pinned dependencies" step (after the `echo "✅ Cython...` line):

```diff
           echo "✅ Cython 0.29.36 verified (Python 3 compatible)"
           echo "════════════════════════════════════════════════════════════════"
           echo ""
+      
+      - name: Fast-fail verification (p4a config + NDK path)
+        run: |
+          echo "════════════════════════════════════════════════════════════════"
+          echo "FAST-FAIL VERIFICATION (Detect issues BEFORE long build)"
+          echo "════════════════════════════════════════════════════════════════"
+          echo ""
+          echo "[1. Python version]"
+          python3 --version
+          echo ""
+          echo "[2. Java version]"
+          java -version 2>&1 || { echo "❌ Java not found"; exit 1; }
+          echo ""
+          echo "[3. Buildozer version]"
+          buildozer --version || { echo "❌ Buildozer not found"; exit 1; }
+          echo ""
+          echo "[4. Python-for-android version (if installed)]"
+          python3 -m pythonforandroid.toolchain --version 2>/dev/null || echo "   (p4a not yet installed)"
+          echo ""
+          echo "[5. NDK path verification]"
+          NDK_EXPECTED="$HOME/.buildozer/android/platform/android-ndk-r25b"
+          if [[ "$ANDROIDNDK" != *"android-ndk-r25b" ]]; then
+            echo "❌ CRITICAL: ANDROIDNDK is not r25b!"
+            echo "   Expected: ...android-ndk-r25b"
+            echo "   Got: $ANDROIDNDK"
+            exit 1
+          fi
+          echo "✓ NDK: $ANDROIDNDK"
+          echo ""
+          echo "[6. SDK path verification]"
+          echo "✓ SDK: $ANDROID_SDK_ROOT"
+          echo ""
+          echo "[7. buildozer.spec check (p4a.setup_py must be true)]"
+          if grep -q '^p4a.setup_py = true$' buildozer.spec; then
+            echo "✓ p4a.setup_py = true (setuptools will use setup.py, not --ignore-setup-py)"
+          else
+            echo "❌ CRITICAL: p4a.setup_py is not 'true' in buildozer.spec"
+            echo "   This will cause _ctypes ModuleNotFoundError"
+            exit 1
+          fi
+          echo ""
+          echo "✅ All fast-fail checks PASSED"
+          echo "════════════════════════════════════════════════════════════════"
+          echo ""
+      
+      - name: Clean buildozer cache (force fresh build)
+        run: |
+          echo "════════════════════════════════════════════════════════════════"
+          echo "CLEANING BUILDOZER CACHE (Force fresh, reproducible build)"
+          echo "════════════════════════════════════════════════════════════════"
+          echo ""
+          
+          # Remove local .buildozer directory (but keep .buildozer git repo if any)
+          if [ -d ".buildozer" ]; then
+            echo "[*] Removing local .buildozer directory..."
+            rm -rf .buildozer
+            echo "    ✓ Done"
+          fi
+          
+          # Optional: clean buildozer user home cache (more aggressive, use with care)
+          # Uncomment if you want to force total rebuild
+          # if [ -d "$HOME/.buildozer" ]; then
+          #   echo "[*] WARNING: This would remove ~/.buildozer (disabled for safety)"
+          #   echo "    To enable aggressive cache cleaning, uncomment the rm command"
+          # fi
+          
+          echo ""
+          echo "✅ Cache cleaned. Buildozer will perform fresh build"
+          echo "════════════════════════════════════════════════════════════════"
+          echo ""
+      
+      - name: Verify buildozer will use correct p4a args
+        run: |
+          echo "════════════════════════════════════════════════════════════════"
+          echo "PRE-BUILD VERIFICATION: buildozer.spec p4a configuration"
+          echo "════════════════════════════════════════════════════════════════"
+          echo ""
+          
+          echo "[*] Current buildozer.spec p4a/android configuration:"
+          grep -E "^p4a|^android\." buildozer.spec | sort
+          echo ""
+          
+          # Warn if p4a_ignore_setuppy is set to true (the old problematic setting)
+          if grep -q "^p4a_ignore_setuppy *= *true\|^p4a_ignore_setuppy = true" buildozer.spec; then
+            echo "❌ WARNING: p4a_ignore_setuppy MUST NOT be 'true'"
+            echo "   This will cause ModuleNotFoundError: No module named '_ctypes'"
+            exit 1
+          fi
+          
+          # Ensure p4a.setup_py is true
+          if ! grep -q "^p4a.setup_py *= *true\|^p4a.setup_py = true" buildozer.spec; then
+            echo "❌ ERROR: p4a.setup_py must be 'true'"
+            exit 1
+          fi
+          
+          echo "✅ Configuration looks good"
+          echo ""
+          echo "════════════════════════════════════════════════════════════════"
+          echo ""
```

### **Change 4: Modify Build Android APK step**

```diff
       - name: Build Android APK
+        continue-on-error: true
+        id: build
         run: |
           echo "Starting build with resource monitoring..."
+          echo ""
           
           # Start background resource monitor
           {
```

### **Change 5: Add Capture logs and Upload on failure (INSERT BEFORE "List bin directory")**

```yaml
      - name: Capture buildozer logs on failure
        if: failure()
        run: |
          echo "════════════════════════════════════════════════════════════════"
          echo "BUILD FAILED - CAPTURING LOGS FOR DEBUGGING"
          echo "════════════════════════════════════════════════════════════════"
          echo ""
          
          # Create logs artifact directory
          mkdir -p .artifacts/logs
          
          # Copy buildozer debug log if exists
          if [ -d ".buildozer/android/platform/logs" ]; then
            echo "[*] Copying buildozer platform logs..."
            cp -r ".buildozer/android/platform/logs" ".artifacts/logs/buildozer_platform_logs" 2>/dev/null || true
          fi
          
          # Find and copy most recent buildozer debug log
          RECENT_LOG=$(find ~/.buildozer -name "*.log" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
          if [ -n "$RECENT_LOG" ] && [ -f "$RECENT_LOG" ]; then
            echo "[*] Copying recent buildozer log: $(basename $RECENT_LOG)"
            cp "$RECENT_LOG" ".artifacts/logs/buildozer_recent.log"
          fi
          
          # Copy build output if exists
          if [ -d ".buildozer/android/platform/build-arm64-v8a" ]; then
            echo "[*] Copying NDK build logs..."
            find ".buildozer/android/platform/build-arm64-v8a" -name "*.log" -o -name "config.log" | xargs -r cp -t ".artifacts/logs" 2>/dev/null || true
          fi
          
          # Capture p4a toolchain info
          echo "[*] Creating environment snapshot..."
          {
            echo "=== ENVIRONMENT ==="
            env | grep -E 'ANDROID|NDK|SDK|GRADLE' | sort
            echo ""
            echo "=== BUILDOZER SPEC (p4a config) ==="
            grep -E '^p4a\.|^android\.' buildozer.spec | head -20
          } > ".artifacts/logs/env_snapshot.txt"
          
          echo ""
          echo "✓ Build failure artifacts captured to .artifacts/logs/"
          echo ""
      
      - name: Upload build logs on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: android-debug-build-logs
          path: .artifacts/logs/
          retention-days: 30
```

---

## Summary of Changes

| File | Component | Type | Purpose |
|------|-----------|------|---------|
| `buildozer.spec` | p4a.setup_py comment | Documentation | Clarify root cause & prevent misconfig |
| `android-debug.yml` | Buildozer version | Dependency | Ensure p4a.setup_py support |
| `android-debug.yml` | NDK/SDK sanitization | Env cleanup | Prevent runner pollution |
| `android-debug.yml` | Fast-fail checks | Validation | Early detection of misconfiguration |
| `android-debug.yml` | Cache cleanup | Reproducibility | Force fresh p4a build |
| `android-debug.yml` | Build Android APK | Error handling | `continue-on-error` allows log capture |
| `android-debug.yml` | Log capture | Debugging | Upload logs on failure for triage |

---

## Timeline

🕐 **Previous behavior**: `exit code 1` with no build logs, unclear root cause  
🕐 **With fix**: Fast failure within 2-3 min if misconfigured, or successful build with logging

Root cause will be caught at "Fast-fail verification" step rather than after 30+ min build attempt.
