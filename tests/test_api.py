"""Tests for the GitHub API client."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from github_repo_analyzer.api import GitHubAPI
from github_repo_analyzer.models import Owner, Repository


class TestGitHubAPI:
    """Test cases for GitHubAPI class."""

    def test_init_with_token(self):
        """Test initialization with token."""
        api = GitHubAPI("test_token", cache_dir=None)  # Disable caching for test
        assert api.token == "test_token"
        assert api.github is not None

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

    @patch("github_repo_analyzer.api.Github")
    def test_get_user_repos_success(self, mock_github_class):
        """Test successful user repos retrieval."""
        # Mock PyGithub objects
        mock_github = Mock()
        mock_user = Mock()
        mock_repo = Mock()

        # Configure mock repo attributes
        mock_repo.name = "test-repo"
        mock_repo.full_name = "user/test-repo"
        mock_repo.description = "Test repository"
        mock_repo.html_url = "https://github.com/user/test-repo"
        mock_repo.clone_url = "https://github.com/user/test-repo.git"
        mock_repo.ssh_url = "git@github.com:user/test-repo.git"
        mock_repo.language = "Python"
        mock_repo.stargazers_count = 10
        mock_repo.forks_count = 5
        mock_repo.open_issues_count = 2
        mock_repo.size = 1024
        mock_repo.created_at = datetime(2023, 1, 1, 0, 0, 0)
        mock_repo.updated_at = datetime(2023, 1, 2, 0, 0, 0)
        mock_repo.pushed_at = datetime(2023, 1, 2, 0, 0, 0)
        mock_repo.private = False
        mock_repo.archived = False
        mock_repo.disabled = False
        mock_repo.get_topics.return_value = ["python", "test"]
        mock_repo.license = None
        mock_repo.owner = Mock()
        mock_repo.owner.login = "user"
        mock_repo.owner.id = 12345
        mock_repo.owner.type = "User"
        mock_repo.owner.html_url = "https://github.com/user"
        mock_repo.owner.avatar_url = "https://avatars.githubusercontent.com/u/12345?v=4"

        # Configure mock user and github
        mock_user.get_repos.return_value = [mock_repo]
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github

        api = GitHubAPI("test_token", cache_dir=None)  # Disable caching for test
        repos = api.get_user_repos("testuser")

        assert len(repos) == 1
        assert isinstance(repos[0], Repository)
        assert repos[0].name == "test-repo"
        assert repos[0].language == "Python"

    @patch("github_repo_analyzer.api.Github")
    def test_get_user_repos_error(self, mock_github_class):
        """Test user repos retrieval with error."""
        from github.GithubException import GithubException

        mock_github = Mock()
        mock_github.get_user.side_effect = GithubException(500, "API Error")
        mock_github_class.return_value = mock_github

        api = GitHubAPI("test_token", cache_dir=None)  # Disable caching for test
        repos = api.get_user_repos("testuser")

        assert repos == []

    @patch("github_repo_analyzer.api.Github")
    def test_get_org_repos_success(self, mock_github_class):
        """Test successful organization repos retrieval."""
        # Mock PyGithub objects
        mock_github = Mock()
        mock_org = Mock()
        mock_repo = Mock()

        # Configure mock repo attributes
        mock_repo.name = "org-repo"
        mock_repo.full_name = "org/org-repo"
        mock_repo.description = "Organization repository"
        mock_repo.html_url = "https://github.com/org/org-repo"
        mock_repo.clone_url = "https://github.com/org/org-repo.git"
        mock_repo.ssh_url = "git@github.com:org/org-repo.git"
        mock_repo.language = "JavaScript"
        mock_repo.stargazers_count = 20
        mock_repo.forks_count = 10
        mock_repo.open_issues_count = 1
        mock_repo.size = 2048
        mock_repo.created_at = datetime(2023, 1, 1, 0, 0, 0)
        mock_repo.updated_at = datetime(2023, 1, 2, 0, 0, 0)
        mock_repo.pushed_at = datetime(2023, 1, 2, 0, 0, 0)
        mock_repo.private = False
        mock_repo.archived = False
        mock_repo.disabled = False
        mock_repo.get_topics.return_value = ["javascript", "org"]
        mock_repo.license = None
        mock_repo.owner = Mock()
        mock_repo.owner.login = "org"
        mock_repo.owner.id = 67890
        mock_repo.owner.type = "Organization"
        mock_repo.owner.html_url = "https://github.com/org"
        mock_repo.owner.avatar_url = "https://avatars.githubusercontent.com/u/67890?v=4"

        # Configure mock org and github
        mock_org.get_repos.return_value = [mock_repo]
        mock_github.get_organization.return_value = mock_org
        mock_github_class.return_value = mock_github

        api = GitHubAPI("test_token", cache_dir=None)  # Disable caching for test
        repos = api.get_org_repos("testorg")

        assert len(repos) == 1
        assert isinstance(repos[0], Repository)
        assert repos[0].name == "org-repo"
        assert repos[0].language == "JavaScript"


class TestRepository:
    """Test cases for Repository model."""

    def test_repository_creation(self):
        """Test Repository creation from dictionary."""
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
            "owner": {
                "login": "user",
                "id": 12345,
                "type": "User",
                "html_url": "https://github.com/user",
                "avatar_url": "https://avatars.githubusercontent.com/u/12345?v=4",
            },
        }

        # Create Repository from dictionary
        repo = Repository.model_validate(repo_data)

        # Test attributes
        assert repo.name == "test-repo"
        assert repo.full_name == "user/test-repo"
        assert repo.language == "Python"
        assert repo.stargazers_count == 10
        assert repo.forks_count == 5
        assert repo.private is False
        assert repo.archived is False
        assert "python" in repo.topics

    def test_repository_to_dict(self):
        """Test Repository to_dict method."""
        repo = Repository(
            name="test-repo",
            full_name="user/test-repo",
            description="Test repository",
            html_url="https://github.com/user/test-repo",
            clone_url="https://github.com/user/test-repo.git",
            ssh_url="git@github.com:user/test-repo.git",
            language="Python",
            stargazers_count=10,
            forks_count=5,
            open_issues_count=2,
            size=1024,
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-02T00:00:00Z",
            pushed_at="2023-01-02T00:00:00Z",
            private=False,
            archived=False,
            disabled=False,
            topics=["python", "test"],
            license=None,
            owner=Owner(
                login="user",
                id=12345,
                type="User",
                html_url="https://github.com/user",
                avatar_url="https://avatars.githubusercontent.com/u/12345?v=4",
            ),
        )

        repo_dict = repo.to_dict()

        assert repo_dict["name"] == "test-repo"
        assert repo_dict["language"] == "Python"
        assert repo_dict["stargazers_count"] == 10
        assert repo_dict["private"] is False
