# Error Handling System

The GitHub Repository Analyzer includes a comprehensive centralized error handling system that provides consistent error processing, user-friendly messages, and detailed logging across the entire application.

## Overview

The error handling system consists of:

- **Custom Exception Hierarchy**: Well-defined exception types for different error categories
- **Error Context**: Rich context information for debugging and user experience
- **Error Handlers**: Centralized processing and conversion of exceptions
- **Migration Utilities**: Tools to help migrate existing code to the new system
- **User-Friendly Messages**: Consistent error formatting and helpful tips

## Exception Hierarchy

### Base Exception

```python
from github_repo_analyzer.errors import GitHubRepoAnalyzerError

# Base exception for all custom errors
error = GitHubRepoAnalyzerError(
    "Something went wrong",
    context=ErrorContext(operation="test_operation")
)
```

### Specific Exception Types

#### Authentication Errors

```python
from github_repo_analyzer.errors import AuthenticationError

# Raised when GitHub token is invalid or missing
raise AuthenticationError("Invalid GitHub token")
```

#### Rate Limit Errors

```python
from github_repo_analyzer.errors import RateLimitError

# Raised when GitHub API rate limit is exceeded
context = ErrorContext(retry_after=60)
raise RateLimitError("Rate limit exceeded", context=context)
```

#### Not Found Errors

```python
from github_repo_analyzer.errors import NotFoundError

# Raised when a requested resource is not found
raise NotFoundError("User not found")
```

#### Network Errors

```python
from github_repo_analyzer.errors import NetworkError

# Raised when network-related errors occur
raise NetworkError("Connection timeout")
```

#### Validation Errors

```python
from github_repo_analyzer.errors import ValidationError

# Raised when input validation fails
raise ValidationError("Invalid username", field="username")
```

#### Configuration Errors

```python
from github_repo_analyzer.errors import ConfigurationError

# Raised when configuration is invalid
raise ConfigurationError("Invalid cache directory")
```

#### API Errors

```python
from github_repo_analyzer.errors import APIError

# Raised when GitHub API returns an error
context = ErrorContext(status_code=500)
raise APIError("Server error", context=context)
```

#### Cache Errors

```python
from github_repo_analyzer.errors import CacheError

# Raised when cache operations fail
raise CacheError("Failed to write cache file")
```

## Error Context

The `ErrorContext` class provides rich context information for errors:

```python
from github_repo_analyzer.errors import ErrorContext

context = ErrorContext(
    operation="get_user_repos",
    field="username",
    value="invalid-user",
    status_code=404,
    retry_after=60,
    additional_info={"api_version": "v4"}
)

# Convert to dictionary for logging
context_dict = context.to_dict()

# Add additional information
context.add_info("user_agent", "github-repo-analyzer/1.0.0")

# Check for retry information
if context.has_retry_info():
    delay = context.get_retry_delay()
```

## Error Handling Functions

### Basic Error Handling

```python
from github_repo_analyzer.errors import handle_error, format_error_message, get_error_tip

try:
    # Some operation that might fail
    result = risky_operation()
except Exception as e:
    # Convert any exception to our custom error system
    custom_error = handle_error(e, "risky_operation")
    
    # Format for user display
    error_msg = format_error_message(custom_error)
    tip = get_error_tip(custom_error)
    
    print(f"Error: {error_msg}")
    if tip:
        print(f"Tip: {tip}")
```

### Error Handler Class

```python
from github_repo_analyzer.errors import ErrorHandler

handler = ErrorHandler()

# Handle GitHub API exceptions
github_exception = GithubException(status=403)
error = handler.handle_github_exception(github_exception, "get_repos")

# Handle network exceptions
network_exception = requests.exceptions.Timeout()
error = handler.handle_network_exception(network_exception, "api_call")

# Handle validation exceptions
validation_exception = ValueError("Invalid input")
error = handler.handle_validation_exception(
    validation_exception, 
    field="username", 
    operation="validation"
)
```

### Error Handler Decorator

```python
from github_repo_analyzer.errors import error_handler

@error_handler("get_user_repos")
def get_user_repos(username: str):
    # This function will automatically convert any exception
    # to our custom error system
    return github_api.get_user(username).get_repos()
```

## Migration Utilities

### Converting Existing Exceptions

```python
from github_repo_analyzer.errors import (
    convert_github_exception,
    convert_network_exception,
    convert_value_error,
    convert_config_error,
    create_legacy_validation_error
)

# Convert GitHub API exceptions
try:
    user = github.get_user(username)
except GithubException as e:
    raise convert_github_exception(e, "get_user")

# Convert network exceptions
try:
    response = requests.get(url)
except requests.exceptions.Timeout as e:
    raise convert_network_exception(e, "api_request")

# Convert validation errors
try:
    validate_username(username)
except ValueError as e:
    raise convert_value_error(e, field="username")

# Create legacy-compatible validation errors
error = create_legacy_validation_error("Invalid username", "username")
```

## Integration with CLI Commands

### Basic Integration

