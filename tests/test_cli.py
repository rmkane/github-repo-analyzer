"""Integration tests for the CLI commands."""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestCLIIntegration:
    """Integration tests for CLI commands."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def github_token(self):
        """Get GitHub token from environment or skip test."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            pytest.skip("GITHUB_TOKEN not set - skipping integration test")
        return token

    def test_analyze_command_help(self):
        """Test that the analyze command shows help."""
        result = subprocess.run(
            ["github-repo-analyzer", "analyze", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Analyze repositories for a GitHub user or organization" in result.stdout

    def test_search_command_help(self):
        """Test that the search command shows help."""
        result = subprocess.run(
            ["github-repo-analyzer", "search", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Search and filter repositories" in result.stdout

    def test_analyze_command_with_limit(self, github_token, temp_output_dir):
        """Test analyze command with limit and JSON output."""
        result = subprocess.run(
            [
                "github-repo-analyzer",
                "analyze",
                "octocat",  # Use a known public user
                "--limit",
                "3",
                "--output",
                "json",
                "--token",
                github_token,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Fetching repositories for user: octocat" in result.stderr

        # Parse JSON output
        repos_data = json.loads(result.stdout)
        assert isinstance(repos_data, list)
        assert len(repos_data) <= 3

        # Check structure of first repo
        if repos_data:
            repo = repos_data[0]
            assert "name" in repo
            assert "full_name" in repo
            assert "language" in repo
            assert "stargazers_count" in repo

    def test_search_command_with_filters(self, github_token):
        """Test search command with filters."""
        result = subprocess.run(
            [
                "github-repo-analyzer",
                "search",
                "octocat",
                "--language",
                "Python",
                "--limit",
                "2",
                "--token",
                github_token,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Searching repositories for user: octocat" in result.stderr
        assert (
            "Found" in result.stderr
            and "repositories matching criteria" in result.stderr
        )

    def test_verbose_option(self, github_token):
        """Test verbose logging option."""
        result = subprocess.run(
            [
                "github-repo-analyzer",
                "--verbose",
                "analyze",
                "octocat",
                "--limit",
                "1",
                "--token",
                github_token,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Verbose mode should show more detailed logging
        assert "Fetching repositories for user: octocat" in result.stderr

    def test_quiet_option(self, github_token):
        """Test quiet logging option."""
        result = subprocess.run(
            [
                "github-repo-analyzer",
                "--quiet",
                "analyze",
                "octocat",
                "--limit",
                "1",
                "--output",
                "json",
                "--token",
                github_token,
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Quiet mode should suppress most logging
        assert result.stderr.strip() == ""

    def test_invalid_token(self):
        """Test behavior with invalid token."""
        result = subprocess.run(
            [
                "github-repo-analyzer",
                "analyze",
                "octocat",
                "--token",
                "invalid_token",
                "--no-cache",  # Disable caching to ensure we test the actual API call
            ],
            capture_output=True,
            text=True,
        )

        # Should fail gracefully
        assert result.returncode != 0
        assert "Error:" in result.stdout or "error" in result.stdout.lower()

    def test_missing_token(self):
        """Test behavior when no token is provided."""
        # Clear environment variables
        env = os.environ.copy()
        if "GITHUB_TOKEN" in env:
            del env["GITHUB_TOKEN"]

        result = subprocess.run(
            ["github-repo-analyzer", "analyze", "octocat"],
            capture_output=True,
            text=True,
            env=env,
        )

        # Should fail with helpful error message
        assert result.returncode != 0
        assert (
            "GitHub token is required" in result.stdout
            or "GITHUB_TOKEN" in result.stdout
        )
