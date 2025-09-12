"""Service layer for GitHub Repository Analyzer."""

import logging
from typing import Any, Dict, List, Optional

from .api import GitHubAPI
from .models import Repository

logger = logging.getLogger(__name__)


class RepositoryService:
    """Service for repository analysis operations."""

    def __init__(self, api: GitHubAPI):
        """Initialize the repository service.

        Args:
            api: GitHub API client instance
        """
        self.api = api

    def analyze_repositories(
        self,
        username_or_org: str,
        is_organization: bool = False,
        limit: int = 100,
        sort_field: str = "updated",
    ) -> Dict[str, Any]:
        """Analyze repositories for a user or organization.

        Args:
            username_or_org: GitHub username or organization name
            is_organization: Whether the target is an organization
            limit: Maximum number of repositories to fetch
            sort_field: Field to sort repositories by

        Returns:
            Dictionary containing repository statistics and sorted repositories
        """
        # Get repository statistics
        stats = self.api.get_repo_stats(
            username_or_org, is_organization=is_organization, limit=limit
        )

        if not stats:
            return {}

        # Sort repositories
        repos = stats["repositories"]
        sorted_repos = self._sort_repositories(repos, sort_field)

        # Update stats with sorted repositories
        stats["repositories"] = sorted_repos
        return stats

    def search_repositories(
        self,
        username_or_org: str,
        is_organization: bool = False,
        language: Optional[str] = None,
        min_stars: Optional[int] = None,
        min_forks: Optional[int] = None,
        public_only: bool = False,
        private_only: bool = False,
        limit: int = 100,
        sort_field: str = "updated",
    ) -> List[Repository]:
        """Search and filter repositories.

        Args:
            username_or_org: GitHub username or organization name
            is_organization: Whether the target is an organization
            language: Filter by programming language
            min_stars: Minimum number of stars
            min_forks: Minimum number of forks
            public_only: Show only public repositories
            private_only: Show only private repositories
            limit: Maximum number of repositories to fetch
            sort_field: Field to sort repositories by

        Returns:
            List of filtered and sorted repositories
        """
        # Get all repositories
        stats = self.api.get_repo_stats(
            username_or_org, is_organization=is_organization, limit=limit
        )

        if not stats:
            return []

        repos = stats["repositories"]

        # Apply filters
        filtered_repos = self._apply_filters(
            repos, language, min_stars, min_forks, public_only, private_only
        )

        # Sort repositories
        sorted_repos = self._sort_repositories(filtered_repos, sort_field)

        return sorted_repos

    def _apply_filters(
        self,
        repos: List[Repository],
        language: Optional[str] = None,
        min_stars: Optional[int] = None,
        min_forks: Optional[int] = None,
        public_only: bool = False,
        private_only: bool = False,
    ) -> List[Repository]:
        """Apply filters to repositories.

        Args:
            repos: List of repositories to filter
            language: Filter by programming language
            min_stars: Minimum number of stars
            min_forks: Minimum number of forks
            public_only: Show only public repositories
            private_only: Show only private repositories

        Returns:
            Filtered list of repositories
        """
        filtered_repos = repos

        if language:
            filtered_repos = [
                r
                for r in filtered_repos
                if r.language and r.language.lower() == language.lower()
            ]

        if min_stars is not None:
            filtered_repos = [
                r for r in filtered_repos if r.stargazers_count >= min_stars
            ]

        if min_forks is not None:
            filtered_repos = [r for r in filtered_repos if r.forks_count >= min_forks]

        if public_only:
            filtered_repos = [r for r in filtered_repos if not r.private]

        if private_only:
            filtered_repos = [r for r in filtered_repos if r.private]

        return filtered_repos

    def _sort_repositories(
        self, repos: List[Repository], sort_field: str
    ) -> List[Repository]:
        """Sort repositories by the specified field.

        Args:
            repos: List of Repository objects
            sort_field: Field to sort by (name, stars, forks, updated, created, size)

        Returns:
            Sorted list of repositories
        """
        if not repos:
            return repos

        if sort_field == "name":
            return sorted(repos, key=lambda r: r.name.lower())
        elif sort_field == "stars":
            return sorted(repos, key=lambda r: r.stargazers_count, reverse=True)
        elif sort_field == "forks":
            return sorted(repos, key=lambda r: r.forks_count, reverse=True)
        elif sort_field == "updated":
            return sorted(repos, key=lambda r: r.updated_at or "", reverse=True)
        elif sort_field == "created":
            return sorted(repos, key=lambda r: r.created_at or "", reverse=True)
        elif sort_field == "size":
            return sorted(repos, key=lambda r: r.size, reverse=True)
        else:
            return repos

    def validate_inputs(
        self,
        username_or_org: str,
        limit: Optional[int] = None,
        public_only: bool = False,
        private_only: bool = False,
    ) -> None:
        """Validate input parameters.

        Args:
            username_or_org: Username or organization name
            limit: Limit value
            public_only: Public only flag
            private_only: Private only flag

        Raises:
            ValueError: If validation fails
        """
        if not username_or_org or not username_or_org.strip():
            raise ValueError("Username or organization name cannot be empty")

        if limit is not None and limit < -1:
            raise ValueError("Limit must be -1 (unlimited) or non-negative")

        if public_only and private_only:
            raise ValueError("Cannot specify both --public-only and --private-only")