```python
import click
from github_repo_analyzer.errors import (
    format_error_message,
    get_error_tip,
    log_error_with_context
)

@click.command()
def analyze_command():
    try:
        # Command logic here
        pass
    except GitHubRepoAnalyzerError as e:
        # Handle our custom errors
        error_msg = format_error_message(e)
        tip = get_error_tip(e)
        
        click.echo(f"Error: {error_msg}", err=True)
        if tip:
            click.echo(f"Tip: {tip}", err=True)
        
        # Log with context
        log_error_with_context(logger, e, "analyze command")
        
        raise click.ClickException(error_msg)
    except Exception as e:
        # Handle unexpected errors
        click.echo(f"Unexpected error: {e}", err=True)
        log_error_with_context(logger, e, "analyze command")
        raise click.ClickException(f"Unexpected error: {e}")
```

### Advanced Integration with Error Conversion

```python
from github_repo_analyzer.errors import handle_error

@click.command()
def analyze_command():
    try:
        # Command logic here
        pass
    except (ValueError, ValidationError) as e:
        # Convert legacy errors to new system
        custom_error = handle_error(e, "analyze command")
        
        error_msg = format_error_message(custom_error)
        tip = get_error_tip(custom_error)
        
        click.echo(f"Error: {error_msg}", err=True)
        if tip:
            click.echo(f"Tip: {tip}", err=True)
        
        log_error_with_context(logger, custom_error, "analyze command")
        raise click.ClickException(error_msg)
    except Exception as e:
        # Handle any other errors
        custom_error = handle_error(e, "analyze command")
        error_msg = format_error_message(custom_error)
        click.echo(f"Error: {error_msg}", err=True)
        raise click.ClickException(error_msg)
```

## Logging Integration

The error handling system integrates seamlessly with the logging system:

```python
from github_repo_analyzer.errors import log_error_with_context
from github_repo_analyzer.loggers import get_logger

logger = get_logger(__name__)

try:
    # Some operation
    result = risky_operation()
except Exception as e:
    # Log with context
    log_error_with_context(logger, e, "risky_operation")
    raise
```

## Best Practices

### 1. Use Specific Exception Types

```python
# Good: Use specific exception types
if not token:
    raise AuthenticationError("GitHub token is required")

# Avoid: Generic exceptions
if not token:
    raise ValueError("GitHub token is required")
```

### 2. Provide Rich Context

```python
# Good: Provide rich context
context = ErrorContext(
    operation="get_user_repos",
    field="username",
    value=username,
    status_code=404
)
raise NotFoundError("User not found", context=context)

# Avoid: Minimal context
raise NotFoundError("User not found")
```

### 3. Use Migration Utilities for Legacy Code

```python
# Good: Use migration utilities
try:
    user = github.get_user(username)
except GithubException as e:
    raise convert_github_exception(e, "get_user")

# Avoid: Manual conversion
try:
    user = github.get_user(username)
except GithubException as e:
    if e.status == 404:
        raise NotFoundError("User not found")
    # ... more manual mapping
```

### 4. Handle Errors at the Right Level

```python
# Good: Handle errors at the CLI level
@click.command()
def analyze_command():
    try:
        # Business logic
        result = service.analyze_repos(username)
    except GitHubRepoAnalyzerError as e:
        # Convert to user-friendly message
        error_msg = format_error_message(e)
        click.echo(f"Error: {error_msg}", err=True)
        raise click.ClickException(error_msg)

# Avoid: Handling errors in business logic
def analyze_repos(username):
    try:
        # Business logic
        pass
    except Exception as e:
        # Don't handle CLI concerns in business logic
        click.echo(f"Error: {e}")
        raise
```

## Testing Error Handling

The error handling system includes comprehensive tests:

```python
def test_error_handling():
    # Test exception creation
    error = AuthenticationError("Invalid token")
    assert isinstance(error, GitHubRepoAnalyzerError)
    
    # Test error formatting
    error_msg = format_error_message(error)
    assert "Authentication Error" in error_msg
    
    # Test error tips
    tip = get_error_tip(error)
    assert "GITHUB_TOKEN" in tip
    
    # Test error conversion
    github_exception = MagicMock()
    github_exception.status = 401
    converted = convert_github_exception(github_exception, "test")
    assert isinstance(converted, AuthenticationError)
```

## Migration Guide

To migrate existing code to use the new error handling system:

1. **Import the error handling modules**:

   ```python
   from github_repo_analyzer.errors import (
       GitHubRepoAnalyzerError,
       AuthenticationError,
       # ... other exceptions
   )
   ```

2. **Replace generic exceptions with specific ones**:

   ```python
   # Before
   raise ValueError("Invalid token")
   
   # After
   raise AuthenticationError("Invalid token")
   ```

3. **Use migration utilities for existing exception handling**:

   ```python
   # Before
   try:
       user = github.get_user(username)
   except GithubException as e:
       if e.status == 404:
           raise ValueError("User not found")
   
   # After
   try:
       user = github.get_user(username)
   except GithubException as e:
       raise convert_github_exception(e, "get_user")
   ```

4. **Update CLI error handling**:

   ```python
   # Before
   except ValueError as e:
       click.echo(f"Error: {e}", err=True)
       raise click.ClickException(str(e))
   
   # After
   except GitHubRepoAnalyzerError as e:
       error_msg = format_error_message(e)
       tip = get_error_tip(e)
       click.echo(f"Error: {error_msg}", err=True)
       if tip:
           click.echo(f"Tip: {tip}", err=True)
       raise click.ClickException(error_msg)
   ```

This centralized error handling system provides a robust foundation for error management across the entire application, making it easier to maintain, debug, and provide a better user experience.
