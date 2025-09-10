"""Command-line interface for GitHub Repository Analyzer."""

import logging
import sys
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import version information from package
from . import __author__, __email__, __license__, __repository__, __version__
from .api import GitHubAPI

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
@click.option("--limit", "-l", type=int, help="Limit number of repositories to show")
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
    cache_dir: str,
    cache_ttl: int,
    no_cache: bool,
) -> None:
    """Analyze repositories for a GitHub user or organization.

    USERNAME_OR_ORG: GitHub username or organization name
    """
    try:
        # Configure cache settings
        cache_dir_val: Optional[str] = None if no_cache else cache_dir
        cache_ttl_val = 0 if no_cache else cache_ttl

        api = GitHubAPI(token, cache_dir=cache_dir_val, cache_ttl=cache_ttl_val)

        logger.info(
            "Fetching repositories for %s: %s",
            "organization" if org else "user",
            username_or_org,
        )

        stats = api.get_repo_stats(username_or_org, is_organization=org)

        if not stats:
            console.print("[red]No repositories found or error occurred.[/red]")
            return

        repos = stats["repositories"]
        if limit:
            repos = repos[:limit]

        if output == "summary":
            _display_summary(stats, username_or_org, org)
        elif output == "json":
            _display_json(repos)
        else:
            _display_table(repos, username_or_org, org)

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print(
            "[yellow]Tip: Set GITHUB_TOKEN environment variable or use "
            "--token option[/yellow]"
        )
        raise click.ClickException(str(e))
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise click.ClickException(str(e))


@main.command()
@click.argument("username_or_org")
@click.option("--org", is_flag=True, help="Treat the input as an organization name")
@click.option("--token", "-t", help="GitHub personal access token")
@click.option("--language", help="Filter by programming language")
@click.option("--min-stars", type=int, help="Minimum number of stars")
@click.option("--min-forks", type=int, help="Minimum number of forks")
@click.option("--public-only", is_flag=True, help="Show only public repositories")
@click.option("--private-only", is_flag=True, help="Show only private repositories")
@click.option("--limit", type=int, help="Limit number of repositories to show")
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
    cache_dir: str,
    cache_ttl: int,
    no_cache: bool,
) -> None:
    """Search and filter repositories for a GitHub user or organization.

    USERNAME_OR_ORG: GitHub username or organization name
    """
    try:
        # Configure cache settings
        cache_dir_val: Optional[str] = None if no_cache else cache_dir
        cache_ttl_val = 0 if no_cache else cache_ttl

        api = GitHubAPI(token, cache_dir=cache_dir_val, cache_ttl=cache_ttl_val)

        logger.info(
            "Searching repositories for %s: %s",
            "organization" if org else "user",
            username_or_org,
        )

        stats = api.get_repo_stats(username_or_org, is_organization=org)

        if not stats:
            console.print("[red]No repositories found or error occurred.[/red]")
            return

        repos = stats["repositories"]

        # Apply filters
        filtered_repos = repos

        if language:
            filtered_repos = [
                r
                for r in filtered_repos
                if r.language and r.language.lower() == language.lower()
            ]

        if min_stars:
            filtered_repos = [
                r for r in filtered_repos if r.stargazers_count >= min_stars
            ]

        if min_forks:
            filtered_repos = [r for r in filtered_repos if r.forks_count >= min_forks]

        if public_only:
            filtered_repos = [r for r in filtered_repos if not r.private]

        if private_only:
            filtered_repos = [r for r in filtered_repos if r.private]

        # Apply limit if specified
        if limit:
            filtered_repos = filtered_repos[:limit]

        logger.info("Found %d repositories matching criteria", len(filtered_repos))
        _display_table(filtered_repos, username_or_org, org)

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print(
            "[yellow]Tip: Set GITHUB_TOKEN environment variable or use "
            "--token option[/yellow]"
        )
        raise click.ClickException(str(e))
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise click.ClickException(str(e))


def _display_summary(stats: dict, username_or_org: str, is_org: bool) -> None:
    """Display repository summary statistics."""
    entity_type = "Organization" if is_org else "User"

    summary_text = f"""
[bold]{entity_type}:[/bold] {username_or_org}

[bold]Repository Statistics:[/bold]
• Total Repositories: {stats['total_repositories']}
• Public Repositories: {stats['public_repositories']}
• Private Repositories: {stats['private_repositories']}
• Archived Repositories: {stats['archived_repositories']}

[bold]Activity Statistics:[/bold]
• Total Stars: {stats['total_stars']:,}
• Total Forks: {stats['total_forks']:,}
• Total Size: {stats['total_size_mb']:.2f} MB

[bold]Top Languages:[/bold]
"""

    for lang, count in stats["top_languages"]:
        summary_text += f"• {lang}: {count} repositories\n"

    panel = Panel(summary_text.strip(), title="Repository Summary", border_style="blue")
    console.print(panel)


def _display_table(repos: list, username_or_org: str, is_org: bool) -> None:
    """Display repositories in a table format."""
    if not repos:
        console.print("[yellow]No repositories to display[/yellow]")
        return

    table = Table(
        title=f"Repositories for {'Organization' if is_org else 'User'}: "
        f"{username_or_org}"
    )

    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Language", style="magenta")
    table.add_column("Stars", justify="right", style="green")
    table.add_column("Forks", justify="right", style="blue")
    table.add_column("Size (MB)", justify="right", style="yellow")
    table.add_column("Private", justify="center")
    table.add_column("Archived", justify="center")
    table.add_column("Updated", style="dim")

    for repo in repos:
        table.add_row(
            repo.name,
            repo.language or "N/A",
            str(repo.stargazers_count),
            str(repo.forks_count),
            f"{repo.size / 1024:.1f}",
            "✓" if repo.private else "✗",
            "✓" if repo.archived else "✗",
            repo.updated_at[:10],  # Just the date part
        )

    console.print(table)


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


def _display_json(repos: list) -> None:
    """Display repositories in JSON format."""
    import json
    import re

    repos_data = []
    for repo in repos:
        repo_dict = repo.dict()

        # Clean control characters from string fields
        for key, value in repo_dict.items():
            if isinstance(value, str):
                # Replace control characters with spaces
                repo_dict[key] = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", value)
                # Collapse multiple spaces
                repo_dict[key] = re.sub(r"\s+", " ", repo_dict[key]).strip()

        repos_data.append(repo_dict)

    # Output clean JSON with proper escaping
    json_str = json.dumps(
        repos_data, indent=2, ensure_ascii=False, separators=(",", ": ")
    )
    print(json_str)


if __name__ == "__main__":
    main()
