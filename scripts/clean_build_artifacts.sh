#!/bin/bash

# Clean build artifacts safely for Kivy Android project
# Usage: ./scripts/clean_build_artifacts.sh

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SIZE_THRESHOLD_MB=100  # Ask for confirmation if deletion > this size
KEEP_LOG_DAYS=7       # Keep logs newer than this (optional)

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Create logs directory
LOGS_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOGS_DIR"
ERROR_LOG="$LOGS_DIR/cleanup_errors.log"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Build Artifacts Cleanup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Arrays to store paths to delete
declare -a PATHS_TO_DELETE=()
declare -a PATH_SIZES=()
TOTAL_SIZE_KB=0

# Function to add path for potential deletion
add_path_if_exists() {
    local path=$1
    local description=$2
    
    if [[ -e "$path" ]]; then
        local size_kb=$(du -sk "$path" | cut -f1)
        TOTAL_SIZE_KB=$((TOTAL_SIZE_KB + size_kb))
        PATHS_TO_DELETE+=("$path")
        PATH_SIZES+=("$description: $(du -sh "$path" | cut -f1)")
    fi
}

# Function to prompt user for confirmation
confirm() {
    local prompt="$1"
    local response
    
    while true; do
        read -p "$(echo -e ${YELLOW}${prompt}${NC}) (yes/no): " response
        case "$response" in
            [yY][eE][sS] | [yY])
                return 0
                ;;
            [nN][oO] | [nN])
                return 1
                ;;
            *)
                echo "Please answer yes or no."
                ;;
        esac
    done
}

# Analyze what needs to be deleted
echo -e "${YELLOW}[1/4]${NC} Scanning build artifacts..."
echo ""

# Check main directories
echo "  Checking directories:"

# bin/ directory
if [[ -d "$PROJECT_ROOT/bin" ]]; then
    add_path_if_exists "$PROJECT_ROOT/bin" "  • bin/ (APK outputs)"
    echo -e "${CYAN}    ✓ bin/${NC} found: $(du -sh "$PROJECT_ROOT/bin" | cut -f1)"
else
    echo -e "${CYAN}    - bin/${NC} not found"
fi

# build/ directory
if [[ -d "$PROJECT_ROOT/build" ]]; then
    add_path_if_exists "$PROJECT_ROOT/build" "  • build/ (Python build cache)"
    echo -e "${CYAN}    ✓ build/${NC} found: $(du -sh "$PROJECT_ROOT/build" | cut -f1)"
else
    echo -e "${CYAN}    - build/${NC} not found"
fi

# dist/ directory
if [[ -d "$PROJECT_ROOT/dist" ]]; then
    add_path_if_exists "$PROJECT_ROOT/dist" "  • dist/ (Distribution outputs)"
    echo -e "${CYAN}    ✓ dist/${NC} found: $(du -sh "$PROJECT_ROOT/dist" | cut -f1)"
else
    echo -e "${CYAN}    - dist/${NC} not found"
fi

# .buildozer/android/platform/build-* directories
BUILDOZER_BUILD_DIR="$PROJECT_ROOT/.buildozer/android/platform"
if [[ -d "$BUILDOZER_BUILD_DIR" ]]; then
    BUILD_DIRS=$(find "$BUILDOZER_BUILD_DIR" -maxdepth 1 -type d -name "build-*" 2>> "$ERROR_LOG" || true)
    if [[ -n "$BUILD_DIRS" ]]; then
        while IFS= read -r build_dir; do
            add_path_if_exists "$build_dir" "  • $(basename "$build_dir")"
            echo -e "${CYAN}    ✓ $(basename "$build_dir")${NC} found: $(du -sh "$build_dir" | cut -f1)"
        done <<< "$BUILD_DIRS"
    else
        echo -e "${CYAN}    - .buildozer/android/platform/build-*${NC} not found"
    fi
else
    echo -e "${CYAN}    - .buildozer/android/platform${NC} not found"
fi

echo ""
echo "  Checking logs (optional):"

