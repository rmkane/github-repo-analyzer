"""Tests for utility functions."""

import pytest

from github_repo_analyzer.utils import clamp_limit


class TestClampLimit:
    """Test cases for clamp_limit function."""

    def test_none_returns_default(self):
        """Test that None returns the default value."""
        assert clamp_limit(None) == 100
        assert clamp_limit(None, default=50, maximum=500) == 50

    def test_negative_one_returns_maximum(self):
        """Test that -1 returns the maximum value (unlimited)."""
        assert clamp_limit(-1) == 10000
        assert clamp_limit(-1, default=50, maximum=500) == 500

    def test_positive_value_returns_min_of_value_and_maximum(self):
        """Test that positive values are clamped to maximum."""
        assert clamp_limit(500, default=100, maximum=1000) == 500
        assert clamp_limit(1500, default=100, maximum=1000) == 1000

    def test_zero_returns_zero(self):
        """Test that zero returns zero."""
        assert clamp_limit(0) == 0
        assert clamp_limit(0, default=50, maximum=500) == 0

    def test_negative_value_raises_error(self):
        """Test that negative values (except -1) raise ValueError."""
        with pytest.raises(
            ValueError, match="Limit must be non-negative or -1 for unlimited"
        ):
            clamp_limit(-5)
        with pytest.raises(
            ValueError, match="Limit must be non-negative or -1 for unlimited"
        ):
            clamp_limit(-5, default=50, maximum=500)

    def test_different_limits(self):
        """Test with different default and maximum values."""
        assert clamp_limit(None, default=10, maximum=20) == 10
        assert clamp_limit(-1, default=10, maximum=20) == 20
        assert clamp_limit(15, default=10, maximum=20) == 15
        assert clamp_limit(25, default=10, maximum=20) == 20

    def test_edge_cases(self):
        """Test edge cases."""
        assert clamp_limit(1) == 1
        assert clamp_limit(100) == 100
        assert clamp_limit(10000) == 10000
        assert clamp_limit(10001) == 10000  # Capped at maximum
