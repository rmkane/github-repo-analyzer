#!/bin/bash

# GitHub Repository Analyzer - User Analysis Script
# This script installs, activates, and runs the CLI tool for a specific user
# Outputs JSON to the output/ directory

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$PROJECT_ROOT/output"
VENV_DIR="$PROJECT_ROOT/venv"
CLI_NAME="github-repo-analyzer"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
GitHub Repository Analyzer - User Analysis Script

Usage: $0 [OPTIONS] USERNAME

ARGUMENTS:
    USERNAME        GitHub username to analyze

OPTIONS:
    -h, --help      Show this help message
    -o, --org       Treat USERNAME as an organization name
    -l, --limit N   Limit number of repositories (default: no limit)
    -t, --token     GitHub personal access token (or set GITHUB_TOKEN env var)
    --no-cache      Disable caching
    --cache-dir DIR Custom cache directory (default: .cache)
    --cache-ttl N   Cache time-to-live in seconds (default: 3600)
    --force-install Force reinstall even if already installed
    --verbose       Enable verbose output

EXAMPLES:
    $0 rmkane
    $0 microsoft --org --limit 50
    $0 octocat --limit 10 --no-cache
    $0 myuser --token \$GITHUB_TOKEN --verbose

ENVIRONMENT VARIABLES:
    GITHUB_TOKEN    GitHub personal access token (required)

EOF
}

# Default values
USERNAME=""
IS_ORG=false
LIMIT=""
TOKEN=""
NO_CACHE=false
CACHE_DIR=""
CACHE_TTL=""
FORCE_INSTALL=false
VERBOSE=false

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -o|--org)
                IS_ORG=true
                shift
                ;;
            -l|--limit)
                LIMIT="$2"
                shift 2
                ;;
            -t|--token)
                TOKEN="$2"
                shift 2
                ;;
            --no-cache)
                NO_CACHE=true
                shift
                ;;
            --cache-dir)
                CACHE_DIR="$2"
                shift 2
                ;;
            --cache-ttl)
                CACHE_TTL="$2"
                shift 2
                ;;
            --force-install)
                FORCE_INSTALL=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
            *)
                if [[ -z "$USERNAME" ]]; then
                    USERNAME="$1"
                else
                    log_error "Multiple usernames provided: $USERNAME and $1"
                    exit 1
                fi
                shift
                ;;
        esac
    done

    # Validate required arguments
    if [[ -z "$USERNAME" ]]; then
        log_error "Username is required"
        show_help
        exit 1
    fi
}

# Check if GitHub token is available
check_token() {
    if [[ -n "$TOKEN" ]]; then
        export GITHUB_TOKEN="$TOKEN"
    elif [[ -z "${GITHUB_TOKEN:-}" ]]; then
        log_error "GitHub token is required. Set GITHUB_TOKEN environment variable or use --token option"
        exit 1
    fi
    log_success "GitHub token is configured"
}

# Check if Python 3 is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi

    local python_version
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_info "Using Python $python_version"
}

# Install or update the project
install_project() {
    log_info "Setting up project environment..."

    # Change to project root
    cd "$PROJECT_ROOT"

    # Create virtual environment if it doesn't exist or force install
    if [[ ! -d "$VENV_DIR" ]] || [[ "$FORCE_INSTALL" == true ]]; then
        if [[ "$FORCE_INSTALL" == true ]]; then
            log_info "Force install requested, removing existing virtual environment"
            rm -rf "$VENV_DIR"
        fi

        log_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    else
        log_info "Using existing virtual environment"
    fi

    # Activate virtual environment
    log_info "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"

    # Install/upgrade the project
    log_info "Installing project dependencies..."
    pip install --upgrade pip
    pip install -e ".[dev]"

    log_success "Project installation completed"
}

# Create output directory
setup_output() {
    log_info "Setting up output directory..."
    mkdir -p "$OUTPUT_DIR"
    log_success "Output directory ready: $OUTPUT_DIR"
}

# Build CLI command
build_cli_command() {
    local cmd_args=()

    # Add verbose flag if requested
    if [[ "$VERBOSE" == true ]]; then
        cmd_args+=("--verbose")
    fi

    # Add subcommand and username
    cmd_args+=("analyze" "$USERNAME")

    # Add organization flag
    if [[ "$IS_ORG" == true ]]; then
        cmd_args+=("--org")
    fi

    # Add limit if specified
    if [[ -n "$LIMIT" ]]; then
        cmd_args+=("--limit" "$LIMIT")
    fi

    # Add token if specified
    if [[ -n "$TOKEN" ]]; then
        cmd_args+=("--token" "$TOKEN")
    fi

    # Add cache options
    if [[ "$NO_CACHE" == true ]]; then
        cmd_args+=("--no-cache")
    else
        if [[ -n "$CACHE_DIR" ]]; then
            cmd_args+=("--cache-dir" "$CACHE_DIR")
        fi
        if [[ -n "$CACHE_TTL" ]]; then
            cmd_args+=("--cache-ttl" "$CACHE_TTL")
        fi
    fi

    # Add output format
    cmd_args+=("--output" "json")

    echo "${cmd_args[@]}"
}

# Run the analysis
run_analysis() {
    local output_file="$OUTPUT_DIR/${USERNAME}_repositories.json"
    local cmd_args
    read -ra cmd_args < <(build_cli_command)

    log_info "Running analysis for user: $USERNAME"
    if [[ "$IS_ORG" == true ]]; then
        log_info "Treating as organization"
    fi

    # Show the command being run
    if [[ "$VERBOSE" == true ]]; then
        log_info "Command: $CLI_NAME ${cmd_args[*]}"
    fi

    # Run the command and capture output
    log_info "Executing analysis..."
    if "$CLI_NAME" "${cmd_args[@]}" > "$output_file" 2>/dev/null; then
        log_success "Analysis completed successfully"
        log_success "Output saved to: $output_file"

        # Show file info
        local file_size
        file_size=$(du -h "$output_file" | cut -f1)
        local repo_count
        repo_count=$(jq length "$output_file" 2>/dev/null || echo "unknown")

        log_info "File size: $file_size"
        log_info "Repository count: $repo_count"

        # Show first few repositories if verbose
        if [[ "$VERBOSE" == true ]] && command -v jq &> /dev/null; then
            log_info "First few repositories:"
            jq -r '.[0:3][] | "  - \(.name) (\(.language // "N/A"))"' "$output_file" 2>/dev/null || true
        fi

    else
        log_error "Analysis failed"
        log_error "Check the output file for details: $output_file"
        exit 1
    fi
}

# Main function
main() {
    log_info "GitHub Repository Analyzer - User Analysis Script"
    log_info "================================================="

    # Parse arguments
    parse_args "$@"

    # Pre-flight checks
    check_token
    check_python

    # Setup
    install_project
    setup_output

    # Run analysis
    run_analysis

    log_success "Script completed successfully!"
}

# Run main function with all arguments
main "$@"