# Check logs directory for old files (optional)
LOGS_DIR="$PROJECT_ROOT/logs"
if [[ -d "$LOGS_DIR" ]]; then
    OLD_LOGS=$(find "$LOGS_DIR" -type f -name "*.log" -mtime +$KEEP_LOG_DAYS 2>> "$ERROR_LOG" || true)
    if [[ -n "$OLD_LOGS" ]]; then
        LOG_SIZE_KB=$(echo "$OLD_LOGS" | xargs du -sk 2>> "$ERROR_LOG" | awk '{sum+=$1} END {print sum}')
        echo -e "${CYAN}    ✓ Old logs (>$KEEP_LOG_DAYS days)${NC} found: $(numfmt --to=iec-i --suffix=B $((LOG_SIZE_KB * 1024)) 2>> "$ERROR_LOG" || echo "${LOG_SIZE_KB} KB")"
        HAS_OLD_LOGS=1
    else
        echo -e "${CYAN}    - No old logs found${NC}"
        HAS_OLD_LOGS=0
    fi
else
    echo -e "${CYAN}    - logs/ not found${NC}"
    HAS_OLD_LOGS=0
fi

echo ""
echo -e "${YELLOW}[2/4]${NC} Summary of items to delete:"
echo ""

if [[ ${#PATHS_TO_DELETE[@]} -eq 0 ]] && [[ $HAS_OLD_LOGS -eq 0 ]]; then
    echo -e "${GREEN}✓ Nothing to clean!${NC}"
    echo ""
    exit 0
fi

# Display sizes
for size_info in "${PATH_SIZES[@]}"; do
    echo "  $size_info"
done

# Convert total size to MB
TOTAL_SIZE_MB=$((TOTAL_SIZE_KB / 1024))
if [[ $TOTAL_SIZE_MB -eq 0 ]] && [[ $TOTAL_SIZE_KB -gt 0 ]]; then
    TOTAL_SIZE_MB=1
fi

echo ""
echo -e "${YELLOW}Total build artifacts: ${CYAN}$(numfmt --to=iec-i --suffix=B $((TOTAL_SIZE_KB * 1024)) 2>> "$ERROR_LOG" || echo "${TOTAL_SIZE_MB} MB")${NC}"
echo ""

# Safety checks
echo -e "${YELLOW}[3/4]${NC} Safety verification:"
echo -e "  ${GREEN}✓${NC} buildozer.spec: PROTECTED"
echo -e "  ${GREEN}✓${NC} .venv/: PROTECTED"
echo -e "  ${GREEN}✓${NC} Source code: PROTECTED"
echo -e "  ${GREEN}✓${NC} Assets: PROTECTED"
echo ""

# Request confirmation
echo -e "${YELLOW}[4/4]${NC} Confirmation:"
echo ""

# Warn if exceeding threshold
if [[ $TOTAL_SIZE_MB -gt $SIZE_THRESHOLD_MB ]]; then
    echo -e "${RED}⚠ WARNING: Will delete $TOTAL_SIZE_MB MB (threshold: $SIZE_THRESHOLD_MB MB)${NC}"
    echo ""
fi

# Ask about logs
if [[ $HAS_OLD_LOGS -eq 1 ]]; then
    if confirm "Delete old logs (>$KEEP_LOG_DAYS days)?"; then
        DELETE_OLD_LOGS=1
    else
        DELETE_OLD_LOGS=0
    fi
else
    DELETE_OLD_LOGS=0
fi

echo ""

# Final confirmation
if ! confirm "Delete all selected build artifacts?"; then
    echo -e "${YELLOW}Aborted.${NC}"
    echo ""
    exit 0
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deleting...${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Delete paths
for path in "${PATHS_TO_DELETE[@]}"; do
    if [[ -e "$path" ]]; then
        echo -e "${YELLOW}Deleting:${NC} $(basename "$path")"
        rm -rf "$path"
    fi
done

# Delete old logs if confirmed
if [[ $DELETE_OLD_LOGS -eq 1 ]]; then
    echo -e "${YELLOW}Deleting:${NC} Old logs"
    find "$LOGS_DIR" -type f -name "*.log" -mtime +$KEEP_LOG_DAYS -delete 2>/dev/null || true
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Cleanup complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Show remaining disk usage
echo -e "${CYAN}Disk usage after cleanup:${NC}"
echo "  bin/: $(du -sh "$PROJECT_ROOT/bin" 2>/dev/null | cut -f1 || echo "removed")"
echo "  build/: $(du -sh "$PROJECT_ROOT/build" 2>/dev/null | cut -f1 || echo "removed")"
echo "  dist/: $(du -sh "$PROJECT_ROOT/dist" 2>/dev/null | cut -f1 || echo "removed")"
echo ""
