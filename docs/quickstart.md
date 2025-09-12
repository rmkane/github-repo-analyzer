# Quick Start

Get up and running with GitHub Repository Analyzer in just a few minutes!

## Basic Usage

### Analyze a User's Repositories

```bash
github-repo-analyzer analyze rmkane
```

This will show a beautiful table with:

- Repository names
- Programming languages
- Star and fork counts
- Repository size
- Privacy status
- Archive status
- Last update date

### Analyze an Organization

```bash
github-repo-analyzer analyze microsoft --org
```

### Limit Results

```bash
# Show only top 10 repositories
github-repo-analyzer analyze rmkane --limit 10

# Show all repositories (no limit)
github-repo-analyzer analyze rmkane --limit -1
```

## Output Formats

### Table Format (Default)

```bash
github-repo-analyzer analyze rmkane
```

### JSON Format

```bash
github-repo-analyzer analyze rmkane --format json
```

### Summary Format

```bash
github-repo-analyzer analyze rmkane --format summary
```

## Filtering and Sorting

### Filter by Language

```bash
github-repo-analyzer analyze rmkane --language python
```

### Filter by Minimum Stars

```bash
github-repo-analyzer analyze rmkane --min-stars 10
```

### Sort by Different Fields

```bash
# Sort by stars (default)
github-repo-analyzer analyze rmkane --sort stars

# Sort by forks
github-repo-analyzer analyze rmkane --sort forks

# Sort by updated date
github-repo-analyzer analyze rmkane --sort updated
```

### Show Only Public Repositories

```bash
github-repo-analyzer analyze rmkane --public-only
```

## Advanced Examples

### Analyze Large Organizations

```bash
# Microsoft has many repositories, so limit to top 50
github-repo-analyzer analyze microsoft --org --limit 50 --sort stars
```

### Find Popular Python Projects

```bash
github-repo-analyzer analyze rmkane --language python --min-stars 5 --sort stars
```

### Get Repository Summary

```bash
github-repo-analyzer analyze rmkane --format summary
```

### Save Results to File

```bash
github-repo-analyzer analyze rmkane --format json > repos.json
```

## Configuration

### Set Default Cache Directory

```bash
github-repo-analyzer analyze rmkane --cache-dir ~/.cache/github-analyzer
```

### Set Cache TTL (Time To Live)

```bash
# Cache results for 1 hour (3600 seconds)
github-repo-analyzer analyze rmkane --cache-ttl 3600
```

### Verbose Output

```bash
github-repo-analyzer analyze rmkane --verbose
```

### Quiet Output

```bash
github-repo-analyzer analyze rmkane --quiet
```

## Search Functionality

You can also search for repositories across GitHub:

```bash
# Search for Python repositories
github-repo-analyzer search python

# Search with filters
github-repo-analyzer search "machine learning" --language python --min-stars 100
```

## Getting Help

### General Help

```bash
github-repo-analyzer --help
```

### Command-Specific Help

```bash
github-repo-analyzer analyze --help
github-repo-analyzer search --help
```

## Next Steps

- Read the [User Guide](user-guide/configuration.md) for detailed configuration options
- Check out the [API Reference](api/core.md) for developer documentation
