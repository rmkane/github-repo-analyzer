"""Tests for centralized error handling system."""

from unittest.mock import MagicMock

import requests.exceptions

from github_repo_analyzer.errors import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    ErrorContext,
    ErrorHandler,
    GitHubRepoAnalyzerError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    convert_config_error,
    convert_github_exception,
    convert_network_exception,
    convert_value_error,
    create_legacy_validation_error,
    format_error_message,
    get_error_tip,
    handle_error,
)


class TestErrorContext:
    """Test cases for ErrorContext class."""

    def test_error_context_creation(self):
        """Test creating ErrorContext with various parameters."""
        context = ErrorContext(
            operation="test_operation",
            field="test_field",
            value="test_value",
            status_code=404,
            retry_after=60,
            additional_info={"key": "value"},
        )

        assert context.operation == "test_operation"
        assert context.field == "test_field"
        assert context.value == "test_value"
        assert context.status_code == 404
        assert context.retry_after == 60
        assert context.additional_info == {"key": "value"}

    def test_error_context_to_dict(self):
        """Test converting ErrorContext to dictionary."""
        context = ErrorContext(
            operation="test_operation", field="test_field", status_code=404
        )

        result = context.to_dict()
        expected = {
            "operation": "test_operation",
            "field": "test_field",
            "status_code": "404",
        }
        assert result == expected

    def test_error_context_add_info(self):
        """Test adding additional information to context."""
        context = ErrorContext()
        context.add_info("new_key", "new_value")

        assert context.additional_info == {"new_key": "new_value"}

    def test_error_context_has_retry_info(self):
        """Test checking if context has retry information."""
        context_with_retry = ErrorContext(retry_after=60)
        context_without_retry = ErrorContext()

        assert context_with_retry.has_retry_info() is True
        assert context_without_retry.has_retry_info() is False

    def test_error_context_get_retry_delay(self):
        """Test getting retry delay from context."""
        context = ErrorContext(retry_after=120)
        assert context.get_retry_delay() == 120


class TestCustomExceptions:
    """Test cases for custom exception classes."""

    def test_github_repo_analyzer_error(self):
        """Test base exception class."""
        context = ErrorContext(operation="test")
        error = GitHubRepoAnalyzerError("Test message", context=context)

        assert str(error) == "test: Test message"
        assert error.message == "Test message"
        assert error.context == context

    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("Invalid token")
        assert isinstance(error, GitHubRepoAnalyzerError)
        assert error.message == "Invalid token"

    def test_rate_limit_error(self):
        """Test RateLimitError."""
        context = ErrorContext(retry_after=60)
        error = RateLimitError("Rate limit exceeded", context=context)
        assert isinstance(error, GitHubRepoAnalyzerError)
        assert error.context.retry_after == 60

    def test_validation_error_with_field(self):
        """Test ValidationError with field context."""
        error = ValidationError("Invalid value", field="username")
        assert error.context.field == "username"

    def test_api_error_with_status_code(self):
        """Test APIError with status code."""
        context = ErrorContext(status_code=500)
        error = APIError("Server error", context=context)
        assert error.context.status_code == 500


class TestErrorHandler:
    """Test cases for ErrorHandler class."""

    def test_handle_github_exception_401(self):
        """Test handling 401 GitHub exception."""
        handler = ErrorHandler()
        exception = MagicMock()
        exception.status = 401

        result = handler.handle_github_exception(exception, "test_operation")

        assert isinstance(result, AuthenticationError)
        assert "Invalid GitHub token" in result.message

    def test_handle_github_exception_403_rate_limit(self):
        """Test handling 403 rate limit exception."""
        handler = ErrorHandler()
        exception = MagicMock()
        exception.status = 403
        exception.__str__ = MagicMock(return_value="rate limit exceeded")

        result = handler.handle_github_exception(exception, "test_operation")

        assert isinstance(result, RateLimitError)
        assert "rate limit exceeded" in result.message

    def test_handle_github_exception_404(self):
        """Test handling 404 GitHub exception."""
        handler = ErrorHandler()
        exception = MagicMock()
        exception.status = 404

        result = handler.handle_github_exception(exception, "test_operation")

        assert isinstance(result, NotFoundError)
        assert "not found" in result.message

    def test_handle_network_exception_timeout(self):
        """Test handling network timeout exception."""
        handler = ErrorHandler()
        exception = Exception("timeout occurred")

        result = handler.handle_network_exception(exception, "test_operation")

        assert isinstance(result, NetworkError)
        assert "timeout" in result.message

    def test_handle_validation_exception(self):
        """Test handling validation exception."""
        handler = ErrorHandler()
        exception = ValueError("Invalid input")

        result = handler.handle_validation_exception(
            exception, field="username", operation="validation"
        )

        assert isinstance(result, ValidationError)
        assert result.context.field == "username"
        assert result.context.operation == "validation"


