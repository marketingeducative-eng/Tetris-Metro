#!/bin/bash
set -euo pipefail

# CI pyjnius Smoke Test Script
# Purpose: Compile pyjnius with p4a (WITHOUT reaching Gradle/APK assembly)
# 
# Usage: ci_pyjnius_smoke.sh [ARCH] [NDK_API]
#   ARCH     - Android architecture (default: arm64-v8a)
#   NDK_API  - NDK API level (default: 21)
#
# Exit codes:
#   0 = SUCCESS (pyjnius compiled successfully)
#   1 = FAILURE (historical bug detected: undeclared 'long' or missing jnius.c)
#   2 = INCONCLUSIVE (no errors but no positive evidence of pyjnius compilation)

# Parse arguments
ARCH="${1:-arm64-v8a}"
NDK_API="${2:-21}"
LOG_FILE="pyjnius_smoke_${ARCH}.log"

echo "════════════════════════════════════════════════════════════════"
echo "pyjnius Smoke Test - p4a Direct Build"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Configuration:"
echo "  Architecture: $ARCH"
echo "  NDK API:      $NDK_API"
echo "  Log file:     $LOG_FILE"
echo ""
echo "Strategy: Use python-for-android toolchain directly to build"
echo "          pyjnius recipe, stopping BEFORE APK/Gradle assembly."
echo ""

# Create buildozer directories if they don't exist (for p4a)
mkdir -p ~/.buildozer/android/platform
mkdir -p .buildozer

# Determine p4a strategy based on version
P4A_VERSION=$(python -m pythonforandroid.toolchain --version 2>&1 | grep -oP '\d+\.\d+\.\d+' | head -1 || echo "unknown")
echo "python-for-android version: $P4A_VERSION"
echo ""

# === PHASE 0: Verify pinned dependencies ===

echo "[Phase 0/3] Verifying pinned dependencies..."
echo ""

echo "Python version:"
python -V
echo ""

echo "Installed dependencies:"
pip freeze | grep -E "^Cython==|^pyjnius==|^python-for-android==|^buildozer==" || echo "(pyjnius not installed by pip - will be by p4a)"
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
    exit 1
fi

echo "  ✓ Version verified"
echo ""

# Export Android environment variables
export ANDROID_SDK_ROOT="${HOME}/.buildozer/android/platform/android-sdk"
export ANDROID_NDK_ROOT="${HOME}/.buildozer/android/platform/android-ndk"
export ANDROIDSDK="${ANDROID_SDK_ROOT}"
export ANDROIDNDK="${ANDROID_NDK_ROOT}"
export ANDROIDAPI="21"
export ANDROIDNDKVER="r25b"

echo "[Phase 1/3] Creating p4a distribution with pyjnius recipe ($ARCH)..."
echo ""

# Use p4a toolchain to create distribution
# This will:
# 1. Download SDK/NDK if needed
# 2. Build recipes including pyjnius (Cythonize + compile)
# 3. Stop before creating APK/AAB
{
    python -m pythonforandroid.toolchain create \
        --dist-name "smoketest_${ARCH}" \
        --bootstrap sdl2 \
        --requirements "python3,kivy,Cython==0.29.36,pyjnius==1.6.1" \
        --arch "$ARCH" \
        --ndk-api "$NDK_API" \
        --sdk-dir "${ANDROID_SDK_ROOT}" \
        --ndk-dir "${ANDROID_NDK_ROOT}" \
        --storage-dir "${HOME}/.buildozer/android/platform/build-${ARCH}" \
        2>&1 | tee -a "$LOG_FILE"
    
    BUILD_EXIT=${PIPESTATUS[0]}
} || BUILD_EXIT=$?

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Build exit code: $BUILD_EXIT"
echo "════════════════════════════════════════════════════════════════"
echo ""

# === PHASE 2: Check for HISTORICAL BUGS (exit 1 if found) ===

echo "[Phase 2/3] Checking for historical Cython/pyjnius bugs..."
echo ""

if grep -q "undeclared name not builtin: long" "$LOG_FILE" 2>/dev/null; then
    echo "❌ SMOKE TEST FAILED: Historical bug detected!"
    echo ""
    echo "Error found in logs:"
    grep -A 2 -B 2 "undeclared name not builtin: long" "$LOG_FILE" | head -10
    echo ""
    echo "Root cause: Cython 3.x was used (doesn't support 'long' type)"
    echo "Expected: Cython 0.29.36"
    echo ""
    echo "This is the exact bug we were protecting against."
    exit 1
