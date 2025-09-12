"""Centralized error handling for GitHub Repository Analyzer.

This module provides a comprehensive error handling system with:
- Custom exception hierarchy
- Error context and formatting
- Consistent error processing
- Integration with logging
"""

from .context import (
    ErrorContext,
    create_api_context,
    create_network_context,
    create_validation_context,
)
from .exceptions import (
    APIError,
    AuthenticationError,
    CacheError,
    ConfigurationError,
    GitHubRepoAnalyzerError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .handlers import (
    ErrorHandler,
    error_handler,
    format_error_message,
    get_error_tip,
    handle_error,
    log_error_with_context,
)
from .migration import (
    convert_config_error,
    convert_github_exception,
    convert_network_exception,
    convert_value_error,
    create_legacy_validation_error,
)

__all__ = [
    # Exceptions
    "APIError",
    "AuthenticationError",
    "CacheError",
    "ConfigurationError",
    "GitHubRepoAnalyzerError",
    "NetworkError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    # Handlers
    "ErrorHandler",
    "error_handler",
    "format_error_message",
    "get_error_tip",
    "handle_error",
    "log_error_with_context",
    # Context
    "ErrorContext",
    "create_api_context",
    "create_network_context",
    "create_validation_context",
    # Migration
    "convert_config_error",
    "convert_github_exception",
    "convert_network_exception",
    "convert_value_error",
    "create_legacy_validation_error",
]
