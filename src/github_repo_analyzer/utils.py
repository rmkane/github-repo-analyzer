"""Utility functions for GitHub Repository Analyzer."""

from typing import Optional


def clamp_limit(limit: Optional[int], default: int = 100, maximum: int = 10000) -> int:
    """Clamp a limit value between default and maximum limits.

    Args:
        limit: Limit value to clamp (None means use default)
        default: Default value when input is None
        maximum: Maximum allowed value

    Returns:
        Clamped limit value:
        - None -> default (default GitHub API max per page)
        - -1 -> maximum (unlimited)
        - 0 -> 0 (zero)
        - positive -> as-is (capped at maximum)

    Raises:
        ValueError: If limit is negative (except -1 for unlimited)
    """
    if limit is None:
        return default
    elif limit == -1:
        return maximum  # Unlimited
    elif limit < 0:
        raise ValueError("Limit must be non-negative or -1 for unlimited")
    else:
        return min(limit, maximum)
