#!/bin/bash

# Cache Demonstration Script
# Shows the difference between cached and non-cached requests

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
# shellcheck disable=SC2034
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Usage
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 USERNAME [LIMIT]"
    echo ""
    echo "This script demonstrates caching by running the same analysis twice:"
    echo "1. First run: Makes API calls and caches results"
    echo "2. Second run: Uses cached data (much faster)"
    echo ""
    echo "Examples:"
    echo "  $0 rmkane"
    echo "  $0 rmkane 5"
    echo ""
    echo "Requires GITHUB_TOKEN environment variable"
    exit 1
fi

USERNAME="$1"
LIMIT="${2:-5}"

# Check for token
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    echo "Error: GITHUB_TOKEN environment variable is required"
    exit 1
fi

# Change to project directory
cd "$PROJECT_ROOT"

# Activate virtual environment
if [[ -d "venv" ]]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found. Run 'make install-dev' first."
    exit 1
fi

# Create output directory
mkdir -p output

# Function to run analysis and measure time
run_analysis() {
    local cache_option="$1"
    local run_label="$2"
    
    log_info "$run_label"
    
    local start_time
    start_time=$(date +%s.%N)
    
    local cmd_args=("analyze" "$USERNAME" "--limit" "$LIMIT" "--output" "json")
    if [[ "$cache_option" == "no-cache" ]]; then
        cmd_args+=("--no-cache")
    fi
    
    if github-repo-analyzer "${cmd_args[@]}" > /dev/null 2>&1; then
        local end_time
        end_time=$(date +%s.%N)
        local duration
        duration=$(echo "$end_time - $start_time" | bc -l)
        
        log_success "Completed in ${duration}s"
        return 0
    else
        log_warning "Analysis failed"
        return 1
    fi
}

# Run the demonstration
echo "=========================================="
echo "GitHub Repository Analyzer - Cache Demo"
echo "=========================================="
echo ""

log_info "Analyzing $USERNAME (limit: $LIMIT repositories)"
echo ""

# First run - with caching
log_info "Run 1: Making API calls and caching results..."
run_analysis "cache" "First run (with caching)"

echo ""

# Second run - using cache
log_info "Run 2: Using cached data..."
run_analysis "cache" "Second run (using cache)"

echo ""

# Third run - without caching (for comparison)
log_info "Run 3: Disabling cache (for comparison)..."
run_analysis "no-cache" "Third run (no cache)"

echo ""
log_success "Cache demonstration complete!"
echo ""
log_info "Notice how the second run was much faster than the first and third runs."
log_info "This is because it used cached data instead of making API calls."
