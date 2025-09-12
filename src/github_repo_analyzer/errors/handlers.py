"""Error handling utilities for GitHub Repository Analyzer.

This module provides centralized error handling functions that ensure
consistent error processing, logging, and user experience across the
application.
"""

import logging
from functools import wraps
from typing import Any, Callable, Optional

from github_repo_analyzer.errors.context import (
    create_api_context,
    create_network_context,
    create_validation_context,
)
from github_repo_analyzer.errors.exceptions import (
    APIError,
    AuthenticationError,
    CacheError,
    ConfigurationError,
    ErrorContext,
    GitHubRepoAnalyzerError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


class ErrorHandler:
    """Centralized error handler for consistent error processing."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize error handler.

        Args:
            logger: Logger instance for error logging
        """
        self.logger = logger or logging.getLogger(__name__)

    def handle_github_exception(
        self, exception: Exception, operation: str, status_code: Optional[int] = None
    ) -> GitHubRepoAnalyzerError:
        """Convert GitHub API exceptions to custom exceptions.

        Args:
            exception: The original GitHub exception
            operation: Description of the operation that failed
            status_code: HTTP status code if available

        Returns:
            Appropriate custom exception
        """
        context = create_api_context(operation, status_code=status_code)

        # Extract status code from exception if not provided
        if status_code is None and hasattr(exception, "status"):
            status_code = getattr(exception, "status")
            context.status_code = status_code

        # Map status codes to appropriate exceptions
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

    def handle_network_exception(
        self, exception: Exception, operation: str
    ) -> NetworkError:
        """Convert network exceptions to custom exceptions.

        Args:
            exception: The original network exception
            operation: Description of the operation that failed

        Returns:
            NetworkError with appropriate context
        """
        context = create_network_context(operation)

        if "timeout" in str(exception).lower():
            message = (
                f"Request timeout during {operation}. Please check your "
                "connection and try again."
            )
        elif "connection" in str(exception).lower():
            message = (
                f"Connection error during {operation}. Please check your "
                "internet connection."
            )
        else:
            message = f"Network error during {operation}: {exception}"

        return NetworkError(message, context=context, cause=exception)

    def handle_validation_exception(
        self,
        exception: Exception,
        field: Optional[str] = None,
        operation: Optional[str] = None,
    ) -> ValidationError:
        """Convert validation exceptions to custom exceptions.

        Args:
            exception: The original validation exception
            field: Field that failed validation
            operation: Operation being performed

        Returns:
            ValidationError with appropriate context
        """
        context = create_validation_context(field or "unknown", operation=operation)
        return ValidationError(str(exception), context=context, cause=exception)


def handle_error(
    error: Exception,
    operation: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
) -> GitHubRepoAnalyzerError:
    """Handle any exception and convert to appropriate custom exception.

    Args:
        error: The exception to handle
        operation: Description of the operation that failed
        logger: Logger instance for error logging

    Returns:
        Appropriate custom exception
    """
    handler = ErrorHandler(logger)

    # If it's already our custom exception, return as-is
    if isinstance(error, GitHubRepoAnalyzerError):
        return error

    # Handle specific exception types
    if hasattr(error, "status"):  # GitHub API exception
        return handler.handle_github_exception(error, operation or "unknown operation")
    elif "timeout" in str(error).lower() or "connection" in str(error).lower():
        return handler.handle_network_exception(error, operation or "network operation")
    elif isinstance(error, ValueError):
        return handler.handle_validation_exception(error, operation=operation)
    else:
        # Generic error handling
        context = ErrorContext(operation=operation)
        return GitHubRepoAnalyzerError(
            f"Unexpected error: {error}", context=context, cause=error
        )


def format_error_message(error: GitHubRepoAnalyzerError) -> str:
    """Format error message for user display.

    Args:
        error: The error to format

    Returns:
        Formatted error message
    """
    if isinstance(error, AuthenticationError):
        return f"Authentication Error: {error.message}"
    elif isinstance(error, RateLimitError):
        return f"Rate Limit Error: {error.message}"
    elif isinstance(error, NotFoundError):
        return f"Not Found Error: {error.message}"
    elif isinstance(error, NetworkError):
        return f"Network Error: {error.message}"
    elif isinstance(error, ValidationError):
        if error.context.field:
            return f"Validation Error ({error.context.field}): {error.message}"
        return f"Validation Error: {error.message}"
    elif isinstance(error, ConfigurationError):
        return f"Configuration Error: {error.message}"
    elif isinstance(error, APIError):
        return f"API Error: {error.message}"
    elif isinstance(error, CacheError):
        return f"Cache Error: {error.message}"
    else:
        return f"Error: {error.message}"


def get_error_tip(error: GitHubRepoAnalyzerError) -> Optional[str]:
    """Get helpful tip for resolving the error.

    Args:
        error: The error to get tip for

    Returns:
        Helpful tip string or None
    """
    if isinstance(error, AuthenticationError):
        return "Tip: Set GITHUB_TOKEN environment variable or use --token option"
    elif isinstance(error, RateLimitError):
        return (
            "Tip: Wait a few minutes before trying again, or use a personal "
            "access token for higher limits"
        )
    elif isinstance(error, NotFoundError):
        return "Tip: Check the username or organization name is correct"
    elif isinstance(error, NetworkError):
        return "Tip: Check your internet connection and try again"
    elif isinstance(error, ValidationError):
        if error.context.field:
            return f"Tip: Check the {error.context.field} value is valid"
        return "Tip: Check your input values are valid"
    elif isinstance(error, ConfigurationError):
        return "Tip: Check your configuration settings"
    elif isinstance(error, APIError):
        return "Tip: Check the GitHub API status and try again later"
    elif isinstance(error, CacheError):
        return "Tip: Try clearing the cache with --no-cache option"

    return None


def log_error_with_context(
    logger: logging.Logger, error: Exception, context: str = ""
) -> None:
    """Log error with additional context.

    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context information
    """
    context_msg = f" in {context}" if context else ""

    if isinstance(error, GitHubRepoAnalyzerError):
        logger.error(
            "Error%s: %s: %s", context_msg, type(error).__name__, error.message
        )

        # Log context information if available
        if error.context and error.context.to_dict():
            logger.debug("Error context%s: %s", context_msg, error.context.to_dict())
    else:
        logger.error("Error%s: %s: %s", context_msg, type(error).__name__, error)

    # Log full traceback for debugging
    logger.debug("Full traceback%s:", context_msg, exc_info=True)


def error_handler(
    operation: str, reraise: bool = True
) -> Callable[[Callable], Callable]:
    """Decorator for automatic error handling.

    Args:
        operation: Description of the operation
        reraise: Whether to reraise the converted exception

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                converted_error = handle_error(e, operation)
                if reraise:
                    raise converted_error
                return converted_error

        return wrapper

    return decorator
