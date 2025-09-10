# Scripts

This directory contains automation scripts for the GitHub Repository Analyzer.

## Scripts Overview

### `analyze-user.sh` - Full-Featured Analysis Script

A comprehensive script that handles installation, activation, and execution of the CLI tool.

**Features:**

- Automatic virtual environment setup
- Project installation/upgrade
- Comprehensive command-line options
- Colored output and logging
- Error handling and validation
- Clean JSON output to `output/` directory (no logging mixed in)

**Usage:**

```bash
# Basic usage
./scripts/analyze-user.sh rmkane

# With options
./scripts/analyze-user.sh microsoft --org --limit 50 --verbose

# Custom cache settings
./scripts/analyze-user.sh octocat --cache-dir my-cache --cache-ttl 7200

# Disable caching
./scripts/analyze-user.sh rmkane --no-cache
```

**Options:**

- `-h, --help`: Show help message
- `-o, --org`: Treat username as organization
- `-l, --limit N`: Limit number of repositories
- `-t, --token`: GitHub token (or set GITHUB_TOKEN env var)
- `--no-cache`: Disable caching
- `--cache-dir DIR`: Custom cache directory
- `--cache-ttl N`: Cache TTL in seconds
- `--force-install`: Force reinstall
- `--verbose`: Enable verbose output

### `quick-analyze.sh` - Simple Analysis Script

A lightweight script for quick repository analysis.

**Features:**

- Minimal setup
- Simple command-line interface
- Automatic virtual environment management
- Basic error handling

**Usage:**

```bash
# Basic usage
./scripts/quick-analyze.sh rmkane

# With limit
./scripts/quick-analyze.sh rmkane 10

# Organization
./scripts/quick-analyze.sh microsoft 50
```

## Prerequisites

### Required

- **Python 3**: Must be installed and available as `python3`
- **GitHub Token**: Set `GITHUB_TOKEN` environment variable or use `--token` option

### Optional

- **jq**: For JSON processing and statistics (recommended)
- **bash**: Scripts require bash 4.0+ (most modern systems)

## Environment Variables

### Required Environment Variables

- `GITHUB_TOKEN`: GitHub personal access token

### Optional Environment Variables

- `GITHUB_CACHE_DIR`: Default cache directory (overridden by `--cache-dir`)
- `GITHUB_CACHE_TTL`: Default cache TTL in seconds (overridden by `--cache-ttl`)

## Output

All scripts output JSON files to the `output/` directory:

- **File naming**: `{username}_repositories.json`
- **Format**: JSON array of repository objects
- **Location**: `output/` directory (created automatically)

## Examples

### Analyze a user's repositories

```bash
export GITHUB_TOKEN="your_token_here"
./scripts/analyze-user.sh rmkane
# Output: output/rmkane_repositories.json
```

### Analyze an organization with limit

```bash
./scripts/analyze-user.sh microsoft --org --limit 100
# Output: output/microsoft_repositories.json
```

### Quick analysis with caching disabled

```bash
./scripts/quick-analyze.sh octocat 5
# Output: output/octocat_repositories.json
```

### Verbose analysis with custom cache

```bash
./scripts/analyze-user.sh rmkane --verbose --cache-dir /tmp/github-cache --cache-ttl 1800
```

## Error Handling

- **Missing dependencies**: Scripts check for Python 3 and required tools
- **Invalid tokens**: Clear error messages for authentication issues
- **Network errors**: Graceful handling of API failures
- **File permissions**: Automatic creation of output directories
- **Cache issues**: Automatic cleanup of corrupted cache files

## Troubleshooting

### Common Issues

1. **"Python 3 not found"**
   - Install Python 3 or ensure it's in your PATH
   - On macOS: `brew install python3`
   - On Ubuntu: `sudo apt install python3 python3-pip python3-venv`

2. **"GitHub token required"**
   - Set `GITHUB_TOKEN` environment variable
   - Or use `--token` option with the script

3. **"Permission denied"**
   - Make scripts executable: `chmod +x scripts/*.sh`
   - Check file permissions in project directory

4. **"Virtual environment issues"**
   - Use `--force-install` to recreate virtual environment
   - Ensure you have write permissions in project directory

### Debug Mode

Use `--verbose` flag for detailed output:

```bash
./scripts/analyze-user.sh rmkane --verbose
```

This shows:

- Command being executed
- Cache hit/miss information
- File sizes and repository counts
- First few repositories in the output

## Integration

These scripts can be integrated into:

- **CI/CD pipelines**: Use in GitHub Actions, Jenkins, etc.
- **Cron jobs**: Schedule regular repository analysis
- **Monitoring systems**: Track repository changes over time
- **Data pipelines**: Feed JSON output into other tools
