<!-- omit in toc -->
# GitHub Repository Analyzer

A modern Python CLI tool for analyzing GitHub repositories for users and organizations. Built with best practices including type hints, comprehensive testing, and containerization support.

<!-- omit in toc -->
## Table of content

- [Features](#features)
- [Installation](#installation)
  - [From Source](#from-source)
  - [Using Docker](#using-docker)
- [Quick Start](#quick-start)
  - [1. Set up GitHub Token](#1-set-up-github-token)
  - [2. Basic Usage](#2-basic-usage)
- [Usage Examples](#usage-examples)
  - [Analyze User Repositories](#analyze-user-repositories)
  - [Analyze Organization Repositories](#analyze-organization-repositories)
  - [Advanced Search and Filtering](#advanced-search-and-filtering)
  - [Using Docker (Usage)](#using-docker-usage)
- [Development](#development)
  - [Setup Development Environment](#setup-development-environment)
  - [Available Make Targets](#available-make-targets)
  - [Running Tests](#running-tests)
  - [Code Quality](#code-quality)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [CLI Options](#cli-options)
    - [Global Options](#global-options)
    - [Analyze Command](#analyze-command)
    - [Search Command](#search-command)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
  - [GitHubAPI Class](#githubapi-class)
    - [Methods](#methods)
  - [Repository Model](#repository-model)
- [Contributing](#contributing)
- [License](#license)
- [Automation Scripts](#automation-scripts)
  - [Quick Analysis Script](#quick-analysis-script)
  - [Full-Featured Analysis Script](#full-featured-analysis-script)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Getting Help](#getting-help)

## Features

- 🔍 **Repository Analysis**: Analyze repositories for any GitHub user or organization
- 📊 **Rich Statistics**: Get comprehensive statistics including stars, forks, languages, and more
- 🎨 **Beautiful CLI**: Rich terminal output with tables and colored text
- 🔍 **Advanced Filtering**: Filter repositories by language, stars, forks, visibility, and more
- 🐳 **Docker Support**: Run in containers for easy deployment
- 🧪 **Well Tested**: Comprehensive test suite with good coverage
- 📦 **Modern Python**: Uses latest Python packaging standards (pyproject.toml)

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd github-project-config

# Install in development mode (creates virtual environment automatically)
make install-dev

# Or install directly with virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Using Docker

```bash
# Build the Docker image
make docker-build

# Or manually
docker build -t github-repo-analyzer .
```

## Quick Start

### 1. Set up GitHub Token

Create a GitHub Personal Access Token:

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Generate a new token with appropriate scopes:
   - `public_repo` for public repositories
   - `repo` for private repositories (if needed)

Set the token as an environment variable:

```bash
export GITHUB_TOKEN=your_token_here
```

Or create a `.env` file:

```bash
echo "GITHUB_TOKEN=your_token_here" > .env
```

### 2. Basic Usage

```bash
# Analyze a user's repositories
github-repo-analyzer analyze microsoft

# Analyze an organization's repositories
github-repo-analyzer analyze microsoft --org

# Get a summary view
github-repo-analyzer analyze microsoft --org --output summary

# Search with filters
github-repo-analyzer search microsoft --org --language Python --min-stars 1000
```

## Usage Examples

### Analyze User Repositories

```bash
# Basic analysis
github-repo-analyzer analyze torvalds

# With summary output
github-repo-analyzer analyze torvalds --output summary

# Limit results
github-repo-analyzer analyze torvalds --limit 10
```

### Analyze Organization Repositories

```bash
# Analyze Microsoft's repositories
github-repo-analyzer analyze microsoft --org

# Get JSON output for processing
github-repo-analyzer analyze microsoft --org --output json
```

### Advanced Search and Filtering

```bash
# Find Python repositories with 100+ stars
github-repo-analyzer search microsoft --org --language Python --min-stars 100

# Find public repositories only
github-repo-analyzer search microsoft --org --public-only

# Find repositories with specific fork count
github-repo-analyzer search microsoft --org --min-forks 50
```

### Using Docker (Usage)

```bash
# Run with Docker
make docker-run ARGS="analyze microsoft --org"

# Or manually
docker run --rm -e GITHUB_TOKEN=$GITHUB_TOKEN github-repo-analyzer analyze microsoft --org

# Interactive shell
make docker-shell
```

## Development

### Setup Development Environment

```bash
# Install development dependencies (creates virtual environment)
make install-dev

# Activate virtual environment
source venv/bin/activate

# Set up pre-commit hooks
make setup-dev

# Run all checks
make all
```

### Available Make Targets

```bash
make help  # Show all available targets

# Development
make install-dev    # Install in development mode
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linting
make format        # Format code
make clean         # Clean build artifacts

# Building
make build         # Build package
make build-wheel   # Build wheel only
make build-sdist   # Build source distribution

# Docker
make docker-build  # Build Docker image
make docker-run    # Run Docker container
make docker-shell  # Interactive Docker shell

# CI
make ci            # Run CI pipeline locally
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_api.py -v
```

### Code Quality

```bash
# Format code
make format

# Check formatting
make format-check

# Run linting
make lint

# Type checking
mypy src/github_repo_analyzer
```

## Configuration

### Environment Variables

- `GITHUB_TOKEN`: GitHub Personal Access Token (required)

### CLI Options

#### Global Options

- `--version`: Show version information
- `--help`: Show help message

#### Analyze Command

- `username_or_org`: GitHub username or organization name
- `--org, -o`: Treat input as organization name
- `--token, -t`: GitHub token (overrides environment variable)
- `--output, -o`: Output format (table, json, summary)
- `--limit, -l`: Limit number of repositories to show

#### Search Command

- `username_or_org`: GitHub username or organization name
- `--org, -o`: Treat input as organization name
- `--token, -t`: GitHub token (overrides environment variable)
- `--language, -l`: Filter by programming language
- `--min-stars`: Minimum number of stars
- `--min-forks`: Minimum number of forks
- `--public-only`: Show only public repositories
- `--private-only`: Show only private repositories

## Project Structure

```none
github-project-config/
├── src/
│   └── github_repo_analyzer/
│       ├── __init__.py
│       ├── api.py          # GitHub API client
│       └── cli.py          # CLI interface
├── tests/
│   ├── __init__.py
│   └── test_api.py         # API tests
├── pyproject.toml          # Project configuration
├── Makefile               # Build and development tasks
├── Dockerfile             # Container configuration
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## API Reference

### GitHubAPI Class

The main API client for interacting with GitHub's API.

#### Methods

- `get_user_repos(username, per_page=100, page=1)`: Get repositories for a user
- `get_org_repos(org_name, per_page=100, page=1)`: Get repositories for an organization
- `get_all_repos(username_or_org, is_organization=False)`: Get all repositories (handles pagination)
- `get_repo_stats(username_or_org, is_organization=False)`: Get comprehensive repository statistics

### Repository Model

Pydantic model representing a GitHub repository with fields like:

- `name`, `full_name`, `description`
- `html_url`, `clone_url`, `ssh_url`
- `language`, `stargazers_count`, `forks_count`
- `size`, `created_at`, `updated_at`, `pushed_at`
- `private`, `archived`, `disabled`
- `topics`, `license`, `owner`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `make test`
5. Run linting: `make lint`
6. Format code: `make format`
7. Commit your changes: `git commit -am 'Add feature'`
8. Push to the branch: `git push origin feature-name`
9. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Automation Scripts

The `scripts/` directory contains automation scripts for easy CLI usage:

### Quick Analysis Script

```bash
# Simple analysis with automatic setup
./scripts/quick-analyze.sh rmkane
./scripts/quick-analyze.sh rmkane 10  # Limit to 10 repos
```

### Full-Featured Analysis Script

```bash
# Comprehensive script with all options
./scripts/analyze-user.sh rmkane --verbose
./scripts/analyze-user.sh microsoft --org --limit 50
./scripts/analyze-user.sh octocat --no-cache --cache-dir /tmp/cache
```

**Features:**

- Automatic virtual environment setup
- Project installation and activation
- JSON output to `output/` directory
- Comprehensive error handling
- Colored output and logging
- All CLI options supported

See `scripts/README.md` for detailed documentation.

## Troubleshooting

### Common Issues

1. **"GitHub token is required" error**
   - Make sure you've set the `GITHUB_TOKEN` environment variable
   - Or use the `--token` option: `github-repo-analyzer analyze user --token your_token`

2. **Rate limiting**
   - GitHub API has rate limits. Authenticated requests have higher limits
   - Consider adding delays between requests for large organizations

3. **Permission errors**
   - Make sure your token has the required scopes
   - For private repositories, you need `repo` scope

4. **Docker issues**
   - Make sure Docker is running
   - Check that the `GITHUB_TOKEN` environment variable is set

### Getting Help

- Check the [Issues](https://github.com/yourusername/github-repo-analyzer/issues) page
- Create a new issue with detailed information about your problem
- Include your Python version, operating system, and error messages