class TestErrorHandlingFunctions:
    """Test cases for error handling utility functions."""

    def test_handle_error_custom_exception(self):
        """Test handle_error with custom exception."""
        error = AuthenticationError("Test error")
        result = handle_error(error)

        assert result is error  # Should return as-is

    def test_handle_error_value_error(self):
        """Test handle_error with ValueError."""
        error = ValueError("Invalid input")
        result = handle_error(error, "test_operation")

        assert isinstance(result, ValidationError)

    def test_format_error_message_authentication(self):
        """Test formatting authentication error message."""
        error = AuthenticationError("Invalid token")
        result = format_error_message(error)

        assert result == "Authentication Error: Invalid token"

    def test_format_error_message_validation_with_field(self):
        """Test formatting validation error message with field."""
        error = ValidationError("Invalid value", field="username")
        result = format_error_message(error)

        assert result == "Validation Error (username): Invalid value"

    def test_get_error_tip_authentication(self):
        """Test getting tip for authentication error."""
        error = AuthenticationError("Invalid token")
        tip = get_error_tip(error)

        assert "GITHUB_TOKEN" in tip
        assert "--token option" in tip

    def test_get_error_tip_rate_limit(self):
        """Test getting tip for rate limit error."""
        error = RateLimitError("Rate limit exceeded")
        tip = get_error_tip(error)

        assert "personal access token" in tip

    def test_get_error_tip_validation(self):
        """Test getting tip for validation error."""
        error = ValidationError("Invalid value", field="username")
        tip = get_error_tip(error)

        assert "username" in tip


class TestMigrationFunctions:
    """Test cases for migration utility functions."""

    def test_convert_github_exception_401(self):
        """Test converting 401 GitHub exception."""
        exception = MagicMock()
        exception.status = 401

        result = convert_github_exception(exception, "test_operation")

        assert isinstance(result, AuthenticationError)
        assert result.context.status_code == 401

    def test_convert_network_exception_timeout(self):
        """Test converting network timeout exception."""
        exception = requests.exceptions.Timeout("Request timeout")

        result = convert_network_exception(exception, "test_operation")

        assert isinstance(result, NetworkError)
        assert "timeout" in result.message

    def test_convert_value_error(self):
        """Test converting ValueError."""
        exception = ValueError("Invalid input")

        result = convert_value_error(exception, field="username")

        assert isinstance(result, ValidationError)
        assert result.context.field == "username"

    def test_convert_config_error(self):
        """Test converting configuration error."""
        exception = ValueError("Invalid config")

        result = convert_config_error(exception, "test_config")

        assert isinstance(result, ConfigurationError)
        assert result.context.operation == "test_config"

    def test_create_legacy_validation_error(self):
        """Test creating legacy validation error."""
        result = create_legacy_validation_error("Invalid value", "username")

        assert isinstance(result, ValidationError)
        assert result.context.field == "username"
        assert result.message == "Invalid value"


class TestErrorIntegration:
    """Integration tests for error handling system."""

    def test_error_handling_workflow(self):
        """Test complete error handling workflow."""
        # Simulate a GitHub API error
        github_exception = MagicMock()
        github_exception.status = 403
        github_exception.__str__ = MagicMock(return_value="rate limit exceeded")

        # Convert to custom exception
        custom_error = convert_github_exception(github_exception, "get_repos")

        # Format for display
        error_msg = format_error_message(custom_error)
        tip = get_error_tip(custom_error)

        # Verify results
        assert isinstance(custom_error, RateLimitError)
        assert "Rate Limit Error" in error_msg
        assert "personal access token" in tip
        assert custom_error.context.operation == "get_repos"

    def test_error_context_preservation(self):
        """Test that error context is preserved through conversion."""
        original_error = ValueError("Original error")

        # Convert with context
        converted_error = convert_value_error(
            original_error, field="test_field", operation="test_operation"
        )

        # Verify context is preserved
        assert converted_error.context.field == "test_field"
        assert converted_error.context.operation == "test_operation"
        assert converted_error.cause is original_error
