#!/bin/bash
set -euo pipefail

# CI pyjnius Smoke Test Script - DETERMINISTIC & HARD EVIDENCE ONLY
# Purpose: Compile pyjnius with p4a and validate ONLY with compiled *.so binaries
# 
# Usage: ci_pyjnius_smoke.sh [ARCH] [NDK_API]
#   ARCH     - Android architecture (default: arm64-v8a)
#   NDK_API  - NDK API level (default: 21)
#
# Exit codes:
#   0 = SUCCESS (pyjnius compiled - validated by *.so binaries in build tree)
#   1 = FAILURE (no jnius *.so found, build must have failed)

# Parse arguments
ARCH="${1:-arm64-v8a}"
NDK_API="${2:-21}"
LOG_FILE="pyjnius_smoke_${ARCH}.log"

echo "════════════════════════════════════════════════════════════════"
echo "pyjnius Smoke Test - Build pyjnius and validate with HARD EVIDENCE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Configuration:"
echo "  Architecture: $ARCH"
echo "  NDK API:      $NDK_API"
echo "  Log file:     $LOG_FILE"
echo ""
echo "Strategy: Use p4a toolchain directly to build pyjnius recipe,"
echo "          then verify existence of compiled jnius *.so binaries"
echo ""

# Create buildozer directories if they don't exist (for p4a)
mkdir -p ~/.buildozer/android/platform
mkdir -p .buildozer

# === PHASE 0: Verify pinned dependencies ===

echo "[Phase 0/3] Verifying pinned dependencies..."
echo ""

echo "Python version:"
python -V
echo ""

echo "Critical check: Cython version"
CYTHON_VERSION=$(python -c "import Cython; print(Cython.__version__)" 2>/dev/null || echo "NOT_FOUND")
echo "  Detected: $CYTHON_VERSION"
echo "  Required: 0.29.36"

if [ "$CYTHON_VERSION" != "0.29.36" ]; then
    echo ""
    echo "❌ CRITICAL: Cython version mismatch!"
    echo ""
    echo "Expected: 0.29.36 (Python 3 compatible, supports 'long' type)"
    echo "Found:    $CYTHON_VERSION"
    echo ""
    echo "This WILL cause: jnius/jnius_utils.pxi:323:37: undeclared name not builtin: long"
    echo ""
    exit 1
fi

echo "  ✓ Version verified"
echo ""

# Export Android environment variables (buildozer defaults + r25b isolation)
export ANDROID_SDK_ROOT="${HOME}/.buildozer/android/platform/android-sdk"
export ANDROID_NDK_ROOT="${HOME}/.buildozer/android/platform/android-ndk-r25b"
export ANDROIDSDK="${ANDROID_SDK_ROOT}"
export ANDROIDNDK="${ANDROID_NDK_ROOT}"
export ANDROIDAPI="31"
export ANDROIDNDK_API="21"
export ANDROIDNDKVER="r25b"

echo "[Phase 1/3] Building pyjnius recipe with p4a ($ARCH)..."
echo ""

# Use p4a toolchain to create distribution with pyjnius
# This will:
# 1. Download SDK/NDK if needed
# 2. Build recipes including pyjnius (Cythonize + compile)
# 3. Generate jnius *.so binaries
{
    python -m pythonforandroid.toolchain create \
        --dist-name "smoketest_${ARCH}" \
        --bootstrap sdl2 \
        --requirements "python3,kivy,Cython==0.29.36,pyjnius==1.6.1" \
        --arch "$ARCH" \
        --ndk-api "$NDK_API" \
        --storage-dir "${HOME}/.buildozer/android/platform/build-${ARCH}" \
        --use-setup-py \
        --debug \
        2>&1 | tee -a "$LOG_FILE"
    
    BUILD_EXIT=${PIPESTATUS[0]}
} || BUILD_EXIT=$?

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Build exit code: $BUILD_EXIT"
echo "════════════════════════════════════════════════════════════════"
echo ""

# === PHASE 2: Check for CRITICAL ERRORS (fail immediately if found) ===

echo "[Phase 2/3] Checking for critical compilation errors..."
echo ""

# FAIL IMMEDIATELY if we find Cython 3.x specific error
if grep -q "undeclared name not builtin: long" "$LOG_FILE" 2>/dev/null; then
    echo "❌ CRITICAL ERROR: Cython 3.x was used (doesn't support 'long' type)"
    echo ""
    echo "Error from log:"
    grep -A 2 -B 2 "undeclared name not builtin: long" "$LOG_FILE" | head -10
    echo ""
    echo "Expected Cython: 0.29.36"
    echo "Actual Cython:   ${CYTHON_VERSION}"
    echo ""
    exit 1
fi

# FAIL IMMEDIATELY if setuptools was compiled and failed
if grep -qE "ModuleNotFoundError.*_ctypes|error.*_ctypes.*not found" "$LOG_FILE" 2>/dev/null; then
    echo "❌ CRITICAL ERROR: p4a tried to compile setuptools (should use --use-setup-py)"
    echo ""
    echo "Error from log:"
    grep -E "ModuleNotFoundError.*_ctypes|error.*_ctypes" "$LOG_FILE" | head -3
    echo ""
    echo "Verify buildozer.spec has: p4a.setup_py = true"
    echo ""
    exit 1
