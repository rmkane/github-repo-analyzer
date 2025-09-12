# Installation

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Install from PyPI

The easiest way to install GitHub Repository Analyzer is using pip:

```bash
pip install github-repo-analyzer
```

## Install from Source

If you want to install the latest development version or contribute to the project:

```bash
# Clone the repository
git clone https://github.com/rmkane/github-repo-analyzer.git
cd github-repo-analyzer

# Install in development mode
pip install -e ".[dev]"
```

## Verify Installation

After installation, verify that the tool is working:

```bash
github-repo-analyzer --version
```

You should see output like:

```none
GitHub Repository Analyzer v0.1.0
```

## GitHub Token Setup (Optional)

While the tool works without a GitHub token, using one provides:

- Higher API rate limits (5,000 vs 60 requests per hour)
- Access to private repository metadata (if you have access)
- Better reliability for large-scale analysis

### Creating a GitHub Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name like "GitHub Repository Analyzer"
4. Select scopes:
   - `public_repo` (for public repositories)
   - `repo` (for private repositories, if needed)
5. Click "Generate token"
6. Copy the token (you won't see it again!)

### Using the Token

You can provide the token in several ways:

#### Environment Variable (Recommended)

```bash
export GITHUB_TOKEN=your_token_here
github-repo-analyzer analyze rmkane
```

#### Command Line Option

```bash
github-repo-analyzer analyze rmkane --token your_token_here
```

#### Configuration File

Create a `.env` file in your home directory:

```bash
echo "GITHUB_TOKEN=your_token_here" >> ~/.env
```

## Development Installation

For development work, install with all dependencies:

```bash
git clone https://github.com/rmkane/github-repo-analyzer.git
cd github-repo-analyzer
pip install -e ".[dev,docs]"
```

This includes:

- Testing tools (pytest, coverage)
- Code formatting (black, isort)
- Linting (flake8, mypy)
- Documentation tools (mkdocs)
- Pre-commit hooks

## Docker Installation

You can also run the tool using Docker:

```bash
# Build the image
docker build -t github-repo-analyzer .

# Run with environment variable
docker run --rm -e GITHUB_TOKEN=your_token github-repo-analyzer analyze rmkane
```

## Troubleshooting

### Permission Errors

If you get permission errors during installation, try:

```bash
pip install --user github-repo-analyzer
```

### Python Version Issues

Make sure you're using Python 3.8 or higher:

```bash
python --version
```

### Network Issues

If you have network issues, try using a different pip index:

```bash
pip install -i https://pypi.org/simple/ github-repo-analyzer
```
