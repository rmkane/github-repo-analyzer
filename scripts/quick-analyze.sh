#!/bin/bash

# Quick GitHub Repository Analysis Script
# Simple wrapper for common use cases

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Usage
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 USERNAME [LIMIT]"
    echo ""
    echo "Examples:"
    echo "  $0 rmkane"
    echo "  $0 rmkane 10"
    echo "  $0 microsoft 50"
    echo ""
    echo "Requires GITHUB_TOKEN environment variable"
    exit 1
fi

USERNAME="$1"
LIMIT="${2:-}"

# Check for token
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    echo "Error: GITHUB_TOKEN environment variable is required"
    exit 1
fi

# Change to project directory
cd "$PROJECT_ROOT"

# Activate virtual environment
if [[ -d "venv" ]]; then
    log_info "Activating virtual environment..."
    source venv/bin/activate
else
    log_info "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -e ".[dev]"
fi

# Create output directory
mkdir -p output

# Build command
CMD_ARGS=("analyze" "$USERNAME" "--output" "json")
if [[ -n "$LIMIT" ]]; then
    CMD_ARGS+=("--limit" "$LIMIT")
fi

# Run analysis
OUTPUT_FILE="output/${USERNAME}_repositories.json"
log_info "Analyzing repositories for: $USERNAME"

if github-repo-analyzer "${CMD_ARGS[@]}" > "$OUTPUT_FILE" 2>/dev/null; then
    log_success "Analysis complete!"
    log_success "Output: $OUTPUT_FILE"
    
    # Show basic stats
    if command -v jq &> /dev/null; then
        REPO_COUNT=$(jq length "$OUTPUT_FILE" 2>/dev/null || echo "unknown")
        echo "Repository count: $REPO_COUNT"
    fi
else
    echo "Analysis failed. Check $OUTPUT_FILE for details."
    exit 1
fi