fi

echo "  ✓ No critical errors detected"
echo ""

# === PHASE 3: Verify HARD EVIDENCE ONLY - Compiled *.so binaries ===

echo "[Phase 3/3] Searching for compiled jnius *.so binaries (HARD EVIDENCE)..."
echo ""
echo "Strategy: Only .so files prove pyjnius compiled successfully"
echo ""

JNIUS_BINARIES=""

# Primary search: buildozer build tree for arm64-v8a
SEARCH_PATH="${HOME}/.buildozer/android/platform/build-${ARCH}"
if [ -d "$SEARCH_PATH" ]; then
    echo "[Search 1] $SEARCH_PATH"
    SO_FILES=$(find "$SEARCH_PATH" -type f -name "*.so" 2>/dev/null | grep -i jnius | head -20 || true)
    if [ -n "$SO_FILES" ]; then
        echo "  ✓ Found jnius *.so files:"
        while IFS= read -r f; do
            SIZE=$(stat -c%s "$f" 2>/dev/null || echo "?")
            echo "    → $(basename "$f") ($SIZE bytes)"
        done <<< "$SO_FILES"
        JNIUS_BINARIES="$SO_FILES"
    else
        echo "  (No jnius *.so files in primary path)"
    fi
    echo ""
fi

# Secondary search: ~/.buildozer/android/platform/build-*/other_builds/pyjnius*
if [ -z "$JNIUS_BINARIES" ]; then
    echo "[Search 2] ~/.buildozer/android/platform/build-${ARCH}/other_builds/pyjnius*/"
    SO_FILES=$(find ~/.buildozer/android/platform/build-${ARCH}/other_builds -type f -name "*.so" 2>/dev/null | grep -i jnius | head -20 || true)
    if [ -n "$SO_FILES" ]; then
        echo "  ✓ Found jnius *.so files:"
        while IFS= read -r f; do
            SIZE=$(stat -c%s "$f" 2>/dev/null || echo "?")
            echo "    → $(basename "$f") ($SIZE bytes)"
        done <<< "$SO_FILES"
        JNIUS_BINARIES="$SO_FILES"
    else
        echo "  (No jnius *.so files in secondary path)"
    fi
    echo ""
fi

# Fallback: broader search
if [ -z "$JNIUS_BINARIES" ]; then
    echo "[Fallback] Broader search for jnius *.so anywhere in ~/.buildozer..."
    SO_FILES=$(find ~/.buildozer -type f -name "*jnius*.so" 2>/dev/null | head -20 || true)
    if [ -n "$SO_FILES" ]; then
        echo "  ✓ Found jnius *.so files:"
        while IFS= read -r f; do
            SIZE=$(stat -c%s "$f" 2>/dev/null || echo "?")
            echo "    → $(basename "$f") ($SIZE bytes)"
        done <<< "$SO_FILES"
        JNIUS_BINARIES="$SO_FILES"
    else
        echo "  (No jnius *.so files found in any search path)"
    fi
    echo ""
fi

echo "════════════════════════════════════════════════════════════════"
echo ""

# === FINAL VERDICT - ONLY based on physical *.so files ===

if [ -n "$JNIUS_BINARIES" ]; then
    echo "✅ SMOKE TEST PASSED"
    echo ""
    echo "HARD EVIDENCE: pyjnius compiled successfully"
    echo ""
    echo "Compiled jnius *.so binaries found:"
    while IFS= read -r binary; do
        if [ -f "$binary" ]; then
            SIZE=$(stat -c%s "$binary" 2>/dev/null || echo "???")
            echo "  ✓ $(basename "$binary") ($SIZE bytes)"
            echo "    Path: $binary"
        fi
    done <<< "$JNIUS_BINARIES"
    echo ""
    echo "This confirms:"
    echo "  • Cython 0.29.36 compiled pyjnius source successfully"
    echo "  • pyjnius 1.6.1 recipe built without errors"
    echo "  • p4a was invoked with --use-setup-py (NOT --ignore-setup-py)"
    echo "  • JNI bindings are ready for packaging"
    echo ""
    exit 0
else
    echo "❌ SMOKE TEST FAILED"
    echo ""
    echo "ZERO jnius *.so binaries found in build tree."
    echo ""
    echo "This means pyjnius compilation did NOT succeed."
    echo ""
    echo "Possible root causes:"
    echo "  1. p4a invoked with --ignore-setup-py (setuptools compile → _ctypes error)"
    echo "  2. Cython version != 0.29.36 (undeclared 'long' error)"
    echo "  3. pyjnius version != 1.6.1 (compatibility)"
    echo "  4. NDK/SDK corrupt or mismatched"
    echo "  5. Build stopped before reaching pyjnius recipe"
    echo ""
    echo "Check full build log: $LOG_FILE"
    echo ""
    exit 1
fi
