"""Migration utilities for converting to centralized error handling.

This module provides utilities to help migrate existing error handling
code to use the new centralized error system.
"""

from typing import Optional

import requests.exceptions
from github import GithubException

from github_repo_analyzer.errors.context import (
    create_api_context,
    create_network_context,
    create_validation_context,
)
from github_repo_analyzer.errors.exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    GitHubRepoAnalyzerError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


def convert_github_exception(
    exception: GithubException, operation: str
) -> GitHubRepoAnalyzerError:
    """Convert GitHub exception to custom exception.

    Args:
        exception: The GitHub exception
        operation: Description of the operation

    Returns:
        Appropriate custom exception
    """
    status_code = getattr(exception, "status", None)
    context = create_api_context(operation, status_code=status_code)

    if status_code == 401:
        return AuthenticationError(
            "Invalid GitHub token. Please check your token and try again.",
            context=context,
            cause=exception,
        )
    elif status_code == 403:
        if "rate limit" in str(exception).lower():
            return RateLimitError(
                "GitHub API rate limit exceeded. Please wait before trying "
                "again. Consider using a personal access token for higher "
                "limits.",
                context=context,
                cause=exception,
            )
        else:
            return AuthenticationError(
                "GitHub API access forbidden. Your token may lack required "
                "permissions.",
                context=context,
                cause=exception,
            )
    elif status_code == 404:
        return NotFoundError(
            "GitHub user or organization not found. Please check the name "
            "and try again.",
            context=context,
            cause=exception,
        )
    elif status_code == 422:
        return ValidationError(
            f"Invalid request: {exception}", context=context, cause=exception
        )
    elif status_code == 429:
        return RateLimitError(
            "GitHub API rate limit exceeded. Please wait before trying "
            "again. Consider using a personal access token for higher "
            "limits.",
            context=context,
            cause=exception,
        )
    else:
        return APIError(
            f"GitHub API error during {operation}: {exception}",
            context=context,
            cause=exception,
        )


def convert_network_exception(
    exception: Exception,
    operation: str,
) -> NetworkError:
    """Convert network exception to custom exception.

    Args:
        exception: The network exception
        operation: Description of the operation

    Returns:
        NetworkError with appropriate context
    """
    context = create_network_context(operation)

    if isinstance(exception, requests.exceptions.Timeout):
        message = (
            f"Request timeout during {operation}. Please check your "
            "connection and try again."
        )
    elif isinstance(exception, requests.exceptions.ConnectionError):
        message = (
            f"Connection error during {operation}. Please check your "
            "internet connection."
        )
    else:
        message = f"Network error during {operation}: {exception}"

    return NetworkError(message, context=context, cause=exception)


def convert_value_error(
    exception: ValueError, field: Optional[str] = None, operation: Optional[str] = None
) -> ValidationError:
    """Convert ValueError to ValidationError.

    Args:
        exception: The ValueError
        field: Field that failed validation
        operation: Operation being performed

    Returns:
        ValidationError with appropriate context
    """
    context = create_validation_context(field or "unknown", operation=operation)
    return ValidationError(str(exception), context=context, cause=exception)


def convert_config_error(
    exception: ValueError, operation: str = "configuration"
) -> ConfigurationError:
    """Convert configuration ValueError to ConfigurationError.

    Args:
        exception: The ValueError
        operation: Description of the configuration operation

    Returns:
        ConfigurationError with appropriate context
    """
    context = create_validation_context("configuration", operation=operation)
    return ConfigurationError(str(exception), context=context, cause=exception)


def create_legacy_validation_error(
    message: str, field: Optional[str] = None
) -> ValidationError:
    """Create ValidationError compatible with legacy ValidationError.

    This function helps maintain compatibility with existing code that
    expects the old ValidationError interface.

    Args:
        message: Error message
        field: Field name that failed validation

    Returns:
        ValidationError instance
    """
    context = create_validation_context(field or "unknown")
    return ValidationError(message, context=context)
