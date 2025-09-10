"""GitHub API client for repository analysis."""

import hashlib
import logging
import os
import pickle
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import requests
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _clean_repository_data(repos_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean control characters from repository data."""
    import re

    logger.debug("Cleaning %d repositories", len(repos_data))
    cleaned_repos = []
    for repo in repos_data:
        cleaned_repo = {}
        for key, value in repo.items():
            if isinstance(value, str):
                # Replace control characters with spaces
                original_value = value
                cleaned_repo[key] = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", value)
                # Collapse multiple spaces
                cleaned_repo[key] = re.sub(r"\s+", " ", cleaned_repo[key]).strip()
                if original_value != cleaned_repo[key]:
                    logger.debug("Cleaned control characters in %s", key)
            else:
                cleaned_repo[key] = value
        cleaned_repos.append(cleaned_repo)
    logger.debug("Cleaned %d repositories", len(cleaned_repos))
    return cleaned_repos


class CacheManager:
    """Simple file-based cache manager for API responses."""

    def __init__(self, cache_dir: Optional[str] = ".cache", ttl_seconds: int = 3600):
        """Initialize cache manager.

        Args:
            cache_dir: Directory to store cache files (None to disable caching)
            ttl_seconds: Time-to-live for cached data in seconds (default: 1 hour)
        """
        self.cache_dir: Optional[Path] = (
            Path(cache_dir) if cache_dir is not None else None
        )
        if self.cache_dir is not None:
            self.cache_dir.mkdir(exist_ok=True)
        self.ttl_seconds = ttl_seconds
        self.enabled = cache_dir is not None

    def _get_cache_key(self, url: str, params: Dict[str, Union[str, int]]) -> str:
        """Generate a cache key for the request."""
        # Create a hash of URL + sorted params for consistent keys
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        cache_string = f"{url}?{param_str}"
        return hashlib.md5(cache_string.encode()).hexdigest()

    def get(self, url: str, params: Dict[str, Union[str, int]]) -> Optional[List[Dict]]:
        """Get cached data if available and not expired."""
        if not self.enabled:
            return None

        cache_key = self._get_cache_key(url, params)
        cache_file = self.cache_dir / f"{cache_key}.pkl"  # type: ignore

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "rb") as f:
                cached_data: Dict[str, Any] = pickle.load(f)

            # Check if cache is expired
            if time.time() - cached_data["timestamp"] > self.ttl_seconds:
                logger.debug("Cache expired for %s", cache_key)
                cache_file.unlink()  # Remove expired cache
                return None

            logger.debug("Cache hit for %s", cache_key)
            return cached_data["data"]  # type: ignore

        except (pickle.PickleError, KeyError, OSError) as e:
            logger.warning("Failed to load cache file %s: %s", cache_file, e)
            cache_file.unlink()  # Remove corrupted cache
            return None

    def set(
        self, url: str, params: Dict[str, Union[str, int]], data: List[Dict]
    ) -> None:
        """Cache the response data."""
        if not self.enabled:
            return

        cache_key = self._get_cache_key(url, params)
        cache_file = self.cache_dir / f"{cache_key}.pkl"  # type: ignore

        try:
            cached_data = {
                "timestamp": time.time(),
                "data": data,
                "url": url,
                "params": params,
            }

            with open(cache_file, "wb") as f:
                pickle.dump(cached_data, f)

            logger.debug("Cached response for %s", cache_key)

        except OSError as e:
            logger.warning("Failed to save cache file %s: %s", cache_file, e)

    def clear(self) -> None:
        """Clear all cached data."""
        if self.enabled and self.cache_dir is not None and self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            logger.info("Cleared all cached data")


class Repository(BaseModel):
    """Repository model."""

    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    clone_url: str
    ssh_url: str
    language: Optional[str] = None
    stargazers_count: int = Field(alias="stargazers_count")
    forks_count: int = Field(alias="forks_count")
    open_issues_count: int = Field(alias="open_issues_count")
    size: int
    created_at: str
    updated_at: str
    pushed_at: Optional[str] = None
    private: bool
    archived: bool
    disabled: bool
    topics: List[str] = Field(default_factory=list)
    license: Optional[Dict] = None
    owner: Dict


class GitHubAPI:
    """GitHub API client."""

    BASE_URL = "https://api.github.com"

    def __init__(
        self,
        token: Optional[str] = None,
        cache_dir: Optional[str] = ".cache",
        cache_ttl: int = 3600,
    ):
        """Initialize GitHub API client.

        Args:
            token: GitHub personal access token. If not provided, will try to get
                from GITHUB_TOKEN env var.
            cache_dir: Directory to store cache files (default: ".cache")
            cache_ttl: Cache time-to-live in seconds (default: 3600 = 1 hour)
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError(
                "GitHub token is required. Set GITHUB_TOKEN env var or pass "
                "token parameter."
            )

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "github-repo-analyzer/0.1.0",
            }
        )

        # Initialize cache
        self.cache = CacheManager(cache_dir, cache_ttl)

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
        url = urljoin(self.BASE_URL, f"/users/{username}/repos")
        params: Dict[str, Union[str, int]] = {
            "per_page": min(per_page, 100),
            "page": page,
            "sort": "updated",
            "direction": "desc",
        }

        # Check cache first
        cached_data = self.cache.get(url, params)
        if cached_data is not None:
            logger.debug("Using cached data for user %s page %d", username, page)
            # Clean cached data as well (in case it was cached before cleaning)
            cleaned_cached_data = _clean_repository_data(cached_data)
            return [Repository(**repo) for repo in cleaned_cached_data]

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            repos_data = response.json()

            # Clean control characters from the data
            cleaned_repos_data = _clean_repository_data(repos_data)

            # Cache the cleaned response
            self.cache.set(url, params, cleaned_repos_data)

            return [Repository(**repo) for repo in cleaned_repos_data]

        except requests.exceptions.RequestException as e:
            logger.error("Error fetching repositories for %s: %s", username, e)
            # Re-raise authentication errors
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 401:
                    raise ValueError("Invalid GitHub token or insufficient permissions")
            return []

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
        url = urljoin(self.BASE_URL, f"/orgs/{org_name}/repos")
        params: Dict[str, Union[str, int]] = {
            "per_page": min(per_page, 100),
            "page": page,
            "sort": "updated",
            "direction": "desc",
        }

        # Check cache first
        cached_data = self.cache.get(url, params)
        if cached_data is not None:
            logger.debug("Using cached data for org %s page %d", org_name, page)
            # Clean cached data as well (in case it was cached before cleaning)
            cleaned_cached_data = _clean_repository_data(cached_data)
            return [Repository(**repo) for repo in cleaned_cached_data]

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            repos_data = response.json()

            # Clean control characters from the data
            cleaned_repos_data = _clean_repository_data(repos_data)

            # Cache the cleaned response
            self.cache.set(url, params, cleaned_repos_data)

            return [Repository(**repo) for repo in cleaned_repos_data]

        except requests.exceptions.RequestException as e:
            logger.error(
                "Error fetching repositories for organization %s: %s", org_name, e
            )
            # Re-raise authentication errors
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 401:
                    raise ValueError("Invalid GitHub token or insufficient permissions")
            return []

    def get_all_repos(
        self, username_or_org: str, is_organization: bool = False
    ) -> List[Repository]:
        """Get all repositories for a user or organization (handles pagination).

        Args:
            username_or_org: GitHub username or organization name
            is_organization: Whether the target is an organization

        Returns:
            List of all Repository objects
        """
        all_repos = []
        page = 1
        per_page = 100

        while True:
            if is_organization:
                repos = self.get_org_repos(username_or_org, per_page, page)
            else:
                repos = self.get_user_repos(username_or_org, per_page, page)

            if not repos:
                break

            all_repos.extend(repos)

            # If we got fewer repos than requested, we've reached the end
            if len(repos) < per_page:
                break

            page += 1

        return all_repos

    def get_repo_stats(
        self, username_or_org: str, is_organization: bool = False
    ) -> Dict:
        """Get repository statistics for a user or organization.

        Args:
            username_or_org: GitHub username or organization name
            is_organization: Whether the target is an organization

        Returns:
            Dictionary with repository statistics
        """
        repos = self.get_all_repos(username_or_org, is_organization)

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
