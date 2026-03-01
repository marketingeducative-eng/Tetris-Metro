#!/bin/bash

# Android SDK Doctor - Diagnostic tool for Android development environment
# Usage: ./tools/android_sdk_doctor.sh

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Create logs directory
LOGS_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOGS_DIR"

# Generate timestamp and log file
TIMESTAMP=$(date +"%Y%m%d_%H%M")
LOG_FILE="$LOGS_DIR/android_sdk_doctor_${TIMESTAMP}.log"

echo -e "${BLUE}========================================${NC}" | tee "$LOG_FILE"
echo -e "${BLUE}Android SDK Doctor${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}========================================${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 1. Environment Variables
echo -e "${YELLOW}[1/6] Environment Variables${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

if [[ -n "${ANDROID_SDK_ROOT:-}" ]]; then
    echo -e "  ${GREEN}✓ ANDROID_SDK_ROOT:${NC} $ANDROID_SDK_ROOT" | tee -a "$LOG_FILE"
else
    echo -e "  ${RED}✗ ANDROID_SDK_ROOT: not set${NC}" | tee -a "$LOG_FILE"
fi

if [[ -n "${ANDROID_HOME:-}" ]]; then
    echo -e "  ${GREEN}✓ ANDROID_HOME:${NC} $ANDROID_HOME" | tee -a "$LOG_FILE"
else
    echo -e "  ${YELLOW}⚠ ANDROID_HOME: not set${NC}" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"

# 2. sdkmanager
echo -e "${YELLOW}[2/6] sdkmanager${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

SDKMANAGER_PATH=$(which sdkmanager 2>> "$LOGS_DIR/doctor_errors.log" || echo "")
if [[ -n "$SDKMANAGER_PATH" ]]; then
    echo -e "  ${GREEN}✓ Location:${NC} $SDKMANAGER_PATH" | tee -a "$LOG_FILE"
    
    # Get version
    SDKMANAGER_VERSION=$(sdkmanager --version 2>&1 | head -n 1 || echo "unknown")
    echo -e "  ${GREEN}✓ Version:${NC} $SDKMANAGER_VERSION" | tee -a "$LOG_FILE"
else
    echo -e "  ${RED}✗ sdkmanager not found in PATH${NC}" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"

# 3. adb (Android Debug Bridge)
echo -e "${YELLOW}[3/6] adb (Android Debug Bridge)${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

ADB_PATH=$(which adb 2>> "$LOGS_DIR/doctor_errors.log" || echo "")
if [[ -n "$ADB_PATH" ]]; then
    echo -e "  ${GREEN}✓ Location:${NC} $ADB_PATH" | tee -a "$LOG_FILE"
    
    # Get version
    ADB_VERSION=$(adb version 2>&1 | head -n 1 || echo "unknown")
    echo -e "  ${GREEN}✓ Version:${NC} $ADB_VERSION" | tee -a "$LOG_FILE"
else
    echo -e "  ${RED}✗ adb not found in PATH${NC}" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"

# 4. Installed SDK Packages
echo -e "${YELLOW}[4/6] Installed SDK Packages${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

if [[ -n "$SDKMANAGER_PATH" ]]; then
    echo -e "  ${CYAN}Platforms (android-*):${NC}" | tee -a "$LOG_FILE"
    sdkmanager --list 2>&1 | grep "platforms;android-" | head -n 20 | tee -a "$LOG_FILE" || echo "    No platforms found" | tee -a "$LOG_FILE"
    
    echo "" | tee -a "$LOG_FILE"
    echo -e "  ${CYAN}Build Tools:${NC}" | tee -a "$LOG_FILE"
    sdkmanager --list 2>&1 | grep "build-tools;" | head -n 20 | tee -a "$LOG_FILE" || echo "    No build-tools found" | tee -a "$LOG_FILE"
else
    echo -e "  ${YELLOW}⚠ Skipped (sdkmanager not available)${NC}" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"

# 5. Disk Space
echo -e "${YELLOW}[5/6] Disk Space${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

df -h | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"

# 6. Java
echo -e "${YELLOW}[6/6] Java${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

JAVA_PATH=$(which java 2>> "$LOGS_DIR/doctor_errors.log" || echo "")
if [[ -n "$JAVA_PATH" ]]; then
    echo -e "  ${GREEN}✓ Location:${NC} $JAVA_PATH" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    java -version 2>&1 | tee -a "$LOG_FILE"
else
    echo -e "  ${RED}✗ java not found in PATH${NC}" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"

# Summary
echo -e "${BLUE}========================================${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}Summary${NC}" | tee -a "$LOG_FILE"
echo -e "${BLUE}========================================${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Count issues
ISSUES=0
[[ -z "${ANDROID_SDK_ROOT:-}" ]] && ((ISSUES++)) || true
[[ -z "$SDKMANAGER_PATH" ]] && ((ISSUES++)) || true
[[ -z "$ADB_PATH" ]] && ((ISSUES++)) || true
[[ -z "$JAVA_PATH" ]] && ((ISSUES++)) || true

if [[ $ISSUES -eq 0 ]]; then
    echo -e "${GREEN}✓ All checks passed${NC}" | tee -a "$LOG_FILE"
else
    echo -e "${YELLOW}⚠ $ISSUES issue(s) detected${NC}" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo -e "${CYAN}Report saved: $LOG_FILE${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
