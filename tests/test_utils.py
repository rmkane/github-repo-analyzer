"""Tests for utility functions."""

import pytest

from github_repo_analyzer.utils import clamp_limit, clamp_value


class TestClampValue:
    """Test cases for clamp_value function."""

    def test_none_returns_default(self):
        """Test that None returns default value."""
        assert clamp_value(None, default=50, maximum=100) == 50

    def test_negative_one_returns_maximum(self):
        """Test that -1 returns maximum (unlimited)."""
        assert clamp_value(-1, default=50, maximum=100) == 100

    def test_positive_value_returns_min_of_value_and_maximum(self):
        """Test that positive values are capped at maximum."""
        assert clamp_value(75, default=50, maximum=100) == 75
        assert clamp_value(150, default=50, maximum=100) == 100

    def test_zero_returns_zero(self):
        """Test that zero returns zero."""
        assert clamp_value(0, default=50, maximum=100) == 0

    def test_negative_value_raises_error(self):
        """Test that negative values (except -1) raise ValueError."""
        with pytest.raises(
            ValueError, match="Limit must be non-negative or -1 for unlimited"
        ):
            clamp_value(-5, default=50, maximum=100)

    def test_different_limits(self):
        """Test with different default and maximum values."""
        assert clamp_value(None, default=10, maximum=20) == 10
        assert clamp_value(-1, default=10, maximum=20) == 20
        assert clamp_value(15, default=10, maximum=20) == 15
        assert clamp_value(25, default=10, maximum=20) == 20


class TestClampLimit:
    """Test cases for clamp_limit function."""

    def test_none_returns_default(self):
        """Test that None returns default GitHub API limit."""
        assert clamp_limit(None) == 100

    def test_negative_one_returns_unlimited(self):
        """Test that -1 returns unlimited value."""
        assert clamp_limit(-1) == 10000

    def test_zero_returns_zero(self):
        """Test that zero returns zero."""
        assert clamp_limit(0) == 0

    def test_positive_value_returns_as_is(self):
        """Test that positive values return as-is."""
        assert clamp_limit(50) == 50
        assert clamp_limit(500) == 500

    def test_large_value_capped_at_hard_limit(self):
        """Test that large values are capped at hard limit."""
        assert clamp_limit(15000) == 10000

    def test_negative_value_raises_error(self):
        """Test that negative values (except -1) raise ValueError."""
        with pytest.raises(
            ValueError, match="Limit must be non-negative or -1 for unlimited"
        ):
            clamp_limit(-5)

    def test_edge_cases(self):
        """Test edge cases."""
        assert clamp_limit(1) == 1
        assert clamp_limit(100) == 100
        assert clamp_limit(10000) == 10000