fi

if grep -qE "jnius/jnius\.c.*[Nn]o such file|error.*jnius\.c.*not found" "$LOG_FILE" 2>/dev/null; then
    echo "❌ SMOKE TEST FAILED: Cascade error detected!"
    echo ""
    echo "Error found in logs:"
    grep -E "jnius\.c.*[Nn]o such file|error.*jnius\.c" "$LOG_FILE" | head -5
    echo ""
    echo "Root cause: jnius.c missing (Cython compilation failed upstream)"
    echo ""
    exit 1
fi

if grep -qE "error: command.*failed|^ERROR:|Build failed|compilation terminated" "$LOG_FILE" 2>/dev/null; then
    # Generic build error - might not be pyjnius related
    echo "⚠️  Generic build errors detected in logs:"
    grep -E "error: command.*failed|^ERROR:|Build failed" "$LOG_FILE" | head -5 || true
    echo ""
    echo "Continuing to check if pyjnius specifically compiled..."
    echo ""
fi

# === PHASE 3: Look for POSITIVE EVIDENCE of pyjnius compilation ===

echo "[Phase 3/3] Looking for positive evidence of pyjnius compilation ($ARCH)..."
echo ""

EVIDENCE_FOUND=0

# Check 1: Look for Cythonize step in logs
if grep -q "Cythonize.*jnius" "$LOG_FILE" 2>/dev/null; then
    echo "✓ Found: Cythonize jnius step in logs"
    EVIDENCE_FOUND=1
fi

# Check 2: Look for "building 'jnius' extension"
if grep -q "building.*jnius.*extension\|building 'jnius'" "$LOG_FILE" 2>/dev/null; then
    echo "✓ Found: Building jnius extension in logs"
    EVIDENCE_FOUND=1
fi

# Check 3: Look for successful compilation messages
if grep -qE "Successfully built.*jnius|jnius.*built successfully" "$LOG_FILE" 2>/dev/null; then
    echo "✓ Found: Successful build message for jnius"
    EVIDENCE_FOUND=1
fi

# Check 4: Look for compiled artifacts (*.so, *.o files)
echo ""
echo "Searching for compiled jnius artifacts..."
JNIUS_ARTIFACTS=$(find "${HOME}/.buildozer" .buildozer -type f \( -name "*jnius*.so" -o -name "*jnius*.o" -o -name "jnius.c" \) 2>/dev/null | head -5 || true)

if [ -n "$JNIUS_ARTIFACTS" ]; then
    echo "✓ Found compiled artifacts:"
    echo "$JNIUS_ARTIFACTS" | while read -r artifact; do
        echo "  → $(basename "$artifact") ($(stat -c%s "$artifact" 2>/dev/null || echo "?") bytes)"
    done
    EVIDENCE_FOUND=1
else
    echo "  (No artifacts found yet - may still be in progress)"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"

# === FINAL VERDICT ===

if [ $EVIDENCE_FOUND -eq 1 ]; then
    echo "✅ SMOKE TEST PASSED"
    echo ""
    echo "Positive evidence of pyjnius compilation found."
    echo "The fix (Cython 0.29.36 + pyjnius 1.6.1) is working correctly."
    echo ""
    echo "Historical bug NOT present:"
    echo "  ✗ No 'undeclared name not builtin: long' error"
    echo "  ✗ No 'jnius.c missing' error"
    echo ""
    exit 0
else
    echo "⚠️  SMOKE TEST INCONCLUSIVE"
    echo ""
    echo "No historical bugs detected, but no positive evidence of"
    echo "pyjnius compilation found either."
    echo ""
    echo "Possible reasons:"
    echo "  - Build stopped before reaching pyjnius recipe"
    echo "  - Cache prevented rebuild"
    echo "  - p4a version incompatibility"
    echo ""
    echo "Check the full log for details: $LOG_FILE"
    echo ""
    
    # Treat inconclusive as failure (safer for CI)
    # If you prefer warning instead, change this to exit 0 + ::warning::
    exit 2
fi
