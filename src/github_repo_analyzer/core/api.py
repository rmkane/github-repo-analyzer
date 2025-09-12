"""GitHub API client for repository analysis."""

import logging
import os
import time
from typing import Any, Dict, List, Optional

import requests
from github import Auth, Github
from github.GithubException import GithubException

from github_repo_analyzer.core.models import Repository

logger = logging.getLogger(__name__)


# Removed the helper functions - now using Repository.from_pygithub() for DRY approach


class GitHubAPI:
    """GitHub API client using PyGithub."""

    def __init__(
        self,
        token: Optional[str] = None,
        cache_dir: Optional[str] = ".cache",
        cache_ttl: int = 3600,
        timeout: int = 30,
    ):
        """Initialize GitHub API client.

        Args:
            token: GitHub personal access token. If not provided, will try to get
                from GITHUB_TOKEN env var.
            cache_dir: Directory to store cache files (PyGithub handles caching
                internally)
            cache_ttl: Cache time-to-live in seconds (PyGithub handles this internally)
            timeout: Request timeout in seconds
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError(
                "GitHub token is required. Set GITHUB_TOKEN env var or pass "
                "token parameter."
            )

        self.timeout = timeout

        try:
            # PyGithub handles authentication, caching, and rate limiting automatically
            self.github = Github(auth=Auth.Token(self.token), timeout=timeout)
            # Test the connection
            self.github.get_user().login
        except requests.exceptions.Timeout:
            raise ValueError(
                f"Connection to GitHub API timed out after {timeout} seconds"
            )
        except requests.exceptions.ConnectionError:
            raise ValueError(
                "Failed to connect to GitHub API. Check your internet connection."
            )
        except GithubException as e:
            if e.status == 401:
                raise ValueError(
                    "Invalid GitHub token. Please check your token and try again."
                )
            elif e.status == 403:
                raise ValueError(
                    "GitHub API access forbidden. Your token may lack required "
                    "permissions."
                )
            else:
                raise ValueError(f"GitHub API error: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error connecting to GitHub: {e}")

    def _handle_github_exception(self, e: GithubException, operation: str) -> None:
        """Handle GitHub API exceptions with appropriate error messages.

        Args:
            e: The GitHub exception
            operation: Description of the operation that failed
        """
        if e.status == 401:
            raise ValueError(
                "Invalid GitHub token. Please check your token and try again."
            )
        elif e.status == 403:
            if "rate limit" in str(e).lower():
                raise ValueError(
                    "GitHub API rate limit exceeded. Please wait before trying again. "
                    "Consider using a personal access token for higher limits."
                )
            else:
                raise ValueError(
                    "GitHub API access forbidden. Your token may lack required "
                    "permissions."
                )
        elif e.status == 404:
            raise ValueError(
                "GitHub user or organization not found. Please check the name and "
                "try again."
            )
        elif e.status == 422:
            raise ValueError(f"Invalid request: {e}")
        elif e.status == 429:
            raise ValueError(
                "GitHub API rate limit exceeded. Please wait before trying again. "
                "Consider using a personal access token for higher limits."
            )
        else:
            raise ValueError(f"GitHub API error during {operation}: {e}")

    def _retry_on_rate_limit(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """Retry a function call if rate limited.

        Args:
            func: Function to retry
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except GithubException as e:
                if e.status == 429 and attempt < max_retries - 1:
                    # Rate limited, wait and retry
                    wait_time = 2**attempt  # Exponential backoff
                    logger.warning(
                        f"Rate limited, waiting {wait_time} seconds before retry..."
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    raise
            except Exception:
                raise

    def get_user_repos(
        self, username: str, per_page: int = 100, page: int = 1
    ) -> List[Repository]:
        """Get all repositories for a user.

        Args:
            username: GitHub username
            per_page: Number of repositories per page (max 100)
            page: Page number

        Returns:
            List of Repository objects
        """
        if not username or not username.strip():
            raise ValueError("Username cannot be empty")

        try:

            def _get_repos() -> List[Any]:
                user = self.github.get_user(username)
                all_repos = user.get_repos(sort="updated", direction="desc")
                return list(all_repos)

            all_repos = self._retry_on_rate_limit(_get_repos)

            # Manual pagination since PyGithub doesn't support per_page/page directly
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            page_repos = all_repos[start_idx:end_idx]

            return [Repository.from_pygithub(repo) for repo in page_repos]
        except GithubException as e:
            logger.error("Error fetching repositories for %s: %s", username, e)
            self._handle_github_exception(
                e, f"fetching repositories for user {username}"
            )
            return []  # This line will never be reached, but satisfies mypy
        except requests.exceptions.Timeout:
            raise ValueError(
                f"Request timed out while fetching repositories for {username}"
            )
        except requests.exceptions.ConnectionError:
            raise ValueError(
                "Network error while fetching repositories. Check your internet "
                "connection."
            )
        except Exception as e:
            logger.error(
                "Unexpected error fetching repositories for %s: %s", username, e
            )
            raise ValueError(f"Unexpected error fetching repositories: {e}")

    def get_org_repos(
        self, org_name: str, per_page: int = 100, page: int = 1
    ) -> List[Repository]:
        """Get all repositories for an organization.

        Args:
            org_name: GitHub organization name
            per_page: Number of repositories per page (max 100)
            page: Page number

        Returns:
            List of Repository objects
        """
        if not org_name or not org_name.strip():
            raise ValueError("Organization name cannot be empty")

        try:

            def _get_org_repos() -> List[Any]:
                org = self.github.get_organization(org_name)
                all_repos = org.get_repos(sort="updated", direction="desc")
                return list(all_repos)

            all_repos = self._retry_on_rate_limit(_get_org_repos)

            # Manual pagination since PyGithub doesn't support per_page/page directly
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            page_repos = all_repos[start_idx:end_idx]

            return [Repository.from_pygithub(repo) for repo in page_repos]
        except GithubException as e:
            logger.error(
                "Error fetching repositories for organization %s: %s", org_name, e
            )
            self._handle_github_exception(
                e, f"fetching repositories for organization {org_name}"
            )
            return []  # This line will never be reached, but satisfies mypy
        except requests.exceptions.Timeout:
            raise ValueError(
                f"Request timed out while fetching repositories for organization "
                f"{org_name}"
            )
        except requests.exceptions.ConnectionError:
            raise ValueError(
                "Network error while fetching repositories. Check your internet "
                "connection."
            )
        except Exception as e:
            logger.error(
                "Unexpected error fetching repositories for organization %s: %s",
                org_name,
                e,
            )
            raise ValueError(f"Unexpected error fetching repositories: {e}")

    def get_all_repos(
        self, username_or_org: str, is_organization: bool = False, limit: int = 100
    ) -> List[Repository]:
        """Get repositories for a user or organization with pagination.

        Args:
            username_or_org: GitHub username or organization name
            is_organization: Whether the target is an organization
            limit: Maximum number of repositories to fetch (default: 100)

        Returns:
            List of Repository objects (up to limit)
        """
        try:
            if is_organization:
                org = self.github.get_organization(username_or_org)
                repos = org.get_repos(sort="updated", direction="desc")
            else:
                user = self.github.get_user(username_or_org)
                repos = user.get_repos(sort="updated", direction="desc")

            # Fetch repositories with limit to prevent hanging
            repo_list = []
            for i, repo in enumerate(repos):
                if i >= limit:
                    break
                repo_list.append(Repository.from_pygithub(repo))

            logger.info(f"Fetched {len(repo_list)} repositories for {username_or_org}")
            return repo_list
        except GithubException as e:
            logger.error("Error fetching repositories for %s: %s", username_or_org, e)
            self._handle_github_exception(
                e, f"fetching repositories for {username_or_org}"
            )
            return []  # This line will never be reached, but satisfies mypy
        except requests.exceptions.Timeout:
            raise ValueError(
                f"Request timed out while fetching repositories for {username_or_org}"
            )
        except requests.exceptions.ConnectionError:
            raise ValueError(
                "Network error while fetching repositories. Check your internet "
                "connection."
            )
        except Exception as e:
            logger.error(
                "Unexpected error fetching repositories for %s: %s", username_or_org, e
            )
            raise ValueError(f"Unexpected error fetching repositories: {e}")

    def get_repo_stats(
        self, username_or_org: str, is_organization: bool = False, limit: int = 100
    ) -> Dict:
        """Get repository statistics for a user or organization.

        Args:
            username_or_org: GitHub username or organization name
            is_organization: Whether the target is an organization
            limit: Maximum number of repositories to fetch (default: 100)

        Returns:
            Dictionary with repository statistics
        """
        repos = self.get_all_repos(username_or_org, is_organization, limit)

        if not repos:
            return {}

        total_repos = len(repos)
        public_repos = len([r for r in repos if not r.private])
        private_repos = total_repos - public_repos
        archived_repos = len([r for r in repos if r.archived])

        languages: Dict[str, int] = {}
        total_stars = 0
        total_forks = 0
        total_size = 0

        for repo in repos:
            if repo.language:
                languages[repo.language] = languages.get(repo.language, 0) + 1
            total_stars += repo.stargazers_count
            total_forks += repo.forks_count
            total_size += repo.size

        # Sort languages by count
        top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "total_repositories": total_repos,
            "public_repositories": public_repos,
            "private_repositories": private_repos,
            "archived_repositories": archived_repos,
            "total_stars": total_stars,
            "total_forks": total_forks,
            "total_size_mb": round(total_size / 1024, 2),
            "top_languages": top_languages,
            "repositories": repos,
        }
