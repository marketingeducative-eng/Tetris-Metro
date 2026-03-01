#!/bin/bash
set -e

echo "=== Metro Tetris ARM64-ONLY BUILD ==="
echo "Starting at $(date)"
cd /mnt/c/Users/Usuario/Desktop/Tetris-Metro

# Activate venv
source .venv/bin/activate

# Set explicit buildozer spec
export BUILDOZER_SPEC="buildozer.spec"

# Log file
LOGFILE="logs/build_arm64_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs

echo "Build log: $LOGFILE"
echo "[$(date)] Starting ARM64-ONLY build" > "$LOGFILE"

# Run buildozer (arm64-v8a is defined in buildozer.spec)
buildozer android debug 2>&1 | tee -a "$LOGFILE" &
BUILD_PID=$!

# Wait for build to complete
wait $BUILD_PID
BUILD_EXIT=$?

echo "[$(date)] Build completed with exit code: $BUILD_EXIT"

if [ $BUILD_EXIT -eq 0 ]; then
    echo "✓ BUILD SUCCESSFUL"
    # Check for APK
    if ls bin/*.apk 1>/dev/null 2>&1; then
        echo "✓ APK found:"
        ls -lh bin/*.apk
    else
        echo "✕ No APK found in bin/ directory"
        echo "Build artifacts:"
        find . -name "*.apk" -type f 2>/dev/null | head -5
    fi
else
    echo "✕ BUILD FAILED with exit code $BUILD_EXIT"
    echo ""
    echo "=== Last 50 lines of log ==="
    tail -50 "$LOGFILE" | grep -E "ERROR|ERROR|error|failed|Failed|FAILED" || echo "(no error lines found)"
    echo ""
    echo "=== Full last 100 lines ==="
    tail -100 "$LOGFILE"
fi

exit $BUILD_EXIT
