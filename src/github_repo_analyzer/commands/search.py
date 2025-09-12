"""Search command for GitHub Repository Analyzer."""

from typing import Optional

import click
from rich.console import Console

from github_repo_analyzer.config import create_config
from github_repo_analyzer.core import GitHubAPI, RepositoryService
from github_repo_analyzer.formatters import display_table
from github_repo_analyzer.loggers import get_logger
from github_repo_analyzer.utils import clamp_limit
from github_repo_analyzer.validation import (
    ValidationError,
    validate_config_inputs,
    validate_search_inputs,
)

logger = get_logger(__name__)
console = Console()


@click.command()
@click.argument("username_or_org")
@click.option("--org", is_flag=True, help="Treat the input as an organization name")
@click.option("--token", "-t", help="GitHub personal access token")
@click.option("--language", help="Filter by programming language")
@click.option("--min-stars", type=int, help="Minimum number of stars")
@click.option("--min-forks", type=int, help="Minimum number of forks")
@click.option("--public-only", is_flag=True, help="Show only public repositories")
@click.option("--private-only", is_flag=True, help="Show only private repositories")
@click.option(
    "--limit",
    type=int,
    help="Limit number of repositories to show (default: 100, use -1 for all)",
)
@click.option(
    "--sort",
    "-s",
    type=click.Choice(["name", "stars", "forks", "updated", "created", "size"]),
    default="updated",
    help="Sort repositories by field (default: updated)",
)
@click.option(
    "--cache-dir", default=".cache", help="Directory for cache files (default: .cache)"
)
@click.option(
    "--cache-ttl",
    type=int,
    default=3600,
    help="Cache time-to-live in seconds (default: 3600)",
)
@click.option("--no-cache", is_flag=True, help="Disable caching")
@click.pass_context
def search(
    ctx: click.Context,
    username_or_org: str,
    org: bool,
    token: Optional[str],
    language: Optional[str],
    min_stars: Optional[int],
    min_forks: Optional[int],
    public_only: bool,
    private_only: bool,
    limit: Optional[int],
    sort: str,
    cache_dir: str,
    cache_ttl: int,
    no_cache: bool,
) -> None:
    """Search and filter repositories for a GitHub user or organization.

    Args:
        ctx: Click context
        username_or_org: GitHub username or organization name
        org: Whether the input is an organization
        token: GitHub personal access token
        language: Filter by programming language
        min_stars: Minimum number of stars
        min_forks: Minimum number of forks
        public_only: Show only public repositories
        private_only: Show only private repositories
        limit: Maximum number of repositories to fetch
        sort: Sort repositories by field (name, stars, forks, updated, created, size)
        cache_dir: Cache directory
        cache_ttl: Cache time-to-live in seconds
        no_cache: Whether to disable caching
    """
    try:
        # Validate configuration inputs
        config_inputs = validate_config_inputs(
            token=token,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
        )

        # Create configuration
        config = create_config(
            token=config_inputs.get("token"),
            cache_dir=config_inputs["cache_dir"],
            cache_ttl=config_inputs["cache_ttl"],
            no_cache=no_cache,
        )

        # Validate search inputs
        search_inputs = validate_search_inputs(
            username_or_org=username_or_org,
            limit=limit,
            sort_field=sort,
            language=language,
            min_stars=min_stars,
            min_forks=min_forks,
            public_only=public_only,
            private_only=private_only,
        )

        # Initialize API and service
        api = GitHubAPI(
            token=config.github_token,
            cache_dir=config.cache.directory if config.cache.enabled else None,
            cache_ttl=config.cache.ttl_seconds,
            timeout=config.api.timeout_seconds,
        )
        service = RepositoryService(api)

        logger.info(
            "Searching repositories for %s: %s",
            "organization" if org else "user",
            search_inputs["username_or_org"],
        )

        # Clamp limit to valid range using config
        limit_val = clamp_limit(
            search_inputs["limit"], config.limits.default_limit, config.limits.max_limit
        )

        # Search repositories using service
        filtered_repos = service.search_repositories(
            search_inputs["username_or_org"],
            is_organization=org,
            language=search_inputs["language"],
            min_stars=search_inputs["min_stars"],
            min_forks=search_inputs["min_forks"],
            public_only=search_inputs["public_only"],
            private_only=search_inputs["private_only"],
            limit=limit_val,
            sort_field=search_inputs["sort_field"],
        )

        if not filtered_repos:
            console.print("[red]No repositories found or error occurred.[/red]")
            return

        logger.info("Found %d repositories matching criteria", len(filtered_repos))
        display_table(filtered_repos, search_inputs["username_or_org"], org)

    except (ValueError, ValidationError) as e:
        error_msg = str(e)
        if "token" in error_msg.lower():
            console.print(f"[red]Authentication Error: {error_msg}[/red]")
            console.print(
                "[yellow]Tip: Set GITHUB_TOKEN environment variable or use "
                "--token option[/yellow]"
            )
        elif "rate limit" in error_msg.lower():
            console.print(f"[red]Rate Limit Error: {error_msg}[/red]")
            console.print(
                "[yellow]Tip: Wait a few minutes before trying again, or use a "
                "personal access token for higher limits[/yellow]"
            )
        elif "not found" in error_msg.lower():
            console.print(f"[red]Not Found Error: {error_msg}[/red]")
            console.print(
                "[yellow]Tip: Check the username or organization name is "
                "correct[/yellow]"
            )
        elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            console.print(f"[red]Network Error: {error_msg}[/red]")
            console.print(
                "[yellow]Tip: Check your internet connection and try again[/yellow]"
            )
        else:
            console.print(f"[red]Error: {error_msg}[/red]")
        raise click.ClickException(error_msg)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        logger.exception("Unexpected error in search command")
        raise click.ClickException(f"Unexpected error: {e}")
