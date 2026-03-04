#!/bin/bash

# ============================================================================
# BUILD ENVIRONMENT SETUP SCRIPT
# ============================================================================
# This script sets up all required environment variables and validates
# configuration for building Tetris-Metro APK with buildozer.
# 
# Usage: source scripts/setup_build_env.sh
# ============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "================================"
echo "🔧 CONFIGURING BUILD ENVIRONMENT"
echo "================================"

# ============================================================================
# 1. SET NDK PATHS
# ============================================================================
export ANDROID_NDK_HOME="$HOME/.buildozer/android/platform/android-ndk-r25b"
export ANDROID_NDK="$HOME/.buildozer/android/platform/android-ndk-r25b"
export ANDROID_NDK_LATEST_HOME="$HOME/.buildozer/android/platform/android-ndk-r25b"

echo -e "\n✅ NDK Environment Variables:"
echo "   ANDROID_NDK_HOME=$ANDROID_NDK_HOME"
echo "   ANDROID_NDK=$ANDROID_NDK"
echo "   ANDROID_NDK_LATEST_HOME=$ANDROID_NDK_LATEST_HOME"

# ============================================================================
# 2. SET SDK PATHS
# ============================================================================
export ANDROID_SDK_ROOT="$HOME/.buildozer/android/platform/android-sdk"
export ANDROID_HOME="$HOME/.buildozer/android/platform/android-sdk"

echo -e "\n✅ SDK Environment Variables:"
echo "   ANDROID_SDK_ROOT=$ANDROID_SDK_ROOT"
echo "   ANDROID_HOME=$ANDROID_HOME"

# ============================================================================
# 3. VALIDATE NDK STRUCTURE
# ============================================================================
echo -e "\n🔍 VALIDATING NDK STRUCTURE..."

NDK_DIR="$ANDROID_NDK_HOME"

# Check platforms/android-21 symlink
if [ -L "$NDK_DIR/platforms/android-21" ]; then
  echo "   ✅ platforms/android-21 symlink is correct"
else
  echo "   ⚠️  Creating platforms/android-21 symlink..."
  mkdir -p "$NDK_DIR/platforms"
  ln -sf "$NDK_DIR/toolchains/llvm/prebuilt/linux-x86_64/sysroot" "$NDK_DIR/platforms/android-21"
  echo "   ✅ Symlink created"
fi

# Check clang
if [ -x "$NDK_DIR/toolchains/llvm/prebuilt/linux-x86_64/bin/clang" ] || \
   [ -L "$NDK_DIR/toolchains/llvm/prebuilt/linux-x86_64/bin/clang" ]; then
  echo "   ✅ clang compiler is present"
else
  echo "   ❌ ERROR: clang compiler not found!"
  exit 1
fi

# ============================================================================
# 4. VALIDATE BUILDOZER CONFIGURATION
# ============================================================================
echo -e "\n🔍 VALIDATING BUILDOZER.SPEC..."

# Check p4a.setup_py
if grep -q "^p4a.setup_py = true" buildozer.spec; then
  echo "   ✅ p4a.setup_py = true"
else
  echo "   ❌ ERROR: p4a.setup_py not set to true in buildozer.spec"
  exit 1
fi

# Check android.archs
if grep -q "^android.archs = arm64-v8a$" buildozer.spec; then
  echo "   ✅ android.archs = arm64-v8a (single architecture)"
else
  echo "   ❌ ERROR: android.archs not set correctly"
  exit 1
fi

# Check requirements pinning
if grep -q "Cython==0.29.36" buildozer.spec && grep -q "pyjnius==1.6.1" buildozer.spec; then
  echo "   ✅ Requirements include Cython==0.29.36 and pyjnius==1.6.1"
else
  echo "   ❌ ERROR: Requirements missing pinned versions"
  exit 1
fi

# ============================================================================
# 5. VALIDATE BUILDOZER VERSION
# ============================================================================
echo -e "\n🔍 CHECKING BUILDOZER VERSION..."

BUILDOZER_VERSION=$(python3 -m pip show buildozer 2>/dev/null | grep Version | awk '{print $2}' || echo "0.0.0")

if [[ "$BUILDOZER_VERSION" > "1.4.0" ]] || [[ "$BUILDOZER_VERSION" == "1.4.0" ]] || [[ "$BUILDOZER_VERSION" > "1.5.0" ]]; then
  echo "   ✅ Buildozer version: $BUILDOZER_VERSION (>= 1.4.0)"
else
  echo "   ❌ ERROR: Buildozer version $BUILDOZER_VERSION is less than 1.4.0"
  exit 1
fi

# ============================================================================
# 6. CLEAN OLD ARTIFACTS (OPTIONAL)
# ============================================================================
if [ "$1" = "--clean" ]; then
  echo -e "\n🧹 CLEANING OLD BUILD ARTIFACTS..."
  rm -rf .buildozer/android/platform/build-arm64-v8a/dists/metrotetris
  rm -rf bin/
  rm -rf .buildozer/android/platform/build-arm64-v8a/*.log
  echo "   ✅ Cleaned"
fi

# ============================================================================
# 7. SUMMARY
# ============================================================================
echo -e "\n================================"
echo "✅ BUILD ENVIRONMENT READY!"
echo "================================"
echo ""
echo "To build the APK, run:"
echo "  buildozer -v android debug"
echo ""
echo "Environment is exported in this shell session."
echo "To use this environment in a new shell:"
echo "  source scripts/setup_build_env.sh"
echo ""
