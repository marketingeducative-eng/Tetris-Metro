#!/bin/bash

# Android SDK Bootstrap for Buildozer/Kivy on WSL Ubuntu
# Usage: ./scripts/android_sdk_bootstrap.sh

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
LOG_FILE="$LOGS_DIR/android_sdk_bootstrap_${TIMESTAMP}.log"

# Function to log to both console and file
log() {
    echo -e "$@" | tee -a "$LOG_FILE"
}

# Redirect all output to tee
exec > >(tee -a "$LOG_FILE") 2>&1

log "${BLUE}========================================${NC}"
log "${BLUE}Android SDK Bootstrap${NC}"
log "${BLUE}========================================${NC}"
log ""

# 1. Detect sdkmanager
log "${YELLOW}[1/7]${NC} Checking for sdkmanager..."

SDKMANAGER_PATH=$(which sdkmanager 2>> "$LOGS_DIR/bootstrap_errors.log" || true)

if [[ -z "$SDKMANAGER_PATH" ]]; then
    log "${YELLOW}  sdkmanager not found in PATH${NC}"
    log "${YELLOW}  Attempting installation via apt...${NC}"
    
    # Try to install via apt
    sudo apt update >> "$LOGS_DIR/apt_update.log" 2>&1
    sudo apt install -y google-android-cmdline-tools-12.0-installer 2>&1 | tee -a "$LOGS_DIR/apt_install.log"
    
    # Re-check after installation
    SDKMANAGER_PATH=$(which sdkmanager 2>> "$LOGS_DIR/bootstrap_errors.log" || true)
    
    if [[ -z "$SDKMANAGER_PATH" ]]; then
        log "${RED}ERROR: Failed to install sdkmanager${NC}"
        log "    Check logs: $LOGS_DIR/apt_install.log"
        log ""
        log "  ${YELLOW}Alternative: Install Android SDK manually${NC}"
        log "    https://developer.android.com/studio#command-tools"
        exit 1
    else
        log "${GREEN}✓ sdkmanager installed: $SDKMANAGER_PATH${NC}"
    fi
else
    log "${GREEN}✓ sdkmanager found: $SDKMANAGER_PATH${NC}"
fi

log ""

# 2. Determine ANDROID_SDK_ROOT
log "${YELLOW}[2/7]${NC} Determining ANDROID_SDK_ROOT..."

# Check standard location
if [[ -d "/usr/lib/android-sdk" ]]; then
    ANDROID_SDK_ROOT="/usr/lib/android-sdk"
    log "${GREEN}✓ Using: $ANDROID_SDK_ROOT${NC}"
elif [[ -n "${ANDROID_SDK_ROOT:-}" ]]; then
    log "${GREEN}✓ Using existing: $ANDROID_SDK_ROOT${NC}"
else
    # Try to find candidate directories
    CANDIDATES=(
        "/usr/lib/android-sdk"
        "$HOME/Android/Sdk"
        "$HOME/.android/sdk"
        "/opt/android-sdk"
    )
    
    FOUND=""
    for candidate in "${CANDIDATES[@]}"; do
        if [[ -d "$candidate" ]]; then
            FOUND="$candidate"
            break
        fi
    done
    
    if [[ -n "$FOUND" ]]; then
        ANDROID_SDK_ROOT="$FOUND"
        log "${GREEN}✓ Found candidate: $ANDROID_SDK_ROOT${NC}"
    else
        log "${RED}ERROR: Could not find ANDROID_SDK_ROOT${NC}"
        log ""
        log "  ${YELLOW}Tried locations:${NC}"
        for candidate in "${CANDIDATES[@]}"; do
            log "    - $candidate"
        done
        log ""
        log "  ${YELLOW}Solution: Set ANDROID_SDK_ROOT manually${NC}"
        log "    export ANDROID_SDK_ROOT=/path/to/android-sdk"
        exit 1
    fi
fi

log ""

# 3. Export environment variables
log "${YELLOW}[3/7]${NC} Setting up environment..."

export ANDROID_SDK_ROOT
export PATH="$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$PATH"
export PATH="$ANDROID_SDK_ROOT/platform-tools:$PATH"

