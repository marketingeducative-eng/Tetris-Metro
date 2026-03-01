#!/bin/bash

# Memory diagnostics for Kivy Android WSL environment
# Usage: ./tools/diag_memory.sh

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

# Create diag directory if it doesn't exist
DIAG_DIR="$SCRIPT_DIR/diag"
mkdir -p "$DIAG_DIR"

# Create logs directory for error tracking
LOGS_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOGS_DIR"
ERROR_LOG="$LOGS_DIR/diagnostics_errors.log"

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M")
REPORT_FILE="$DIAG_DIR/memory_${TIMESTAMP}.txt"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Memory Diagnostics Report${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${CYAN}Report: $REPORT_FILE${NC}"
echo ""

# Create report file and write to both file and stdout
{
    echo "=================================================="
    echo "Memory Diagnostics Report"
    echo "Generated: $(date)"
    echo "System: $(uname -a)"
    echo "=================================================="
    echo ""
    
    # 1. Memory overview
    echo "=== MEMORY OVERVIEW ==="
    echo ""
    free -h
    echo ""
    
    # 2. Swap status
    echo "=== SWAP STATUS ==="
    echo ""
    if command -v swapon &>> "$ERROR_LOG"; then
        swapon --show 2>> "$ERROR_LOG" || echo "No swap configured"
    else
        echo "swapon command not found"
    fi
    echo ""
    
    # 3. Resource limits
    echo "=== RESOURCE LIMITS (ulimit -a) ==="
    echo ""
    ulimit -a
    echo ""
    
    # 4. Top 15 processes by RSS
    echo "=== TOP 15 PROCESSES BY RSS ==="
    echo ""
    ps aux --sort=-rss | head -n 16
    echo ""
    
    # 5. Search for specific processes
    echo "=== BUILD-RELATED PROCESSES ==="
    echo ""
    
    # Check for Java
    if pgrep -f java >> "$ERROR_LOG" 2>&1; then
        echo "*** JAVA PROCESSES ***"
        ps aux --sort=-rss | grep -i java | grep -v grep 2>> "$ERROR_LOG" || echo "No matching processes"
        echo ""
    fi
    
    # Check for Gradle
    if pgrep -f gradle >> "$ERROR_LOG" 2>&1; then
        echo "*** GRADLE PROCESSES ***"
        ps aux --sort=-rss | grep -i gradle | grep -v grep 2>> "$ERROR_LOG" || echo "No matching processes"
        echo ""
    fi
    
    # Check for Python
    if pgrep -f python >> "$ERROR_LOG" 2>&1; then
        echo "*** PYTHON PROCESSES ***"
        ps aux --sort=-rss | grep -i python | grep -v grep 2>> "$ERROR_LOG" || echo "No matching processes"
        echo ""
    fi
    
    # Check for Buildozer
    if pgrep -f buildozer >> "$ERROR_LOG" 2>&1; then
        echo "*** BUILDOZER PROCESSES ***"
        ps aux --sort=-rss | grep -i buildozer | grep -v grep 2>> "$ERROR_LOG" || echo "No matching processes"
        echo ""
    fi
    
    # Check if no build processes found
    if ! pgrep -f "java|gradle|python|buildozer" >> "$ERROR_LOG" 2>&1; then
        echo "No build-related processes currently running"
        echo ""
    fi
    
    # 6. Memory metrics
    echo "=== MEMORY METRICS ==="
    echo ""
    
    # Total memory usage
    TOTAL_MEM=$(free -b | awk '/^Mem:/ {print $2}')
    USED_MEM=$(free -b | awk '/^Mem:/ {print $3}')
    PERCENT=$((USED_MEM * 100 / TOTAL_MEM))
    echo "Memory Usage: $PERCENT%"
    echo ""
    
    # 7. System load
    echo "=== SYSTEM LOAD ==="
    echo ""
    uptime
    echo ""
    
    # 8. Virtual memory statistics
    echo "=== VIRTUAL MEMORY STATS ==="
    echo ""
    if command -v vmstat &>> "$ERROR_LOG"; then
        vmstat 1 2 2>> "$ERROR_LOG" | tail -n 1
    else
        echo "vmstat command not found"
    fi
    echo ""
    
    echo "=================================================="
    echo "End of Report"
    echo "=================================================="
    
} | tee "$REPORT_FILE"

echo ""
echo -e "${GREEN}✓ Report saved: $REPORT_FILE${NC}"
echo ""

# Print summary to console only
echo -e "${YELLOW}Summary:${NC}"
TOTAL_MEM=$(free -h | awk '/^Mem:/ {print $2}')
USED_MEM=$(free -h | awk '/^Mem:/ {print $3}')
AVAILABLE_MEM=$(free -h | awk '/^Mem:/ {print $7}')
echo "  Total Memory: $TOTAL_MEM"
echo "  Used Memory: $USED_MEM"
echo "  Available Memory: $AVAILABLE_MEM"

# Check if memory usage is concerning
PERCENT=$(free | awk '/^Mem:/ {print int($3/$2*100)}')
if [[ $PERCENT -gt 80 ]]; then
    echo ""
    echo -e "${RED}⚠ WARNING: Memory usage is high ($PERCENT%)${NC}"
elif [[ $PERCENT -gt 60 ]]; then
    echo ""
    echo -e "${YELLOW}⚠ NOTE: Memory usage is moderate ($PERCENT%)${NC}"
fi

echo ""
