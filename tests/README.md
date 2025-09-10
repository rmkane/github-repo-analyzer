# Tests

This directory contains tests for the GitHub Repository Analyzer project.

## Test Structure

### Unit Tests (`test_api.py`)

- **Purpose**: Test individual components in isolation
- **Scope**: GitHub API client, Repository model, error handling
- **Mocking**: Uses `unittest.mock` to mock external API calls
- **Run**: `pytest tests/test_api.py`

### Integration Tests (`test_cli.py`)

- **Purpose**: Test CLI commands end-to-end
- **Scope**: Command-line interface, real GitHub API calls, output formats
- **Requirements**: Requires `GITHUB_TOKEN` environment variable
- **Run**: `pytest tests/test_cli.py`

## Running Tests

```bash
# Run all tests
make test

# Run only unit tests (no API calls)
pytest tests/test_api.py

# Run only integration tests (requires GITHUB_TOKEN)
pytest tests/test_cli.py

# Run with coverage
make test-coverage
```

## Test Environment

### Unit Tests

- No external dependencies
- Use mocked GitHub API responses
- Fast execution
- Always pass regardless of network/API status

### Integration Tests

- Require `GITHUB_TOKEN` environment variable
- Make real API calls to GitHub
- Test actual CLI behavior
- May be slower due to network calls
- Skip automatically if token not available

## Adding New Tests

### For Unit Tests

- Add to `test_api.py` or create new `test_*.py` files
- Mock all external dependencies
- Focus on testing logic, error handling, data validation

### For Integration Tests

- Add to `test_cli.py` or create new `test_*_integration.py` files
- Use `@pytest.fixture` for setup (tokens, temp directories)
- Test real CLI commands with `subprocess.run()`
- Verify output formats, error messages, exit codes

## Test Data

- Integration tests use public GitHub users (e.g., `octocat`)
- No sensitive data should be committed to tests
- Use `tempfile.TemporaryDirectory()` for temporary files
- Clean up after tests
