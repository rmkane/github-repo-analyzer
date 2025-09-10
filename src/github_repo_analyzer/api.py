"""GitHub API client for repository analysis."""

import os
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin

import requests
from pydantic import BaseModel, Field
from rich.console import Console

console = Console()


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

    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub API client.

        Args:
            token: GitHub personal access token. If not provided, will try to get
                from GITHUB_TOKEN env var.
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

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            repos_data = response.json()
            return [Repository(**repo) for repo in repos_data]

        except requests.exceptions.RequestException as e:
            console.print(f"[red]Error fetching repositories for {username}: {e}[/red]")
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

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            repos_data = response.json()
            return [Repository(**repo) for repo in repos_data]

        except requests.exceptions.RequestException as e:
            console.print(
                f"[red]Error fetching repositories for organization "
                f"{org_name}: {e}[/red]"
            )
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
