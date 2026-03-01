#!/bin/bash

# Build script for Kivy Android Debug APK
# Usage: ./scripts/build_android_debug.sh

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Tetris Metro - Android Debug Build${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. Verify buildozer.spec exists
echo -e "${YELLOW}[1/5]${NC} Checking buildozer.spec..."
if [[ ! -f "$PROJECT_ROOT/buildozer.spec" ]]; then
    echo -e "${RED}ERROR: buildozer.spec not found in $PROJECT_ROOT${NC}"
    echo "Create buildozer.spec first with: buildozer init"
    exit 1
fi
echo -e "${GREEN}✓ buildozer.spec found${NC}"
echo ""

# 2. Create logs directory
echo -e "${YELLOW}[2/5]${NC} Setting up logs directory..."
LOGS_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOGS_DIR"
ERROR_LOG="$LOGS_DIR/errors.log"
echo -e "${GREEN}✓ Logs directory ready: $LOGS_DIR${NC}"
echo ""

# 3. Verify and activate virtual environment
echo -e "${YELLOW}[3/5]${NC} Checking virtual environment..."
VENV_PATH="$PROJECT_ROOT/.venv"
if [[ ! -d "$VENV_PATH" ]]; then
    echo -e "${RED}ERROR: Virtual environment not found at $VENV_PATH${NC}"
    echo "Create it with: python -m venv .venv"
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# 4. Print Python info
echo -e "${YELLOW}[4/5]${NC} Python environment:"
echo "  Python version: $(python --version)"
echo "  Python path:    $(which python)"
echo ""

# 5. Run buildozer with logging
echo -e "${YELLOW}[5/5]${NC} Building Android Debug APK..."
echo "  Command: buildozer -v android debug"
echo ""

# Generate log filename with timestamp (YYYYMMDD_HHMM)
TIMESTAMP=$(date +"%Y%m%d_%H%M")
LOG_FILE="$LOGS_DIR/buildozer_debug_${TIMESTAMP}.log"

# Run buildozer and capture output
# We use tee to both display and save output while preserving exit code
buildozer -v android debug 2>&1 | tee "$LOG_FILE"
BUILD_EXIT_CODE=$?

echo ""
echo -e "${BLUE}========================================${NC}"

if [[ $BUILD_EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}✓ Build completed successfully${NC}"
    
    # Find the most recent APK in bin/
    echo ""
    echo -e "${YELLOW}Locating APK:${NC}"
    
    BIN_DIR="$PROJECT_ROOT/bin"
    if [[ -d "$BIN_DIR" ]]; then
        # Find the most recent .apk file
        LATEST_APK=$(find "$BIN_DIR" -name "*.apk" -type f -printf '%T@ %p\n' 2>> "$ERROR_LOG" | sort -rn | head -1 | cut -d' ' -f2-)
        
        if [[ -n "$LATEST_APK" && -f "$LATEST_APK" ]]; then
            APK_SIZE=$(du -h "$LATEST_APK" | cut -f1)
            APK_SIZE_BYTES=$(stat -f%z "$LATEST_APK" 2>> "$ERROR_LOG" || stat -c%s "$LATEST_APK" 2>> "$ERROR_LOG")
            
            echo -e "${GREEN}  APK:  $LATEST_APK${NC}"
            echo "  Size: $APK_SIZE ($APK_SIZE_BYTES bytes)"
        else
            echo -e "${YELLOW}  Warning: No APK found in $BIN_DIR${NC}"
        fi
    else
        echo -e "${YELLOW}  Warning: bin/ directory not found${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}Build log: $LOG_FILE${NC}"
else
    echo -e "${RED}✗ Build failed with exit code $BUILD_EXIT_CODE${NC}"
    echo -e "${YELLOW}Check build log: $LOG_FILE${NC}"
fi

echo -e "${BLUE}========================================${NC}"
echo ""

exit $BUILD_EXIT_CODE
