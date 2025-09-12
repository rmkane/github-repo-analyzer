"""Custom exception hierarchy for GitHub Repository Analyzer.

This module defines a comprehensive exception hierarchy that provides
clear error categorization and context for different types of failures.
"""

from typing import Any, Optional

from github_repo_analyzer.errors.context import ErrorContext


class GitHubRepoAnalyzerError(Exception):
    """Base exception for all GitHub Repository Analyzer errors.

    This is the root exception class that all other custom exceptions
    inherit from, providing a common interface for error handling.
    """

    def __init__(
        self,
        message: str,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize the error.

        Args:
            message: Human-readable error message
            context: Additional context about the error
            cause: The underlying exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.context = context or ErrorContext()
        self.cause = cause

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.context.operation:
            return f"{self.context.operation}: {self.message}"
        return self.message


class AuthenticationError(GitHubRepoAnalyzerError):
    """Raised when authentication fails or token is invalid."""

    def __init__(
        self,
        message: str = "Authentication failed",
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, context, cause)


class RateLimitError(GitHubRepoAnalyzerError):
    """Raised when GitHub API rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, context, cause)


class NotFoundError(GitHubRepoAnalyzerError):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, context, cause)


class NetworkError(GitHubRepoAnalyzerError):
    """Raised when network-related errors occur."""

    def __init__(
        self,
        message: str = "Network error occurred",
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, context, cause)


class ValidationError(GitHubRepoAnalyzerError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        if context is None:
            context = ErrorContext(field=field, value=value)
        elif field is not None:
            context.field = field
        if value is not None:
            context.value = value
        super().__init__(message, context, cause)


class ConfigurationError(GitHubRepoAnalyzerError):
    """Raised when configuration is invalid or missing."""

    def __init__(
        self,
        message: str = "Configuration error",
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, context, cause)


class APIError(GitHubRepoAnalyzerError):
    """Raised when GitHub API returns an error."""

    def __init__(
        self,
        message: str = "API error occurred",
        status_code: Optional[int] = None,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        if context is None:
            context = ErrorContext(status_code=status_code)
        elif status_code is not None:
            context.status_code = status_code
        super().__init__(message, context, cause)


class CacheError(GitHubRepoAnalyzerError):
    """Raised when cache operations fail."""

    def __init__(
        self,
        message: str = "Cache error occurred",
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, context, cause)
