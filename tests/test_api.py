"""Tests for the GitHub API client."""

from unittest.mock import Mock, patch

import pytest
import requests

from github_repo_analyzer.api import GitHubAPI
from github_repo_analyzer.models import Repository


class TestGitHubAPI:
    """Test cases for GitHubAPI class."""

    def test_init_with_token(self):
        """Test initialization with token."""
        api = GitHubAPI("test_token", cache_dir=None)  # Disable caching for test
        assert api.token == "test_token"
        assert "Authorization" in api.session.headers
        assert api.session.headers["Authorization"] == "token test_token"

    def test_init_without_token(self):
        """Test initialization without token raises ValueError."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="GitHub token is required"):
                GitHubAPI()

    def test_init_with_env_token(self):
        """Test initialization with token from environment."""
        with patch.dict("os.environ", {"GITHUB_TOKEN": "env_token"}):
            api = GitHubAPI()
            assert api.token == "env_token"

    @patch("github_repo_analyzer.api.requests.Session.get")
    def test_get_user_repos_success(self, mock_get):
        """Test successful user repos retrieval."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "name": "test-repo",
                "full_name": "user/test-repo",
                "description": "Test repository",
                "html_url": "https://github.com/user/test-repo",
                "clone_url": "https://github.com/user/test-repo.git",
                "ssh_url": "git@github.com:user/test-repo.git",
                "language": "Python",
                "stargazers_count": 10,
                "forks_count": 5,
                "open_issues_count": 2,
                "size": 1024,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-02T00:00:00Z",
                "pushed_at": "2023-01-02T00:00:00Z",
                "private": False,
                "archived": False,
                "disabled": False,
                "topics": ["python", "test"],
                "license": None,
                "owner": {"login": "user"},
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = GitHubAPI("test_token", cache_dir=None)  # Disable caching for test
        repos = api.get_user_repos("testuser")

        assert len(repos) == 1
        assert isinstance(repos[0], Repository)
        assert repos[0].name == "test-repo"
        assert repos[0].language == "Python"

    @patch("github_repo_analyzer.api.requests.Session.get")
    def test_get_user_repos_error(self, mock_get):
        """Test user repos retrieval with error."""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        api = GitHubAPI("test_token", cache_dir=None)  # Disable caching for test
        repos = api.get_user_repos("testuser")

        assert repos == []

    @patch("github_repo_analyzer.api.requests.Session.get")
    def test_get_org_repos_success(self, mock_get):
        """Test successful organization repos retrieval."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "name": "org-repo",
                "full_name": "org/org-repo",
                "description": "Organization repository",
                "html_url": "https://github.com/org/org-repo",
                "clone_url": "https://github.com/org/org-repo.git",
                "ssh_url": "git@github.com:org/org-repo.git",
                "language": "JavaScript",
                "stargazers_count": 20,
                "forks_count": 10,
                "open_issues_count": 1,
                "size": 2048,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-02T00:00:00Z",
                "pushed_at": "2023-01-02T00:00:00Z",
                "private": False,
                "archived": False,
                "disabled": False,
                "topics": ["javascript", "org"],
                "license": None,
                "owner": {"login": "org"},
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = GitHubAPI("test_token", cache_dir=None)  # Disable caching for test
        repos = api.get_org_repos("testorg")

        assert len(repos) == 1
        assert isinstance(repos[0], Repository)
        assert repos[0].name == "org-repo"
        assert repos[0].language == "JavaScript"


class TestRepository:
    """Test cases for Repository model."""

    def test_repository_creation(self):
        """Test Repository model creation."""
        repo_data = {
            "name": "test-repo",
            "full_name": "user/test-repo",
            "description": "Test repository",
            "html_url": "https://github.com/user/test-repo",
            "clone_url": "https://github.com/user/test-repo.git",
            "ssh_url": "git@github.com:user/test-repo.git",
            "language": "Python",
            "stargazers_count": 10,
            "forks_count": 5,
            "open_issues_count": 2,
            "size": 1024,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z",
            "pushed_at": "2023-01-02T00:00:00Z",
            "private": False,
            "archived": False,
            "disabled": False,
            "topics": ["python", "test"],
            "license": None,
            "owner": {"login": "user"},
        }

        repo = Repository(**repo_data)

        assert repo.name == "test-repo"
        assert repo.full_name == "user/test-repo"
        assert repo.language == "Python"
        assert repo.stargazers_count == 10
        assert repo.forks_count == 5
        assert repo.private is False
        assert repo.archived is False
        assert "python" in repo.topics
