"""Command-line interface for GitHub Repository Analyzer."""

import logging
import sys
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# Import version information from package
from . import __author__, __email__, __license__, __repository__, __version__
from .api import GitHubAPI
from .formatters import display_json, display_summary, display_table
from .services import RepositoryService

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    stream=sys.stderr,  # Log to stderr so it doesn't interfere with stdout
)
logger = logging.getLogger(__name__)

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="github-repo-analyzer")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--quiet", "-q", is_flag=True, help="Suppress all logging output")
@click.pass_context
def main(ctx: click.Context, verbose: bool, quiet: bool) -> None:
    """GitHub Repository Analyzer - Analyze GitHub repositories for users and organizations."""  # noqa: E501
    # Configure logging level based on options
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    # Store options in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet


@main.command()
@click.argument("username_or_org")
@click.option("--org", is_flag=True, help="Treat the input as an organization name")
@click.option("--token", "-t", help="GitHub personal access token")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["table", "json", "summary"]),
    default="table",
    help="Output format",
)
@click.option(
    "--limit",
    "-l",
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
def analyze(
    ctx: click.Context,
    username_or_org: str,
    org: bool,
    token: Optional[str],
    output: str,
    limit: Optional[int],
    sort: str,
    cache_dir: str,
    cache_ttl: int,
    no_cache: bool,
) -> None:
    """Analyze repositories for a GitHub user or organization.

    Args:
        ctx: Click context
        username_or_org: GitHub username or organization name
        org: Whether the input is an organization
        token: GitHub personal access token
        output: Output format (table, json, summary)
        limit: Maximum number of repositories to fetch
        sort: Sort repositories by field (name, stars, forks, updated, created, size)
        cache_dir: Cache directory
        cache_ttl: Cache time-to-live in seconds
        no_cache: Whether to disable caching
    """
    try:
        # Configure cache settings
        cache_dir_val: Optional[str] = None if no_cache else cache_dir
        cache_ttl_val = 0 if no_cache else cache_ttl

        # Initialize API and service
        api = GitHubAPI(token, cache_dir=cache_dir_val, cache_ttl=cache_ttl_val)
        service = RepositoryService(api)

        # Validate inputs
        service.validate_inputs(username_or_org, limit)

        logger.info(
            "Fetching repositories for %s: %s",
            "organization" if org else "user",
            username_or_org,
        )

        # Use limit if provided, otherwise use API default (100)
        # Use -1 to mean unlimited (all repositories), 0 means actually 0
        if limit is None:
            limit_val = 100  # Default to GitHub API max per page
        elif limit == -1:
            limit_val = 10000  # Unlimited - set very high limit
        else:
            limit_val = limit

        # Analyze repositories using service
        stats = service.analyze_repositories(
            username_or_org, is_organization=org, limit=limit_val, sort_field=sort
        )

        if not stats:
            console.print("[red]No repositories found or error occurred.[/red]")
            return

        repos = stats["repositories"]

        if limit:
            repos = repos[:limit]

        if output == "summary":
            display_summary(stats, username_or_org, org)
        elif output == "json":
            display_json(repos)
        else:
            display_table(repos, username_or_org, org)

    except ValueError as e:
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
        logger.exception("Unexpected error in analyze command")
        raise click.ClickException(f"Unexpected error: {e}")


@main.command()
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
        # Configure cache settings
        cache_dir_val: Optional[str] = None if no_cache else cache_dir
        cache_ttl_val = 0 if no_cache else cache_ttl

        # Initialize API and service
        api = GitHubAPI(token, cache_dir=cache_dir_val, cache_ttl=cache_ttl_val)
        service = RepositoryService(api)

        # Validate inputs
        service.validate_inputs(username_or_org, limit, public_only, private_only)

        logger.info(
            "Searching repositories for %s: %s",
            "organization" if org else "user",
            username_or_org,
        )

        # Use limit if provided, otherwise use API default (100)
        # Use -1 to mean unlimited (all repositories), 0 means actually 0
        if limit is None:
            limit_val = 100  # Default to GitHub API max per page
        elif limit == -1:
            limit_val = 10000  # Unlimited - set very high limit
        else:
            limit_val = limit

        # Search repositories using service
        filtered_repos = service.search_repositories(
            username_or_org,
            is_organization=org,
            language=language,
            min_stars=min_stars,
            min_forks=min_forks,
            public_only=public_only,
            private_only=private_only,
            limit=limit_val,
            sort_field=sort,
        )

        if not filtered_repos:
            console.print("[red]No repositories found or error occurred.[/red]")
            return

        # Apply limit if specified
        if limit:
            filtered_repos = filtered_repos[:limit]

        logger.info("Found %d repositories matching criteria", len(filtered_repos))
        display_table(filtered_repos, username_or_org, org)

    except ValueError as e:
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


@main.command()
def version() -> None:
    """Show detailed version information."""
    version_info = f"""
[bold blue]GitHub Repository Analyzer[/bold blue]
Version: [green]{__version__}[/green]
Author: [yellow]{__author__}[/yellow]
Email: [cyan]{__email__}[/cyan]
Repository: [blue]{__repository__}[/blue]
License: [green]{__license__}[/green]
"""
    console.print(
        Panel(version_info.strip(), title="Version Information", border_style="blue")
    )


if __name__ == "__main__":
    main()
