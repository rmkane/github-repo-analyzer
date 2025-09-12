"""Utility functions for GitHub Repository Analyzer."""

from typing import Optional


def clamp_value(value: Optional[int], default: int, maximum: int) -> int:
    """Clamp a value between default and maximum limits.

    Args:
        value: Value to clamp (None means use default)
        default: Default value when input is None
        maximum: Maximum allowed value

    Returns:
        Clamped value between default and maximum

    Raises:
        ValueError: If value is negative (except -1 for unlimited)
    """
    if value is None:
        return default
    elif value == -1:
        return maximum  # Unlimited
    elif value < 0:
        raise ValueError("Limit must be non-negative or -1 for unlimited")
    else:
        return min(value, maximum)


def clamp_limit(limit: Optional[int]) -> int:
    """Clamp repository limit to valid range.

    Args:
        limit: Limit value to clamp

    Returns:
        Clamped limit value:
        - None -> 100 (default GitHub API max per page)
        - -1 -> 10000 (unlimited)
        - 0 -> 0 (zero)
        - positive -> as-is (capped at 10000)

    Raises:
        ValueError: If limit is negative (except -1)
    """
    return clamp_value(limit, default=100, maximum=10000)
