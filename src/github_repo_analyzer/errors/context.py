"""Error context utilities for GitHub Repository Analyzer.

This module provides utilities for creating and managing error context
information that helps with debugging and user experience.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ErrorContext:
    """Context information for an error.

    This class provides structured context information that can be
    attached to errors to help with debugging and user experience.
    """

    operation: Optional[str] = None
    field: Optional[str] = None
    value: Optional[Any] = None
    status_code: Optional[int] = None
    retry_after: Optional[int] = None
    additional_info: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for logging."""
        result = {}

        if self.operation:
            result["operation"] = self.operation
        if self.field:
            result["field"] = self.field
        if self.value is not None:
            result["value"] = self.value
        if self.status_code is not None:
            result["status_code"] = str(self.status_code)
        if self.retry_after is not None:
            result["retry_after"] = str(self.retry_after)
        if self.additional_info:
            result["additional_info"] = str(self.additional_info)

        return result

    def add_info(self, key: str, value: Any) -> None:
        """Add additional information to the context.

        Args:
            key: Information key
            value: Information value
        """
        if self.additional_info is None:
            self.additional_info = {}
        self.additional_info[key] = value

    def has_retry_info(self) -> bool:
        """Check if context contains retry information."""
        return self.retry_after is not None

    def get_retry_delay(self) -> Optional[int]:
        """Get retry delay in seconds."""
        return self.retry_after


def create_api_context(
    operation: str,
    status_code: Optional[int] = None,
    retry_after: Optional[int] = None,
    **kwargs: Any,
) -> ErrorContext:
    """Create error context for API operations.

    Args:
        operation: Description of the API operation
        status_code: HTTP status code from the API
        retry_after: Retry delay in seconds (for rate limits)
        **kwargs: Additional context information

    Returns:
        ErrorContext instance configured for API operations
    """
    return ErrorContext(
        operation=operation,
        status_code=status_code,
        retry_after=retry_after,
        additional_info=kwargs if kwargs else None,
    )


def create_validation_context(
    field: str,
    value: Optional[Any] = None,
    operation: Optional[str] = None,
    **kwargs: Any,
) -> ErrorContext:
    """Create error context for validation errors.

    Args:
        field: Field name that failed validation
        value: Value that failed validation
        operation: Operation being performed
        **kwargs: Additional context information

    Returns:
        ErrorContext instance configured for validation errors
    """
    return ErrorContext(
        operation=operation,
        field=field,
        value=value,
        additional_info=kwargs if kwargs else None,
    )


def create_network_context(operation: str, **kwargs: Any) -> ErrorContext:
    """Create error context for network operations.

    Args:
        operation: Description of the network operation
        **kwargs: Additional context information

    Returns:
        ErrorContext instance configured for network operations
    """
    return ErrorContext(operation=operation, additional_info=kwargs if kwargs else None)