log "  ANDROID_SDK_ROOT: $ANDROID_SDK_ROOT"
log "  PATH additions:"
log "    - cmdline-tools/latest/bin"
log "    - platform-tools"
log "${GREEN}✓ Environment configured${NC}"
log ""

# 4. Accept SDK licenses
log "${YELLOW}[4/7]${NC} Accepting Android SDK licenses..."
log "  ${CYAN}This requires interactive input (yes to all)${NC}"
log ""

# Check if sdkmanager accepts --sdk_root flag
if sdkmanager --help 2>&1 | grep -q "sdk_root"; then
    echo "y" | sdkmanager --licenses --sdk_root="$ANDROID_SDK_ROOT" 2>&1 | tee -a "$LOGS_DIR/licenses.log"
else
    echo "y" | sdkmanager --licenses 2>&1 | tee -a "$LOGS_DIR/licenses.log"
fi

log "${GREEN}✓ Licenses accepted${NC}"
log ""

# 5. Install minimum required packages
log "${YELLOW}[5/7]${NC} Installing minimum SDK packages..."
log "  - platform-tools (adb, fastboot)"
log "  - platforms;android-34 (API 34)"
log "  - build-tools;34.0.0"
log ""

# Install packages
if sdkmanager --help 2>&1 | grep -q "sdk_root"; then
    sdkmanager --sdk_root="$ANDROID_SDK_ROOT" \
        "platform-tools" \
        "platforms;android-34" \
        "build-tools;34.0.0" 2>&1 | tee -a "$LOGS_DIR/sdk_install.log"
else
    sdkmanager \
        "platform-tools" \
        "platforms;android-34" \
        "build-tools;34.0.0" 2>&1 | tee -a "$LOGS_DIR/sdk_install.log"
fi

log "${GREEN}✓ SDK packages installed${NC}"
log ""

# 6. Verify installations
log "${YELLOW}[6/7]${NC} Verifying installations..."

# Check for adb
ADB_PATH=$(which adb 2>> "$LOGS_DIR/bootstrap_errors.log" || true)
if [[ -n "$ADB_PATH" ]]; then
    ADB_VERSION=$(adb version 2>&1 | head -n 1)
    log "${GREEN}✓ adb found: $ADB_PATH${NC}"
    log "    Version: $ADB_VERSION"
else
    log "${RED}✗ adb not found in PATH${NC}"
    log "    Expected: $ANDROID_SDK_ROOT/platform-tools/adb"
fi

# Verify sdkmanager works
log ""
log "  Testing sdkmanager..."
if sdkmanager --list 2>&1 | head -n 3 | grep -q "Installed packages"; then
    log "${GREEN}✓ sdkmanager functional${NC}"
else
    log "${YELLOW}⚠ sdkmanager may have issues${NC}"
fi

log ""

# 7. Final summary
log "${YELLOW}[7/7]${NC} Bootstrap Summary:"
log ""
log "  ${CYAN}SDK Location:${NC} $ANDROID_SDK_ROOT"
log "  ${CYAN}Log File:${NC} $LOG_FILE"
log ""

# List installed packages
log "  ${CYAN}Installed Packages:${NC}"
if sdkmanager --list 2>&1 | grep -A 20 "Installed packages" | head -n 15 > /tmp/sdk_packages.txt; then
    cat /tmp/sdk_packages.txt | tee -a "$LOG_FILE"
    rm /tmp/sdk_packages.txt
fi

log ""
log "${BLUE}========================================${NC}"
log "${GREEN}✓ Android SDK Bootstrap Complete${NC}"
log "${BLUE}========================================${NC}"
log ""

# Export commands for user
log "${CYAN}Add to your ~/.bashrc or session:${NC}"
log ""
log "  export ANDROID_SDK_ROOT=\"$ANDROID_SDK_ROOT\""
log "  export PATH=\"\$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:\$PATH\""
log "  export PATH=\"\$ANDROID_SDK_ROOT/platform-tools:\$PATH\""
log ""
log "${YELLOW}Then reload shell: source ~/.bashrc${NC}"
log ""
