# Configuration

GitHub Repository Analyzer supports various configuration options to customize its behavior.

## Environment Variables

### GITHUB_TOKEN

Your GitHub Personal Access Token for API authentication.

```bash
export GITHUB_TOKEN=your_token_here
```

**Benefits:**

- Higher rate limits (5,000 vs 60 requests per hour)
- Access to private repository metadata
- Better reliability for large-scale analysis

## Command Line Options

### Global Options

#### `--token`

Specify GitHub token directly.

```bash
github-repo-analyzer analyze rmkane --token your_token_here
```

#### `--cache-dir`

Set custom cache directory.

```bash
github-repo-analyzer analyze rmkane --cache-dir ~/.cache/github-analyzer
```

**Default:** `~/.cache/github-repo-analyzer`

#### `--cache-ttl`

Set cache time-to-live in seconds.

```bash
github-repo-analyzer analyze rmkane --cache-ttl 3600  # 1 hour
```

**Default:** `3600` (1 hour)  
**Range:** `0` to `2592000` (30 days)

#### `--verbose`

Enable verbose logging.

```bash
github-repo-analyzer analyze rmkane --verbose
```

#### `--quiet`

Suppress all output except errors.

```bash
github-repo-analyzer analyze rmkane --quiet
```

#### `--log-file`

Specify custom log file.

```bash
github-repo-analyzer analyze rmkane --log-file /path/to/logfile.log
```

#### `--no-auto-log`

Disable automatic log file creation.

```bash
github-repo-analyzer analyze rmkane --no-auto-log
```

### Analyze Command Options

#### `--limit`

Limit number of repositories to fetch.

```bash
github-repo-analyzer analyze rmkane --limit 50
```

**Values:**

- `-1`: Unlimited (fetch all repositories)
- `0`: Zero repositories
- `100`: Default limit
- Any positive integer

#### `--sort`

Sort repositories by field.

```bash
github-repo-analyzer analyze rmkane --sort stars
```

**Options:**

- `stars` (default): Sort by star count
- `forks`: Sort by fork count  
- `updated`: Sort by last update date
- `created`: Sort by creation date
- `name`: Sort alphabetically by name
- `size`: Sort by repository size

#### `--language`

Filter by programming language.

```bash
github-repo-analyzer analyze rmkane --language python
```

#### `--min-stars`

Filter by minimum star count.

```bash
github-repo-analyzer analyze rmkane --min-stars 10
```

#### `--min-forks`

Filter by minimum fork count.

```bash
github-repo-analyzer analyze rmkane --min-forks 5
```

#### `--public-only`

Show only public repositories.

```bash
github-repo-analyzer analyze rmkane --public-only
```

#### `--private-only`

Show only private repositories.

```bash
github-repo-analyzer analyze rmkane --private-only
```

#### `--format`

Choose output format.

```bash
github-repo-analyzer analyze rmkane --format table
```

**Options:**

- `table` (default): Beautiful terminal table
- `json`: JSON output
- `summary`: Statistical summary

### Search Command Options

All analyze options plus:

#### `--query`

Search query string.

```bash
github-repo-analyzer search "machine learning" --language python
```

## Configuration File

You can create a `.env` file in your home directory for persistent configuration:

```bash
# ~/.env
GITHUB_TOKEN=your_token_here
CACHE_DIR=~/.cache/github-analyzer
CACHE_TTL=7200
```

## Logging Configuration

### Log Levels

- `DEBUG`: Detailed information for debugging
- `INFO`: General information about program execution
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for failures
- `CRITICAL`: Critical errors that may cause program termination

### Log Output

**Console Output:**

- Colored output for better readability
- Configurable verbosity levels
- Real-time feedback

**File Output:**

- Automatic log file creation
- Platform-specific default locations:
  - **Windows**: `%APPDATA%\github-repo-analyzer\logs\`
  - **macOS**: `~/Library/Logs/github-repo-analyzer/`
  - **Linux**: `~/.github-repo-analyzer/logs/`
- Date-based naming: `github-repo-analyzer-YYYY-MM-DD.log`
- Automatic cleanup of old log files

### Custom Log Configuration

```bash
# Verbose logging to console
github-repo-analyzer analyze rmkane --verbose

# Quiet mode (errors only)
github-repo-analyzer analyze rmkane --quiet

# Custom log file
github-repo-analyzer analyze rmkane --log-file /path/to/custom.log

# Disable automatic log files
github-repo-analyzer analyze rmkane --no-auto-log
```

## Best Practices

### Performance Optimization

1. **Use GitHub Token**: Significantly improves rate limits
2. **Enable Caching**: Reduces API calls for repeated analysis
3. **Limit Results**: Use `--limit` for large organizations
4. **Filter Early**: Use `--language`, `--min-stars` to reduce data

### Rate Limiting

- **Without Token**: 60 requests/hour
- **With Token**: 5,000 requests/hour
- **Caching**: Reduces API calls for repeated queries
- **Pagination**: Automatically handles large result sets

### Error Handling

The tool includes comprehensive error handling:

- **Network Issues**: Automatic retries with exponential backoff
- **Rate Limiting**: Clear error messages and suggestions
- **Invalid Input**: Detailed validation error messages
- **API Errors**: Graceful handling of GitHub API issues
